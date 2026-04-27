---
name: dependency-audit
description: Audit project dependencies for known CVEs. Auto-detects project type (npm, pip, bundler, go modules) and runs the appropriate audit tool. Reports CVEs by severity with fix commands. Writes critical CVEs to security-gate-state.json so the stop-quality-gate blocks session exit until resolved.
version: 1.0.1
triggers:
  - User runs /prodmasterai dependency-audit
  - User says "check dependencies", "audit packages", "check for CVEs", "vulnerable packages"
  - cso skill triggers this as Phase 2
reads:
  - memory/security-gate-state.json
writes:
  - memory/security-gate-state.json
generated: false
generated_from: ""
---

# Dependency Audit

Scan project dependencies for known security vulnerabilities (CVEs).

## Process

### 1. Detect Project Type

Check for these files in parallel to identify which ecosystems are present:

| File | Ecosystem | Audit command |
|---|---|---|
| `package.json` or `package-lock.json` | Node.js | `npm audit --json` |
| `yarn.lock` | Node.js (Yarn) | `yarn audit --json` |
| `requirements.txt` or `Pipfile.lock` | Python | `pip-audit --format json` or `safety check --json` |
| `pyproject.toml` | Python | `pip-audit --format json` |
| `Gemfile.lock` | Ruby | `bundle audit check --format json` |
| `go.sum` or `go.mod` | Go | `go list -json -m all` + `govulncheck ./...` |
| `Cargo.lock` | Rust | `cargo audit --json` |
| `pom.xml` | Java (Maven) | `mvn dependency-check:check` |

Run detected ecosystem audits in **parallel**.

### 2. Parse Results

For each ecosystem, parse the audit output and extract:
- CVE ID
- Package name and affected version
- Severity (CRITICAL / HIGH / MEDIUM / LOW)
- Fixed version (if available)

If audit tool is not installed, fall back to checking the lockfile against the OSV database or note the gap clearly.

### 3. Report

```
Dependency Audit — <project name>
==================================
Scanned: <N> packages across <M> ecosystems
Found: C critical, H high, M medium, L low

CRITICAL
  <package>@<version>  CVE-XXXX-YYYY  <description>
  Fix: npm update <package>@<fixed_version>

HIGH
  <package>@<version>  CVE-XXXX-YYYY  <description>
  Fix: pip install "<package>>=<fixed_version>"

MEDIUM / LOW
  <count> lower-severity issues (run with --all to see them)
```

If no vulnerabilities: `All dependencies clean. No known CVEs found.`

### 4. Update Security Gate State

Read `memory/security-gate-state.json` (create if missing). Merge in critical CVEs found:

```json
{
  "secret_leaks": [],
  "critical_cves": ["CVE-2024-XXXX", "CVE-2024-YYYY"],
  "tests_failing": false
}
```

This causes the stop-quality-gate hook to block session exit until CRITICAL CVEs are fixed.

Clear `critical_cves` from the gate state once all CRITICAL issues are resolved.

### 5. Fix Guidance

For each CRITICAL and HIGH finding, provide the exact command to update:

```bash
# npm
npm update <package>

# pip
pip install "<package>>=<fixed_version>"

# bundler
bundle update <gem>

# go
go get <module>@<fixed_version>
```

If no fix is available (no patched version exists): recommend pinning to the last safe version and note the risk.

Next: `/prodmasterai cso` for full security audit | `/prodmasterai ship` once all CRITICAL CVEs are resolved

## Rules

- Never silence audit output — if the tool errors, report the error
- CRITICAL CVEs must be added to security-gate-state.json
- Clear the gate state after the user confirms fixes are applied
- If no audit tool is installed, tell the user exactly how to install it
- Run all ecosystem audits in parallel — never serialize
