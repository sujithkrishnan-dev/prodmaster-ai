---
name: report
description: Use to generate productivity reports and refresh the HTML dashboard. Run with /report or /report weekly. Reads all memory files, produces a markdown weekly summary and a self-contained HTML dashboard. When no data exists, auto-bootstraps a getting-started guide and kicks off orchestrate.
version: 1.3.0
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
writes:
  - reports/weekly-YYYY-MM-DD.md
  - reports/dashboard.html
generated: false
generated_from: ""
---

# Report

Generate the weekly markdown report and regenerate the HTML dashboard.

## Data Sources

Read all sources in **parallel** (do not serialize):
- `memory/skill-performance.md` — metrics per cycle
- `memory/project-context.md` — Active Features, Blockers, Decisions Log
- `memory/patterns.md` — top 3 patterns (most recent)
- `memory/mistakes.md` — top 3 mistakes (most recent)
- `memory/connectors/slack.md` — connector config
- `memory/connectors/linear.md` — connector config + cycle data if active

Skip entries with `example: true` when processing results. Wait for all reads to complete before computing stats.

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

## Fresh-State Bootstrap (no real data detected)

When `skill-performance.md` has no non-example entries:

1. **Do not write a zero-metrics report.** Instead write `reports/getting-started-YYYY-MM-DD.md`:

```markdown
# ProdMaster AI — Getting Started
**Date:** YYYY-MM-DD

No cycle data recorded yet. Here's your fast path to a live dashboard:

## Step 1 — Start a feature
/prodmasterai build [feature name]

## Step 2 — After your first work session, log the cycle
/prodmasterai cycle done — N tasks, QA X%, Y reviews, Z hours

## Step 3 — Generate your first real report
/prodmasterai report

ProdMaster AI will populate all metrics automatically after Step 2.
```

2. **Do NOT write dashboard.html with zeros.** Skip dashboard generation entirely in fresh state.
3. **Completion message** (fresh state): *"No cycle data yet — wrote `reports/getting-started-YYYY-MM-DD.md`."* Then ask: *"What are you building first? Tell me the feature name and I'll break it into tasks right now."*

## Rules

- Skip `example: true` entries in all calculations
- If no real data: run Fresh-State Bootstrap (above) — never silently output zero-metrics
- Never overwrite existing report files — create new dated files
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
