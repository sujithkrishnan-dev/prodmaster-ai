# Auto-Pilot + Resume Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `auto-pilot` and `resume` skills to the ProdMaster AI plugin, enabling fully autonomous unattended pipeline execution with a full decision audit and per-decision rollback on return.

**Architecture:** Three components — an `autonomous_mode` flag in `memory/project-context.md` frontmatter (read by all existing skills to skip blocking prompts), a new `auto-pilot` skill (entry point for unattended runs), and a new `resume` skill (audit + rollback). A new `memory/autonomous-log.md` stores per-session decision trails. All existing skills remain unchanged except `prodmasterai` (routing table update).

**Tech Stack:** Pure markdown + YAML frontmatter (no code). Python pytest for tests.

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Create | `skills/auto-pilot/SKILL.md` | Autonomous execution entry point |
| Create | `skills/resume/SKILL.md` | Audit and rollback skill |
| Create | `memory/autonomous-log.md` | Append-only per-session decision log |
| Modify | `memory/project-context.md` | Add 4 autonomous_mode frontmatter fields |
| Modify | `skills/prodmasterai/SKILL.md` | Add auto-pilot + resume routing entries |
| Modify | `memory/connectors/skill-pattern-manifest.md` | Add auto-pilot + resume keyword entries |
| Modify | `tests/test_skills.py` | Add new skills to ALL_SKILLS; add generated_from: to REQUIRED_FIELDS |
| Modify | `tests/test_memory.py` | Add autonomous-log.md to REQUIRED_FILES; extend counter + manifest tests |
| Modify | `tests/test_integration.py` | Add new files to required list; extend counter + frontmatter tests |
| Modify | `docs/README.md` | Add two rows to Skills table |

---

## Task 1: Add Failing Tests (RED)

**Files:**
- Modify: `tests/test_skills.py`
- Modify: `tests/test_memory.py`
- Modify: `tests/test_integration.py`

This task establishes the red state. All new assertions must fail before any implementation files are created.

- [ ] **Step 1: Update tests/test_skills.py**

Replace the file content:

```python
import os, pytest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(PLUGIN_ROOT, "skills")

ALL_SKILLS = ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
              "dev-loop", "research-resolve", "auto-pilot", "resume"]
REQUIRED_FIELDS = ["name:", "description:", "version:", "triggers:", "reads:", "writes:",
                   "generated:", "generated_from:"]

@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_skill_exists(skill):
    assert os.path.exists(os.path.join(SKILLS_DIR, skill, "SKILL.md"))

@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_skill_frontmatter(skill):
    path = os.path.join(SKILLS_DIR, skill, "SKILL.md")
    if not os.path.exists(path): pytest.skip("missing")
    content = open(path).read()
    assert content.startswith("---"), f"{skill}: must start with frontmatter"
    for f in REQUIRED_FIELDS:
        assert f in content, f"{skill}: missing '{f}'"

def test_evolve_self_has_research_template():
    assert os.path.exists(os.path.join(SKILLS_DIR, "evolve-self", "research-subagent-prompt.md"))

def test_evolve_self_has_pr_template():
    assert os.path.exists(os.path.join(SKILLS_DIR, "evolve-self", "pr-template.md"))
```

- [ ] **Step 2: Run test_skills.py to verify failures**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/test_skills.py -v 2>&1 | head -40
```

Expected: `test_skill_exists[auto-pilot]` FAIL, `test_skill_exists[resume]` FAIL. Existing tests still pass.

- [ ] **Step 3: Update tests/test_memory.py**

Replace the file content:

```python
import os, re, pytest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_DIR = os.path.join(PLUGIN_ROOT, "memory")

REQUIRED_FILES = [
    "patterns.md", "mistakes.md", "feedback.md", "research-findings.md",
    "skill-performance.md", "skill-gaps.md", "project-context.md",
    "evolution-log.md",
    "pending-upstream/.gitkeep",
    "pending-upstream/last-pr.txt",
    "connectors/README.md",
    "connectors/skill-pattern-manifest.md",
    "connectors/github.md",
    "connectors/slack.md",
    "connectors/linear.md",
    "blocker-research.md",
    "autonomous-log.md",
]

@pytest.mark.parametrize("filename", REQUIRED_FILES)
def test_memory_file_exists(filename):
    assert os.path.exists(os.path.join(MEMORY_DIR, filename)), f"Missing: memory/{filename}"

def test_project_context_has_counters():
    content = open(os.path.join(MEMORY_DIR, "project-context.md")).read()
    for f in [
        "total_tasks_completed:", "last_evolved_at_task:", "evolve_every_n_tasks:",
        "autonomous_mode:", "autonomous_session_id:",
        "autonomous_max_iterations:", "autonomous_confidence_floor:",
    ]:
        assert f in content, f"Missing: {f}"

def test_skill_performance_has_example():
    assert "example: true" in open(os.path.join(MEMORY_DIR, "skill-performance.md")).read()

def test_connectors_all_inactive():
    for c in ["github.md", "slack.md", "linear.md"]:
        content = open(os.path.join(MEMORY_DIR, "connectors", c)).read()
        assert "active: false" in content, f"{c} must default to active: false"

def test_skill_pattern_manifest_has_all_skills():
    content = open(os.path.join(MEMORY_DIR, "connectors", "skill-pattern-manifest.md")).read()
    for skill in ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
                  "dev-loop", "research-resolve", "auto-pilot", "resume"]:
        assert f"### {skill}" in content

def test_last_pr_txt_valid_timestamp():
    content = open(os.path.join(MEMORY_DIR, "pending-upstream", "last-pr.txt")).read().strip()
    assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', content)
```

- [ ] **Step 4: Update tests/test_integration.py**

In `test_all_required_files_exist`, the `required` list currently ends at `"EVOLUTION-LOG.md"`. Add three entries after `"memory/connectors/linear.md"`:

```python
"skills/auto-pilot/SKILL.md", "skills/resume/SKILL.md",
"memory/autonomous-log.md",
```

In `test_all_skill_frontmatter` (line 44), change the `required` list from:
```python
required = ["name:", "description:", "version:", "triggers:", "reads:", "writes:", "generated:"]
```
to:
```python
required = ["name:", "description:", "version:", "triggers:", "reads:", "writes:", "generated:", "generated_from:"]
```

In `test_project_context_counters`, change the `for f in [...]` list from:
```python
for f in ["total_tasks_completed:", "last_evolved_at_task:", "evolve_every_n_tasks:"]:
```
to:
```python
for f in [
    "total_tasks_completed:", "last_evolved_at_task:", "evolve_every_n_tasks:",
    "autonomous_mode:", "autonomous_session_id:",
    "autonomous_max_iterations:", "autonomous_confidence_floor:",
]:
```

- [ ] **Step 5: Run full test suite to confirm red state**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/ -v 2>&1 | tail -30
```

Expected failures (and only these):
- `test_skill_exists[auto-pilot]`
- `test_skill_exists[resume]`
- `test_skill_frontmatter[auto-pilot]`
- `test_skill_frontmatter[resume]`
- `test_memory_file_exists[autonomous-log.md]`
- `test_project_context_has_counters`
- `test_skill_pattern_manifest_has_all_skills`
- `test_all_required_files_exist`
- `test_all_skill_frontmatter`
- `test_project_context_counters`

All pre-existing tests must still pass.

- [ ] **Step 6: Commit red tests**

```bash
cd C:\Users\teame\Desktop\Plugin && git add tests/test_skills.py tests/test_memory.py tests/test_integration.py
git commit -m "test: add failing tests for auto-pilot + resume (RED)"
```

---

## Task 2: Create memory/autonomous-log.md

**Files:**
- Create: `memory/autonomous-log.md`

*Can be done in parallel with Tasks 3, 4, 5 after Task 1.*

- [ ] **Step 1: Create the file**

Create `memory/autonomous-log.md` with this exact content:

```markdown
# Autonomous Session Log

Written by: auto-pilot. Read by: resume.

<!-- Session blocks appended below.
---
session_id: YYYY-MM-DD-HHmm
goal: <feature goal>
status: complete | parked | stuck
branch: auto/<session_id>
pr_url: ""
tests_final: 0/0
reviewed: false
archived: false
spec_confidence: high | medium | low
decisions:
  - id: 1
    type: architecture | file_structure | library | test_strategy | approach
    question: <self-generated question>
    answer: <chosen answer>
    source: pattern | research | decide | default
    confidence: high | medium | low
    affected_files: []
    pre_action_sha: ""
    downstream_decision_ids: []
    status: active | rolled_back
stuck_reason: ""
park_reason: ""
---
-->
```

- [ ] **Step 2: Run memory file test to confirm it passes**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/test_memory.py::test_memory_file_exists[autonomous-log.md] -v
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add memory/autonomous-log.md
git commit -m "feat: add memory/autonomous-log.md"
```

---

## Task 3: Update project-context.md Frontmatter

**Files:**
- Modify: `memory/project-context.md`

*Can be done in parallel with Tasks 2, 4, 5 after Task 1.*

- [ ] **Step 1: Add the 4 new fields to the frontmatter block**

The current frontmatter block is:
```yaml
---
total_tasks_completed: 8
last_evolved_at_task: 0
evolution_threshold_reached: false
evolve_every_n_tasks: 10
last_evolved_date: 2026-03-18
first_run_complete: false
---
```

Replace it with:
```yaml
---
total_tasks_completed: 8
last_evolved_at_task: 0
evolution_threshold_reached: false
evolve_every_n_tasks: 10
last_evolved_date: 2026-03-18
first_run_complete: false
autonomous_mode: false
autonomous_session_id: ""
autonomous_max_iterations: 5
autonomous_confidence_floor: medium
---
```

- [ ] **Step 2: Run counter tests to confirm they pass**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/test_memory.py::test_project_context_has_counters tests/test_integration.py::test_project_context_counters -v
```

Expected: both PASS

- [ ] **Step 3: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add memory/project-context.md
git commit -m "feat: add autonomous_mode fields to project-context.md"
```

---

## Task 4: Create skills/auto-pilot/SKILL.md

**Files:**
- Create: `skills/auto-pilot/SKILL.md`

*Can be done in parallel with Tasks 2, 3, 5 after Task 1.*

- [ ] **Step 1: Create the file**

Create `skills/auto-pilot/SKILL.md` with this exact content:

```markdown
---
name: auto-pilot
description: Fully autonomous unattended execution -- runs the complete brainstorm->plan->implement->test->PR pipeline without blocking on questions. Every decision is logged with source and confidence. User returns to a completion card and full decision audit.
version: 1.0.0
triggers:
  - /prodmasterai auto <goal>
  - run autonomously
  - work while I sleep
  - unattended execution
  - autonomously
  - while I sleep
  - unattended
reads:
  - memory/project-context.md
  - memory/patterns.md
  - memory/research-findings.md
  - memory/mistakes.md
writes:
  - memory/project-context.md
  - memory/autonomous-log.md
generated: false
generated_from: ""
---

# Auto-Pilot

Run the full ProdMaster AI pipeline autonomously -- brainstorm, plan, implement, test, and create a PR -- without pausing for questions. Every decision is logged with its source and confidence. On completion, run `/prodmasterai resume` to review what was done and optionally re-run any decision manually.

---

## Pre-flight

### 1. Check concurrency lock

Read `memory/project-context.md` frontmatter. If `autonomous_session_id` is non-empty, exit:
*"Auto-pilot already running (session: [id]). Run `/prodmasterai resume` to check status."*

### 2. Set session lock

Generate `session_id: YYYY-MM-DD-HHmm` from current UTC datetime.
Update `memory/project-context.md` frontmatter:
- `autonomous_mode: true`
- `autonomous_session_id: <session_id>`

Read `autonomous_max_iterations` and `autonomous_confidence_floor` from frontmatter.

---

## Self-Brainstorm

### Step 1 -- Pattern Match

Match the feature goal against known archetypes (checked in priority order):

| Archetype | Keywords |
|---|---|
| plugin-skill | skill, capability, command, trigger, SKILL.md |
| rest-api | endpoint, API, route, CRUD, resource |
| cli-tool | CLI, command line, script, flag, argument |
| dashboard | report, dashboard, chart, visualise, metrics |
| generic | fallback -- no keyword match |

Each archetype has a pre-built question set and default answer strategy, filling ~70% of the mini spec automatically.

### Step 2 -- Gap Questions

Generate up to 5 clarifying questions for remaining unknowns. Answer each in priority order:
1. `memory/patterns.md` -- entries with matching context keyword
2. `memory/research-findings.md` -- conclusions with `confidence: high` or `medium`
3. `decide` scoring against current project state
4. Hardcoded best-practice default (e.g., always TDD, follow existing file structure)

Log each answer as a decision entry (id, type, question, answer, source, confidence, affected_files, pre_action_sha, downstream_decision_ids).

### Step 3 -- Confidence Check

If any answer's source is `default` AND affects a destructive or irreversible action:
- Reset `autonomous_mode: false`, `autonomous_session_id: ""`
- Append park block to `memory/autonomous-log.md`
- Notify: *"Paused -- couldn't confidently decide [X]. Please answer and re-run `/prodmasterai auto`."*
- Stop.

If overall confidence falls below `autonomous_confidence_floor`: park before touching files. Stop.

### Step 4 -- Produce Mini Spec

Assemble into: goal, approach, file structure, test strategy.
Internal check: all required fields present, no contradictions, no conflicts with `memory/mistakes.md`.
Log `spec_confidence: high | medium | low`.

---

## Execution

### Create branch

Create and checkout branch `auto/<session_id>`. This is the only branch auto-pilot ever commits to.

### Invoke orchestrate

Invoke `orchestrate` with the mini spec as the feature goal. `autonomous_mode: true` causes all blocking prompts across the pipeline to self-answer using the same priority order as Step 2.

Repeat dev-loop cycles up to `autonomous_max_iterations`. If `dev-loop` escalates to `research-resolve` and research-resolve also exhausts its attempts:
1. Commit all progress to `auto/<session_id>` branch
2. Reset `autonomous_mode: false`, `autonomous_session_id: ""`
3. Append blocker to `memory/project-context.md ## Blockers`
4. Append stuck session block to `memory/autonomous-log.md`
5. Notify: *"Auto-pilot parked -- stuck on [X]. Branch `auto/<session_id>` has progress. Run `/prodmasterai resume` to review."*
6. Stop.

---

## Completion

On successful pipeline completion:
1. Reset `autonomous_mode: false`, `autonomous_session_id: ""`
2. Append complete session block to `memory/autonomous-log.md`
3. Print completion card:

```
== Auto-Pilot Complete: <session_id> ==
Goal:    <goal>
Branch:  auto/<session_id>
PR:      <url or "not created -- run /prodmasterai update">
Tests:   N/N passing
Decisions: <N> made autonomously

Run `/prodmasterai resume` to review decisions and optionally re-run any step.
```

---

## Hard Limits

Never bypass these regardless of autonomous_mode:
- Never merge PRs -- create only
- Never push to main/master -- always branch `auto/<session_id>`
- Never delete files or branches
- Never run hook-blocked commands (pre-tool-bash.py applies in all modes)
- Never exceed `autonomous_max_iterations` cycles

---

## Rules

- All decisions must be logged to autonomous-log.md with source and confidence before acting
- Only `resume` may clear a stale lock -- auto-pilot never does
- Park rather than guess on default-sourced answers affecting irreversible actions
- **Never contribute anything upstream** -- upstream is exclusively evolve-self's responsibility
```

- [ ] **Step 2: Run skill tests to confirm they pass**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/test_skills.py::test_skill_exists[auto-pilot] tests/test_skills.py::test_skill_frontmatter[auto-pilot] -v
```

Expected: both PASS

- [ ] **Step 3: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add skills/auto-pilot/SKILL.md
git commit -m "feat: add auto-pilot skill"
```

---

## Task 5: Create skills/resume/SKILL.md

**Files:**
- Create: `skills/resume/SKILL.md`

*Can be done in parallel with Tasks 2, 3, 4 after Task 1.*

- [ ] **Step 1: Create the file**

Create `skills/resume/SKILL.md` with this exact content:

```markdown
---
name: resume
description: Show autonomous session audit -- every decision made during an auto-pilot run, with rationale, confidence, and per-decision rollback. Also detects and clears stale auto-pilot locks.
version: 1.0.0
triggers:
  - /prodmasterai resume
  - what happened while I was away
  - show autonomous summary
  - autonomous summary
reads:
  - memory/autonomous-log.md
  - memory/project-context.md
writes:
  - memory/autonomous-log.md
  - memory/project-context.md
generated: false
generated_from: ""
---

# Resume

Review what auto-pilot did while you were away. See every autonomous decision with its source and confidence. Optionally re-run any decision in normal attended mode.

---

## Step 1 -- Check for Stale Lock

Read `memory/project-context.md` frontmatter. If `autonomous_session_id` is non-empty, check whether the lock is stale:

```bash
git log auto/<session_id> -1 --format=%ct
```

Parse `autonomous_session_id` (`YYYY-MM-DD-HHmm`) as UTC Unix timestamp. If the branch's last commit timestamp is earlier than the `autonomous_session_id` datetime (or the branch does not exist): lock is stale.

Offer: *"Found stale auto-pilot lock (session: [id]) -- no active run detected. Clear lock and start fresh?"*
- Yes: reset `autonomous_mode: false`, `autonomous_session_id: ""` in project-context.md frontmatter
- No: exit

## Step 2 -- Find Last Session

Read `memory/autonomous-log.md`. Find the most recent session block (last `---` YAML block).
If none: *"No autonomous sessions found."* Stop.

## Step 3 -- Print Completion Card

```
== Auto-Pilot Session: <session_id> ==
Goal:    <goal>
Status:  COMPLETE | PARKED | STUCK
Branch:  auto/<session_id>
PR:      <pr_url or "not created">
Tests:   <tests_final>

Decisions made (<N>):
  [1] <type>: <answer>
      Source: <source> | Confidence: <confidence>
  [2] ...
```

## Step 4 -- Per-Decision Review

For each decision (in order), offer:
- `[A]ccept` -- keep as-is (default, Enter to accept)
- `[R]e-run` -- reset this step, hand off to the relevant skill in normal attended mode

If `[R]` chosen and `downstream_decision_ids` is non-empty:
- Warn: *"Re-running [N] will also reset decisions [X], [Y]. Continue?"*
- On confirm:
  1. Run `git checkout auto/<session_id>`. If branch missing: *"Branch no longer exists -- cannot revert. History preserved in autonomous-log.md."* Abort.
  2. For each file in `affected_files`: run `git checkout <pre_action_sha> -- <filepath>`.
     `affected_files` lists are non-overlapping across decisions by design.
  3. Mark each downstream decision `status: rolled_back` in the session block.
  4. Invoke the relevant skill in normal attended mode from that decision point.

## Step 5 -- Archive

After review completes: set `reviewed: true` on the session block.
Sessions with `archived: false` and date older than 30 days: set `archived: true`.
Never delete entries.

---

## Rules

- Only `resume` may clear a stale `autonomous_session_id` lock -- auto-pilot never does
- Rollback uses `git checkout <sha> -- <file>` -- never `git reset` or `git revert`
- `affected_files` lists are non-overlapping by construction -- safe to apply sequentially
- **Never contribute anything upstream** -- upstream is exclusively evolve-self's responsibility
```

- [ ] **Step 2: Run skill tests to confirm they pass**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/test_skills.py::test_skill_exists[resume] tests/test_skills.py::test_skill_frontmatter[resume] -v
```

Expected: both PASS

- [ ] **Step 3: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add skills/resume/SKILL.md
git commit -m "feat: add resume skill"
```

---

## Task 6: Update prodmasterai Routing, Manifest, and README

**Files:**
- Modify: `skills/prodmasterai/SKILL.md` (line ~38)
- Modify: `memory/connectors/skill-pattern-manifest.md` (append)
- Modify: `docs/README.md` (append to Skills table)

*All three are independent writes. Do them sequentially in this task.*

- [ ] **Step 1: Add routing entries to skills/prodmasterai/SKILL.md**

In the routing table in Step 1 (Parse Intent), after the row:
```
| "update plugin", "update", "publish", "contribute upstream" | `evolve-self` Phase 2 (upstream PR) |
```

Add these two rows:
```
| "auto", "autonomously", "run autonomously", "while I sleep", "work while I sleep", "unattended", "unattended execution" | `auto-pilot` |
| "resume", "what happened while I was away", "show autonomous summary", "autonomous summary" | `resume` |
```

- [ ] **Step 2: Append to memory/connectors/skill-pattern-manifest.md**

At the end of the file (after the `### research-resolve` block), append:

```markdown

### auto-pilot
keywords: [auto, autonomously, run autonomously, unattended, while I sleep, work while I sleep, autonomous pipeline, no questions, full pipeline auto]

### resume
keywords: [resume, what happened while I was away, autonomous summary, show autonomous summary, decision audit, rollback, auto-pilot review]
```

- [ ] **Step 3: Add two rows to docs/README.md Skills table**

After the `| \`research-resolve\` | ...` row, add:

```markdown
| `auto-pilot` | "auto" / "run autonomously" / "work while I sleep" | Full autonomous pipeline: brainstorm, plan, implement, test, and create PR — no questions asked. |
| `resume` | "resume" / "what happened while I was away" | Show autonomous session audit: every decision made, with rationale and per-decision rollback. |
```

- [ ] **Step 4: Run manifest test**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/test_memory.py::test_skill_pattern_manifest_has_all_skills tests/test_integration.py::test_manifest_covers_all_skills -v
```

Expected: both PASS

- [ ] **Step 5: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add skills/prodmasterai/SKILL.md memory/connectors/skill-pattern-manifest.md docs/README.md
git commit -m "feat: wire auto-pilot + resume into routing, manifest, and README"
```

---

## Task 7: Full Test Suite — Verify Green

- [ ] **Step 1: Run the complete test suite**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/ -v
```

Expected: all tests pass. Zero failures.

If any test fails, read the failure message carefully and fix the specific file before re-running. Do not move on until all tests are green.

- [ ] **Step 2: Commit (if any fixes were needed)**

```bash
cd C:\Users\teame\Desktop\Plugin && git add -A && git commit -m "fix: resolve remaining test failures"
```

Only run this step if fixes were needed in Step 1. If all tests passed first time, skip.
