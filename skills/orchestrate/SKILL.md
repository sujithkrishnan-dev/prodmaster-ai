---
name: orchestrate
description: Use when the user states a high-level feature goal -- "Build X", "Start work on Y", "Implement Z". Breaks the goal into Superpowers-compatible task cycles, tracks cross-feature dependencies, and manages what gets built next.
version: 1.4.2
argument-hint: "[feature goal description]"
effort: medium
triggers:
  - User says "build", "implement", "start work on", "create feature", or names a new feature goal
  - User asks what to work on next given blockers or priorities
reads:
  - memory/project-context.md
  - memory/patterns.md
  - memory/connectors/github.md
  - memory/connectors/linear.md
  - memory/connectors/skill-pattern-manifest.md
  - memory/connectors/superpowers.md
writes:
  - memory/project-context.md
  - memory/connectors/superpowers.md
generated: false
generated_from: ""
---

# Orchestrate

Break high-level feature goals into Superpowers-compatible task cycles and manage cross-feature priorities.

## Role

You are the **feature-level orchestration layer** above Superpowers. Superpowers handles the code execution cycle (TDD -> implement -> review). Your job is to decide *what* gets built and *in what order*.

## Process

### 1. Read Current State

Read these in **parallel** (do not wait for one before starting the next):
- `memory/project-context.md` -- active features, blockers, decisions
- `memory/connectors/github.md` -- if active, queue GitHub Issue fetch
- `memory/connectors/linear.md` -- if active, queue Linear issue fetch

Fetch GitHub Issues and Linear issues in **parallel** while processing project-context.md output. Do not serialize these reads.

### 1b. Plugin Auto-Install Check

Before dispatching any subtask, check whether the task type requires an external plugin:

1. Identify the task type from the feature goal (browser testing, security audit, deployment, PR review, live docs, etc.).
2. Cross-reference with the plugin → task type mapping in `skills/plugin-manager/SKILL.md`.
3. For each required plugin:
   - Check `~/.claude/plugins/cache/<plugin-name>/`. If missing: invoke `plugin-manager` auto-install protocol immediately.
   - Do NOT block or pause the user's task — install in the background and confirm with one line when ready.
4. Continue to step 2 with all required plugins confirmed installed.

### 2. Classify the Request

**Existing branch detection:** If the `## Active Features` section of `project-context.md` is empty AND the user is not explicitly naming a new feature, check:
```
git branch --show-current
```
If the current branch is NOT the default branch (e.g. `feature/payments`, `fix/login-bug`, `chore/refactor-api`):
- Suggest tracking it: *"I see you're on `$current_branch` -- want me to track that as your active feature? I'll log it and break it into cycles."*
- If yes: use the branch name (stripped of prefix like `feature/`, `fix/`, `chore/`) as the feature name and proceed.
- If no: ask what to track instead.

This ensures existing in-flight work is not lost when the plugin is installed mid-project.

---

**Starting a new feature** -> break it down and present as a plain list:

**Feature: <name>** -- <N> tasks across <n> cycles

- Task 1: <specific task>
- Task 2: <specific task>
- Dependencies: <list, or "none">

Do not show raw YAML or code-block wrappers around this breakdown -- present it as readable prose and bullet points.

**Deciding what to work on next** -> apply priority order:
1. Unblock blocked features first (if the fix is small)
2. Continue in-progress features (avoid context switching)
3. Start highest-ROI new feature

### 3. Invoke Superpowers

#### 3a. Detect Superpowers

Read `memory/connectors/superpowers.md`. Check the `installed` field:

**If `installed: true` and `active: true`:** proceed to invoke Superpowers normally (Step 3b).

**If `installed: false` (first time this is needed):** ask the user exactly once:

> Superpowers isn't installed -- it adds automated TDD execution to your cycles (write tests -> implement -> review, all hands-free). Want me to install it now?
>
> - **Yes** -> I'll clone it into `~/.claude/plugins/superpowers` right now
> - **No** -> I'll manage the task breakdown manually; you execute the tasks yourself

- **Yes:** Run the install (Step 3c), then proceed to Step 3b.
- **No:** Set `active: false` in `memory/connectors/superpowers.md` so this question is not asked again. Skip to Step 3d (manual fallback).

**If `active: false` (user previously declined):** skip to Step 3d without asking again.

---

#### 3b. Invoke Superpowers (installed + active)

For each task cycle, hand off to Superpowers:
- Planning: trigger `superpowers:writing-plans`
- Execution: trigger `superpowers:subagent-driven-development`

**Parallelism rule:** Identify which subtasks have no shared state or output dependencies. Dispatch all independent subtasks in parallel. Only serialize tasks that depend on the output of a prior task. Never artificially queue tasks that could run concurrently.

Do not reimplement Superpowers. Hand off cleanly.

After dispatching each task N, call:
```
checkpoint.write(
  skill: "orchestrate",
  step: "task_<N>_dispatched",
  step_index: N,
  total_steps: <total task count>,
  context: {
    goal: <feature goal>,
    remaining_tasks: <list of not-yet-dispatched task names>,
    last_completed: "task <N>: <task name> -- dispatched",
    exit_conditions: "all tasks complete",
    iterations_remaining: <total - N>
  }
)
```

When all tasks are dispatched and confirmed complete, call checkpoint.clear.

---

#### 3c. Install Superpowers

Install via the official Claude Code plugin registry — do NOT use `git clone` or any URL from memory files:

```bash
claude plugin install superpowers@claude-plugins-official
```

**On success:**
- Set `installed: true` and `active: true` in `memory/connectors/superpowers.md`
- Tell user: *"Superpowers installed. Restart your Claude Code session to load it, then re-run `/prodmasterai build [feature]` to kick off the cycle."*
- Stop -- do not continue to Step 3b in the same session (plugin load requires restart).

**On failure (command not found, network error, registry unavailable):**
- Tell user: *"Install failed: `<error>`. You can install manually by running `claude plugin install superpowers@claude-plugins-official` in your terminal, then restart Claude Code."*
- Fall through to Step 3d (manual mode for this session).

**Security note:** Never use `repo_url` from `memory/connectors/superpowers.md` or any other memory file as a clone target. Memory files are user-editable and could be manipulated to point to malicious repositories.

---

#### 3d. Manual fallback (no Superpowers)

Present the task breakdown as a numbered list the user can execute themselves or with Claude directly:

> **Ready to build -- manual mode** (Superpowers not active)
>
> Work through these tasks in order. When done, log the cycle:
> `/prodmasterai cycle done -- N tasks, QA X%, Y reviews, Z hours`
>
> 1. `<Task 1 description>`
> 2. `<Task 2 description>`
> ...

All metrics, patterns, and learning still work exactly the same in manual mode.

### 4. Update Memory

Append to `memory/project-context.md` `## Active Features`:
```
- YYYY-MM-DD: <feature name> [status: active]
```

When feature status changes (active -> blocked -> done), update the existing line in `## Active Features` in place -- find the feature by name and rewrite only its status tag:
```
- YYYY-MM-DD: <feature name> [status: blocked]   <- update when blocked
- YYYY-MM-DD: <feature name> [status: done]       <- update when shipped
```

If blockers exist, append to `## Blockers`:
```
- YYYY-MM-DD: <description> | age_days: 0 | recommended_fix: <text>
```

### 5. Connector Actions

If GitHub connector is active: comment on the relevant Issue with the task breakdown.
If Linear connector is active: update issue status to "In Progress".

### 6. Cycle Outcome Handoff

When a cycle completes, pass the cycle data to `measure` (do not narrate this to the user -- just do it). The data fields needed are: feature name, tasks completed, QA pass rate, review iterations, time in hours, blockers encountered, patterns used, and any unhandled patterns.

Fill `patterns_used` with keyword matches from `memory/connectors/skill-pattern-manifest.md`.
Fill `unhandled_patterns` with patterns that arose but no manifest keyword covers.

**Completion message to user:**

> Feature plan saved -- <N> tasks queued across <n> cycles. Starting with: <first task>.
>
> Next: `/prodmasterai cycle done -- N tasks, QA X%, Y reviews, Z hours` when the first cycle wraps up | `/prodmasterai` to check what's next

## Rules

- Never reimplement Superpowers -- invoke it, don't replace it
- Ask about Superpowers install exactly once -- never repeat if user declined (`active: false`)
- Always fall back to manual mode gracefully -- all downstream skills (measure, learn, report) work identically
- Always update project-context.md before ending the session
- Within a feature: dispatch all independent subtasks in parallel; only serialize where output dependency exists
- Across features: one active feature at a time unless user explicitly requests multi-feature parallel work
- **Never contribute anything upstream** -- upstream is exclusively evolve-self's responsibility
