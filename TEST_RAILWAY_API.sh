#!/bin/bash
# Test script for Railway API deployment

echo "🧪 Testing Railway API Deployment"
echo "=================================="
echo ""

# Get Railway URL from user
read -p "Enter your Railway URL (e.g., https://your-project.railway.app): " RAILWAY_URL

if [ -z "$RAILWAY_URL" ]; then
    echo "❌ Railway URL is required"
    exit 1
fi

# Remove trailing slash if present
RAILWAY_URL="${RAILWAY_URL%/}"

echo ""
echo "📡 Testing API endpoints..."
echo ""

# Test 1: Health endpoint
echo "1. Testing /api/health..."
HEALTH_RESPONSE=$(curl -s "${RAILWAY_URL}/api/health")
echo "   Response: $HEALTH_RESPONSE"
if echo "$HEALTH_RESPONSE" | grep -q "OK"; then
    echo "   ✅ Health check passed"
else
    echo "   ❌ Health check failed"
fi
echo ""

# Test 2: Earnings endpoint (lightweight)
echo "2. Testing /api/earnings/lightweight..."
LIGHTWEIGHT_RESPONSE=$(curl -s "${RAILWAY_URL}/api/earnings/lightweight?location=San%20Francisco&date=2025-11-09&startTime=9:00%20PM")
if echo "$LIGHTWEIGHT_RESPONSE" | grep -q "predictions"; then
    echo "   ✅ Lightweight endpoint working"
    echo "   Response preview: $(echo $LIGHTWEIGHT_RESPONSE | head -c 100)..."
else
    echo "   ❌ Lightweight endpoint failed"
    echo "   Response: $LIGHTWEIGHT_RESPONSE"
fi
echo ""

# Test 3: Full earnings endpoint with event boost
echo "3. Testing /api/earnings (with Ticketmaster events)..."
FULL_RESPONSE=$(curl -s "${RAILWAY_URL}/api/earnings?location=San%20Francisco&date=2025-11-09&startTime=9:00%20PM&lat=37.7749&lng=-122.4194")
if echo "$FULL_RESPONSE" | grep -q "eventBoost"; then
    echo "   ✅ Full earnings endpoint working"
    EVENT_BOOST=$(echo "$FULL_RESPONSE" | grep -o '"eventBoost":[0-9.]*' | head -1)
    echo "   Event boost: $EVENT_BOOST"
else
    echo "   ⚠️  Full earnings endpoint response (may take a few seconds)"
    echo "   Response preview: $(echo $FULL_RESPONSE | head -c 200)..."
fi
echo ""

echo "✅ Testing complete!"
echo ""
echo "📊 Check Railway logs for:"
echo "   - '✅ Ticketmaster API: X events found'"
echo "   - '📊 Events Summary for San Francisco'"
echo "   - '💰 Event boost impact'"
echo ""

