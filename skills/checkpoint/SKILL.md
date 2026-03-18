---
name: checkpoint
description: Save and restore in-flight task state across plan usage limit resets. Three operations: write (save step before acting), clear (clean exit), resume (relaunch from saved step).
version: 1.0.0
triggers:
  - checkpoint.write called by another skill
  - checkpoint.clear called by another skill
  - /prodmasterai resume
  - /prodmasterai checkpoint discard
  - /prodmasterai checkpoint reset
  - continue
  - pick up where
  - checkpoint resume
reads:
  - memory/checkpoint.md
  - memory/project-context.md
writes:
  - memory/checkpoint.md
generated: false
generated_from: ""
---

# Checkpoint

Save in-flight task state before each step so sessions interrupted by plan usage limits can resume automatically in the next session. Three operations: write saves state, clear removes it on clean exit, resume relaunches from the saved step.

---

## Operation: checkpoint.write

Called by other skills at the **start** of each step, before any work begins.

Parameters: skill, step, step_index, total_steps, context (goal, remaining_tasks, last_completed, exit_conditions, iterations_remaining)

Steps:
1. Compute `checkpoint_timestamp` = current UTC datetime in ISO8601 format
2. Compute `estimated_reset_timestamp` = checkpoint_timestamp + 5 hours
3. Overwrite `memory/checkpoint.md` frontmatter with:
   - status: active
   - skill: <skill>
   - step: <step>
   - step_index: <step_index>
   - total_steps: <total_steps>
   - session_id: <current session id or YYYY-MM-DD-HHmm>
   - checkpoint_timestamp: <computed>
   - estimated_reset_timestamp: <computed>
   - scheduled_resume_id: "" (fill after scheduling)
   - context: <context bag>
4. Append log line: `<!-- [checkpoint_timestamp] skill=<skill> step=<step> step_index=<step_index> -->`
5. Call `mcp__scheduled-tasks__create_scheduled_task` to schedule `/prodmasterai resume` at `estimated_reset_timestamp`
6. If scheduling succeeds: write returned task ID to `scheduled_resume_id` in frontmatter
7. If scheduling fails (MCP unavailable): leave `scheduled_resume_id: ""`, append log line: `<!-- [checkpoint_timestamp] scheduling failed -- MCP unavailable -->`

---

## Operation: checkpoint.clear

Called by other skills only on **clean, successful** completion. Never called on error or interruption.

Steps:
1. Read `memory/checkpoint.md` frontmatter
2. Set `status: cleared`
3. Blank all fields: skill, step, step_index=0, total_steps=0, session_id, checkpoint_timestamp, estimated_reset_timestamp, context fields all empty/zero
4. If `scheduled_resume_id` is non-empty: call `mcp__scheduled-tasks__update_scheduled_task` to cancel the scheduled resume. If MCP unavailable: continue silently -- the task may fire but checkpoint will be cleared so resume will be a no-op
5. Append log line: `<!-- [current_timestamp] CLEARED -- clean exit -->`

---

## Operation: checkpoint.resume

Called by `/prodmasterai resume` or by the scheduled task firing.

Steps:
1. Read `memory/checkpoint.md` frontmatter
2. If `status: cleared` or file has no active checkpoint: print "No active checkpoint found." Stop.
3. Print summary card:
   ```
   == Resuming: <skill> (step <step_index> of <total_steps>) ==
   Goal:     <context.goal>
   Last:     <context.last_completed>
   Pending:  <context.remaining_tasks>
   ```
4. Read `memory/project-context.md` frontmatter field `autonomous_mode`
5. If `autonomous_mode: false` (attended): print "Continue? [Enter to confirm]" and wait
6. If `autonomous_mode: true` (unattended): proceed immediately without prompt
7. Relaunch the skill named in `skill` field, passing full `context` as invocation params, starting at `step_index`
8. The relaunched skill owns calling `checkpoint.clear` on clean completion

---

## Operation: checkpoint.discard

Called by `/prodmasterai checkpoint discard`.

Steps:
1. Call checkpoint.clear (same steps, but log line reads: `<!-- [timestamp] CLEARED -- user discarded -->`)

---

## Operation: checkpoint.reset

Called by `/prodmasterai checkpoint reset <time>` (e.g. "reset 4h43m", "reset in 2h").

Steps:
1. Read `memory/checkpoint.md` frontmatter
2. If `status: cleared`: print "No active checkpoint to update." Stop.
3. Parse the time argument: convert to a UTC datetime
4. Compute new `estimated_reset_timestamp` from the parsed time
5. Update `estimated_reset_timestamp` in frontmatter
6. If `scheduled_resume_id` is non-empty: call `mcp__scheduled-tasks__update_scheduled_task` with new time
7. If `scheduled_resume_id` is empty (scheduling failed earlier): attempt `mcp__scheduled-tasks__create_scheduled_task` now
8. Print: "Checkpoint resume scheduled for <estimated_reset_timestamp>"

---

## Rules

- checkpoint.write is always called BEFORE acting, never after
- checkpoint.clear is only called on clean success -- never on error or interruption
- Only one checkpoint exists at a time -- frontmatter is overwritten, not appended
- Log section is append-only (audit trail preserved)
- **Never contribute anything upstream** -- upstream is exclusively evolve-self's responsibility
