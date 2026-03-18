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
/prodmasterai update
```

**Standalone (auto-decides based on context):**
```
/prodmasterai
```

---

## What Happens Automatically

| You say | Plugin does |
|---|---|
| `/prodmasterai help` | `help` — shows all skills, triggers, and examples |
| `/prodmasterai pull latest` | `smooth-dev` — git pull, repo health check, run tests, surface blockers, print session card |
| `/prodmasterai build X` | `orchestrate` — breaks feature into tracked tasks, dispatches independent subtasks in parallel |
| `/prodmasterai cycle done — …` | `measure` → `learn` auto-fires (parallel writes) |
| `/prodmasterai should we A or B?` | `decide` — scored recommendation |
| `/prodmasterai report` | Markdown + HTML dashboard in `reports/`; fresh-state bootstrap if no data yet |
| `/evolve` | `evolve-self` — convergence loop: runs until all changed skills are clean; upstream PR only on explicit publish |
| `/prodmasterai update` | Push all locally evolved improvements upstream via PR |
| `/prodmasterai` (no args) | Reads state, acts or prompts with exactly one question |

---

## Hooks (active automatically)

| Hook | Fires on | What it does |
|---|---|---|
| `session-start` | Session open | Injects active features, top patterns, open gaps, recent evolutions into context |
| `pre-tool-bash.py` | Every Bash call | Blocks: `rm -rf`, force push, `git reset --hard`, `git clean -f`, `DROP TABLE/DATABASE`. Allows safe dev commands through immediately. |

---

## Connectors (optional)

Edit `memory/connectors/github.md`, `slack.md`, or `linear.md` — set `active: true` and fill in config.

---

## Memory

All learning is stored in `memory/`. The hook injects context at session start. Memory is append-only — nothing is ever overwritten. Memory files never leave this machine; only plugin code improvements go upstream.

---

## Self-Evolution

The plugin improves itself automatically:
- Every N completed tasks (default: 10), `evolve-self` fires silently and runs a **convergence loop** — no fixed iteration cap, reruns until a full pass finds zero issues
- All research subagents and per-file checks run in parallel
- Local improvements stay local until you run `/prodmasterai update`
- Upstream PRs are never created automatically — always require explicit publish confirmation
