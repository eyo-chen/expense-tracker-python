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
    docker-compose down -v mongodb-test
    rm -rf __pycache__ tests/__pycache__
}

# Set trap to call cleanup on exit (success or failure)
trap cleanup EXIT

echo -e "${YELLOW}"
print_emoji_line "=>" "${YELLOW}"
echo -e "=> Starting test environment..."
print_emoji_line "=>" "${YELLOW}"
docker-compose up -d mongodb-test
uv run tools/tests/wait_for_mongo.py
PYTHONPATH=./src python -m pytest src/tests/
pytest_exit_code=$?
if [ $pytest_exit_code -eq 0 ]; then
    echo -e "${GREEN}🎉 Tests passed successfully!"
    exit 0
else
    echo -e "${RED}❌ Tests failed!"
    exit $pytest_exit_code
fi