#!/usr/bin/env python3
"""
Flask API server for rideshare and delivery earnings forecaster
Provides REST endpoints for the frontend to fetch real-time earnings predictions
Supports: Uber, Lyft (rideshare) and DoorDash, Uber Eats, GrubHub (delivery)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from scrape import UberEarningsForecaster
from delivery_forecaster import DeliveryEarningsForecaster
from config import *
import datetime
import json
from functools import lru_cache
import hashlib

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global forecaster instances (reused for efficiency)
rideshare_forecaster = None
delivery_forecaster = None

def get_rideshare_forecaster():
    """Get or create rideshare forecaster instance"""
    global rideshare_forecaster
    if rideshare_forecaster is None:
        rideshare_forecaster = UberEarningsForecaster()
    return rideshare_forecaster

def get_delivery_forecaster():
    """Get or create delivery forecaster instance"""
    global delivery_forecaster
    if delivery_forecaster is None:
        delivery_forecaster = DeliveryEarningsForecaster()
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

        predictions = []

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
                'note': 'Fast estimates from config defaults (no live scraping)'
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

        # Parse hour from start time
        target_hour = parse_time_to_hour(start_time)

        # Check cache first (use coordinates or city name as key)
        cached_data = get_cached_earnings(location, date_str, target_hour)
        if cached_data:
            return jsonify(cached_data)

        # Determine which services to calculate
        needs_rideshare = service_filter in ['all', 'Uber', 'Lyft']
        needs_delivery = service_filter in ['all', 'DoorDash', 'UberEats', 'GrubHub']

        # Build predictions
        predictions = []
        metadata = {}

        # ========== RIDESHARE CALCULATIONS ==========
        if needs_rideshare:
            fc = get_rideshare_forecaster()

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

    Query Parameters:
    - location: string
    - startDate: string (YYYY-MM-DD, defaults to current week start)

    Returns earnings predictions for all days/hours of the week
    """
    try:
        location = request.args.get('location', 'San Francisco')
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

        for day_offset in range(7):
            current_date = start_date + datetime.timedelta(days=day_offset)
            date_str = current_date.strftime('%Y-%m-%d')
            day_name = days[current_date.weekday()]

            week_data[day_name] = {}

            for hour in hours:
                # Check cache
                cached_data = get_cached_earnings(location, date_str, hour)
                if cached_data:
                    week_data[day_name][str(hour)] = cached_data['predictions']
                else:
                    # For week view, use simplified calculation (no scraping for performance)
                    # This is a placeholder - you can optimize this further
                    week_data[day_name][str(hour)] = [{
                        'service': 'Uber',
                        'min': 20,
                        'max': 35,
                        'hotspot': 'Downtown Core',
                        'demandScore': 0.75
                    }]

        return jsonify({
            'location': location,
            'startDate': start_date_str,
            'weekData': week_data
        })

    except Exception as e:
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

    # Run in development mode on port 5002 (different from Express server on 5001)
    app.run(host='0.0.0.0', port=5002, debug=True)
