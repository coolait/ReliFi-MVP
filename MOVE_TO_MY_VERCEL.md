# Move Deployment to Your Vercel Account

This guide will help you transfer your ReliFi MVP from your friend's Vercel account to your own.

## Step 1: Remove from Friend's Vercel (Optional)

If you have access to your friend's Vercel account:
1. Go to [vercel.com](https://vercel.com) and log into their account
2. Find your project in the dashboard
3. Go to Project Settings → General
4. Scroll down and click "Delete Project" (or just leave it - you can have it on both accounts)

**Note**: You don't actually need to delete it. You can deploy the same GitHub repo to multiple Vercel accounts!

## Step 2: Deploy to Your Vercel Account

### Option A: Using Vercel Dashboard (Recommended)

1. **Sign up/Login**: Go to [vercel.com](https://vercel.com) and sign up or log in with your GitHub account

2. **Import Project**:
   - Click "Add New Project" or "Import Project"
   - Select your GitHub repository (`ReliFi-MVP`)
   - Click "Import"

3. **Configure Project**:
   - **Framework Preset**: Vercel will auto-detect (React)
   - **Root Directory**: Leave as `.` (root)
   - **Build Command**: `cd client && npm install && npm run build`
   - **Output Directory**: `client/build`
   - **Install Command**: `npm install && cd client && npm install`

4. **Add Environment Variables**:
   - Before clicking "Deploy", go to "Environment Variables" section
   - Click "Add" and add:
     - **Name**: `PYTHON_API_URL`
     - **Value**: Your Python API URL (from Railway/Render)
     - **Environment**: Select all (Production, Preview, Development)
   - Click "Save"

5. **Deploy**:
   - Click "Deploy" button
   - Wait for build to complete (usually 2-3 minutes)
   - You'll get a new URL like `https://your-app.vercel.app`

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Logout from friend's account (if logged in)
vercel logout

# Login to YOUR account
vercel login

# Navigate to your project directory
cd /Users/abansal/github/Untitled/ReliFi-MVP

# Deploy to your account
vercel

# When prompted:
# - Set up and deploy? Yes
# - Which scope? Select your account
# - Link to existing project? No (create new)
# - Project name? relifi-mvp (or whatever you want)
# - Directory? . (root)

# Add environment variable
vercel env add PYTHON_API_URL
# Enter your Python API URL when prompted
# Select all environments (Production, Preview, Development)

# Deploy to production
vercel --prod
```

## Step 3: Verify Deployment

1. **Check your new URL**: Visit `https://your-app.vercel.app`
2. **Test health endpoint**: `https://your-app.vercel.app/api/health`
3. **Test earnings endpoint**: 
   ```
   https://your-app.vercel.app/api/earnings/lightweight?location=San%20Francisco&date=2025-01-15&startTime=9:00%20AM&endTime=10:00%20AM
   ```

## Step 4: Update Any Hardcoded URLs (If Needed)

If you have any documentation or links pointing to your friend's Vercel URL, update them to your new URL.

## Step 5: Set Up Custom Domain (Optional)

If you want a custom domain:

1. Go to your project in Vercel dashboard
2. Click "Settings" → "Domains"
3. Add your domain
4. Follow Vercel's DNS configuration instructions

## Troubleshooting

### Issue: Build fails

**Solution**: 
- Check build logs in Vercel dashboard
- Make sure all dependencies are in `package.json` files
- Verify `@vercel/node` and `axios` are in root `package.json`

### Issue: Environment variable not working

**Solution**:
- Go to Project Settings → Environment Variables
- Make sure `PYTHON_API_URL` is set for all environments
- Redeploy after adding environment variables

### Issue: API endpoints return 404

**Solution**:
- Check that `api/` folder structure is correct
- Verify `vercel.json` has correct routing
- Check Vercel Functions tab to see if functions are deployed

## Quick Checklist

- [ ] Logged into YOUR Vercel account
- [ ] Imported GitHub repository
- [ ] Set build configuration
- [ ] Added `PYTHON_API_URL` environment variable
- [ ] Deployed successfully
- [ ] Tested all endpoints
- [ ] Updated any documentation with new URL

## That's It!

Your app is now deployed on your own Vercel account. You can:
- Manage deployments yourself
- View analytics and logs
- Add team members
- Set up custom domains
- Configure environment variables

Your friend's deployment can stay active or be removed - it's up to you both!


