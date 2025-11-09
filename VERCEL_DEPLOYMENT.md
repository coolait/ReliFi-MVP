# Vercel Deployment Guide

This guide explains how to deploy the ReliFi MVP to Vercel.

## Architecture Overview

Your application consists of two main components:

1. **Frontend (React)** - Deployed to Vercel
2. **Python Scraper API** - Deployed on Railway (or similar platform)

**Note**: The Express server is no longer used. The React frontend connects directly to the Python API on Railway.

## Prerequisites

1. A Vercel account (free tier works)
2. A deployment platform for the Python API (Railway, Render, PythonAnywhere, etc.)
3. GitHub repository connected to Vercel

## Step 1: Deploy Python API Separately

Since Vercel doesn't support Python, you need to deploy the Python scraper API separately:

### Option A: Railway (Recommended)

1. Go to [Railway.app](https://railway.app)
2. Create a new project
3. Connect your GitHub repository
4. Add a new service and select the `scrapper` directory
5. Set the start command: `python api_server.py`
6. Railway will automatically detect Python and install dependencies
7. Copy the generated URL (e.g., `https://your-app.railway.app`)

### Option B: Render

1. Go to [Render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set the root directory to `scrapper`
5. Build command: `pip install -r requirements.txt`
6. Start command: `python api_server.py`
7. Copy the generated URL

### Option C: PythonAnywhere

1. Upload your `scrapper` folder to PythonAnywhere
2. Install dependencies: `pip install -r requirements.txt`
3. Configure the web app to run `api_server.py`
4. Copy the URL

## Step 2: Configure Environment Variables

In your Vercel dashboard:

1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add the following variable:
   - **Key**: `REACT_APP_PYTHON_API_URL`
   - **Value**: The URL of your deployed Python API on Railway (e.g., `https://your-app.railway.app`)
   - **Important**: Make sure to include the protocol (`https://`) and do NOT include a trailing slash

## Step 3: Deploy to Vercel

### Option A: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# For production deployment
vercel --prod
```

### Option B: Using GitHub Integration

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the configuration from `vercel.json`
5. Add the `REACT_APP_PYTHON_API_URL` environment variable with your Railway API URL
6. Click "Deploy"

## Step 4: Verify Deployment

1. Once deployed, visit your Vercel URL
2. Test the Python API directly:
   - `https://your-app.railway.app/api/health` - Should return status
   - `https://your-app.railway.app/api/earnings/lightweight?location=San%20Francisco&date=2025-11-04&startTime=9:00%20AM&endTime=10:00%20AM` - Should return earnings data
3. Test the frontend:
   - Open the Vercel app in your browser
   - Open browser DevTools console
   - Click a time slot - you should see API calls to the Railway URL
   - Check for any CORS errors or connection issues

## Troubleshooting

### Build Fails

**Issue**: Build fails with TypeScript errors
**Solution**: Make sure `@vercel/node` and `axios` are installed in root `package.json`

**Issue**: Build fails with "Cannot find module"
**Solution**: Run `npm install` in the root directory and ensure all dependencies are listed

### API Endpoints Not Working

**Issue**: Frontend can't connect to Python API
**Solution**: 
- Check that `REACT_APP_PYTHON_API_URL` environment variable is set in Vercel
- Verify the Railway URL is correct (including `https://`)
- Check browser console for CORS errors
- Verify your Python API on Railway is running and accessible
- Test the Railway URL directly in your browser

**Issue**: API returns fallback data instead of real data
**Solution**:
- Check that `REACT_APP_PYTHON_API_URL` environment variable is set correctly in Vercel
- Verify your Python API on Railway is accessible and running
- Check browser console for network errors
- Ensure Railway API has CORS enabled (check `api_server.py` CORS configuration)

### Python API Connection Issues

**Issue**: Timeout errors when calling Python API
**Solution**:
- Check that your Python API on Railway is publicly accessible
- Verify CORS is enabled on the Python API (check `api_server.py`)
- Check Railway logs for any errors
- Ensure Railway service is running (not sleeping)
- For Railway free tier, services may sleep after inactivity - consider upgrading or using a keep-alive service

## Project Structure for Vercel

```
ReliFi MVP/
├── client/                       # React frontend
│   ├── src/
│   │   ├── config/
│   │   │   └── api.ts          # API configuration (points to Railway)
│   │   └── components/
│   ├── build/                   # Build output (generated)
│   └── package.json
├── scrapper/                    # Python API (deployed on Railway)
│   ├── api_server.py
│   └── requirements.txt
├── vercel.json                  # Vercel configuration (serves React app only)
└── package.json
```

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `REACT_APP_PYTHON_API_URL` | URL of your deployed Python scraper API on Railway | Yes | `https://your-app.railway.app` |

**Important Notes:**
- The variable name must start with `REACT_APP_` for React to access it
- Include the full URL with `https://` protocol
- Do NOT include a trailing slash
- Set this in Vercel project settings > Environment Variables
- After adding/updating, you need to redeploy for changes to take effect

## Notes

- The frontend connects directly to the Python API on Railway (no Express server needed)
- The React app will automatically use fallback data if the Python API is unavailable
- Make sure CORS is enabled in your Python API (`api_server.py` should already have this)
- Vercel automatically handles HTTPS and CDN distribution
- The `api/` folder with serverless functions is no longer used but can remain in the repository

## Cost Considerations

- **Vercel**: Free tier includes 100GB bandwidth and serverless function execution
- **Railway**: Free tier includes $5/month credit (usually enough for MVP)
- **Render**: Free tier available but may sleep after inactivity

## Next Steps

1. Deploy Python API to Railway (see Step 1)
2. Copy your Railway API URL (e.g., `https://your-app.railway.app`)
3. Set `REACT_APP_PYTHON_API_URL` environment variable in Vercel
4. Deploy frontend to Vercel
5. Test the frontend - it should connect to Railway API
6. Monitor logs in both Vercel and Railway dashboards

## Local Development

For local development:

1. **Start Python API** (in `scrapper/` folder):
   ```bash
   cd scrapper
   python api_server.py
   ```
   This will run on `http://localhost:5002`

2. **Start React frontend** (in `client/` folder):
   ```bash
   cd client
   npm start
   ```
   This will run on `http://localhost:3000` and automatically connect to `http://localhost:5002`

The frontend is configured to use `http://localhost:5002` in development mode automatically.

