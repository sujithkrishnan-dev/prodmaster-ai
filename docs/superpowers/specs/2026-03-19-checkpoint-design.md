# Checkpoint + Auto-Resume Design

> **Status:** Approved
> **Date:** 2026-03-19
> **Scope:** New `checkpoint` skill + `memory/checkpoint.md` + session-start hook update + prodmasterai routing + 3 skill updates (dev-loop, auto-pilot, orchestrate)

---

## Goal

Automatically save in-flight task state before each step so that when a plan usage limit interrupts a session, the next session can resume exactly where it left off -- with zero required user action in the happy path.

---

## Architecture

### Components

| Component | Type | Role |
|---|---|---|
| `skills/checkpoint/SKILL.md` | New skill | Three operations: write, clear, resume |
| `memory/checkpoint.md` | New memory file | Single active checkpoint record (overwritten on each write, cleared on clean finish) |
| `hooks/session-start.md` | Modified | Detect non-empty checkpoint on session open, inject resume banner |
| `skills/prodmasterai/SKILL.md` | Modified | New routing entries for resume, discard, and reset operations |
| `skills/dev-loop/SKILL.md` | Modified | Calls checkpoint.write before each iteration, checkpoint.clear on clean exit |
| `skills/auto-pilot/SKILL.md` | Modified | Calls checkpoint.write before each pipeline step, checkpoint.clear on completion |
| `skills/orchestrate/SKILL.md` | Modified | Calls checkpoint.write after each task dispatched |

### Data Flow

```
skill starts step
  -> checkpoint.write(skill, step, step_index, total_steps, context)
  -> mcp__scheduled-tasks creates resume task at estimated_reset_timestamp
  -> [limit hits mid-session]
  -> new session opens
  -> session-start reads checkpoint.md
  -> injects resume banner into context
  -> user runs /prodmasterai resume (or scheduled task fires)
  -> checkpoint.resume relaunches correct skill at correct step_index
  -> skill runs to completion
  -> checkpoint.clear + cancel scheduled task
```

---

## Checkpoint File Schema

File: `memory/checkpoint.md`

Holds exactly one active checkpoint at a time. Frontmatter is overwritten on each write. A log section is appended for audit trail.

```yaml
---
status: active | cleared
skill: dev-loop
step: iteration_3_of_5
step_index: 3
total_steps: 5
session_id: 2026-03-19-1430
checkpoint_timestamp: 2026-03-19T14:32:00Z
estimated_reset_timestamp: 2026-03-19T19:32:00Z
scheduled_resume_id: ""
context:
  goal: "build user authentication"
  remaining_tasks: ["task-4", "task-5", "task-6"]
  last_completed: "task-3: write failing tests -- DONE"
  exit_conditions: "tests_pass"
  iterations_remaining: 2
---
# Checkpoint Log
<!-- Appended on each write for audit trail -->
```

Fields:
- `status` -- `active` means interrupted; `cleared` means clean finish
- `skill` -- name of the skill that was running
- `step` -- human-readable step label
- `step_index` / `total_steps` -- numeric position for resume logic
- `checkpoint_timestamp` -- UTC ISO8601 time the checkpoint was written
- `estimated_reset_timestamp` -- `checkpoint_timestamp + 5 hours` (plan limit typical reset window)
- `scheduled_resume_id` -- ID returned by mcp__scheduled-tasks; empty if scheduling failed
- `session_id` -- audit logging only; not used by resume logic (resume uses step_index + context to relaunch)
- `context` -- skill-specific state bag; each skill defines what it stores here

---

## Three Operations

### checkpoint.write

Called at the **start** of each step, before any work begins.

1. Read current `memory/checkpoint.md` frontmatter
2. Overwrite frontmatter with new state (status: active, all fields)
3. Append one line to log section: `<!-- [timestamp] skill=X step=Y -->`
4. Compute `estimated_reset_timestamp = checkpoint_timestamp + 5 hours`
5. Call `mcp__scheduled-tasks__create_scheduled_task` to schedule `/prodmasterai resume` at `estimated_reset_timestamp`
6. Store returned task ID in `scheduled_resume_id`
7. If scheduling fails (MCP unavailable): continue silently, leave `scheduled_resume_id: ""`. Log one line to checkpoint log section: `<!-- [timestamp] scheduling failed -- MCP unavailable -->`

### checkpoint.clear

Called only on **clean, successful** completion of a skill run.

1. Set `status: cleared` in frontmatter
2. Blank all context fields
3. If `scheduled_resume_id` is non-empty: call `mcp__scheduled-tasks__update_scheduled_task` to cancel the scheduled resume. If MCP unavailable: continue silently -- the scheduled task may fire but checkpoint will be cleared so resume will be a no-op
4. Append one line to log: `<!-- [timestamp] CLEARED -- clean exit -->`

Never called if an error, limit, or unexpected stop interrupts work. Silence = checkpoint preserved.

### checkpoint.resume

Called by `/prodmasterai resume` or by the scheduled task.

1. Read `memory/checkpoint.md`
2. If `status: cleared` or file empty: "No active checkpoint found." Stop.
3. Print summary card:
   ```
   == Resuming: <skill> (step <step_index> of <total_steps>) ==
   Goal:     <context.goal>
   Last:     <context.last_completed>
   Pending:  <context.remaining_tasks>
   ```
4. In attended mode: "Continue? [Enter to confirm]"
5. In `autonomous_mode: true` (from project-context.md): resume immediately, no prompt
6. Relaunch the skill at `step_index` with `context` restored
7. The relaunched skill owns calling `checkpoint.clear` on clean completion

---

## Session-Start Hook Update

`hooks/session-start.md` -- after injecting standard context, read `memory/checkpoint.md`:

| Checkpoint state | Action |
|---|---|
| File missing or `status: cleared` | Normal session start -- no mention of checkpoint |
| `status: active`, age < 6 hours | Inject resume banner |
| `status: active`, age >= 6 hours | Inject resume banner + note "limit likely reset -- ready to resume" |

Age is computed as: `current_time - checkpoint_timestamp`.

**Resume banner injected into context:**
```
== Interrupted Task Detected ==
Skill:    <skill> (step <step_index> of <total_steps>)
Goal:     <context.goal>
Last:     <context.last_completed>
Pending:  <context.remaining_tasks>
Limit resets ~: <estimated_reset_timestamp>

Run `/prodmasterai resume` to continue, or `/prodmasterai checkpoint discard` to clear.
```

---

## prodmasterai Routing Updates

Add to the routing table in `skills/prodmasterai/SKILL.md`:

| Trigger keywords | Routes to |
|---|---|
| "resume", "continue", "pick up where", "checkpoint resume" | `checkpoint` resume mode |
| "checkpoint discard", "discard checkpoint", "clear checkpoint" | `checkpoint` clear operation |
| "checkpoint reset Xh Ym", "reset in", "limit resets in" | `checkpoint` update scheduled task with user-supplied reset time |

**Disambiguation rule for "resume" keyword** (replaces the existing simple `resume` -> `resume-skill` routing row):

```
"resume", "continue", "pick up where", "checkpoint resume":
  1. Read memory/checkpoint.md
  2. If file does not exist OR status == "cleared" -> route to `resume` skill (autonomous session audit)
  3. If status == "active" -> route to `checkpoint` resume mode
```

Replace the current prodmasterai routing row `| "resume", ... | resume |` with this conditional logic. The `resume` skill remains reachable -- it just requires the checkpoint to be cleared first.

The other two new routing rows are unconditional (no disambiguation needed):
- "checkpoint discard" / "discard checkpoint" / "clear checkpoint" -- always routes to `checkpoint` clear operation
- "checkpoint reset" / "reset in" / "limit resets in" -- always routes to `checkpoint` scheduled task update

**Resume banner injection order:** Inject the resume banner AFTER the standard session context block and BEFORE the final tip line (`*One command: /prodmasterai...*`). This ensures active project context appears first, then the interruption notice.

**Scheduled task command:** Schedule exactly `/prodmasterai resume` with no additional parameters. Only one checkpoint exists at a time (overwrite pattern), so no checkpoint ID is needed.

---

## Skill Updates: Checkpoint Write/Clear Calls

### dev-loop

Add at the start of each iteration loop body:
```
checkpoint.write(
  skill: "dev-loop",
  step: "iteration_N_of_M",
  step_index: N,
  total_steps: M,
  context: { goal, exit_conditions, iterations_remaining, last_test_result }
)
```
Add at the clean exit point (all exit conditions met):
```
checkpoint.clear
```

### auto-pilot

Add before each pipeline stage (brainstorm, plan, implement, test, PR):
```
checkpoint.write(
  skill: "auto-pilot",
  step: "<stage_name>",
  step_index: N,
  total_steps: 5,
  context: { goal, session_id, decisions_made, current_stage, remaining_stages }
)
```
Add at completion card print:
```
checkpoint.clear
```

### orchestrate

Add after each task is dispatched:
```
checkpoint.write(
  skill: "orchestrate",
  step: "task_N_dispatched",
  step_index: N,
  total_steps: total_task_count,
  context: { goal, completed_tasks, pending_tasks, current_task }
)
```
Add when all tasks are dispatched and confirmed complete:
```
checkpoint.clear
```

---

## New Files

| File | Purpose |
|---|---|
| `skills/checkpoint/SKILL.md` | Checkpoint skill: write, clear, resume operations |
| `memory/checkpoint.md` | Active checkpoint record (single entry, overwrite pattern) |

## Modified Files

| File | Change |
|---|---|
| `hooks/session-start.md` | Add checkpoint detection + resume banner injection |
| `skills/prodmasterai/SKILL.md` | Add 3 new routing entries + disambiguation rule |
| `skills/dev-loop/SKILL.md` | Add checkpoint.write before each iteration + checkpoint.clear on exit |
| `skills/auto-pilot/SKILL.md` | Add checkpoint.write before each stage + checkpoint.clear on completion |
| `skills/orchestrate/SKILL.md` | Add checkpoint.write after each task dispatch + checkpoint.clear on all done |
| `tests/test_skills.py` | Add `"checkpoint"` to `ALL_SKILLS` list (line 6) |
| `tests/test_memory.py` | Add `"checkpoint.md"` to `REQUIRED_FILES` list |
| `tests/test_integration.py` | (a) Add `"skills/checkpoint/SKILL.md"` and `"memory/checkpoint.md"` to the `required` list in `test_all_required_files_exist`. (b) No frontmatter or counter changes needed. |
| `memory/connectors/skill-pattern-manifest.md` | Add checkpoint entry |
| `docs/README.md` | Add checkpoint row to Skills table |
