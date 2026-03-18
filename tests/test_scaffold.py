import json, os, re, pytest

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
    assert data["upstream"]["repo"] == "sujithkrishnan-dev/prodmaster-ai"

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

def test_dashboard_no_external_resources():
    path = os.path.join(PLUGIN_ROOT, "reports", "dashboard.html")
    content = open(path).read()
    external = re.findall(r'(?:src|href)=["\']https?://', content)
    assert not external, f"External resources found: {external}"
