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

## 2026-03-19 — Structural review v2: frontmatter accuracy + help card sync
PR: auto-evolved/2026-03-18-structural-review-v2 | Type: skill_improvement | Trigger: structural-review

- prodmasterai v2.0.1: removed stale reads declarations (evolution-log.md, patterns.md)
- orchestrate v1.4.1: added superpowers.md to writes frontmatter
- help v1.0.1: updated evolve-self triggers to include optimize/deep review/audit

## 2026-04-01 — Three-layer security system: cso, dependency-audit, secret-scan + 2 hooks
PR: https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/14 | Type: new_skill (×3) + hook_improvement (×3) | Trigger: user request

### skills/cso (new) v1.0.0
14-phase security audit: OWASP Top 10 coverage, exploit-path required for every HIGH/CRITICAL finding, scored report (0–100), writes to security-gate-state.json to block session exit.

### skills/dependency-audit (new) v1.0.0
CVE scanning across npm/pip/bundler/go/rust/java. Auto-detects package managers. Writes critical CVEs to security-gate-state.json. Blocks session exit on CRITICAL findings.

### skills/secret-scan (new) v1.0.0
25+ credential pattern detection (AWS, GitHub, OpenAI, Stripe, Slack, etc.). Staged-file scan, git history mode, per-finding remediation with exact commands.

### hooks/post-tool-write.py (new)
PostToolUse hook scanning every Write/Edit for secrets, SQL injection, unsafe deserialization, subprocess misuse. Advisory for high/medium; blocks on critical secret material.

### hooks/stop-quality-gate.py (new)
Stop hook blocking session exit when critical leaks or CVEs are active in security-gate-state.json.

### hooks/pre-tool-bash.py v1.1.0
Expanded with 8 new blocked patterns: chmod 777, pip/npm installs from unverified URLs, AWS credential exports in shell, PATH hijacking via /tmp.

## 2026-04-06 — Structural review pass 2: frontmatter fixes + Next: hints + 10 missing skills in help
PR: https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/17 | Type: skill_improvement (×7) | Trigger: explicit /evolve structural-review

- auto-pilot v1.2.1: added memory/task-queue.md to reads/writes (Queue Advance section)
- prodmasterai v2.2.0: added memory/pending-input.md + usage-log.md to reads/writes; added stakeholder routing
- auto-pilot-revoke v1.0.1: added Next: hints to Step 5 output block
- dev-loop v1.0.1: added Next: hint + max_iterations minimum-1 guard
- research-resolve v1.0.1: added Next: hint to Step 5 exhaustion path
- parallel-explore v1.0.1: added explicit stop+error when --approaches N > 4
- help v1.0.2: added 10 missing skills across Automate/Build/Improve/Ship sections
