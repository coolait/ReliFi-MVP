# Google Maps API Troubleshooting Guide

## Error: "Failed to load Google Maps. Please check your API key configuration."

This error means the Google Maps API key is either missing, incorrect, or not properly configured.

---

## Step-by-Step Fix

### Step 1: Verify You Have an API Key

**Go to Google Cloud Console:**
https://console.cloud.google.com/google/maps-apis/credentials

**You should see:**
- A project name (e.g., "ReliFi App")
- API Keys section with at least one key
- Click on the key name to see/copy it

**If you don't see any API key:**
1. Click "Create Credentials" → "API Key"
2. Copy the key (it looks like: `AIzaSyABC123...`)

---

### Step 2: Add API Key to .env File

**Edit this file:**
```
client/.env
```

**Find line 15:**
```bash
REACT_APP_GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY_HERE
```

**Replace with your actual key:**
```bash
REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSyABC123...your_actual_key
```

**Important:**
- ❌ Don't leave quotes: `"AIzaSy..."` (WRONG)
- ❌ Don't add spaces: `AIzaSy ... ` (WRONG)
- ✅ Just the key: `AIzaSyABC123...` (CORRECT)

---

### Step 3: Verify .env File is Correct

**Run this command:**
```bash
cd /Users/abansal/github/Untitled/ReliFi-MVP/client
cat .env | grep GOOGLE_MAPS
```

**Should show:**
```bash
REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSyABC123...
```

**If it still shows `YOUR_GOOGLE_MAPS_API_KEY_HERE`:**
- You didn't save the file
- Or edited the wrong file
- Make sure you're editing `client/.env` (not `scrapper/.env.example`)

---

### Step 4: Restart React App

**This is CRITICAL!** React only reads `.env` on startup.

```bash
# Stop React (Ctrl+C in the terminal)

# Start React again
cd /Users/abansal/github/Untitled/ReliFi-MVP/client
npm start
```

**Wait for:** `webpack compiled successfully`

---

### Step 5: Test in Browser

1. Open http://localhost:3000
2. Open Browser Console (F12 or Cmd+Option+I)
3. Click "Choose on Map" button

**Check Console Messages:**

**✅ Success looks like:**
```
✅ Google Maps API loaded successfully
```

**❌ Error looks like:**
```
Google Maps JavaScript API error: InvalidKeyMapError
```

---

## Common Issues & Fixes

### Issue 1: "InvalidKeyMapError"

**Cause:** API key is wrong or restricted too much

**Fix:**
1. Go to Google Cloud Console
2. Click on your API key
3. Under "Application restrictions":
   - Select: "HTTP referrers (web sites)"
   - Add: `http://localhost:*`
   - Add: `http://localhost:3000/*`
4. Under "API restrictions":
   - Select: "Restrict key"
   - Make sure these are checked:
     - ✅ Maps JavaScript API
     - ✅ Geocoding API
     - ✅ Geolocation API
5. Click "Save"
6. **Wait 2-3 minutes** for changes to propagate
7. Refresh browser

---

### Issue 2: "This page can't load Google Maps correctly"

**Cause:** APIs not enabled

**Fix:**
1. Go to: https://console.cloud.google.com/apis/library
2. Search for each and click "Enable":
   - Maps JavaScript API
   - Geocoding API
   - Geolocation API
3. Wait 1-2 minutes
4. Refresh browser

---

### Issue 3: API Key Still Shows Placeholder

**Fix:**
```bash
# 1. Check which file you're editing
pwd
# Should show: /Users/abansal/github/Untitled/ReliFi-MVP/client

# 2. Edit the correct file
nano .env
# Or use your IDE: VSCode, etc.

# 3. Find line 15 and replace with your key
REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSy...your_actual_key

# 4. Save and exit (Ctrl+X, Y, Enter)

# 5. Verify it saved
cat .env | grep GOOGLE_MAPS

# 6. MUST restart React
npm start
```

---

### Issue 4: "Cannot find namespace 'google'"

**Fix:**
```bash
cd /Users/abansal/github/Untitled/ReliFi-MVP/client
npm install --save-dev @types/google.maps
npm start
```

This should already be installed, but run it if you see TypeScript errors.

---

## Quick Verification Checklist

Run these commands to verify everything:

```bash
cd /Users/abansal/github/Untitled/ReliFi-MVP/client

# 1. Check API key is set (not placeholder)
echo "Checking API key..."
cat .env | grep REACT_APP_GOOGLE_MAPS_API_KEY

# Should show: REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSy...
# Should NOT show: YOUR_GOOGLE_MAPS_API_KEY_HERE

# 2. Check types are installed
echo "Checking Google Maps types..."
cat package.json | grep "@types/google.maps"

# Should show: "@types/google.maps": "^3.58.1"

# 3. Check app is running
echo "Check if React is running..."
curl http://localhost:3000 > /dev/null 2>&1 && echo "✅ React is running" || echo "❌ React is not running"
```

---

## Visual Guide: Where to Get API Key

### Step-by-Step with Screenshots:

**1. Go to Google Cloud Console:**
```
https://console.cloud.google.com/google/maps-apis/credentials
```

**2. You'll see something like:**
```
┌─────────────────────────────────────────────────────┐
│ API Keys                                            │
├─────────────────────────────────────────────────────┤
│ Browser key (auto created by Google Maps)          │
│ AIzaSyABC123def456GHI789jkl012MNO345pqr678        │
│                                                     │
│ [Show key] [Restrict key] [Delete]                 │
└─────────────────────────────────────────────────────┘
```

**3. Click "Show key" or click the key name**

**4. Copy the ENTIRE key:**
```
AIzaSyABC123def456GHI789jkl012MNO345pqr678
```

**5. Paste into client/.env:**
```bash
REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSyABC123def456GHI789jkl012MNO345pqr678
```

---

## Test Command

Run this to test if your API key works:

```bash
# Replace YOUR_KEY_HERE with your actual key
curl "https://maps.googleapis.com/maps/api/geocode/json?latlng=37.7749,-122.4194&key=YOUR_KEY_HERE"
```

**Expected response:**
```json
{
  "results": [
    {
      "formatted_address": "San Francisco, CA, USA",
      ...
    }
  ],
  "status": "OK"
}
```

**Error response:**
```json
{
  "error_message": "The provided API key is invalid.",
  "status": "REQUEST_DENIED"
}
```

---

## Still Not Working?

### Check These:

1. **Billing enabled?**
   - Google Maps requires billing enabled (but $200 free/month)
   - Go to: https://console.cloud.google.com/billing
   - Make sure billing is enabled for your project

2. **Correct project selected?**
   - Top of Google Cloud Console shows project name
   - Make sure it's the same project where you created the API key

3. **API key recently created?**
   - Sometimes takes 2-3 minutes to activate
   - Wait a few minutes and try again

4. **Browser cache?**
   - Try hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Or open in incognito/private window

---

## Get Help

**If still stuck, run this and share the output:**

```bash
cd /Users/abansal/github/Untitled/ReliFi-MVP/client

echo "=== Environment Check ==="
cat .env | grep REACT_APP_GOOGLE_MAPS_API_KEY | sed 's/\(.\{20\}\).*/\1.../'
# This will show first 20 chars of your key (for privacy)

echo -e "\n=== Package Check ==="
cat package.json | grep "@types/google.maps"

echo -e "\n=== React Status ==="
curl -s http://localhost:3000 > /dev/null && echo "✅ Running" || echo "❌ Not running"

echo -e "\n=== Browser Console Errors ==="
echo "Open browser console (F12) and look for red errors"
```

---

## Summary

**Most Common Fix:**

1. Get API key from Google Cloud Console
2. Edit `client/.env` line 15
3. Replace `YOUR_GOOGLE_MAPS_API_KEY_HERE` with actual key
4. Save file
5. **Restart React app** (this is critical!)
6. Refresh browser

**90% of the time, the issue is:**
- ❌ API key not replaced (still shows placeholder)
- ❌ React app not restarted after editing .env
- ❌ Wrong file edited (editing scrapper/.env.example instead of client/.env)

**Fix:** Just follow the 6 steps above carefully!
