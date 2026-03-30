# Task Queue
<!-- task-queue appends one YAML block per queued goal -->
<!-- auto-pilot advances queue on completion -->

---
id: tq-2026-03-27-0001
goal: Build a qa skill for prodmaster-ai — systematic QA pipeline inspired by gstack: 11-phase testing (authenticate, orient, explore, document, triage, fix-loop, final-qa, report), three depth tiers (quick/standard/exhaustive), health scoring across 8 categories, atomic fix commits per discovered bug, regression test generation, WTF-likelihood heuristics to auto-regulate
status: done
added_at: 2026-03-27T00:00:00Z
started_at: 2026-03-27T00:02:00Z
completed_at: 2026-03-27T00:15:00Z
session_id: 2026-03-27-0002
---

---
id: tq-2026-03-27-0002
goal: Build a review skill for prodmaster-ai — systematic code review inspired by gstack: two-pass approach (Pass 1 critical: SQL safety/race conditions/LLM trust boundaries/enum completeness; Pass 2 informational: side effects/magic numbers/dead code/test gaps/performance), test coverage ASCII diagrams, scope drift detection, adversarial scaling by diff size (small/medium/large with multi-pass), fix-first triage (auto-fix mechanicals, batch judgment calls for approval)
status: done
added_at: 2026-03-27T00:01:00Z
started_at: 2026-03-27T00:16:00Z
completed_at: 2026-03-27T00:30:00Z
session_id: 2026-03-27-0003
---

---
id: tq-2026-03-27-0003
goal: Build a deploy skill for prodmaster-ai — deployment pipeline inspired by gstack: auto-detect platform (Fly/Vercel/Render/Railway), dry-run validation first, pre-merge readiness gates (stale reviews/failing tests/CHANGELOG gaps), merge queue awareness, deploy wait with progress polling, canary verification (live site load/console errors/load time/screenshots), scope-aware skipping for docs-only changes, revert escape hatch on production failure
status: done
added_at: 2026-03-27T00:02:00Z
started_at: 2026-03-27T00:30:00Z
completed_at: 2026-03-27T00:45:00Z
session_id: 2026-03-27-0003
---

---
id: tq-2026-03-27-0004
goal: Build a cso skill for prodmaster-ai — security audit inspired by gstack: 14-phase infrastructure-first audit (architecture/attack surface/secrets archaeology/supply chain/CI-CD/infrastructure/webhooks/LLM security/skill supply chain/OWASP Top 10/STRIDE threat modeling/data classification/filtering/report), two modes (daily at 8/10 confidence vs comprehensive at 2/10 threshold), concrete exploit-path verification for every finding (no theoretical risks), supply chain depth beyond npm audit
status: done
added_at: 2026-03-27T00:03:00Z
started_at: 2026-03-27T00:45:00Z
completed_at: 2026-03-27T01:00:00Z
session_id: 2026-03-27-0003
---

---
id: tq-2026-03-27-0005
goal: Build a ship skill for prodmaster-ai — completeness-principle pre-merge pipeline inspired by gstack: tests → coverage audit → review → changelog generation → scope/plan completeness check → PR creation. Boil-the-lake approach: 100% test coverage, full error handling, comprehensive review as default. Adversarial review scaling by diff size. Greptile comment triage. Inline verification gate re-runs tests if code changed post-review.
status: done
added_at: 2026-03-27T01:00:00Z
started_at: 2026-03-27T01:01:00Z
completed_at: 2026-03-27T02:30:00Z
session_id: 2026-03-27-0004
---

---
id: tq-2026-03-27-0006
goal: Build a benchmark skill for prodmaster-ai — performance regression detection inspired by gstack: Core Web Vitals capture, bundle size tracking (JS/CSS separate), request count, largest resources (top 15), baseline storage in .prodmaster/benchmark-reports/, trend history, regression alerts (>50% timing regression, >25% bundle growth), four modes (capture baseline, measure current, diff vs baseline, trend report).
status: done
added_at: 2026-03-27T01:01:00Z
started_at: 2026-03-27T01:30:00Z
completed_at: 2026-03-27T02:30:00Z
session_id: 2026-03-27-0004
---

---
id: tq-2026-03-27-0007
goal: Build a codex skill for prodmaster-ai — cross-model adversarial review inspired by gstack: three modes (review with PASS/FAIL gate, challenge for adversarial testing, consult for Q&A). Claude subagent + second AI model run independently on same code, results compared. Session memory in memory/codex-sessions/. Plan file embedding for context. Cost tracking (tokens + estimated $). Useful when: high-stakes decisions, security-sensitive code, architecture choices.
status: done
added_at: 2026-03-27T01:02:00Z
started_at: 2026-03-27T01:30:00Z
completed_at: 2026-03-27T02:30:00Z
session_id: 2026-03-27-0004
---

---
id: tq-2026-03-27-0008
goal: Build a document-release skill for prodmaster-ai — post-ship documentation sync inspired by gstack: analyzes diff, auto-updates README/ARCHITECTURE/CONTRIBUTING/CLAUDE.md, polishes CHANGELOG voice (never regenerates — polish only), cleans TODOS, optional VERSION bump. Conservative approach: auto-execute safe updates, use AskUserQuestion for risky changes. Cross-doc consistency checks. Never regenerates CHANGELOG entries, only polishes existing ones.
status: done
added_at: 2026-03-27T01:03:00Z
started_at: 2026-03-27T02:00:00Z
completed_at: 2026-03-27T02:30:00Z
session_id: 2026-03-27-0004
---

---
id: tq-2026-03-27-0009
goal: Build a qa-only skill for prodmaster-ai — lightweight report-only QA variant inspired by gstack: systematic page/feature testing with NO fix-loop, diff-aware scope detection (auto-detects affected pages from git diff), baseline.json regression tracking in .prodmaster/qa-baselines/, screenshot evidence required for every finding, health score across 8 categories, structured issue docs. Complement to the full qa skill — use when you want findings only, not fixes.
status: done
added_at: 2026-03-27T01:04:00Z
started_at: 2026-03-27T02:00:00Z
completed_at: 2026-03-27T02:30:00Z
session_id: 2026-03-27-0004
---

---
id: tq-2026-03-27-0010
goal: Build a learn skill for prodmaster-ai — autonomous topic research and SKILL.md generation inspired by claude-self-learning: /prodmasterai learn <topic> triggers four-stage workflow (research → review → generate → store). Multi-source verification. Generates complete SKILL.md with proper frontmatter, triggers, process steps. Stores in skills/<topic>/SKILL.md. Updates skill-pattern-manifest. Version tracking. Quick reference tables in output. Works for any tool, framework, or workflow the user wants to learn.
status: done
added_at: 2026-03-27T01:05:00Z
started_at: 2026-03-27T02:00:00Z
completed_at: 2026-03-27T02:30:00Z
session_id: 2026-03-27-0004
---
