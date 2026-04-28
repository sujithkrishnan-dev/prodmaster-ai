"""Shared utilities for ProdMaster AI hooks."""
import json
import sys


def emit(event_name, decision, reason=""):
    """Print hook decision JSON to stdout. Does NOT call sys.exit — caller decides."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(output))


def parse_tool_input(raw_stdin):
    """Extract tool_input dict from hook JSON stdin. Returns empty dict on failure."""
    try:
        data = json.loads(raw_stdin)
        return data.get("tool_input") or data.get("input") or {}
    except Exception:
        return {}
