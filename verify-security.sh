#!/bin/bash

# Security Verification Script
# Run this to verify your API keys are protected

echo ""
echo "🔒 Security Verification Check"
echo "=============================="
echo ""

PASS=0
FAIL=0

# Check 1: .env not tracked by git
echo "📋 Check 1: .env not tracked by git"
if git ls-files | grep -q "^client/\.env$"; then
    echo "   ❌ FAIL: client/.env is tracked by git (INSECURE!)"
    echo "   Fix: git rm --cached client/.env"
    FAIL=$((FAIL + 1))
else
    echo "   ✅ PASS: client/.env is not tracked"
    PASS=$((PASS + 1))
fi
echo ""

# Check 2: .env exists locally
echo "📋 Check 2: .env exists locally"
if [ -f "client/.env" ]; then
    echo "   ✅ PASS: client/.env exists locally"
    PASS=$((PASS + 1))
else
    echo "   ⚠️  WARNING: client/.env missing"
    echo "   Fix: cp client/.env.example client/.env"
fi
echo ""

# Check 3: .env.example is tracked
echo "📋 Check 3: .env.example is tracked"
if git ls-files | grep -q "client/\.env\.example"; then
    echo "   ✅ PASS: client/.env.example is tracked"
    PASS=$((PASS + 1))
else
    echo "   ⚠️  WARNING: client/.env.example not tracked"
    echo "   Fix: git add -f client/.env.example"
fi
echo ""

# Check 4: .gitignore includes .env
echo "📋 Check 4: .gitignore includes .env rules"
if [ -f ".gitignore" ] && grep -q "^\.env$" .gitignore && grep -q "^client/\.env$" .gitignore; then
    echo "   ✅ PASS: .gitignore includes .env files"
    PASS=$((PASS + 1))
else
    echo "   ❌ FAIL: .gitignore missing or incomplete"
    echo "   Fix: Add .env rules to .gitignore"
    FAIL=$((FAIL + 1))
fi
echo ""

# Check 5: API keys in .env
echo "📋 Check 5: API keys are configured"
if [ -f "client/.env" ]; then
    GOOGLE_KEY=$(grep "REACT_APP_GOOGLE_MAPS_API_KEY=" client/.env | cut -d '=' -f2)
    if [ "$GOOGLE_KEY" = "YOUR_GOOGLE_MAPS_API_KEY_HERE" ] || [ -z "$GOOGLE_KEY" ]; then
        echo "   ⚠️  WARNING: Google Maps API key not configured"
        echo "   Fix: Add your real API key to client/.env"
    else
        echo "   ✅ PASS: Google Maps API key is set"
        PASS=$((PASS + 1))
    fi
else
    echo "   ⚠️  WARNING: client/.env not found"
fi
echo ""

# Check 6: Git status clean of .env (except deletion)
echo "📋 Check 6: Git status doesn't show .env modifications"
ENV_STATUS=$(git status --porcelain | grep "client/\.env$")
if echo "$ENV_STATUS" | grep -q "^D "; then
    echo "   ✅ PASS: client/.env marked for deletion (correct)"
    PASS=$((PASS + 1))
elif echo "$ENV_STATUS" | grep -qE "^[MA] "; then
    echo "   ❌ FAIL: client/.env being added/modified (INSECURE!)"
    echo "   Fix: git rm --cached client/.env"
    FAIL=$((FAIL + 1))
elif [ -z "$ENV_STATUS" ]; then
    echo "   ✅ PASS: client/.env not in git status"
    PASS=$((PASS + 1))
else
    echo "   ⚠️  WARNING: Unexpected git status for .env"
fi
echo ""

# Summary
echo "=============================="
echo "📊 Summary"
echo "=============================="
echo "✅ Passed: $PASS checks"
if [ $FAIL -gt 0 ]; then
    echo "❌ Failed: $FAIL checks"
fi
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 All security checks passed!"
    echo ""
    echo "Next steps:"
    echo "1. Commit changes: git commit -m '🔒 Security: Protect API keys'"
    echo "2. Push to GitHub: git push"
    echo "3. Verify keys not visible in GitHub repo"
else
    echo "⚠️  Some security checks failed!"
    echo "Please fix the issues above before committing."
fi
echo ""
