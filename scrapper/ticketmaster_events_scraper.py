#!/usr/bin/env python3
"""
Ticketmaster Discovery API Integration for Real-Time Events Data
Provides location-based event search using Ticketmaster Discovery API
"""

import requests
import datetime
import time
from typing import Dict, List, Optional, Tuple
from data_sources import DataSourcesConfig
import base64

class TicketmasterEventsScraper:
    """
    Fetches real-time events data from Ticketmaster Discovery API
    Provides event boost calculation based on attendance/capacity
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache for events
        self.base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
        self.min_delay = 0.5  # Minimum delay between requests to avoid rate limits (seconds)
        self.last_request_time = 0
    
    def get_events(self, location: str, lat: Optional[float] = None, lng: Optional[float] = None,
                   target_date: Optional[str] = None, radius: int = 25) -> Dict:
        """
        Get events from Ticketmaster API for a specific location and date
        
        Args:
            location: City name or location string
            lat: Latitude (optional, will geocode if not provided)
            lng: Longitude (optional, will geocode if not provided)
            target_date: Target date in YYYY-MM-DD format
            radius: Search radius in miles (default: 10)
        
        Returns:
            Dict with events data including count and demand multiplier
        """
        cache_key = f"ticketmaster_events_{location}_{target_date}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.datetime.now().timestamp() - timestamp < self.cache_ttl:
                return cached_data
        
        events_data = {
            'events_found': 0,
            'demand_multiplier': 1.0,
            'source': 'default',
            'events': []  # Store full event details for boost calculation
        }
        
        api_key = DataSourcesConfig.get_ticketmaster_key()
        consumer_secret = DataSourcesConfig.get_ticketmaster_secret()
        
        if not api_key:
            print("  ⚠️  Ticketmaster API key (Consumer Key) not found")
            return self._get_time_based_estimate(target_date)
        
        try:
            # IMPORTANT: Use location name (e.g., "San Francisco") for all data calculations
            # Get coordinates if not provided (coordinates are only used for API calls that require them)
            if not lat or not lng:
                print(f"  📍 Geocoding location '{location}' to get coordinates for Ticketmaster API")
                coords = self._geocode_location(location)
                if coords:
                    lat, lng = coords
                else:
                    print(f"  ⚠️  Could not geocode '{location}', using time-based estimate")
                    return self._get_time_based_estimate(target_date)
            else:
                print(f"  📍 Using provided coordinates for Ticketmaster API: {lat:.4f}, {lng:.4f} (location: {location})")
            
            # Build API request parameters
            # Ticketmaster Discovery API uses 'apikey' parameter with Consumer Key
            # Note: We use location name in logs, but API requires coordinates for geoPoint
            params = {
                'apikey': api_key,  # Consumer Key works as API key for Discovery API
                'geoPoint': f"{lat},{lng}",  # Ticketmaster uses geoPoint format: "lat,lng" (required by API)
                'radius': radius,  # Radius in miles (increased to 25 for better coverage)
                'unit': 'miles',
                'size': 200,  # Maximum events per page (API limit)
                'page': 0,  # Start with first page
                'sort': 'date,asc'  # Sort by date ascending
            }
            
            # Add date filter if provided
            if target_date:
                try:
                    date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
                    # Ticketmaster uses localDateTime range for date filtering
                    # Format: "YYYY-MM-DDTHH:MM:SS,YYYY-MM-DDTHH:MM:SS"
                    start_datetime = date_obj.strftime("%Y-%m-%dT00:00:00")
                    # End of day (next day at 00:00:00, which is end of current day)
                    end_datetime = (date_obj + datetime.timedelta(days=1)).strftime("%Y-%m-%dT00:00:00")
                    params['localStartDateTime'] = f"{start_datetime},{end_datetime}"
                except ValueError:
                    pass  # Invalid date format, skip date filter
            
            # Rate limiting: Add small delay between requests
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)
            self.last_request_time = time.time()
            
            # Make API request with pagination support
            print(f"  🔍 Calling Ticketmaster API: {self.base_url}")
            print(f"  🔑 Using Consumer Key: {api_key[:10]}... (first 10 chars)")
            
            all_events = []
            page = 0
            total_pages = 1
            total_elements = 0
            
            # Fetch all pages of events
            while page < total_pages:
                params['page'] = page
                response = self.session.get(self.base_url, params=params, timeout=10)
                
                # Debug: Print response details
                if page == 0:
                    print(f"  📡 Ticketmaster API Response: {response.status_code}")
                
                if response.status_code != 200:
                    # Try to get error details
                    try:
                        error_data = response.json()
                        error_message = error_data.get('fault', {}).get('faultstring', 'Unknown error')
                        print(f"  ⚠️  Ticketmaster API Error: {error_message}")
                        if page == 0:  # Only print full response on first page
                            print(f"  📄 Full response: {error_data}")
                    except:
                        print(f"  ⚠️  Ticketmaster API returned status {response.status_code}")
                        if page == 0:  # Only print response text on first page
                            print(f"  📄 Response text: {response.text[:500]}")
                    break  # Stop pagination on error
                
                data = response.json()
                
                # Check for errors in response
                if 'fault' in data:
                    error_message = data['fault'].get('faultstring', 'Unknown error')
                    print(f"  ⚠️  Ticketmaster API Error in response: {error_message}")
                    break  # Stop pagination on error
                
                # Get pagination info
                page_info = data.get('page', {})
                total_elements = page_info.get('totalElements', 0)
                total_pages = page_info.get('totalPages', 1)
                current_page_size = page_info.get('size', 200)
                
                # Parse events from current page
                if '_embedded' in data and 'events' in data['_embedded']:
                    for event in data['_embedded']['events']:
                        parsed_event = self._parse_event(event, target_date)
                        if parsed_event:
                            all_events.append(parsed_event)
                
                # Log pagination progress
                if total_pages > 1:
                    print(f"  📄 Page {page + 1}/{total_pages}: Found {len(all_events)} events so far (total available: {total_elements})")
                
                # Move to next page
                page += 1
                
                # Rate limiting between pages
                if page < total_pages:
                    time.sleep(self.min_delay)
            
            if all_events:
                events_data.update({
                    'events_found': len(all_events),
                    'events': all_events,
                    'source': 'ticketmaster'
                })
                print(f"  ✅ Ticketmaster API: {len(all_events)} events found (out of {total_elements} total)")
            else:
                # No events found, use time-based estimate
                print(f"  ⚠️  No events found after parsing {total_elements} events from API")
                return self._get_time_based_estimate(target_date)
            
            # Cache the result
            self.cache[cache_key] = (events_data, datetime.datetime.now().timestamp())
            return events_data
            
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Ticketmaster API request error: {e}")
            import traceback
            traceback.print_exc()
            return self._get_time_based_estimate(target_date)
        except Exception as e:
            print(f"  ⚠️  Ticketmaster API error: {e}")
            import traceback
            traceback.print_exc()
            return self._get_time_based_estimate(target_date)
    
    def _parse_event(self, event_data: Dict, target_date: Optional[str] = None) -> Optional[Dict]:
        """
        Parse a single event from Ticketmaster API response
        
        Args:
            event_data: Raw event data from API
            target_date: Target date for filtering (YYYY-MM-DD)
        
        Returns:
            Parsed event dict with name, start_time, end_time, venue_location, capacity
            or None if event is invalid or doesn't match target_date
        """
        try:
            # Extract event name
            name = event_data.get('name', '')
            if not name:
                return None
            
            # Extract start time (handle multiple formats)
            start_time = None
            if 'dates' in event_data and 'start' in event_data['dates']:
                start_info = event_data['dates']['start']
                
                # Try localDateTime first (preferred format)
                if 'localDateTime' in start_info:
                    local_dt_str = start_info['localDateTime']
                    try:
                        # Try parsing as-is (format: "2025-11-08T18:00:00")
                        start_time = datetime.datetime.strptime(local_dt_str, "%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        try:
                            # Try parsing with timezone (format: "2025-11-08T18:00:00-08:00")
                            # Remove timezone for parsing, we'll handle it separately
                            if '+' in local_dt_str or (local_dt_str.count('-') > 2 and 'T' in local_dt_str):
                                # Has timezone, extract just the datetime part
                                if '+' in local_dt_str:
                                    dt_part = local_dt_str.split('+')[0]
                                else:
                                    # Timezone at end like "-08:00"
                                    parts = local_dt_str.rsplit('-', 1)
                                    if len(parts) == 2 and ':' in parts[1]:
                                        dt_part = parts[0]
                                    else:
                                        dt_part = local_dt_str
                                start_time = datetime.datetime.strptime(dt_part, "%Y-%m-%dT%H:%M:%S")
                            else:
                                start_time = datetime.datetime.strptime(local_dt_str, "%Y-%m-%dT%H:%M:%S")
                        except:
                            # Last resort: try to extract just the date and time parts
                            try:
                                # Extract date and time using regex-like string manipulation
                                if 'T' in local_dt_str:
                                    dt_part = local_dt_str.split('T')[0] + 'T' + local_dt_str.split('T')[1].split('+')[0].split('-')[0].split('.')[0]
                                    if len(dt_part) >= 16:  # At least "YYYY-MM-DDTHH:MM"
                                        start_time = datetime.datetime.strptime(dt_part[:19], "%Y-%m-%dT%H:%M:%S")
                            except:
                                pass
                
                # Fallback to dateTime if localDateTime not available
                if not start_time and 'dateTime' in start_info:
                    try:
                        # Parse ISO 8601 datetime
                        dt_str = start_info['dateTime']
                        # Handle Zulu time (UTC)
                        if dt_str.endswith('Z'):
                            dt_str = dt_str[:-1] + '+00:00'
                        start_time = datetime.datetime.fromisoformat(dt_str)
                    except:
                        # Try parsing as string and removing timezone
                        try:
                            dt_str = start_info['dateTime'].replace('Z', '').split('+')[0].split('-')[0]
                            if 'T' in dt_str:
                                start_time = datetime.datetime.strptime(dt_str[:19], "%Y-%m-%dT%H:%M:%S")
                        except:
                            pass
                
                # Fallback to localDate if available
                if not start_time and 'localDate' in start_info:
                    try:
                        date_str = start_info['localDate']
                        start_time = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    except:
                        pass
            
            # Extract end time (if available)
            end_time = None
            if 'dates' in event_data and 'end' in event_data['dates']:
                end_info = event_data['dates']['end']
                if 'localDateTime' in end_info:
                    try:
                        end_time = datetime.datetime.strptime(
                            end_info['localDateTime'],
                            "%Y-%m-%dT%H:%M:%S"
                        )
                    except ValueError:
                        try:
                            end_time = datetime.datetime.strptime(
                                end_info['localDateTime'].split('+')[0].split('-')[0] if '+' in end_info['localDateTime'] or end_info['localDateTime'].count('-') > 2 else end_info['localDateTime'],
                                "%Y-%m-%dT%H:%M:%S"
                            )
                        except:
                            pass
                elif 'dateTime' in end_info:
                    try:
                        end_time = datetime.datetime.fromisoformat(
                            end_info['dateTime'].replace('Z', '+00:00')
                        )
                    except:
                        pass
            
            # If no end time, estimate based on event classification (typically 2-3 hours)
            if not end_time and start_time:
                # Estimate end time based on event type
                event_type = event_data.get('classifications', [{}])[0].get('segment', {}).get('name', '').lower()
                if 'concert' in event_type or 'music' in event_type:
                    duration_hours = 3  # Concerts typically 2-3 hours
                elif 'sports' in event_type:
                    duration_hours = 3  # Sports events typically 2-3 hours
                elif 'theater' in event_type or 'comedy' in event_type:
                    duration_hours = 2  # Theater/comedy typically 2 hours
                else:
                    duration_hours = 2  # Default 2 hours
                end_time = start_time + datetime.timedelta(hours=duration_hours)
            
            # IMPORTANT: Don't filter by date here - the API request already filters by date
            # Trust the API's date filtering and include all events it returns
            # Only exclude events that don't have a valid start_time (needed for boost calculation)
            if not start_time:
                # If we can't parse start_time, we can't calculate event boost, so skip this event
                # But try to use localDate as fallback
                if 'dates' in event_data and 'start' in event_data['dates']:
                    start_info = event_data['dates']['start']
                    if 'localDate' in start_info:
                        try:
                            date_str = start_info['localDate']
                            start_time = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                            # Set default time to noon if only date is available
                            start_time = start_time.replace(hour=12, minute=0, second=0)
                        except:
                            pass
                
                # If still no start_time, skip this event
                if not start_time:
                    return None
            
            # Extract venue location (lat/lon)
            venue_location = None
            if '_embedded' in event_data and 'venues' in event_data['_embedded']:
                venues = event_data['_embedded']['venues']
                if venues and len(venues) > 0:
                    venue = venues[0]
                    if 'location' in venue:
                        lat = venue['location'].get('latitude')
                        lng = venue['location'].get('longitude')
                        if lat and lng:
                            venue_location = {'lat': float(lat), 'lng': float(lng)}
            
            # Extract capacity (if available)
            capacity = None
            if '_embedded' in event_data and 'venues' in event_data['_embedded']:
                venues = event_data['_embedded']['venues']
                if venues and len(venues) > 0:
                    venue = venues[0]
                    # Ticketmaster may have capacity in different fields
                    if 'capacity' in venue:
                        capacity = venue['capacity']
                    # Alternatively, estimate based on event classification
                    elif 'type' in venue:
                        venue_type = venue['type'].lower()
                        if 'stadium' in venue_type:
                            capacity = 50000  # Large stadium
                        elif 'arena' in venue_type:
                            capacity = 20000  # Medium arena
                        elif 'theater' in venue_type or 'auditorium' in venue_type:
                            capacity = 2000  # Medium theater
                        elif 'club' in venue_type or 'bar' in venue_type:
                            capacity = 500  # Small club
                        else:
                            capacity = 1000  # Default medium venue
            
            # Estimate capacity based on event classification if not available
            if not capacity:
                classifications = event_data.get('classifications', [])
                if classifications:
                    segment = classifications[0].get('segment', {}).get('name', '').lower()
                    genre = classifications[0].get('genre', {}).get('name', '').lower()
                    
                    # Large events (stadiums, major concerts)
                    if 'sports' in segment or 'music' in segment:
                        if 'stadium' in genre or 'arena' in genre:
                            capacity = 20000  # Large venue
                        else:
                            capacity = 5000  # Medium venue
                    # Medium events (theaters, clubs)
                    elif 'theater' in segment or 'comedy' in segment:
                        capacity = 1500  # Medium theater
                    # Small events (clubs, bars)
                    else:
                        capacity = 500  # Small venue
            
            # Default capacity if still not available
            if not capacity:
                capacity = 1000  # Default medium venue
            
            return {
                'name': name,
                'start_time': start_time,
                'end_time': end_time,
                'venue_location': venue_location,
                'capacity': capacity
            }
            
        except Exception as e:
            print(f"    ⚠️  Error parsing event: {e}")
            return None
    
    def _geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """Geocode location string to lat/lng using Nominatim"""
        try:
            from live_data_scraper import LiveDataScraper
            scraper = LiveDataScraper()
            # Use the geocoding from live_data_scraper
            coords = scraper._geocode_location(location)
            return coords
        except:
            return None
    
    def _get_time_based_estimate(self, target_date: Optional[str] = None) -> Dict:
        """Fallback to time-based estimate if API is unavailable"""
        try:
            if target_date:
                date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
                weekday = date_obj.weekday()
                is_weekend = weekday >= 5
                is_friday = weekday == 4
                
                if is_weekend:
                    return {
                        'events_found': 0,
                        'demand_multiplier': 1.15,  # Weekend boost
                        'source': 'time_estimate_weekend',
                        'events': []
                    }
                elif is_friday:
                    return {
                        'events_found': 0,
                        'demand_multiplier': 1.1,  # Friday boost
                        'source': 'time_estimate_friday',
                        'events': []
                    }
        except:
            pass
        
        return {
            'events_found': 0,
            'demand_multiplier': 1.0,
            'source': 'time_estimate',
            'events': []
        }


def get_event_boost(city: str, date: str, hour: int, lat: Optional[float] = None, 
                   lng: Optional[float] = None) -> float:
    """
    Calculate event boost factor for a specific city, date, and hour
    
    Event boost is applied during three windows based on actual event times:
    - Arrival surge: Before event start (1-3 hours before, based on event capacity)
    - During event: Full boost while event is happening
    - Departure surge: After event end (1-3 hours after, based on event capacity)
    
    Surge window duration is dynamically calculated based on event capacity:
    - Small events (<500 attendees): 1 hour before/after
    - Medium events (500-5000 attendees): 2 hours before/after
    - Large events (>5000 attendees): 3 hours before/after
    
    Boost factors based on attendance/capacity:
    - Small event (<500 attendees): +0.05
    - Medium event (500-5000 attendees): +0.2
    - Large event (>5000 attendees): +0.5
    
    Multiple overlapping events: Sum boost factors but cap at +1.5
    
    Args:
        city: City name (string)
        date: Date in YYYY-MM-DD format
        hour: Hour of day (0-23)
        lat: Latitude (optional)
        lng: Longitude (optional)
    
    Returns:
        Event boost factor (0.0 to 1.5)
    """
    try:
        scraper = TicketmasterEventsScraper()
        events_data = scraper.get_events(city, lat, lng, date)
        
        # If no events found or API error, return 0
        if events_data.get('source') in ['default', 'time_estimate', 'time_estimate_weekend', 'time_estimate_friday']:
            return 0.0
        
        events = events_data.get('events', [])
        if not events:
            return 0.0
        
        # Calculate boost for the specific hour
        total_boost = 0.0
        try:
            # Parse target datetime (hour in 24-hour format)
            target_datetime = datetime.datetime.strptime(f"{date} {hour:02d}:00:00", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Fallback if date parsing fails
            print(f"  ⚠️  Error parsing target datetime: {date} {hour:02d}:00:00")
            return 0.0
        
        for event in events:
            start_time = event.get('start_time')
            end_time = event.get('end_time')
            capacity = event.get('capacity', 1000)
            
            if not start_time:
                continue
            
            # Ensure start_time is a datetime object
            if isinstance(start_time, str):
                try:
                    start_time = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                except:
                    continue
            
            # Determine attendance multiplier based on capacity
            if capacity < 500:
                attendance_multiplier = 0.05  # Small event
            elif capacity < 5000:
                attendance_multiplier = 0.2   # Medium event
            else:
                attendance_multiplier = 0.5   # Large event
            
            # Normalize datetimes for comparison (remove timezone, keep naive datetime)
            # Convert to naive datetime for easier comparison
            if start_time.tzinfo:
                start_time_naive = start_time.replace(tzinfo=None)
            else:
                start_time_naive = start_time
            
            if end_time:
                # Ensure end_time is a datetime object
                if isinstance(end_time, str):
                    try:
                        end_time = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    except:
                        # Estimate end time if parsing fails
                        end_time = start_time_naive + datetime.timedelta(hours=2)
                
                if end_time.tzinfo:
                    end_time_naive = end_time.replace(tzinfo=None)
                else:
                    end_time_naive = end_time
            else:
                # If no end time, estimate based on event type
                # Default to 2-3 hours depending on event type
                end_time_naive = start_time_naive + datetime.timedelta(hours=2)
            
            # Calculate dynamic surge windows based on actual event times and capacity
            # Larger events have longer surge windows (more people = longer arrival/departure times)
            # Small events (<500): 1 hour before/after
            # Medium events (500-5000): 2 hours before/after  
            # Large events (>5000): 3 hours before/after
            
            if capacity < 500:
                arrival_hours_before = 1.0
                departure_hours_after = 1.0
            elif capacity < 5000:
                arrival_hours_before = 2.0
                departure_hours_after = 2.0
            else:
                arrival_hours_before = 3.0
                departure_hours_after = 3.0
            
            # Arrival surge: Before event starts (people arriving at venue)
            arrival_window_start = start_time_naive - datetime.timedelta(hours=arrival_hours_before)
            arrival_window_end = start_time_naive
            
            # During event: Full boost while event is happening (people at venue)
            event_window_start = start_time_naive
            event_window_end = end_time_naive
            
            # Departure surge: After event ends (people leaving venue)
            departure_window_start = end_time_naive
            departure_window_end = end_time_naive + datetime.timedelta(hours=departure_hours_after)
            
            # Target hour represents the start of the hour (e.g., 21:00 for hour 21)
            # Check if this hour overlaps with any of the surge windows
            hour_start = target_datetime
            hour_end = target_datetime + datetime.timedelta(hours=1)
            
            # Check if target hour overlaps with arrival surge window
            # Hour overlaps if: hour_start < window_end AND hour_end > window_start
            if hour_start < arrival_window_end and hour_end > arrival_window_start:
                total_boost += attendance_multiplier
                continue
            
            # Check if target hour overlaps with event window (during event)
            if hour_start < event_window_end and hour_end > event_window_start:
                # During event gets full boost
                total_boost += attendance_multiplier
                continue
            
            # Check if target hour overlaps with departure surge window
            if hour_start < departure_window_end and hour_end > departure_window_start:
                total_boost += attendance_multiplier
        
        # Cap total boost at +1.5 to avoid unrealistic spikes
        return min(total_boost, 1.5)
        
    except Exception as e:
        print(f"  ⚠️  Error calculating event boost: {e}")
        import traceback
        traceback.print_exc()
        return 0.0

