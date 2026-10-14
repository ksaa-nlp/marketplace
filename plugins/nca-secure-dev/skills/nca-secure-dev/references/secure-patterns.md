# Secure patterns: what to write instead

Concrete replacements for the red flags in `audit-playbook.md`. Use in BUILD mode when writing code, and in FIX mode when remediating. Control codes are ECC-2:2024; cite the matching NCNICC sub-component for private non-CNI entities.

Adapt to the project's existing stack and conventions — do not introduce a new library when the project already has one that does the job.

## Secrets and configuration (2-8-3-2)

| ❌ Avoid | ✅ Do |
|---|---|
| `const key = "sk_live_..."` | read from env / secrets manager at startup; fail fast if absent |
| `.env` committed | `.env` in `.gitignore`; commit `.env.example` with empty values |
| secret in a Docker `ENV` or image layer | runtime secret injection (K8s secret, task-definition secret, Vault/KMS) |
| secret rotated by editing code | rotation through the secrets manager; app re-reads on restart |

Validate config on boot, so a missing secret is a startup failure rather than a silent insecure default:
```ts
// NCA ECC 2-8-3-2: secrets from the environment, never in code
const env = z.object({ DATABASE_URL: z.string().url(), JWT_SECRET: z.string().min(32) }).parse(process.env);
```

If a secret ever reached a commit, treat it as compromised: revoke and rotate it first, then clean history. Removing the line alone is not remediation — record both steps as the evidence.

## Passwords and authentication (2-2-3-1, 2-2-3-2)

- Hash with **Argon2id** (preferred) or bcrypt cost ≥ 12 / scrypt. Never MD5, SHA-1, SHA-256-alone, or a homemade scheme.
- Minimum length 12, no composition rules that fight password managers, check against a breach list.
- Generic error on failed login (`invalid credentials`) — never "user not found" vs "wrong password".
- Rate limit **and** lock out per account and per IP; log every failure (2-12-3-1).
- Timing-safe comparison for tokens, API keys and OTPs (`crypto.timingSafeEqual`, `hmac.compare_digest`).
- MFA (TOTP or WebAuthn) for admin, privileged and remote access — and for external applications under NCNICC.

```python
# NCA ECC 2-2-3-1: Argon2id password hashing
from argon2 import PasswordHasher
ph = PasswordHasher()           # verify with ph.verify(hash, password)
```

## Authorization (2-2-3-3)

- Deny by default: the framework's auth guard is applied globally, and public routes opt out explicitly — not the reverse.
- Check **ownership**, not just role, on every object fetched by an id from the request (IDOR).
- Enforce server-side on every request. A hidden UI button is not a control.
- Scope every query to the caller's tenant/user at the data layer, so a forgotten check cannot leak rows.

```ts
// NCA ECC 2-2-3-3: ownership enforced in the query, not after it
const doc = await db.doc.findFirst({ where: { id, ownerId: session.userId } });
if (!doc) return notFound();   // same response as "exists but not yours"
```

## Sessions

| Setting | Value |
|---|---|
| Cookies | `HttpOnly`, `Secure`, `SameSite=Lax` (or `Strict` for admin) |
| Session id | rotated on login and on privilege change |
| Idle timeout | ~5 minutes for critical systems (NCA web application standard); 15–30 min otherwise |
| Absolute timeout | yes, in addition to idle |
| Logout | invalidated server-side, not just cleared client-side |
| JWT | short-lived access token + rotating refresh token with server-side revocation; never `alg: none`; never a weak shared secret |

Sensitive apps: keep tokens in HttpOnly cookies, not `localStorage`.

## Injection and input handling (1-6-3-1)

| ❌ Avoid | ✅ Do |
|---|---|
| `f"SELECT * FROM users WHERE id = {uid}"` | parameterized query / ORM binding |
| dynamic table or column names from input | allow-list mapping input → fixed identifier |
| `eval`, `exec`, `os.system`, `child_process.exec` with input | avoid entirely; else `execFile` with an argument array and no shell |
| `pickle.loads`, `yaml.load`, PHP `unserialize` on untrusted data | `json.loads`, `yaml.safe_load`, signed payloads |
| `innerHTML`, `dangerouslySetInnerHTML`, `v-html`, `\|safe` | text binding; if HTML is required, sanitize with a maintained sanitizer |
| regex validation only | schema validation server-side (zod, pydantic, class-validator, Bean Validation) with allow-lists |

Validate on the server even when the client validates. Encode at the point of output, per context (HTML, attribute, URL, SQL, shell).

## File upload (2-15)

Check type by content (magic bytes) and not only by extension or `Content-Type`; cap size and count; generate a new random filename; store outside the webroot or in object storage with no execute and no public listing; scan for malware; serve back through an authorized endpoint with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff`.

## Transport and headers (2-8-3-3, 2-15-3-3, 2-15)

- TLS 1.2 minimum, 1.3 preferred; strong cipher suites only; HTTP redirects to HTTPS.
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (add `preload` once verified).
- Never disable verification: no `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify: true`, `NODE_TLS_REJECT_UNAUTHORIZED=0`. If a dev environment needs it, gate it so it cannot be enabled in production.
- CSP without `unsafe-inline` / `unsafe-eval`, plus `frame-ancestors`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`.
- CORS: explicit origin allow-list. `*` with credentials is invalid and insecure.
- CSRF protection on cookie-authenticated state-changing requests (framework token or `SameSite` + origin check).

## Cryptography (2-8-3-1, NCS)

- Symmetric: AES-256-GCM (or ChaCha20-Poly1305) — authenticated encryption, unique nonce per message.
- Hashing: SHA-256 or better. Passwords use a password hash, not a general hash.
- Signatures/KEX: RSA ≥ 3072 or ECDSA/EdDSA on standard curves.
- Never: DES/3DES, RC4, ECB mode, MD5, SHA-1, custom algorithms, unauthenticated CBC.
- Tokens and ids: a CSPRNG (`crypto.randomBytes`, `secrets.token_urlsafe`, `SecureRandom`) — never `Math.random()` or `random.random()`.
- Keys in a KMS/HSM/secrets manager, with documented rotation and revocation.
- Match the NCS level (MODERATE / ADVANCED) to the data classification. If NCS-2 is final, apply it.

## Logging (2-12)

Log security events as structured JSON: login success/failure, MFA events, password and permission changes, privileged actions, remote access, sensitive data access — each with user id, source IP, UTC timestamp, action, result and request id.

Never log: passwords, tokens, session ids, keys, national ID, card data, full personal records. Redact at the logger, not at each call site. Ship to stdout/syslog/OpenTelemetry for SIEM ingestion; retain security logs ≥ 12 months.

## Errors and hardening (1-6-3-5)

Generic error to the client plus a correlation id; full detail to the log only. No stack traces, SQL or framework banners in responses. Debug off in production (`DEBUG=False`, `app.debug = false`, no `android:debuggable`). Remove default accounts, sample data, seed admins and unused endpoints before launch.

## Rate limiting and abuse (2-5-3-9)

Rate limit login, password reset, OTP, search and all public APIs. Cap request body size, pagination page size, file count, and query depth/complexity for GraphQL. Timeouts and retry limits on every outbound call.

## Architecture and deployment (2-5-3-2, 2-5-3-5, 2-15-3-1, 2-15-3-2)

- At least 3-tier (or microservices): web tier in DMZ, app tier in the production zone, database in a trusted zone. Critical apps isolated.
- Database never publicly reachable: no published DB port in `docker-compose`, no `0.0.0.0/0` security-group rule, private subnets only.
- Containers: non-root user, pinned base image digest, read-only filesystem where possible, no secrets in the image, minimal base.
- Production separated from dev/test, with no production data or secrets in lower environments.
- External web apps behind a WAF; record it in the report as ❓ with the owner if it lives outside the repo.

## Mobile (2-6)

Sensitive data in Keychain / Android Keystore (never `UserDefaults`, `SharedPreferences`, plain SQLite or logs). No cleartext traffic (`usesCleartextTraffic="false"`, no `NSAllowsArbitraryLoads`). Certificate pinning and root/jailbreak detection where the risk justifies it. Remote logout / data wipe on device loss (2-6-3-3). Follow OWASP MASVS.

## AI and LLM features

Treat model output as untrusted input: never `eval` it, never render it as raw HTML, never pass it to a shell or SQL unparameterized. Keep user content out of the system prompt's instruction space (separate roles / delimiters). Allow-list and authorize every tool a model can call, and check the caller's permissions inside the tool, not in the prompt. Rate limit and cap token spend per user. Redact secrets and personal data before sending to a model, and confirm the provider's hosting region against NDMO/PDPL rules. Apply OWASP Top 10 for LLM Applications, and check whether the NCA AI Cybersecurity Guidelines are final.

## CI gate (1-6-3-3)

Run on every pull request, failing the build on critical/high: SAST (Semgrep/CodeQL), dependency scan (npm audit / pip-audit / Trivy / Dependabot), secret scan (gitleaks, history included), IaC scan (Trivy/Checkov), SBOM generation (CycloneDX), and automated authorization tests. Pin action/image versions and give the pipeline's own credentials least privilege.
