#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== ProdMaster AI — Full Validation ==="
cd "${PLUGIN_ROOT}"

echo ""
echo "1. Python test suite..."
python -m pytest tests/ -v --tb=short

echo ""
echo "2. JSON validation..."
for f in ".claude-plugin/plugin.json" "hooks/hooks.json"; do
  python -c "import json; json.load(open('${f}')); print('   \u2713 ${f}')"
done

echo ""
echo "3. Hook runner..."
bash hooks/run-hook.sh session-start > /dev/null \
  && echo "   \u2713 run-hook.sh OK" \
  || echo "   \u2717 run-hook.sh FAILED"

echo ""
echo "4. File count..."
TOTAL=$(find . -not -path './.git/*' -type f | wc -l | tr -d ' ')
echo "   Total files: ${TOTAL}"

echo ""
echo "=== Done ==="
