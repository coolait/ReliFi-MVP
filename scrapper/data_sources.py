#!/usr/bin/env python3
"""
Real-time Data Sources Configuration
Handles API keys and data source initialization
"""

import os
from typing import Optional, Dict

# Try to load .env file if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system environment variables

class DataSourcesConfig:
    """Configuration for real-time data sources"""
    
    # Free APIs (no key required)
    GAS_PRICE_API = 'https://www.gasbuddy.com/gaspricemap/county'  # Free, no API key
    NOMINATIM_API = 'https://nominatim.openstreetmap.org'  # Free, no API key
    
    @classmethod
    def get_openweather_key(cls) -> str:
        """Get OpenWeatherMap API key (reads from environment dynamically)"""
        return os.getenv('OPENWEATHER_API_KEY', '')
    
    @classmethod
    def get_eventbrite_key(cls) -> str:
        """Get Eventbrite Application Key (reads from environment dynamically)"""
        return os.getenv('EVENTBRITE_API_KEY', '')
    
    @classmethod
    def get_eventbrite_secret(cls) -> str:
        """Get Eventbrite OAuth Client Secret (reads from environment dynamically)"""
        return os.getenv('EVENTBRITE_CLIENT_SECRET', '')
    
    @classmethod
    def get_google_maps_key(cls) -> str:
        """Get Google Maps API key (reads from environment dynamically)"""
        return os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    @classmethod
    def get_meetup_key(cls) -> str:
        """Get Meetup API key (reads from environment dynamically)"""
        return os.getenv('MEETUP_API_KEY', '')
    
    @classmethod
    def get_songkick_key(cls) -> str:
        """Get Songkick API key (reads from environment dynamically)"""
        return os.getenv('SONGKICK_API_KEY', '')
    
    @classmethod
    def get_ticketmaster_key(cls) -> str:
        """Get Ticketmaster Consumer Key (Client ID) (reads from environment dynamically)"""
        return os.getenv('TICKETMASTER_API_KEY', '')
    
    @classmethod
    def get_ticketmaster_secret(cls) -> str:
        """Get Ticketmaster Consumer Secret (Client Secret) (reads from environment dynamically)"""
        return os.getenv('TICKETMASTER_CONSUMER_SECRET', '')
    
    @classmethod
    def get_facebook_token(cls) -> str:
        """Get Facebook API access token (reads from environment dynamically)"""
        return os.getenv('FACEBOOK_ACCESS_TOKEN', '')
    
    # For backward compatibility
    @property
    def OPENWEATHER_API_KEY(self):
        return self.get_openweather_key()
    
    @property
    def EVENTBRITE_API_KEY(self):
        return self.get_eventbrite_key()
    
    @property
    def GOOGLE_MAPS_API_KEY(self):
        return self.get_google_maps_key()
    
    @classmethod
    def is_weather_available(cls) -> bool:
        """Check if weather API is configured"""
        return bool(cls.get_openweather_key())
    
    @classmethod
    def is_events_available(cls) -> bool:
        """Check if events API is configured (needs Personal OAuth Token)"""
        # Eventbrite requires a Personal OAuth Token, not Application Key
        # For now, just check if key exists (will validate when making API calls)
        return bool(cls.get_eventbrite_key())
    
    @classmethod
    def is_traffic_available(cls) -> bool:
        """Check if traffic API is configured"""
        return bool(cls.get_google_maps_key())
    
    @classmethod
    def is_meetup_available(cls) -> bool:
        """Check if Meetup API is configured"""
        return bool(cls.get_meetup_key())
    
    @classmethod
    def is_songkick_available(cls) -> bool:
        """Check if Songkick API is configured"""
        return bool(cls.get_songkick_key())
    
    @classmethod
    def is_ticketmaster_available(cls) -> bool:
        """Check if Ticketmaster API is configured"""
        return bool(cls.get_ticketmaster_key())
    
    @classmethod
    def is_facebook_available(cls) -> bool:
        """Check if Facebook API is configured"""
        return bool(cls.get_facebook_token())

