---
name: smooth-dev
description: Use before starting any development session, after a context switch, or when the codebase state is uncertain. Pulls latest changes, checks repo health, verifies tests pass, and surfaces any blockers — ensuring the dev environment is clean before work begins.
version: 1.0.0
triggers:
  - User says "take a pull", "pull latest", "sync code", "get latest", "ensure code is up to date"
  - User says "start dev", "start development", "ready to code", "begin session"
  - User says "smooth dev", "health check", "pre-flight", "ensure smooth development"
  - Before any orchestrate cycle when the repo state is unknown
reads:
  - memory/project-context.md
  - memory/connectors/github.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# Smooth Dev

Run a pre-development health check: pull latest, verify repo state, run tests, surface blockers. Ensures every dev session starts from a clean, known state.

---

## Process

### 1. Pull Latest (parallel)

Run these simultaneously:
- `git fetch --all` — fetch all remotes without merging
- Read `memory/project-context.md` — note active features and open blockers
- If GitHub connector active: check for open PRs targeting current branch

After fetch, check divergence:
```
git status
git log HEAD..origin/<default-branch> --oneline
```

**If remote is ahead:** run `git pull --ff-only`. If fast-forward fails (diverged history), surface the conflict and stop — do not force-merge. Tell user: *"Branch has diverged from origin — resolve conflicts before proceeding."*

**If already up to date:** continue.

### 2. Repo Health Check (parallel)

Run these simultaneously:

**Thread A — Working tree state:**
```
git status
```
- Uncommitted changes present → list them. Ask: *"You have uncommitted changes — stash, commit, or continue?"*
  - Stash: `git stash push -m "smooth-dev auto-stash YYYY-MM-DD"`
  - Commit: hand off to user with file list
  - Continue: proceed with dirty tree (note it in output)
- Clean tree → proceed immediately

**Thread B — Recent commit context:**
```
git log --oneline -5
```
Surface the last 5 commits so the user knows what changed recently.

### 3. Run Tests

Run the project test suite. Use these in order (first match wins):
1. `python -m pytest tests/ -q` — if `tests/` directory exists
2. `npm test` — if `package.json` exists with a `test` script
3. `make test` — if `Makefile` has a `test` target
4. Skip and note: *"No test runner detected — skipping test step."*

**On failure:** Show failing test names. Do NOT proceed with feature work. Tell user: *"Tests failing — fix these before starting new work to avoid compounding issues."* Hand off to `orchestrate` if user wants to fix them as a feature.

**On pass:** Proceed.

### 4. Blocker Review

Read `## Blockers` from `memory/project-context.md`. For each open blocker, compute age:
```
age_days = today - blocker_date
```

Surface any blocker older than 3 days as a priority:
*"Blocker '[description]' is [N] days old — recommended fix: [recommended_fix]. Address this before new work?"*

### 5. Session Ready Output

Print a concise session card:

```
Dev session ready.

  Branch:        <branch name>
  Last commit:   <hash> <message>
  Tests:         PASS (N tests) | FAIL (N failing) | SKIPPED
  Working tree:  clean | N uncommitted files | stashed
  Open blockers: N  (oldest: N days)
  Active features: <feature names from project-context.md>

Next: /prodmasterai build [feature] | /prodmasterai cycle done — ...
```

### 6. Update Memory

If any new blockers were surfaced during this check, append to `memory/project-context.md` `## Blockers`. Do not duplicate existing entries.

---

## Rules

- Never force-merge or rebase without explicit user instruction
- If tests fail, stop and surface — do not proceed to feature work
- Stash message must include date so stashes are identifiable
- Always output the session card at the end — even if everything is clean
- If working tree is dirty and user chooses "continue", add a note to the session card: `Working tree: dirty (N files) — stash before cycle end`
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
- Parallelism: Steps 1 reads, Step 2 threads, Step 3 detection all run in parallel where independent
