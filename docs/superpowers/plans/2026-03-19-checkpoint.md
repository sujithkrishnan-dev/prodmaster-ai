# Checkpoint + Auto-Resume Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a checkpoint skill that saves in-flight task state before each step so sessions interrupted by plan usage limits can resume automatically in the next session.

**Architecture:** A new `checkpoint` skill (write/clear/resume operations) writes state to `memory/checkpoint.md` before each step. The session-start hook detects an active checkpoint on session open and injects a resume banner. Three existing skills (dev-loop, auto-pilot, orchestrate) get checkpoint.write/clear calls added. prodmasterai routing gets a disambiguation rule so "resume" routes to checkpoint when one is active.

**Tech Stack:** Pure markdown + YAML frontmatter. Python pytest for tests. mcp__scheduled-tasks for auto-scheduling resumes.

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Modify | `tests/test_skills.py` | Add "checkpoint" to ALL_SKILLS |
| Modify | `tests/test_memory.py` | Add "checkpoint.md" to REQUIRED_FILES; extend manifest test |
| Modify | `tests/test_integration.py` | Add new files to required list |
| Create | `memory/checkpoint.md` | Single active checkpoint record |
| Create | `skills/checkpoint/SKILL.md` | Write/clear/resume operations |
| Modify | `hooks/session-start.md` | Checkpoint detection + resume banner injection |
| Modify | `skills/prodmasterai/SKILL.md` | Disambiguation rule + 3 new routing rows |
| Modify | `skills/dev-loop/SKILL.md` | checkpoint.write at iteration start, checkpoint.clear on exit |
| Modify | `skills/auto-pilot/SKILL.md` | checkpoint.write before each stage, checkpoint.clear on completion |
| Modify | `skills/orchestrate/SKILL.md` | checkpoint.write after task dispatch, checkpoint.clear on all done |
| Modify | `memory/connectors/skill-pattern-manifest.md` | Add checkpoint entry |
| Modify | `docs/README.md` | Add checkpoint row to Skills table |

---

## Task 1: Add Failing Tests (RED)

**Files:**
- Modify: `tests/test_skills.py`
- Modify: `tests/test_memory.py`
- Modify: `tests/test_integration.py`

- [ ] **Step 1: Add "checkpoint" to ALL_SKILLS in tests/test_skills.py**

Change line 6 from:
```python
ALL_SKILLS = ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
              "dev-loop", "research-resolve", "auto-pilot", "resume"]
```
to:
```python
ALL_SKILLS = ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
              "dev-loop", "research-resolve", "auto-pilot", "resume", "checkpoint"]
```

- [ ] **Step 2: Add "checkpoint.md" to REQUIRED_FILES and extend manifest test in tests/test_memory.py**

In `REQUIRED_FILES`, after `"autonomous-log.md"`, add:
```python
    "checkpoint.md",
```

In `test_skill_pattern_manifest_has_all_skills`, change the skills list from:
```python
    for skill in ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
                  "dev-loop", "research-resolve", "auto-pilot", "resume"]:
```
to:
```python
    for skill in ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
                  "dev-loop", "research-resolve", "auto-pilot", "resume", "checkpoint"]:
```

- [ ] **Step 3: Add new files to required list in tests/test_integration.py**

In `test_all_required_files_exist`, after the line `"memory/autonomous-log.md",` add:
```python
        "skills/checkpoint/SKILL.md",
        "memory/checkpoint.md",
```

- [ ] **Step 4: Run full test suite to confirm red state**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/ -v 2>&1 | tail -20
```

Expected failures (and only these):
- `test_skill_exists[checkpoint]`
- `test_skill_frontmatter[checkpoint]`
- `test_memory_file_exists[checkpoint.md]`
- `test_skill_pattern_manifest_has_all_skills`
- `test_all_required_files_exist`

All other tests must still pass.

- [ ] **Step 5: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add tests/test_skills.py tests/test_memory.py tests/test_integration.py
git commit -m "test: add failing tests for checkpoint skill (RED)"
```

---

## Task 2: Create memory/checkpoint.md

**Files:**
- Create: `memory/checkpoint.md`

*Can run in parallel with nothing — must complete before Task 3.*

- [ ] **Step 1: Create the file**

Create `memory/checkpoint.md` with this exact content:

```markdown
---
status: cleared
skill: ""
step: ""
step_index: 0
total_steps: 0
session_id: ""
checkpoint_timestamp: ""
estimated_reset_timestamp: ""
scheduled_resume_id: ""
context:
  goal: ""
  remaining_tasks: []
  last_completed: ""
  exit_conditions: ""
  iterations_remaining: 0
---
# Checkpoint Log

Written by: checkpoint. Read by: session-start, prodmasterai.

<!-- Entries appended below on each write. Format:
[YYYY-MM-DDThh:mm:ssZ] skill=X step=Y step_index=N
[YYYY-MM-DDThh:mm:ssZ] CLEARED -- clean exit
[YYYY-MM-DDThh:mm:ssZ] scheduling failed -- MCP unavailable
-->
```

- [ ] **Step 2: Run the memory file test**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/test_memory.py::test_memory_file_exists[checkpoint.md] -v
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add memory/checkpoint.md
git commit -m "feat: add memory/checkpoint.md seed file"
```

---

## Task 3: Create skills/checkpoint/SKILL.md

**Files:**
- Create: `skills/checkpoint/SKILL.md`

*Depends on Task 2 (references memory/checkpoint.md).*

- [ ] **Step 1: Create the file**

Create `skills/checkpoint/SKILL.md` with this exact content:

```markdown
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
```

- [ ] **Step 2: Run skill tests**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/test_skills.py::test_skill_exists[checkpoint] tests/test_skills.py::test_skill_frontmatter[checkpoint] -v
```

Expected: both PASS

- [ ] **Step 3: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add skills/checkpoint/SKILL.md
git commit -m "feat: add checkpoint skill"
```

---

## Task 4: Update session-start.md Hook

**Files:**
- Modify: `hooks/session-start.md`

*Can run in parallel with Tasks 5, 6, 7 after Task 3.*

- [ ] **Step 1: Read the current session-start.md**

Read `C:\Users\teame\Desktop\Plugin\hooks\session-start.md` to find the exact current content and insertion point.

- [ ] **Step 2: Add checkpoint detection block**

Append the following block to `hooks/session-start.md`, AFTER the existing content and BEFORE the final tip line (`*One command: /prodmasterai...*`):

```markdown
**Checkpoint Status:**
{{checkpoint_status}}
```

Then add a new section below the existing template variables block explaining how `checkpoint_status` is resolved:

```markdown
## Checkpoint Detection

After injecting active features and patterns above, read `memory/checkpoint.md` frontmatter:

- If file does not exist OR `status: cleared`: set `{{checkpoint_status}}` to empty string (inject nothing)
- If `status: active` AND age < 6 hours (age = current_time - checkpoint_timestamp): inject resume banner
- If `status: active` AND age >= 6 hours: inject resume banner + add note "Limit likely reset -- ready to resume now."

**Resume banner format:**
```
== Interrupted Task Detected ==
Skill:    <skill> (step <step_index> of <total_steps>)
Goal:     <context.goal>
Last:     <context.last_completed>
Pending:  <context.remaining_tasks>
Limit resets ~: <estimated_reset_timestamp>

Run `/prodmasterai resume` to continue, or `/prodmasterai checkpoint discard` to clear.
```
```

- [ ] **Step 3: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add hooks/session-start.md
git commit -m "feat: add checkpoint detection to session-start hook"
```

---

## Task 5: Update prodmasterai Routing

**Files:**
- Modify: `skills/prodmasterai/SKILL.md`

*Can run in parallel with Tasks 4, 6, 7 after Task 3.*

- [ ] **Step 1: Read the current routing table**

Read `C:\Users\teame\Desktop\Plugin\skills\prodmasterai\SKILL.md` lines 28-45 to find the exact current "resume" row.

- [ ] **Step 2: Replace "resume" routing row with disambiguation rule**

Find this row in the routing table:
```
| "resume", "what happened while I was away", "show autonomous summary", "autonomous summary" | `resume` |
```

Replace it with:
```
| "resume", "continue", "pick up where", "checkpoint resume", "what happened while I was away", "show autonomous summary", "autonomous summary" | `checkpoint` if `memory/checkpoint.md` has `status: active`; otherwise `resume` skill |
```

- [ ] **Step 3: Add two new routing rows**

After the row added in Step 2, add:
```
| "checkpoint discard", "discard checkpoint", "clear checkpoint" | `checkpoint` clear operation |
| "checkpoint reset", "reset in", "limit resets in" | `checkpoint` update scheduled task with user-supplied reset time |
```

- [ ] **Step 4: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add skills/prodmasterai/SKILL.md
git commit -m "feat: add checkpoint routing + disambiguation to prodmasterai"
```

---

## Task 6: Add Checkpoint Calls to dev-loop, auto-pilot, orchestrate

**Files:**
- Modify: `skills/dev-loop/SKILL.md`
- Modify: `skills/auto-pilot/SKILL.md`
- Modify: `skills/orchestrate/SKILL.md`

*Can run in parallel with Tasks 4, 5, 7 after Task 3.*

- [ ] **Step 1: Update dev-loop/SKILL.md**

In `skills/dev-loop/SKILL.md`, find the Step 4 iteration loop section. The line reads:
```
Each pass begins with: `iteration = iteration + 1`
```

After that line, add:
```
Before any other work in this pass, call:
```
checkpoint.write(
  skill: "dev-loop",
  step: "iteration_<iteration>_of_<max_iterations or ongoing>",
  step_index: iteration,
  total_steps: max_iterations (or 999 if uncapped),
  context: {
    goal: <task name / feature>,
    remaining_tasks: [],
    last_completed: "iteration <iteration-1> -- <last test result>",
    exit_conditions: <exit_when value>,
    iterations_remaining: <max_iterations - iteration if capped, else -1>
  }
)
```

Then find the Step 7 Loop Summary Output section. After the output block, add:
```
After printing the summary, call checkpoint.clear.
```

- [ ] **Step 2: Update auto-pilot/SKILL.md**

In `skills/auto-pilot/SKILL.md`, find the Execution section. Before the "Create branch" step, add:

```
Before each pipeline stage below, call checkpoint.write with:
- skill: "auto-pilot"
- step: "<stage_name>" (one of: brainstorm, plan, implement, test, pr)
- step_index: stage number (1=brainstorm, 2=plan, 3=implement, 4=test, 5=pr)
- total_steps: 5
- context: { goal: <goal>, remaining_tasks: <remaining stages>, last_completed: <last completed stage>, exit_conditions: "", iterations_remaining: 0 }
```

In the Completion section, after "Reset autonomous_mode: false, autonomous_session_id: """, add:
```
Call checkpoint.clear.
```

- [ ] **Step 3: Update orchestrate/SKILL.md**

Read `skills/orchestrate/SKILL.md` to find the task dispatch section. After each task is dispatched to a Superpowers cycle, add:

```
After dispatching task N, call:
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

After confirming all tasks are dispatched and complete, add:
```
Call checkpoint.clear.
```

- [ ] **Step 4: Commit all three skill updates**

```bash
cd C:\Users\teame\Desktop\Plugin && git add skills/dev-loop/SKILL.md skills/auto-pilot/SKILL.md skills/orchestrate/SKILL.md
git commit -m "feat: add checkpoint.write/clear calls to dev-loop, auto-pilot, orchestrate"
```

---

## Task 7: Update Manifest and README

**Files:**
- Modify: `memory/connectors/skill-pattern-manifest.md`
- Modify: `docs/README.md`

*Can run in parallel with Tasks 4, 5, 6 after Task 3.*

- [ ] **Step 1: Append checkpoint entry to skill-pattern-manifest.md**

At the end of `memory/connectors/skill-pattern-manifest.md` (after the `### resume` block), append:

```markdown

### checkpoint
keywords: [checkpoint, resume session, pick up where I left off, continue after limit, save progress, interrupted task, plan limit reset, auto-resume, checkpoint discard, checkpoint reset]
```

- [ ] **Step 2: Add checkpoint row to docs/README.md**

In the Skills table in `docs/README.md`, after the `| \`resume\` | ...` row, add:

```markdown
| `checkpoint` | "resume" / "continue" / "checkpoint reset Xh" | Save in-flight task state before each step. Resumes automatically after plan usage limit resets — with scheduled auto-resume. |
```

- [ ] **Step 3: Run manifest test**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/test_memory.py::test_skill_pattern_manifest_has_all_skills -v
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add memory/connectors/skill-pattern-manifest.md docs/README.md
git commit -m "feat: add checkpoint to manifest and README"
```

---

## Task 8: Full Test Suite — Verify Green

- [ ] **Step 1: Run the complete test suite**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/ -v
```

Expected: all tests pass. Zero failures.

If any test fails, read the failure message carefully and fix only the specific file before re-running.

- [ ] **Step 2: Commit fixes (only if needed)**

Stage only the specific files that needed fixing:

```bash
cd C:\Users\teame\Desktop\Plugin && git add <specific-files> && git commit -m "fix: resolve test failures after checkpoint implementation"
```

Skip this step if all tests passed on the first run.
