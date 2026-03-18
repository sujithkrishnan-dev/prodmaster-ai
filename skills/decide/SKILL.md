---
name: decide
description: Use when user is at a decision fork — "should we do A or B?", "what should we prioritise?", "which approach?". Reads project state and metrics to rank options by ROI/risk and give one clear recommendation.
version: 1.0.0
triggers:
  - User asks "should we", "which option", "prioritise", "help me decide", "recommend"
  - User presents two or more options and asks what to do
reads:
  - memory/project-context.md
  - memory/skill-performance.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# Decide

Give data-backed recommendations at decision forks.

## Process

### 1. Read Context

- `memory/project-context.md` — active features, blockers, recent decisions
- `memory/skill-performance.md` — last 5 entries (skip `example: true`)

### 2. Get the Options

Ensure the user has stated all options clearly. You need: what each option achieves, constraints, dependencies.

### 3. Score Options

**ROI (1–5):** 5 = unblocks critical work or delivers clear user value. 1 = low value.
**Risk (1–5):** 1 = reversible, isolated. 5 = irreversible, high uncertainty.
**Priority = ROI / Risk** — higher is better.

Also factor in:
- Declining velocity trend → prefer lower-risk options
- Many open blockers → prefer options that unblock first
- Declining QA pass rate → prefer simpler options

### 4. Present Recommendation

```
## Decision: <short title>

**Recommendation: Option <X>**

| Option | ROI | Risk | Score |
|--------|-----|------|-------|
| A      |  4  |  2   | 2.0   |
| B      |  5  |  4   | 1.25  |

**Why Option X:** <2-3 sentences with data references>

**Trade-offs:**
- Pro: ...
- Con: ...

**Why not Option Y:** <1-2 sentences>
```

### 5. Log Decision

Append to `memory/project-context.md` `## Decisions Log`:

```yaml
---
date: YYYY-MM-DD
decision: <one sentence summary>
rationale: <reasoning>
options_considered: [A, B]
status: pending_outcome
---
```

Tell the user: *"Decision logged. When you see how it plays out, let me know and I'll update the status — this helps the system learn which decision patterns work."*

## Rules

- Give ONE clear recommendation — no hedging without a conclusion
- Use actual performance data when available; flag when there is none
- Log every decision, even simple ones
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
