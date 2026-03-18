---
name: learn
description: Use after each Superpowers cycle to capture patterns, mistakes, and skill gaps. Also use when user provides explicit feedback ("that was wrong", "that worked well", "remember this").
version: 1.2.2
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

- `qa_pass_rate >= 0.9` AND `review_iterations <= 2` -> write to `patterns.md` (success)
- `qa_pass_rate < 0.6` OR `review_iterations > 4` -> write to `mistakes.md` (failure)
- Middle range (QA 0.6-0.9 OR reviews 3-4, not hitting either threshold above) -> write a **marginal entry** to `mistakes.md` with `root_cause: "marginal cycle -- no clear failure but below success threshold"` and `fix_applied: "review for improvement opportunities"`. Do not discard mid-range cycles silently.

### Parallel Write Block

Run the pattern/mistake write AND the skill-gap detection in **parallel** -- they read/write different files:

**Thread A -- Pattern or Mistake write (parallel):**

Write the pattern or mistake entry to the appropriate file (internal format -- do not show raw YAML to the user).

Root cause analysis for mistakes:
- High `review_iterations` -> usually unclear spec or over-built solution
- Low `qa_pass_rate` -> usually insufficient upfront test coverage or wrong integration assumptions

**Completion message to user** (success path):
> Pattern saved -- "<specific description of what worked>" added to your playbook.
>
> Next: `/prodmasterai report` to see trends | `/prodmasterai build [feature]` to start the next cycle

**Completion message to user** (failure path):
> Mistake logged -- <specific description>. Root cause: <why it went wrong>.
>
> Next: `/prodmasterai build [fix]` to address this | `/prodmasterai report` to review recent mistakes

**Thread B -- Detect Skill Gaps (parallel):**

Read `memory/connectors/skill-pattern-manifest.md`. Compare `unhandled_patterns` against all keyword lists using substring matching.

For each unhandled pattern:
1. Search `skill-gaps.md` for existing entry with matching pattern text
2. **Found:** increment `occurrences` by 1, update `last_seen` date
3. **Not found:** append new entry (internal format -- do not show raw YAML to the user)

**Slug derivation for gap IDs:** Take the first 3 significant words of the pattern text, lowercase, hyphenated (strip stop words: a, an, the, to, for, in, of, with). Truncate total slug to 20 characters max. Example: pattern "user asked to export CSV data" -> slug `user-export-csv`. The full ID: `gap-2026-03-18-user-export-csv`.

**Rule:** One increment per cycle per pattern -- even if the pattern appeared multiple times within that cycle.

**Gap threshold alert:** After incrementing, if a gap entry now has `occurrences >= 3` and `status: open`, surface this message:

> Heads up -- the pattern **"[pattern]"** has come up 3 times without a skill to handle it. Run `/evolve` to auto-generate one.

Do not invoke evolve-self automatically from learn; just surface the alert.

---

## Feedback Path (user input)

Write ONLY to `memory/feedback.md` (internal format -- do not show raw YAML to the user).

Tell the user: *"Got it -- feedback saved. Run `/evolve` whenever you want to consider contributing this back to the plugin."*

**Strict rule:** Feedback path writes ONLY to feedback.md. Never to patterns.md or mistakes.md.

---

## Rules

- Auto path: one write per cycle, never double-count
- feedback.md is WRITE-RESTRICTED -- only this skill (feedback path) may write to it
- Be specific in descriptions -- "used small focused tasks with clear acceptance criteria" not just "good process"
- Skill gap IDs must be unique: `gap-<date>-<slug>`
- **Never contribute anything upstream** -- upstream is exclusively evolve-self's responsibility
