# AUDIT playbook: checking an existing project

Read-only. Do not change application code or config. Write only under `compliance/`.

## A. Discover (5–10 minutes of reading, before judging)

1. Read README, docs, `package.json` / `requirements.txt` / `pyproject.toml` / `pom.xml` / `build.gradle` / `go.mod` / `composer.json` / `Gemfile` / `*.csproj` / `pubspec.yaml`.
2. Identify: language and framework, app types (web, API, mobile, AI), entry points, auth library, database/ORM, deployment (Dockerfile, docker-compose, k8s, Terraform, CI files), cloud provider and region.
3. List components in the report's scope section. Note anything not in the repo (WAF, network, SIEM, backups run by ops) — those rows become ❓ unless evidence is provided.
4. Check `git log` size and age if available; note the commit hash you audited.

## B. Collect evidence automatically

Run `bash <skill-dir>/scripts/nca-scan.sh <project-dir>`. It detects the stack, runs whichever scanners are installed, and saves outputs to `<project-dir>/compliance/evidence/`. It never installs anything or modifies the project. If a scanner is missing, it prints the install command; ask the user before installing anything. If you cannot run shell commands, list the commands in the report for the reviewer and mark dependent rows ❓.

**When `gitleaks` is unavailable**, do not simply mark the secrets row ❓ — run this fallback and report what it shows:

```sh
# every historical value assigned to a secret-looking variable, with its length
git log --all -p -S'SECRET=' | grep -E '^\+.*(SECRET|API_KEY|PASSWORD|TOKEN)=' | sort -u
git ls-files | grep -iE '\.env|secret|\.pem$|\.key$'      # tracked secret-bearing files
git check-ignore -v .env                                     # is the local .env actually ignored?
```
Judge the *values*: `your-secret-here`, `change-me-…`, `example` are placeholders (row stays ✅ with this as evidence); anything that looks like real entropy is a Critical finding and needs history rewriting plus key rotation.

**Check the evidence files before citing them.** `quick-checks.txt` collects pattern hits from the whole tree; if a project serves minified or generated assets, a single hit line can be megabytes wide. The scanner caps line width (`NCA_MAX_LINE_CHARS`, default 400) and hits per check (`NCA_MAX_HITS`, default 200) — if you still end up with an evidence file too large to read, note it in the report and keep a filtered copy rather than citing a file nobody can open.

Read the summary it prints, then open the evidence files for details. Count findings by severity for the report's section 5.

## C. Review the code per control

Use the hints below to find relevant code fast, then actually read the code: a grep hit is a lead, not evidence. Record `file:line` for each finding.

| Area / control | Look for | Red flags |
|---|---|---|
| Secrets, 2-8-3-2 | `.env` committed, `API_KEY=`, `password =`, `secret`, `BEGIN PRIVATE KEY`, cloud keys `AKIA` | secrets in code or git history; `.env` not in `.gitignore` |
| Fallback secrets, 2-8-3-2 | `process.env.X_SECRET \|\| '...'`, `os.environ.get('SECRET', '...')` — a default used when the variable is unset | **High-yield check.** A committed default signing key means an unset variable in production signs sessions with a secret that is public in the repo ⇒ admin impersonation. Also check whether anything *stops* production booting without it |
| Token storage, 2-2 | `localStorage.setItem('token'…)`, `sessionStorage`, `document.cookie =` | tokens readable by JavaScript ⇒ any XSS is full session theft. A cookie written from JS can never be `HttpOnly`, and is usually missing `Secure` too — read the exact string, don't assume `SameSite` alone is enough |
| Session lifetime, 2-2-3-4 | `expiresIn: '7d'`, `maxAge`, `MAX_AGE = n * …` | multi-day tokens, no idle timeout, no server-side revocation list. Check admin sessions separately from user sessions |
| Log retention, 2-12-3-5 | TTL indexes, `expiresAt`, `expireAfterSeconds`, retention constants | retention < 12 months. Check each event type separately — decisions and mutations often differ, and only one may be short |
| Proxy trust, 2-5-3-9 | `x-forwarded-for`, `x-real-ip` | taking the *first* value of a client-controlled header as the IP, which defeats per-IP rate limiting. Cross-check the dependency scan for `proxy-addr`-class spoofing CVEs |
| Passwords, 2-2-3-1 | `bcrypt`, `argon2`, `scrypt`, `pbkdf2`, `md5(`, `sha1(`, `createHash` | plain/MD5/SHA-1 hashing; no lockout or rate limit on login |
| MFA, 2-2-3-2 | `totp`, `otp`, `webauthn`, `2fa`, `mfa` | admin login without MFA |
| Authorization, 2-2-3-3 | middleware/guards/decorators (`@PreAuthorize`, `authorize`, `permission`, `role`, `isAdmin`), routes/controllers | routes without auth checks; ownership not checked (IDOR); client-side-only checks |
| Sessions | cookie config (`httpOnly`, `secure`, `sameSite`), `expiresIn`, `maxAge`, session store | long-lived tokens, no idle timeout, JWT `none`/weak secret, tokens in localStorage for sensitive apps |
| Injection, 1-6-3-1 | raw SQL string concatenation, `eval`, `exec`, `child_process`, `Runtime.exec`, `pickle.loads`, `yaml.load`, `innerHTML`, `dangerouslySetInnerHTML`, `|safe` | user input reaching these without validation/encoding |
| Input validation | schema validators (zod, joi, pydantic, class-validator, Bean Validation) | endpoints without validation |
| File upload | `multer`, `upload`, `MultipartFile`, `FileField` | no type/size check, stored in webroot, original filename used |
| CORS / headers, 2-15 | `cors(`, `Access-Control-Allow-Origin`, `helmet`, CSP, HSTS config | `*` with credentials; no security headers |
| TLS, 2-8-3-3 / 2-15-3-3 | `http://` URLs, `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify`, TLS config | TLS verification disabled; HTTP in production |
| Crypto, 2-8-3-1 | `DES`, `RC4`, `ECB`, `MD5`, `SHA1`, `Math.random` for tokens, key sizes | weak algorithms; custom crypto; non-CSPRNG tokens |
| Encryption at rest | DB encryption settings, field-level encryption, storage bucket encryption in IaC | sensitive fields stored plain |
| Logging, 2-12 | logger setup, audit log for login/admin actions, log shipping, retention config | no security events logged; passwords/tokens logged; retention < 12 months |
| Errors / debug, 1-6-3-5 | `DEBUG=True`, `app.debug`, stack traces returned, default credentials, sample admin users | debug in prod config; verbose errors |
| Dependencies, 1-6-3-2 / 2-10 | lockfiles present, scanner output | no lockfile; critical/high CVEs; unmaintained packages |
| Environments, 2-5-3-2 | separate configs for dev/test/prod, seed scripts | prod secrets or data in dev/test |
| Architecture, 2-15-3-2 | Dockerfile / compose / k8s / Terraform: DB exposure, network zones | DB port published publicly; single-tier |
| Rate limiting, 2-5-3-9 | `rate-limit`, `throttle`, gateway config | none on login and public APIs |
| Backups, 2-9 | backup scripts, IaC backup policies, restore docs | none in repo → ❓ (ask ops) |
| CI security, 1-6-3-3 | `.github/workflows`, `.gitlab-ci.yml`, etc. | no SAST / dependency / secret scanning in pipeline |
| Mobile, 2-6 | `SharedPreferences`, `UserDefaults`, `NSAllowsArbitraryLoads`, `android:debuggable`, `usesCleartextTraffic` | sensitive data in plain storage; cleartext allowed |
| AI features | LLM calls, prompt building, tool use | user input concatenated into system prompts; model output executed or rendered unsanitized |
| Personal data (PDPL) | user models with national ID, phone, email, location | no retention/deletion; logged in plain text |

## D. Judge and write

- Use the statuses and honesty rules in SKILL.md Step 3.
- Severity of gaps: Critical (exploitable now, e.g. secrets in repo, SQL injection, auth bypass), High (missing MFA on admin, weak hashing, TLS disabled, critical CVEs), Medium (missing headers, weak logging, no rate limit), Low (hygiene, documentation).
- Say what you did NOT review and why (size, missing infra, no access).
- Keep the report readable: one row per control, details in the remediation section.

## E. After the audit

Summarize for the user and offer FIX mode for Critical and High gaps. Never claim the project "is compliant" — say how many controls are met with evidence.
