---
name: qa
description: 11-phase QA pipeline with health score across 8 categories. Scans the codebase, reports findings, and applies atomic fix commits per issue. Produces a scored health report.
version: 1.0.0
triggers:
  - User runs /prodmasterai qa
  - User says "run QA", "quality check", "check quality", "QA pass"
reads:
  - memory/project-context.md
  - memory/patterns.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# QA — Quality Assurance Pipeline

Run an 11-phase QA pipeline. Each finding gets an atomic fix commit. Produces a scored health report across 8 categories.

## Health Categories

| Category | Weight | What it measures |
|---|---|---|
| Functionality | 20% | All features work as specified, no regressions |
| Test coverage | 15% | Lines/branches covered, critical paths tested |
| Error handling | 15% | Graceful failure, user-facing error messages, no unhandled exceptions |
| Code quality | 15% | Readability, consistency, naming conventions, DRY |
| Security | 10% | OWASP basics, secrets, dependency CVEs (delegates to cso if installed) |
| Performance | 10% | No obvious N+1 queries, no blocking operations, reasonable complexity |
| Accessibility | 10% | Semantic HTML, ARIA labels, keyboard navigation (if UI exists) |
| UX | 5% | Consistent patterns, clear feedback, no dead ends |

## Process

### Phase Sequence

Run phases in parallel where findings don't depend on prior phases.

| # | Phase | Action |
|---|---|---|
| 1 | **Test suite** | Run full test suite, capture pass/fail/skip counts |
| 2 | **Coverage** | Run coverage tool, identify uncovered critical paths |
| 3 | **Lint** | Run project linter, collect violations |
| 4 | **Type check** | Run type checker (tsc, mypy, pyright) if applicable |
| 5 | **Dead code** | Find unused exports, unreachable branches, orphaned files |
| 6 | **Error handling** | Scan for bare except/catch, missing error boundaries, unhandled promise rejections |
| 7 | **Security** | Delegate to cso skill if available; otherwise run basic secret + injection scan |
| 8 | **Performance** | Check for N+1 patterns, synchronous blocking calls, oversized bundles |
| 9 | **Accessibility** | Check semantic HTML, missing alt/ARIA, focus management (skip if no UI) |
| 10 | **UX consistency** | Check for dead-end flows, inconsistent patterns, missing loading states |
| 11 | **Regression** | Compare against previous QA baseline if available |

### Finding Format

```
[CATEGORY] [SEVERITY] <file>:<line>
  Issue: <description>
  Fix: <specific fix>
```

### Atomic Fix Commits

For each fixable finding:
1. Apply the fix
2. Run the affected test(s)
3. If tests pass: commit with message `fix(qa): <category> — <one-line summary>`
4. If tests fail: revert and report as manual-fix-needed

### Health Score

```
QA Health Score: XX/100

  Functionality   ████████░░  80/100
  Test coverage   ██████░░░░  60/100
  Error handling  ████████░░  80/100
  ...

Findings: N total (X auto-fixed, Y manual)
Commits: N atomic fix commits applied
```

## Rules

- Every finding must have a specific fix recommendation
- Atomic commits: one commit per fix, never batch
- If cso skill is available, delegate security phase entirely
- If no test suite exists, skip phase 1-2 and note the gap
- Never lower the health score from a previous baseline without explanation
