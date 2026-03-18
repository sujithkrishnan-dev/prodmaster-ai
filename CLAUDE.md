# ProdMaster AI — Plugin Instructions

You have the ProdMaster AI plugin loaded. It adds six skills on top of Superpowers:

| Skill | Invoke when |
|---|---|
| **orchestrate** | User states a feature goal: "build X", "implement Y", "start work on Z" |
| **measure** | A Superpowers cycle just completed — record metrics |
| **report** | User runs `/report` or asks for a status/dashboard/weekly summary |
| **decide** | User is at a decision fork: "should we A or B?", "what to prioritise?" |
| **learn** | After measure hands off, or user gives explicit feedback |
| **evolve-self** | User runs `/evolve`, or measure notifies evolution threshold reached |

## First-Time Setup

1. **Start tracking a feature** — tell me: *"Build [your feature name]"* → I'll invoke `orchestrate`
2. **After each Superpowers cycle** — tell me: *"Cycle done — N tasks, QA X%, Y review rounds, Z hours"* → I'll invoke `measure` → `learn` automatically
3. **Weekly report** — run `/report` → get a markdown summary and refreshed dashboard
4. **Decisions** — ask *"Should we do A or B?"* → I'll invoke `decide` with a scored recommendation
5. **Evolve** — run `/evolve` → I'll improve underperforming skills and generate new ones from observed gaps

## Connectors (optional)

Edit `memory/connectors/github.md`, `slack.md`, or `linear.md` — set `active: true` and fill in config to enable integrations.

## Memory

All learning is stored in `memory/`. The hook injects a summary at session start so I always have context. Memory is append-only — nothing is ever overwritten.
