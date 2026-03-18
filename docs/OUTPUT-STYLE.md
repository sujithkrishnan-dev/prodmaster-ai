# ProdMaster AI — Output Style Guide

This guide defines how every skill presents information to the user. All skill outputs must follow these rules.

---

## Tone

- **Direct.** Say what happened, then say what to do next. No throat-clearing.
- **Warm.** Write like a knowledgeable colleague, not a system log.
- **Jargon-free.** No internal terms in user-facing output. "I saved your cycle data" not "appending entry to skill-performance.md".
- **Confident.** Give one clear answer or recommendation. Hedge only when uncertainty is genuinely relevant to the user's decision.

---

## Format Rules

### Use markdown tables for comparisons
When presenting two or more options side by side (scores, trade-offs, metrics), use a markdown table.

### Use bullet lists for actions and status items
When listing things to do, files changed, or status items — use `-` bullet lists, not numbered lists (unless order matters).

### Use code blocks only for actual commands
Commands the user should run go in fenced code blocks. Do not wrap prose, YAML data, or internal state in code blocks.

### Keep outputs scannable in under 10 seconds
A skill's completion output should fit on one screen. Aim for:
- 1 summary line (what happened)
- 1 short data block or table (key numbers/status)
- 1 "Next:" hint line

If more detail is genuinely needed, put it after the "Next:" line under a collapsible or secondary heading.

---

## Prohibited

These must never appear in user-facing output:

| Prohibited phrase | Use instead |
|---|---|
| "appending entry" | "saved" or "logged" |
| "invoking skill" | (just do it — don't narrate internal routing) |
| "dispatching subagent" | (just do it — don't narrate internal routing) |
| "handoff to learn" | (just do it — don't narrate internal routing) |
| Raw YAML frontmatter blocks | Never show `---` YAML blocks to the user |
| Internal file paths as the primary message | Mention paths as supporting detail only, not as the main output |
| "triggering" (internal trigger language) | Describe what is happening, not the internal mechanism |

---

## Required: "Next:" hint line

Every skill's completion message must end with a `Next:` line showing 1–2 logical next actions.

Format:
```
Next: /prodmasterai [action] | /prodmasterai [alternative action]
```

The actions should be concrete and directly relevant to what the user just did. Do not use generic fallbacks like "run /help".

---

## Error Messages

Error messages must be:

1. **Friendly** — no stack traces, no raw error strings shown as the primary message.
2. **Specific** — say what went wrong, not just "an error occurred".
3. **Actionable** — always include what the user should do next.

### Template

> [What went wrong] — [why it matters or what was expected]. [What to do next.]

### Examples

**Bad:**
> Error: field missing in YAML

**Good:**
> Missing `qa_pass_rate` for this cycle. Add it like this: `/prodmasterai cycle done — 5 tasks, QA 85%, 2 reviews, 3 hours`

---

**Bad:**
> Branch has diverged from origin.

**Good:**
> Your branch has diverged from origin — a fast-forward pull isn't possible. Run `git status` to see the conflict, resolve it, then restart the session.

---

## Skill Completion Message Template

Every skill should end with a message that follows this shape:

```
[What was done — 1 sentence, plain English]

[Key data — table or short bullet list, only if relevant]

Next: /prodmasterai [logical next action] | /prodmasterai [alternative]
```

---

## Skill-Specific Notes

### orchestrate
- Present the task breakdown as a bullet list, not a YAML block.
- State the number of tasks and estimated cycles up front.

### measure
- Show the calculated velocity and QA pass rate to the user — these are useful, not internal.
- Do not show the raw YAML entry that was written to `skill-performance.md`.

### learn
- Do not tell the user "appending entry to patterns.md". Say "Pattern saved" or "Mistake logged".
- When surfacing a skill gap threshold alert, be specific: name the pattern, its count, and what to run.

### report
- The fresh-state bootstrap message should be encouraging, not apologetic.
- Dashboard generation success should confirm the file path and how to open it.

### decide
- The recommendation section must always include the scoring table.
- The "Decision logged" confirmation should be one line, followed by the Next: hint.

### smooth-dev
- The session card is the primary output — keep it compact.
- Error paths (diverged branch, test failures) must give specific next steps, not just surface the problem.
