---
name: evolve-self
description: Use when total_tasks_completed reaches a multiple of evolve_every_n_tasks (check project-context.md frontmatter), or when user runs /evolve. Improves underperforming skills and generates new skills from gaps locally. Runs a convergence loop -- no fixed cap, reruns until all changed skills are clean. Upstream PR is a separate explicit act -- only when user says "update plugin" or "/prodmasterai update".
version: 1.8.1
triggers:
  - User runs /evolve
  - measure notifies that evolution threshold was reached
  - User asks the plugin to improve itself or generate new skills
  - User says "update plugin" or "/prodmasterai update" (triggers Upstream Pipeline only)
reads:
  - memory/patterns.md
  - memory/mistakes.md
  - memory/feedback.md
  - memory/research-findings.md
  - memory/skill-performance.md
  - memory/skill-gaps.md
  - memory/project-context.md
  - memory/evolution-log.md
  - memory/connectors/skill-pattern-manifest.md
writes:
  - skills/*/SKILL.md
  - memory/research-findings.md
  - memory/evolution-log.md
  - memory/pending-upstream/
  - memory/connectors/skill-pattern-manifest.md
  - EVOLUTION-LOG.md (only on upstream merge)
generated: false
generated_from: ""
---

# Evolve Self

Two separate phases. Phase 1 (local) runs on every `/evolve`. Phase 2 (upstream) runs ONLY on explicit publish request.

---

## Phase 1 -- Local Evolution (runs on /evolve or threshold)

### Pre-flight

Read `memory/project-context.md` frontmatter. Record `total_tasks_completed`. Do NOT update `last_evolved_at_task` yet.

---

### Mode 0 -- Structural Review (explicit trigger only)

Runs ONLY when the user explicitly invokes `/evolve`, "deep review", "optimize the plugin", or similar -- i.e., NOT on automatic threshold triggers.

**Purpose:** Check all skill files for structural quality without requiring performance data. This enables improvement on fresh installs or early use before cycle data exists.

1. Collect all `skills/*/SKILL.md` files.
2. **Check all files in parallel** (same checks as the Convergence Refinement Loop):
   - Vague or ambiguous process steps
   - Missing edge-case rules (e.g., divide-by-zero, empty inputs, no-data states)
   - `reads:`/`writes:` frontmatter declarations that don't match body references
   - Contradicting rules within the same skill
   - Missing "Next:" completion hints
3. For each file with issues: apply targeted fixes, increment `version:` patch, append evolution-log entry with `trigger: structural-review`.
4. Files with no issues: mark clean.

If Mode 0 finds at least one changed skill: proceed to the **Convergence Refinement Loop** with those files as the initial set. Do NOT skip to No-Op.

If Mode 0 finds zero issues: skip Mode 0's log entry and continue to Mode 1.

---

### Mode 1 -- Improve Existing Skills

#### 1. Identify Underperforming Skills

Read `memory/skill-performance.md`. A skill is underperforming if the last 5 entries show a declining `qa_pass_rate` trend.

**No real data:** If `skill-performance.md` has no real-data entries (an entry qualifies as real data only if both `example: true` and `inferred: true` are absent), skip Mode 1 entirely (no data to analyse) and proceed to Mode 2.

**Exclude inferred entries:** When reading entries for underperformance detection or trend analysis, skip entries with `inferred: true`. These carry no real performance signal (all fields are default values) and would produce misleading quality assessments.

Map metrics to skills:
- High blockers -> check `orchestrate`
- Low qa_pass_rate -> check `learn` and `orchestrate`
- High review_iterations -> check skills in that workflow

#### 2. Research Better Approaches

Dispatch **all research subagents in parallel** -- one per underperforming skill simultaneously. Do not wait for one to complete before starting the next.

For each underperforming skill, dispatch a research subagent using `skills/evolve-self/research-subagent-prompt.md`. Fill in `{{skill_name}}`, `{{current_skill_content}}`, `{{performance_data}}`, `{{research_question}}`.

Wait for all subagents to complete, then proceed. Each subagent writes its finding to `memory/research-findings.md`.

#### 3. Apply Improvements

For research-findings entries with `confidence: high` or `medium` and `applied: false`:
1. Read the target SKILL.md
2. Apply the finding -- update relevant sections
3. Preserve frontmatter schema; increment `version:` (1.0.0 -> 1.1.0)
4. Set `applied: true` on the research-findings entry

Append to `memory/evolution-log.md`:
```yaml
---
date: YYYY-MM-DD
mode: improve
skill: <name>
trigger: declining qa_pass_rate + research: <source>
change_summary: <one sentence>
upstream_status: pending_publish
---
```

---

### Mode 2 -- Generate New Skills

#### 1. Find Candidates

Read `memory/skill-gaps.md`. Collect entries where `occurrences >= 3` AND `status: open`.

#### 2. Check Name Collision

Derive skill name: lowercase, hyphen-separated, 1-3 words.
Check if `skills/<name>/SKILL.md` already exists.

- **Exists:** Set gap `status: generated`, `generated_skill: <existing name>`. Log warning. Move to next.
- **Does not exist:** Proceed.

#### 3. Create Skill File

Create `skills/<name>/SKILL.md` with the standard frontmatter schema:

```markdown
---
name: <derived-name>
description: <one-line trigger description from gap pattern>
version: 1.0.0
triggers:
  - <plain language condition matching the gap pattern>
reads:
  - memory/project-context.md
writes:
  - memory/project-context.md
generated: true
generated_from: <gap entry id>
---

# <Title Case Name>

<What this skill does -- derived from the gap pattern>

## Process

<Draft specific steps. Be actionable. Include what to read, what to write, what to output.>

## Rules

- Always update memory files after acting
- Document actions so they can be measured
- Never contribute anything upstream -- upstream is exclusively evolve-self's responsibility
- <Add 2-3 more rules specific to this skill's purpose>
```

#### 4. Update Manifest

Append to `memory/connectors/skill-pattern-manifest.md`:
```markdown

### <skill-name>
keywords: [<5-10 keywords from the gap pattern>]
```

#### 5. Update Gap Entry

Set `status: generating`. After file written: `status: generated`, `generated_skill: <name>`.

Append to `memory/evolution-log.md`:
```yaml
---
date: YYYY-MM-DD
mode: generate
skill: <new skill name>
trigger: gap <id> reached 3+ occurrences
change_summary: New skill generated for: <gap pattern>
upstream_status: pending_publish
---
```

---

### No-Op Case

If none of Mode 0, Mode 1, or Mode 2 produced any output (no skills improved, no skills generated):
1. Append to `memory/evolution-log.md`:
```yaml
---
date: YYYY-MM-DD
mode: no-op
skill: ""
trigger: scheduled evolution check
change_summary: No improvements or new skills needed at this time
upstream_status: n/a
---
```
2. Tell user: *"Evolution check ran -- nothing needed at this time."*
3. **Skip the Convergence Refinement Loop entirely.** Jump directly to Post-Phase-1 Update.

---

### Convergence Refinement Loop

> Only runs when Mode 1 or Mode 2 produced at least one changed or created skill file. If No-Op case fired, skip this section.

Phase 1 runs a **convergence loop** -- no fixed iteration cap. It continues until a full pass over all changed skills produces zero further changes.

**Pass structure (repeat until clean):**

1. Collect the list of all SKILL.md files changed or created in this evolution run (starts with Mode 1 + Mode 2 output; grows if a refinement pass modifies additional files).
2. **Check all files in parallel** -- dispatch independent file checks simultaneously:
   a. Re-read the file.
   b. Check for: vague steps, missing edge-case rules, missing `reads:`/`writes:` declarations, contradicting rules, incomplete process steps.
   c. If issues found: apply targeted refinements, increment `version:` by a patch (e.g. 1.1.0 -> 1.1.1), append an evolution-log entry with `trigger: convergence-pass-N` (N = pass number).
   d. If no issues found: mark the file as clean for this pass.

   Wait for all parallel checks to complete before running the convergence check.
3. **Convergence check:** If every file in the list was clean in step 2d -- stop. Otherwise run another pass (back to step 1).

**Safeguard:** If the same file is modified in 5 consecutive passes without becoming clean, log a warning entry in `memory/evolution-log.md` (`trigger: stuck-after-5-passes`) and mark it clean to prevent infinite loops.

### Post-Phase-1 Update

After the convergence loop exits: update `last_evolved_at_task` in `memory/project-context.md` frontmatter to the recorded `total_tasks_completed`.

Tell user: *"Local evolution complete ([N] passes, converged). [X] skills improved, [Y] new skills generated. Run `/prodmasterai update` when you want to contribute these improvements upstream."*

**Stop here. Do NOT proceed to Phase 2 unless the user explicitly requests it.**

---

## Phase 2 -- Upstream Pipeline (ONLY on explicit publish request)

> **This phase runs ONLY when the user explicitly says one of:**
> - `/prodmasterai update`
> - "update plugin"
> - "publish improvements"
> - "contribute upstream"
>
> It NEVER runs automatically after Phase 1. If the current trigger is `/evolve` or a
> threshold notification, stop at the end of Phase 1.
>
> No other skill (orchestrate, measure, report, decide, learn, prodmasterai) ever
> runs this phase.

### What can go upstream

**Plugin files (always eligible):**
- `skills/*/SKILL.md` -- improved or newly generated skill files
- `skills/evolve-self/research-subagent-prompt.md`, `pr-template.md`
- `hooks/session-start.md`

**Memory / user data (eligible as supporting evidence, anonymised):**
- `memory/patterns.md`, `memory/mistakes.md`, `memory/skill-gaps.md` -- aggregates only
- `memory/feedback.md` -- user-gated separately (see Step 4 gate)
- `memory/skill-performance.md` -- metric trends, not raw project names
- `memory/research-findings.md` -- research conclusions only

**Anonymisation rule:** Strip all project names, feature names, and personal identifiers before
including memory data. Use aggregated signals only:
- OK: *"qa_pass_rate declined 3 cycles in a row"*
- Not OK: *"feature: user authentication login flow failed"*

### 1. Find Pending Changes

Collect all `memory/evolution-log.md` entries with `upstream_status: pending_publish`.
If none: tell user *"Nothing pending to publish upstream."* Stop.

### 2. Package Proposals

For each pending change create `memory/pending-upstream/YYYY-MM-DD-<skill-name>-<mode>.md`:

```yaml
---
proposal_id: YYYY-MM-DD-<skill-name>-<mode>
type: skill_improvement | new_skill
source: outcome | research | feedback
target_skill: skills/<name>/SKILL.md
occurrence_count: <1 for Mode 1, gap occurrences for Mode 2>
created: YYYY-MM-DD
status: pending
pr_url: ""
---
## What Changed
<description of skill file changes>

## Why
<trigger and evidence -- anonymised patterns/performance trends>

## Supporting Data (anonymised)
<aggregated memory signals, stripped of project/user identifiers>
```

### 4. Validate (no duplicates)

Check existing files in `memory/pending-upstream/` (any status), existing `skills/`, and `applied: true` entries in `memory/research-findings.md`. If duplicate: delete proposal, log, skip.

### 5. Create PRs

**Feedback-sourced proposals:** Always ask first:
*"Improvement from your feedback on [topic]: [change_summary]. Include anonymised supporting patterns and contribute back for all users?"*
- Yes -> create PR
- No -> `status: rejected`, keep local only

**Outcome/research-sourced proposals:** Create GitHub PR:
- Branch: `auto-evolved/YYYY-MM-DD-<skill-name>-<mode>` (suffix `-v2` if branch exists)
- Body: render `skills/evolve-self/pr-template.md`
- Label: `auto-evolved`
- Auth order: GitHub MCP -> `gh` CLI -> local-only fallback (log + notify)

After each PR: set `upstream_status: pr_created` on the evolution-log entry, update proposal `status: pr_created`.

### 6. Check Pending PRs

For all `status: pr_created` proposals:
- Merged -> `status: pr_merged`, set `upstream_status: merged`, append to root `EVOLUTION-LOG.md`:
  ```markdown
  ## YYYY-MM-DD -- <change_summary>
  PR: <url> | Type: <type> | Trigger: <trigger>
  ```
- Closed without merge -> `status: rejected`, `upstream_status: rejected`
- API unavailable -> leave as-is, retry next run
- Older than 30 days -> `status: rejected`, log "30-day timeout"

---

## Rules

- Phase 1 (local) runs on `/evolve` and threshold -- STOP before Phase 2
- Phase 2 (upstream) runs ONLY on explicit publish request -- never automatic
- **No other skill ever runs Phase 2** -- upstream is exclusively evolve-self's responsibility
- Memory data MAY go upstream as supporting evidence -- MUST be anonymised first
- Never delete existing skills upstream -- additive only
- feedback.md is READ-ONLY for this skill -- only the learn skill writes to it
- PRs are created whenever the user explicitly runs `/prodmasterai update` -- no time-based rate limit
- PRs never self-merge
- Generated skills must use the full standard frontmatter schema
