---
name: report
description: Print a productivity report directly in the terminal. Run with /report or /report weekly. All output appears inline — no files written. When no data exists, prints a getting-started guide in the terminal.
version: 1.4.0
triggers:
  - User runs /report
  - User asks for weekly summary, status update, management report, or dashboard refresh
reads:
  - memory/skill-performance.md
  - memory/project-context.md
  - memory/patterns.md
  - memory/mistakes.md
  - memory/connectors/slack.md
  - memory/connectors/linear.md
  - memory/connectors/github.md
writes: []
generated: false
generated_from: ""
---

# Report

Print a full productivity report directly in the terminal. No files are written. Everything appears inline.

## Data Sources

Read all sources in **parallel** (do not serialize):
- `memory/skill-performance.md` -- metrics per cycle
- `memory/project-context.md` -- Active Features, Blockers, Decisions Log
- `memory/patterns.md` -- top 3 patterns (most recent)
- `memory/mistakes.md` -- top 3 mistakes (most recent)
- `memory/connectors/slack.md` -- connector config
- `memory/connectors/linear.md` -- connector config + cycle data if active

Skip entries with `example: true` or `inferred: true` when processing results and computing averages. These entries do not reflect real measured outcomes.

Wait for all reads to complete before computing stats.

## Computed Stats (from skill-performance.md, excluding example and inferred entries)

- Total features delivered
- Average QA pass rate (mean of qa_pass_rate values)
- Average velocity (mean of velocity_tasks_per_week, null if no time data)
- Average review iterations
- Active blockers (count from project-context.md Blockers section)
- Pending decisions (status: pending_outcome count)
- Auto-tracked sessions count (inferred: true entries — shown separately, not in averages)

## Terminal Output (normal — data present)

Print this block directly to the terminal. Use `—` for any null/unavailable metric. Do not write to any file.

```
===============================================
  ProdMaster AI — Report · {DATE}
===============================================

  Features delivered:    {N}
  Avg QA pass rate:     {N%}
  Avg velocity:         {N tasks/week | —}
  Review iterations:    {N}
  Active blockers:      {N}
  Pending decisions:    {N}

  Auto-tracked sessions: {N} (excluded from averages)

---Features ───────────────────────────────────
{list each non-example, non-inferred entry: "  · {feature} ({date}) — {tasks_completed} tasks"}
(none) if empty

---Top Patterns ───────────────────────────────
{top 3 from patterns.md: "  · {pattern description}"}
(none yet) if empty

---Recent Mistakes ────────────────────────────
{top 3 from mistakes.md: "  · {mistake description}"}
(none yet) if empty

---Active Blockers ────────────────────────────
{each blocker from project-context.md ## Blockers: "  · {description} (age: {age_days}d) → {recommended_fix}"}
(none) if empty

---Decisions ──────────────────────────────────
{each decision YAML block from project-context.md ## Decisions Log: "  · [{status}] {decision}"}
(none) if empty

===============================================
Next: /prodmasterai build [feature]  ·  /prodmasterai cycle done — …
```

**age_days** for blockers: always compute as `today − YYYY-MM-DD` at report time — the value in the file is a snapshot, use the date field for the live age.

## Fresh-State Bootstrap (no real data detected)

When `skill-performance.md` has no real-data entries (an entry qualifies as real data only if both `example: true` is absent AND `inferred: true` is absent):

Print this directly in the terminal — do not write any file:

```
===============================================
  ProdMaster AI — Getting Started
===============================================

  No cycle data recorded yet.
  Here's your fast path to a live report:

  Step 1 — Start a feature
    /prodmasterai build [feature name]

  Step 2 — After your first work session, log the cycle
    /prodmasterai cycle done — N tasks, QA X%, Y reviews, Z hours

  Step 3 — Generate your first real report
    /prodmasterai report

  ProdMaster AI will populate all metrics automatically after Step 2.

===============================================
```

Then ask: *"What are you building first? Tell me the feature name and I'll break it into tasks right now."*

## Slack (if connector active)

If `memory/connectors/slack.md` has `active: true` and non-empty `webhook_url`: post the computed stats block (Features delivered, QA pass rate, velocity, blockers, decisions) to the webhook after printing to terminal.

## Rules

- Skip `example: true` and `inferred: true` entries in all calculations and averages
- If no real data: run Fresh-State Bootstrap (above) — print in terminal, write no files
- **Do not write any files** — all output is printed to the terminal inline
- Do not show raw YAML or internal memory file contents in the report output
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
