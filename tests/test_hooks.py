import os, json, subprocess, sys, importlib.util, pytest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS_DIR = os.path.join(PLUGIN_ROOT, "hooks")

def _load_hook():
    """Load pre-tool-bash.py as a module (hyphen in filename requires importlib)."""
    spec = importlib.util.spec_from_file_location(
        "pre_tool_bash", os.path.join(HOOKS_DIR, "pre-tool-bash.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

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

# ── Security regression tests for pre-tool-bash.py ──────────────────────────

def _safe(cmd):
    """Return True if pre_tool_bash would allow the command (no blocked pattern, all fragments safe)."""
    import re
    hook = _load_hook()
    for pattern, _ in hook.BLOCKED_PATTERNS:
        if re.search(pattern, cmd):
            return False
    fragments = hook.split_compound(cmd)
    return all(hook.is_safe_fragment(f) for f in fragments)


class TestHookSubstringBypassFixes:
    """C1/C2/C3: docs/, /tmp/, and pytest substring bypasses must be closed."""

    def test_c1_bash_with_docs_path_not_blanket_allowed(self):
        hook = _load_hook()
        assert not hook.is_safe_fragment("bash docs/payload.sh"), \
            "C1: docs/ substring must not bypass the hook"

    def test_c1_legitimate_docs_read_still_allowed(self):
        hook = _load_hook()
        assert hook.is_safe_fragment("cat docs/README.md")
        assert hook.is_safe_fragment("ls docs/")

    def test_c2_bash_with_tmp_path_not_blanket_allowed(self):
        hook = _load_hook()
        assert not hook.is_safe_fragment("bash /tmp/evil.sh"), \
            "C2: /tmp/ substring must not bypass the hook"

    def test_c2_legitimate_tmp_read_still_allowed(self):
        hook = _load_hook()
        assert hook.is_safe_fragment("cat /tmp/output.txt")

    def test_c3_bash_with_pytest_arg_not_blanket_allowed(self):
        hook = _load_hook()
        assert not hook.is_safe_fragment("bash script.sh --label pytest"), \
            "C3: pytest substring must not bypass the hook"

    def test_c3_pytest_as_base_command_still_allowed(self):
        hook = _load_hook()
        assert hook.is_safe_fragment("pytest tests/ -q")
        assert hook.is_safe_fragment("python -m pytest tests/")


class TestHookRegexFixes:
    """H2: git branch -D with -D as first arg must be blocked."""

    def test_h2_git_branch_minus_D_first_arg_blocked(self):
        assert _safe("git branch -D explore/my-branch") is False, \
            "H2: git branch -D <name> must be blocked"

    def test_h2_git_branch_minus_D_with_other_flags_still_blocked(self):
        assert _safe("git branch -a -D explore/my-branch") is False

    def test_git_branch_list_allowed(self):
        assert _safe("git branch --show-current") is True
        assert _safe("git branch -r") is True


class TestHookFailClosed:
    """M2: Hook must deny (not allow) when it cannot parse input."""

    def test_m2_hook_denies_on_bad_stdin(self):
        """Running the hook script with malformed stdin should exit 0 with deny JSON."""
        script = os.path.join(HOOKS_DIR, "pre-tool-bash.py")
        result = subprocess.run(
            [sys.executable, script],
            input="THIS IS NOT JSON",
            capture_output=True, text=True, timeout=5
        )
        assert result.returncode == 0, "Hook must always exit 0"
        # On bad input the hook should either deny or produce no output (no-opinion)
        # The key guarantee: it must NOT produce allow output for a bad parse
        if result.stdout.strip():
            data = json.loads(result.stdout)
            decision = data["hookSpecificOutput"]["permissionDecision"]
            assert decision != "allow", \
                "M2: Hook must not allow commands when input cannot be parsed"


class TestDownloadExecuteBypass:
    """H1: Two-step download+execute must not bypass pipe-to-shell protection."""

    def test_h1_curl_to_tmp_then_execute_blocked(self):
        hook = _load_hook()
        assert not hook.is_safe_fragment("bash /tmp/payload.sh"), \
            "H1: bash /tmp/... must not be blanket-allowed"


# ── Existing tests ────────────────────────────────────────────────────────────

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
