---
name: cso
description: Security audit — 14-phase infrastructure-first audit covering architecture through STRIDE threat modeling. Two modes (daily/comprehensive). Every finding requires a concrete exploit path, not theoretical risk. Covers supply chain, CI/CD, LLM/AI security, and OWASP Top 10.
version: 1.1.0
argument-hint: "[--daily | --comprehensive]"
effort: high
allowed-tools: Read, Grep, Glob, Bash, WebFetch, WebSearch
paths:
  - "src/**/*.{js,ts,py,go,rb,java}"
  - "**/*.env*"
  - ".github/**"
  - "docker*"
  - "Dockerfile*"
triggers:
  - /prodmasterai cso
  - security audit
  - run a security audit
  - check for vulnerabilities
  - security check
  - threat model this
  - OWASP check
  - pentest review
reads:
  - memory/security-gate-state.json
  - memory/project-context.md
  - memory/mistakes.md
writes:
  - memory/security-gate-state.json
  - memory/cso-log.md
  - memory/project-context.md
generated: false
generated_from: ""
---

# CSO (Security Audit)

14-phase infrastructure-first security audit. Every finding must include a concrete exploit path — no theoretical risks without evidence. Two modes: daily (high-signal only) and comprehensive (full depth, monthly cadence).

---

## Audit Modes

| Mode | Confidence threshold | When to use |
|---|---|---|
| **daily** | 8/10 — include only findings where exploit path is clear and high-confidence | Pre-merge, PR reviews, CI gate |
| **comprehensive** | 2/10 — include all plausible findings for full analysis | Monthly deep scan, pre-release, new feature with security surface |

Default: `daily`. Use `comprehensive` when explicitly requested or when the diff introduces auth, payments, file handling, or LLM integration.

**Attestation rule (applies to all modes):** Every finding must include:
- Exact file path and line number
- Concrete exploit steps (numbered, reproducible)
- Impact statement (what an attacker gains)

Findings without all three fields are invalid and must be dropped.

---

## Phase 1 — Architecture Review

Map the system's trust boundaries:

1. Identify all entry points: HTTP endpoints, CLI args, file inputs, queue consumers, webhooks.
2. Identify all trust boundaries: where user input crosses into privileged operations (DB writes, file system, external API calls, LLM prompts).
3. Identify all data stores: which hold secrets, PII, or credentials.
4. Draw a simple trust boundary diagram (ASCII is fine):

```
[User] --> [API Gateway] --> [App Server] --> [DB]
                                          --> [LLM API]
                                          --> [File Store]
```

Record boundary crossings as the primary audit surface for subsequent phases.

---

## Phase 2 — Attack Surface Enumeration

List every externally-reachable surface:

- All HTTP routes (method + path + auth requirement)
- All WebSocket endpoints
- All file upload/download endpoints
- All admin or internal-only routes (check for auth bypass risk)
- All third-party callbacks/webhooks

For each surface: record `authenticated: true/false`, `rate_limited: true/false`, `input_validated: true/false`.

Unauthenticated surfaces with write capability or file access are high-priority audit targets.

---

## Phase 3 — Secrets Archaeology

Search the codebase and git history for leaked secrets:

1. Scan current source: grep for patterns matching API keys, tokens, passwords, connection strings. Check: `*.env*`, `*.config.*`, hardcoded strings in source files.
2. Scan git history: `git log --all --full-history -- '*.env'` and `git log -p | grep -E "(password|secret|token|key)\s*="`.
3. Check CI/CD config files for secrets in plain text (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`).
4. Check `package-lock.json` / `yarn.lock` / `Cargo.lock` for packages with known credential-harvesting behavior.

For each finding: record file, line, secret type, whether it is still valid (if determinable), and remediation (rotate + add to `.gitignore`).

---

## Phase 4 — Supply Chain Audit

Go beyond `npm audit` / `pip check`:

1. Run standard vulnerability scanner: `npm audit --audit-level=high`, `pip-audit`, `cargo audit`, or `govulncheck`.
2. Check install scripts: scan `package.json` `preinstall`/`postinstall` scripts and any `setup.py` for network calls or shell commands.
3. Check lockfile integrity: verify `package-lock.json` or `yarn.lock` hashes match expected registry values (flag any mismatches as possible lockfile poisoning).
4. Check for typosquatting: scan direct dependencies for names that are one character away from popular packages.
5. Check for dependency confusion: if the org has internal packages, verify they are scoped correctly and cannot be shadowed by public registry packages.

---

## Phase 5 — CI/CD Security

Audit the build and deployment pipeline:

1. Check that secrets are injected via environment variables, not hardcoded in workflow files.
2. Check for `pull_request_target` triggers combined with code checkout — classic privilege escalation vector in GitHub Actions.
3. Check that third-party GitHub Actions are pinned to commit SHAs, not mutable tags.
4. Check deployment workflows for manual approval gates on production environments.
5. Check that branch protections prevent direct push to main/master.

---

## Phase 6 — Infrastructure Review

Review infrastructure configuration if present (`terraform/`, `pulumi/`, `cdk/`, `k8s/`):

1. Storage buckets: public read/write disabled by default?
2. Network: security groups/firewall rules with `0.0.0.0/0` ingress on non-HTTP ports?
3. IAM/RBAC: least-privilege? Any wildcard resource permissions (`*`)?
4. Encryption: data at rest and in transit encrypted?
5. Logging: audit logs enabled on sensitive operations?

---

## Phase 7 — Webhook Security

For any webhook receivers:

1. Is the webhook payload signature verified before processing?
2. Is the verification done with a constant-time comparison (not `===`)?
3. Is the webhook endpoint rate-limited?
4. Is the webhook payload size bounded (protection against payload bombs)?

---

## Phase 8 — LLM and AI Security

*Skip if no LLM integration detected.*

1. **Prompt injection:** is user input included in system prompts or tool call results without sanitization? Test: can a user inject `Ignore all previous instructions and...`?
2. **Indirect prompt injection:** does the app fetch external content (URLs, emails, documents) and pass it to the LLM? Flag as high-risk surface.
3. **LLM output trust:** is LLM-generated content used in database queries, file writes, shell invocations, or rendered as HTML without escaping?
4. **Model exfiltration:** could an attacker extract the system prompt via clever input? Check for prompt disclosure patterns.
5. **Token budget attacks:** is there a max token guard on user-supplied input before it reaches the LLM?
6. **Tool call authorization:** if the LLM has tools (function calling, MCP), are tool actions authorized against the original user's permissions, not the LLM's?

---

## Phase 9 — Skill Supply Chain (Plugin/Skill Security)

*Applies when auditing a Claude Code plugin or skill-based system.*

Scan skill files for malicious patterns:

1. Skills that instruct the model to exfiltrate data (write to external URLs, send to unexpected endpoints).
2. Skills that override safety rules or instruct the model to bypass permissions.
3. Skills that reference external URLs in their body (could trigger SSRF via WebFetch).
4. Skills with `writes:` declarations to sensitive paths (`.claude/settings.json`, `~/.ssh/`).
5. Hook files that run shell commands with user-controlled input without sanitization.

---

## Phase 10 — OWASP Top 10

Check the codebase against the OWASP Top 10 (2021):

| # | Category | Key checks |
|---|---|---|
| A01 | Broken Access Control | Missing auth on routes, IDOR, path traversal |
| A02 | Cryptographic Failures | Weak algorithms (MD5/SHA1 for passwords), unencrypted PII in transit |
| A03 | Injection | SQL, command, LDAP, XPath injection |
| A04 | Insecure Design | Missing rate limiting, no abuse case modeling |
| A05 | Security Misconfiguration | Default creds, directory listing, verbose errors in prod |
| A06 | Vulnerable Components | Supply chain findings from Phase 4 |
| A07 | Auth Failures | Weak passwords, missing MFA, session fixation |
| A08 | Software Integrity | Phase 4 + Phase 5 findings |
| A09 | Logging Failures | Missing security event logging, logs contain secrets |
| A10 | SSRF | User-controlled URLs fetched server-side without allowlist |

For each category: `pass`, `warning`, or `finding` with evidence.

---

## Phase 11 — STRIDE Threat Modeling

For the top 3 trust boundary crossings identified in Phase 1, apply STRIDE:

| Threat | Question |
|---|---|
| **S**poofing | Can an attacker impersonate a legitimate user or service at this boundary? |
| **T**ampering | Can an attacker modify data in transit or at rest across this boundary? |
| **R**epudiation | Can an attacker deny having performed an action that crossed this boundary? |
| **I**nformation Disclosure | Can an attacker read data they should not have access to across this boundary? |
| **D**enial of Service | Can an attacker exhaust resources at this boundary to block legitimate users? |
| **E**levation of Privilege | Can an attacker gain higher permissions by crossing this boundary in an unexpected way? |

For each STRIDE threat: `mitigated`, `partial`, or `unmitigated` with evidence.

---

## Phase 12 — Data Classification

Identify all PII and sensitive data in the system:

1. List all fields that store or process: names, emails, addresses, payment data, health data, government IDs.
2. For each: is it encrypted at rest? Is access logged? Is it included in backups? Can it be deleted on request (GDPR/CCPA right to erasure)?
3. Check for PII leaking into logs, error messages, or analytics.

---

## Phase 13 — Filtering and Rate Limiting

1. Is there a rate limiter on all authentication endpoints (login, password reset, MFA)?
2. Is there a global rate limiter per IP or user on the API?
3. Is file upload bounded by size and type?
4. Is there input length validation on all text fields?
5. Is there output encoding for all user-supplied content rendered in HTML?

---

## Phase 14 — Report

```
== Security Audit: <feature or repo> ==
Mode:       <daily | comprehensive>
Phases:     14/14 complete

Critical findings:  N
High findings:      N
Medium findings:    N
Low findings:       N

━━━ Critical ━━━
[SEC-001] <title>
  Phase:   <phase number>
  File:    <path>:<line>
  Exploit: <numbered steps>
  Impact:  <what attacker gains>
  Fix:     <one-line remediation>

[SEC-002] ...

━━━ High ━━━
[SEC-003] ...

━━━ Summary by Phase ━━━
Phase 1  Architecture      <pass | N findings>
Phase 2  Attack Surface    <pass | N findings>
Phase 3  Secrets           <pass | N findings>
Phase 4  Supply Chain      <pass | N findings>
Phase 5  CI/CD             <pass | N findings>
Phase 6  Infrastructure    <pass | N findings>
Phase 7  Webhooks          <pass | N findings>
Phase 8  LLM/AI            <pass | N findings | skipped>
Phase 9  Skill Supply Chain <pass | N findings | skipped>
Phase 10 OWASP Top 10      <pass | N findings>
Phase 11 STRIDE            <N unmitigated>
Phase 12 Data Class.       <pass | N findings>
Phase 13 Filtering         <pass | N findings>

Verdict: <SECURE | REVIEW REQUIRED | CRITICAL ISSUES — DO NOT SHIP>

Next:
  <"No critical findings — safe to ship" | "Fix N critical issues before next deploy" | "Run /prodmasterai cso --comprehensive for full depth scan">
```

Append to `memory/cso-log.md`:

```yaml
---
date: <YYYY-MM-DD>
feature: <active_feature or "general">
mode: daily | comprehensive
critical_count: N
high_count: N
verdict: SECURE | REVIEW REQUIRED | CRITICAL ISSUES
session_id: <session_id>
---
```

---

## Integration with Auto-Pilot

When `autonomous_mode: true`:
- Default mode: `daily`
- If diff introduces auth, payments, file handling, or LLM integration: escalate to `comprehensive`
- If verdict is CRITICAL ISSUES: park auto-pilot, all findings appended as blockers
- If verdict is REVIEW REQUIRED: log findings, continue (judgment calls logged as decisions)
- If verdict is SECURE: continue to deploy phase

---

## Rules

- Every finding requires file path + line number + concrete exploit path — no exceptions
- Theoretical risks without exploit path are dropped (do not log as low — drop entirely)
- Phase 3 (secrets archaeology) must check git history, not just current HEAD
- Comprehensive mode runs all 14 phases; daily mode may skip Phase 6 (infra) and Phase 12 (data classification) if no changes detected in those areas
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
- After audit, update `memory/security-gate-state.json` with critical findings so stop-quality-gate hook can block session exit
