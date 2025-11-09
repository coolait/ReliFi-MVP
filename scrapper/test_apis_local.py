#!/usr/bin/env python3
"""
Test script to verify API integrations are working locally
Run this to test OpenWeatherMap, Eventbrite, and other APIs
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_environment_variables():
    """Test if API keys are set"""
    print("=" * 60)
    print("Testing Environment Variables")
    print("=" * 60)
    
    openweather_key = os.getenv('OPENWEATHER_API_KEY', '')
    eventbrite_key = os.getenv('EVENTBRITE_API_KEY', '')
    google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    # Check if keys are real or placeholders
    is_placeholder = lambda key: key and ('your_' in key.lower() or 'here' in key.lower() or len(key) < 10)
    
    openweather_valid = openweather_key and not is_placeholder(openweather_key)
    eventbrite_valid = eventbrite_key and not is_placeholder(eventbrite_key)
    google_maps_valid = google_maps_key and not is_placeholder(google_maps_key)
    
    print(f"OPENWEATHER_API_KEY: {'✅ Set (real key)' if openweather_valid else '⚠️  Set (placeholder)' if openweather_key else '❌ Not set'}")
    if openweather_key:
        if is_placeholder(openweather_key):
            print(f"  ⚠️  Warning: This appears to be a placeholder. Update .env with your real API key.")
        else:
            print(f"  Key: {openweather_key[:10]}...{openweather_key[-5:]}")
    
    print(f"EVENTBRITE_API_KEY: {'✅ Set (real key)' if eventbrite_valid else '⚠️  Set (placeholder)' if eventbrite_key else '❌ Not set'}")
    if eventbrite_key:
        if is_placeholder(eventbrite_key):
            print(f"  ⚠️  Warning: This appears to be a placeholder. Update .env with your real API key.")
        else:
            print(f"  Key: {eventbrite_key[:10]}...{eventbrite_key[-5:]}")
    
    print(f"GOOGLE_MAPS_API_KEY: {'✅ Set (real key)' if google_maps_valid else '⚠️  Set (placeholder)' if google_maps_key else '❌ Not set (optional)'}")
    if google_maps_key:
        if is_placeholder(google_maps_key):
            print(f"  ⚠️  Warning: This appears to be a placeholder. Update .env with your real API key.")
        else:
            print(f"  Key: {google_maps_key[:10]}...{google_maps_key[-5:]}")
    
    if not openweather_valid or not eventbrite_valid:
        print("⚠️  Note: API tests will use fallback/default data if keys are not set or are placeholders.")
        print("   To test with real APIs, update your .env file with actual API keys.")
        print()
    
    return openweather_valid, eventbrite_valid, google_maps_valid

def test_weather_api():
    """Test OpenWeatherMap API"""
    print("=" * 60)
    print("Testing OpenWeatherMap API")
    print("=" * 60)
    
    try:
        from live_data_scraper import LiveDataScraper
        scraper = LiveDataScraper()
        
        # Test current weather
        print("Testing current weather for San Francisco...")
        weather = scraper.get_weather_data('San Francisco', 37.7749, -122.4194)
        
        print(f"✅ Weather API working!")
        print(f"   Temperature: {weather.get('temperature', 'N/A')}°F")
        print(f"   Condition: {weather.get('condition', 'N/A')}")
        print(f"   Precipitation: {weather.get('precipitation', 0)}mm")
        print(f"   Multiplier: {weather.get('multiplier', 1.0)}")
        print(f"   Source: {weather.get('source', 'unknown')}")
        
        # Test forecast (future date)
        print("\nTesting forecast for tomorrow...")
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        forecast = scraper.get_weather_data('San Francisco', 37.7749, -122.4194, tomorrow, 18)
        
        print(f"✅ Forecast API working!")
        print(f"   Temperature: {forecast.get('temperature', 'N/A')}°F")
        print(f"   Condition: {forecast.get('condition', 'N/A')}")
        print(f"   Source: {forecast.get('source', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Weather API failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_events_api():
    """Test Eventbrite API"""
    print("\n" + "=" * 60)
    print("Testing Eventbrite API")
    print("=" * 60)
    
    try:
        from live_data_scraper import LiveDataScraper
        scraper = LiveDataScraper()
        
        # Test events for San Francisco
        print("Testing events for San Francisco...")
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        events = scraper.get_events_data('San Francisco', 37.7749, -122.4194, tomorrow)
        
        print(f"✅ Events API working!")
        print(f"   Events found: {events.get('events_found', 0)}")
        print(f"   Demand multiplier: {events.get('demand_multiplier', 1.0)}")
        print(f"   Source: {events.get('source', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Events API failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_traffic_api():
    """Test Google Maps Traffic API"""
    print("\n" + "=" * 60)
    print("Testing Google Maps Traffic API")
    print("=" * 60)
    
    try:
        from live_data_scraper import LiveDataScraper
        scraper = LiveDataScraper()
        
        print("Testing traffic data for San Francisco...")
        traffic = scraper.get_traffic_data('San Francisco', 37.7749, -122.4194)
        
        print(f"✅ Traffic API working!")
        print(f"   Congestion level: {traffic.get('congestion_level', 0.5)}")
        print(f"   Avg speed: {traffic.get('avg_speed_mph', 25)} mph")
        print(f"   Traffic factor: {traffic.get('traffic_factor', 1.0)}")
        print(f"   Source: {traffic.get('source', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"⚠️  Traffic API not available (this is OK if you don't have Google Maps key): {e}")
        return False

def test_gas_prices():
    """Test gas prices API"""
    print("\n" + "=" * 60)
    print("Testing Gas Prices")
    print("=" * 60)
    
    try:
        from live_data_scraper import LiveDataScraper
        scraper = LiveDataScraper()
        
        print("Testing gas prices for San Francisco...")
        gas = scraper.get_gas_prices('San Francisco', 37.7749, -122.4194)
        
        print(f"✅ Gas prices working!")
        print(f"   Price per gallon: ${gas.get('price_per_gallon', 5.25)}")
        print(f"   Source: {gas.get('source', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Gas prices failed: {e}")
        return False

def test_full_earnings_estimate():
    """Test full earnings estimate with all APIs"""
    print("\n" + "=" * 60)
    print("Testing Full Earnings Estimate")
    print("=" * 60)
    
    try:
        from improved_data_scraper import ImprovedEarningsScraper
        scraper = ImprovedEarningsScraper()
        
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"Testing earnings estimate for San Francisco on {tomorrow} at 6 PM...")
        estimates = scraper.get_all_estimates('San Francisco', tomorrow, 18, 37.7749, -122.4194)
        
        print(f"✅ Full estimate working!")
        print(f"   Predictions: {len(estimates.get('predictions', []))}")
        
        for pred in estimates.get('predictions', [])[:3]:  # Show first 3
            print(f"\n   Service: {pred.get('service', 'N/A')}")
            print(f"   Net Earnings: ${pred.get('netEarnings', 0):.2f}")
            print(f"   Base Earnings: ${pred.get('baseEarnings', 0):.2f}")
            print(f"   Costs: ${pred.get('costs', 0):.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Full estimate failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_server():
    """Test the API server endpoint"""
    print("\n" + "=" * 60)
    print("Testing API Server Endpoint")
    print("=" * 60)
    
    try:
        import requests
        import time
        
        # Wait a bit for server to start if needed
        print("Testing /api/health endpoint...")
        response = requests.get('http://localhost:5002/api/health', timeout=5)
        
        if response.status_code == 200:
            print("✅ API server is running!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
        
        # Test earnings endpoint
        print("\nTesting /api/earnings/lightweight endpoint...")
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        url = f'http://localhost:5002/api/earnings/lightweight?location=San%20Francisco&date={tomorrow}&startTime=6:00%20PM&endTime=7:00%20PM'
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Earnings endpoint working!")
            print(f"   Predictions: {len(data.get('predictions', []))}")
        else:
            print(f"❌ Earnings endpoint returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        return True
    except requests.exceptions.ConnectionError:
        print("⚠️  API server is not running. Start it with: python api_server.py")
        return False
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ReliFi API Integration Test Suite")
    print("=" * 60)
    print()
    
    # Test environment variables
    openweather_valid, eventbrite_valid, google_maps_valid = test_environment_variables()
    
    results = {}
    
    # Test APIs (always test, but will use fallbacks if keys not valid)
    results['weather'] = test_weather_api()
    results['events'] = test_events_api()
    
    if google_maps_valid:
        results['traffic'] = test_traffic_api()
    else:
        print("\n⚠️  Skipping traffic API test (no valid API key - optional)")
        results['traffic'] = None
    
    results['gas'] = test_gas_prices()
    
    # Test full integration (always test, will use fallbacks if needed)
    results['full_estimate'] = test_full_earnings_estimate()
    
    # Test API server (optional) - skip in non-interactive mode
    try:
        test_api_server_input = input("\nTest API server? (y/n): ").lower().strip()
        if test_api_server_input == 'y':
            results['api_server'] = test_api_server()
        else:
            results['api_server'] = None
    except (EOFError, KeyboardInterrupt):
        # Non-interactive mode - skip API server test
        print("\n⚠️  Skipping API server test (non-interactive mode)")
        results['api_server'] = None
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is True:
            print(f"✅ {test_name}: PASSED")
        elif result is False:
            print(f"❌ {test_name}: FAILED")
        else:
            print(f"⚠️  {test_name}: SKIPPED")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == '__main__':
    main()

