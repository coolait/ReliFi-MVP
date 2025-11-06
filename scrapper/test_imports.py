#!/usr/bin/env python3
"""
Quick test to verify all imports work
Run: python3 test_imports.py
"""

def test_imports():
    print("=" * 60)
    print("TESTING IMPORTS")
    print("=" * 60)
    print()

    errors = []

    # Test scraper imports
    try:
        from scrapers.nyc_tlc import NYCTLCScraper
        print("✓ NYC TLC scraper imported")
    except ImportError as e:
        print(f"✗ NYC TLC scraper failed: {e}")
        errors.append("NYC TLC")

    try:
        from scrapers.chicago_tnp import ChicagoTNPScraper
        print("✓ Chicago TNP scraper imported")
    except ImportError as e:
        print(f"✗ Chicago TNP scraper failed: {e}")
        errors.append("Chicago TNP")

    try:
        from scrapers.seattle_tnc import SeattleTNCScraper
        print("✓ Seattle TNC scraper imported")
    except ImportError as e:
        print(f"✗ Seattle TNC scraper failed: {e}")
        errors.append("Seattle TNC")

    try:
        from scrapers.boston_massdot import BostonMassDOTScraper
        print("✓ Boston MassDOT scraper imported")
    except ImportError as e:
        print(f"✗ Boston MassDOT scraper failed: {e}")
        errors.append("Boston MassDOT")

    try:
        from scrapers.california_cpuc import CaliforniaCPUCScraper
        print("✓ California CPUC scraper imported")
    except ImportError as e:
        print(f"✗ California CPUC scraper failed: {e}")
        errors.append("California CPUC")

    try:
        from scrapers.airport_reports import AirportReportsScraper
        print("✓ Airport reports scraper imported")
    except ImportError as e:
        print(f"✗ Airport reports scraper failed: {e}")
        errors.append("Airport Reports")

    print()

    # Test database imports
    try:
        from database.models import RideshareStats, DataFetchLog, init_database
        print("✓ Database models imported")
    except ImportError as e:
        print(f"✗ Database models failed: {e}")
        errors.append("Database models")

    try:
        from database.queries import RideshareQueries
        print("✓ Query utilities imported")
    except ImportError as e:
        print(f"✗ Query utilities failed: {e}")
        errors.append("Query utilities")

    print()

    # Test core dependencies
    try:
        import requests
        print("✓ requests library")
    except ImportError:
        print("✗ requests library missing")
        errors.append("requests")

    try:
        import pandas
        print("✓ pandas library")
    except ImportError:
        print("✗ pandas library missing")
        errors.append("pandas")

    try:
        import sqlalchemy
        print("✓ sqlalchemy library")
    except ImportError:
        print("✗ sqlalchemy library missing")
        errors.append("sqlalchemy")

    try:
        from bs4 import BeautifulSoup
        print("✓ beautifulsoup4 library")
    except ImportError:
        print("✗ beautifulsoup4 library missing")
        errors.append("beautifulsoup4")

    try:
        import pdfplumber
        print("✓ pdfplumber library")
    except ImportError:
        print("✗ pdfplumber library missing (optional for PDF parsing)")

    print()
    print("=" * 60)

    if not errors:
        print("✓ ALL IMPORTS SUCCESSFUL!")
        print("=" * 60)
        return True
    else:
        print(f"✗ {len(errors)} IMPORT(S) FAILED:")
        for error in errors:
            print(f"  - {error}")
        print()
        print("Fix with: pip install -r requirements.txt")
        print("=" * 60)
        return False


if __name__ == "__main__":
    import sys
    success = test_imports()
    sys.exit(0 if success else 1)
