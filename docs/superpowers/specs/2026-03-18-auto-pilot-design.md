# Auto-Pilot + Resume Skills Design

> **Status:** Approved
> **Date:** 2026-03-18
> **Scope:** Two new skills (`auto-pilot`, `resume`) + `autonomous_mode` flag in project-context.md

---

## Goal

Enable fully autonomous unattended execution of the full ProdMaster AI pipeline (brainstorm -> plan -> implement -> test -> PR) without blocking on questions. When the user returns, a `resume` skill provides a full decision audit with per-decision rollback.

## Architecture

Three components, each with a single responsibility:

### 1. `autonomous_mode` flag (project-context.md)

Two new frontmatter fields added to `memory/project-context.md`:

```yaml
autonomous_mode: false
autonomous_session_id: ""
autonomous_max_iterations: 5
autonomous_confidence_floor: medium
```

- `autonomous_mode` — when `true`, every existing skill skips all blocking prompts and self-answers
- `autonomous_session_id` — non-empty value acts as a concurrency lock; prevents two auto-pilot runs at once
- `autonomous_max_iterations` — hard cap on dev-loop cycles per unattended session (user-configurable)
- `autonomous_confidence_floor` — minimum answer confidence required to proceed; below this auto-pilot parks (`low | medium | high`)

Every skill reads `memory/project-context.md` on entry. No skill rewrites are required beyond adding a single autonomous_mode check at each blocking prompt.

### 2. `skills/auto-pilot/SKILL.md`

Entry point for unattended execution. Frontmatter values: `generated: false`, `generated_from: ""`.

Triggers on (canonical list — must match prodmasterai routing table exactly):
- `/prodmasterai auto <goal>`
- "run autonomously"
- "work while I sleep"
- "unattended execution"
- "autonomously" (substring match)
- "while I sleep" (substring match)
- "unattended" (substring match)

Routing in `prodmasterai` uses substring matching: if any routing keyword appears anywhere in the user's input, the skill is invoked.

Responsibilities:
- Set `autonomous_mode: true` and `autonomous_session_id: YYYY-MM-DD-HHmm` in project-context.md
- Run context-aware self-brainstorm (see Self-Brainstorm Logic below)
- Invoke `orchestrate` -> full pipeline runs unattended
- On completion or hard stop: reset `autonomous_mode: false`, `autonomous_session_id: ""`
- Append session block to `memory/autonomous-log.md`
- Print completion card to user (or park notice if stuck)

### 3. `skills/resume/SKILL.md`

Audit and rollback skill. Frontmatter values: `generated: false`, `generated_from: ""`.

Triggers on (canonical list — must match prodmasterai routing table exactly):
- `/prodmasterai resume`
- "what happened while I was away"
- "show autonomous summary"
- "autonomous summary"

Responsibilities:
- Read last session from `memory/autonomous-log.md`
- Print structured completion card
- For each autonomous decision: offer Accept / Re-run
- Handle cascade resets for dependent decisions
- Archive reviewed sessions in autonomous-log.md

### 4. `memory/autonomous-log.md` (new file)

Header convention (matches all other memory files):
```
# Autonomous Session Log

Written by: auto-pilot. Read by: resume.
```

Append-only log. One block per session:

```yaml
---
session_id: YYYY-MM-DD-HHmm
goal: <feature goal>
status: complete | parked | stuck
branch: auto/<session_id>
pr_url: ""
tests_final: 0/0
reviewed: false
archived: false
decisions:
  - id: 1
    type: architecture | file_structure | library | test_strategy | approach
    question: <self-generated question>
    answer: <chosen answer>
    source: pattern | research | decide | default
    confidence: high | medium | low
    affected_files: []
    pre_action_sha: <git SHA>
    downstream_decision_ids: []
stuck_reason: ""
park_reason: ""
---
```

---

## Self-Brainstorm Logic

When auto-pilot runs its internal brainstorm, it follows four steps:

### Step 1 — Pattern Match

Match the feature goal against known archetypes (checked in priority order):

| Archetype | Keywords |
|---|---|
| `plugin-skill` | skill, capability, command, trigger, SKILL.md |
| `rest-api` | endpoint, API, route, CRUD, resource |
| `cli-tool` | CLI, command line, script, flag, argument |
| `dashboard` | report, dashboard, chart, visualise, metrics |
| `generic` | fallback — no keyword match |

Each archetype provides a pre-built question set and default answer strategy, filling ~70% of the spec automatically.

### Step 2 — Gap Questions

For remaining unknowns, auto-pilot generates up to 5 clarifying questions and answers each using this priority order:

1. `memory/patterns.md` — entries with matching context keyword
2. `memory/research-findings.md` — conclusions with `confidence: high` or `medium`
3. `decide` scoring against current project state
4. Hardcoded best-practice default (e.g., always TDD, follow existing file structure)

Every answer is logged with its source in the session's decisions list.

### Step 3 — Confidence Check

If any answer's source is `default` AND the answer affects a destructive or irreversible action:
- Park immediately, reset `autonomous_mode: false`
- Notify: *"Paused — couldn't confidently decide [X]. Please answer and re-run `/prodmasterai auto`."*

If overall `spec_confidence` falls below `autonomous_confidence_floor`:
- Park before touching any files
- Write park reason to autonomous-log.md

### Step 4 — Produce Mini Spec

Assembles answers into: goal, approach, file structure, test strategy.

Skips the full spec review loop. Instead runs a single internal structural check:
- All required fields present
- No logical contradictions between answers
- No answer conflicts with existing `memory/mistakes.md` entries

Logs `spec_confidence: high | medium | low` in the session block.

---

## Safeguards and Hard Limits

The following are never bypassed regardless of autonomous_mode setting:

| Limit | Enforcement |
|---|---|
| Never merge PRs | create only; no `gh pr merge` ever called |
| Never push to main/master | always branch `auto/<session_id>` |
| Never delete files or branches | no `rm`, `git branch -D`, or equivalent |
| Never run hook-blocked commands | pre-tool-bash.py hook applies in all modes |
| Never exceed autonomous_max_iterations | hard cap per session, default 5 |

**Stuck handling** (dev-loop escalated to research-resolve, both exhausted):
1. Commit all progress to `auto/<session_id>` branch
2. Reset `autonomous_mode: false`, `autonomous_session_id: ""`
3. Write blocker to `memory/project-context.md ## Blockers`
4. Write full stuck context to autonomous-log.md
5. Notify: *"Auto-pilot parked — stuck on [X]. Branch `auto/<session_id>` has progress so far. Run `/prodmasterai resume` to review."*

**Concurrency lock:** On startup, if `autonomous_session_id` is non-empty, exit immediately:
*"Auto-pilot already running (session: [id]). Run `/prodmasterai resume` to check status."*

**Stale lock recovery:** If `autonomous_session_id` is non-empty, `resume` checks whether the lock is stale using:
```bash
git log auto/<session_id> -1 --format=%ct
```
Parse the `autonomous_session_id` value (`YYYY-MM-DD-HHmm`) as a UTC datetime and convert to a Unix timestamp. If the branch's last commit timestamp is earlier than the `autonomous_session_id` datetime (or the branch does not exist), the lock is stale. `resume` offers: *"Found stale auto-pilot lock (session: [id]) — no active run detected. Clear lock and start fresh?"* On confirm: reset `autonomous_mode: false`, `autonomous_session_id: ""`. `auto-pilot` never clears a lock itself — only `resume` may do so, after user confirmation.

---

## Resume Skill: Audit and Rollback Flow

### Step 1 — Find Last Session
Read `memory/autonomous-log.md`, find most recent session block.
If none: *"No autonomous sessions found."*

### Step 2 — Print Completion Card

```
== Auto-Pilot Session: YYYY-MM-DD-HHmm ==
Goal:    <goal>
Status:  COMPLETE | PARKED | STUCK
Branch:  auto/<session_id>
PR:      <url or "not created">
Tests:   N/N passing

Decisions made (N):
  [1] <type>: <answer>
      Source: <source> | Confidence: <confidence>
  [2] ...
```

### Step 3 — Per-Decision Review

For each decision, offer:
- `[A]ccept` — keep as-is (default, Enter to accept)
- `[R]e-run` — reset this step and hand off to the relevant skill in normal attended mode

### Step 4 — Cascade Reset

If re-run chosen for a decision with downstream dependents:
- List all affected decisions: *"Re-running [1] will also reset decisions [3], [5]. Continue?"*
- On confirm:
  1. Ensure the working tree is on the `auto/<session_id>` branch: run `git checkout auto/<session_id>`. If the branch does not exist, notify the user: *"Branch auto/<session_id> no longer exists — cannot revert. The session history is preserved in autonomous-log.md for reference."* Abort the cascade reset.
  2. For each affected file in the decision's `affected_files` list, run `git checkout <pre_action_sha> -- <filepath>`.
  3. `affected_files` lists are guaranteed non-overlapping across decisions by construction — each file is recorded under the first decision that touches it, so no two decisions share a file path.
  4. Remove downstream decision entries from the session block in autonomous-log.md (mark each as `status: rolled_back`).
  5. Invoke the relevant skill in normal attended mode from that decision point.

### Step 5 — Archive

After review: mark session `reviewed: true`.
Sessions older than 30 days: marked `archived: true` (never deleted).

---

## prodmasterai Routing Updates

Add to the routing table in `skills/prodmasterai/SKILL.md`:

| Trigger keywords | Routes to |
|---|---|
| `auto`, `autonomously`, `run autonomously`, `while I sleep`, `work while I sleep`, `unattended`, `unattended execution` | `auto-pilot` |
| `resume`, `what happened while I was away`, `show autonomous summary`, `autonomous summary` | `resume` |

Note: Routing uses substring matching. The routing table keywords must cover all trigger phrases in each skill's `triggers:` frontmatter. Both lists above are the canonical definition — the SKILL.md triggers and the routing table keywords must match exactly (no addition or removal permitted at implementation time without updating both).

---

## New Files

| File | Purpose |
|---|---|
| `skills/auto-pilot/SKILL.md` | Autonomous execution entry point |
| `skills/resume/SKILL.md` | Audit and rollback skill |
| `memory/autonomous-log.md` | Append-only session decision log |

## Modified Files

| File | Change |
|---|---|
| `memory/project-context.md` | Add 4 new frontmatter fields: `autonomous_mode`, `autonomous_session_id`, `autonomous_max_iterations`, `autonomous_confidence_floor` |
| `skills/prodmasterai/SKILL.md` | Add routing entries for auto-pilot and resume (see prodmasterai Routing Updates) |
| `memory/connectors/skill-pattern-manifest.md` | Add `### auto-pilot` and `### resume` keyword entries |
| `tests/test_skills.py` | (a) Add `"auto-pilot"` and `"resume"` to `ALL_SKILLS` list. (b) Add `"generated_from:"` to the `REQUIRED_FIELDS` list (currently missing from all skill tests — this spec introduces it). |
| `tests/test_memory.py` | (a) Add `"autonomous-log.md"` to `REQUIRED_FILES` list. (b) In `test_project_context_has_counters`, append `"autonomous_mode:"`, `"autonomous_session_id:"`, `"autonomous_max_iterations:"`, `"autonomous_confidence_floor:"` to the existing `for f in [...]` list — same pattern as existing entries. (c) In `test_skill_pattern_manifest_has_all_skills`, add `"auto-pilot"` and `"resume"` to the hardcoded skills list on the `for skill in [...]` line. |
| `tests/test_integration.py` | (a) Add `"skills/auto-pilot/SKILL.md"` and `"skills/resume/SKILL.md"` to the hardcoded `required` list in `test_all_required_files_exist`. (b) Add `"memory/autonomous-log.md"` to the same `required` list. (c) In `test_project_context_counters`, append `"autonomous_mode:"`, `"autonomous_session_id:"`, `"autonomous_max_iterations:"`, `"autonomous_confidence_floor:"` to the existing `for f in [...]` list — same pattern as existing entries. (d) In `test_all_skill_frontmatter`, add `"generated_from:"` to the local `required` list (line 44 of the file — currently `["name:", "description:", "version:", "triggers:", "reads:", "writes:", "generated:"]`). |
| `docs/README.md` | Add two rows to the Skills table (after the `research-resolve` row): `\| \`auto-pilot\` \| "auto" / "run autonomously" / "work while I sleep" \| Full autonomous pipeline: brainstorm, plan, implement, test, and create PR — no questions asked. \|` and `\| \`resume\` \| "resume" / "what happened while I was away" \| Show autonomous session audit: every decision made, with rationale and per-decision rollback. \|` |
