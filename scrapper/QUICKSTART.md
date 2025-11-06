# Quick Start Guide

Get up and running with the Rideshare Data Scraper in 5 minutes.

## Prerequisites

- Python 3.10+
- PostgreSQL 12+
- 5 minutes

## Installation (One-Command Setup)

```bash
cd scrapper
./setup.sh
```

## Manual Setup (3 Steps)

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Database

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

Update `DATABASE_URL`:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/rideshare_data
```

### 3. Initialize Database

```bash
# Create database
createdb rideshare_data

# Initialize schema
python3 -c "from database.models import init_database; init_database()"
```

## Run Your First Scrape

### Test Single Scraper

```bash
python3 main.py --scrapers "NYC TLC"
```

Expected output:
```
============================================================
STARTING RIDESHARE DATA SCRAPING SESSION
============================================================
Starting scraper: NYC TLC
Successfully fetched 100 records from NYC TLC
Transformed 100 records from NYC TLC
NYC TLC: Successfully processed 100 records
...
```

### Run All Scrapers

```bash
python3 main.py
```

This will scrape all data sources (takes 3-5 minutes).

## View Your Data

### Using Python

```bash
python3 database/queries.py
```

### Using SQL

```bash
psql rideshare_data
```

```sql
-- View latest data
SELECT city, date, active_drivers, total_rides
FROM rideshare_stats
ORDER BY date DESC
LIMIT 10;
```

## Schedule Weekly Updates

### Option 1: Built-in Scheduler

```bash
python3 main.py --schedule
```

Runs every Monday at 2:00 AM (configurable in main.py).

### Option 2: Cron

```bash
crontab -e
```

Add:
```
0 2 * * 1 cd /path/to/scrapper && /path/to/venv/bin/python3 main.py
```

## Common Issues

### Issue: Database connection failed

**Solution:**
```bash
# Check PostgreSQL is running
pg_isready

# Verify credentials in .env file
cat .env
```

### Issue: Module not found

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: PDF parsing errors (California CPUC)

**Solution:**
```bash
# Install Java (required for tabula-py)
# macOS:
brew install java

# Ubuntu:
sudo apt-get install default-jre
```

## Example Queries

### Get Latest Data for All Cities

```python
from database.queries import RideshareQueries

queries = RideshareQueries()
df = queries.get_all_cities_latest()
print(df)
```

### Compare Cities

```python
df = queries.compare_cities(
    ["New York City", "Chicago", "Seattle"],
    metric="total_rides"
)
print(df)
```

### Calculate Growth

```python
growth = queries.get_city_growth_rate("New York City", days=30)
print(f"30-day growth: {growth['ride_growth_percent']:.1f}%")
```

## Next Steps

1. **Explore the data**: Run example queries in [database/queries.py](database/queries.py)
2. **Customize**: Edit scraper parameters in individual scraper files
3. **Extend**: Add new cities or data sources (see [README.md](README.md))
4. **Monitor**: Check logs in `rideshare_scraper.log`

## Documentation

- Full documentation: [README.md](README.md)
- API queries: [database/queries.py](database/queries.py)
- Individual scrapers: [scrapers/](scrapers/)

## Get Help

Check logs for errors:
```bash
tail -f rideshare_scraper.log
```

Test database connection:
```bash
python3 -c "from database.models import get_session; print(get_session())"
```

---

**Time to first data**: ~5 minutes
**Questions?** See README.md for detailed documentation
