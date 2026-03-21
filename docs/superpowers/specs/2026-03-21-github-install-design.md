# Design: GitHub-based Plugin Install

**Date:** 2026-03-21
**Goal:** Enable `claude plugin install prodmaster-ai@github:sujithkrishnan-dev/prodmaster-ai` without cloning.

## Problem

Currently the only install path is manual clone + `/plugin install --local`. Users cannot install without a local clone.

## Approach

Add a root-level `claude-plugin.json` install manifest that the Claude Code CLI reads when resolving a `@github:` source. Sync version numbers across all manifests. Update README with the one-line install command.

## Files Changed

| File | Action |
|---|---|
| `claude-plugin.json` | Create — root-level install manifest |
| `.claude-plugin/marketplace.json` | Update — fix version `1.3.0` → `2.0.0` |
| `docs/README.md` | Update — add one-line install command, keep manual section for dev use |

## `claude-plugin.json` Schema

```json
{
  "name": "prodmaster-ai",
  "version": "2.0.0",
  "description": "Meta-orchestration, measurement, and self-evolving intelligence layer for Claude Code.",
  "author": "sujithkrishnan-dev",
  "source": {
    "type": "github",
    "url": "https://github.com/sujithkrishnan-dev/prodmaster-ai.git"
  },
  "skills": "skills/"
}
```

**Notes:**
- `hooks` is intentionally omitted — hook registration is already defined in `.claude-plugin/hooks.json` with correct matchers and nested structure. The CLI discovers hooks from the plugin directory structure.
- `requires` is omitted — not a documented Claude Code CLI standard field.
- `source.url` uses the `.git` suffix to match the format in `marketplace.json` which is the known-working format.

## Version Sync

All manifests must agree on version `2.0.0`:
- `claude-plugin.json` — `2.0.0` (new)
- `.claude-plugin/plugin.json` — already `2.0.0` (no change needed)
- `.claude-plugin/marketplace.json` — fix `1.3.0` → `2.0.0`

## README Install Block

Replace the current "Manual" section header with a primary install command:

```
## Installation

claude plugin install prodmaster-ai@github:sujithkrishnan-dev/prodmaster-ai
```

Keep the existing `--local` instructions under a "Local Development" subsection for contributors.

## Out of Scope

- npm publishing
- Submission to `claude-plugins-official` (requires Anthropic approval)
- Windows/macOS hook path switching (already handled in existing docs)
