"""
NYC TLC (Taxi & Limousine Commission) Data Scraper
Fetches rideshare statistics from NYC Open Data API
API: https://data.cityofnewyork.us/resource/gnke-dk5s.json
"""

import requests
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class NYCTLCScraper:
    """
    Scraper for NYC TLC rideshare data
    Uses Socrata Open Data API
    """

    def __init__(self):
        self.base_url = "https://data.cityofnewyork.us/resource/gnke-dk5s.json"
        self.city = "New York City"
        self.state = "NY"
        self.data_source = "NYC TLC API"

    def fetch_data(self, limit: int = 10000, offset: int = 0) -> Optional[pd.DataFrame]:
        """
        Fetch data from NYC TLC API

        Args:
            limit: Maximum number of records to fetch
            offset: Offset for pagination

        Returns:
            DataFrame with rideshare statistics or None if failed
        """
        try:
            logger.info(f"Fetching NYC TLC data (limit={limit}, offset={offset})")

            params = {
                '$limit': limit,
                '$offset': offset,
                '$order': 'month DESC'
            }

            response = requests.get(
                self.base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if not data:
                logger.warning("No data returned from NYC TLC API")
                return None

            df = pd.DataFrame(data)
            logger.info(f"Successfully fetched {len(df)} records from NYC TLC")

            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching NYC TLC data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in NYC TLC scraper: {e}")
            return None

    def transform_data(self, df: pd.DataFrame) -> List[Dict]:
        """
        Transform raw API data to standardized format

        Args:
            df: Raw DataFrame from API

        Returns:
            List of dictionaries in standardized format
        """
        if df is None or df.empty:
            return []

        records = []

        for _, row in df.iterrows():
            try:
                # Parse date from 'month' field (format: YYYY-MM-DD or YYYY-MM)
                date_str = row.get('month', '')
                if date_str:
                    # Handle both YYYY-MM-DD and YYYY-MM formats
                    if len(date_str) == 7:  # YYYY-MM
                        date_obj = datetime.strptime(date_str, "%Y-%m")
                    else:  # YYYY-MM-DD
                        date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d")
                else:
                    logger.warning(f"Missing date in row: {row}")
                    continue

                # Extract metrics
                record = {
                    'city': self.city,
                    'state': self.state,
                    'date': date_obj.date(),
                    'active_drivers': self._parse_int(row.get('unique_drivers')),
                    'total_rides': self._parse_int(row.get('total_trips')),
                    'total_trips': self._parse_int(row.get('total_trips')),
                    'unique_vehicles': self._parse_int(row.get('unique_vehicles')),
                    'total_miles': self._parse_float(row.get('total_trip_miles')),
                    'average_trip_distance': self._parse_float(row.get('avg_trip_miles')),
                    'total_duration_hours': self._parse_float(row.get('total_trip_time')) / 60 if row.get('total_trip_time') else None,
                    'data_source': self.data_source,
                    'source_url': self.base_url,
                    'data_quality': 'verified'
                }

                records.append(record)

            except Exception as e:
                logger.warning(f"Error transforming row: {e}")
                continue

        logger.info(f"Transformed {len(records)} records from NYC TLC")
        return records

    def _parse_int(self, value) -> Optional[int]:
        """Safely parse integer value"""
        if value is None or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def _parse_float(self, value) -> Optional[float]:
        """Safely parse float value"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def scrape(self, limit: int = 10000) -> List[Dict]:
        """
        Main scraping method - fetch and transform data

        Args:
            limit: Maximum number of records to fetch

        Returns:
            List of standardized records
        """
        logger.info("Starting NYC TLC scraper")

        # Fetch data
        df = self.fetch_data(limit=limit)

        if df is None or df.empty:
            logger.error("Failed to fetch NYC TLC data")
            return []

        # Transform data
        records = self.transform_data(df)

        logger.info(f"NYC TLC scraper completed: {len(records)} records")
        return records


def main():
    """Test function for NYC TLC scraper"""
    logging.basicConfig(level=logging.INFO)

    scraper = NYCTLCScraper()
    records = scraper.scrape(limit=100)

    if records:
        print(f"\nFetched {len(records)} records")
        print("\nSample record:")
        print(records[0])
    else:
        print("No records fetched")


if __name__ == "__main__":
    main()
