generate:
	docker-compose run --rm -T protoc

test:
	./tools/tests/run_tests.sh $(TEST_FILE)