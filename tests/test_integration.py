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
        "skills/auto-pilot/SKILL.md", "skills/resume/SKILL.md",
        "memory/autonomous-log.md",
        "skills/checkpoint/SKILL.md",
        "memory/checkpoint.md",
        "skills/token-efficiency/SKILL.md",
        "memory/token-efficiency-log.md",
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
    required = ["name:", "description:", "version:", "triggers:", "reads:", "writes:", "generated:", "generated_from:"]
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
    # Check field presence only — values change as cycles are logged
    for f in [
        "total_tasks_completed:", "last_evolved_at_task:", "evolve_every_n_tasks:",
        "autonomous_mode:", "autonomous_session_id:",
        "autonomous_max_iterations:", "autonomous_confidence_floor:",
    ]:
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
