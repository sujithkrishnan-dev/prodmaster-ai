# Token Efficiency Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `token-efficiency` skill with three modes (audit, enforce, rewrite) that reduces token consumption across all plugin operations to delay hitting the plan usage limit.

**Architecture:** One new skill file and one new memory log file. No hooks or existing skill rewrites required. prodmasterai gets one new routing row. The skill parses audit/enforce/rewrite sub-modes internally from the command argument.

**Tech Stack:** Pure markdown + YAML frontmatter. Python pytest for tests.

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Modify | `tests/test_skills.py` | Add "token-efficiency" to ALL_SKILLS |
| Modify | `tests/test_memory.py` | Add "token-efficiency-log.md" to REQUIRED_FILES; extend manifest test |
| Modify | `tests/test_integration.py` | Add new files to required list |
| Create | `memory/token-efficiency-log.md` | Append-only log of audits, enforcements, rewrites |
| Create | `skills/token-efficiency/SKILL.md` | Three-mode skill: audit, enforce, rewrite |
| Modify | `skills/prodmasterai/SKILL.md` | Add token-efficiency routing row |
| Modify | `memory/connectors/skill-pattern-manifest.md` | Add token-efficiency keyword entry |
| Modify | `docs/README.md` | Add token-efficiency row to Skills table |

---

## Task 1: Add Failing Tests (RED)

**Files:**
- Modify: `tests/test_skills.py`
- Modify: `tests/test_memory.py`
- Modify: `tests/test_integration.py`

- [ ] **Step 1: Add "token-efficiency" to ALL_SKILLS in tests/test_skills.py**

Change the `ALL_SKILLS` list from:
```python
ALL_SKILLS = ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
              "dev-loop", "research-resolve", "auto-pilot", "resume", "checkpoint"]
```
to:
```python
ALL_SKILLS = ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
              "dev-loop", "research-resolve", "auto-pilot", "resume", "checkpoint",
              "token-efficiency"]
```

- [ ] **Step 2: Update tests/test_memory.py**

In `REQUIRED_FILES`, after `"checkpoint.md"`, add:
```python
    "token-efficiency-log.md",
```

In `test_skill_pattern_manifest_has_all_skills`, extend the skills list to include `"token-efficiency"`:
```python
    for skill in ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
                  "dev-loop", "research-resolve", "auto-pilot", "resume", "checkpoint",
                  "token-efficiency"]:
```

- [ ] **Step 3: Add new files to required list in tests/test_integration.py**

In `test_all_required_files_exist`, after the line `"memory/checkpoint.md",` add:
```python
        "skills/token-efficiency/SKILL.md",
        "memory/token-efficiency-log.md",
```

- [ ] **Step 4: Run full test suite to confirm red state**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/ -v 2>&1 | tail -20
```

Expected failures (and only these):
- `test_skill_exists[token-efficiency]`
- `test_skill_frontmatter[token-efficiency]`
- `test_memory_file_exists[token-efficiency-log.md]`
- `test_skill_pattern_manifest_has_all_skills`
- `test_all_required_files_exist`

All other tests must still pass.

- [ ] **Step 5: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add tests/test_skills.py tests/test_memory.py tests/test_integration.py
git commit -m "test: add failing tests for token-efficiency skill (RED)"
```

---

## Task 2: Create memory/token-efficiency-log.md

**Files:**
- Create: `memory/token-efficiency-log.md`

*Can run in parallel with Tasks 3 and 4 after Task 1.*

- [ ] **Step 1: Create the file**

Create `memory/token-efficiency-log.md` with this exact content:

```markdown
# Token Efficiency Log

Written by: token-efficiency. Read by: token-efficiency audit (for trend analysis).

<!-- Entries appended below.
Audit entry format:
---
type: audit
date: YYYY-MM-DD
issues_found: N
high: N
medium: N
low: N
top_issue: "description"
---

Enforce entry format:
---
type: enforce
date: YYYY-MM-DD
rule: E1 | E2 | E3 | E4 | E5
action: "description of action checked"
result: ALLOW_WITH_WARNING | SUGGEST_ALTERNATIVE
message: "returned message"
---

Rewrite entry format:
---
type: rewrite
date: YYYY-MM-DD
skill: skill-name
lines_before: N
lines_after: N
reduction_pct: N
---
-->
```

- [ ] **Step 2: Run the memory file test**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/test_memory.py::test_memory_file_exists[token-efficiency-log.md] -v
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add memory/token-efficiency-log.md
git commit -m "feat: add memory/token-efficiency-log.md seed file"
```

---

## Task 3: Create skills/token-efficiency/SKILL.md

**Files:**
- Create: `skills/token-efficiency/SKILL.md`

*Can run in parallel with Tasks 2 and 4 after Task 1.*

- [ ] **Step 1: Create the file**

Create `skills/token-efficiency/SKILL.md` with this exact content:

```markdown
---
name: token-efficiency
description: Reduce token consumption across all plugin operations. Three modes: audit (scan + report waste hotspots), enforce (pre-action gate for expensive operations), rewrite (trim verbose skill files).
version: 1.0.0
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
```

- [ ] **Step 2: Run skill tests**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/test_skills.py::test_skill_exists[token-efficiency] tests/test_skills.py::test_skill_frontmatter[token-efficiency] -v
```

Expected: both PASS

- [ ] **Step 3: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add skills/token-efficiency/SKILL.md
git commit -m "feat: add token-efficiency skill"
```

---

## Task 4: Update prodmasterai Routing, Manifest, and README

**Files:**
- Modify: `skills/prodmasterai/SKILL.md`
- Modify: `memory/connectors/skill-pattern-manifest.md`
- Modify: `docs/README.md`

*Can run in parallel with Tasks 2 and 3 after Task 1.*

- [ ] **Step 1: Add token-efficiency routing row to prodmasterai/SKILL.md**

In the routing table in `skills/prodmasterai/SKILL.md`, after the checkpoint routing rows added previously, add:
```
| "token efficiency", "reduce tokens", "token audit", "I'm hitting limits", "too many tokens", "optimize tokens", "token-efficiency" | `token-efficiency` |
```

- [ ] **Step 2: Append token-efficiency entry to skill-pattern-manifest.md**

At the end of `memory/connectors/skill-pattern-manifest.md` (after the `### checkpoint` block), append:

```markdown

### token-efficiency
keywords: [token efficiency, reduce tokens, token audit, I'm hitting limits, too many tokens, optimize tokens, token waste, token usage, plan limit, efficiency audit]
```

- [ ] **Step 3: Add token-efficiency row to docs/README.md**

In the Skills table, after the `| \`checkpoint\` | ...` row, add:

```markdown
| `token-efficiency` | "token efficiency" / "reduce tokens" / "I'm hitting limits" | Audit, enforce, and rewrite plugin operations to reduce token consumption and delay plan usage limit. |
```

- [ ] **Step 4: Run manifest test**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/test_memory.py::test_skill_pattern_manifest_has_all_skills -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd C:\Users\teame\Desktop\Plugin && git add skills/prodmasterai/SKILL.md memory/connectors/skill-pattern-manifest.md docs/README.md
git commit -m "feat: wire token-efficiency into routing, manifest, and README"
```

---

## Task 5: Full Test Suite — Verify Green

- [ ] **Step 1: Run the complete test suite**

```bash
cd C:\Users\teame\Desktop\Plugin && python -m pytest tests/ -v
```

Expected: all tests pass. Zero failures.

If any test fails, read the failure message carefully and fix only the specific file before re-running.

- [ ] **Step 2: Commit fixes (only if needed)**

Stage only the specific files that needed fixing:

```bash
cd C:\Users\teame\Desktop\Plugin && git add <specific-files> && git commit -m "fix: resolve test failures after token-efficiency implementation"
```

Skip this step if all tests passed on the first run.
