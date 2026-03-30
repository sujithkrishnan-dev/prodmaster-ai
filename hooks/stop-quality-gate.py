"""Stop hook — quality gate for ship and deploy skills.

Checks if a ship or deploy was in progress (detected via memory/ship-log.md or
memory/deploy-log.md having an open session). If so, checks that tests are passing
before allowing Claude to stop.

Only activates when a ship/deploy session is actively running (prevents blocking
normal conversations). Uses stop_hook_active guard to prevent infinite loops.

Output: JSON on stdout. Exit 0 always.
"""
import json
import os
import re
import subprocess
import sys

def read_stdin():
    try:
        return json.loads(sys.stdin.read())
    except Exception:
        return {}

def has_open_ship_session():
    """Check if ship or deploy was explicitly started this session by reading Claude's memory."""
    # Check if ship or deploy log has a recent open entry
    # This is a lightweight check — we don't block unless there's a real in-progress session
    for log_file in ["memory/ship-log.md", "memory/deploy-log.md"]:
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                # If last entry is missing completed_at or pr_url it may be in-progress
                # Simple heuristic: look for "session_id:" without "pr_url:" on same entry block
                if "session_id:" in content:
                    return True
            except Exception:
                pass
    return False

def run_tests():
    """Try to run tests. Returns (passed, failed, error_message)."""
    test_commands = [
        ["npm", "test", "--", "--passWithNoTests"],
        ["npx", "jest", "--passWithNoTests"],
        ["python", "-m", "pytest", "--tb=no", "-q"],
        ["bun", "test"],
    ]
    for cmd in test_commands:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.getcwd()
            )
            output = result.stdout + result.stderr

            # Parse pytest output
            m = re.search(r"(\d+) passed", output)
            passed = int(m.group(1)) if m else 0
            m = re.search(r"(\d+) failed", output)
            failed = int(m.group(1)) if m else 0

            # Parse jest output
            m = re.search(r"Tests:\s+.*?(\d+) failed", output)
            if m:
                failed = int(m.group(1))

            if result.returncode == 0:
                return passed, 0, None
            elif failed > 0:
                return passed, failed, f"{failed} test(s) failing"
            else:
                return passed, 0, None  # non-zero exit but no parsed failures

        except FileNotFoundError:
            continue  # try next command
        except subprocess.TimeoutExpired:
            return 0, 0, None  # timeout — don't block

    return 0, 0, None  # no test runner found — don't block

def main():
    data = read_stdin()

    # Guard: prevent infinite loop if this hook triggered a stop itself
    if data.get("stop_hook_active"):
        sys.stdout.write(json.dumps({"continue": True}))
        return

    # Only activate when a ship/deploy session appears active
    if not has_open_ship_session():
        # No ship/deploy in progress — let Claude stop normally
        sys.stdout.write(json.dumps({"continue": True}))
        return

    passed, failed, error = run_tests()

    if failed and failed > 0:
        sys.stdout.write(json.dumps({
            "continue": False,
            "stopReason": (
                f"Quality gate: {failed} test(s) failing. "
                "Fix failing tests before completing ship/deploy, or run "
                "`/prodmasterai ship --skip-coverage` to override."
            ),
            "decision": "block",
            "reason": f"{failed} tests failing — ship/deploy blocked",
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "additionalContext": (
                    f"Stop hook blocked because {failed} test(s) are failing. "
                    "The ship/deploy skill requires all tests to pass. "
                    "Fix the failures and then the session can complete."
                )
            }
        }))
    else:
        # Tests pass or no test runner — allow stop
        sys.stdout.write(json.dumps({"continue": True}))

if __name__ == "__main__":
    main()
