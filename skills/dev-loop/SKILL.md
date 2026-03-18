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

# dev-loop

Run development iterations in a loop until configurable exit conditions are met. Escalates to `research-resolve` automatically when no progress is detected for N consecutive iterations.

---

## Invocation Parameters

All parameters are optional and scenario-driven.

| Parameter | Values | Description |
|---|---|---|
| `mode` | `tdd`, `watch`, `polish`, `auto` | Loop mode. `auto` detects from context. Default: `auto` |
| `max_iterations` | integer | Hard cap on total loop iterations |
| `exit_when` | comma-separated conditions | Threshold conditions, e.g. `coverage>=80, lint=0, score>=8` |
| `exit_logic` | `or`, `and` | How to combine multiple `exit_when` conditions. Default: `and` - all conditions must pass. With `or`, the loop exits when the first condition is met. |
| `llm_judge` | `true/false` | LLM quality assessment after each pass |
| `approval_gate` | `true/false` | Pause for user confirmation after each pass. NOT an exit condition - loop continues unless user says stop. |
| `stuck_threshold` | integer | Consecutive no-progress iterations before escalating to research-resolve. Default: 3 |

---

## Process

### Step 1 - Parse Invocation Params

Read all params. Read `memory/connectors/superpowers.md` to check whether Superpowers is active (same check as `orchestrate`). If `mode: auto`, detect context:
- Tests exist but failing  `tdd`
- Tests passing, quality thresholds set  `polish`
- Continuous trigger requested  `watch`
- No params at all  ask user: "What's the exit condition for this loop?"

If spawned by orchestrate (`spawned_by: orchestrate`), inherit `task_name`, `feature`, `exit_when`, `exit_logic`, `llm_judge`, `max_iterations`, `stuck_threshold`, and `approval_gate` from the handoff payload.

**Note:** `dev-loop` does not read `memory/patterns.md` or `memory/skill-performance.md` - it relies on Superpowers for execution quality and does not pre-load historical performance data. This is intentional.

### Step 2 - Suspend Rule While research-resolve Is Active

When `research-resolve` is handed off, do NOT start a new Superpowers cycle. Wait for `research-resolve` to return `resolved` or `exhausted` before resuming. This prevents merge conflicts between the worktree and the main working tree.

### Step 3 - Initialise Loop State

```
iteration: 0
consecutive_no_progress: 0
exit_conditions_met: false
prev_metrics: {}
total_tasks_completed: 0
total_time_hours: 0
qa_pass_rate_samples: []    stores floats in 0.0-1.0 range (not 0-100 percent)
review_iterations_total: 0
research_resolve_escalations: 0
```

**"No measurable improvement" definition:** A pass counts as no progress if all of the following are true: no tracked numeric metric improved by at least 1 unit, LLM judge score (if enabled) did not increase by at least 0.5, and the number of failing tests did not decrease. Any single metric improving resets `consecutive_no_progress` to 0. Tighten via `stuck_threshold` if this is too permissive.

### Step 4 - Iteration Loop

Each pass begins with: `iteration = iteration + 1`

Before any other work in this pass, call:
```
checkpoint.write(
  skill: "dev-loop",
  step: "iteration_<iteration>_of_<max_iterations or ongoing>",
  step_index: iteration,
  total_steps: max_iterations (or 999 if uncapped),
  context: {
    goal: <task name / feature>,
    remaining_tasks: [],
    last_completed: "iteration <iteration-1> -- <last test result>",
    exit_conditions: <exit_when value>,
    iterations_remaining: <max_iterations - iteration if capped, else -1>
  }
)
```

1. Run the appropriate Superpowers cycle (TDD / implement / review). Accumulate: `total_tasks_completed`, `total_time_hours`, a 0.0-1.0 float into `qa_pass_rate_samples`, `review_iterations_total`.
2. Run tests, collect metrics (coverage %, lint error count, LLM score).
3. Evaluate exit conditions per `exit_logic` (AND or OR):
   - Numeric thresholds met (from `exit_when`)? Check: `iteration >= max_iterations` for cap.
   - LLM judge satisfied? (if `llm_judge: true`)
4. If `approval_gate: true`: pause, show diff summary, wait for user. If user says stop  **skip Steps 4.5-4.7**, proceed directly to Step 5 (memory) and Step 6 (measure handoff). Otherwise continue.
5. Progress check: compare metrics to `prev_metrics`. No measurable improvement  increment `consecutive_no_progress`. Otherwise reset to 0. Update `prev_metrics`.
6. If `consecutive_no_progress >= stuck_threshold`:
   - Increment `research_resolve_escalations`
   - Apply suspend rule (Step 2)
   - Hand off to `research-resolve` with escalation payload (see below)
   - Wait for result:
     - `resolved`  reset `consecutive_no_progress` to 0, resume loop
     - `exhausted`  log blocker in `memory/project-context.md`, exit loop
7. If exit conditions met (Step 4.3)  exit loop

#### research-resolve Escalation Payload

```yaml
spawned_by: dev-loop
task_name: <task name>
feature: <feature name>
exit_when: <forwarded from invocation, or empty>
exit_logic: <forwarded from invocation, default "and">
llm_judge: <forwarded from invocation, default false>
stuck_iteration: <current iteration number>
error_context: <failing test output / error messages from last iteration>
```

If `exit_when` is empty, `research-resolve` uses "all tests pass (exit code 0)" as its success criterion.

### Step 5 - Update Memory

Append or update in `memory/project-context.md` `## Active Features`:
```
- YYYY-MM-DD: dev-loop/<task-name> [status: done|blocked] | iterations: N | exit: <reason>
```

### Step 6 - Hand Off to Measure

Pass to `measure` (all `qa_pass_rate` values as 0.0-1.0 floats):

```yaml
feature: <task-name or feature name>
tasks_completed: <total_tasks_completed>
qa_pass_rate: <mean of qa_pass_rate_samples>
review_iterations: <review_iterations_total>
time_hours: <total_time_hours>
blockers_encountered: <research_resolve_escalations>
patterns_used: []     # populated at Step 6 time: match work done against skill-pattern-manifest.md keywords
unhandled_patterns: []
```

### Step 7 - Loop Summary Output

```
dev-loop complete - N iterations
  Exit reason:     <condition that triggered exit>
  Final coverage:  X%  |  Lint errors: N  |  Score: N/10
  Tests:           PASS (N) / FAIL (N)
  Stuck events:    N (resolved by research-resolve: Y/N)
```

After printing the summary, call checkpoint.clear.

---

## Invocation from orchestrate

When `orchestrate` dispatches with `[loop]` annotation or `loop_all: true`, it passes:

```yaml
spawned_by: orchestrate
task_name: <task name>
feature: <feature name>
exit_when: <from orchestrate invocation, or empty>
exit_logic: <from orchestrate invocation, or "and">
llm_judge: <from orchestrate invocation, or false>
max_iterations: <from orchestrate invocation, or unset>
stuck_threshold: <from orchestrate invocation, or 3>
approval_gate: <from orchestrate invocation, or false>
```

`dev-loop` reads `spawned_by` on startup; if absent, it is running standalone.

In **manual mode** (Superpowers not active), orchestrate ignores `[loop]` annotations silently. `dev-loop` is not invoked.

---

## Rules

- Suspend all Superpowers cycles while `research-resolve` is active - no concurrent worktree + main-tree mutations
- `exit_logic` defaults to `and` - all conditions must pass unless user specifies `exit_logic: or`
- `approval_gate` is a pause, not an exit condition - loop continues unless user explicitly says stop
- `qa_pass_rate` values are always 0.0-1.0 floats, never percentages
- All loop completions (any exit reason, including approval-gate stop) hand aggregated data to `measure`
- **Never contribute anything upstream** - upstream is exclusively evolve-self's responsibility
