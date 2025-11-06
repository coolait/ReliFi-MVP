# Delivery Services in the UI

## Current Status

Your UI **should already be showing delivery services** (DoorDash, Uber Eats, GrubHub) because:

1. The API returns all 5 services by default (`service=all`)
2. The SidePanel.tsx displays whatever services the API returns
3. The backend properly separates delivery from rideshare calculations

## Expected UI Display

When you click a time slot, the side panel should show predictions for **5 services**:

### Rideshare Services
- **Uber** (Blue, #4285F4)
- **Lyft** (Pink, #FF00BF)

### Delivery Services
- **DoorDash** (Gold, #FFD700)
- **UberEats** (Green, #06C167)
- **GrubHub** (Orange, #FF8000)

## Visual Comparison

### 6 PM Time Slot Example

```
┌─────────────────────────────────────────────┐
│ Projected Earnings: 6:00 PM - 7:00 PM     │
├─────────────────────────────────────────────┤
│                                             │
│ 💼 Uber                          $40 - $50  │
│    📍 Restaurant Districts                  │
│    Demand: ████████░░ 85%                   │
│    Trips/hour: 2.7                          │
│    ⭐ 1.15x Surge Pricing                   │
│                                             │
│ 💼 Lyft                          $37 - $46  │
│    📍 Restaurant Districts                  │
│    Demand: ███████░░░ 81%                   │
│    Trips/hour: 2.4                          │
│    ⭐ 1.09x Surge Pricing                   │
│                                             │
│ 🍔 DoorDash                      $37 - $49  │
│    📍 Restaurant Districts                  │
│    Demand: ████████░░ 85%                   │
│    Trips/hour: 3.8                          │
│    💰 1.20x Peak Pay                        │
│                                             │
│ 🍔 UberEats                      $35 - $47  │
│    📍 Restaurant Districts                  │
│    Demand: ███████░░░ 81%                   │
│    Trips/hour: 3.6                          │
│    💰 1.20x Peak Pay                        │
│                                             │
│ 🍔 GrubHub                       $37 - $49  │
│    📍 Restaurant Districts                  │
│    Demand: ████████░░ 85%                   │
│    Trips/hour: 3.8                          │
│                                             │
└─────────────────────────────────────────────┘
```

## Key Differences: Rideshare vs Delivery

| Feature | Rideshare (Uber/Lyft) | Delivery (DoorDash/UberEats/GrubHub) |
|---------|----------------------|--------------------------------------|
| **Peak Hours** | 7-8 AM, 5-6 PM (commutes) | 12-1 PM, 6-7 PM (meals) |
| **Hotspots** | Financial District, Downtown | Restaurant Districts |
| **Trips/Hour** | 1.5 - 2.5 | 2.5 - 4.0 |
| **Distance** | 4.2 miles avg | 2.5 miles avg |
| **Duration** | 18 minutes avg | 10 minutes avg |
| **Tips** | 10% of income | 30-40% of income |
| **Peak Pay** | Surge pricing (1.0-2.0x) | Peak pay ($1-5 bonus) |

## How to Verify Delivery Services Are Showing

### 1. Check API Response

Open browser DevTools (F12) → Network tab → Click a time slot

Look for the `/api/earnings` request response:

```json
{
  "predictions": [
    {"service": "Uber", ...},
    {"service": "Lyft", ...},
    {"service": "DoorDash", ...},     // ← Should be here
    {"service": "UberEats", ...},     // ← Should be here
    {"service": "GrubHub", ...}       // ← Should be here
  ]
}
```

### 2. Check SidePanel Display

The SidePanel should map over all predictions:

```typescript
{earnings.map((opportunity, index) => (
  <div key={index}>
    <h4>{opportunity.service}</h4>
    <p>${opportunity.min} - ${opportunity.max}</p>
  </div>
))}
```

This should render 5 service cards (2 rideshare + 3 delivery).

### 3. Visual Check

You should see:
- 2 services with blue/pink colors (Uber/Lyft)
- 3 services with gold/green/orange colors (DoorDash/UberEats/GrubHub)

## If Delivery Services Are NOT Showing

### Possible Issues

1. **API not returning delivery services**
   - Check API response in DevTools Network tab
   - Verify Python API is running (`python3 api_server.py`)
   - Test endpoint directly: `curl "http://localhost:5002/api/earnings?startTime=6:00%20PM"`

2. **Frontend filtering delivery services**
   - Check if there's any filtering logic in Calendar.tsx or SidePanel.tsx
   - Look for code like `filter(opp => opp.service === 'Uber' || opp.service === 'Lyft')`

3. **Wrong endpoint being called**
   - Verify frontend calls `/api/earnings` (not old mock endpoint)
   - Check Calendar.tsx uses correct API endpoint

4. **Caching old data**
   - Clear browser cache
   - Restart all services (Python API, Express, React)

### Debug Steps

```bash
# 1. Test Python API directly
curl "http://localhost:5002/api/earnings?location=San%20Francisco&startTime=6:00%20PM&endTime=7:00%20PM"

# Expected: Should return 5 services in predictions array

# 2. Test Express API
curl "http://localhost:5001/api/earnings?location=San%20Francisco&startTime=6:00%20PM&endTime=7:00%20PM"

# Expected: Should proxy Python API response with 5 services

# 3. Check React is calling correct endpoint
# Open DevTools → Console → Look for fetch/axios calls
# Should see: fetch('/api/earnings?...')
```

## Delivery vs Rideshare Earnings Patterns

### Lunch Rush (12-1 PM)

- **Rideshare**: $25-35/hour (moderate demand)
- **Delivery**: $30-40/hour (HIGH demand - lunch orders)

### Dinner Rush (6-7 PM)

- **Rideshare**: $40-50/hour (high demand - commute overlap)
- **Delivery**: $37-49/hour (HIGH demand - dinner orders)

### Late Night (11 PM - 2 AM)

- **Rideshare**: $25-35/hour (bar/nightlife demand)
- **Delivery**: $15-25/hour (low demand - few restaurants open)

### Early Morning (6-8 AM)

- **Rideshare**: $30-40/hour (commute demand)
- **Delivery**: $12-22/hour (low demand - breakfast is smaller market)

## Color Coding

Make sure your UI uses these colors to differentiate services:

```typescript
const serviceColors = {
  'Uber': '#4285F4',      // Uber blue
  'Lyft': '#FF00BF',      // Lyft pink
  'DoorDash': '#FFD700',  // DoorDash gold
  'UberEats': '#06C167',  // Uber Eats green
  'GrubHub': '#FF8000'    // GrubHub orange
};
```

These are returned in the API response in the `color` field.

## Testing Delivery Display

### Test Case 1: Dinner Rush (High Delivery)

```bash
curl "http://localhost:5001/api/earnings?location=San%20Francisco&startTime=6:00%20PM"
```

Expected:
- DoorDash: $37-49
- Uber Eats: $35-47
- GrubHub: $37-49
- **Higher than typical afternoon hours**

### Test Case 2: Morning Commute (High Rideshare)

```bash
curl "http://localhost:5001/api/earnings?location=San%20Francisco&startTime=8:00%20AM"
```

Expected:
- Uber: $35-45
- Lyft: $32-42
- DoorDash: $12-22 (LOW - breakfast is weak)

### Test Case 3: Late Night (Low Delivery)

```bash
curl "http://localhost:5001/api/earnings?location=San%20Francisco&startTime=11:00%20PM"
```

Expected:
- Uber: $25-35 (nightlife)
- Lyft: $22-32
- DoorDash: $15-25 (LOW - few restaurants)

## Summary

✅ **Delivery services SHOULD already be showing** in your UI

✅ The API returns all 5 services by default

✅ Each service has proper calculations:
   - Rideshare: Commute-based demand
   - Delivery: Meal-based demand

✅ Visual differentiation by color

If delivery services are NOT showing, follow the debug steps above to identify the issue.

## Quick Verification Command

Run this to see all 5 services in JSON format:

```bash
curl -s "http://localhost:5001/api/earnings?startTime=6:00%20PM" | python3 -m json.tool | grep -A 2 '"service"'
```

Expected output:
```
"service": "Uber",
--
"service": "Lyft",
--
"service": "DoorDash",
--
"service": "UberEats",
--
"service": "GrubHub",
```

If you see all 5, the API is working correctly and the issue is in the frontend display.
