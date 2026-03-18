# ProdMaster AI Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the ProdMaster AI Claude Code plugin — a three-layer meta-orchestration, measurement, and self-evolving intelligence system that sits above Superpowers workflows.

**Architecture:** Three layers: (1) SessionStart hook injects memory context into every conversation, (2) six focused skills handle orchestration/measurement/reporting/decisions/learning/evolution, (3) an append-only memory system of structured markdown files grows each cycle and drives auto-evolution via the `evolve-self` skill.

**Tech Stack:** Markdown skill files, JSON manifests, PowerShell/Bash hook runners, vanilla HTML dashboard (no npm, no frameworks, DOM-safe JS), Python validation scripts for testing.

**Spec:** `docs/superpowers/specs/2026-03-18-prodmaster-ai-design.md`

---

## Chunk 1: Project Scaffold

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `EVOLUTION-LOG.md`
- Create: `tests/__init__.py`

### Task 1: Git init + base directory structure

- [ ] **Step 1: Init git repo and create all top-level directories**

```bash
cd "C:\Users\teame\Desktop\Plugin"
git init
mkdir -p .claude-plugin hooks skills/orchestrate skills/measure skills/report skills/decide skills/learn skills/evolve-self memory/pending-upstream memory/connectors reports docs tests
```

- [ ] **Step 2: Write validation test for plugin.json (failing first)**

Create `tests/test_scaffold.py`:
```python
import json, os, pytest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_plugin_json_exists():
    assert os.path.exists(os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json"))

def test_plugin_json_valid():
    path = os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json")
    with open(path) as f:
        data = json.load(f)
    assert data["name"] == "prodmaster-ai"
    assert "version" in data
    assert "description" in data
    assert "upstream" in data

def test_evolution_log_exists():
    assert os.path.exists(os.path.join(PLUGIN_ROOT, "EVOLUTION-LOG.md"))

def test_dashboard_html_exists():
    assert os.path.exists(os.path.join(PLUGIN_ROOT, "reports", "dashboard.html"))

def test_dashboard_html_valid():
    path = os.path.join(PLUGIN_ROOT, "reports", "dashboard.html")
    content = open(path).read()
    assert "<!DOCTYPE html>" in content
    assert "ProdMaster AI Dashboard" in content
    for panel in ["Feature Velocity", "QA Health", "Active Blockers", "BA Decisions Log"]:
        assert panel in content, f"Missing panel: {panel}"

def test_dashboard_has_no_external_resources():
    import re
    path = os.path.join(PLUGIN_ROOT, "reports", "dashboard.html")
    content = open(path).read()
    external = re.findall(r'(?:src|href)=["\']https?://', content)
    assert not external, f"External resources found: {external}"
```

- [ ] **Step 3: Run test — verify it fails**

```bash
cd "C:\Users\teame\Desktop\Plugin"
python -m pytest tests/test_scaffold.py -v
```
Expected: FAIL

- [ ] **Step 4: Create `.claude-plugin/plugin.json`**

```json
{
  "name": "prodmaster-ai",
  "version": "1.0.0",
  "description": "Meta-orchestration, measurement, and self-evolving intelligence layer for Claude Code. Sits above Superpowers to orchestrate features, track velocity, generate reports, and auto-improve itself.",
  "category": "productivity",
  "author": {
    "name": "",
    "email": ""
  },
  "upstream": {
    "repo": "",
    "branch": "main",
    "pr_label": "auto-evolved"
  }
}
```

- [ ] **Step 5: Create `EVOLUTION-LOG.md`**

```markdown
# ProdMaster AI — Upstream Evolution Log

Records changes contributed back to the plugin repository via auto-PR.
Local-only evolution is tracked in `memory/evolution-log.md`.

<!-- evolve-self appends entries here when PRs are merged upstream -->
```

- [ ] **Step 6: Create `tests/__init__.py`** — empty file

- [ ] **Step 7: Run test — verify scaffold tests pass (dashboard tests will still fail)**

```bash
python -m pytest tests/test_scaffold.py::test_plugin_json_exists tests/test_scaffold.py::test_plugin_json_valid tests/test_scaffold.py::test_evolution_log_exists -v
```
Expected: PASS (3/3)

- [ ] **Step 8: Commit**

```bash
git add .claude-plugin/ EVOLUTION-LOG.md tests/
git commit -m "feat: initial plugin scaffold and manifest"
```

---

## Chunk 2: Hook System

**Files:**
- Create: `hooks/hooks.json`
- Create: `hooks/run-hook.cmd`
- Create: `hooks/run-hook.sh`
- Create: `hooks/session-start.md`

### Task 2: Hook runners and session-start template

- [ ] **Step 1: Write test for hooks (failing first)**

Create `tests/test_hooks.py`:
```python
import os, json, subprocess, pytest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS_DIR = os.path.join(PLUGIN_ROOT, "hooks")

def test_hooks_json_exists():
    assert os.path.exists(os.path.join(HOOKS_DIR, "hooks.json"))

def test_hooks_json_valid():
    with open(os.path.join(HOOKS_DIR, "hooks.json")) as f:
        data = json.load(f)
    assert "hooks" in data
    assert "SessionStart" in data["hooks"]

def test_run_hook_sh_exists():
    assert os.path.exists(os.path.join(HOOKS_DIR, "run-hook.sh"))

def test_run_hook_cmd_exists():
    assert os.path.exists(os.path.join(HOOKS_DIR, "run-hook.cmd"))

def test_session_start_template_exists():
    assert os.path.exists(os.path.join(HOOKS_DIR, "session-start.md"))

def test_run_hook_sh_produces_output():
    hook = os.path.join(HOOKS_DIR, "run-hook.sh")
    try:
        result = subprocess.run(
            ["bash", hook, "session-start"],
            cwd=PLUGIN_ROOT, capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"Hook failed: {result.stderr}"
        assert "ProdMaster AI" in result.stdout
    except FileNotFoundError:
        pytest.skip("bash not available")
```

- [ ] **Step 2: Run test — verify it fails**

```bash
python -m pytest tests/test_hooks.py -v
```

- [ ] **Step 3: Create `hooks/hooks.json`**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "async": false
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 4: Create `hooks/session-start.md`**

```markdown
## ProdMaster AI — Session Context

**Active Features:**
{{active_features}}

**Top Patterns (last 5):**
{{top_patterns}}

**Open Skill Gaps:**
{{open_gaps}}

**Recent Evolutions:**
{{recent_evolutions}}

---
*Skills available: orchestrate, measure, report, decide, learn, evolve-self*
```

- [ ] **Step 5: Create `hooks/run-hook.sh`**

```bash
#!/usr/bin/env bash
# ProdMaster AI — SessionStart hook runner (Unix/macOS/WSL)
# Reads memory files and outputs formatted context to stdout.
# Usage: run-hook.sh session-start

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MEMORY_DIR="${PLUGIN_ROOT}/memory"
TEMPLATE="${SCRIPT_DIR}/session-start.md"

if [[ ! -f "${TEMPLATE}" ]]; then
  printf '## ProdMaster AI\n*Memory not yet initialized.*\n'
  exit 0
fi

# Extract ## Active Features section (up to next ## heading)
extract_section() {
  local file="$1" section="$2"
  if [[ ! -f "${file}" ]]; then printf '(none yet)'; return; fi
  local result
  result=$(awk "/^## ${section}/{found=1; next} found && /^## /{exit} found && NF{print}" "${file}" \
    | grep -v '^<!--' | head -5)
  printf '%s' "${result:-"(none yet)"}"
}

# Extract last N lines matching a pattern
extract_last() {
  local file="$1" pattern="$2" n="$3" prefix="$4"
  if [[ ! -f "${file}" ]]; then printf '(none yet)'; return; fi
  local result
  result=$(grep "^${pattern}" "${file}" 2>/dev/null | tail -"${n}" | sed "s/^${pattern}/- /")
  printf '%s' "${result:-"(none yet)"}"
}

ACTIVE_FEATURES=$(extract_section "${MEMORY_DIR}/project-context.md" "Active Features")
TOP_PATTERNS=$(extract_last "${MEMORY_DIR}/patterns.md" "pattern: " 5 "- ")
OPEN_GAPS=$(grep -A3 "status: open" "${MEMORY_DIR}/skill-gaps.md" 2>/dev/null \
  | grep "^pattern:" | sed 's/^pattern: /- /' | head -5 || printf '(none yet)')
RECENT_EVOLUTIONS=$(extract_last "${MEMORY_DIR}/evolution-log.md" "change_summary: " 3 "- ")

OUTPUT=$(cat "${TEMPLATE}")
OUTPUT="${OUTPUT//\{\{active_features\}\}/${ACTIVE_FEATURES}}"
OUTPUT="${OUTPUT//\{\{top_patterns\}\}/${TOP_PATTERNS}}"
OUTPUT="${OUTPUT//\{\{open_gaps\}\}/${OPEN_GAPS}}"
OUTPUT="${OUTPUT//\{\{recent_evolutions\}\}/${RECENT_EVOLUTIONS}}"

printf '%s\n' "${OUTPUT}"
exit 0
```

- [ ] **Step 6: Make run-hook.sh executable**

```bash
chmod +x hooks/run-hook.sh
```

- [ ] **Step 7: Create `hooks/run-hook.cmd`**

```batch
@echo off
:: ProdMaster AI -- SessionStart hook runner (Windows)
:: Delegates to PowerShell for robust file reading and string substitution.
setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "PLUGIN_ROOT=%SCRIPT_DIR%.."

powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run-hook.ps1" session-start
exit /b %ERRORLEVEL%
```

- [ ] **Step 8: Create `hooks/run-hook.ps1`** (PowerShell helper invoked by .cmd)

```powershell
# ProdMaster AI -- SessionStart hook runner (PowerShell)
param([string]$Event = "session-start")

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pluginRoot = Split-Path -Parent $scriptDir
$memDir = Join-Path $pluginRoot "memory"
$templatePath = Join-Path $scriptDir "session-start.md"

if (-not (Test-Path $templatePath)) {
    Write-Output "## ProdMaster AI`n*Memory not yet initialized.*"
    exit 0
}

function Get-Section {
    param([string]$FilePath, [string]$Section)
    if (-not (Test-Path $FilePath)) { return "(none yet)" }
    $lines = Get-Content $FilePath
    $capture = $false
    $out = [System.Collections.Generic.List[string]]::new()
    foreach ($line in $lines) {
        if ($line -match "^## $Section") { $capture = $true; continue }
        if ($capture -and $line -match "^## ") { break }
        if ($capture -and $line.Trim() -and $line -notmatch "^<!--") { $out.Add($line) }
    }
    if ($out.Count -eq 0) { return "(none yet)" }
    return ($out | Select-Object -Last 5) -join "`n"
}

function Get-LastMatches {
    param([string]$FilePath, [string]$Pattern, [int]$Count)
    if (-not (Test-Path $FilePath)) { return "(none yet)" }
    $matches = (Select-String -Path $FilePath -Pattern "^$Pattern" | Select-Object -Last $Count)
    if (-not $matches) { return "(none yet)" }
    return ($matches | ForEach-Object { "- " + ($_.Line -replace "^$Pattern", "") }) -join "`n"
}

$activeFeatures = Get-Section (Join-Path $memDir "project-context.md") "Active Features"
$topPatterns = Get-LastMatches (Join-Path $memDir "patterns.md") "pattern: " 5
$openGaps = if (Test-Path (Join-Path $memDir "skill-gaps.md")) {
    $gapLines = Get-Content (Join-Path $memDir "skill-gaps.md")
    $out = [System.Collections.Generic.List[string]]::new()
    $capture = $false
    foreach ($line in $gapLines) {
        if ($line -match "^status: open") { $capture = $true; continue }
        if ($capture -and $line -match "^pattern:") { $out.Add("- " + ($line -replace "^pattern: ","")); $capture = $false }
        if ($line -match "^---") { $capture = $false }
    }
    if ($out.Count -eq 0) { "(none yet)" } else { ($out | Select-Object -First 5) -join "`n" }
} else { "(none yet)" }
$recentEvolutions = Get-LastMatches (Join-Path $memDir "evolution-log.md") "change_summary: " 3

$tpl = Get-Content $templatePath -Raw
$out = $tpl `
    -replace '\{\{active_features\}\}', $activeFeatures `
    -replace '\{\{top_patterns\}\}', $topPatterns `
    -replace '\{\{open_gaps\}\}', $openGaps `
    -replace '\{\{recent_evolutions\}\}', $recentEvolutions

Write-Output $out
```

- [ ] **Step 9: Run tests**

```bash
python -m pytest tests/test_hooks.py -v
```
Expected: PASS (all 6 tests — `test_run_hook_sh_produces_output` needs bash)

- [ ] **Step 10: Commit**

```bash
git add hooks/ tests/test_hooks.py
git commit -m "feat: hook system — SessionStart runner for Windows (PowerShell) and Unix (bash)"
```

---

## Chunk 3: Memory System

**Files:** All `memory/*.md` pre-seeded files, `pending-upstream/`, `connectors/`

### Task 3: Memory files with schemas and initial state

- [ ] **Step 1: Write memory validation test (failing first)**

Create `tests/test_memory.py`:
```python
import os, pytest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_DIR = os.path.join(PLUGIN_ROOT, "memory")

REQUIRED_FILES = [
    "patterns.md", "mistakes.md", "feedback.md", "research-findings.md",
    "skill-performance.md", "skill-gaps.md", "project-context.md",
    "evolution-log.md",
    "pending-upstream/.gitkeep",
    "pending-upstream/last-pr.txt",
    "connectors/README.md", "connectors/skill-pattern-manifest.md",
    "connectors/github.md", "connectors/slack.md", "connectors/linear.md",
]

@pytest.mark.parametrize("filename", REQUIRED_FILES)
def test_memory_file_exists(filename):
    assert os.path.exists(os.path.join(MEMORY_DIR, filename)), f"Missing: memory/{filename}"

def test_project_context_has_counters():
    content = open(os.path.join(MEMORY_DIR, "project-context.md")).read()
    for f in ["total_tasks_completed:", "last_evolved_at_task:", "evolve_every_n_tasks:"]:
        assert f in content

def test_skill_performance_has_example():
    assert "example: true" in open(os.path.join(MEMORY_DIR, "skill-performance.md")).read()

def test_connectors_all_inactive():
    for c in ["github.md", "slack.md", "linear.md"]:
        assert "active: false" in open(os.path.join(MEMORY_DIR, "connectors", c)).read()

def test_skill_pattern_manifest_has_all_skills():
    content = open(os.path.join(MEMORY_DIR, "connectors", "skill-pattern-manifest.md")).read()
    for skill in ["orchestrate", "measure", "report", "decide", "learn", "evolve-self"]:
        assert f"### {skill}" in content

def test_last_pr_txt_has_timestamp():
    import re
    content = open(os.path.join(MEMORY_DIR, "pending-upstream", "last-pr.txt")).read().strip()
    assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', content)
```

- [ ] **Step 2: Run — verify fails**

```bash
python -m pytest tests/test_memory.py -v
```

- [ ] **Step 3: Create `memory/project-context.md`**

```markdown
---
total_tasks_completed: 0
last_evolved_at_task: 0
evolve_every_n_tasks: 10
---

## Active Features
<!-- orchestrate appends: "- YYYY-MM-DD: <feature name> [status: active|blocked|done]" -->

## Blockers
<!-- append: "- YYYY-MM-DD: <description> | age_days: 0 | recommended_fix: <text>" -->

## Decisions Log
<!-- decide appends YAML blocks:
---
date: YYYY-MM-DD
decision: <summary>
rationale: <why>
options_considered: []
status: pending_outcome
---
-->
```

- [ ] **Step 4: Create `memory/skill-performance.md`**

```markdown
# Skill Performance Log

Written by: measure. Read by: report, decide, evolve-self.

---
date: 2026-01-01
feature: example-feature
tasks_completed: 5
velocity_tasks_per_week: 5
qa_pass_rate: 0.9
review_iterations: 2
time_per_feature_hours: 8
blockers: 0
blocker_age_days_avg: 0
example: true
---
```

- [ ] **Step 5: Create `memory/patterns.md`**

```markdown
# Patterns Log

Written by: learn (auto, qa_pass_rate >= 0.9 AND review_iterations <= 2).

<!-- Format:
---
date: YYYY-MM-DD
pattern: <specific description>
context: <task/feature type>
qa_pass_rate: 0.0
review_iterations: 0
---
-->
```

- [ ] **Step 6: Create `memory/mistakes.md`**

```markdown
# Mistakes Log

Written by: learn (auto, qa_pass_rate < 0.6 OR review_iterations > 4).

<!-- Format:
---
date: YYYY-MM-DD
mistake: <what went wrong>
root_cause: <why>
fix_applied: <resolution or "unresolved">
qa_pass_rate: 0.0
review_iterations: 0
---
-->
```

- [ ] **Step 7: Create `memory/feedback.md`**

```markdown
# User Feedback Log

WRITE-RESTRICTED: only learn skill (feedback path) may write here.
evolve-self reads this but never auto-PRs from it without user gate.

<!-- Format:
---
date: YYYY-MM-DD
feedback: <verbatim user input>
context: <what was happening>
contributed_upstream: false
---
-->
```

- [ ] **Step 8: Create `memory/research-findings.md`**

```markdown
# Research Findings Log

Written by: evolve-self via research subagent.

<!-- Format:
---
date: YYYY-MM-DD
research_question: <question>
skill_target: skills/<name>/SKILL.md
finding: <actionable finding>
source: <URL, doc name, or "Context7: <topic>">
confidence: high | medium | low
applied: false
---
-->
```

- [ ] **Step 9: Create `memory/skill-gaps.md`**

```markdown
# Skill Gaps Log

Written by: learn. evolve-self generates new skills when occurrences >= 3.

<!-- Format:
---
id: gap-YYYY-MM-DD-<slug>
pattern: <unhandled pattern description>
first_seen: YYYY-MM-DD
last_seen: YYYY-MM-DD
occurrences: 1
status: open | generating | generated
generated_skill: ""
---
-->
```

- [ ] **Step 10: Create `memory/evolution-log.md`**

```markdown
# Local Evolution Log

Written by: evolve-self (local changes only).
Root EVOLUTION-LOG.md tracks upstream-merged changes.

<!-- Format:
---
date: YYYY-MM-DD
mode: improve | generate | no-op
skill: <skill name>
trigger: <what triggered this>
change_summary: <one sentence>
---
-->
```

- [ ] **Step 11: Create `memory/pending-upstream/.gitkeep`** — empty file

- [ ] **Step 12: Create `memory/pending-upstream/last-pr.txt`**

```
1970-01-01T00:00:00Z
```

- [ ] **Step 13: Create `memory/connectors/README.md`**

```markdown
# Connector Interface

Activate a connector by setting `active: true` in the connector file.
Remove or set `active: false` to deactivate. No code changes needed.

## Supported Connectors

| File | Integration | Skills that use it |
|---|---|---|
| `github.md` | GitHub Issues and PRs | orchestrate, evolve-self |
| `slack.md` | Slack webhook notifications | report, evolve-self |
| `linear.md` | Linear issue tracking | orchestrate, report |

## Connector File Format

```yaml
---
connector: <name>
active: true
---
## Config
mcp_server: <mcp server registered in Claude Code>
default_repo: owner/repo      # github only
webhook_url: ""               # slack only
workspace_id: ""              # linear only
## State
last_sync: YYYY-MM-DD
```

## skill-pattern-manifest.md

Auto-maintained by `evolve-self`. Maps skill names to pattern keywords
used by `learn` for gap detection. Do not edit manually.
```

- [ ] **Step 14: Create `memory/connectors/skill-pattern-manifest.md`**

```markdown
---
last_updated: 2026-03-18
---
## Skills

### orchestrate
keywords: [feature goal, build, start work, implement feature, create feature, dependency, task cycle, kick off, begin work on]

### measure
keywords: [cycle complete, metrics, velocity, qa pass, review iterations, task done, finished feature, completed sprint]

### report
keywords: [report, dashboard, weekly summary, status update, management report, show progress, what got done, delivery summary]

### decide
keywords: [decision, prioritise, prioritize, which option, trade-off, should we, a or b, what should we focus, rank options, recommend]

### learn
keywords: [learned, pattern, mistake, feedback, wrong, worked well, did not work, retrospective, what went wrong, improvement]

### evolve-self
keywords: [evolve, improve plugin, generate skill, self-improve, /evolve, plugin update, new skill, skill gap, auto-improve]
```

- [ ] **Step 15: Create `memory/connectors/github.md`**

```markdown
---
connector: github
active: false
---
## Config
mcp_server: github
default_repo: owner/repo
## State
last_sync: 1970-01-01
```

- [ ] **Step 16: Create `memory/connectors/slack.md`**

```markdown
---
connector: slack
active: false
---
## Config
mcp_server: ""
webhook_url: ""
## State
last_sync: 1970-01-01
```

- [ ] **Step 17: Create `memory/connectors/linear.md`**

```markdown
---
connector: linear
active: false
---
## Config
mcp_server: linear
workspace_id: ""
## State
last_sync: 1970-01-01
```

- [ ] **Step 18: Run tests**

```bash
python -m pytest tests/test_memory.py -v
```
Expected: PASS (all)

- [ ] **Step 19: Commit**

```bash
git add memory/ tests/test_memory.py
git commit -m "feat: memory system — all pre-seeded files with schemas and initial state"
```

---

## Chunk 4: Core Skills — orchestrate, measure, report, decide

**Files:** `skills/orchestrate/SKILL.md`, `skills/measure/SKILL.md`, `skills/report/SKILL.md`, `skills/decide/SKILL.md`

### Task 4: Skill validation test

- [ ] **Step 1: Create `tests/test_skills.py`**

```python
import os, pytest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(PLUGIN_ROOT, "skills")

ALL_SKILLS = ["orchestrate", "measure", "report", "decide", "learn", "evolve-self"]
REQUIRED_FIELDS = ["name:", "description:", "version:", "triggers:", "reads:", "writes:", "generated:"]

@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_skill_exists(skill):
    assert os.path.exists(os.path.join(SKILLS_DIR, skill, "SKILL.md"))

@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_skill_frontmatter(skill):
    path = os.path.join(SKILLS_DIR, skill, "SKILL.md")
    if not os.path.exists(path): pytest.skip("missing")
    content = open(path).read()
    assert content.startswith("---"), f"{skill}: must start with frontmatter"
    for f in REQUIRED_FIELDS:
        assert f in content, f"{skill}: missing '{f}'"

def test_evolve_self_has_research_template():
    assert os.path.exists(os.path.join(SKILLS_DIR, "evolve-self", "research-subagent-prompt.md"))

def test_evolve_self_has_pr_template():
    assert os.path.exists(os.path.join(SKILLS_DIR, "evolve-self", "pr-template.md"))
```

- [ ] **Step 2: Run — verify fails**

```bash
python -m pytest tests/test_skills.py -v
```

### Task 5: Create `skills/orchestrate/SKILL.md`

- [ ] **Step 3: Write the file**

```markdown
---
name: orchestrate
description: Use when the user states a high-level feature goal — "Build X", "Start work on Y", "Implement Z". Breaks the goal into Superpowers-compatible task cycles, tracks cross-feature dependencies, and manages what gets built next.
version: 1.0.0
triggers:
  - User says "build", "implement", "start work on", "create feature", or names a new feature goal
  - User asks what to work on next given blockers or priorities
reads:
  - memory/project-context.md
  - memory/patterns.md
  - memory/connectors/github.md
  - memory/connectors/linear.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# Orchestrate

Break high-level feature goals into Superpowers-compatible task cycles and manage cross-feature priorities.

## Role

You are the **feature-level orchestration layer** above Superpowers. Superpowers handles the code execution cycle (TDD → implement → review). Your job is to decide *what* gets built and *in what order*.

## Process

### 1. Read Current State

Read `memory/project-context.md`:
- Active features and their statuses
- Open blockers and their ages
- Recent decisions

If GitHub connector is active (`memory/connectors/github.md` has `active: true`): read open Issues to augment the feature list.
If Linear connector is active: read open Linear issues.

### 2. Classify the Request

**Starting a new feature** → break it down:
```
Feature: <name>
Subtasks:
  1. <specific task> → Superpowers cycle
  2. <specific task> → Superpowers cycle
Dependencies: <list>
Estimated cycles: <n>
```

**Deciding what to work on next** → apply priority order:
1. Unblock blocked features first (if the fix is small)
2. Continue in-progress features (avoid context switching)
3. Start highest-ROI new feature

### 3. Invoke Superpowers

For each task cycle, hand off to Superpowers:
- Planning: trigger `superpowers:writing-plans`
- Execution: trigger `superpowers:subagent-driven-development`

Do not reimplement Superpowers. Hand off cleanly.

### 4. Update Memory

Append to `memory/project-context.md` `## Active Features`:
```
- YYYY-MM-DD: <feature name> [status: active]
```

If blockers exist, append to `## Blockers`:
```
- YYYY-MM-DD: <description> | age_days: 0 | recommended_fix: <text>
```

### 5. Connector Actions

If GitHub connector is active: comment on the relevant Issue with the task breakdown.
If Linear connector is active: update issue status to "In Progress".

### 6. Cycle Outcome Handoff

When a cycle completes, construct this object and hand it to `measure`:

```yaml
feature: <feature name>
tasks_completed: <n>
qa_pass_rate: <0.0-1.0>
review_iterations: <n>
time_hours: <n>
blockers_encountered: <n>
patterns_used: []
unhandled_patterns: []
```

Fill `patterns_used` with keyword matches from `memory/connectors/skill-pattern-manifest.md`.
Fill `unhandled_patterns` with patterns that arose but no manifest keyword covers.

## Rules

- Never reimplement Superpowers — invoke it, don't replace it
- Always update project-context.md before ending the session
- One feature at a time unless user explicitly requests parallel work
```

### Task 6: Create `skills/measure/SKILL.md`

- [ ] **Step 4: Write the file**

```markdown
---
name: measure
description: Use after every completed Superpowers cycle to record metrics. Captures velocity, QA pass rate, review iterations, and blockers. Always hand off to learn after recording.
version: 1.0.0
triggers:
  - A Superpowers cycle has just completed
  - User says "cycle done", "feature finished", "tasks completed"
  - orchestrate passes a cycle outcome object
reads:
  - memory/project-context.md
writes:
  - memory/skill-performance.md
  - memory/project-context.md
generated: false
generated_from: ""
---

# Measure

Record quantitative data after every Superpowers cycle.

## Input

Receive cycle outcome (from `orchestrate` or user):

```yaml
feature: <name>
tasks_completed: <n>
qa_pass_rate: <0.0-1.0>
review_iterations: <n>
time_hours: <n>
blockers_encountered: <n>
patterns_used: []
unhandled_patterns: []
```

If any field is missing, ask for it before recording.

## Process

### 1. Calculate Velocity

```
velocity_tasks_per_week = (tasks_completed / time_hours) * 40
```
Round to 1 decimal.

### 2. Append Entry to skill-performance.md

```yaml
---
date: YYYY-MM-DD
feature: <value>
tasks_completed: <value>
velocity_tasks_per_week: <calculated>
qa_pass_rate: <value>
review_iterations: <value>
time_per_feature_hours: <value>
blockers: <value>
blocker_age_days_avg: 0
---
```

### 3. Increment Counter in project-context.md

Read the frontmatter of `memory/project-context.md` (the block between the first `---` and second `---`). Find `total_tasks_completed:` and add `tasks_completed` to it. Rewrite the frontmatter block only — do not touch the rest of the file.

### 4. Hand Off to learn

Pass the same cycle outcome object to `learn` immediately after recording.

### 5. Check Evolution Threshold

After `learn` completes: compare `total_tasks_completed` to `last_evolved_at_task + evolve_every_n_tasks` in project-context.md frontmatter. If threshold reached, notify the user: *"Evolution check threshold reached — run /evolve when ready."*

## Rules

- Always record even for failed/partial cycles (qa_pass_rate reflects reality)
- Append only — never modify existing entries
- Always hand off to `learn`
```

### Task 7: Create `skills/report/SKILL.md`

- [ ] **Step 5: Write the file**

```markdown
---
name: report
description: Use to generate productivity reports and refresh the HTML dashboard. Run with /report or /report weekly. Reads all memory files, produces a markdown weekly summary and a self-contained HTML dashboard.
version: 1.0.0
triggers:
  - User runs /report
  - User asks for weekly summary, status update, management report, or dashboard refresh
reads:
  - memory/skill-performance.md
  - memory/project-context.md
  - memory/patterns.md
  - memory/mistakes.md
  - memory/connectors/slack.md
  - memory/connectors/linear.md
writes:
  - reports/weekly-YYYY-MM-DD.md
  - reports/dashboard.html
generated: false
generated_from: ""
---

# Report

Generate the weekly markdown report and regenerate the HTML dashboard.

## Data Sources

Read these files (skip entries with `example: true`):
- `memory/skill-performance.md` — metrics per cycle
- `memory/project-context.md` — Active Features, Blockers, Decisions Log
- `memory/patterns.md` — top 3 patterns (most recent)
- `memory/mistakes.md` — top 3 mistakes (most recent)

If Linear connector is active: include Linear cycle data in the summary.

## Computed Stats (from skill-performance.md, excluding example entries)

- Total features delivered
- Average QA pass rate (mean of qa_pass_rate values)
- Average velocity (mean of velocity_tasks_per_week)
- Average review iterations
- Active blockers (count from project-context.md Blockers section)
- Pending decisions (status: pending_outcome count)

## Output 1: Markdown Report

Write to `reports/weekly-YYYY-MM-DD.md`:

```markdown
# ProdMaster AI — Weekly Report
**Date:** YYYY-MM-DD

## Summary
- Features delivered: N
- Avg QA pass rate: N%
- Avg velocity: N tasks/week
- Avg review iterations: N
- Active blockers: N
- Pending decisions: N

## Features Delivered
<list from skill-performance.md this period>

## Active Blockers
<from project-context.md ## Blockers>

## Top Patterns
<top 3 from patterns.md>

## Recent Mistakes
<top 3 from mistakes.md>

## Decisions
<from project-context.md ## Decisions Log>
```

## Output 2: HTML Dashboard

Regenerate `reports/dashboard.html`. Requirements:
- Single self-contained file, no CDN, no external scripts or stylesheets
- Vanilla JS only — use `createElement` and `textContent` for all dynamic content (never `innerHTML` with unsanitised data)
- Opens by double-clicking — no server needed
- Four panels in 2x2 grid

**Panel data mapping:**

| Panel | Source | Key fields |
|---|---|---|
| Feature Velocity | skill-performance.md | velocity_tasks_per_week (sparkline of last 10), current value |
| QA Health | skill-performance.md | qa_pass_rate (donut), avg review_iterations |
| Active Blockers | project-context.md ## Blockers | text, age_days, recommended_fix |
| BA Decisions Log | project-context.md ## Decisions Log | decision text, status |

**DOM safety rule:** When rendering user data (feature names, blocker text, decision text), always use `textContent` or `createTextNode` — never string-interpolate into HTML markup. Build elements with `document.createElement` and set their `textContent`.

Embed all stats as a JSON object in a `<script>` tag with `type="application/json"` id `prodmaster-data`, then read it with `JSON.parse(document.getElementById('prodmaster-data').textContent)` on load.

## Slack (if connector active)

If `memory/connectors/slack.md` has `active: true` and non-empty `webhook_url`: post the Summary section of the markdown report to the webhook.

## Completion Message

Tell the user:
- *"Weekly report written to `reports/weekly-YYYY-MM-DD.md`"*
- *"Dashboard updated at `reports/dashboard.html` — double-click to open"*

## Rules

- Skip `example: true` entries in all calculations
- If no real data: generate report with zeros and note "No cycle data yet — run orchestrate and measure first"
- Never overwrite existing report files — create new dated files
```

### Task 8: Create `skills/decide/SKILL.md`

- [ ] **Step 6: Write the file**

```markdown
---
name: decide
description: Use when user is at a decision fork — "should we do A or B?", "what should we prioritise?", "which approach?". Reads project state and metrics to rank options by ROI/risk and give one clear recommendation.
version: 1.0.0
triggers:
  - User asks "should we", "which option", "prioritise", "help me decide", "recommend"
  - User presents two or more options and asks what to do
reads:
  - memory/project-context.md
  - memory/skill-performance.md
writes:
  - memory/project-context.md
generated: false
generated_from: ""
---

# Decide

Give data-backed recommendations at decision forks.

## Process

### 1. Read Context

- `memory/project-context.md` — active features, blockers, recent decisions
- `memory/skill-performance.md` — last 5 entries (skip `example: true`)

### 2. Get the Options

Ensure the user has stated all options clearly. You need: what each option achieves, constraints, dependencies.

### 3. Score Options

**ROI (1–5):** 5 = unblocks critical work or delivers clear user value. 1 = low value.
**Risk (1–5):** 1 = reversible, isolated. 5 = irreversible, high uncertainty.
**Priority = ROI / Risk** — higher is better.

Also factor in:
- Declining velocity trend → prefer lower-risk options
- Many open blockers → prefer options that unblock first
- Declining QA pass rate → prefer simpler options

### 4. Present Recommendation

```
## Decision: <short title>

**Recommendation: Option <X>**

| Option | ROI | Risk | Score |
|--------|-----|------|-------|
| A      |  4  |  2   | 2.0   |
| B      |  5  |  4   | 1.25  |

**Why Option X:** <2-3 sentences with data references>

**Trade-offs:**
- Pro: ...
- Con: ...

**Why not Option Y:** <1-2 sentences>
```

### 5. Log Decision

Append to `memory/project-context.md` `## Decisions Log`:

```yaml
---
date: YYYY-MM-DD
decision: <one sentence summary>
rationale: <reasoning>
options_considered: [A, B]
status: pending_outcome
---
```

Tell the user: *"Decision logged. When you see how it plays out, let me know and I'll update the status — this helps the system learn which decision patterns work."*

## Rules

- Give ONE clear recommendation — no hedging without a conclusion
- Use actual performance data when available; flag when there is none
- Log every decision, even simple ones
```

- [ ] **Step 7: Run skill tests for the four core skills**

```bash
python -m pytest tests/test_skills.py -v -k "orchestrate or measure or report or decide"
```
Expected: 8 tests pass

- [ ] **Step 8: Commit**

```bash
git add skills/orchestrate/ skills/measure/ skills/report/ skills/decide/ tests/test_skills.py
git commit -m "feat: core skills — orchestrate, measure, report, decide"
```

---

## Chunk 5: Skills — learn + evolve-self + templates

### Task 9: Create `skills/learn/SKILL.md`

- [ ] **Step 1: Write the file**

```markdown
---
name: learn
description: Use after each Superpowers cycle to capture patterns, mistakes, and skill gaps. Also use when user provides explicit feedback ("that was wrong", "that worked well", "remember this").
version: 1.0.0
triggers:
  - measure hands off a cycle outcome object
  - User gives explicit feedback about a workflow or decision
  - User says "log this pattern", "note this mistake", "remember that"
reads:
  - memory/connectors/skill-pattern-manifest.md
writes:
  - memory/patterns.md
  - memory/mistakes.md
  - memory/skill-gaps.md
  - memory/feedback.md
generated: false
generated_from: ""
---

# Learn

Capture patterns, mistakes, skill gaps, and user feedback from every cycle.

## Two Paths

Choose based on what triggered this skill.

---

## Auto Path (cycle outcome)

### Input

```yaml
feature: <name>
qa_pass_rate: <0.0-1.0>
review_iterations: <n>
patterns_used: [keywords]
unhandled_patterns: [keywords]
```

### Classify

- `qa_pass_rate >= 0.9` AND `review_iterations <= 2` → write to `patterns.md`
- `qa_pass_rate < 0.6` OR `review_iterations > 4` → write to `mistakes.md`
- Neither condition → no write to patterns or mistakes

### Write Pattern (if success)

```yaml
---
date: YYYY-MM-DD
pattern: <specific description of what worked — not just "it worked">
context: <task/feature type>
qa_pass_rate: <value>
review_iterations: <value>
---
```

### Write Mistake (if failure)

Analyse root cause:
- High `review_iterations` → usually unclear spec or over-built solution
- Low `qa_pass_rate` → usually insufficient upfront test coverage or wrong integration assumptions

```yaml
---
date: YYYY-MM-DD
mistake: <specific actionable description>
root_cause: <why it went wrong>
fix_applied: <resolution or "unresolved">
qa_pass_rate: <value>
review_iterations: <value>
---
```

### Detect Skill Gaps

Read `memory/connectors/skill-pattern-manifest.md`. Compare `unhandled_patterns` against all keyword lists using substring matching.

For each unhandled pattern:
1. Search `skill-gaps.md` for existing entry with matching pattern text
2. **Found:** increment `occurrences` by 1, update `last_seen` date
3. **Not found:** append new entry:

```yaml
---
id: gap-YYYY-MM-DD-<slugified-pattern-text>
pattern: <description>
first_seen: YYYY-MM-DD
last_seen: YYYY-MM-DD
occurrences: 1
status: open
generated_skill: ""
---
```

**Rule:** One increment per cycle per pattern — even if the pattern appeared multiple times within that cycle.

---

## Feedback Path (user input)

Write ONLY to `memory/feedback.md`:

```yaml
---
date: YYYY-MM-DD
feedback: <exact words the user used>
context: <what was happening — feature, decision, stage>
contributed_upstream: false
---
```

Tell the user: *"Logged. Run /evolve when you want to consider contributing this back to the plugin."*

**Strict rule:** Feedback path writes ONLY to feedback.md. Never to patterns.md or mistakes.md.

---

## Rules

- Auto path: one write per cycle, never double-count
- feedback.md is WRITE-RESTRICTED — only this skill (feedback path) may write to it
- Be specific in descriptions — "used small focused tasks with clear acceptance criteria" not just "good process"
- Skill gap IDs must be unique: `gap-<date>-<slug>`
```

### Task 10: Create `skills/evolve-self/SKILL.md`

- [ ] **Step 2: Write the file**

```markdown
---
name: evolve-self
description: Use when total_tasks_completed reaches a multiple of evolve_every_n_tasks (check project-context.md frontmatter), or when user runs /evolve. Improves underperforming skills, generates new skills from gaps, and contributes improvements upstream.
version: 1.0.0
triggers:
  - User runs /evolve
  - measure notifies that evolution threshold was reached
  - User asks the plugin to improve itself or generate new skills
reads:
  - memory/patterns.md
  - memory/mistakes.md
  - memory/feedback.md
  - memory/research-findings.md
  - memory/skill-performance.md
  - memory/skill-gaps.md
  - memory/project-context.md
  - memory/evolution-log.md
  - memory/connectors/skill-pattern-manifest.md
writes:
  - skills/*/SKILL.md
  - memory/research-findings.md
  - memory/evolution-log.md
  - memory/pending-upstream/
  - memory/pending-upstream/last-pr.txt
  - memory/connectors/skill-pattern-manifest.md
  - EVOLUTION-LOG.md
generated: false
generated_from: ""
---

# Evolve Self

Improve existing skills, generate new ones, and contribute changes upstream.

## Pre-flight

Read `memory/project-context.md` frontmatter. Update `last_evolved_at_task` to equal the current `total_tasks_completed`. This prevents repeated triggering.

---

## Mode 1 — Improve Existing Skills (runs first)

### 1. Identify Underperforming Skills

Read `memory/skill-performance.md`. A skill is underperforming if the last 3+ consecutive cycle entries show a declining `qa_pass_rate` trend (each lower than the previous).

Map cycle metrics to skills:
- High blockers → check `orchestrate`
- Low qa_pass_rate → check `learn` (capturing patterns?) and `orchestrate` (task breakdown quality?)
- High review_iterations → check the skills involved in that workflow

### 2. Research Better Approaches

For each underperforming skill, dispatch a research subagent using `skills/evolve-self/research-subagent-prompt.md`. Fill in:
- `{{skill_name}}` — skill to investigate
- `{{current_skill_content}}` — current SKILL.md content
- `{{performance_data}}` — last 5 skill-performance.md entries
- `{{research_question}}` — specific question about how to improve

The research subagent writes its finding to `memory/research-findings.md`.

### 3. Apply Improvements

For research-findings entries with `confidence: high` or `medium` and `applied: false`:
1. Read the target SKILL.md
2. Apply the finding — update the relevant sections
3. Preserve frontmatter schema; increment `version:` (1.0.0 → 1.1.0)
4. Set `applied: true` on the research-findings entry

Append to `memory/evolution-log.md`:
```yaml
---
date: YYYY-MM-DD
mode: improve
skill: <name>
trigger: declining qa_pass_rate + research: <source>
change_summary: <one sentence>
---
```

---

## Mode 2 — Generate New Skills (runs second)

### 1. Find Candidates

Read `memory/skill-gaps.md`. Collect entries where `occurrences >= 3` AND `status: open`.

### 2. Check Name Collision

Derive skill name: lowercase, hyphen-separated, 1-3 words from the gap pattern.
Check if `skills/<name>/SKILL.md` already exists.

- **Exists:** Set gap `status: generated`, `generated_skill: <existing name>`. Log warning. Move to next candidate.
- **Does not exist:** Proceed.

### 3. Create Skill File

Create `skills/<name>/SKILL.md` using the standard frontmatter schema:

```markdown
---
name: <derived-name>
description: <one-line trigger description from gap pattern>
version: 1.0.0
triggers:
  - <plain language condition matching the gap pattern>
reads:
  - memory/project-context.md
writes:
  - memory/project-context.md
generated: true
generated_from: <gap entry id>
---

# <Title Case Name>

<What this skill does — derived from the gap pattern>

## Process

<Draft specific steps. Follow the same structure as other skills.
Be actionable. Include what to read, what to write, what to output.>

## Rules

- Always update memory files after acting
- Document actions so they can be measured
- <Add 2-3 more rules specific to this skill's purpose>
```

### 4. Update Manifest

Append to `memory/connectors/skill-pattern-manifest.md`:
```markdown

### <skill-name>
keywords: [<5-10 keywords from the gap pattern>]
```

### 5. Update Gap Entry

Set `status: generating`. After file is written: `status: generated`, `generated_skill: <name>`.

Append to `memory/evolution-log.md`:
```yaml
---
date: YYYY-MM-DD
mode: generate
skill: <new skill name>
trigger: gap <id> reached 3+ occurrences
change_summary: New skill generated for: <gap pattern>
---
```

---

## No-Op Case

If neither mode produced output:
```yaml
---
date: YYYY-MM-DD
mode: no-op
skill: ""
trigger: scheduled evolution check
change_summary: No improvements or new skills needed at this time
---
```

Tell user: *"Evolution check ran — nothing needed at this time."*

---

## Upstream Pipeline (runs after any Mode 1 or Mode 2 output)

### 1. Rate Limit Check

Read `memory/pending-upstream/last-pr.txt`. Parse as ISO 8601 UTC. If fewer than 24 hours have elapsed: skip PR creation, queue proposal, tell user: *"Upstream proposal queued — rate limit active until [timestamp + 24h]."* Queue means the proposal file sits in pending-upstream/ with `status: pending`.

### 2. Package Proposal

For each changed/generated skill create `memory/pending-upstream/YYYY-MM-DD-<skill-name>-<mode>.md`:

```yaml
---
proposal_id: YYYY-MM-DD-<skill-name>-<mode>
type: skill_improvement | new_skill
source: outcome | research | feedback
target_skill: skills/<name>/SKILL.md
occurrence_count: <1 for Mode 1, gap occurrences for Mode 2>
created: YYYY-MM-DD
status: pending
pr_url: ""
---
## What Changed
<description>

## Why
<trigger and evidence>

## Evidence
<relevant entries from memory files>
```

### 3. Validate (no duplicates)

Check for duplicates in:
- All files in `memory/pending-upstream/` (any status)
- All existing `skills/` files
- `applied: true` entries in `memory/research-findings.md`

If duplicate: delete proposal, log, skip.

### 4. Create PR or Gate

**Source = outcome or research:** Create GitHub PR:
- Branch: `auto-evolved/YYYY-MM-DD-<skill-name>-<mode>` (suffix `-v2` if branch exists)
- Body: render `skills/evolve-self/pr-template.md`
- Label: `auto-evolved`
- Auth order: GitHub MCP → `gh` CLI → local-only fallback (log + notify)

Update `status: pr_created`, `pr_url: <url>`.
Write current UTC timestamp to `memory/pending-upstream/last-pr.txt`.

**Source = feedback:**
Ask: *"I've prepared an improvement based on your feedback about [topic]: [change_summary]. Contribute this back for all users?"*
- Yes → create PR as above
- No → set `status: rejected`, keep local changes

### 5. Check Pending PRs

On every run, check all `status: pr_created` proposals:
- Query GitHub API once per proposal
- Merged → `status: pr_merged`, append to root `EVOLUTION-LOG.md`:
  ```markdown
  ## YYYY-MM-DD — <change_summary>
  PR: <url> | Type: <type> | Trigger: <trigger>
  ```
- Closed without merge → `status: rejected`
- API unavailable → leave as `pr_created`, retry next run
- Older than 30 days → `status: rejected`, log "30-day timeout"

---

## Rules

- Mode 1 always before Mode 2
- Never delete existing skills upstream — additive only
- feedback.md is READ-ONLY for this skill — only read, never write
- Max 1 upstream PR per 24 hours
- PRs never self-merge
- Generated skills must use the full standard frontmatter schema
```

### Task 11: Create templates

- [ ] **Step 3: Create `skills/evolve-self/research-subagent-prompt.md`**

```markdown
# Research Subagent

You are a research subagent for the ProdMaster AI plugin. Investigate whether better approaches exist for the target skill and report your findings.

## Target Skill: {{skill_name}}

## Current Skill Content
{{current_skill_content}}

## Performance Data (last 5 cycles)
{{performance_data}}

## Research Question
{{research_question}}

## Instructions

1. If Context7 MCP is available, use it to pull current documentation related to the research question.
2. Search the project codebase for existing patterns that may already address this.
3. Analyse the performance data: what does it reveal about where this skill is failing?
4. Determine whether a concrete, actionable improvement exists.

## Output

Write a YAML entry to `memory/research-findings.md`:

```yaml
---
date: YYYY-MM-DD
research_question: <the question above>
skill_target: skills/{{skill_name}}/SKILL.md
finding: <specific actionable finding, or "No actionable improvement found">
source: <URL, doc name, "codebase analysis", or "Context7: <topic>">
confidence: high | medium | low
applied: false
---
```

Confidence:
- `high` — concrete improvement with clear implementation path and evidence
- `medium` — plausible improvement, some uncertainty
- `low` — speculative or not directly applicable

Return to evolve-self: "Finding written: [confidence] — [one-line summary]" or "No actionable improvement found for {{skill_name}}."
```

- [ ] **Step 4: Create `skills/evolve-self/pr-template.md`**

```markdown
## Summary

{{change_summary}}

## What Changed

{{what_changed}}

## Why

{{why}}

## Evidence

- **Type:** {{type}}
- **Source:** {{source}}
- **Occurrences:** {{occurrence_count}}

{{evidence}}

---

## Auto-generated by ProdMaster AI

Created by the `evolve-self` skill based on observed performance patterns or research findings. Not yet reviewed by a human.

If this looks correct, merge it. If not, close the PR — the plugin will treat it as rejected.

Label: `auto-evolved` | Proposal ID: `{{proposal_id}}`
```

- [ ] **Step 5: Run all skill tests**

```bash
python -m pytest tests/test_skills.py -v
```
Expected: PASS (all 14 tests)

- [ ] **Step 6: Commit**

```bash
git add skills/learn/ skills/evolve-self/ tests/test_skills.py
git commit -m "feat: learn and evolve-self skills with research and PR templates"
```

---

## Chunk 6: Dashboard HTML

**Files:** `reports/dashboard.html`, `reports/.gitkeep`

### Task 12: Self-contained HTML dashboard

DOM safety rule: all user-sourced data must use `textContent` or `createTextNode` — never string-interpolated into HTML markup.

- [ ] **Step 1: Create `reports/.gitkeep`** — empty file

- [ ] **Step 2: Create `reports/dashboard.html`**

Write a complete self-contained HTML file. All dynamic content uses safe DOM methods. Data is embedded as JSON in a `<script type="application/json">` tag.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ProdMaster AI Dashboard</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
       background: #0f172a; color: #e2e8f0; min-height: 100vh; }
header { background: #1e293b; border-bottom: 1px solid #334155;
         padding: .75rem 1.25rem; display: flex; justify-content: space-between; align-items: center; }
header h1 { font-size: 1.1rem; font-weight: 700; color: #f8fafc; }
.meta { font-size: .75rem; color: #94a3b8; }
.dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; padding: 1rem; }
@media(max-width:640px){ .dashboard { grid-template-columns: 1fr; } }
.panel { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 1.25rem; }
.panel-title { font-size: .65rem; font-weight: 700; text-transform: uppercase;
               letter-spacing: .1em; color: #64748b; margin-bottom: .75rem; }
.big-num { font-size: 2.25rem; font-weight: 800; color: #f8fafc; line-height: 1; }
.sub-label { font-size: .75rem; color: #94a3b8; margin-top: .2rem; }
.donut-row { display: flex; gap: 1.5rem; align-items: center; }
.donut-info .stat { margin-top: .4rem; font-size: .8rem; color: #94a3b8; }
.donut-info .stat b { color: #f8fafc; }
.badge { display: inline-block; padding: 1px 7px; border-radius: 9999px;
         font-size: .65rem; font-weight: 700; }
.g { background:#14532d; color:#86efac; }
.a { background:#78350f; color:#fcd34d; }
.r { background:#7f1d1d; color:#fca5a5; }
.row { padding: .5rem 0; border-bottom: 1px solid #0f172a;
       display: flex; justify-content: space-between; align-items: flex-start; gap: .5rem; }
.row:last-child { border-bottom: none; }
.row-text { font-size: .8rem; flex: 1; }
.row-fix { font-size: .7rem; color: #64748b; margin-top: 2px; }
.row-right { flex-shrink: 0; }
.empty { color: #475569; font-size: .8rem; font-style: italic; }
footer { text-align: center; padding: .75rem; color: #334155; font-size: .7rem; }
</style>
</head>
<body>

<header>
  <h1>&#9889; ProdMaster AI</h1>
  <div class="meta" id="gen-meta">Dashboard — no data yet</div>
</header>

<div class="dashboard">
  <div class="panel" id="panel-velocity">
    <div class="panel-title">Feature Velocity</div>
    <div class="big-num" id="vel-num">—</div>
    <div class="sub-label">tasks / week</div>
    <svg id="sparkline" width="100%" height="48" viewBox="0 0 260 48"
         style="margin-top:.75rem" aria-label="velocity sparkline"></svg>
  </div>
  <div class="panel" id="panel-qa">
    <div class="panel-title">QA Health</div>
    <div class="donut-row">
      <svg width="90" height="90" viewBox="0 0 90 90" aria-label="QA pass rate donut">
        <circle cx="45" cy="45" r="32" fill="none" stroke="#1e293b" stroke-width="12"/>
        <circle id="donut-arc" cx="45" cy="45" r="32" fill="none" stroke="#334155"
          stroke-width="12" stroke-dasharray="0 201" stroke-linecap="round"
          transform="rotate(-90 45 45)"/>
        <text id="donut-pct" x="45" y="50" text-anchor="middle"
          fill="#f8fafc" font-size="15" font-weight="800">—</text>
      </svg>
      <div class="donut-info">
        <div class="sub-label">avg pass rate</div>
        <div class="stat">Avg iterations: <b id="avg-iter">—</b></div>
        <div style="margin-top:.4rem" id="qa-badge"></div>
      </div>
    </div>
  </div>
  <div class="panel">
    <div class="panel-title">Active Blockers</div>
    <div id="blockers-list"><p class="empty">No active blockers.</p></div>
  </div>
  <div class="panel">
    <div class="panel-title">BA Decisions Log</div>
    <div id="decisions-list"><p class="empty">No decisions logged yet.</p></div>
  </div>
</div>

<footer>ProdMaster AI &mdash; run the <code>report</code> skill to refresh</footer>

<!-- Data injected by report skill. type=application/json prevents execution. -->
<script type="application/json" id="prodmaster-data">
{
  "generated": "",
  "velocity": [],
  "qaPassRates": [],
  "avgIterations": null,
  "blockers": [],
  "decisions": []
}
</script>

<script>
(function () {
  'use strict';

  // Safe: reads from <script type="application/json"> — not executable
  var raw = document.getElementById('prodmaster-data');
  var d = {};
  try { d = JSON.parse(raw.textContent); } catch (e) { d = {}; }

  // Header date — uses textContent only
  if (d.generated) {
    var dt = new Date(d.generated);
    var meta = document.getElementById('gen-meta');
    meta.textContent = 'Generated: ' + dt.toLocaleDateString('en-GB',
      {day:'numeric', month:'short', year:'numeric'});
  }

  // Panel 1: Velocity sparkline
  var vel = Array.isArray(d.velocity) ? d.velocity : [];
  if (vel.length > 0) {
    var cur = vel[vel.length - 1].value;
    document.getElementById('vel-num').textContent = Number(cur).toFixed(1);
    drawSparkline(vel.slice(-10).map(function(x){ return x.value; }));
  }

  // Panel 2: QA donut
  var qa = Array.isArray(d.qaPassRates) ? d.qaPassRates : [];
  if (qa.length > 0) {
    var avg = qa.reduce(function(a,b){return a+b;},0) / qa.length;
    var pct = Math.round(avg * 100);
    document.getElementById('donut-pct').textContent = pct + '%';
    var circ = 2 * Math.PI * 32; // r=32
    var arc = document.getElementById('donut-arc');
    arc.setAttribute('stroke-dasharray', (circ*avg).toFixed(2) + ' ' + (circ*(1-avg)).toFixed(2));
    var col = avg >= 0.8 ? '#22c55e' : avg >= 0.6 ? '#f59e0b' : '#ef4444';
    arc.setAttribute('stroke', col);
    var badge = document.createElement('span');
    badge.className = 'badge ' + (avg>=0.8?'g':avg>=0.6?'a':'r');
    badge.textContent = avg>=0.8 ? 'Healthy' : avg>=0.6 ? 'Watch' : 'Critical';
    document.getElementById('qa-badge').appendChild(badge);
  }
  if (d.avgIterations != null) {
    document.getElementById('avg-iter').textContent = Number(d.avgIterations).toFixed(1);
  }

  // Panel 3: Blockers — safe DOM construction
  var bl = Array.isArray(d.blockers) ? d.blockers : [];
  var bList = document.getElementById('blockers-list');
  if (bl.length > 0) {
    bList.textContent = '';
    bl.slice().sort(function(a,b){return b.age_days-a.age_days;}).forEach(function(b){
      var row = document.createElement('div');
      row.className = 'row';
      var left = document.createElement('div');
      left.className = 'row-text';
      var t = document.createElement('div');
      t.textContent = b.text || '';
      left.appendChild(t);
      if (b.recommended_fix) {
        var fix = document.createElement('div');
        fix.className = 'row-fix';
        fix.textContent = '\u2192 ' + b.recommended_fix;
        left.appendChild(fix);
      }
      var right = document.createElement('div');
      right.className = 'row-right';
      var ag = document.createElement('span');
      ag.className = 'badge ' + (b.age_days > 7 ? 'r' : 'a');
      ag.textContent = b.age_days + 'd';
      right.appendChild(ag);
      row.appendChild(left);
      row.appendChild(right);
      bList.appendChild(row);
    });
  }

  // Panel 4: Decisions — safe DOM construction
  var dec = Array.isArray(d.decisions) ? d.decisions : [];
  var dList = document.getElementById('decisions-list');
  if (dec.length > 0) {
    dList.textContent = '';
    dec.forEach(function(decision){
      var row = document.createElement('div');
      row.className = 'row';
      var txt = document.createElement('div');
      txt.className = 'row-text';
      txt.textContent = decision.text || '';
      var right = document.createElement('div');
      right.className = 'row-right';
      var badge = document.createElement('span');
      var s = decision.status || '';
      badge.className = 'badge ' + (s==='confirmed_good'?'g':s==='confirmed_bad'?'r':'a');
      badge.textContent = s==='confirmed_good' ? '\u2713 Good'
                        : s==='confirmed_bad'  ? '\u2717 Bad'
                        : '\u23f3 Pending';
      right.appendChild(badge);
      row.appendChild(txt);
      row.appendChild(right);
      dList.appendChild(row);
    });
  }

  // Sparkline using inline SVG polyline (values are numbers only — safe)
  function drawSparkline(values) {
    var svg = document.getElementById('sparkline');
    if (values.length < 2) return;
    var W = 260, H = 48, pad = 4;
    var mn = Math.min.apply(null, values);
    var mx = Math.max.apply(null, values);
    var rng = mx - mn || 1;
    var pts = values.map(function(v, i) {
      var x = pad + (i / (values.length - 1)) * (W - 2*pad);
      var y = H - pad - ((v - mn) / rng) * (H - 2*pad);
      return x.toFixed(1) + ',' + y.toFixed(1);
    }).join(' ');
    // Use setAttribute with safe numeric strings — no user text involved
    var line = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    line.setAttribute('points', pts);
    line.setAttribute('fill', 'none');
    line.setAttribute('stroke', '#3b82f6');
    line.setAttribute('stroke-width', '2');
    line.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(line);
    var lastPt = pts.split(' ').pop().split(',');
    var dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    dot.setAttribute('cx', lastPt[0]);
    dot.setAttribute('cy', lastPt[1]);
    dot.setAttribute('r', '3');
    dot.setAttribute('fill', '#60a5fa');
    svg.appendChild(dot);
  }
}());
</script>
</body>
</html>
```

- [ ] **Step 3: Run scaffold tests including dashboard**

```bash
python -m pytest tests/test_scaffold.py -v
```
Expected: PASS (all 6 tests)

- [ ] **Step 4: Commit**

```bash
git add reports/ tests/test_scaffold.py
git commit -m "feat: self-contained HTML dashboard — vanilla JS, DOM-safe, 4 panels"
```

---

## Chunk 7: Docs + README

### Task 13: Create `docs/README.md`

- [ ] **Step 1: Write docs/README.md**

```markdown
# ProdMaster AI

A Claude Code plugin that sits above Superpowers to orchestrate features, measure productivity, support decisions, and **evolve itself** over time.

## Installation

### Manual (local development)

```bash
git clone <this-repo> ~/.claude/plugins/prodmaster-ai
```

Then in Claude Code:
```
/plugin install --local ~/.claude/plugins/prodmaster-ai
```

### Platform Hook Setup

**Windows:** works out of the box (uses `run-hook.cmd` + PowerShell).

**macOS/Linux:** Edit `hooks/hooks.json` and change the command to:
```json
"command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.sh\" session-start"
```

## Skills

| Skill | Trigger | Job |
|---|---|---|
| `orchestrate` | "Build X" / feature goal | Break into task cycles, track dependencies |
| `measure` | After each Superpowers cycle | Capture velocity, QA rate, blockers |
| `report` | `/report` | Markdown report + HTML dashboard |
| `decide` | At a decision fork | ROI-ranked recommendation |
| `learn` | After cycle or on feedback | Patterns, mistakes, gaps, feedback |
| `evolve-self` | Every N tasks or `/evolve` | Improve skills + generate new ones |

## Connectors

Edit `memory/connectors/<name>.md`, set `active: true`, fill in config. That's it.

| Connector | Integration |
|---|---|
| `github.md` | GitHub Issues/PRs |
| `slack.md` | Slack webhook |
| `linear.md` | Linear issue tracking |

## Upstream Evolution

When `evolve-self` runs, set `upstream.repo` in `.claude-plugin/plugin.json` to your fork's `owner/repo` to enable auto-PRs.

- Outcome/research improvements → automatic PR
- Feedback improvements → asks you first

## Dashboard

After `/report`, open `reports/dashboard.html` in any browser. No server needed.

## Auto-Evolution Flow

```
Superpowers cycle completes
  orchestrate → measure → learn
  (every N tasks) → evolve-self
    Mode 1: improve underperforming skills
    Mode 2: generate skills for repeated gaps
    upstream PR pipeline
```
```

- [ ] **Step 2: Run full test suite**

```bash
python -m pytest tests/ -v
```
Expected: PASS (all tests)

- [ ] **Step 3: Commit**

```bash
git add docs/
git commit -m "docs: README with installation, skills reference, connector setup"
```

---

## Chunk 8: Integration Tests + Final Validation

### Task 14: Integration test suite

- [ ] **Step 1: Create `tests/test_integration.py`**

```python
"""Integration tests — validates complete plugin structure."""
import os, json, re, subprocess, pytest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_all_required_files_exist():
    required = [
        ".claude-plugin/plugin.json",
        "hooks/hooks.json", "hooks/run-hook.cmd", "hooks/run-hook.sh",
        "hooks/run-hook.ps1", "hooks/session-start.md",
        "skills/orchestrate/SKILL.md", "skills/measure/SKILL.md",
        "skills/report/SKILL.md", "skills/decide/SKILL.md",
        "skills/learn/SKILL.md", "skills/evolve-self/SKILL.md",
        "skills/evolve-self/research-subagent-prompt.md",
        "skills/evolve-self/pr-template.md",
        "memory/patterns.md", "memory/mistakes.md", "memory/feedback.md",
        "memory/research-findings.md", "memory/skill-performance.md",
        "memory/skill-gaps.md", "memory/project-context.md",
        "memory/evolution-log.md",
        "memory/pending-upstream/.gitkeep",
        "memory/pending-upstream/last-pr.txt",
        "memory/connectors/README.md",
        "memory/connectors/skill-pattern-manifest.md",
        "memory/connectors/github.md",
        "memory/connectors/slack.md",
        "memory/connectors/linear.md",
        "reports/dashboard.html", "reports/.gitkeep",
        "docs/README.md", "EVOLUTION-LOG.md",
    ]
    missing = [f for f in required
               if not os.path.exists(os.path.join(PLUGIN_ROOT, f))]
    assert not missing, "Missing files:\n" + "\n".join(missing)

def test_all_json_valid():
    for f in [".claude-plugin/plugin.json", "hooks/hooks.json"]:
        path = os.path.join(PLUGIN_ROOT, f)
        try:
            json.load(open(path))
        except json.JSONDecodeError as e:
            pytest.fail(f"{f} invalid JSON: {e}")

def test_all_skill_frontmatter():
    skills_dir = os.path.join(PLUGIN_ROOT, "skills")
    required = ["name:", "description:", "version:", "triggers:", "reads:", "writes:", "generated:"]
    failures = []
    for name in os.listdir(skills_dir):
        p = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.exists(p):
            failures.append(f"skills/{name}/SKILL.md missing"); continue
        c = open(p).read()
        if not c.startswith("---"):
            failures.append(f"skills/{name}/SKILL.md: no frontmatter"); continue
        for f in required:
            if f not in c:
                failures.append(f"skills/{name}/SKILL.md missing: {f}")
    assert not failures, "\n".join(failures)

def test_project_context_counters():
    c = open(os.path.join(PLUGIN_ROOT, "memory", "project-context.md")).read()
    for f in ["total_tasks_completed: 0", "last_evolved_at_task: 0", "evolve_every_n_tasks: 10"]:
        assert f in c, f"project-context.md missing: {f}"

def test_hook_output(tmp_path):
    hook = os.path.join(PLUGIN_ROOT, "hooks", "run-hook.sh")
    try:
        r = subprocess.run(["bash", hook, "session-start"],
            cwd=PLUGIN_ROOT, capture_output=True, text=True, timeout=15)
        assert r.returncode == 0, f"Hook failed: {r.stderr}"
        assert "ProdMaster AI" in r.stdout
        assert len(r.stdout.strip()) > 20
    except FileNotFoundError:
        pytest.skip("bash not available")

def test_dashboard_self_contained():
    c = open(os.path.join(PLUGIN_ROOT, "reports", "dashboard.html")).read()
    assert "<!DOCTYPE html>" in c
    external = re.findall(r'(?:src|href)=["\']https?://', c)
    assert not external, f"External resources: {external}"

def test_dashboard_has_json_data_tag():
    c = open(os.path.join(PLUGIN_ROOT, "reports", "dashboard.html")).read()
    assert 'id="prodmaster-data"' in c
    assert 'type="application/json"' in c

def test_connectors_inactive_by_default():
    for conn in ["github.md", "slack.md", "linear.md"]:
        c = open(os.path.join(PLUGIN_ROOT, "memory", "connectors", conn)).read()
        assert "active: false" in c

def test_manifest_covers_all_skills():
    manifest = open(os.path.join(PLUGIN_ROOT, "memory", "connectors",
                                  "skill-pattern-manifest.md")).read()
    skills_dir = os.path.join(PLUGIN_ROOT, "skills")
    missing = [s for s in os.listdir(skills_dir)
               if os.path.isdir(os.path.join(skills_dir, s))
               and f"### {s}" not in manifest]
    assert not missing, f"Manifest missing: {missing}"

def test_last_pr_timestamp():
    c = open(os.path.join(PLUGIN_ROOT, "memory", "pending-upstream",
                           "last-pr.txt")).read().strip()
    assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', c)
```

- [ ] **Step 2: Create `tests/validate_all.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== ProdMaster AI — Full Validation ==="
cd "${PLUGIN_ROOT}"

echo ""
echo "1. Python test suite..."
python -m pytest tests/ -v --tb=short

echo ""
echo "2. JSON validation..."
for f in ".claude-plugin/plugin.json" "hooks/hooks.json"; do
  python -c "import json; json.load(open('${f}')); print('   \u2713 ${f}')"
done

echo ""
echo "3. Hook runner..."
bash hooks/run-hook.sh session-start > /dev/null \
  && echo "   \u2713 run-hook.sh OK" \
  || echo "   \u2717 run-hook.sh FAILED"

echo ""
echo "4. File count..."
TOTAL=$(find . -not -path './.git/*' -type f | wc -l | tr -d ' ')
echo "   Total files: ${TOTAL}"

echo ""
echo "=== Done ==="
```

- [ ] **Step 3: Make validate script executable**

```bash
chmod +x tests/validate_all.sh
```

- [ ] **Step 4: Run integration tests**

```bash
python -m pytest tests/test_integration.py -v
```
Expected: PASS (all 10 tests)

- [ ] **Step 5: Run full suite**

```bash
python -m pytest tests/ -v
```
Expected: PASS (all tests)

- [ ] **Step 6: Run full validation**

```bash
bash tests/validate_all.sh
```
Expected: All green

- [ ] **Step 7: Final commit and tag**

```bash
git add tests/
git commit -m "feat: integration tests and full validation suite"
git tag v1.0.0 -m "ProdMaster AI v1.0.0 — initial release"
```

---

## Post-Implementation Review Loop

After all tasks pass:

1. **Open `reports/dashboard.html`** in a browser — verify 4 panels render, no console errors
2. **Read each SKILL.md in full** — are the instructions unambiguous? Would Claude follow them correctly?
3. **Run `bash tests/validate_all.sh`** — all green
4. **Review evolve-self skill** — walk through upstream pipeline steps and verify all edge cases are covered
5. **Check skill trigger descriptions** — are they distinctive enough not to conflict with Superpowers?
6. **Improve any vague sections** — rewrite if needed
7. **Run `python -m pytest tests/ -v`** — still all green after improvements
8. **Commit improvements** — `git commit -m "improve: skill clarity and edge case coverage after review"`
