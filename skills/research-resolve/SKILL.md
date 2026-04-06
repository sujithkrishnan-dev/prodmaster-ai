---
name: research-resolve
description: Use when a dev-loop or any development task is stuck with no progress after N iterations. Spins up an isolated git worktree, researches the failure, applies fixes autonomously, and merges back only on success.
version: 1.0.1
triggers:
  - dev-loop reaches stuck_threshold consecutive no-progress iterations
  - User says "research and resolve", "investigate failure", "loop is stuck", "can't make progress"
  - Standalone: /prodmasterai research-resolve
reads:
  - memory/project-context.md
  - memory/blocker-research.md
writes:
  - memory/blocker-research.md
  - memory/project-context.md
generated: false
generated_from: ""
---

# research-resolve

Autonomous fallback for stuck development loops. Spins up an isolated git worktree, researches the failure, applies fix hypotheses, and merges back only on success. Never modifies the main working tree until a fix is confirmed passing.

---

## Standalone Invocation

When called directly (not via `dev-loop`), `research-resolve` has no forwarded `exit_when` params. Success criterion: all tests pass (exit code 0). If no test suite is detected, ask the user: "What does success look like for this fix? (e.g., tests pass, file compiles, output matches X)"

---

## Process

### Step 1 -- Spin Up Isolated Worktree

```bash
git worktree add .worktrees/research-resolve-<timestamp> HEAD
```

A local branch `research-resolve-<timestamp>` is created pointing to HEAD. All fix attempts happen inside this worktree. The main working tree is never modified until a successful merge.

### Step 2 -- Research Phase (run in parallel)

Run all of these simultaneously:
- Analyse failing tests + error messages -> extract root cause hypotheses ranked by confidence
- Search codebase for related patterns
- Check `memory/blocker-research.md` for prior similar failures (treat missing file as empty -- non-fatal)
- If web search available: look up error signatures

### Step 3 -- Fix Loop (inside worktree)

The `exit_when`, `exit_logic`, and `llm_judge` values from the triggering `dev-loop` escalation payload are used to evaluate success. If `exit_when` is empty, success = all tests pass (exit code 0).

```
fix_attempt: 0
max_fix_attempts: 5  <- hard safety cap -- prevents runaway inner loop
```

Each attempt:
1. Apply highest-confidence fix hypothesis inside the worktree
2. Run tests inside the worktree
3. Evaluate success using forwarded exit conditions
4. Pass -> proceed to Step 4 (merge)
5. Still failing -> log the attempt, pick the next hypothesis, increment `fix_attempt`. If `fix_attempt >= max_fix_attempts` -> proceed to Step 5 (exhaustion).

### Step 4 -- Merge Back on Success

```bash
COMMIT=$(git -C .worktrees/research-resolve-<timestamp> rev-parse HEAD)
git merge $COMMIT
git worktree remove .worktrees/research-resolve-<timestamp>
```

Return `resolved` to `dev-loop`.

**On merge conflict:**
```bash
git merge --abort
git worktree remove .worktrees/research-resolve-<timestamp>
```
Log conflict as a blocker, proceed to Step 5 with `outcome: exhausted`.

### Step 5 -- On Exhaustion (all attempts failed or merge conflict)

1. Clean up worktree -- use `--force` to handle dirty working tree, staged changes, or both:
   ```bash
   git worktree remove --force .worktrees/research-resolve-<timestamp>
   ```
2. Surface the full attempt log to the user.
3. Log blocker in `memory/project-context.md`:
   ```
   - YYYY-MM-DD: research-resolve exhausted on <task-name> | age_days: 0 | recommended_fix: manual review required
   ```
4. Return `exhausted` to `dev-loop`.

Next: `/prodmasterai build fix <task-name>` to treat as a new task | `/prodmasterai` to reassess priorities

### Step 6 -- Log Findings (always runs -- after Step 4 or Step 5)

Append to `memory/blocker-research.md` (create the file if it does not exist):

```yaml
---
date: YYYY-MM-DD
type: blocker-fix
task: <task-name>
root_cause: <identified root cause or "unknown">
fix_applied: <fix description, or "none -- exhausted">
attempts: N
outcome: resolved | exhausted
keywords: [keyword1, keyword2]
---
```

---

## Rules

- Always use an isolated git worktree -- never apply fixes directly to the main working tree
- Worktree is cleaned up in every exit path (success, exhaustion, merge conflict) -- no leftover `.worktrees/` entries
- Use `git worktree remove --force` on exhaustion path to handle dirty/staged state
- Hard cap of 5 fix attempts -- prevents runaway inner loops
- Step 6 (log findings) always runs regardless of outcome
- Write to `memory/blocker-research.md` only -- never write to `memory/research-findings.md` (owned by evolve-self)
- **Never contribute anything upstream** -- upstream is exclusively evolve-self's responsibility
