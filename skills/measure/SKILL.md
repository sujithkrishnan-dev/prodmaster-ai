---
name: measure
description: Use after every completed Superpowers cycle to record metrics. Captures velocity, QA pass rate, review iterations, and blockers. Always hand off to learn after recording.
version: 1.4.0
triggers:
  - A Superpowers cycle has just completed
  - User says "cycle done", "feature finished", "tasks completed"
  - orchestrate passes a cycle outcome object
reads:
  - memory/project-context.md
writes:
  - memory/skill-performance.md
  - memory/project-context.md
generated: false
generated_from: ""
---

# Measure

Record quantitative data after every Superpowers cycle.

## Auto-Session Path

Triggered when `source: auto-session` is passed by prodmasterai Step 3E.
Skip all fuzzy parsing. Skip all user prompts. Use the inferred defaults passed in directly (already computed by Step 3E):

| Field | Inferred value |
|---|---|
| `tasks_completed` | count of `orchestrate` + `decide` + `learn` route calls (min 1) |
| `qa_pass_rate` | 1.0 |
| `review_iterations` | 0 |
| `time_hours` | null |
| `feature` | last active feature, or "mixed-session" |
| `blockers_encountered` | 0 |
| `patterns_used` | [] |
| `unhandled_patterns` | [] |
| inferred | true |

**Step 4 (auto-session only):** Skip the `learn` handoff entirely. `patterns_used` and `unhandled_patterns` are both empty — passing them to `learn` would write meaningless entries.

**Step 5 still runs.** `tasks_completed` is at least 1, so the threshold counter must be incremented.

**Step sequencing:** Run Steps 2 and 3 in parallel (as in the normal path). After both complete, run Step 5. Do not run 2, 3, and 5 concurrently — Step 5 depends on the Step 3 write to `project-context.md` (total_tasks_completed must be updated before Step 5 can check the threshold).

Do not output a completion message to the user. Velocity will be null due to null `time_hours`.

---

## Input

Receive cycle outcome (from `orchestrate` or user). Expected fields: feature name, tasks completed, QA pass rate (0.0-1.0), review iterations, time in hours, blockers encountered, patterns used, unhandled patterns.

Before asking for missing fields, attempt fuzzy extraction from the raw input string:

**Fuzzy Input Parsing**

Try each of the following formats in order until values are extracted:

| Input format | Example |
|---|---|
| Standard prose | `"5 tasks, 90% QA, 2 reviews, 3 hours"` |
| Shorthand | `"done -- 5t 90q 2r 3h"` (t=tasks, q=QA%, r=reviews, h=hours) |
| Natural past-tense | `"finished 5 tasks, all passed, 1 review, took 2 hours"` |
| Key=value | `"cycle done: tasks=5 qa=0.9 reviews=2 hours=3"` |

Extraction rules:
- `tasks`: any integer preceded or followed by "task(s)", "t" (shorthand), `tasks=N`, or a standalone integer when context implies a count
- `qa_pass_rate`: any percentage (e.g. `90%`, `90q`, `qa=0.9`, "all passed" -> 1.0, "all failed" -> 0.0)
- `review_iterations`: any integer near "review(s)", "r" (shorthand), `reviews=N`
- `time_hours`: any number near "hour(s)", "hrs", "h" (shorthand), `hours=N`

After extraction, only ask for fields that could not be parsed. Never re-ask for a field that was successfully extracted. Prompt only for what is still missing:

> Missing `<field>` for this cycle. Example: `/prodmasterai cycle done -- 5 tasks, QA 85%, 2 reviews, 3 hours`

## Process

### 1. Calculate Velocity

```
velocity_tasks_per_week = (tasks_completed / time_hours) * 40
```
Round to 1 decimal.

**Zero guard:** If `time_hours = 0` or was not provided, set `velocity_tasks_per_week = null` and note `"velocity not calculable (0 hours logged)"` in the cycle entry. Do not divide by zero.

### 2 + 3. Write in Parallel

Run steps 2 and 3 simultaneously -- they write to different files with no shared state:

**Step 2 (parallel)** -- Append the cycle entry to `skill-performance.md` (internal format, do not show the raw YAML to the user).

`blocker_age_days_avg`: Read `## Blockers` in `project-context.md`. For each open blocker, compute `(today - blocker_date)` in days. Average all values. If no blockers: `0`.

`blockers_encountered`: Record the integer value from the input's `blockers_encountered` field (count of `research-resolve` escalations this cycle). If absent or not provided, record `0`. This is distinct from `blockers` (open blocker count) and `blocker_age_days_avg`.

**Step 3 (parallel)** -- Increment counter in `project-context.md`:
Read frontmatter (between first `---` and second `---`). Add the cycle's `tasks_completed` count (the integer from this cycle's input) to the current `total_tasks_completed:` value. Rewrite frontmatter block only -- do not touch the rest of the file.

### 4 + 5. Hand Off and Threshold Check in Parallel

Run steps 4 and 5 simultaneously -- they are independent:

**Step 4 (parallel)** -- Pass the cycle data to `learn` (do not narrate this step to the user).

**Completion message to user** (after both steps 2 and 3 complete):

> Cycle logged for **<feature>** -- <tasks_completed> tasks, QA <qa_pass_rate as %>%, velocity <velocity_tasks_per_week | "not calculable"> tasks/week.
>
> Next: `/prodmasterai build [next feature]` to start the next feature | `/prodmasterai report` to see your dashboard

**Step 5 (parallel)** -- Compare updated `total_tasks_completed` to `last_evolved_at_task + evolve_every_n_tasks`. If threshold reached: write `evolution_threshold_reached: true` to the frontmatter of `memory/project-context.md` (alongside the `total_tasks_completed` update). The `prodmasterai` master skill reads this flag on its next invocation and owns the decision to invoke `evolve-self`. After evolve-self runs, it resets this flag to `false`. Do not invoke evolve-self directly from measure.

## Rules

- Always record even for failed/partial cycles (qa_pass_rate reflects reality)
- Append only -- never modify existing entries
- Always hand off to `learn` — except on the `source: auto-session` path (Step 4 skipped; see Auto-Session Path above)
- **Never contribute anything upstream** -- upstream is exclusively evolve-self's responsibility
