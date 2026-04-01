---
name: secret-scan
description: Scan staged/committed files for 25+ secret patterns (AWS keys, GitHub tokens, Stripe keys, private keys, JWT secrets, .env leaks). Designed to run pre-commit. Outputs per-file findings with line numbers and remediation. Writes critical leaks to security-gate-state.json.
version: 1.0.0
triggers:
  - User runs /prodmasterai secret-scan
  - User says "scan for secrets", "check for leaked keys", "pre-commit check", "credential scan"
  - ship skill triggers this before creating PR
reads:
  - memory/security-gate-state.json
writes:
  - memory/security-gate-state.json
generated: false
generated_from: ""
---

# Secret Scan

Scan source files for hardcoded secrets and credential leaks before they reach version control.

## Process

### 1. Determine Scan Scope

```bash
# Staged files (pre-commit mode — preferred)
git diff --cached --name-only

# All tracked files (full audit mode)
git ls-files

# Untracked files that might be staged later
git ls-files --others --exclude-standard
```

Default: scan staged files + any untracked files not in .gitignore.

### 2. Pattern Library

Scan each file against these pattern categories:

| Category | Patterns |
|---|---|
| AWS | Access Key ID (`AKIA...`), Secret Access Key, session tokens |
| GitHub | PAT (`ghp_...`), App token (`ghs_...`), OAuth token |
| Google | API key (`AIza...`), service account JSON |
| OpenAI | API key (`sk-...`) |
| Stripe | Live key (`sk_live_...`), restricted key (`rk_live_...`) |
| Slack | Bot token (`xoxb-...`), webhook URLs |
| Twilio | Auth token, account SID |
| SendGrid | API key (`SG....`) |
| JWT | Compact serialization with HS256/RS256 signature |
| Private keys | PEM headers for RSA, EC, OPENSSH, DSA |
| Database URLs | Connection strings with embedded credentials |
| Generic | Assignments where key name suggests credential and value is 8+ chars non-trivial |
| .env leaks | Files named `.env`, `.env.local`, `.env.production` staged for commit |

Skip files: `*.lock`, `*.min.js`, `node_modules/`, `.git/`, binary files, test fixtures with obvious dummy values.

### 3. Report Format

For each file with findings:

```
[CRITICAL] src/config.py
  Line 12: AWS Access Key ID (AKIA...)
  Line 13: AWS Secret Access Key
  Action:  git reset HEAD src/config.py && add to .gitignore
           Rotate keys at https://console.aws.amazon.com/iam

[HIGH] .env
  File staged for commit — contains credentials
  Action:  git reset HEAD .env && echo ".env" >> .gitignore

Summary: 2 files with secrets, 3 findings total
```

If nothing found: `Secret scan complete — no credentials detected in staged files.`

### 4. Remediation Steps

For each finding, provide:
1. The exact git command to un-stage the file
2. The exact command to add it to .gitignore
3. Where to rotate the credential (URL if known)
4. How to inject the secret safely (env var, secrets manager)

### 5. Update Security Gate State

Write critical findings to `memory/security-gate-state.json`:

```json
{
  "secret_leaks": [
    {"severity": "critical", "file": "src/config.py", "type": "aws-access-key"},
    {"severity": "high", "file": ".env", "type": "env-file-staged"}
  ],
  "critical_cves": [],
  "tests_failing": false
}
```

Clear `secret_leaks` once the user confirms secrets are removed and credentials rotated.

### 6. Git History Check (optional)

If the user requests `--history` mode:

```bash
git log --all --oneline | head -100
git grep -I "AKIA" $(git log --all --format="%H" | head -50)
```

Report if secrets were committed in recent history. If found, provide BFG Repo Cleaner instructions.

## Rules

- Never print the actual secret value in output — show only the first 6 and last 4 characters masked
- Always provide the exact remediation command, not just advice
- .env files staged for commit are always HIGH severity regardless of content
- Clear gate state once user confirms cleanup — do not leave stale blocks
- Run pattern matching in parallel across files
