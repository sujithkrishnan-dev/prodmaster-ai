---
name: cso
description: 14-phase security audit on demand. Scans OWASP Top 10, secrets, dependency CVEs, auth/authz, input validation, output encoding, crypto usage, logging, error handling, third-party libs, environment config, API security, access control, and security headers. Every HIGH/CRITICAL finding requires an exploit path.
version: 1.0.0
triggers:
  - User runs /prodmasterai cso
  - User asks for a security audit
  - User says "audit security", "check for vulnerabilities", "security review"
reads:
  - memory/security-gate-state.json
  - memory/project-context.md
writes:
  - memory/security-gate-state.json
generated: false
generated_from: ""
---

# CSO — Chief Security Officer Audit

Run a 14-phase security audit. Every HIGH and CRITICAL finding must include an exploit path — how an attacker would actually use it, not just that it exists.

## Role

You are a security engineer performing a threat-model-driven audit. Your job is to find real, exploitable issues — not theoretical hygiene. Low-signal findings (missing headers on internal APIs, overly broad CORS on dev configs) are noted but not elevated.

## Process

### Phase Sequence

Run all 14 phases in parallel where findings don't depend on prior phases.

| # | Phase | What to check |
|---|---|---|
| 1 | **Secrets & credentials** | Hardcoded API keys, tokens, passwords, private keys in source/config/env files |
| 2 | **Dependency CVEs** | Run language-appropriate audit. Flag CRITICAL and HIGH CVEs |
| 3 | **Injection** | SQL, command, LDAP, XPath, template injection. String-concatenated queries and shell calls |
| 4 | **Authentication** | Session management, JWT verification, OAuth flows, password storage (bcrypt vs plain/MD5) |
| 5 | **Authorization** | Missing ownership checks, IDOR, privilege escalation paths, role enforcement gaps |
| 6 | **Input validation** | Unvalidated user input reaching sinks (DB, shell, file system, HTML output) |
| 7 | **Output encoding** | XSS: innerHTML assignments, document-write calls, React's dangerously-set-inner-HTML with unescaped data |
| 8 | **Cryptography** | Weak algorithms (MD5/SHA1 for passwords, ECB mode, predictable IVs), short key lengths |
| 9 | **Logging & monitoring** | Sensitive data in logs, missing audit trail for auth events, log injection |
| 10 | **Error handling** | Stack traces exposed to users, verbose errors leaking internals |
| 11 | **Third-party libraries** | Outdated, abandoned, or known-vulnerable packages beyond CVE scanner |
| 12 | **Environment & config** | Debug mode in production, open cloud buckets, permissive CORS, .env committed |
| 13 | **API security** | Missing rate limiting, unauthenticated endpoints, mass assignment, broken object level auth |
| 14 | **Access control** | File/directory permissions, server-side enforcement, admin routes exposed |

### Finding Format

For each finding:

```
[SEVERITY] Phase N — <title>
File: <path>:<line>
Exploit path: <step-by-step how an attacker uses this>
Fix: <specific remediation with code example if short>
```

Severity levels: CRITICAL / HIGH / MEDIUM / LOW / INFO

Only CRITICAL and HIGH require exploit paths. MEDIUM and below: finding + fix is sufficient.

### Scoring

After all 14 phases, produce a security score:

```
Security Score: XX/100

Critical: N  High: N  Medium: N  Low: N  Info: N

Risk areas:
  ████████░░  Secrets (8/10)
  ██████░░░░  Injection (6/10)
  ...
```

Score formula: start at 100, deduct per finding:
- CRITICAL: -15 (capped at -60 total)
- HIGH: -8 (capped at -40 total)
- MEDIUM: -3
- LOW: -1

### Security Gate State

After the audit, write findings to `memory/security-gate-state.json`:

```json
{
  "secret_leaks": [
    {"severity": "critical", "file": "<path>", "type": "<type>"}
  ],
  "critical_cves": ["CVE-XXXX-YYYY"],
  "tests_failing": false
}
```

This enables the stop-quality-gate hook to block session exit until critical issues are resolved.

### Completion Message

```
CSO Audit Complete — Score: XX/100
Critical: N | High: N | Medium: N | Low: N

[CRITICAL findings with exploit paths]
[HIGH findings with exploit paths]

Run /prodmasterai dependency-audit to get CVE fix commands.
Run /prodmasterai secret-scan before committing to catch remaining leaks.
```

## Rules

- Every CRITICAL/HIGH finding requires a realistic exploit path — skip theoretical ones
- Never report a finding without a fix
- Findings without exploit paths are automatically downgraded to INFO
- Do not block on MEDIUM or below — flag only
- Update security-gate-state.json so the stop-quality-gate fires correctly
