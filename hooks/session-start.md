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
*One command: `/prodmasterai` — reads your state and acts. Fresh? Try `/prodmasterai build [feature]`.*
