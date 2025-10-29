"""
Boston MassDOT TNC Data Scraper
Downloads and parses CSV files from Massachusetts Department of Transportation
Source: https://massdot.state.ma.us (TNC Annual/Quarterly reports)
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from typing import Dict, List, Optional
import io
import re
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class BostonMassDOTScraper:
    """
    Scraper for Boston/Massachusetts TNC data from MassDOT
    Downloads and parses CSV files from annual/quarterly reports
    """

    def __init__(self):
        self.base_url = "https://www.mass.gov/info-details/transportation-network-company-tnc-reports"
        self.city = "Boston"
        self.state = "MA"
        self.data_source = "MassDOT TNC Reports"

    def fetch_report_urls(self) -> List[Dict[str, str]]:
        """
        Scrape the MassDOT page to find all TNC report CSV URLs

        Returns:
            List of dictionaries with report metadata
        """
        try:
            logger.info("Fetching MassDOT TNC report URLs")

            response = requests.get(self.base_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links to CSV files
            csv_links = []

            # Look for links containing "tnc", "rideshare", "transportation network"
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text().lower()

                # Check if it's a CSV or Excel file related to TNC
                if any(keyword in text for keyword in ['tnc', 'rideshare', 'transportation network']) and \
                   any(ext in href.lower() for ext in ['.csv', '.xlsx', '.xls']):

                    full_url = urljoin(self.base_url, href)

                    csv_links.append({
                        'url': full_url,
                        'title': link.get_text().strip(),
                        'type': 'csv' if '.csv' in href.lower() else 'excel'
                    })

            logger.info(f"Found {len(csv_links)} TNC report files")
            return csv_links

        except Exception as e:
            logger.error(f"Error fetching MassDOT report URLs: {e}")
            return []

    def download_csv(self, url: str) -> Optional[pd.DataFrame]:
        """
        Download and parse a CSV file

        Args:
            url: URL of the CSV file

        Returns:
            DataFrame or None if failed
        """
        try:
            logger.info(f"Downloading CSV from {url}")

            response = requests.get(url, timeout=60)
            response.raise_for_status()

            # Try to read CSV
            df = pd.read_csv(io.StringIO(response.text))
            logger.info(f"Successfully downloaded CSV with {len(df)} rows")

            return df

        except Exception as e:
            logger.error(f"Error downloading CSV from {url}: {e}")
            return None

    def download_excel(self, url: str) -> Optional[pd.DataFrame]:
        """
        Download and parse an Excel file

        Args:
            url: URL of the Excel file

        Returns:
            DataFrame or None if failed
        """
        try:
            logger.info(f"Downloading Excel from {url}")

            response = requests.get(url, timeout=60)
            response.raise_for_status()

            # Try to read Excel (first sheet)
            df = pd.read_excel(io.BytesIO(response.content), sheet_name=0)
            logger.info(f"Successfully downloaded Excel with {len(df)} rows")

            return df

        except Exception as e:
            logger.error(f"Error downloading Excel from {url}: {e}")
            return None

    def transform_data(self, df: pd.DataFrame, source_url: str = None) -> List[Dict]:
        """
        Transform raw CSV/Excel data to standardized format
        MassDOT format varies, so we need flexible parsing

        Args:
            df: Raw DataFrame from CSV/Excel
            source_url: URL of the source file

        Returns:
            List of dictionaries in standardized format
        """
        if df is None or df.empty:
            return []

        records = []

        try:
            # Normalize column names
            df.columns = df.columns.str.lower().str.strip()

            # Try to identify date column
            date_cols = ['date', 'month', 'period', 'report_date', 'report_period']
            date_column = None
            for col in date_cols:
                if col in df.columns:
                    date_column = col
                    break

            # Try to identify key metric columns
            driver_cols = ['drivers', 'active_drivers', 'unique_drivers', 'driver_count']
            ride_cols = ['rides', 'trips', 'total_rides', 'total_trips', 'trip_count']

            driver_col = None
            ride_col = None

            for col in driver_cols:
                if col in df.columns:
                    driver_col = col
                    break

            for col in ride_cols:
                if col in df.columns:
                    ride_col = col
                    break

            # If no date column, try to extract from report title or use today
            if not date_column:
                logger.warning("No date column found, using current date")
                default_date = datetime.now().date()
            else:
                default_date = None

            for idx, row in df.iterrows():
                try:
                    # Parse date
                    if date_column and pd.notna(row[date_column]):
                        date_str = str(row[date_column])
                        # Try multiple date formats
                        for fmt in ['%Y-%m-%d', '%Y-%m', '%m/%d/%Y', '%m-%d-%Y', '%Y']:
                            try:
                                date_obj = datetime.strptime(date_str[:10] if len(date_str) > 10 else date_str, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            date_obj = datetime.now()
                    else:
                        date_obj = datetime.now() if default_date is None else datetime.combine(default_date, datetime.min.time())

                    # Extract metrics
                    active_drivers = self._parse_int(row[driver_col]) if driver_col and driver_col in row else None
                    total_rides = self._parse_int(row[ride_col]) if ride_col and ride_col in row else None

                    # Skip row if no meaningful data
                    if not active_drivers and not total_rides:
                        continue

                    record = {
                        'city': self.city,
                        'state': self.state,
                        'date': date_obj.date(),
                        'active_drivers': active_drivers,
                        'total_rides': total_rides,
                        'total_trips': total_rides,
                        'data_source': self.data_source,
                        'source_url': source_url or self.base_url,
                        'data_quality': 'verified'
                    }

                    records.append(record)

                except Exception as e:
                    logger.warning(f"Error transforming row {idx}: {e}")
                    continue

            logger.info(f"Transformed {len(records)} records from MassDOT data")

        except Exception as e:
            logger.error(f"Error during data transformation: {e}")
            return []

        return records

    def _parse_int(self, value) -> Optional[int]:
        """Safely parse integer value"""
        if value is None or value == '' or pd.isna(value):
            return None
        try:
            # Remove commas and convert to int
            if isinstance(value, str):
                value = value.replace(',', '').strip()
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def scrape(self) -> List[Dict]:
        """
        Main scraping method - fetch and transform all available reports

        Returns:
            List of standardized records
        """
        logger.info("Starting MassDOT TNC scraper")

        # Get all report URLs
        report_urls = self.fetch_report_urls()

        if not report_urls:
            logger.warning("No report URLs found")
            return []

        all_records = []

        # Download and parse each report
        for report in report_urls[:10]:  # Limit to 10 most recent reports
            url = report['url']
            file_type = report['type']

            try:
                # Download based on file type
                if file_type == 'csv':
                    df = self.download_csv(url)
                else:
                    df = self.download_excel(url)

                if df is not None:
                    # Transform data
                    records = self.transform_data(df, source_url=url)
                    all_records.extend(records)

            except Exception as e:
                logger.error(f"Error processing report {url}: {e}")
                continue

        logger.info(f"MassDOT scraper completed: {len(all_records)} total records")
        return all_records


def main():
    """Test function for MassDOT scraper"""
    logging.basicConfig(level=logging.INFO)

    scraper = BostonMassDOTScraper()
    records = scraper.scrape()

    if records:
        print(f"\nFetched {len(records)} records")
        print("\nSample record:")
        print(records[0])
    else:
        print("No records fetched")


if __name__ == "__main__":
    main()
