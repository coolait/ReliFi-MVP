#!/usr/bin/env python3
"""
Meetup API Integration for Real-Time Events Data
Provides location-based event search using Meetup API
"""

import requests
import datetime
from typing import Dict, List, Optional, Tuple
from data_sources import DataSourcesConfig

class MeetupEventsScraper:
    """
    Fetches real-time events data from Meetup API
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache for events
    
    def get_events(self, location: str, lat: Optional[float] = None, lng: Optional[float] = None,
                   target_date: Optional[str] = None, radius: int = 10) -> Dict:
        """
        Get events from Meetup API for a specific location and date
        
        Args:
            location: City name or location string
            lat: Latitude (optional, will geocode if not provided)
            lng: Longitude (optional, will geocode if not provided)
            target_date: Target date in YYYY-MM-DD format
            radius: Search radius in miles (default: 10)
        
        Returns:
            Dict with events data including count and demand multiplier
        """
        cache_key = f"meetup_events_{location}_{target_date}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.datetime.now().timestamp() - timestamp < self.cache_ttl:
                return cached_data
        
        events_data = {
            'events_found': 0,
            'demand_multiplier': 1.0,
            'source': 'default'
        }
        
        api_key = DataSourcesConfig.get_meetup_key()
        if not api_key:
            # Fallback to time-based estimates
            return self._get_time_based_estimate(target_date)
        
        try:
            # Get coordinates if not provided
            if not lat or not lng:
                coords = self._geocode_location(location)
                if coords:
                    lat, lng = coords
                else:
                    return self._get_time_based_estimate(target_date)
            
            # Meetup API endpoint
            url = "https://api.meetup.com/find/upcoming_events"
            
            # Calculate date range
            if target_date:
                try:
                    target_date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
                    start_date = target_date_obj.strftime("%Y-%m-%d")
                    end_date = (target_date_obj + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                except:
                    start_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                start_date = datetime.datetime.now().strftime("%Y-%m-%d")
                end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            
            params = {
                'key': api_key,
                'lat': lat,
                'lon': lng,
                'radius': radius,  # miles
                'page': 100,  # Max events per request
                'start_date_range': f"{start_date}T00:00:00",
                'end_date_range': f"{end_date}T23:59:59",
                'status': 'upcoming'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                
                events_data.update({
                    'events_found': len(events),
                    'source': 'meetup'
                })
                
                # Calculate demand multiplier
                # More events = higher demand
                if len(events) > 0:
                    # Base multiplier from event count
                    # 1 event = 1.02x, 10 events = 1.2x, 20+ events = 1.4x max
                    event_multiplier = 1.0 + (min(len(events), 20) * 0.02)
                    events_data['demand_multiplier'] = event_multiplier
                else:
                    # No events found, use time-based estimate
                    time_estimate = self._get_time_based_estimate(target_date)
                    events_data['demand_multiplier'] = time_estimate['demand_multiplier']
                    
            else:
                print(f"Meetup API error: {response.status_code} - {response.text[:200]}")
                # Fallback to time-based estimate
                return self._get_time_based_estimate(target_date)
                
        except Exception as e:
            print(f"Error fetching Meetup events: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to time-based estimate
            return self._get_time_based_estimate(target_date)
        
        self.cache[cache_key] = (events_data, datetime.datetime.now().timestamp())
        return events_data
    
    def _get_time_based_estimate(self, target_date: Optional[str] = None) -> Dict:
        """Fallback to time-based estimates if API unavailable"""
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
                elif weekday == 4:  # Friday
                    events_data['demand_multiplier'] = 1.2
            except:
                pass
        
        return events_data
    
    def _geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """Get coordinates from location name using Nominatim"""
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': location,
                'format': 'json',
                'limit': 1
            }
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return (float(data[0]['lat']), float(data[0]['lon']))
        except Exception as e:
            print(f"Geocoding error: {e}")
        return None

