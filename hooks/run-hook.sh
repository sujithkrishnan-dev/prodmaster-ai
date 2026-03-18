#!/usr/bin/env bash
# ProdMaster AI — SessionStart hook runner (Unix/macOS/WSL)
# Reads memory files and outputs formatted context to stdout.
# Usage: run-hook.sh session-start

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MEMORY_DIR="${PLUGIN_ROOT}/memory"
TEMPLATE="${SCRIPT_DIR}/session-start.md"

if [[ ! -f "${TEMPLATE}" ]]; then
  printf '## ProdMaster AI\n*Memory not yet initialized.*\n'
  exit 0
fi

# Extract a named ## Section from a markdown file (up to next ## heading)
extract_section() {
  local file="$1" section="$2"
  if [[ ! -f "${file}" ]]; then printf '(none yet)'; return; fi
  local result
  result=$(awk "/^## ${section}/{found=1; next} found && /^## /{exit} found && /^[^<]/ && NF{print}" "${file}" \
    | grep -v '^<!--' | grep -v '^$' | head -5 || true)
  printf '%s' "${result:-"(none yet)"}"
}

# Extract last N lines matching a field prefix
extract_last_field() {
  local file="$1" field="$2" n="$3"
  if [[ ! -f "${file}" ]]; then printf '(none yet)'; return; fi
  local result
  result=$(grep "^${field}" "${file}" 2>/dev/null | tail -"${n}" \
    | sed "s/^${field}/- /" || true)
  printf '%s' "${result:-"(none yet)"}"
}

ACTIVE_FEATURES=$(extract_section "${MEMORY_DIR}/project-context.md" "Active Features")
TOP_PATTERNS=$(extract_last_field "${MEMORY_DIR}/patterns.md" "pattern: " 5)
OPEN_GAPS=$(grep -B2 "status: open" "${MEMORY_DIR}/skill-gaps.md" 2>/dev/null \
  | grep "^pattern:" | sed 's/^pattern: /- /' | head -5 || printf '(none yet)')
RECENT_EVOLUTIONS=$(extract_last_field "${MEMORY_DIR}/evolution-log.md" "change_summary: " 3)

OUTPUT=$(cat "${TEMPLATE}")
OUTPUT="${OUTPUT//\{\{active_features\}\}/${ACTIVE_FEATURES}}"
OUTPUT="${OUTPUT//\{\{top_patterns\}\}/${TOP_PATTERNS}}"
OUTPUT="${OUTPUT//\{\{open_gaps\}\}/${OPEN_GAPS}}"
OUTPUT="${OUTPUT//\{\{recent_evolutions\}\}/${RECENT_EVOLUTIONS}}"

printf '%s\n' "${OUTPUT}"
exit 0
