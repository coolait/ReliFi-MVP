#!/bin/bash
# Test script to verify local API is using live data

echo "🧪 Testing Local API with Live Data"
echo "===================================="
echo ""

# Check if server is running
if ! curl -s http://localhost:5002/api/health > /dev/null 2>&1; then
    echo "❌ API server is not running!"
    echo "   Start it with: cd scrapper && source venv/bin/activate && python3 api_server.py"
    exit 1
fi

echo "✅ API server is running"
echo ""

# Test 1: Check health
echo "1️⃣  Testing health endpoint..."
curl -s http://localhost:5002/api/health | python3 -m json.tool
echo ""

# Test 2: Test earnings with live data
echo "2️⃣  Testing earnings endpoint with live APIs..."
echo "   Request: San Francisco, tomorrow at 6 PM"
echo ""

TOMORROW=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "+1 day" +%Y-%m-%d 2>/dev/null)
if [ -z "$TOMORROW" ]; then
    TOMORROW="2025-11-09"  # Fallback
fi

RESPONSE=$(curl -s "http://localhost:5002/api/earnings/lightweight?location=San%20Francisco&date=${TOMORROW}&startTime=6:00%20PM&endTime=7:00%20PM")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool

echo ""
echo "3️⃣  Checking metadata..."
METADATA=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data.get('metadata', {}), indent=2))" 2>/dev/null)

echo "$METADATA"

echo ""
echo "4️⃣  Verifying live data usage..."
USING_LIVE=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('metadata', {}).get('usingLiveData', False))" 2>/dev/null)

if [ "$USING_LIVE" = "True" ]; then
    echo "✅ Using live data!"
    DATA_SOURCES=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(', '.join(data.get('metadata', {}).get('dataSources', [])))" 2>/dev/null)
    echo "   Data sources: $DATA_SOURCES"
else
    echo "⚠️  Not using live data - check API keys in .env file"
fi

echo ""
echo "===================================="
echo "Done! Check the metadata field in the response above."

