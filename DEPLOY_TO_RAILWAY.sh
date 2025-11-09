#!/bin/bash
# Quick script to deploy updates to Railway

set -e

echo "🚀 Deploying updates to Railway..."
echo ""

# Check if we're in the right directory
if [ ! -d "scrapper" ]; then
    echo "❌ Error: scrapper directory not found"
    echo "Please run this script from the project root"
    exit 1
fi

# Check git status
echo "📋 Checking git status..."
git status --short

# Show what will be committed
echo ""
echo "📦 Files to commit:"
git status --short | grep -E "scrapper/(ticketmaster|improved_data|live_data|api_server)" || echo "No changes to main files"

# Ask for confirmation
echo ""
read -p "Do you want to commit and push these changes to Railway? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Add important files
echo "➕ Adding files..."
git add scrapper/ticketmaster_events_scraper.py
git add scrapper/improved_data_scraper.py
git add scrapper/live_data_scraper.py
git add scrapper/api_server.py

# Commit
echo "💾 Committing changes..."
git commit -m "Fix Ticketmaster API: Fetch all events with pagination, dynamic surge windows, fix Saturday-only issue

- Increased search radius from 10 to 25 miles
- Added pagination support to fetch all events
- Fixed date filtering to trust API date filtering
- Dynamic surge windows based on event capacity (1-3 hours)
- Fixed Saturday-only issue - windows now work on all days
- Added boost during event (not just before/after)
- Improved date parsing to handle multiple formats"

# Push
echo "🚀 Pushing to GitHub..."
git push origin avani4

echo ""
echo "✅ Changes pushed to GitHub!"
echo "🔄 Railway will automatically deploy the updates"
echo ""
echo "📊 Check deployment status at: https://railway.app"
echo ""

