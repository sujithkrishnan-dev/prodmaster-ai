---
name: decide
description: Use when user is at a decision fork -- "should we do A or B?", "what should we prioritise?", "which approach?". Reads project state and metrics to rank options by ROI/risk and give one clear recommendation.
version: 1.2.1
argument-hint: "[option A] vs [option B]"
effort: high
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

Give data-backed recommendations at decision forks. ultrathink before scoring — reason through tradeoffs deeply before committing to a recommendation.

## Process

### 1. Read Context (parallel)

Read both files simultaneously -- no shared state:
- `memory/project-context.md` -- active features, blockers, recent decisions
- `memory/skill-performance.md` -- last 5 entries (skip `example: true`)

### 2. Get the Options

Ensure the user has stated all options clearly. You need: what each option achieves, constraints, dependencies.

### 3. Score Options

**ROI (1-5):** 5 = unblocks critical work or delivers clear user value. 1 = low value.
**Risk (1-5):** 1 = reversible, isolated. 5 = irreversible, high uncertainty.
**Priority = ROI / Risk** -- higher is better.

Also factor in:
- Declining velocity trend -> prefer lower-risk options
- Many open blockers -> prefer options that unblock first
- Declining QA pass rate -> prefer simpler options

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

Append the decision entry to `memory/project-context.md` `## Decisions Log` (internal format -- do not show raw YAML to the user).

Tell the user: *"Decision logged. When you see how it plays out, say `/prodmasterai decision on [topic] was good/bad` -- I'll update the outcome and the system will learn from it."*

Next: `/prodmasterai build [chosen option]` to start the work | `/prodmasterai` to check what else needs attention

### 6. Close Prior Decisions (if outcome provided)

If the user provides outcome feedback on a previously logged decision (e.g. "that decision worked" / "that decision failed"):
1. **Find the matching entry** in `## Decisions Log` using keyword overlap:
   - Tokenise the user's topic phrase into significant words (strip stop words).
   - Score each `pending_outcome` decision entry by counting how many of its `decision:` words match the user's tokens.
   - Select the entry with the highest score. If tied, select the most recent.
   - If highest score is zero (no word overlap), ask the user: *"Which decision are you referring to? Here are the open ones: [list decision summaries]."*
2. Update `status:` from `pending_outcome` to `confirmed_good` or `confirmed_bad`.
3. Hand off to `learn` (feedback path) with the outcome as feedback.

## Rules

- Give ONE clear recommendation -- no hedging without a conclusion
- Use actual performance data when available; flag when there is none
- Log every decision, even simple ones
- **Never contribute anything upstream** -- upstream is exclusively evolve-self's responsibility
