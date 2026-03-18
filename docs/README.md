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

**macOS/Linux:** Edit `hooks/hooks.json` and change the command to:
```json
"command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.sh\" session-start"
```

## Skills

| Skill | Trigger | Job |
|---|---|---|
| `orchestrate` | "Build X" / feature goal | Break into task cycles, track dependencies |
| `measure` | After each Superpowers cycle | Capture velocity, QA rate, blockers |
| `report` | `/report` | Markdown report + HTML dashboard |
| `decide` | At a decision fork | ROI-ranked recommendation |
| `learn` | After cycle or on feedback | Patterns, mistakes, gaps, feedback |
| `evolve-self` | Every N tasks or `/evolve` | Improve skills + generate new ones |

## Connectors

Edit `memory/connectors/<name>.md`, set `active: true`, fill in config. That's it.

| Connector | Integration |
|---|---|
| `github.md` | GitHub Issues/PRs |
| `slack.md` | Slack webhook |
| `linear.md` | Linear issue tracking |

## Upstream Evolution

When `evolve-self` runs, set `upstream.repo` in `.claude-plugin/plugin.json` to your fork's `owner/repo` to enable auto-PRs.

- Outcome/research improvements → automatic PR
- Feedback improvements → asks you first

## Dashboard

After `/report`, open `reports/dashboard.html` in any browser. No server needed.

## Auto-Evolution Flow

```
Superpowers cycle completes
  orchestrate → measure → learn
  (every N tasks) → evolve-self
    Mode 1: improve underperforming skills
    Mode 2: generate skills for repeated gaps
    upstream PR pipeline
```
