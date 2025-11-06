# Gig Economy Earnings Forecast Configuration
# Supports both rideshare (Uber/Lyft) and delivery (DoorDash/Uber Eats/GrubHub)
# Modify these values to customize your forecast

# Target forecast parameters
TARGET_DATE = "2025-10-23"
TARGET_START = "17:00"
TARGET_END = "18:00"
LOCATION = "San Francisco"

# ========================================
# RIDESHARE CONFIGURATION (Uber/Lyft)
# ========================================

# Market assumptions (realistic 2024 San Francisco data)
BASE_DEMAND_SF = 12000  # Base trips per hour in SF (peak hours can reach 15k+)
BASE_DRIVERS_SF = 3500  # Base active drivers in SF (more realistic for 2024)
AVG_TRIP_DISTANCE_MILES = 4.2  # Average trip distance (SF is dense but trips are longer)
AVG_TRIP_DURATION_MINUTES = 18  # Average trip duration (SF traffic increases time)
AVG_MPG = 22  # Average miles per gallon (city driving, SF hills)
WEAR_TEAR_PER_MILE = 0.35  # Wear and tear cost per mile (higher in SF, includes depreciation)

# Uber pricing (SF rates - realistic 2024 levels)
UBER_BASE_FARE = 2.20
UBER_COST_PER_MINUTE = 0.22
UBER_COST_PER_MILE = 1.15
UBER_BOOKING_FEE = 2.40
UBER_MINIMUM_FARE = 5.20

# Gas prices (SF average - updated for 2024)
GAS_PRICE_PER_GALLON = 5.25

# Time factors for demand (refined based on SF patterns)
DEMAND_TIME_FACTORS = {
    0: 0.35,  1: 0.30,  2: 0.25,  3: 0.25,  4: 0.30,  5: 0.45,
    6: 0.65,  7: 0.90,  8: 1.10,  9: 0.85, 10: 0.75, 11: 0.85,
    12: 0.95, 13: 0.85, 14: 0.70, 15: 0.85, 16: 1.15, 17: 1.35,
    18: 1.50, 19: 1.25, 20: 1.00, 21: 0.85, 22: 0.70, 23: 0.50
}

# Time-of-day driver-supply multipliers (refined for SF driver patterns)
SUPPLY_TIME_FACTORS = {
    0: 0.35,  1: 0.30,  2: 0.25,  3: 0.25,  4: 0.30,  5: 0.45,
    6: 0.60,  7: 0.80,  8: 0.95,  9: 0.90, 10: 0.85, 11: 0.85,
    12: 0.90, 13: 0.85, 14: 0.75, 15: 0.85, 16: 0.95, 17: 1.05,
    18: 1.10, 19: 0.95, 20: 0.85, 21: 0.75, 22: 0.60, 23: 0.45
}

# Deadtime configuration - refined based on real driver data
DEADTIME_CONFIG = {
    # Average time spent waiting for next ride request (minutes)
    'avg_wait_time_minutes': 12,  # Increased based on driver reports
    
    # Average time spent driving to pickup location (minutes)
    'avg_pickup_time_minutes': 7,  # SF traffic and distance increases pickup time
    
    # Time-of-day factors for deadtime (higher during low demand periods)
    'deadtime_factors': {
        0: 1.8,  1: 2.0,  2: 2.2,  3: 2.2,  4: 1.8,  5: 1.4,
        6: 1.2,  7: 1.0,  8: 0.8,  9: 0.8, 10: 0.8, 11: 0.8,
        12: 0.8, 13: 0.8, 14: 0.9, 15: 0.8, 16: 0.8, 17: 0.7,
        18: 0.7, 19: 0.8, 20: 0.9, 21: 1.1, 22: 1.4, 23: 1.6
    },
    
    # Additional deadtime during peak hours due to traffic
    'traffic_deadtime_multiplier': 1.3,  # SF traffic is significant
    
    # Minimum deadtime between trips (minutes)
    'min_deadtime_minutes': 5,  # More realistic minimum
    
    # Maximum deadtime between trips (minutes)
    'max_deadtime_minutes': 25  # Increased for low-demand periods
}

# ========================================
# DELIVERY CONFIGURATION (DoorDash/Uber Eats/GrubHub)
# ========================================

# Delivery market assumptions (SF data)
BASE_DELIVERY_DEMAND_SF = 8000  # Base orders per hour during peak meal times
BASE_DELIVERY_DRIVERS_SF = 2500  # Active delivery drivers
AVG_DELIVERY_DISTANCE_MILES = 2.5  # Much shorter than rideshare (dense restaurant areas)
AVG_DELIVERY_DURATION_MINUTES = 10  # Faster turnaround
DELIVERY_MPG = 25  # Slightly better (shorter trips, less stop-and-go)

# DoorDash pricing (2024 estimates)
DOORDASH_BASE_PAY_MIN = 2.00  # Minimum base pay per delivery
DOORDASH_BASE_PAY_MAX = 10.00  # Maximum base pay (long distance/complex orders)
DOORDASH_PER_MILE = 0.60  # Per mile component
DOORDASH_AVG_TIP_LOW = 3.00  # Low-tipping customers
DOORDASH_AVG_TIP_HIGH = 6.00  # Good-tipping customers
DOORDASH_AVG_TIP = 4.50  # Average tip
DOORDASH_PEAK_PAY_MAX = 5.00  # Maximum peak pay bonus

# Uber Eats pricing (2024 estimates)
UBEREATS_BASE_FARE = 3.00  # Base delivery fee
UBEREATS_PICKUP_FEE = 2.00  # Restaurant pickup component
UBEREATS_DROPOFF_FEE = 1.50  # Customer dropoff component
UBEREATS_PER_MILE = 0.60  # Per mile rate
UBEREATS_PER_MINUTE = 0.10  # Per minute rate
UBEREATS_AVG_TIP = 4.00  # Average tip
UBEREATS_TRIP_SUPPLEMENT_MAX = 8.00  # Distance/demand bonus

# GrubHub pricing (2024 estimates)
GRUBHUB_BASE_PAY = 3.50  # Guaranteed base per order
GRUBHUB_PER_MILE = 0.50  # Per mile component
GRUBHUB_PER_MINUTE = 0.13  # Per minute component
GRUBHUB_AVG_TIP = 5.00  # Average tip (higher than competitors)
GRUBHUB_BLOCK_BONUS = 1.10  # 10% bonus for scheduling blocks
GRUBHUB_CONTRIBUTION_PAY_MAX = 10.00  # Makes up difference if order is low

# Delivery time factors (meal-time centric, different from rideshare)
DELIVERY_DEMAND_TIME_FACTORS = {
    0: 0.10,  1: 0.05,  2: 0.05,  3: 0.05,  4: 0.05,  5: 0.10,  # Dead hours
    6: 0.20,  7: 0.40,  8: 0.50,  9: 0.40, 10: 0.60,  # Morning pickup
    11: 0.90, 12: 1.50, 13: 1.30, 14: 0.80, 15: 0.50,  # Lunch rush
    16: 0.60, 17: 1.00, 18: 1.50, 19: 1.40, 20: 1.20,  # Dinner rush
    21: 0.80, 22: 0.40, 23: 0.20  # Late night
}

# Delivery driver supply factors (more evening/weekend drivers)
DELIVERY_SUPPLY_TIME_FACTORS = {
    0: 0.25,  1: 0.20,  2: 0.15,  3: 0.15,  4: 0.20,  5: 0.30,
    6: 0.40,  7: 0.55,  8: 0.65,  9: 0.60, 10: 0.65, 11: 0.75,
    12: 0.85, 13: 0.80, 14: 0.65, 15: 0.70, 16: 0.80, 17: 0.90,
    18: 1.00, 19: 0.95, 20: 0.90, 21: 0.75, 22: 0.50, 23: 0.35
}

# Delivery deadtime configuration (includes restaurant wait)
DELIVERY_DEADTIME_CONFIG = {
    # Time waiting for order assignment (minutes)
    'avg_wait_time_minutes': 6,  # Shorter than rideshare in busy areas

    # Time driving to restaurant (minutes)
    'avg_pickup_time_minutes': 4,  # Shorter distances

    # Time waiting at restaurant for food (minutes) - CRITICAL for delivery
    'restaurant_wait_minutes': 5,  # Can vary 2-10 minutes

    # Time-of-day factors for deadtime
    'deadtime_factors': {
        0: 2.0,  1: 2.5,  2: 2.5,  3: 2.5,  4: 2.0,  5: 1.5,
        6: 1.3,  7: 1.1,  8: 1.0,  9: 0.9, 10: 0.8, 11: 0.7,  # Morning pickup
        12: 0.5, 13: 0.6, 14: 1.0, 15: 1.2, 16: 0.9, 17: 0.6,  # Lunch/dinner rushes
        18: 0.5, 19: 0.6, 20: 0.7, 21: 0.9, 22: 1.3, 23: 1.7   # Late night slowdown
    },

    # Minimum deadtime between deliveries (minutes)
    'min_deadtime_minutes': 3,

    # Maximum deadtime between deliveries (minutes)
    'max_deadtime_minutes': 15
}

# Restaurant density multipliers by area (affects order volume)
RESTAURANT_DENSITY = {
    'Downtown Core': 2.5,
    'Financial District': 2.0,
    'Mission District': 2.8,
    'Chinatown': 3.0,
    'North Beach': 2.6,
    'Marina': 1.5,
    'Richmond': 1.8,
    'Sunset': 1.6,
    'SoMa': 2.2,
    'Castro': 2.1
}

# Tipping patterns by neighborhood (multiplier on base tip)
TIP_MULTIPLIERS = {
    'Pacific Heights': 1.5,
    'Nob Hill': 1.4,
    'Russian Hill': 1.4,
    'Financial District': 1.3,
    'Marina': 1.3,
    'Castro': 1.1,
    'Mission District': 1.0,
    'Haight-Ashbury': 0.9,
    'Tenderloin': 0.7,
    'Bayview': 0.8
}

# Stacked orders configuration (multiple deliveries at once)
STACKED_ORDERS_CONFIG = {
    'min_demand_ratio': 1.5,  # Need high demand to get stacked orders
    'max_stack_size': 2,  # Usually 2 orders, occasionally 3
    'efficiency_multiplier': 1.3,  # 30% more deliveries per hour when stacking
    'per_order_time_reduction': 0.7  # Each additional order takes 70% of normal time
}