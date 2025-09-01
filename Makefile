.PHONY: test_schema generate_ts_interfaces

test_schema: # Test that the python objects match with the JSONschema
	python3 tests/schemas/test_python.py
	set -e; \
	for f in schemas/*; \
		do jsonschema validate $$f tests/schemas/`basename $$f .json`_python.json --trace; \
	done

generate_ts_interfaces:
	cd control-panel/models && npm run schema
