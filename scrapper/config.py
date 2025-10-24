# Uber Driver Earnings Forecast Configuration
# Modify these values to customize your forecast

# Target forecast parameters
TARGET_DATE = "2025-10-23"
TARGET_START = "17:00"
TARGET_END = "18:00"
LOCATION = "San Francisco"

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