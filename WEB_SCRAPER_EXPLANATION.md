# Web Scraper Explanation

## Overview

The web scraper (`web_events_scraper.py`) scrapes Eventbrite's public event discovery pages to find events happening on a specific date in a specific location. It then uses the number of events found to calculate a demand multiplier for earnings predictions.

## How It Works

### 1. **Location Normalization** 
   - **Input**: Location string (e.g., "San Francisco" or coordinates like "37.7749, -122.4194")
   - **Process**: 
     - If coordinates are provided, geocodes them to a city name using Nominatim API or a fast local lookup
     - Extracts state code if present (e.g., "San Francisco, CA" → "CA")
     - Normalizes to Eventbrite's format: `state--city` (e.g., "ca--san-francisco")
   - **Output**: Normalized location string like "San Francisco, CA"

### 2. **URL Construction**
   - **Format**: `https://www.eventbrite.com/d/{state}--{city}/all-events/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
   - **Example**: `https://www.eventbrite.com/d/ca--san-francisco/all-events/?start_date=2025-11-08&end_date=2025-11-08`
   - **Why**: This matches Eventbrite's date picker URL format, which filters events by the selected date

### 3. **Pagination**
   - Scrapes up to **3 pages** of Eventbrite results
   - Each page typically shows 20-25 events
   - Uses URL parameters: `?page=2`, `?page=3`, etc.
   - **Rate limiting**: Waits 2+ seconds between requests to respect Eventbrite's servers

### 4. **Event Extraction**
   For each page, it:
   - **Parses HTML** using BeautifulSoup
   - **Finds event links** matching pattern: `/e/event-name-tickets-{id}`
   - **Extracts event IDs** from URLs (10+ digit numbers)
   - **Deduplicates** events using event IDs (same event might appear multiple times)
   - **Extracts event titles** from link text or parent elements

### 5. **Date Extraction** (Most Important Part)
   Since Eventbrite renders dates with JavaScript, the scraper uses multiple methods:

   **Method 1: Fetch Individual Event Pages**
   - For each event found, fetches the individual event page
   - Looks for **JSON-LD structured data** (most reliable):
     ```json
     {
       "@type": "Event",
       "startDate": "2025-11-08T18:00:00-0800"
     }
     ```
   - Also looks for embedded JSON in `<script>` tags
   - Parses dates from meta tags

   **Method 2: Parse from HTML**
   - Looks for `<time>` elements with `datetime` attributes
   - Searches for date patterns in text (e.g., "November 8, 2025")
   - Tries multiple date formats (ISO 8601, US formats, etc.)

   **Method 3: Caching**
   - Caches extracted dates to avoid re-fetching the same event page
   - Significantly speeds up subsequent requests

### 6. **Date Filtering**
   - **Input**: List of events + target date (e.g., "2025-11-08")
   - **Process**:
     - For each event, extracts its date
     - Compares event date with target date
     - Only includes events where dates match
   - **Output**: Filtered list of events happening on the target date
   - **Fallback**: If dates can't be extracted, trusts Eventbrite's URL date filter

### 7. **Demand Multiplier Calculation**
   - **Input**: Number of events found on the target date
   - **Formula**: 
     ```python
     if events_found == 0:
         multiplier = 1.0  # No events, no demand boost
     elif events_found < 5:
         multiplier = 1.05  # Small boost for few events
     elif events_found < 10:
         multiplier = 1.15  # Moderate boost
     elif events_found < 20:
         multiplier = 1.3   # Good boost
     elif events_found < 50:
         multiplier = 1.5   # High boost
     else:
         multiplier = 1.7   # Very high boost for many events
     ```
   - **Output**: Demand multiplier (1.0 to 1.7) used to adjust earnings predictions

## Example Flow

### User clicks: Saturday, November 8, 12 PM

1. **Location**: "San Francisco" (or coordinates)
   - Normalized to: "San Francisco, CA"
   - URL format: `ca--san-francisco`

2. **Date**: "2025-11-08"
   - URL: `https://www.eventbrite.com/d/ca--san-francisco/all-events/?start_date=2025-11-08&end_date=2025-11-08`

3. **Scraping**:
   - Page 1: Finds 20 events
   - Page 2: Finds 20 events  
   - Page 3: Finds 19 events
   - Total: 59 events found

4. **Date Extraction**:
   - Fetches individual event pages for all 59 events
   - Extracts dates from JSON-LD or HTML
   - Finds 38 events actually happening on November 8, 2025

5. **Filtering**:
   - Filters to 38 events matching the target date
   - Removes 21 events happening on other dates

6. **Demand Multiplier**:
   - 38 events → multiplier = 1.5 (high boost)
   - This means earnings are estimated to be 1.5x higher due to event demand

7. **Result**:
   ```python
   {
     'events_found': 38,
     'demand_multiplier': 1.5,
     'source': 'eventbrite'
   }
   ```

## Features

### ✅ **Rate Limiting**
- Waits 2+ seconds between requests
- Prevents overwhelming Eventbrite's servers
- Respects their Terms of Service

### ✅ **Caching**
- Caches geocoding results (coordinates → city names)
- Caches event dates (avoid re-fetching same event)
- Caches scraping results (1 hour TTL)

### ✅ **Error Handling**
- Handles 404 errors gracefully
- Falls back to time-based estimates if scraping fails
- Logs warnings instead of crashing

### ✅ **Multiple Date Formats**
- Supports ISO 8601, US formats, European formats
- Handles timezones
- Parses dates from various HTML structures

### ✅ **Deduplication**
- Uses event IDs to avoid counting same event multiple times
- Tracks seen event IDs across pages

## Limitations

### ⚠️ **Terms of Service**
- Web scraping may violate Eventbrite's Terms of Service
- Should be used responsibly and with rate limiting
- Consider using Eventbrite's official API if available

### ⚠️ **JavaScript Rendering**
- Eventbrite uses React/JavaScript to render content
- Some dates may not be in initial HTML
- Requires fetching individual event pages (slower)

### ⚠️ **Rate Limits**
- Too many requests may get blocked
- Current rate limit: 2+ seconds between requests
- Scraping 3 pages + 59 event pages = ~2-3 minutes

### ⚠️ **Accuracy**
- Date extraction isn't 100% accurate
- Some events may be missed or incorrectly dated
- Falls back to time-based estimates if scraping fails

## Performance

- **Fast lookup**: ~2-3 seconds for cached results
- **First-time scraping**: ~60-120 seconds (3 pages + date extraction)
- **Cached scraping**: ~5-10 seconds (uses cached dates)

## Usage in Earnings Prediction

The scraper is used by `improved_data_scraper.py` to:
1. Get event count for a specific date/location
2. Calculate demand multiplier based on event count
3. Apply multiplier to base earnings estimates
4. Provide more accurate earnings predictions

**Example**:
- Base earnings: $25/hour
- Events found: 38
- Demand multiplier: 1.5
- Adjusted earnings: $25 × 1.5 = $37.50/hour

## Code Structure

```
WebEventsScraper
├── get_events()              # Main entry point
│   ├── _normalize_location() # Geocode coordinates → city name
│   ├── _scrape_eventbrite()  # Scrape Eventbrite pages
│   │   ├── Build URL with date filter
│   │   ├── Scrape pages 1-3
│   │   ├── Extract event links
│   │   └── Extract event titles
│   ├── _fetch_event_date()   # Fetch individual event pages
│   │   ├── Parse JSON-LD
│   │   ├── Parse embedded JSON
│   │   └── Parse HTML meta tags
│   ├── _filter_events_by_date() # Filter events by target date
│   └── _calculate_demand_multiplier() # Calculate multiplier
└── Caching & Rate Limiting
```

## Summary

The web scraper:
1. **Finds events** on Eventbrite for a specific date/location
2. **Extracts dates** from individual event pages
3. **Filters events** to only include those on the target date
4. **Calculates demand multiplier** based on event count
5. **Returns multiplier** to adjust earnings predictions

This allows the earnings prediction system to account for real-time event demand, making estimates more accurate when many events are happening (higher demand = higher earnings).

