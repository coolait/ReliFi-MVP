#!/usr/bin/env python3
"""
Test the API endpoint directly to see what error occurs
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Flask test client
from api_server import app

print("=" * 60)
print("Testing API Endpoint Directly")
print("=" * 60)
print()

# Create test client
client = app.test_client()

# Test the lightweight endpoint
print("Testing /api/earnings/lightweight endpoint...")
print("URL: /api/earnings/lightweight?location=San%20Francisco&date=2025-11-09&startTime=6:00%20PM")
print()

try:
    response = client.get('/api/earnings/lightweight?location=San%20Francisco&date=2025-11-09&startTime=6:00%20PM')
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.get_json()
        print("Response Metadata:")
        metadata = data.get('metadata', {})
        print(f"  usingLiveData: {metadata.get('usingLiveData', False)}")
        print(f"  note: {metadata.get('note', 'N/A')}")
        print(f"  dataSources: {metadata.get('dataSources', [])}")
        print()
        print(f"Predictions: {len(data.get('predictions', []))}")
        
        if metadata.get('usingLiveData') == False:
            print()
            print("⚠️  Improved scraper failed!")
            print(f"   Error message: {metadata.get('note', 'N/A')}")
    else:
        print(f"Error: {response.get_data(as_text=True)}")
        
except Exception as e:
    print(f"❌ Error testing endpoint: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("Done!")
print("=" * 60)

