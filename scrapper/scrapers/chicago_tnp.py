"""
Chicago TNP (Transportation Network Providers) Data Scraper
Fetches rideshare statistics from Chicago Open Data Portal
API: https://data.cityofchicago.org/resource/m6dm-c72p.json
"""

import requests
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ChicagoTNPScraper:
    """
    Scraper for Chicago TNP rideshare data
    Uses Socrata Open Data API
    """

    def __init__(self):
        self.base_url = "https://data.cityofchicago.org/resource/m6dm-c72p.json"
        self.city = "Chicago"
        self.state = "IL"
        self.data_source = "Chicago TNP API"

    def fetch_data(self, limit: int = 10000, offset: int = 0) -> Optional[pd.DataFrame]:
        """
        Fetch data from Chicago TNP API

        Args:
            limit: Maximum number of records to fetch
            offset: Offset for pagination

        Returns:
            DataFrame with rideshare statistics or None if failed
        """
        try:
            logger.info(f"Fetching Chicago TNP data (limit={limit}, offset={offset})")

            params = {
                '$limit': limit,
                '$offset': offset,
                '$order': 'trip_start_timestamp DESC'
            }

            response = requests.get(
                self.base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if not data:
                logger.warning("No data returned from Chicago TNP API")
                return None

            df = pd.DataFrame(data)
            logger.info(f"Successfully fetched {len(df)} records from Chicago TNP")

            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Chicago TNP data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Chicago TNP scraper: {e}")
            return None

    def transform_data(self, df: pd.DataFrame) -> List[Dict]:
        """
        Transform raw API data to standardized format
        Note: Chicago data is trip-level, so we aggregate by date

        Args:
            df: Raw DataFrame from API

        Returns:
            List of dictionaries in standardized format
        """
        if df is None or df.empty:
            return []

        records = []

        try:
            # Extract date from trip_start_timestamp
            if 'trip_start_timestamp' in df.columns:
                df['date'] = pd.to_datetime(df['trip_start_timestamp']).dt.date
            elif 'trip_date' in df.columns:
                df['date'] = pd.to_datetime(df['trip_date']).dt.date
            else:
                logger.error("No date column found in Chicago TNP data")
                return []

            # Group by date and aggregate
            grouped = df.groupby('date').agg({
                'trip_id': 'count',  # Total trips
                'trip_miles': 'sum',  # Total miles
                'trip_seconds': 'sum'  # Total duration
            }).reset_index()

            for _, row in grouped.iterrows():
                try:
                    # Calculate metrics
                    total_trips = int(row['trip_id'])
                    total_miles = float(row['trip_miles']) if pd.notna(row['trip_miles']) else None
                    total_seconds = float(row['trip_seconds']) if pd.notna(row['trip_seconds']) else None

                    record = {
                        'city': self.city,
                        'state': self.state,
                        'date': row['date'],
                        'active_drivers': None,  # Not available in trip-level data
                        'total_rides': total_trips,
                        'total_trips': total_trips,
                        'unique_vehicles': None,  # Would need to count unique vehicle IDs
                        'total_miles': total_miles,
                        'average_trip_distance': total_miles / total_trips if total_miles and total_trips else None,
                        'total_duration_hours': total_seconds / 3600 if total_seconds else None,
                        'data_source': self.data_source,
                        'source_url': self.base_url,
                        'data_quality': 'verified',
                        'notes': 'Aggregated from trip-level data'
                    }

                    records.append(record)

                except Exception as e:
                    logger.warning(f"Error transforming row: {e}")
                    continue

            logger.info(f"Transformed {len(records)} records from Chicago TNP")

        except Exception as e:
            logger.error(f"Error during data transformation: {e}")
            return []

        return records

    def scrape(self, limit: int = 10000) -> List[Dict]:
        """
        Main scraping method - fetch and transform data

        Args:
            limit: Maximum number of records to fetch

        Returns:
            List of standardized records
        """
        logger.info("Starting Chicago TNP scraper")

        # Fetch data
        df = self.fetch_data(limit=limit)

        if df is None or df.empty:
            logger.error("Failed to fetch Chicago TNP data")
            return []

        # Transform data
        records = self.transform_data(df)

        logger.info(f"Chicago TNP scraper completed: {len(records)} records")
        return records

    def fetch_aggregated_stats(self) -> List[Dict]:
        """
        Fetch pre-aggregated statistics using Socrata aggregation
        This is more efficient than downloading all trip records

        Returns:
            List of aggregated statistics by date
        """
        try:
            logger.info("Fetching aggregated Chicago TNP stats")

            # Use SoQL aggregation to group by date
            query = """
            SELECT
                date_trunc_ymd(trip_start_timestamp) as trip_date,
                count(*) as total_trips,
                sum(trip_miles) as total_miles,
                sum(trip_seconds) as total_seconds,
                avg(trip_miles) as avg_trip_miles
            GROUP BY trip_date
            ORDER BY trip_date DESC
            LIMIT 1000
            """

            params = {
                '$query': query
            }

            response = requests.get(
                self.base_url,
                params=params,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()

            if not data:
                logger.warning("No aggregated data returned")
                return []

            records = []
            for row in data:
                try:
                    date_obj = datetime.strptime(row['trip_date'][:10], "%Y-%m-%d")

                    record = {
                        'city': self.city,
                        'state': self.state,
                        'date': date_obj.date(),
                        'active_drivers': None,
                        'total_rides': int(row['total_trips']),
                        'total_trips': int(row['total_trips']),
                        'total_miles': float(row['total_miles']) if row.get('total_miles') else None,
                        'average_trip_distance': float(row['avg_trip_miles']) if row.get('avg_trip_miles') else None,
                        'total_duration_hours': float(row['total_seconds']) / 3600 if row.get('total_seconds') else None,
                        'data_source': self.data_source,
                        'source_url': self.base_url,
                        'data_quality': 'verified'
                    }

                    records.append(record)

                except Exception as e:
                    logger.warning(f"Error parsing aggregated row: {e}")
                    continue

            logger.info(f"Fetched {len(records)} aggregated records")
            return records

        except Exception as e:
            logger.error(f"Error fetching aggregated stats: {e}")
            return []


def main():
    """Test function for Chicago TNP scraper"""
    logging.basicConfig(level=logging.INFO)

    scraper = ChicagoTNPScraper()

    # Try aggregated approach first (more efficient)
    print("Fetching aggregated stats...")
    records = scraper.fetch_aggregated_stats()

    if records:
        print(f"\nFetched {len(records)} records")
        print("\nSample record:")
        print(records[0])
    else:
        print("No records fetched")


if __name__ == "__main__":
    main()
