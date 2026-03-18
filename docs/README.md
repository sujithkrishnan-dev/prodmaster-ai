# ProdMaster AI

A Claude Code plugin that sits above Superpowers to orchestrate features, measure productivity, support decisions, and **evolve itself** over time.

## Installation

### Manual (local development)

```bash
git clone <this-repo> ~/.claude/plugins/prodmaster-ai
```

Then in Claude Code:
```
/plugin install --local ~/.claude/plugins/prodmaster-ai
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
| `/prodmasterai build X` | `orchestrate` — breaks feature into tracked task cycles |
| `/prodmasterai cycle done — N tasks, QA X%, Y reviews, Z hours` | `measure` → `learn` auto-fires |
| `/prodmasterai should we A or B?` | `decide` — ROI-ranked recommendation |
| `/prodmasterai report` | Markdown weekly report + HTML dashboard in `reports/` |
| `/evolve` | `evolve-self` — convergence loop until all skills clean; upstream PR only on explicit publish |
| `/prodmasterai update` | Push locally evolved improvements upstream via PR |
| `/prodmasterai` (no args) | Reads state, acts or asks exactly one question |

## Skills

| Skill | Trigger | Job |
|---|---|---|
| `prodmasterai` | `/prodmasterai` | Master entry point — reads state, routes to the right skill automatically |
| `smooth-dev` | "pull latest" / "start dev" / "pre-flight" | Pull latest, health-check repo, run tests, surface blockers, print session card |
| `orchestrate` | "Build X" / feature goal | Break into task cycles, dispatch independent subtasks in parallel |
| `measure` | After each Superpowers cycle | Capture velocity, QA rate, blockers — parallel writes |
| `report` | `/prodmasterai report` | Markdown report + HTML dashboard; fresh-state bootstrap if no data yet |
| `decide` | At a decision fork | ROI-ranked recommendation |
| `learn` | After cycle or on feedback | Patterns, mistakes, gaps — parallel write ‖ gap detection |
| `evolve-self` | Every N tasks or `/evolve` | Convergence loop: improve skills + generate new ones until clean |

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

## Upstream Evolution

`evolve-self` runs a **convergence loop** — no fixed iteration cap. It reruns until a full pass over all changed skills finds zero issues. Each pass checks all skills in parallel.

- Outcome/research improvements → automatic PR (no confirmation needed)
- Feedback improvements → asks you first, then creates PR on confirmation
- Max 1 upstream PR per 24 hours
- Run `/prodmasterai update` to push pending improvements

## Dashboard

After `/prodmasterai report`, open `reports/dashboard.html` in any browser. No server needed.

If no cycle data exists yet, report writes `reports/getting-started-YYYY-MM-DD.md` and immediately asks what you want to build — no passive zero-metrics output.

## Auto-Evolution Flow

```
Superpowers cycle completes
  orchestrate → measure (parallel writes) → learn (parallel threads)
  (every N tasks) → evolve-self fires automatically
    Mode 1: research underperforming skills in parallel → apply improvements
    Mode 2: generate skills for gaps with 3+ occurrences
    Convergence loop: rerun until all changed skills are clean
    (explicit /prodmasterai update) → upstream PR pipeline
```

## Parallelism

All skills run independent operations in parallel:
- `orchestrate` — reads context + GitHub + Linear simultaneously; dispatches independent subtasks in parallel
- `measure` — writes to skill-performance.md ‖ project-context.md; learn handoff ‖ threshold check
- `learn` — pattern/mistake write ‖ gap detection
- `evolve-self` — all research subagents dispatched simultaneously; all file checks per convergence pass run in parallel
- `report` — all data source reads dispatched simultaneously
