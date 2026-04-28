# Task Queue — Design Spec

**Date:** 2026-03-21
**Status:** approved

---

## Problem

Auto-pilot runs one goal at a time. There is no way to queue multiple goals and have them execute sequentially without the user manually re-triggering after each completes.

## Solution

A `memory/task-queue.md` file (append-only YAML blocks) and a `skills/task-queue/SKILL.md` skill with three sub-commands: `add`, `list`, and `run`. Auto-advance: when auto-pilot completes a session, it checks the queue for the next pending task and fires automatically.

---

## Scope

One new skill file, one new memory seed file, one modification to `skills/auto-pilot/SKILL.md` (add queue-advance hook to the Completion section).

---

## File Map

| File | Action |
|---|---|
| `memory/task-queue.md` | Create (seed) |
| `skills/task-queue/SKILL.md` | Create |
| `skills/auto-pilot/SKILL.md` | Modify — add queue-advance in Completion section |

---

## Data Format — `memory/task-queue.md`

```markdown
# Task Queue
<!-- task-queue appends one YAML block per queued goal -->
<!-- auto-pilot advances queue on completion -->
```

Each entry:
```yaml
---
id: tq-<YYYY-MM-DD-HHmm>
goal: <goal text>
status: pending | running | done | failed | skipped
added_at: <ISO 8601>
started_at: <ISO 8601 or null>
completed_at: <ISO 8601 or null>
session_id: <auto-pilot session_id or null>
---
```

**Rules:**
- Append only — never delete entries
- `status: running` means auto-pilot currently holds this task
- Only one entry may have `status: running` at a time
- `status: done` is written by auto-pilot on completion
- `status: failed` is written by auto-pilot on stuck/parked
- `status: skipped` is written by queue run when a task is manually bypassed

---

## Skill Behaviour — `skills/task-queue/SKILL.md`

### Sub-command: `add`

Triggers: `/prodmasterai queue add <goal>`, "add to queue", "queue this"

1. Generate `id: tq-<YYYY-MM-DD-HHmm>`
2. Append YAML block with `status: pending`, `added_at: <now>`, `started_at: null`, `completed_at: null`, `session_id: null`
3. Output: *"Added to queue: [goal] (id: tq-…)"*

### Sub-command: `list`

Triggers: `/prodmasterai queue list`, "show queue", "what's queued"

Read `memory/task-queue.md`. Group by status:
```
Task Queue
──────────
Running (1):
  [tq-…] Build auth feature

Pending (2):
  [tq-…] Add rate limiting
  [tq-…] Write integration tests

Done (3): … (collapsed — use /queue list --all to expand)
```

### Sub-command: `run`

Triggers: `/prodmasterai queue run`, "start queue", "run queue"

1. Check `project-context.md`: if `autonomous_session_id` non-empty → *"Auto-pilot already running. Finish current session first."* Stop.
2. Find the first entry with `status: pending` in `task-queue.md`.
3. If none: *"Queue is empty. Add tasks with `/prodmasterai queue add <goal>`."* Stop.
4. Update that entry: `status: running`, `started_at: <now>`.
5. Fire auto-pilot with that entry's `goal`.
6. On auto-pilot completion (or stuck/parked): update entry `status: done|failed`, `completed_at: <now>`, `session_id: <auto-pilot session_id>`.
7. Auto-advance: check for next `status: pending` entry. If found, repeat from step 4. If none: *"Queue complete. All tasks done."*

---

## Auto-Pilot Integration

Add to `skills/auto-pilot/SKILL.md` — Completion section, after the completion card:

```
## Queue Advance

After printing the completion card:
1. Read `memory/task-queue.md`.
2. Find the entry with `status: running` matching this `session_id`. Update to `status: done`, `completed_at: <now>`.
3. Find the next entry with `status: pending`.
4. If found: update to `status: running`, `started_at: <now>`. Fire `task-queue run` with that entry's goal.
5. If none: output *"Queue complete."*

If `task-queue.md` does not exist or no running entry matches this session_id, skip silently (queue not in use).
```

---

## Rules

- Queue is append-only — never delete or overwrite entries
- Only one `status: running` entry at a time
- Auto-advance never skips `failed` tasks — they stay as `failed` and the next `pending` is picked up
- If auto-pilot is `revoked`, the running task entry is updated to `status: failed` by auto-pilot-revoke

---

## Tests Required

1. `memory/task-queue.md` seed file exists with correct header
2. `skills/task-queue/SKILL.md` exists with correct frontmatter
3. `add` sub-command: appends a YAML block with `status: pending`
4. `list` sub-command: groups by status (running/pending/done)
5. `run` sub-command: finds first pending, fires auto-pilot
6. `run` sub-command: auto-advances to next pending on completion
7. `run` sub-command: reports queue empty when no pending entries
8. Auto-pilot Completion section includes queue-advance step
9. Queue-advance updates `status: done` on the completed task
10. Queue-advance skips silently when `task-queue.md` does not exist
