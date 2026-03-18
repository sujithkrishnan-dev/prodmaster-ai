# Local Evolution Log

Written by: evolve-self (local changes only).
Root EVOLUTION-LOG.md tracks upstream-merged changes only.

<!-- Entries appended below:
---
date: YYYY-MM-DD
mode: improve | generate | no-op
skill: <skill name>
trigger: <what triggered this>
change_summary: <one sentence>
---
-->
---
date: 2026-03-18
mode: improve
skill: report
trigger: explicit user feedback — report showed zeros passively instead of bootstrapping
change_summary: Report now auto-bootstraps a getting-started guide and invokes orchestrate when no cycle data exists, instead of silently outputting zero-metrics.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: evolve-self
trigger: explicit user feedback — evolution should be automatic and run a 2-iteration loop
change_summary: evolve-self Phase 1 now runs a mandatory 2-iteration refinement loop without stopping for user confirmation.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: prodmasterai
trigger: explicit user feedback — evolve-self should fire automatically on threshold, not announce and wait
change_summary: prodmasterai now silently runs the 2-iteration evolve-self loop when threshold is hit, then continues to the next action.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: report
trigger: iteration-2-refinement — completion message contradicted fresh-state bootstrap path
change_summary: Split completion message into two branches; fresh-state path never outputs zero-metrics dashboard and immediately asks what to build.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: evolve-self
trigger: explicit user feedback — fixed 2-loop limit removed; loop until convergence
change_summary: Replaced 2-iteration cap with a convergence loop that reruns until a full pass over all changed skills produces zero further changes; 5-pass safeguard prevents infinite loops.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: prodmasterai
trigger: downstream update from evolve-self convergence loop change
change_summary: Updated auto-evolve reference from "2-iteration loop" to "convergence loop — runs until all changed skills are clean".
upstream_status: pr_created
---
---
date: 2026-03-18
mode: no-op
skill: ""
trigger: /evolve invoked directly — no performance data, no skill gaps with 3+ occurrences
change_summary: No improvements or new skills needed at this time; all locally evolved skills are ahead of the cached upstream version (local v1.6.0 vs cached v1.3.0).
upstream_status: n/a
---
---
date: 2026-03-18
mode: improve
skill: orchestrate
trigger: explicit user feedback — always run independent tasks in parallel
change_summary: Context reads (project-context, GitHub, Linear) now dispatched in parallel; independent subtasks within a feature dispatched in parallel; rule updated to reflect per-feature parallelism.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: measure
trigger: explicit user feedback — always run independent tasks in parallel
change_summary: Steps 2+3 (writes to different files) now run in parallel; steps 4+5 (learn handoff + threshold check) now run in parallel.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: learn
trigger: explicit user feedback — always run independent tasks in parallel
change_summary: Pattern/mistake write and skill-gap detection now dispatched in parallel as they operate on different files.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: evolve-self
trigger: explicit user feedback — always run independent tasks in parallel
change_summary: Research subagents dispatched in parallel per skill; convergence loop checks all files in parallel per pass.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: report
trigger: explicit user feedback — always run independent tasks in parallel
change_summary: All data source reads (skill-performance, project-context, patterns, mistakes, connectors) now dispatched in parallel.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: prodmasterai
trigger: explicit user feedback — always run independent tasks in parallel
change_summary: Added global parallelism rule — all independent reads/writes/dispatches run in parallel; only serialized when explicit output dependency exists.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: prodmasterai
trigger: structural-review — optimize keyword missing from routing table
change_summary: Added "optimize", "deep review", "audit the plugin", "quality pass" to evolve-self routing keywords. Added evolution_threshold_reached flag check and reset to Step 3A.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: evolve-self
trigger: structural-review — no structural quality pass when no performance data exists
change_summary: Added Mode 0 (Structural Review) that checks all skill files for quality issues on explicit /evolve invocations; enables improvement before any cycle data is logged.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: measure
trigger: structural-review — division by zero, ambiguous variable naming, stale flag mechanism
change_summary: Zero guard for velocity when time_hours=0; clarified tasks_completed naming; evolution_threshold_reached now written to project-context.md frontmatter; null velocity in completion message.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: smooth-dev
trigger: structural-review — default branch detection unspecified
change_summary: Added explicit default branch detection via git remote show origin; $default_branch variable used throughout pull commands.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: learn
trigger: structural-review — gap slug derivation unspecified
change_summary: Defined gap ID slug algorithm: first 3 significant words, stop-word stripped, lowercase, hyphenated, max 20 chars.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: decide
trigger: structural-review — topic matching algorithm undefined in Step 6
change_summary: Added keyword-overlap scoring algorithm for finding matching decisions; fallback to asking user when overlap is zero.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: report
trigger: structural-review — stale blocker age_days and JSON XSS risk
change_summary: age_days now recomputed from date field at report generation time; XSS escaping added for </script> in embedded JSON.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: prodmasterai
trigger: structural-review convergence-pass-1
change_summary: Removed stale reads declarations (evolution-log.md, patterns.md) that were declared in frontmatter but never read in any step.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: orchestrate
trigger: structural-review convergence-pass-1
change_summary: Added memory/connectors/superpowers.md to writes: frontmatter — Step 3c writes installed/active flags but the declaration was missing.
upstream_status: pr_created
---
---
date: 2026-03-18
mode: improve
skill: help
trigger: structural-review convergence-pass-1
change_summary: Updated Improve table triggers to include optimize/deep review/audit keywords added in prodmasterai v1.9.0 routing table.
upstream_status: pr_created
---
