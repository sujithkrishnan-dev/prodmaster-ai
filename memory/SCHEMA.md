# Memory Schema

The `memory/` directory holds all local plugin state. Files here are:
- **Local-only** — never sent upstream or included in PRs
- **Append-only** — existing entries are never overwritten or deleted
- **Machine-readable** — YAML frontmatter blocks separated by `---`, or inline markdown comments

---

## File Reference

### `usage-log.md`

Tracks every `/prodmasterai` invocation for auto-session measure.

**Format:** One markdown list entry per invocation.
```
- <ISO-8601 timestamp> | route: <skill-name> | processed: <true|false>
```

**Written by:** `prodmasterai` (master entry point) — appends one entry per invocation.
**Read by:** `session-start` hook — scans for entries where `processed: false` and fires a silent measure cycle. `prodmasterai` marks entries `processed: true` after auto-measure fires.

---

### `skill-performance.md`

Velocity and quality metrics captured after each completed cycle.

**Format:** YAML entry blocks separated by `---`.
```yaml
---
date: YYYY-MM-DD
feature: <feature or task name>
tasks_completed: <integer>
velocity_tasks_per_week: <float>
qa_pass_rate: <0.0–1.0>
review_iterations: <integer>
time_per_feature_hours: <float>
blockers: <integer>
blocker_age_days_avg: <float>
blockers_encountered: <integer>   # optional, added in later entries
example: true                     # optional — omit from all calculations when present
---
```

**Written by:** `measure`.
**Read by:** `report`, `decide`, `evolve-self`.
Note: entries with `example: true` are sample/bootstrap rows and must be excluded from all metric calculations.

---

### `evolution-log.md`

Local history of skill improvements and newly generated skills. Does not track upstream-merged changes (see root `EVOLUTION-LOG.md` for those).

**Format:** YAML entry blocks separated by `---`.
```yaml
---
date: YYYY-MM-DD
mode: improve | generate | no-op
skill: <skill name, or "" for no-op>
trigger: <what caused this evolution>
change_summary: <one sentence>
upstream_status: merged | pending | n/a
pr_url: "<GitHub PR URL>"   # optional, present when merged
---
```

**Written by:** `evolve-self`.
**Read by:** `evolve-self` (to avoid re-applying identical changes), `resume`.

---

### `connectors/github.md`

GitHub integration connector configuration.

**Format:** YAML frontmatter + markdown sections.
```yaml
---
connector: github
active: false
---
## Config
mcp_server: <name of MCP server registered in Claude Code>
default_repo: owner/repo
## State
last_sync: YYYY-MM-DD
```

Set `active: true` to enable GitHub integration (Issues, PRs). Set `active: false` or delete to disable.
**Read by:** `orchestrate`, `report`, `smooth-dev` (when connector is active).
**Not git-ignored** — contains no secrets.

---

### `connectors/slack.md`

Slack webhook connector configuration.

**Format:** YAML frontmatter + markdown sections.
```yaml
---
connector: slack
active: false
---
## Config
mcp_server: ""
webhook_url: ""
## State
last_sync: YYYY-MM-DD
```

**IMPORTANT: This file is listed in `.gitignore` and is never committed.** The `webhook_url` field is a secret. Do not remove it from `.gitignore`.
**Read by:** `report`, `measure` (when connector is active).

---

### `connectors/linear.md`

Linear issue tracking connector. Format mirrors `github.md`.
**IMPORTANT: Also git-ignored** — may contain API tokens. Never committed.

---

## Git-ignored files

The following memory files are excluded from version control:
- `memory/connectors/slack.md` — contains webhook URL
- `memory/connectors/linear.md` — may contain API tokens

All other memory files are also effectively local-only because the `memory/` directory is not pushed upstream (plugin PRs only contain skill and hook changes).

---

## Adding new memory fields

See [docs/EXTENDING.md](../docs/EXTENDING.md#adding-new-memory-fields) for the full procedure. Short version: add to new entries only, never backfill, document the field in a comment at the top of the memory file, and update the skill that writes it.
