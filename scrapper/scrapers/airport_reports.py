"""
Airport Ground Transportation Reports Scraper
Downloads monthly reports from LAX and SFO airports
LAX: Los Angeles International Airport
SFO: San Francisco International Airport
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
import pdfplumber
import tempfile
import os

logger = logging.getLogger(__name__)


class AirportReportsScraper:
    """
    Scraper for airport ground transportation reports
    Supports LAX and SFO
    """

    def __init__(self):
        self.lax_url = "https://www.lawa.org/en/lawa-airport-experience/ground-transportation/dashboards-and-reports"
        self.sfo_url = "https://www.flysfo.com/content/ground-transportation-operators"
        self.data_source = "Airport Ground Transportation Reports"

    def scrape_lax(self) -> List[Dict]:
        """
        Scrape LAX ground transportation reports

        Returns:
            List of records from LAX
        """
        logger.info("Starting LAX scraper")
        records = []

        try:
            response = requests.get(self.lax_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find links to reports (Excel, PDF, CSV)
            report_links = []

            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text().lower()

                # Look for TNC/rideshare reports
                if any(keyword in text for keyword in ['tnc', 'rideshare', 'ground transportation', 'monthly report']):
                    if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.pdf', '.csv']):
                        full_url = urljoin(self.lax_url, href)
                        report_links.append({
                            'url': full_url,
                            'title': link.get_text().strip(),
                            'type': self._get_file_type(href)
                        })

            logger.info(f"Found {len(report_links)} LAX reports")

            # Process each report
            for report in report_links[:5]:  # Limit to 5 most recent
                try:
                    report_records = self._process_report(
                        report['url'],
                        report['type'],
                        city="Los Angeles",
                        state="CA"
                    )
                    records.extend(report_records)

                except Exception as e:
                    logger.error(f"Error processing LAX report {report['url']}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping LAX: {e}")

        logger.info(f"LAX scraper completed: {len(records)} records")
        return records

    def scrape_sfo(self) -> List[Dict]:
        """
        Scrape SFO ground transportation reports

        Returns:
            List of records from SFO
        """
        logger.info("Starting SFO scraper")
        records = []

        try:
            response = requests.get(self.sfo_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find links to reports
            report_links = []

            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text().lower()

                # Look for TNC/rideshare reports
                if any(keyword in text for keyword in ['tnc', 'rideshare', 'ground transportation', 'report']):
                    if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.pdf', '.csv']):
                        full_url = urljoin(self.sfo_url, href)
                        report_links.append({
                            'url': full_url,
                            'title': link.get_text().strip(),
                            'type': self._get_file_type(href)
                        })

            logger.info(f"Found {len(report_links)} SFO reports")

            # Process each report
            for report in report_links[:5]:  # Limit to 5 most recent
                try:
                    report_records = self._process_report(
                        report['url'],
                        report['type'],
                        city="San Francisco",
                        state="CA"
                    )
                    records.extend(report_records)

                except Exception as e:
                    logger.error(f"Error processing SFO report {report['url']}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping SFO: {e}")

        logger.info(f"SFO scraper completed: {len(records)} records")
        return records

    def _get_file_type(self, url: str) -> str:
        """Determine file type from URL"""
        url_lower = url.lower()
        if '.xlsx' in url_lower or '.xls' in url_lower:
            return 'excel'
        elif '.csv' in url_lower:
            return 'csv'
        elif '.pdf' in url_lower:
            return 'pdf'
        return 'unknown'

    def _process_report(self, url: str, file_type: str, city: str, state: str) -> List[Dict]:
        """
        Download and process a report file

        Args:
            url: URL of the report
            file_type: Type of file (excel, csv, pdf)
            city: City name
            state: State code

        Returns:
            List of records
        """
        logger.info(f"Processing {file_type} report: {url}")

        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            if file_type == 'excel':
                df = pd.read_excel(io.BytesIO(response.content), sheet_name=0)
                return self._parse_dataframe(df, city, state, url)

            elif file_type == 'csv':
                df = pd.read_csv(io.StringIO(response.text))
                return self._parse_dataframe(df, city, state, url)

            elif file_type == 'pdf':
                return self._parse_pdf(response.content, city, state, url)

        except Exception as e:
            logger.error(f"Error processing report: {e}")
            return []

        return []

    def _parse_dataframe(self, df: pd.DataFrame, city: str, state: str, source_url: str) -> List[Dict]:
        """
        Parse DataFrame from Excel/CSV

        Args:
            df: DataFrame to parse
            city: City name
            state: State code
            source_url: Source URL

        Returns:
            List of records
        """
        if df is None or df.empty:
            return []

        records = []

        try:
            # Normalize column names
            df.columns = df.columns.str.lower().str.strip()

            # Find relevant columns
            date_col = None
            for col in ['date', 'month', 'period', 'report_date']:
                if col in df.columns:
                    date_col = col
                    break

            driver_col = None
            for col in ['drivers', 'active_drivers', 'driver_count', 'vehicles']:
                if col in df.columns:
                    driver_col = col
                    break

            trip_col = None
            for col in ['trips', 'rides', 'pickups', 'total_trips']:
                if col in df.columns:
                    trip_col = col
                    break

            # Parse rows
            for _, row in df.iterrows():
                try:
                    # Parse date
                    if date_col and pd.notna(row[date_col]):
                        date_str = str(row[date_col])
                        date_obj = pd.to_datetime(date_str).date()
                    else:
                        date_obj = datetime.now().date()

                    # Extract metrics
                    drivers = self._parse_int(row[driver_col]) if driver_col else None
                    trips = self._parse_int(row[trip_col]) if trip_col else None

                    if not drivers and not trips:
                        continue

                    record = {
                        'city': city,
                        'state': state,
                        'date': date_obj,
                        'active_drivers': drivers,
                        'total_rides': trips,
                        'total_trips': trips,
                        'data_source': self.data_source,
                        'source_url': source_url,
                        'data_quality': 'verified',
                        'notes': f'Airport ground transportation data for {city}'
                    }

                    records.append(record)

                except Exception as e:
                    logger.warning(f"Error parsing row: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing DataFrame: {e}")

        return records

    def _parse_pdf(self, pdf_content: bytes, city: str, state: str, source_url: str) -> List[Dict]:
        """
        Parse PDF report

        Args:
            pdf_content: PDF content as bytes
            city: City name
            state: State code
            source_url: Source URL

        Returns:
            List of records
        """
        records = []

        try:
            # Write to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_content)
                tmp_path = tmp_file.name

            # Extract tables
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages:
                    try:
                        tables = page.extract_tables()

                        for table in tables:
                            if table and len(table) > 1:
                                df = pd.DataFrame(table[1:], columns=table[0])
                                table_records = self._parse_dataframe(df, city, state, source_url)
                                records.extend(table_records)

                    except Exception as e:
                        logger.warning(f"Error extracting table from PDF page: {e}")
                        continue

            # Clean up
            try:
                os.unlink(tmp_path)
            except:
                pass

        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")

        return records

    def _parse_int(self, value) -> Optional[int]:
        """Safely parse integer value"""
        if value is None or value == '' or pd.isna(value):
            return None
        try:
            if isinstance(value, str):
                value = value.replace(',', '').strip()
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def scrape(self) -> List[Dict]:
        """
        Main scraping method - scrape both LAX and SFO

        Returns:
            Combined list of records from both airports
        """
        logger.info("Starting Airport Reports scraper")

        all_records = []

        # Scrape LAX
        lax_records = self.scrape_lax()
        all_records.extend(lax_records)

        # Scrape SFO
        sfo_records = self.scrape_sfo()
        all_records.extend(sfo_records)

        logger.info(f"Airport Reports scraper completed: {len(all_records)} total records")
        return all_records


def main():
    """Test function for Airport Reports scraper"""
    logging.basicConfig(level=logging.INFO)

    scraper = AirportReportsScraper()
    records = scraper.scrape()

    if records:
        print(f"\nFetched {len(records)} records")
        print("\nSample record:")
        print(records[0])
    else:
        print("No records fetched")


if __name__ == "__main__":
    main()
