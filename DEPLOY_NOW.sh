#!/bin/bash
# Quick deploy script for Railway

echo "🚀 Deploying to Railway..."
echo ""

# Check git status
echo "📋 Current git status:"
git status --short

echo ""
echo "📦 Checking for changes to deploy..."

# Check if key files have uncommitted changes
FILES_TO_CHECK=(
    "scrapper/ticketmaster_events_scraper.py"
    "scrapper/improved_data_scraper.py"
    "scrapper/live_data_scraper.py"
    "scrapper/api_server.py"
)

HAS_CHANGES=false
for file in "${FILES_TO_CHECK[@]}"; do
    if git diff --quiet "$file" 2>/dev/null; then
        echo "✅ $file - No changes"
    else
        echo "📝 $file - Has changes"
        HAS_CHANGES=true
    fi
done

echo ""

if [ "$HAS_CHANGES" = true ]; then
    echo "📝 Staging changes..."
    git add scrapper/ticketmaster_events_scraper.py
    git add scrapper/improved_data_scraper.py
    git add scrapper/live_data_scraper.py
    git add scrapper/api_server.py
    
    echo "💾 Committing changes..."
    git commit -m "Fix Ticketmaster API: Fetch all events, dynamic surge windows, fix Saturday-only issue

- Increased search radius from 10 to 25 miles
- Added pagination support to fetch all events
- Fixed date filtering to trust API date filtering
- Dynamic surge windows based on event capacity (1-3 hours)
- Fixed Saturday-only issue - windows now work on all days
- Added boost during event (not just before/after)
- Improved date parsing to handle multiple formats"
    
    echo "🚀 Pushing to GitHub..."
    git push origin avani4
    echo ""
    echo "✅ Changes pushed! Railway will automatically deploy."
else
    echo "✅ No changes to commit. Current code is already committed."
    echo ""
    echo "🔄 To trigger a redeploy:"
    echo "   1. Go to Railway Dashboard: https://railway.app"
    echo "   2. Click on your project"
    echo "   3. Go to 'Deployments' tab"
    echo "   4. Click 'Redeploy'"
    echo ""
    echo "   OR push an empty commit:"
    echo "   git commit --allow-empty -m 'Trigger Railway deployment'"
    echo "   git push origin avani4"
fi

echo ""
echo "📊 Check deployment status at: https://railway.app"
echo ""

