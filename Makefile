.PHONY: test_schema_py

test_schema_py:
	python3 tests/schemas/test_python.py
	set -e; \
	for f in schemas/*; \
		do jsonschema validate $$f tests/schemas/`basename $$f .json`_python.json --trace; \
	done
