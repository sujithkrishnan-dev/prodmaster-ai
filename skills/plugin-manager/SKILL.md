---
name: plugin-manager
description: Auto-detect, install, and activate Claude Code official plugins. Called by orchestrate and other skills before invoking plugin-dependent capabilities. Never just suggests — always installs.
version: 1.0.0
triggers:
  - /prodmasterai plugins
  - /prodmasterai install plugin
  - install plugin
  - what plugins are installed
  - check plugins
  - plugin status
reads:
  - memory/connectors/official-plugins-registry.md
writes: []
generated: false
generated_from: ""
---

# Plugin Manager

Auto-detect and install official Claude Code plugins. When a skill needs a plugin that isn't installed, this skill installs it immediately — no manual steps, no copy-pasting commands.

---

## Auto-Install Protocol

When any skill determines it needs an official plugin:

1. **Check installed:** Look up `~/.claude/plugins/cache/<plugin-name>/`. If directory exists: plugin is installed — skip to step 3.
2. **Install silently:**
   ```bash
   claude plugin install <plugin-name>@claude-plugins-official
   ```
   Wait for completion. If exit code != 0: report the error and stop — do not proceed as if the plugin is available.
3. **Confirm and continue:** Output one line: `Plugin <name> ready.` then proceed with the original task.

Never ask the user "should I install this?" — just install it. The user's original request is the authorization.

---

## Sub-command: status

Triggered by: `/prodmasterai plugins`, "what plugins are installed", "plugin status"

1. Check `~/.claude/plugins/cache/` for all installed plugin directories.
2. Read `memory/connectors/official-plugins-registry.md` for the full plugin list.
3. Print:

```
Installed plugins:
  [name] v[version]
  [name] v[version]
  ...

Available to install (from claude-plugins-official):
  [name] — [description]
  [name] — [description]
  ...

Install any: claude plugin install <name>@claude-plugins-official
```

---

## Plugin → Task Type Mapping

Skills use this mapping to decide which plugin to auto-install:

| Task type | Required plugin |
|---|---|
| E2E / browser testing | `playwright` |
| Security audit | `security-guidance` |
| Static analysis | `semgrep` (or `security-guidance` as fallback) |
| PR review | `pr-review-toolkit` |
| Live library docs | `context7` |
| Semantic refactoring | `serena` |
| GitHub API | `github` |
| Supabase backend | `supabase` |
| Deployment (Vercel) | `vercel` |
| Deployment (Railway) | `railway` |
| Commit / push / PR | `commit-commands` |
| Feature planning (alt) | `feature-dev` |
| MCP server building | `mcp-server-dev` |
| Claude plugin building | `plugin-dev` |

---

## Rules

- Never just suggest — always install
- Never ask permission — the user's task request is the authorization
- If install fails: report error clearly, do not silently continue as if plugin is available
- Log installed plugins to context after installation so other skills can see them
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
