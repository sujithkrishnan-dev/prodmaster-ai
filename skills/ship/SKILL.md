---
name: ship
description: Completeness-principle pre-merge checklist. Runs tests, checks coverage, triggers code review, updates CHANGELOG, and creates PR. Ensures nothing ships incomplete.
version: 1.0.0
triggers:
  - User runs /prodmasterai ship
  - User says "ship it", "ready to merge", "let's ship", "create PR", "prepare for merge"
reads:
  - memory/project-context.md
  - memory/security-gate-state.json
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# Ship — Pre-Merge Completeness Check

Ensure nothing ships incomplete. Runs a sequential pipeline: tests, coverage, security, review, changelog, PR.

## Process

### 1. Pre-flight Checks (parallel)

Run these simultaneously:
- `git status` — ensure no uncommitted changes
- `git diff main...HEAD --stat` — show what's being shipped
- Read `memory/security-gate-state.json` — check for unresolved critical issues

If uncommitted changes exist: prompt to commit or stash first.
If critical security issues exist: block and redirect to the relevant skill.

### 2. Test Suite

```bash
# Auto-detect and run
pytest / npm test / go test / cargo test / bundle exec rspec
```

If any test fails: **stop**. Do not proceed. Report failing tests and suggest fixes.

### 3. Coverage Check

Run coverage tool. If coverage drops below previous baseline: warn but don't block.

### 4. Security Gate

Run `secret-scan` (staged files mode).
If critical secrets found: **stop**. Redirect to secret-scan for remediation.

### 5. Code Review

If `review` skill is available: invoke it on the diff against main.
If not: skip, note "No automated review — consider manual review."

### 6. CHANGELOG Update

Check if `CHANGELOG.md` exists:
- **Yes:** Check if the current branch's changes are documented. If not, draft an entry.
- **No:** Skip (don't create CHANGELOG for projects that don't use one).

### 7. Create PR

```bash
gh pr create --title "<conventional commit title>" --body "<body>"
```

PR body includes:
- Summary of changes (from commit log)
- Test results (pass count)
- Coverage delta
- Security scan result
- Link to QA report if qa/qa-only was run this session

If `gh` CLI not available: print the PR body and provide the GitHub URL for manual creation.

### 8. Mark Feature Complete

Update `memory/project-context.md`:
- Set active feature status to `done`
- Log ship timestamp

### Completion Message

```
Ship Complete
=============
Branch:   <branch>
PR:       <url>
Tests:    N/N passing
Coverage: XX% (delta: +/-Y%)
Security: clean / N issues (severity breakdown)
Review:   completed / skipped
CHANGELOG: updated / skipped

Feature "<name>" marked as done.
```

## Rules

- NEVER ship with failing tests — hard stop
- NEVER ship with critical secret leaks — hard stop
- Coverage decline is a warning, not a blocker
- Always create PR, never push directly to main
- If `gh` is unavailable, provide manual PR instructions — never skip
