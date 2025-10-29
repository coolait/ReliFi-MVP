# Testing Guide

Complete guide for testing the Rideshare Data Scraper system.

## Quick Test (30 seconds)

```bash
# Test if all imports work
python3 -c "from scrapers import *; from database import *; print('✓ All imports successful')"
```

---

## Testing Options

### 1. Test Individual Scrapers (Recommended First Step)

Each scraper can run independently without database setup:

#### Test NYC TLC Scraper
```bash
cd scrapper
python3 scrapers/nyc_tlc.py
```

**Expected Output:**
```
INFO - Fetching NYC TLC data (limit=100, offset=0)
INFO - Successfully fetched 100 records from NYC TLC
INFO - Transformed 100 records from NYC TLC
INFO - NYC TLC scraper completed: 100 records

Fetched 100 records

Sample record:
{'city': 'New York City', 'state': 'NY', 'date': datetime.date(2024, 10, 1), ...}
```

#### Test Other Scrapers
```bash
# Chicago
python3 scrapers/chicago_tnp.py

# Seattle
python3 scrapers/seattle_tnc.py

# Boston (may be slow, downloads CSVs)
python3 scrapers/boston_massdot.py

# California (may be slow, parses PDFs)
python3 scrapers/california_cpuc.py

# Airports
python3 scrapers/airport_reports.py
```

**What This Tests:**
- HTTP requests to APIs/websites
- Data parsing and transformation
- Error handling
- No database required

---

### 2. Test Database Connection

#### Option A: Quick Connection Test
```bash
python3 -c "
from database.models import get_engine, get_session
try:
    engine = get_engine()
    session = get_session(engine)
    print('✓ Database connection successful')
    session.close()
except Exception as e:
    print(f'✗ Database connection failed: {e}')
"
```

#### Option B: Test Database Schema Creation
```bash
python3 -c "
from database.models import init_database
try:
    engine = init_database()
    print('✓ Database schema created successfully')
except Exception as e:
    print(f'✗ Schema creation failed: {e}')
"
```

**Expected Output:**
```
✓ Database schema created successfully
```

#### Option C: Verify Tables Exist
```bash
psql rideshare_data -c "\dt"
```

**Expected Output:**
```
                List of relations
 Schema |       Name        | Type  |  Owner
--------+-------------------+-------+----------
 public | data_fetch_log    | table | postgres
 public | rideshare_stats   | table | postgres
```

---

### 3. Test Complete System (Without Data)

Run the main script with a dry-run approach:

```bash
# This will attempt to fetch data but won't fail if no data is available
python3 main.py 2>&1 | head -50
```

**What to Look For:**
- "Initializing database..." ✓
- "Database initialized successfully" ✓
- "Starting scraper: NYC TLC" ✓
- No Python errors or stack traces

---

### 4. Test Single Scraper with Database

Test one scraper end-to-end:

```bash
# Test NYC TLC only (fastest)
python3 main.py --scrapers "NYC TLC"
```

**Expected Output:**
```
============================================================
STARTING RIDESHARE DATA SCRAPING SESSION
============================================================
Starting scraper: NYC TLC
Fetching NYC TLC data (limit=10000, offset=0)
Successfully fetched 100 records from NYC TLC
Transformed 100 records from NYC TLC
NYC TLC: Successfully processed 100 records

============================================================
SCRAPING SUMMARY
============================================================
✓ NYC TLC: 100 fetched, 100 inserted, 0 updated (8.5s)
============================================================
Total: 100 records fetched, 100 inserted, 0 updated
Scrapers: 1 successful, 0 failed
============================================================
```

#### Verify Data Was Inserted
```bash
psql rideshare_data -c "SELECT city, date, active_drivers, total_rides FROM rideshare_stats LIMIT 5;"
```

**Expected Output:**
```
     city      |    date    | active_drivers | total_rides
---------------+------------+----------------+-------------
 New York City | 2024-10-01 |          45000 |     1500000
 New York City | 2024-09-01 |          44500 |     1450000
 ...
```

---

### 5. Test Query Utilities

```bash
python3 database/queries.py
```

**Expected Output:**
```
============================================================
EXAMPLE QUERIES
============================================================

1. Latest data for all cities:
     city      state    date    active_drivers  total_rides
0    New York City   NY   2024-10-01     45000     1500000
1    Chicago         IL   2024-10-01     18000      750000
...

2. NYC data (last 30 days):
...

3. Monthly totals (current month):
...
```

---

## Step-by-Step Testing Process

### Phase 1: Environment Setup (5 minutes)

```bash
# 1. Check Python version
python3 --version
# Should be 3.10 or higher

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installations
pip list | grep -E "requests|pandas|sqlalchemy|beautifulsoup4|pdfplumber"
```

**Expected:** All packages shown with version numbers

---

### Phase 2: Database Setup (2 minutes)

```bash
# 1. Create database
createdb rideshare_data

# 2. Verify it exists
psql -l | grep rideshare_data

# 3. Configure .env
cp .env.example .env
echo "DATABASE_URL=postgresql://postgres:password@localhost:5432/rideshare_data" >> .env

# 4. Initialize schema
python3 -c "from database.models import init_database; init_database()"

# 5. Verify tables
psql rideshare_data -c "\dt"
```

**Expected:** Two tables (rideshare_stats, data_fetch_log)

---

### Phase 3: Scraper Testing (10 minutes)

```bash
# Test each scraper individually
echo "Testing NYC TLC..."
python3 scrapers/nyc_tlc.py > /tmp/nyc_test.log 2>&1
echo "Result: $(tail -1 /tmp/nyc_test.log)"

echo "Testing Chicago..."
python3 scrapers/chicago_tnp.py > /tmp/chicago_test.log 2>&1
echo "Result: $(tail -1 /tmp/chicago_test.log)"

# Check for errors
if grep -i "error\|traceback" /tmp/nyc_test.log; then
    echo "NYC scraper has errors"
else
    echo "✓ NYC scraper OK"
fi
```

---

### Phase 4: Integration Testing (5 minutes)

```bash
# Run full system
python3 main.py

# Check logs
tail -20 rideshare_scraper.log

# Verify data
psql rideshare_data -c "
SELECT
    data_source,
    COUNT(*) as records,
    MIN(date) as earliest,
    MAX(date) as latest
FROM rideshare_stats
GROUP BY data_source;
"
```

---

## Troubleshooting Tests

### Test 1: Database Connectivity

```python
# Save as test_db.py
from database.models import get_engine, get_session

def test_database():
    try:
        engine = get_engine()
        print("✓ Engine created")

        session = get_session(engine)
        print("✓ Session created")

        # Try a simple query
        result = session.execute("SELECT 1")
        print("✓ Query executed")

        session.close()
        print("✓ All database tests passed")
        return True

    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database()
```

Run:
```bash
python3 test_db.py
```

---

### Test 2: API Connectivity

```python
# Save as test_apis.py
import requests

apis = {
    'NYC TLC': 'https://data.cityofnewyork.us/resource/gnke-dk5s.json?$limit=1',
    'Chicago': 'https://data.cityofchicago.org/resource/m6dm-c72p.json?$limit=1',
    'Seattle': 'https://data.seattle.gov/resource/4j8s-v8vy.json?$limit=1'
}

for name, url in apis.items():
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✓ {name} API accessible")
        else:
            print(f"✗ {name} API returned {response.status_code}")
    except Exception as e:
        print(f"✗ {name} API failed: {e}")
```

Run:
```bash
python3 test_apis.py
```

---

### Test 3: Import Check

```python
# Save as test_imports.py
def test_imports():
    try:
        print("Testing imports...")

        from scrapers.nyc_tlc import NYCTLCScraper
        print("✓ NYC TLC scraper")

        from scrapers.chicago_tnp import ChicagoTNPScraper
        print("✓ Chicago TNP scraper")

        from scrapers.seattle_tnc import SeattleTNCScraper
        print("✓ Seattle TNC scraper")

        from scrapers.boston_massdot import BostonMassDOTScraper
        print("✓ Boston MassDOT scraper")

        from scrapers.california_cpuc import CaliforniaCPUCScraper
        print("✓ California CPUC scraper")

        from scrapers.airport_reports import AirportReportsScraper
        print("✓ Airport reports scraper")

        from database.models import RideshareStats, DataFetchLog
        print("✓ Database models")

        from database.queries import RideshareQueries
        print("✓ Query utilities")

        print("\n✓ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n✗ Import failed: {e}")
        return False

if __name__ == "__main__":
    test_imports()
```

Run:
```bash
python3 test_imports.py
```

---

## Quick Diagnostic Script

Save this as `diagnose.sh`:

```bash
#!/bin/bash
echo "===== RIDESHARE SCRAPER DIAGNOSTICS ====="
echo ""

echo "1. Python Version:"
python3 --version
echo ""

echo "2. PostgreSQL Status:"
pg_isready
echo ""

echo "3. Database Exists:"
psql -l | grep rideshare_data
echo ""

echo "4. Virtual Environment:"
if [ -d "venv" ]; then
    echo "✓ venv exists"
else
    echo "✗ venv not found"
fi
echo ""

echo "5. Dependencies Installed:"
pip show requests pandas sqlalchemy > /dev/null 2>&1 && echo "✓ Core deps OK" || echo "✗ Install deps"
echo ""

echo "6. Database Tables:"
psql rideshare_data -c "\dt" 2>/dev/null || echo "✗ Tables not created"
echo ""

echo "7. Import Test:"
python3 -c "from scrapers import *; from database import *" 2>/dev/null && echo "✓ Imports OK" || echo "✗ Import errors"
echo ""

echo "8. Log File:"
if [ -f "rideshare_scraper.log" ]; then
    echo "✓ Log file exists ($(wc -l < rideshare_scraper.log) lines)"
else
    echo "○ No log file yet (run scraper first)"
fi
echo ""

echo "===== END DIAGNOSTICS ====="
```

Make executable and run:
```bash
chmod +x diagnose.sh
./diagnose.sh
```

---

## Expected Test Results Summary

| Test | Expected Result | Time |
|------|----------------|------|
| NYC TLC Scraper | 50-100 records fetched | 5-10s |
| Chicago Scraper | 50-100 records fetched | 10-15s |
| Seattle Scraper | 50-100 records fetched | 5-10s |
| Database Init | Tables created | 1s |
| Full System Run | 200+ records total | 3-5min |

---

## Common Issues & Solutions

### Issue: ModuleNotFoundError

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Issue: Database connection refused

**Solution:**
```bash
# Check PostgreSQL is running
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Linux

# Start if needed
brew services start postgresql        # macOS
sudo systemctl start postgresql       # Linux

# Test connection
psql -U postgres -c "SELECT 1"
```

---

### Issue: No records fetched

**Possible Causes:**
1. API rate limiting (wait a few minutes)
2. Network connectivity (check internet)
3. API endpoint changed (check URLs in scrapers)

**Debug:**
```bash
# Test API directly
curl "https://data.cityofnewyork.us/resource/gnke-dk5s.json?$limit=1"
```

---

### Issue: PDF parsing errors (California)

**Solution:**
```bash
# Install Java (required for tabula-py)
# macOS:
brew install java

# Ubuntu:
sudo apt-get install default-jre

# Verify:
java -version
```

---

## Minimal Working Test

If you just want to verify the system works:

```bash
# 1. Setup
cd scrapper
source venv/bin/activate  # if using venv
createdb rideshare_data
python3 -c "from database.models import init_database; init_database()"

# 2. Test one scraper
python3 main.py --scrapers "NYC TLC"

# 3. Verify data
psql rideshare_data -c "SELECT COUNT(*) FROM rideshare_stats;"

# Should show a number > 0
```

**If this works, your system is fully functional!**

---

## Next Steps After Testing

Once all tests pass:

1. **Run full scraper**: `python3 main.py`
2. **Explore data**: `python3 database/queries.py`
3. **Setup scheduling**: `python3 main.py --schedule`
4. **Monitor logs**: `tail -f rideshare_scraper.log`

---

## Need Help?

Check logs for detailed error messages:
```bash
tail -100 rideshare_scraper.log
```

Or run with verbose output:
```bash
python3 main.py 2>&1 | tee test_output.log
```
