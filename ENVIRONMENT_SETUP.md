# Environment Setup Guide

## 🔒 Security Notice

**IMPORTANT**: Never commit `.env` files to git! They contain sensitive API keys and credentials.

---

## Initial Setup

### 1. Copy the example file

```bash
cd client
cp .env.example .env
```

### 2. Fill in your API keys

Edit `client/.env` and replace all placeholder values:

```bash
# Firebase Configuration (from Firebase Console)
REACT_APP_FIREBASE_API_KEY=your_actual_firebase_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
REACT_APP_FIREBASE_APP_ID=1:123456789:web:abc123
REACT_APP_FIREBASE_MEASUREMENT_ID=G-ABCD1234

# Leave empty for production
REACT_APP_API_BASE_URL=

# Google Maps API Key (from Google Cloud Console)
REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSyABC123...your_actual_key
```

### 3. Verify it's not tracked by git

```bash
git status
# Should NOT show client/.env in changes
```

---

## Getting API Keys

### Firebase Configuration

1. Go to: https://console.firebase.google.com
2. Select your project
3. Click Settings (gear icon) → Project settings
4. Scroll to "Your apps" section
5. Copy each config value

### Google Maps API Key

1. Go to: https://console.cloud.google.com/google/maps-apis
2. Create/select project
3. Enable APIs:
   - Maps JavaScript API
   - Geocoding API
   - Geolocation API
4. Create API key
5. Restrict key:
   - HTTP referrers: `http://localhost:*`, `https://your-domain.com/*`
   - API restrictions: Only the 3 APIs above

---

## Verification

### Check if .env is ignored

```bash
# This should return nothing
git ls-files | grep "client/.env"

# If it returns "client/.env", your keys are still tracked!
# Run: git rm --cached client/.env
```

### Check if values are loaded

```bash
cd client
npm start

# In browser console:
console.log(process.env.REACT_APP_GOOGLE_MAPS_API_KEY?.substring(0, 10))
# Should show first 10 chars of your key
```

---

## Security Checklist

- [ ] `client/.env` exists locally
- [ ] `client/.env` has real API keys
- [ ] `client/.env` is NOT in git (`git status` doesn't show it)
- [ ] `client/.env.example` exists and has placeholder values
- [ ] `.gitignore` includes `.env` files
- [ ] Committed changes don't include secrets

---

## If You Already Committed Secrets

If you accidentally committed API keys:

### Option A: Remove from most recent commit (if not pushed)

```bash
# Remove .env from git
git rm --cached client/.env

# Amend the commit
git commit --amend --no-edit

# Add to .gitignore
echo "client/.env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
```

### Option B: Remove from git history (if pushed)

⚠️ **WARNING**: This rewrites history. Coordinate with team!

```bash
# Remove from all history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch client/.env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (DANGER!)
git push origin --force --all
```

### Option C: Rotate all keys (SAFEST)

1. **Rotate Firebase API key**:
   - Firebase Console → Project Settings → Web API Key
   - Create new key, delete old one

2. **Rotate Google Maps API key**:
   - Google Cloud Console → Credentials
   - Create new key, delete old one

3. **Update your local `.env`** with new keys

4. **Remove from git**:
   ```bash
   git rm --cached client/.env
   git commit -m "Remove .env from tracking"
   git push
   ```

---

## GitHub Security Features

### Enable Secret Scanning

1. Go to your GitHub repo
2. Settings → Code security and analysis
3. Enable:
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Secret scanning

### .gitignore Best Practices

Your `.gitignore` should include:

```
# Environment variables
.env
.env.local
.env.*.local
client/.env
server/.env
scrapper/.env

# Keep templates
!.env.example
!*.env.example
```

---

## Team Setup

When a new developer joins:

1. **Clone repo**:
   ```bash
   git clone https://github.com/your-org/ReliFi-MVP.git
   cd ReliFi-MVP
   ```

2. **Copy example files**:
   ```bash
   cp client/.env.example client/.env
   ```

3. **Get credentials** from team lead (via secure channel)

4. **Fill in `.env`** with real values

5. **Verify**:
   ```bash
   git status
   # Should NOT show client/.env
   ```

---

## Production Deployment

### Environment Variables in Production

**DO NOT** use `.env` files in production!

Instead, use platform environment variables:

**Vercel**:
```bash
Settings → Environment Variables
Add: REACT_APP_GOOGLE_MAPS_API_KEY = AIzaSy...
```

**Netlify**:
```bash
Site settings → Environment → Environment variables
Add: REACT_APP_GOOGLE_MAPS_API_KEY = AIzaSy...
```

**Heroku**:
```bash
heroku config:set REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSy...
```

**AWS/GCP**:
- Use Secrets Manager or Parameter Store
- Never hardcode in Dockerfile or config files

---

## Troubleshooting

### "My app can't find environment variables"

**Check**:
1. File is named `.env` (not `.env.txt`)
2. File is in `client/` directory
3. Variables start with `REACT_APP_`
4. React app was restarted after editing `.env`

### ".env is showing in git status"

**Fix**:
```bash
git rm --cached client/.env
git add .gitignore
git commit -m "Remove .env from tracking"
```

### "I pushed secrets to GitHub"

**Fix**:
1. Rotate ALL API keys immediately
2. Follow "Option C: Rotate all keys" above
3. Enable GitHub secret scanning

---

## Summary

✅ **DO**:
- Use `.env.example` with placeholder values (commit this)
- Keep `.env` files local only (never commit)
- Add `.env` to `.gitignore`
- Use platform environment variables in production
- Rotate keys if exposed

❌ **DON'T**:
- Commit `.env` files
- Hardcode API keys in source code
- Share `.env` files via Slack/Email
- Push secrets to public repos
- Reuse same keys across projects

---

## Quick Commands

```bash
# Setup new environment
cp client/.env.example client/.env
nano client/.env  # Fill in your keys

# Check if .env is ignored
git status | grep ".env"  # Should return nothing

# Verify keys are loaded
npm start
# Check browser console for loaded env vars

# Remove .env if accidentally tracked
git rm --cached client/.env
git commit -m "Remove .env from tracking"
```

---

**Your API keys are now secure!** 🔒
