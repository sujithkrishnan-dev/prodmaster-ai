# Task Queue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sequential auto-execution of queued goals — add tasks to a queue, run them one after another without user intervention.

**Architecture:** `memory/task-queue.md` (append-only YAML blocks) + `skills/task-queue/SKILL.md` (add/list/run sub-commands) + auto-advance hook in `skills/auto-pilot/SKILL.md`.

**Tech Stack:** Markdown skill files, Python pytest content-checks.

**Spec:** `docs/superpowers/specs/2026-03-21-task-queue-design.md`

---

## File Map

| File | Action |
|---|---|
| `memory/task-queue.md` | Create (seed) |
| `skills/task-queue/SKILL.md` | Create |
| `skills/auto-pilot/SKILL.md` | Modify — add Queue Advance section in Completion |
| `tests/test_skills.py` | Modify — add `"task-queue"` to ALL_SKILLS |
| `tests/test_memory.py` | Modify — add `"task-queue.md"` to REQUIRED_FILES |
| `memory/connectors/skill-pattern-manifest.md` | Modify — add entry |

---

## Task 1: Write failing tests

**Files:**
- Modify: `tests/test_skills.py`
- Modify: `tests/test_memory.py`

- [ ] **Step 1: Add to ALL_SKILLS**

In `tests/test_skills.py`, add `"task-queue"` to `ALL_SKILLS`.

- [ ] **Step 2: Add to REQUIRED_FILES**

In `tests/test_memory.py`, add `"task-queue.md"` to `REQUIRED_FILES` (after `"usage-log.md"`).

- [ ] **Step 3: Run tests — verify they fail**

```
python -m pytest tests/test_skills.py::test_skill_exists[task-queue] tests/test_skills.py::test_skill_frontmatter[task-queue] tests/test_memory.py::test_memory_file_exists[task-queue.md] -v
```

Expected: 3 FAIL

- [ ] **Step 4: Commit**

```bash
git add tests/test_skills.py tests/test_memory.py
git commit -m "test: add task-queue to ALL_SKILLS and REQUIRED_FILES (red)"
```

---

## Task 2: Create `memory/task-queue.md`

**Files:**
- Create: `memory/task-queue.md`
- Test: `test_memory_file_exists[task-queue.md]`

- [ ] **Step 1: Create seed file**

Exact content:
```markdown
# Task Queue
<!-- task-queue appends one YAML block per queued goal -->
<!-- auto-pilot advances queue on completion -->
```

- [ ] **Step 2: Run test**

```
python -m pytest tests/test_memory.py::test_memory_file_exists[task-queue.md] -v
```

Expected: 1 PASS

- [ ] **Step 3: Commit**

```bash
git add memory/task-queue.md
git commit -m "feat: add memory/task-queue.md seed file"
```

---

## Task 3: Create `skills/task-queue/SKILL.md`

**Files:**
- Create: `skills/task-queue/SKILL.md`
- Tests: `test_skill_exists[task-queue]`, `test_skill_frontmatter[task-queue]`

- [ ] **Step 1: Create the skill file**

```markdown
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
```

- [ ] **Step 2: Run tests**

```
python -m pytest tests/test_skills.py::test_skill_exists[task-queue] tests/test_skills.py::test_skill_frontmatter[task-queue] -v
```

Expected: 2 PASS

- [ ] **Step 3: Commit**

```bash
git add skills/task-queue/SKILL.md
git commit -m "feat: add task-queue skill"
```

---

## Task 4: Add queue-advance to `skills/auto-pilot/SKILL.md`

**Files:**
- Modify: `skills/auto-pilot/SKILL.md`

The Completion section currently ends after printing the completion card. Add a Queue Advance section after it.

- [ ] **Step 1: Read the current Completion section**

Read `skills/auto-pilot/SKILL.md`. Find the `## Completion` section — specifically after the completion card print block (step 4, the ``` block ending with "Run /prodmasterai resume…"```).

- [ ] **Step 2: Append Queue Advance section**

Immediately after the completion card code block, insert:

```markdown
### Queue Advance

After printing the completion card:
1. Read `memory/task-queue.md`. If the file does not exist, skip silently.
2. Find the entry with `status: running` whose `session_id` matches this session. If none, skip silently (queue not in use).
3. Update that entry: `status: done`, `completed_at: <ISO 8601 now>`.
4. Find the next entry with `status: pending`.
5. If found: update to `status: running`, `started_at: <now>`. Re-invoke `task-queue run` with that entry's goal. Do not print a separate "Queue advance" message — the auto-pilot completion card for the next task will appear naturally.
6. If none: output *"Queue complete. All tasks processed."*
```

- [ ] **Step 3: Commit**

```bash
git add skills/auto-pilot/SKILL.md
git commit -m "feat: add queue-advance to auto-pilot completion"
```

---

## Task 5: Update manifest + full suite

- [ ] **Step 1: Update skill-pattern-manifest.md**

Add entry after `### auto-pilot-revoke`:

```markdown
### task-queue
- trigger: /prodmasterai queue add
- trigger: /prodmasterai queue list
- trigger: /prodmasterai queue run
- reads: memory/task-queue.md, memory/project-context.md
- writes: memory/task-queue.md
```

- [ ] **Step 2: Run full suite**

```
python -m pytest tests/ -v --tb=short
```

Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add memory/connectors/skill-pattern-manifest.md
git commit -m "chore: add task-queue to skill-pattern-manifest"
```
