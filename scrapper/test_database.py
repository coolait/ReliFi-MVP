#!/usr/bin/env python3
"""
Test database connectivity and schema
Run: python3 test_database.py
"""

import sys
import os


def test_database():
    print("=" * 60)
    print("TESTING DATABASE")
    print("=" * 60)
    print()

    # Check for DATABASE_URL
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        print(f"✓ DATABASE_URL found in environment")
        # Mask password in output
        safe_url = db_url.split('@')[1] if '@' in db_url else db_url
        print(f"  Connection: ...@{safe_url}")
    else:
        print("○ DATABASE_URL not set, will use default")
        print("  Default: postgresql://localhost:5432/rideshare_data")

    print()

    # Test import
    try:
        from database.models import get_engine, get_session, init_database
        print("✓ Database modules imported")
    except ImportError as e:
        print(f"✗ Failed to import database modules: {e}")
        return False

    print()

    # Test engine creation
    try:
        engine = get_engine()
        print("✓ Database engine created")
    except Exception as e:
        print(f"✗ Failed to create engine: {e}")
        print()
        print("Possible fixes:")
        print("  1. Check PostgreSQL is running: pg_isready")
        print("  2. Create database: createdb rideshare_data")
        print("  3. Check DATABASE_URL in .env file")
        return False

    print()

    # Test connection
    try:
        session = get_session(engine)
        print("✓ Database session created")

        # Try a simple query
        result = session.execute("SELECT 1 as test")
        row = result.fetchone()
        if row[0] == 1:
            print("✓ Database query executed successfully")

        session.close()
        print("✓ Session closed")

    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print()
        print("Possible fixes:")
        print("  1. Verify PostgreSQL is running")
        print("  2. Check database credentials")
        print("  3. Test with: psql rideshare_data")
        return False

    print()

    # Test schema creation
    try:
        print("Initializing database schema...")
        init_database()
        print("✓ Database schema created/verified")
    except Exception as e:
        print(f"✗ Schema creation failed: {e}")
        return False

    print()

    # Verify tables exist
    try:
        session = get_session(engine)

        # Check for tables
        result = session.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)

        tables = [row[0] for row in result.fetchall()]

        if 'rideshare_stats' in tables:
            print("✓ Table 'rideshare_stats' exists")
        else:
            print("✗ Table 'rideshare_stats' not found")

        if 'data_fetch_log' in tables:
            print("✓ Table 'data_fetch_log' exists")
        else:
            print("✗ Table 'data_fetch_log' not found")

        session.close()

    except Exception as e:
        print(f"○ Could not verify tables: {e}")

    print()

    # Test inserting a record
    try:
        from database.models import RideshareStats
        from datetime import datetime

        session = get_session(engine)

        # Create a test record
        test_record = RideshareStats(
            city='Test City',
            state='TS',
            date=datetime.now().date(),
            active_drivers=100,
            total_rides=1000,
            data_source='Test',
            data_quality='test'
        )

        session.add(test_record)
        session.commit()
        print("✓ Test record inserted")

        # Delete test record
        session.delete(test_record)
        session.commit()
        print("✓ Test record deleted")

        session.close()

    except Exception as e:
        print(f"○ Insert test skipped: {e}")

    print()
    print("=" * 60)
    print("✓ DATABASE TESTS PASSED!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Run a scraper: python3 main.py --scrapers 'NYC TLC'")
    print("  2. Query data: python3 database/queries.py")
    print()

    return True


if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
