# Installation Steps - Fix All Test Failures

Your tests failed because dependencies aren't installed yet. Follow these steps in order:

---

## Step 1: Install Dependencies (REQUIRED)

### Option A: Without Virtual Environment (Simpler)
```bash
cd /Users/abansal/github/Untitled/ReliFi-MVP/scrapper
pip3 install -r requirements.txt
```

### Option B: With Virtual Environment (Recommended)
```bash
cd /Users/abansal/github/Untitled/ReliFi-MVP/scrapper

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Wait for installation to complete (1-2 minutes)**

---

## Step 2: Verify Imports Work

```bash
python3 test_imports.py
```

**Expected Output:**
```
✓ NYC TLC scraper imported
✓ Chicago TNP scraper imported
✓ requests library
✓ pandas library
✓ ALL IMPORTS SUCCESSFUL!
```

If this still fails, run:
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt --force-reinstall
```

---

## Step 3: Test Scrapers (No Database Needed)

```bash
# Test NYC scraper (fastest)
python3 scrapers/nyc_tlc.py
```

**Expected:** You should see "Fetched X records" and sample data

---

## Step 4: Setup PostgreSQL (If You Have It)

### Check if PostgreSQL is installed:
```bash
which psql
```

If not installed:

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Create database:
```bash
createdb rideshare_data
```

### Test connection:
```bash
psql rideshare_data -c "SELECT 1"
```

---

## Step 5: Initialize Database Schema

```bash
python3 -c "from database.models import init_database; init_database()"
```

**Expected:** No errors

---

## Step 6: Run Integration Test

```bash
python3 main.py --scrapers "NYC TLC"
```

**Expected:** Data fetched and inserted successfully

---

## If You Don't Have PostgreSQL

You can still test scrapers without a database:

```bash
# Each scraper works independently
python3 scrapers/nyc_tlc.py
python3 scrapers/chicago_tnp.py
python3 scrapers/seattle_tnc.py
```

These will fetch and display data without storing it.

---

## Quick Fix Commands (Copy-Paste)

```bash
# Navigate to directory
cd /Users/abansal/github/Untitled/ReliFi-MVP/scrapper

# Install dependencies
pip3 install -r requirements.txt

# Test imports
python3 test_imports.py

# Test a scraper (no database needed)
python3 scrapers/nyc_tlc.py
```

---

## Common Issues

### Issue: "pip3: command not found"
**Fix:** Use `pip` instead of `pip3`
```bash
pip install -r requirements.txt
```

### Issue: "Permission denied"
**Fix:** Use `--user` flag
```bash
pip3 install --user -r requirements.txt
```

### Issue: "No module named 'requests'" after install
**Fix:** Check you're using the right Python
```bash
which python3
python3 -m pip install -r requirements.txt
```

### Issue: PostgreSQL not installed
**Fix:** You can test without it! Just run:
```bash
python3 scrapers/nyc_tlc.py
```

---

## Verification Checklist

- [ ] Dependencies installed: `pip3 list | grep requests`
- [ ] Imports work: `python3 test_imports.py`
- [ ] Scraper works: `python3 scrapers/nyc_tlc.py`
- [ ] (Optional) PostgreSQL running: `pg_isready`
- [ ] (Optional) Database exists: `psql -l | grep rideshare_data`

---

## What You Should See

After fixing, run:
```bash
python3 test_imports.py
```

**Success looks like:**
```
✓ NYC TLC scraper imported
✓ Chicago TNP scraper imported
✓ Seattle TNC scraper imported
✓ Boston MassDOT scraper imported
✓ California CPUC scraper imported
✓ Airport reports scraper imported

✓ Database models imported
✓ Query utilities imported

✓ requests library
✓ pandas library
✓ sqlalchemy library
✓ beautifulsoup4 library
✓ pdfplumber library

✓ ALL IMPORTS SUCCESSFUL!
```

---

**Start with Step 1 now!** Once dependencies are installed, everything else will work.
