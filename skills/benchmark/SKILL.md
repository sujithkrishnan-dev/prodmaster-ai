---
name: benchmark
description: Performance measurement with 4 modes — Core Web Vitals, bundle size analysis, custom benchmark suites, and regression alerts. Stores baselines for trend tracking.
version: 1.0.0
triggers:
  - User runs /prodmasterai benchmark
  - User says "run benchmarks", "check performance", "is it slower", "performance regression", "bundle size"
reads:
  - memory/project-context.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# Benchmark — Performance Measurement

Measure performance across 4 modes. Store baselines for regression detection.

## Modes

### Mode 1: Core Web Vitals (web projects)

Requires Playwright plugin or browser automation.

| Metric | Target | Measurement |
|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s | Time to largest visible element |
| FID (First Input Delay) | < 100ms | Time to first interaction response |
| CLS (Cumulative Layout Shift) | < 0.1 | Visual stability score |
| TTFB (Time to First Byte) | < 800ms | Server response time |
| FCP (First Contentful Paint) | < 1.8s | Time to first render |

If Playwright not available: skip and suggest installation.

### Mode 2: Bundle Size

Detect bundler and measure:

| Tool | Command | Output |
|---|---|---|
| webpack | `npx webpack --json` | Asset sizes |
| Vite | `npx vite build` | Chunk report |
| esbuild | `npx esbuild --bundle --analyze` | Size breakdown |
| Rollup | `npx rollup -c` + plugin | Module sizes |
| Go | `go build -o /dev/null` | Binary size |
| Rust | `cargo build --release` | Binary size |

Compare against baseline. Alert if any asset grows >10%.

### Mode 3: Custom Benchmarks

Run project-specific benchmark suites:
- `npm run bench` / `pytest --benchmark` / `go test -bench` / `cargo bench`
- Parse output for timing data
- Compare against stored baselines

### Mode 4: Regression Detection

Compare all metrics against `memory/benchmark-baseline.json`:
- Improved (>5% better): green
- Stable (within 5%): neutral
- Regressed (>5% worse): red alert with suspected cause

## Process

### 1. Auto-Detect Applicable Modes

Check project type and available tools in parallel. Enable all applicable modes.

### 2. Run Benchmarks

Execute all enabled modes in parallel. Capture results.

### 3. Report

```
Benchmark Report
================
Mode: Core Web Vitals + Bundle Size + Custom

Core Web Vitals:
  LCP:  1.8s  (target: <2.5s)  PASS
  CLS:  0.05  (target: <0.1)   PASS
  TTFB: 650ms (target: <800ms) PASS

Bundle Size:
  main.js:   142kb (baseline: 138kb, +2.9%)  OK
  vendor.js: 89kb  (baseline: 87kb,  +2.3%)  OK
  Total:     231kb (baseline: 225kb, +2.7%)  OK

Custom Benchmarks:
  test_sort: 12ms (baseline: 11ms, +9.1%)  WARN
  test_search: 3ms (baseline: 3ms, 0%)     OK

Regressions: 1 (test_sort +9.1%)
```

### 4. Save Baseline

Write to `memory/benchmark-baseline.json`:
```json
{
  "date": "YYYY-MM-DD",
  "web_vitals": {"lcp": 1.8, "cls": 0.05, "ttfb": 650},
  "bundle_size": {"total": 231000, "assets": {}},
  "custom": {"test_sort": 12, "test_search": 3}
}
```

## Rules

- Run all applicable modes — never skip a mode that can run
- Store baselines after every run for future comparison
- Regression threshold: 5% for alerts, 20% for hard warnings
- If no benchmarks exist at all, set up baseline and report "First run — baseline established"
- Never block deployment for performance — warn only
