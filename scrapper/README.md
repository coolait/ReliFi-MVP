# Rideshare Data Scraper

A production-ready Python system for automatically downloading and updating rideshare datasets across multiple cities in the United States. This tool aggregates data from various official sources including city APIs, state government reports, and airport statistics.

## Features

- **Multi-City Support**: NYC, Chicago, Seattle, Boston, San Francisco, Los Angeles, and other California cities
- **Multiple Data Sources**: APIs, CSVs, Excel files, and PDFs
- **Automated Scheduling**: Weekly updates via built-in scheduler or cron
- **PostgreSQL Storage**: Standardized schema for easy querying
- **Comprehensive Logging**: Track success/failure of all operations
- **Production-Ready**: Error handling, retries, and data quality indicators

## Data Sources

| Source | Cities | Type | URL |
|--------|--------|------|-----|
| NYC TLC API | New York City | Socrata API | https://data.cityofnewyork.us/resource/gnke-dk5s.json |
| Chicago TNP API | Chicago | Socrata API | https://data.cityofchicago.org/resource/m6dm-c72p.json |
| Seattle TNC API | Seattle | Socrata API | https://data.seattle.gov/resource/4j8s-v8vy.json |
| Boston MassDOT | Boston | CSV/Excel | https://massdot.state.ma.us |
| California CPUC | CA Cities | PDF Reports | https://www.cpuc.ca.gov/tncinfo |
| LAX/SFO Reports | LA, SF | Excel/PDF | Airport websites |

## Architecture

```
scrapper/
├── main.py                    # Main orchestration script
├── scrapers/                  # Modular scrapers
│   ├── nyc_tlc.py            # NYC TLC scraper
│   ├── chicago_tnp.py        # Chicago TNP scraper
│   ├── seattle_tnc.py        # Seattle TNC scraper
│   ├── boston_massdot.py     # Boston MassDOT scraper
│   ├── california_cpuc.py    # California CPUC scraper
│   └── airport_reports.py    # LAX/SFO scraper
├── database/                  # Database models & queries
│   ├── models.py             # SQLAlchemy models
│   └── queries.py            # Example queries
├── requirements.txt           # Python dependencies
├── .env.example              # Environment configuration
└── README.md                 # This file
```

## Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### Step 1: Clone Repository

```bash
cd /Users/abansal/github/Untitled/ReliFi-MVP/scrapper
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up PostgreSQL Database

```bash
# Create database
createdb rideshare_data

# Or using psql:
psql -U postgres
CREATE DATABASE rideshare_data;
\q
```

### Step 5: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

Update the `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://username:password@localhost:5432/rideshare_data
```

### Step 6: Initialize Database Schema

```bash
python3 -c "from database.models import init_database; init_database()"
```

## Usage

### Run All Scrapers Once

```bash
python3 main.py
```

### Run Specific Scrapers

```bash
python3 main.py --scrapers "NYC TLC" "Chicago TNP"
```

Available scrapers:
- `NYC TLC`
- `Chicago TNP`
- `Seattle TNC`
- `Boston MassDOT`
- `California CPUC`
- `Airport Reports`

### Run on Weekly Schedule

```bash
python3 main.py --schedule
```

This runs every Monday at 2:00 AM by default. To customize, edit the schedule in [main.py](main.py:296).

### Use with Cron

Add to your crontab for weekly execution:

```bash
crontab -e
```

Add this line (runs every Monday at 2:00 AM):
```
0 2 * * 1 cd /path/to/scrapper && /path/to/venv/bin/python3 main.py >> scraper_cron.log 2>&1
```

## Database Schema

### Main Table: `rideshare_stats`

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| city | String | City name |
| state | String | State code (e.g., NY, CA) |
| date | Date | Date of statistics |
| active_drivers | Integer | Number of active drivers |
| total_rides | Integer | Total rides/trips |
| total_miles | Float | Total miles driven |
| average_trip_distance | Float | Average trip distance |
| total_duration_hours | Float | Total trip duration in hours |
| data_source | String | Source of the data |
| source_url | String | URL of data source |
| data_quality | String | verified/estimated/incomplete |
| created_at | DateTime | Record creation time |
| updated_at | DateTime | Record update time |

### Logging Table: `data_fetch_log`

Tracks all scraping operations with status, timing, and error information.

## Example Queries

### Python API

```python
from database.queries import RideshareQueries

# Initialize
queries = RideshareQueries()

# Get latest data for all cities
df = queries.get_all_cities_latest()
print(df)

# Get NYC data for last 30 days
df = queries.get_city_data_range("New York City", days=30)
print(df)

# Get growth rate
growth = queries.get_city_growth_rate("Chicago", days=30)
print(f"Driver growth: {growth['driver_growth_percent']:.1f}%")

# Compare cities
df = queries.compare_cities(["New York City", "Chicago", "Seattle"])
print(df)

# Clean up
queries.close()
```

### SQL Queries

```sql
-- Latest data for all cities
SELECT city, date, active_drivers, total_rides
FROM rideshare_stats
WHERE (city, date) IN (
    SELECT city, MAX(date)
    FROM rideshare_stats
    GROUP BY city
)
ORDER BY city;

-- Monthly totals by city
SELECT
    city,
    DATE_TRUNC('month', date) as month,
    SUM(total_rides) as monthly_rides,
    AVG(active_drivers) as avg_drivers
FROM rideshare_stats
WHERE date >= '2024-01-01'
GROUP BY city, DATE_TRUNC('month', date)
ORDER BY city, month;

-- Growth over time
SELECT
    city,
    date,
    total_rides,
    LAG(total_rides) OVER (PARTITION BY city ORDER BY date) as prev_rides,
    (total_rides - LAG(total_rides) OVER (PARTITION BY city ORDER BY date)) * 100.0 /
        LAG(total_rides) OVER (PARTITION BY city ORDER BY date) as growth_percent
FROM rideshare_stats
ORDER BY city, date;

-- Data quality summary
SELECT
    data_source,
    COUNT(*) as records,
    MIN(date) as earliest,
    MAX(date) as latest,
    COUNT(DISTINCT city) as cities
FROM rideshare_stats
GROUP BY data_source;
```

## Logging

All operations are logged to:
- Console (stdout)
- File: `rideshare_scraper.log`

Log format includes timestamp, module, level, and message.

## Error Handling

The scraper includes:
- Automatic retry logic for network failures
- Graceful degradation (continues with other scrapers if one fails)
- Detailed error logging with stack traces
- Data quality indicators for uncertain data

## Extending the System

### Adding a New Scraper

1. Create a new file in `scrapers/` directory:

```python
# scrapers/my_city.py
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class MyCityScraper:
    def __init__(self):
        self.city = "My City"
        self.state = "XX"
        self.data_source = "My Source"

    def scrape(self) -> List[Dict]:
        """Main scraping method"""
        # Implement your scraping logic
        records = []
        # ... fetch and transform data ...
        return records
```

2. Register in [main.py](main.py:45):

```python
from scrapers.my_city import MyCityScraper

# Add to scrapers dict
self.scrapers = {
    # ... existing scrapers ...
    'My City': MyCityScraper()
}
```

## Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -U postgres -d rideshare_data -c "SELECT 1"

# Check if tables exist
psql -U postgres -d rideshare_data -c "\dt"
```

### Missing Dependencies

```bash
pip install -r requirements.txt --upgrade
```

### PDF Parsing Issues

For California CPUC PDFs, ensure Java is installed (required by tabula-py):

```bash
# macOS
brew install java

# Ubuntu/Debian
sudo apt-get install default-jre
```

### Rate Limiting

Some APIs may rate-limit requests. The scraper includes 2-second delays between scrapers. To increase:

Edit [main.py](main.py:209):
```python
time.sleep(5)  # Increase from 2 to 5 seconds
```

## Performance

Typical execution times:
- NYC TLC API: 5-10 seconds
- Chicago TNP API: 10-15 seconds (large dataset)
- Seattle TNC API: 5-10 seconds
- Boston MassDOT: 30-60 seconds (multiple CSV downloads)
- California CPUC: 60-120 seconds (PDF processing)
- Airport Reports: 30-60 seconds

Total runtime: 3-5 minutes for all scrapers

## Data Quality

Data quality indicators:
- **verified**: Official API or government source
- **estimated**: Extracted from unstructured sources (PDFs)
- **incomplete**: Missing some fields

## Security

- Never commit `.env` file to version control
- Use environment variables for sensitive credentials
- Consider using PostgreSQL SSL connections for production
- Implement API key rotation if using authenticated endpoints

## License

This project is intended for data collection and analysis purposes. Always respect the terms of service of data sources and applicable data usage policies.

## Contributing

To contribute:
1. Create a new branch for your feature
2. Add tests if adding new scrapers
3. Update documentation
4. Submit a pull request

## Support

For issues or questions:
1. Check the logs: `tail -f rideshare_scraper.log`
2. Review error messages in console output
3. Verify database connectivity
4. Ensure all dependencies are installed

## Maintenance

### Regular Tasks

- **Weekly**: Review scraper logs for failures
- **Monthly**: Check for API changes or new data sources
- **Quarterly**: Update dependencies (`pip install -r requirements.txt --upgrade`)
- **As needed**: Update scraper logic if source formats change

### Monitoring Queries

```python
# Check recent scraper activity
from database.queries import RideshareQueries
queries = RideshareQueries()

# View recent fetch logs
logs = queries.get_fetch_log_summary(days=7)
print(logs)

# Check data freshness
latest = queries.get_all_cities_latest()
print(latest[['city', 'date']])
```

## Future Enhancements

Potential improvements:
- Add more cities (Austin, Denver, Portland, etc.)
- Implement data validation rules
- Add data visualization dashboard
- Create API endpoint for querying data
- Implement incremental updates (only fetch new data)
- Add email notifications for failures
- Create Docker containerization

---

**Version**: 1.0.0
**Python**: 3.10+
**Last Updated**: 2025-10-28
