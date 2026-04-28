# ProdMaster AI

![Version](https://img.shields.io/badge/version-2.1.0-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Platform](https://img.shields.io/badge/platform-Claude%20Code-orange) ![Skills](https://img.shields.io/badge/skills-31-purple)

> The engineering ops layer for Claude Code — one command orchestrates features, QA, code review, deployment, security audits, and performance benchmarks, while the plugin self-improves based on your velocity data.

**Install:**
```bash
claude plugin install prodmaster-ai@prodmaster-ai-marketplace
```

**Or via the official marketplace (once listed):**
```bash
claude plugin install prodmaster-ai@claude-plugins-official
```

---

## Why ProdMaster AI

Most Claude Code workflows require juggling many commands across many contexts. ProdMaster AI collapses that into one entry point:

- **`/prodmasterai build auth`** — breaks the feature into tracked parallel tasks, dispatches subtasks, monitors progress
- **`/prodmasterai qa`** — 11-phase quality check with health scores across 8 categories, atomic fix commits
- **`/prodmasterai cso`** — 14-phase OWASP + STRIDE security audit, exploit path required for every finding
- **`/prodmasterai auto <goal>`** — fully autonomous: brainstorm → plan → implement → test → PR, no hand-holding

And then it self-improves: every N tasks the plugin runs a convergence loop, detects skill gaps, and evolves its own skills. Your local improvements can be pushed upstream with `/prodmasterai update`.

---

## Platform Setup

**Windows** — works out of the box (uses `run-hook.cmd` + PowerShell).

**macOS / Linux** — after install, edit `hooks/hooks.json` and `.claude-plugin/hooks.json`, change the SessionStart command to:
```json
"command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.sh\" session-start"
```

Python 3 must be on PATH (default on macOS/Linux) — required for the safety hooks.

---

## Quick Start

```
/prodmasterai help
```

Or jump straight in:
```
/prodmasterai build user authentication
```

The plugin reads your current state and routes to the right skill — no need to remember command names.

---

## All Commands

| Command | What it does |
|---|---|
| `/prodmasterai` | Reads state and acts — or asks exactly one clarifying question |
| `/prodmasterai build <feature>` | Breaks feature into tasks, coordinates parallel implementation |
| `/prodmasterai pull latest` | `git pull`, repo health check, run tests |
| `/prodmasterai should we A or B?` | Scored decision with deep reasoning |
| `/prodmasterai report` | Prints full productivity report to terminal |
| `/prodmasterai review` | Two-pass code review with live diff context, auto-fix mechanicals |
| `/prodmasterai qa` | 11-phase QA, health score across 8 categories, atomic fix commits |
| `/prodmasterai qa-only` | Findings-only QA, no fixes, screenshot evidence, baseline regression |
| `/prodmasterai ship` | Completeness-principle pre-merge: tests → coverage → review → changelog → PR |
| `/prodmasterai deploy` | Platform auto-detect, dry-run, canary verification, revert escape hatch |
| `/prodmasterai cso` | 14-phase security audit (OWASP + STRIDE), exploit-path required for every finding |
| `/prodmasterai dependency-audit` | CVE scan across npm/pip/bundler/go — blocks on CRITICAL CVEs |
| `/prodmasterai secret-scan` | 25+ credential patterns, staged-file scan, git history check |
| `/prodmasterai benchmark` | Core Web Vitals, bundle size, regression alerts, 4 modes |
| `/prodmasterai codex` | Cross-model adversarial review, PASS/FAIL gate, cost tracking |
| `/prodmasterai document-release` | Post-ship doc sync, CHANGELOG polish, consistency checks |
| `/prodmasterai learn <topic>` | Research any topic, generate a production-ready SKILL.md |
| `/prodmasterai queue add <goal>` | Add goal to sequential execution queue |
| `/prodmasterai queue list` | Show pending/running/done queue |
| `/prodmasterai queue run` | Run all queued tasks sequentially, auto-advance |
| `/prodmasterai explore <goal>` | Run 2+ approaches in isolated worktrees, pick best by test pass rate |
| `/prodmasterai auto <goal>` | Fully autonomous: brainstorm → plan → implement → test → PR |
| `/prodmasterai resume` | Per-decision review and rollback of auto-pilot sessions |
| `/prodmasterai plugins` | Show installed/available plugins, auto-install when needed |
| `/prodmasterai cycle done — <summary>` | Record completed cycle, fire measure + learn |
| `/prodmasterai update` | Push locally evolved improvements upstream via PR |
| `/prodmasterai help` | Show all skills, triggers, and examples |
| `/auto-pilot-revoke` | Stop a running auto-pilot, commit progress, reset lock |
| `/evolve` | Convergence loop until all skills clean |

---

## Skills (31 total)

| Skill | Purpose |
|---|---|
| `auto-pilot` | Fully autonomous unattended development session |
| `auto-pilot-revoke` | Gracefully stop a running auto-pilot |
| `benchmark` | Core Web Vitals, bundle size, 4 measurement modes |
| `checkpoint` | Save and restore in-flight work across context resets |
| `codex` | Cross-model adversarial code review |
| `cso` | 14-phase security audit (OWASP + STRIDE) |
| `decide` | Scored decision recommendation with deep reasoning |
| `dependency-audit` | CVE scan across npm/pip/bundler/go |
| `deploy` | Platform-aware deployment with dry-run and revert |
| `dev-loop` | Repeating development loop for iterative tasks |
| `document-release` | Post-ship doc sync and CHANGELOG polish |
| `evolve-self` | Convergence loop — runs until all skills pass quality check |
| `help` | Show all skills, triggers, and examples |
| `learn` | Research a topic and generate a SKILL.md |
| `measure` | Record cycle metrics: tasks, QA score, reviews, hours |
| `orchestrate` | Break a feature into tracked parallel tasks |
| `parallel-explore` | Run 2+ approaches in isolated worktrees, compare results |
| `plugin-manager` | Detect, install, and manage plugins |
| `prodmasterai` | Master entry point — routes to all other skills |
| `qa` | 11-phase QA with health scoring and atomic fix commits |
| `qa-only` | Findings-only QA with screenshot evidence |
| `report` | Full productivity report printed to terminal |
| `research-resolve` | Deep research to resolve a blocked task |
| `resume` | Per-decision review and rollback of auto-pilot sessions |
| `review` | Two-pass code review with auto-fix |
| `secret-scan` | 25+ credential patterns, staged-file and history scan |
| `ship` | Pre-merge completeness gate |
| `skill-forge` | Create new production-ready skills from research |
| `smooth-dev` | Git pull, repo health check, test run |
| `task-queue` | Sequential task queue with auto-advance |
| `token-efficiency` | Reduce token consumption and optimize context usage |

---

## Safety Hooks (4 active)

The plugin installs four hooks that run automatically in every session:

| Hook | Fires on | What it does |
|---|---|---|
| `session-start` | Session open | Injects active features, patterns, gaps, open tasks, installed plugins |
| `pre-tool-bash` | Every Bash call | Blocks: `rm -rf`, force push, `git reset --hard`, `DROP TABLE`, `chmod 777`, pipe-to-shell, base64-to-shell, PATH hijack, AWS key exports |
| `post-tool-write` | Every Write/Edit | Scans for AWS/GitHub/OpenAI keys, private key material, SQL injection, XSS sinks, unsafe deserialization. Blocks on critical secrets. |
| `stop-quality-gate` | Session stop | Blocks exit when: critical secrets leaked, critical CVEs unfixed, tests failing during ship/deploy |

All hooks are pure Python (standard library only, no pip installs). They fail open — a hook crash never silently blocks valid work.

---

## Optional Connectors

All inactive by default. Opt-in by editing the connector file:

| Connector | How to activate |
|---|---|
| GitHub | Set `active: true` in `memory/connectors/github.md`, configure MCP server |
| Slack | Set `active: true` in `memory/connectors/slack.md`, add webhook URL |
| Linear | Set `active: true` in `memory/connectors/linear.md`, configure MCP server |
| Superpowers | Set `active: true` in `memory/connectors/superpowers.md` |

Credential files (`slack.md`, `linear.md`) are in `.gitignore` and never committed.

---

## External Network Access

The plugin makes no outbound network calls on its own. External access only occurs when:

- A connector is explicitly activated and a Claude Code MCP server is configured by the user
- A skill uses Claude Code's built-in `WebSearch` or `WebFetch` tools (user-approved per-call)
- The `dependency-audit` skill queries public package registries to check CVE data

No telemetry. No analytics. No data leaves the machine unless you configure a connector.

---

## Memory and State

All state is stored locally in `memory/`. Nothing is sent upstream automatically.

| File | Purpose |
|---|---|
| `memory/usage-log.md` | Per-invocation log, processed locally for auto-session measure |
| `memory/skill-performance.md` | Velocity and quality metrics per cycle |
| `memory/security-gate-state.json` | Active security gate state for the stop hook |
| `memory/connectors/` | Connector configuration (most files git-ignored) |

---

## Requirements

- Claude Code CLI (any recent version)
- Python 3.8+ (standard library only — no pip installs required)
- Git

**Skills that require additional tools (optional):**
| Skill | Tool required |
|---|---|
| `ship`, `review`, `deploy` | `gh` (GitHub CLI) |
| `dependency-audit` | `npm` (for Node projects), `pip` (for Python projects) |
| `benchmark` | Browser / Lighthouse (auto-detected) |
| `qa`, `qa-only` | `pytest` or project test runner |

---

## Installation

```bash
# From the plugin's own marketplace
claude plugin install prodmaster-ai@prodmaster-ai-marketplace

# Verify
claude plugin list

# Get started
/prodmasterai help
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## License

MIT — see [LICENSE](LICENSE).

**Author:** Sujith Krishnan — sujith.krishnan@techjays.com
**Organization:** techjays (https://techjays.com)
**Repository:** https://github.com/sujithkrishnan-dev/prodmaster-ai
