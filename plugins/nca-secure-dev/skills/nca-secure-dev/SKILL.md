---
name: nca-secure-dev
description: يطبّق ويدقّق متطلبات الهيئة الوطنية للأمن السيبراني (NCA) السارية — ECC-2:2024 و NCNICC-1:2025 و NCS-2:2025 ونموذجَي التطوير الآمن وحماية تطبيقات الويب — على أي تطبيق أو واجهة برمجية أو موقع أو تطبيق جوال. وضعان: BUILD يطبّق المتطلبات أثناء كتابة الكود، و AUDIT يفحص مشروعًا قائمًا بلا تعديل أي سطر. كلاهما يُخرج تقريرًا عربيًّا في compliance/NCA-COMPLIANCE-REPORT.md لمراجع الأمن السيبراني. استعمله في كل مهمة تطوير أو مراجعة أو نشر، وعند طلب «افحص المشروع» أو «راجع الامتثال» أو «دقق أمنيًّا» أو «تقييم امتثال» أو "audit compliance" أو "security review"، حتى إن لم تُذكر الهيئة. لا تستعمله لأسئلة غير برمجية.
argument-hint: "[audit|build|fix] [نطاق اختياري]"
---

# NCA Secure Development, Audit + Compliance Report

You (Claude, Codex or any coding agent) work on software that must comply with the Saudi National Cybersecurity Authority (NCA).

## Choose the mode first

| Mode | When | What you do |
|---|---|---|
| **BUILD** | Writing new code or features | Apply requirements while coding (Steps 0–2), then update the report (Step 3) |
| **AUDIT** | User asks to check / scan / audit / review an existing project, or you are dropped into a codebase you did not write and asked about compliance | Read-only assessment following `references/audit-playbook.md`, then write the report (Step 3) |
| **FIX** | After an audit, the user asks to fix gaps | Fix in priority order (Critical first) using BUILD rules and `references/secure-patterns.md`, re-check each fixed control, update report rows and change log |

If the request is ambiguous (e.g. "check my project"), use AUDIT. AUDIT is **read-only**: do not modify application code or config; only create files under `compliance/`. Offer FIX at the end.

In every mode: write the report in Arabic (control codes and technical terms in English) unless the user asks otherwise. Talk to the user in their language.

## Step 0: Check for newer NCA editions (when web access is available)

Search nca.gov.sa (news + regulatory documents) for editions newer than those in `references/frameworks.md`. If found, tell the user, follow the newer edition, and record it in the report's "frameworks applied" section. The Arabic text of NCA documents is legally binding.

## Step 1: Scope (ask once, in a single message, only what is unknown)

Determine and record in the report:

| Item | Options |
|---|---|
| Entity type | Government / affiliated / CNI → **ECC-2:2024** · Private non-CNI → **NCNICC-1:2025** (Class A large, Class B SME) · Unknown → apply ECC-2:2024 technical baseline and say so |
| Data classification | Public / Internal / Sensitive / Secret (default: Sensitive) |
| Critical system? | Yes → also CSCC, ASVS L3, stricter session/architecture rules |
| Hosting | Cloud (which provider, which region) / on-prem → CCC + NDMO hosting rules if cloud |
| Personal data? | Yes → PDPL / NDMO items in the report |
| App types | Web / API / Mobile / AI features |

If the user is not available to answer, use the defaults, and list every assumption in the report's "Assumptions" section.

In AUDIT mode, infer as much of the scope as possible from the code and config first (README, deployment files, env examples, cloud IaC), then ask only what remains unknown.

## Step 2 (AUDIT mode): Assess the existing project

Follow `references/audit-playbook.md`: discover the stack and components, run `scripts/nca-scan.sh` (or the equivalent commands manually) to collect evidence, review the code against every relevant item in `references/dev-checklist.md` using the playbook's per-control search hints (`references/secure-patterns.md` gives the ❌/✅ pattern per area, and the fix to recommend), then go to Step 3. For large codebases, review security-critical areas first (auth, sessions, access control, crypto, input handling, file upload, logging, config, infra) and state in the report which parts were reviewed and which were not.

## Step 2 (BUILD mode): While coding

Read `references/dev-checklist.md` and apply every item that is relevant to what you are building. Use `references/secure-patterns.md` for the concrete pattern to write in place of an insecure one. Never skip:

- SSDLC: security requirements at design, security tests in CI, dev/test separated from production.
- OWASP Top 10 + ASVS L2 (L3 for critical); MASVS for mobile; OWASP LLM Top 10 for AI features.
- Trusted, licensed, current dependencies; lockfiles; SBOM; SAST + dependency + secret scanning.
- MFA for admin/privileged and remote access (and external apps under NCNICC); least privilege; deny by default; server-side authorization on every request.
- Session timeout and idle lockout (around 5 min for critical systems).
- TLS 1.2+ (prefer 1.3), HSTS; encryption at rest per classification with NCS-approved algorithms; no secrets in code.
- Security event logging, SIEM-ready, retention ≥ 12 months.
- External web apps: WAF, multi-tier architecture, DB never public, HTTPS only.
- Backups with a tested restore procedure.

Rules of conduct:
- Never silently weaken security (disable TLS verification, wildcard CORS, hardcoded secrets, debug in prod, skip scans). If the user insists, warn once citing the control, do it only if they confirm, and record it in the report as ❌ with "user-approved exception" so the reviewer sees it.
- When you add or change security-relevant code, note the control code in a short code comment only where it helps a reviewer find it (e.g. `// NCA ECC 2-2-3-2: MFA for admin`). Do not spam comments.
- Do not invent control codes. If unsure, cite the subdomain name only and mark the code "to verify".

## Step 3: Produce / update the compliance report

Create the report from `assets/compliance-report-template.md` at `compliance/NCA-COMPLIANCE-REPORT.md`. Keep the template's `<div dir="rtl" align="right">` opening block and its closing `</div>` — the report is Arabic and must render right-to-left. The blank line after the opening tag is required: a CommonMark HTML block ends at the first blank line, so headings and tables after it are still parsed as Markdown while the direction applies to the rendered output. Do not convert the tables to raw HTML to achieve RTL, and do not insert bidi control characters (RLM/LRM) into the text — they make the source unreadable and are not needed once the wrapper is present. Note for the user that the wrapper affects *rendered* output (GitHub, VS Code preview, PDF export); the raw file in a plain editor still reads left-to-right unless that editor supports RTL itself. Set the report's "assessment type" field to BUILD or AUDIT. Update it:
- BUILD: after each feature or security-relevant change (affected rows + change log), and in full before any release;
- AUDIT: once, in full, at the end of the assessment; if a previous report exists, keep its reviewer columns and change log, and add a new change-log entry;
- FIX: after each fix, change the row status with new evidence and add a change-log entry;
- whenever the user says "جهز ملف الالتزام" / "compliance report" / "review".

### How to fill it — honesty rules (the reviewer depends on these)

1. **Evidence or no ✅.** A row is ✅ only if you can cite concrete evidence the reviewer can open: `path/to/file.ts:42`, a config file, a CI job, a test name, or scan output saved in `compliance/evidence/`. No evidence → 🟡 or ❓.
2. **Run the checks, don't guess.** Where tools exist in the environment, run them and save outputs to `compliance/evidence/` (e.g. `npm audit --json`, `pip-audit -f json`, `semgrep --config auto --json`, `gitleaks detect --report-path ...`, `trivy fs`). If a tool can't run, write the exact command for the reviewer and mark the row ❓.
3. **Use exactly these statuses:**
   - ✅ ملتزم (Met) — implemented, with evidence
   - 🟡 جزئي (Partial) — partly implemented; say what is missing
   - ❌ غير ملتزم (Not met) — not implemented, or a user-approved exception
   - ❓ يحتاج تحقق (Needs verification) — cannot be verified from code (e.g. WAF in infra not in repo)
   - 🏢 مسؤولية الجهة (Entity responsibility) — organizational control outside code (staffing, SOC contract, policies, physical security, NCA incident reporting)
   - ➖ لا ينطبق (N/A) — with the reason
4. **Every ❌ and 🟡 gets a remediation line**: what to do, priority (Critical / High / Medium / Low), suggested owner (Dev / DevOps / Cybersecurity / Management).
5. **Give the reviewer a way to verify** each ✅: a file to open, a command to run, or a test to execute.
6. **Never claim certification.** Only the entity's own assessment or the NCA determines compliance, so the report never states or implies that the project *is* compliant or certified — it reports how many controls are met with evidence. Do not add an AI-authorship banner or a self-assessment disclaimer to the top of the report; the preparer row in the approval section already records who produced it, and the entity owns how it presents the document to its reviewers.
7. Cover every relevant control from the checklist, not only the ones that pass. Missing rows are worse than ❌ rows.
8. **Count the statuses from the finished table, never by hand.** The summary in section 2 is the first thing a reviewer reads, and a mismatch between it and the detail rows discredits the whole report. After writing the tables, recount and correct the summary:
   ```sh
   awk '/^## 3\. /,/^## 4\. /' compliance/NCA-COMPLIANCE-REPORT.md \
     | grep -oE '✅|🟡|❌|❓|🏢|➖' | sort | uniq -c
   ```
9. **In AUDIT mode, fill the "what was not reviewed" section.** An audit that silently omits the riskiest component reads as a clean bill of health. Name what you skipped and why — especially anything that executes third-party or user-supplied code, which is usually the single most dangerous surface and the easiest to leave out.
10. **Never report a hit from an automated scan you did not open.** A grep hit is a lead. Before a row cites it, read the file at that line: a `dangerouslySetInnerHTML` on a static string and one on user input are the same hit and different verdicts.

## Step 4: Tell the user

After writing or updating the report, give the user a short summary: counts per status, the top critical gaps, and the report path. Do not paste the whole report into the chat. In AUDIT mode, end by offering FIX mode for the Critical and High gaps.
