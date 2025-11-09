#!/usr/bin/env python3
"""
Simple test for event boost calculation with different dates
Tests event boost without making excessive API calls
"""

from datetime import datetime, timedelta
from ticketmaster_events_scraper import TicketmasterEventsScraper
from data_sources import DataSourcesConfig

def test_event_boost_for_date(date_str, location="San Francisco", lat=37.7749, lng=-122.4194):
    """Test event boost for a specific date"""
    
    print(f"\n{'='*80}")
    print(f"Testing: {location} on {date_str}")
    print(f"{'='*80}")
    
    # Check API key
    api_key = DataSourcesConfig.get_ticketmaster_key()
    if not api_key:
        print("❌ TICKETMASTER_API_KEY not found")
        return
    
    # Fetch events once
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
            
            # Determine boost category
            if capacity < 500:
                boost_category = "Small (+0.05)"
            elif capacity < 5000:
                boost_category = "Medium (+0.2)"
            else:
                boost_category = "Large (+0.5)"
            print(f"     Boost: {boost_category}")
        
        # Calculate boost for key hours (arrival and departure windows)
        print(f"\n📈 Event Boost by Hour (Key Hours):")
        print(f"  Hour | Boost | Window")
        print(f"  " + "-" * 50)
        
        # Test hours around event times
        test_hours = []
        for event in events:
            start_time = event.get('start_time')
            end_time = event.get('end_time')
            
            if start_time:
                if isinstance(start_time, str):
                    try:
                        start_time = datetime.strptime(start_time.split('+')[0], "%Y-%m-%d %H:%M:%S")
                    except:
                        continue
                else:
                    start_time = start_time.replace(tzinfo=None) if start_time.tzinfo else start_time
                
                start_hour = start_time.hour
                # Arrival window: 2 hours before to start
                for h in range(max(0, start_hour - 2), min(24, start_hour + 1)):
                    if h not in test_hours:
                        test_hours.append(h)
                
                if end_time:
                    if isinstance(end_time, str):
                        try:
                            end_time = datetime.strptime(end_time.split('+')[0], "%Y-%m-%d %H:%M:%S")
                        except:
                            end_time = start_time + timedelta(hours=2)
                    else:
                        end_time = end_time.replace(tzinfo=None) if end_time.tzinfo else end_time
                    
                    end_hour = end_time.hour
                    # Departure window: end to 2 hours after
                    for h in range(end_hour, min(24, end_hour + 3)):
                        if h not in test_hours:
                            test_hours.append(h)
        
        # Sort and test hours
        test_hours = sorted(set(test_hours))
        
        for hour in test_hours:
            # Calculate boost manually using cached events
            total_boost = 0.0
            window_type = "None"
            
            for event in events:
                start_time = event.get('start_time')
                end_time = event.get('end_time')
                capacity = event.get('capacity', 1000)
                
                if not start_time:
                    continue
                
                # Parse start time
                if isinstance(start_time, str):
                    try:
                        start_time = datetime.strptime(start_time.split('+')[0], "%Y-%m-%d %H:%M:%S")
                    except:
                        continue
                else:
                    start_time = start_time.replace(tzinfo=None) if start_time.tzinfo else start_time
                
                # Determine boost multiplier
                if capacity < 500:
                    attendance_multiplier = 0.05
                elif capacity < 5000:
                    attendance_multiplier = 0.2
                else:
                    attendance_multiplier = 0.5
                
                # Arrival window: 1-2 hours before start
                arrival_start = (start_time - timedelta(hours=2)).hour
                arrival_end = start_time.hour
                
                # Departure window
                if end_time:
                    if isinstance(end_time, str):
                        try:
                            end_time = datetime.strptime(end_time.split('+')[0], "%Y-%m-%d %H:%M:%S")
                        except:
                            end_time = start_time + timedelta(hours=2)
                    else:
                        end_time = end_time.replace(tzinfo=None) if end_time.tzinfo else end_time
                else:
                    end_time = start_time + timedelta(hours=2)
                
                departure_start = end_time.hour
                departure_end = (end_time + timedelta(hours=2)).hour
                
                # Check if hour is in arrival window
                if arrival_start <= hour <= arrival_end or (arrival_start > arrival_end and (hour >= arrival_start or hour <= arrival_end)):
                    total_boost += attendance_multiplier
                    window_type = "Arrival"
                # Check if hour is in departure window
                elif departure_start <= hour <= departure_end or (departure_start > departure_end and (hour >= departure_start or hour <= departure_end)):
                    total_boost += attendance_multiplier
                    window_type = "Departure"
            
            # Cap boost at 1.5
            total_boost = min(total_boost, 1.5)
            
            if total_boost > 0:
                time_str = f"{hour:02d}:00"
                print(f"  {time_str}  | {total_boost:5.2f}  | {window_type}")
    else:
        print(f"\n⚠️  No events found for this date")
        print(f"   Source: {source}")
    
    print()


def main():
    """Test multiple dates"""
    
    print("="*80)
    print("EVENT BOOST TEST - MULTIPLE DATES")
    print("="*80)
    
    # Test dates
    today = datetime.now().date()
    test_dates = [
        today.strftime("%Y-%m-%d"),
        (today + timedelta(days=1)).strftime("%Y-%m-%d"),
        (today + timedelta(days=7)).strftime("%Y-%m-%d"),
        "2025-11-08",  # Known date with events
    ]
    
    for date_str in test_dates:
        test_event_boost_for_date(date_str)
    
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\n💡 Tips:")
    print("   - Test specific dates: python3 test_event_boost_simple.py 2025-11-08")
    print("   - Test different cities: Modify location and coordinates in the script")
    print("   - Event boost applies during arrival (1-2 hours before) and departure (1-2 hours after) windows")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test specific date from command line
        date_str = sys.argv[1]
        test_event_boost_for_date(date_str)
    else:
        # Test multiple dates
        main()

