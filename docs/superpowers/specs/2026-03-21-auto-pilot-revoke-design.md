# Auto-Pilot Revoke — Design Spec

**Date:** 2026-03-21
**Status:** approved

---

## Problem

Once auto-pilot starts, there is no way to stop it mid-run without manually editing `project-context.md`. Users need a clean `/auto-pilot-revoke` command that gracefully cancels a running session.

## Solution

New skill `skills/auto-pilot-revoke/SKILL.md`. Reads the concurrency lock, commits current progress, resets the lock, appends a `revoked` entry to `autonomous-log.md`.

---

## Scope

One new skill file. No changes to existing skills.

---

## File Map

| File | Action |
|---|---|
| `skills/auto-pilot-revoke/SKILL.md` | Create |

---

## Behaviour

### Triggers

- `/auto-pilot-revoke`
- `/prodmasterai revoke`
- "stop auto-pilot"
- "cancel autonomous"
- "kill auto-pilot"

### Steps

**Step 1 — Read lock**

Read `memory/project-context.md` frontmatter.

If `autonomous_session_id` is empty:
→ Output: *"No auto-pilot session is running."*
→ Stop.

**Step 2 — Commit progress**

Run:
```bash
git add -A
git commit -m "chore: auto-pilot-revoke checkpoint (session: <autonomous_session_id>)"
```

If nothing to commit (clean tree), skip the commit — do not fail.

**Step 3 — Reset lock**

Update `memory/project-context.md` frontmatter:
- `autonomous_mode: false`
- `autonomous_session_id: ""`

**Step 4 — Append to autonomous-log.md**

Append:
```yaml
---
session_id: <autonomous_session_id>
status: revoked
revoked_at: <ISO 8601 timestamp>
branch: auto/<autonomous_session_id>
note: "Session cancelled by user via auto-pilot-revoke"
---
```

**Step 5 — Output**

```
Auto-pilot revoked.
Session: <session_id>
Branch:  auto/<session_id> (progress preserved)
Run `/prodmasterai resume` to review what was completed before revoke.
```

---

## Rules

- Never delete the branch — progress is preserved
- Never use `git reset` or `git revert` — only `git commit` for the checkpoint
- If the lock was already cleared (stale), report it and stop without writing to autonomous-log.md

---

## Tests Required

1. Skill file exists at `skills/auto-pilot-revoke/SKILL.md`
2. Frontmatter has correct `name`, `triggers`, `reads`, `writes`
3. Step 1 handles empty `autonomous_session_id` (no-op path)
4. Step 2 commits progress to `auto/<session_id>` branch
5. Step 3 resets `autonomous_mode: false` and clears `autonomous_session_id`
6. Step 4 appends `status: revoked` to `autonomous-log.md`
7. Step 5 outputs the revoke summary with branch name
8. Rules section: never delete branch, never use git reset/revert
