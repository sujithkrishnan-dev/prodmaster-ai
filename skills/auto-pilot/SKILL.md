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

Before each pipeline stage (brainstorm, plan, implement, test, pr), call:
```
checkpoint.write(
  skill: "auto-pilot",
  step: "<stage_name>",
  step_index: <stage number: 1=brainstorm, 2=plan, 3=implement, 4=test, 5=pr>,
  total_steps: 5,
  context: {
    goal: <goal>,
    remaining_tasks: <remaining stages>,
    last_completed: <last completed stage>,
    exit_conditions: "",
    iterations_remaining: 0
  }
)
```

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
2. Call checkpoint.clear.
3. Append complete session block to `memory/autonomous-log.md`
4. Print completion card:

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
