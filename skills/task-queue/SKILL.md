---
name: task-queue
description: Sequential task queue — add goals, list queue, run all automatically one after another.
version: 1.0.0
triggers:
  - /prodmasterai queue add
  - /prodmasterai queue list
  - /prodmasterai queue run
  - add to queue
  - queue this
  - show queue
  - what's queued
  - start queue
  - run queue
reads:
  - memory/task-queue.md
  - memory/project-context.md
writes:
  - memory/task-queue.md
generated: false
generated_from: ""
---

# Task Queue

Add goals to a queue and run them sequentially. Auto-pilot processes each task in order, advancing to the next automatically on completion.

---

## Entry Format

Each queue entry is a YAML block in `memory/task-queue.md`:

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

---

## Sub-command: add

Triggered by: `/prodmasterai queue add <goal>`, "add to queue", "queue this"

1. Generate `id: tq-<YYYY-MM-DD-HHmm>`.
2. Append YAML block to `memory/task-queue.md` with `status: pending`, `added_at: <now>`, `started_at: null`, `completed_at: null`, `session_id: null`.
3. Output: *"Added to queue: [goal] (id: tq-…)"*

---

## Sub-command: list

Triggered by: `/prodmasterai queue list`, "show queue", "what's queued"

Read `memory/task-queue.md`. Group entries by status and output:

```
Task Queue
──────────
Running (N):
  [tq-…] <goal>

Pending (N):
  [tq-…] <goal>
  [tq-…] <goal>

Done (N): <count> completed (use /queue list --all to expand)
Failed (N): <count> failed
```

If `task-queue.md` does not exist or is empty: *"Queue is empty. Add tasks with `/prodmasterai queue add <goal>`."*

---

## Sub-command: run

Triggered by: `/prodmasterai queue run`, "start queue", "run queue"

1. Read `memory/project-context.md` frontmatter. If `autonomous_session_id` is non-empty: *"Auto-pilot already running (session: [id]). Finish current session first."* Stop.
2. Read `memory/task-queue.md`. Find the first entry with `status: pending`.
3. If none: *"Queue is empty. No pending tasks."* Stop.
4. Update that entry in-place: `status: running`, `started_at: <now>`.
5. Fire `auto-pilot` with that entry's `goal` and record the `session_id`.
6. On completion: update entry `status: done`, `completed_at: <now>`, `session_id: <session_id>`.
   On stuck/parked: update entry `status: failed`, `completed_at: <now>`.
7. Auto-advance: find next entry with `status: pending`. If found, repeat from step 4.
   If none: *"Queue complete. All tasks processed."*

---

## Rules

- `memory/task-queue.md` is append-only — never delete entries
- Only one entry may have `status: running` at a time
- Auto-advance skips `failed` entries — picks up the next `pending`
- If auto-pilot is revoked mid-queue: the running entry is left as `status: running` (stale) — user must manually set to `failed` or `skipped` before re-running the queue
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
