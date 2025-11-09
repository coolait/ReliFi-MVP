# Running the Application on Localhost

This guide will help you run the full application locally on your computer.

## Prerequisites

1. **Python 3.10+** installed
2. **Node.js 16+** installed
3. **npm** installed
4. **API Keys** (optional but recommended for full functionality):
   - OpenWeatherMap API key
   - Eventbrite API key (Personal OAuth Token)
   - Google Maps API key
   - Meetup API key (recommended)
   - Songkick API key (optional)

## Quick Start

### Step 1: Set Up Python API Server

1. **Navigate to the scrapper directory**:
   ```bash
   cd scrapper
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit .env and add your API keys
   # OPENWEATHER_API_KEY=your_key_here
   # EVENTBRITE_API_KEY=your_key_here
   # GOOGLE_MAPS_API_KEY=your_key_here
   # MEETUP_API_KEY=your_key_here
   ```

5. **Start the Python API server** (Port 5001):
   ```bash
   python3 api_server.py
   ```

   You should see:
   ```
   ✅ Loaded environment variables from .env file
   ============================================================
   Starting Earnings Forecaster API Server
   ============================================================
   Starting development server on port 5001 (debug=True)
   * Running on all addresses (0.0.0.0)
   * Running on http://127.0.0.1:5001
   ```

6. **Test the API** (in a new terminal):
   ```bash
   curl http://localhost:5001/api/health
   ```

   You should see:
   ```json
   {"status":"healthy","timestamp":"2025-11-09T..."}
   ```

### Step 2: Set Up React Frontend

1. **Open a new terminal** (keep the Python server running)

2. **Navigate to the client directory**:
   ```bash
   cd client
   ```

3. **Install dependencies**:
   ```bash
   npm install
   ```

4. **Set up environment variables** (if using Firebase):
   ```bash
   # Create .env file in client directory
   # REACT_APP_FIREBASE_API_KEY=your_key
   # REACT_APP_FIREBASE_AUTH_DOMAIN=your_domain
   # REACT_APP_FIREBASE_PROJECT_ID=your_project_id
   # ... (other Firebase config)
   ```

5. **Start the React development server**:
   ```bash
   npm start
   ```

   The browser should automatically open to `http://localhost:3000`

### Step 3: Verify Everything Works

1. **Frontend**: Should be running at `http://localhost:3000`
2. **Backend API**: Should be running at `http://localhost:5001`
3. **Test API Connection**: Click the "🧪 Test API" button in the frontend
4. **Check Console**: Open browser DevTools (F12) and check for any errors

## Ports Used

- **Frontend (React)**: `http://localhost:3000`
- **Backend API (Python)**: `http://localhost:5001`
- **Python API Health Check**: `http://localhost:5001/api/health`

## Troubleshooting

### Python API Server Issues

**Port already in use**:
```bash
# Find and kill the process using port 5001
lsof -ti:5001 | xargs kill -9  # macOS/Linux
```

**Module not found errors**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**API keys not working**:
```bash
# Check if .env file exists and has correct keys
cat .env

# Test API keys individually
python3 test_apis_local.py
```

### React Frontend Issues

**Port 3000 already in use**:
```bash
# React will automatically use the next available port (3001, 3002, etc.)
# Or kill the process:
lsof -ti:3000 | xargs kill -9  # macOS/Linux
```

**API connection errors**:
- Make sure Python API server is running on port 5001
- Check `client/src/config/api.ts` - should use `http://localhost:5001` in development
- Check browser console for CORS errors (should be handled by Flask-CORS)

**npm install fails**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Common Issues

**CORS Errors**:
- Flask-CORS should handle this automatically
- Make sure `CORS(app)` is enabled in `api_server.py`

**API Not Responding**:
- Check Python server logs for errors
- Test API directly: `curl http://localhost:5001/api/health`
- Check if port 5001 is correct in both frontend config and Python server

**Environment Variables Not Loading**:
- Make sure `.env` file is in the `scrapper/` directory
- Make sure `python-dotenv` is installed: `pip install python-dotenv`
- Restart the Python server after changing `.env`

## Development Workflow

1. **Start Python API server** (Terminal 1):
   ```bash
   cd scrapper
   source venv/bin/activate
   python3 api_server.py
   ```

2. **Start React frontend** (Terminal 2):
   ```bash
   cd client
   npm start
   ```

3. **Make changes**:
   - Python API: Changes require server restart
   - React frontend: Changes hot-reload automatically

4. **Test changes**:
   - Frontend: Refresh browser (or auto-reloads)
   - API: Test endpoints directly or use frontend "Test API" button

## API Endpoints

Once the Python server is running, you can test these endpoints:

- **Health Check**: `GET http://localhost:5001/api/health`
- **Lightweight Earnings**: `GET http://localhost:5001/api/earnings/lightweight?location=San%20Francisco&date=2025-11-09&startTime=6:00%20PM`
- **Full Earnings**: `GET http://localhost:5001/api/earnings?location=San%20Francisco&date=2025-11-09&startTime=6:00%20PM`
- **Week Earnings**: `GET http://localhost:5001/api/earnings/week?location=San%20Francisco&date=2025-11-09`

## Next Steps

- Add API keys to `.env` for full functionality
- Test different locations and dates
- Check browser console for any errors
- Use the "🧪 Test API" button in the frontend to verify connection

## That's It! 🎉

Your application should now be running locally at `http://localhost:3000`!

