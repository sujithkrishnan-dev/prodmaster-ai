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
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: evolve-self
trigger: explicit user feedback — evolution should be automatic and run a 2-iteration loop
change_summary: evolve-self Phase 1 now runs a mandatory 2-iteration refinement loop without stopping for user confirmation.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: prodmasterai
trigger: explicit user feedback — evolve-self should fire automatically on threshold, not announce and wait
change_summary: prodmasterai now silently runs the 2-iteration evolve-self loop when threshold is hit, then continues to the next action.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: report
trigger: iteration-2-refinement — completion message contradicted fresh-state bootstrap path
change_summary: Split completion message into two branches; fresh-state path never outputs zero-metrics dashboard and immediately asks what to build.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: evolve-self
trigger: explicit user feedback — fixed 2-loop limit removed; loop until convergence
change_summary: Replaced 2-iteration cap with a convergence loop that reruns until a full pass over all changed skills produces zero further changes; 5-pass safeguard prevents infinite loops.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: prodmasterai
trigger: downstream update from evolve-self convergence loop change
change_summary: Updated auto-evolve reference from "2-iteration loop" to "convergence loop — runs until all changed skills are clean".
upstream_status: merged
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
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: measure
trigger: explicit user feedback — always run independent tasks in parallel
change_summary: Steps 2+3 (writes to different files) now run in parallel; steps 4+5 (learn handoff + threshold check) now run in parallel.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: learn
trigger: explicit user feedback — always run independent tasks in parallel
change_summary: Pattern/mistake write and skill-gap detection now dispatched in parallel as they operate on different files.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: evolve-self
trigger: explicit user feedback — always run independent tasks in parallel
change_summary: Research subagents dispatched in parallel per skill; convergence loop checks all files in parallel per pass.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: report
trigger: explicit user feedback — always run independent tasks in parallel
change_summary: All data source reads (skill-performance, project-context, patterns, mistakes, connectors) now dispatched in parallel.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: prodmasterai
trigger: explicit user feedback — always run independent tasks in parallel
change_summary: Added global parallelism rule — all independent reads/writes/dispatches run in parallel; only serialized when explicit output dependency exists.
upstream_status: merged
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
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: orchestrate
trigger: structural-review convergence-pass-1
change_summary: Added memory/connectors/superpowers.md to writes: frontmatter — Step 3c writes installed/active flags but the declaration was missing.
upstream_status: merged
---
---
date: 2026-03-18
mode: improve
skill: help
trigger: structural-review convergence-pass-1
change_summary: Updated Improve table triggers to include optimize/deep review/audit keywords added in prodmasterai v1.9.0 routing table.
upstream_status: merged
---
---
date: 2026-03-19
mode: no-op
skill: ""
trigger: scheduled evolution check
change_summary: No improvements or new skills needed at this time
upstream_status: n/a
---
---
date: 2026-04-01
mode: generate
skill: cso
trigger: user request — 14-phase security audit skill missing from plugin
change_summary: New cso skill — 14-phase audit with OWASP Top 10, exploit-path requirement, scored report, security gate state integration.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/14"
---
---
date: 2026-04-01
mode: generate
skill: dependency-audit
trigger: user request — CVE scanning skill missing from plugin
change_summary: New dependency-audit skill — auto-detects npm/pip/bundler/go/rust, reports CVEs by severity, writes critical CVEs to security gate state.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/14"
---
---
date: 2026-04-01
mode: generate
skill: secret-scan
trigger: user request — credential scanning skill missing from plugin
change_summary: New secret-scan skill — 25+ credential patterns, staged-file scan, git history mode, per-finding remediation commands.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/14"
---
---
date: 2026-04-01
mode: improve
skill: pre-tool-bash (hook)
trigger: user request — expand bash hook with more dangerous patterns
change_summary: Added 8 blocked patterns — chmod 777, pip/npm installs from unverified sources, AWS key exports in shell, PATH hijacking via /tmp.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/14"
---
---
date: 2026-04-01
mode: generate
skill: post-tool-write (hook)
trigger: user request — passive security scanning on every file write
change_summary: New PostToolUse hook scanning all Write/Edit calls for secrets, SQL injection, unsafe deserialization, subprocess misuse. Advisory for high; blocks on critical.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/14"
---
---
date: 2026-04-01
mode: generate
skill: stop-quality-gate (hook)
trigger: user request — security gate blocking session exit
change_summary: New Stop hook blocking session exit when critical secret leaks or CVEs are flagged via security-gate-state.json.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/14"
---
---
date: 2026-04-06
mode: improve
skill: auto-pilot
trigger: structural-review -- writes: missing memory/task-queue.md (Queue Advance section reads and writes it)
change_summary: Added memory/task-queue.md to both reads: and writes: frontmatter declarations to match Queue Advance step body.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/17"
---
---
date: 2026-04-06
mode: improve
skill: prodmasterai
trigger: structural-review -- reads:/writes: missing memory/pending-input.md and writes: missing memory/usage-log.md
change_summary: Added memory/pending-input.md to reads/writes and memory/usage-log.md to writes to match Idle Auto-Pilot Check and Step 0 body references.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/17"
---
---
date: 2026-04-06
mode: improve
skill: auto-pilot-revoke
trigger: structural-review -- output block missing explicit Next: hint
change_summary: Added Next: completion hints to Step 5 output block so users know how to proceed after revoke.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/17"
---
---
date: 2026-04-06
mode: improve
skill: dev-loop
trigger: structural-review -- missing Next: hint and no edge-case for max_iterations=0
change_summary: Added Next: hint to loop summary output and documented max_iterations minimum-1 guard in parameter table.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/17"
---
---
date: 2026-04-06
mode: improve
skill: research-resolve
trigger: structural-review -- exhaustion path (Step 5) missing Next: hint
change_summary: Added Next: completion hint to Step 5 exhaustion path so users know how to treat the blocker as a new task.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/17"
---
---
date: 2026-04-06
mode: improve
skill: parallel-explore
trigger: structural-review -- no explicit error path when --approaches N > 4
change_summary: Added explicit stop-and-error output when N > 4 is passed, matching the stated hard limit in the rules section.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/17"
---
---
date: 2026-04-06
mode: improve
skill: help
trigger: structural-review -- reference card missing 10 skills added since last help update
change_summary: Added Automate section (auto-pilot, auto-pilot-revoke, resume, checkpoint, task-queue) and expanded Build/Improve sections with dev-loop, parallel-explore, research-resolve, plugin-manager, token-efficiency.
upstream_status: merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/17"
---
