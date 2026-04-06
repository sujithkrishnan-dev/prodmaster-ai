---
name: ship
description: Completeness-principle pre-merge pipeline — tests, coverage, review, changelog, scope check, PR. Boils the lake by default: 100% coverage, full error handling, comprehensive review. One command takes a branch from working to PR-ready.
version: 1.1.0
argument-hint: "[--skip-coverage] [--skip-review]"
disable-model-invocation: true
effort: medium
triggers:
  - /prodmasterai ship
  - ship this
  - ready to merge
  - pre-merge
  - create PR
  - prepare for merge
  - ready to ship
reads:
  - memory/project-context.md
  - memory/review-log.md
  - memory/mistakes.md
writes:
  - memory/ship-log.md
  - memory/project-context.md
generated: false
generated_from: ""
---

# Ship

Pre-merge pipeline that takes a branch from working code to a reviewed, documented, tested PR. Applies the **completeness principle**: with AI assistance, thoroughness is near-free — do it fully or don't do it.

Run this instead of manually creating PRs. It catches what you'd miss at 11pm.

## Live Context (injected at load time)

- Branch: !`git branch --show-current`
- Commits on branch: !`git log main...HEAD --oneline 2>/dev/null | head -20`
- Files changed: !`git diff main...HEAD --name-only 2>/dev/null`
- Working tree: !`git status --porcelain`

---

## The Completeness Principle

Before starting: internalize this rule.

> When fixing issue X, fix all issues in the blast radius if total effort is under one day.
> 100% test coverage is the default, not a stretch goal.
> Full error handling is the default, not a nice-to-have.

AI makes thoroughness cheap. Ship skips nothing.

---

## Phase 1 — Pre-flight

Run all checks in parallel:

1. **Branch check**: confirm current branch is NOT `main`/`master`. If on main: stop, output "Checkout a feature branch first."
2. **Working tree check**: `git status --porcelain`. If untracked/modified files exist: offer to commit or stash before continuing.
3. **Upstream sync**: `git fetch origin`. If branch is behind upstream main by >0 commits: output rebase suggestion. Do not auto-rebase — user decides.
4. **Review log check**: read last entry in `memory/review-log.md`. If `verdict: REWORK REQUIRED` and entry is from today: stop, output "Resolve open review issues first (`/prodmasterai review`)."

---

## Phase 2 — Test Suite

Run the full test suite:

```bash
# detect and run whichever applies:
npm test / yarn test / pnpm test
pytest / python -m pytest
cargo test
go test ./...
bun test
```

**Classify failures:**
- **In-branch failures**: failures in files changed by this branch → must fix before proceeding
- **Pre-existing failures**: failures in files NOT changed by this branch → log, do not block

Fix in-branch failures now. For each fix:
1. Apply targeted fix (completeness principle: fix the whole failure class, not just the symptom)
2. Re-run only the affected test file to verify
3. Commit: `git commit -m "fix: <test failure description>"`

If any in-branch failure cannot be fixed after 2 attempts: stop, output blocker with test name and error.

---

## Phase 3 — Coverage Audit

Check test coverage for all files changed in this branch:

```bash
git diff main...HEAD --name-only
```

For each changed file, check if a corresponding test exists and covers:
- Happy path
- Primary error path
- At least one edge case (empty input, boundary value, null/nil)

**Missing coverage** (completeness principle applies):
- Write the missing tests now — do not skip
- Each new test: atomic commit `git commit -m "test: coverage for <file>"`

If coverage tooling is available (`jest --coverage`, `pytest-cov`, `cargo tarpaulin`): run it. Flag any changed file below 80% coverage.

---

## Phase 4 — Review Gate

Run `/prodmasterai review` on the current diff.

- **Adversarial scaling**: if diff < 50 lines → quick pass. If > 500 lines → deep pass with subagent.
- Wait for review to complete.
- If verdict is REWORK REQUIRED: fix all critical issues now (completeness principle). Re-run review after fixes.
- If verdict is SHIP or SHIP WITH NOTES: continue.

Mechanical fixes from review are applied automatically. Judgment calls are surfaced once at end of Phase 4 as a single approval block (do not interrupt mid-pipeline).

---

## Phase 5 — Scope and Plan Completeness Check

1. Read the branch name and `git log main...HEAD --oneline` to understand stated intent.
2. Check for a plan file: look for `PLAN.md`, `docs/plan.md`, `memory/plans/`, or `## Active Features` in `memory/project-context.md`.
3. If a plan exists: verify every item marked complete in the plan has a corresponding commit. Flag any declared item with no commit evidence as `undeclared-incomplete`.
4. Check `TODOS.md` or inline TODOs in the diff: any TODO added in this diff that references work NOT in this PR → flag as `scope-leak`.
5. Output: clean OR list of undeclared-incomplete and scope-leak items (informational, not blocking).

---

## Phase 6 — Changelog

Check if `CHANGELOG.md` exists. If not: create it with today's entry. If it exists:

1. Read the last release entry.
2. Generate a new entry for this branch:
   - Date: today
   - Version: read from `VERSION` file, `package.json`, `Cargo.toml`, or `pyproject.toml`. If none found: use `Unreleased`.
   - Content: derived from `git log main...HEAD --oneline` — group by feat/fix/chore/docs/test prefixes.
3. Insert the entry at the top of CHANGELOG.md.
4. Commit: `git commit -m "docs: update CHANGELOG for <branch>"`

**Voice rules for changelog entries:**
- Active voice: "Add X", not "Added X"
- User-facing language: what the user gains, not what the code does
- No internal implementation details in user-facing entries

---

## Phase 7 — PR Creation

Assemble the PR:

**Title**: `<type>: <one-line summary>` (50 chars max). Type = feat/fix/docs/refactor/test.

**Body**:
```
## Summary
<2-3 bullet points — what changed and why>

## Test plan
- [ ] <specific thing to verify manually>
- [ ] <another thing>

## Notes
<scope-leak items, undeclared-incomplete items, known limitations>
```

Create the PR (prefer `gh pr create` if available; otherwise output the body for manual creation):

```bash
gh pr create --title "<title>" --body "<body>" --base main
```

If `gh` not available: output the full PR content formatted for copy-paste.

---

## Phase 8 — Post-ship Handoff

After PR is created:

1. Output the PR URL (or copy-paste content).
2. Suggest next steps:
   - "Run `/prodmasterai document-release` to sync docs after merge"
   - "Run `/prodmasterai qa` for end-to-end verification"
3. Append to `memory/ship-log.md`.
4. Mark active feature as `status: shipped` in `memory/project-context.md`.

---

## Inline Verification Gate

After Phase 4 (review), if any code was changed as part of fixing review issues: re-run the test suite before proceeding to Phase 5. Do not skip this even if tests just passed in Phase 2 — code changed means tests must re-run.

---

## Report

```
== Ship Report: <branch> ==
Tests:      <N passing / N total> (<N in-branch failures fixed>)
Coverage:   <N files audited, N tests added>
Review:     <verdict> (<N mechanical fixes, N judgment calls>)
Scope:      <clean | N items flagged>
Changelog:  <updated | created>
PR:         <url or "not created — gh not available">

Completeness check:
  <"All gaps filled — ready to merge" | "N items deferred (see PR notes)">
```

Append to `memory/ship-log.md`:
```yaml
---
date: <YYYY-MM-DD>
branch: <branch name>
tests_fixed: N
tests_added: N
review_verdict: SHIP | SHIP WITH NOTES | REWORK REQUIRED
pr_url: <url or "">
session_id: <session_id>
---
```

---

## Integration with Auto-Pilot

When `autonomous_mode: true`:
- All judgment calls auto-approved using best-practice defaults
- Scope-leak and undeclared-incomplete items logged as decisions, not blockers
- If in-branch test failures cannot be fixed: park auto-pilot with blocker
- If review verdict is REWORK REQUIRED after one fix attempt: park with blocker
- `gh pr create` runs automatically if available

---

## Rules

- Never skip Phase 3 (coverage) — completeness principle is non-negotiable
- In-branch test failures block the pipeline — pre-existing failures do not
- Changelog entries use active voice and user-facing language only
- Never force-push — only atomic commits
- Inline verification gate always re-runs after code changes post-review
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
