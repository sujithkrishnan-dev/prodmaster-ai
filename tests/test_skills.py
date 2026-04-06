import os, pytest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(PLUGIN_ROOT, "skills")

ALL_SKILLS = ["orchestrate", "measure", "report", "decide", "learn", "evolve-self",
              "dev-loop", "research-resolve", "auto-pilot", "resume", "checkpoint",
              "token-efficiency", "auto-pilot-revoke", "task-queue", "parallel-explore",
              "plugin-manager", "qa", "qa-only", "ship", "deploy", "benchmark",
              "codex", "document-release", "review", "skill-forge",
              "cso", "dependency-audit", "secret-scan"]

REQUIRED_FIELDS = ["name:", "description:", "version:", "triggers:", "reads:", "writes:",
                   "generated:", "generated_from:"]

@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_skill_exists(skill):
    assert os.path.exists(os.path.join(SKILLS_DIR, skill, "SKILL.md"))

@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_skill_frontmatter(skill):
    path = os.path.join(SKILLS_DIR, skill, "SKILL.md")
    if not os.path.exists(path): pytest.skip("missing")
    content = open(path, encoding='utf-8').read()
    assert content.startswith("---"), f"{skill}: must start with frontmatter"
    for f in REQUIRED_FIELDS:
        assert f in content, f"{skill}: missing '{f}'"

def test_evolve_self_has_research_template():
    assert os.path.exists(os.path.join(SKILLS_DIR, "evolve-self", "research-subagent-prompt.md"))

def test_evolve_self_has_pr_template():
    assert os.path.exists(os.path.join(SKILLS_DIR, "evolve-self", "pr-template.md"))
