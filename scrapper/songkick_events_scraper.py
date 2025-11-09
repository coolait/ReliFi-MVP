#!/usr/bin/env python3
"""
Songkick API Integration for Music Events
Provides location-based concert/music event search
"""

import requests
import datetime
from typing import Dict, List, Optional, Tuple
from data_sources import DataSourcesConfig

class SongkickEventsScraper:
    """
    Fetches music events data from Songkick API
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
    
    def get_events(self, location: str, lat: Optional[float] = None, lng: Optional[float] = None,
                   target_date: Optional[str] = None, radius: int = 10) -> Dict:
        """
        Get music events from Songkick API for a specific location and date
        
        Args:
            location: City name or location string
            lat: Latitude (optional, will geocode if not provided)
            lng: Longitude (optional, will geocode if not provided)
            target_date: Target date in YYYY-MM-DD format
            radius: Search radius in miles (default: 10)
        
        Returns:
            Dict with events data including count and demand multiplier
        """
        cache_key = f"songkick_events_{location}_{target_date}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.datetime.now().timestamp() - timestamp < self.cache_ttl:
                return cached_data
        
        events_data = {
            'events_found': 0,
            'demand_multiplier': 1.0,
            'source': 'default'
        }
        
        api_key = DataSourcesConfig.get_songkick_key()
        if not api_key:
            return self._get_time_based_estimate(target_date)
        
        try:
            # Get coordinates if not provided
            if not lat or not lng:
                coords = self._geocode_location(location)
                if coords:
                    lat, lng = coords
                else:
                    return self._get_time_based_estimate(target_date)
            
            # Songkick API endpoint
            url = "http://api.songkick.com/api/3.0/events.json"
            
            # Calculate date range
            if target_date:
                try:
                    target_date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
                    min_date = target_date_obj.strftime("%Y-%m-%d")
                    max_date = (target_date_obj + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                except:
                    min_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    max_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                min_date = datetime.datetime.now().strftime("%Y-%m-%d")
                max_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Songkick uses geo location format: "geo:lat,lng"
            params = {
                'apikey': api_key,
                'location': f'geo:{lat},{lng}',
                'min_date': min_date,
                'max_date': max_date,
                'per_page': 50  # Max events per request
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                events = data.get('resultsPage', {}).get('results', {}).get('event', [])
                
                events_data.update({
                    'events_found': len(events),
                    'source': 'songkick'
                })
                
                # Calculate demand multiplier
                # Concerts significantly increase demand
                if len(events) > 0:
                    # More concerts = higher demand
                    # 1 concert = 1.05x, 5 concerts = 1.25x, 10+ concerts = 1.5x max
                    event_multiplier = 1.0 + (min(len(events), 10) * 0.05)
                    events_data['demand_multiplier'] = event_multiplier
                else:
                    # No events found, use time-based estimate
                    time_estimate = self._get_time_based_estimate(target_date)
                    events_data['demand_multiplier'] = time_estimate['demand_multiplier']
                    
            else:
                print(f"Songkick API error: {response.status_code} - {response.text[:200]}")
                return self._get_time_based_estimate(target_date)
                
        except Exception as e:
            print(f"Error fetching Songkick events: {e}")
            import traceback
            traceback.print_exc()
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

