---
name: document-release
description: Post-ship documentation sync. Updates CHANGELOG, polishes release notes, checks docs-code consistency, and flags stale documentation.
version: 1.0.0
triggers:
  - User runs /prodmasterai document-release
  - User says "update docs", "document the release", "sync documentation", "release notes"
reads:
  - memory/project-context.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# Document Release — Post-Ship Documentation Sync

After shipping, sync all documentation with what was actually built. Catch stale docs, update CHANGELOG, and ensure consistency.

## Process

### 1. Gather Release Context

Read in parallel:
- `git log <last-release-tag>..HEAD --oneline` — all commits since last release
- `CHANGELOG.md` — current state
- `README.md` — current state
- `docs/` directory — any project documentation

If no release tag exists: use all commits on the branch.

### 2. CHANGELOG Update

Check `CHANGELOG.md`:
- **Exists:** Parse current entries. For each commit not yet documented, draft a CHANGELOG entry following the existing format.
- **Does not exist:** Ask user if they want one created. If yes, generate from commit history.

Group entries by type:
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- <new features>

### Changed
- <modifications>

### Fixed
- <bug fixes>

### Security
- <security-related changes>
```

### 3. README Consistency Check

Scan README.md for:
- Installation instructions referencing old versions
- Feature descriptions that no longer match the code
- Broken internal links
- API examples using deprecated patterns

Report and fix inline.

### 4. Documentation Consistency

For each file in `docs/`:
- Check if referenced functions/APIs still exist in the codebase
- Check if new public APIs are documented
- Flag any doc file not updated in >90 days that references active code

### 5. Release Notes

Generate release notes from CHANGELOG + commit history:

```markdown
# Release vX.Y.Z

## Highlights
- <top 3 most impactful changes>

## What's New
<grouped by category>

## Breaking Changes
<if any>

## Migration Guide
<if breaking changes exist>
```

### 6. Commit Documentation Changes

If any files were modified:
```
docs: sync documentation for release vX.Y.Z
```

### Completion Message

```
Documentation sync complete for vX.Y.Z
=======================================
CHANGELOG:  updated (N new entries)
README:     N fixes applied
Docs:       N stale references flagged, M fixed
Release notes: generated

Review: docs/release-notes-vX.Y.Z.md
```

## Rules

- Follow existing CHANGELOG format — never impose a new one
- If no CHANGELOG exists, ask before creating — some projects prefer GitHub Releases
- README fixes should be minimal and targeted — don't rewrite
- Never fabricate features — only document what the commits actually did
- Flag stale docs but don't delete them without confirmation
