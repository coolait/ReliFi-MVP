# Scraper Integration Guide

This guide explains how to set up and run the integrated rideshare earnings scraper with the Weekly Shift Recommendations UI.

## Overview

The integration connects your Python-based earnings scraper to the React frontend through a two-tier API architecture:

1. **Python Flask API** (Port 5002) - Runs the earnings forecaster and provides real-time predictions
2. **Express.js API** (Port 5001) - Acts as a proxy between the frontend and Python API
3. **React Frontend** - Displays recommendations with location-based filtering

## Architecture

```
┌─────────────────┐
│  React Frontend │
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP Requests
         ▼
┌─────────────────┐
│  Express Server │
│  (Port 5001)    │
└────────┬────────┘
         │ HTTP Requests
         ▼
┌─────────────────┐
│  Python Flask   │
│  API Server     │
│  (Port 5002)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Earnings        │
│ Scraper         │
│ (scrape.py)     │
└─────────────────┘
```

## Prerequisites

### Python Dependencies

```bash
cd scrapper
pip install flask flask-cors requests beautifulsoup4 pandas selenium
```

### Node.js Dependencies

```bash
# Install server dependencies
cd server
npm install

# Install client dependencies
cd ../client
npm install
```

## Setup Instructions

### Step 1: Install Python Dependencies

```bash
cd scrapper
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:

```bash
pip install flask flask-cors requests beautifulsoup4 pandas selenium
```

### Step 2: Install Selenium WebDriver

The scraper uses Selenium for dynamic content. Install ChromeDriver:

**macOS:**
```bash
brew install chromedriver
```

**Linux:**
```bash
sudo apt-get install chromium-chromedriver
```

**Windows:**
Download from: https://chromedriver.chromium.org/

### Step 3: Configure the Scraper

Edit `scrapper/config.py` to customize settings:

```python
# Location (can be overridden by API calls)
LOCATION = "San Francisco"

# Market assumptions
BASE_DEMAND_SF = 12000  # Base trips per hour
BASE_DRIVERS_SF = 3500  # Active drivers
AVG_TRIP_DISTANCE_MILES = 4.2
AVG_TRIP_DURATION_MINUTES = 18

# Pricing (adjust for your market)
UBER_BASE_FARE = 2.20
UBER_COST_PER_MINUTE = 0.22
UBER_COST_PER_MILE = 1.15
```

### Step 4: Install Server Dependencies

```bash
cd server
npm install
```

This will install:
- `express` - Web server
- `cors` - Cross-origin resource sharing
- `axios` - HTTP client for calling Python API

### Step 5: Install Client Dependencies

```bash
cd client
npm install
```

## Running the Application

### Method 1: Run All Services Manually

**Terminal 1 - Python Flask API:**
```bash
cd scrapper
python api_server.py
```

Expected output:
```
============================================================
Starting Earnings Forecaster API Server
============================================================
Endpoints:
  GET  /api/health              - Health check
  GET  /api/earnings            - Get earnings for single timeslot
  POST /api/earnings/batch      - Get earnings for multiple timeslots
  GET  /api/earnings/week       - Get earnings for entire week
============================================================
 * Running on http://0.0.0.0:5002
```

**Terminal 2 - Express Backend:**
```bash
cd server
npm start
```

Expected output:
```
Server is running on port 5001
Python scraper API expected at: http://localhost:5002
```

**Terminal 3 - React Frontend:**
```bash
cd client
npm start
```

Expected output:
```
Compiled successfully!
You can now view the app in the browser.
  Local:            http://localhost:3000
```

### Method 2: Create a Startup Script

Create `start-all.sh` in the root directory:

```bash
#!/bin/bash

# Start Python API
echo "Starting Python Flask API..."
cd scrapper
python api_server.py &
PYTHON_PID=$!

# Wait for Python API to start
sleep 3

# Start Express server
echo "Starting Express server..."
cd ../server
npm start &
EXPRESS_PID=$!

# Wait for Express to start
sleep 2

# Start React frontend
echo "Starting React frontend..."
cd ../client
npm start &
REACT_PID=$!

# Wait for all processes
wait $PYTHON_PID $EXPRESS_PID $REACT_PID
```

Make it executable:
```bash
chmod +x start-all.sh
./start-all.sh
```

## API Endpoints

### Python Flask API (Port 5002)

#### GET /api/earnings

Get projected earnings for a specific timeslot.

**Query Parameters:**
- `location` (string) - e.g., "San Francisco", "New York"
- `date` (string) - Format: YYYY-MM-DD (optional, defaults to today)
- `startTime` (string) - e.g., "6:00 AM" or "06:00"
- `endTime` (string) - e.g., "7:00 AM" or "07:00"
- `service` (string) - "Uber", "Lyft", or "all" (optional, defaults to "all")

**Example Request:**
```bash
curl "http://localhost:5002/api/earnings?location=San%20Francisco&date=2025-10-23&startTime=6:00%20AM&endTime=7:00%20AM"
```

**Example Response:**
```json
{
  "location": "San Francisco",
  "date": "2025-10-23",
  "timeSlot": "6:00 AM - 7:00 AM",
  "hour": 6,
  "predictions": [
    {
      "service": "Uber",
      "min": 25.50,
      "max": 35.75,
      "hotspot": "Downtown Core",
      "demandScore": 0.85,
      "tripsPerHour": 2.3,
      "surgeMultiplier": 1.1,
      "color": "#4285F4",
      "startTime": "6:00 AM",
      "endTime": "7:00 AM"
    },
    {
      "service": "Lyft",
      "min": 23.00,
      "max": 33.25,
      "hotspot": "Downtown Core",
      "demandScore": 0.82,
      "tripsPerHour": 2.2,
      "surgeMultiplier": 1.05,
      "color": "#FF00BF",
      "startTime": "6:00 AM",
      "endTime": "7:00 AM"
    }
  ],
  "metadata": {
    "demandEstimate": 7800,
    "driverSupply": 2100,
    "demandSupplyRatio": 3.71,
    "trafficLevel": 0.5,
    "weekday": "thursday"
  }
}
```

#### POST /api/earnings/batch

Get earnings for multiple timeslots at once.

**Request Body:**
```json
{
  "location": "San Francisco",
  "date": "2025-10-23",
  "timeSlots": [
    {"startTime": "6:00 AM", "endTime": "7:00 AM"},
    {"startTime": "7:00 AM", "endTime": "8:00 AM"}
  ]
}
```

#### GET /api/earnings/week

Get earnings for an entire week.

**Query Parameters:**
- `location` (string) - City name
- `startDate` (string) - Start of week (YYYY-MM-DD), defaults to current week

### Express Backend API (Port 5001)

The Express server proxies all requests to the Python API with the same endpoints:

- `GET /api/earnings` - Proxies to Python API
- `POST /api/earnings/batch` - Proxies to Python API
- `GET /api/earnings/week` - Proxies to Python API
- `GET /api/recommendations/:day/:hour` - Legacy endpoint (mock data)

## Frontend Features

### Location Input Component

The location input is displayed at the top of the Weekly Shift Recommendations page.

**Features:**
- Change location by clicking "Change"
- Quick select from common cities (SF, NYC, LA, Chicago, etc.)
- Automatically refreshes earnings when location changes
- Shows loading indicator during API calls

### Calendar Integration

- Click any time slot to fetch real earnings predictions
- Earnings are cached per location to reduce API calls
- Cache is cleared when location changes
- Fallback to mock data if Python API is unavailable

### Enhanced Shift Details

The side panel now displays:
- **Projected Earnings**: Real min/max range from scraper
- **Hotspot Area**: Dynamic location based on demand
- **Demand Forecast**: Visual bar showing demand score (0-100%)
- **Est. Trips/Hour**: Expected number of trips
- **Surge Pricing**: Indicator when surge multiplier > 1.0

## Caching Strategy

### Frontend Cache (React State)

- Cache key format: `{location}-{day}-{hour}`
- Stored in React component state
- Cleared on location change
- Example: `San Francisco-Monday-6`

### Python Cache (In-Memory)

- Cache key: MD5 hash of `{location}_{date}_{hour}`
- TTL: 1 hour (3600 seconds)
- Reduces scraping overhead
- Shared across all clients

## Troubleshooting

### Python API Not Starting

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
cd scrapper
pip install flask flask-cors
```

**Error:** `selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH`

**Solution:**
```bash
# macOS
brew install chromedriver

# Linux
sudo apt-get install chromium-chromedriver
```

### Express Server Can't Connect to Python API

**Error:** `Error calling Python earnings API: connect ECONNREFUSED 127.0.0.1:5002`

**Solution:**
1. Check if Python API is running: `curl http://localhost:5002/api/health`
2. Restart Python API: `cd scrapper && python api_server.py`

### Frontend Shows Mock Data

**Check these:**
1. Python API is running on port 5002
2. Express server is running on port 5001
3. Check browser console for API errors
4. Verify network requests in browser DevTools

### Slow API Response

The scraper performs real-time web scraping, which can be slow. To improve:

1. **Use batch endpoints** for multiple timeslots
2. **Pre-warm the cache** by making initial requests
3. **Reduce scraping sources** in `scrape.py` (comment out slow scrapers)
4. **Increase cache TTL** in `api_server.py` (default: 1 hour)

## Configuration Options

### Environment Variables

Create `.env` files:

**server/.env:**
```
PORT=5001
PYTHON_API_URL=http://localhost:5002
```

**scrapper/.env:**
```
FLASK_PORT=5002
FLASK_ENV=development
```

### Scraper Configuration

Edit `scrapper/config.py`:

```python
# Adjust for your market
BASE_DEMAND_SF = 12000  # Higher = more demand
BASE_DRIVERS_SF = 3500  # Higher = more supply

# Pricing
UBER_BASE_FARE = 2.20  # Adjust for your city
GAS_PRICE_PER_GALLON = 5.25  # Current gas prices

# Deadtime (time between rides)
DEADTIME_CONFIG = {
    'avg_wait_time_minutes': 12,  # Reduce for busier markets
    'avg_pickup_time_minutes': 7   # Adjust for traffic
}
```

## Production Deployment

### Option 1: Separate Services

Deploy each service independently:

1. **Python API** - Deploy to Heroku, AWS Lambda, or DigitalOcean
2. **Express Backend** - Deploy to Vercel, Heroku, or AWS
3. **React Frontend** - Deploy to Vercel, Netlify, or AWS S3/CloudFront

Update environment variables:
```
PYTHON_API_URL=https://your-python-api.herokuapp.com
```

### Option 2: Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  python-api:
    build: ./scrapper
    ports:
      - "5002:5002"
    environment:
      - FLASK_ENV=production

  express-server:
    build: ./server
    ports:
      - "5001:5001"
    environment:
      - PYTHON_API_URL=http://python-api:5002
    depends_on:
      - python-api

  react-frontend:
    build: ./client
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5001
    depends_on:
      - express-server
```

Run with:
```bash
docker-compose up
```

## Performance Optimization

### 1. Pre-compute Week Data

Instead of real-time scraping for every slot, pre-compute the entire week:

```bash
# Add cron job to run every morning
0 6 * * * cd /path/to/scrapper && python precompute_week.py
```

### 2. Use Redis for Caching

Replace in-memory cache with Redis:

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

def cache_earnings(location, date, hour, data):
    key = f"{location}_{date}_{hour}"
    r.setex(key, 3600, json.dumps(data))  # 1 hour TTL
```

### 3. Add Database Storage

Store historical predictions:

```sql
CREATE TABLE earnings_predictions (
    id SERIAL PRIMARY KEY,
    location VARCHAR(100),
    date DATE,
    hour INT,
    service VARCHAR(50),
    min_earnings DECIMAL(10,2),
    max_earnings DECIMAL(10,2),
    demand_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Testing

### Test Python API

```bash
# Health check
curl http://localhost:5002/api/health

# Get earnings for a timeslot
curl "http://localhost:5002/api/earnings?location=San%20Francisco&startTime=6:00%20AM&endTime=7:00%20AM"
```

### Test Express API

```bash
# Health check
curl http://localhost:5001/api/health

# Get earnings (should proxy to Python)
curl "http://localhost:5001/api/earnings?location=New%20York&startTime=6:00%20AM&endTime=7:00%20AM"
```

### Test Frontend

1. Open http://localhost:3000
2. Click "Change" in the location input
3. Select a different city
4. Click any time slot in the calendar
5. Verify real earnings data appears in the side panel

## Support

For issues or questions:
- Check console logs in browser DevTools
- Review Python API logs in terminal
- Check Express server logs
- Verify all services are running on correct ports

## Next Steps

- Add more cities to the scraper configuration
- Implement user authentication and saved preferences
- Add historical data visualization
- Create mobile-responsive design improvements
- Add email notifications for high-demand periods
