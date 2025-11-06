#!/bin/bash
# Comprehensive test suite for Rideshare Data Scraper
# Run: ./run_tests.sh

echo "========================================"
echo "RIDESHARE SCRAPER TEST SUITE"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo "----------------------------------------"
    echo "TEST: $test_name"
    echo "----------------------------------------"

    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# Test 1: Python version
run_test "Python Version Check" "python3 --version | grep -E 'Python 3\.(10|11|12)'"

# Test 2: Virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
    if [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${YELLOW}○${NC} Activating virtual environment..."
        source venv/bin/activate
    fi
else
    echo -e "${YELLOW}○${NC} No virtual environment found (optional)"
fi
echo ""

# Test 3: Dependencies
run_test "Import Test" "python3 test_imports.py"

# Test 4: PostgreSQL
echo "----------------------------------------"
echo "TEST: PostgreSQL Status"
echo "----------------------------------------"
if command -v pg_isready &> /dev/null; then
    if pg_isready; then
        echo -e "${GREEN}✓ PostgreSQL is running${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ PostgreSQL is not running${NC}"
        echo "Start with: brew services start postgresql (macOS)"
        echo "         or: sudo systemctl start postgresql (Linux)"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${YELLOW}○ pg_isready not found, skipping${NC}"
fi
echo ""

# Test 5: Database exists
echo "----------------------------------------"
echo "TEST: Database Exists"
echo "----------------------------------------"
if psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw rideshare_data; then
    echo -e "${GREEN}✓ Database 'rideshare_data' exists${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}○ Database not found${NC}"
    echo "Create with: createdb rideshare_data"
fi
echo ""

# Test 6: Database connectivity
run_test "Database Connection" "python3 test_database.py"

# Test 7: API connectivity
run_test "API Connectivity" "python3 test_apis.py"

# Test 8: Individual scraper test
echo "----------------------------------------"
echo "TEST: Individual Scraper (NYC TLC)"
echo "----------------------------------------"
if python3 scrapers/nyc_tlc.py 2>&1 | grep -q "records"; then
    echo -e "${GREEN}✓ NYC TLC scraper works${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ NYC TLC scraper failed${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# Test 9: Integration test (if database is set up)
if psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw rideshare_data; then
    echo "----------------------------------------"
    echo "TEST: Integration Test"
    echo "----------------------------------------"
    echo "Running single scraper with database..."

    if python3 main.py --scrapers "NYC TLC" 2>&1 | grep -q "successful"; then
        echo -e "${GREEN}✓ Integration test passed${NC}"
        ((TESTS_PASSED++))

        # Check if data was inserted
        COUNT=$(psql rideshare_data -t -c "SELECT COUNT(*) FROM rideshare_stats;" 2>/dev/null | tr -d ' ')
        if [ "$COUNT" -gt 0 ]; then
            echo -e "${GREEN}✓ Data was inserted ($COUNT records)${NC}"
        fi
    else
        echo -e "${RED}✗ Integration test failed${NC}"
        ((TESTS_FAILED++))
    fi
    echo ""
fi

# Summary
echo "========================================"
echo "TEST SUMMARY"
echo "========================================"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo ""
    echo "Your system is ready to use!"
    echo ""
    echo "Next steps:"
    echo "  1. Run all scrapers: python3 main.py"
    echo "  2. Query data: python3 database/queries.py"
    echo "  3. Setup schedule: python3 main.py --schedule"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    echo "Review the errors above and:"
    echo "  1. Install missing dependencies: pip install -r requirements.txt"
    echo "  2. Setup database: createdb rideshare_data"
    echo "  3. Check PostgreSQL is running: pg_isready"
    echo "  4. See TESTING.md for detailed troubleshooting"
    exit 1
fi
