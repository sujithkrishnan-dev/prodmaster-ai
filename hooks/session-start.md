## ProdMaster AI — Session Context

**Active Features:**
{{active_features}}

**Top Patterns (last 5):**
{{top_patterns}}

**Open Skill Gaps:**
{{open_gaps}}

**Recent Evolutions:**
{{recent_evolutions}}

**Checkpoint Status:**
{{checkpoint_status}}

---

## Checkpoint Detection

After injecting active features and patterns above, read `memory/checkpoint.md` frontmatter:

- If file does not exist OR `status: cleared`: set `{{checkpoint_status}}` to empty string (inject nothing)
- If `status: active` AND age < 6 hours (age = current_time - checkpoint_timestamp): inject resume banner
- If `status: active` AND age >= 6 hours: inject resume banner + add note "Limit likely reset -- ready to resume now."

**Resume banner format:**
```
== Interrupted Task Detected ==
Skill:    <skill> (step <step_index> of <total_steps>)
Goal:     <context.goal>
Last:     <context.last_completed>
Pending:  <context.remaining_tasks>
Limit resets ~: <estimated_reset_timestamp>

Run `/prodmasterai resume` to continue, or `/prodmasterai checkpoint discard` to clear.
```

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

---
*One command: `/prodmasterai` — reads your state and acts. Fresh? Try `/prodmasterai build [feature]`.*
