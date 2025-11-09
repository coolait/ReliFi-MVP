#!/bin/bash
# Simple script to push changes and deploy to Railway

echo "🚀 Deploying to Railway..."
echo ""

# Check if we have uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes:"
    git status --short
    echo ""
    read -p "Do you want to commit these changes? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add -A
        git commit -m "Update: Ticketmaster API fixes and improvements"
    fi
fi

# Check if we're ahead of remote
AHEAD=$(git rev-list --count origin/avani4..HEAD 2>/dev/null || echo "0")

if [ "$AHEAD" -gt "0" ]; then
    echo "📤 You have $AHEAD commit(s) to push"
    echo ""
    echo "🚀 Pushing to GitHub..."
    git push origin avani4
    echo ""
    echo "✅ Pushed! Railway will automatically deploy."
else
    echo "✅ Your local branch is up to date with remote."
    echo ""
    echo "🔄 To trigger a redeploy in Railway:"
    echo "   1. Go to https://railway.app"
    echo "   2. Click on your project"
    echo "   3. Go to 'Deployments' tab"
    echo "   4. Click 'Redeploy'"
    echo ""
    echo "   OR create an empty commit:"
    echo "   git commit --allow-empty -m 'Trigger deployment' && git push origin avani4"
fi

echo ""
echo "📊 Check deployment at: https://railway.app"
echo ""

