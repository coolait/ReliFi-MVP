# 🔧 Restoring Your .env File

If your `.env` file keeps disappearing, here's how to restore it and prevent it from happening again.

## 📍 Where Your .env File Should Be

Your `.env` file should be located at:
```
client/.env
```

**Important**: This file is intentionally NOT tracked by git (it's in `.gitignore`) because it contains your API keys and secrets.

---

## 🚨 Why .env Files Disappear

Common reasons your `.env` file might disappear:

### 1. **Git Cleanup Commands** ⚠️ MOST COMMON
If you run any of these commands, they can delete untracked files (including `.env`):
```bash
git clean -fd          # Removes untracked files and directories
git reset --hard       # Resets all changes including untracked files
git checkout -- .      # Can sometimes affect untracked files
```

**Solution**: Always check what will be deleted first:
```bash
git clean -fdn         # Preview what will be deleted (dry-run)
```

### 2. **IDE Cleanup**
Some IDEs (VS Code, WebStorm, etc.) have "clean" or "reset" features that remove untracked files.

**Solution**: Be careful with IDE cleanup features. Check settings to exclude `.env` files.

### 3. **Windows-Specific Issues**
- **OneDrive Sync**: If your project is in OneDrive, sync issues can cause file loss
- **Windows Defender**: May quarantine files with "secrets" in them
- **File Permissions**: Permission changes can make files invisible

**Solution**: 
- Exclude `.env` files from antivirus scanning
- Check OneDrive sync settings
- Verify file isn't just hidden (enable "Show hidden files" in Windows)

### 4. **Build/Deployment Processes**
Some build tools clean directories before building.

**Solution**: Check your build scripts in `package.json` - they shouldn't clean `.env` files.

### 5. **Manual Deletion**
You might have accidentally deleted it.

**Solution**: Check your Recycle Bin!

---

## ✅ How to Restore Your .env File

### Step 1: Check if it exists
```powershell
# Windows PowerShell
Test-Path "client\.env"

# If it returns False, the file is missing
```

### Step 2: Copy from example template
```powershell
# Windows PowerShell
Copy-Item "client\.env.example" "client\.env"

# Or manually:
# 1. Open client/.env.example
# 2. Copy all contents
# 3. Create new file: client/.env
# 4. Paste contents
# 5. Fill in your actual API keys
```

### Step 3: Fill in your API keys
Edit `client/.env` and replace all placeholder values with your actual keys:

1. **Firebase keys**: Get from [Firebase Console](https://console.firebase.google.com)
   - Go to Project Settings → Your apps → Firebase SDK snippet
   - Copy each config value

2. **Google Maps API key**: Get from [Google Cloud Console](https://console.cloud.google.com/google/maps-apis/credentials)
   - Enable: Maps JavaScript API, Geocoding API, Geolocation API
   - Create API key
   - Restrict key to your domain/localhost

3. **Google Calendar API** (optional):
   - Get from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create OAuth 2.0 Client ID

### Step 4: Verify it's not tracked by git
```bash
git status
# Should NOT show client/.env in the output
```

---

## 🛡️ Prevent Future Loss

### Option 1: Create a Backup Script
Create a script that backs up your `.env` file (keep backups outside the project):

```powershell
# backup-env.ps1
$backupDir = "$env:USERPROFILE\Documents\ReliFi-Env-Backups"
New-Item -ItemType Directory -Force -Path $backupDir
Copy-Item "client\.env" "$backupDir\.env.backup-$(Get-Date -Format 'yyyy-MM-dd-HHmmss')"
Write-Host "✅ .env backed up to $backupDir"
```

Run this periodically:
```powershell
.\backup-env.ps1
```

### Option 2: Store Keys Securely Elsewhere
Keep a copy of your API keys in a secure password manager (LastPass, 1Password, etc.) so you can quickly restore them.

### Option 3: Use Environment Variables (Alternative)
Instead of `.env` file, you can set environment variables directly:

**Windows PowerShell:**
```powershell
$env:REACT_APP_GOOGLE_MAPS_API_KEY = "your_key_here"
$env:REACT_APP_FIREBASE_API_KEY = "your_key_here"
# ... etc
```

**Windows CMD:**
```cmd
set REACT_APP_GOOGLE_MAPS_API_KEY=your_key_here
set REACT_APP_FIREBASE_API_KEY=your_key_here
```

---

## 🔍 Troubleshooting

### "File exists but I can't see it"
1. Enable "Show hidden files" in Windows Explorer
2. Check if file is actually there:
   ```powershell
   Get-ChildItem -Path "client" -Filter ".env*" -Force
   ```

### "File disappears after git operations"
1. Never run `git clean -fd` without checking first
2. Use `git clean -fdn` to preview
3. Add `.env` to a git "skip-worktree" if needed (not recommended)

### "Can't find my API keys"
1. Check your password manager
2. Check your email for API key confirmations
3. Check your cloud console dashboards (Firebase, Google Cloud)
4. You may need to regenerate keys if they're lost

---

## 📝 Quick Reference

| Location | Purpose |
|----------|---------|
| `client/.env` | **Your actual keys** (DO NOT commit) |
| `client/.env.example` | Template with placeholders (safe to commit) |
| `.gitignore` | Prevents `.env` from being committed |

---

## 🆘 Need Help?

If you've lost your API keys:
1. **Firebase**: Go to Firebase Console → Project Settings → Your apps
2. **Google Maps**: Go to Google Cloud Console → APIs & Services → Credentials
3. **Google Calendar**: Go to Google Cloud Console → APIs & Services → Credentials

You can always regenerate API keys if needed (just update them in your apps).

---

**Remember**: The `.env` file is meant to be local-only. It's normal for it not to be in git. Just make sure you have a way to restore it when needed!

