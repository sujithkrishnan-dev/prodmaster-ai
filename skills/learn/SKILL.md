---
name: learn
description: Use after each Superpowers cycle to capture patterns, mistakes, and skill gaps. Also use when user provides explicit feedback ("that was wrong", "that worked well", "remember this").
version: 1.0.0
triggers:
  - measure hands off a cycle outcome object
  - User gives explicit feedback about a workflow or decision
  - User says "log this pattern", "note this mistake", "remember that"
reads:
  - memory/connectors/skill-pattern-manifest.md
writes:
  - memory/patterns.md
  - memory/mistakes.md
  - memory/skill-gaps.md
  - memory/feedback.md
generated: false
generated_from: ""
---

# Learn

Capture patterns, mistakes, skill gaps, and user feedback from every cycle.

## Two Paths

Choose based on what triggered this skill.

---

## Auto Path (cycle outcome)

### Input

```yaml
feature: <name>
qa_pass_rate: <0.0-1.0>
review_iterations: <n>
patterns_used: [keywords]
unhandled_patterns: [keywords]
```

### Classify

- `qa_pass_rate >= 0.9` AND `review_iterations <= 2` → write to `patterns.md`
- `qa_pass_rate < 0.6` OR `review_iterations > 4` → write to `mistakes.md`
- Neither condition → no write to patterns or mistakes

### Write Pattern (if success)

```yaml
---
date: YYYY-MM-DD
pattern: <specific description of what worked — not just "it worked">
context: <task/feature type>
qa_pass_rate: <value>
review_iterations: <value>
---
```

### Write Mistake (if failure)

Analyse root cause:
- High `review_iterations` → usually unclear spec or over-built solution
- Low `qa_pass_rate` → usually insufficient upfront test coverage or wrong integration assumptions

```yaml
---
date: YYYY-MM-DD
mistake: <specific actionable description>
root_cause: <why it went wrong>
fix_applied: <resolution or "unresolved">
qa_pass_rate: <value>
review_iterations: <value>
---
```

### Detect Skill Gaps

Read `memory/connectors/skill-pattern-manifest.md`. Compare `unhandled_patterns` against all keyword lists using substring matching.

For each unhandled pattern:
1. Search `skill-gaps.md` for existing entry with matching pattern text
2. **Found:** increment `occurrences` by 1, update `last_seen` date
3. **Not found:** append new entry:

```yaml
---
id: gap-YYYY-MM-DD-<slugified-pattern-text>
pattern: <description>
first_seen: YYYY-MM-DD
last_seen: YYYY-MM-DD
occurrences: 1
status: open
generated_skill: ""
---
```

**Rule:** One increment per cycle per pattern — even if the pattern appeared multiple times within that cycle.

---

## Feedback Path (user input)

Write ONLY to `memory/feedback.md`:

```yaml
---
date: YYYY-MM-DD
feedback: <exact words the user used>
context: <what was happening — feature, decision, stage>
contributed_upstream: false
---
```

Tell the user: *"Logged. Run /evolve when you want to consider contributing this back to the plugin."*

**Strict rule:** Feedback path writes ONLY to feedback.md. Never to patterns.md or mistakes.md.

---

## Rules

- Auto path: one write per cycle, never double-count
- feedback.md is WRITE-RESTRICTED — only this skill (feedback path) may write to it
- Be specific in descriptions — "used small focused tasks with clear acceptance criteria" not just "good process"
- Skill gap IDs must be unique: `gap-<date>-<slug>`
