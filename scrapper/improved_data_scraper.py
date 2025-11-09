#!/usr/bin/env python3
"""
Improved Data Scraper for Accurate Earnings Estimates
Provides location and time-based estimates for both rideshare and delivery
"""

import requests
from bs4 import BeautifulSoup
import json
import datetime
import re
import math
from typing import Dict, List, Optional, Tuple
from config import *
from live_data_scraper import LiveDataScraper

class ImprovedEarningsScraper:
    """
    Improved scraper that uses multiple data sources for accurate earnings estimates
    Works for both rideshare (Uber/Lyft) and delivery (DoorDash/Uber Eats/GrubHub)
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.location_cache = {}
        self.live_scraper = LiveDataScraper()  # Real-time data scraper
    
    def get_location_data(self, location: str, lat: Optional[float] = None, lng: Optional[float] = None) -> Dict:
        """
        Get location-specific data including city, market size, cost of living adjustments
        IMPORTANT: Uses location name (e.g., "San Francisco") as primary identifier
        Coordinates are only used as supplementary data for geocoding if needed
        """
        # IMPORTANT: Use location name as primary identifier
        # If location is a name like "San Francisco", use it directly
        # If location is coordinates, coordinates should already be handled separately (lat/lng params)
        location_lower = location.lower().strip()
        
        # Check if location looks like coordinates (e.g., "37.7749,-122.4194")
        # Only geocode if we don't have coordinates provided separately
        if ',' in location_lower and not any(c.isalpha() for c in location_lower.split(',')[0]):
            # This looks like coordinates
            # If lat/lng are provided separately, use those instead
            if lat and lng:
                # We have coordinates, so location should be a name
                # Don't geocode coordinates in location string
                pass
            else:
                # No separate coordinates, try to geocode location string to city name
                try:
                    parts = location.split(',')
                    if len(parts) == 2:
                        coord_lat = float(parts[0].strip())
                        coord_lng = float(parts[1].strip())
                        # Try to get city name from coordinates using reverse geocoding
                        from live_data_scraper import LiveDataScraper
                        live_scraper = LiveDataScraper()
                        city_name = live_scraper._reverse_geocode(coord_lat, coord_lng)
                        if city_name:
                            location_lower = city_name.lower()
                            location = city_name
                            print(f"  📍 Reverse geocoded coordinates to city: {location}")
                except:
                    pass  # Use coordinates as-is if geocoding fails
        
        cache_key = location_lower
        if cache_key in self.location_cache:
            return self.location_cache[cache_key]
        
        location_data = {
            'city': location,  # Use location name (e.g., "San Francisco")
            'market_size': 'medium',  # small, medium, large, mega
            'cost_of_living_multiplier': 1.0,
            'base_demand_multiplier': 1.0,
            'pricing_multiplier': 1.0,
            'population_density': 'medium'
        }
        
        # Major cities with known data (use location name, not coordinates)
        major_cities = {
            'san francisco': {
                'market_size': 'large',
                'cost_of_living_multiplier': 1.4,
                'base_demand_multiplier': 1.3,
                'pricing_multiplier': 1.2,
                'population_density': 'high',
                'base_hourly_rideshare': 28,
                'base_hourly_delivery': 24
            },
            'new york': {
                'market_size': 'mega',
                'cost_of_living_multiplier': 1.5,
                'base_demand_multiplier': 1.5,
                'pricing_multiplier': 1.3,
                'population_density': 'very_high',
                'base_hourly_rideshare': 32,
                'base_hourly_delivery': 26
            },
            'los angeles': {
                'market_size': 'mega',
                'cost_of_living_multiplier': 1.3,
                'base_demand_multiplier': 1.4,
                'pricing_multiplier': 1.15,
                'population_density': 'high',
                'base_hourly_rideshare': 26,
                'base_hourly_delivery': 22
            },
            'chicago': {
                'market_size': 'large',
                'cost_of_living_multiplier': 1.1,
                'base_demand_multiplier': 1.2,
                'pricing_multiplier': 1.1,
                'population_density': 'high',
                'base_hourly_rideshare': 24,
                'base_hourly_delivery': 20
            },
            'seattle': {
                'market_size': 'medium',
                'cost_of_living_multiplier': 1.3,
                'base_demand_multiplier': 1.1,
                'pricing_multiplier': 1.15,
                'population_density': 'medium',
                'base_hourly_rideshare': 25,
                'base_hourly_delivery': 21
            },
            'boston': {
                'market_size': 'medium',
                'cost_of_living_multiplier': 1.2,
                'base_demand_multiplier': 1.15,
                'pricing_multiplier': 1.1,
                'population_density': 'high',
                'base_hourly_rideshare': 24,
                'base_hourly_delivery': 20
            },
            'austin': {
                'market_size': 'medium',
                'cost_of_living_multiplier': 1.0,
                'base_demand_multiplier': 1.05,
                'pricing_multiplier': 1.0,
                'population_density': 'medium',
                'base_hourly_rideshare': 22,
                'base_hourly_delivery': 18
            },
            'miami': {
                'market_size': 'large',
                'cost_of_living_multiplier': 1.15,
                'base_demand_multiplier': 1.25,
                'pricing_multiplier': 1.1,
                'population_density': 'high',
                'base_hourly_rideshare': 23,
                'base_hourly_delivery': 19
            }
        }
        
        # Normalize location name
        location_lower = location.lower()
        for city_key, city_data in major_cities.items():
            if city_key in location_lower:
                location_data.update(city_data)
                break
        
        # If using coordinates, try to reverse geocode
        if lat and lng:
            try:
                # Use Nominatim (OpenStreetMap) for reverse geocoding
                geocode_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}"
                response = self.session.get(geocode_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    address = data.get('address', {})
                    city = address.get('city') or address.get('town') or address.get('village')
                    if city:
                        location_lower = city.lower()
                        for city_key, city_data in major_cities.items():
                            if city_key in location_lower:
                                location_data.update(city_data)
                                break
            except Exception as e:
                print(f"Geocoding failed: {e}")
        
        # Default values if city not found
        if 'base_hourly_rideshare' not in location_data:
            location_data['base_hourly_rideshare'] = 22
            location_data['base_hourly_delivery'] = 18
        
        self.location_cache[cache_key] = location_data
        return location_data
    
    def get_demand_multipliers(self, location: str, target_date: str, target_hour: int, service_type: str = 'rideshare',
                              lat: Optional[float] = None, lng: Optional[float] = None) -> Dict:
        """
        Get demand multipliers based on location, date, time, and service type
        """
        try:
            date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
            weekday = date_obj.weekday()  # 0=Monday, 6=Sunday
            is_weekend = weekday >= 5
        except:
            weekday = 0
            is_weekend = False
        
        multipliers = {
            'base_demand': 1.0,
            'time_multiplier': 1.0,
            'weekend_multiplier': 1.0,
            'event_multiplier': 1.0,
            'event_boost': 0.0,  # Additive event boost (0.0 to 1.5)
            'weather_multiplier': 1.0,
            'seasonal_multiplier': 1.0,
            'traffic_factor': 0.0  # Additive traffic factor
        }
        
        # Time-of-day multiplier
        if service_type == 'rideshare':
            multipliers['time_multiplier'] = DEMAND_TIME_FACTORS.get(target_hour, 0.5)
        else:  # delivery
            multipliers['time_multiplier'] = DELIVERY_DEMAND_TIME_FACTORS.get(target_hour, 0.5)
        
        # Weekend multiplier
        if service_type == 'rideshare':
            if is_weekend:
                multipliers['weekend_multiplier'] = 1.25  # More rides on weekends
            if weekday == 4:  # Friday
                multipliers['weekend_multiplier'] = 1.15
        else:  # delivery
            if is_weekend:
                multipliers['weekend_multiplier'] = 1.35  # Much more delivery on weekends
            if weekday == 4:  # Friday
                multipliers['weekend_multiplier'] = 1.25
        
        # Seasonal multiplier (holidays, summer, etc.)
        month = date_obj.month if 'date_obj' in locals() else datetime.datetime.now().month
        if month in [11, 12]:  # November/December (holiday season)
            multipliers['seasonal_multiplier'] = 1.2
        elif month in [6, 7, 8]:  # Summer
            if service_type == 'rideshare':
                multipliers['seasonal_multiplier'] = 1.1  # More travel
            else:
                multipliers['seasonal_multiplier'] = 0.95  # People eat out more
        
        # Get REAL weather data (uses forecast API for future dates)
        # IMPORTANT: Location name (e.g., "San Francisco") is used for all data calculations
        print(f"  🌤️  Fetching weather data for location: {location}")
        weather_data = self.live_scraper.get_weather_data(location, lat, lng, target_date, target_hour)
        multipliers['weather_multiplier'] = weather_data.get('multiplier', 1.0)
        print(f"  ✅ Weather multiplier: {multipliers['weather_multiplier']:.2f}x (source: {weather_data.get('source', 'default')})")
        
        # Get REAL events data from Ticketmaster API
        # IMPORTANT: Location name (e.g., "San Francisco") is used for all data calculations
        print(f"  🎟️  Fetching events data for location: {location} on {target_date}...")
        events_data = self.live_scraper.get_events_data(location, lat, lng, target_date)
        events_found = events_data.get('events_found', 0)
        event_multiplier = events_data.get('demand_multiplier', 1.0)
        event_source = events_data.get('source', 'unknown')
        
        print(f"  📊 Events Summary for {location}: {events_found} events found (source: {event_source})")
        print(f"  ✅ Event multiplier: {event_multiplier:.2f}x")
        
        multipliers['event_multiplier'] = event_multiplier
        
        # Get Ticketmaster event boost (additive factor based on arrival/departure surges)
        # This calculates boost for the specific hour based on event start/end times and capacity
        try:
            from ticketmaster_events_scraper import get_event_boost
            event_boost = get_event_boost(location, target_date, target_hour, lat, lng)
            multipliers['event_boost'] = event_boost
            if event_boost > 0:
                print(f"  🎟️  Ticketmaster event boost for hour {target_hour:02d}:00: +{event_boost:.2f} (arrival/departure surge)")
            elif events_found > 0:
                print(f"  ℹ️  Ticketmaster: {events_found} events found, but no boost for hour {target_hour:02d}:00 (outside surge windows)")
        except ImportError:
            # Ticketmaster scraper not available, use default event multiplier
            multipliers['event_boost'] = 0.0
            print(f"  ⚠️  Ticketmaster scraper not available, event boost disabled")
        except Exception as e:
            print(f"  ⚠️  Error calculating event boost: {e}")
            multipliers['event_boost'] = 0.0
        
        # Get REAL traffic data (for traffic_factor)
        traffic_data = self.live_scraper.get_traffic_data(location, lat, lng)
        # Convert traffic multiplier to additive factor (traffic_factor: 0.0 to 0.3)
        traffic_multiplier = traffic_data.get('traffic_factor', 1.0)
        if traffic_multiplier > 1.0:
            # High traffic = positive additive factor (0.0 to 0.3)
            multipliers['traffic_factor'] = min((traffic_multiplier - 1.0) * 0.5, 0.3)
        elif traffic_multiplier < 1.0:
            # Low traffic = negative additive factor (-0.1 to 0.0)
            multipliers['traffic_factor'] = max((traffic_multiplier - 1.0) * 0.2, -0.1)
        else:
            multipliers['traffic_factor'] = 0.0
        
        # Calculate total demand multiplier (multiplicative factors)
        # Cap the total to avoid unrealistic earnings (max 1.8x for rideshare, 2.0x for delivery)
        base_total = (
            multipliers['time_multiplier'] *
            multipliers['weekend_multiplier'] *
            multipliers['event_multiplier'] *
            multipliers['weather_multiplier'] *
            multipliers['seasonal_multiplier']
        )
        
        # Cap total demand multiplier to realistic levels
        if service_type == 'rideshare':
            multipliers['total_demand'] = min(base_total, 1.8)  # Max 1.8x for rideshare
        else:
            multipliers['total_demand'] = min(base_total, 2.0)  # Max 2.0x for delivery (peak meal times)
        
        return multipliers
    
    def estimate_rideshare_earnings(self, location: str, target_date: str, target_hour: int, 
                                   lat: Optional[float] = None, lng: Optional[float] = None) -> Dict:
        """
        Estimate rideshare earnings (Uber/Lyft) for a specific location and time
        Uses REAL-TIME data from APIs
        """
        location_data = self.get_location_data(location, lat, lng)
        demand_multipliers = self.get_demand_multipliers(location, target_date, target_hour, 'rideshare', lat, lng)
        
        # Get REAL gas prices
        gas_data = self.live_scraper.get_gas_prices(location, lat, lng)
        gas_price = gas_data.get('price_per_gallon', GAS_PRICE_PER_GALLON)
        
        # Get REAL traffic data
        traffic_data = self.live_scraper.get_traffic_data(location, lat, lng)
        traffic_factor = traffic_data.get('traffic_factor', 1.0)
        
        # Get REAL pricing estimates
        pricing_data = self.live_scraper.get_real_time_pricing_estimates(location, 'uber', lat, lng)
        
        # Base hourly earnings for the location
        base_hourly = location_data.get('base_hourly_rideshare', 22)
        
        # Apply demand multipliers (already capped in get_demand_multipliers)
        adjusted_earnings = base_hourly * demand_multipliers['total_demand']
        
        # Apply additive factors: event_boost and traffic_factor
        # IMPORTANT: Event boost from Ticketmaster is applied here to increase earnings during event arrival/departure
        # Formula: adjusted_rate = base_rate * (1 + traffic_factor + event_boost)
        event_boost = demand_multipliers.get('event_boost', 0.0)
        traffic_factor_additive = demand_multipliers.get('traffic_factor', 0.0)
        additive_factor = 1.0 + traffic_factor_additive + event_boost
        adjusted_earnings *= additive_factor
        
        # Log the impact of event boost on earnings
        if event_boost > 0:
            earnings_before_boost = adjusted_earnings / additive_factor
            earnings_boost_amount = adjusted_earnings - earnings_before_boost
            print(f"  💰 Event boost impact: +${earnings_boost_amount:.2f}/hour (${earnings_before_boost:.2f} → ${adjusted_earnings:.2f})")
            print(f"  📈 Event boost percentage: +{(event_boost * 100):.1f}% increase due to Ticketmaster events")
        
        # Apply location-specific multipliers (but cap total adjustment)
        location_multiplier = location_data.get('pricing_multiplier', 1.0)
        # Don't multiply by location_multiplier again if it's already factored into base_hourly
        # Just use a smaller adjustment (1.0-1.1x) for high-cost areas
        if location_multiplier > 1.2:
            location_adjustment = 1.1  # Cap location adjustment
        else:
            location_adjustment = 1.0
        adjusted_earnings *= location_adjustment
        
        # Calculate surge multiplier based on demand and event boost
        # IMPORTANT: Event boost increases surge multiplier to reflect higher demand during events
        surge_multiplier = 1.0
        base_demand = demand_multipliers['total_demand']
        
        # Base surge calculation
        if base_demand > 1.5:
            surge_multiplier = 1.15  # Reduced from 1.2
        elif base_demand > 1.3:
            surge_multiplier = 1.1   # Reduced from 1.2
        elif base_demand < 0.7:
            surge_multiplier = 0.95  # Slight reduction for low demand
        
        # Additional surge boost from Ticketmaster events (event_boost already applied additively, but also boost surge)
        # This ensures events have a visible impact on final earnings
        if event_boost > 0:
            # Event boost increases surge multiplier (events = higher demand = higher surge)
            surge_boost_from_events = min(event_boost * 0.3, 0.15)  # Max 15% surge boost from events
            surge_multiplier = min(surge_multiplier + surge_boost_from_events, 1.3)  # Cap total surge at 1.3x
            print(f"  📊 Surge multiplier: {surge_multiplier:.2f}x (includes +{surge_boost_from_events:.2f}x from event boost)")
        
        # Calculate trips per hour (varies with demand)
        base_trips_per_hour = 2.2
        trips_per_hour = base_trips_per_hour * demand_multipliers['time_multiplier']
        trips_per_hour = max(1.0, min(3.5, trips_per_hour))  # Clamp between 1 and 3.5
        
        # Calculate costs (gas, wear/tear) - using REAL gas prices
        miles_per_hour = trips_per_hour * AVG_TRIP_DISTANCE_MILES
        # Adjust miles based on traffic
        miles_per_hour *= traffic_factor  # More traffic = more miles
        gas_cost_per_hour = (miles_per_hour / AVG_MPG) * gas_price  # Use real gas price
        wear_tear_cost = miles_per_hour * WEAR_TEAR_PER_MILE
        total_costs = gas_cost_per_hour + wear_tear_cost
        
        # Net earnings (final earnings should be realistic: $15-45/hr typical range)
        gross_earnings = adjusted_earnings * surge_multiplier
        net_earnings = gross_earnings - total_costs
        
        # Ensure earnings are realistic (cap at reasonable maximum)
        net_earnings = min(net_earnings, 55)  # Cap at $55/hr (very high surge)
        net_earnings = max(net_earnings, 8)   # Minimum $8/hr
        
        # Determine hotspot
        if target_hour in [7, 8, 17, 18]:
            hotspot = "Financial District / Commute Corridors"
        elif target_hour in [12, 13]:
            hotspot = "Downtown / Business Districts"
        elif target_hour in [18, 19, 20]:
            hotspot = "Entertainment Districts"
        elif target_hour >= 21 or target_hour <= 2:
            hotspot = "Nightlife Areas"
        else:
            hotspot = "Downtown Core"
        
        # Include event boost in response metadata
        event_boost = demand_multipliers.get('event_boost', 0.0)
        events_found = 0  # Will be set from events_data if available
        
        return {
            'service': 'Uber',
            'min': round(max(10, net_earnings - 5), 2),
            'max': round(net_earnings + 5, 2),
            'hotspot': hotspot,
            'demandScore': round(min(1.0, demand_multipliers['total_demand'] / 1.5), 2),
            'tripsPerHour': round(trips_per_hour, 2),
            'surgeMultiplier': round(surge_multiplier, 2),
            'color': '#4285F4',
            'baseEarnings': round(gross_earnings, 2),
            'costs': round(total_costs, 2),
            'netEarnings': round(net_earnings, 2),
            'eventBoost': round(event_boost, 3),  # Include event boost in response
            'eventBoostPercentage': round(event_boost * 100, 1)  # Percentage increase from events
        }
    
    def estimate_delivery_earnings(self, location: str, target_date: str, target_hour: int,
                                   service: str = 'doordash',
                                   lat: Optional[float] = None, lng: Optional[float] = None) -> Dict:
        """
        Estimate delivery earnings (DoorDash/Uber Eats/GrubHub) for a specific location and time
        Uses REAL-TIME data from APIs
        """
        # IMPORTANT: Use location name (e.g., "San Francisco") for all data calculations
        coord_str = f"{lat:.4f}, {lng:.4f}" if lat and lng else "not provided (will geocode if needed)"
        print(f"  📍 Location: {location} (coordinates: {coord_str})")
        location_data = self.get_location_data(location, lat, lng)
        demand_multipliers = self.get_demand_multipliers(location, target_date, target_hour, 'delivery', lat, lng)
        
        # Get REAL gas prices for location
        print(f"  ⛽ Fetching gas prices for location: {location}")
        gas_data = self.live_scraper.get_gas_prices(location, lat, lng)
        gas_price = gas_data.get('price_per_gallon', GAS_PRICE_PER_GALLON)
        print(f"  ✅ Gas price: ${gas_price:.2f}/gallon (source: {gas_data.get('source', 'default')})")
        
        # Get REAL traffic data for location (affects delivery times)
        print(f"  🚦 Fetching traffic data for location: {location}")
        traffic_data = self.live_scraper.get_traffic_data(location, lat, lng)
        traffic_factor = traffic_data.get('traffic_factor', 1.0)
        print(f"  ✅ Traffic factor: {traffic_factor:.2f}x (source: {traffic_data.get('source', 'default')})")
        
        # Base hourly earnings for the location
        base_hourly = location_data.get('base_hourly_delivery', 18)
        
        # Apply demand multipliers (already capped in get_demand_multipliers)
        adjusted_earnings = base_hourly * demand_multipliers['total_demand']
        
        # Apply additive factors: event_boost and traffic_factor
        # IMPORTANT: Event boost from Ticketmaster is applied here to increase earnings during event arrival/departure
        # Formula: adjusted_rate = base_rate * (1 + traffic_factor + event_boost)
        event_boost = demand_multipliers.get('event_boost', 0.0)
        traffic_factor_additive = demand_multipliers.get('traffic_factor', 0.0)
        additive_factor = 1.0 + traffic_factor_additive + event_boost
        adjusted_earnings *= additive_factor
        
        # Log the impact of event boost on earnings
        if event_boost > 0:
            earnings_before_boost = adjusted_earnings / additive_factor
            earnings_boost_amount = adjusted_earnings - earnings_before_boost
            print(f"  💰 Event boost impact: +${earnings_boost_amount:.2f}/hour (${earnings_before_boost:.2f} → ${adjusted_earnings:.2f})")
            print(f"  📈 Event boost percentage: +{(event_boost * 100):.1f}% increase due to Ticketmaster events")
        
        # Apply location-specific multipliers (smaller adjustment)
        location_multiplier = location_data.get('pricing_multiplier', 1.0)
        if location_multiplier > 1.2:
            location_adjustment = 1.1  # Cap location adjustment
        else:
            location_adjustment = 1.0
        adjusted_earnings *= location_adjustment
        
        # Service-specific adjustments
        service_multipliers = {
            'doordash': 1.0,
            'ubereats': 0.95,
            'grubhub': 1.05
        }
        adjusted_earnings *= service_multipliers.get(service.lower(), 1.0)
        
        # Peak pay multiplier (meal times get bonus pay, but smaller)
        # IMPORTANT: Event boost also increases peak pay multiplier for delivery during events
        peak_pay_multiplier = 1.0
        event_boost = demand_multipliers.get('event_boost', 0.0)
        
        if target_hour in [12, 13]:  # Lunch
            peak_pay_multiplier = 1.15  # Reduced from 1.2
        elif target_hour in [18, 19, 20]:  # Dinner
            peak_pay_multiplier = 1.2   # Reduced from 1.3
        elif target_hour in [11, 17, 21]:  # Shoulder hours
            peak_pay_multiplier = 1.05  # Reduced from 1.1
        
        # Additional peak pay boost from Ticketmaster events
        if event_boost > 0:
            # Events increase peak pay (more demand = higher peak pay)
            peak_pay_boost_from_events = min(event_boost * 0.25, 0.12)  # Max 12% peak pay boost from events
            peak_pay_multiplier = min(peak_pay_multiplier + peak_pay_boost_from_events, 1.35)  # Cap total at 1.35x
            print(f"  📊 Peak pay multiplier: {peak_pay_multiplier:.2f}x (includes +{peak_pay_boost_from_events:.2f}x from event boost)")
        
        # Calculate deliveries per hour
        base_deliveries_per_hour = 2.5
        deliveries_per_hour = base_deliveries_per_hour * demand_multipliers['time_multiplier']
        deliveries_per_hour = max(1.0, min(4.0, deliveries_per_hour))  # Clamp between 1 and 4
        
        # Calculate costs (gas, wear/tear - lower for delivery) - using REAL gas prices
        miles_per_hour = deliveries_per_hour * AVG_DELIVERY_DISTANCE_MILES
        # Adjust for traffic (more traffic = slower deliveries = more time = more costs)
        miles_per_hour *= traffic_factor
        gas_cost_per_hour = (miles_per_hour / DELIVERY_MPG) * gas_price  # Use real gas price
        wear_tear_cost = miles_per_hour * (WEAR_TEAR_PER_MILE * 0.7)  # Lower wear/tear for shorter trips
        total_costs = gas_cost_per_hour + wear_tear_cost
        
        # Net earnings with peak pay (final earnings should be realistic: $12-40/hr typical range)
        gross_earnings = adjusted_earnings * peak_pay_multiplier
        net_earnings = gross_earnings - total_costs
        
        # Ensure earnings are realistic (cap at reasonable maximum)
        net_earnings = min(net_earnings, 45)  # Cap at $45/hr (very high peak pay)
        net_earnings = max(net_earnings, 10)  # Minimum $10/hr
        
        # Service colors
        service_colors = {
            'doordash': '#FFD700',
            'ubereats': '#06C167',
            'grubhub': '#FF8000'
        }
        
        # Include event boost in response metadata
        event_boost = demand_multipliers.get('event_boost', 0.0)
        
        return {
            'service': service.capitalize(),
            'min': round(max(12, net_earnings - 6), 2),
            'max': round(net_earnings + 6, 2),
            'hotspot': 'Restaurant Districts',
            'demandScore': round(min(1.0, demand_multipliers['total_demand'] / 1.5), 2),
            'tripsPerHour': round(deliveries_per_hour, 2),
            'surgeMultiplier': round(peak_pay_multiplier, 2),
            'color': service_colors.get(service.lower(), '#FFD700'),
            'baseEarnings': round(gross_earnings, 2),
            'costs': round(total_costs, 2),
            'netEarnings': round(net_earnings, 2),
            'eventBoost': round(event_boost, 3),  # Include event boost in response
            'eventBoostPercentage': round(event_boost * 100, 1)  # Percentage increase from events
        }
    
    def get_all_estimates(self, location: str, target_date: str, target_hour: int,
                         lat: Optional[float] = None, lng: Optional[float] = None) -> Dict:
        """
        Get estimates for both rideshare and delivery services
        """
        results = {
            'location': location,
            'date': target_date,
            'hour': target_hour,
            'predictions': []
        }
        
        # Rideshare estimates
        uber_estimate = self.estimate_rideshare_earnings(location, target_date, target_hour, lat, lng)
        results['predictions'].append(uber_estimate)
        
        # Lyft (typically 8-10% less than Uber)
        lyft_estimate = uber_estimate.copy()
        lyft_estimate['service'] = 'Lyft'
        lyft_estimate['min'] = round(lyft_estimate['min'] * 0.92, 2)
        lyft_estimate['max'] = round(lyft_estimate['max'] * 0.92, 2)
        lyft_estimate['demandScore'] = round(lyft_estimate['demandScore'] * 0.95, 2)
        lyft_estimate['tripsPerHour'] = round(lyft_estimate['tripsPerHour'] * 0.9, 2)
        lyft_estimate['color'] = '#FF00BF'
        results['predictions'].append(lyft_estimate)
        
        # Delivery estimates
        for service in ['doordash', 'ubereats', 'grubhub']:
            delivery_estimate = self.estimate_delivery_earnings(location, target_date, target_hour, service, lat, lng)
            results['predictions'].append(delivery_estimate)
        
        return results

