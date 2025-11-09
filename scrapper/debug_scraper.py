#!/usr/bin/env python3
"""
Debug script to test the improved scraper directly
This helps identify what's failing in the API endpoint
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("Testing Improved Scraper")
print("=" * 60)
print()

try:
    print("1. Testing imports...")
    from improved_data_scraper import ImprovedEarningsScraper
    print("   ✅ ImprovedEarningsScraper imported")
    
    from live_data_scraper import LiveDataScraper
    print("   ✅ LiveDataScraper imported")
    
    from data_sources import DataSourcesConfig
    print("   ✅ DataSourcesConfig imported")
    print()
    
    print("2. Testing API keys...")
    print(f"   OPENWEATHER_API_KEY: {'✅ Set' if DataSourcesConfig.is_weather_available() else '❌ Not set'}")
    print(f"   EVENTBRITE_API_KEY: {'✅ Set' if DataSourcesConfig.is_events_available() else '❌ Not set'}")
    print(f"   GOOGLE_MAPS_API_KEY: {'✅ Set' if DataSourcesConfig.is_traffic_available() else '❌ Not set'}")
    print()
    
    print("3. Testing scraper instantiation...")
    scraper = ImprovedEarningsScraper()
    print("   ✅ Scraper instantiated")
    print()
    
    print("4. Testing get_all_estimates...")
    location = "San Francisco"
    date_str = "2025-11-09"
    target_hour = 18
    lat_val = None
    lng_val = None
    
    print(f"   Location: {location}")
    print(f"   Date: {date_str}")
    print(f"   Hour: {target_hour}")
    print(f"   Lat: {lat_val}, Lng: {lng_val}")
    print()
    
    result = scraper.get_all_estimates(location, date_str, target_hour, lat_val, lng_val)
    print(f"   ✅ get_all_estimates successful")
    print(f"   Predictions: {len(result.get('predictions', []))}")
    print()
    
    print("5. Testing with coordinates...")
    lat_val = 37.7749
    lng_val = -122.4194
    result2 = scraper.get_all_estimates(location, date_str, target_hour, lat_val, lng_val)
    print(f"   ✅ get_all_estimates with coordinates successful")
    print(f"   Predictions: {len(result2.get('predictions', []))}")
    print()
    
    print("6. Testing data source checking...")
    try:
        if DataSourcesConfig.is_weather_available():
            weather_data = scraper.live_scraper.get_weather_data(location, lat_val, lng_val, date_str, target_hour)
            print(f"   ✅ Weather API: {weather_data.get('source', 'unknown')}")
            print(f"      Temperature: {weather_data.get('temperature', 'N/A')}°F")
            print(f"      Condition: {weather_data.get('condition', 'N/A')}")
        
        if DataSourcesConfig.is_events_available():
            events_data = scraper.live_scraper.get_events_data(location, lat_val, lng_val, date_str)
            print(f"   ✅ Events API: {events_data.get('source', 'unknown')}")
            print(f"      Events found: {events_data.get('events_found', 0)}")
    except Exception as e:
        print(f"   ⚠️  Error checking data sources: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    print("=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    
except Exception as e:
    print()
    print("=" * 60)
    print(f"❌ Error: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)

