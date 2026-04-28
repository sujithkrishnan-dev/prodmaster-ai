# Changelog

All notable changes to ProdMaster AI are documented here.

---

## [2.1.0] — 2026-03-21

### Added
- `parallel-explore` skill: run 2+ implementation approaches in isolated git worktrees, auto-pick winner by test pass rate
- `task-queue` skill: sequential execution queue — add, list, and run goals without context switching
- `auto-pilot-revoke` skill: gracefully stop a running auto-pilot session, commit progress, reset lock
- `research-resolve` skill: deep research agent for unblocking stuck dev-loop or orchestrate tasks
- `dev-loop` skill: repeating development loop for iterative tasks until condition is met
- `checkpoint` skill: save and restore in-flight work state across context resets
- `token-efficiency` skill: audit and reduce token consumption across plugin operations

### Improved
- `evolve-self`: replaced fixed 2-iteration cap with convergence loop — reruns until a full pass finds zero issues
- `prodmasterai` entry point: global parallelism rule — all independent reads/writes/dispatches now run in parallel
- `orchestrate`: context reads (project-context, GitHub, Linear) dispatched in parallel
- `measure`: writes to disjoint files now run in parallel; learn handoff + threshold check run in parallel
- `report`: fresh-state detection added; all data source reads parallelised
- `hooks.json`: PostToolUse hook (post-tool-write.py) now registered in `.claude-plugin/hooks.json`

### Fixed
- `post-tool-write.py` security scanner: split secret patterns at runtime to prevent self-triggering on write
- `pre-tool-bash.py`: heredoc body lines no longer split as commands; quote-aware fragment parser added

---

## [2.0.0] — 2026-03-18

### Added
- `auto-pilot` skill: fully autonomous unattended development — brainstorm → plan → implement → test → PR
- `resume` skill: per-decision audit and rollback of auto-pilot sessions
- `cso` skill: 14-phase OWASP + STRIDE security audit, exploit-path required for every finding
- `dependency-audit` skill: CVE scan across npm/pip/bundler/go with session-exit block on CRITICAL
- `secret-scan` skill: 25+ credential patterns, staged-file scan, git history check, remediation commands
- `benchmark` skill: Core Web Vitals, bundle size tracking, regression alerts, 4 measurement modes
- `codex` skill: cross-model adversarial code review with PASS/FAIL gate and cost tracking
- `document-release` skill: post-ship doc sync, CHANGELOG polish, consistency checks
- `qa` skill: 11-phase QA with health scores across 8 categories and atomic fix commits
- `qa-only` skill: findings-only QA with screenshot evidence and baseline regression
- `ship` skill: completeness-principle pre-merge gate
- `deploy` skill: platform-aware deployment with dry-run, canary verification, revert escape hatch
- `hooks/pre-tool-bash.py`: PreToolUse safety hook (blocks rm -rf, force push, DROP TABLE, etc.)
- `hooks/post-tool-write.py`: PostToolUse security scanner (AWS keys, private key material, SQL injection, XSS, unsafe deserialization)
- `hooks/stop-quality-gate.py`: Stop hook — blocks session exit on critical secrets, critical CVEs, or failing tests during ship/deploy
- Auto-session tracking via `memory/usage-log.md` — measure fires silently between sessions

### Improved
- `evolve-self`: all research subagents dispatched in parallel; all file checks per convergence pass run in parallel
- `orchestrate`: independent subtasks dispatched in parallel
- `learn`: pattern write and gap detection now run in parallel

---

## [1.0.0] — 2026-02-01

### Added
- Initial release
- Core skills: `prodmasterai`, `orchestrate`, `measure`, `learn`, `report`, `decide`, `smooth-dev`, `help`
- `evolve-self`: automatic skill improvement and gap-filling convergence loop
- `plugin-manager`: installed/available plugin detection and auto-install
- `skill-forge`: research-driven SKILL.md generation
- Session-start hook with memory injection
- Connector support: GitHub, Slack, Linear, Superpowers
