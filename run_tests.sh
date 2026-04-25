#!/bin/bash
# run_tests.sh - Automated test runner with coverage for BetaTrax Sprint 3

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR/BetaTrax"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}BetaTrax Automated Test Runner${NC}"
echo -e "${BLUE}Sprint 3 - Testing & Coverage${NC}"
echo -e "${BLUE}================================${NC}\n"

# Change to project directory
cd "$PROJECT_DIR"

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: manage.py not found in $PROJECT_DIR${NC}"
    exit 1
fi

# Parse command line arguments
COVERAGE_MODE=false
HTML_REPORT=false
VERBOSE=1

for arg in "$@"; do
    case $arg in
        --coverage|-c)
            COVERAGE_MODE=true
            ;;
        --html)
            HTML_REPORT=true
            COVERAGE_MODE=true
            ;;
        --verbose|-v)
            VERBOSE=2
            ;;
        --help|-h)
            echo "Usage: ./run_tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --coverage, -c      Run tests with coverage measurement"
            echo "  --html              Generate HTML coverage report"
            echo "  --verbose, -v       Show verbose test output"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh                    # Run tests only"
            echo "  ./run_tests.sh --coverage         # Run with coverage"
            echo "  ./run_tests.sh --coverage --html  # Generate HTML report"
            exit 0
            ;;
    esac
done

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}\n"
fi

# Check Python and Django
echo -e "${YELLOW}Checking environment...${NC}"
python --version
python -c "import django; print('Django:', django.VERSION)"
python -c "import rest_framework; print('Django REST Framework installed')"

if [ "$COVERAGE_MODE" = true ]; then
    python -c "import coverage; print('coverage.py installed')"
fi
echo ""

# Run tests
if [ "$COVERAGE_MODE" = true ]; then
    echo -e "${YELLOW}Running tests with coverage...${NC}\n"
    coverage erase
    coverage run --source='.' manage.py test --verbosity=$VERBOSE
    
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}Coverage Report${NC}"
    echo -e "${BLUE}================================${NC}\n"
    coverage report
    
    # Generate missing lines report
    echo -e "\n${YELLOW}Detailed coverage with missing lines:${NC}\n"
    coverage report -m
    
    # Metrics.py specific coverage
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}Metrics Module Coverage (Critical)${NC}"
    echo -e "${BLUE}================================${NC}\n"
    coverage report -m defects/metrics.py || echo "Metrics module analysis completed"
    
    if [ "$HTML_REPORT" = true ]; then
        echo -e "\n${YELLOW}Generating HTML coverage report...${NC}"
        coverage html
        echo -e "${GREEN}✓ HTML report generated in htmlcov/index.html${NC}\n"
        
        # Try to open in browser
        if command -v open &> /dev/null; then
            open htmlcov/index.html
        elif command -v xdg-open &> /dev/null; then
            xdg-open htmlcov/index.html
        fi
    fi
else
    echo -e "${YELLOW}Running tests (without coverage)...${NC}\n"
    python manage.py test --verbosity=$VERBOSE
fi

echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}✓ Test run completed successfully${NC}"
echo -e "${GREEN}================================${NC}"

exit 0
