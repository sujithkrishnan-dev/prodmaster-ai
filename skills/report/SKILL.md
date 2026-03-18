---
name: report
description: Use to generate productivity reports and refresh the HTML dashboard. Run with /report or /report weekly. Reads all memory files, produces a markdown weekly summary and a self-contained HTML dashboard.
version: 1.0.0
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
writes:
  - reports/weekly-YYYY-MM-DD.md
  - reports/dashboard.html
generated: false
generated_from: ""
---

# Report

Generate the weekly markdown report and regenerate the HTML dashboard.

## Data Sources

Read these files (skip entries with `example: true`):
- `memory/skill-performance.md` — metrics per cycle
- `memory/project-context.md` — Active Features, Blockers, Decisions Log
- `memory/patterns.md` — top 3 patterns (most recent)
- `memory/mistakes.md` — top 3 mistakes (most recent)

If Linear connector is active: include Linear cycle data in the summary.

## Computed Stats (from skill-performance.md, excluding example entries)

- Total features delivered
- Average QA pass rate (mean of qa_pass_rate values)
- Average velocity (mean of velocity_tasks_per_week)
- Average review iterations
- Active blockers (count from project-context.md Blockers section)
- Pending decisions (status: pending_outcome count)

## Output 1: Markdown Report

Write to `reports/weekly-YYYY-MM-DD.md`:

```markdown
# ProdMaster AI — Weekly Report
**Date:** YYYY-MM-DD

## Summary
- Features delivered: N
- Avg QA pass rate: N%
- Avg velocity: N tasks/week
- Avg review iterations: N
- Active blockers: N
- Pending decisions: N

## Features Delivered
<list from skill-performance.md this period>

## Active Blockers
<from project-context.md ## Blockers>

## Top Patterns
<top 3 from patterns.md>

## Recent Mistakes
<top 3 from mistakes.md>

## Decisions
<from project-context.md ## Decisions Log>
```

## Output 2: HTML Dashboard

Regenerate `reports/dashboard.html`. Requirements:
- Single self-contained file, no CDN, no external scripts or stylesheets
- Vanilla JS only — use `createElement` and `textContent` for all dynamic content (never `innerHTML` with unsanitised data)
- Opens by double-clicking — no server needed
- Four panels in 2x2 grid

**Panel data mapping:**

| Panel | Source | Key fields |
|---|---|---|
| Feature Velocity | skill-performance.md | velocity_tasks_per_week (sparkline of last 10), current value |
| QA Health | skill-performance.md | qa_pass_rate (donut), avg review_iterations |
| Active Blockers | project-context.md ## Blockers | text, age_days, recommended_fix |
| BA Decisions Log | project-context.md ## Decisions Log | decision text, status |

**DOM safety rule:** When rendering user data (feature names, blocker text, decision text), always use `textContent` or `createTextNode` — never string-interpolate into HTML markup. Build elements with `document.createElement` and set their `textContent`.

Embed all stats as a JSON object in a `<script>` tag with `type="application/json"` id `prodmaster-data`, then read it with `JSON.parse(document.getElementById('prodmaster-data').textContent)` on load.

**Required JSON shape** (the dashboard HTML reads exactly these keys):

```json
{
  "generated": "YYYY-MM-DD",
  "velocity": [
    { "feature": "<feature name>", "value": <velocity_tasks_per_week> }
  ],
  "qaPassRates": [0.0],
  "avgIterations": 0.0,
  "blockers": [
    { "text": "<blocker description>", "age_days": 0, "recommended_fix": "<text>" }
  ],
  "decisions": [
    { "text": "<decision summary>", "status": "pending_outcome | confirmed_good | confirmed_bad" }
  ]
}
```

- `velocity`: last 10 entries from `skill-performance.md` (excluding `example: true`), ordered oldest-first
- `qaPassRates`: all `qa_pass_rate` values from non-example entries, ordered oldest-first
- `avgIterations`: mean of all `review_iterations` values from non-example entries, or `null` if no data
- `blockers`: parsed from `## Blockers` section of `project-context.md` — each line `- YYYY-MM-DD: <text> | age_days: <n> | recommended_fix: <text>`
- `decisions`: parsed from `## Decisions Log` section of `project-context.md` — each YAML block's `decision` and `status` fields

## Slack (if connector active)

If `memory/connectors/slack.md` has `active: true` and non-empty `webhook_url`: post the Summary section of the markdown report to the webhook.

## Completion Message

Tell the user:
- *"Weekly report written to `reports/weekly-YYYY-MM-DD.md`"*
- *"Dashboard updated at `reports/dashboard.html` — double-click to open"*

## Rules

- Skip `example: true` entries in all calculations
- If no real data: generate report with zeros and note "No cycle data yet — run orchestrate and measure first"
- Never overwrite existing report files — create new dated files
