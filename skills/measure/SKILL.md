---
name: measure
description: Use after every completed Superpowers cycle to record metrics. Captures velocity, QA pass rate, review iterations, and blockers. Always hand off to learn after recording.
version: 1.0.0
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

Receive cycle outcome (from `orchestrate` or user):

```yaml
feature: <name>
tasks_completed: <n>
qa_pass_rate: <0.0-1.0>
review_iterations: <n>
time_hours: <n>
blockers_encountered: <n>
patterns_used: []
unhandled_patterns: []
```

If any field is missing, ask for it before recording.

## Process

### 1. Calculate Velocity

```
velocity_tasks_per_week = (tasks_completed / time_hours) * 40
```
Round to 1 decimal.

### 2. Append Entry to skill-performance.md

```yaml
---
date: YYYY-MM-DD
feature: <value>
tasks_completed: <value>
velocity_tasks_per_week: <calculated>
qa_pass_rate: <value>
review_iterations: <value>
time_per_feature_hours: <value>
blockers: <value>
blocker_age_days_avg: 0
---
```

### 3. Increment Counter in project-context.md

Read the frontmatter of `memory/project-context.md` (the block between the first `---` and second `---`). Find `total_tasks_completed:` and add `tasks_completed` to it. Rewrite the frontmatter block only — do not touch the rest of the file.

### 4. Hand Off to learn

Pass the same cycle outcome object to `learn` immediately after recording.

### 5. Check Evolution Threshold

After `learn` completes: compare `total_tasks_completed` to `last_evolved_at_task + evolve_every_n_tasks` in project-context.md frontmatter. If threshold reached, notify the user: *"Evolution check threshold reached — run /evolve when ready."*

## Rules

- Always record even for failed/partial cycles (qa_pass_rate reflects reality)
- Append only — never modify existing entries
- Always hand off to `learn`
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
