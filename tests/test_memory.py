import os, re, pytest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_DIR = os.path.join(PLUGIN_ROOT, "memory")

REQUIRED_FILES = [
    "patterns.md", "mistakes.md", "feedback.md", "research-findings.md",
    "skill-performance.md", "skill-gaps.md", "project-context.md",
    "evolution-log.md",
    "pending-upstream/.gitkeep",
    "pending-upstream/last-pr.txt",
    "connectors/README.md",
    "connectors/skill-pattern-manifest.md",
    "connectors/github.md",
    "connectors/slack.md",
    "connectors/linear.md",
    "blocker-research.md",
    "autonomous-log.md",
]

@pytest.mark.parametrize("filename", REQUIRED_FILES)
def test_memory_file_exists(filename):
    assert os.path.exists(os.path.join(MEMORY_DIR, filename)), f"Missing: memory/{filename}"

def test_project_context_has_counters():
    content = open(os.path.join(MEMORY_DIR, "project-context.md")).read()
    for f in [
        "total_tasks_completed:", "last_evolved_at_task:", "evolve_every_n_tasks:",
        "autonomous_mode:", "autonomous_session_id:",
        "autonomous_max_iterations:", "autonomous_confidence_floor:",
    ]:
        assert f in content, f"Missing: {f}"

def test_skill_performance_has_example():
    assert "example: true" in open(os.path.join(MEMORY_DIR, "skill-performance.md")).read()

def test_connectors_all_inactive():
    for c in ["github.md", "slack.md", "linear.md"]:
        content = open(os.path.join(MEMORY_DIR, "connectors", c)).read()
        assert "active: false" in content, f"{c} must default to active: false"

def test_skill_pattern_manifest_has_all_skills():
    content = open(os.path.join(MEMORY_DIR, "connectors", "skill-pattern-manifest.md")).read()
    for skill in ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
                  "dev-loop", "research-resolve", "auto-pilot", "resume"]:
        assert f"### {skill}" in content

def test_last_pr_txt_valid_timestamp():
    content = open(os.path.join(MEMORY_DIR, "pending-upstream", "last-pr.txt")).read().strip()
    assert re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', content)
