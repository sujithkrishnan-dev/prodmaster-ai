---
name: orchestrate
description: Use when the user states a high-level feature goal — "Build X", "Start work on Y", "Implement Z". Breaks the goal into Superpowers-compatible task cycles, tracks cross-feature dependencies, and manages what gets built next.
version: 1.0.0
triggers:
  - User says "build", "implement", "start work on", "create feature", or names a new feature goal
  - User asks what to work on next given blockers or priorities
reads:
  - memory/project-context.md
  - memory/patterns.md
  - memory/connectors/github.md
  - memory/connectors/linear.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# Orchestrate

Break high-level feature goals into Superpowers-compatible task cycles and manage cross-feature priorities.

## Role

You are the **feature-level orchestration layer** above Superpowers. Superpowers handles the code execution cycle (TDD → implement → review). Your job is to decide *what* gets built and *in what order*.

## Process

### 1. Read Current State

Read `memory/project-context.md`:
- Active features and their statuses
- Open blockers and their ages
- Recent decisions

If GitHub connector is active (`memory/connectors/github.md` has `active: true`): read open Issues to augment the feature list.
If Linear connector is active: read open Linear issues.

### 2. Classify the Request

**Starting a new feature** → break it down:
```
Feature: <name>
Subtasks:
  1. <specific task> → Superpowers cycle
  2. <specific task> → Superpowers cycle
Dependencies: <list>
Estimated cycles: <n>
```

**Deciding what to work on next** → apply priority order:
1. Unblock blocked features first (if the fix is small)
2. Continue in-progress features (avoid context switching)
3. Start highest-ROI new feature

### 3. Invoke Superpowers

For each task cycle, hand off to Superpowers:
- Planning: trigger `superpowers:writing-plans`
- Execution: trigger `superpowers:subagent-driven-development`

Do not reimplement Superpowers. Hand off cleanly.

### 4. Update Memory

Append to `memory/project-context.md` `## Active Features`:
```
- YYYY-MM-DD: <feature name> [status: active]
```

If blockers exist, append to `## Blockers`:
```
- YYYY-MM-DD: <description> | age_days: 0 | recommended_fix: <text>
```

### 5. Connector Actions

If GitHub connector is active: comment on the relevant Issue with the task breakdown.
If Linear connector is active: update issue status to "In Progress".

### 6. Cycle Outcome Handoff

When a cycle completes, construct this object and hand it to `measure`:

```yaml
feature: <feature name>
tasks_completed: <n>
qa_pass_rate: <0.0-1.0>
review_iterations: <n>
time_hours: <n>
blockers_encountered: <n>
patterns_used: []
unhandled_patterns: []
```

Fill `patterns_used` with keyword matches from `memory/connectors/skill-pattern-manifest.md`.
Fill `unhandled_patterns` with patterns that arose but no manifest keyword covers.

## Rules

- Never reimplement Superpowers — invoke it, don't replace it
- Always update project-context.md before ending the session
- One feature at a time unless user explicitly requests parallel work
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
