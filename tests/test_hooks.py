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

def test_run_hook_ps1_exists():
    assert os.path.exists(os.path.join(HOOKS_DIR, "run-hook.ps1"))

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
        assert len(result.stdout.strip()) > 20
    except FileNotFoundError:
        pytest.skip("bash not available")
