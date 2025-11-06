#!/usr/bin/env python3
"""
Delivery Driver Earnings Forecast Tool
Calculates projected earnings for food delivery services (DoorDash, Uber Eats, GrubHub)
"""

import requests
from bs4 import BeautifulSoup
import datetime
import re
from config import *

class DeliveryEarningsForecaster:
    """
    Forecaster for delivery driver earnings (DoorDash, Uber Eats, GrubHub)
    Uses separate calculation model from rideshare
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_events(self, target_date, target_hour):
        """Scrape events data - affects delivery demand (food events, concerts, etc.)"""
        print("Scraping events data for delivery demand...")

        events_data = []
        demand_multiplier = 1.0

        try:
            date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
            weekday = date_obj.strftime("%A").lower()
        except:
            weekday = "monday"

        # Weekend boost for delivery (people order more on weekends)
        if weekday in ['saturday', 'sunday']:
            demand_multiplier = 1.4
        elif weekday == 'friday':
            demand_multiplier = 1.2

        # Food festivals, concerts, sports events increase delivery demand
        try:
            url = "https://sf.funcheap.com"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            event_elements = soup.find_all(['div', 'article'], class_=re.compile(r'event|listing|post'))

            for element in event_elements[:15]:
                text = element.get_text().lower()
                # Food events particularly relevant
                if any(keyword in text for keyword in ['food', 'restaurant', 'festival', 'concert', 'game']):
                    events_data.append({
                        'source': 'SF FunCheap',
                        'text': text[:100]
                    })
        except Exception as e:
            print(f"Error scraping events: {e}")

        # Events have moderate impact on delivery
        event_count = len(events_data)
        if event_count > 0:
            demand_multiplier *= (1.0 + event_count * 0.02)  # 2% boost per event

        print(f"Found {event_count} events, weekday: {weekday}, demand multiplier: {demand_multiplier:.2f}")

        return {
            'events_found': event_count,
            'demand_multiplier': demand_multiplier,
            'events_data': events_data,
            'weekday': weekday
        }

    def scrape_weather(self, target_date):
        """Weather has MAJOR impact on delivery demand (rain/snow = more orders)"""
        print("Scraping weather data...")

        weather_multiplier = 1.0

        try:
            date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
            month = date_obj.month

            # Seasonal factors for SF delivery
            if month in [12, 1, 2]:  # Winter
                weather_multiplier = 1.25  # Cold weather = more delivery orders
            elif month in [6, 7, 8]:  # Summer
                weather_multiplier = 0.95  # Nice weather = people eat out more
            else:  # Spring/Fall
                weather_multiplier = 1.05

            # TODO: Add real-time weather API for rain/snow detection
            # Rain can increase delivery demand by 30-50%

            print(f"Weather multiplier: {weather_multiplier:.2f}")

        except Exception as e:
            print(f"Error checking weather: {e}")
            weather_multiplier = 1.0

        return weather_multiplier

    def scrape_restaurant_density(self, location='San Francisco', neighborhood=None):
        """
        Scrape restaurant density from Yelp
        More restaurants = more delivery opportunities
        """
        print(f"Checking restaurant density for {location}...")

        # Use predefined densities from config
        if neighborhood and neighborhood in RESTAURANT_DENSITY:
            density = RESTAURANT_DENSITY[neighborhood]
            print(f"Restaurant density for {neighborhood}: {density}x")
            return density

        # Default for SF areas
        return RESTAURANT_DENSITY.get('Downtown Core', 2.5)

    def scrape_delivery_pricing(self, service='doordash'):
        """
        Get current delivery pricing
        In production, would scrape from driver forums, Gridwise, etc.
        """
        print(f"Getting {service} pricing data...")

        pricing_models = {
            'doordash': {
                'base_pay_min': DOORDASH_BASE_PAY_MIN,
                'base_pay_max': DOORDASH_BASE_PAY_MAX,
                'per_mile': DOORDASH_PER_MILE,
                'avg_tip': DOORDASH_AVG_TIP,
                'peak_pay_max': DOORDASH_PEAK_PAY_MAX
            },
            'ubereats': {
                'base_fare': UBEREATS_BASE_FARE,
                'pickup_fee': UBEREATS_PICKUP_FEE,
                'dropoff_fee': UBEREATS_DROPOFF_FEE,
                'per_mile': UBEREATS_PER_MILE,
                'per_minute': UBEREATS_PER_MINUTE,
                'avg_tip': UBEREATS_AVG_TIP,
                'trip_supplement_max': UBEREATS_TRIP_SUPPLEMENT_MAX
            },
            'grubhub': {
                'base_pay': GRUBHUB_BASE_PAY,
                'per_mile': GRUBHUB_PER_MILE,
                'per_minute': GRUBHUB_PER_MINUTE,
                'avg_tip': GRUBHUB_AVG_TIP,
                'block_bonus': GRUBHUB_BLOCK_BONUS,
                'contribution_pay_max': GRUBHUB_CONTRIBUTION_PAY_MAX
            }
        }

        pricing = pricing_models.get(service.lower(), pricing_models['doordash'])
        print(f"{service} pricing loaded")
        return pricing

    def estimate_demand(self, events_data, weather_multiplier, target_hour, restaurant_density=1.0):
        """
        Estimate delivery demand - MEAL-TIME FOCUSED
        Peak hours: 11 AM-2 PM (lunch), 5-9 PM (dinner)
        """
        print("Estimating delivery demand...")

        # Base delivery demand
        base_demand = BASE_DELIVERY_DEMAND_SF

        # Apply meal-time multipliers (CRITICAL for delivery)
        time_factor = DELIVERY_DEMAND_TIME_FACTORS.get(target_hour, 0.5)

        # Events multiplier
        events_multiplier = events_data['demand_multiplier']

        # Weather has BIGGER impact on delivery than rideshare
        weather_boost = 1.0 + (weather_multiplier - 1.0) * 1.5

        # Restaurant density is critical
        density_factor = restaurant_density

        # Calculate final demand
        estimated_demand = base_demand * time_factor * events_multiplier * weather_boost * density_factor

        print(f"Delivery demand estimate: {estimated_demand:.0f} orders/hour")
        print(f"  - Time factor: {time_factor:.2f}")
        print(f"  - Events: {events_multiplier:.2f}")
        print(f"  - Weather: {weather_boost:.2f}")
        print(f"  - Restaurant density: {density_factor:.2f}")

        return estimated_demand

    def estimate_driver_supply(self, target_hour):
        """Estimate active delivery drivers"""
        print("Estimating delivery driver supply...")

        # Base delivery drivers
        base_drivers = BASE_DELIVERY_DRIVERS_SF

        # Use delivery-specific supply factors
        supply_factor = DELIVERY_SUPPLY_TIME_FACTORS.get(target_hour, 0.5)

        # Calculate active drivers
        active_drivers = base_drivers * supply_factor

        print(f"Active delivery drivers estimate: {active_drivers:.0f}")
        return active_drivers

    def calculate_deadtime(self, target_hour, demand_supply_ratio):
        """
        Calculate deadtime for delivery (includes restaurant wait!)
        Different from rideshare - includes waiting at restaurant
        """
        print("Calculating delivery deadtime...")

        # Base times from config
        base_wait = DELIVERY_DEADTIME_CONFIG['avg_wait_time_minutes']
        pickup_time = DELIVERY_DEADTIME_CONFIG['avg_pickup_time_minutes']
        restaurant_wait = DELIVERY_DEADTIME_CONFIG['restaurant_wait_minutes']

        # Time-of-day factor
        deadtime_factor = DELIVERY_DEADTIME_CONFIG['deadtime_factors'].get(target_hour, 1.0)

        # Adjust wait time based on demand/supply ratio
        if demand_supply_ratio > 1.5:
            # High demand - orders come fast
            wait_multiplier = 0.4
        elif demand_supply_ratio > 1.0:
            wait_multiplier = 0.7
        else:
            # Low demand - more waiting
            wait_multiplier = 1.5

        # Calculate adjusted wait time
        adjusted_wait = base_wait * deadtime_factor * wait_multiplier

        # Restaurant wait varies by meal rush
        if target_hour in [12, 13, 18, 19]:  # Peak meal times
            restaurant_wait *= 1.3  # 30% longer wait during rush

        # Total deadtime
        total_deadtime = adjusted_wait + pickup_time + restaurant_wait

        # Apply constraints
        total_deadtime = max(DELIVERY_DEADTIME_CONFIG['min_deadtime_minutes'],
                           min(total_deadtime, DELIVERY_DEADTIME_CONFIG['max_deadtime_minutes']))

        print(f"Delivery deadtime: {total_deadtime:.1f} min (wait: {adjusted_wait:.1f}, pickup: {pickup_time:.1f}, restaurant: {restaurant_wait:.1f})")

        return {
            'wait_time_minutes': adjusted_wait,
            'pickup_time_minutes': pickup_time,
            'restaurant_wait_minutes': restaurant_wait,
            'total_deadtime_minutes': total_deadtime
        }

    def estimate_delivery_earnings(self, pricing_data, target_hour, service='doordash', neighborhood=None):
        """
        Calculate earnings per delivery
        DIFFERENT MODEL than rideshare: base + distance + tips + peak pay
        """
        print(f"Estimating {service} delivery earnings...")

        avg_distance = AVG_DELIVERY_DISTANCE_MILES
        avg_duration = AVG_DELIVERY_DURATION_MINUTES

        if service.lower() == 'doordash':
            # Base pay varies by distance and complexity
            if avg_distance < 2:
                base_pay = pricing_data['base_pay_min']
            elif avg_distance > 5:
                base_pay = pricing_data['base_pay_max']
            else:
                # Linear interpolation
                base_pay = pricing_data['base_pay_min'] + (avg_distance - 2) * (pricing_data['base_pay_max'] - pricing_data['base_pay_min']) / 3

            # Distance component
            distance_pay = avg_distance * pricing_data['per_mile']

            # Peak pay during meal rushes
            peak_pay = 0
            if target_hour in [12, 13]:  # Lunch rush
                peak_pay = pricing_data['peak_pay_max'] * 0.6
            elif target_hour in [18, 19]:  # Dinner rush
                peak_pay = pricing_data['peak_pay_max']
            elif target_hour in [11, 14, 17, 20]:  # Shoulder hours
                peak_pay = pricing_data['peak_pay_max'] * 0.3

            # Tips (MAJOR component - can be 30-40% of earnings)
            base_tip = pricing_data['avg_tip']
            if neighborhood and neighborhood in TIP_MULTIPLIERS:
                tip = base_tip * TIP_MULTIPLIERS[neighborhood]
            else:
                tip = base_tip

            total_earnings = base_pay + distance_pay + peak_pay + tip

            print(f"  Base: ${base_pay:.2f}, Distance: ${distance_pay:.2f}, Peak: ${peak_pay:.2f}, Tip: ${tip:.2f}")

        elif service.lower() == 'ubereats':
            # Uber Eats model: base + pickup + dropoff + distance + time + supplement + tip
            base = pricing_data['base_fare']
            pickup = pricing_data['pickup_fee']
            dropoff = pricing_data['dropoff_fee']
            distance = avg_distance * pricing_data['per_mile']
            time = avg_duration * pricing_data['per_minute']

            # Trip supplement for long/complex deliveries
            if avg_distance > 3:
                supplement = min(pricing_data['trip_supplement_max'], avg_distance * 0.5)
            else:
                supplement = 0

            # Tips
            base_tip = pricing_data['avg_tip']
            if neighborhood and neighborhood in TIP_MULTIPLIERS:
                tip = base_tip * TIP_MULTIPLIERS[neighborhood]
            else:
                tip = base_tip

            total_earnings = base + pickup + dropoff + distance + time + supplement + tip

            print(f"  Base: ${base:.2f}, Fees: ${pickup + dropoff:.2f}, Distance: ${distance:.2f}, Tip: ${tip:.2f}")

        elif service.lower() == 'grubhub':
            # GrubHub model: base + distance + time + contribution + tip
            base = pricing_data['base_pay']
            distance = avg_distance * pricing_data['per_mile']
            time = avg_duration * pricing_data['per_minute']

            # GrubHub guarantees minimum, adds contribution pay if needed
            min_without_tip = base + distance + time
            if min_without_tip < 7.00:  # GrubHub typical minimum
                contribution = 7.00 - min_without_tip
            else:
                contribution = 0

            # Tips (GrubHub tends to get higher tips)
            base_tip = pricing_data['avg_tip']
            if neighborhood and neighborhood in TIP_MULTIPLIERS:
                tip = base_tip * TIP_MULTIPLIERS[neighborhood]
            else:
                tip = base_tip

            total_earnings = base + distance + time + contribution + tip

            print(f"  Base: ${base:.2f}, Distance: ${distance:.2f}, Contribution: ${contribution:.2f}, Tip: ${tip:.2f}")

        else:
            # Fallback
            total_earnings = 10.00

        print(f"Total per delivery: ${total_earnings:.2f}")
        return total_earnings

    def estimate_costs(self, gas_price_per_gallon, avg_miles_per_hour=None):
        """
        Estimate hourly operating costs for delivery
        Similar to rideshare but shorter distances
        """
        print("Estimating delivery costs...")

        # Delivery drivers cover less miles per hour than rideshare
        if avg_miles_per_hour is None:
            # Estimate based on avg delivery distance and deliveries per hour
            avg_miles_per_hour = 12  # Typically 10-15 miles/hour for delivery

        # Gas costs
        gas_cost_per_hour = avg_miles_per_hour * (gas_price_per_gallon / DELIVERY_MPG)

        # Wear and tear (slightly less per mile due to shorter trips)
        wear_tear_cost = avg_miles_per_hour * (WEAR_TEAR_PER_MILE * 0.9)

        # Other costs (insurance, maintenance) - lower for delivery
        other_costs = 3.50  # Lower than rideshare (less strict insurance requirements)

        total_costs = gas_cost_per_hour + wear_tear_cost + other_costs

        print(f"Hourly costs: ${total_costs:.2f} (gas: ${gas_cost_per_hour:.2f}, wear: ${wear_tear_cost:.2f}, other: ${other_costs:.2f})")
        return total_costs

    def calculate_net_earnings(self, demand, supply, earnings_per_delivery, costs, target_hour, deadtime_data):
        """
        Calculate final net earnings for delivery driver
        Includes stacked orders logic (multiple deliveries at once)
        """
        print("Calculating net delivery earnings...")

        # Calculate deliveries per driver based on demand/supply
        deliveries_per_driver = demand / supply if supply > 0 else 0
        demand_supply_ratio = demand / supply if supply > 0 else 0

        # Calculate max deliveries per hour with deadtime
        total_time_per_delivery = AVG_DELIVERY_DURATION_MINUTES + deadtime_data['total_deadtime_minutes']
        max_deliveries_per_hour = 60 / total_time_per_delivery

        # Stacked orders boost (CRITICAL for delivery profitability)
        stacking_factor = 1.0
        if demand_supply_ratio > STACKED_ORDERS_CONFIG['min_demand_ratio']:
            # High demand allows stacked orders
            stacking_factor = STACKED_ORDERS_CONFIG['efficiency_multiplier']
            max_deliveries_per_hour *= stacking_factor
            print(f"  Stacked orders enabled: {stacking_factor:.2f}x efficiency")

        # Apply limits
        deliveries_per_driver = min(deliveries_per_driver, max_deliveries_per_hour)

        # Calculate earnings
        gross_hourly = deliveries_per_driver * earnings_per_delivery
        net_hourly = gross_hourly - costs

        # Peak pay acts like surge
        peak_pay_multiplier = 1.0
        if target_hour in [12, 13, 18, 19]:
            peak_pay_multiplier = 1.2  # Reflects peak pay bonuses

        print(f"Deliveries per driver: {deliveries_per_driver:.2f}")
        print(f"Stacking factor: {stacking_factor:.2f}")
        print(f"Gross hourly: ${gross_hourly:.2f}")
        print(f"Net hourly: ${net_hourly:.2f}")

        return {
            'deliveries_per_driver': deliveries_per_driver,
            'stacking_factor': stacking_factor,
            'gross_hourly_earnings': gross_hourly,
            'net_hourly_earnings': net_hourly,
            'peak_pay_multiplier': peak_pay_multiplier,
            'deadtime_impact': deadtime_data['total_deadtime_minutes']
        }

    def cleanup(self):
        """Clean up resources"""
        pass

# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("DELIVERY DRIVER EARNINGS FORECAST")
    print("=" * 60)

    forecaster = DeliveryEarningsForecaster()

    # Example: Dinner rush on Friday
    target_date = "2025-10-24"  # Friday
    target_hour = 18  # 6 PM dinner rush
    service = "doordash"
    neighborhood = "Mission District"

    # Run forecast
    events_data = forecaster.scrape_events(target_date, target_hour)
    weather_multiplier = forecaster.scrape_weather(target_date)
    restaurant_density = forecaster.scrape_restaurant_density('San Francisco', neighborhood)
    pricing_data = forecaster.scrape_delivery_pricing(service)

    # Calculate demand and supply
    demand = forecaster.estimate_demand(events_data, weather_multiplier, target_hour, restaurant_density)
    supply = forecaster.estimate_driver_supply(target_hour)

    # Calculate deadtime
    demand_supply_ratio = demand / supply if supply > 0 else 0
    deadtime_data = forecaster.calculate_deadtime(target_hour, demand_supply_ratio)

    # Calculate earnings
    earnings_per_delivery = forecaster.estimate_delivery_earnings(pricing_data, target_hour, service, neighborhood)
    costs = forecaster.estimate_costs(GAS_PRICE_PER_GALLON)
    results = forecaster.calculate_net_earnings(demand, supply, earnings_per_delivery, costs, target_hour, deadtime_data)

    print("\n" + "=" * 60)
    print("FORECAST RESULTS")
    print("=" * 60)
    print(f"Service: {service.title()}")
    print(f"Location: {neighborhood}")
    print(f"Time: {target_hour}:00 (Dinner Rush)")
    print(f"Demand: {demand:.0f} orders/hour")
    print(f"Active Drivers: {supply:.0f}")
    print(f"Deliveries per Driver: {results['deliveries_per_driver']:.2f}")
    print(f"Stacking Factor: {results['stacking_factor']:.2f}x")
    print(f"Gross Hourly: ${results['gross_hourly_earnings']:.2f}")
    print(f"Costs: ${costs:.2f}")
    print(f"NET HOURLY EARNINGS: ${results['net_hourly_earnings']:.2f}")
    print("=" * 60)

    forecaster.cleanup()
