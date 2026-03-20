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
| `skills/prodmasterai/SKILL.md` | Modified | +Step 0 (log invocation) + +Step 3E (auto-session fire) |
| `hooks/session-start.md` | Modified | +Section to detect unprocessed invocations and inject context |
| `skills/measure/SKILL.md` | Modified | +auto-session input path with inferred defaults |

---

## Data Flow

```
User runs /prodmasterai
  └─> Step 0: append {ts, route, processed:false} to usage-log.md

Session ends. New session starts.
  └─> session-start hook fires
        └─> reads usage-log.md: count processed:false entries
        └─> reads skill-performance.md: get last measure date
        └─> if unprocessed > 0 AND last measure not this session:
              inject "Auto-session queued: N invocations (route breakdown) since last measure on DATE"

User runs any /prodmasterai command
  └─> Step 3E: if "Auto-session queued" in session context:
        └─> silently fire measure (auto-session path)
        └─> mark all processed:false entries as processed:true in usage-log.md
        └─> continue to handle user's actual command
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
- Route is the classified destination (decide, orchestrate, measure, report, learn, evolve-self, smooth-dev, help, auto-pilot, checkpoint, token-efficiency, unknown)
- `processed: true` written by prodmasterai Step 3E after auto-measure fires

---

### `skills/prodmasterai/SKILL.md` changes

**Add Step 0** — prepended before Step 1 (intent parsing):

> **Step 0 — Log Invocation (silent)**
> Append one line to `memory/usage-log.md`:
> `- {ISO 8601 timestamp} | route: {classified route, or "unknown" if not yet classified} | processed: false`
> If the file does not exist, create it with the standard header first.
> Do not output anything to the user. Do not wait for this write before continuing.

**Add Step 3E** — new condition appended after D in the Step 3 evaluation block:

> **E. Auto-session queued**
> Session context contains `"Auto-session queued"`.
> → Silently fire `measure` (auto-session path) with inferred metrics (see measure spec below).
> → After measure completes: rewrite all `processed: false` lines in `memory/usage-log.md` to `processed: true`.
> → Then continue: evaluate B/C/D as normal and handle the user's actual command.
> → Do not tell the user that auto-measure fired. The cycle entry in skill-performance.md is the only record.

**Priority order update:** A > B > C > D > E (E is lowest — only fires if nothing else is active, and only once per session boundary).

Wait — E should fire at the START of a new session, before B/C/D, so that metrics are captured before new work begins. Revised priority: **A > E > B > C > D**.

Rationale: Evolution (A) must always run first. Auto-session close (E) should capture the previous session before starting new work. B/C/D then act on the freshly updated state.

---

### `hooks/session-start.md` changes

Add this section after the existing active-features/patterns/gaps injection:

```
## Auto-Session Detection

After injecting active features, patterns, and gaps:

1. Read `memory/usage-log.md`. Count lines where `processed: false`. Call this N.
2. Read `memory/skill-performance.md`. Get the date of the last entry. Call this LAST_MEASURE_DATE.
3. If N > 0 AND LAST_MEASURE_DATE is not today:
   - Count route breakdown: how many lines per route value (decide, orchestrate, etc.)
   - Inject into context:
     "Auto-session queued: {N} invocations ({route: count, route: count, ...}) since last measure on {LAST_MEASURE_DATE}."
4. If N = 0 OR LAST_MEASURE_DATE is today: inject nothing (silent).
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
> | `tasks_completed` | count of orchestrate + decide + learn route calls in usage-log (unprocessed) | These are the routes that represent real work |
> | `qa_pass_rate` | 1.0 | No failure signals detected; honest optimistic default |
> | `review_iterations` | 0 | No data |
> | `time_hours` | null | Not calculable without timestamps |
> | `feature` | Last active feature name from project-context.md, or "mixed-session" if none active |
> | `blockers_encountered` | 0 |
> | `inferred` | true | Flag this entry so report can note it |
>
> Proceed through Steps 2–5 as normal (velocity will be null due to null time_hours).
> Do not output a completion message to the user (this fires silently in the background).

---

## Inferred Metric Logic

`tasks_completed` counts only routes that represent work output:
- `orchestrate` → counts as 1 (a build action was initiated)
- `decide` → counts as 1 (a decision was made)
- `learn` (feedback path) → counts as 1 (knowledge was captured)
- All other routes (report, help, smooth-dev, token-efficiency, etc.) → count as 0

Minimum `tasks_completed` = 1 (even if all routes are non-work, at least one session happened).

---

## Tests Required

1. `memory/usage-log.md` exists after first prodmasterai invocation
2. Each invocation appends exactly one line with correct format
3. session-start injects "Auto-session queued" when unprocessed entries exist and last measure ≠ today
4. session-start injects nothing when last measure = today
5. prodmasterai Step 3E fires measure silently and marks entries as processed
6. measure auto-session path does not prompt the user
7. measure auto-session entries have `inferred: true` in skill-performance.md
8. `tasks_completed` minimum is 1 for any non-empty session

---

## Non-Goals

- Precise time tracking (null is honest)
- Per-invocation QA scoring (not feasible without test results)
- Retroactive backfill of past sessions (start fresh from now)
- Changing the "cycle done" explicit path (it still works and takes precedence)
