---
name: help
description: Use when the user asks what the plugin can do, asks for help, or seems lost. Lists all skills with triggers and examples.
version: 1.0.2
triggers:
  - User says "help", "/help", "what can you do", "show commands", "what skills", "how does this work"
  - User seems confused or asks an open-ended question about the plugin
reads: []
writes: []
generated: false
generated_from: ""
---

# Help -- ProdMaster AI Skill Reference

Print the card below exactly as formatted. Do not paraphrase. Do not add preamble.

---

## ProdMaster AI -- Skill Reference Card

---

### Setup

| Skill | Trigger | Example |
|---|---|---|
| `prodmasterai` | `/prodmasterai` (no args) | `/prodmasterai` -- reads state, acts or asks one question |
| `smooth-dev` | "pull latest" / "start dev" / "pre-flight" | `/prodmasterai pull latest` |
| `plugin-manager` | "what plugins are installed" / "plugin status" | `/prodmasterai plugins` |

---

### Build

| Skill | Trigger | Example |
|---|---|---|
| `orchestrate` | "build X" / "implement X" / "start work on X" | `/prodmasterai build user authentication` |
| `dev-loop` | "loop until passing" / "run until tests pass" | `/prodmasterai dev-loop exit_when=coverage>=80` |
| `parallel-explore` | "try multiple approaches" / "best of N" | `/prodmasterai explore --approaches 3 <goal>` |
| `research-resolve` | "loop is stuck" / "investigate failure" | `/prodmasterai research-resolve` |

---

### Automate

| Skill | Trigger | Example |
|---|---|---|
| `auto-pilot` | "auto X" / "run autonomously" / "work while I sleep" | `/prodmasterai auto build login feature` |
| `auto-pilot-revoke` | "stop auto-pilot" / "cancel autonomous" | `/auto-pilot-revoke` |
| `resume` | "what happened while I was away" / "show autonomous summary" | `/prodmasterai resume` |
| `checkpoint` | "pick up where" / "checkpoint discard" | `/prodmasterai checkpoint discard` |
| `task-queue` | "queue add X" / "queue list" / "queue run" | `/prodmasterai queue add build payments` |

---

### Measure

| Skill | Trigger | Example |
|---|---|---|
| `measure` | "cycle done -- N tasks, QA X%, Y reviews, Z hours" | `/prodmasterai cycle done -- 5 tasks, QA 90%, 2 reviews, 3 hours` |
| `report` | "report" / "dashboard" / "weekly summary" | `/prodmasterai report` |

---

### Decide

| Skill | Trigger | Example |
|---|---|---|
| `decide` | "should we A or B?" / "prioritise" / "which option" | `/prodmasterai should we use REST or GraphQL?` |
| `learn` | "remember this" / "that was wrong" / "log this" | `/prodmasterai that approach worked well -- log it` |

---

### Improve

| Skill | Trigger | Example |
|---|---|---|
| `evolve-self` | `/evolve` / "optimize the plugin" / "deep review" / "audit" | `/evolve` |
| `token-efficiency` | "I'm hitting limits" / "too many tokens" / "token audit" | `/prodmasterai token-efficiency` |
| `prodmasterai update` | "update" / "publish" / "contribute upstream" | `/prodmasterai update` |

---

**Tip:** just type `/prodmasterai` and describe what you want -- the plugin will route you automatically.
