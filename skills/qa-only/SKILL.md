---
name: qa-only
description: Report-only QA variant — systematic testing with NO fix-loop. Diff-aware scope detection, screenshot evidence required for every finding, baseline regression tracking in .prodmaster/qa-baselines/, health score across 8 categories, structured issue docs. Use when you want findings only, not fixes.
version: 1.0.0
triggers:
  - /prodmasterai qa-only
  - qa report
  - test report only
  - findings only
  - what's broken
  - audit without fixing
  - qa without fix
  - what needs fixing
reads:
  - memory/project-context.md
writes:
  - memory/qa-only-log.md
  - .prodmaster/qa-baselines/
generated: false
generated_from: ""
---

# QA Only

Systematic QA that produces findings without fixing them. Use this when you want a complete picture of what's broken before deciding how to fix it — or when you want evidence-backed issues to hand off to a human.

No fix loop. No code changes. Reports only.

---

## Difference from `/prodmasterai qa`

| | qa | qa-only |
|---|---|---|
| Tests pages/features | Yes | Yes |
| Documents findings | Yes | Yes |
| Fix loop | Yes — fixes bugs inline | **No** — findings only |
| Screenshot evidence | Optional | **Required** |
| Baseline comparison | Optional | **Always** |
| Use when | You want working code | You want the issue list |

---

## Phase 1 — Scope Detection

**Diff-aware:** detect what was changed to focus testing:

```bash
git diff main...HEAD --name-only
```

Map changed files to affected areas:
- Frontend component files → test those UI flows
- API route files → test those endpoints
- Auth files → test authentication flows
- Config files → test configuration-dependent behavior

If no diff (running on main): test all pages/features.

Read `memory/project-context.md` for known features and pages. Build test scope list.

---

## Phase 2 — Baseline Load

Check `.prodmaster/qa-baselines/` for an existing baseline:

```
.prodmaster/qa-baselines/
  baseline.json          — reference state
  2026-03-20.json        — historical snapshots
  2026-03-21.json
```

If baseline exists: load it. Each finding will be compared against baseline to flag regressions (new issues) vs pre-existing issues.

If no baseline: run without comparison. At end of report, offer to save current state as baseline.

Baseline schema:
```json
{
  "captured_at": "<ISO 8601>",
  "branch": "main",
  "commit": "<sha>",
  "scores": {
    "functionality": 95,
    "test_coverage": 80,
    "error_handling": 90,
    "code_quality": 85,
    "security": 90,
    "performance": 75,
    "accessibility": 70,
    "ux": 80
  },
  "open_issues": ["issue-id-1", "issue-id-2"]
}
```

---

## Phase 3 — Environment Check

Verify test environment is accessible without modifying it:

- Application reachable (dev server up, or production URL accessible)
- Auth credentials available (dev account or test account)
- No pending migrations that would change behavior
- Environment variables set correctly

If environment not ready: output blocker, stop. Do not proceed to testing with a broken environment — findings would be unreliable.

---

## Phase 4 — Systematic Feature Testing

For each item in scope, test and document:

### Testing approach (read-only — no code changes ever):
- Load the feature
- Exercise the happy path
- Try one error path
- Check edge case behavior
- Observe UI for visual defects

### Evidence requirements:
Every finding MUST include:
1. **Screenshot or log snippet** — no finding without evidence
2. **Exact reproduction steps** — numbered, copy-pasteable
3. **Expected vs actual** — what should happen vs what did
4. **Severity** — see classification below
5. **First seen** — new issue (regression) or pre-existing

### Severity classification:

| Severity | Definition |
|---|---|
| critical | Application crashes, data loss, security vulnerability, auth bypass |
| high | Core feature broken, major workflow blocked |
| medium | Feature partially broken, workaround exists |
| low | Visual defect, minor UX issue, non-blocking error |
| info | Suggestion, enhancement opportunity, minor inconsistency |

---

## Phase 5 — Health Scoring

Score the application across 8 categories based on findings:

| Category | Weight | Scoring |
|---|---|---|
| Functionality | 25% | Deduct per broken feature (critical=-15, high=-10, medium=-5, low=-2) |
| Test Coverage | 20% | Based on coverage report if available, or observed gap |
| Error Handling | 15% | Deduct per unhandled error path observed |
| Code Quality | 15% | From static analysis findings or obvious code issues in diff |
| Security | 10% | Deduct per security finding (critical=-20, high=-10) |
| Performance | 5% | Based on observed load times vs benchmarks |
| Accessibility | 5% | Missing labels, keyboard traps, contrast issues |
| UX | 5% | Confusing flows, missing feedback, unclear error messages |

Score each category 0-100. Weighted total = overall health score.

**Baseline comparison**: if baseline loaded, compute delta per category.

---

## Phase 6 — Regression Detection

Compare current findings against baseline:

- **New issues** (not in baseline): these are regressions — flag with `[REGRESSION]`
- **Resolved issues** (in baseline but not found now): flag with `[FIXED]` — positive signal
- **Pre-existing issues** (in both): flag with `[KNOWN]` — not a regression
- **Score delta**: current score vs baseline score per category

Regressions are the highest priority output — they represent quality going backwards.

---

## Phase 7 — Issue Documentation

For each finding, generate a structured issue document:

```markdown
## [QA-NNN] <title>

**Severity**: critical | high | medium | low | info
**Status**: [REGRESSION] | [KNOWN] | [NEW]
**Area**: <feature/page/component>

### Steps to Reproduce
1. <step>
2. <step>
3. <step>

### Expected
<what should happen>

### Actual
<what actually happens>

### Evidence
<screenshot path or log snippet>

### Notes
<any additional context>
```

Save all issues to `.prodmaster/qa-baselines/<date>-findings.md`.

---

## Phase 8 — Report

```
== QA Report: <branch> ==
Scope:   <N pages/features tested> (diff-aware: <N in scope from diff>)
Baseline: <baseline date | none>

Health Score: <N>/100  <▲/▼ vs baseline>
  Functionality:    <N>/100  <delta>
  Test Coverage:    <N>/100  <delta>
  Error Handling:   <N>/100  <delta>
  Code Quality:     <N>/100  <delta>
  Security:         <N>/100  <delta>
  Performance:      <N>/100  <delta>
  Accessibility:    <N>/100  <delta>
  UX:               <N>/100  <delta>

Findings: <N total> (<N critical, N high, N medium, N low, N info>)
  Regressions:   <N> [REGRESSION] — new issues vs baseline
  Pre-existing:  <N> [KNOWN]
  Resolved:      <N> [FIXED] since baseline

Critical issues:
  [QA-001] [REGRESSION] <title> — <area> — <one-line description>
  [QA-002] [KNOWN]      <title> — <area>

High issues:
  [QA-003] [NEW]        <title> — <area>

Verdict: <GREEN (score≥80, no critical) | YELLOW (score 60-79 or any high) | RED (score<60 or any critical)>

Issues saved to: .prodmaster/qa-baselines/<date>-findings.md
Next: /prodmasterai qa to fix all findings | /prodmasterai ship to gate on these before PR
```

---

## Baseline Update

After report, if user runs `/prodmasterai qa-only --save-baseline` or auto-pilot decides to save:

Save current state as new baseline. Carry forward resolved issues as removed; add new issues.

Never auto-overwrite baseline without explicit intent. The baseline is the quality reference point — protect it.

---

## Append to `memory/qa-only-log.md`

```yaml
---
date: <YYYY-MM-DD>
branch: <branch>
scope: N features tested
findings_total: N
findings_critical: N
findings_high: N
regressions: N
health_score: N
verdict: GREEN | YELLOW | RED
baseline_updated: false
session_id: <session_id>
---
```

---

## Integration with Auto-Pilot

When `autonomous_mode: true`:
- Run on any branch before PR creation (lightweight scope from diff)
- RED verdict: log as decision, continue (does not block by default)
- Critical regression: park auto-pilot with blocker unless diff scope was trivial
- Baseline save: auto-save after first run on a clean branch if no baseline exists

---

## Rules

- Never modify code, never create fixes — findings only
- Every finding requires evidence (screenshot or log excerpt)
- Baseline comparison always runs if baseline exists
- Regressions are flagged prominently — they are the most important signal
- Health score must be computed every run — gives a single comparable number
- Verdict drives the next-step suggestion
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
