# Vercel Deployment Guide

This guide explains how to deploy the ReliFi MVP to Vercel.

## Architecture Overview

Your application consists of three main components:

1. **Frontend (React)** - Deployed to Vercel
2. **Node.js API Server** - Converted to Vercel serverless functions
3. **Python Scraper API** - Must be deployed separately (Railway, Render, or similar)

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
   - **Key**: `PYTHON_API_URL`
   - **Value**: The URL of your deployed Python API (e.g., `https://your-app.railway.app`)

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
5. Add the `PYTHON_API_URL` environment variable
6. Click "Deploy"

## Step 4: Verify Deployment

1. Once deployed, visit your Vercel URL
2. Test the API endpoints:
   - `https://your-app.vercel.app/api/health` - Should return status
   - `https://your-app.vercel.app/api/earnings/lightweight?location=San%20Francisco&date=2025-11-04&startTime=9:00%20AM&endTime=10:00%20AM` - Should return earnings data

## Troubleshooting

### Build Fails

**Issue**: Build fails with TypeScript errors
**Solution**: Make sure `@vercel/node` and `axios` are installed in root `package.json`

**Issue**: Build fails with "Cannot find module"
**Solution**: Run `npm install` in the root directory and ensure all dependencies are listed

### API Endpoints Not Working

**Issue**: `/api/earnings` returns 404
**Solution**: 
- Check that `api/earnings/index.ts` exists
- Verify `vercel.json` has correct routing configuration
- Ensure the function is deployed (check Vercel dashboard > Functions tab)

**Issue**: API returns fallback data instead of real data
**Solution**:
- Check that `PYTHON_API_URL` environment variable is set correctly
- Verify your Python API is accessible and running
- Check Vercel function logs for errors

### Python API Connection Issues

**Issue**: Timeout errors when calling Python API
**Solution**:
- Increase timeout in the serverless function (currently 30s for full, 5s for lightweight)
- Check that your Python API is publicly accessible
- Verify CORS is enabled on the Python API

## Project Structure for Vercel

```
ReliFi MVP/
├── api/                          # Vercel serverless functions
│   ├── health.ts
│   ├── test.ts
│   ├── earnings/
│   │   ├── index.ts             # Full earnings endpoint
│   │   └── lightweight.ts       # Lightweight earnings endpoint
│   └── recommendations/
│       └── [day]/
│           └── [hour].ts
├── client/                       # React frontend
│   ├── src/
│   ├── build/                   # Build output (generated)
│   └── package.json
├── vercel.json                  # Vercel configuration
└── package.json                 # Root dependencies
```

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `PYTHON_API_URL` | URL of your deployed Python scraper API | Yes | `https://your-app.railway.app` |

## Notes

- The frontend will automatically use fallback data if the Python API is unavailable
- All API endpoints include CORS headers for cross-origin requests
- Serverless functions have a 10-second default timeout (increased to 30s for full earnings)
- Vercel automatically handles HTTPS and CDN distribution

## Cost Considerations

- **Vercel**: Free tier includes 100GB bandwidth and serverless function execution
- **Railway**: Free tier includes $5/month credit (usually enough for MVP)
- **Render**: Free tier available but may sleep after inactivity

## Next Steps

1. Deploy Python API to Railway/Render
2. Set `PYTHON_API_URL` in Vercel
3. Deploy frontend to Vercel
4. Test all endpoints
5. Monitor logs in Vercel dashboard

