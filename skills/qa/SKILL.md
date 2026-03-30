---
name: qa
description: Systematic QA pipeline — runs 11 phases of testing with health scoring across 8 categories, atomic fix commits per bug, and regression test generation. Three depth tiers adapt to available time and severity threshold.
version: 1.1.0
argument-hint: "[--quick | --standard | --exhaustive]"
effort: medium
paths:
  - "src/**"
  - "**/*.test.*"
  - "**/*.spec.*"
  - "tests/**"
  - "test/**"
triggers:
  - /prodmasterai qa
  - run qa
  - quality check
  - QA pass
  - test the app
  - qa the feature
  - systematic qa
  - health check the codebase
reads:
  - memory/project-context.md
  - memory/mistakes.md
writes:
  - memory/qa-log.md
  - memory/project-context.md
generated: false
generated_from: ""
---

# QA

Systematic quality assurance pipeline. Runs 11 phases from setup through report, scores health across 8 categories, commits one fix per discovered bug, and generates regression tests for every fix. Depth tier controls how much of the pipeline runs and what severity threshold triggers a fix.

---

## Depth Tiers

Choose tier before starting. Default: `standard`. When invoked by `auto-pilot`, use `quick`.

| Tier | Phases | Fix threshold | Time budget |
|---|---|---|---|
| **quick** | 1–4 + 10–11 (no fix-loop) | none — report only | ~30 seconds |
| **standard** | 1–9 + 11 | high + medium severity | bounded by WTF heuristics |
| **exhaustive** | all 11 | all severity levels | no cap |

---

## Phase 1 — Setup

1. Read `memory/project-context.md` frontmatter. Record `active_feature` and any open blockers.
2. Identify the test surface: run `git diff main...HEAD --name-only` to find changed files. If no changes, test surface = full codebase.
3. Determine available test commands: look for `package.json` scripts (`test`, `test:e2e`, `test:unit`), `Makefile` targets, or `pytest`/`cargo test`/`go test` equivalents.
4. Record baseline: run existing tests, capture pass/fail counts and any pre-existing failures. Label these `baseline_failures` — do NOT fix them during this session unless they are in the changed file set.

---

## Phase 2 — Authenticate

*Skip if the app has no auth layer.*

1. Identify auth mechanism from codebase (JWT, session cookie, OAuth, API key).
2. Locate test credentials: check `.env.test`, `README`, fixture files, or `memory/research-findings.md`.
3. Verify auth works end-to-end: attempt login, confirm session/token is returned.
4. If auth is broken: log as `severity: critical`, stop here, output partial report. Do not continue testing behind a broken auth gate.

---

## Phase 3 — Orient

1. Map the feature surface: list all routes/screens/components added or modified in this diff.
2. For each route/component: identify the happy path, the primary error path, and any edge inputs.
3. Record the map as the test plan for Phases 4–6.

---

## Phase 4 — Explore

Systematically exercise the feature surface from Phase 3:

- **Happy path:** correct inputs, expected outputs, no errors in console/logs.
- **Error path:** invalid inputs, missing required fields, boundary values (empty string, 0, MAX_INT, null).
- **Edge cases:** concurrent requests (if applicable), stale data, permission boundaries.

For each test:
- Record: test_id, path/component, input, expected, actual, pass/fail.
- On failure: assign severity (critical / high / medium / low) using this rubric:
  - **critical:** data loss, security bypass, total breakage of primary flow
  - **high:** primary user flow broken, no workaround
  - **medium:** degraded experience, workaround exists
  - **low:** cosmetic, typo, minor UX friction

*Quick tier stops here after Phase 4 and jumps to Phase 10.*

---

## Phase 5 — Document

Compile all failures from Phase 4 into a structured findings list:

```
[QA-001] <title>
  Severity:   critical | high | medium | low
  Path:       <route or component>
  Steps:      1. ... 2. ... 3. ...
  Expected:   <expected behaviour>
  Actual:     <observed behaviour>
  Evidence:   <log line, error message, or screenshot reference>
```

Sort by severity descending. Count totals per severity level.

---

## Phase 6 — Triage

Apply the **WTF-likelihood heuristics** to regulate fix scope:

- If `critical_count + high_count > 50`: flag to user, ask before proceeding. Do not auto-fix more than 50 issues per session.
- If fixing all medium issues would change >20% of the codebase by line count: downgrade medium issues to "log only" for this session, notify user.
- If `standard` tier: exclude `low` severity from the fix list.
- If `quick` tier: no fix list — jump to Phase 10.

Produce `fix_list` (ordered by severity) and `log_only_list`.

---

## Phase 7 — Fix Loop

For each item in `fix_list` (in severity order):

1. **Pre-fix SHA:** record `git rev-parse HEAD` as `pre_fix_sha`.
2. **Apply fix:** make the targeted code change. Fix only the issue at hand — do not refactor surrounding code.
3. **Verify fix:** re-run the specific test case from Phase 4 that failed. If it passes: continue. If it still fails after 2 attempts: move item to `log_only_list`, revert with `git checkout <pre_fix_sha> -- <affected_files>`, continue to next.
4. **Atomic commit:** `git commit -m "fix: <QA-NNN> <one-line description>"`. One commit per fix — never batch multiple fixes.
5. **Regression check:** re-run the full test suite (Phase 1 baseline commands). If a previously-passing test now fails: revert the fix commit, move item to `log_only_list`, note `caused_regression: true`.

*Exhaustive tier applies this loop to all severity levels including low.*

---

## Phase 8 — Regression Tests

For each successfully committed fix from Phase 7:

1. Write a regression test that would have caught the bug before the fix.
2. Test must be in the same test file/suite as the affected module. Follow the existing test style (describe/it, pytest fixtures, etc.).
3. Run the regression test: it must pass. If it fails to pass, debug and fix the test (not the code).
4. Commit: `git commit -m "test: regression for QA-NNN <issue title>"`.

*Skip Phase 8 in `quick` tier.*

---

## Phase 9 — Final QA

Re-run the full Phase 4 explore pass against the current codebase (post all fixes).

- Any item from `fix_list` that is still failing: escalate to `severity: critical` in the report regardless of original severity.
- Any new failures introduced (not in original findings): add to report as `introduced_by: fix-loop`.

*Skip Phase 9 in `quick` tier.*

---

## Phase 10 — Score

Calculate health score across 8 categories. Each category is 0–10. Weight by importance:

| Category | Weight | Scoring signal |
|---|---|---|
| Functionality | 25% | critical+high failures remaining / total test cases |
| Test Coverage | 20% | estimated % of changed lines covered by passing tests |
| Error Handling | 15% | error-path tests passing / error-path tests total |
| Code Quality | 15% | lint errors + type errors present in diff (0 = 10/10) |
| Security | 10% | any security-severity findings remaining (0 = 10/10) |
| Performance | 5% | P95 load time < 1s = 10, < 3s = 7, < 5s = 4, >5s = 0 |
| Accessibility | 5% | ARIA violations, keyboard nav failures present |
| UX | 5% | empty states, loading states, error messages present and clear |

**Overall score** = weighted average of all 8 categories.

Classify:
- 9.0–10: Excellent — ship
- 7.0–8.9: Good — minor issues, acceptable to ship with logging
- 5.0–6.9: Fair — medium issues present, fix before ship
- <5.0: Poor — critical/high issues remain, do not ship

---

## Phase 11 — Report

Output the QA report:

```
== QA Report: <session_id or feature_name> ==
Tier:       <quick | standard | exhaustive>
Tested:     <N files changed, M routes/components>

Health Score: <X.X>/10 — <Excellent | Good | Fair | Poor>

  Functionality    <score>/10  (weight 25%)
  Test Coverage    <score>/10  (weight 20%)
  Error Handling   <score>/10  (weight 15%)
  Code Quality     <score>/10  (weight 15%)
  Security         <score>/10  (weight 10%)
  Performance      <score>/10  (weight 5%)
  Accessibility    <score>/10  (weight 5%)
  UX               <score>/10  (weight 5%)

Findings:
  Critical:  N  (N fixed, N remaining)
  High:      N  (N fixed, N remaining)
  Medium:    N  (N fixed, N remaining)
  Low:       N  (logged only)

Fixes committed: N
Regression tests added: N

Remaining issues:
  [QA-NNN] <title> — <severity> — <one-line reason not fixed>

Next:
  <"All critical/high issues resolved — ready to ship" | "N critical issues remain — fix before merging" | "Run /prodmasterai qa --exhaustive to fix medium/low issues">
```

Append to `memory/qa-log.md`:

```yaml
---
date: <YYYY-MM-DD>
feature: <active_feature or "general">
tier: <quick | standard | exhaustive>
health_score: <X.X>
critical_remaining: N
high_remaining: N
fixes_committed: N
regression_tests_added: N
session_id: <session_id>
---
```

---

## Integration with Auto-Pilot

When `autonomous_mode: true`:
- Default tier: `quick` (fast, no fix-loop, report only)
- Override: if `spec_confidence: high` AND no critical baseline failures → use `standard`
- Never use `exhaustive` in autonomous mode — requires human judgment on fix scope
- Log QA health score as a decision entry in `memory/autonomous-log.md`
- If health score < 5.0: park auto-pilot session, output blocker with findings

---

## Rules

- One commit per fix — never batch
- Never fix issues outside the current diff's file set unless severity is critical
- Never exceed 50 atomic fix commits per session (WTF heuristic hard cap)
- Revert and log rather than committing a broken fix
- Regression tests must pass before committing them
- `baseline_failures` from Phase 1 are never touched unless in the changed file set
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
