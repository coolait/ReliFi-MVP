#!/bin/bash

# Google Maps API Key Setup Script
# This script helps you add your Google Maps API key to .env

echo "=================================================="
echo "   Google Maps API Key Setup for ReliFi"
echo "=================================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Make sure you're in the client directory:"
    echo "  cd /Users/abansal/github/Untitled/ReliFi-MVP/client"
    exit 1
fi

# Check current API key
current_key=$(grep "REACT_APP_GOOGLE_MAPS_API_KEY=" .env | cut -d '=' -f2)

echo "📋 Current API key status:"
if [ "$current_key" == "YOUR_GOOGLE_MAPS_API_KEY_HERE" ]; then
    echo "   ❌ Not set (still showing placeholder)"
elif [ -z "$current_key" ]; then
    echo "   ❌ Empty (no key set)"
else
    # Show first 20 characters for privacy
    echo "   ✅ Set: ${current_key:0:20}..."
    echo ""
    read -p "Do you want to update it? (y/n): " update_choice
    if [ "$update_choice" != "y" ]; then
        echo "Exiting. No changes made."
        exit 0
    fi
fi

echo ""
echo "=================================================="
echo "   Step 1: Get Your Google Maps API Key"
echo "=================================================="
echo ""
echo "1. Open this URL in your browser:"
echo "   👉 https://console.cloud.google.com/google/maps-apis/credentials"
echo ""
echo "2. Create a project if you don't have one"
echo ""
echo "3. Enable these 3 APIs:"
echo "   • Maps JavaScript API"
echo "   • Geocoding API"
echo "   • Geolocation API"
echo ""
echo "4. Create API Key and copy it"
echo ""
echo "5. The key looks like: AIzaSyABC123def456..."
echo ""
echo "=================================================="
echo ""

# Ask for API key
read -p "Paste your Google Maps API key here: " api_key

# Validate input
if [ -z "$api_key" ]; then
    echo "❌ Error: No API key provided"
    exit 1
fi

if [ "$api_key" == "YOUR_GOOGLE_MAPS_API_KEY_HERE" ]; then
    echo "❌ Error: That's the placeholder, not your actual key!"
    exit 1
fi

if [[ ! "$api_key" =~ ^AIzaSy ]]; then
    echo "⚠️  Warning: API key doesn't start with 'AIzaSy'"
    echo "   Are you sure this is a valid Google Maps API key?"
    read -p "Continue anyway? (y/n): " continue_choice
    if [ "$continue_choice" != "y" ]; then
        echo "Exiting. No changes made."
        exit 0
    fi
fi

echo ""
echo "=================================================="
echo "   Step 2: Updating .env file"
echo "=================================================="
echo ""

# Backup .env
cp .env .env.backup
echo "✅ Created backup: .env.backup"

# Update .env file
if grep -q "REACT_APP_GOOGLE_MAPS_API_KEY=" .env; then
    # Replace existing line
    sed -i.tmp "s|REACT_APP_GOOGLE_MAPS_API_KEY=.*|REACT_APP_GOOGLE_MAPS_API_KEY=$api_key|" .env
    rm -f .env.tmp
    echo "✅ Updated API key in .env"
else
    # Add new line
    echo "REACT_APP_GOOGLE_MAPS_API_KEY=$api_key" >> .env
    echo "✅ Added API key to .env"
fi

# Verify
new_key=$(grep "REACT_APP_GOOGLE_MAPS_API_KEY=" .env | cut -d '=' -f2)
echo ""
echo "📋 New API key (first 20 chars): ${new_key:0:20}..."

echo ""
echo "=================================================="
echo "   Step 3: Test API Key"
echo "=================================================="
echo ""

echo "Testing API key with Google Geocoding API..."
response=$(curl -s "https://maps.googleapis.com/maps/api/geocode/json?latlng=37.7749,-122.4194&key=$api_key")

if echo "$response" | grep -q '"status" : "OK"'; then
    echo "✅ SUCCESS! Your API key works!"
    echo ""
    echo "Response:"
    echo "$response" | grep -o '"formatted_address" : "[^"]*"' | head -1
else
    echo "❌ API key test failed"
    echo ""
    echo "Response:"
    echo "$response" | grep -o '"status" : "[^"]*"'
    echo "$response" | grep -o '"error_message" : "[^"]*"'
    echo ""
    echo "Common issues:"
    echo "  • APIs not enabled (enable Maps JavaScript, Geocoding, Geolocation)"
    echo "  • Billing not enabled (required but $200 free/month)"
    echo "  • Key restrictions too strict (allow localhost)"
    echo "  • Key just created (wait 2-3 minutes)"
fi

echo ""
echo "=================================================="
echo "   Step 4: Restart React App"
echo "=================================================="
echo ""
echo "⚠️  IMPORTANT: You MUST restart React for changes to take effect!"
echo ""
echo "In your React terminal:"
echo "  1. Press Ctrl+C to stop"
echo "  2. Run: npm start"
echo ""
echo "Then test in browser:"
echo "  • Open: http://localhost:3000"
echo "  • Click: 'Choose on Map' button"
echo "  • Check console for: '✅ Google Maps API loaded successfully'"
echo ""
echo "=================================================="
echo ""

read -p "Press Enter to exit..."
