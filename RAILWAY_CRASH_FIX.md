# Fix Railway Crash Issues

I've fixed the port issue, but here are common causes and solutions:

## ✅ Fix Applied: Port Configuration

I updated `api_server.py` to use Railway's `PORT` environment variable instead of hardcoded port 5002.

**What changed:**
- Now reads `PORT` from environment (Railway provides this)
- Falls back to 5002 for local development
- Disables debug mode in production

## Common Crash Causes & Fixes

### 1. Check Railway Logs

First, check what the actual error is:

1. Go to Railway dashboard
2. Click your service
3. Go to **Deployments** tab
4. Click on the latest deployment
5. Check **Logs** tab

Look for error messages like:
- `ModuleNotFoundError` - Missing dependency
- `ImportError` - Can't import a module
- `Port already in use` - Port conflict (should be fixed now)
- `Database connection failed` - Database issue

### 2. Missing Dependencies

If you see `ModuleNotFoundError`, check `requirements.txt`:

```bash
# Make sure all dependencies are listed
cd scrapper
cat requirements.txt
```

Common missing ones:
- `gunicorn` - Production WSGI server (recommended for Railway)

### 3. Add Gunicorn for Production

Railway works better with a production WSGI server. Update `requirements.txt`:

```txt
gunicorn>=21.2.0
```

Then update Railway **Start Command** to:
```
gunicorn --bind 0.0.0.0:$PORT api_server:app
```

Or keep using Python directly (should work now with the port fix).

### 4. Import Errors

If you see import errors, check:
- All files exist in `scrapper/` directory
- `config.py` exists and is valid
- `scrape.py` and `delivery_forecaster.py` exist

### 5. Database Connection Issues

If your app tries to connect to a database:
- Make sure database URL is in Railway environment variables
- Or disable database features if not needed for MVP

## Quick Fix Steps

1. **Commit the port fix:**
   ```bash
   git add scrapper/api_server.py
   git commit -m "Fix port configuration for Railway"
   git push
   ```

2. **Check Railway settings:**
   - Root Directory: `scrapper`
   - Start Command: `python api_server.py`
   - Build Command: (empty or `pip install -r requirements.txt`)

3. **Redeploy:**
   - Railway should auto-deploy on push
   - Or manually click "Redeploy" in Railway dashboard

4. **Check logs:**
   - Go to Deployments → Latest → Logs
   - Look for the actual error message

## Test After Fix

Once deployed, test:
```
https://your-app.railway.app/api/health
```

Should return: `{"status": "OK", "service": "Earnings Forecaster API"}`

## If Still Crashing

Share the error from Railway logs and I can help fix it!

Common things to check:
- [ ] Port fix is deployed (check logs for "Starting server on port...")
- [ ] All dependencies installed (check for ModuleNotFoundError)
- [ ] Root Directory is `scrapper`
- [ ] Start Command is `python api_server.py`


