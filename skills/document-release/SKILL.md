---
name: document-release
description: Post-ship documentation sync — analyzes diff, auto-updates README/ARCHITECTURE/CONTRIBUTING/CLAUDE.md, polishes CHANGELOG voice (never regenerates), cleans TODOs, optional VERSION bump. Conservative: auto-execute safe updates, ask for risky changes. Cross-doc consistency checks.
version: 1.1.0
argument-hint: "[--bump patch|minor|major]"
effort: low
paths:
  - "**/*.md"
  - "docs/**"
  - "CHANGELOG*"
  - "README*"
triggers:
  - /prodmasterai document-release
  - sync docs
  - update docs
  - post-ship docs
  - document this release
  - docs sync
  - update readme
reads:
  - memory/project-context.md
  - memory/ship-log.md
writes:
  - memory/document-release-log.md
  - memory/project-context.md
generated: false
generated_from: ""
---

# Document Release

Post-ship documentation sync. Runs after `/prodmasterai ship` or any significant merge to keep README, ARCHITECTURE, CONTRIBUTING, CLAUDE.md, and CHANGELOG in sync with the actual code.

Conservative by default: safe updates execute automatically, risky changes ask before acting.

---

## Principles

- **Never regenerate** CHANGELOG entries — polish voice only, never replace content
- **Diff-aware** — only update docs affected by what actually changed
- **Cross-doc consistency** — if README mentions a feature, all other docs agree
- **Ask before deleting** — never remove documentation without confirmation
- **No hallucination** — every doc claim must be verifiable from the current code

---

## Phase 1 — Diff Analysis

Read the diff to understand what changed:

```bash
git diff main...HEAD --name-only
git log main...HEAD --oneline
```

Categorize changes:
- **New features**: new files, new exported functions/classes
- **Changed APIs**: renamed/removed functions, changed signatures, changed flags
- **New dependencies**: new entries in package.json/Cargo.toml/pyproject.toml
- **Config changes**: new env vars, new config keys, changed defaults
- **Removed code**: deleted files, removed functions

Build a doc impact map: which documentation files need review based on what changed.

---

## Phase 2 — README Update

Check README.md (or readme.md, README.rst):

### Auto-execute (safe, no confirmation needed):
- Add new commands/features to "Features" or equivalent section
- Update installation steps if dependencies changed
- Add new config env vars to the Configuration section
- Update "Quick Start" if the main workflow changed
- Fix broken code examples (wrong function names, outdated flags)

### Ask before acting (risky):
- Removing any section (even if it looks outdated)
- Changing the project description or tagline
- Restructuring the document layout

### Checks:
- Every feature listed in README must exist in the codebase
- Every code example in README must be syntactically valid
- If a command is shown, it must match the current CLI interface

---

## Phase 3 — ARCHITECTURE Update

Check ARCHITECTURE.md (or docs/architecture.md, docs/ARCHITECTURE.md):

### Auto-execute:
- Add new modules/services to the component list
- Update data flow diagrams if new integrations were added
- Note new external dependencies

### Ask before acting:
- Any removal or restructuring of architectural sections
- Changes to decision records or rationale sections

### Checks:
- All components listed exist in the codebase
- No references to deleted files or deprecated patterns

---

## Phase 4 — CONTRIBUTING Update

Check CONTRIBUTING.md:

### Auto-execute:
- Add new skill triggers to the trigger list (if this is a plugin)
- Update "How to run tests" if test commands changed
- Add new required environment variables to the setup section

### Ask before acting:
- Changing contribution guidelines or PR requirements
- Modifying the code of conduct or governance sections

---

## Phase 5 — CLAUDE.md Update

Check CLAUDE.md:

### Auto-execute:
- Add new `/command` entries to the command table
- Update hook descriptions if hooks changed
- Add new skill triggers if new skills were added

### Ask before acting:
- Removing any existing entry
- Changing the plugin description or top-level overview

---

## Phase 6 — CHANGELOG Polish

CHANGELOG entries are never regenerated. Only polish:

Read the most recent entry (usually `Unreleased` or today's date).

**Polish rules:**
- Active voice: "Add X" not "Added X", "Fix Y" not "Fixed Y"
- User-facing language: "Users can now X" not "Refactored the X module"
- No internal details: no function names, no file paths, no PR numbers in user-facing entries
- Consistent tense: all entries in same entry use same voice
- No trailing punctuation on bullet items

**Never:**
- Regenerate entries from scratch
- Delete entries
- Reorder entries
- Add entries not authored by ship/user

---

## Phase 7 — TODO Cleanup

Scan for inline TODOs in changed files:

```bash
git diff main...HEAD -U0 | grep "^\+" | grep -i "TODO\|FIXME\|HACK\|XXX"
```

For each TODO added in this diff:
- If it references a specific issue/ticket: leave it
- If it's a vague "TODO: clean up later": flag it (ask user whether to remove or convert to a GitHub issue)
- If it says "TODO: remove before ship": remove it automatically and note in output

Scan `TODOS.md` if it exists:
- Mark items that have a corresponding commit as `[done]`
- Never delete entries — mark status only

---

## Phase 8 — VERSION Bump (optional)

Only run if `--bump` flag is passed or user explicitly asked.

Read current version from:
1. `VERSION` file
2. `package.json` → `version` field
3. `Cargo.toml` → `version` field
4. `pyproject.toml` → `tool.poetry.version` or `project.version`

Determine bump type:
- **patch**: bug fixes only (no new features, no API changes)
- **minor**: new features, no breaking changes
- **major**: breaking changes

Ask for confirmation before bumping. Never auto-bump without explicit intent.

---

## Phase 9 — Cross-Doc Consistency Check

After all updates, run consistency checks:

| Check | What to verify |
|---|---|
| Feature list parity | Features in README match features in CHANGELOG |
| Command parity | Commands in CLAUDE.md match commands in README |
| Config parity | Env vars in README match env vars in CONTRIBUTING setup |
| Link validity | Internal markdown links point to existing files/sections |
| Version parity | Version in README/package.json/VERSION all match |

Flag inconsistencies. Auto-fix obvious ones (wrong link target). Ask for the rest.

---

## Output Format

```
== Document Release: <branch> ==
Diff analyzed: <N files changed, N features added, N APIs changed>

README:      <N updates applied | no changes needed>
ARCHITECTURE: <N updates applied | not found | no changes needed>
CONTRIBUTING: <N updates applied | not found | no changes needed>
CLAUDE.md:   <N updates applied | no changes needed>
CHANGELOG:   <N entries polished | no changes needed>
TODOs:       <N resolved, N flagged for review>
VERSION:     <skipped | bumped X.Y.Z → X.Y.Z>

Consistency: <clean | N inconsistencies (N auto-fixed, N need review)>

Pending approval (N items):
  1. README: Remove "Legacy API" section — confirm? (y/n)
  2. TODO on line 47 of auth.js: "clean this up" — remove or convert to issue?
```

Commit doc changes:
```bash
git commit -m "docs: sync documentation for <branch>"
```

---

## Append to `memory/document-release-log.md`

```yaml
---
date: <YYYY-MM-DD>
branch: <branch>
files_updated: N
changelog_entries_polished: N
todos_resolved: N
version_bumped: false | X.Y.Z
session_id: <session_id>
---
```

---

## Integration with Auto-Pilot

When `autonomous_mode: true`:
- All safe Phase 2-7 updates execute automatically
- Risky changes (removals, restructuring) logged as decisions, not blocked
- VERSION bump skipped unless explicitly in the task goal
- Cross-doc inconsistencies auto-fixed where unambiguous

---

## Rules

- Never regenerate CHANGELOG entries — polish voice only
- Never delete documentation without user confirmation
- Every doc claim must be verifiable from current code
- Cross-doc consistency check always runs — never skip Phase 9
- Commit doc changes separately from code changes
- **Never contribute anything upstream** — upstream is exclusively evolve-self's responsibility
