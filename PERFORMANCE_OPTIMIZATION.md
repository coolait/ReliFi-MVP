# Performance Optimization Guide

## Problem

The current implementation is **slow** because:
1. Each time slot click scrapes 5-10 websites
2. Scraping takes 3-10 seconds per request
3. No pre-computation
4. Heavy calculations repeated for similar requests

## Solutions

### Solution 1: Pre-compute Daily Data (Recommended)
### Solution 2: Lightweight Fast Mode
### Solution 3: Batch Requests
### Solution 4: Better Caching Strategy

---

## Solution 1: Pre-compute Daily Data ⚡ (BEST)

**Concept:** Run scraper once per day in background, store results in database/JSON files.

### Implementation

**Step 1: Create Pre-computation Script**

Create `scrapper/precompute_daily.py`:

```python
#!/usr/bin/env python3
"""
Pre-compute earnings for entire day
Run once per day (e.g., 6 AM via cron job)
Stores results in JSON files for instant API responses
"""

import json
import datetime
from scrape import UberEarningsForecaster
from delivery_forecaster import DeliveryEarningsForecaster
from config import *

def precompute_day(location='San Francisco', date_str=None):
    """Pre-compute earnings for all hours of a day"""

    if not date_str:
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')

    print(f"Pre-computing earnings for {location} on {date_str}...")

    # Initialize forecasters
    rideshare_fc = UberEarningsForecaster()
    delivery_fc = DeliveryEarningsForecaster()

    results = {}

    # Scrape once, reuse for all hours
    print("Scraping shared data...")
    events_data = rideshare_fc.scrape_events(date_str, 12)  # Use noon as reference
    weather_multiplier = rideshare_fc.scrape_weather(date_str)
    traffic_data = rideshare_fc.scrape_traffic()
    pricing_data = rideshare_fc.scrape_uber_pricing()
    gas_data = rideshare_fc.scrape_gas_prices()

    delivery_events = delivery_fc.scrape_events(date_str, 12)
    delivery_weather = delivery_fc.scrape_weather(date_str)

    # Pre-compute for all hours (6 AM to 11 PM)
    for hour in range(6, 24):
        print(f"\nCalculating hour {hour}:00...")

        hour_results = {
            'hour': hour,
            'rideshare': {},
            'delivery': {}
        }

        # Rideshare calculations
        demand = rideshare_fc.estimate_demand(events_data, weather_multiplier, hour)
        supply = rideshare_fc.estimate_driver_supply(hour)
        demand_ratio = demand / supply if supply > 0 else 0
        deadtime = rideshare_fc.calculate_deadtime(hour, traffic_data, demand_ratio)
        earnings_per_trip = rideshare_fc.estimate_trip_earnings(pricing_data, traffic_data, hour)
        costs = rideshare_fc.estimate_costs(gas_data, traffic_data, deadtime)
        rideshare_results = rideshare_fc.calculate_net_earnings(
            demand, supply, earnings_per_trip, costs, hour, deadtime
        )

        hour_results['rideshare'] = {
            'net_earnings': rideshare_results['net_hourly_earnings'],
            'trips_per_hour': rideshare_results['trips_per_driver'],
            'surge': rideshare_results['surge_multiplier'],
            'demand_ratio': demand_ratio
        }

        # Delivery calculations
        restaurant_density = delivery_fc.scrape_restaurant_density(location)
        delivery_demand = delivery_fc.estimate_demand(delivery_events, delivery_weather, hour, restaurant_density)
        delivery_supply = delivery_fc.estimate_driver_supply(hour)
        delivery_ratio = delivery_demand / delivery_supply if delivery_supply > 0 else 0
        delivery_deadtime = delivery_fc.calculate_deadtime(hour, delivery_ratio)
        delivery_costs = delivery_fc.estimate_costs(gas_data['price_per_gallon'])

        # DoorDash
        dd_pricing = delivery_fc.scrape_delivery_pricing('doordash')
        dd_earnings = delivery_fc.estimate_delivery_earnings(dd_pricing, hour, 'doordash')
        dd_results = delivery_fc.calculate_net_earnings(
            delivery_demand, delivery_supply, dd_earnings, delivery_costs, hour, delivery_deadtime
        )

        hour_results['delivery']['doordash'] = {
            'net_earnings': dd_results['net_hourly_earnings'],
            'deliveries_per_hour': dd_results['deliveries_per_driver'],
            'peak_pay': dd_results.get('peak_pay_multiplier', 1.0),
            'demand_ratio': delivery_ratio
        }

        # UberEats
        ue_pricing = delivery_fc.scrape_delivery_pricing('ubereats')
        ue_earnings = delivery_fc.estimate_delivery_earnings(ue_pricing, hour, 'ubereats')
        ue_results = delivery_fc.calculate_net_earnings(
            delivery_demand, delivery_supply, ue_earnings, delivery_costs, hour, delivery_deadtime
        )

        hour_results['delivery']['ubereats'] = {
            'net_earnings': ue_results['net_hourly_earnings'],
            'deliveries_per_hour': ue_results['deliveries_per_driver'],
            'peak_pay': ue_results.get('peak_pay_multiplier', 1.0),
            'demand_ratio': delivery_ratio
        }

        # GrubHub
        gh_pricing = delivery_fc.scrape_delivery_pricing('grubhub')
        gh_earnings = delivery_fc.estimate_delivery_earnings(gh_pricing, hour, 'grubhub')
        gh_results = delivery_fc.calculate_net_earnings(
            delivery_demand, delivery_supply, gh_earnings, delivery_costs, hour, delivery_deadtime
        )

        hour_results['delivery']['grubhub'] = {
            'net_earnings': gh_results['net_hourly_earnings'],
            'deliveries_per_hour': gh_results['deliveries_per_driver'],
            'peak_pay': gh_results.get('peak_pay_multiplier', 1.0),
            'demand_ratio': delivery_ratio
        }

        results[str(hour)] = hour_results

    # Save to file
    filename = f"precomputed_{location.lower().replace(' ', '_')}_{date_str}.json"
    with open(filename, 'w') as f:
        json.dump({
            'location': location,
            'date': date_str,
            'computed_at': datetime.datetime.now().isoformat(),
            'hours': results
        }, f, indent=2)

    print(f"\n✅ Saved to {filename}")

    rideshare_fc.cleanup()
    delivery_fc.cleanup()

    return filename

if __name__ == "__main__":
    # Pre-compute for today
    precompute_day('San Francisco')

    # Optionally pre-compute for tomorrow
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    precompute_day('San Francisco', tomorrow)
```

**Step 2: Update API Server to Use Pre-computed Data**

Add to `scrapper/api_server.py`:

```python
import os
import glob

def load_precomputed_data(location, date_str):
    """Load pre-computed earnings data"""
    filename = f"precomputed_{location.lower().replace(' ', '_')}_{date_str}.json"

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)

    return None

@app.route('/api/earnings/fast', methods=['GET'])
def get_earnings_fast():
    """
    Fast endpoint using pre-computed data
    Falls back to real-time calculation if not available
    """
    try:
        location = request.args.get('location', 'San Francisco')
        date_str = request.args.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
        start_time = request.args.get('startTime', '9:00 AM')
        service_filter = request.args.get('service', 'all')

        target_hour = parse_time_to_hour(start_time)

        # Try to load pre-computed data
        precomputed = load_precomputed_data(location, date_str)

        if precomputed and str(target_hour) in precomputed['hours']:
            # Use pre-computed data (instant response!)
            hour_data = precomputed['hours'][str(target_hour)]
            predictions = []

            # Build predictions from pre-computed data
            if service_filter in ['all', 'Uber']:
                uber_earnings = hour_data['rideshare']['net_earnings']
                predictions.append({
                    'service': 'Uber',
                    'min': round(max(10, uber_earnings - 5), 2),
                    'max': round(uber_earnings + 5, 2),
                    'hotspot': 'Downtown Core',
                    'demandScore': min(1.0, hour_data['rideshare']['demand_ratio'] / 2.0),
                    'tripsPerHour': hour_data['rideshare']['trips_per_hour'],
                    'surgeMultiplier': hour_data['rideshare']['surge'],
                    'color': '#4285F4',
                    'startTime': format_hour_to_time(target_hour),
                    'endTime': format_hour_to_time(target_hour + 1)
                })

            if service_filter in ['all', 'Lyft']:
                uber_earnings = hour_data['rideshare']['net_earnings']
                lyft_earnings = uber_earnings * 0.92
                predictions.append({
                    'service': 'Lyft',
                    'min': round(max(10, lyft_earnings - 5), 2),
                    'max': round(lyft_earnings + 5, 2),
                    'hotspot': 'Downtown Core',
                    'demandScore': min(1.0, hour_data['rideshare']['demand_ratio'] / 2.0 * 0.95),
                    'tripsPerHour': round(hour_data['rideshare']['trips_per_hour'] * 0.9, 2),
                    'surgeMultiplier': round(hour_data['rideshare']['surge'] * 0.95, 2),
                    'color': '#FF00BF',
                    'startTime': format_hour_to_time(target_hour),
                    'endTime': format_hour_to_time(target_hour + 1)
                })

            if service_filter in ['all', 'DoorDash']:
                dd_data = hour_data['delivery']['doordash']
                predictions.append({
                    'service': 'DoorDash',
                    'min': round(max(12, dd_data['net_earnings'] - 6), 2),
                    'max': round(dd_data['net_earnings'] + 6, 2),
                    'hotspot': 'Restaurant Districts',
                    'demandScore': min(1.0, dd_data['demand_ratio'] / 2.0),
                    'tripsPerHour': dd_data['deliveries_per_hour'],
                    'surgeMultiplier': dd_data['peak_pay'],
                    'color': '#FFD700',
                    'startTime': format_hour_to_time(target_hour),
                    'endTime': format_hour_to_time(target_hour + 1)
                })

            if service_filter in ['all', 'UberEats']:
                ue_data = hour_data['delivery']['ubereats']
                predictions.append({
                    'service': 'UberEats',
                    'min': round(max(12, ue_data['net_earnings'] - 6), 2),
                    'max': round(ue_data['net_earnings'] + 6, 2),
                    'hotspot': 'Restaurant Districts',
                    'demandScore': min(1.0, ue_data['demand_ratio'] / 2.0 * 0.95),
                    'tripsPerHour': round(ue_data['deliveries_per_hour'] * 0.95, 2),
                    'surgeMultiplier': ue_data['peak_pay'],
                    'color': '#06C167',
                    'startTime': format_hour_to_time(target_hour),
                    'endTime': format_hour_to_time(target_hour + 1)
                })

            if service_filter in ['all', 'GrubHub']:
                gh_data = hour_data['delivery']['grubhub']
                predictions.append({
                    'service': 'GrubHub',
                    'min': round(max(12, gh_data['net_earnings'] - 6), 2),
                    'max': round(gh_data['net_earnings'] + 6, 2),
                    'hotspot': 'Restaurant Districts',
                    'demandScore': min(1.0, gh_data['demand_ratio'] / 2.0),
                    'tripsPerHour': gh_data['deliveries_per_hour'],
                    'surgeMultiplier': 1.0,
                    'color': '#FF8000',
                    'startTime': format_hour_to_time(target_hour),
                    'endTime': format_hour_to_time(target_hour + 1)
                })

            return jsonify({
                'location': location,
                'date': date_str,
                'timeSlot': f"{format_hour_to_time(target_hour)} - {format_hour_to_time(target_hour + 1)}",
                'hour': target_hour,
                'predictions': predictions,
                'precomputed': True,
                'computed_at': precomputed['computed_at']
            })

        # Fall back to real-time calculation
        return get_earnings()

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Step 3: Set Up Cron Job**

```bash
# Add to crontab (crontab -e)
0 6 * * * cd /path/to/scrapper && python3 precompute_daily.py >> precompute.log 2>&1
```

**Benefits:**
- ⚡ **Instant responses** (< 10ms vs 3-10 seconds)
- 💾 **Scrapes once per day** instead of on every request
- 📊 **Consistent data** across all users
- 🔄 **Auto-updates** daily via cron

---

## Solution 2: Lightweight Fast Mode

**Concept:** Skip scraping, use config defaults with minor variations.

Add to `scrapper/api_server.py`:

```python
@app.route('/api/earnings/lightweight', methods=['GET'])
def get_earnings_lightweight():
    """
    Ultra-fast endpoint using config defaults
    No scraping, instant response
    Good for UI preview/skeleton while real data loads
    """
    try:
        location = request.args.get('location', 'San Francisco')
        date_str = request.args.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
        start_time = request.args.get('startTime', '9:00 AM')
        service_filter = request.args.get('service', 'all')

        target_hour = parse_time_to_hour(start_time)

        # Use config-based calculations (no scraping!)
        rideshare_time_factor = DEMAND_TIME_FACTORS.get(target_hour, 0.5)
        delivery_time_factor = DELIVERY_DEMAND_TIME_FACTORS.get(target_hour, 0.5)

        # Quick rideshare estimate
        base_rideshare_earnings = 25  # Base hourly
        rideshare_earnings = base_rideshare_earnings * rideshare_time_factor * 1.2

        # Quick delivery estimate
        base_delivery_earnings = 22  # Base hourly
        delivery_earnings = base_delivery_earnings * delivery_time_factor * 1.3

        predictions = []

        if service_filter in ['all', 'Uber']:
            predictions.append({
                'service': 'Uber',
                'min': round(rideshare_earnings - 5, 2),
                'max': round(rideshare_earnings + 5, 2),
                'hotspot': 'Downtown Core',
                'demandScore': 0.75,
                'tripsPerHour': 2.5,
                'surgeMultiplier': 1.1 if rideshare_time_factor > 1.0 else 1.0,
                'color': '#4285F4',
                'startTime': format_hour_to_time(target_hour),
                'endTime': format_hour_to_time(target_hour + 1)
            })

        if service_filter in ['all', 'Lyft']:
            predictions.append({
                'service': 'Lyft',
                'min': round((rideshare_earnings - 5) * 0.92, 2),
                'max': round((rideshare_earnings + 5) * 0.92, 2),
                'hotspot': 'Downtown Core',
                'demandScore': 0.72,
                'tripsPerHour': 2.3,
                'surgeMultiplier': 1.05 if rideshare_time_factor > 1.0 else 1.0,
                'color': '#FF00BF',
                'startTime': format_hour_to_time(target_hour),
                'endTime': format_hour_to_time(target_hour + 1)
            })

        if service_filter in ['all', 'DoorDash']:
            predictions.append({
                'service': 'DoorDash',
                'min': round(delivery_earnings - 6, 2),
                'max': round(delivery_earnings + 6, 2),
                'hotspot': 'Restaurant Districts',
                'demandScore': 0.80,
                'tripsPerHour': 3.5,
                'surgeMultiplier': 1.2 if target_hour in [12, 13, 18, 19] else 1.0,
                'color': '#FFD700',
                'startTime': format_hour_to_time(target_hour),
                'endTime': format_hour_to_time(target_hour + 1)
            })

        if service_filter in ['all', 'UberEats']:
            predictions.append({
                'service': 'UberEats',
                'min': round((delivery_earnings - 6) * 0.95, 2),
                'max': round((delivery_earnings + 6) * 0.95, 2),
                'hotspot': 'Restaurant Districts',
                'demandScore': 0.76,
                'tripsPerHour': 3.3,
                'surgeMultiplier': 1.2 if target_hour in [12, 13, 18, 19] else 1.0,
                'color': '#06C167',
                'startTime': format_hour_to_time(target_hour),
                'endTime': format_hour_to_time(target_hour + 1)
            })

        if service_filter in ['all', 'GrubHub']:
            predictions.append({
                'service': 'GrubHub',
                'min': round(delivery_earnings - 6, 2),
                'max': round(delivery_earnings + 6, 2),
                'hotspot': 'Restaurant Districts',
                'demandScore': 0.80,
                'tripsPerHour': 3.5,
                'surgeMultiplier': 1.0,
                'color': '#FF8000',
                'startTime': format_hour_to_time(target_hour),
                'endTime': format_hour_to_time(target_hour + 1)
            })

        return jsonify({
            'location': location,
            'date': date_str,
            'timeSlot': f"{format_hour_to_time(target_hour)} - {format_hour_to_time(target_hour + 1)}",
            'hour': target_hour,
            'predictions': predictions,
            'lightweight': True
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Benefits:**
- ⚡ **< 50ms response time**
- 🎯 **Good enough** for UI preview
- 💨 **No external dependencies**

---

## Solution 3: Update Frontend to Use Fast Endpoint

Update `client/src/components/Calendar.tsx`:

```typescript
const handleSlotClick = async (day: string, hour: number) => {
  setLoading(true);
  try {
    // Check cache first
    const cacheKey = `${location}-${day}-${hour}`;
    if (earningsCache.has(cacheKey)) {
      console.log('📦 Using cached earnings data for', cacheKey);
      onSlotClick(day, hour.toString(), earningsCache.get(cacheKey)!);
      setLoading(false);
      return;
    }

    const formatTime = (h: number) => {
      if (h === 0) return '12:00 AM';
      if (h < 12) return `${h}:00 AM`;
      if (h === 12) return '12:00 PM';
      return `${h - 12}:00 PM`;
    };

    const startTime = formatTime(hour);
    const endTime = formatTime(hour + 1);
    const dayIndex = days.indexOf(day);
    const slotDate = weekDates[dayIndex];
    const dateStr = slotDate.toISOString().split('T')[0];

    // Try fast endpoint first (pre-computed data)
    const fastUrl = `${API_BASE_URL}/api/earnings/fast?location=${encodeURIComponent(location)}&date=${dateStr}&startTime=${encodeURIComponent(startTime)}&endTime=${encodeURIComponent(endTime)}`;
    console.log('⚡ Trying fast endpoint first...');

    const response = await fetch(fastUrl);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ Earnings data received:', data.precomputed ? '(pre-computed)' : '(real-time)');

    // Transform and cache...
    const recommendations: GigOpportunity[] = data.predictions.map((pred: any) => ({
      service: pred.service,
      startTime: pred.startTime,
      endTime: pred.endTime,
      projectedEarnings: `$${pred.min} - $${pred.max}`,
      color: pred.color,
      min: pred.min,
      max: pred.max,
      hotspot: pred.hotspot,
      demandScore: pred.demandScore,
      tripsPerHour: pred.tripsPerHour,
      surgeMultiplier: pred.surgeMultiplier
    }));

    setEarningsCache(prev => {
      const newCache = new Map(prev);
      newCache.set(cacheKey, recommendations);
      return newCache;
    });

    onSlotClick(day, hour.toString(), recommendations);
  } catch (error) {
    console.error('❌ Error fetching earnings:', error);
    // Fallback to mock data...
  } finally {
    setLoading(false);
  }
};
```

---

## Solution 4: Add Service Filter Toggle

Create `client/src/components/ServiceFilter.tsx`:

```typescript
import React from 'react';

interface ServiceFilterProps {
  selectedServices: string[];
  onServiceToggle: (service: string) => void;
}

const ServiceFilter: React.FC<ServiceFilterProps> = ({ selectedServices, onServiceToggle }) => {
  const services = [
    { name: 'Uber', color: '#4285F4', category: 'rideshare' },
    { name: 'Lyft', color: '#FF00BF', category: 'rideshare' },
    { name: 'DoorDash', color: '#FFD700', category: 'delivery' },
    { name: 'UberEats', color: '#06C167', category: 'delivery' },
    { name: 'GrubHub', color: '#FF8000', category: 'delivery' }
  ];

  return (
    <div className="service-filter mb-4">
      <div className="text-sm font-medium text-gray-700 mb-2">Show Services:</div>
      <div className="flex flex-wrap gap-2">
        {services.map(service => (
          <button
            key={service.name}
            onClick={() => onServiceToggle(service.name)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
              selectedServices.includes(service.name)
                ? 'text-white shadow-md'
                : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
            }`}
            style={{
              backgroundColor: selectedServices.includes(service.name) ? service.color : undefined
            }}
          >
            {service.name}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ServiceFilter;
```

Update `App.tsx` to manage service filter:

```typescript
const [selectedServices, setSelectedServices] = useState<string[]>([
  'Uber', 'Lyft', 'DoorDash', 'UberEats', 'GrubHub'  // All enabled by default
]);

const handleServiceToggle = (service: string) => {
  setSelectedServices(prev =>
    prev.includes(service)
      ? prev.filter(s => s !== service)
      : [...prev, service]
  );
};

// Pass to ShiftsPage
<ShiftsPage
  selectedServices={selectedServices}
  onServiceToggle={handleServiceToggle}
  // ... other props
/>
```

---

## Recommended Implementation Plan

### Phase 1: Immediate (Quick Wins)

1. **Use Lightweight Endpoint** (2 hours)
   - Add `/api/earnings/lightweight` endpoint
   - Update frontend to use it
   - **Result: < 50ms response time**

2. **Add Service Filter UI** (3 hours)
   - Create ServiceFilter component
   - Let users show/hide delivery vs rideshare
   - **Result: Better UX, less data to load**

### Phase 2: Short Term (Best Performance)

3. **Implement Pre-computation** (1 day)
   - Create `precompute_daily.py`
   - Add `/api/earnings/fast` endpoint
   - Set up cron job
   - **Result: < 10ms response time**

4. **Update Frontend** (2 hours)
   - Use fast endpoint
   - Show "Data as of [time]" indicator
   - **Result: Instant loading**

### Phase 3: Long Term (Production Ready)

5. **Add Redis** (1 day)
   - Replace in-memory cache with Redis
   - Share cache across servers
   - **Result: Scalable caching**

6. **Add Database** (2 days)
   - Store historical predictions
   - Show trends over time
   - **Result: Analytics features**

---

## Quick Start: Lightweight Mode (Do This Now)

**1. Run this command:**
```bash
cd scrapper
python3 -c "
from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

# Copy the lightweight endpoint code here
# (see Solution 2 above)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
"
```

**2. Update frontend to call port 5003 for fast mode**

**3. Response time:** < 50ms (vs 3-10 seconds)

---

## Performance Comparison

| Method | Response Time | Accuracy | Best For |
|--------|---------------|----------|----------|
| **Current (Full Scraping)** | 3-10 seconds | High | N/A (too slow) |
| **Lightweight Mode** | < 50ms | Medium | Quick preview |
| **Pre-computed Daily** | < 10ms | High | Production use |
| **Cached (1 hour TTL)** | 50-100ms | High | Second+ requests |

---

## Summary

**To show delivery services:**
- They should already show! Check the response includes DoorDash/UberEats/GrubHub

**To make it faster:**
1. **Quick fix:** Add lightweight endpoint (< 50ms)
2. **Best fix:** Pre-compute daily data (< 10ms)
3. **UI fix:** Add service filter to show/hide services

Want me to implement the lightweight mode or pre-computation script now?
