#!/bin/bash

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Function to print a line of repeated emojis
print_emoji_line() {
    local emoji=$1
    local color=$2
    local cols=$(tput cols) # Get terminal width
    local line=""

    # Calculate how many emojis fit in the terminal width (approximate, as emojis vary in width)
    for ((i=0; i<cols/2; i++)); do
        line="${line}${emoji}"
    done
    echo -e "${color}${line}"
}

# Function to clean up resources
cleanup() {
    echo -e "${BLUE}"
    print_emoji_line "<=" "${BLUE}"
    echo -e "<= Cleaning up resources..."
    print_emoji_line "<=" "${BLUE}"
    # Only stop MongoDB if it was started
    if [ "$MONGO_STARTED" = "true" ]; then
        docker-compose down -v mongodb-test
    fi
    rm -rf __pycache__ tests/__pycache__ coverage.out .coverage
    # Only remove coverage.xml if it exists
    [ -f coverage.xml ] && rm -f coverage.xml
}

# Set trap to call cleanup on exit (success or failure)
trap cleanup EXIT

# Check if a test file path is provided and if it contains "_adapters"
TEST_FILE=$1
MONGO_STARTED="false"

if [ -n "$TEST_FILE" ]; then
    echo -e "Running tests for: $TEST_FILE"
    TEST_PATH="$TEST_FILE"
    # Check if the test file contains "_adapters"
    if [[ "$TEST_FILE" == *"_adapters"* ]]; then
        echo -e "${YELLOW}"
        print_emoji_line "=>" "${YELLOW}"
        echo -e "=> Starting test environment with MongoDB..."
        print_emoji_line "=>" "${YELLOW}"
        docker-compose up -d mongodb-test
        uv run tools/tests/wait_for_mongo.py
        MONGO_STARTED="true"
    else
        echo -e "${YELLOW}"
        print_emoji_line "=>" "${YELLOW}"
        echo -e "=> Running tests without MongoDB..."
        print_emoji_line "=>" "${YELLOW}"
    fi
else
    echo -e "${YELLOW}"
    print_emoji_line "=>" "${YELLOW}"
    echo -e "=> Starting test environment with MongoDB for all tests..."
    print_emoji_line "=>" "${YELLOW}"
    docker-compose up -d mongodb-test
    uv run tools/tests/wait_for_mongo.py
    TEST_PATH="src/tests/"
    MONGO_STARTED="true"
fi

# Conditionally set coverage report options based on CI environment
if [ "$CI" = "true" ]; then
    cov_report="--cov-report=term-missing --cov-report=xml"
else
    cov_report="--cov-report=term-missing"
fi

# Run pytest with coverage
PYTHONPATH=./src uv run pytest "$TEST_PATH" --cov=src $cov_report -v
pytest_exit_code=$?
# Extract total coverage percentage
total_coverage=$(uv run coverage report | grep TOTAL | awk '{print $NF}' | sed 's/%//')
echo "Total Coverage: $total_coverage%"
echo "total_coverage=$total_coverage" >> $GITHUB_ENV

if [ $pytest_exit_code -eq 0 ]; then
    echo -e "${GREEN}🎉 Tests passed successfully!"
    exit 0
else
    echo -e "${RED}❌ Tests failed!"
    exit $pytest_exit_code
fi