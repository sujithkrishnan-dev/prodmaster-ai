---
name: prodmasterai
description: Master entry point — invoked when user says /prodmasterai (with or without arguments). Reads current memory state and autonomously determines and executes the right action. Routes to orchestrate, measure, report, decide, learn, or evolve-self with no further prompting needed.
version: 1.0.0
triggers:
  - User says /prodmasterai
  - User says /prodmasterai followed by any text
reads:
  - memory/project-context.md
  - memory/skill-performance.md
  - memory/skill-gaps.md
  - memory/patterns.md
  - memory/evolution-log.md
writes:
  - delegates to the invoked skill
generated: false
generated_from: ""
---

# ProdMaster AI — Master Entry Point

This is the single command the user needs to know. Read context, decide the right action, execute it — all without asking the user to remember which skill to invoke.

---

## Step 1 — Parse Intent (if argument given)

If the user wrote `/prodmasterai <text>`, classify the text immediately:

| Pattern | Route to |
|---|---|
| "build X", "implement X", "start X", "work on X" | `orchestrate` |
| "cycle done", "N tasks, QA X%, Y reviews, Z hours" | `measure` → `learn` |
| "should we A or B", "what to prioritise", "pick between" | `decide` |
| "report", "summary", "dashboard", "weekly" | `report` |
| "remember this", "log this", "that was wrong/right" | `learn` (feedback path) |
| "evolve", "improve yourself", "generate skill" | `evolve-self` |

**If classified:** invoke the matched skill immediately with the supplied text as input. Do not re-present a menu.

---

## Step 2 — Read Context (if no argument or classification unclear)

Read these three files in parallel:
1. `memory/project-context.md` — frontmatter gives `total_tasks_completed`, `last_evolved_at_task`, `evolve_every_n_tasks`; body gives Active Features list
2. `memory/skill-performance.md` — last 3 entries
3. `memory/skill-gaps.md` — count of `status: open` gaps

---

## Step 3 — Auto-Decide

Evaluate in order (first match wins):

### A. Evolution threshold reached
`total_tasks_completed - last_evolved_at_task >= evolve_every_n_tasks`
→ Tell user: *"Evolution threshold reached — running evolve-self now."*
→ Invoke `evolve-self` immediately. No confirmation needed.

### B. Active feature in progress
`## Active Features` section of project-context.md contains at least one non-empty feature entry.
→ Show a single-line status for each active feature (name + last known stage).
→ Ask ONE question: *"Update on [most recently active feature]? (or say 'cycle done — N tasks, QA X%, Y reviews, Z hours' to log a cycle)"*
→ Wait for response, then route:
  - Metrics given → `measure` → `learn`
  - Progress update → continue `orchestrate` from current stage
  - "done" / "shipped" → `measure` with completion data, mark feature complete

### C. No active features + 3 or more open skill gaps
→ Tell user: *"No active features. [N] skill gaps detected — run /evolve to generate new skills, or tell me what to build next."*
→ Wait. Route response to `orchestrate` or `evolve-self`.

### D. Fresh / empty state (no active features, no gaps, <3 performance entries)
→ Show the quick-start card:

```
ProdMaster AI is ready.

  Build something:   /prodmasterai build [feature name]
  Log a cycle:       /prodmasterai cycle done — N tasks, QA X%, Y reviews, Z hours
  Weekly report:     /prodmasterai report
  Make a decision:   /prodmasterai should we A or B?
  Self-improve:      /evolve
```

---

## Step 4 — Execute

Invoke the target skill as if the user had called it directly — pass all relevant context.
Do not describe what you are about to do. Just do it.

---

## Rules

- Never ask the user to remember skill names
- Never show a numbered menu — route autonomously or ask exactly one question
- Always execute; never just explain
- If two conditions in Step 3 match, take the higher-priority one (A > B > C > D)
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
