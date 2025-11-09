# Testing Web Scraper on Localhost

## Quick Start

### Step 1: Start the API Server

```bash
# Terminal 1
cd scrapper
source venv/bin/activate
python3 api_server.py
```

You should see:
```
Starting development server on port 5001 (debug=True)
* Running on http://127.0.0.1:5001
```

### Step 2: Run the Test Script

```bash
# Terminal 2 (new terminal)
cd scrapper
source venv/bin/activate
python3 test_localhost.py
```

## What the Test Does

1. **Health Check**: Verifies API is running
2. **Lightweight Endpoint**: Tests `/api/earnings/lightweight` with web scraper
3. **Week Endpoint**: Tests `/api/earnings/week` (optional, takes longer)
4. **Location Comparison**: Tests different locations to verify scraper works

## Expected Output

```
============================================================
Testing Web Scraper on Localhost API
============================================================
API URL: http://localhost:5001
============================================================

1. Testing API health...
   ✅ API is running
   Response: {'status': 'healthy', ...}

2. Testing lightweight endpoint with web scraper...
   ✅ Request successful
   Predictions: 5
   Using live data: True
   Data sources: ['Weather: openweathermap_forecast', ...]
   ✅ Web scraper appears to be used
   
   Earnings estimates:
     Uber: $44-$54/hr
     Lyft: $40-$50/hr
     Doordash: $39-$51/hr
     ...
```

## Manual Testing

### Test API Endpoint Directly

```bash
curl "http://localhost:5001/api/earnings/lightweight?location=San%20Francisco&date=2025-11-09&startTime=6:00%20PM"
```

### Test with Browser

1. Open browser to: `http://localhost:5001/api/health`
2. Should see: `{"status":"healthy",...}`

3. Test earnings endpoint:
   `http://localhost:5001/api/earnings/lightweight?location=San%20Francisco&date=2025-11-09&startTime=6:00%20PM`

### Test Frontend

1. **Start frontend** (Terminal 3):
   ```bash
   cd client
   npm start
   ```

2. **Open browser**: `http://localhost:3000`

3. **Test in UI**:
   - Change location
   - Change date
   - Click different time slots
   - Check browser console (F12) for API calls

## Verify Web Scraper is Working

### Check API Logs

Look for these messages in the API server logs:
```
🌐 Scraping Eventbrite: https://www.eventbrite.com/d/san-francisco/events/...
✅ Eventbrite scraper: Found 19 events
✅ Web Scraper (eventbrite): 19 events found
```

### Check API Response

The response should include:
```json
{
  "metadata": {
    "usingLiveData": true,
    "dataSources": ["Weather: openweathermap_forecast", ...],
    "note": "Live data from: ..."
  },
  "predictions": [...]
}
```

### Check Earnings Estimates

- Different locations should show different estimates
- Estimates should be higher when events are found
- Estimates should vary by time of day

## Troubleshooting

### API Not Running

**Error**: `Cannot connect to API`

**Solution**:
```bash
cd scrapper
source venv/bin/activate
python3 api_server.py
```

### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find and kill process on port 5001
lsof -ti:5001 | xargs kill -9

# Or change port in api_server.py
```

### Web Scraper Not Working

**Symptoms**: No events found, estimates don't vary

**Check**:
1. Internet connection
2. Eventbrite website is accessible
3. API logs for errors
4. Rate limiting (wait a few minutes between tests)

### Frontend Not Connecting

**Symptoms**: Frontend shows errors, can't fetch data

**Check**:
1. API is running on port 5001
2. CORS is enabled (should be automatic)
3. Browser console for errors
4. Network tab for API calls

## Full Integration Test

### Step 1: Start API
```bash
cd scrapper
source venv/bin/activate
python3 api_server.py
```

### Step 2: Start Frontend
```bash
cd client
npm start
```

### Step 3: Test in Browser
1. Open `http://localhost:3000`
2. Select a location (e.g., San Francisco)
3. Select a date (e.g., 2025-11-09)
4. Click a time slot (e.g., 6:00 PM)
5. Check earnings estimates
6. Verify both "Rideshare" and "Food Delivery" show
7. Verify estimates vary by location/time

### Step 4: Verify Web Scraper
1. Check API server logs for scraping messages
2. Check browser console for API responses
3. Verify estimates are adjusted based on events

## That's It!

Your web scraper should be working on localhost! 🎉

