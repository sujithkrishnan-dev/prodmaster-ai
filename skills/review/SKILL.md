---
name: review
description: Systematic code review — two-pass approach (critical then informational), test coverage diagrams, scope drift detection, adversarial scaling by diff size, and fix-first triage that auto-fixes mechanical issues and batches judgment calls for approval.
version: 1.0.0
triggers:
  - /prodmasterai review
  - code review
  - review this PR
  - review the diff
  - review my changes
  - pre-merge review
  - review before ship
reads:
  - memory/project-context.md
  - memory/mistakes.md
writes:
  - memory/review-log.md
  - memory/project-context.md
generated: false
generated_from: ""
---

# Review

Two-pass systematic code review. Pass 1 catches critical correctness and security issues. Pass 2 catches informational quality issues. Scales depth to diff size. Auto-fixes mechanical issues immediately; batches judgment calls for a single human approval gate at the end.

---

## Adversarial Scaling

Before starting, measure the diff:

```bash
git diff main...HEAD --stat
```

| Diff size | Strategy |
|---|---|
| < 50 lines changed | Single-pass quick review — combine Pass 1 + Pass 2 |
| 50–500 lines | Standard two-pass review |
| > 500 lines | Deep review — two-pass + subagent cross-check (see Phase 5) |

Record `diff_size` and `strategy` before continuing.

---

## Phase 1 — Scope Check

Before reviewing code, verify the diff matches its stated intent:

1. Read the PR title/description (or `git log main...HEAD --oneline` if no PR).
2. Read `memory/project-context.md` ## Active Features for the stated feature goal.
3. Scan changed files: do they match the stated scope?
4. **Scope drift:** if changed files include modules unrelated to the stated goal, flag each as `scope-drift: <filename> — reason this file should not be in this diff`.
5. Check for TODO comments in the diff that reference items NOT in the PR description — log as `undeclared-todo`.

Output scope check result before proceeding: clean or list of drift/undeclared items.

---

## Phase 2 — Pass 1: Critical Issues

Check every changed file for critical correctness and security issues. Run all checks in parallel per file.

### SQL Safety
- Raw string interpolation into SQL queries → flag as `sql-injection`
- Missing parameterized queries
- ORM queries with raw `WHERE` clauses using user input

### Race Conditions
- Shared mutable state accessed from concurrent goroutines/threads/async paths without synchronization
- Read-modify-write patterns on shared resources (counter increments, cache updates) without atomics or locks
- async/await gaps where state can change between awaited calls

### LLM Trust Boundaries
- User-controlled input passed directly to LLM prompt without sanitization → flag `prompt-injection`
- LLM output used in dynamic evaluation, shell invocation, or SQL without validation
- System prompt leaked in error messages or API responses

### Enum / Switch Completeness
- switch/match/if-elif chains on enum-like types missing at least one variant
- No default/else clause when variants can be extended

### Secrets and Credentials
- Hardcoded API keys, tokens, passwords, or connection strings in source (not `.env`)
- Secrets passed as CLI arguments (visible in process list output)

For each finding: assign `id: R1-NNN`, record file, line number, issue type, severity (all Pass 1 issues are `critical` or `high`), and a one-line remediation.

---

## Phase 3 — Pass 2: Informational Issues

Check for quality issues that do not break correctness but degrade maintainability. Run all checks in parallel.

### Side Effects
- Functions with names suggesting pure computation that also write to DB, disk, or external service
- Mutation of input parameters without documentation

### Magic Numbers / Strings
- Numeric or string literals used inline without a named constant (threshold: appears more than once or is non-obvious)

### Dead Code
- Exported functions/methods/types with zero internal usages and no documented external consumer
- Commented-out code blocks longer than 3 lines

### Test Gaps
- New functions/methods with no corresponding test
- Error paths tested in implementation but absent from test suite
- Mocked tests that could be integration tests without meaningful extra cost

### Performance
- N+1 query patterns (loop containing a DB call)
- Unbounded result sets (no LIMIT on user-facing queries)
- Synchronous I/O on the hot path where async exists

### Prompt Issues (if LLM code present)
- System prompts over 2000 tokens without compression
- No token count guard before API calls
- Retry logic missing on rate-limit responses

For each finding: assign `id: R2-NNN`, file, line, issue type, severity (`medium` or `low`), remediation.

---

## Phase 4 — Test Coverage Diagram

For each changed file with a corresponding test file, generate an ASCII coverage map:

```
<filename>
  fn authenticate()          ★★★  (happy path + error path + edge)
  fn validate_token()        ★★   (happy path + error path)
  fn refresh_session()       ★    (happy path only)
  fn logout()                ✗    (no tests)
```

Legend: ★★★ = full coverage, ★★ = partial, ★ = minimal, ✗ = none

If no test file exists for a changed source file: mark entire file as `✗ no test file`.

---

## Phase 5 — Deep Review Subagent (>500 lines only)

*Skip for standard and quick strategies.*

Dispatch a second review pass as a subagent with a different lens:
- Focus: architectural concerns, abstraction violations, cross-module coupling
- Input: the same diff
- Output: additional findings not captured in Pass 1 or Pass 2

Merge subagent findings into the main findings list, deduplicating by file+line.

---

## Phase 6 — Fix-First Triage

Split all findings into two buckets:

**Mechanical fixes** (auto-fix immediately, no judgment needed):
- Missing enum variants when the correct value is unambiguous
- Magic number → extract to named constant
- Dead code removal (commented-out blocks)
- Missing LIMIT on obvious list queries
- Hardcoded secrets → move to environment variable reference

**Judgment calls** (batch for human approval):
- Architectural concerns
- Scope drift decisions (keep or revert?)
- Test gap decisions (write now or log as tech debt?)
- Any finding where the correct fix is ambiguous

For each mechanical fix:
1. Record `pre_fix_sha: git rev-parse HEAD`
2. Apply fix
3. Commit: `git commit -m "fix(review): R1-NNN <one-line description>"`

---

## Phase 7 — Judgment Gate

Present all judgment-call findings as a single approval block:

```
Review: Judgment Calls Requiring Approval
──────────────────────────────────────────
[R1-001] SQL injection risk in user_query.go:47
  Suggested fix: use parameterized query
  [A]pply  [S]kip  [E]scalate to blocker

[R2-003] test gap — fn refresh_session() has no error-path test
  Suggested fix: add test for expired token case
  [A]pply  [S]kip  [E]scalate to blocker
```

Wait for user response. Apply approved fixes with atomic commits. Log skipped items in review-log as `status: deferred`.

*When `autonomous_mode: true`: auto-apply all `high` judgment calls using best-practice defaults. Auto-skip all `low` judgment calls. Log all decisions.*

---

## Phase 8 — Report

Output the review report:

```
== Code Review: <branch or PR title> ==
Strategy:   <quick | standard | deep>
Diff size:  <N lines across M files>

Scope:      <clean | N drift items>

Pass 1 (Critical):
  SQL Safety       <pass | N findings>
  Race Conditions  <pass | N findings>
  LLM Boundaries   <pass | N findings>
  Enum Coverage    <pass | N findings>
  Secrets          <pass | N findings>

Pass 2 (Informational):
  Side Effects     <pass | N findings>
  Magic Numbers    <pass | N findings>
  Dead Code        <pass | N findings>
  Test Gaps        <pass | N findings>
  Performance      <pass | N findings>

Test Coverage:
  <coverage diagram — files with no coverage only>

Mechanical fixes applied: N commits
Judgment calls approved: N / deferred: N / escalated: N

Verdict: <SHIP | SHIP WITH NOTES | REWORK REQUIRED>
  Reason: <one sentence>

Next:
  <"No blockers — ready to merge" | "N critical issues require rework before merge" | "Run /prodmasterai qa to verify fixes end-to-end">
```

Verdict rules:
- Any `critical` finding remaining → REWORK REQUIRED
- Any `high` security finding remaining → REWORK REQUIRED
- Any `high` non-security finding remaining → SHIP WITH NOTES
- Only `medium` or `low` remaining → SHIP WITH NOTES
- Zero findings remaining → SHIP

Append to `memory/review-log.md`:

```yaml
---
date: <YYYY-MM-DD>
feature: <active_feature or branch name>
strategy: <quick | standard | deep>
critical_found: N
high_found: N
mechanical_fixes: N
judgment_approved: N
judgment_deferred: N
verdict: SHIP | SHIP WITH NOTES | REWORK REQUIRED
session_id: <session_id>
---
```

---

## Integration with Auto-Pilot

When `autonomous_mode: true`:
- Default strategy: determined by diff size (adversarial scaling applies)
- Judgment gate: auto-apply `high`, auto-skip `low`, log all decisions
- If verdict is REWORK REQUIRED: park auto-pilot, append blocker to project-context.md
- If verdict is SHIP or SHIP WITH NOTES: continue to PR creation

---

## Rules

- Every finding must cite file path and line number — no line number, no finding
- Mechanical fixes are atomic commits — never batch two fixes in one commit
- Never auto-fix judgment calls in attended mode — always present the gate
- Scope drift items are flagged but never auto-reverted — user decides
- Deferred findings are logged, never silently dropped
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
