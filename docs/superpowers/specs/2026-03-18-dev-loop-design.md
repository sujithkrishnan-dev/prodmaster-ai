# dev-loop + research-resolve — Design Spec

**Date:** 2026-03-18
**Status:** approved
**Approach:** Option B — two separate skills with clean handoff

---

## Overview

Two new skills that add autonomous iterative development loops to ProdMaster AI:

- **`dev-loop`** — runs development iterations in a loop until configurable exit conditions are met
- **`research-resolve`** — autonomous fallback that activates when dev-loop gets stuck; works in an isolated git worktree and only merges back on success

---

## Architecture

### New Files

```
skills/dev-loop/SKILL.md
skills/research-resolve/SKILL.md
memory/blocker-research.md       ← new memory file, written by research-resolve
```

### Integration Points

- `orchestrate` — when dispatching a task, user can opt in with a `[loop]` flag on the task annotation, or pass `loop_all: true` at orchestrate invocation. Orchestrate passes `spawned_by: orchestrate` + the original task name to `dev-loop` at handoff. No changes to orchestrate's skill file are required. In manual mode (Superpowers not active), orchestrate silently skips the loop flag and presents the task normally.
- `dev-loop` → `measure` — hands aggregated cycle outcome data to measure after loop completes (fields and units specified below). **Note:** `measure`'s skill file needs one additive update to carry the `blockers_encountered` field through to `skill-performance.md`. This is the only change to an existing skill file.
- `research-resolve` → `memory/blocker-research.md` — dedicated file for blocker research findings, separate from `memory/research-findings.md` (which is owned by evolve-self and must not be written to by this skill)
- `research-resolve` → `memory/project-context.md` — logs blocker entry if all fix attempts exhausted

---

## Skill Frontmatter

### `dev-loop`

```yaml
---
name: dev-loop
description: Use when a task should repeat until tests pass, quality thresholds are met, or a set number of iterations complete. Supports tdd, watch, and polish loop modes with configurable exit conditions. Escalates to research-resolve when stuck.
version: 1.0.0
triggers:
  - User says "loop until passing", "keep iterating", "run until tests pass"
  - User says "dev loop", "improvement loop", "polish loop", "watch mode"
  - orchestrate dispatches a task annotated with [loop] or loop_all: true
  - User runs /prodmasterai dev-loop [params]
reads:
  - memory/project-context.md
  - memory/connectors/skill-pattern-manifest.md
  - memory/connectors/superpowers.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---
```

**Note:** `dev-loop` does not read `memory/blocker-research.md` directly. It receives only the `resolved`/`exhausted` status from `research-resolve` at runtime. The file is owned and read by `research-resolve`.

### `research-resolve`

```yaml
---
name: research-resolve
description: Use when a dev-loop or any development task is stuck with no progress after N iterations. Spins up an isolated git worktree, researches the failure, applies fixes autonomously, and merges back only on success.
version: 1.0.0
triggers:
  - dev-loop reaches stuck_threshold consecutive no-progress iterations
  - User says "research and resolve", "investigate failure", "loop is stuck", "can't make progress"
  - Standalone: /prodmasterai research-resolve
reads:
  - memory/project-context.md
  - memory/blocker-research.md
writes:
  - memory/blocker-research.md
  - memory/project-context.md
generated: false
generated_from: ""
---
```

---

## Invocation Parameters

All parameters are optional and scenario-driven.

| Parameter | Values | Description |
|---|---|---|
| `mode` | `tdd`, `watch`, `polish`, `auto` | Loop mode. `auto` detects from context. Default: `auto` |
| `max_iterations` | integer | Hard cap on total loop iterations |
| `exit_when` | comma-separated conditions | Threshold conditions, e.g. `coverage>=80, lint=0, score>=8` |
| `exit_logic` | `or`, `and` | How to combine multiple `exit_when` conditions. Default: `and`. **Warning:** with `or`, the loop exits the moment the first condition is met — even if others are not. Specify `exit_logic: or` explicitly only when any single condition passing is sufficient. |
| `llm_judge` | `true/false` | LLM quality assessment after each pass |
| `approval_gate` | `true/false` | Pause for user confirmation after each pass before continuing. This is NOT an exit condition — the loop continues unless the user explicitly says to stop. |
| `stuck_threshold` | integer | Consecutive no-progress iterations before escalating to research-resolve. Default: 3 |

---

## `dev-loop` Process Flow

### Step 1 — Parse Invocation Params

Read all params. Read `memory/connectors/superpowers.md` to check whether Superpowers is active (same detection as `orchestrate`). If `mode: auto`, detect:
- Tests exist but failing → `tdd`
- Tests passing, quality thresholds set → `polish`
- Continuous trigger requested → `watch`
- No params at all → ask user: "What's the exit condition for this loop?"

If spawned by orchestrate (`spawned_by: orchestrate`), inherit `task_name`, `feature`, `exit_when`, `exit_logic`, `llm_judge`, and any other `loop_params` from the handoff.

**Note:** `dev-loop` does not read `memory/patterns.md` or `memory/skill-performance.md` — it relies on Superpowers for execution quality and does not pre-load historical performance data before starting a loop. This is intentional.

### Step 2 — Suspend Rule While research-resolve Is Active

When `research-resolve` is handed off, `dev-loop` does NOT start a new Superpowers cycle. It waits for `research-resolve` to return `resolved` or `exhausted` before resuming. This prevents merge conflicts between the worktree and the main working tree.

### Step 3 — Initialise Loop State

`iteration` is incremented to `iteration + 1` at the **start** of each pass (before Step 4.1). The `max_iterations` cap check in Step 4.3 compares `iteration >= max_iterations`.

```
iteration: 0
consecutive_no_progress: 0
exit_conditions_met: false
prev_metrics: {}
total_tasks_completed: 0
total_time_hours: 0
qa_pass_rate_samples: []   ← stores floats in 0.0–1.0 range (not 0–100 percent)
review_iterations_total: 0
research_resolve_escalations: 0
```

**"No measurable improvement" definition:** A pass counts as no progress if all of the following are true: no tracked numeric metric improved by at least 1 unit (e.g. coverage percentage points, lint error count decrease), LLM judge score (if enabled) did not increase by at least 0.5, and the number of failing tests did not decrease. **Design note:** this is intentionally liberal — any single metric improving resets the `consecutive_no_progress` counter. This prevents premature escalation to `research-resolve` when incremental fixes are still making progress on one dimension (e.g. lint cleans up while coverage is stable). Tighten via `stuck_threshold` if this is too permissive for a given project.

### Step 4 — Iteration Loop

Each pass begins with: `iteration = iteration + 1`

1. Run the appropriate Superpowers cycle (TDD / implement / review). Accumulate: `total_tasks_completed`, `total_time_hours`, a 0.0–1.0 float into `qa_pass_rate_samples`, `review_iterations_total`.
2. Run tests, collect metrics (coverage %, lint error count, LLM score, custom)
3. Evaluate exit conditions per `exit_logic` (AND or OR):
   - Numeric thresholds met (from `exit_when`)?
   - Iteration cap (`max_iterations`) reached?
   - LLM judge satisfied? (if `llm_judge: true`)
4. If `approval_gate: true`: pause, show diff summary, wait for user. If user says stop → treat as a normal loop exit: **skip Steps 4.5–4.7**, proceed directly to Step 5 (memory update) and Step 6 (measure handoff) with accumulated data. Otherwise continue.
5. Progress check: compare metrics to `prev_metrics` using the no-progress definition from Step 3. No measurable improvement → increment `consecutive_no_progress`. Otherwise reset `consecutive_no_progress` to 0.
6. If `consecutive_no_progress >= stuck_threshold` → increment `research_resolve_escalations`, suspend iterations (Step 2 rule), hand off to `research-resolve`, wait for result:
   - `resolved` → reset `consecutive_no_progress` to 0, resume loop
   - `exhausted` → log blocker, exit loop
7. If exit conditions met (from step 3) → exit loop

### Step 5 — Update Memory

Append or update in `memory/project-context.md` `## Active Features`:
```
- YYYY-MM-DD: dev-loop/<task-name> [status: done|blocked] | iterations: N | exit: <reason>
```

### Step 6 — Hand Off to Measure

Pass this object to `measure` (all `qa_pass_rate` values in 0.0–1.0 float format):

```yaml
feature: <task-name or feature name>
tasks_completed: <total_tasks_completed>
qa_pass_rate: <mean of qa_pass_rate_samples>     # float 0.0–1.0
review_iterations: <review_iterations_total>
time_hours: <total_time_hours>
blockers_encountered: <research_resolve_escalations>
patterns_used: []     # populated once at Step 6 time by matching all work done in the loop against skill-pattern-manifest.md keywords — not accumulated per iteration
unhandled_patterns: []
```

**measure additive update required:** Add `blockers_encountered` to measure's YAML append template in `measure/SKILL.md` so it is recorded in `skill-performance.md` and visible to `learn`/`report`.

### Step 7 — Loop Summary Output

```
dev-loop complete — N iterations
  Exit reason:     <condition that triggered exit>
  Final coverage:  X%  |  Lint errors: N  |  Score: N/10
  Tests:           PASS (N) / FAIL (N)
  Stuck events:    N (resolved by research-resolve: Y/N)
```

---

## dev-loop → research-resolve Escalation Payload

When `dev-loop` escalates to `research-resolve` at Step 4.6, it passes:

```yaml
spawned_by: dev-loop
task_name: <task name>
feature: <feature name>
exit_when: <forwarded from dev-loop invocation, or empty>
exit_logic: <forwarded from dev-loop invocation, default "and">
llm_judge: <forwarded from dev-loop invocation, default false>
stuck_iteration: <current iteration number>
error_context: <failing test output / error messages from the last iteration>
```

`research-resolve` uses these values to evaluate whether a fix succeeds in Step 3. If `exit_when` is empty (no threshold conditions were set), success is defined as: all tests pass (exit code 0). This is the minimum viable success criterion for any test-based loop.

---

## `research-resolve` Process Flow

**Triggered by:** `dev-loop` reaching `stuck_threshold`, or standalone invocation.

**Standalone invocation exit conditions:** When `research-resolve` is called directly (not via `dev-loop`), it has no forwarded `exit_when` params. In standalone mode, success is defined as: all tests pass (exit code 0). If no test suite is detected, `research-resolve` asks the user: "What does success look like for this fix? (e.g., tests pass, file compiles, output matches X)"

### Step 1 — Spin Up Isolated Worktree

```bash
git worktree add .worktrees/research-resolve-<timestamp> HEAD
```

A local branch `research-resolve-<timestamp>` is created pointing to HEAD. All fix attempts happen inside this worktree. Main working tree is never modified until merge.

### Step 2 — Research Phase (parallel)

Run simultaneously:
- Analyse failing tests + error messages → extract root cause hypotheses ranked by confidence
- Search codebase for related patterns
- Check `memory/blocker-research.md` for prior similar failures
- If web search available: look up error signatures

### Step 3 — Fix Loop (inside worktree)

The `exit_when`, `exit_logic`, and `llm_judge` values from the triggering `dev-loop` invocation are forwarded to `research-resolve` at escalation time and used here to evaluate success.

```
fix_attempt: 0
max_fix_attempts: 5  ← hard safety cap
```

Each attempt:
1. Apply highest-confidence fix hypothesis inside the worktree
2. Run tests inside worktree
3. Check all forwarded `dev-loop` exit conditions (`exit_when`, `exit_logic`, `llm_judge`)
4. Pass → proceed to Step 4
5. Still failing → log attempt, pick next hypothesis, increment `fix_attempt`, repeat until `max_fix_attempts` reached

### Step 4 — Merge Back on Success

Get the commit ref from the worktree and merge it into the main working tree:

```bash
COMMIT=$(git -C .worktrees/research-resolve-<timestamp> rev-parse HEAD)
git merge $COMMIT
git worktree remove .worktrees/research-resolve-<timestamp>
```

**On merge conflict:**
```bash
git merge --abort
git worktree remove .worktrees/research-resolve-<timestamp>
```
Log the conflict as a blocker and proceed to Step 5 (exhaustion path) with `outcome: exhausted`.

Return `resolved` to `dev-loop` on clean merge.

### Step 5 — On Exhaustion (all 5 attempts failed or merge conflict)

1. Clean up worktree (already done in merge-conflict path above; also run here if fix loop exhausted without a merge attempt). The worktree may have uncommitted or staged-but-not-committed changes. Use `--force` as the standard cleanup to handle all dirty-tree states (working tree changes, staged changes, or both):
   ```bash
   git worktree remove --force .worktrees/research-resolve-<timestamp>
   ```
2. Surface full attempt log to user
3. Log blocker in `memory/project-context.md`:
   ```
   - YYYY-MM-DD: research-resolve exhausted on <task-name> | age_days: 0 | recommended_fix: manual review required
   ```
4. Return `exhausted` to `dev-loop`

### Step 6 — Log Findings (always runs, regardless of outcome)

After either Step 4 (success) or Step 5 (exhaustion) completes, append to `memory/blocker-research.md`:

```yaml
---
date: YYYY-MM-DD
type: blocker-fix
task: <task-name>
root_cause: <identified root cause or "unknown">
fix_applied: <fix description, or "none — exhausted">
attempts: N
outcome: resolved | exhausted
keywords: [keyword1, keyword2]
---
```

---

## Invocation from orchestrate

When `orchestrate` dispatches a task with `[loop]` annotation or `loop_all: true`, it passes:

```yaml
spawned_by: orchestrate
task_name: <task name>
feature: <feature name>
exit_when: <from user's orchestrate invocation, or empty>
exit_logic: <from user's orchestrate invocation, or "and">
llm_judge: <from user's orchestrate invocation, or false>
max_iterations: <from user's orchestrate invocation, or unset>
stuck_threshold: <from user's orchestrate invocation, or 3>
approval_gate: <from user's orchestrate invocation, or false>
```

`dev-loop` reads `spawned_by` on startup. If absent, it is running standalone.

In **manual mode** (Superpowers not active), orchestrate ignores `[loop]` annotations silently. `dev-loop` is not invoked.

---

## Memory Schema

### `memory/blocker-research.md` (new file, created by research-resolve on first write)

```markdown
# Blocker Research Log
<!-- Written by research-resolve. Schema: date, type, task, root_cause, fix_applied, attempts, outcome, keywords -->
<!-- Entries are YAML blocks separated by --- -->
```

This file is separate from `memory/research-findings.md` (owned by evolve-self). Never write to `research-findings.md` from this skill.

---

## Changes to Existing Files

| File | Change |
|---|---|
| `skills/measure/SKILL.md` | Add `blockers_encountered` field to the YAML append template (additive, non-breaking). Increment version (e.g. `1.x.x → 1.x+1.0`). |
| `memory/connectors/skill-pattern-manifest.md` | Add `dev-loop` and `research-resolve` keyword entries |
| `tests/test_skills.py` | Add `"dev-loop"` and `"research-resolve"` to `ALL_SKILLS` |
| `docs/README.md` | Add two rows to the skills table |

---

## Tests

Add to `tests/test_skills.py` `ALL_SKILLS`:
```python
"dev-loop", "research-resolve"
```

Add to `memory/connectors/skill-pattern-manifest.md`:
```
### dev-loop
keywords: [dev loop, loop until passing, iterate until tests pass, loop mode, improvement loop, polish loop, watch mode, keep improving, run until done]

### research-resolve
keywords: [stuck, research and resolve, autonomous fix, worktree fix, can't make progress, loop stuck, investigate failure, research the problem]
```

---

## Rules

- `dev-loop` suspends all Superpowers cycles while `research-resolve` is active — no concurrent worktree + main-tree mutations
- `research-resolve` always uses an isolated git worktree — never applies fixes directly to the main working tree
- Worktree is always cleaned up in every exit path (success merge, exhaustion, merge conflict) — no leftover `.worktrees/` entries
- `exit_logic` defaults to `and` — all conditions must pass unless user specifies `exit_logic: or`
- `approval_gate` is a pause mechanism, not an exit condition — the loop continues unless the user explicitly says stop
- `qa_pass_rate` values are always stored and passed as 0.0–1.0 floats, never as percentages
- `research-resolve` logs findings to `memory/blocker-research.md` after every run (success or exhaustion)
- `research-resolve` never writes to `memory/research-findings.md` (owned by evolve-self)
- `stuck_threshold` default of 3 is a suggestion — user param overrides at any time
- `research-resolve` has a hard inner cap of 5 fix attempts
- All loop completions hand aggregated data to `measure`
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
