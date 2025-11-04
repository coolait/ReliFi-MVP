# Google Calendar Import Setup Guide

This guide will walk you through setting up Google Calendar integration so you can import your calendar and see busy times highlighted in gray on your schedule.

## Step-by-Step Setup

### Step 1: Create/Select a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click the project dropdown at the top (next to "Google Cloud")
4. Either:
   - Select an existing project, OR
   - Click "New Project" → Enter project name (e.g., "ReliFi MVP") → Click "Create"

### Step 2: Enable Google Calendar API

1. In your project, go to **APIs & Services** → **Library** (or search "API Library" in the top search bar)
2. Search for "Google Calendar API"
3. Click on "Google Calendar API"
4. Click the **"Enable"** button
5. Wait for it to enable (you'll see a success message)

### Step 3: Create OAuth 2.0 Client ID (for user authentication)

1. Go to **APIs & Services** → **Credentials**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**
4. If prompted, configure the OAuth consent screen first:
   - Choose **"External"** (unless you have a Google Workspace account)
   - Click **"Create"**
   - Fill in the required fields:
     - **App name**: ReliFi MVP (or your app name)
     - **User support email**: Your email
     - **Developer contact information**: Your email
   - Click **"Save and Continue"**
   - On "Scopes" page, click **"Save and Continue"**
   - On "Test users" page, add your email address, then click **"Save and Continue"**
   - Review and click **"Back to Dashboard"**
5. Back at "Create OAuth client ID":
   - **Application type**: Select **"Web application"**
   - **Name**: ReliFi MVP Client (or any name)
   - **Authorized JavaScript origins**: Click **"+ ADD URI"** and add:
     - `http://localhost:3000`
     - `http://127.0.0.1:3000`
   - **Authorized redirect URIs**: Click **"+ ADD URI"** and add:
     - `http://localhost:3000`
     - `http://127.0.0.1:3000`
   - Click **"Create"**
6. **IMPORTANT**: Copy the **Client ID** (looks like: `123456789-abcdefghijklmnop.apps.googleusercontent.com`)
   - Save this - you'll need it for your `.env` file
   - You can close the popup (we don't need the Client Secret for this)

### Step 4: Create API Key (for Google APIs access)

1. Still in **APIs & Services** → **Credentials**
2. Click **"+ CREATE CREDENTIALS"** → **"API key"**
3. Your API key will be created immediately
4. Click **"Restrict key"** to secure it:
   - **Application restrictions**: Select **"HTTP referrers (web sites)"**
   - Under "Website restrictions", click **"ADD AN ITEM"** and add:
     - `http://localhost:3000/*`
     - `http://127.0.0.1:3000/*`
   - **API restrictions**: Select **"Restrict key"**
   - Under "Select APIs", check:
     - ✅ **Google Calendar API**
     - ✅ **Google Maps JavaScript API** (if you're using maps)
   - Click **"Save"**
5. **IMPORTANT**: Copy the **API Key** (looks like: `AIzaSyAbc123...`)
   - Save this - you'll need it for your `.env` file

### Step 5: Add Credentials to Your `.env` File

1. Open your `client` folder in the project
2. Create a file named `.env` if it doesn't exist (or edit the existing one)
3. Add these two lines (replace with YOUR actual values):

```env
REACT_APP_GOOGLE_API_KEY=YOUR_API_KEY_HERE
REACT_APP_GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE
```

**Example:**
```env
REACT_APP_GOOGLE_API_KEY=AIzaSyAbc123def456ghi789jkl012mno345pqr
REACT_APP_GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
```

4. **Save the file**

### Step 6: Restart Your Development Server

1. Stop your React dev server (Ctrl+C in the terminal where it's running)
2. Start it again:
   ```bash
   cd client
   npm start
   ```
3. The app should reload with the new environment variables

### Step 7: Test the Integration

1. Open your app at `http://localhost:3000`
2. Click the **"📅 Import Gcal"** button in the calendar header
3. You should see a Google sign-in popup
4. Sign in with your Google account
5. Grant permissions when prompted (the app needs read-only access to your calendar)
6. After signing in, your calendar's busy times should appear as **gray blocks** on the calendar

## Troubleshooting

### "Missing Google API credentials" error
- Make sure your `.env` file is in the `client` folder
- Check that the variable names are exactly: `REACT_APP_GOOGLE_API_KEY` and `REACT_APP_GOOGLE_CLIENT_ID`
- Restart your dev server after adding/editing the `.env` file

### "Origin not allowed" error
- Go back to Google Cloud Console → Credentials
- Edit your OAuth 2.0 Client ID
- Make sure `http://localhost:3000` is in "Authorized JavaScript origins"
- Save and wait 1-2 minutes for changes to propagate

### "API key not valid" error
- Check that your API key has "Google Calendar API" enabled in API restrictions
- Make sure the HTTP referrers include `http://localhost:3000/*`

### "Access blocked" or "This app isn't verified"
- This is normal for testing - click "Advanced" → "Go to ReliFi MVP (unsafe)"
- The app is in testing mode, so only test users you added can use it

### Calendar not showing busy times
- Check the browser console (F12) for errors
- Make sure you granted calendar read permissions
- Try clicking "Import Gcal" again after signing in

## Security Notes

- **Never commit your `.env` file to Git** - it should already be in `.gitignore`
- The API key is restricted to localhost, so it's safe for development
- For production, you'll need to:
  - Add your production domain to authorized origins
  - Update the OAuth consent screen
  - Possibly submit for verification if you want public access

## Next Steps

Once this works, you can:
- See your busy times highlighted in gray on the calendar
- Plan gig shifts around your existing commitments
- The busy times update when you click "Import Gcal" for different weeks

