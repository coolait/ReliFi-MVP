#!/bin/bash
# Quick test script for localhost

echo "============================================================"
echo "Quick Test: Web Scraper on Localhost"
echo "============================================================"
echo ""

# Check if API is running
echo "1. Checking if API is running..."
if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo "   ✅ API is running"
else
    echo "   ❌ API is not running"
    echo ""
    echo "   Please start the API server:"
    echo "   cd scrapper"
    echo "   source venv/bin/activate"
    echo "   python3 api_server.py"
    echo ""
    exit 1
fi

echo ""
echo "2. Testing lightweight endpoint..."
response=$(curl -s "http://localhost:5001/api/earnings/lightweight?location=San%20Francisco&date=2025-11-09&startTime=6:00%20PM")

if [ $? -eq 0 ]; then
    echo "   ✅ Request successful"
    echo "$response" | python3 -m json.tool | head -20
else
    echo "   ❌ Request failed"
fi

echo ""
echo "============================================================"
echo "Test complete!"
echo "============================================================"
echo ""
echo "For more detailed testing, run:"
echo "  cd scrapper"
echo "  source venv/bin/activate"
echo "  python3 test_localhost.py"

