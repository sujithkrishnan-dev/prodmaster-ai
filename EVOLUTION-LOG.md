# ProdMaster AI — Upstream Evolution Log

Records changes contributed back to the plugin repository via auto-PR.
Local-only evolution is tracked in `memory/evolution-log.md`.

<!-- evolve-self appends entries here when PRs are merged upstream -->

## 2026-03-18 — Convergence loop, parallelism, fresh-state bootstrap, PreToolUse hook

PR: https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/1 | Type: skill_improvement (×6) + new hook | Trigger: explicit user feedback

### evolve-self 1.3.0 → 1.6.0
Replaced fixed 2-iteration refinement cap with a convergence loop. Phase 1 reruns until a full pass over all changed skills produces zero further changes. 5-pass per-file safeguard prevents infinite loops. Research subagents dispatched in parallel. Convergence pass checks all files in parallel per pass.

### prodmasterai 1.0.0 → 1.3.0
Evolution threshold now triggers silently and immediately — no announcement, runs evolve-self then continues to next action. Global parallelism rule added: all independent reads/writes/dispatches run in parallel, serialized only on explicit output dependency.

### report 1.0.0 → 1.2.0
Fresh-state detection: when no cycle data exists, writes `reports/getting-started-YYYY-MM-DD.md` and immediately asks what to build — no passive zero-metrics output. Completion message split into two branches. All data source reads parallelised.

### orchestrate 1.0.0 → 1.1.0
Context reads (project-context, GitHub, Linear) dispatched in parallel. Independent subtasks within a feature dispatched in parallel; serialized only where output dependency exists.

### measure 1.0.0 → 1.1.0
Steps 2+3 (writes to different files) run in parallel. Steps 4+5 (learn handoff + threshold check) run in parallel.

### learn 1.0.0 → 1.1.0
Pattern/mistake write (Thread A) and skill-gap detection (Thread B) run in parallel — disjoint file targets confirmed.

### hooks/pre-tool-bash.py (new)
PreToolUse hook for Bash commands. Blocks: recursive rm, force push, `git branch -D`, `git reset --hard`, `git clean -f`, discard-all checkout/restore, `DROP TABLE/DATABASE/SCHEMA`. Registered in `.claude-plugin/hooks.json`.

## 2026-03-18 — Structural review pass: 8 issues fixed across 7 skills
PR: auto-evolved/2026-03-18-structural-review-improve | Type: skill_improvement | Trigger: explicit structural-review (/prodmasterai optimize the plugin)

- evolve-self: Mode 0 structural review + 24h rate limit removed
- prodmasterai: "optimize/deep review" routing keywords + threshold flag reset
- measure: division-by-zero guard + persistent evolution_threshold_reached flag
- smooth-dev: auto default-branch detection
- learn: gap slug derivation algorithm
- decide: keyword-overlap topic matching for Step 6
- report: live blocker age_days + JSON XSS escaping
