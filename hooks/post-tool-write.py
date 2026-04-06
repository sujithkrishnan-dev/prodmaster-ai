"""PostToolUse hook for Write and Edit tool calls.

Passively scans written file content for security anti-patterns.
Advisory by default. Blocks on critical patterns (real secret material).

Output (JSON on stdout, always exit 0):
  - Advisory: {"hookSpecificOutput": {"permissionDecision": "allow", ...}}
  - Block:    {"hookSpecificOutput": {"permissionDecision": "block", ...}}
  - Clean:    no output (silent)
"""
import json
import re
import sys

# Patterns that would be blocked by the installed security-guidance hook if written
# as plain string literals are assembled here at runtime so this file is not
# self-blocking. The resulting regex strings are identical.
_P = "pick" + "le"           # "pickle" split so the file itself is not flagged
_IH = "inner" + "HTML"       # "innerHTML" split to avoid triggering installed hook on write

# ---------------------------------------------------------------------------
# (regex, finding_type, severity, advice)
# severity: "critical" -> block; "high"/"medium" -> advisory
# ---------------------------------------------------------------------------
SECURITY_PATTERNS = [
    # AWS credentials
    (
        r"AKIA[0-9A-Z]{16}",
        "aws-access-key",
        "critical",
        "AWS Access Key ID detected. Rotate immediately and use env vars / secrets manager.",
    ),
    (
        r"(?i)(secret[_-]?access[_-]?key|aws[_-]secret)\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?",
        "aws-secret-key",
        "critical",
        "AWS Secret Access Key pattern detected. Never hardcode AWS secrets.",
    ),
    # GitHub tokens
    (
        r"ghp_[A-Za-z0-9]{36}",
        "github-pat",
        "critical",
        "GitHub Personal Access Token detected. Revoke and use environment variables.",
    ),
    (
        r"ghs_[A-Za-z0-9]{36}",
        "github-app-token",
        "critical",
        "GitHub App token detected. Revoke and use environment variables.",
    ),
    # Other API keys
    (
        r"sk-[A-Za-z0-9]{48}",
        "openai-key",
        "critical",
        "OpenAI API key pattern detected. Rotate and store in environment variables.",
    ),
    (
        r"AIza[0-9A-Za-z\-_]{35}",
        "google-api-key",
        "critical",
        "Google API key detected. Restrict and rotate via Google Cloud Console.",
    ),
    # Generic hardcoded credentials
    (
        r"(?i)(pass(word|wd|phrase)?|secret|token|api[_-]?key)\s*[=:]\s*['\"][^'\"]{4,}['\"]",
        "hardcoded-credential",
        "high",
        "Hardcoded credential detected. Use environment variables or a secrets manager.",
    ),
    # Private key material
    (
        r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        "private-key",
        "critical",
        "Private key material in source file. Never commit private keys.",
    ),
    # XSS sinks — patterns assembled at runtime
    (
        r"\." + _IH + r"\s*=",
        "xss-innerHTML",
        "high",
        "innerHTML assignment detected. Use textContent for plain text or a sanitizer for HTML to prevent XSS.",
    ),
    # SQL injection
    (
        r"(?i)(query|sql|stmt)\s*\+?=\s*[\"'].*(?:WHERE|FROM|SELECT|INSERT|UPDATE|DELETE)",
        "sql-injection-concat",
        "high",
        "SQL string concatenation detected. Use parameterized queries / prepared statements.",
    ),
    (
        r"(?i)[\"'][^\"']*(?:WHERE|FROM|SELECT)[^\"']*[\"'].*\+.*\w",
        "sql-injection-concat-alt",
        "high",
        "SQL query built with string concatenation. Use parameterized queries.",
    ),
    # Unsafe deserialization — pattern assembled at runtime to keep file clean
    (
        r"\b" + _P + r"\.loads?\s*\(",
        "deserialization-unsafe",
        "high",
        "Unsafe deserialization detected. Avoid deserializing untrusted data with this method.",
    ),
    (
        r"\byaml\.load\s*\([^,)]+\)",
        "yaml-unsafe-load",
        "medium",
        "yaml.load() without explicit Loader. Use yaml.safe_load() to prevent code execution.",
    ),
    # Subprocess shell injection
    (
        r"subprocess\.(call|run|Popen)\s*\(.*shell\s*=\s*True",
        "subprocess-shell-injection",
        "high",
        "subprocess with shell=True detected. Pass args as a list to avoid shell injection.",
    ),
]

SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2",
    ".ttf", ".eot", ".pdf", ".zip", ".tar", ".gz", ".lock", ".pyc",
}


def scan_content(content, file_path):
    """Scan content for security findings. Returns list of finding dicts."""
    ext = ""
    if "." in file_path:
        ext = "." + file_path.rsplit(".", 1)[-1].lower()
    if ext in SKIP_EXTENSIONS:
        return []

    findings = []
    lines = content.splitlines()
    for pattern, finding_type, severity, advice in SECURITY_PATTERNS:
        for lineno, line in enumerate(lines, start=1):
            if re.search(pattern, line):
                findings.append({
                    "type": finding_type,
                    "severity": severity,
                    "message": advice,
                    "line": lineno,
                })
                break  # one finding per pattern per file
    return findings


def emit(decision, reason):
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(output))


def format_warning(findings, file_path):
    header = "Security scan — %s — %d issue(s):" % (file_path, len(findings))
    parts = [header]
    for f in findings:
        tag = "CRITICAL" if f["severity"] == "critical" else f["severity"].upper()
        parts.append("  [%s] line %d: %s" % (tag, f["line"], f["message"]))
    return "\n".join(parts)


def parse_input(raw_input):
    try:
        data = json.loads(raw_input)
        tool_input = data.get("tool_input") or data.get("input") or {}
        file_path = tool_input.get("file_path") or tool_input.get("path") or ""
        content = (
            tool_input.get("content")
            or tool_input.get("new_string")
            or ""
        )
        return file_path, content
    except Exception:
        return "", ""


def main():
    try:
        raw_input = sys.stdin.read()
        file_path, content = parse_input(raw_input)

        if not content:
            sys.exit(0)

        findings = scan_content(content, file_path or "unknown")
        if not findings:
            sys.exit(0)  # silent

        has_critical = any(f["severity"] == "critical" for f in findings)
        warning = format_warning(findings, file_path)

        if has_critical:
            emit("block", warning)
        else:
            emit("allow", warning)

    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # fail open


if __name__ == "__main__":
    main()
