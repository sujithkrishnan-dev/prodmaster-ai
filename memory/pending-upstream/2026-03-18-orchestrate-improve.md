---
proposal_id: 2026-03-18-orchestrate-improve
type: skill_improvement
source: feedback
target_skill: skills/orchestrate/SKILL.md
occurrence_count: 1
created: 2026-03-18
status: pr_merged
pr_url: "https://github.com/sujithkrishnan-dev/prodmaster-ai/pull/new/auto-evolved/2026-03-18-session-improvements"
---
## What Changed
- Step 1 reads (project-context, GitHub connector, Linear connector) dispatched in parallel.
- Step 3 (Invoke Superpowers): independent subtasks within a feature now dispatched in parallel; only serialized when output dependency exists.
- Rule updated: within-feature parallelism is default; cross-feature remains one at a time unless user requests otherwise.
- Version: 1.0.0 → 1.1.0

## Why
Sequential reads of independent files and sequential dispatch of independent subtasks wastes wall-clock time with no benefit. Parallelism here is safe — files are read-only in Step 1, and subtask independence is explicitly checked before dispatch.

## Supporting Data (anonymised)
- Pattern: context reads serialised despite having no dependency on each other
- Pattern: subtasks queued sequentially when they operate on independent code areas
- Fix confidence: high — read parallelism is always safe; subtask parallelism is gated on explicit independence check
