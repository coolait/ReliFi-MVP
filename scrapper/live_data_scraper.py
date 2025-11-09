#!/usr/bin/env python3
"""
Live Data Scraper - Fetches Real-Time Data from APIs
Replaces hardcoded data with live sources
"""

import requests
import json
import datetime
import os
from typing import Dict, List, Optional, Tuple

# Import data sources config with fallback
try:
    from data_sources import DataSourcesConfig
except ImportError:
    # Fallback if data_sources not available
    class DataSourcesConfig:
        OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
        EVENTBRITE_API_KEY = os.getenv('EVENTBRITE_API_KEY', '')
        GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
        @classmethod
        def is_weather_available(cls): return bool(cls.OPENWEATHER_API_KEY)
        @classmethod
        def is_events_available(cls): return bool(cls.EVENTBRITE_API_KEY)
        @classmethod
        def is_traffic_available(cls): return bool(cls.GOOGLE_MAPS_API_KEY)

# Import config with fallback
try:
    from config import *
except ImportError:
    GAS_PRICE_PER_GALLON = 5.25
    UBER_BASE_FARE = 2.20
    UBER_COST_PER_MINUTE = 0.22
    UBER_COST_PER_MILE = 1.15
    UBER_BOOKING_FEE = 2.40
    UBER_MINIMUM_FARE = 5.20

class LiveDataScraper:
    """
    Fetches real-time data from various APIs and sources
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache
    
    def get_weather_data(self, location: str, lat: Optional[float] = None, lng: Optional[float] = None, 
                        target_date: Optional[str] = None, target_hour: Optional[int] = None) -> Dict:
        """
        Get weather data from OpenWeatherMap API
        Uses forecast API for future dates, current API for today
        """
        cache_key = f"weather_{location}_{target_date}_{target_hour}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.datetime.now().timestamp() - timestamp < self.cache_ttl:
                return cached_data
        
        weather_data = {
            'temperature': 65,  # Default
            'condition': 'clear',
            'precipitation': 0,
            'humidity': 50,
            'multiplier': 1.0,
            'source': 'default'
        }
        
        if not DataSourcesConfig.is_weather_available():
            # Use seasonal estimates if no API key
            if target_date:
                try:
                    date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
                    month = date_obj.month
                    if month in [12, 1, 2]:  # Winter
                        weather_data['multiplier'] = 1.15
                    elif month in [6, 7, 8]:  # Summer
                        weather_data['multiplier'] = 1.05
                except:
                    pass
            return weather_data
        
        try:
            # IMPORTANT: Use location name (e.g., "San Francisco") for all data calculations
            # Get coordinates if not provided (coordinates are only used for API calls that require them)
            if not lat or not lng:
                print(f"  📍 Geocoding location '{location}' to get coordinates for weather API")
                coords = self._geocode_location(location)
                if coords:
                    lat, lng = coords
                else:
                    print(f"  ⚠️  Could not geocode '{location}', using default weather data")
                    return weather_data
            else:
                print(f"  📍 Using provided coordinates for weather API: {lat:.4f}, {lng:.4f} (location: {location})")
            
            api_key = DataSourcesConfig.get_openweather_key()
            today = datetime.datetime.now().date()
            
            # Parse target date
            if target_date:
                try:
                    target_date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
                    days_ahead = (target_date_obj - today).days
                except:
                    days_ahead = 0
            else:
                days_ahead = 0
            
            # Use forecast API for future dates (up to 5 days)
            if days_ahead > 0 and days_ahead <= 5:
                # Use 5-day forecast API
                url = "http://api.openweathermap.org/data/2.5/forecast"
                params = {
                    'lat': lat,
                    'lon': lng,
                    'appid': api_key,
                    'units': 'imperial',
                    'cnt': 40  # 40 forecasts (5 days * 8 forecasts per day = 40)
                }
                
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    forecasts = data.get('list', [])
                    
                    # Find forecast closest to target date and hour
                    target_datetime = None
                    if target_date and target_hour is not None:
                        try:
                            target_datetime = datetime.datetime.strptime(target_date, "%Y-%m-%d")
                            target_datetime = target_datetime.replace(hour=target_hour, minute=0, second=0)
                        except:
                            pass
                    
                    # Find closest forecast
                    best_forecast = None
                    if target_datetime:
                        min_diff = float('inf')
                        for forecast in forecasts:
                            forecast_time = datetime.datetime.fromtimestamp(forecast['dt'])
                            diff = abs((forecast_time - target_datetime).total_seconds())
                            if diff < min_diff:
                                min_diff = diff
                                best_forecast = forecast
                    else:
                        # Use forecast for the day
                        for forecast in forecasts:
                            forecast_time = datetime.datetime.fromtimestamp(forecast['dt'])
                            if forecast_time.date() == target_date_obj:
                                best_forecast = forecast
                                break
                    
                    if best_forecast:
                        weather_data.update({
                            'temperature': best_forecast['main']['temp'],
                            'condition': best_forecast['weather'][0]['main'].lower(),
                            'precipitation': best_forecast.get('rain', {}).get('3h', 0) or best_forecast.get('snow', {}).get('3h', 0),
                            'humidity': best_forecast['main']['humidity'],
                            'source': 'openweathermap_forecast'
                        })
                        
                        # Calculate demand multiplier
                        if 'rain' in weather_data['condition'] or weather_data['precipitation'] > 0:
                            weather_data['multiplier'] = 1.4
                        elif 'snow' in weather_data['condition']:
                            weather_data['multiplier'] = 1.5
                        elif weather_data['condition'] in ['clear', 'sunny']:
                            weather_data['multiplier'] = 1.0
                        elif weather_data['temperature'] < 40 or weather_data['temperature'] > 85:
                            weather_data['multiplier'] = 1.2
                        else:
                            weather_data['multiplier'] = 1.0
                    else:
                        # Fallback to first forecast if exact match not found
                        if forecasts:
                            forecast = forecasts[0]
                            weather_data.update({
                                'temperature': forecast['main']['temp'],
                                'condition': forecast['weather'][0]['main'].lower(),
                                'precipitation': forecast.get('rain', {}).get('3h', 0) or forecast.get('snow', {}).get('3h', 0),
                                'humidity': forecast['main']['humidity'],
                                'source': 'openweathermap_forecast'
                            })
                            if 'rain' in weather_data['condition'] or weather_data['precipitation'] > 0:
                                weather_data['multiplier'] = 1.4
                            elif 'snow' in weather_data['condition']:
                                weather_data['multiplier'] = 1.5
                            else:
                                weather_data['multiplier'] = 1.0
                
            else:
                # Use current weather API for today or past dates
                url = "http://api.openweathermap.org/data/2.5/weather"
                params = {
                    'lat': lat,
                    'lon': lng,
                    'appid': api_key,
                    'units': 'imperial'
                }
                
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    weather_data.update({
                        'temperature': data['main']['temp'],
                        'condition': data['weather'][0]['main'].lower(),
                        'precipitation': data.get('rain', {}).get('1h', 0) or data.get('snow', {}).get('1h', 0),
                        'humidity': data['main']['humidity'],
                        'source': 'openweathermap_current'
                    })
                    
                    # Calculate demand multiplier
                    if 'rain' in weather_data['condition'] or weather_data['precipitation'] > 0:
                        weather_data['multiplier'] = 1.4
                    elif 'snow' in weather_data['condition']:
                        weather_data['multiplier'] = 1.5
                    elif weather_data['condition'] in ['clear', 'sunny']:
                        weather_data['multiplier'] = 1.0
                    elif weather_data['temperature'] < 40 or weather_data['temperature'] > 85:
                        weather_data['multiplier'] = 1.2
                    else:
                        weather_data['multiplier'] = 1.0
                        
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            # Keep default values
        
        self.cache[cache_key] = (weather_data, datetime.datetime.now().timestamp())
        return weather_data
    
    def _get_eventbrite_token(self) -> Optional[str]:
        """
        Get Eventbrite API token
        Eventbrite uses Personal OAuth Tokens which can be used directly
        The Application Key can sometimes be used as a token, but Personal OAuth Token is preferred
        """
        # For Eventbrite, we can use the Application Key directly as a token
        # If you have a Personal OAuth Token, use that instead
        app_key = DataSourcesConfig.get_eventbrite_key()
        
        if not app_key:
            return None
        
        # Try using Application Key as Personal OAuth Token
        # If this doesn't work, user needs to create a Personal OAuth Token
        return app_key
    
    def get_events_data(self, location: str, lat: Optional[float] = None, lng: Optional[float] = None,
                       target_date: Optional[str] = None) -> Dict:
        """
        Get real-time events data
        Tries Meetup API first (if available), then falls back to time-based estimates
        """
        cache_key = f"events_{location}_{target_date}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.datetime.now().timestamp() - timestamp < self.cache_ttl:
                return cached_data
        
        events_data = {
            'events_found': 0,
            'demand_multiplier': 1.0,
            'source': 'default'
        }
        
        # Use ONLY Ticketmaster API for event data
        # Ticketmaster provides capacity data for accurate boost calculations
        
        try:
            from ticketmaster_events_scraper import TicketmasterEventsScraper
            if DataSourcesConfig.is_ticketmaster_available():
                ticketmaster_scraper = TicketmasterEventsScraper()
                ticketmaster_events = ticketmaster_scraper.get_events(location, lat, lng, target_date)
                
                if ticketmaster_events.get('source') == 'ticketmaster':
                    events_found = ticketmaster_events.get('events_found', 0)
                    print(f"  🎟️  Ticketmaster API: Found {events_found} events for {location} on {target_date}")
                    
                    events_data.update({
                        'events_found': events_found,
                        'demand_multiplier': ticketmaster_events.get('demand_multiplier', 1.0),
                        'source': 'ticketmaster',
                        'events': ticketmaster_events.get('events', [])  # Store events for boost calculation
                    })
                    
                    self.cache[cache_key] = (events_data, datetime.datetime.now().timestamp())
                    return events_data
                else:
                    print(f"  ⚠️  Ticketmaster API: No events found for {location} on {target_date} (using time-based estimate)")
            else:
                print(f"  ⚠️  Ticketmaster API: API key not configured (using time-based estimate)")
        except ImportError:
            print(f"  ⚠️  Ticketmaster API: Module not found (using time-based estimate)")
        except Exception as e:
            print(f"  ⚠️  Ticketmaster API error: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback to time-based estimates
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
                else:
                    events_data['demand_multiplier'] = 1.0
                    events_data['source'] = 'time_estimate'
            except Exception as date_error:
                events_data['source'] = 'default'
        
        self.cache[cache_key] = (events_data, datetime.datetime.now().timestamp())
        return events_data
    
    def get_traffic_data(self, location: str, lat: Optional[float] = None, lng: Optional[float] = None) -> Dict:
        """
        Get real-time traffic data
        Uses Google Maps API if available, otherwise estimates
        """
        cache_key = f"traffic_{location}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.datetime.now().timestamp() - timestamp < 300:  # 5 min cache for traffic
                return cached_data
        
        traffic_data = {
            'congestion_level': 0.5,
            'avg_speed_mph': 25,
            'traffic_factor': 1.0,
            'source': 'estimate'
        }
        
        if DataSourcesConfig.is_traffic_available():
            try:
                # Google Maps Traffic API (requires billing enabled)
                api_key = DataSourcesConfig.GOOGLE_MAPS_API_KEY
                if not lat or not lng:
                    coords = self._geocode_location(location)
                    if coords:
                        lat, lng = coords
                    else:
                        return traffic_data
                
                # Use Google Maps Distance Matrix API to estimate traffic
                api_key = DataSourcesConfig.get_google_maps_key()
                url = "https://maps.googleapis.com/maps/api/distancematrix/json"
                params = {
                    'origins': f"{lat},{lng}",
                    'destinations': f"{lat + 0.01},{lng + 0.01}",  # Nearby point
                    'departure_time': 'now',
                    'traffic_model': 'best_guess',
                    'key': api_key
                }
                
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 'OK' and data['rows']:
                        element = data['rows'][0]['elements'][0]
                        if 'duration_in_traffic' in element:
                            normal_duration = element['duration']['value']
                            traffic_duration = element['duration_in_traffic']['value']
                            congestion_ratio = (traffic_duration / normal_duration) - 1.0
                            
                            traffic_data.update({
                                'congestion_level': min(1.0, congestion_ratio),
                                'avg_speed_mph': max(15, 35 - (congestion_ratio * 20)),
                                'traffic_factor': 1.0 + (congestion_ratio * 0.3),
                                'source': 'google_maps'
                            })
                            
            except Exception as e:
                print(f"Error fetching traffic data: {e}")
        
        # Time-based traffic estimation if API not available
        if traffic_data['source'] == 'estimate':
            current_hour = datetime.datetime.now().hour
            # Peak hours: 7-9 AM, 5-7 PM
            if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
                traffic_data['congestion_level'] = 0.7
                traffic_data['avg_speed_mph'] = 20
                traffic_data['traffic_factor'] = 1.2
            elif 10 <= current_hour <= 15:
                traffic_data['congestion_level'] = 0.4
                traffic_data['avg_speed_mph'] = 28
                traffic_data['traffic_factor'] = 1.1
        
        self.cache[cache_key] = (traffic_data, datetime.datetime.now().timestamp())
        return traffic_data
    
    def get_gas_prices(self, location: str, lat: Optional[float] = None, lng: Optional[float] = None) -> Dict:
        """
        Get real-time gas prices
        Uses GasBuddy or AAA data
        """
        cache_key = f"gas_{location}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.datetime.now().timestamp() - timestamp < 3600:  # 1 hour cache
                return cached_data
        
        gas_data = {
            'price_per_gallon': GAS_PRICE_PER_GALLON,  # Default from config
            'source': 'default'
        }
        
        try:
            # Try to get state from location
            state = self._get_state_from_location(location)
            if not state and lat and lng:
                state = self._get_state_from_coords(lat, lng)
            
            if state:
                # Use AAA gas price API (free, no key required)
                # Note: This is a simplified approach - actual implementation would need AAA API access
                # For now, use regional averages
                regional_prices = {
                    'CA': 5.25, 'NY': 4.80, 'TX': 3.90, 'FL': 4.20,
                    'IL': 4.50, 'WA': 5.10, 'MA': 4.70, 'AZ': 4.30
                }
                
                if state in regional_prices:
                    gas_data['price_per_gallon'] = regional_prices[state]
                    gas_data['source'] = 'regional_average'
                    
        except Exception as e:
            print(f"Error fetching gas prices: {e}")
        
        self.cache[cache_key] = (gas_data, datetime.datetime.now().timestamp())
        return gas_data
    
    def get_real_time_pricing_estimates(self, location: str, service: str = 'uber',
                                       lat: Optional[float] = None, lng: Optional[float] = None) -> Dict:
        """
        Attempt to get real-time pricing estimates
        Uses web scraping and pattern matching (since no official APIs)
        """
        pricing_data = {
            'base_fare': UBER_BASE_FARE if service == 'uber' else 2.0,
            'cost_per_minute': UBER_COST_PER_MINUTE if service == 'uber' else 0.20,
            'cost_per_mile': UBER_COST_PER_MILE if service == 'uber' else 1.0,
            'booking_fee': UBER_BOOKING_FEE if service == 'uber' else 2.0,
            'minimum_fare': UBER_MINIMUM_FARE if service == 'uber' else 5.0,
            'source': 'config_default'
        }
        
        # Note: Uber/Lyft don't provide public APIs for real-time pricing
        # This would require:
        # 1. Partner API access (not available)
        # 2. Web scraping (unreliable, against ToS)
        # 3. User-reported data (would need to build database)
        
        # For now, use location-based adjustments
        location_multipliers = {
            'san francisco': 1.2,
            'new york': 1.3,
            'los angeles': 1.15,
            'chicago': 1.1,
            'seattle': 1.15,
            'boston': 1.1
        }
        
        location_lower = location.lower()
        multiplier = 1.0
        for city, mult in location_multipliers.items():
            if city in location_lower:
                multiplier = mult
                break
        
        pricing_data['base_fare'] *= multiplier
        pricing_data['cost_per_mile'] *= multiplier
        pricing_data['source'] = 'location_adjusted'
        
        return pricing_data
    
    def _geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """Get coordinates from location name (e.g., "San Francisco" -> lat, lng)"""
        try:
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': location,
                'format': 'json',
                'limit': 1
            }
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data:
                    coords = (float(data[0]['lat']), float(data[0]['lon']))
                    print(f"  📍 Geocoded '{location}' to coordinates: {coords[0]:.4f}, {coords[1]:.4f}")
                    return coords
        except Exception as e:
            print(f"  ⚠️  Geocoding error for '{location}': {e}")
        return None
    
    def _reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """Get city name from coordinates (reverse geocoding)"""
        try:
            url = f"https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat,
                'lon': lng,
                'format': 'json'
            }
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                # Try to get city name (various fields)
                city = (address.get('city') or 
                       address.get('town') or 
                       address.get('village') or
                       address.get('municipality') or
                       address.get('county'))
                if city:
                    print(f"  📍 Reverse geocoded coordinates to city: {city}")
                    return city
        except Exception as e:
            print(f"  ⚠️  Reverse geocoding error: {e}")
        return None
    
    def _get_state_from_location(self, location: str) -> Optional[str]:
        """Extract state abbreviation from location string"""
        state_abbreviations = {
            'california': 'CA', 'new york': 'NY', 'texas': 'TX', 'florida': 'FL',
            'illinois': 'IL', 'washington': 'WA', 'massachusetts': 'MA', 'arizona': 'AZ'
        }
        location_lower = location.lower()
        for state, abbrev in state_abbreviations.items():
            if state in location_lower:
                return abbrev
        return None
    
    def _get_state_from_coords(self, lat: float, lng: float) -> Optional[str]:
        """Get state from coordinates using reverse geocoding"""
        try:
            url = f"https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat,
                'lon': lng,
                'format': 'json'
            }
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                state = address.get('state') or address.get('region')
                # Convert state name to abbreviation if needed
                state_abbreviations = {
                    'california': 'CA', 'new york': 'NY', 'texas': 'TX', 'florida': 'FL',
                    'illinois': 'IL', 'washington': 'WA', 'massachusetts': 'MA', 'arizona': 'AZ'
                }
                if state:
                    state_lower = state.lower()
                    for state_name, abbrev in state_abbreviations.items():
                        if state_name in state_lower:
                            return abbrev
                    return state
        except Exception as e:
            print(f"Error getting state from coords: {e}")
        return None

