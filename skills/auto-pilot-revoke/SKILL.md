---
name: auto-pilot-revoke
description: Gracefully stop a running auto-pilot session — commits progress, resets concurrency lock, logs revoked status.
version: 1.0.1
triggers:
  - /auto-pilot-revoke
  - /prodmasterai revoke
  - stop auto-pilot
  - cancel autonomous
  - kill auto-pilot
reads:
  - memory/project-context.md
  - memory/autonomous-log.md
writes:
  - memory/project-context.md
  - memory/autonomous-log.md
generated: false
generated_from: ""
---

# Auto-Pilot Revoke

Stop a running auto-pilot session. Commits any in-progress work, resets the concurrency lock, and records the revoke in the autonomous session log. Run `/prodmasterai resume` afterward to review what was completed before the revoke.

---

## Step 1 — Read lock

Read `memory/project-context.md` frontmatter.

If `autonomous_session_id` is empty:
→ Output: *"No auto-pilot session is running."*
→ Stop.

Set `session_id = autonomous_session_id`.

## Step 2 — Commit progress

```bash
git add -A
git commit -m "chore: auto-pilot-revoke checkpoint (session: <session_id>)"
```

If nothing to commit (clean working tree), skip the commit silently — do not fail.

## Step 3 — Reset lock

Update `memory/project-context.md` frontmatter:
- `autonomous_mode: false`
- `autonomous_session_id: ""`

## Step 4 — Append to autonomous-log.md

Append:
```yaml
---
session_id: <session_id>
status: revoked
revoked_at: <ISO 8601 timestamp>
branch: auto/<session_id>
note: "Session cancelled by user via auto-pilot-revoke"
---
```

## Step 5 — Output

```
Auto-pilot revoked.
Session: <session_id>
Branch:  auto/<session_id> (progress preserved)

Next: /prodmasterai resume  — review what was completed before revoke
      /prodmasterai         — return to normal operation
```

---

## Rules

- Never delete the branch — in-progress work is preserved on `auto/<session_id>`
- Never use `git reset` or `git revert` — only `git commit` for the checkpoint
- If `autonomous_session_id` is already empty (stale/already cleared): report no active session and stop — do not write to autonomous-log.md
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
