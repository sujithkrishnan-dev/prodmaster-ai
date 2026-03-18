# ProdMaster AI — Plugin Instructions

You have the ProdMaster AI plugin loaded.

## The One Command You Need

```
/prodmasterai
```

That's it. The plugin reads your current state and decides what to do next — no need to remember skill names.

**With intent:**
```
/prodmasterai build user authentication
/prodmasterai cycle done — 5 tasks, QA 90%, 2 reviews, 3 hours
/prodmasterai should we use REST or GraphQL?
/prodmasterai report
```

**Standalone (auto-decides based on context):**
```
/prodmasterai
```

---

## What Happens Automatically

| You say | Plugin does |
|---|---|
| `/prodmasterai build X` | `orchestrate` — breaks feature into tracked tasks |
| `/prodmasterai cycle done — …` | `measure` → `learn` auto-fires |
| `/prodmasterai should we A or B?` | `decide` — scored recommendation |
| `/prodmasterai report` | Markdown + HTML dashboard in `reports/` |
| `/evolve` | `evolve-self` — improves skills, generates new ones, PRs upstream |
| `/prodmasterai` (no args) | Reads state, acts or prompts with one question |

---

## Connectors (optional)

Edit `memory/connectors/github.md`, `slack.md`, or `linear.md` — set `active: true` and fill in config.

## Memory

All learning is stored in `memory/`. The hook injects context at session start. Memory is append-only — nothing is ever overwritten. Memory files never leave this machine; only plugin code improvements go upstream.
