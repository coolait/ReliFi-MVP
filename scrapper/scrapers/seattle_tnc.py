"""
Seattle TNC (Transportation Network Companies) Data Scraper
Fetches rideshare statistics from Seattle Open Data Portal
API: https://data.seattle.gov/resource/4j8s-v8vy.json
"""

import requests
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SeattleTNCScraper:
    """
    Scraper for Seattle TNC rideshare data
    Uses Socrata Open Data API
    """

    def __init__(self):
        self.base_url = "https://data.seattle.gov/resource/4j8s-v8vy.json"
        self.city = "Seattle"
        self.state = "WA"
        self.data_source = "Seattle TNC API"

    def fetch_data(self, limit: int = 10000, offset: int = 0) -> Optional[pd.DataFrame]:
        """
        Fetch data from Seattle TNC API

        Args:
            limit: Maximum number of records to fetch
            offset: Offset for pagination

        Returns:
            DataFrame with rideshare statistics or None if failed
        """
        try:
            logger.info(f"Fetching Seattle TNC data (limit={limit}, offset={offset})")

            params = {
                '$limit': limit,
                '$offset': offset,
                '$order': 'request_date DESC'
            }

            response = requests.get(
                self.base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if not data:
                logger.warning("No data returned from Seattle TNC API")
                return None

            df = pd.DataFrame(data)
            logger.info(f"Successfully fetched {len(df)} records from Seattle TNC")

            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Seattle TNC data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Seattle TNC scraper: {e}")
            return None

    def transform_data(self, df: pd.DataFrame) -> List[Dict]:
        """
        Transform raw API data to standardized format
        Seattle provides trip-level data that needs aggregation

        Args:
            df: Raw DataFrame from API

        Returns:
            List of dictionaries in standardized format
        """
        if df is None or df.empty:
            return []

        records = []

        try:
            # Extract date from request_date or trip_start_time
            date_column = None
            for col in ['request_date', 'trip_start_time', 'date']:
                if col in df.columns:
                    date_column = col
                    break

            if not date_column:
                logger.error("No date column found in Seattle TNC data")
                return []

            df['date'] = pd.to_datetime(df[date_column]).dt.date

            # Group by date and aggregate
            aggregations = {
                # Count trips
                date_column: 'count'
            }

            # Add other columns if they exist
            if 'trip_miles' in df.columns:
                aggregations['trip_miles'] = 'sum'
            if 'trip_time' in df.columns:
                aggregations['trip_time'] = 'sum'
            if 'driver_id' in df.columns:
                aggregations['driver_id'] = 'nunique'

            grouped = df.groupby('date').agg(aggregations).reset_index()

            for _, row in grouped.iterrows():
                try:
                    total_trips = int(row[date_column]) if date_column in row else None

                    record = {
                        'city': self.city,
                        'state': self.state,
                        'date': row['date'],
                        'active_drivers': int(row['driver_id']) if 'driver_id' in row else None,
                        'total_rides': total_trips,
                        'total_trips': total_trips,
                        'total_miles': float(row['trip_miles']) if 'trip_miles' in row and pd.notna(row['trip_miles']) else None,
                        'average_trip_distance': None,  # Calculate if we have total_miles and total_trips
                        'total_duration_hours': float(row['trip_time']) / 3600 if 'trip_time' in row and pd.notna(row['trip_time']) else None,
                        'data_source': self.data_source,
                        'source_url': self.base_url,
                        'data_quality': 'verified',
                        'notes': 'Aggregated from trip-level data'
                    }

                    # Calculate average trip distance if possible
                    if record['total_miles'] and record['total_trips']:
                        record['average_trip_distance'] = record['total_miles'] / record['total_trips']

                    records.append(record)

                except Exception as e:
                    logger.warning(f"Error transforming row: {e}")
                    continue

            logger.info(f"Transformed {len(records)} records from Seattle TNC")

        except Exception as e:
            logger.error(f"Error during data transformation: {e}")
            return []

        return records

    def fetch_aggregated_stats(self) -> List[Dict]:
        """
        Fetch pre-aggregated statistics using Socrata aggregation
        More efficient than downloading all trip records

        Returns:
            List of aggregated statistics by date
        """
        try:
            logger.info("Fetching aggregated Seattle TNC stats")

            # Use SoQL aggregation
            query = """
            SELECT
                date_trunc_ymd(request_date) as trip_date,
                count(*) as total_trips
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
                    date_str = row.get('trip_date', '')
                    if not date_str:
                        continue

                    date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d")

                    record = {
                        'city': self.city,
                        'state': self.state,
                        'date': date_obj.date(),
                        'active_drivers': None,
                        'total_rides': int(row['total_trips']),
                        'total_trips': int(row['total_trips']),
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

    def scrape(self, limit: int = 10000, use_aggregation: bool = True) -> List[Dict]:
        """
        Main scraping method - fetch and transform data

        Args:
            limit: Maximum number of records to fetch
            use_aggregation: Whether to use aggregated API endpoint (more efficient)

        Returns:
            List of standardized records
        """
        logger.info("Starting Seattle TNC scraper")

        if use_aggregation:
            # Try aggregated approach first
            records = self.fetch_aggregated_stats()
            if records:
                logger.info(f"Seattle TNC scraper completed: {len(records)} records")
                return records

        # Fall back to regular scraping
        df = self.fetch_data(limit=limit)

        if df is None or df.empty:
            logger.error("Failed to fetch Seattle TNC data")
            return []

        # Transform data
        records = self.transform_data(df)

        logger.info(f"Seattle TNC scraper completed: {len(records)} records")
        return records


def main():
    """Test function for Seattle TNC scraper"""
    logging.basicConfig(level=logging.INFO)

    scraper = SeattleTNCScraper()
    records = scraper.scrape(limit=100)

    if records:
        print(f"\nFetched {len(records)} records")
        print("\nSample record:")
        print(records[0])
    else:
        print("No records fetched")


if __name__ == "__main__":
    main()
