---
name: evolve-self
description: Use when total_tasks_completed reaches a multiple of evolve_every_n_tasks (check project-context.md frontmatter), or when user runs /evolve. Improves underperforming skills, generates new skills from gaps, and contributes improvements upstream.
version: 1.0.0
triggers:
  - User runs /evolve
  - measure notifies that evolution threshold was reached
  - User asks the plugin to improve itself or generate new skills
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
  - memory/pending-upstream/last-pr.txt
  - memory/connectors/skill-pattern-manifest.md
  - EVOLUTION-LOG.md
generated: false
generated_from: ""
---

# Evolve Self

Improve existing skills, generate new ones, and contribute changes upstream.

## Pre-flight

Read `memory/project-context.md` frontmatter. Record the current value of `total_tasks_completed` — you will use it later. Do NOT update `last_evolved_at_task` yet; that happens after Mode 1 and Mode 2 complete so that a mid-run failure does not silently skip the next evolution cycle.

---

## Mode 1 — Improve Existing Skills (runs first)

### 1. Identify Underperforming Skills

Read `memory/skill-performance.md`. A skill is underperforming if the last 5 entries (or all entries if fewer than 5 exist) show a declining `qa_pass_rate` trend — meaning each entry's `qa_pass_rate` is lower than the one before it across that window.

Map cycle metrics to skills:
- High blockers → check `orchestrate`
- Low qa_pass_rate → check `learn` (capturing patterns?) and `orchestrate` (task breakdown quality?)
- High review_iterations → check the skills involved in that workflow

### 2. Research Better Approaches

For each underperforming skill, dispatch a research subagent using `skills/evolve-self/research-subagent-prompt.md`. Fill in:
- `{{skill_name}}` — skill to investigate
- `{{current_skill_content}}` — current SKILL.md content
- `{{performance_data}}` — last 5 skill-performance.md entries
- `{{research_question}}` — specific question about how to improve

The research subagent writes its finding to `memory/research-findings.md`.

### 3. Apply Improvements

For research-findings entries with `confidence: high` or `medium` and `applied: false`:
1. Read the target SKILL.md
2. Apply the finding — update the relevant sections
3. Preserve frontmatter schema; increment `version:` (1.0.0 → 1.1.0)
4. Set `applied: true` on the research-findings entry

Append to `memory/evolution-log.md`:
```yaml
---
date: YYYY-MM-DD
mode: improve
skill: <name>
trigger: declining qa_pass_rate + research: <source>
change_summary: <one sentence>
---
```

---

## Mode 2 — Generate New Skills (runs second)

### 1. Find Candidates

Read `memory/skill-gaps.md`. Collect entries where `occurrences >= 3` AND `status: open`.

### 2. Check Name Collision

Derive skill name: lowercase, hyphen-separated, 1-3 words from the gap pattern.
Check if `skills/<name>/SKILL.md` already exists.

- **Exists:** Set gap `status: generated`, `generated_skill: <existing name>`. Log warning. Move to next candidate.
- **Does not exist:** Proceed.

### 3. Create Skill File

Create `skills/<name>/SKILL.md` using the standard frontmatter schema:

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

<What this skill does — derived from the gap pattern>

## Process

<Draft specific steps. Follow the same structure as other skills.
Be actionable. Include what to read, what to write, what to output.>

## Rules

- Always update memory files after acting
- Document actions so they can be measured
- <Add 2-3 more rules specific to this skill's purpose>
```

### 4. Update Manifest

Append to `memory/connectors/skill-pattern-manifest.md`:
```markdown

### <skill-name>
keywords: [<5-10 keywords from the gap pattern>]
```

### 5. Update Gap Entry

Set `status: generating`. After file is written: `status: generated`, `generated_skill: <name>`.

Append to `memory/evolution-log.md`:
```yaml
---
date: YYYY-MM-DD
mode: generate
skill: <new skill name>
trigger: gap <id> reached 3+ occurrences
change_summary: New skill generated for: <gap pattern>
---
```

---

## No-Op Case

If neither mode produced output:
```yaml
---
date: YYYY-MM-DD
mode: no-op
skill: ""
trigger: scheduled evolution check
change_summary: No improvements or new skills needed at this time
---
```

Tell user: *"Evolution check ran — nothing needed at this time."*

---

## Post-Mode Update

After Mode 1 and Mode 2 have both completed (whether or not they produced output): update `last_evolved_at_task` in `memory/project-context.md` frontmatter to the value of `total_tasks_completed` recorded during Pre-flight. This prevents the threshold from triggering again until another `evolve_every_n_tasks` tasks are completed.

---

## Upstream Pipeline (runs after any Mode 1 or Mode 2 output)

### 1. Rate Limit Check

Read `memory/pending-upstream/last-pr.txt`. Parse as ISO 8601 UTC. If fewer than 24 hours have elapsed: skip PR creation, queue proposal, tell user: *"Upstream proposal queued — rate limit active until [timestamp + 24h]."* Queue means the proposal file sits in pending-upstream/ with `status: pending`.

### 2. Package Proposal

For each changed/generated skill create `memory/pending-upstream/YYYY-MM-DD-<skill-name>-<mode>.md`:

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
<description>

## Why
<trigger and evidence>

## Evidence
<relevant entries from memory files>
```

### 3. Validate (no duplicates)

Check for duplicates in:
- All files in `memory/pending-upstream/` (any status)
- All existing `skills/` files
- `applied: true` entries in `memory/research-findings.md`

If duplicate: delete proposal, log, skip.

### 4. Create PR or Gate

**Source = outcome or research:** Create GitHub PR:
- Branch: `auto-evolved/YYYY-MM-DD-<skill-name>-<mode>` (suffix `-v2` if branch exists)
- Body: render `skills/evolve-self/pr-template.md`
- Label: `auto-evolved`
- Auth order: GitHub MCP → `gh` CLI → local-only fallback (log + notify)

Update `status: pr_created`, `pr_url: <url>`.
Write current UTC timestamp to `memory/pending-upstream/last-pr.txt`.

**Source = feedback:**
Ask: *"I've prepared an improvement based on your feedback about [topic]: [change_summary]. Contribute this back for all users?"*
- Yes → create PR as above
- No → set `status: rejected`, keep local changes

### 5. Check Pending PRs

On every run, check all `status: pr_created` proposals:
- Query GitHub API once per proposal
- Merged → `status: pr_merged`, append to root `EVOLUTION-LOG.md`:
  ```markdown
  ## YYYY-MM-DD — <change_summary>
  PR: <url> | Type: <type> | Trigger: <trigger>
  ```
- Closed without merge → `status: rejected`
- API unavailable → leave as `pr_created`, retry next run
- Older than 30 days → `status: rejected`, log "30-day timeout"

---

## Rules

- Mode 1 always before Mode 2
- Never delete existing skills upstream — additive only
- feedback.md is READ-ONLY for this skill — only read, never write
- Max 1 upstream PR per 24 hours
- PRs never self-merge
- Generated skills must use the full standard frontmatter schema
