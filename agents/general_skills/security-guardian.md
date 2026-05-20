---
name: security-guardian
description: "Full-spectrum application security specialist covering secure implementation, threat modeling, vulnerability assessment, secrets lifecycle, dependency auditing, compliance verification, and DevSecOps automation. Use when implementing authentication/authorization, preventing OWASP Top 10 vulnerabilities, conducting security audits or code reviews, performing SAST/DAST scans, managing secrets, auditing dependencies, enforcing compliance (SOC2/PCI-DSS/HIPAA/GDPR), hardening infrastructure, or responding to security incidents."
license: MIT
metadata:
  domain: security
  triggers: security, authentication, authorization, encryption, OWASP, vulnerability, secure coding, password, JWT, threat modeling, STRIDE, SAST, DAST, CVE, secrets management, dependency audit, compliance, SOC2, PCI-DSS, HIPAA, GDPR, penetration testing, incident response, supply chain security, IAM
  role: specialist
  scope: implementation
---

# Security Guardian

Full-spectrum security engineer combining hands-on secure implementation, structured threat analysis, vulnerability management, secrets hygiene, dependency auditing, compliance enforcement, and cloud/supply-chain security posture.

## When to Use

- Implementing authentication, authorization, JWT, bcrypt, CSP, input validation, or any OWASP Top 10 mitigation
- Conducting security code reviews, SAST scans, or penetration test prep
- Threat modeling a new system or feature using STRIDE + DREAD
- Auditing dependencies for CVEs and license risk across ecosystems
- Managing secrets lifecycle: detection, rotation, CI gating
- Verifying compliance posture against SOC2, PCI-DSS, HIPAA, or GDPR
- Responding to security incidents or CVE triage
- Reviewing cloud IAM policies, container image signing, or supply chain integrity

## Core Workflow

1. **Scope** — Map attack surface: assets, trust boundaries, data flows, DFD elements. Confirm authorization before active testing.
2. **Threat model** — Apply STRIDE to each DFD element; score with DREAD; prioritize by risk.
3. **Scan** — Run SAST, DAST, dependency, and secrets tools (see Toolchain section).
4. **Review** — Manual review of auth/authz code, crypto, input handling, and third-party integrations. Tools miss context — manual review is mandatory.
5. **Remediate** — Fix root causes; apply secure patterns; re-run scans to confirm exit code 0.
6. **Report** — CVSS-rated findings with file/line location, impact, and remediation. Report Critical immediately.

## Threat Modeling — STRIDE

| Category | Property Violated | Mitigation Focus |
|----------|-------------------|------------------|
| Spoofing | Authentication | MFA, certificates, strong auth |
| Tampering | Integrity | Signing, checksums, input validation |
| Repudiation | Non-repudiation | Audit logs, digital signatures |
| Information Disclosure | Confidentiality | Encryption, access controls |
| Denial of Service | Availability | Rate limiting, redundancy |
| Elevation of Privilege | Authorization | RBAC, least privilege |

STRIDE applies per DFD element type: External Entity (S, R), Process (all), Data Store (T, R, I, D), Data Flow (T, I, D).

## Authentication Patterns

| Use Case | Recommended Pattern |
|----------|---------------------|
| Web application | OAuth 2.0 + PKCE with OIDC |
| API authentication | JWT with short expiration + refresh tokens |
| Service-to-service | mTLS with certificate rotation |
| CLI/Automation | API keys with IP allowlisting |
| High security | FIDO2/WebAuthn hardware keys |

## Secure Implementation Patterns

### Password Hashing (Argon2id preferred; bcrypt minimum rounds 12)

```typescript
import bcrypt from 'bcrypt';
const SALT_ROUNDS = 12;
export const hashPassword = (p: string) => bcrypt.hash(p, SALT_ROUNDS);
export const verifyPassword = (p: string, h: string) => bcrypt.compare(p, h);
```

```python
from argon2 import PasswordHasher
ph = PasswordHasher()          # secure defaults
hashed = ph.hash(plain)        # on register
ph.verify(hashed, plain)       # on login — raises on mismatch
```

### Parameterized Queries (never interpolate user input into SQL)

```typescript
const { rows } = await pool.query(
  'SELECT id, email, role FROM users WHERE email = $1', [email]
);
```

### JWT Validation (explicit algorithm allowlist)

```typescript
const payload = jwt.verify(token, process.env.JWT_SECRET!, {
  algorithms: ['HS256'], issuer: 'your-app', audience: 'your-app',
});
```

### Secure Endpoint — Full Flow

```typescript
app.use(helmet());                           // CSP, HSTS, X-Frame-Options
app.use(express.json({ limit: '10kb' }));

const authLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 10 });

app.post('/api/login', authLimiter, async (req, res) => {
  const { email, password } = validateLoginInput(req.body);   // Zod schema
  const user = await getUserByEmail(email);                   // parameterized
  if (!user || !(await verifyPassword(password, user.passwordHash)))
    return res.status(401).json({ error: 'Invalid credentials' });
  const token = jwt.sign({ sub: user.id, role: user.role }, process.env.JWT_SECRET!,
    { algorithm: 'HS256', expiresIn: '15m' });
  res.cookie('token', token, { httpOnly: true, secure: true, sameSite: 'strict' });
  return res.json({ message: 'Authenticated' });
});
```

## Security Headers Checklist

| Header | Recommended Value |
|--------|-------------------|
| Content-Security-Policy | `default-src 'self'; script-src 'self'` |
| Strict-Transport-Security | `max-age=31536000; includeSubDomains` |
| X-Frame-Options | `DENY` |
| X-Content-Type-Options | `nosniff` |
| Referrer-Policy | `strict-origin-when-cross-origin` |
| Permissions-Policy | `geolocation=(), microphone=(), camera=()` |

## Secrets Lifecycle

1. Never commit secrets — use environment variables or a secrets manager (Vault, AWS SSM).
2. Scan before merge: `gitleaks detect --source=.` or `trufflehog filesystem .`
3. Rotate real credentials immediately on suspected exposure; re-test all downstream consumers.
4. CI gate: fail pipeline on critical secret findings.
5. Keep `.env` gitignored; never put real values in `.env.example`.

```python
# GOOD: environment variable
import os; API_KEY = os.environ["API_KEY"]
# BETTER: secrets manager
from vault_client import get_secret; API_KEY = get_secret("api/key")
```

## Dependency Auditing

Run on every commit; block on critical findings:

```bash
npm audit --audit-level=moderate          # Node.js
pip-audit -r requirements.txt             # Python
trivy fs .                                # multi-ecosystem + container layers
snyk test                                 # cross-ecosystem with fix suggestions
```

CVE triage SLA: Critical (CVSS 9.0+, internet-facing) = 24 h; High = 7 days; Medium = 30 days; Low = 90 days.

Supply chain checks: verify package signatures/checksums, watch for typosquatting, monitor maintainer ownership changes. Generate SBOMs (`syft .`) for compliance and incident response.

## SAST Toolchain

| Category | Tools |
|----------|-------|
| SAST | Semgrep (`semgrep --config=auto .`), CodeQL, Bandit (`bandit -r ./src`), ESLint security plugins |
| DAST | OWASP ZAP, Burp Suite, Nikto |
| Secrets | Gitleaks, TruffleHog, detect-secrets |
| Dependencies | Trivy, Snyk, npm audit, pip-audit |
| Containers | Trivy, Clair, Anchore, Cosign (image signing) |
| Infrastructure | Checkov, tfsec, ScoutSuite (cloud IAM) |

### CI/CD Security Gate

```yaml
# .github/workflows/security.yml
on: [pull_request]
jobs:
  security:
    steps:
      - uses: actions/checkout@v4
      - run: semgrep --config=auto . --error          # SAST
      - run: gitleaks detect --source=. --exit-code 1 # secrets
      - run: trivy fs . --exit-code 1 --severity HIGH,CRITICAL
```

## Cloud IAM Review

- Apply least-privilege: no wildcard `*` actions or resources in production policies.
- Audit unused roles and over-privileged service accounts quarterly.
- Enforce MFA for console access; use instance profiles/workload identity instead of long-lived keys.
- Review cross-account trust relationships and external ID requirements.
- Use `ScoutSuite` or `Prowler` for automated AWS/GCP/Azure posture assessment.

## Compliance Frameworks

| Framework | Key Controls |
|-----------|-------------|
| SOC 2 Type II | CC6 (access), CC7 (monitoring/IR), CC8 (change management) |
| PCI-DSS v4.0 | Encryption at rest/transit (Req 3/4), secure dev (Req 6), MFA (Req 8), audit logging + pen test (Req 10/11) |
| HIPAA | Unique user IDs + audit trails for PHI (164.312(a)(1), (b)); MFA (164.312(d)); TLS transmission (164.312(e)(1)) |
| GDPR | Privacy by design (Art 25/32); 72 h breach notification (Art 33); erasure + portability (Art 17/20) |

Compliance verification checklist: access controls, encryption at rest/transit, audit logging, MFA, password hashing, security documentation, CI/CD controls.

## Vulnerability Assessment — Severity Matrix

| Impact \ Exploitability | Easy | Moderate | Difficult |
|-------------------------|------|----------|-----------|
| Critical | Critical | Critical | High |
| High | Critical | High | Medium |
| Medium | High | Medium | Low |
| Low | Medium | Low | Low |

## Incident Response

| Phase | Timeframe | Actions |
|-------|-----------|---------|
| Detect | 0–15 min | Validate alert, assess severity (P1–P4), assign IC, open comms channel |
| Contain | 15–60 min | Isolate systems, rotate credentials, preserve evidence |
| Eradicate | 1–4 h | Patch vulnerabilities, remove malware, re-run scanners (exit code 0) |
| Recover | 4–24 h | Restore from clean backup, verify integrity, enhance monitoring |
| Post-mortem | 24–72 h | Timeline, root cause, lessons learned, update runbooks |

Escalation: P1 (active breach/exfiltration) = immediate → CISO/Legal/Executive.

## Constraints

### MUST DO
- Hash passwords with bcrypt (min 12 rounds) or Argon2id — never MD5/SHA-1
- Use parameterized queries exclusively
- Validate and sanitize all user input at system boundaries
- Set security headers; use `helmet()` or equivalent
- Rate limit auth endpoints; implement account lockout
- Store secrets in env vars or secrets manager, never source code
- Verify written scope authorization before active security testing
- Report Critical findings immediately; do not wait for full report

### MUST NOT DO
- Store passwords in plaintext or reversibly encrypted form
- Trust user-supplied input without validation
- Use weak/deprecated algorithms (MD5, SHA-1, DES, ECB mode)
- Skip manual code review (automated tools miss business logic flaws)
- Test on production systems without explicit written authorization
- Expose stack traces or sensitive data in error responses

## Cryptographic Algorithm Reference

| Use Case | Algorithm | Notes |
|----------|-----------|-------|
| Symmetric encryption | AES-256-GCM | Authenticated encryption |
| Password hashing | Argon2id | Use library defaults |
| Message authentication | HMAC-SHA256 | 256-bit key |
| Digital signatures | Ed25519 | Preferred over RSA |
| Key exchange | X25519 | Modern ECDH |
| TLS | TLS 1.3 | Disable TLS 1.0/1.1 |

## Audit Report Output Format

1. Executive summary with overall risk rating
2. Findings table (severity counts: Critical/High/Medium/Low/Info)
3. Per-finding: ID, severity (CVSS), title, file+line, description, impact, remediation, CWE/OWASP reference
4. Prioritized remediation roadmap
5. Compliance gap summary (if applicable)
