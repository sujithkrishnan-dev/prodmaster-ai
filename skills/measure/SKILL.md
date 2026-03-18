---
name: measure
description: Use after every completed Superpowers cycle to record metrics. Captures velocity, QA pass rate, review iterations, and blockers. Always hand off to learn after recording.
version: 1.3.0
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

## Input

Receive cycle outcome (from `orchestrate` or user). Expected fields: feature name, tasks completed, QA pass rate (0.0–1.0), review iterations, time in hours, blockers encountered, patterns used, unhandled patterns.

Before asking for missing fields, attempt fuzzy extraction from the raw input string:

**Fuzzy Input Parsing**

Try each of the following formats in order until values are extracted:

| Input format | Example |
|---|---|
| Standard prose | `"5 tasks, 90% QA, 2 reviews, 3 hours"` |
| Shorthand | `"done — 5t 90q 2r 3h"` (t=tasks, q=QA%, r=reviews, h=hours) |
| Natural past-tense | `"finished 5 tasks, all passed, 1 review, took 2 hours"` |
| Key=value | `"cycle done: tasks=5 qa=0.9 reviews=2 hours=3"` |

Extraction rules:
- `tasks`: any integer preceded or followed by "task(s)", "t" (shorthand), `tasks=N`, or a standalone integer when context implies a count
- `qa_pass_rate`: any percentage (e.g. `90%`, `90q`, `qa=0.9`, "all passed" → 1.0, "all failed" → 0.0)
- `review_iterations`: any integer near "review(s)", "r" (shorthand), `reviews=N`
- `time_hours`: any number near "hour(s)", "hrs", "h" (shorthand), `hours=N`

After extraction, only ask for fields that could not be parsed. Never re-ask for a field that was successfully extracted. Prompt only for what is still missing:

> Missing `<field>` for this cycle. Example: `/prodmasterai cycle done — 5 tasks, QA 85%, 2 reviews, 3 hours`

## Process

### 1. Calculate Velocity

```
velocity_tasks_per_week = (tasks_completed / time_hours) * 40
```
Round to 1 decimal.

### 2 + 3. Write in Parallel

Run steps 2 and 3 simultaneously — they write to different files with no shared state:

**Step 2 (parallel)** — Append the cycle entry to `skill-performance.md` (internal format, do not show the raw YAML to the user).

`blocker_age_days_avg`: Read `## Blockers` in `project-context.md`. For each open blocker, compute `(today - blocker_date)` in days. Average all values. If no blockers: `0`.

**Step 3 (parallel)** — Increment counter in `project-context.md`:
Read frontmatter (between first `---` and second `---`). Add `tasks_completed` to `total_tasks_completed:`. Rewrite frontmatter block only — do not touch the rest of the file.

### 4 + 5. Hand Off and Threshold Check in Parallel

Run steps 4 and 5 simultaneously — they are independent:

**Step 4 (parallel)** — Pass the cycle data to `learn` (do not narrate this step to the user).

**Completion message to user** (after both steps 2 and 3 complete):

> Cycle logged for **<feature>** — <tasks_completed> tasks, QA <qa_pass_rate as %>%, velocity <velocity_tasks_per_week> tasks/week.
>
> Next: `/prodmasterai build [next feature]` to start the next feature | `/prodmasterai report` to see your dashboard

**Step 5 (parallel)** — Compare updated `total_tasks_completed` to `last_evolved_at_task + evolve_every_n_tasks`. If threshold reached: set a flag on the cycle outcome object (`evolution_threshold_reached: true`). The `prodmasterai` master skill owns the decision to invoke `evolve-self` — measure only records the flag. Do not invoke evolve-self directly from measure.

## Rules

- Always record even for failed/partial cycles (qa_pass_rate reflects reality)
- Append only — never modify existing entries
- Always hand off to `learn`
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
