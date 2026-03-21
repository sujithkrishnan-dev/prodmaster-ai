# GitHub Install Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable `claude plugin install prodmaster-ai@github:sujithkrishnan-dev/prodmaster-ai` so users can install without cloning.

**Architecture:** Create a root-level `claude-plugin.json` install manifest the CLI reads when fetching from GitHub. Fix the stale version in `.claude-plugin/marketplace.json`. Update README to surface the one-line install command as the primary path.

**Tech Stack:** JSON, Markdown

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `claude-plugin.json` | Create | Root-level install manifest — name, version, source, skills path |
| `.claude-plugin/marketplace.json` | Modify | Fix stale version `1.3.0` → `2.0.0` |
| `docs/README.md` | Modify | Add one-line GitHub install command, demote manual clone to "Local Development" subsection |

---

### Task 1: Create `claude-plugin.json`

**Files:**
- Create: `claude-plugin.json` (repo root)

- [ ] **Step 1: Create the file**

Create `claude-plugin.json` at the repo root with this exact content:

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

- [ ] **Step 2: Verify the file is valid JSON**

Run:
```bash
python -c "import json; json.load(open('claude-plugin.json')); print('valid')"
```
Expected output: `valid`

- [ ] **Step 3: Commit**

```bash
git add claude-plugin.json
git commit -m "feat: add claude-plugin.json root install manifest for GitHub-based install"
```

---

### Task 2: Fix version in `marketplace.json`

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Update the version field**

In `.claude-plugin/marketplace.json`, change line 11:
```json
"version": "1.3.0",
```
to:
```json
"version": "2.0.0",
```

- [ ] **Step 2: Verify all manifest versions agree**

Run:
```bash
python -c "
import json
root = json.load(open('claude-plugin.json'))
plugin = json.load(open('.claude-plugin/plugin.json'))
market = json.load(open('.claude-plugin/marketplace.json'))
mv = market['plugins'][0]['version']
print(f'claude-plugin.json: {root[\"version\"]}')
print(f'.claude-plugin/plugin.json: {plugin[\"version\"]}')
print(f'.claude-plugin/marketplace.json: {mv}')
assert root['version'] == plugin['version'] == mv, 'VERSION MISMATCH'
print('all versions match')
"
```
Expected output:
```
claude-plugin.json: 2.0.0
.claude-plugin/plugin.json: 2.0.0
.claude-plugin/marketplace.json: 2.0.0
all versions match
```

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "fix: sync marketplace.json version to 2.0.0"
```

---

### Task 3: Update README install section

**Files:**
- Modify: `docs/README.md`

- [ ] **Step 1: Replace the Installation section**

In `docs/README.md`, replace the current `## Installation` section (lines 5–16):

```markdown
## Installation

### Manual (local development)

```bash
git clone <this-repo> ~/.claude/plugins/prodmaster-ai
```

Then in Claude Code:
```
/plugin install --local ~/.claude/plugins/prodmaster-ai
```
```

With:

```markdown
## Installation

```
claude plugin install prodmaster-ai@github:sujithkrishnan-dev/prodmaster-ai
```

### Local Development

```bash
git clone https://github.com/sujithkrishnan-dev/prodmaster-ai ~/.claude/plugins/prodmaster-ai
```

Then in Claude Code:
```
/plugin install --local ~/.claude/plugins/prodmaster-ai
```
```

- [ ] **Step 2: Verify the README renders the install command correctly**

Open `docs/README.md` and confirm:
- The first code block under `## Installation` shows `claude plugin install prodmaster-ai@github:sujithkrishnan-dev/prodmaster-ai`
- The clone instructions still exist under `### Local Development`
- `### Platform Hook Setup` section is untouched (starts at what was line 18)

- [ ] **Step 3: Commit**

```bash
git add docs/README.md
git commit -m "docs: add GitHub install command as primary install path"
```

---

## Done

After all 3 tasks, verify end state:

```bash
python -c "
import json, pathlib
assert pathlib.Path('claude-plugin.json').exists(), 'missing claude-plugin.json'
root = json.load(open('claude-plugin.json'))
plugin = json.load(open('.claude-plugin/plugin.json'))
market = json.load(open('.claude-plugin/marketplace.json'))
mv = market['plugins'][0]['version']
assert root['version'] == plugin['version'] == mv == '2.0.0'
readme = pathlib.Path('docs/README.md').read_text()
assert 'claude plugin install prodmaster-ai@github:sujithkrishnan-dev/prodmaster-ai' in readme
assert 'Local Development' in readme
print('all checks passed')
"
```
Expected: `all checks passed`
