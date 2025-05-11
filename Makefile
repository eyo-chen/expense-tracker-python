generate:
	docker-compose run --rm -T protoc

test:
	echo "Starting test environment..."
	docker-compose up -d mongodb-test
	sleep 5  # Wait for MongoDB to be ready
	PYTHONPATH=./src python -m pytest src/tests/
	docker-compose down mongodb-test

clean:
	docker-compose down -v mongodb-test
	rm -rf __pycache__ tests/__pycache__