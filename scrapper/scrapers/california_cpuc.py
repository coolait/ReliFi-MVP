"""
California CPUC (Public Utilities Commission) TNC Data Scraper
Downloads and parses PDF reports to extract driver/trip counts
Source: https://www.cpuc.ca.gov/tncinfo
"""

import requests
import pdfplumber
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple
import io
import re
from urllib.parse import urljoin
import tempfile
import os

logger = logging.getLogger(__name__)


class CaliforniaCPUCScraper:
    """
    Scraper for California CPUC TNC data
    Downloads and parses PDF reports to extract rideshare statistics
    """

    def __init__(self):
        self.base_url = "https://www.cpuc.ca.gov/industries-and-topics/ride-hailing/tncinfo"
        self.alternate_url = "https://www.cpuc.ca.gov/tncinfo"
        self.state = "CA"
        self.data_source = "California CPUC"

    def fetch_pdf_urls(self) -> List[Dict[str, str]]:
        """
        Scrape CPUC website to find all TNC report PDF URLs

        Returns:
            List of dictionaries with PDF metadata
        """
        pdf_links = []

        for url in [self.base_url, self.alternate_url]:
            try:
                logger.info(f"Fetching CPUC TNC report URLs from {url}")

                response = requests.get(url, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all PDF links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.get_text().lower()

                    # Check if it's a TNC-related PDF
                    if '.pdf' in href.lower() and any(keyword in text for keyword in ['tnc', 'annual', 'report', 'quarterly']):
                        full_url = urljoin(url, href)

                        pdf_links.append({
                            'url': full_url,
                            'title': link.get_text().strip(),
                            'year': self._extract_year(link.get_text())
                        })

                if pdf_links:
                    logger.info(f"Found {len(pdf_links)} PDF reports from {url}")
                    break  # Stop if we found PDFs

            except Exception as e:
                logger.warning(f"Error fetching from {url}: {e}")
                continue

        return pdf_links

    def _extract_year(self, text: str) -> Optional[int]:
        """Extract year from text"""
        match = re.search(r'20\d{2}', text)
        if match:
            return int(match.group())
        return None

    def download_pdf(self, url: str) -> Optional[bytes]:
        """
        Download PDF file

        Args:
            url: URL of the PDF

        Returns:
            PDF content as bytes or None if failed
        """
        try:
            logger.info(f"Downloading PDF from {url}")

            response = requests.get(url, timeout=60)
            response.raise_for_status()

            logger.info(f"Successfully downloaded PDF ({len(response.content)} bytes)")
            return response.content

        except Exception as e:
            logger.error(f"Error downloading PDF from {url}: {e}")
            return None

    def extract_tables_from_pdf(self, pdf_content: bytes) -> List[pd.DataFrame]:
        """
        Extract tables from PDF using pdfplumber

        Args:
            pdf_content: PDF content as bytes

        Returns:
            List of DataFrames extracted from PDF tables
        """
        tables = []

        try:
            # Write to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_content)
                tmp_path = tmp_file.name

            # Extract tables from PDF
            with pdfplumber.open(tmp_path) as pdf:
                logger.info(f"Extracting tables from PDF ({len(pdf.pages)} pages)")

                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_tables = page.extract_tables()

                        for table in page_tables:
                            if table and len(table) > 1:  # Has header and at least one row
                                df = pd.DataFrame(table[1:], columns=table[0])
                                tables.append(df)

                    except Exception as e:
                        logger.warning(f"Error extracting tables from page {page_num}: {e}")
                        continue

            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass

            logger.info(f"Extracted {len(tables)} tables from PDF")

        except Exception as e:
            logger.error(f"Error extracting tables from PDF: {e}")

        return tables

    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extract all text from PDF

        Args:
            pdf_content: PDF content as bytes

        Returns:
            Extracted text
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_content)
                tmp_path = tmp_file.name

            text = ""
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"

            # Clean up
            try:
                os.unlink(tmp_path)
            except:
                pass

            return text

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

    def parse_pdf_data(self, pdf_content: bytes, year: Optional[int] = None) -> List[Dict]:
        """
        Parse PDF to extract rideshare statistics

        Args:
            pdf_content: PDF content as bytes
            year: Year of the report (for date assignment)

        Returns:
            List of records in standardized format
        """
        records = []

        try:
            # Extract tables
            tables = self.extract_tables_from_pdf(pdf_content)

            # Extract text for pattern matching
            text = self.extract_text_from_pdf(pdf_content)

            # Try to parse tables first
            for df in tables:
                table_records = self._parse_table(df, year)
                records.extend(table_records)

            # If no records from tables, try text parsing
            if not records:
                text_records = self._parse_text(text, year)
                records.extend(text_records)

        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")

        return records

    def _parse_table(self, df: pd.DataFrame, year: Optional[int]) -> List[Dict]:
        """Parse a DataFrame table from PDF"""
        records = []

        try:
            # Normalize column names
            df.columns = df.columns.astype(str).str.lower().str.strip()

            # Look for key columns
            city_cols = ['city', 'location', 'area', 'region']
            driver_cols = ['drivers', 'active drivers', 'driver count']
            trip_cols = ['trips', 'rides', 'total trips', 'trip count']

            city_col = None
            driver_col = None
            trip_col = None

            for col in df.columns:
                if any(c in col for c in city_cols):
                    city_col = col
                if any(c in col for c in driver_cols):
                    driver_col = col
                if any(c in col for c in trip_cols):
                    trip_col = col

            # Parse rows
            for _, row in df.iterrows():
                try:
                    city = self._extract_city(row[city_col]) if city_col else None
                    drivers = self._parse_int(row[driver_col]) if driver_col else None
                    trips = self._parse_int(row[trip_col]) if trip_col else None

                    if not city or (not drivers and not trips):
                        continue

                    # Use year for date, default to January 1st
                    if year:
                        date_obj = datetime(year, 1, 1).date()
                    else:
                        date_obj = datetime.now().date()

                    record = {
                        'city': city,
                        'state': self.state,
                        'date': date_obj,
                        'active_drivers': drivers,
                        'total_rides': trips,
                        'total_trips': trips,
                        'data_source': self.data_source,
                        'source_url': self.base_url,
                        'data_quality': 'estimated',
                        'notes': 'Extracted from CPUC PDF report'
                    }

                    records.append(record)

                except Exception as e:
                    logger.warning(f"Error parsing table row: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Error parsing table: {e}")

        return records

    def _parse_text(self, text: str, year: Optional[int]) -> List[Dict]:
        """Parse raw text to extract statistics"""
        records = []

        try:
            # Pattern matching for common report formats
            # Example: "Los Angeles: 150,000 drivers, 50 million trips"

            # Look for city names followed by numbers
            ca_cities = ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento',
                        'San Jose', 'Oakland', 'Fresno', 'Long Beach']

            for city in ca_cities:
                # Find mentions of this city with numbers
                pattern = rf'{city}[:\s]+.*?(\d{{1,3}}(?:,\d{{3}})*)\s*(?:drivers?|active\s*drivers?)'
                driver_match = re.search(pattern, text, re.IGNORECASE)

                pattern_trips = rf'{city}[:\s]+.*?(\d{{1,3}}(?:,\d{{3}})*)\s*(?:trips?|rides?)'
                trip_match = re.search(pattern_trips, text, re.IGNORECASE)

                if driver_match or trip_match:
                    drivers = self._parse_int(driver_match.group(1)) if driver_match else None
                    trips = self._parse_int(trip_match.group(1)) if trip_match else None

                    if year:
                        date_obj = datetime(year, 1, 1).date()
                    else:
                        date_obj = datetime.now().date()

                    record = {
                        'city': city,
                        'state': self.state,
                        'date': date_obj,
                        'active_drivers': drivers,
                        'total_rides': trips,
                        'total_trips': trips,
                        'data_source': self.data_source,
                        'source_url': self.base_url,
                        'data_quality': 'estimated',
                        'notes': 'Extracted from CPUC PDF text'
                    }

                    records.append(record)

        except Exception as e:
            logger.warning(f"Error parsing text: {e}")

        return records

    def _extract_city(self, value) -> Optional[str]:
        """Extract city name from value"""
        if pd.isna(value) or value == '':
            return None

        city_str = str(value).strip()

        # Clean up common formatting
        city_str = re.sub(r'[^a-zA-Z\s]', '', city_str)

        return city_str if city_str else None

    def _parse_int(self, value) -> Optional[int]:
        """Safely parse integer value (handles commas)"""
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
        Main scraping method - download and parse all PDFs

        Returns:
            List of standardized records
        """
        logger.info("Starting California CPUC scraper")

        # Get PDF URLs
        pdf_urls = self.fetch_pdf_urls()

        if not pdf_urls:
            logger.warning("No PDF URLs found")
            return []

        all_records = []

        # Process each PDF (limit to 5 most recent)
        for pdf_info in pdf_urls[:5]:
            url = pdf_info['url']
            year = pdf_info['year']

            try:
                # Download PDF
                pdf_content = self.download_pdf(url)

                if pdf_content:
                    # Parse PDF
                    records = self.parse_pdf_data(pdf_content, year=year)
                    all_records.extend(records)

            except Exception as e:
                logger.error(f"Error processing PDF {url}: {e}")
                continue

        logger.info(f"CPUC scraper completed: {len(all_records)} total records")
        return all_records


def main():
    """Test function for CPUC scraper"""
    logging.basicConfig(level=logging.INFO)

    scraper = CaliforniaCPUCScraper()
    records = scraper.scrape()

    if records:
        print(f"\nFetched {len(records)} records")
        print("\nSample record:")
        print(records[0])
    else:
        print("No records fetched")


if __name__ == "__main__":
    main()
