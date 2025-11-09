# Railway Setup - Python API Only

## Important: Railway vs Vercel

- **Railway** = Python API (in `scrapper/` folder) - NO Node.js build needed!
- **Vercel** = Frontend React app - Uses the build command

---

## Railway Configuration (Python API)

In your Railway dashboard, configure your service like this:

### Settings to Change:

1. **Root Directory**: `scrapper`
   - This tells Railway to look in the `scrapper` folder, not the root
   - This is the MOST IMPORTANT setting!

2. **Build Command**: Leave **EMPTY** or use:
   ```
   pip install -r requirements.txt
   ```
   - Railway will auto-detect this from `requirements.txt`
   - DO NOT use `cd client && npm install && npm run build` (that's for Vercel!)

3. **Start Command**: 
   ```
   python api_server.py
   ```

### Step-by-Step in Railway Dashboard:

1. Go to your Railway project
2. Click on your service (the one showing the npm error)
3. Click **Settings** tab
4. Scroll to **Build & Deploy** section
5. Set:
   - **Root Directory**: `scrapper` ⚠️ (This fixes the npm error!)
   - **Build Command**: (leave empty or `pip install -r requirements.txt`)
   - **Start Command**: `python api_server.py`
6. Click **Save**
7. Go to **Deployments** tab
8. Click **Redeploy**

---

## What Should Happen

After setting Root Directory to `scrapper`, Railway should:

✅ Detect Python from `scrapper/requirements.txt`
✅ Run: `pip install -r requirements.txt`
✅ Start: `python api_server.py`
❌ NOT run: `npm ci` or any Node.js commands

---

## If It Still Doesn't Work

### Option 1: Delete and Recreate Service

1. Delete the current service in Railway
2. Create new service:
   - Click "New" → "GitHub Repo"
   - Select `ReliFi-MVP`
   - **IMPORTANT**: Set Root Directory to `scrapper` during setup
   - Railway should auto-detect Python

### Option 2: Check Build Logs

After redeploying, check the build logs. You should see:
- ✅ "Detected Python"
- ✅ "Installing dependencies from requirements.txt"
- ❌ NOT "npm ci" or "npm install"

---

## Quick Checklist

- [ ] Root Directory = `scrapper` (not `.` or empty)
- [ ] Start Command = `python api_server.py`
- [ ] Build Command = empty or `pip install -r requirements.txt`
- [ ] Redeployed after changes
- [ ] Checked build logs - should see Python, not Node.js

---

## Test After Deployment

Once Railway deploys successfully, test:
```
https://your-app.railway.app/api/health
```

Should return: `{"status": "OK", "service": "Earnings Forecaster API"}`

---

## Summary

**For Railway (Python API):**
- ❌ DON'T use: `cd client && npm install && npm run build`
- ✅ DO use: Root Directory = `scrapper`, Start = `python api_server.py`

**For Vercel (Frontend):**
- ✅ DO use: `cd client && npm install && npm run build` (automatic)


