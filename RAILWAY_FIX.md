# Fix Railway Deployment - Python API

Railway is trying to use Node.js instead of Python. Here's how to fix it:

## Quick Fix Steps

### Step 1: Update Railway Service Settings

1. Go to your Railway project dashboard
2. Click on your service (the one that's failing)
3. Go to **Settings** tab
4. Scroll down to **Build & Deploy** section

### Step 2: Configure Build Settings

Update these settings:

- **Root Directory**: Set to `scrapper` (this is critical!)
- **Build Command**: Leave empty or set to `pip install -r requirements.txt`
- **Start Command**: `python api_server.py`

### Step 3: Force Python Detection

Railway should auto-detect Python from `requirements.txt`, but if it doesn't:

1. In Railway dashboard, go to **Variables** tab
2. Add environment variable:
   - **Name**: `NIXPACKS_PYTHON_VERSION`
   - **Value**: `3.10`

### Step 4: Redeploy

1. Go to **Deployments** tab
2. Click **Redeploy** or push a new commit to trigger a rebuild

## Alternative: Delete and Recreate Service

If the above doesn't work:

1. **Delete the current service** in Railway
2. **Create a new service**:
   - Click "New" → "GitHub Repo"
   - Select your `ReliFi-MVP` repository
   - **IMPORTANT**: When configuring, set:
     - **Root Directory**: `scrapper`
     - **Start Command**: `python api_server.py`
3. Railway should now detect Python automatically

## Verify Configuration

After redeploying, check the build logs. You should see:
- ✅ `Installing Python dependencies...`
- ✅ `pip install -r requirements.txt`
- ❌ NOT `npm ci` or any Node.js commands

## Files I Created

I've added these files to help Railway detect Python:
- `scrapper/railway.toml` - Railway configuration
- `scrapper/Procfile` - Process file for Railway
- `scrapper/runtime.txt` - Python version specification

These files should help Railway detect Python correctly.

## Still Having Issues?

If Railway still tries to use Node.js:

1. Make sure **Root Directory** is set to `scrapper` (not `.` or root)
2. Check that `scrapper/requirements.txt` exists
3. Try adding a `.railwayignore` file in the root to ignore Node.js files:

```bash
# In root directory, create .railwayignore
node_modules/
package.json
package-lock.json
client/
server/
```

## Test After Deployment

Once deployed, test your API:
```
https://your-app.railway.app/api/health
```

This should return: `{"status": "OK", "service": "Earnings Forecaster API"}`

