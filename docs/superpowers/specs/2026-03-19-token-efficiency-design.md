# Token Efficiency Skill Design

> **Status:** Approved
> **Date:** 2026-03-19
> **Scope:** New `token-efficiency` skill (three modes: audit, enforce, rewrite) + `memory/token-efficiency-log.md`

---

## Goal

Reduce token consumption across all plugin operations to delay hitting the plan usage limit. Provides three modes: audit (scan + report waste), enforce (pre-action gate for other skills), and rewrite (trim verbose skill files).

---

## Architecture

### Components

| Component | Type | Role |
|---|---|---|
| `skills/token-efficiency/SKILL.md` | New skill | Three modes: audit, enforce, rewrite |
| `memory/token-efficiency-log.md` | New memory file | Append-only log of audits, enforcements, and rewrites |

### No hook changes required

Token efficiency is opt-in, not automatic. Other skills call `enforce` explicitly before expensive operations. This avoids adding latency to every tool call.

---

## Triggers

| Trigger | Mode |
|---|---|
| `/prodmasterai token-efficiency audit` | Scan all skills + memory for waste, print report |
| `/prodmasterai token-efficiency enforce <action>` | Check a proposed action against efficiency rules |
| `/prodmasterai token-efficiency rewrite <skill-path>` | Rewrite a skill file to be leaner |
| "token efficiency", "reduce tokens", "token audit", "I'm hitting limits" | Routes to audit mode by default |

---

## Mode 1: Audit

### What it scans

Reads all files in `skills/*/SKILL.md` and `hooks/session-start.md`. Checks against 5 waste patterns:

| Rule | Severity | Detection |
|---|---|---|
| Full file read > 100 lines where only frontmatter or partial content needed | HIGH | Reads instruction uses full path with no `limit:` parameter |
| Subagent prompt references session history or full file contents inline | HIGH | Prompt length signal in skill description > 500 words |
| Code quality review dispatched on tasks touching <= 2 lines | MED | Review step present with no size guard |
| Same memory file read in multiple sequential steps | MED | Multiple reads of same path in one skill body |
| Memory file injection in session-start with no empty-check guard | LOW | session-start.md injects files unconditionally |

### Output format

Prints to terminal:
```
[token-efficiency audit 2026-03-19] N issues found:
  HIGH  skills/orchestrate/SKILL.md:45 -- full file read (312 lines), only frontmatter needed
  MED   skills/evolve-self/SKILL.md -- subagent prompt exceeds 500 words
  MED   subagent-driven-development -- quality review has no size guard
  LOW   hooks/session-start.md -- injects memory files without empty-check
```

Appends summary block to `memory/token-efficiency-log.md`:
```yaml
---
type: audit
date: 2026-03-19
issues_found: 4
high: 1
medium: 2
low: 1
top_issue: "skills/orchestrate/SKILL.md full file read"
---
```

---

## Mode 2: Enforce

### Called by other skills

Any skill can include this line before an expensive operation:
```
Before reading <file>: call token-efficiency enforce -- check if full read is necessary
```

### Five enforcement rules

| Rule ID | Trigger condition | Response |
|---|---|---|
| E1 | File read with no `limit:` and file > 100 lines | SUGGEST_ALTERNATIVE: use `limit: 30` + `offset: 0` |
| E2 | Subagent prompt > 2000 tokens estimated | ALLOW_WITH_WARNING: trim session history from prompt |
| E3 | Review subagent on task touching <= 2 lines | SUGGEST_ALTERNATIVE: self-review only |
| E4 | Same file path read twice in same skill execution | SUGGEST_ALTERNATIVE: cache content from first read |
| E5 | Memory file is empty (0 bytes or header-only) | SUGGEST_ALTERNATIVE: skip injection |

### Return values

- `ALLOW` -- action is efficient, proceed
- `ALLOW_WITH_WARNING <message>` -- proceed but log the warning
- `SUGGEST_ALTERNATIVE <leaner approach>` -- do not proceed; try the suggested alternative instead

Enforce never blocks unconditionally -- it always provides an alternative. The calling skill decides whether to follow the suggestion.

Appends one line to `memory/token-efficiency-log.md` for each non-ALLOW result.

---

## Mode 3: Rewrite

### Input

A skill file path: `/prodmasterai token-efficiency rewrite skills/orchestrate/SKILL.md`

### What it rewrites (style + efficiency only -- never logic)

| Pattern | Rewrite |
|---|---|
| Frontmatter description > 2 lines | Trim to 2 lines, preserve meaning |
| Redundant step descriptions ("Read. Check. Verify.") | Collapse to single step ("Read and verify.") |
| Full-file read instructions with no limit | Add `limit: 30` guidance |
| Hedge phrases ("if applicable", "where possible", "as needed") | Remove |
| Repeated context re-statements across sections | Deduplicate (first occurrence kept) |

### Output flow

1. Read the skill file
2. Apply rewrite rules
3. Print unified diff to terminal
4. Ask: "Apply these changes? [Y/n]"
5. On confirm: write the file, commit with message `refactor: token-efficiency rewrite <skill-name>`
6. Append to `memory/token-efficiency-log.md`:
```yaml
---
type: rewrite
date: 2026-03-19
skill: orchestrate
lines_before: 145
lines_after: 112
reduction_pct: 23
---
```
7. On decline: discard, no file changes

### Safety rules

- Never remove functional behaviour (steps, rules, routing logic, hard limits)
- Never rewrite tests or memory files -- skills only
- Never batch-rewrite multiple skills in one invocation
- Always show diff before writing

---

## Memory File Schema

`memory/token-efficiency-log.md`:

```markdown
# Token Efficiency Log

Written by: token-efficiency. Read by: token-efficiency audit (for trend analysis).

<!-- Entries appended below -->
```

Each entry is a YAML block appended after the header comment. Fields vary by type (audit / enforce / rewrite) as shown in each mode above.

---

## New Files

| File | Purpose |
|---|---|
| `skills/token-efficiency/SKILL.md` | Three-mode token efficiency skill |
| `memory/token-efficiency-log.md` | Append-only log of all efficiency operations |

## Modified Files

| File | Change |
|---|---|
| `skills/prodmasterai/SKILL.md` | Add routing entry for token-efficiency triggers |
| `memory/connectors/skill-pattern-manifest.md` | Add token-efficiency keyword entry |
| `tests/test_skills.py` | Add "token-efficiency" to ALL_SKILLS |
| `tests/test_memory.py` | Add "token-efficiency-log.md" to REQUIRED_FILES |
| `tests/test_integration.py` | Add skill + memory file to required lists |
| `docs/README.md` | Add token-efficiency row to Skills table |
