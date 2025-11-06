# Quick Start Guide

Get the scraper-integrated Weekly Shift Recommendations running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Node.js 14+ installed
- Chrome browser installed (for Selenium)

## Installation

### 1. Install Python Dependencies

```bash
cd scrapper
pip install flask flask-cors requests beautifulsoup4 pandas selenium
```

### 2. Install ChromeDriver (for Selenium)

**macOS:**
```bash
brew install chromedriver
```

**Linux:**
```bash
sudo apt-get install chromium-chromedriver
```

**Windows:**
Download from https://chromedriver.chromium.org/ and add to PATH

### 3. Install Node.js Dependencies

```bash
# Server dependencies
cd server
npm install

# Client dependencies
cd ../client
npm install
```

## Running the Application

### Option 1: Manual (Recommended for Development)

Open 3 separate terminal windows:

**Terminal 1 - Python API:**
```bash
cd scrapper
python api_server.py
```

Wait for:
```
============================================================
Starting Earnings Forecaster API Server
============================================================
 * Running on http://0.0.0.0:5002
```

**Terminal 2 - Express Server:**
```bash
cd server
npm start
```

Wait for:
```
Server is running on port 5001
Python scraper API expected at: http://localhost:5002
```

**Terminal 3 - React Frontend:**
```bash
cd client
npm start
```

Wait for:
```
Compiled successfully!
Local: http://localhost:3000
```

### Option 2: Using a Startup Script

Create `start-all.sh` in the root directory:

```bash
#!/bin/bash
cd scrapper && python api_server.py &
sleep 3
cd ../server && npm start &
sleep 2
cd ../client && npm start &
wait
```

Make it executable and run:
```bash
chmod +x start-all.sh
./start-all.sh
```

## Testing the Integration

### 1. Open the Application

Visit: http://localhost:3000

### 2. Test Location Change

1. Click **"Change"** in the location input at the top
2. Select **"New York"** from the quick-select buttons
3. Open browser DevTools console (F12)
4. Look for: `📍 Location changed to: New York`

### 3. Test Earnings Fetch

1. Click any time slot in the weekly calendar (e.g., Monday 6 AM)
2. In the console, look for:
   ```
   💰 Fetching earnings: {location: 'New York', date: '2025-10-28', ...}
   📡 Response status: 200
   ✅ Earnings data received: {...}
   ```
3. The side panel should appear with real earnings data

### 4. Test Caching

1. Click the **same time slot** again
2. In the console, look for:
   ```
   📦 Using cached earnings data for New York-Monday-6
   ```
3. Response should be instant (< 1ms)

### 5. Verify Real Data Display

Check the side panel shows:
- ✅ Dynamic earnings range (e.g., "$28 - $38")
- ✅ Hotspot location (e.g., "Financial District")
- ✅ Demand bar with percentage (e.g., "85%")
- ✅ Trips per hour (e.g., "2.3")
- ✅ Surge indicator if > 1.0x (e.g., "1.2x Surge Pricing")

## Troubleshooting

### Python API won't start

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Fix:**
```bash
cd scrapper
pip install flask flask-cors
```

### Express can't connect to Python

**Error:** `Error calling Python earnings API: ECONNREFUSED`

**Fix:**
1. Verify Python API is running: `curl http://localhost:5002/api/health`
2. If not running, start it: `cd scrapper && python api_server.py`

### ChromeDriver issues

**Error:** `selenium.common.exceptions.WebDriverException`

**Fix (macOS):**
```bash
brew install chromedriver
# If you get security warnings:
xattr -d com.apple.quarantine /usr/local/bin/chromedriver
```

**Fix (Linux):**
```bash
sudo apt-get install chromium-chromedriver
```

### Frontend shows mock data

**Check:**
1. Python API running? → `curl http://localhost:5002/api/health`
2. Express running? → `curl http://localhost:5001/api/health`
3. Check browser console for errors
4. Check Network tab in DevTools for failed requests

### Slow API responses

**Expected:**
- First request: 3-10 seconds (scraping)
- Cached requests: 50-100ms
- React cached: < 1ms

**If slower:**
- Check your internet connection
- Some scrapers may be timing out (this is OK - fallback data is used)
- Consider increasing cache TTL in `api_server.py`

## Quick Health Checks

Run these commands to verify all services:

```bash
# Python API
curl http://localhost:5002/api/health
# Expected: {"status": "OK", "service": "Earnings Forecaster API"}

# Express API
curl http://localhost:5001/api/health
# Expected: {"status": "Server is running!"}

# Test earnings endpoint
curl "http://localhost:5001/api/earnings?location=San%20Francisco&startTime=6:00%20AM&endTime=7:00%20AM"
# Expected: JSON with predictions array
```

## What to Expect

### First Time Slot Click
- **Duration:** 3-10 seconds
- **What's happening:**
  - Scraping events from SF FunCheap, Eventbrite
  - Scraping Uber pricing from multiple sources
  - Scraping gas prices from AAA, GasBuddy
  - Checking traffic on 511.org
  - Calculating demand, supply, deadtime
  - Computing net earnings

### Subsequent Clicks (Same Location)
- **Duration:** < 1ms (React cache) or 50-100ms (Python cache)
- **What's happening:**
  - Retrieving cached data
  - No scraping required

### Location Change
- **Duration:** < 1 second
- **What's happening:**
  - Clearing React cache
  - Next slot click will re-scrape for new location

## Configuration

### Change Default Location

Edit `scrapper/config.py`:
```python
LOCATION = "New York"  # Change from "San Francisco"
```

### Adjust Cache Duration

Edit `scrapper/api_server.py`:
```python
CACHE_TTL_SECONDS = 7200  # Change from 3600 (2 hours instead of 1)
```

### Change API Ports

**Python API:**
Edit `scrapper/api_server.py` (bottom):
```python
app.run(host='0.0.0.0', port=5003, debug=True)  # Change from 5002
```

**Express Server:**
Create `server/.env`:
```
PORT=5002
PYTHON_API_URL=http://localhost:5003
```

## Next Steps

Once everything is working:

1. **Read the full documentation:**
   - [SCRAPER_INTEGRATION_GUIDE.md](SCRAPER_INTEGRATION_GUIDE.md) - Complete setup guide
   - [INTEGRATION_EXAMPLE.md](INTEGRATION_EXAMPLE.md) - Code walkthrough
   - [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Architecture overview

2. **Customize for your needs:**
   - Add more cities in `config.py`
   - Adjust pricing, demand, and supply parameters
   - Customize UI colors and branding

3. **Deploy to production:**
   - Use Docker Compose (see SCRAPER_INTEGRATION_GUIDE.md)
   - Deploy to Heroku, AWS, or Vercel
   - Set up Redis for distributed caching

## Getting Help

If you encounter issues:

1. **Check console logs** in browser DevTools
2. **Check terminal logs** for Python and Express servers
3. **Verify all services are running** on correct ports
4. **Review troubleshooting section** in SCRAPER_INTEGRATION_GUIDE.md
5. **Test API endpoints directly** with curl commands above

## Summary

You now have:

✅ Python Flask API scraping real earnings data
✅ Express backend proxying requests
✅ React frontend with location selector
✅ Real-time earnings predictions
✅ Smart caching for performance
✅ Enhanced UI with demand metrics

**Happy coding!** 🚀
