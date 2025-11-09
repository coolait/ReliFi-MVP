# Fix: Individual Slot Date/Time Accuracy

## Issue

When a user clicks on a specific time slot (e.g., Saturday, November 8, 12-1 PM), the system was not using the exact date and time of that slot. Instead, it was relying on cached weekly data which might have been scraped with incorrect dates.

## Root Cause

1. **Frontend**: When a slot was clicked, it primarily used the weekly cache (`weeklyCache`) which was populated by the `/api/earnings/week` endpoint.
2. **Weekly Cache**: Even though the weekly endpoint correctly calculates dates for each day, if the cache was stale or from a previous request, it might contain data for the wrong dates.
3. **No Direct API Call**: The frontend wasn't directly calling the `/api/earnings` endpoint with the specific date and time when a slot was clicked.

## Solution

### 1. Frontend Changes (`client/src/components/Calendar.tsx`)

**Updated `handleSlotClick` to:**
- Extract the exact date from `weekDates[dayIndex]` for the clicked slot
- If the slot is not in the weekly cache, **directly call the `/api/earnings` endpoint** with:
  - The exact date (`dateStr` from `weekDates[dayIndex]`)
  - The exact hour (`hour`)
  - The location (coordinates or city name)

**Key Changes:**
```typescript
// Get the actual date for this specific slot
const dayIndex = days.indexOf(day);
const slotDate = weekDates[dayIndex];
const dateStr = slotDate.toISOString().split('T')[0];

// If not in cache, fetch from API with SPECIFIC date and time
let apiUrl = `${API_BASE_URL}/api/earnings?`;
apiUrl += `date=${dateStr}&startTime=${formatHour(hour)}&endTime=${formatHour(hour + 1)}`;
```

### 2. Backend Changes (`scrapper/api_server.py`)

**Updated `/api/earnings` endpoint to:**
- Add logging to show the exact date and time being processed
- Prioritize the `ImprovedEarningsScraper` which uses the exact date passed in the request
- Ensure the scraper receives and uses the correct `date_str` and `target_hour`

**Key Changes:**
```python
# Log the exact date and time being used
print(f"  📅 API request: date={date_str}, startTime={start_time}, endTime={end_time}, location={location}")
print(f"  ⏰ Parsed hour: {target_hour}:00")

# Use improved scraper with the EXACT date and time
all_estimates = scraper.get_all_estimates(location_str, date_str, target_hour, lat_val, lng_val)
```

## Flow

### Before Fix:
1. User clicks Saturday, Nov 8, 12 PM
2. Frontend checks weekly cache
3. If found, uses cached data (might be wrong date)
4. If not found, uses fallback mock data (wrong date)

### After Fix:
1. User clicks Saturday, Nov 8, 12 PM
2. Frontend checks weekly cache
3. If found and correct, uses cached data
4. **If not found, calls `/api/earnings?date=2025-11-08&startTime=12:00 PM&endTime=1:00 PM`**
5. Backend receives exact date (`2025-11-08`) and hour (`12`)
6. Backend calls scraper with exact date and hour
7. Scraper scrapes events for November 8, 2025
8. Scraper calculates earnings based on events for that specific date
9. Results are cached and returned to frontend

## Testing

To verify the fix:

1. **Clear cache** (or wait for cache to expire)
2. **Click on a specific time slot** (e.g., Saturday, November 8, 12 PM)
3. **Check browser console** - you should see:
   - `📅 Slot clicked: Saturday (2025-11-08) at 12:00`
   - `🔍 Fetching earnings for 2025-11-08 at 12:00 from API`
   - `📡 Calling API for specific slot: ...date=2025-11-08&startTime=12:00 PM...`

4. **Check API logs** - you should see:
   - `📅 API request: date=2025-11-08, startTime=12:00 PM, endTime=1:00 PM`
   - `⏰ Parsed hour: 12:00`
   - `🔍 Using improved scraper for ... on 2025-11-08 at 12:00`
   - `🔍 Fetching events data for ... on 2025-11-08...`
   - `🌐 Scraping Eventbrite: ...?start_date=2025-11-08&end_date=2025-11-08`

## Status

✅ **Fixed!**
- Frontend now calls API with exact date and time when slot is clicked
- Backend uses the exact date and time passed in the request
- Scraper scrapes events for the correct date
- Earnings are calculated based on events for that specific date and time

