---
name: qa-only
description: Findings-only QA — same 11-phase pipeline as qa but no fixes applied. Outputs findings with screenshot evidence where possible. Compares against baseline for regression detection.
version: 1.0.0
triggers:
  - User runs /prodmasterai qa-only
  - User says "just show me the issues", "QA report only", "findings only", "don't fix anything"
reads:
  - memory/project-context.md
  - memory/patterns.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# QA-Only — Findings Report (No Fixes)

Same 11-phase pipeline as `qa` but read-only. No files are modified. Outputs a findings report with evidence.

## Process

### 1. Run All 11 Phases

Same phases as the `qa` skill (test suite, coverage, lint, type check, dead code, error handling, security, performance, accessibility, UX, regression). Run in parallel where independent.

### 2. Collect Evidence

For each finding, attach evidence:
- **Code findings:** file path, line number, code snippet (3-line context)
- **Test failures:** test name, assertion message, stack trace summary
- **Visual findings:** if Playwright or browser plugin is available, capture screenshot

### 3. Baseline Comparison

Read previous QA report from `memory/qa-baseline.json` (if exists).

For each category:
- Score improved: mark with upward arrow
- Score unchanged: no marker
- Score declined: mark with downward arrow + flag as regression

If no baseline: skip comparison, note "First QA run — establishing baseline."

### 4. Report

```
QA Report (findings only — no fixes applied)
=============================================

Findings: N total across M categories

[FUNCTIONALITY] 3 issues
  1. [HIGH] src/api.js:42 — unhandled edge case when input is empty
  2. [MEDIUM] src/utils.js:18 — return value ignored
  3. [LOW] src/config.js:5 — magic number

[TEST COVERAGE] 2 issues
  1. [HIGH] src/auth.js — 0% coverage on critical auth flow
  2. [MEDIUM] src/payments.js — branch at line 22 untested

...

Health Score: XX/100  (baseline: YY/100, delta: +/-Z)
Regressions: N categories declined
```

### 5. Save Baseline

Write current scores to `memory/qa-baseline.json`:
```json
{
  "date": "YYYY-MM-DD",
  "score": 72,
  "categories": {"functionality": 80, "test_coverage": 60, ...},
  "finding_count": 15
}
```

## Rules

- NEVER modify any source file — read-only mode
- NEVER apply fixes or create commits
- Always save baseline after report for future regression detection
- If qa skill is requested instead, redirect — do not run qa-only when user wants fixes
