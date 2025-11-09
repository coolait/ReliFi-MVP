#!/usr/bin/env python3
"""
Rideshare Data Scraper - Main Orchestration Script
Coordinates data collection from multiple sources and stores in PostgreSQL
"""

import logging
import sys
import os
from datetime import datetime, timedelta
import time
import schedule
import argparse

# Add scrapers directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scrapers'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'database'))

# Import scrapers
from scrapers.nyc_tlc import NYCTLCScraper
from scrapers.chicago_tnp import ChicagoTNPScraper
from scrapers.seattle_tnc import SeattleTNCScraper
from scrapers.boston_massdot import BostonMassDOTScraper
from scrapers.california_cpuc import CaliforniaCPUCScraper
from scrapers.airport_reports import AirportReportsScraper

# Import database
from database.models import (
    init_database, get_session, RideshareStats, DataFetchLog
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rideshare_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class RideshareScraper:
    """
    Main orchestrator for rideshare data scraping
    """

    def __init__(self, database_url=None):
        """
        Initialize scraper with database connection

        Args:
            database_url: PostgreSQL connection string
        """
        self.database_url = database_url
        self.engine = None
        self.session = None

        # Initialize scrapers
        self.scrapers = {
            'NYC TLC': NYCTLCScraper(),
            'Chicago TNP': ChicagoTNPScraper(),
            'Seattle TNC': SeattleTNCScraper(),
            'Boston MassDOT': BostonMassDOTScraper(),
            'California CPUC': CaliforniaCPUCScraper(),
            'Airport Reports': AirportReportsScraper()
        }

    def initialize_database(self):
        """Initialize database connection and schema (optional)"""
        try:
            logger.info("Initializing database...")
            self.engine = init_database(self.database_url)
            if self.engine is None:
                logger.warning("No database configured - operating without database")
                return False
            self.session = get_session(self.engine)
            logger.info("Database initialized successfully")
            return True

        except Exception as e:
            logger.warning(f"Database not available: {e} - continuing without database")
            return False

    def run_scraper(self, scraper_name: str, scraper_obj) -> dict:
        """
        Run a single scraper and return results

        Args:
            scraper_name: Name of the scraper
            scraper_obj: Scraper instance

        Returns:
            Dictionary with scraping results
        """
        start_time = time.time()
        result = {
            'scraper': scraper_name,
            'status': 'success',
            'records_fetched': 0,
            'records_inserted': 0,
            'records_updated': 0,
            'error': None,
            'duration': 0
        }

        try:
            logger.info(f"Starting scraper: {scraper_name}")

            # Run the scraper
            records = scraper_obj.scrape()

            result['records_fetched'] = len(records)

            if not records:
                logger.warning(f"{scraper_name}: No records fetched")
                result['status'] = 'no_data'
                return result

            # Save records to database
            if self.session:
                inserted, updated = self._save_records(records)
                result['records_inserted'] = inserted
                result['records_updated'] = updated

            logger.info(f"{scraper_name}: Successfully processed {len(records)} records")

        except Exception as e:
            logger.error(f"{scraper_name}: Error - {e}", exc_info=True)
            result['status'] = 'failure'
            result['error'] = str(e)

        finally:
            result['duration'] = time.time() - start_time

        return result

    def _save_records(self, records: list) -> tuple:
        """
        Save records to database

        Args:
            records: List of record dictionaries

        Returns:
            Tuple of (inserted_count, updated_count)
        """
        inserted = 0
        updated = 0

        for record in records:
            try:
                # Check if record already exists
                existing = self.session.query(RideshareStats).filter_by(
                    city=record['city'],
                    date=record['date'],
                    data_source=record['data_source']
                ).first()

                if existing:
                    # Update existing record
                    for key, value in record.items():
                        if value is not None:  # Only update non-null values
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    # Insert new record
                    new_record = RideshareStats(**record)
                    self.session.add(new_record)
                    inserted += 1

            except Exception as e:
                logger.warning(f"Error saving record: {e}")
                continue

        # Commit all changes
        try:
            self.session.commit()
        except Exception as e:
            logger.error(f"Error committing to database: {e}")
            self.session.rollback()
            raise

        return inserted, updated

    def _log_fetch(self, result: dict):
        """
        Log fetch operation to database

        Args:
            result: Result dictionary from scraper
        """
        if not self.session:
            return

        try:
            log_entry = DataFetchLog(
                data_source=result['scraper'],
                status=result['status'],
                records_fetched=result['records_fetched'],
                records_inserted=result['records_inserted'],
                records_updated=result['records_updated'],
                error_message=result['error'],
                duration_seconds=result['duration']
            )

            self.session.add(log_entry)
            self.session.commit()

        except Exception as e:
            logger.error(f"Error logging fetch operation: {e}")
            self.session.rollback()

    def run_all_scrapers(self):
        """
        Run all scrapers sequentially

        Returns:
            List of results from all scrapers
        """
        logger.info("=" * 60)
        logger.info("STARTING RIDESHARE DATA SCRAPING SESSION")
        logger.info("=" * 60)

        results = []

        for scraper_name, scraper_obj in self.scrapers.items():
            result = self.run_scraper(scraper_name, scraper_obj)
            results.append(result)

            # Log to database
            self._log_fetch(result)

            # Brief pause between scrapers
            time.sleep(2)

        # Print summary
        self._print_summary(results)

        logger.info("=" * 60)
        logger.info("SCRAPING SESSION COMPLETED")
        logger.info("=" * 60)

        return results

    def run_selected_scrapers(self, scraper_names: list):
        """
        Run specific scrapers

        Args:
            scraper_names: List of scraper names to run

        Returns:
            List of results
        """
        logger.info(f"Running selected scrapers: {', '.join(scraper_names)}")

        results = []

        for name in scraper_names:
            if name in self.scrapers:
                result = self.run_scraper(name, self.scrapers[name])
                results.append(result)
                self._log_fetch(result)
                time.sleep(2)
            else:
                logger.warning(f"Unknown scraper: {name}")

        self._print_summary(results)
        return results

    def _print_summary(self, results: list):
        """Print summary of scraping results"""
        logger.info("\n" + "=" * 60)
        logger.info("SCRAPING SUMMARY")
        logger.info("=" * 60)

        total_fetched = 0
        total_inserted = 0
        total_updated = 0
        successful = 0
        failed = 0

        for result in results:
            status_icon = "✓" if result['status'] == 'success' else "✗"
            logger.info(f"{status_icon} {result['scraper']}: "
                       f"{result['records_fetched']} fetched, "
                       f"{result['records_inserted']} inserted, "
                       f"{result['records_updated']} updated "
                       f"({result['duration']:.1f}s)")

            total_fetched += result['records_fetched']
            total_inserted += result['records_inserted']
            total_updated += result['records_updated']

            if result['status'] == 'success':
                successful += 1
            else:
                failed += 1

        logger.info("=" * 60)
        logger.info(f"Total: {total_fetched} records fetched, "
                   f"{total_inserted} inserted, {total_updated} updated")
        logger.info(f"Scrapers: {successful} successful, {failed} failed")
        logger.info("=" * 60)

    def schedule_weekly(self):
        """
        Schedule scraping to run weekly

        Runs every Monday at 2:00 AM
        """
        logger.info("Setting up weekly schedule (Mondays at 2:00 AM)")

        schedule.every().monday.at("02:00").do(self.run_all_scrapers)

        logger.info("Scheduler started. Press Ctrl+C to stop.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")

    def cleanup(self):
        """Clean up database connections"""
        if self.session:
            self.session.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Rideshare Data Scraper')

    parser.add_argument(
        '--scrapers',
        nargs='+',
        help='Specific scrapers to run (default: all)',
        choices=['NYC TLC', 'Chicago TNP', 'Seattle TNC', 'Boston MassDOT',
                'California CPUC', 'Airport Reports']
    )

    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Run on weekly schedule'
    )

    parser.add_argument(
        '--db-url',
        type=str,
        help='PostgreSQL database URL',
        default=os.getenv('DATABASE_URL')
    )

    args = parser.parse_args()

    # Create scraper instance
    scraper = RideshareScraper(database_url=args.db_url)

    # Initialize database (optional - only needed for scraping with storage)
    if not scraper.initialize_database():
        logger.warning("Database not available - continuing without database storage")
        # Don't exit - allow scraping without database

    try:
        if args.schedule:
            # Run on schedule
            scraper.schedule_weekly()
        elif args.scrapers:
            # Run specific scrapers
            scraper.run_selected_scrapers(args.scrapers)
        else:
            # Run all scrapers once
            scraper.run_all_scrapers()

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        scraper.cleanup()


if __name__ == "__main__":
    # Only run if explicitly called (not imported)
    # This prevents Railway from accidentally running this as the entry point
    import sys
    if len(sys.argv) > 0 and 'api_server' not in sys.argv[0]:
        main()
    else:
        print("Note: Use 'python api_server.py' to start the API server")
        print("Use 'python main.py' to run the scraper")
