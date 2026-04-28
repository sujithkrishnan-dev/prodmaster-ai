.PHONY: all test lint validate-json

all: test lint validate-json

test:
	python -m pytest tests/ -v

lint:
	python -m py_compile hooks/pre-tool-bash.py hooks/post-tool-write.py hooks/stop-quality-gate.py && echo "Syntax OK"

validate-json:
	python -m json.tool .claude-plugin/plugin.json > /dev/null && \
	python -m json.tool .claude-plugin/marketplace.json > /dev/null && \
	python -m json.tool .claude-plugin/hooks.json > /dev/null && \
	python -m json.tool hooks/hooks.json > /dev/null && \
	echo "All JSON files are valid"
