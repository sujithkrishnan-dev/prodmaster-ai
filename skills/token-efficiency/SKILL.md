---
name: token-efficiency
description: Reduce token consumption across all plugin operations. Three modes: audit (scan + report waste hotspots), enforce (pre-action gate for expensive operations), rewrite (trim verbose skill files).
version: 1.0.1
triggers:
  - /prodmasterai token-efficiency
  - /prodmasterai token-efficiency audit
  - /prodmasterai token-efficiency enforce <action>
  - /prodmasterai token-efficiency rewrite <skill-path>
  - token efficiency
  - reduce tokens
  - token audit
  - I'm hitting limits
  - too many tokens
  - optimize tokens
reads:
  - skills/*/SKILL.md
  - hooks/session-start.md
  - memory/token-efficiency-log.md
writes:
  - memory/token-efficiency-log.md
generated: false
generated_from: ""
---

# Token Efficiency

Reduce token consumption to delay hitting the plan usage limit. Parse the sub-mode from the command argument: `audit` (default), `enforce`, or `rewrite`.

---

## Mode Dispatch

Read the full command:
- `/prodmasterai token-efficiency` or natural language trigger -> **audit mode**
- `/prodmasterai token-efficiency audit` -> **audit mode**
- `/prodmasterai token-efficiency enforce <action>` -> **enforce mode**
- `/prodmasterai token-efficiency rewrite <skill-path>` -> **rewrite mode**

---

## Mode 1: Audit

Scan all skill files and session-start hook for token waste. Print prioritised report.

### Scan targets

Read all files matching `skills/*/SKILL.md` and `hooks/session-start.md`.

### Five waste rules

| Rule | Severity | Detection |
|---|---|---|
| A1 | HIGH | Full file read (> 100 lines) with no `limit:` parameter in the instruction |
| A2 | HIGH | Subagent prompt body > 500 words in the skill description |
| A3 | MED | Review subagent dispatched with no size guard (no "skip if <= 2 lines" condition) |
| A4 | MED | Same memory file path appears in multiple sequential read steps in one skill body |
| A5 | LOW | session-start.md injects memory files without an empty-check guard |

### Output

Print to terminal:
```
[token-efficiency audit YYYY-MM-DD] N issues found:
  HIGH  skills/<name>/SKILL.md:<line> -- <description>
  MED   skills/<name>/SKILL.md -- <description>
  LOW   hooks/session-start.md -- <description>
```

Append audit block to `memory/token-efficiency-log.md`:
```yaml
---
type: audit
date: YYYY-MM-DD
issues_found: N
high: N
medium: N
low: N
top_issue: "<highest-severity issue description>"
---
```

Next: `/prodmasterai token-efficiency rewrite <skill-path>` to trim the top HIGH issue | `/prodmasterai` to return to normal operation

---

## Mode 2: Enforce

Check a proposed action against 5 efficiency rules before the calling skill proceeds.

### Invocation pattern

Other skills include this line before expensive operations:
```
Before reading <file>: invoke token-efficiency enforce with action="read <file>" -- follow the returned recommendation before proceeding.
```

### Five enforcement rules

| Rule | Trigger condition | Response |
|---|---|---|
| E1 | File read with no `limit:` and file > 100 lines | SUGGEST_ALTERNATIVE: use `limit: 30` + `offset: 0` |
| E2 | Subagent prompt > 2000 tokens estimated (1 token ~= 4 chars, flag at > 8000 chars) | ALLOW_WITH_WARNING: trim session history from prompt |
| E3 | Review subagent on task touching <= 2 lines | SUGGEST_ALTERNATIVE: self-review only |
| E4 | Same file path read twice in same skill execution | SUGGEST_ALTERNATIVE: cache content from first read |
| E5 | Memory file is empty (0 bytes or header-only) | SUGGEST_ALTERNATIVE: skip injection |

### Return values

- `ALLOW` -- action is efficient, proceed
- `ALLOW_WITH_WARNING <message>` -- proceed but note the inefficiency. Example: `ALLOW_WITH_WARNING: subagent prompt is 2100 tokens -- trim session history before next dispatch`
- `SUGGEST_ALTERNATIVE <approach>` -- try the leaner alternative instead. Example for E1: `SUGGEST_ALTERNATIVE: use Read tool with limit: 30 offset: 0 instead of full file read`. Example for E3: `SUGGEST_ALTERNATIVE: task touches 1 line -- skip review subagent, use implementer self-review only`

Calling skill decides whether to follow SUGGEST_ALTERNATIVE. Override is not logged.

Append one line to `memory/token-efficiency-log.md` for each non-ALLOW result:
```yaml
---
type: enforce
date: YYYY-MM-DD
rule: E1
action: "read skills/orchestrate/SKILL.md"
result: SUGGEST_ALTERNATIVE
message: "use Read tool with limit: 30 offset: 0"
---
```

---

## Mode 3: Rewrite

Trim a single skill file for token efficiency. Style and verbosity only -- never removes functional behaviour.

### Input

Skill file path from command argument. Example: `token-efficiency rewrite skills/orchestrate/SKILL.md`

### What gets rewritten (style + efficiency only)

| Pattern | Action |
|---|---|
| Frontmatter description > 2 lines | Keep first line verbatim + produce summary second line. Max 3 lines if meaning requires it. |
| Redundant step descriptions ("Read. Check. Verify.") | Collapse to single step ("Read and verify.") |
| Full-file read instructions with no limit | Add `limit: 30` guidance |
| Hedge phrases ("if applicable", "where possible", "as needed") | Remove |
| Repeated context re-statements across sections | Deduplicate (keep first occurrence) |

### Safety rules

- **Never remove functional behaviour.** Functional = steps, rules, routing logic, conditionals (if/else), error handlers, hard limits, tool call instructions. Non-functional = hedge phrases, verbose preambles, redundant re-statements, decorative comments.
- Never rewrite tests or memory files -- skills only
- Never batch-rewrite -- one skill per invocation
- Always show diff before writing -- never write without user confirmation

### Output flow

1. Read the skill file
2. Apply rewrite rules
3. Print unified diff to terminal
4. Print: "Apply these changes? [Y/n]"
5. On Y: write the file, then commit:
   ```bash
   git add <skill-path>
   git commit -m "refactor: token-efficiency rewrite <skill-name>"
   ```
6. Append rewrite block to `memory/token-efficiency-log.md`:
   ```yaml
   ---
   type: rewrite
   date: YYYY-MM-DD
   skill: <skill-name>
   lines_before: N
   lines_after: N
   reduction_pct: N
   ---
   ```
7. On N: discard all changes, no file writes

---

## Rules

- Default mode is audit -- if no sub-mode is specified, run audit
- Enforce is advisory -- calling skills may override SUGGEST_ALTERNATIVE
- Rewrite requires explicit user confirmation -- never writes silently
- **Never contribute anything upstream** -- upstream is exclusively evolve-self's responsibility
