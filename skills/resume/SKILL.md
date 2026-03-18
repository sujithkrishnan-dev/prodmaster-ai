---
name: resume
description: Show autonomous session audit -- every decision made during an auto-pilot run, with rationale, confidence, and per-decision rollback. Also detects and clears stale auto-pilot locks.
version: 1.0.0
triggers:
  - /prodmasterai resume
  - what happened while I was away
  - show autonomous summary
  - autonomous summary
reads:
  - memory/autonomous-log.md
  - memory/project-context.md
writes:
  - memory/autonomous-log.md
  - memory/project-context.md
generated: false
generated_from: ""
---

# Resume

Review what auto-pilot did while you were away. See every autonomous decision with its source and confidence. Optionally re-run any decision in normal attended mode.

---

## Step 1 -- Check for Stale Lock

Read `memory/project-context.md` frontmatter. If `autonomous_session_id` is non-empty, check whether the lock is stale:

```bash
git log auto/<session_id> -1 --format=%ct
```

Parse `autonomous_session_id` (`YYYY-MM-DD-HHmm`) as UTC Unix timestamp. If the branch's last commit timestamp is earlier than the `autonomous_session_id` datetime (or the branch does not exist): lock is stale.

Offer: *"Found stale auto-pilot lock (session: [id]) -- no active run detected. Clear lock and start fresh?"*
- Yes: reset `autonomous_mode: false`, `autonomous_session_id: ""` in project-context.md frontmatter
- No: exit

## Step 2 -- Find Last Session

Read `memory/autonomous-log.md`. Find the most recent session block (last `---` YAML block).
If none: *"No autonomous sessions found."* Stop.

## Step 3 -- Print Completion Card

```
== Auto-Pilot Session: <session_id> ==
Goal:    <goal>
Status:  COMPLETE | PARKED | STUCK
Branch:  auto/<session_id>
PR:      <pr_url or "not created">
Tests:   <tests_final>

Decisions made (<N>):
  [1] <type>: <answer>
      Source: <source> | Confidence: <confidence>
  [2] ...
```

## Step 4 -- Per-Decision Review

For each decision (in order), offer:
- `[A]ccept` -- keep as-is (default, Enter to accept)
- `[R]e-run` -- reset this step, hand off to the relevant skill in normal attended mode

If `[R]` chosen and `downstream_decision_ids` is non-empty:
- Warn: *"Re-running [N] will also reset decisions [X], [Y]. Continue?"*
- On confirm:
  1. Run `git checkout auto/<session_id>`. If branch missing: *"Branch no longer exists -- cannot revert. History preserved in autonomous-log.md."* Abort.
  2. For each file in `affected_files`: run `git checkout <pre_action_sha> -- <filepath>`.
     `affected_files` lists are non-overlapping across decisions by design.
  3. Mark each downstream decision `status: rolled_back` in the session block.
  4. Invoke the relevant skill in normal attended mode from that decision point.

## Step 5 -- Archive

After review completes: set `reviewed: true` on the session block.
Sessions with `archived: false` and date older than 30 days: set `archived: true`.
Never delete entries.

---

## Rules

- Only `resume` may clear a stale `autonomous_session_id` lock -- auto-pilot never does
- Rollback uses `git checkout <sha> -- <file>` -- never `git reset` or `git revert`
- `affected_files` lists are non-overlapping by construction -- safe to apply sequentially
- **Never contribute anything upstream** -- upstream is exclusively evolve-self's responsibility
