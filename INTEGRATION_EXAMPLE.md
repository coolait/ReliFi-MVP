# Integration Example

This document provides a quick example of how the scraper integration works end-to-end.

## Example Flow

### 1. User Changes Location

**User Action:** User types "New York" in the location input and clicks a quick-select button.

**Frontend (LocationInput.tsx):**
```typescript
const handleLocationChange = (newLocation: string) => {
  onLocationChange(newLocation); // Triggers parent state update
};
```


**App State (App.tsx):**
```typescript
const handleLocationChange = async (newLocation: string) => {
  setIsLocationLoading(true);
  setLocation(newLocation);  // Updates location state
  // Clear selected slot
  setSelectedSlot(null);
  setSelectedSlotKey(null);
};
```

**Calendar Effect (Calendar.tsx):**
```typescript
useEffect(() => {
  console.log('📍 Location changed to:', location);
  setEarningsCache(new Map()); // Clear cache for new location
}, [location]);
```

### 2. User Clicks a Time Slot

**User Action:** User clicks on Monday 6 AM slot in the calendar.

**Calendar Component (Calendar.tsx):**
```typescript
const handleSlotClick = async (day: string, hour: number) => {
  // Generate cache key
  const cacheKey = `${location}-${day}-${hour}`;
  // Example: "New York-Monday-6"

  // Check cache
  if (earningsCache.has(cacheKey)) {
    // Use cached data
    return;
  }

  // Format time for API
  const startTime = "6:00 AM";
  const endTime = "7:00 AM";
  const dateStr = "2025-10-28"; // Calculated from current week

  // Call Express API
  const url = `http://localhost:5001/api/earnings?location=New%20York&date=2025-10-28&startTime=6:00%20AM&endTime=7:00%20AM`;
  const response = await fetch(url);
  const data = await response.json();

  // Transform and cache
  const recommendations = data.predictions.map(pred => ({
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

  // Store in cache
  setEarningsCache(prev => {
    const newCache = new Map(prev);
    newCache.set(cacheKey, recommendations);
    return newCache;
  });
};
```

### 3. Express Server Proxies Request

**Express Server (server/index.js):**
```javascript
app.get('/api/earnings', async (req, res) => {
  try {
    const { location, date, startTime, endTime, service } = req.query;

    // Forward to Python API
    const response = await axios.get(
      'http://localhost:5002/api/earnings',
      { params: { location, date, startTime, endTime, service } }
    );

    res.json(response.data);
  } catch (error) {
    console.error('Error calling Python API:', error);
    // Return fallback mock data
    res.json({
      location: req.query.location,
      predictions: [/* mock data */],
      fallback: true
    });
  }
});
```

### 4. Python API Calculates Earnings

**Python Flask API (scrapper/api_server.py):**
```python
@app.route('/api/earnings', methods=['GET'])
def get_earnings():
    location = request.args.get('location', 'San Francisco')
    date_str = request.args.get('date')
    start_time = request.args.get('startTime', '9:00 AM')

    # Parse hour
    target_hour = parse_time_to_hour(start_time)  # 6

    # Check cache
    cached_data = get_cached_earnings(location, date_str, target_hour)
    if cached_data:
        return jsonify(cached_data)

    # Get forecaster
    fc = get_forecaster()

    # Run scraping and calculations
    events_data = fc.scrape_events(date_str, target_hour)
    weather_multiplier = fc.scrape_weather(date_str)
    traffic_data = fc.scrape_traffic()
    pricing_data = fc.scrape_uber_pricing()
    gas_data = fc.scrape_gas_prices()

    # Calculate demand and supply
    demand = fc.estimate_demand(events_data, weather_multiplier, target_hour)
    supply = fc.estimate_driver_supply(target_hour)

    # Calculate earnings
    earnings_per_trip = fc.estimate_trip_earnings(pricing_data, traffic_data, target_hour)
    costs = fc.estimate_costs(gas_data, traffic_data)
    results = fc.calculate_net_earnings(demand, supply, earnings_per_trip, costs, target_hour)

    # Build response
    predictions = [
        {
            'service': 'Uber',
            'min': results['net_hourly_earnings'] - 5,
            'max': results['net_hourly_earnings'] + 5,
            'hotspot': 'Downtown Core',
            'demandScore': 0.85,
            'tripsPerHour': results['trips_per_driver'],
            'surgeMultiplier': results['surge_multiplier']
        }
    ]

    response_data = {
        'location': location,
        'date': date_str,
        'predictions': predictions
    }

    # Cache and return
    cache_earnings(location, date_str, target_hour, response_data)
    return jsonify(response_data)
```

### 5. Scraper Calculates Earnings

**Earnings Forecaster (scrapper/scrape.py):**
```python
# Scrape events (SF FunCheap, Eventbrite)
events_data = scrape_events("2025-10-28", 6)
# Result: {'events_found': 3, 'demand_multiplier': 1.15}

# Scrape weather
weather_multiplier = scrape_weather("2025-10-28")
# Result: 1.1 (winter boost)

# Scrape traffic
traffic_data = scrape_traffic()
# Result: {'congestion_level': 0.5, 'avg_speed_mph': 25}

# Scrape Uber pricing
pricing_data = scrape_uber_pricing()
# Result: {'base_fare': 2.55, 'cost_per_mile': 1.35, ...}

# Scrape gas prices
gas_data = scrape_gas_prices()
# Result: {'price_per_gallon': 5.25}

# Calculate demand
demand = estimate_demand(events_data, weather_multiplier, 6)
# Formula: BASE_DEMAND * events_multiplier * time_factor * weather
# Result: 12000 * 1.15 * 0.65 * 1.1 = 9,801 trips/hour

# Calculate supply
supply = estimate_driver_supply(6)
# Formula: BASE_DRIVERS * supply_factor
# Result: 3500 * 0.60 = 2,100 active drivers

# Calculate earnings per trip
earnings_per_trip = estimate_trip_earnings(pricing_data, traffic_data, 6)
# Formula: base + (distance * cost_per_mile) + (duration * cost_per_minute)
# Result: $12.50 per trip

# Calculate costs
costs = estimate_costs(gas_data, traffic_data)
# Formula: gas + wear_tear + insurance
# Result: $8.50 per hour

# Calculate net earnings
results = calculate_net_earnings(demand, supply, earnings_per_trip, costs, 6)
# trips_per_driver = 9801 / 2100 = 4.67 trips/hour
# But limited by deadtime: 60 min / (18 min trip + 19 min deadtime) = 1.62 trips/hour
# gross = 1.62 * $12.50 = $20.25
# net = $20.25 - $8.50 = $11.75
```

### 6. Frontend Displays Results

**Side Panel (SidePanel.tsx):**
```typescript
// Received data from API
const opportunity = {
  service: 'Uber',
  startTime: '6:00 AM',
  endTime: '7:00 AM',
  projectedEarnings: '$25 - $35',
  min: 25,
  max: 35,
  hotspot: 'Downtown Core',
  demandScore: 0.85,
  tripsPerHour: 2.3,
  surgeMultiplier: 1.1
};

// Rendered UI
return (
  <div>
    <div className="text-lg font-bold">$25 - $35</div>
    <div className="text-sm">Downtown Core</div>
    <div className="progress-bar" style={{ width: '85%' }} />
    <div>Est. Trips/Hour: 2.3</div>
    <div className="surge-badge">1.1x Surge Pricing</div>
  </div>
);
```

## Data Flow Diagram

```
┌──────────────┐
│   User       │
│   Changes    │
│   Location   │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  LocationInput.tsx   │
│  onLocationChange()  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  App.tsx             │
│  setLocation("NYC")  │
│  Clear cache         │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Calendar.tsx        │
│  useEffect clears    │
│  earnings cache      │
└──────────────────────┘

       │ User clicks slot
       ▼
┌──────────────────────┐
│  handleSlotClick()   │
│  Check cache: MISS   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  fetch()             │
│  GET /api/earnings   │
│  ?location=NYC       │
│  &date=2025-10-28    │
│  &startTime=6:00 AM  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Express Server      │
│  Port 5001           │
│  Proxy to Python     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Python Flask API    │
│  Port 5002           │
│  Check cache: MISS   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  UberEarnings        │
│  Forecaster          │
│  • Scrape events     │
│  • Scrape weather    │
│  • Scrape traffic    │
│  • Scrape pricing    │
│  • Calculate demand  │
│  • Calculate supply  │
│  • Calculate earnings│
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Response:           │
│  {                   │
│    predictions: [    │
│      {               │
│        service: 'Uber'│
│        min: 25       │
│        max: 35       │
│        hotspot: '...'│
│        demandScore..│
│      }               │
│    ]                 │
│  }                   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Cache in Python     │
│  TTL: 1 hour         │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Return to Express   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Return to Frontend  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Calendar.tsx        │
│  Cache result        │
│  Call onSlotClick()  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  SidePanel.tsx       │
│  Display:            │
│  • Earnings range    │
│  • Hotspot location  │
│  • Demand bar        │
│  • Trips/hour        │
│  • Surge indicator   │
└──────────────────────┘
```

## Example API Responses

### Successful Response

```json
{
  "location": "New York",
  "date": "2025-10-28",
  "timeSlot": "6:00 AM - 7:00 AM",
  "hour": 6,
  "predictions": [
    {
      "service": "Uber",
      "min": 28.50,
      "max": 38.75,
      "hotspot": "Financial District",
      "demandScore": 0.92,
      "tripsPerHour": 2.8,
      "surgeMultiplier": 1.3,
      "color": "#4285F4",
      "startTime": "6:00 AM",
      "endTime": "7:00 AM"
    },
    {
      "service": "Lyft",
      "min": 26.20,
      "max": 36.45,
      "hotspot": "Financial District",
      "demandScore": 0.88,
      "tripsPerHour": 2.6,
      "surgeMultiplier": 1.2,
      "color": "#FF00BF",
      "startTime": "6:00 AM",
      "endTime": "7:00 AM"
    },
    {
      "service": "DoorDash",
      "min": 20.00,
      "max": 28.50,
      "hotspot": "Restaurant Districts",
      "demandScore": 0.75,
      "tripsPerHour": 3.5,
      "surgeMultiplier": 1.0,
      "color": "#FFD700",
      "startTime": "6:00 AM",
      "endTime": "7:00 AM"
    }
  ],
  "metadata": {
    "demandEstimate": 14500,
    "driverSupply": 2800,
    "demandSupplyRatio": 5.18,
    "trafficLevel": 0.65,
    "weekday": "monday"
  }
}
```

### Fallback Response (Python API Unavailable)

```json
{
  "location": "New York",
  "date": "2025-10-28",
  "timeSlot": "6:00 AM - 7:00 AM",
  "hour": 6,
  "predictions": [
    {
      "service": "Uber",
      "min": 25,
      "max": 35,
      "hotspot": "Downtown Core",
      "demandScore": 0.75,
      "tripsPerHour": 2.3,
      "surgeMultiplier": 1.0,
      "color": "#4285F4",
      "startTime": "6:00 AM",
      "endTime": "7:00 AM"
    },
    {
      "service": "Lyft",
      "min": 22,
      "max": 32,
      "hotspot": "Downtown Core",
      "demandScore": 0.72,
      "tripsPerHour": 2.1,
      "surgeMultiplier": 1.0,
      "color": "#FF00BF",
      "startTime": "6:00 AM",
      "endTime": "7:00 AM"
    }
  ],
  "fallback": true
}
```

## Caching Behavior

### First Request (Cache Miss)

```
User clicks Monday 6 AM (NYC)
  └─> Calendar checks cache: "New York-Monday-6" → NOT FOUND
      └─> Fetch from API (takes 3-5 seconds)
          └─> Python scrapes data
              └─> Response cached in Python (1 hour)
                  └─> Response cached in React state
                      └─> Display data
```

### Second Request (Cache Hit - Same Slot)

```
User clicks Monday 6 AM again (NYC)
  └─> Calendar checks cache: "New York-Monday-6" → FOUND
      └─> Display data immediately (< 1ms)
```

### Third Request (Cache Hit - Python Cache)

```
Different user clicks Monday 6 AM (NYC)
  └─> Calendar checks cache: "New York-Monday-6" → NOT FOUND (different session)
      └─> Fetch from API
          └─> Python checks cache: "New York_2025-10-28_6" → FOUND
              └─> Return cached data (< 50ms)
                  └─> Cache in React state
                      └─> Display data
```

### Cache Invalidation

```
User changes location to "Los Angeles"
  └─> useEffect triggers in Calendar.tsx
      └─> Clear entire React cache
          └─> Next click requires fresh API call
```

## Performance Metrics

### API Response Times

| Scenario | Expected Time | Notes |
|----------|---------------|-------|
| Cache hit (React) | < 1ms | Instant from memory |
| Cache hit (Python) | 50-100ms | Network + Python lookup |
| Cache miss | 3-10 seconds | Full scraping required |
| Fallback (API down) | 100-200ms | Mock data from Express |

### Optimization Tips

1. **Pre-warm cache on page load:**
   ```typescript
   useEffect(() => {
     // Fetch data for current hour on load
     const currentHour = new Date().getHours();
     handleSlotClick('Monday', currentHour);
   }, []);
   ```

2. **Batch requests for visible slots:**
   ```typescript
   const preloadVisibleSlots = async () => {
     const visibleHours = [6, 7, 8, 9, 10]; // Morning hours
     const promises = visibleHours.map(hour =>
       fetch(`/api/earnings?location=${location}&hour=${hour}`)
     );
     await Promise.all(promises);
   };
   ```

3. **Use service worker for offline support:**
   ```javascript
   // Cache API responses for offline access
   self.addEventListener('fetch', (event) => {
     if (event.request.url.includes('/api/earnings')) {
       event.respondWith(
         caches.match(event.request).then(response => {
           return response || fetch(event.request);
         })
       );
     }
   });
   ```

## Testing the Integration

### 1. Test Location Change

```javascript
// Open browser console
// Type a location
document.querySelector('input[type="text"]').value = 'Chicago';
// Submit
document.querySelector('form').dispatchEvent(new Event('submit'));
// Check console for:
// "📍 Location changed to: Chicago"
```

### 2. Test API Call

```javascript
// Click a time slot
// Check console for:
// "💰 Fetching earnings: {location: 'Chicago', date: '2025-10-28', ...}"
// "📡 Response status: 200"
// "✅ Earnings data received: {...}"
```

### 3. Test Cache

```javascript
// Click same slot twice
// First time: "💰 Fetching earnings..."
// Second time: "📦 Using cached earnings data for Chicago-Monday-6"
```

### 4. Test Fallback

```javascript
// Stop Python API
// Click a slot
// Check console for:
// "❌ Error fetching earnings: ..."
// "🔄 Using fallback mock data for hour: 6"
// Verify mock data is displayed
```

## Common Issues and Solutions

### Issue: "CORS error when calling API"

**Solution:** Ensure Flask has CORS enabled:
```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

### Issue: "Cache never invalidates"

**Solution:** Check useEffect dependency:
```typescript
useEffect(() => {
  setEarningsCache(new Map());
}, [location]);  // ← Must include location
```

### Issue: "Earnings show $0 - $0"

**Solution:** Check scraper calculations:
```python
# Add debug logging
print(f"Net earnings: {results['net_hourly_earnings']}")
# Ensure not negative
net_hourly = max(0, results['net_hourly_earnings'])
```

This example demonstrates the complete integration flow from user interaction to data display!
