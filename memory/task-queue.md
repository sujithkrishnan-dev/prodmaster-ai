# Task Queue
<!-- task-queue appends one YAML block per queued goal -->
<!-- auto-pilot advances queue on completion -->

---
id: tq-2026-03-27-0001
goal: Build a qa skill for prodmaster-ai — systematic QA pipeline inspired by gstack: 11-phase testing (authenticate, orient, explore, document, triage, fix-loop, final-qa, report), three depth tiers (quick/standard/exhaustive), health scoring across 8 categories, atomic fix commits per discovered bug, regression test generation, WTF-likelihood heuristics to auto-regulate
status: running
added_at: 2026-03-27T00:00:00Z
started_at: 2026-03-27T00:02:00Z
completed_at: null
session_id: null
---

---
id: tq-2026-03-27-0002
goal: Build a review skill for prodmaster-ai — systematic code review inspired by gstack: two-pass approach (Pass 1 critical: SQL safety/race conditions/LLM trust boundaries/enum completeness; Pass 2 informational: side effects/magic numbers/dead code/test gaps/performance), test coverage ASCII diagrams, scope drift detection, adversarial scaling by diff size (small/medium/large with multi-pass), fix-first triage (auto-fix mechanicals, batch judgment calls for approval)
status: pending
added_at: 2026-03-27T00:01:00Z
started_at: null
completed_at: null
session_id: null
---

---
id: tq-2026-03-27-0003
goal: Build a deploy skill for prodmaster-ai — deployment pipeline inspired by gstack: auto-detect platform (Fly/Vercel/Render/Railway), dry-run validation first, pre-merge readiness gates (stale reviews/failing tests/CHANGELOG gaps), merge queue awareness, deploy wait with progress polling, canary verification (live site load/console errors/load time/screenshots), scope-aware skipping for docs-only changes, revert escape hatch on production failure
status: pending
added_at: 2026-03-27T00:02:00Z
started_at: null
completed_at: null
session_id: null
---

---
id: tq-2026-03-27-0004
goal: Build a cso skill for prodmaster-ai — security audit inspired by gstack: 14-phase infrastructure-first audit (architecture/attack surface/secrets archaeology/supply chain/CI-CD/infrastructure/webhooks/LLM security/skill supply chain/OWASP Top 10/STRIDE threat modeling/data classification/filtering/report), two modes (daily at 8/10 confidence vs comprehensive at 2/10 threshold), concrete exploit-path verification for every finding (no theoretical risks), supply chain depth beyond npm audit
status: pending
added_at: 2026-03-27T00:03:00Z
started_at: null
completed_at: null
session_id: null
---
