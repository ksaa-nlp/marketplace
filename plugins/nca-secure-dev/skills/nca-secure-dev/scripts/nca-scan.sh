#!/usr/bin/env bash
# nca-scan.sh — read-only evidence collector for NCA compliance audits.
# Usage: bash nca-scan.sh [project-dir]
# - Never modifies project files (writes only to <project>/compliance/evidence/).
# - Never installs anything; prints install hints for missing tools.
# - Works on Linux, macOS, and Windows (Git Bash / WSL).

PROJECT="${1:-.}"
if [ ! -d "$PROJECT" ]; then echo "Project dir not found: $PROJECT"; exit 1; fi
PROJECT="$(cd "$PROJECT" && pwd)"
EV="$PROJECT/compliance/evidence"
mkdir -p "$EV"
SUMMARY="$EV/SUMMARY.txt"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

have() { command -v "$1" >/dev/null 2>&1; }
log() { echo "$*" | tee -a "$SUMMARY"; }

: > "$SUMMARY"
log "NCA evidence scan — $STAMP"
log "Project: $PROJECT"
if have git && git -C "$PROJECT" rev-parse >/dev/null 2>&1; then
  log "Commit: $(git -C "$PROJECT" rev-parse HEAD 2>/dev/null) (branch $(git -C "$PROJECT" rev-parse --abbrev-ref HEAD 2>/dev/null))"
  if [ -n "$(git -C "$PROJECT" status --porcelain 2>/dev/null | grep -v '^?? compliance/')" ]; then
    log "Note: working tree has uncommitted changes."
  fi
fi
log ""

# ---------- Stack detection ----------
log "== Stack detection =="
STACK=""
f() { [ -e "$PROJECT/$1" ]; }
f package.json && STACK="$STACK node"
{ f requirements.txt || f pyproject.toml || f Pipfile; } && STACK="$STACK python"
{ f pom.xml || f build.gradle || f build.gradle.kts; } && STACK="$STACK java"
f go.mod && STACK="$STACK go"
f composer.json && STACK="$STACK php"
f Gemfile && STACK="$STACK ruby"
ls "$PROJECT"/*.csproj "$PROJECT"/*.sln >/dev/null 2>&1 && STACK="$STACK dotnet"
f pubspec.yaml && STACK="$STACK flutter"
{ f android || f app/src/main/AndroidManifest.xml; } && STACK="$STACK android"
{ f ios || ls "$PROJECT"/*.xcodeproj >/dev/null 2>&1; } && STACK="$STACK ios"
f Dockerfile && STACK="$STACK docker"
{ ls "$PROJECT"/*.tf >/dev/null 2>&1 || f terraform; } && STACK="$STACK terraform"
{ f .github/workflows || f .gitlab-ci.yml || f azure-pipelines.yml || f Jenkinsfile || f bitbucket-pipelines.yml; } && STACK="$STACK ci"
log "Detected:${STACK:- unknown}"
for lf in package-lock.json yarn.lock pnpm-lock.yaml poetry.lock Pipfile.lock requirements.txt go.sum composer.lock Gemfile.lock; do
  f "$lf" && log "Lockfile/manifest present: $lf"
done
log ""

MISSING=""
run_tool() { # name, outfile, command...
  name="$1"; out="$2"; shift 2
  log "-- $name -> evidence/$out"
  ( cd "$PROJECT" && "$@" ) > "$EV/$out" 2>"$EV/$out.stderr"
  code=$?
  [ -s "$EV/$out.stderr" ] || rm -f "$EV/$out.stderr"
  log "   exit code $code (non-zero usually means findings)"
}

# ---------- Secrets ----------
log "== Secrets scan (2-8-3-2) =="
if have gitleaks; then
  # gitleaks writes the JSON itself via --report-path, so stdout goes to a separate log.
  run_tool gitleaks gitleaks.log gitleaks detect --source . --report-format json --report-path "$EV/gitleaks.json" --no-banner --exit-code 0
  if [ -s "$EV/gitleaks.json" ]; then
    n=$(grep -c '"RuleID"' "$EV/gitleaks.json" 2>/dev/null || echo 0)
    log "   leaked secrets reported: $n (evidence/gitleaks.json)"
  fi
else MISSING="$MISSING gitleaks"; log "gitleaks not installed"; fi
log ""

# ---------- SAST ----------
log "== SAST (1-6-3-1, 1-6-3-3) =="
if have semgrep; then
  run_tool semgrep semgrep.json semgrep scan --config auto --json --quiet --exclude compliance
else MISSING="$MISSING semgrep"; log "semgrep not installed"; fi
log ""

# ---------- Dependencies ----------
log "== Dependency vulnerabilities (1-6-3-2, 2-10) =="
case "$STACK" in *node*)
  if have npm && f package-lock.json; then run_tool "npm audit" npm-audit.json npm audit --json --omit=dev
  elif have pnpm && f pnpm-lock.yaml; then run_tool "pnpm audit" pnpm-audit.json pnpm audit --json --prod
  elif have yarn && f yarn.lock; then run_tool "yarn audit" yarn-audit.json yarn audit --json --groups dependencies
  else log "Node project without a usable lockfile/tool"; fi ;;
esac
case "$STACK" in *python*)
  if have pip-audit; then
    if f requirements.txt; then run_tool pip-audit pip-audit.json pip-audit -r requirements.txt -f json
    else run_tool pip-audit pip-audit.json pip-audit -f json; fi
  else MISSING="$MISSING pip-audit"; log "pip-audit not installed"; fi ;;
esac
if have osv-scanner; then
  run_tool osv-scanner osv.json osv-scanner scan source -r --format json .
elif have trivy; then
  run_tool "trivy fs" trivy-fs.json trivy fs --quiet --format json --scanners vuln,misconfig,secret --skip-dirs compliance .
else MISSING="$MISSING osv-scanner/trivy"; log "osv-scanner / trivy not installed (multi-language dependency + IaC scan)"; fi
log ""

# ---------- SBOM ----------
log "== SBOM (1-6-3-2) =="
if have syft; then run_tool syft sbom.cdx.json syft dir:. -o cyclonedx-json
elif have trivy; then run_tool "trivy sbom" sbom.cdx.json trivy fs --quiet --format cyclonedx .
else MISSING="$MISSING syft"; log "syft not installed"; fi
log ""

# ---------- Quick pattern checks (leads, not verdicts) ----------
log "== Quick pattern checks -> evidence/quick-checks.txt (leads to review manually) =="
QC="$EV/quick-checks.txt"
: > "$QC"
EXCL_DIRS="node_modules .git vendor dist build out target .next .nuxt coverage compliance __pycache__ .venv venv Pods .gradle uploaded-games uploaded_games .docker-data .docker-data-beta public/uploaded-games bundle bundles"
# Longest line kept in the evidence file. A single minified JS/WASM line can be
# megabytes wide, so capping lines (not just their count) is what keeps the
# evidence readable: an uncapped run on a project serving minified third-party
# bundles produced a 90 MB quick-checks.txt from only a few hundred lines.
MAX_LINE_CHARS="${NCA_MAX_LINE_CHARS:-400}"
MAX_HITS_PER_CHECK="${NCA_MAX_HITS:-200}"
search() { # title, regex
  echo "### $1" >> "$QC"
  if have rg; then
    globs=""; for d in $EXCL_DIRS; do globs="$globs -g !**/$d/**"; done
    # shellcheck disable=SC2086
    rg -n -i --no-heading --max-columns "$MAX_LINE_CHARS" --max-columns-preview \
       -g '!**/*.min.js' -g '!**/*.min.css' -g '!**/*.map' -g '!**/*.wasm' \
       $globs -e "$2" "$PROJECT" 2>/dev/null \
      | head -n "$MAX_HITS_PER_CHECK" | cut -c "1-$MAX_LINE_CHARS" >> "$QC"
  else
    ex=""; for d in $EXCL_DIRS; do ex="$ex --exclude-dir=$d"; done
    # shellcheck disable=SC2086
    grep -rniE $ex --exclude='*.min.js' --exclude='*.min.css' --exclude='*.map' \
      --exclude='*.wasm' -e "$2" "$PROJECT" 2>/dev/null \
      | head -n "$MAX_HITS_PER_CHECK" | cut -c "1-$MAX_LINE_CHARS" >> "$QC"
  fi
  n=$(awk -v t="### $1" 'BEGIN{c=0;on=0} $0==t{on=1;next} /^### /{on=0} on{c++} END{print c}' "$QC")
  log "$(printf '%-55s %s hit(s)' "$1" "$n")"
  echo "" >> "$QC"
}
search "Hardcoded secrets (2-8-3-2)" '(api[_-]?key|secret|passwd|password|token)["'"'"']?\s*[:=]\s*["'"'"'][^"'"'"'$\{]{8,}|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC )?PRIVATE KEY'
search "TLS verification disabled (2-8-3-3)" 'verify\s*=\s*False|rejectUnauthorized\s*:\s*false|InsecureSkipVerify\s*:\s*true|NODE_TLS_REJECT_UNAUTHORIZED|usesCleartextTraffic="true"|NSAllowsArbitraryLoads'
search "Weak crypto / hashing (2-8-3-1)" '\b(md5|sha1)\s*\(|createHash\(["'"'"'](md5|sha1)|\bDES\b|TripleDES|RC4|/ECB/|AES/ECB|MessageDigest\.getInstance\("(MD5|SHA-?1)"'
search "Insecure randomness for tokens" 'Math\.random\(|random\.random\(|new Random\('
search "Dangerous execution / deserialization (1-6-3-1)" '\beval\(|child_process|Runtime\.getRuntime\(\)\.exec|pickle\.loads|yaml\.load\(|unserialize\(|os\.system\('
search "Possible SQL string building (1-6-3-1)" '(SELECT|INSERT|UPDATE|DELETE)\b[^;\n]{0,80}("\s*\+|\+\s*"|\$\{|%s|f")'
search "XSS sinks (1-6-3-1)" 'innerHTML\s*=|dangerouslySetInnerHTML|\|\s*safe\b|v-html|bypassSecurityTrust'
search "Debug / verbose mode (1-6-3-5)" 'DEBUG\s*=\s*True|app\.debug\s*=\s*True|android:debuggable="true"|"debug"\s*:\s*true'
search "Permissive CORS (2-15)" 'Access-Control-Allow-Origin["'"'"']?\s*[,:]\s*["'"'"']\*|origin\s*:\s*["'"'"']\*|allow_origins=\[\s*["'"'"']\*'
search "Plain HTTP endpoints, excl. localhost (2-15-3-3)" 'http://[a-km-zA-Z2-9]'
search "Security headers / helmet present (2-15)" 'helmet\(|Content-Security-Policy|Strict-Transport-Security|SECURE_HSTS'
search "Password hashing present (2-2-3-1)" 'bcrypt|argon2|scrypt|pbkdf2|PasswordHasher|BCryptPasswordEncoder'
search "MFA / OTP present (2-2-3-2)" 'totp|otplib|pyotp|webauthn|two[_-]?factor|\bmfa\b|\b2fa\b'
search "Rate limiting present (2-5-3-9)" 'rate[-_]?limit|throttl|slowapi|bucket4j'
search "Hardcoded fallback secrets (2-8-3-2, 1-6-3-5)" 'process\.env\.[A-Z_]*(SECRET|KEY|TOKEN|PASSWORD)[A-Z_]*\s*\|\||getenv\(["'"'"'][A-Z_]*(SECRET|KEY|PASSWORD)[^)]*\)\s*(or|\|\|)\s*["'"'"']|os\.environ\.get\(["'"'"'][A-Z_]*(SECRET|KEY)[^)]*,\s*["'"'"']'
search "Session token in JS-readable storage (2-2)" 'localStorage\.(set|get)Item\(["'"'"'][^"'"'"']*(token|jwt|auth|session)|sessionStorage\.setItem\(["'"'"'][^"'"'"']*(token|jwt)|document\.cookie\s*='
search "Long-lived or missing session expiry (2-2-3-4)" 'expiresIn\s*:\s*["'"'"'][0-9]+(d|w|y)|maxAge\s*[:=]\s*[0-9]{6,}|MAX_AGE\s*=\s*[0-9]+\s*\*'
search "Trusting client-supplied IP (2-5-3-9)" 'x-forwarded-for|x-real-ip|X-Forwarded-For'
search "Security / audit logging present (2-12)" 'audit[_-]?log|security[_-]?log|login (failed|success)|logger\.(warn|info)\(.*(login|auth)'
log ""

# ---------- Repo hygiene ----------
log "== Repo hygiene =="
if f .gitignore; then
  grep -qE '(^|/)\.env' "$PROJECT/.gitignore" && log ".env is gitignored: yes" || log ".env is gitignored: NO (check)"
else log ".gitignore: missing"; fi
ENVF=$(cd "$PROJECT" && ls -a 2>/dev/null | grep -E '^\.env($|\.)' | grep -vE 'example|sample|template' | tr '\n' ' ')
[ -n "$ENVF" ] && log "Env files present in project root: $ENVF (check they are not committed)"
if have git && git -C "$PROJECT" rev-parse >/dev/null 2>&1; then
  TRACKED=$(git -C "$PROJECT" ls-files | grep -E '(^|/)\.env($|\.)' | grep -vE 'example|sample|template' | tr '\n' ' ')
  [ -n "$TRACKED" ] && log "COMMITTED env files: $TRACKED  <-- likely Critical" || log "No committed .env files"
fi
log ""

# ---------- Missing tools ----------
if [ -n "$MISSING" ]; then
  log "== Missing tools (install with the user's approval, then re-run) =="
  for t in $MISSING; do
    case "$t" in
      gitleaks) log "gitleaks:   brew install gitleaks | https://github.com/gitleaks/gitleaks/releases" ;;
      semgrep) log "semgrep:    pip install semgrep  (or brew install semgrep)" ;;
      pip-audit) log "pip-audit:  pip install pip-audit" ;;
      osv-scanner/trivy) log "osv-scanner: go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest | trivy: brew install trivy" ;;
      syft) log "syft:       brew install syft | https://github.com/anchore/syft" ;;
    esac
  done
  log ""
fi

log "Done. Evidence in: $EV"
log "Pattern hits are leads only; confirm each by reading the code before reporting."
