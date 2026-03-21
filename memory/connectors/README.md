# Connector Interface

Activate a connector by setting `active: true` in the connector file and filling in the Config section. Remove the file or set `active: false` to deactivate. No code changes needed.

## Supported Connectors

| File | Integration | Skills that use it |
|---|---|---|
| `github.md` | GitHub Issues and PRs | orchestrate, evolve-self |
| `slack.md` | Slack webhook | report, evolve-self |
| `linear.md` | Linear issue tracking | orchestrate, report |
| `superpowers.md` | Superpowers plugin (TDD execution) | orchestrate — auto-detects, offers install on first use |

## Official Plugins (auto-detected)

All installed Claude Code plugins are detected automatically at session start by reading `~/.claude/plugins/cache/`. No connector file needed — installed plugins are surfaced directly in session context.

See `official-plugins-registry.md` for the full list of available official plugins and install commands. Highlights:

| Plugin | Install | Best for |
|---|---|---|
| code-review | `code-review@claude-plugins-official` | Automated PR review |
| security-guidance | `security-guidance@claude-plugins-official` | Security audits |
| playwright | `playwright@claude-plugins-official` | E2E / browser tests |
| semgrep | `semgrep@claude-plugins-official` | Static analysis |
| vercel | `vercel@claude-plugins-official` | Deployment |
| supabase | `supabase@claude-plugins-official` | Database + auth |

Install any plugin: `claude plugin install <name>@claude-plugins-official`

## Security Notes

- `slack.md` contains a `webhook_url` secret — it is listed in `.gitignore` and will not be committed to git. Never remove it from `.gitignore`.
- `github.md` and `linear.md` use MCP servers — no tokens are stored in these files; credentials are managed by Claude Code.
- `superpowers.md` contains only a repo URL — not a secret, safe to commit.

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
