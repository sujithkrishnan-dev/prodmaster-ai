# ProdMaster AI

A Claude Code plugin that sits above Superpowers to orchestrate features, measure productivity, support decisions, and **evolve itself** over time.

## Installation

```bash
claude plugin marketplace add sujithkrishnan-dev/prodmaster-ai
claude plugin install prodmaster-ai@prodmaster-ai-marketplace
```

### Local Development

```bash
git clone https://github.com/sujithkrishnan-dev/prodmaster-ai ~/.claude/plugins/prodmaster-ai
cd ~/.claude/plugins/prodmaster-ai
claude plugin install prodmaster-ai@prodmaster-ai-marketplace
```

### Platform Hook Setup

**Windows:** works out of the box (uses `run-hook.cmd` + PowerShell).

**macOS/Linux:** Edit `hooks/hooks.json` and `.claude-plugin/hooks.json`, change the SessionStart command to:
```json
"command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.sh\" session-start"
```

The PreToolUse hook (`hooks/pre-tool-bash.py`) requires Python 3 on PATH — available by default on macOS/Linux.

## The One Command

```
/prodmasterai
```

The plugin reads your current state and decides what to do. No need to remember skill names.

| You say | Plugin does |
|---|---|
| `/prodmasterai help` | `help` — shows all skills, triggers, and examples |
| `/prodmasterai pull latest` | `smooth-dev` — git pull, repo health check, run tests |
| `/prodmasterai build X` | `orchestrate` — breaks feature into tracked tasks, parallel subtasks, auto-installs needed plugins |
| `/prodmasterai cycle done — …` | `measure` → `learn` auto-fires (parallel writes) |
| `/prodmasterai should we A or B?` | `decide` — scored recommendation |
| `/prodmasterai report` | Prints full report directly in terminal (no files written) |
| `/prodmasterai queue add X` | `task-queue` — adds goal to sequential execution queue |
| `/prodmasterai queue list` | `task-queue` — shows pending/running/done queue |
| `/prodmasterai queue run` | `task-queue` — runs all queued tasks sequentially, auto-advances |
| `/prodmasterai explore X` | `parallel-explore` — runs 2+ approaches in separate worktrees, picks best by test pass rate |
| `/prodmasterai auto X` | `auto-pilot` — fully autonomous: brainstorm → plan → implement → test → PR |
| `/auto-pilot-revoke` | `auto-pilot-revoke` — stops running auto-pilot, commits progress, resets lock |
| `/prodmasterai resume` | `resume` — shows what auto-pilot did, per-decision review and rollback |
| `/prodmasterai plugins` | `plugin-manager` — shows installed/available plugins, auto-installs when needed |
| `/evolve` | `evolve-self` — convergence loop until all skills clean |
| `/prodmasterai update` | Push locally evolved improvements upstream via PR |
| `/prodmasterai` (no args) | Reads state, acts or prompts with exactly one question |

## Skills

| Skill | Trigger | Job |
|---|---|---|
| `prodmasterai` | `/prodmasterai` | Master entry point — reads state, routes to the right skill automatically |
| `help` | "help" / "what can you do" / "show commands" | List all skills, triggers, and one-line examples |
| `smooth-dev` | "pull latest" / "start dev" / "pre-flight" | Pull latest, health-check repo, run tests, surface blockers |
| `orchestrate` | "Build X" / feature goal | Break into task cycles, dispatch independent subtasks in parallel, auto-install needed plugins |
| `measure` | After each cycle | Capture velocity, QA rate, blockers — parallel writes |
| `report` | `/prodmasterai report` | Print full report directly in terminal; bootstrap if no cycle data yet |
| `decide` | At a decision fork | ROI-ranked recommendation |
| `learn` | After cycle or on feedback | Patterns, mistakes, gaps — parallel write ‖ gap detection |
| `task-queue` | `/prodmasterai queue` | Manage sequential execution queue — add, list, run |
| `parallel-explore` | `/prodmasterai explore` | Run 2+ approaches in separate worktrees, pick best by test pass rate |
| `auto-pilot` | `/prodmasterai auto` | Full autonomous pipeline: brainstorm, plan, implement, test, PR — no questions asked |
| `auto-pilot-revoke` | `/auto-pilot-revoke` | Stop running auto-pilot, commit progress, reset lock |
| `resume` | `/prodmasterai resume` | Show autonomous session audit: every decision made, with per-decision rollback |
| `plugin-manager` | `/prodmasterai plugins` | Show installed/available plugins, auto-install when needed |
| `evolve-self` | Every N tasks or `/evolve` | Convergence loop: improve skills + generate new ones until clean |
| `token-efficiency` | "token efficiency" / "reduce tokens" / "I'm hitting limits" | Audit, enforce, and rewrite plugin operations to reduce token consumption |

## Hooks

| Hook | Event | What it does |
|---|---|---|
| `run-hook.cmd` / `run-hook.sh` | SessionStart | Injects memory context (active features, patterns, gaps, evolutions) |
| `pre-tool-bash.py` | PreToolUse (Bash) | Blocks destructive commands: `rm -rf`, force push, `git reset --hard`, `DROP TABLE`, etc. |

## Connectors

Edit `memory/connectors/<name>.md`, set `active: true`, fill in config.

| Connector | Integration |
|---|---|
| `github.md` | GitHub Issues/PRs |
| `slack.md` | Slack webhook |
| `linear.md` | Linear issue tracking |

Official plugins (47 available) are auto-detected from `~/.claude/plugins/cache/` and auto-installed when needed. See `memory/connectors/official-plugins-registry.md` for the full list.

## Upstream Evolution

`evolve-self` runs a **convergence loop** — no fixed iteration cap. It reruns until a full pass over all changed skills finds zero issues. Each pass checks all skills in parallel.

- Outcome/research improvements → automatic PR (no confirmation needed)
- Feedback improvements → asks you first, then creates PR on confirmation
- PRs created immediately on `/prodmasterai update` — no time-based rate limit
- Run `/prodmasterai update` to push pending improvements

## Report

`/prodmasterai report` prints a full report directly in the terminal. If no cycle data exists yet, it asks what you want to build — no passive zero-metrics output.

## Auto-Evolution Flow

```
Superpowers cycle completes
  orchestrate → measure (parallel writes) → learn (parallel threads)
  (every N tasks) → evolve-self fires automatically
    Mode 1: research underperforming skills in parallel → apply improvements
    Mode 2: generate skills for gaps with 3+ occurrences
    Convergence loop: rerun until all changed skills are clean
    (explicit /prodmasterai update) → upstream PR pipeline

Auto-session tracking: Every /prodmasterai invocation is logged to memory/usage-log.md.
At next session start, if unprocessed invocations exist, measure cycle fires silently
with inferred defaults — no "cycle done" command needed.
```

## Parallelism

All skills run independent operations in parallel:
- `orchestrate` — reads context + GitHub + Linear simultaneously; dispatches independent subtasks in parallel
- `measure` — writes to skill-performance.md ‖ project-context.md; learn handoff ‖ threshold check
- `learn` — pattern/mistake write ‖ gap detection
- `evolve-self` — all research subagents dispatched simultaneously; all file checks per convergence pass run in parallel
- `report` — all data source reads dispatched simultaneously
