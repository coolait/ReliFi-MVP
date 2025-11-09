#!/usr/bin/env python3
"""
Test script for Ticketmaster API
Helps diagnose authentication and API issues
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ticketmaster_api():
    """Test Ticketmaster Discovery API with Consumer Key"""
    
    # Get API key from environment
    api_key = os.getenv('TICKETMASTER_API_KEY', '')
    consumer_secret = os.getenv('TICKETMASTER_CONSUMER_SECRET', '')
    
    if not api_key:
        print("❌ TICKETMASTER_API_KEY not found in environment variables")
        print("   Please add it to your .env file:")
        print("   TICKETMASTER_API_KEY=your_consumer_key_here")
        return
    
    print(f"✅ Found Consumer Key: {api_key[:10]}...{api_key[-5:]}")
    if consumer_secret:
        print(f"✅ Found Consumer Secret: {consumer_secret[:5]}...{consumer_secret[-5:]}")
    else:
        print("⚠️  Consumer Secret not found (not required for Discovery API)")
    
    # Test 1: Simple API call with Consumer Key
    print("\n" + "="*60)
    print("TEST 1: Discovery API with Consumer Key (apikey parameter)")
    print("="*60)
    
    base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
    
    # Test with San Francisco coordinates
    params = {
        'apikey': api_key,
        'geoPoint': '37.7749,-122.4194',  # San Francisco
        'radius': 10,
        'unit': 'miles',
        'size': 10  # Just get 10 events for testing
    }
    
    print(f"\n📍 Testing with San Francisco coordinates")
    print(f"🔗 URL: {base_url}")
    print(f"📋 Parameters: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        
        print(f"\n📡 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS! API call worked!")
            
            # Check for events
            if '_embedded' in data and 'events' in data['_embedded']:
                events = data['_embedded']['events']
                print(f"📅 Found {len(events)} events")
                
                # Show first event
                if events:
                    first_event = events[0]
                    print(f"\n🎟️  First Event:")
                    print(f"   Name: {first_event.get('name', 'N/A')}")
                    if 'dates' in first_event and 'start' in first_event['dates']:
                        start = first_event['dates']['start']
                        print(f"   Start: {start.get('localDateTime', 'N/A')}")
                    if '_embedded' in first_event and 'venues' in first_event['_embedded']:
                        venues = first_event['_embedded']['venues']
                        if venues:
                            venue = venues[0]
                            print(f"   Venue: {venue.get('name', 'N/A')}")
                            if 'location' in venue:
                                loc = venue['location']
                                print(f"   Location: {loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')}")
            else:
                print(f"⚠️  No events found in response")
                print(f"📄 Response data: {json.dumps(data, indent=2)[:500]}")
        else:
            print(f"\n❌ ERROR: API returned status {response.status_code}")
            print(f"📄 Response text: {response.text}")
            
            # Try to parse error
            try:
                error_data = response.json()
                print(f"📄 Error JSON: {json.dumps(error_data, indent=2)}")
                
                # Check for common errors
                if 'fault' in error_data:
                    fault = error_data['fault']
                    faultstring = fault.get('faultstring', 'Unknown error')
                    print(f"\n🔍 Error Details:")
                    print(f"   Fault String: {faultstring}")
                    if 'detail' in fault:
                        print(f"   Detail: {fault['detail']}")
            except:
                pass
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request Exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Try with different parameter format
    print("\n" + "="*60)
    print("TEST 2: Discovery API with city name (if supported)")
    print("="*60)
    
    params2 = {
        'apikey': api_key,
        'city': 'San Francisco',
        'size': 10
    }
    
    print(f"\n📍 Testing with city name: San Francisco")
    print(f"📋 Parameters: {json.dumps(params2, indent=2)}")
    
    try:
        response2 = requests.get(base_url, params=params2, timeout=10)
        print(f"\n📡 Response Status: {response2.status_code}")
        
        if response2.status_code == 200:
            data2 = response2.json()
            if '_embedded' in data2 and 'events' in data2['_embedded']:
                events2 = data2['_embedded']['events']
                print(f"✅ Found {len(events2)} events with city parameter")
            else:
                print(f"⚠️  No events found with city parameter")
        else:
            print(f"⚠️  City parameter not supported or error: {response2.status_code}")
            print(f"📄 Response: {response2.text[:200]}")
    except Exception as e:
        print(f"⚠️  Error with city parameter: {e}")
    
    # Test 3: Check API key format
    print("\n" + "="*60)
    print("TEST 3: API Key Validation")
    print("="*60)
    
    print(f"\n🔑 Consumer Key Details:")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Format: {api_key[:5]}...{api_key[-5:]}")
    print(f"   Contains spaces: {'Yes' if ' ' in api_key else 'No'}")
    print(f"   Contains newlines: {'Yes' if '\\n' in api_key else 'No'}")
    
    # Common issues
    print(f"\n🔍 Common Issues to Check:")
    print(f"   1. API key should be the Consumer Key (not Consumer Secret)")
    print(f"   2. API key should not have extra spaces or newlines")
    print(f"   3. API key should be approved for 'Public APIs' product")
    print(f"   4. Check if API key has expired (yours shows 'Never')")
    print(f"   5. Make sure the application is approved")

if __name__ == "__main__":
    test_ticketmaster_api()

