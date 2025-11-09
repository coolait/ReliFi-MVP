# Quick Start - Run Locally

## 🚀 Fastest Way to Start

### Option 1: Use the Startup Script (macOS/Linux)

```bash
# Make script executable (first time only)
chmod +x start_local.sh

# Run both servers (opens in separate terminals)
./start_local.sh

# Or run individually:
./start_local.sh api        # Just the API server
./start_local.sh frontend   # Just the frontend
```

### Option 2: Manual Start (All Platforms)

**Terminal 1 - Python API Server:**
```bash
cd scrapper
source venv/bin/activate  # Windows: venv\Scripts\activate
python3 api_server.py
```

**Terminal 2 - React Frontend:**
```bash
cd client
npm start
```

## ✅ Verify It's Working

1. **API Server**: Should show `Running on http://127.0.0.1:5001`
2. **Frontend**: Should open browser to `http://localhost:3000`
3. **Test API**: Click "🧪 Test API" button in the frontend

## 📍 URLs

- **Frontend**: http://localhost:3000
- **API Server**: http://localhost:5001
- **API Health**: http://localhost:5001/api/health

## ⚠️ Troubleshooting

**Port 5001 already in use:**
```bash
lsof -ti:5001 | xargs kill -9  # macOS/Linux
```

**Port 3000 already in use:**
- React will automatically use port 3001, 3002, etc.

**API not connecting:**
- Make sure Python server is running on port 5001
- Check browser console for errors
- Test API directly: `curl http://localhost:5001/api/health`

## 📚 Full Guide

See `RUN_LOCALLY.md` for detailed instructions and troubleshooting.

