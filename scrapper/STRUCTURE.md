# Project Structure

```
scrapper/
│
├── main.py                      # Main orchestration script
├── setup.sh                     # Quick setup script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
│
├── README.md                    # Full documentation
├── QUICKSTART.md               # 5-minute setup guide
├── STRUCTURE.md                # This file
│
├── database/                    # Database layer
│   ├── __init__.py             # Package initialization
│   ├── models.py               # SQLAlchemy models & schema
│   └── queries.py              # Example queries & utilities
│
├── scrapers/                    # Data source scrapers
│   ├── __init__.py             # Package initialization
│   ├── nyc_tlc.py              # NYC TLC API scraper
│   ├── chicago_tnp.py          # Chicago TNP API scraper
│   ├── seattle_tnc.py          # Seattle TNC API scraper
│   ├── boston_massdot.py       # Boston MassDOT CSV scraper
│   ├── california_cpuc.py      # California CPUC PDF scraper
│   └── airport_reports.py      # LAX/SFO reports scraper
│
├── config.py                    # Legacy config (from old scrape.py)
├── scrape.py                    # Legacy scraper (kept for reference)
│
└── logs/                        # Log files (created on first run)
    └── rideshare_scraper.log   # Application logs
```

## File Descriptions

### Core Files

| File | Description | Lines of Code |
|------|-------------|---------------|
| `main.py` | Main orchestration script that coordinates all scrapers, handles database operations, and manages scheduling | ~350 |
| `setup.sh` | Bash script for quick environment setup | ~40 |
| `requirements.txt` | Python package dependencies | ~20 |

### Database Layer

| File | Description | Lines of Code |
|------|-------------|---------------|
| `database/models.py` | SQLAlchemy ORM models for `rideshare_stats` and `data_fetch_log` tables | ~150 |
| `database/queries.py` | Helper class with pre-built queries for common data analysis tasks | ~350 |

### Scrapers

| File | Data Source | Type | Lines of Code |
|------|-------------|------|---------------|
| `scrapers/nyc_tlc.py` | NYC Taxi & Limousine Commission | Socrata API | ~200 |
| `scrapers/chicago_tnp.py` | Chicago Transportation Network Providers | Socrata API | ~250 |
| `scrapers/seattle_tnc.py` | Seattle Transportation Network Companies | Socrata API | ~220 |
| `scrapers/boston_massdot.py` | Massachusetts Department of Transportation | CSV/Excel | ~300 |
| `scrapers/california_cpuc.py` | California Public Utilities Commission | PDF Reports | ~400 |
| `scrapers/airport_reports.py` | LAX & SFO Airports | Excel/PDF | ~300 |

### Documentation

| File | Description | Purpose |
|------|-------------|---------|
| `README.md` | Comprehensive documentation | Full setup, usage, and API reference |
| `QUICKSTART.md` | Quick start guide | Get running in 5 minutes |
| `STRUCTURE.md` | This file | Project organization overview |

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Sources                            │
├─────────────┬──────────────┬──────────────┬────────────────┤
│  NYC TLC    │  Chicago TNP │  Seattle TNC │  Boston        │
│  API        │  API         │  API         │  MassDOT CSV   │
└──────┬──────┴──────┬───────┴──────┬───────┴────┬───────────┘
       │             │              │            │
       ▼             ▼              ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                Individual Scrapers                          │
│  (scrapers/*.py - Fetch & Transform Data)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Main Orchestrator                         │
│              (main.py - Coordinates All)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database Layer                             │
│         (database/models.py - SQLAlchemy ORM)              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL Database                        │
│        Tables: rideshare_stats, data_fetch_log             │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Scrapers (Modular Design)

Each scraper is a self-contained Python class with:
- `__init__()` - Initialize with city/source info
- `fetch_data()` - Download raw data
- `transform_data()` - Convert to standard format
- `scrape()` - Main method that orchestrates fetch & transform

**Standard Output Format:**
```python
{
    'city': str,
    'state': str,
    'date': datetime.date,
    'active_drivers': int,
    'total_rides': int,
    'total_miles': float,
    'data_source': str,
    'source_url': str,
    'data_quality': str
}
```

### 2. Database Models

**RideshareStats Table:**
- Stores all rideshare metrics
- Indexed on city, date, and data_source
- Supports upsert operations (insert or update)

**DataFetchLog Table:**
- Tracks scraper execution
- Logs success/failure, timing, and errors
- Useful for monitoring and debugging

### 3. Main Orchestrator

**Responsibilities:**
- Initialize database connection
- Run scrapers sequentially
- Handle errors gracefully
- Log all operations
- Support scheduling

**Command-line Options:**
```bash
python3 main.py                              # Run all scrapers
python3 main.py --scrapers "NYC TLC"        # Run specific scraper
python3 main.py --schedule                   # Run on schedule
python3 main.py --db-url "postgresql://..."  # Custom DB
```

## Dependencies

### Core Libraries
- **requests**: HTTP client for API calls
- **pandas**: Data manipulation
- **beautifulsoup4**: HTML parsing
- **sqlalchemy**: ORM and database abstraction
- **psycopg2-binary**: PostgreSQL adapter

### Specialized Libraries
- **pdfplumber**: PDF text/table extraction
- **tabula-py**: Alternative PDF parser
- **openpyxl**: Excel file support
- **schedule**: Task scheduling
- **selenium**: JavaScript-heavy websites (optional)

## Configuration

### Environment Variables (.env)

```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
LOG_LEVEL=INFO
LOG_FILE=rideshare_scraper.log
```

### Database Configuration

Connection managed through SQLAlchemy engine:
```python
engine = create_engine(DATABASE_URL)
```

Supports connection pooling and automatic reconnection.

## Logging

### Log Levels
- **INFO**: Normal operations
- **WARNING**: Non-fatal issues (missing data, retries)
- **ERROR**: Scraper failures, database errors

### Log Destinations
1. Console (stdout)
2. File: `rideshare_scraper.log`

### Log Format
```
2025-10-28 10:30:15 - scrapers.nyc_tlc - INFO - Successfully fetched 100 records
```

## Error Handling

### Network Errors
- Automatic timeout (30-60s depending on operation)
- Graceful failure (continues with next scraper)
- Error logged with full stack trace

### Data Quality Issues
- Invalid dates → Skip record, log warning
- Missing required fields → Skip record
- Parsing errors → Mark as 'incomplete' quality

### Database Errors
- Connection failures → Retry with exponential backoff
- Constraint violations → Skip duplicate records
- Transaction errors → Rollback and log

## Performance

### Optimization Techniques
1. **Batch inserts**: SQLAlchemy bulk operations
2. **Connection pooling**: Reuse database connections
3. **Parallel processing**: Can run scrapers in parallel (future enhancement)
4. **Selective fetching**: Date range filters to avoid re-fetching old data

### Typical Performance
- Single scraper: 5-60 seconds
- All scrapers: 3-5 minutes
- Database insert: ~100 records/second

## Testing

### Test Individual Scraper
```bash
python3 scrapers/nyc_tlc.py
```

### Test Database Connection
```bash
python3 -c "from database.models import get_session; print(get_session())"
```

### Test Queries
```bash
python3 database/queries.py
```

## Maintenance

### Regular Tasks
- Review logs weekly
- Check for API changes monthly
- Update dependencies quarterly
- Backup database regularly

### Monitoring Queries
```sql
-- Check data freshness
SELECT city, MAX(date) FROM rideshare_stats GROUP BY city;

-- Check scraper health
SELECT data_source, status, COUNT(*)
FROM data_fetch_log
WHERE fetch_time > NOW() - INTERVAL '7 days'
GROUP BY data_source, status;
```

## Future Enhancements

### Planned Features
1. **More cities**: Austin, Denver, Portland, Miami, etc.
2. **Real-time updates**: Stream processing for APIs
3. **Data validation**: Automated quality checks
4. **API endpoint**: REST API for querying data
5. **Dashboard**: Web-based visualization
6. **Containerization**: Docker support

### Scalability
- Horizontal scaling: Run scrapers on multiple workers
- Caching: Redis for API response caching
- Message queue: RabbitMQ/Celery for task distribution

---

**Total Lines of Code**: ~2,500
**Number of Data Sources**: 6
**Cities Covered**: 8+
**Last Updated**: 2025-10-28
