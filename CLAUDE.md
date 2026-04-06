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
| `/prodmasterai pull latest` | `smooth-dev` — git pull, repo health check, run tests |
| `/prodmasterai build X` | `orchestrate` — breaks feature into tracked tasks, parallel subtasks, auto-installs needed plugins |
| `/prodmasterai cycle done — …` | `measure` → `learn` auto-fires (parallel writes) |
| `/prodmasterai should we A or B?` | `decide` — scored recommendation with deep reasoning |
| `/prodmasterai report` | Prints full report directly in terminal (no files written) |
| `/prodmasterai stakeholder request X` | `stakeholder` — open approval gate, track sign-offs by role (PM/QA/CTO/EM) |
| `/prodmasterai approve <id> --role PM` | `stakeholder` — record a stakeholder sign-off |
| `/prodmasterai review` | `review` — two-pass code review, live diff context, auto-fix mechanicals |
| `/prodmasterai qa` | `qa` — 11-phase QA, health score across 8 categories, atomic fix commits |
| `/prodmasterai qa-only` | `qa-only` — findings-only QA, no fixes, screenshot evidence, baseline regression |
| `/prodmasterai ship` | `ship` — completeness-principle pre-merge: tests → coverage → review → changelog → PR |
| `/prodmasterai deploy` | `deploy` — platform auto-detect, dry-run, canary verification, revert escape hatch |
| `/prodmasterai cso` | `cso` — 14-phase security audit, exploit-path required for every finding. Writes findings to security gate |
| `/prodmasterai dependency-audit` | `dependency-audit` — CVE scan across npm/pip/bundler/go. Blocks session exit on CRITICAL CVEs |
| `/prodmasterai secret-scan` | `secret-scan` — 25+ credential patterns, staged-file scan, git history check, remediation commands |
| `/prodmasterai benchmark` | `benchmark` — Core Web Vitals, bundle size, regression alerts, 4 modes |
| `/prodmasterai codex` | `codex` — cross-model adversarial review, PASS/FAIL gate, cost tracking |
| `/prodmasterai document-release` | `document-release` — post-ship doc sync, CHANGELOG polish, consistency checks |
| `/prodmasterai learn <topic>` | `skill-forge` — research any topic and generate a production-ready SKILL.md |
| `/prodmasterai queue add X` | `task-queue` — adds goal to sequential execution queue |
| `/prodmasterai queue list` | `task-queue` — shows pending/running/done queue |
| `/prodmasterai queue run` | `task-queue` — runs all queued tasks sequentially, auto-advances |
| `/prodmasterai explore X` | `parallel-explore` — runs 2+ approaches in isolated worktrees, picks best by test pass rate |
| `/prodmasterai auto X` | `auto-pilot` — fully autonomous: brainstorm → plan → implement → test → PR |
| `/auto-pilot-revoke` | `auto-pilot-revoke` — stops running auto-pilot, commits progress, resets lock |
| `/prodmasterai resume` | `resume` — shows what auto-pilot did, per-decision review and rollback |
| `/prodmasterai plugins` | `plugin-manager` — shows installed/available plugins, auto-installs when needed |
| `/evolve` | `evolve-self` — convergence loop until all skills clean |
| `/prodmasterai update` | Push locally evolved improvements upstream via PR |
| `/prodmasterai` (no args) | Reads state, acts or prompts with exactly one question |

---

## Hooks (active automatically)

| Hook | Fires on | What it does |
|---|---|---|
| `session-start` | Session open | Injects active features, patterns, gaps, evolutions; detects unprocessed invocations for auto-session; surfaces installed plugins |
| `pre-tool-bash.py` | Every Bash call | Blocks: `rm -rf`, force push, `git reset --hard`, `git clean -f`, `DROP TABLE/DATABASE`, `chmod 777`, package installs from unverified sources, AWS key exports, PATH hijacking. |
| `post-tool-write.py` | Every Write/Edit | Passive scanner: detects secrets, SQL injection, unsafe deserialization, subprocess misuse. Advisory warnings; blocks on critical secret material. |
| `stop-quality-gate.py` | Claude stop | Blocks session exit when: tests failing during ship/deploy, critical secret leaks detected, critical CVEs in dependencies. |

---

## Connectors (optional)

Edit `memory/connectors/github.md`, `slack.md`, or `linear.md` — set `active: true` and fill in config.

Official plugins (47 available) are auto-detected from `~/.claude/plugins/cache/` and auto-installed when needed. See `memory/connectors/official-plugins-registry.md` for the full list.

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

**Auto-session tracking:** Every `/prodmasterai` invocation is logged to `memory/usage-log.md`. At the next session start, if unprocessed invocations exist, a measure cycle fires silently with inferred defaults — no "cycle done" command needed.
