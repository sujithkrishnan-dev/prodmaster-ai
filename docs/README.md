# ProdMaster AI — Developer Guide

For contributors and developers working on the plugin itself.
For user documentation, see the root [README.md](../README.md).

---

## Clone & local install

```bash
git clone https://github.com/sujithkrishnan-dev/prodmaster-ai ~/.claude/plugins/prodmaster-ai
cd ~/.claude/plugins/prodmaster-ai
claude plugin install prodmaster-ai@prodmaster-ai-marketplace
```

---

## Platform hook setup

**Windows** — works out of the box. The SessionStart hook uses `run-hook.cmd` + PowerShell with no changes needed.

**macOS / Linux** — after cloning, edit `.claude-plugin/hooks.json` and change the SessionStart command to:

```json
"command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.sh\" session-start"
```

Python 3 must be on PATH (default on macOS/Linux) — required for `pre-tool-bash.py`, `post-tool-write.py`, and `stop-quality-gate.py`.

---

## Running tests

```bash
python -m pytest tests/ -v
```

Or with the convenience wrapper:

```bash
make test
```

The test suite validates skill frontmatter, hook files, memory file schemas, and the plugin manifest. All tests must pass before opening a PR.

---

## Adding a skill

See [docs/EXTENDING.md](EXTENDING.md) for the full walkthrough: frontmatter requirements, keyword registration, test entry, and documentation steps.

---

## Project layout

```
.claude-plugin/   ← canonical plugin manifest and hook registration
hooks/            ← hook scripts (run-hook.cmd, run-hook.sh, *.py)
skills/           ← one directory per skill, each containing SKILL.md
memory/           ← local state (never committed upstream)
tests/            ← pytest suite
docs/             ← developer documentation (this file, EXTENDING.md)
```
