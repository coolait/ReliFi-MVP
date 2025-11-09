# Deployment Guide - Make Your App Public

This guide will walk you through deploying your ReliFi MVP so others can access it online.

## Overview

Your app has 3 components that need to be deployed:

1. **Frontend (React)** → Deploy to **Vercel** (free)
2. **Node.js API** → Already converted to Vercel serverless functions (in `api/` folder)
3. **Python Scraper API** → Deploy to **Railway** or **Render** (free tier available)

---

## Step 1: Deploy Python API (Required)

The Python API provides real earnings data. You need to deploy it separately since Vercel doesn't support Python.

### Option A: Railway (Recommended - Easiest)

1. **Sign up**: Go to [railway.app](https://railway.app) and sign up with GitHub
2. **Create project**: Click "New Project" → "Deploy from GitHub repo"
3. **Select your repo**: Choose `ReliFi-MVP`
4. **Configure service**:
   - Root Directory: Set to `scrapper`
   - Start Command: `python api_server.py`
   - Railway will auto-detect Python and install dependencies
5. **Get URL**: Once deployed, Railway gives you a URL like `https://your-app.railway.app`
   - Copy this URL - you'll need it in Step 3

### Option B: Render (Alternative)

1. **Sign up**: Go to [render.com](https://render.com) and sign up
2. **Create Web Service**: Click "New" → "Web Service"
3. **Connect GitHub**: Select your `ReliFi-MVP` repository
4. **Configure**:
   - Name: `relifi-python-api`
   - Root Directory: `scrapper`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python api_server.py`
5. **Deploy**: Click "Create Web Service"
6. **Get URL**: Copy the URL (e.g., `https://your-app.onrender.com`)

---

## Step 2: Push Code to GitHub (If Not Already)

If your code isn't on GitHub yet:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ReliFi-MVP.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy Frontend + API to Vercel

### Method 1: Using Vercel Dashboard (Easiest)

1. **Sign up**: Go to [vercel.com](https://vercel.com) and sign up with GitHub
2. **Import project**: Click "Add New Project" → Import your `ReliFi-MVP` repository
3. **Configure**:
   - Framework Preset: Vercel will auto-detect (React)
   - Root Directory: Leave as `.` (root)
   - Build Command: `cd client && npm install && npm run build`
   - Output Directory: `client/build`
   - Install Command: `npm install && cd client && npm install`
4. **Add Environment Variable**:
   - Go to "Environment Variables" section
   - Add: `PYTHON_API_URL` = `https://your-app.railway.app` (use the URL from Step 1)
5. **Deploy**: Click "Deploy"
6. **Done!**: Vercel will give you a URL like `https://your-app.vercel.app`

### Method 2: Using Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy (first time - will ask questions)
vercel

# Set environment variable
vercel env add PYTHON_API_URL
# When prompted, enter: https://your-app.railway.app

# Deploy to production
vercel --prod
```

---

## Step 4: Verify Everything Works

Your frontend is already configured correctly! The `client/src/config/api.ts` file automatically uses:
- `http://localhost:5001` in development
- Relative URLs (your Vercel domain) in production

So no changes needed! 🎉

### Test Your Deployment

1. **Visit your Vercel URL**: `https://your-app.vercel.app`
2. **Test the health endpoint**: `https://your-app.vercel.app/api/health`
3. **Test earnings endpoint**: `https://your-app.vercel.app/api/earnings/lightweight?location=San%20Francisco&date=2025-01-15&startTime=9:00%20AM&endTime=10:00%20AM`

---

## Quick Reference: Deployment URLs

After deployment, you'll have:

- **Frontend + API**: `https://your-app.vercel.app` (from Vercel)
- **Python API**: `https://your-app.railway.app` (from Railway/Render)

The frontend automatically connects to both!

---

## Troubleshooting

### Issue: "Python API not available" errors

**Solution**: 
- Check that `PYTHON_API_URL` environment variable is set in Vercel
- Verify your Python API is running and accessible
- Test the Python API directly: `https://your-python-api.railway.app/api/health`

### Issue: Build fails on Vercel

**Solution**:
- Check Vercel build logs for specific errors
- Ensure all dependencies are in `package.json` files
- Make sure `@vercel/node` and `axios` are in root `package.json`

### Issue: API endpoints return 404

**Solution**:
- Verify `api/` folder structure matches Vercel's expectations
- Check that `vercel.json` has correct routing
- Ensure TypeScript files in `api/` are properly formatted

### Issue: Frontend can't connect to API

**Solution**:
- Check browser console for CORS errors
- Verify API endpoints are using correct URLs
- Make sure environment variables are set in Vercel dashboard

---

## Cost Breakdown

- **Vercel**: Free tier includes:
  - 100GB bandwidth/month
  - Unlimited serverless function invocations
  - Perfect for MVP!

- **Railway**: Free tier includes:
  - $5 credit/month (usually enough for MVP)
  - Auto-sleeps after inactivity (wakes on first request)

- **Render**: Free tier available but:
  - May sleep after 15 minutes of inactivity
  - Takes ~30 seconds to wake up

**Recommendation**: Use Railway for Python API (more reliable, faster wake-up)

---

## Next Steps After Deployment

1. ✅ Share your Vercel URL with others
2. ✅ Set up a custom domain (optional - Vercel supports this)
3. ✅ Monitor usage in Vercel dashboard
4. ✅ Check Python API logs in Railway/Render dashboard

---

## Summary Checklist

- [ ] Deploy Python API to Railway/Render
- [ ] Copy Python API URL
- [ ] Deploy frontend to Vercel
- [ ] Add `PYTHON_API_URL` environment variable in Vercel
- [ ] Test all endpoints
- [ ] Share your app URL! 🚀

---

## Need Help?

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs

Your app should now be live and accessible to anyone with the URL!
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
read_file
