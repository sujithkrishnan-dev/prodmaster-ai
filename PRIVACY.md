# Privacy Policy — ProdMaster AI

**Last updated:** 2026-04-28
**Plugin:** ProdMaster AI (prodmaster-ai)
**Author:** Sujith Krishnan, techjays
**Contact:** sujith.krishnan@techjays.com

---

## Summary

ProdMaster AI collects no personal data, sends no telemetry, and makes no outbound network calls by default. All state is stored locally on your machine.

---

## Data Collection

ProdMaster AI does **not** collect, transmit, or store any personal data. Specifically:

- No analytics or usage telemetry is sent to any server
- No crash reports are transmitted
- No user identifiers, session IDs, or device fingerprints are collected
- No data is sent to techjays or any third party

---

## Local State

The plugin stores operational state locally in the `memory/` directory inside your project. This includes:

- Usage logs (`memory/usage-log.md`) — invocation counts, processed locally only
- Skill performance metrics (`memory/skill-performance.md`) — velocity and QA data, local only
- Security gate state (`memory/security-gate-state.json`) — active session state, local only
- Connector configuration files — local only, most are git-ignored by default

None of these files leave your machine unless you explicitly commit and push them to a remote repository under your own control.

---

## Safety Hooks

The plugin installs four local hooks that run inside your Claude Code session:

- **SessionStart hook** — reads local memory files to inject context; no network calls
- **PreToolUse hook** — inspects Bash commands for dangerous patterns; runs locally in Python, no network calls
- **PostToolUse hook** — scans written file content for security anti-patterns; runs locally in Python, no network calls
- **Stop hook** — reads local security gate state to decide whether to block session exit; no network calls

All hooks run as local Python processes using the Python standard library only. No third-party packages are installed or called.

---

## Optional Connectors

ProdMaster AI supports optional integrations with external services. **All connectors are inactive by default** and require explicit opt-in by the user:

| Connector | External service | Activation required |
|---|---|---|
| GitHub | GitHub API via Claude Code MCP server | User must configure MCP server and set `active: true` |
| Slack | Slack webhook | User must provide webhook URL and set `active: true` |
| Linear | Linear API via Claude Code MCP server | User must configure MCP server and set `active: true` |

When a connector is activated, data flow is governed by the respective service's privacy policy (GitHub, Slack, Linear). ProdMaster AI itself does not proxy, store, or transmit connector data — it passes instructions to Claude Code's MCP layer, which the user has independently configured.

Credential files for Slack and Linear are listed in `.gitignore` and are not committed to the plugin repository.

---

## External Network Access by Skills

Some skills use Claude Code's built-in `WebSearch` or `WebFetch` tools to retrieve public information (e.g., CVE data from public package registries during a dependency audit). These calls:

- Are initiated by Claude Code, not by the plugin directly
- Require user approval per Claude Code's standard tool-use permission model
- Access only public, unauthenticated endpoints

No personal data is included in these requests.

---

## Children's Privacy

ProdMaster AI is a developer tool intended for use by software engineers and is not directed at children under 13. No data is knowingly collected from minors.

---

## Changes to This Policy

If this policy changes materially, the updated version will be committed to the plugin repository with an updated "Last updated" date. Users can review the history at any time via the repository's git log.

---

## Contact

For privacy questions or concerns:

**Email:** sujith.krishnan@techjays.com
**Repository:** https://github.com/sujithkrishnan-dev/prodmaster-ai
