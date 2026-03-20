# Auto-Session Tracking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatically record every plugin session's metrics without the user ever needing to type "cycle done".

**Architecture:** Every `/prodmasterai` invocation appends a line to `memory/usage-log.md`. At session start, if unprocessed entries exist, the session-start hook injects "Auto-session queued" context. On the next prodmasterai command that session, Step 3E silently fires `measure` with inferred defaults and marks all entries processed.

**Tech Stack:** Markdown skill files (Claude-interpreted), Python pytest for structural tests, no code compilation.

**Spec:** `docs/superpowers/specs/2026-03-20-auto-session-tracking-design.md`

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `memory/usage-log.md` | Create | Append-only invocation log |
| `tests/test_auto_session.py` | Create | All 14 structural tests for this feature |
| `skills/prodmasterai/SKILL.md` | Modify | Add Step 0, Step 3E, update reads frontmatter, update priority in Rules |
| `hooks/session-start.md` | Modify | Add Auto-Session Detection section |
| `skills/measure/SKILL.md` | Modify | Add Auto-Session Path, update Rules exception |
| `skills/report/SKILL.md` | Modify | Add inferred:true skip rule + Fresh-State Bootstrap guard update |
| `skills/evolve-self/SKILL.md` | Modify | Add inferred:true skip rule + Mode 1 skip guard update |
| `tests/test_memory.py` | Modify | Add `usage-log.md` to REQUIRED_FILES list |

---

## Task 1: Create test file with all 14 failing tests

**Files:**
- Create: `tests/test_auto_session.py`

Tests are content checks on markdown files — the standard pattern in this repo. All tests will fail until the corresponding changes are made in Tasks 2-7.

- [ ] **Step 1: Create the test file**

```python
# tests/test_auto_session.py
import os
import pytest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read(rel):
    return open(os.path.join(PLUGIN_ROOT, rel)).read()

def exists(rel):
    return os.path.exists(os.path.join(PLUGIN_ROOT, rel))

# ── Spec test 1 ──────────────────────────────────────────────────────────────
def test_usage_log_exists():
    """memory/usage-log.md seed file is created."""
    assert exists("memory/usage-log.md"), "memory/usage-log.md must exist"

# ── Spec test 2 ──────────────────────────────────────────────────────────────
def test_prodmasterai_step0_describes_append_format():
    """Step 0 in prodmasterai describes the ISO 8601 + processed:false format."""
    content = read("skills/prodmasterai/SKILL.md")
    assert "Step 0" in content
    assert "ISO 8601" in content
    assert "processed: false" in content

# ── Spec test 3 ──────────────────────────────────────────────────────────────
def test_session_start_injects_when_unprocessed():
    """session-start injects 'Auto-session queued' when processed:false entries exist."""
    content = read("hooks/session-start.md")
    assert "Auto-session queued" in content
    assert "processed: false" in content

# ── Spec test 4 ──────────────────────────────────────────────────────────────
def test_session_start_silent_when_no_unprocessed():
    """session-start injects nothing when N=0."""
    content = read("hooks/session-start.md")
    assert "inject nothing" in content or "Else: inject nothing" in content

# ── Spec test 5 ──────────────────────────────────────────────────────────────
def test_session_start_handles_missing_usage_log():
    """session-start sets N=0 and skips injection when usage-log.md does not exist."""
    content = read("hooks/session-start.md")
    assert "does not exist" in content or "If file does not exist" in content
    # The N=0 path must lead to no injection — validated by presence of silent skip
    assert "inject nothing" in content or "skip to step" in content

# ── Spec test 6 ──────────────────────────────────────────────────────────────
def test_session_start_last_measure_date_fallback():
    """session-start uses 'never' as LAST_MEASURE_DATE when skill-performance has no real entries."""
    content = read("hooks/session-start.md")
    assert '"never"' in content or "= \"never\"" in content or "set LAST_MEASURE_DATE" in content

# ── Spec test 7 ──────────────────────────────────────────────────────────────
def test_prodmasterai_step3e_marks_processed_true():
    """Step 3E fires measure and marks all processed:false entries as processed:true."""
    content = read("skills/prodmasterai/SKILL.md")
    assert "Auto-session queued" in content
    assert "processed: true" in content   # write-back instruction must be present

# ── Spec test 8 ──────────────────────────────────────────────────────────────
def test_prodmasterai_step3e_has_precondition_guard():
    """Step 3E does not fire when all entries are already processed:true."""
    content = read("skills/prodmasterai/SKILL.md")
    # Precondition requires at least one processed:false line
    assert "processed: false" in content
    assert "Precondition" in content or "precondition" in content

# ── Spec test 9 ──────────────────────────────────────────────────────────────
def test_measure_auto_session_path():
    """measure has Auto-Session Path: no user prompts, skips learn, runs Step 5."""
    content = read("skills/measure/SKILL.md")
    assert "Auto-Session Path" in content
    assert "source: auto-session" in content
    assert "Skip" in content and "learn" in content   # Step 4 skip instruction
    assert "Step 5" in content                         # Step 5 still runs

# ── Spec test 10 ─────────────────────────────────────────────────────────────
def test_measure_auto_session_sets_inferred():
    """measure auto-session entries include inferred: true."""
    content = read("skills/measure/SKILL.md")
    assert "inferred" in content
    assert "inferred: true" in content or "inferred | true" in content

# ── Spec test 11 ─────────────────────────────────────────────────────────────
def test_measure_minimum_tasks_completed():
    """tasks_completed minimum is 1 for any session."""
    content = read("skills/measure/SKILL.md")
    assert "min 1" in content or "minimum 1" in content or "(min 1)" in content

# ── Spec test 12 ─────────────────────────────────────────────────────────────
def test_report_excludes_inferred_from_averages():
    """report excludes inferred:true entries from averages and shows separate count."""
    content = read("skills/report/SKILL.md")
    assert "inferred: true" in content
    assert "excluded from averages" in content
    assert "Auto-tracked sessions" in content

# ── Spec test 13 ─────────────────────────────────────────────────────────────
def test_session_start_uses_processed_flag_not_date():
    """session-start uses the processed flag as the canonical counter (no date filter)."""
    content = read("hooks/session-start.md")
    # The canonical comment must be present — this is the sole guard mechanism
    assert "canonical" in content or "no date filtering" in content or "processed flag" in content

# ── Spec test 14 ─────────────────────────────────────────────────────────────
def test_report_bootstrap_excludes_inferred():
    """report Fresh-State Bootstrap fires when only inferred:true entries exist."""
    content = read("skills/report/SKILL.md")
    # Bootstrap guard must reference inferred as non-real data — unique to the guard section
    assert "qualifies as real data" in content or "inferred: true` is absent" in content or \
           "real-data entries" in content
```

- [ ] **Step 2: Run tests — verify all fail**

```
python -m pytest tests/test_auto_session.py -v
```

Expected: 14 failures (files/content don't exist yet). If any pass accidentally, note which ones and verify they aren't false positives.

- [ ] **Step 3: Add usage-log.md to test_memory.py REQUIRED_FILES**

In `tests/test_memory.py`, add `"usage-log.md"` to the `REQUIRED_FILES` list:

```python
REQUIRED_FILES = [
    "patterns.md", "mistakes.md", "feedback.md", "research-findings.md",
    "skill-performance.md", "skill-gaps.md", "project-context.md",
    "evolution-log.md",
    "pending-upstream/.gitkeep",
    "pending-upstream/last-pr.txt",
    "connectors/README.md",
    "connectors/skill-pattern-manifest.md",
    "connectors/github.md",
    "connectors/slack.md",
    "connectors/linear.md",
    "blocker-research.md",
    "autonomous-log.md",
    "checkpoint.md",
    "token-efficiency-log.md",
    "usage-log.md",   # <-- add this line
]
```

- [ ] **Step 4: Commit**

```bash
git add tests/test_auto_session.py tests/test_memory.py
git commit -m "test: add 14 auto-session tracking tests (all red)"
```

---

## Task 2: Create `memory/usage-log.md`

**Files:**
- Create: `memory/usage-log.md`
- Test: `tests/test_auto_session.py::test_usage_log_exists`, `test_usage_log_has_header`
- Test: `tests/test_memory.py::test_memory_file_exists[usage-log.md]`

- [ ] **Step 1: Create the seed file**

```markdown
# Usage Log
<!-- prodmasterai appends one entry per invocation -->
<!-- session-start reads; prodmasterai marks processed:true after auto-measure fires -->
```

Exact file content — three lines, nothing else.

- [ ] **Step 2: Run tests — verify target tests pass**

```
python -m pytest tests/test_auto_session.py::test_usage_log_exists tests/test_auto_session.py::test_usage_log_has_header tests/test_memory.py::test_memory_file_exists[usage-log.md] -v
```

Expected: 3 PASS

- [ ] **Step 3: Commit**

```bash
git add memory/usage-log.md tests/test_memory.py
git commit -m "feat: add memory/usage-log.md seed file"
```

---

## Task 3: Update `skills/prodmasterai/SKILL.md`

**Files:**
- Modify: `skills/prodmasterai/SKILL.md`
- Tests: `test_prodmasterai_step0_describes_append_format`, `test_prodmasterai_step3e_marks_processed_true`, `test_prodmasterai_step3e_has_precondition_guard`, `test_prodmasterai_reads_usage_log`, `test_prodmasterai_priority_includes_e`

Four changes to make in one edit:

**Change 1 — Frontmatter `reads:` list.** Add `memory/usage-log.md` as the 4th entry in the reads list (after `memory/skill-gaps.md`).

**Change 2 — Step 0.** Insert this block immediately before the `## Step 1 -- Parse Intent` heading.

The exact text to insert (note: the inner header block uses indented format to avoid nested fences):

    ## Step 0 -- Log Invocation (synchronous, silent)

    Append one line to `memory/usage-log.md`:
    `- {ISO 8601 timestamp} | route: {classified route, or "unknown" if not yet classified} | processed: false`

    If the file does not exist, create it with this header first:

        # Usage Log
        <!-- prodmasterai appends one entry per invocation -->
        <!-- session-start reads; prodmasterai marks processed:true after auto-measure fires -->

    This write is synchronous — complete it before continuing to Step 1.
    Do not output anything to the user.

    ---

**Change 3 — Step 3E.** Insert this block between `### A. Evolution threshold reached` and `### B. Active feature in progress`:

```markdown
### E. Auto-session queued

Precondition: session context contains `"Auto-session queued"` AND `memory/usage-log.md` has at least one `processed: false` line.
If precondition is not met (already fired this session, or no unprocessed entries), skip E entirely and evaluate B.

→ Count `processed: false` entries. Compute inferred metrics:
  - `tasks_completed` = count of lines with `route: orchestrate`, `route: decide`, or `route: learn` (minimum 1)
  - `qa_pass_rate` = 1.0
  - `review_iterations` = 0
  - `time_hours` = null
  - `feature` = last active feature name from `project-context.md ## Active Features`, or "mixed-session" if none
  - `blockers_encountered` = 0
  - `inferred` = true

→ Silently fire `measure` (auto-session path — source: auto-session) with the above metrics.
→ After measure completes: rewrite ALL `processed: false` lines in `memory/usage-log.md` to `processed: true` (including any stale entries, regardless of age). `processed: true` means "will not be counted again", not "was included in a measure entry".
→ Do not tell the user that auto-measure fired. The cycle entry in `skill-performance.md` is the only record.
→ Continue: evaluate B/C/D on the now-updated state and handle the user's actual command.

```

**Change 4 — Rules section priority line.** Find the line:
```
If two conditions in Step 3 match, take the higher-priority one (A > B > C > D)
```
Change to:
```
If two conditions in Step 3 match, take the higher-priority one (A > E > B > C > D)
```

- [ ] **Step 1: Apply all four changes to `skills/prodmasterai/SKILL.md`**

- [ ] **Step 2: Run tests**

```
python -m pytest tests/test_auto_session.py::test_prodmasterai_step0_describes_append_format tests/test_auto_session.py::test_prodmasterai_step3e_marks_processed_true tests/test_auto_session.py::test_prodmasterai_step3e_has_precondition_guard tests/test_auto_session.py::test_prodmasterai_reads_usage_log tests/test_auto_session.py::test_prodmasterai_priority_includes_e -v
```

Expected: 5 PASS

- [ ] **Step 3: Commit**

```bash
git add skills/prodmasterai/SKILL.md
git commit -m "feat: add Step 0 invocation log and Step 3E auto-session to prodmasterai"
```

---

## Task 4: Update `hooks/session-start.md`

**Files:**
- Modify: `hooks/session-start.md`
- Tests: `test_session_start_injects_when_unprocessed`, `test_session_start_silent_when_no_unprocessed`, `test_session_start_handles_missing_usage_log`, `test_session_start_last_measure_date_fallback`, `test_session_start_uses_processed_flag_not_date`

**Note — intentional improvement over spec:** The spec (step 2 of session-start changes) says `LAST_MEASURE_DATE` is drawn from any non-example entry. The implementation below uses non-example AND non-inferred entries. This is intentional: an inferred entry's date is not a useful "last real measure" signal. This deviation is safe and correct.

Append this section to the end of `hooks/session-start.md` (after the existing content):

```markdown
---

## Auto-Session Detection

After injecting active features, patterns, and gaps:

1. Read `memory/usage-log.md`.
   - If file does not exist: set N = 0 and skip to step 3.
   - Count lines where `processed: false`. Call this N.
   - The `processed` flag is the canonical "already counted" marker — no date filtering is needed.
     Step 3E marks all entries as `processed: true` when it fires, so any `processed: false`
     entries are by definition from after the last auto-measure, regardless of date.

2. Read `memory/skill-performance.md`.
   - Find the most recent entry where `example: true` is absent (or false) AND `inferred: true` is absent.
   - Extract its `date` field as LAST_MEASURE_DATE (used only for the injection message, not for filtering).
   - If no such entry exists: set LAST_MEASURE_DATE = "never".

3. If N > 0:
   - Count route breakdown: how many of the N `processed: false` lines per route value
     (count only those N lines — not the full file).
   - Inject into context:
     "Auto-session queued: {N} invocations ({route: count, route: count, ...}) since last measure on {LAST_MEASURE_DATE}."
   Else: inject nothing (silent).
```

- [ ] **Step 1: Append the Auto-Session Detection section to `hooks/session-start.md`**

- [ ] **Step 2: Run tests**

```
python -m pytest tests/test_auto_session.py::test_session_start_injects_when_unprocessed tests/test_auto_session.py::test_session_start_silent_when_no_unprocessed tests/test_auto_session.py::test_session_start_handles_missing_usage_log tests/test_auto_session.py::test_session_start_last_measure_date_fallback tests/test_auto_session.py::test_session_start_uses_processed_flag_not_date -v
```

Expected: 5 PASS

- [ ] **Step 3: Commit**

```bash
git add hooks/session-start.md
git commit -m "feat: add auto-session detection to session-start hook"
```

---

## Task 5: Update `skills/measure/SKILL.md`

**Files:**
- Modify: `skills/measure/SKILL.md`
- Tests: `test_measure_auto_session_path`, `test_measure_auto_session_sets_inferred`, `test_measure_minimum_tasks_completed`

Two changes:

**Change 1 — Auto-Session Path section.** Insert this block immediately before the existing `## Input` section:

```markdown
## Auto-Session Path

Triggered when `source: auto-session` is passed by prodmasterai Step 3E.
Skip all fuzzy parsing. Skip all user prompts. Use the inferred defaults passed in directly (already computed by Step 3E):

| Field | Inferred value |
|---|---|
| `tasks_completed` | count of `orchestrate` + `decide` + `learn` route calls (min 1) |
| `qa_pass_rate` | 1.0 |
| `review_iterations` | 0 |
| `time_hours` | null |
| `feature` | last active feature, or "mixed-session" |
| `blockers_encountered` | 0 |
| `patterns_used` | [] |
| `unhandled_patterns` | [] |
| `inferred` | true |

**Step 4 (auto-session only):** Skip the `learn` handoff entirely. `patterns_used` and `unhandled_patterns` are both empty — passing them to `learn` would write meaningless entries.

**Step 5 still runs.** `tasks_completed` is at least 1, so the threshold counter must be incremented.

**Step sequencing:** Run Steps 2 and 3 in parallel (as in the normal path). After both complete, run Step 5. Do not run 2, 3, and 5 concurrently — Step 5 depends on the Step 3 write to `project-context.md` (total_tasks_completed must be updated before Step 5 can check the threshold).

Do not output a completion message to the user. Velocity will be null due to null `time_hours`.

---
```

**Change 2 — Rules section.** Find the line:
```
Always hand off to learn
```
Change to:
```
Always hand off to learn — except on the `source: auto-session` path (Step 4 skipped; see Auto-Session Path above)
```

- [ ] **Step 1: Apply both changes to `skills/measure/SKILL.md`**

- [ ] **Step 2: Run tests**

```
python -m pytest tests/test_auto_session.py::test_measure_auto_session_path tests/test_auto_session.py::test_measure_auto_session_sets_inferred tests/test_auto_session.py::test_measure_minimum_tasks_completed -v
```

Expected: 3 PASS

- [ ] **Step 3: Commit**

```bash
git add skills/measure/SKILL.md
git commit -m "feat: add auto-session input path to measure skill"
```

---

## Task 6: Update `skills/report/SKILL.md`

**Files:**
- Modify: `skills/report/SKILL.md`
- Tests: `test_report_excludes_inferred_entries`, `test_report_bootstrap_excludes_inferred`

Two changes:

**Change 1 — Computed Stats section.** Find the line:
```
Skip entries with `example: true` when processing results.
```
Change to:
```
Skip entries with `example: true` or `inferred: true` when processing results and computing averages. These entries do not reflect real measured outcomes.

In the dashboard output, show auto-tracked sessions as a separate count (do not mix into averages):
`Auto-tracked sessions: N (excluded from averages)`
```

**Change 2 — Fresh-State Bootstrap guard.** Find:
```
When `skill-performance.md` has no non-example entries:
```
Change to:
```
When `skill-performance.md` has no real-data entries (an entry qualifies as real data only if both `example: true` is absent AND `inferred: true` is absent):
```

**Change 3 — Rules section.** Find:
```
Skip `example: true` entries in all calculations
```
Change to:
```
Skip `example: true` and `inferred: true` entries in all calculations and averages
```

- [ ] **Step 1: Apply all three changes to `skills/report/SKILL.md`**

- [ ] **Step 2: Run tests**

```
python -m pytest tests/test_auto_session.py::test_report_excludes_inferred_from_averages tests/test_auto_session.py::test_report_bootstrap_excludes_inferred -v
```

Expected: 2 PASS

- [ ] **Step 3: Commit**

```bash
git add skills/report/SKILL.md
git commit -m "feat: exclude inferred entries from report averages and bootstrap guard"
```

---

## Task 7: Update `skills/evolve-self/SKILL.md`

**Files:**
- Modify: `skills/evolve-self/SKILL.md`
- Test: `test_evolve_self_excludes_inferred`

Two changes:

**Change 1 — Mode 1 "No real data" guard.** Find:
```
**No real data:** If `skill-performance.md` has no non-example entries, skip Mode 1 entirely (no data to analyse) and proceed to Mode 2.
```
Change to:
```
**No real data:** If `skill-performance.md` has no real-data entries (an entry qualifies as real data only if both `example: true` and `inferred: true` are absent), skip Mode 1 entirely (no data to analyse) and proceed to Mode 2.
```

**Change 2 — Performance data reading.** Immediately after the "No real data" guard, add:
```
**Exclude inferred entries:** When reading entries for underperformance detection or trend analysis, skip entries with `inferred: true`. These carry no real performance signal (all fields are default values) and would produce misleading quality assessments.
```

- [ ] **Step 1: Apply both changes to `skills/evolve-self/SKILL.md`**

- [ ] **Step 2: Run tests**

```
python -m pytest tests/test_auto_session.py::test_evolve_self_excludes_inferred -v
```

Expected: 1 PASS

- [ ] **Step 3: Commit**

```bash
git add skills/evolve-self/SKILL.md
git commit -m "feat: exclude inferred entries from evolve-self pattern analysis"
```

---

## Task 8: Full test suite — verify all 14 pass

- [ ] **Step 1: Run all auto-session tests**

```
python -m pytest tests/test_auto_session.py -v
```

Expected: 14 PASS, 0 FAIL

- [ ] **Step 2: Run full test suite — verify no regressions**

```
python -m pytest tests/ -v --tb=short
```

Expected: All previously passing tests still PASS.

- [ ] **Step 3: Final commit**

```bash
git add tests/test_auto_session.py tests/test_memory.py \
        memory/usage-log.md \
        skills/prodmasterai/SKILL.md \
        hooks/session-start.md \
        skills/measure/SKILL.md \
        skills/report/SKILL.md \
        skills/evolve-self/SKILL.md
git commit -m "feat: auto-session tracking — zero-friction usage measurement

Adds session-close auto-measure: every /prodmasterai invocation is logged
to memory/usage-log.md. At session start, unprocessed entries trigger a
silent measure call with inferred defaults (tasks, qa=1.0, no time).
report and evolve-self skip inferred entries from averages/analysis.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Checklist Summary

| Task | Spec tests covered | Plan test functions | Status |
|---|---|---|---|
| 1. Create test file | — (all written red) | all 14 | — |
| 2. `memory/usage-log.md` | Spec 1 + memory REQUIRED_FILES | `test_usage_log_exists` + memory test | — |
| 3. `skills/prodmasterai/SKILL.md` | Spec 2, 7, 8 + reads + priority | `test_prodmasterai_step0_describes_append_format`, `test_prodmasterai_step3e_marks_processed_true`, `test_prodmasterai_step3e_has_precondition_guard`, `test_prodmasterai_reads_usage_log`, `test_prodmasterai_priority_includes_e` | — |
| 4. `hooks/session-start.md` | Spec 3, 4, 5, 6, 13 | `test_session_start_injects_when_unprocessed`, `test_session_start_silent_when_no_unprocessed`, `test_session_start_handles_missing_usage_log`, `test_session_start_last_measure_date_fallback`, `test_session_start_uses_processed_flag_not_date` | — |
| 5. `skills/measure/SKILL.md` | Spec 9, 10, 11 | `test_measure_auto_session_path`, `test_measure_auto_session_sets_inferred`, `test_measure_minimum_tasks_completed` | — |
| 6. `skills/report/SKILL.md` | Spec 12, 14 | `test_report_excludes_inferred_from_averages`, `test_report_bootstrap_excludes_inferred` | — |
| 7. `skills/evolve-self/SKILL.md` | (Mode 1 guard + exclusion) | `test_evolve_self_excludes_inferred` | — |
| 8. Full suite green | All 14 + regressions | Full test suite | — |
