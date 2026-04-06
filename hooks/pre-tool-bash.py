"""PreToolUse hook for Bash commands.

Output format (JSON on stdout, always exit 0):
  - Allow:  {"hookSpecificOutput": {"permissionDecision": "allow", ...}}
  - Deny:   {"hookSpecificOutput": {"permissionDecision": "deny", ...}}
  - No opinion: no output (just exit 0)
"""
import json
import re
import sys

BLOCKED_PATTERNS = [
    (r"rm\s+-[a-zA-Z]*r", "recursive rm"),
    (r"rm\s+--recursive", "recursive rm (--recursive flag)"),
    (r"git\s+push\s.*--force", "force push"),
    (r"git\s+push\s.*\s-[a-zA-Z]*f", "force push"),
    (r"git\s+branch\b[^|;&]*-D\b", "force branch delete"),
    (r"git\s+reset\s.*--hard", "git reset --hard"),
    (r"git\s+clean\s.*-[a-zA-Z]*f", "git clean -f"),
    (r"git\s+(checkout|restore)\s+\.\s*($|[;&|])", "discard all changes"),
    (r"(?i)drop\s+(table|database|schema)", "DROP operation"),
    # Pipe-to-shell: fetching and executing remote code is never safe
    (r"(curl|wget)\s+.*\|\s*(bash|sh|zsh|fish|python3?|ruby|perl|node)", "pipe remote content to shell"),
    # eval with base64-decoded content — common obfuscation technique
    (r"eval\s+.*base64", "eval with encoded payload"),
    (r"base64\s+.*\|\s*(bash|sh|zsh|eval)", "base64 decode to shell"),
    # chmod 777 — world-writable permissions are almost never correct
    (r"chmod\s+777\b", "world-writable chmod 777"),
    # Package installs from unverified sources (git+http, direct http URLs)
    (r"pip\s+install\s+git\+http://", "pip install from unverified git+http source"),
    (r"npm\s+install\s+https?://", "npm install from direct HTTP URL"),
    # Secret key exports in shell — exporting AWS/GCP/private keys inline
    (r"export\s+AWS_SECRET_ACCESS_KEY\s*=\s*\S+", "AWS secret key export in shell"),
    (r"export\s+AWS_ACCESS_KEY_ID\s*=\s*AKIA\S+", "AWS access key export in shell"),
    (r"export\s+GOOGLE_APPLICATION_CREDENTIALS\s*=", "GCP credentials export in shell"),
    # PATH hijacking via /tmp prepend
    (r"export\s+PATH\s*=\s*/tmp[/:]", "PATH hijack via /tmp prepend"),
]

SAFE_COMMANDS = {
    "git",
    "python", "python3", "pip", "pip3", "pytest",
    "ls", "pwd", "which", "where", "file", "wc", "head", "tail",
    "cat", "less", "tree", "du", "df", "find",
    "mkdir", "touch", "cp", "mv", "chmod", "ln", "rm",
    "curl", "wget", "http", "gh",
    "ps", "lsof", "top", "htop", "kill", "pgrep", "pkill", "xargs",
    "node", "npm", "npx", "yarn", "pnpm", "bun",
    "echo", "printf", "date", "env", "export", "source", "type",
    "realpath", "dirname", "basename", "sort", "uniq", "tee",
    "diff", "jq", "sed", "awk", "grep", "rg", "sleep", "true",
    "false", "test", "read", "wait", "jobs", "fg", "bg", "nohup",
    "for", "while", "if", "do", "done", "then", "fi", "case", "esac",
}


def emit(decision, reason=""):
    """Print hook decision JSON to stdout."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def parse_command(raw_input):
    """Extract the command string from hook JSON input."""
    try:
        data = json.loads(raw_input)
        # Try both possible input key names
        tool_input = data.get("tool_input") or data.get("input") or {}
        return tool_input.get("command", "")
    except Exception:
        return ""


def split_compound(cmd):
    """Split a compound command into top-level shell fragments.

    Respects quoted strings, heredocs, and inline code so they aren't split.
    Only splits on &&, ;, |, and newlines that are OUTSIDE quotes/heredocs.
    """
    # First, collapse heredocs into the line that starts them.
    # This prevents heredoc body lines from being treated as commands.
    lines = cmd.split("\n")
    collapsed = []
    heredoc_delim = None
    heredoc_buf = []
    for line in lines:
        if heredoc_delim is not None:
            heredoc_buf.append(line)
            if line.strip() == heredoc_delim:
                # End of heredoc — append entire heredoc as one fragment
                collapsed[-1] += "\n" + "\n".join(heredoc_buf)
                heredoc_delim = None
                heredoc_buf = []
            continue
        # Check for heredoc start: << 'DELIM', << "DELIM", <<DELIM, <<-DELIM
        m = re.search(r"<<-?\s*['\"]?(\w+)['\"]?", line)
        if m:
            heredoc_delim = m.group(1)
            heredoc_buf = []
            collapsed.append(line)
        else:
            collapsed.append(line)
    # If heredoc wasn't closed, just append remaining
    if heredoc_buf:
        collapsed[-1] += "\n" + "\n".join(heredoc_buf)

    # Now split each collapsed line on &&, ;, | respecting quotes
    fragments = []
    for line in collapsed:
        current = []
        in_single = False
        in_double = False
        i = 0
        while i < len(line):
            c = line[i]
            if c == "'" and not in_double:
                in_single = not in_single
                current.append(c)
            elif c == '"' and not in_single:
                if i > 0 and line[i - 1] == "\\":
                    current.append(c)
                else:
                    in_double = not in_double
                    current.append(c)
            elif not in_single and not in_double:
                if c == "|":
                    fragments.append("".join(current))
                    current = []
                elif c == ";":
                    fragments.append("".join(current))
                    current = []
                elif c == "&" and i + 1 < len(line) and line[i + 1] == "&":
                    fragments.append("".join(current))
                    current = []
                    i += 1
                else:
                    current.append(c)
            else:
                current.append(c)
            i += 1
        if current:
            fragments.append("".join(current))
    return [f.strip() for f in fragments if f.strip()]


def get_base_command(fragment):
    """Extract the base command name from a fragment."""
    cleaned = re.sub(r"\d*>[>&]?\s*\S+", "", fragment)
    cleaned = re.sub(r"\s*&\s*$", "", cleaned)
    cleaned = cleaned.strip()
    if not cleaned:
        return ""
    first_word = cleaned.split()[0]
    return first_word.rsplit("/", 1)[-1]


def is_safe_fragment(fragment):
    """Check if a single command fragment is safe."""
    base = get_base_command(fragment)
    if not base:
        return True
    if base in SAFE_COMMANDS:
        return True
    stripped = fragment.strip()
    if stripped.startswith(".venv/bin/") or "/venv/bin/" in stripped:
        return True
    return False


def main():
    try:
        raw_input = sys.stdin.read()
        command = parse_command(raw_input)
        if not command:
            sys.exit(0)  # no opinion

        # Check blocked patterns first
        for pattern, label in BLOCKED_PATTERNS:
            if re.search(pattern, command):
                emit("deny", "%s is not allowed" % label)

        # Allow any python command early (before split_compound mangles -c strings)
        first_word = command.strip().split()[0] if command.strip() else ""
        base = first_word.rsplit("/", 1)[-1]
        if base in ("python", "python3", "pytest"):
            emit("allow", "python command")

        # Check all fragments are safe
        fragments = split_compound(command)
        if all(is_safe_fragment(f) for f in fragments):
            emit("allow", "safe development command")

        # Allow everything else that isn't explicitly blocked above
        emit("allow", "not a destructive command")
    except SystemExit:
        raise
    except Exception:
        emit("deny", "hook parse error — command blocked for safety")


if __name__ == "__main__":
    main()
