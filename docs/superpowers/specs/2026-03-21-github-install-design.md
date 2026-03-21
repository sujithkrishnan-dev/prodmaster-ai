# Design: GitHub-based Plugin Install

**Date:** 2026-03-21
**Status:** Implemented (2026-03-21) — see notes below.

**Goal:** Enable users to install from GitHub without a local clone.

## How It Works

`claude plugin install` does not support `@github:` as a source format. The correct approach is a two-step process:

1. Register the GitHub repo as a marketplace
2. Install the plugin from that marketplace

```bash
claude plugin marketplace add sujithkrishnan-dev/prodmaster-ai
claude plugin install prodmaster-ai@prodmaster-ai-marketplace
```

## Root Cause of Original Failure

`.claude-plugin/marketplace.json` had `"source": { "type": "github", "url": "..." }` which fails schema validation. The CLI requires `"source": "./"` (relative path string pointing to the plugin directory within the repo).

## Files Changed

| File | Action |
|---|---|
| `.claude-plugin/marketplace.json` | Fix `source` field: object → `"./"`, version `1.3.0` → `2.0.0` |
| `docs/README.md` | Update install commands to two-step marketplace flow |

## Out of Scope

- npm publishing
- Submission to `claude-plugins-official` (requires Anthropic approval)
- Windows/macOS hook path switching (already handled in existing docs)
