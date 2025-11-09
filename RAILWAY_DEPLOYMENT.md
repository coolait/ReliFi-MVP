# Deploying Updates to Railway

## Quick Deploy Steps

### Option 1: Deploy via Git (Recommended)

If your Railway project is connected to your GitHub repository:

1. **Commit your changes:**
   ```bash
   git add scrapper/ticketmaster_events_scraper.py
   git add scrapper/improved_data_scraper.py
   git add scrapper/live_data_scraper.py
   git add scrapper/api_server.py
   git commit -m "Fix Ticketmaster API: Fetch all events, dynamic surge windows, fix Saturday-only issue"
   ```

2. **Push to GitHub:**
   ```bash
   git push origin avani4
   ```

3. **Railway will automatically deploy:**
   - Railway monitors your GitHub repository
   - When you push changes, it automatically triggers a new deployment
   - Check the Railway dashboard for deployment status

### Option 2: Manual Deploy via Railway CLI

If you prefer to deploy manually:

1. **Install Railway CLI** (if not already installed):
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Link your project** (if not already linked):
   ```bash
   cd scrapper
   railway link
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

### Option 3: Deploy via Railway Dashboard

1. Go to [Railway Dashboard](https://railway.app)
2. Select your project
3. Go to the "Deployments" tab
4. Click "Redeploy" or trigger a new deployment from your GitHub repository

## Verify Deployment

After deployment, verify the changes:

1. **Check Railway logs:**
   - Go to Railway dashboard
   - Click on your service
   - View "Logs" tab
   - Look for: "✅ Ticketmaster API: X events found"

2. **Test the API:**
   ```bash
   # Get your Railway URL from the dashboard
   curl https://your-railway-url.railway.app/api/health
   ```

3. **Test event boost:**
   ```bash
   # Test with a date that has events (e.g., Nov 9, 2025)
   curl "https://your-railway-url.railway.app/api/earnings?location=San%20Francisco&date=2025-11-09&startTime=9:00%20PM&lat=37.7749&lng=-122.4194"
   ```

## Important Files for Deployment

The following files have been updated and need to be deployed:

- `scrapper/ticketmaster_events_scraper.py` - Fixed event fetching, dynamic surge windows
- `scrapper/improved_data_scraper.py` - Event boost integration
- `scrapper/live_data_scraper.py` - Location consistency
- `scrapper/api_server.py` - Location name preservation

## Environment Variables

Make sure these environment variables are set in Railway:

- `TICKETMASTER_API_KEY` - Your Ticketmaster Consumer Key
- `OPENWEATHER_API_KEY` - Your OpenWeatherMap API key
- `PORT` - Railway sets this automatically

## Troubleshooting

### Deployment Fails

1. **Check Railway logs:**
   - Look for error messages in the deployment logs
   - Common issues: Missing dependencies, syntax errors

2. **Check requirements.txt:**
   ```bash
   cd scrapper
   pip install -r requirements.txt
   ```

3. **Test locally first:**
   ```bash
   cd scrapper
   python3 api_server.py
   ```

### API Not Working

1. **Check API keys:**
   - Verify `TICKETMASTER_API_KEY` is set in Railway
   - Check Railway dashboard → Variables tab

2. **Check logs:**
   - Look for API errors in Railway logs
   - Check for rate limiting or authentication errors

### Events Not Found

1. **Check API response:**
   - Look for "✅ Ticketmaster API: X events found" in logs
   - If 0 events, check API key and location parameters

2. **Test with different dates:**
   - Try dates with known events (e.g., Nov 9, 2025)
   - Check if events exist in Ticketmaster for that date

## Next Steps

After deployment:

1. **Test the API endpoints:**
   - `/api/health` - Health check
   - `/api/earnings` - Get earnings with event boost
   - `/api/earnings/week` - Get weekly earnings

2. **Update frontend:**
   - Make sure frontend is pointing to Railway URL
   - Update `API_BASE_URL` in frontend config if needed

3. **Monitor performance:**
   - Check Railway metrics
   - Monitor API response times
   - Check for errors in logs

