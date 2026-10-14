# Developer checklist mapped to NCA requirements

Codes are ECC-2:2024 unless marked NCNICC. For NCNICC projects, cite the matching NCNICC sub-component (same topics) and verify codes against the official text.

## 1. SSDLC and secure coding (ECC 1-6-2, 1-6-3; NCA Secure Coding Standard template)
- [ ] Security requirements written at the design phase; risk assessment early in the project and before release (1-5-3).
- [ ] Secure coding standard followed: OWASP Top 10 mitigations (mandatory for critical systems per NCA template), OWASP ASVS L2 (L3 for critical).
- [ ] Server-side input validation (allow-lists), parameterized queries, output encoding, no eval / dynamic SQL / unsafe deserialization (1-6-3-1).
- [ ] Only up-to-date, trusted, licensed tools, libraries and components; pinned versions, lockfiles, official registries, SBOM (CycloneDX), license check (1-6-3-2).
- [ ] Security testing in CI: SAST (Semgrep/CodeQL), dependency scan (npm audit / pip-audit / Trivy / Dependabot), secret scan (gitleaks), security unit tests for authz (1-6-3-3).
- [ ] Secure integration between applications: mTLS or OAuth2 client credentials, signed webhooks, scoped API keys, timeouts, rate limits (1-6-3-4).
- [ ] Hardening before launch: debug off, default accounts/passwords removed, unused endpoints/ports/services disabled, latest patches (1-6-2-2, 1-6-3-5).
- [ ] Vulnerability assessment and remediation before launch and before changes (1-6-2-1).
- [ ] Source code repository with authentication, version control and logging; access limited to developers and owners (NCA template).
- [ ] Secure, separate environments for development, testing and QA; no production data or secrets in them (NCA template, 2-5-3-2).

## 2. Identity and access (ECC 2-2; NCNICC 2-2-1-2, 2-2-1-4)
- [ ] Passwords: Argon2id (or bcrypt cost ≥ 12), min length 12, breached-password check, throttling/lockout, generic errors (2-2-3-1).
- [ ] MFA for privileged/admin accounts and remote access; for NCNICC, also for external applications. Factors chosen by impact of auth bypass; prefer TOTP/WebAuthn (2-2-3-2).
- [ ] Least privilege, need-to-know, segregation of duties; RBAC/ABAC enforced server-side on every request; deny by default; IDOR checks (2-2-3-3).
- [ ] Privileged access management: separate admin roles, all privileged actions logged, short admin sessions (2-2-3-4).
- [ ] Admin report/export of users and permissions for periodic access review (2-2-3-5).
- [ ] Sessions: Secure, HttpOnly, SameSite cookies; rotate ID on login; idle + absolute timeout (around 5 min idle for critical systems per NCA web standard template); server-side logout; short-lived JWT + refresh rotation if JWT.

## 3. System protection (ECC 2-3)
- [ ] Patch management for runtime, framework, base images, dependencies (2-3-3-3).
- [ ] Clock sync to a trusted NTP source (SASO where applicable); UTC timestamps in logs (2-3-3-4).

## 4. Network (ECC 2-5)
- [ ] Production isolated from dev/test (2-5-3-2).
- [ ] Only required ports/protocols exposed; DB never public (2-5-3-5).
- [ ] DDoS/abuse protection: rate limiting, body size limits, pagination caps, CDN/WAF (2-5-3-9).

## 5. Mobile apps (ECC 2-6, 2-11-3-1)
- [ ] OWASP MASVS; sensitive local data in Keychain / Android Keystore, encrypted; nothing sensitive in logs or plain storage (2-6-3-1).
- [ ] Remote logout / wipe of app data on device loss (2-6-3-3).
- [ ] Certificate pinning and root/jailbreak detection where risk justifies.

## 6. Data protection (ECC 2-7; PDPL/NDMO)
- [ ] Controls applied by classification level; minimize and mask sensitive fields; never log passwords, tokens, national ID, card data (2-7-2).
- [ ] Personal data: consent, purpose limitation, retention, data subject rights, and hosting location confirmed under PDPL / NDMO rules.

## 7. Cryptography (ECC 2-8; NCS)
- [ ] TLS 1.2 minimum, 1.3 preferred, HSTS, strong cipher suites only (2-8-3-3).
- [ ] Sensitive data encrypted at rest (e.g. AES-256-GCM) per classification (2-8-3-3).
- [ ] Algorithms and key sizes per NCS at the required level (MODERATE / ADVANCED); never MD5, SHA-1, DES/3DES, RC4, ECB, custom crypto (2-8-3-1). If NCS-2 is final, use it.
- [ ] Keys and secrets in a secrets manager / KMS / HSM; never in code or git; rotation and revocation process (2-8-3-2).

## 8. Backup (ECC 2-9; NCNICC 2-9-1-2)
- [ ] Automated, encrypted backups of DB and configs, stored separately (2-9-3-1).
- [ ] Documented restore runbook/script; restore tested periodically (2-9-3-2, 2-9-3-3).

## 9. Vulnerability management and pen testing (ECC 2-10, 2-11)
- [ ] CI scanning, CVSS-based severity, critical/high fixed before release, patches tested in non-production first, advisory subscriptions (2-10-3).
- [ ] Internet-facing web, mobile apps and APIs in periodic pen-test scope (2-11-3-1, 2-11-3-2).

## 10. Logging and monitoring (ECC 2-12)
- [ ] Log: login success/failure, MFA, password and permission changes, privileged/admin actions, remote access, sensitive data access (2-12-3-1, 2-12-3-2).
- [ ] Structured JSON logs (user ID, IP, timestamp, action, result, request ID), tamper-protected, no secrets.
- [ ] Shippable to SIEM (stdout/syslog/OpenTelemetry) (2-12-3-3, 2-12-3-4).
- [ ] Security log retention ≥ 12 months (2-12-3-5).

## 11. Incidents (ECC 2-13; NCNICC 2-13-1-2, 2-13-1-3)
- [ ] Alerts on anomalies (brute force, mass export); fast account disable and token revocation.
- [ ] Runbook includes reporting incidents to NCA (entity responsibility).

## 12. External web applications (ECC 2-15; NCA Web Application Protection template)
- [ ] Behind a WAF (2-15-3-1).
- [ ] Multi-tier: at least 3-tier or microservices; web tier in DMZ, app tier in production zone, DB in trusted zone; critical apps isolated (2-15-3-2).
- [ ] HTTPS only, HTTP redirect, HSTS (2-15-3-3).
- [ ] Published secure usage policy for users (2-15-3-4).
- [ ] Authentication strength chosen by impact assessment (2-15-3-5).
- [ ] Headers: CSP, X-Content-Type-Options, frame-ancestors, Referrer-Policy; strict CORS allow-list; CSRF protection; safe file upload (type/size, outside webroot, malware scan).

## 13. Cloud and third parties (ECC 4-1, 4-2; NCNICC component 3)
- [ ] Provider protects data per classification; data returned in usable format at exit (4-2-3-1).
- [ ] Tenant separation with evidence (4-2-3-2; NCNICC 3-2-1-2).
- [ ] Managed SOC with remote access located in KSA (4-1-3-2); NCA-licensed SOC for NCNICC Class A.
- [ ] Hosting location per NDMO rules; for government/CNI prefer providers registered with the regulator.

## 14. AI features (if the app uses AI/LLMs)
- [ ] Check NCA AI Cybersecurity Guidelines status; meanwhile apply OWASP Top 10 for LLM Applications (prompt injection, data leakage, output handling).

## Release gate (all must pass before saying "done")
- [ ] No secrets in code or git history
- [ ] SAST + dependency + secret scans clean of critical/high
- [ ] AuthN/AuthZ tests pass; MFA on admin (and external apps for NCNICC)
- [ ] TLS 1.2+/HSTS, security headers, WAF in plan
- [ ] Sensitive data encrypted at rest with NCS-approved algorithms
- [ ] Security logging live, 12-month retention configured
- [ ] Backups + tested restore
- [ ] Prod separated from dev/test; debug off; defaults removed
- [ ] Pen test scheduled for internet-facing parts
- [ ] Organizational controls listed for the entity
- [ ] `compliance/NCA-COMPLIANCE-REPORT.md` updated: every relevant control has a row, every ✅ has evidence, every ❌/🟡 has a remediation line, scan outputs saved in `compliance/evidence/`
