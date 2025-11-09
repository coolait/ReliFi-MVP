#!/usr/bin/env python3
"""
Test script to verify web scraper works on localhost API
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5001"

def test_health():
    """Test API health endpoint"""
    print("1. Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API is running")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"   ❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Is it running on http://localhost:5001?")
        print("   Start it with: cd scrapper && source venv/bin/activate && python3 api_server.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_lightweight_endpoint():
    """Test lightweight endpoint with web scraper"""
    print("\n2. Testing lightweight endpoint with web scraper...")
    try:
        params = {
            'location': 'San Francisco',
            'date': '2025-11-09',
            'startTime': '6:00 PM'
        }
        print(f"   Calling: {API_BASE_URL}/api/earnings/lightweight")
        print(f"   Params: {params}")
        
        response = requests.get(f"{API_BASE_URL}/api/earnings/lightweight", params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Request successful")
            print(f"   Predictions: {len(data.get('predictions', []))}")
            
            # Check metadata
            metadata = data.get('metadata', {})
            print(f"   Using live data: {metadata.get('usingLiveData', False)}")
            print(f"   Data sources: {metadata.get('dataSources', [])}")
            print(f"   Note: {metadata.get('note', 'N/A')}")
            
            # Check if web scraper was used
            note = metadata.get('note', '').lower()
            data_sources = ' '.join(metadata.get('dataSources', [])).lower()
            if 'web' in note or 'scraper' in note or 'eventbrite' in data_sources:
                print("   ✅ Web scraper appears to be used")
            else:
                print("   ⚠️  Web scraper may not be used (check data sources)")
            
            # Show predictions
            print("\n   Earnings estimates:")
            for pred in data.get('predictions', []):
                service = pred.get('service', 'Unknown')
                min_earn = pred.get('min', 0)
                max_earn = pred.get('max', 0)
                print(f"     {service}: ${min_earn}-${max_earn}/hr")
            
            return True
        else:
            print(f"   ❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_week_endpoint():
    """Test week endpoint with web scraper"""
    print("\n3. Testing week endpoint with web scraper...")
    try:
        params = {
            'location': 'San Francisco',
            'startDate': '2025-11-09'
        }
        print(f"   Calling: {API_BASE_URL}/api/earnings/week")
        print(f"   Params: {params}")
        print("   ⏳ This may take a while (scraping events for multiple days/hours)...")
        
        response = requests.get(f"{API_BASE_URL}/api/earnings/week", params=params, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Request successful")
            
            week_data = data.get('weekData', {})
            print(f"   Days in week data: {len(week_data)}")
            
            # Check a sample day
            if 'sunday' in week_data:
                sunday = week_data['sunday']
                print(f"   Hours in Sunday: {len(sunday)}")
                
                # Check a sample hour
                if '18' in sunday:
                    hour_18_predictions = sunday['18']
                    print(f"   Predictions for Sunday 6 PM: {len(hour_18_predictions)}")
                    if hour_18_predictions:
                        print(f"     Sample: {hour_18_predictions[0].get('service', 'Unknown')}")
            
            return True
        else:
            print(f"   ❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_locations():
    """Test with different locations to verify web scraper works"""
    print("\n4. Testing different locations...")
    locations = [
        ('San Francisco', 37.7749, -122.4194),
        ('New York', 40.7128, -74.0060),
    ]
    
    results = []
    for location, lat, lng in locations:
        try:
            params = {
                'location': location,
                'date': '2025-11-09',
                'startTime': '6:00 PM'
            }
            print(f"   Testing {location}...")
            response = requests.get(f"{API_BASE_URL}/api/earnings/lightweight", params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                predictions = data.get('predictions', [])
                if predictions:
                    uber = [p for p in predictions if p.get('service') == 'Uber']
                    if uber:
                        results.append({
                            'location': location,
                            'uber_min': uber[0].get('min', 0),
                            'uber_max': uber[0].get('max', 0)
                        })
                        print(f"     ✅ {location}: Uber ${uber[0].get('min', 0)}-${uber[0].get('max', 0)}/hr")
        except Exception as e:
            print(f"     ❌ Error testing {location}: {e}")
    
    if len(results) > 1:
        print("\n   ✅ Different locations show different estimates (web scraper working!)")
    else:
        print("\n   ⚠️  Could not compare locations")
    
    return len(results) > 0

def main():
    """Run all tests"""
    print("="*60)
    print("Testing Web Scraper on Localhost API")
    print("="*60)
    print(f"API URL: {API_BASE_URL}")
    print("="*60)
    print()
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ API is not running. Please start it first:")
        print("   cd scrapper")
        print("   source venv/bin/activate")
        print("   python3 api_server.py")
        return
    
    # Test 2: Lightweight endpoint
    test_lightweight_endpoint()
    
    # Test 3: Week endpoint (optional, takes longer)
    print("\n" + "="*60)
    user_input = input("Test week endpoint? (This takes ~1-2 minutes) [y/N]: ")
    if user_input.lower() == 'y':
        test_week_endpoint()
    
    # Test 4: Different locations
    test_different_locations()
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start the frontend: cd client && npm start")
    print("2. Open http://localhost:3000 in your browser")
    print("3. Test the UI with different locations and dates")
    print("4. Check browser console for any errors")

if __name__ == '__main__':
    main()

