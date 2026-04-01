---
name: codex
description: Cross-model adversarial review — runs Claude and a second AI model independently on the same code, compares results to catch blind spots. Three modes (review, challenge, consult). Session memory for continuity. Cost tracking per invocation.
version: 1.1.0
argument-hint: "[review | challenge | consult] [question]"
effort: max
model: claude-opus-4-6
triggers:
  - /prodmasterai codex
  - second opinion
  - cross-model review
  - ask codex
  - codex review
  - challenge this
  - adversarial review
  - get a second opinion
reads:
  - memory/project-context.md
  - memory/codex-sessions/
writes:
  - memory/codex-sessions/
  - memory/codex-log.md
  - memory/project-context.md
generated: false
generated_from: ""
---

# Codex

Cross-model adversarial review. Claude and a second AI model review the same code independently, then results are compared to surface blind spots neither model finds alone.

Use this for: high-stakes decisions, security-sensitive code, architecture choices, anything where a second opinion matters.

---

## Modes

| Mode | Trigger | What it does |
|---|---|---|
| **review** | `/prodmasterai codex review` | Independent reviews by 2 models, PASS/FAIL gate, merged findings |
| **challenge** | `/prodmasterai codex challenge` | Adversarial testing — second model tries to break Claude's plan |
| **consult** | `/prodmasterai codex <question>` or `ask codex <q>` | Q&A with second model, session continuity |

Default mode when no subcommand: `review` if a diff exists, `consult` otherwise.

---

## Phase 1 — Context Assembly

1. Read the current diff: `git diff main...HEAD` (or `git diff HEAD~1` for last commit).
2. Check for a plan file: `PLAN.md`, `docs/plan.md`, `memory/plans/`. If found: embed plan context into the review prompt — both models see the stated intent alongside the code.
3. Check `memory/codex-sessions/` for an existing session matching the current branch. If found: load session for continuity (consult mode).
4. Record `pre_review_sha: git rev-parse HEAD`.

---

## Phase 2 — Dual-Model Execution

### Model A: Claude (self-review)

Run Claude's own analysis on the diff:
- Apply the same checks as `/prodmasterai review` Pass 1 + Pass 2
- Produce findings list with file, line, severity, description

### Model B: Second model (independent)

Dispatch a subagent configured to simulate a different review perspective:
- Different focus: architectural concerns, edge cases Claude tends to miss, security assumptions
- Prompt: "You are reviewing this diff independently. Find issues the original author missed. Be adversarial. Every finding needs a line number."
- If an external model API is available (OpenAI, Gemini via env var): use it. Otherwise: use a Claude subagent with explicit instruction to take an adversarial stance.

Run both models **in parallel**. Wait for both to complete before comparing.

---

## Phase 3 — Comparison and Synthesis

After both models complete:

1. **Agreement**: findings present in BOTH models → high confidence, surface first
2. **Claude-only**: findings only Claude found → medium confidence, include with note
3. **Model B-only**: findings only Model B found → high value (blind spots), include with highlight
4. **Contradictions**: models disagree on severity or approach → flag as `contested`, present both views

Output the merged finding list sorted by: agreement (both) → Model B only → Claude only → contested.

---

## Phase 4 — Mode-Specific Output

### Review Mode

```
== Codex Review: <branch> ==
Model A (Claude):    <N findings>
Model B (secondary): <N findings>
Agreement:           <N shared findings>
Blind spots (B only): <N — high value>

PASS / FAIL
  Reason: <one line>

Findings (by confidence):
  [CC-001] Both models: <title> — <file>:<line> — <severity>
  [CC-002] Model B only: <title> — <file>:<line> — <severity> ⚠ blind spot
  [CC-003] Claude only: <title> — <file>:<line> — <severity>
  [CC-004] Contested: <title> — Model A says X, Model B says Y

Cost: ~<N> tokens | ~$<X.XX>
```

FAIL verdict if: any critical finding in agreement zone, OR any critical finding in Model B-only zone.

### Challenge Mode

Model B is given Claude's implementation plan and instructed to attack it:
- Find logical flaws in the approach
- Identify missing edge cases
- Propose alternative approaches that are strictly better
- Challenge every assumption

Output:
```
== Codex Challenge: <plan summary> ==
Challenges raised: <N>
  [CH-001] Logical flaw: <description> — severity: high
  [CH-002] Missing edge case: <description>
  [CH-003] Better approach: <description>

Verdict: <PLAN HOLDS | PLAN HAS WEAKNESSES | PLAN SHOULD BE REVISED>
```

### Consult Mode

Direct Q&A with the second model. Session memory preserved:

```
== Codex Consult ==
Session: <branch>-<date>
Q: <user question>

Model B response:
<response>

Cost: ~<N> tokens | ~$<X.XX>
Session saved to memory/codex-sessions/<branch>.md
```

---

## Session Memory

Save session to `memory/codex-sessions/<branch>-<YYYY-MM-DD>.md`:

```markdown
# Codex Session: <branch> — <date>
Mode: <review | challenge | consult>
Pre-review SHA: <sha>

## Exchange
Q: <question or "code review">
A: <model B response>

## Findings
<findings list>
```

On next invocation for the same branch: load prior session for context continuity.

---

## Cost Tracking

Parse token usage from model responses. Display at end of every invocation:

```
Cost: ~<N input tokens> + <N output tokens> = ~<N total> | ~$<X.XX>
```

Estimated cost rates (approximate, update if stale):
- Claude Sonnet: ~$3/M input, ~$15/M output
- Claude Haiku: ~$0.25/M input, ~$1.25/M output

Append to `memory/codex-log.md`:

```yaml
---
date: <YYYY-MM-DD>
mode: review | challenge | consult
branch: <branch>
agreement_findings: N
blind_spot_findings: N
verdict: PASS | FAIL | PLAN HOLDS | PLAN HAS WEAKNESSES
estimated_cost_usd: 0.00
session_id: <session_id>
---
```

---

## Integration with Auto-Pilot

When `autonomous_mode: true`:
- Mode: `review` on any diff > 200 lines, skip otherwise (cost optimization)
- FAIL verdict: log as decision, continue (does not block — auto-pilot uses judgment)
- Blind spot findings: append to autonomous-log as high-confidence decisions for review
- Challenge mode: never runs in autonomous mode (too disruptive to plan)

---

## Rules

- Both models run in parallel — never sequential (defeats the independence goal)
- Model B prompt must not include Model A's findings before Model B runs
- Session memory is per-branch — different branches never share sessions
- Contested findings are always surfaced — never silently dropped
- Cost is always displayed — no invisible spend
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
