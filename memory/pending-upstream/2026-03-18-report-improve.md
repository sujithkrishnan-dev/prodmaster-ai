---
proposal_id: 2026-03-18-report-improve
type: skill_improvement
source: feedback
target_skill: skills/report/SKILL.md
occurrence_count: 3
created: 2026-03-18
status: pr_created
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/new/auto-evolved/2026-03-18-session-improvements"
---
## What Changed
- Fresh-state detection: when no real cycle data exists, report no longer outputs a zero-metrics file. Instead writes a getting-started guide (`reports/getting-started-YYYY-MM-DD.md`) and immediately prompts the user for what to build.
- Completion message split into two branches: real-data path vs fresh-state path — no contradicting messages.
- All data source reads (skill-performance, project-context, patterns, mistakes, connectors) dispatched in parallel.
- Version: 1.0.0 → 1.2.0

## Why
Users invoking /report with no cycle data received an unhelpful zero-metrics report with a passive "run orchestrate first" note. Plugin should be active, not passive — bootstrap the user into their first cycle immediately.

## Supporting Data (anonymised)
- Pattern: skill invoked before any cycle data exists (fresh install state)
- Observed: passive zero output creates confusion about what to do next
- Fix confidence: high — behaviour is unambiguously better for all fresh installs
