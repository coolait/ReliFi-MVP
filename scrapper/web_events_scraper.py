#!/usr/bin/env python3
"""
Web Scraper for Event Websites
Scrapes public event discovery pages to find events by location

⚠️ WARNING: Web scraping may violate Terms of Service of some websites.
Use responsibly and respect rate limits.
"""

import requests
from bs4 import BeautifulSoup
import datetime
import re
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus
import random

class WebEventsScraper:
    """
    Scrapes event websites for location-based event data
    Supports multiple sources: Eventbrite, Meetup (fallback), etc.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        self.min_delay = 2  # Minimum delay between requests (seconds)
        self.last_request_time = 0
        self._geocode_cache = {}  # Cache for geocoding results
        self._event_date_cache = {}  # Cache for event dates
    
    def _rate_limit(self):
        """Respect rate limits by adding delay between requests"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed + random.uniform(0, 1))  # Add some randomness
        self.last_request_time = time.time()
    
    def get_events(self, location: str, lat: Optional[float] = None, lng: Optional[float] = None,
                   target_date: Optional[str] = None, radius: int = 10) -> Dict:
        """
        Get events from web scraping multiple sources
        """
        # Normalize location - if it looks like coordinates, geocode to city name
        actual_location = self._normalize_location(location, lat, lng)
        
        # Include both original location and normalized location in cache key to avoid cross-location caching
        # Also include lat/lng to ensure unique cache entries
        location_key = f"{actual_location}_{lat}_{lng}" if lat and lng else actual_location
        cache_key = f"web_events_{location_key}_{target_date}"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.datetime.now().timestamp() - timestamp < self.cache_ttl:
                print(f"  📦 Using cached events for {actual_location} on {target_date}")
                return cached_data
        
        events_data = {
            'events_found': 0,
            'demand_multiplier': 1.0,
            'source': 'default'
        }
        
        all_events = []
        sources_used = []
        
        # Try Eventbrite scraping (use actual_location, not raw location)
        # IMPORTANT: Wait for scraping to complete before returning
        try:
            print(f"  🔍 Starting Eventbrite scraping for {actual_location} on {target_date}...")
            eventbrite_events = self._scrape_eventbrite(actual_location, lat, lng, target_date)
            print(f"  ✅ Eventbrite scraping completed. Found {len(eventbrite_events)} total events.")
            
            if eventbrite_events:
                # Filter events by target_date (only count events on that specific date)
                if target_date:
                    print(f"  🔍 Filtering events by date {target_date}...")
                    filtered_events = self._filter_events_by_date(eventbrite_events, target_date)
                    all_events.extend(filtered_events)
                    print(f"  ✅ Eventbrite scraper: Found {len(filtered_events)} events on {target_date} (out of {len(eventbrite_events)} total)")
                else:
                    all_events.extend(eventbrite_events)
                    print(f"  ✅ Eventbrite scraper: Found {len(eventbrite_events)} events")
                
                if all_events:
                    sources_used.append('eventbrite')
        except Exception as e:
            print(f"  ⚠️  Eventbrite scraper error: {e}")
            import traceback
            traceback.print_exc()
        
        # Try additional sources (can add more)
        # For now, we'll focus on Eventbrite as it's the most comprehensive
        
        if all_events:
            events_data.update({
                'events_found': len(all_events),
                'demand_multiplier': self._calculate_demand_multiplier(len(all_events)),
                'source': '+'.join(sources_used)
            })
        else:
            # Fallback to time-based estimates
            events_data = self._get_time_based_estimate(target_date)
        
        self.cache[cache_key] = (events_data, datetime.datetime.now().timestamp())
        return events_data
    
    def _filter_events_by_date(self, events: List[Dict], target_date: str) -> List[Dict]:
        """
        Filter events to only include those on the target date
        Since we can't always parse dates from scraped HTML, we use a more lenient approach:
        - If date is found and matches: include
        - If date is found but doesn't match: exclude
        - If date is not found: exclude (to avoid counting future events)
        """
        if not target_date:
            return events  # No date filter, return all
        
        try:
            target_date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
        except:
            return events  # If date parsing fails, return all events
        
        filtered = []
        events_with_date = 0
        events_matching_date = 0
        
        for event in events:
            event_date = None
            
            # Try to extract date from event data
            if 'date' in event and event['date']:
                event_date_str = event['date']
                # Try various date formats
                date_formats = [
                    "%Y-%m-%d",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%d %H:%M:%S",
                    "%B %d, %Y",
                    "%b %d, %Y",
                    "%m/%d/%Y",
                    "%d/%m/%Y",
                    "%Y-%m-%d %H:%M",
                ]
                
                for fmt in date_formats:
                    try:
                        event_date = datetime.datetime.strptime(event_date_str, fmt).date()
                        events_with_date += 1
                        break
                    except:
                        continue
            
            # Only include events where:
            # 1. Date is found AND matches target date, OR
            # 2. Date is not found (we'll be conservative and exclude to avoid counting future events)
            # Actually, let's be more lenient: if we can't determine the date, we'll include it
            # but log a warning
            if event_date:
                if event_date == target_date_obj:
                    filtered.append(event)
                    events_matching_date += 1
                # else: date doesn't match, exclude it
            else:
                # No date found - be conservative and exclude to avoid counting future events
                # But we could include a small percentage to account for events we can't date
                pass
        
        if events_with_date > 0:
            print(f"    📅 Date filtering: {events_matching_date} events match {target_date} (out of {events_with_date} with dates, {len(events)} total)")
            # If we found some matching dates, return only those
            if events_matching_date > 0:
                return filtered
            # If no events match the date but we have dates, return empty (events are on different dates)
            elif events_with_date > 0:
                return filtered  # Return empty list
        else:
            # If we can't extract dates, use Eventbrite's date filter as fallback
            # Eventbrite's URL filter should have filtered events, so we trust it
            print(f"    ⚠️  Could not extract dates from events - trusting Eventbrite's date filter ({len(events)} events)")
            # Return all events (Eventbrite should have filtered them by date)
            return events
        
        return filtered
    
    def _normalize_location(self, location: str, lat: Optional[float] = None, lng: Optional[float] = None) -> str:
        """
        Normalize location string for Eventbrite URL
        - If location looks like coordinates, geocode to city name
        - If location is a city name, use it directly
        - If we have lat/lng but no good location, geocode
        - Has fallbacks if geocoding fails
        """
        # Check if location looks like coordinates (e.g., "37.7749,-122.4194" or "377749-1224194")
        if location and (',' in location or re.match(r'^\d+\.?\d*-?\d+\.?\d*$', location.replace('.', '').replace('-', ''))):
            # Looks like coordinates, need to geocode
            if lat and lng:
                # Try approximate lookup first (fast, no API call)
                city_name = self._approximate_city_from_coords(lat, lng)
                if city_name:
                    return city_name
                # Try geocoding API (slower, may timeout)
                city_name = self._geocode_to_city(lat, lng)
                if city_name:
                    return city_name
            # Try to parse coordinates from location string
            try:
                if ',' in location:
                    parts = location.split(',')
                    lat_val = float(parts[0].strip())
                    lng_val = float(parts[1].strip())
                    # Try approximate first
                    city_name = self._approximate_city_from_coords(lat_val, lng_val)
                    if city_name:
                        return city_name
                    # Try geocoding
                    city_name = self._geocode_to_city(lat_val, lng_val)
                    if city_name:
                        return city_name
            except:
                pass
        
        # If location is already a city name, preserve it with state code if present
        # We want to keep state codes for Eventbrite URL format (ca--san-francisco)
        location_clean = location.strip() if location else ''
        
        # Check if location already has state code (e.g., "San Francisco, CA")
        # If so, keep it - we'll extract it later for the URL
        has_state_code = bool(re.search(r',\s*[A-Z]{2}$', location_clean))
        
        # If we have lat/lng but location looks wrong or is coordinates, try geocoding
        if lat and lng:
            # Check if location_clean is still coordinates-like
            if not location_clean or re.match(r'^\d+\.?\d*-?\d+\.?\d*$', location_clean.replace('.', '').replace('-', '').replace(',', '')):
                # Try approximate first (with state code)
                city_name = self._approximate_city_from_coords(lat, lng)
                if city_name:
                    # Add state code based on coordinates
                    city_with_state = self._add_state_code(city_name, lat, lng)
                    return city_with_state
                # Try geocoding (with state code)
                city_name = self._geocode_to_city(lat, lng)
                if city_name:
                    return city_name
        
        # If location doesn't have state code but we have coordinates, try to add it
        if location_clean and not has_state_code and lat and lng:
            city_with_state = self._add_state_code(location_clean, lat, lng)
            if city_with_state != location_clean:
                return city_with_state
        
        # Final fallback - return location as-is if it looks valid
        if location_clean and not re.match(r'^\d+\.?\d*-?\d+\.?\d*$', location_clean.replace('.', '').replace('-', '').replace(',', '')):
            return location_clean
        
        # If we have coordinates but geocoding failed, use approximate or default
        if lat and lng:
            approximate = self._approximate_city_from_coords(lat, lng)
            if approximate:
                city_with_state = self._add_state_code(approximate, lat, lng)
                return city_with_state
        
        return 'San Francisco, CA'  # Ultimate fallback (with state code)
    
    def _geocode_to_city(self, lat: float, lng: float) -> Optional[str]:
        """
        Geocode coordinates to city name using Nominatim (OpenStreetMap)
        Has retry logic and fallback to approximate city lookup
        """
        # Check cache first
        cache_key = f"geocode_{lat:.2f}_{lng:.2f}"
        if hasattr(self, '_geocode_cache'):
            if cache_key in self._geocode_cache:
                return self._geocode_cache[cache_key]
        else:
            self._geocode_cache = {}
        
        # Try to use approximate lookup first (faster, no API call)
        approximate_city = self._approximate_city_from_coords(lat, lng)
        if approximate_city:
            self._geocode_cache[cache_key] = approximate_city
            return approximate_city
        
        # Try Nominatim API with retry logic
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Use Nominatim for reverse geocoding (free, no API key needed)
                url = "https://nominatim.openstreetmap.org/reverse"
                params = {
                    'lat': lat,
                    'lon': lng,
                    'format': 'json',
                    'addressdetails': 1
                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                
                self._rate_limit()
                # Increase timeout and add retry delay
                timeout = 15 if attempt == 0 else 20
                response = self.session.get(url, params=params, headers=headers, timeout=timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    address = data.get('address', {})
                    
                    # Try to get city name (various possible keys)
                    city = (address.get('city') or 
                           address.get('town') or 
                           address.get('village') or
                           address.get('municipality') or
                           address.get('county') or
                           address.get('state'))
                    
                    if city:
                        self._geocode_cache[cache_key] = city
                        return city
                elif response.status_code == 429:
                    # Rate limited, wait longer
                    time.sleep(2)
                    continue
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    # Wait before retry
                    time.sleep(1)
                    continue
                else:
                    # Final attempt failed, use fallback
                    print(f"  ⚠️  Geocoding timeout after {max_retries} attempts, using approximate city")
                    break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    print(f"  ⚠️  Geocoding error: {e}")
                    break
        
        # Fallback: Use approximate city lookup
        fallback_city = self._approximate_city_from_coords(lat, lng)
        if fallback_city:
            self._geocode_cache[cache_key] = fallback_city
            return fallback_city
        
        return None
    
    def _approximate_city_from_coords(self, lat: float, lng: float) -> Optional[str]:
        """
        Approximate city name from coordinates using known city coordinates
        Fast, no API call needed
        """
        # Major cities with their approximate coordinates
        major_cities = {
            'San Francisco': (37.7749, -122.4194),
            'New York': (40.7128, -74.0060),
            'Los Angeles': (34.0522, -118.2437),
            'Chicago': (41.8781, -87.6298),
            'Seattle': (47.6062, -122.3321),
            'Boston': (42.3601, -71.0589),
            'Austin': (30.2672, -97.7431),
            'Miami': (25.7617, -80.1918),
            'Denver': (39.7392, -104.9903),
            'Portland': (45.5152, -122.6784),
            'Philadelphia': (39.9526, -75.1652),
            'San Diego': (32.7157, -117.1611),
            'Dallas': (32.7767, -96.7970),
            'Houston': (29.7604, -95.3698),
            'Atlanta': (33.7490, -84.3880),
        }
        
        # Find closest city (within ~50 miles / 0.7 degrees)
        threshold = 0.7
        closest_city = None
        min_distance = float('inf')
        
        for city_name, (city_lat, city_lng) in major_cities.items():
            distance = ((lat - city_lat) ** 2 + (lng - city_lng) ** 2) ** 0.5
            if distance < threshold and distance < min_distance:
                min_distance = distance
                closest_city = city_name
        
        return closest_city
    
    def _add_state_code(self, city_name: str, lat: float, lng: float) -> str:
        """Add state code to city name based on coordinates"""
        # Map of major cities to their state codes
        city_state_map = {
            'San Francisco': 'CA', 'Los Angeles': 'CA', 'San Diego': 'CA', 'San Jose': 'CA',
            'Oakland': 'CA', 'Sacramento': 'CA', 'Fresno': 'CA', 'Long Beach': 'CA',
            'New York': 'NY', 'Buffalo': 'NY', 'Rochester': 'NY', 'Albany': 'NY',
            'Chicago': 'IL', 'Houston': 'TX', 'Dallas': 'TX', 'Austin': 'TX', 'San Antonio': 'TX',
            'Phoenix': 'AZ', 'Philadelphia': 'PA', 'San Antonio': 'TX', 'San Diego': 'CA',
            'Dallas': 'TX', 'San Jose': 'CA', 'Austin': 'TX', 'Jacksonville': 'FL',
            'Fort Worth': 'TX', 'Columbus': 'OH', 'Charlotte': 'NC', 'San Francisco': 'CA',
            'Indianapolis': 'IN', 'Seattle': 'WA', 'Denver': 'CO', 'Boston': 'MA',
            'El Paso': 'TX', 'Detroit': 'MI', 'Nashville': 'TN', 'Portland': 'OR',
            'Memphis': 'TN', 'Oklahoma City': 'OK', 'Las Vegas': 'NV', 'Louisville': 'KY',
            'Baltimore': 'MD', 'Milwaukee': 'WI', 'Albuquerque': 'NM', 'Tucson': 'AZ',
            'Fresno': 'CA', 'Sacramento': 'CA', 'Kansas City': 'MO', 'Mesa': 'AZ',
            'Atlanta': 'GA', 'Omaha': 'NE', 'Colorado Springs': 'CO', 'Raleigh': 'NC',
            'Virginia Beach': 'VA', 'Miami': 'FL', 'Oakland': 'CA', 'Minneapolis': 'MN',
            'Tulsa': 'OK', 'Cleveland': 'OH', 'Wichita': 'KS', 'Arlington': 'TX',
        }
        
        # Check if city already has state code
        if ', ' in city_name and len(city_name.split(', ')[-1]) == 2:
            return city_name  # Already has state code
        
        # Add state code if we know it
        if city_name in city_state_map:
            return f"{city_name}, {city_state_map[city_name]}"
        
        # Try to infer state from coordinates using approximate lookup
        # For major cities, we can infer the state from known coordinates
        major_cities_with_states = {
            (37.7749, -122.4194): ('San Francisco', 'CA'),
            (40.7128, -74.0060): ('New York', 'NY'),
            (34.0522, -118.2437): ('Los Angeles', 'CA'),
            (41.8781, -87.6298): ('Chicago', 'IL'),
            (47.6062, -122.3321): ('Seattle', 'WA'),
            (42.3601, -71.0589): ('Boston', 'MA'),
            (30.2672, -97.7431): ('Austin', 'TX'),
            (25.7617, -80.1918): ('Miami', 'FL'),
            (39.7392, -104.9903): ('Denver', 'CO'),
            (45.5152, -122.6784): ('Portland', 'OR'),
            (39.9526, -75.1652): ('Philadelphia', 'PA'),
            (32.7157, -117.1611): ('San Diego', 'CA'),
            (32.7767, -96.7970): ('Dallas', 'TX'),
            (29.7604, -95.3698): ('Houston', 'TX'),
            (33.7490, -84.3880): ('Atlanta', 'GA'),
        }
        
        # Check if coordinates match a known city
        threshold = 0.1  # ~10 miles
        for (city_lat, city_lng), (known_city, state_code) in major_cities_with_states.items():
            distance = ((lat - city_lat) ** 2 + (lng - city_lng) ** 2) ** 0.5
            if distance < threshold:
                return f"{city_name}, {state_code}"
        
        return city_name  # Return as-is if we can't determine state
    
    def _parse_event_date(self, date_text: str, target_date: Optional[str] = None) -> Optional[str]:
        """
        Parse event date from text and return in YYYY-MM-DD format
        Supports various formats including ISO 8601
        """
        if not date_text:
            return None
        
        # Clean up the date text
        date_text = date_text.strip()
        
        # Try ISO 8601 formats first (most common in JSON-LD)
        iso_formats = [
            "%Y-%m-%dT%H:%M:%S%z",  # 2025-11-12T18:00:00-0800
            "%Y-%m-%dT%H:%M:%SZ",   # 2025-11-12T18:00:00Z
            "%Y-%m-%dT%H:%M:%S",    # 2025-11-12T18:00:00
            "%Y-%m-%dT%H:%M",       # 2025-11-12T18:00
            "%Y-%m-%d",             # 2025-11-12
        ]
        
        for fmt in iso_formats:
            try:
                # Try parsing with timezone
                date_obj = datetime.datetime.strptime(date_text, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except:
                try:
                    # Try parsing without timezone info
                    date_text_clean = date_text.split('+')[0].split('-')[0] if '+' in date_text or (date_text.count('-') > 2) else date_text
                    date_text_clean = date_text_clean.replace('Z', '').strip()
                    date_obj = datetime.datetime.strptime(date_text_clean, fmt.replace('%z', '').replace('Z', ''))
                    return date_obj.strftime("%Y-%m-%d")
                except:
                    continue
        
        # Try other common formats
        date_formats = [
            "%B %d, %Y",      # November 12, 2025
            "%b %d, %Y",      # Nov 12, 2025
            "%m/%d/%Y",       # 11/12/2025
            "%d/%m/%Y",       # 12/11/2025
            "%Y-%m-%d %H:%M:%S",  # 2025-11-12 18:00:00
        ]
        
        # Try to find date-like patterns in text
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'([A-Za-z]+ \d{1,2}, \d{4})',  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_text)
            if match:
                date_str = match.group(1)
                for fmt in date_formats:
                    try:
                        date_obj = datetime.datetime.strptime(date_str, fmt)
                        return date_obj.strftime("%Y-%m-%d")
                    except:
                        continue
        
        # If target_date provided and we can't parse, try to infer from context
        if target_date:
            # Check if date_text mentions "today", "tomorrow", etc.
            date_text_lower = date_text.lower()
            if 'today' in date_text_lower:
                return target_date
            elif 'tomorrow' in date_text_lower:
                try:
                    target_date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
                    tomorrow = (target_date_obj + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                    return tomorrow
                except:
                    pass
        
        return None
    
    def _fetch_event_date(self, event_url: str, target_date: Optional[str] = None) -> Optional[str]:
        """
        Fetch event page to extract date information
        This is slower but more accurate than trying to parse from discovery page
        Uses caching to avoid fetching the same event multiple times
        """
        # Check cache first
        if hasattr(self, '_event_date_cache') and event_url in self._event_date_cache:
            return self._event_date_cache[event_url]
        
        try:
            self._rate_limit()
            response = self.session.get(event_url, timeout=10, allow_redirects=True)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Method 1: Look for JSON-LD structured data (most reliable)
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'Event':
                        start_date = data.get('startDate')
                        if start_date:
                            # Parse ISO 8601 date
                            event_date = self._parse_event_date(start_date, target_date)
                            if event_date:
                                # Cache it
                                if not hasattr(self, '_event_date_cache'):
                                    self._event_date_cache = {}
                                self._event_date_cache[event_url] = event_date
                                return event_date
                    elif isinstance(data, list):
                        # Handle list of events
                        for item in data:
                            if isinstance(item, dict) and item.get('@type') == 'Event':
                                start_date = item.get('startDate')
                                if start_date:
                                    event_date = self._parse_event_date(start_date, target_date)
                                    if event_date:
                                        if not hasattr(self, '_event_date_cache'):
                                            self._event_date_cache = {}
                                        self._event_date_cache[event_url] = event_date
                                        return event_date
                except:
                    continue
            
            # Method 2: Look for embedded JSON in scripts
            scripts = soup.find_all('script')
            for script in scripts:
                script_text = script.string or ''
                if 'startDate' in script_text or '"start_date"' in script_text:
                    # Try to extract date from JSON (various formats)
                    date_patterns = [
                        r'"startDate":\s*"([^"]+)"',
                        r'"start_date":\s*"([^"]+)"',
                        r'startDate["\']?\s*:\s*["\']([^"\']+)',
                    ]
                    for pattern in date_patterns:
                        date_match = re.search(pattern, script_text)
                        if date_match:
                            start_date = date_match.group(1)
                            event_date = self._parse_event_date(start_date, target_date)
                            if event_date:
                                if not hasattr(self, '_event_date_cache'):
                                    self._event_date_cache = {}
                                self._event_date_cache[event_url] = event_date
                                return event_date
                    
                    # Try ISO 8601 format directly
                    iso_match = re.search(r'(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}', script_text)
                    if iso_match:
                        event_date = iso_match.group(1)
                        if not hasattr(self, '_event_date_cache'):
                            self._event_date_cache = {}
                        self._event_date_cache[event_url] = event_date
                        return event_date
            
            # Method 3: Look for date in meta tags
            meta_tags = [
                ('meta', {'property': 'event:start_time'}),
                ('meta', {'name': 'start_date'}),
                ('meta', {'property': 'og:start_time'}),
            ]
            for tag_name, attrs in meta_tags:
                meta_date = soup.find(tag_name, attrs)
                if meta_date and meta_date.get('content'):
                    event_date = self._parse_event_date(meta_date.get('content'), target_date)
                    if event_date:
                        if not hasattr(self, '_event_date_cache'):
                            self._event_date_cache = {}
                        self._event_date_cache[event_url] = event_date
                        return event_date
            
        except Exception as e:
            # Silently fail - don't spam errors
            pass
        
        return None
    
    def _scrape_eventbrite(self, location: str, lat: Optional[float] = None, lng: Optional[float] = None,
                           target_date: Optional[str] = None) -> List[Dict]:
        """
        Scrape Eventbrite's public discovery page
        ⚠️ WARNING: This may violate Eventbrite's Terms of Service
        Use responsibly and respect rate limits
        
        Eventbrite uses React/JavaScript to render content, so we need to:
        1. Look for JSON data embedded in page
        2. Parse event links
        3. Use heuristics to estimate event count
        """
        events = []
        
        try:
            # Clean location for URL (Eventbrite needs city names, not coordinates)
            # Remove any coordinates-like patterns
            location_clean = location.strip()
            if not location_clean or re.match(r'^\d+\.?\d*-?\d+\.?\d*$', location_clean.replace('.', '').replace('-', '').replace(',', '')):
                # This looks like coordinates, can't use for Eventbrite URL
                print(f"  ⚠️  Cannot scrape Eventbrite with coordinates: {location}")
                return events
            
            # Build Eventbrite discovery URL
            # Format: https://www.eventbrite.com/d/ca--san-francisco/all-events/?start_date=2025-11-08&end_date=2025-11-08
            # Eventbrite uses state--city format and /all-events/ endpoint with query parameters
            
            # Try to extract state code from location (e.g., "San Francisco, CA" -> "ca")
            state_code = None
            location_parts = location_clean.split(',')
            if len(location_parts) > 1:
                state_part = location_parts[-1].strip().upper()
                # Map common state names to codes
                state_map = {
                    'CA': 'ca', 'CALIFORNIA': 'ca',
                    'NY': 'ny', 'NEW YORK': 'ny',
                    'TX': 'tx', 'TEXAS': 'tx',
                    'FL': 'fl', 'FLORIDA': 'fl',
                    'IL': 'il', 'ILLINOIS': 'il',
                    'PA': 'pa', 'PENNSYLVANIA': 'pa',
                    'AZ': 'az', 'ARIZONA': 'az',
                    'MA': 'ma', 'MASSACHUSETTS': 'ma',
                    'TN': 'tn', 'TENNESSEE': 'tn',
                    'WA': 'wa', 'WASHINGTON': 'wa',
                    'CO': 'co', 'COLORADO': 'co',
                    'MI': 'mi', 'MICHIGAN': 'mi',
                    'NC': 'nc', 'NORTH CAROLINA': 'nc',
                    'GA': 'ga', 'GEORGIA': 'ga',
                }
                if state_part in state_map:
                    state_code = state_map[state_part]
                elif len(state_part) == 2:
                    state_code = state_part.lower()
            
            # Clean location name (remove state, country, etc.)
            city_name = location_parts[0].strip() if location_parts else location_clean
            city_slug = city_name.lower().replace(' ', '-').replace(',', '').replace('.', '')
            # Remove multiple dashes
            city_slug = re.sub(r'-+', '-', city_slug).strip('-')
            
            # Build location variations
            location_variations = []
            if state_code:
                # Try state--city format first (most accurate for Eventbrite)
                location_variations.append(f"{state_code}--{city_slug}")
            location_variations.append(city_slug)
            location_variations.append(city_name.lower().replace(' ', '-'))
            
            urls_to_try = []
            for loc_var in location_variations:
                # Use /all-events/ endpoint with query parameters (matches Eventbrite's date picker)
                base_url = f"https://www.eventbrite.com/d/{loc_var}/all-events/"
                
                if target_date:
                    try:
                        # Use query parameters: ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
                        # This matches the actual Eventbrite URL format when using date picker
                        url_with_date = f"{base_url}?start_date={target_date}&end_date={target_date}"
                        urls_to_try.append(url_with_date)
                    except Exception as e:
                        print(f"  ⚠️  Error formatting date for URL: {e}")
                        pass
                else:
                    # If no date, use base URL
                    urls_to_try.append(base_url)
                
                # Only try first variation (state--city format) if it exists
                if state_code and loc_var == f"{state_code}--{city_slug}":
                    break
            
            # Scrape multiple pages (up to 3 pages to get more events, but respect rate limits)
            max_pages = 3  # Reduced to 3 pages to avoid too many requests
            seen_event_ids = set()
            
            # Use the first URL (prefer date-filtered if available)
            # Fallback to first location variation if no URLs generated
            if not urls_to_try:
                # Generate a fallback URL with the first location variation
                fallback_loc = location_variations[0] if location_variations else city_slug
                url_base = f"https://www.eventbrite.com/d/{fallback_loc}/all-events/"
            else:
                url_base = urls_to_try[0]
            
            for page in range(1, max_pages + 1):
                try:
                    # Add page parameter if not first page
                    # Eventbrite pagination: ?page=2, ?page=3, etc.
                    if page > 1:
                        if '?' in url_base:
                            url = f"{url_base}&page={page}"
                        else:
                            url = f"{url_base}?page={page}"
                    else:
                        url = url_base
                    
                    self._rate_limit()
                    
                    print(f"  🌐 Scraping Eventbrite page {page} for {location}: {url}")
                    response = self.session.get(url, timeout=15, allow_redirects=True)
                    
                    if response.status_code != 200:
                        if page == 1:
                            print(f"  ⚠️  Eventbrite returned status {response.status_code}")
                        else:
                            # No more pages available
                            break
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                        
                    # Method 1: Look for event links (most reliable)
                    # Eventbrite event URLs follow patterns:
                    # - /e/event-name-tickets-{id}?aff=...
                    # - /e/event-name-{id}/
                    # - https://www.eventbrite.com/e/event-name-tickets-{id}
                    event_links = soup.find_all('a', href=re.compile(r'/e/'))
                    page_events_count = 0
                    
                    for link in event_links:
                        href = link.get('href', '')
                        if href and '/e/' in href and 'tickets' in href.lower():
                            # Extract event ID from URL (various patterns)
                            # Pattern: /e/event-name-tickets-{id} or /e/event-name-{id}
                            match = re.search(r'/e/[^/\s?]+-(\d+)', href)
                            if match:
                                event_id = match.group(1)
                                # Event IDs are usually 10+ digits
                                if event_id not in seen_event_ids and len(event_id) >= 10:
                                    seen_event_ids.add(event_id)
                                    
                                    # Try to get event title - be more flexible
                                    event_title = link.get_text(strip=True)
                                    parent = link.find_parent(['div', 'article', 'li', 'section'])
                                    
                                    # If no title from link text, try various methods
                                    if not event_title or len(event_title) < 3:
                                        if parent:
                                            # Try to find title in parent
                                            title_elem = (parent.find(['h2', 'h3', 'h4', 'h5'], 
                                                                     class_=re.compile(r'title|name|event|heading', re.I)) or
                                                         parent.find('span', class_=re.compile(r'title|name', re.I)) or
                                                         parent.find('div', class_=re.compile(r'title|name|event', re.I)))
                                            if title_elem:
                                                event_title = title_elem.get_text(strip=True)
                                    
                                    # If still no title, use a default based on URL
                                    if not event_title or len(event_title) < 3:
                                        # Extract from URL as fallback
                                        url_parts = href.split('/e/')
                                        if len(url_parts) > 1:
                                            event_slug = url_parts[1].split('-tickets-')[0].replace('-', ' ').title()
                                            event_title = event_slug or f'Event {event_id}'
                                    
                                    # Try to extract event date
                                    # Since Eventbrite renders dates via JavaScript, we'll fetch the event page
                                    # IMPORTANT: Fetch dates for ALL events to ensure accurate filtering
                                    # This ensures we only count events on the target date
                                    event_date = None
                                    event_page_url = href if href.startswith('http') else f"https://www.eventbrite.com{href.split('?')[0]}"
                                    
                                    # Always fetch date for events when target_date is specified
                                    # This is slower but ensures accuracy
                                    if target_date:
                                        try:
                                            event_date = self._fetch_event_date(event_page_url, target_date)
                                            if event_date:
                                                # Cache the date for this event URL
                                                if not hasattr(self, '_event_date_cache'):
                                                    self._event_date_cache = {}
                                                self._event_date_cache[event_page_url] = event_date
                                        except Exception as e:
                                            # Silently fail - we'll filter by URL date filter as fallback
                                            pass
                                    else:
                                        # If no target date, check cache for dates we've already fetched
                                        if hasattr(self, '_event_date_cache'):
                                            event_date = self._event_date_cache.get(event_page_url)
                                    
                                    # Method 2: Look for date in parent HTML (may not work due to JS rendering)
                                    if not event_date and parent:
                                        # Look for <time> element with datetime attribute
                                        time_elem = parent.find('time')
                                        if time_elem and time_elem.get('datetime'):
                                            datetime_str = time_elem.get('datetime')
                                            event_date = self._parse_event_date(datetime_str, target_date)
                                        
                                        # Look for date in text content
                                        if not event_date:
                                            parent_text = parent.get_text()
                                            # Look for date patterns in text
                                            date_patterns = [
                                                r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
                                                r'([A-Za-z]+ \d{1,2}, \d{4})',  # Month DD, YYYY
                                                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # MM/DD/YYYY
                                            ]
                                            for pattern in date_patterns:
                                                match = re.search(pattern, parent_text)
                                                if match:
                                                    date_text = match.group(1)
                                                    event_date = self._parse_event_date(date_text, target_date)
                                                    if event_date:
                                                        break
                                        
                                        # Look for date-related elements
                                        if not event_date:
                                            date_elems = parent.find_all(['span', 'div', 'p'], 
                                                                         class_=re.compile(r'date|time|start|when|event-date', re.I))
                                            for date_elem in date_elems:
                                                date_text = date_elem.get_text(strip=True)
                                                if date_text:
                                                    event_date = self._parse_event_date(date_text, target_date)
                                                    if event_date:
                                                        break
                                    
                                    # Add event even if no title (we have event_id)
                                    events.append({
                                        'name': event_title or f'Event in {location}',
                                        'url': href if href.startswith('http') else f"https://www.eventbrite.com{href.split('?')[0]}",
                                        'location': location,
                                        'event_id': event_id,
                                        'date': event_date
                                    })
                                    page_events_count += 1
                    
                    # If we found events on this page, continue to next page
                    if page_events_count > 0:
                        print(f"    Found {page_events_count} events on page {page}")
                        # Continue to next page
                        continue
                    else:
                        # No events on this page, stop pagination
                        if page == 1:
                            # Try alternative methods only on first page if no events found
                            # Method 2: Look for JSON-LD structured data
                            json_ld_scripts = soup.find_all('script', type='application/ld+json')
                            for script in json_ld_scripts:
                                try:
                                    import json
                                    data = json.loads(script.string)
                                    # Handle both single events and lists
                                    if isinstance(data, dict):
                                        if data.get('@type') == 'Event':
                                            events.append({
                                                'name': data.get('name', ''),
                                                'date': data.get('startDate', ''),
                                                'location': data.get('location', {}).get('name', location)
                                            })
                                    elif isinstance(data, list):
                                        for item in data:
                                            if isinstance(item, dict) and item.get('@type') == 'Event':
                                                events.append({
                                                    'name': item.get('name', ''),
                                                    'date': item.get('startDate', ''),
                                                    'location': item.get('location', {}).get('name', location)
                                                })
                                except:
                                    pass
                            
                            # If still no events, break
                            if not events:
                                break
                        else:
                            # No events on subsequent page, stop pagination
                            break
                        
                except Exception as e:
                    if page == 1:
                        print(f"  ⚠️  Error trying URL {url}: {e}")
                    # Continue to next page or break
                    if page > 1:
                        break
                    continue
            
            print(f"  📊 Total events found across all pages for {location}: {len(events)}")
            
        except Exception as e:
            print(f"  ❌ Error scraping Eventbrite: {e}")
            import traceback
            traceback.print_exc()
        
        return events
    
    def _parse_eventbrite_event(self, element, location: str) -> Optional[Dict]:
        """Parse a single Eventbrite event element"""
        try:
            event_data = {
                'name': '',
                'date': '',
                'location': location,
                'url': ''
            }
            
            # Try to extract event name
            title_elem = element.find(['h2', 'h3', 'h4', 'div[class*="title"]', 'div[class*="name"]'])
            if title_elem:
                event_data['name'] = title_elem.get_text(strip=True)
            else:
                # Try data attributes
                event_data['name'] = element.get('data-event-name', '') or element.get('aria-label', '')
            
            # Try to extract event URL
            link_elem = element.find('a', href=True)
            if link_elem:
                href = link_elem.get('href', '')
                if href:
                    if href.startswith('/'):
                        event_data['url'] = f"https://www.eventbrite.com{href}"
                    else:
                        event_data['url'] = href
            
            # Try to extract date
            date_elem = element.find(['time', 'span[class*="date"]', 'div[class*="date"]'])
            if date_elem:
                event_data['date'] = date_elem.get_text(strip=True)
            
            # Only return if we found at least a name
            if event_data['name']:
                return event_data
            
        except Exception as e:
            print(f"    ⚠️  Error parsing event element: {e}")
        
        return None
    
    def _calculate_demand_multiplier(self, event_count: int) -> float:
        """
        Calculate demand multiplier based on number of events found
        More events = higher demand for rideshare/delivery
        """
        if event_count == 0:
            return 1.0
        
        # Base multiplier increases with event count
        # 1 event: +2.5%, 10 events: +25%, 20+ events: +50% max
        multiplier = 1.0 + (min(event_count, 20) * 0.025)
        return round(multiplier, 2)
    
    def _get_time_based_estimate(self, target_date: Optional[str] = None) -> Dict:
        """Fallback to time-based estimates"""
        events_data = {
            'events_found': 0,
            'demand_multiplier': 1.0,
            'source': 'time_estimate'
        }
        
        if target_date:
            try:
                date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
                weekday = date_obj.weekday()
                is_weekend = weekday >= 5
                
                if is_weekend:
                    events_data['demand_multiplier'] = 1.3
                    events_data['source'] = 'time_estimate_weekend'
                elif weekday == 4:  # Friday
                    events_data['demand_multiplier'] = 1.2
                    events_data['source'] = 'time_estimate_friday'
            except:
                pass
        
        return events_data

