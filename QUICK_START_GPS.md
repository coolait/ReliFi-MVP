# Quick Start: GPS + Google Maps (5 Minutes)

## ✅ What You Need

- [ ] Google account
- [ ] 5-10 minutes
- [ ] Credit card (for Google Cloud - won't be charged, $200 free/month)

---

## Step-by-Step Setup

### 1. Get Google Maps API Key (3 minutes)

**Open**: https://console.cloud.google.com/google/maps-apis

**Do**:
1. Click "Select a project" → "New Project"
2. Name: "ReliFi App" → Click "Create"
3. Click "Go to APIs & Services"
4. Click "Library" (left sidebar)
5. Search and enable these 3 APIs:
   - ✅ **Maps JavaScript API**
   - ✅ **Geocoding API**
   - ✅ **Geolocation API**
6. Click "Credentials" (left sidebar)
7. Click "Create Credentials" → "API Key"
8. Copy the API key

### 2. Restrict API Key (1 minute)

**Still in Google Cloud Console**:

1. Click on your API key name
2. Under "Application restrictions":
   - Select: ☑️ HTTP referrers (web sites)
   - Add referrer: `http://localhost:3000/*`
   - Add referrer: `http://localhost:*`
3. Under "API restrictions":
   - Select: ☑️ Restrict key
   - Check: Maps JavaScript API
   - Check: Geocoding API
   - Check: Geolocation API
4. Click "Save"

### 3. Add Key to Your App (30 seconds)

**Edit** `client/.env`:

```bash
# Find this line:
REACT_APP_GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY_HERE

# Replace with your actual key:
REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSy...actual_key_here
```

### 4. Restart Your App (30 seconds)

```bash
# Stop React if running (Ctrl+C)

# Start React
cd client
npm start
```

---

## ✅ Test It Works

### Test 1: GPS Detection

1. Open http://localhost:3000
2. See blue banner: "Get more accurate earnings predictions"
3. Click **"Use My Location"**
4. Browser asks permission → Click **"Allow"**
5. Location updates with your coordinates
6. ✅ Success: `San Francisco (37.7749, -122.4194)`

### Test 2: Map Picker

1. Click **"Choose on Map"** button
2. Google Maps modal opens
3. Click anywhere on map
4. Marker moves, city name updates
5. Click **"Confirm Location"**
6. ✅ Success: Location updated

### Test 3: API Calls

1. Open browser DevTools (F12)
2. Go to Network tab
3. Click any time slot in calendar
4. Find request: `/api/earnings/lightweight`
5. Check Query Params
6. ✅ Success: See `lat` and `lng` parameters

---

## 🐛 Troubleshooting

### "Google Maps API key not configured"

**Fix**:
```bash
# Check file exists
cat client/.env | grep GOOGLE_MAPS_API_KEY

# Should show:
REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSy...

# If shows: YOUR_GOOGLE_MAPS_API_KEY_HERE
# → Replace with your actual key
```

### "This page can't load Google Maps correctly"

**Fix**:
1. Go to Google Cloud Console
2. Click on your API key
3. Check "Application restrictions" includes `localhost`
4. Check "API restrictions" has all 3 APIs enabled
5. Wait 1-2 minutes for restrictions to propagate
6. Refresh browser

### GPS Permission Denied

**Fix**:
1. Clear browser permissions: Settings → Privacy → Site Settings → Location
2. Or just use "Choose on Map" or quick-select city buttons

---

## 📚 Full Documentation

- **Setup Guide**: [GOOGLE_MAPS_GPS_SETUP.md](GOOGLE_MAPS_GPS_SETUP.md)
- **Feature Summary**: [GPS_FEATURE_SUMMARY.md](GPS_FEATURE_SUMMARY.md)
- **Performance**: [LIGHTWEIGHT_ENDPOINT_GUIDE.md](LIGHTWEIGHT_ENDPOINT_GUIDE.md)

---

## ✅ Done!

Your app now has:
- ✅ GPS location detection
- ✅ Google Maps picker
- ✅ Coordinate-based predictions
- ✅ Smart caching

**Enjoy precise, location-based earnings predictions!** 🎉
