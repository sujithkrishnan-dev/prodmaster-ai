# Auto-Pilot Revoke Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `/auto-pilot-revoke` skill that gracefully stops a running auto-pilot session.

**Architecture:** Single new skill file. Reads concurrency lock from project-context.md, commits progress, resets lock, appends revoked entry to autonomous-log.md.

**Tech Stack:** Markdown skill file, Python pytest content-checks.

**Spec:** `docs/superpowers/specs/2026-03-21-auto-pilot-revoke-design.md`

---

## File Map

| File | Action |
|---|---|
| `skills/auto-pilot-revoke/SKILL.md` | Create |
| `tests/test_skills.py` | Modify — add `"auto-pilot-revoke"` to `ALL_SKILLS` |
| `memory/connectors/skill-pattern-manifest.md` | Modify — add entry |

---

## Task 1: Write failing tests

**Files:**
- Modify: `tests/test_skills.py`

The existing parametrized `test_skill_exists` and `test_skill_frontmatter` tests cover all new skills automatically once added to `ALL_SKILLS`.

- [ ] **Step 1: Add skill to ALL_SKILLS**

In `tests/test_skills.py`, change:
```python
ALL_SKILLS = ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
              "dev-loop", "research-resolve", "auto-pilot", "resume", "checkpoint",
              "token-efficiency"]
```
To:
```python
ALL_SKILLS = ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
              "dev-loop", "research-resolve", "auto-pilot", "resume", "checkpoint",
              "token-efficiency", "auto-pilot-revoke"]
```

- [ ] **Step 2: Run tests — verify they fail**

```
python -m pytest tests/test_skills.py::test_skill_exists[auto-pilot-revoke] tests/test_skills.py::test_skill_frontmatter[auto-pilot-revoke] -v
```

Expected: 2 FAIL (skill doesn't exist yet)

- [ ] **Step 3: Commit**

```bash
git add tests/test_skills.py
git commit -m "test: add auto-pilot-revoke to ALL_SKILLS (red)"
```

---

## Task 2: Create `skills/auto-pilot-revoke/SKILL.md`

**Files:**
- Create: `skills/auto-pilot-revoke/SKILL.md`
- Tests: `test_skill_exists[auto-pilot-revoke]`, `test_skill_frontmatter[auto-pilot-revoke]`

- [ ] **Step 1: Create the skill file**

```markdown
---
name: auto-pilot-revoke
description: Gracefully stop a running auto-pilot session — commits progress, resets concurrency lock, logs revoked status.
version: 1.0.0
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
Run `/prodmasterai resume` to review what was completed before revoke.
```

---

## Rules

- Never delete the branch — in-progress work is preserved on `auto/<session_id>`
- Never use `git reset` or `git revert` — only `git commit` for the checkpoint
- If `autonomous_session_id` is already empty (stale/already cleared): report no active session and stop — do not write to autonomous-log.md
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
```

- [ ] **Step 2: Run tests — verify they pass**

```
python -m pytest tests/test_skills.py::test_skill_exists[auto-pilot-revoke] tests/test_skills.py::test_skill_frontmatter[auto-pilot-revoke] -v
```

Expected: 2 PASS

- [ ] **Step 3: Update skill-pattern-manifest.md**

In `memory/connectors/skill-pattern-manifest.md`, add this entry (after the `### resume` section):

```markdown
### auto-pilot-revoke
- trigger: /auto-pilot-revoke
- trigger: stop auto-pilot
- trigger: cancel autonomous
- reads: memory/project-context.md, memory/autonomous-log.md
- writes: memory/project-context.md, memory/autonomous-log.md
```

- [ ] **Step 4: Commit**

```bash
git add skills/auto-pilot-revoke/SKILL.md memory/connectors/skill-pattern-manifest.md
git commit -m "feat: add auto-pilot-revoke skill"
```

---

## Task 3: Full test suite — verify no regressions

- [ ] **Step 1: Run full suite**

```
python -m pytest tests/ -v --tb=short
```

Expected: All tests pass, including the 2 new auto-pilot-revoke tests.
