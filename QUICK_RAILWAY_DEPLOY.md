# Quick Guide: Deploy to Railway

## Current Status

Your changes to the Ticketmaster API are ready to deploy. Here's how to get them on Railway:

## Step 1: Check if Changes are Committed

```bash
git status
```

If you see "nothing to commit, working tree clean", your changes are already committed.

## Step 2: Push to GitHub

If Railway is connected to your GitHub repository (most common setup):

```bash
# Make sure you're on the right branch
git branch

# Push to GitHub
git push origin avani4
```

**Railway will automatically deploy** when you push to GitHub!

## Step 3: Verify Deployment

1. **Check Railway Dashboard:**
   - Go to https://railway.app
   - Click on your project
   - Go to "Deployments" tab
   - You should see a new deployment starting

2. **Check Deployment Logs:**
   - Click on the deployment
   - View logs to see:
     - ✅ Build successful
     - ✅ Server started
     - ✅ "Starting Earnings Forecaster API Server"

3. **Test the API:**
   ```bash
   # Get your Railway URL from the dashboard
   # Then test:
   curl https://your-railway-url.railway.app/api/health
   ```

## Step 4: Test Event Boost

Test that the Ticketmaster API is working:

```bash
# Test with Nov 9, 2025 (has 23 events)
curl "https://your-railway-url.railway.app/api/earnings?location=San%20Francisco&date=2025-11-09&startTime=9:00%20PM&lat=37.7749&lng=-122.4194"
```

Look for:
- `"eventBoost"` in the response
- Event count in the logs
- Dynamic surge windows working

## If Railway is NOT Connected to GitHub

If Railway is not connected to GitHub, you can:

### Option A: Connect Railway to GitHub (Recommended)

1. Go to Railway Dashboard
2. Click on your project
3. Go to "Settings" → "Source"
4. Connect to GitHub repository
5. Select branch: `avani4`
6. Railway will auto-deploy on every push

### Option B: Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
cd scrapper
railway link

# Deploy
railway up
```

## Environment Variables

Make sure these are set in Railway:

1. Go to Railway Dashboard
2. Click on your project
3. Go to "Variables" tab
4. Verify these are set:
   - `TICKETMASTER_API_KEY` - Your Ticketmaster Consumer Key
   - `OPENWEATHER_API_KEY` - Your OpenWeatherMap API key
   - `PORT` - Railway sets this automatically

## What Was Updated

The following improvements are being deployed:

✅ **Ticketmaster API:**
- Fetches all events (not just 4)
- Increased search radius to 25 miles
- Added pagination support
- Improved date parsing

✅ **Dynamic Surge Windows:**
- Windows based on actual event times
- Capacity-based window duration (1-3 hours)
- Boost during event (not just before/after)
- Works on all days (fixed Saturday-only issue)

✅ **Event Boost Integration:**
- Event boost applied to earnings
- Multiple overlapping events supported
- Boost capped at 1.5x (150%)

## Troubleshooting

### Deployment Fails

1. Check Railway logs for errors
2. Verify `requirements.txt` has all dependencies
3. Check that `TICKETMASTER_API_KEY` is set

### API Not Working

1. Check Railway logs for API errors
2. Verify API keys are set correctly
3. Test with: `curl https://your-url.railway.app/api/health`

### Events Not Found

1. Check logs for "✅ Ticketmaster API: X events found"
2. Verify `TICKETMASTER_API_KEY` is valid
3. Test with dates that have events (e.g., Nov 9, 2025)

## Need Help?

1. Check Railway logs in the dashboard
2. Test API locally first: `python3 scrapper/api_server.py`
3. Verify environment variables are set
4. Check Railway documentation: https://docs.railway.app

