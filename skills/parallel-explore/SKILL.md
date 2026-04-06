---
name: parallel-explore
description: Run multiple implementation approaches in parallel git worktrees, evaluate by test pass rate (quality as tiebreaker), apply the best-performing solution automatically.
version: 1.0.1
triggers:
  - /prodmasterai explore
  - try multiple approaches
  - parallel worktrees
  - compare approaches
  - run N approaches
  - best of N
reads:
  - memory/project-context.md
  - memory/patterns.md
  - memory/parallel-explore-log.md
writes:
  - memory/parallel-explore-log.md
  - memory/patterns.md
generated: false
generated_from: ""
---

# Parallel Explore

Try multiple implementation approaches simultaneously in isolated git worktrees. The approach with the best test pass rate wins. Quality score breaks ties. The winner's changes are applied to the current branch; all worktrees are cleaned up.

---

## Hard Limits

- Maximum 4 approaches (hard limit — beyond this, worktree overhead exceeds benefit)
- Never push explore branches to remote
- Never modify the current branch until a winner is confirmed
- If only N=1 approach specified: run as normal auto-pilot without worktree overhead
- Always clean up all worktrees on completion, success, or failure

---

## Step 1 — Setup

Parse goal and approach count from the trigger. Default: 2 approaches. Accept `--approaches N` flag (max 4).

**If N > 4:** stop immediately and output: *"Maximum 4 approaches supported -- worktree overhead beyond 4 exceeds benefit. Re-run with `--approaches 4` or fewer."*

Generate `session_id: pe-<YYYY-MM-DD-HHmm>`.

Create N worktrees in parallel:
```bash
git worktree add ../Plugin-explore-<session_id>-1 -b explore/<session_id>-1
git worktree add ../Plugin-explore-<session_id>-2 -b explore/<session_id>-2
# … up to N
```

Append session-open block to `memory/parallel-explore-log.md`:
```yaml
---
session_id: pe-<session_id>
goal: <goal>
approaches: N
status: running
started_at: <ISO 8601>
---
```

---

## Step 2 — Approach Strategy Assignment

For each approach (1 through N), assign a `strategy_seed`:
1. Check `memory/patterns.md` for entries with `context: parallel-explore` and `confidence: medium|high`. Use top N entries as seeds (most recent first).
2. If fewer patterns than approaches: fill remaining slots with:
   - Approach 1: "default — conventional implementation, follow existing patterns"
   - Approach 2: "performance — minimise steps and file changes"
   - Approach 3: "safety — maximise test coverage, defensive assertions"
   - Approach 4: "minimal — fewest files touched, smallest diff"

Log `strategy_seed` per approach.

---

## Step 3 — Parallel Execution

Dispatch one auto-pilot subagent per worktree simultaneously. Each subagent:
- Works exclusively in its worktree directory (`../Plugin-explore-<session_id>-<n>`)
- Receives the same goal + its `strategy_seed` as context
- Has `autonomous_mode: true` (no blocking prompts)
- Commits to `explore/<session_id>-<n>` branch only

Wait for all subagents to complete. Timeout: `autonomous_max_iterations × 2 minutes` per approach.

If an approach fails entirely (stuck/parked): mark it `status: failed`, assign `test_pass_rate: 0, quality_score: 0`. Continue evaluation with remaining approaches.

If ALL approaches fail: output failure summary, clean up all worktrees, stop — do not touch current branch.

---

## Step 4 — Evaluation

Run all evaluations in parallel.

### Primary: Test Pass Rate

For each approach:
```bash
cd ../Plugin-explore-<session_id>-<n>
python -m pytest tests/ -q --tb=no 2>/dev/null
```
Parse output: `N passed, M failed` → `test_pass_rate = N / (N + M)`.
If no tests found: `test_pass_rate = 0.5` (neutral).

### Tiebreaker: Quality Score

For each approach, get changed files:
```bash
git diff main...explore/<session_id>-<n> --name-only
```
For each changed `.md` skill file, check presence of:
- Frontmatter block (`---` … `---`) → 1 point
- Numbered steps → 1 point
- `## Rules` section → 1 point
- At least one trigger → 1 point

`quality_score = total_points / (4 × changed_skill_file_count)`. If no skill files changed: `quality_score = 0.5`.

### Ranking

Sort by `(test_pass_rate DESC, quality_score DESC)`. Tiebreak on fewer files changed. Winner = rank 1.

---

## Step 5 — Apply Winner

```bash
git diff main...explore/<session_id>-<winner_n> | git apply --index
git commit -m "feat: parallel-explore winner (session: <session_id>, approach: <winner_n>, tests: <test_pass_rate>)"
```

If `git apply` fails (merge conflict): fall back to cherry-picking the winning branch's commits onto current branch one by one.

---

## Step 6 — Cleanup

Remove all worktrees and branches (including the winner — its changes are already on current branch):
```bash
git worktree remove ../Plugin-explore-<session_id>-<n> --force
git branch -D explore/<session_id>-<n>
```

Run for each n = 1 through N.

---

## Step 7 — Log and Self-Optimise

Update session block in `memory/parallel-explore-log.md`:
```yaml
status: complete
completed_at: <ISO 8601>
winner: <n>
winner_strategy: <strategy_seed>
scores:
  - approach: 1
    test_pass_rate: <score>
    quality_score: <score>
    rank: <rank>
```

Append winning strategy to `memory/patterns.md`:
```yaml
---
context: parallel-explore
pattern: <winner_strategy_seed>
confidence: medium
added_at: <ISO 8601>
source: parallel-explore session <session_id>
---
```

Output:
```
== Parallel Explore Complete: <session_id> ==
Goal:    <goal>
Approaches tried: N

Results:
  Approach 1 [<strategy>]: tests <pct>%, quality <pct>% → rank <n>
  Approach 2 [<strategy>]: tests <pct>%, quality <pct>% → rank <n> ✓ WINNER

Winner applied to current branch.
Run `/prodmasterai resume` to review autonomous decisions made per approach.
```

---

## Rules

- Hard limit: 4 approaches maximum
- Never push `explore/*` branches to remote
- Clean up all worktrees regardless of outcome
- Never modify current branch until winner is confirmed (Step 5)
- Self-optimisation: always append winning strategy to patterns.md after successful session
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
