---
name: benchmark
description: Performance regression detection — captures Core Web Vitals, bundle size, request counts, and largest resources. Four modes (baseline, measure, diff, trend). Alerts on >50% timing regression or >25% bundle growth. Stores history in .prodmaster/benchmark-reports/.
version: 1.0.0
triggers:
  - /prodmasterai benchmark
  - benchmark this
  - performance check
  - check performance
  - perf regression
  - measure performance
  - how fast is this
reads:
  - memory/project-context.md
writes:
  - memory/benchmark-log.md
  - .prodmaster/benchmark-reports/
generated: false
generated_from: ""
---

# Benchmark

Performance regression detection for web applications. Captures Core Web Vitals, bundle sizes, and network metrics. Compares against stored baselines and tracks trends over time.

---

## Modes

| Mode | Trigger | What it does |
|---|---|---|
| **baseline** | `/prodmasterai benchmark --baseline` | Captures current performance as the reference point |
| **measure** | `/prodmasterai benchmark <url>` | Measures current performance, compares to baseline |
| **diff** | `/prodmasterai benchmark --diff` | Before/after comparison for current branch changes |
| **trend** | `/prodmasterai benchmark --trend` | Historical trend report from stored reports |

Default mode when no flag given: `measure` if baseline exists, `baseline` if no baseline found.

---

## Phase 1 — Setup

1. Check for `.prodmaster/benchmark-reports/` directory. Create if absent.
2. Read existing baseline: `.prodmaster/benchmark-reports/baseline.json`. If absent and mode is `measure`: switch to `baseline` mode, notify user.
3. Identify the target URL:
   - Explicit `<url>` argument → use directly
   - `memory/project-context.md` → check for `deploy_url` field
   - `CLAUDE.md` → scan for production or staging URL
   - If none found: ask user for URL before proceeding

---

## Phase 2 — Measurement

For each measurement run, collect metrics via browser automation (if available) or `curl`/`fetch` fallback:

### Core Web Vitals (browser required)
Extract via `performance.getEntries()` and PerformanceObserver:

| Metric | Target | Critical threshold |
|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s | > 4.0s |
| FID / INP (Interaction to Next Paint) | < 200ms | > 500ms |
| CLS (Cumulative Layout Shift) | < 0.1 | > 0.25 |
| TTFB (Time to First Byte) | < 800ms | > 1800ms |
| FCP (First Contentful Paint) | < 1.8s | > 3.0s |

### Bundle Metrics (from network requests)
- Total JS bytes (sum of all `.js` responses)
- Total CSS bytes (sum of all `.css` responses)
- Total image bytes
- Total request count
- Largest 15 resources (URL + size + type)

### Fallback (no browser available)
Use `curl -w` timing metrics:
- `time_namelookup`, `time_connect`, `time_starttransfer`, `time_total`
- Response size from Content-Length or actual download
- HTTP status code

Run 3 measurements and take the median to reduce noise.

---

## Phase 3 — Baseline Mode

Save current measurements as baseline:

```json
// .prodmaster/benchmark-reports/baseline.json
{
  "captured_at": "<ISO 8601>",
  "url": "<url>",
  "branch": "<git branch>",
  "commit": "<git rev-parse HEAD>",
  "metrics": {
    "lcp_ms": 1200,
    "fcp_ms": 800,
    "ttfb_ms": 300,
    "cls": 0.05,
    "js_bytes": 245000,
    "css_bytes": 45000,
    "image_bytes": 180000,
    "request_count": 32,
    "largest_resources": [...]
  }
}
```

Output: `Baseline captured. Run /prodmasterai benchmark <url> to measure against it.`

---

## Phase 4 — Measure Mode

Compare current measurements to baseline:

### Regression Detection

| Condition | Severity |
|---|---|
| Any Core Web Vital > critical threshold | critical |
| Timing metric increased > 50% vs baseline | high |
| JS bundle grew > 25% vs baseline | high |
| Total bytes grew > 30% vs baseline | medium |
| Request count grew > 20% vs baseline | medium |
| Any metric improved > 20% | positive (log, don't alert) |

### Output Format

```
== Benchmark: <url> ==
Captured:  <timestamp>  (baseline: <baseline date>)

Core Web Vitals:
  LCP     <value>ms   <▲/▼ delta vs baseline>  <PASS/WARN/FAIL>
  FCP     <value>ms   <delta>                   <PASS/WARN/FAIL>
  TTFB    <value>ms   <delta>                   <PASS/WARN/FAIL>
  CLS     <value>     <delta>                   <PASS/WARN/FAIL>

Bundle:
  JS      <size>KB    <delta>  <PASS/WARN/FAIL>
  CSS     <size>KB    <delta>  <PASS/WARN/FAIL>
  Images  <size>KB    <delta>
  Total   <N> requests (<delta>)

Largest resources (new or grown >10%):
  1. <url fragment>  <size>KB  <type>

Regressions: <N critical, N high, N medium>
Verdict: <GREEN | YELLOW | RED>

Next:
  <"No regressions — performance is stable" | "N regressions detected — review before shipping" | "Critical regression: <metric> — investigate before deploying">
```

---

## Phase 5 — Diff Mode

For the current branch: measure performance before and after the diff.

1. Stash current changes or use `git worktree` to isolate.
2. Measure baseline (on main branch HEAD).
3. Apply changes (or switch to feature branch).
4. Measure current.
5. Compare — same regression thresholds as Measure mode.
6. Output side-by-side before/after table.

---

## Phase 6 — Trend Mode

Read all stored report files in `.prodmaster/benchmark-reports/`:

```
.prodmaster/benchmark-reports/
  baseline.json
  2026-03-20T14:30.json
  2026-03-21T09:15.json
  2026-03-27T01:00.json
```

Compute trends over the last N reports (default: last 10):
- Direction: improving / stable / degrading per metric
- Rate of change: X ms/week for timing metrics, X KB/week for bundle
- Longest regression streak (how many consecutive reports got worse)

Output trend table:

```
== Benchmark Trend: last <N> measurements ==

  Metric    Current   30d ago   Change    Trend
  ─────────────────────────────────────────────
  LCP       1.2s      1.1s      +9%       ↗ degrading slowly
  JS bundle 245KB     198KB     +24%      ↗ degrading (near threshold)
  TTFB      300ms     280ms     +7%       → stable
  CLS       0.05      0.08      -38%      ↘ improving
```

---

## Storage Format

Each measurement saved as:
```
.prodmaster/benchmark-reports/<ISO-timestamp>.json
```

Contains: url, branch, commit, metrics (same schema as baseline.json).

Baseline is always a separate `baseline.json` — never overwritten by measure runs.

---

## Append to `memory/benchmark-log.md`

```yaml
---
date: <YYYY-MM-DD>
url: <url>
mode: baseline | measure | diff | trend
regressions: N
verdict: GREEN | YELLOW | RED
session_id: <session_id>
---
```

---

## Integration with Auto-Pilot

When `autonomous_mode: true`:
- Mode: `measure` if baseline exists, `baseline` otherwise
- On RED verdict: log as decision, continue (performance regressions don't block auto-pilot by default)
- On critical Web Vital failure: park auto-pilot with blocker

---

## Rules

- Always run 3 measurements and use the median — single measurements are noisy
- Never overwrite `baseline.json` except with explicit `--baseline` flag
- Diff mode must not modify the working tree — use stash or worktree isolation
- Trend reports require at least 3 stored measurements to be meaningful
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
