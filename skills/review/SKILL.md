---
name: review
description: Two-pass code review with live diff context and auto-fix for mechanicals. First pass catches logic and design issues. Second pass fixes formatting, naming, and style automatically.
version: 1.0.0
triggers:
  - User runs /prodmasterai review
  - User says "review my code", "code review", "review the diff", "check my changes"
reads:
  - memory/project-context.md
  - memory/patterns.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# Review — Two-Pass Code Review

Automated code review with two passes: logic/design review first, then mechanical auto-fix.

## Process

### 1. Gather Diff

```bash
git diff main...HEAD
```

If no diff: check staged changes (`git diff --cached`). If still nothing: "No changes to review."

### 2. Pass 1 — Logic and Design Review (manual findings)

Review the full diff for:

| Category | What to look for |
|---|---|
| **Logic errors** | Off-by-one, null/undefined paths, race conditions, wrong operator |
| **Design issues** | God functions, tight coupling, missing abstractions, wrong layer |
| **API contracts** | Breaking changes, missing validation, inconsistent naming |
| **Error handling** | Swallowed errors, missing try/catch, user-facing stack traces |
| **Security** | Injection points, auth bypass, data exposure (delegate to cso for deep scan) |
| **Performance** | N+1 queries, unnecessary re-renders, blocking I/O in hot paths |
| **Tests** | Missing tests for new behavior, fragile assertions, test coverage gaps |

Finding format:
```
[CATEGORY] [SEVERITY] file:line
  Issue: <what's wrong>
  Suggestion: <how to fix>
  Context: <surrounding code snippet from diff>
```

### 3. Pass 2 — Mechanical Auto-Fix

Automatically fix without asking:
- Trailing whitespace
- Missing/extra blank lines between functions
- Inconsistent naming (match project convention)
- Unused imports
- Missing semicolons (JS projects with semi: true)
- Obvious typos in comments and strings

Each auto-fix: one atomic commit with message `style(review): <fix description>`

### 4. Report

```
Code Review — <branch>
======================
Pass 1 (logic/design): N findings
  CRITICAL: 0
  HIGH: 2
  MEDIUM: 3
  LOW: 1

Pass 2 (mechanicals): M auto-fixed
  - Removed 3 unused imports
  - Fixed 2 naming inconsistencies
  - Added 1 missing blank line

Top issues requiring attention:
  1. [HIGH] src/api.js:42 — missing input validation on user-supplied ID
  2. [HIGH] src/db.js:78 — N+1 query in loop
  3. [MEDIUM] src/auth.js:15 — session token not rotated on privilege change
```

## Rules

- Pass 1 findings are advisory — never auto-fix logic/design issues
- Pass 2 mechanicals are auto-fixed — always commit individually
- If review finds CRITICAL issues, recommend blocking merge
- Live diff context: always show the relevant code snippet from the diff, not just the line number
- Never review generated files (lockfiles, minified JS, build output)
