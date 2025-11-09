#!/usr/bin/env python3
"""
Flask API server for rideshare and delivery earnings forecaster
Provides REST endpoints for the frontend to fetch real-time earnings predictions
Supports: Uber, Lyft (rideshare) and DoorDash, Uber Eats, GrubHub (delivery)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import json
from functools import lru_cache
import hashlib
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, environment variables must be set manually")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

# Lazy imports - only import when needed to avoid startup crashes
try:
    from config import *
except ImportError as e:
    print(f"Warning: Could not import config: {e}")
    # Set minimal defaults
    DEMAND_TIME_FACTORS = {h: 0.5 for h in range(24)}
    DELIVERY_DEMAND_TIME_FACTORS = {h: 0.5 for h in range(24)}
    GAS_PRICE_PER_GALLON = 5.25

# Import improved scraper
try:
    from improved_data_scraper import ImprovedEarningsScraper
    improved_scraper_available = True
except ImportError as e:
    print(f"Warning: Improved scraper not available: {e}")
    improved_scraper_available = False
    ImprovedEarningsScraper = None

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global forecaster instances (reused for efficiency)
rideshare_forecaster = None
delivery_forecaster = None
_forecasters_available = False

def _check_forecasters():
    """Check if forecasters can be imported"""
    global _forecasters_available
    if _forecasters_available:
        return True
    try:
        from scrape import UberEarningsForecaster
        from delivery_forecaster import DeliveryEarningsForecaster
        _forecasters_available = True
        return True
    except ImportError as e:
        print(f"Warning: Forecasters not available: {e}")
        return False

def get_rideshare_forecaster():
    """Get or create rideshare forecaster instance"""
    global rideshare_forecaster
    if not _check_forecasters():
        return None
    if rideshare_forecaster is None:
        try:
            from scrape import UberEarningsForecaster
            rideshare_forecaster = UberEarningsForecaster()
        except Exception as e:
            print(f"Warning: Could not create rideshare forecaster: {e}")
            return None
    return rideshare_forecaster

def get_delivery_forecaster():
    """Get or create delivery forecaster instance"""
    global delivery_forecaster
    if not _check_forecasters():
        return None
    if delivery_forecaster is None:
        try:
            from delivery_forecaster import DeliveryEarningsForecaster
            delivery_forecaster = DeliveryEarningsForecaster()
        except Exception as e:
            print(f"Warning: Could not create delivery forecaster: {e}")
            return None
    return delivery_forecaster

def is_delivery_service(service):
    """Check if service is a delivery app"""
    return service.lower() in ['doordash', 'ubereats', 'grubhub']

def is_rideshare_service(service):
    """Check if service is a rideshare app"""
    return service.lower() in ['uber', 'lyft']

def parse_time_to_hour(time_str):
    """Convert time string like '6:00 AM' to 24-hour format"""
    try:
        time_obj = datetime.datetime.strptime(time_str, '%I:%M %p')
        return time_obj.hour
    except:
        try:
            # Try 24-hour format
            return int(time_str.split(':')[0])
        except:
            return 9  # Default to 9 AM

def format_hour_to_time(hour):
    """Convert hour (0-23) to formatted time string"""
    if hour == 0:
        return '12:00 AM'
    elif hour < 12:
        return f'{hour}:00 AM'
    elif hour == 12:
        return '12:00 PM'
    else:
        return f'{hour - 12}:00 PM'

def get_cache_key(location, date, hour):
    """Generate cache key for earnings data"""
    # Normalize location string (handle coordinates)
    if isinstance(location, str) and ',' in location:
        # Try to parse as coordinates and normalize
        try:
            parts = location.split(',')
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lng = float(parts[1].strip())
                # Round to 2 decimal places for cache key (prevents minor coordinate differences from creating new cache entries)
                location = f"{lat:.2f},{lng:.2f}"
        except:
            pass  # Use location as-is if parsing fails
    key_str = f"{location}_{date}_{hour}"
    return hashlib.md5(key_str.encode()).hexdigest()

# Simple in-memory cache with TTL
earnings_cache = {}
CACHE_TTL_SECONDS = 3600  # 1 hour cache

def get_cached_earnings(location, date, hour):
    """Get cached earnings if available and not expired"""
    cache_key = get_cache_key(location, date, hour)
    if cache_key in earnings_cache:
        cached_data, timestamp = earnings_cache[cache_key]
        age = datetime.datetime.now().timestamp() - timestamp
        if age < CACHE_TTL_SECONDS:
            return cached_data
    return None

def cache_earnings(location, date, hour, data):
    """Cache earnings data"""
    cache_key = get_cache_key(location, date, hour)
    earnings_cache[cache_key] = (data, datetime.datetime.now().timestamp())

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'OK', 'service': 'Earnings Forecaster API'})

@app.route('/api/earnings/lightweight', methods=['GET'])
def get_earnings_lightweight():
    """
    Ultra-fast earnings endpoint using config-based estimates (NO scraping)
    Response time: < 50ms (vs 3-10 seconds for full scraping)

    Use this for:
    - Initial page load / preview
    - Quick location changes
    - UI responsiveness

    Query Parameters:
    - location: string (city name, e.g., "San Francisco") OR
    - lat: float (latitude) + lng: float (longitude)
    - date: string (YYYY-MM-DD)
    - startTime: string (e.g., "6:00 AM")
    - endTime: string
    - service: string (optional, defaults to "all")

    Returns: Same format as /api/earnings but calculated from config defaults
    """
    try:
        # Parse query parameters
        # Support both city name and coordinates
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        location = request.args.get('location')

        # If coordinates provided, use them
        if lat and lng:
            try:
                lat_val = float(lat)
                lng_val = float(lng)
                location = f"{lat_val:.4f},{lng_val:.4f}"
                print(f"📍 Using GPS coordinates: {location}")
            except ValueError:
                location = 'San Francisco'  # Fallback
        elif not location:
            location = 'San Francisco'  # Default

        date_str = request.args.get('date')
        start_time = request.args.get('startTime', '9:00 AM')
        end_time = request.args.get('endTime', '10:00 AM')
        service_filter = request.args.get('service', 'all')

        if not date_str:
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')

        target_hour = parse_time_to_hour(start_time)

        # Use improved scraper if available (uses live APIs)
        predictions = []
        use_improved_scraper = False
        data_sources = []
        metadata_note = "Using live API data"
        
        if improved_scraper_available:
            try:
                scraper = ImprovedEarningsScraper()
                
                # Safely parse coordinates
                lat_val = None
                lng_val = None
                try:
                    if lat and lat.strip():
                        lat_val = float(lat)
                    if lng and lng.strip():
                        lng_val = float(lng)
                except (ValueError, TypeError) as e:
                    print(f"  ⚠️  Could not parse coordinates: lat={lat}, lng={lng}, error={e}")
                    lat_val = None
                    lng_val = None
                
                # Determine location string
                # If coordinates provided but no location name, use coordinates
                if lat_val and lng_val:
                    if not location or location == f"{lat_val:.4f},{lng_val:.4f}":
                        # Use coordinates directly, scraper will handle geocoding
                        location_str = f"{lat_val:.4f},{lng_val:.4f}"
                    else:
                        # Use provided location name
                        location_str = location
                else:
                    # No coordinates, use location name
                    location_str = location if location else 'San Francisco'
                
                print(f"🌐 Using improved scraper with live APIs for: {location_str}, {date_str}, hour {target_hour}")
                
                # Get all estimates (this will use live APIs)
                all_estimates = scraper.get_all_estimates(location_str, date_str, target_hour, lat_val, lng_val)
                
                # Check which data sources were used by inspecting the actual API calls
                # The improved scraper already made API calls, so we check the results
                try:
                    from data_sources import DataSourcesConfig
                    import os
                    
                    # Check if API keys are real (not placeholders)
                    openweather_key = DataSourcesConfig.get_openweather_key()
                    eventbrite_key = DataSourcesConfig.get_eventbrite_key()
                    google_maps_key = DataSourcesConfig.get_google_maps_key()
                    
                    # Detect placeholders
                    is_placeholder = lambda key: key and ('your_' in key.lower() or 'here' in key.lower() or len(key) < 10)
                    
                    # Check weather API
                    if DataSourcesConfig.is_weather_available() and not is_placeholder(openweather_key):
                        try:
                            weather_data = scraper.live_scraper.get_weather_data(location_str, lat_val, lng_val, date_str, target_hour)
                            if weather_data.get('source') and weather_data.get('source') != 'default':
                                data_sources.append(f"Weather: {weather_data.get('source', 'unknown')}")
                                print(f"  ✅ Weather API: {weather_data.get('condition', 'N/A')}, {weather_data.get('temperature', 'N/A')}°F")
                            else:
                                print(f"  ⚠️  Weather API key may be invalid (returned default data)")
                        except Exception as e:
                            print(f"  ⚠️  Weather API error: {e}")
                    elif is_placeholder(openweather_key):
                        print(f"  ⚠️  OpenWeatherMap API key appears to be a placeholder")
                    
                    # Check events API (Meetup or Eventbrite)
                    try:
                        events_data = scraper.live_scraper.get_events_data(location_str, lat_val, lng_val, date_str)
                        if events_data.get('source') and events_data.get('source') not in ['default', 'time_estimate', 'time_estimate_weekend', 'time_estimate_friday']:
                            source_name = events_data.get('source', 'unknown')
                            events_count = events_data.get('events_found', 0)
                            if source_name == 'meetup':
                                data_sources.append(f"Events: Meetup API ({events_count} events)")
                                print(f"  ✅ Meetup API: {events_count} events found")
                            else:
                                data_sources.append(f"Events: {source_name} ({events_count} events)")
                                print(f"  ✅ Events API: {events_count} events found")
                        else:
                            # Using time-based estimates
                            source_name = events_data.get('source', 'time_estimate')
                            if 'weekend' in source_name:
                                print(f"  ℹ️  Events: Using weekend multiplier (no API configured)")
                            elif 'friday' in source_name:
                                print(f"  ℹ️  Events: Using Friday multiplier (no API configured)")
                            else:
                                print(f"  ℹ️  Events: Using time-based estimates (no API configured)")
                    except Exception as e:
                        print(f"  ⚠️  Events API error: {e}")
                    
                    # Check traffic API
                    if DataSourcesConfig.is_traffic_available() and not is_placeholder(google_maps_key):
                        try:
                            traffic_data = scraper.live_scraper.get_traffic_data(location_str, lat_val, lng_val)
                            if traffic_data.get('source') and traffic_data.get('source') != 'estimate':
                                data_sources.append(f"Traffic: {traffic_data.get('source', 'unknown')}")
                                print(f"  ✅ Traffic API: {traffic_data.get('source', 'unknown')}")
                        except Exception as e:
                            print(f"  ⚠️  Traffic API error: {e}")
                    elif is_placeholder(google_maps_key) and google_maps_key:
                        print(f"  ⚠️  Google Maps API key appears to be a placeholder")
                        
                except Exception as e:
                    print(f"  ⚠️  Could not check data sources: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Filter by service if needed
                for pred in all_estimates['predictions']:
                    pred_service = pred['service'].lower()
                    if service_filter == 'all' or pred_service == service_filter.lower():
                        # Add time formatting
                        pred['startTime'] = format_hour_to_time(target_hour)
                        pred['endTime'] = format_hour_to_time(target_hour + 1)
                        predictions.append(pred)
                
                use_improved_scraper = True
                if data_sources:
                    metadata_note = f"Live data from: {', '.join(data_sources)}"
                else:
                    metadata_note = "Using location/time-based estimates (APIs may not be configured)"
                print(f"  ✅ Generated {len(predictions)} predictions using improved scraper")
                
            except Exception as e:
                error_msg = str(e)
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ Error using improved scraper: {error_msg}")
                print(f"❌ Full traceback:")
                print(error_trace)
                use_improved_scraper = False
                predictions = []  # Clear any partial predictions
                metadata_note = f"Fell back to config defaults (improved scraper failed: {error_msg})"
        
        # Fallback to basic estimates only if improved scraper completely failed
        if not use_improved_scraper:
            # Get time factors from config
            rideshare_time_factor = DEMAND_TIME_FACTORS.get(target_hour, 0.5)
            delivery_time_factor = DELIVERY_DEMAND_TIME_FACTORS.get(target_hour, 0.5)

            # Calculate base earnings using config defaults (no scraping)
            # Rideshare: Average SF earnings are ~$25-30/hour
            base_rideshare_earnings = 25 * rideshare_time_factor * 1.2
            rideshare_demand_score = min(1.0, rideshare_time_factor)
            rideshare_trips = 2.0 * rideshare_time_factor

            # Delivery: Average SF earnings are ~$20-25/hour
            base_delivery_earnings = 22 * delivery_time_factor * 1.3
            delivery_demand_score = min(1.0, delivery_time_factor)
            delivery_trips = 2.5 * delivery_time_factor

            # Determine hotspot based on time
            if target_hour in [7, 8, 17, 18]:  # Commute hours
                hotspot = "Financial District"
                surge = 1.2
            elif target_hour in [12, 13, 18, 19]:  # Meal times
                hotspot = "Restaurant Districts"
                surge = 1.15
            elif target_hour >= 20 or target_hour <= 5:  # Late night
                hotspot = "Entertainment Areas"
                surge = 1.1
            else:
                hotspot = "Downtown Core"
                surge = 1.0

            # Rideshare services
            if service_filter in ['all', 'Uber']:
                predictions.append({
                    'service': 'Uber',
                    'min': round(max(10, base_rideshare_earnings - 5), 2),
                    'max': round(base_rideshare_earnings + 5, 2),
                    'hotspot': hotspot,
                    'demandScore': round(rideshare_demand_score, 2),
                    'tripsPerHour': round(rideshare_trips, 2),
                    'surgeMultiplier': round(surge, 2),
                    'color': '#4285F4',
                    'startTime': format_hour_to_time(target_hour),
                    'endTime': format_hour_to_time(target_hour + 1)
                })

            if service_filter in ['all', 'Lyft']:
                predictions.append({
                    'service': 'Lyft',
                    'min': round(max(10, (base_rideshare_earnings - 5) * 0.92), 2),
                    'max': round((base_rideshare_earnings + 5) * 0.92, 2),
                    'hotspot': hotspot,
                    'demandScore': round(rideshare_demand_score * 0.95, 2),
                    'tripsPerHour': round(rideshare_trips * 0.9, 2),
                    'surgeMultiplier': round(surge * 0.95, 2),
                    'color': '#FF00BF',
                    'startTime': format_hour_to_time(target_hour),
                    'endTime': format_hour_to_time(target_hour + 1)
                })

            # Delivery services
            if service_filter in ['all', 'DoorDash']:
                predictions.append({
                    'service': 'DoorDash',
                    'min': round(max(12, base_delivery_earnings - 6), 2),
                    'max': round(base_delivery_earnings + 6, 2),
                    'hotspot': 'Restaurant Districts',
                    'demandScore': round(delivery_demand_score, 2),
                    'tripsPerHour': round(delivery_trips, 2),
                    'surgeMultiplier': round(1.0 + (delivery_time_factor - 0.5) * 0.4, 2),
                    'color': '#FFD700',
                    'startTime': format_hour_to_time(target_hour),
                    'endTime': format_hour_to_time(target_hour + 1)
                })

            if service_filter in ['all', 'UberEats']:
                predictions.append({
                    'service': 'UberEats',
                    'min': round(max(12, base_delivery_earnings * 0.95 - 6), 2),
                    'max': round(base_delivery_earnings * 0.95 + 6, 2),
                    'hotspot': 'Restaurant Districts',
                    'demandScore': round(delivery_demand_score * 0.95, 2),
                    'tripsPerHour': round(delivery_trips * 0.95, 2),
                    'surgeMultiplier': round(1.0 + (delivery_time_factor - 0.5) * 0.4, 2),
                    'color': '#06C167',
                    'startTime': format_hour_to_time(target_hour),
                    'endTime': format_hour_to_time(target_hour + 1)
                })

            if service_filter in ['all', 'GrubHub']:
                predictions.append({
                    'service': 'GrubHub',
                    'min': round(max(12, base_delivery_earnings * 1.05 - 6), 2),
                    'max': round(base_delivery_earnings * 1.05 + 6, 2),
                    'hotspot': 'Restaurant Districts',
                    'demandScore': round(delivery_demand_score, 2),
                    'tripsPerHour': round(delivery_trips, 2),
                    'surgeMultiplier': 1.0,
                    'color': '#FF8000',
                    'startTime': format_hour_to_time(target_hour),
                    'endTime': format_hour_to_time(target_hour + 1)
                })

        response_data = {
            'location': location,
            'date': date_str,
            'timeSlot': f"{format_hour_to_time(target_hour)} - {format_hour_to_time(target_hour + 1)}",
            'hour': target_hour,
            'predictions': predictions,
            'metadata': {
                'lightweight': True,
                'usingLiveData': use_improved_scraper,
                'note': metadata_note,
                'dataSources': data_sources if data_sources else ['Config defaults']
            }
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to calculate lightweight forecast'
        }), 500

@app.route('/api/earnings', methods=['GET'])
def get_earnings():
    """
    Get projected earnings for a specific location and timeslot

    Query Parameters:
    - location: string (e.g., "San Francisco", "New York") OR
    - lat: float (latitude) + lng: float (longitude)
    - date: string in format YYYY-MM-DD (optional, defaults to today)
    - startTime: string (e.g., "6:00 AM" or "06:00")
    - endTime: string (e.g., "7:00 AM" or "07:00")
    - service: string (optional, "Uber" or "Lyft", defaults to both)

    Returns:
    {
      "location": "San Francisco",
      "date": "2025-10-23",
      "timeSlot": "6:00 AM - 7:00 AM",
      "predictions": [
        {
          "service": "Uber",
          "min": 25.50,
          "max": 35.75,
          "hotspot": "Downtown Core",
          "demandScore": 0.85,
          "tripsPerHour": 2.3,
          "surgeMultiplier": 1.1
        },
        {
          "service": "Lyft",
          "min": 23.00,
          "max": 33.25,
          "hotspot": "Downtown Core",
          "demandScore": 0.82,
          "tripsPerHour": 2.2,
          "surgeMultiplier": 1.05
        }
      ]
    }
    """
    try:
        # Parse query parameters
        # Support both city name and coordinates
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        location = request.args.get('location')

        # If coordinates provided, use them
        if lat and lng:
            try:
                lat_val = float(lat)
                lng_val = float(lng)
                location = f"{lat_val:.4f},{lng_val:.4f}"
                print(f"📍 Using GPS coordinates: {location}")
            except ValueError:
                location = 'San Francisco'  # Fallback
        elif not location:
            location = 'San Francisco'  # Default

        date_str = request.args.get('date')
        start_time = request.args.get('startTime', '9:00 AM')
        end_time = request.args.get('endTime', '10:00 AM')
        service_filter = request.args.get('service', 'all')  # 'Uber', 'Lyft', or 'all'

        # Default to today if no date provided
        if not date_str:
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Log the exact date and time being used
        print(f"  📅 API request: date={date_str}, startTime={start_time}, endTime={end_time}, location={location}")

        # Parse hour from start time
        target_hour = parse_time_to_hour(start_time)
        print(f"  ⏰ Parsed hour: {target_hour}:00")

        # Check cache first (use coordinates or city name as key)
        cached_data = get_cached_earnings(location, date_str, target_hour)
        if cached_data:
            print(f"  📦 Using cached data for {date_str} at {target_hour}:00")
            return jsonify(cached_data)

        # IMPORTANT: Use improved scraper if available to get accurate, date-specific estimates
        # This ensures the scraper uses the EXACT date and time the user clicked
        if improved_scraper_available:
            try:
                scraper = ImprovedEarningsScraper()
                
                # IMPORTANT: Use location name as primary identifier for all data calculations
                # Coordinates are only used as supplementary data (for geocoding if needed)
                # This ensures "San Francisco" is used for all APIs (weather, events, etc.)
                location_str = location  # Use location name (e.g., "San Francisco")
                
                print(f"  🔍 Using improved scraper for location '{location_str}' on {date_str} at {target_hour}:00")
                if lat_val and lng_val:
                    print(f"  📍 Coordinates available: {lat_val:.4f}, {lng_val:.4f} (used as supplementary data)")
                
                # Pass location name as primary, coordinates as supplementary
                all_estimates = scraper.get_all_estimates(location_str, date_str, target_hour, lat_val, lng_val)
                predictions = all_estimates.get('predictions', [])
                
                # Cache the results
                if predictions:
                    cache_earnings(location_str, date_str, target_hour, {
                        'predictions': predictions,
                        'metadata': {
                            'usingLiveData': True,
                            'note': 'Live data from improved scraper with specific date/time'
                        }
                    })
                
                return jsonify({
                    'location': location_str,
                    'date': date_str,
                    'timeSlot': f"{start_time} - {end_time}",
                    'predictions': predictions
                })
            except Exception as e:
                print(f"  ⚠️  Improved scraper error: {e}")
                import traceback
                traceback.print_exc()
                # Fall through to legacy code below

        # Determine which services to calculate (legacy code, used if improved scraper unavailable)
        needs_rideshare = service_filter in ['all', 'Uber', 'Lyft']
        needs_delivery = service_filter in ['all', 'DoorDash', 'UberEats', 'GrubHub']

        # Build predictions
        predictions = []
        metadata = {}

        # ========== RIDESHARE CALCULATIONS ==========
        if needs_rideshare:
            fc = get_rideshare_forecaster()
            if fc is None:
                # Fallback to lightweight estimates if forecaster unavailable
                print("Warning: Rideshare forecaster unavailable, using fallback")
                rideshare_time_factor = DEMAND_TIME_FACTORS.get(target_hour, 0.5)
                base_earnings = 25 * rideshare_time_factor * 1.2
                predictions.append({
                    'service': 'Uber',
                    'min': round(max(10, base_earnings - 5), 2),
                    'max': round(base_earnings + 5, 2),
                    'hotspot': 'Downtown Core',
                    'demandScore': round(min(1.0, rideshare_time_factor), 2),
                    'tripsPerHour': round(2.0 * rideshare_time_factor, 2),
                    'surgeMultiplier': 1.0,
                    'color': '#4285F4',
                    'startTime': format_hour_to_time(target_hour),
                    'endTime': format_hour_to_time(target_hour + 1)
                })
                if service_filter in ['all', 'Lyft']:
                    predictions.append({
                        'service': 'Lyft',
                        'min': round(max(10, (base_earnings - 5) * 0.92), 2),
                        'max': round((base_earnings + 5) * 0.92, 2),
                        'hotspot': 'Downtown Core',
                        'demandScore': round(min(1.0, rideshare_time_factor * 0.95), 2),
                        'tripsPerHour': round(2.0 * rideshare_time_factor * 0.9, 2),
                        'surgeMultiplier': 0.95,
                        'color': '#FF00BF',
                        'startTime': format_hour_to_time(target_hour),
                        'endTime': format_hour_to_time(target_hour + 1)
                    })
            else:
                # Run rideshare forecast
                events_data = fc.scrape_events(date_str, target_hour)
                weather_multiplier = fc.scrape_weather(date_str)
                traffic_data = fc.scrape_traffic()
                pricing_data = fc.scrape_uber_pricing()
                gas_data = fc.scrape_gas_prices()

                # Calculate demand and supply
                demand = fc.estimate_demand(events_data, weather_multiplier, target_hour)
                supply = fc.estimate_driver_supply(target_hour)

                # Calculate deadtime
                demand_supply_ratio = demand / supply if supply > 0 else 0
                deadtime_data = fc.calculate_deadtime(target_hour, traffic_data, demand_supply_ratio)

                # Calculate earnings
                earnings_per_trip = fc.estimate_trip_earnings(pricing_data, traffic_data, target_hour)
                costs = fc.estimate_costs(gas_data, traffic_data, deadtime_data)
                results = fc.calculate_net_earnings(demand, supply, earnings_per_trip, costs, target_hour, deadtime_data)

                # Determine hotspot based on demand
                hotspot = "Downtown Core"
                if demand_supply_ratio > 1.5:
                    hotspot = "Financial District"
                elif demand_supply_ratio > 1.2:
                    hotspot = "Downtown Core"
                elif demand_supply_ratio > 0.8:
                    hotspot = "Mission District"
                else:
                    hotspot = "Various Areas"

                # Calculate demand score (0-1)
                demand_score = min(1.0, demand_supply_ratio / 2.0)

                # Uber prediction
                if service_filter in ['all', 'Uber']:
                    uber_min = max(10, results['net_hourly_earnings'] - 5)
                    uber_max = results['net_hourly_earnings'] + 5
                    predictions.append({
                        'service': 'Uber',
                        'min': round(uber_min, 2),
                        'max': round(uber_max, 2),
                        'hotspot': hotspot,
                        'demandScore': round(demand_score, 2),
                        'tripsPerHour': round(results['trips_per_driver'], 2),
                        'surgeMultiplier': round(results['surge_multiplier'], 2),
                        'color': '#4285F4',  # Uber blue
                        'startTime': format_hour_to_time(target_hour),
                        'endTime': format_hour_to_time(target_hour + 1)
                    })

                # Lyft prediction
                if service_filter in ['all', 'Lyft']:
                    lyft_adjustment = 0.92  # Lyft typically pays ~8% less
                    lyft_min = max(10, (results['net_hourly_earnings'] - 5) * lyft_adjustment)
                    lyft_max = (results['net_hourly_earnings'] + 5) * lyft_adjustment
                    predictions.append({
                        'service': 'Lyft',
                        'min': round(lyft_min, 2),
                        'max': round(lyft_max, 2),
                        'hotspot': hotspot,
                        'demandScore': round(demand_score * 0.95, 2),
                        'tripsPerHour': round(results['trips_per_driver'] * 0.9, 2),
                        'surgeMultiplier': round(results['surge_multiplier'] * 0.95, 2),
                        'color': '#FF00BF',  # Lyft pink
                        'startTime': format_hour_to_time(target_hour),
                        'endTime': format_hour_to_time(target_hour + 1)
                    })

                metadata['rideshare'] = {
                    'demandEstimate': round(demand, 0),
                    'driverSupply': round(supply, 0),
                    'demandSupplyRatio': round(demand_supply_ratio, 2),
                    'trafficLevel': traffic_data['congestion_level'] if isinstance(traffic_data, dict) else 0.5
                }

        # ========== DELIVERY CALCULATIONS ==========
        if needs_delivery:
            fc_delivery = get_delivery_forecaster()
            if fc_delivery is None:
                # Fallback to lightweight estimates if forecaster unavailable
                print("Warning: Delivery forecaster unavailable, using fallback")
                delivery_time_factor = DELIVERY_DEMAND_TIME_FACTORS.get(target_hour, 0.5)
                base_delivery_earnings = 22 * delivery_time_factor * 1.3
                delivery_demand_score = min(1.0, delivery_time_factor)
                delivery_trips = 2.5 * delivery_time_factor
                
                if service_filter in ['all', 'DoorDash']:
                    predictions.append({
                        'service': 'DoorDash',
                        'min': round(max(12, base_delivery_earnings - 6), 2),
                        'max': round(base_delivery_earnings + 6, 2),
                        'hotspot': 'Restaurant Districts',
                        'demandScore': round(delivery_demand_score, 2),
                        'tripsPerHour': round(delivery_trips, 2),
                        'surgeMultiplier': 1.0,
                        'color': '#FFD700',
                        'startTime': format_hour_to_time(target_hour),
                        'endTime': format_hour_to_time(target_hour + 1)
                    })
                if service_filter in ['all', 'UberEats']:
                    predictions.append({
                        'service': 'UberEats',
                        'min': round(max(12, base_delivery_earnings * 0.95 - 6), 2),
                        'max': round(base_delivery_earnings * 0.95 + 6, 2),
                        'hotspot': 'Restaurant Districts',
                        'demandScore': round(delivery_demand_score * 0.95, 2),
                        'tripsPerHour': round(delivery_trips * 0.95, 2),
                        'surgeMultiplier': 1.0,
                        'color': '#06C167',
                        'startTime': format_hour_to_time(target_hour),
                        'endTime': format_hour_to_time(target_hour + 1)
                    })
                if service_filter in ['all', 'GrubHub']:
                    predictions.append({
                        'service': 'GrubHub',
                        'min': round(max(12, base_delivery_earnings * 1.05 - 6), 2),
                        'max': round(base_delivery_earnings * 1.05 + 6, 2),
                        'hotspot': 'Restaurant Districts',
                        'demandScore': round(delivery_demand_score, 2),
                        'tripsPerHour': round(delivery_trips, 2),
                        'surgeMultiplier': 1.0,
                        'color': '#FF8000',
                        'startTime': format_hour_to_time(target_hour),
                        'endTime': format_hour_to_time(target_hour + 1)
                    })
            else:
                # Run delivery forecast
                delivery_events = fc_delivery.scrape_events(date_str, target_hour)
                delivery_weather = fc_delivery.scrape_weather(date_str)

                # Get neighborhood for tipping/restaurant density
                neighborhood = None  # Could be extracted from location string
                restaurant_density = fc_delivery.scrape_restaurant_density(location, neighborhood)

                # Calculate delivery demand and supply
                delivery_demand = fc_delivery.estimate_demand(delivery_events, delivery_weather, target_hour, restaurant_density)
                delivery_supply = fc_delivery.estimate_driver_supply(target_hour)

                # Calculate delivery deadtime
                delivery_ratio = delivery_demand / delivery_supply if delivery_supply > 0 else 0
                delivery_deadtime = fc_delivery.calculate_deadtime(target_hour, delivery_ratio)

                # Calculate delivery costs
                delivery_costs = fc_delivery.estimate_costs(GAS_PRICE_PER_GALLON)

                # Calculate demand score for delivery
                delivery_score = min(1.0, delivery_ratio / 2.0)

                # DoorDash prediction
                if service_filter in ['all', 'DoorDash']:
                    pricing = fc_delivery.scrape_delivery_pricing('doordash')
                    earnings_per_delivery = fc_delivery.estimate_delivery_earnings(pricing, target_hour, 'doordash', neighborhood)
                    delivery_results = fc_delivery.calculate_net_earnings(
                        delivery_demand, delivery_supply, earnings_per_delivery,
                        delivery_costs, target_hour, delivery_deadtime
                    )

                    predictions.append({
                        'service': 'DoorDash',
                        'min': round(max(12, delivery_results['net_hourly_earnings'] - 6), 2),
                        'max': round(delivery_results['net_hourly_earnings'] + 6, 2),
                        'hotspot': 'Restaurant Districts',
                        'demandScore': round(delivery_score, 2),
                        'tripsPerHour': round(delivery_results['deliveries_per_driver'], 2),
                        'surgeMultiplier': round(delivery_results.get('peak_pay_multiplier', 1.0), 2),
                        'color': '#FFD700',  # DoorDash gold
                        'startTime': format_hour_to_time(target_hour),
                        'endTime': format_hour_to_time(target_hour + 1)
                    })

                # Uber Eats prediction
                if service_filter in ['all', 'UberEats']:
                    pricing = fc_delivery.scrape_delivery_pricing('ubereats')
                    earnings_per_delivery = fc_delivery.estimate_delivery_earnings(pricing, target_hour, 'ubereats', neighborhood)
                    delivery_results = fc_delivery.calculate_net_earnings(
                        delivery_demand, delivery_supply, earnings_per_delivery,
                        delivery_costs, target_hour, delivery_deadtime
                    )

                    predictions.append({
                        'service': 'UberEats',
                        'min': round(max(12, delivery_results['net_hourly_earnings'] - 6), 2),
                        'max': round(delivery_results['net_hourly_earnings'] + 6, 2),
                        'hotspot': 'Restaurant Districts',
                        'demandScore': round(delivery_score * 0.95, 2),
                        'tripsPerHour': round(delivery_results['deliveries_per_driver'] * 0.95, 2),
                        'surgeMultiplier': round(delivery_results.get('peak_pay_multiplier', 1.0), 2),
                        'color': '#06C167',  # Uber Eats green
                        'startTime': format_hour_to_time(target_hour),
                        'endTime': format_hour_to_time(target_hour + 1)
                    })

                # GrubHub prediction
                if service_filter in ['all', 'GrubHub']:
                    pricing = fc_delivery.scrape_delivery_pricing('grubhub')
                    earnings_per_delivery = fc_delivery.estimate_delivery_earnings(pricing, target_hour, 'grubhub', neighborhood)
                    delivery_results = fc_delivery.calculate_net_earnings(
                        delivery_demand, delivery_supply, earnings_per_delivery,
                        delivery_costs, target_hour, delivery_deadtime
                    )

                    predictions.append({
                        'service': 'GrubHub',
                        'min': round(max(12, delivery_results['net_hourly_earnings'] - 6), 2),
                        'max': round(delivery_results['net_hourly_earnings'] + 6, 2),
                        'hotspot': 'Restaurant Districts',
                        'demandScore': round(delivery_score, 2),
                        'tripsPerHour': round(delivery_results['deliveries_per_driver'], 2),
                        'surgeMultiplier': 1.0,
                        'color': '#FF8000',  # GrubHub orange
                        'startTime': format_hour_to_time(target_hour),
                        'endTime': format_hour_to_time(target_hour + 1)
                    })

                metadata['delivery'] = {
                    'demandEstimate': round(delivery_demand, 0),
                    'driverSupply': round(delivery_supply, 0),
                    'demandSupplyRatio': round(delivery_ratio, 2),
                    'restaurantDensity': round(restaurant_density, 2)
                }

        # Build response
        response_data = {
            'location': location,
            'date': date_str,
            'timeSlot': f"{format_hour_to_time(target_hour)} - {format_hour_to_time(target_hour + 1)}",
            'hour': target_hour,
            'predictions': predictions,
            'metadata': metadata
        }

        # Cache the result
        cache_earnings(location, date_str, target_hour, response_data)

        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to calculate earnings forecast'
        }), 500

@app.route('/api/earnings/batch', methods=['POST'])
def get_earnings_batch():
    """
    Get projected earnings for multiple timeslots at once

    Request Body:
    {
      "location": "San Francisco",
      "date": "2025-10-23",
      "timeSlots": [
        {"startTime": "6:00 AM", "endTime": "7:00 AM"},
        {"startTime": "7:00 AM", "endTime": "8:00 AM"},
        ...
      ]
    }

    Returns array of earnings predictions for each timeslot
    """
    try:
        data = request.get_json()
        location = data.get('location', 'San Francisco')
        date_str = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
        time_slots = data.get('timeSlots', [])

        results = []
        for slot in time_slots:
            start_time = slot.get('startTime')
            end_time = slot.get('endTime')
            target_hour = parse_time_to_hour(start_time)

            # Check cache first
            cached_data = get_cached_earnings(location, date_str, target_hour)
            if cached_data:
                results.append(cached_data)
                continue

            # If not cached, fetch (reuse logic from single endpoint)
            # For brevity, we'll make an internal call
            with app.test_request_context(
                f'/api/earnings?location={location}&date={date_str}&startTime={start_time}&endTime={end_time}'
            ):
                response = get_earnings()
                if isinstance(response, tuple):
                    results.append({'error': 'Failed to fetch'})
                else:
                    results.append(response.get_json())

        return jsonify({
            'location': location,
            'date': date_str,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to process batch request'
        }), 500

@app.route('/api/earnings/week', methods=['GET'])
def get_earnings_week():
    """
    Get projected earnings for an entire week
    Uses improved scraper with live APIs for accurate, location-specific estimates

    Query Parameters:
    - location: string (city name, e.g., "San Francisco") OR
    - lat: float (latitude) + lng: float (longitude)
    - startDate: string (YYYY-MM-DD, defaults to current week start)

    Returns earnings predictions for all days/hours of the week (both rideshare and delivery)
    """
    try:
        # Support both location name and coordinates
        # IMPORTANT: Preserve location name if provided, even if coordinates are also provided
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        location = request.args.get('location', 'San Francisco')
        
        # Parse coordinates if provided (but don't replace location name)
        lat_val = None
        lng_val = None
        if lat and lng:
            try:
                lat_val = float(lat)
                lng_val = float(lng)
                print(f"  📍 GPS coordinates provided: {lat_val:.4f}, {lng_val:.4f}")
            except ValueError:
                pass
        
        # Use location name as primary identifier
        print(f"  📍 Using location name: {location} (coordinates used as supplementary data)")
        
        start_date_str = request.args.get('startDate')

        # Default to start of current week
        if not start_date_str:
            today = datetime.datetime.now()
            start_of_week = today - datetime.timedelta(days=today.weekday())
            start_date_str = start_of_week.strftime('%Y-%m-%d')

        # Generate all hours for the week (6 AM to 11 PM for 7 days)
        days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        hours = range(6, 24)  # 6 AM to 11 PM

        week_data = {}
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')

        # Use improved scraper if available
        scraper = None
        if improved_scraper_available:
            try:
                scraper = ImprovedEarningsScraper()
            except Exception as e:
                print(f"Warning: Could not create improved scraper: {e}")

        for day_offset in range(7):
            # Calculate the actual date for this day (start_date + day_offset)
            # IMPORTANT: This ensures each day uses its correct date, not the week start date
            # The frontend sends start_date as the Sunday of the week
            # So if start_date is Nov 2 (Sunday), then:
            #   day_offset 0 = Nov 2 (Sunday) - use days[0] = 'sunday'
            #   day_offset 1 = Nov 3 (Monday) - use days[1] = 'monday'
            #   ...
            #   day_offset 6 = Nov 8 (Saturday) - use days[6] = 'saturday'
            current_date = start_date + datetime.timedelta(days=day_offset)
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Use day_offset to index days array (matches frontend's weekDates order)
            # days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
            # day_offset 0 = Sunday (first day of week from frontend)
            day_name = days[day_offset]
            
            # Verify the day name matches the actual weekday (for debugging)
            actual_weekday = current_date.strftime('%A').lower()
            if day_name != actual_weekday:
                print(f"  ⚠️  Day name mismatch: day_offset={day_offset}, day_name={day_name}, actual={actual_weekday}, date={date_str}")
                # Use actual weekday to ensure correctness
                day_name = actual_weekday
            
            # Log which date we're processing for debugging
            print(f"  📅 Processing {day_name} ({date_str}) - day {day_offset + 1} of week starting {start_date_str}")

            week_data[day_name] = {}

            for hour in hours:
                # Use cache key with location (includes coordinates if provided)
                cache_location = location
                cached_data = get_cached_earnings(cache_location, date_str, hour)
                
                if cached_data and 'predictions' in cached_data:
                    week_data[day_name][str(hour)] = cached_data['predictions']
                else:
                    # Use improved scraper to get all estimates (both rideshare and delivery)
                    # IMPORTANT: Pass date_str (the actual day's date) to ensure events are scraped for the correct date
                    if scraper:
                        try:
                            print(f"    🔍 Fetching estimates for {date_str} at {hour}:00 (location: {location})")
                            all_estimates = scraper.get_all_estimates(location, date_str, hour, lat_val, lng_val)
                            predictions = all_estimates.get('predictions', [])
                            
                            # Format predictions for frontend
                            formatted_predictions = []
                            for pred in predictions:
                                formatted_predictions.append({
                                    'service': pred.get('service'),
                                    'min': pred.get('min'),
                                    'max': pred.get('max'),
                                    'hotspot': pred.get('hotspot', 'Downtown Core'),
                                    'demandScore': pred.get('demandScore', 0.75),
                                    'tripsPerHour': pred.get('tripsPerHour'),
                                    'surgeMultiplier': pred.get('surgeMultiplier'),
                                    'color': pred.get('color')
                                })
                            
                            # Cache the results
                            if formatted_predictions:
                                cache_data = {
                                    'predictions': formatted_predictions,
                                    'metadata': {
                                        'usingLiveData': True,
                                        'note': 'Live data from improved scraper'
                                    }
                                }
                                cache_earnings(cache_location, date_str, hour, cache_data)
                                week_data[day_name][str(hour)] = formatted_predictions
                            else:
                                # Fallback if scraper returns empty
                                week_data[day_name][str(hour)] = []
                        except Exception as e:
                            print(f"Error getting estimates for {location}, {date_str}, {hour}: {e}")
                            # Fallback to empty array
                            week_data[day_name][str(hour)] = []
                    else:
                        # Fallback if improved scraper not available
                        week_data[day_name][str(hour)] = []

        return jsonify({
            'location': location,
            'startDate': start_date_str,
            'weekData': week_data
        })

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_earnings_week: {e}")
        print(error_trace)
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch week data'
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Earnings Forecaster API Server")
    print("=" * 60)
    print("Endpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/earnings/lightweight- FAST estimates (< 50ms, no scraping)")
    print("  GET  /api/earnings            - Full earnings with scraping (3-10s)")
    print("  POST /api/earnings/batch      - Get earnings for multiple timeslots")
    print("  GET  /api/earnings/week       - Get earnings for entire week")
    print("=" * 60)
    print("TIP: Use /lightweight endpoint for instant UI responses!")
    print("=" * 60)
    print("NOTE: For production, use: gunicorn --bind 0.0.0.0:$PORT api_server:app")
    print("=" * 60)

    # Get port from environment variable (Railway/Heroku) or default to 5001 for local
    # Frontend expects API on port 5001 in development (see client/src/config/api.ts)
    port = int(os.environ.get('PORT', 5001))
    # Disable debug mode in production (Railway sets RAILWAY_ENVIRONMENT)
    debug_mode = os.environ.get('RAILWAY_ENVIRONMENT') != 'production'
    
    print(f"Starting development server on port {port} (debug={debug_mode})")
    print("WARNING: This is a development server. Use gunicorn for production!")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
