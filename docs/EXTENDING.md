# Adding to ProdMaster AI

How to extend the plugin with new skills, connectors, and memory fields.

---

## Adding a New Skill

### 1. Create the skill directory and file

```
skills/<your-skill-name>/SKILL.md
```

Every skill file **must** start with this frontmatter block:

```markdown
---
name: <your-skill-name>
description: One-line trigger description — this is what Claude reads to decide whether to invoke this skill. Be specific about WHEN to use it.
version: 1.0.0
triggers:
  - Plain language condition, e.g. "User says X"
  - Another condition
reads:
  - memory/project-context.md      # list every memory file you read
writes:
  - memory/project-context.md      # list every memory file you write
generated: false
generated_from: ""
---
```

After the frontmatter, write the skill body in plain markdown. Follow the structure used by the existing skills:

```markdown
# Skill Title

One sentence: what does this skill do.

## Process

### 1. Read Context
...

### 2. Do the Work
...

### 3. Update Memory
...

## Rules

- Rule 1
- Rule 2
```

### 2. Add keywords to the pattern manifest

Open `memory/connectors/skill-pattern-manifest.md` and append:

```markdown

### <your-skill-name>
keywords: [keyword1, keyword2, keyword3, ...]
```

These keywords are how the `learn` skill detects that your skill covers a pattern (so it does not create a gap entry for it).

### 3. Write a test

Add a parametrized entry to `tests/test_skills.py` — the `ALL_SKILLS` list:

```python
ALL_SKILLS = ["orchestrate", "measure", "report", "decide", "learn", "evolve-self", "your-skill-name"]
```

Run `python -m pytest tests/test_skills.py -v` to confirm your skill passes frontmatter validation.

### 4. Document it in docs/README.md

Add a row to the Skills table:

```markdown
| `your-skill-name` | "trigger phrase" | What it does |
```

---

## Adding a New Connector

Connectors activate integrations by presence. No code changes required — just a file.

### 1. Create the connector file

```
memory/connectors/<name>.md
```

```markdown
---
connector: <name>
active: false
---
## Config
mcp_server: <mcp server name registered in Claude Code>
## State
last_sync: 1970-01-01
```

Set `active: true` to enable it. Set `active: false` or delete the file to disable.

### 2. Document which skills check for it

In each skill that should use this connector, add to the `reads:` frontmatter list:

```yaml
reads:
  - memory/connectors/<name>.md
```

Then in the skill body, add a conditional section:

```markdown
If `<name>` connector is active (`memory/connectors/<name>.md` has `active: true`): ...
```

### 3. Add it to the connector README

Open `memory/connectors/README.md` and add a row to the table:

```markdown
| `<name>.md` | What it integrates | Which skills use it |
```

---

## Adding New Memory Fields

Memory files use append-only YAML entry blocks separated by `---`. To add a new field to existing entries:

1. **Add it to new entries only** — never backfill old entries. Old entries without the field are valid.
2. **Document the schema** in a comment at the top of the memory file.
3. **Update the relevant skill** that writes this file to include the new field.
4. **Update `evolve-self`** if the new field should inform evolution decisions.

### Example: adding `time_per_task_hours` to `skill-performance.md`

In `memory/skill-performance.md`, update the schema comment:
```markdown
# Skill Performance Log
<!-- New field from v1.1.0: time_per_task_hours (optional) -->
```

In `skills/measure/SKILL.md`, add to the append template:
```yaml
time_per_task_hours: <time_hours / tasks_completed>
```

---

## Modifying an Existing Skill

1. Edit `skills/<name>/SKILL.md` directly.
2. Increment the `version:` field in the frontmatter (e.g. `1.0.0` → `1.1.0`).
3. Run `python -m pytest tests/ -v` — your edit must not break frontmatter validation.
4. Commit: `git commit -m "improve: <skill-name> — <what changed>"`

If the change is significant and you want it to reach all users of the plugin, open a PR against the upstream repo (`sujithkrishnan-dev/prodmaster-ai`). The `evolve-self` skill does this automatically for performance-driven improvements.

---

## How evolve-self generates new skills

When the `learn` skill records a skill gap entry in `memory/skill-gaps.md` with `occurrences >= 3` and `status: open`, the next `/evolve` run will auto-generate a new skill file using the gap pattern as its specification.

To influence what gets generated:
- Write clear, specific gap patterns — the generated skill title and description come directly from them.
- A gap like `"user asks for sprint planning but no skill handles it"` produces a better skill than `"sprint"`.

Generated skills have `generated: true` and `generated_from: <gap-id>` in their frontmatter. Review them after generation and refine the body if needed. Increment the version when you do.

---

## File layout reference

```
.claude-plugin/
  plugin.json           ← plugin manifest, upstream repo config

hooks/
  hooks.json            ← hook registration
  session-start.md      ← context template ({{placeholders}})
  run-hook.sh           ← Unix runner
  run-hook.cmd          ← Windows launcher
  run-hook.ps1          ← Windows PowerShell runner

skills/
  <name>/
    SKILL.md            ← required: frontmatter + body

memory/
  project-context.md    ← active features, blockers, decisions
  skill-performance.md  ← metrics per cycle (written by measure)
  patterns.md           ← what worked (written by learn)
  mistakes.md           ← what failed (written by learn)
  feedback.md           ← user feedback (write-restricted to learn)
  research-findings.md  ← evolve-self research output
  skill-gaps.md         ← unhandled patterns (written by learn)
  evolution-log.md      ← local evolution history
  pending-upstream/     ← staged PR proposals
  connectors/
    skill-pattern-manifest.md   ← keyword map for gap detection
    github.md                   ← GitHub connector config
    slack.md                    ← Slack connector config
    linear.md                   ← Linear connector config

reports/
  dashboard.html        ← generated by report skill
  weekly-YYYY-MM-DD.md  ← generated by report skill

tests/
  test_scaffold.py      ← validates manifest + dashboard
  test_hooks.py         ← validates hook files
  test_memory.py        ← validates memory file schemas
  test_skills.py        ← validates all skill frontmatter
  test_integration.py   ← full-plugin integration tests
  validate_all.sh       ← runs everything

EVOLUTION-LOG.md        ← upstream-merged changes only
docs/
  README.md             ← user-facing docs
  EXTENDING.md          ← this file
```
