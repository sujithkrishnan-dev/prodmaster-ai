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
```

### Integration Points

- `orchestrate` — when dispatching a task, user can opt in with a `[loop]` flag to trigger `dev-loop` instead of a single Superpowers cycle
- `dev-loop` → `measure` — hands cycle outcome data to measure after loop completes (same contract as any Superpowers cycle)
- `research-resolve` → `memory/research-findings.md` — logs all research and fix attempts
- `research-resolve` → `memory/project-context.md` — logs blocker if all fix attempts exhausted

### No Changes to Existing Skills

All integration is additive. No existing skill files are modified.

---

## Invocation Parameters

All parameters are optional and scenario-driven. None are hardcoded defaults that override user intent.

| Parameter | Values | Description |
|---|---|---|
| `mode` | `tdd`, `watch`, `polish`, `auto` | Loop mode. `auto` detects from context. Default: `auto` |
| `max_iterations` | integer | Hard cap on loop iterations |
| `exit_when` | `coverage>=X`, `lint=0`, `score>=N` | Comma-separated threshold conditions |
| `llm_judge` | `true/false` | LLM quality assessment after each pass |
| `approval_gate` | `true/false` | Pause for user approval after each pass |
| `stuck_threshold` | integer | Consecutive no-progress iterations before escalating to research-resolve. Default: 3 |

Exit conditions are evaluated in combination — any condition met triggers exit (OR logic), unless user specifies AND explicitly.

---

## `dev-loop` Process Flow

### Step 1 — Parse Invocation Params

Read all params. If `mode: auto`, detect:
- Tests exist but failing → `tdd`
- Tests passing, quality thresholds set → `polish`
- Continuous trigger requested → `watch`
- No params at all → ask user: "What's the exit condition for this loop?"

### Step 2 — Initialise Loop State

```
iteration: 0
consecutive_no_progress: 0
exit_conditions_met: false
prev_metrics: {}
```

### Step 3 — Iteration Loop

Each pass:
1. Run the appropriate Superpowers cycle (TDD / implement / review)
2. Run tests, collect metrics (coverage %, lint error count, LLM score, custom)
3. Evaluate all exit conditions in parallel:
   - Numeric thresholds met?
   - Iteration cap reached?
   - LLM judge satisfied? (if enabled)
   - Approval gate? (if enabled — pause, show diff summary, wait for user)
4. Progress check: compare metrics to previous iteration. No measurable improvement → increment `consecutive_no_progress`
5. If `consecutive_no_progress >= stuck_threshold` → hand off to `research-resolve`, wait for result, resume loop
6. If any exit condition met → exit loop, hand cycle data to `measure`

### Step 4 — Loop Summary Output

```
dev-loop complete — N iterations
  Exit reason:     <condition that triggered exit>
  Final coverage:  X%  |  Lint errors: N  |  Score: N/10
  Tests:           PASS (N) / FAIL (N)
  Stuck events:    N (resolved by research-resolve: Y/N)
```

---

## `research-resolve` Process Flow

**Triggered by:** `dev-loop` reaching `stuck_threshold` consecutive no-progress iterations, OR standalone invocation.

### Step 1 — Spin Up Isolated Worktree

```bash
git worktree add .worktrees/research-resolve-<timestamp> HEAD
```

All fix attempts happen inside this worktree. Main working tree is never touched until success.

### Step 2 — Research Phase (parallel)

Run simultaneously:
- Analyse failing tests + error messages → extract root cause hypotheses
- Search codebase for related patterns
- Check `memory/research-findings.md` for prior similar failures
- If web search available: look up error signatures

### Step 3 — Fix Loop (inside worktree)

```
fix_attempt: 0
max_fix_attempts: 5  ← safety cap, prevents infinite inner loop
```

Each attempt:
1. Apply highest-confidence fix hypothesis
2. Run tests inside worktree
3. Check all `dev-loop` exit conditions
4. Pass → proceed to Step 4
5. Still failing → log attempt, pick next hypothesis, repeat

### Step 4 — Merge Back on Success

```bash
git merge .worktrees/research-resolve-<timestamp>
git worktree remove .worktrees/research-resolve-<timestamp>
```

Return control to `dev-loop` with status: `resolved` or `exhausted`.

### Step 5 — Log Findings

Append to `memory/research-findings.md`:
- Root cause identified
- Fix that worked (or all attempts if exhausted)
- Pattern keywords for future gap detection

### On Exhaustion (all 5 attempts failed)

- Surface full attempt log to user
- Log blocker in `memory/project-context.md`
- Clean up worktree

---

## Trigger Modes

| Mode | How |
|---|---|
| Standalone | `/prodmasterai dev-loop [params]` |
| Per-task opt-in | `orchestrate` task flagged with `[loop]` |
| Auto-wrapped on orchestrate | `orchestrate` param `loop_all: true` |

---

## Memory Reads / Writes

| Skill | Reads | Writes |
|---|---|---|
| `dev-loop` | `memory/project-context.md` | `memory/project-context.md` |
| `research-resolve` | `memory/project-context.md`, `memory/research-findings.md` | `memory/research-findings.md`, `memory/project-context.md` |

---

## Tests

Add to `tests/test_skills.py` `ALL_SKILLS` list:
```python
"dev-loop", "research-resolve"
```

Add to `memory/connectors/skill-pattern-manifest.md`:
```
### dev-loop
keywords: [dev loop, loop until passing, iterate until tests pass, loop mode, improvement loop, polish loop, watch mode, keep improving]

### research-resolve
keywords: [stuck, research and resolve, autonomous fix, worktree fix, can't make progress, loop stuck, investigate failure]
```

Add rows to `docs/README.md` skills table.

---

## Rules

- `dev-loop` never modifies main working tree directly — all Superpowers cycles run normally; only `research-resolve` uses a worktree
- `research-resolve` always uses an isolated worktree — never applies fixes directly to main tree
- Worktree is always cleaned up (success or exhaustion) — no leftover `.worktrees/` entries
- Exit conditions are evaluated as OR by default — any condition met exits the loop
- `stuck_threshold` default of 3 is a suggestion only — user param overrides it at any time
- `research-resolve` has a hard inner cap of 5 fix attempts to prevent runaway loops
- All loop completions (pass or exhausted) hand data to `measure`
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
