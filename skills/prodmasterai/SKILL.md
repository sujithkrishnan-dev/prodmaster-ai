---
name: prodmasterai
description: Master entry point -- invoked when user says /prodmasterai (with or without arguments). Reads current memory state and autonomously determines and executes the right action. Routes to orchestrate, measure, report, decide, learn, or evolve-self with no further prompting needed. Evolution is automatic -- runs a convergence loop (until clean) whenever the threshold is hit, no confirmation required.
version: 2.1.1
triggers:
  - User says /prodmasterai
  - User says /prodmasterai followed by any text
reads:
  - memory/project-context.md
  - memory/skill-performance.md
  - memory/skill-gaps.md
  - memory/usage-log.md
  - memory/pending-input.md
writes:
  - memory/usage-log.md
  - memory/pending-input.md
  - delegates to the invoked skill
generated: false
generated_from: ""
---

# ProdMaster AI -- Master Entry Point

This is the single command the user needs to know. Read context, decide the right action, execute it -- all without asking the user to remember which skill to invoke.

---

## Step 0 -- Log Invocation (synchronous, silent)

Append one line to `memory/usage-log.md`:
`- {ISO 8601 timestamp} | route: {classified route, or "unknown" if not yet classified} | processed: false`

If the file does not exist, create it with this header first:

    # Usage Log
    <!-- prodmasterai appends one entry per invocation -->
    <!-- session-start reads; prodmasterai marks processed:true after auto-measure fires -->

This write is synchronous -- complete it before continuing to Step 1.
Do not output anything to the user.

---

## Step 1 -- Parse Intent (if argument given)

If the user wrote `/prodmasterai <text>`, classify the text immediately:

| Pattern | Route to |
|---|---|
| "help", "what can you do", "show commands", "how does this work" | `help` |
| "pull latest", "take a pull", "sync code", "start dev", "smooth dev", "pre-flight", "ensure up to date", "ready to code", "let's get started", "beginning work", "check everything", "is everything ok", "set me up", "get me ready", "am I good to go", "before I start coding" | `smooth-dev` |
| "build X", "implement X", "start X", "work on X", "let's build", "i want to work on", "kick off", "create", "new feature", "add", "i want to add", "we should build", "can we build", "feature request", "i need to implement", "let's create", "spin up" | `orchestrate` |
| "cycle done", "N tasks, QA X%, Y reviews, Z hours", "just finished", "wrapped up", "completed", "logged N tasks", "done with", "that's done", "finished the cycle", "we're done", "shipping done", "sprint complete", "cycle complete", "done -- N tasks" | `measure` -> `learn` |
| "should we A or B", "what to prioritise", "pick between", "help me choose", "not sure whether to", "what's better", "trade-off between", "which is better", "A vs B", "compare A and B", "i can't decide", "pros and cons of" | `decide` |
| "report", "summary", "dashboard", "weekly", "show me stats", "how are we doing", "progress", "metrics", "what did we ship", "status update", "how's the project", "give me a summary", "what have we done" | `report` |
| "remember this", "log this", "that was wrong/right", "note that", "worth remembering", "lesson learned", "that was a mistake", "take note", "important learning", "write this down", "don't forget", "i learned that", "add to memory" | `learn` (feedback path) |
| "evolve", "improve yourself", "generate skill", "review plugin", "research plugin", "analyze plugin", "how can this be improved", "optimize", "optimize the plugin", "deep review", "audit the plugin", "quality pass", "run a review", "find issues", "check the plugin", "tighten up" | `evolve-self` Phase 1 (local only) |
| "update plugin", "update", "publish", "contribute upstream" | `evolve-self` Phase 2 (upstream PR) |
| "auto", "autonomously", "run autonomously", "while I sleep", "work while I sleep", "unattended", "unattended execution" | `auto-pilot` |
| "resume", "continue", "pick up where", "checkpoint resume", "what happened while I was away", "show autonomous summary", "autonomous summary" | `checkpoint` if `memory/checkpoint.md` has `status: active`; otherwise `resume` skill |
| "checkpoint discard", "discard checkpoint", "clear checkpoint" | `checkpoint` clear operation |
| "checkpoint reset", "reset in", "limit resets in" | `checkpoint` update scheduled task with user-supplied reset time |
| "token efficiency", "reduce tokens", "token audit", "I'm hitting limits", "too many tokens", "optimize tokens", "token-efficiency" | `token-efficiency` |
| "decision on X was good/bad", "that worked", "that failed", "update decision" | `decide` (outcome close path) |

**If classified:** invoke the matched skill immediately with the supplied text as input. Do not re-present a menu.

---

**Ambiguous input:** If the intent does not match any route with confidence, pick the most likely route and confirm with ONE question.

Before asking, run the **Idle Auto-Pilot Check** (see below). If escalation fires, skip the question.

Otherwise ask:
> "That sounds like [route] -- shall I [action]? (or tell me what you meant)"

Never reject input silently. Always offer the best guess. Route on confirmation without further prompting.

---

## Step 2 -- Read Context (if no argument or classification unclear)

Read these three files in parallel:
1. `memory/project-context.md` -- frontmatter gives `total_tasks_completed`, `last_evolved_at_task`, `evolve_every_n_tasks`; body gives Active Features list
2. `memory/skill-performance.md` -- last 3 entries
3. `memory/skill-gaps.md` -- count of `status: open` gaps

---

## Step 3 -- Auto-Decide

Evaluate in order (first match wins):

### A. Evolution threshold reached
`total_tasks_completed - last_evolved_at_task >= evolve_every_n_tasks` OR `evolution_threshold_reached: true` in project-context.md frontmatter
-> **Do not tell the user. Do not ask. Run immediately.**
-> After evolve-self completes, reset `evolution_threshold_reached: false` in project-context.md frontmatter.
-> Invoke `evolve-self` Phase 1 (convergence loop -- runs until all changed skills are clean). Show output only after convergence.
-> After evolve-self finishes, continue to check B/C/D and act on whatever is next.

### E. Auto-session queued

Precondition: session context contains `"Auto-session queued"` AND `memory/usage-log.md` has at least one `processed: false` line.
If precondition is not met (already fired this session, or no unprocessed entries), skip E entirely and evaluate B.

→ Count `processed: false` entries. Compute inferred metrics:
  - `tasks_completed` = count of lines with `route: orchestrate`, `route: decide`, or `route: learn` (minimum 1)
  - `qa_pass_rate` = 1.0
  - `review_iterations` = 0
  - `time_hours` = null
  - `feature` = last active feature name from `project-context.md ## Active Features`, or "mixed-session" if none
  - `blockers_encountered` = 0
  - `inferred` = true

→ Silently fire `measure` (auto-session path -- source: auto-session) with the above metrics.
→ After measure completes: rewrite ALL `processed: false` lines in `memory/usage-log.md` to `processed: true` (including any stale entries, regardless of age). `processed: true` means "will not be counted again", not "was included in a measure entry".
→ Do not tell the user that auto-measure fired. The cycle entry in `skill-performance.md` is the only record.
→ Continue: evaluate B/C/D on the now-updated state and handle the user's actual command.

### B. Active feature in progress
`## Active Features` section of project-context.md contains at least one non-empty feature entry.
-> Show a single-line status for each active feature (name + last known stage).
-> Run the **Idle Auto-Pilot Check** (see below). If escalation fires, skip the question.
-> Otherwise ask ONE question: *"Update on [most recently active feature]? (or say 'cycle done -- N tasks, QA X%, Y reviews, Z hours' to log a cycle)"*
-> Wait for response, then route:
  - Metrics given -> `measure` -> `learn`
  - Progress update -> continue `orchestrate` from current stage
  - "done" / "shipped" -> `measure` with completion data, mark feature complete

### C. No active features + 3 or more open skill gaps
-> Tell user: *"No active features. [N] skill gaps detected -- run /evolve to generate new skills, or tell me what to build next."*
-> Wait. Route response to `orchestrate` or `evolve-self`.

### D. Fresh / empty state (no active features, no gaps, <3 performance entries)

Read the `first_run_complete` field from the frontmatter of `memory/project-context.md`.

**If `first_run_complete: true`:** show the quick-start card:

```
ProdMaster AI is ready.

  Build something:   /prodmasterai build [feature name]
  Log a cycle:       /prodmasterai cycle done -- N tasks, QA X%, Y reviews, Z hours
  Weekly report:     /prodmasterai report
  Make a decision:   /prodmasterai should we A or B?
  Self-improve:      /evolve
```

**If `first_run_complete: false` (or absent):** run the onboarding flow below.

---

#### First-Run Onboarding Flow

Before asking anything, **detect the project context** by running these in parallel:
```
git log --oneline -1          <- does the repo have commits?
git branch --show-current     <- what branch are we on?
git remote show origin | grep "HEAD branch"  <- what is the default branch?
```

**Existing project detection:** If `git log` returns at least one commit AND the current branch differs from the default branch -> this is an **existing project already in flight**. Run the **Existing Project variant** below.

Otherwise -> run the **New Project variant**.

---

##### New Project variant

1. *"Welcome to ProdMaster AI -- let's get you set up in under a minute."*
2. Ask: *"What's the name of your project?"* -- store as `$project_name` (session only, never written).
3. Ask: *"What are you building first in $project_name?"* -- invoke `orchestrate` with the answer immediately.
4. After `orchestrate` returns: write `first_run_complete: true` to frontmatter.

---

##### Existing Project variant

1. *"ProdMaster AI is now tracking `$current_branch` -- let me catch up with where you are."*
2. Ask ONE question only: *"What are you currently working on in this branch? (I'll start tracking it as an active feature)"*
   - Take the answer and invoke `orchestrate` with it -- this logs it as an active feature in project-context.md.
   - If the branch name is descriptive (e.g. `feature/user-auth`, `fix/payment-bug`), pre-fill the suggestion: *"Looks like you're working on `user auth` -- is that right, or would you describe it differently?"*
3. After `orchestrate` returns: write `first_run_complete: true` to frontmatter.

**Do not ask about project history, past tasks, or metrics** -- let the user start logging from now. `total_tasks_completed` starts at 0 for new installs on existing repos; that is correct and expected.

---

**Rules for all onboarding variants:**
- Never exceed 3 questions total across both variants
- Do not show the quick-start card during onboarding -- user is already being routed to action
- Do not explain the plugin in detail -- one sentence greeting, then act

---

## Step 4 -- Execute

Invoke the target skill as if the user had called it directly -- pass all relevant context.
Do not describe what you are about to do. Just do it.

---

## Idle Auto-Pilot Check

Run this check whenever you are about to ask a blocking question (Step 3B and ambiguous-input path).

### Read
1. Read `memory/project-context.md` frontmatter: extract `auto_pilot_on_idle_after` (default: 2 if absent).
2. Read `memory/pending-input.md`: look for any YAML block (delimited by `---`) with `missed_sessions` present.

### Escalate
If any entry has `missed_sessions >= auto_pilot_on_idle_after`:
- Do NOT ask the question.
- Print: `"User has been away for {missed_sessions} sessions — switching to auto-pilot for: {entry.goal}"`
- Remove that entry from `memory/pending-input.md` (delete the YAML block and its surrounding `---` delimiters).
- Invoke `auto-pilot` with `goal: {entry.goal}`.

### Record (when no escalation)
When you are about to ask a blocking question and no entry currently exists for the same goal:
- Append a new YAML block to `memory/pending-input.md`:

```
---
goal: <feature name or topic being asked about>
question: <the exact question you are about to ask>
asked_on: <YYYY-MM-DD today>
missed_sessions: 0
---
```

If an entry for the same goal already exists (same `goal` value), do not append a duplicate — the existing entry is already being tracked.

### Clear (when user responds)
When the user gives a real answer to a question:
- Find the matching entry in `memory/pending-input.md` by `goal`.
- Delete that YAML block (including its surrounding `---` delimiters).
- Continue routing normally.

---

## Rules

- Never ask the user to remember skill names
- Never show a numbered menu -- route autonomously or ask exactly one question
- Always execute; never just explain
- If two conditions in Step 3 match, take the higher-priority one (A > E > B > C > D)
- **Parallelism:** whenever invoking multiple independent reads, writes, or skill dispatches, run them in parallel. Only serialize operations that have an explicit output dependency on a prior step. Never queue work that can run concurrently.
- **Never contribute anything upstream** -- upstream is exclusively evolve-self's responsibility
