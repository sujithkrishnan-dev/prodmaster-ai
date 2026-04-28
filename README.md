# ProdMaster AI

> Full-stack AI development operations for Claude Code — one command orchestrates your entire engineering workflow.

**Install:**
```bash
claude plugin install prodmaster-ai@prodmaster-ai-marketplace
```

**Or via the official marketplace (once listed):**
```bash
claude plugin install prodmaster-ai@claude-plugins-official
```

---

## What It Does

ProdMaster AI is a meta-orchestration layer for Claude Code. A single command — `/prodmasterai` — reads your current state and routes to the right operation automatically. It covers the full engineering lifecycle: feature planning, implementation, QA, code review, deployment, security auditing, performance benchmarking, and self-evolution.

The plugin improves itself over time: every N completed tasks it runs a convergence loop, detects skill gaps, and submits upstream PRs with improvements.

---

## Quick Start

```
/prodmasterai build user authentication
```

That's it. The plugin breaks the feature into tracked tasks, coordinates parallel subtasks, and auto-installs any needed plugins.

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
| `/prodmasterai resume` | Show what auto-pilot did, per-decision review and rollback |
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

## Active Safety Hooks

The plugin installs four hooks that run automatically:

| Hook | Fires on | What it does |
|---|---|---|
| `session-start` | Session open | Injects active features, patterns, gaps, open tasks, installed plugins |
| `pre-tool-bash` | Every Bash call | Blocks: `rm -rf`, force push, `git reset --hard`, `DROP TABLE`, `chmod 777`, pipe-to-shell, base64-to-shell, PATH hijack, AWS key exports |
| `post-tool-write` | Every Write/Edit | Passive scanner: AWS/GitHub/OpenAI keys, private key material, SQL injection, XSS sinks, unsafe deserialization. Blocks on critical secrets. |
| `stop-quality-gate` | Claude stop | Blocks session exit when: critical secrets leaked, critical CVEs unfixed, tests failing during ship/deploy |

All hooks are implemented in pure Python (no external dependencies) and fail open — a hook crash never silently blocks valid work.

---

## Optional Connectors

The plugin supports optional integrations. All are inactive by default and require explicit opt-in:

| Connector | How to activate |
|---|---|
| GitHub | Set `active: true` in `memory/connectors/github.md`, configure MCP server |
| Slack | Set `active: true` in `memory/connectors/slack.md`, add webhook URL |
| Linear | Set `active: true` in `memory/connectors/linear.md`, configure MCP server |
| Superpowers | Set `active: true` in `memory/connectors/superpowers.md` |

Credential files (`slack.md`, `linear.md`) are listed in `.gitignore` and never committed.

---

## External Services

The plugin makes no outbound network calls on its own. External network access only occurs when:

- A connector is explicitly activated by the user and a Claude Code MCP server is configured
- A skill uses Claude Code's built-in `WebSearch` or `WebFetch` tools (user-approved per-call)
- The `dependency-audit` skill calls package registry APIs to check CVEs (advisory, not automatic)

No telemetry. No analytics. No data leaves the machine unless you configure a connector.

---

## Memory and State

All state is stored locally in `memory/`. Nothing is sent upstream. Files in `memory/` are excluded from plugin update PRs — your session data, usage logs, and connector configs stay on your machine.

The plugin tracks:
- `memory/usage-log.md` — per-invocation log (processed locally for auto-session measure)
- `memory/skill-performance.md` — velocity and quality metrics per cycle
- `memory/security-gate-state.json` — active security gate state for the stop hook
- `memory/connectors/` — connector configuration (most files git-ignored)

---

## Requirements

- Claude Code CLI (any recent version)
- Python 3.8+ (for hooks — standard library only, no pip installs required)
- Git

---

## Installation

```bash
# From the plugin's own marketplace
claude plugin install prodmaster-ai@prodmaster-ai-marketplace

# Verify installation
claude plugin list
```

After installation, start any session and run:
```
/prodmasterai help
```

---

## License

MIT — see [LICENSE](LICENSE).

**Author:** sujithkrishnan-dev — sujith.krishnan@techjays.com
**Repository:** https://github.com/sujithkrishnan-dev/prodmaster-ai
