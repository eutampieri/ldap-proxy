.PHONY: test_schema generate_ts_interfaces docker docker_backend docker_frontend docker_merger

test_schema: # Test that the python objects match with the JSONschema
	python3 tests/schemas/test_python.py
	set -e; \
	for f in schemas/*; \
		do jsonschema validate $$f tests/schemas/`basename $$f .json`_python.json --trace; \
	done

generate_ts_interfaces:
	cd control-panel/models && npm i && npm run schema

docker: docker_backend docker_frontend docker_merger

docker_backend: generate_ts_interfaces
	docker build -t ghcr.io/eutampieri/ldap-proxy/backend -f control-panel/backend/Dockerfile .
docker_frontend:
	docker build -t ghcr.io/eutampieri/ldap-proxy/frontend -f control-panel/frontend/Dockerfile .
docker_merger:
	docker build -t ghcr.io/eutampieri/ldap-proxy/merger -f merger/Dockerfile merger
