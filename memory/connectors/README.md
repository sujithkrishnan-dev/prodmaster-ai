# Connector Interface

Activate a connector by setting `active: true` in the connector file and filling in the Config section. Remove the file or set `active: false` to deactivate. No code changes needed.

## Supported Connectors

| File | Integration | Skills that use it |
|---|---|---|
| `github.md` | GitHub Issues and PRs | orchestrate, evolve-self |
| `slack.md` | Slack webhook | report, evolve-self |
| `linear.md` | Linear issue tracking | orchestrate, report |
| `superpowers.md` | Superpowers plugin (TDD execution) | orchestrate — auto-detects, offers install on first use |

## Connector File Format

```yaml
---
connector: <name>
active: true
---
## Config
mcp_server: <mcp server registered in Claude Code>
default_repo: owner/repo      # github only
webhook_url: ""               # slack only
workspace_id: ""              # linear only
## State
last_sync: YYYY-MM-DD
```

## skill-pattern-manifest.md

Auto-maintained by `evolve-self`. Lists pattern keywords per skill used by `learn` for gap detection. Do not edit manually.
