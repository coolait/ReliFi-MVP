# Deploy to Railway - Quick Steps

## ✅ Your changes are already committed!

Your Ticketmaster API fixes are ready to deploy. Here are the steps:

## Option 1: Push to GitHub (Auto-Deploy)

If Railway is connected to your GitHub repository:

```bash
# Push to GitHub
git push origin avani4
```

**Railway will automatically deploy** when you push!

## Option 2: Manual Redeploy in Railway Dashboard

1. Go to [Railway Dashboard](https://railway.app)
2. Click on your project
3. Go to **"Deployments"** tab
4. Click **"Redeploy"** on the latest deployment

## Option 3: Trigger Deployment with Empty Commit

If you want to force a new deployment:

```bash
git commit --allow-empty -m "Trigger Railway deployment - Ticketmaster API fixes"
git push origin avani4
```

## Verify Deployment

After deployment, check:

1. **Railway Logs:**
   - Look for: "✅ Ticketmaster API: X events found"
   - Check for any errors

2. **Test API:**
   ```bash
   # Replace with your Railway URL
   curl https://your-railway-url.railway.app/api/health
   ```

3. **Test Event Boost:**
   ```bash
   curl "https://your-railway-url.railway.app/api/earnings?location=San%20Francisco&date=2025-11-09&startTime=9:00%20PM&lat=37.7749&lng=-122.4194"
   ```

## What's Being Deployed

✅ **Ticketmaster API Improvements:**
- Fetches all events (not just 4)
- Increased search radius to 25 miles
- Added pagination support
- Improved date parsing

✅ **Dynamic Surge Windows:**
- Windows based on actual event times
- Capacity-based duration (1-3 hours)
- Boost during event
- Works on all days (fixed Saturday-only issue)

✅ **Event Boost Integration:**
- Event boost applied to earnings
- Multiple overlapping events supported
- Boost capped at 1.5x

## Environment Variables

Make sure these are set in Railway:
- `TICKETMASTER_API_KEY` - Your Ticketmaster Consumer Key
- `OPENWEATHER_API_KEY` - Your OpenWeatherMap API key

## Need Help?

1. Check Railway logs in the dashboard
2. Verify environment variables are set
3. Test API locally first: `python3 scrapper/api_server.py`

