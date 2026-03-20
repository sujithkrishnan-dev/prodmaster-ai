# Auto-Session Tracking — Design Spec

**Date:** 2026-03-20
**Status:** approved
**Problem:** Plugin usage is never recorded unless the user explicitly says "cycle done". In practice, users never do this, so `skill-performance.md` stays empty and the plugin has no data to learn from or evolve with.
**Solution:** Session-close auto-measure — every session's work is automatically logged at the start of the next session, with zero user friction.

---

## Scope

Fix the tracking gap without changing the user-facing experience. The user should never need to type "cycle done" again unless they want to provide precise metrics.

---

## Architecture

Four components change. Everything else is untouched.

| Component | Type | Change |
|---|---|---|
| `memory/usage-log.md` | New file | Append-only invocation log |
| `skills/prodmasterai/SKILL.md` | Modified | +Step 0 (log invocation) + Step 3E (auto-session fire) |
| `hooks/session-start.md` | Modified | +Section to detect unprocessed invocations and inject context |
| `skills/measure/SKILL.md` | Modified | +auto-session input path with inferred defaults |
| `skills/report/SKILL.md` | Modified | +skip rule for `inferred: true` entries in averages |
| `skills/evolve-self/SKILL.md` | Modified | +skip rule for `inferred: true` entries in pattern analysis |

---

## Data Flow

```
User runs /prodmasterai
  └─> Step 0 (synchronous, silent): append {ts, route, processed:false} to usage-log.md

Session ends. New session starts.
  └─> session-start hook fires
        └─> reads usage-log.md: count processed:false entries with ts > LAST_MEASURE_DATE
        └─> reads skill-performance.md: get timestamp of last non-example entry
        └─> if unprocessed > 0:
              inject "Auto-session queued: N invocations (route breakdown) since last measure on DATE"

User runs any /prodmasterai command
  └─> Step 3E: if "Auto-session queued" in session context AND processed:false count > 0:
        └─> silently fire measure (auto-session path)
        └─> mark all processed:false entries as processed:true in usage-log.md
        └─> continue to handle user's actual command (evaluate B/C/D on updated state)
```

---

## File Specifications

### `memory/usage-log.md` (new)

```markdown
# Usage Log
<!-- prodmasterai appends one entry per invocation -->
<!-- session-start reads; prodmasterai marks processed:true after auto-measure fires -->
- 2026-03-20T10:00 | route: decide | processed: false
- 2026-03-20T10:05 | route: orchestrate | processed: false
```

**Rules:**
- Append only — never delete or overwrite entries
- One line per invocation, ISO 8601 timestamp
- Valid route values: `decide`, `orchestrate`, `measure`, `report`, `learn`, `evolve-self`, `smooth-dev`, `help`, `auto-pilot`, `checkpoint`, `resume`, `token-efficiency`, `unknown`
- `processed: true` written by prodmasterai Step 3E after auto-measure fires; replace in-place on that line only

---

### `skills/prodmasterai/SKILL.md` changes

**Frontmatter update:** Add `memory/usage-log.md` to the `reads:` list.

**Add Step 0** — prepended before Step 1 (intent parsing):

> **Step 0 — Log Invocation (synchronous, silent)**
> Write one line to `memory/usage-log.md` (append):
> `- {ISO 8601 timestamp} | route: {classified route, or "unknown" if not yet classified} | processed: false`
> If the file does not exist, create it with the standard header first.
> This write is synchronous — complete it before continuing to Step 1.
> Do not output anything to the user.

**Add Step 3E** — inserted between A and B in the Step 3 evaluation block:

> **E. Auto-session queued**
> Precondition: session context contains `"Auto-session queued"` AND `memory/usage-log.md` has at least one `processed: false` line.
> If precondition is not met (already fired this session, or no unprocessed entries), skip E entirely.
> → Count `processed: false` entries. Compute inferred metrics (see measure spec below).
> → Silently fire `measure` (auto-session path).
> → After measure completes: rewrite ALL `processed: false` lines in `memory/usage-log.md` to `processed: true` — including entries older than LAST_MEASURE_DATE that were not counted in N. This clears stale entries so they are never double-counted in future sessions. Note: `processed: true` means "will not be counted again", not "was included in a measure entry".
> → Do not tell the user that auto-measure fired. The cycle entry in `skill-performance.md` is the only record.
> → Continue: evaluate B/C/D on the now-updated state and handle the user's actual command.

**Priority order:** `A > E > B > C > D`

Rationale: Evolution (A) always runs first. Auto-session close (E) captures the previous session before new work is evaluated. B/C/D then act on the freshly updated state.

---

### `hooks/session-start.md` changes

Add this section after the existing active-features/patterns/gaps injection:

```
## Auto-Session Detection

After injecting active features, patterns, and gaps:

1. Read `memory/usage-log.md`.
   - If file does not exist: set N = 0 and skip to step 4.
   - Count lines where `processed: false`. Call this ALL_UNPROCESSED.

2. Read `memory/skill-performance.md`.
   - Find the most recent entry where `example: true` is absent (or false).
   - Extract its `date` field as LAST_MEASURE_DATE.
   - If no such entry exists: set LAST_MEASURE_DATE = "1970-01-01" (epoch — always trigger).

3. Count lines where `processed: false` AND date-prefix of timestamp > LAST_MEASURE_DATE.
   Timestamp comparison rule: truncate the time component from the usage-log entry timestamp
   (take only the `YYYY-MM-DD` prefix) before comparing to `LAST_MEASURE_DATE`.
   Example: `2026-03-20T10:00` → compare `"2026-03-20" > "2026-03-18"` → true (include).
   Example: `2026-03-18T14:00` with LAST_MEASURE_DATE `"2026-03-18"` → `"2026-03-18" > "2026-03-18"` → false (exclude).
   This is a strict greater-than: entries on the exact same date as the last measure are excluded
   (the previous measure already covers that day).
   Call this N (entries from after the last measure date).

4. If N > 0:
   - Count route breakdown: how many of the N lines per route value.
   - Inject into context:
     "Auto-session queued: {N} invocations ({route: count, route: count, ...}) since last measure on {LAST_MEASURE_DATE}."
   Else: inject nothing (silent).
```

---

### `skills/measure/SKILL.md` changes

Add a new input path before the existing "Input" section:

> **Auto-Session Path**
> Triggered when `source: auto-session` is passed by prodmasterai Step 3E.
> Skip all fuzzy parsing. Skip all user prompts. Use these inferred defaults:
>
> | Field | Inferred value | Rationale |
> |---|---|---|
> | `tasks_completed` | count of `orchestrate` + `decide` + `learn` route calls in unprocessed usage-log entries (min 1) | Routes that represent real work output |
> | `qa_pass_rate` | 1.0 | No failure signals detected; honest optimistic default |
> | `review_iterations` | 0 | No data available |
> | `time_hours` | null | Not calculable from invocation log alone |
> | `feature` | Last active feature name from `project-context.md`, or `"mixed-session"` if none active |
> | `blockers_encountered` | 0 | No data available |
> | `patterns_used` | [] | Not derivable from routes |
> | `unhandled_patterns` | [] | Not derivable from routes |
> | `inferred` | true | Flags this entry for report and evolve-self consumers |
>
> **Step 4 modification (auto-session only):** Skip the `learn` handoff. `patterns_used` and `unhandled_patterns` are both empty — there is no pattern data to capture. Passing empty arrays to `learn` would write meaningless entries. Omit Step 4 entirely for auto-session cycles.
>
> Proceed through Steps 2, 3, and 5 as normal (velocity will be null due to null `time_hours`).
> Do not output a completion message to the user (fires silently).

---

### `skills/report/SKILL.md` changes

Add to the existing skip rule (currently `example: true`):

> When computing averages (QA pass rate, velocity, review iterations): exclude entries where `inferred: true`. These are auto-tracked sessions with default values that do not reflect real measured outcomes.
>
> In the dashboard output, show inferred entries as a separate count:
> `Auto-tracked sessions: N (excluded from averages)`
>
---

### `skills/evolve-self/SKILL.md` changes

When reading `skill-performance.md` for pattern analysis or underperformance detection: exclude entries where `inferred: true`. These entries carry no real performance signal (all defaults) and would skew quality assessments. Apply the same skip rule already used for `example: true` entries.

---

## Sample `skill-performance.md` Entry (auto-session)

```yaml
---
date: 2026-03-20
feature: mixed-session
tasks_completed: 2
velocity_tasks_per_week: null
qa_pass_rate: 1.0
review_iterations: 0
time_per_feature_hours: null
blockers: 0
blocker_age_days_avg: 0
blockers_encountered: 0
inferred: true
---
```

Note: `velocity_tasks_per_week: null` and `time_per_feature_hours: null` because `time_hours` was not available.

---

## Inferred Metric Logic

`tasks_completed` counts only routes that represent work output:
- `orchestrate` → counts as 1
- `decide` → counts as 1
- `learn` (feedback path) → counts as 1
- All other routes (`report`, `help`, `smooth-dev`, `token-efficiency`, `resume`, `checkpoint`, etc.) → count as 0

Minimum `tasks_completed` = 1 (even if all routes are non-work, at least one session happened).

---

## Tests Required

1. `memory/usage-log.md` is created on first prodmasterai invocation if it did not exist
2. Each invocation appends exactly one line with correct ISO 8601 format and `processed: false`
3. session-start injects "Auto-session queued" when unprocessed entries exist with timestamp after LAST_MEASURE_DATE
4. session-start injects nothing when no unprocessed entries exist
5. session-start injects nothing when `usage-log.md` does not exist (N=0 path)
6. session-start uses epoch as LAST_MEASURE_DATE when `skill-performance.md` has no real entries
7. prodmasterai Step 3E fires measure silently and marks all `processed: false` entries as `processed: true`
8. prodmasterai Step 3E does NOT fire again on the same session if all entries are already `processed: true`
9. measure auto-session path does not prompt the user and does not invoke `learn`
10. measure auto-session entries have `inferred: true` in `skill-performance.md`
11. `tasks_completed` minimum is 1 for any non-empty session
12. report excludes `inferred: true` entries from averages and shows them as separate count
13. Same-day multi-session: if auto-session fired at 9am and new invocations occur before a 2pm session, the 2pm session-start correctly detects the new unprocessed entries (timestamp comparison, not date comparison)

---

## Non-Goals

- Precise time tracking (null is honest)
- Per-invocation QA scoring (not feasible without test results)
- Retroactive backfill of past sessions (start fresh from now)
- Changing the "cycle done" explicit path (still works and takes precedence)
