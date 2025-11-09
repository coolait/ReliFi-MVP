# How to Build Your App

## For Vercel Deployment (Automatic) ✅

**You DON'T need to run the build command manually!**

Vercel automatically runs this command when you deploy:
```bash
cd client && npm install && npm run build
```

It's already configured in your `vercel.json` file. Just:
1. Push your code to GitHub
2. Deploy on Vercel
3. Vercel will build it automatically

---

## If You Want to Test Build Locally (Optional)

If you want to test the build process locally before deploying:

### From Project Root

```bash
# Navigate to your project root
cd /Users/abansal/github/Untitled/ReliFi-MVP

# Run the build command
cd client && npm install && npm run build
```

Or as separate commands:

```bash
# From project root
cd client
npm install
npm run build
```

This will create a `client/build` folder with the production-ready files.

### Verify Build Worked

After building, check that `client/build` folder exists:
```bash
ls -la client/build
```

You should see files like:
- `index.html`
- `static/` folder with CSS and JS files
- `asset-manifest.json`

---

## Quick Reference

| Scenario | Command | Where to Run |
|----------|---------|--------------|
| **Vercel Deployment** | None needed - automatic | N/A |
| **Local Test Build** | `cd client && npm install && npm run build` | Project root |
| **Development Server** | `cd client && npm start` | Project root |

---

## For Vercel: Just Deploy!

When deploying to Vercel:
1. ✅ Make sure your code is pushed to GitHub
2. ✅ Go to Vercel dashboard
3. ✅ Import your repo
4. ✅ Vercel will automatically:
   - Run `npm install && cd client && npm install` (install dependencies)
   - Run `cd client && npm install && npm run build` (build the app)
   - Deploy the `client/build` folder

**You don't need to build locally first!** Vercel does it all for you. 🚀


