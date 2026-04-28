# Parallel Explore — Design Spec

**Date:** 2026-03-21
**Status:** approved

---

## Problem

When tackling a complex feature, a single approach may not be optimal. There is no mechanism to run multiple strategies simultaneously, compare their results, and automatically apply the best one.

## Solution

New `skills/parallel-explore/SKILL.md`. Creates N git worktrees, dispatches one auto-pilot subagent per worktree in parallel, runs evaluation (tests first, quality as tiebreaker), applies the winning approach to the current branch, and cleans up.

---

## Scope

One new skill file, one new memory seed file (`memory/parallel-explore-log.md`). No changes to existing skills.

---

## File Map

| File | Action |
|---|---|
| `skills/parallel-explore/SKILL.md` | Create |
| `memory/parallel-explore-log.md` | Create (seed) |

---

## Triggers

- `/prodmasterai explore <goal>`
- "try multiple approaches"
- "parallel worktrees"
- "compare approaches"
- "run N approaches"
- "best of N"

---

## Approach Generation

Default: 2 approaches. User may specify: `/prodmasterai explore <goal> --approaches 3`.
Maximum: 4 approaches (hard limit — beyond this, worktree overhead exceeds benefit).

Approach strategies drawn from `memory/patterns.md` high-confidence entries. If fewer patterns exist than requested approaches, fall back to:
- Approach 1: default/conventional (no pattern seed)
- Approach 2: performance-optimised (minimise steps)
- Approach 3: safety-first (maximise test coverage)
- Approach 4: minimal (fewest files touched)

Each approach gets a `strategy_seed` string logged to `parallel-explore-log.md`.

---

## Execution Steps

### Step 1 — Session setup

Generate `session_id: pe-<YYYY-MM-DD-HHmm>`.
Create N worktrees:
```bash
git worktree add ../Plugin-explore-<session_id>-1 -b explore/<session_id>-1
git worktree add ../Plugin-explore-<session_id>-2 -b explore/<session_id>-2
# … up to N
```

Append session-open block to `memory/parallel-explore-log.md`:
```yaml
---
session_id: pe-<session_id>
goal: <goal>
approaches: N
status: running
started_at: <ISO 8601>
---
```

### Step 2 — Parallel execution

Dispatch one auto-pilot subagent per worktree in parallel. Each subagent:
- Works exclusively in its worktree directory
- Receives the same goal + its `strategy_seed`
- Has `autonomous_mode: true` forced (no blocking prompts)
- Writes results to `explore/<session_id>-<n>` branch

Wait for all subagents to complete (or timeout after `autonomous_max_iterations` × 2 minutes per approach).

### Step 3 — Evaluation

For each approach, run in parallel:

**Primary: Test pass rate**
```bash
cd ../Plugin-explore-<session_id>-<n>
python -m pytest tests/ -q --tb=no 2>/dev/null
# → parse: N passed, M failed → score = N / (N + M)
```
If no tests exist: score = 0.5 (neutral).

**Tiebreaker: Quality score**
Read changed files in the approach branch (`git diff main...HEAD --name-only`).
For each changed markdown skill file: count structural markers (frontmatter complete, steps numbered, rules present, examples present).
Quality score = (markers_present / markers_expected) across all changed files.

**Ranking:**
Sort by `(test_pass_rate DESC, quality_score DESC)`.
Winner = rank 1. Ties broken by fewest files changed (prefer minimal approach).

### Step 4 — Apply winner

```bash
# Get winning branch's commits as a patch
git diff main...explore/<session_id>-<winner_n> | git apply --index
git commit -m "feat: parallel-explore winner (session: <session_id>, approach: <winner_n>, tests: <score>)"
```

If `git apply` fails (conflict): fall back to cherry-pick of the winning branch's commits onto current branch.

### Step 5 — Cleanup

Remove all worktrees and their branches (including winner — changes are already on current branch):
```bash
git worktree remove ../Plugin-explore-<session_id>-<n> --force
git branch -D explore/<session_id>-<n>
```

### Step 6 — Log and report

Update session block in `memory/parallel-explore-log.md`:
```yaml
status: complete
completed_at: <ISO 8601>
winner: <n>
winner_strategy: <strategy_seed>
scores:
  - approach: 1
    test_pass_rate: 0.92
    quality_score: 0.85
    rank: 2
  - approach: 2
    test_pass_rate: 1.0
    quality_score: 0.88
    rank: 1
```

Output:
```
== Parallel Explore Complete: <session_id> ==
Goal:    <goal>
Approaches tried: N

Results:
  Approach 1 [strategy]: tests 92%, quality 85% → rank 2
  Approach 2 [strategy]: tests 100%, quality 88% → rank 1 ✓ WINNER

Winner applied to current branch.
```

---

## Failure Handling

**If an approach fails entirely** (auto-pilot parked/stuck): assign `test_pass_rate: 0`, `quality_score: 0`. Still rank and evaluate against remaining approaches.

**If ALL approaches fail:** Output failure summary. Clean up all worktrees. Do not apply anything to current branch.

**If evaluation cannot run** (pytest not found, etc.): fall back to quality score only.

---

## Self-Optimisation Hook

After each successful parallel-explore session, append the winning strategy seed to `memory/patterns.md` with `confidence: medium` and context `parallel-explore`. This feeds future approach generation — strategies that win are more likely to be tried first.

---

## Rules

- Hard limit: 4 approaches maximum
- Never push explore branches to remote
- Always clean up worktrees regardless of outcome (success or failure)
- Current branch is never modified until winner is confirmed
- If only one approach exists (N=1): run normally without worktree overhead

---

## Tests Required

1. `skills/parallel-explore/SKILL.md` exists with correct frontmatter
2. `memory/parallel-explore-log.md` seed file exists
3. Step 1: session_id format `pe-<YYYY-MM-DD-HHmm>` in skill
4. Step 2: parallel dispatch described (all subagents at once)
5. Step 3: primary evaluation is test pass rate
6. Step 3: tiebreaker is quality score
7. Step 4: winner applied via git apply/cherry-pick
8. Step 5: cleanup removes worktrees and branches
9. Step 6: log includes scores for all approaches + winner
10. Self-optimisation: winning strategy appended to patterns.md
11. Hard limit of 4 approaches in Rules
12. All-failure path: no changes applied to current branch
