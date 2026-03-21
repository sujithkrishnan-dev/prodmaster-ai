# Official Claude Plugins Registry

Source: https://github.com/anthropics/claude-plugins-official (47 plugins, Anthropic-maintained)
Install: `claude plugin install <name>@claude-plugins-official`
Browse: `/plugin > Discover` in Claude Code

<!-- session-start reads installed plugins from ~/.claude/plugins/cache/ -->
<!-- orchestrate reads this file to suggest relevant plugins per task type -->

---

## Internal Plugins (Anthropic-authored)

### Development Workflow

| Plugin | Install Name | What It Adds |
|---|---|---|
| Feature Dev | `feature-dev` | End-to-end feature planning: codebase exploration, architecture design, quality review |
| Commit Commands | `commit-commands` | Streamline git: commit, push, PR creation in one command |
| Code Review | `code-review` | Multi-agent PR analysis with confidence scoring |
| PR Review Toolkit | `pr-review-toolkit` | Full-spectrum PR review: comments, tests, error handling, types, quality, simplification |
| Code Simplifier | `code-simplifier` | Refactoring for clarity, consistency, maintainability |
| Security Guidance | `security-guidance` | Passive hook: alerts on injection, XSS, unsafe patterns on every file edit |
| Hookify | `hookify` | Create custom hooks to block unwanted behaviors |

### Plugin & Tool Development

| Plugin | Install Name | What It Adds |
|---|---|---|
| Plugin Dev | `plugin-dev` | 7 skills for building Claude Code plugins |
| Skill Creator | `skill-creator` | Author, optimize, and benchmark skills |
| MCP Server Dev | `mcp-server-dev` | Design and build MCP servers (HTTP, local, auth) |
| Agent SDK Dev | `agent-sdk-dev` | Claude Agent SDK scaffolding |
| Claude Code Setup | `claude-code-setup` | Analyze codebase, recommend hooks/skills/MCPs |
| CLAUDE.md Manager | `claude-md-management` | Maintain and improve CLAUDE.md project memory |

### UI & Frontend

| Plugin | Install Name | What It Adds |
|---|---|---|
| Frontend Design | `frontend-design` | UI/UX implementation skill |
| Playground | `playground` | Interactive HTML prototyping explorer |

### Automation

| Plugin | Install Name | What It Adds |
|---|---|---|
| Superpowers | `superpowers` | TDD, writing plans, subagent-driven dev, brainstorming |
| Ralph Loop | `ralph-loop` | Continuous iterative loops until task completion |

### Language Servers (LSPs)

| Plugin | Install Name | Language |
|---|---|---|
| Pyright | `pyright-lsp` | Python type checking |
| TypeScript LSP | `typescript-lsp` | TypeScript diagnostics |
| Rust Analyzer | `rust-analyzer` | Rust type inference |
| Gopls | `gopls-lsp` | Go |
| Ruby LSP | `ruby-lsp` | Ruby |
| Clangd | `clangd-lsp` | C/C++ |
| C# LSP | `csharp-lsp` | C# |
| Java (JDTLS) | `jdtls-lsp` | Java |
| Kotlin | `kotlin-lsp` | Kotlin |
| Lua LSP | `lua-lsp` | Lua |
| PHP LSP | `php-lsp` | PHP |
| Swift LSP | `swift-lsp` | Swift |

---

## External Plugins (Partner-authored)

| Plugin | Author | Install Name | What It Adds |
|---|---|---|---|
| GitHub | GitHub | `github` | Full GitHub API: PRs, issues, code review, repo search |
| GitLab | GitLab | `gitlab` | MRs, CI/CD pipelines, issues, wikis |
| Linear | Linear | `linear` | Issue/project management, workflow integration |
| Playwright | Microsoft | `playwright` | Browser automation, E2E testing, screenshots |
| Greptile | Greptile | `greptile` | AI-powered PR review from GitHub/GitLab in Claude Code |
| Serena | Oraios | `serena` | Semantic code analysis + refactoring via LSP |
| Context7 | Upstash | `context7` | Live, version-specific library docs injected into context |
| Supabase | Supabase | `supabase` | DB, auth, storage, real-time subscriptions |
| Slack | Slack | `slack` | Send/read messages, channel management |
| Firebase | Firebase | `firebase` | Firestore, auth, storage operations |
| Asana | Asana | `asana` | Task/project creation, updates, search |

---

## Recommended for This Plugin's Workflow

Ranked by direct impact on ProdMaster AI use cases:

1. **github** — GitHub API for PRs/issues (complements existing github.md MCP connector)
2. **pr-review-toolkit** — Deep PR review across all quality dimensions
3. **context7** — Live docs = accurate library usage in orchestrated features
4. **security-guidance** — Passive hook, catches issues on every edit automatically
5. **commit-commands** — Streamlines the commit/push/PR loop
6. **feature-dev** — Parallel to orchestrate; use for exploration vs. orchestrate for tracking
7. **serena** — Semantic refactoring for large codebases
8. **playwright** — E2E tests for features involving UI

---

## Detection

`session-start` checks `~/.claude/plugins/cache/` at session open.
Each subdirectory is an installed plugin (format: `<name>/<version>/`).
Installed plugins are injected as: `Installed plugins: <name> (v<version>), ...`

If a task type is requested (browser testing, deployment, security audit, etc.) and the
relevant plugin is not installed, skills may suggest:
`claude plugin install <name>@claude-plugins-official`
