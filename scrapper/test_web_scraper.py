#!/usr/bin/env python3
"""
Test script for web events scraper
"""

from improved_data_scraper import ImprovedEarningsScraper
from web_events_scraper import WebEventsScraper

def test_web_scraper():
    """Test the web scraper"""
    print("=== Testing Web Events Scraper ===\n")
    
    scraper = WebEventsScraper()
    
    # Test different locations
    locations = [
        ('San Francisco', 37.7749, -122.4194),
        ('New York', 40.7128, -74.0060),
    ]
    
    for loc_name, lat, lng in locations:
        print(f"Testing {loc_name}:")
        result = scraper.get_events(loc_name, lat, lng, '2025-11-09')
        print(f"  Events found: {result.get('events_found', 0)}")
        print(f"  Demand multiplier: {result.get('demand_multiplier', 1.0)}")
        print(f"  Source: {result.get('source', 'unknown')}")
        print()

def test_integration():
    """Test integration with improved scraper"""
    print("=== Testing Integration with Improved Scraper ===\n")
    
    scraper = ImprovedEarningsScraper()
    
    # Test with web scraper
    print("Getting estimates with web scraper:")
    result = scraper.get_all_estimates('San Francisco', '2025-11-09', 18, 37.7749, -122.4194)
    
    print(f"  Location: {result['location']}")
    print(f"  Date: {result['date']}")
    print(f"  Hour: {result['hour']}")
    print(f"  Predictions: {len(result['predictions'])}")
    print()
    
    # Show rideshare and delivery
    print("Earnings estimates:")
    for pred in result['predictions']:
        service = pred['service']
        min_earn = pred['min']
        max_earn = pred['max']
        print(f"  {service}: ${min_earn}-${max_earn}/hr")
    
    print()
    
    # Compare different locations
    print("Comparing different locations (should vary based on events):")
    locations = [
        ('San Francisco', 37.7749, -122.4194),
        ('New York', 40.7128, -74.0060),
    ]
    
    for loc_name, lat, lng in locations:
        result = scraper.get_all_estimates(loc_name, '2025-11-09', 18, lat, lng)
        uber = [p for p in result['predictions'] if p['service'] == 'Uber'][0]
        doordash = [p for p in result['predictions'] if p['service'] == 'Doordash'][0]
        print(f"  {loc_name}:")
        print(f"    Uber: ${uber['min']}-${uber['max']}/hr")
        print(f"    DoorDash: ${doordash['min']}-${doordash['max']}/hr")
        print()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--integration':
        test_integration()
    else:
        test_web_scraper()
        print("\n" + "="*60 + "\n")
        test_integration()

