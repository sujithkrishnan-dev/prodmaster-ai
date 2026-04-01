---
name: codex
description: Cross-model adversarial review. Sends code to a second model for independent analysis. PASS/FAIL gate with cost tracking. Catches blind spots from single-model review.
version: 1.0.0
triggers:
  - User runs /prodmasterai codex
  - User says "cross-model review", "adversarial review", "second opinion", "codex check"
reads:
  - memory/project-context.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# Codex — Cross-Model Adversarial Review

Get a second opinion by sending code to an independent model for review. Catches blind spots that single-model review misses.

## Process

### 1. Gather Review Scope

Determine what to review:
- `git diff main...HEAD` — all changes on the current branch
- If diff is too large (>500 lines): split into file-by-file reviews

### 2. Prepare Review Prompt

For each chunk, construct a review prompt:
```
Review this code change. You are an adversarial reviewer — your job is to find
issues the author missed, not to confirm the code works.

Focus on:
1. Logic errors and edge cases
2. Security vulnerabilities
3. Performance issues
4. API contract violations
5. Missing error handling

For each issue found, provide:
- Severity (CRITICAL / HIGH / MEDIUM / LOW)
- File and line
- What's wrong
- How to fix it

If the code is clean, say PASS with a brief rationale.
```

### 3. Model Selection

Use available models in preference order:
1. Claude API (if API key configured)
2. Second Claude Code session via Agent tool
3. Fallback: self-review with explicit adversarial framing

### 4. PASS/FAIL Gate

Aggregate findings across all chunks:
- **PASS:** Zero CRITICAL or HIGH findings
- **FAIL:** Any CRITICAL or HIGH finding

### 5. Cost Tracking

Track and report:
- Input tokens consumed
- Output tokens consumed
- Estimated cost (based on model pricing)
- Cumulative session cost

### 6. Report

```
Codex Review — <branch>
========================
Verdict: PASS / FAIL
Model:   <model used>
Cost:    ~$X.XX (<N>k input + <M>k output tokens)

Findings:
  [CRITICAL] None
  [HIGH]     None
  [MEDIUM]   2 issues
    1. src/api.js:42 — race condition in concurrent request handling
    2. src/db.js:18 — missing index on frequently queried column

  [LOW]      1 issue
    1. src/utils.js:5 — unnecessary variable allocation

Recommendation: SHIP / FIX BEFORE SHIPPING
```

## Rules

- Adversarial framing: always instruct the reviewer to find issues, never confirm
- PASS requires zero CRITICAL and zero HIGH — no exceptions
- Cost tracking is mandatory — always report token usage
- If no external model is available, fall back to self-review with explicit adversarial system prompt
- Never send secrets, credentials, or .env content to external models
