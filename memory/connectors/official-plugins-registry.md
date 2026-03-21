# Official Claude Plugins Registry

Auto-maintained reference of useful official plugins from `claude-plugins-official`.
Install any plugin with: `claude plugin install <name>@claude-plugins-official`

<!-- Source: https://github.com/anthropics/claude-plugins-official -->
<!-- Skills that read this: orchestrate (plugin suggestion), session-start (detection) -->

---

## Development & Code Quality

| Plugin | Install Name | What It Adds |
|---|---|---|
| Superpowers | `superpowers` | TDD, writing plans, subagent-driven development, brainstorming |
| Code Review | `code-review` | Automated PR reviews with structured feedback |
| Code Simplifier | `code-simplifier` | Refactoring and complexity reduction skills |
| Autofix Bot | `autofix-bot` | Auto-fixes lint errors, type errors, test failures |
| Security Guidance | `security-guidance` | Security audit, OWASP checks, dependency scanning |
| Plugin Dev | `plugin-dev` | Skills for building new Claude Code plugins |
| Skill Creator | `skill-creator` | Generate new skill files from descriptions |

## Testing & Quality Gates

| Plugin | Install Name | What It Adds |
|---|---|---|
| Playwright | `playwright` | Browser automation, E2E test generation |
| Semgrep | `semgrep` | Static analysis, code quality scanning |
| Aikido Security | `aikido` | Vulnerability scanning, SAST |

## Cloud & Deployment

| Plugin | Install Name | What It Adds |
|---|---|---|
| Vercel | `vercel` | Deploy, preview URLs, project management |
| Railway | `railway` | Container deployment, environment management |
| AWS Serverless | `aws-serverless` | Lambda, API Gateway, CloudFormation |
| Netlify Skills | `netlify` | Build hooks, deploy previews, forms |

## Databases

| Plugin | Install Name | What It Adds |
|---|---|---|
| Supabase | `supabase` | Database, auth, storage, edge functions |
| Prisma | `prisma` | Schema management, migrations, query generation |
| Neon | `neon` | Serverless Postgres, branching |
| PlanetScale | `planetscale` | MySQL branching, schema changes |

## Integrations

| Plugin | Install Name | What It Adds |
|---|---|---|
| GitHub | `github` | Issues, PRs, Actions (also available as MCP connector) |
| GitLab | `gitlab` | MR reviews, CI pipelines, issue management |
| Linear | `linear` | Issue tracking, roadmaps (also available as MCP connector) |
| Sentry | `sentry` | Error monitoring, stack trace analysis |
| PagerDuty | `pagerduty` | On-call, incident management |

## Language Servers (LSPs)

| Plugin | Install Name | What It Adds |
|---|---|---|
| Pyright | `pyright-lsp` | Python type checking, completions |
| TypeScript LSP | `typescript-lsp` | TS type info, diagnostics |
| Rust Analyzer | `rust-analyzer` | Rust type inference, completions |
| Gopls | `gopls-lsp` | Go language server |
| Ruby LSP | `ruby-lsp` | Ruby diagnostics, formatting |

---

## Detection

`session-start` checks `~/.claude/plugins/cache/` for installed plugins and injects a one-line summary:
`Installed plugins: superpowers (v5.0.5), code-review (v1.2.0)`

## Connector Files

Active integrations are configured in `memory/connectors/`:
- `superpowers.md` — Superpowers plugin (active/inactive toggle)
- `github.md` — GitHub MCP connector
- `slack.md` — Slack webhook
- `linear.md` — Linear MCP connector

To add a connector for a new plugin: create `memory/connectors/<plugin-name>.md` following the format in `README.md`.
