# How to Start the Python Scraper API

The projected earnings are currently showing mock/fallback data because the Python scraper API server is not running.

## Quick Start

**In a new terminal window, run:**

```bash
cd scrapper
python api_server.py
```

Or if you need to use `python3`:

```bash
cd scrapper
python3 api_server.py
```

## Expected Output

You should see:
```
============================================================
Starting Earnings Forecaster API Server
============================================================
Endpoints:
  GET  /api/health              - Health check
  GET  /api/earnings/lightweight- FAST estimates (< 50ms, no scraping)
  GET  /api/earnings            - Full earnings with scraping (3-10s)
  POST /api/earnings/batch      - Get earnings for multiple timeslots
  GET  /api/earnings/week       - Get earnings for entire week
============================================================
TIP: Use /lightweight endpoint for instant UI responses!
============================================================
 * Running on http://0.0.0.0:5002
```

## Running All Three Servers

You need **three terminals** running:

1. **Terminal 1 - Python API** (port 5002):
   ```bash
   cd scrapper
   python api_server.py
   ```

2. **Terminal 2 - Express Server** (port 5001):
   ```bash
   cd server
   node index.js
   ```

3. **Terminal 3 - React Client** (port 3000):
   ```bash
   cd client
   npm start
   ```

## Verify It's Working

Once the Python API is running, you should see:
- ✅ No more "Error calling Python lightweight API" messages in the Express server logs
- ✅ Earnings values change based on location, date, and time
- ✅ Console warnings about fallback data should disappear

## Troubleshooting

**If you get "Module not found" errors:**
```bash
cd scrapper
pip install -r requirements.txt
```

**If port 5002 is already in use:**
- Check what's using it: `netstat -ano | findstr :5002` (Windows) or `lsof -i :5002` (Mac/Linux)
- Or change the port in `api_server.py` and update `PYTHON_API_URL` in `server/index.js`

