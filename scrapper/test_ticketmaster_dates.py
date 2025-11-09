#!/usr/bin/env python3
"""
Test Ticketmaster API with different dates and locations
Helps verify event boost calculation works correctly
"""

import sys
from datetime import datetime, timedelta
from ticketmaster_events_scraper import TicketmasterEventsScraper, get_event_boost
from data_sources import DataSourcesConfig

def test_multiple_dates():
    """Test Ticketmaster API with multiple dates"""
    
    print("="*80)
    print("TICKETMASTER API - MULTI-DATE TEST")
    print("="*80)
    
    # Check API key
    api_key = DataSourcesConfig.get_ticketmaster_key()
    if not api_key:
        print("❌ TICKETMASTER_API_KEY not found in environment variables")
        print("   Please add it to your .env file")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-5:]}\n")
    
    # Test locations
    test_locations = [
        {'name': 'San Francisco', 'lat': 37.7749, 'lng': -122.4194},
        {'name': 'New York', 'lat': 40.7128, 'lng': -74.0060},
        {'name': 'Los Angeles', 'lat': 34.0522, 'lng': -118.2437},
        {'name': 'Chicago', 'lat': 41.8781, 'lng': -87.6298},
    ]
    
    # Test dates (today, tomorrow, next week, next month)
    today = datetime.now().date()
    test_dates = [
        today,
        today + timedelta(days=1),
        today + timedelta(days=7),
        today + timedelta(days=30),
    ]
    
    scraper = TicketmasterEventsScraper()
    
    print("Testing Events for Different Dates and Locations")
    print("="*80)
    
    for location in test_locations:
        print(f"\n📍 Location: {location['name']}")
        print("-" * 80)
        
        for test_date in test_dates:
            date_str = test_date.strftime("%Y-%m-%d")
            date_display = test_date.strftime("%B %d, %Y")
            
            print(f"\n  📅 Date: {date_display} ({date_str})")
            
            try:
                # Fetch events
                events_data = scraper.get_events(
                    location['name'],
                    lat=location['lat'],
                    lng=location['lng'],
                    target_date=date_str
                )
                
                events_found = events_data.get('events_found', 0)
                source = events_data.get('source', 'unknown')
                
                if source == 'ticketmaster':
                    print(f"    ✅ Found {events_found} events")
                    
                    # Show first 3 events
                    events = events_data.get('events', [])
                    for i, event in enumerate(events[:3], 1):
                        name = event.get('name', 'N/A')
                        start_time = event.get('start_time')
                        capacity = event.get('capacity', 'N/A')
                        
                        if start_time:
                            if isinstance(start_time, str):
                                start_display = start_time
                            else:
                                start_display = start_time.strftime("%Y-%m-%d %H:%M")
                        else:
                            start_display = 'N/A'
                        
                        print(f"      {i}. {name}")
                        print(f"         Start: {start_display}, Capacity: {capacity}")
                    
                    if events_found > 3:
                        print(f"      ... and {events_found - 3} more events")
                else:
                    print(f"    ⚠️  {source} (no events found or API unavailable)")
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


def test_event_boost_hours():
    """Test event boost calculation for different hours"""
    
    print("\n" + "="*80)
    print("EVENT BOOST CALCULATION - MULTI-HOUR TEST")
    print("="*80)
    
    # Test with San Francisco, November 8, 2025 (we know there's an event)
    test_date = "2025-11-08"
    location = "San Francisco"
    lat = 37.7749
    lng = -122.4194
    
    print(f"\n📍 Location: {location}")
    print(f"📅 Date: {test_date}")
    print("-" * 80)
    
    # Test all 24 hours
    print("\n  Hour | Boost | Status")
    print("  " + "-" * 50)
    
    for hour in range(24):
        try:
            boost = get_event_boost(location, test_date, hour, lat, lng)
            
            # Determine status
            if boost == 0:
                status = "No boost"
            elif boost < 0.1:
                status = "Small boost"
            elif boost < 0.3:
                status = "Medium boost"
            else:
                status = "Large boost"
            
            time_str = f"{hour:02d}:00"
            print(f"  {time_str}  | {boost:5.2f}  | {status}")
            
        except Exception as e:
            print(f"  {hour:02d}:00  | ERROR | {e}")


def test_specific_date_interactive():
    """Interactive test for a specific date"""
    
    print("\n" + "="*80)
    print("INTERACTIVE DATE TEST")
    print("="*80)
    
    # Parse command line arguments
    # Format: --interactive [date] [city] [lat] [lng]
    date_str = None
    location = "San Francisco"
    lat = 37.7749
    lng = -122.4194
    
    # Skip --interactive flag
    args = [arg for arg in sys.argv[1:] if arg != '--interactive']
    
    if len(args) > 0:
        # Get date from command line
        date_str = args[0]
    else:
        # Get date from user input
        print("\nEnter a date to test (YYYY-MM-DD):")
        print("(Press Enter to use today's date)")
        date_input = input("Date: ").strip()
        
        if date_input:
            date_str = date_input
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Get location from command line if provided
    if len(args) > 1:
        location = args[1]
        if len(args) > 2:
            try:
                lat = float(args[2])
            except ValueError:
                pass
        if len(args) > 3:
            try:
                lng = float(args[3])
            except ValueError:
                pass
    
    print(f"\n📍 Testing: {location}")
    print(f"📅 Date: {date_str}")
    print(f"🌐 Coordinates: {lat}, {lng}")
    print("-" * 80)
    
    # Fetch events
    scraper = TicketmasterEventsScraper()
    events_data = scraper.get_events(location, lat=lat, lng=lng, target_date=date_str)
    
    events_found = events_data.get('events_found', 0)
    source = events_data.get('source', 'unknown')
    
    print(f"\n📊 Results:")
    print(f"  Source: {source}")
    print(f"  Events found: {events_found}")
    
    if source == 'ticketmaster' and events_found > 0:
        events = events_data.get('events', [])
        
        print(f"\n🎟️  Events:")
        for i, event in enumerate(events, 1):
            name = event.get('name', 'N/A')
            start_time = event.get('start_time')
            end_time = event.get('end_time')
            capacity = event.get('capacity', 'N/A')
            venue_location = event.get('venue_location', {})
            
            print(f"\n  {i}. {name}")
            if start_time:
                if isinstance(start_time, str):
                    start_display = start_time
                else:
                    start_display = start_time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"     Start: {start_display}")
            if end_time:
                if isinstance(end_time, str):
                    end_display = end_time
                else:
                    end_display = end_time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"     End: {end_display}")
            print(f"     Capacity: {capacity}")
            if venue_location:
                print(f"     Venue: {venue_location.get('lat', 'N/A')}, {venue_location.get('lng', 'N/A')}")
        
        # Test event boost for peak hours (use cached events data)
        print(f"\n📈 Event Boost by Hour:")
        print(f"  Hour | Boost | Window")
        print(f"  " + "-" * 40)
        
        # Calculate boost for each hour using the already-fetched events
        # This avoids making 24 separate API calls
        for hour in range(24):
            # Use the scraper's cached data
            boost = get_event_boost(location, date_str, hour, lat, lng)
            
            if boost > 0:
                time_str = f"{hour:02d}:00"
                
                # Determine window based on event times
                window = "None"
                for event in events:
                    start_time = event.get('start_time')
                    end_time = event.get('end_time')
                    
                    if start_time:
                        if isinstance(start_time, str):
                            try:
                                start_time = datetime.strptime(start_time.split('+')[0], "%Y-%m-%d %H:%M:%S")
                            except:
                                continue
                        start_hour = start_time.hour
                        
                        if end_time:
                            if isinstance(end_time, str):
                                try:
                                    end_time = datetime.strptime(end_time.split('+')[0], "%Y-%m-%d %H:%M:%S")
                                except:
                                    continue
                            end_hour = end_time.hour
                        else:
                            end_hour = (start_hour + 2) % 24
                        
                        # Arrival window: 1-2 hours before start
                        arrival_start = (start_hour - 2) % 24
                        arrival_end = start_hour
                        
                        # Departure window: 1-2 hours after end
                        departure_start = end_hour
                        departure_end = (end_hour + 2) % 24
                        
                        if arrival_start <= hour <= arrival_end or (arrival_start > arrival_end and (hour >= arrival_start or hour <= arrival_end)):
                            window = "Arrival"
                            break
                        elif departure_start <= hour <= departure_end or (departure_start > departure_end and (hour >= departure_start or hour <= departure_end)):
                            window = "Departure"
                            break
                
                print(f"  {time_str}  | {boost:5.2f}  | {window}")
        
        print(f"\n💡 Note: Boost is calculated for hours with events.")
        print(f"   Arrival surge: 1-2 hours before event start")
        print(f"   Departure surge: 1-2 hours after event end")
    else:
        print(f"\n⚠️  No events found for this date")
        print(f"   This is normal if there are no events scheduled")


def main():
    """Main test function"""
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        # Interactive mode
        test_specific_date_interactive()
    elif len(sys.argv) > 1 and sys.argv[1] == '--hours':
        # Test hours only
        test_event_boost_hours()
    else:
        # Full test suite
        test_multiple_dates()
        test_event_boost_hours()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TICKETMASTER API TESTING SUITE")
    print("="*80)
    print("\nUsage:")
    print("  python3 test_ticketmaster_dates.py              # Full test suite")
    print("  python3 test_ticketmaster_dates.py --hours      # Test hours only")
    print("  python3 test_ticketmaster_dates.py --interactive [date] [city] [lat] [lng]")
    print("  python3 test_ticketmaster_dates.py --interactive 2025-11-08")
    print("  python3 test_ticketmaster_dates.py --interactive 2025-11-08 'New York' 40.7128 -74.0060")
    print("\n")
    
    main()

