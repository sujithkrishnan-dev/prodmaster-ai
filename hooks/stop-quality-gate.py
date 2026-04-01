"""Stop hook — quality and security gate.

Fires on Claude stop events. Blocks session exit if:
  1. Critical secret leaks were detected by post-tool-write.py this session
  2. Critical CVEs were flagged by dependency-audit skill this session
  3. Tests are failing during an active ship/deploy cycle

State is written to memory/security-gate-state.json by skills/hooks.
If the state file does not exist, gate allows (clean state assumption).

Output (JSON on stdout, always exit 0):
  - Block: {"hookSpecificOutput": {"permissionDecision": "block", "permissionDecisionReason": "..."}}
  - Allow: no output (silent)
"""
import json
import os
import sys

DEFAULT_STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "memory",
    "security-gate-state.json",
)


def load_state(state_file):
    """Load gate state. Returns empty/clean state if file missing or unreadable."""
    if not os.path.exists(state_file):
        return {"secret_leaks": [], "critical_cves": [], "tests_failing": False}
    try:
        with open(state_file) as f:
            return json.load(f)
    except Exception:
        return {"secret_leaks": [], "critical_cves": [], "tests_failing": False}


def check_gate(state_file=None):
    """Evaluate gate conditions. Returns {"allow": bool, "reason": str}.

    Accepts optional state_file path for testability.
    """
    if state_file is None:
        state_file = DEFAULT_STATE_FILE

    state = load_state(state_file)

    critical_leaks = [
        leak for leak in state.get("secret_leaks", [])
        if leak.get("severity") == "critical"
    ]
    critical_cves = state.get("critical_cves", [])
    tests_failing = state.get("tests_failing", False)

    if critical_leaks:
        files = ", ".join(leak.get("file", "unknown") for leak in critical_leaks[:3])
        reason = (
            "Session blocked: %d critical secret leak(s) detected in %s. "
            "Rotate the exposed credentials before ending the session." % (len(critical_leaks), files)
        )
        return {"allow": False, "reason": reason}

    if critical_cves:
        cve_list = ", ".join(critical_cves[:5])
        reason = (
            "Session blocked: critical CVE(s) detected in dependencies: %s. "
            "Run /prodmasterai dependency-audit and apply fixes before ending the session." % cve_list
        )
        return {"allow": False, "reason": reason}

    if tests_failing:
        reason = (
            "Session blocked: tests are failing during an active ship/deploy cycle. "
            "Fix failing tests before ending the session."
        )
        return {"allow": False, "reason": reason}

    return {"allow": True, "reason": ""}


def emit_block(reason):
    output = {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "permissionDecision": "block",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(output))


def main():
    try:
        result = check_gate()
        if not result["allow"]:
            emit_block(result["reason"])
        # allow = silent (no output)
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # fail open — never crash-block a session


if __name__ == "__main__":
    main()
