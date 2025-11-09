import React, { useState, useEffect } from 'react';
import { GigOpportunity, BookedShift } from '../App';
import { API_BASE_URL } from '../config/api';
import { LocationState } from './LocationInput';

interface CalendarProps {
  onSlotClick: (day: string, hour: string, recommendations: GigOpportunity[]) => void;
  bookedShifts: Map<string, BookedShift>;
  selectedSlotKey: string | null;
  currentWeek: Date;
  onWeekChange: (newWeek: Date) => void;
  onDeleteShift: (shiftKey: string) => void;
  weeklyEarnings: { min: number; max: number };
  location: LocationState;
  gcalBusySlotKeys: Set<string>;
  onImportGcal: () => Promise<void> | void;
}

const Calendar: React.FC<CalendarProps> = ({
  onSlotClick,
  bookedShifts,
  selectedSlotKey,
  currentWeek,
  onWeekChange,
  onDeleteShift,
  weeklyEarnings,
  location,
  gcalBusySlotKeys,
  onImportGcal
}) => {
  const [loading, setLoading] = useState(false);
  const [weeklyLoading, setWeeklyLoading] = useState(false);
  const [earningsCache, setEarningsCache] = useState<Map<string, GigOpportunity[]>>(new Map());
  const [weeklyCache, setWeeklyCache] = useState<Map<string, Map<string, Map<number, GigOpportunity[]>>>>(new Map()); // weekKey -> day -> hour -> recommendations

  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const hours = Array.from({ length: 18 }, (_, i) => i + 6); // 6 AM to 11 PM

  // Map a raw service name to one of the two categories
  const mapServiceToCategory = (service: string): 'Rideshare' | 'Food Delivery' => {
    const s = service.toLowerCase();
    // Rideshare services
    if (s.includes('uber') && !s.includes('eats') && !s.includes('uber eats')) return 'Rideshare';
    if (s.includes('lyft')) return 'Rideshare';
    if (s.includes('rideshare')) return 'Rideshare';
    // Food Delivery services
    if (s.includes('doordash') || s.includes('door dash')) return 'Food Delivery';
    if (s.includes('ubereats') || s.includes('uber eats')) return 'Food Delivery';
    if (s.includes('grubhub') || s.includes('grub hub')) return 'Food Delivery';
    if (s.includes('food delivery') || s.includes('delivery')) return 'Food Delivery';
    // Default to Food Delivery if unknown
    return 'Food Delivery';
  };

  // Aggregate multiple predictions into the two categories
  const aggregateToCategories = (predictions: any[], hour: number): GigOpportunity[] => {
    type Acc = {
      count: number;
      minSum: number;
      maxSum: number;
      color: string;
    };
    const acc: Record<'Rideshare' | 'Food Delivery', Acc> = {
      'Rideshare': { count: 0, minSum: 0, maxSum: 0, color: '#4285F4' },
      'Food Delivery': { count: 0, minSum: 0, maxSum: 0, color: '#FFD700' }
    };

    for (let i = 0; i < predictions.length; i++) {
      const p = predictions[i];
      const category = mapServiceToCategory(p.service || '');
      const minVal = typeof p.min === 'number' ? p.min : parseInt((p.min || '0').toString());
      const maxVal = typeof p.max === 'number' ? p.max : parseInt((p.max || '0').toString());
      acc[category].count += 1;
      acc[category].minSum += isNaN(minVal) ? 0 : minVal;
      acc[category].maxSum += isNaN(maxVal) ? 0 : maxVal;
    }

    const formatTime = (h: number) => {
      if (h === 0) return '12:00 AM';
      if (h < 12) return `${h}:00 AM`;
      if (h === 12) return '12:00 PM';
      return `${h - 12}:00 PM`;
    };

    const startTime = formatTime(hour);
    const endTime = formatTime(hour + 1);

    const results: GigOpportunity[] = [];
    (['Rideshare', 'Food Delivery'] as const).forEach((cat) => {
      if (acc[cat].count > 0) {
        const avgMin = Math.round(acc[cat].minSum / acc[cat].count);
        const avgMax = Math.round(acc[cat].maxSum / acc[cat].count);
        results.push({
          service: cat,
          startTime,
          endTime,
          projectedEarnings: `$${avgMin} - $${avgMax}`,
          color: acc[cat].color,
          min: avgMin,
          max: avgMax,
          hotspot: predictions[0]?.hotspot,
          demandScore: predictions[0]?.demandScore,
          tripsPerHour: predictions[0]?.tripsPerHour,
          surgeMultiplier: predictions[0]?.surgeMultiplier
        } as any);
      }
    });

    // If a category had no entries, still include a placeholder with $0 - $0? We'll omit to avoid clutter
    return results;
  };

  // Generate week cache key
  const getWeekCacheKey = (weekDate: Date): string => {
    const startOfWeek = new Date(weekDate);
    startOfWeek.setDate(weekDate.getDate() - weekDate.getDay());
    return `${location.coordinates ? `${location.coordinates.lat.toFixed(4)},${location.coordinates.lng.toFixed(4)}` : location.cityName}-${startOfWeek.toISOString().split('T')[0]}`;
  };

  // Clear caches when location changes
  useEffect(() => {
    console.log('📍 Location changed to:', location);
    setEarningsCache(new Map());
    setWeeklyCache(new Map());
  }, [location]);

  // DISABLED: Automatic weekly data fetching on page load
  // This was causing the scraper to run for ALL slots (7 days × 18 hours = 126 requests!)
  // Now data is only fetched when user clicks on a specific slot
  //
  // If you want to re-enable automatic weekly fetching, uncomment the code below:
  /*
  useEffect(() => {
    const fetchWeeklyData = async () => {
      const weekKey = getWeekCacheKey(currentWeek);
      
      // Check if we already have this week's data
      if (weeklyCache.has(weekKey)) {
        console.log('📦 Using cached weekly data for', weekKey);
        return;
      }

      setWeeklyLoading(true);
      console.log('📅 Fetching weekly earnings data for week:', currentWeek.toLocaleDateString());

      try {
        const startOfWeek = new Date(currentWeek);
        startOfWeek.setDate(currentWeek.getDate() - currentWeek.getDay());
        const startDateStr = startOfWeek.toISOString().split('T')[0];

        // Build URL
        let url = `${API_BASE_URL}/api/earnings/week?`;
        if (location.coordinates) {
          url += `lat=${location.coordinates.lat}&lng=${location.coordinates.lng}&`;
        } else {
          url += `location=${encodeURIComponent(location.cityName)}&`;
        }
        url += `startDate=${startDateStr}`;

        console.log('📡 Calling weekly API:', url);

        const response = await fetch(url, {
          signal: AbortSignal.timeout(120000) // 2 minute timeout for weekly data
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('✅ Weekly data received:', data);

        // Process and cache weekly data
        const weekDataMap = new Map<string, Map<number, GigOpportunity[]>>();
        
        if (data.weekData) {
          // Process the week data structure from API
          const dayNameMap: { [key: string]: string } = {
            'sunday': 'Sunday',
            'monday': 'Monday',
            'tuesday': 'Tuesday',
            'wednesday': 'Wednesday',
            'thursday': 'Thursday',
            'friday': 'Friday',
            'saturday': 'Saturday'
          };
          
          Object.keys(data.weekData).forEach((dayNameLower) => {
            const dayName = dayNameMap[dayNameLower] || dayNameLower.charAt(0).toUpperCase() + dayNameLower.slice(1);
            const dayData = data.weekData[dayNameLower];
            const hourMap = new Map<number, GigOpportunity[]>();
            
            Object.keys(dayData).forEach((hourStr) => {
              const hour = parseInt(hourStr);
              const predictions = dayData[hourStr];
              if (Array.isArray(predictions)) {
                const recommendations = aggregateToCategories(predictions, hour);
                hourMap.set(hour, recommendations);
              }
            });
            
            weekDataMap.set(dayName, hourMap);
          });
        }

        // Cache the weekly data
        setWeeklyCache(prev => {
          const newCache = new Map(prev);
          newCache.set(weekKey, weekDataMap);
          return newCache;
        });

        console.log('✅ Weekly data cached for', weekKey);
      } catch (error: any) {
        console.error('❌ Error fetching weekly data:', error);
      } finally {
        setWeeklyLoading(false);
      }
    };

    fetchWeeklyData();
  }, [currentWeek, location]);
  */

  const getWeekDates = (date: Date) => {
    const startOfWeek = new Date(date);
    startOfWeek.setDate(date.getDate() - date.getDay());
    return Array.from({ length: 7 }, (_, i) => {
      const day = new Date(startOfWeek);
      day.setDate(startOfWeek.getDate() + i);
      return day;
    });
  };

  const weekDates = getWeekDates(currentWeek);

  const handleSlotClick = async (day: string, hour: number) => {
    setLoading(true);
    try {
      // Get the exact date for the clicked slot
      const dayIndex = days.indexOf(day);
      const slotDate = weekDates[dayIndex];
      const dateStr = slotDate.toISOString().split('T')[0];
      const locationKey = location.coordinates
        ? `${location.coordinates.lat.toFixed(4)},${location.coordinates.lng.toFixed(4)}`
        : location.cityName;
      const cacheKey = `${locationKey}-${dateStr}-${day}-${hour}`;

      // Check individual cache first (faster, but only for previously clicked slots)
      if (earningsCache.has(cacheKey)) {
        console.log('📦 Using cached earnings data for', cacheKey);
        onSlotClick(day, hour.toString(), earningsCache.get(cacheKey)!);
        setLoading(false);
        return;
      }

      // Fetch from API with the SPECIFIC date and time the user clicked
      // This ensures we scrape events for the exact date/time, not pre-fetched data
      console.log(`🔍 User clicked ${day} (${dateStr}) at ${hour}:00 - fetching earnings from API`);
      
      // Build API URL with specific date and time
      const formatHour = (h: number) => {
        if (h === 0) return '12:00 AM';
        if (h < 12) return `${h}:00 AM`;
        if (h === 12) return '12:00 PM';
        return `${h - 12}:00 PM`;
      };
      
      let apiUrl = `${API_BASE_URL}/api/earnings?`;
      if (location.coordinates) {
        apiUrl += `lat=${location.coordinates.lat}&lng=${location.coordinates.lng}&`;
      } else {
        apiUrl += `location=${encodeURIComponent(location.cityName)}&`;
      }
      apiUrl += `date=${dateStr}&startTime=${encodeURIComponent(formatHour(hour))}&endTime=${encodeURIComponent(formatHour(hour + 1))}`;
      
      console.log('📡 Calling API for specific slot:', apiUrl);
      
      const response = await fetch(apiUrl, {
        signal: AbortSignal.timeout(60000) // 1 minute timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Received API response:', data);
      
      // Convert API response to our format
      const predictions = data.predictions || [];
      const recommendations = aggregateToCategories(predictions, hour);
      
      // Cache the results
      setEarningsCache(prev => {
        const newCache = new Map(prev);
        newCache.set(cacheKey, recommendations);
        return newCache;
      });
      
      onSlotClick(day, hour.toString(), recommendations);
    } catch (error: any) {
      console.error('❌ Error in handleSlotClick:', error);
      // Fallback to basic estimates
      const hourMultiplier = hour >= 17 && hour <= 20 ? 1.3 : hour >= 11 && hour <= 14 ? 1.2 : 1.0;
      const dayMultiplier = ['Friday', 'Saturday'].includes(day) ? 1.2 : 1.0;
      const baseMultiplier = hourMultiplier * dayMultiplier;
      
      const baseUber = Math.round(20 * baseMultiplier);
      const baseLyft = Math.round(18 * baseMultiplier);
      const baseDoorDash = Math.round(15 * baseMultiplier);

      const mockPreds = [
        { 
          service: 'Uber', 
          min: baseUber, 
          max: Math.round(baseUber * 1.4), 
          color: '#4285F4', 
          hotspot: 'Downtown Core', 
          demandScore: Math.min(0.95, 0.6 + (hour % 12) * 0.03) 
        },
        { 
          service: 'Lyft', 
          min: baseLyft, 
          max: Math.round(baseLyft * 1.4), 
          color: '#FF00BF', 
          hotspot: 'Downtown Core', 
          demandScore: Math.min(0.92, 0.58 + (hour % 12) * 0.03) 
        },
        { 
          service: 'DoorDash', 
          min: baseDoorDash, 
          max: Math.round(baseDoorDash * 1.5), 
          color: '#FFD700', 
          hotspot: 'Restaurant Districts', 
          demandScore: Math.min(0.90, 0.55 + (hour % 12) * 0.03) 
        }
      ];
      const mockRecommendations = aggregateToCategories(mockPreds as any, hour);
      onSlotClick(day, hour.toString(), mockRecommendations);
    } finally {
      setLoading(false);
    }
  };

  const getBookedShift = (day: string, hour: number): BookedShift | null => {
    const entries = Array.from(bookedShifts.entries());
    for (let i = 0; i < entries.length; i++) {
      const [, shift] = entries[i];
      if (shift.day === day && shift.hour === hour.toString()) {
        return shift;
      }
    }
    return null;
  };

  const getShiftKey = (day: string, hour: number): string | null => {
    const entries = Array.from(bookedShifts.entries());
    for (let i = 0; i < entries.length; i++) {
      const [key, shift] = entries[i];
      if (shift.day === day && shift.hour === hour.toString()) {
        return key;
      }
    }
    return null;
  };

  const formatHour = (hour: number) => {
    if (hour === 0) return '12 AM';
    if (hour < 12) return `${hour} AM`;
    if (hour === 12) return '12 PM';
    return `${hour - 12} PM`;
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const handleWeekNavigation = (direction: 'prev' | 'next') => {
    const newWeek = new Date(currentWeek);
    if (direction === 'prev') {
      newWeek.setDate(currentWeek.getDate() - 7);
    } else {
      newWeek.setDate(currentWeek.getDate() + 7);
    }
    onWeekChange(newWeek);
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-gray-900">Weekly Shift Recommendations</h1>
          <div className="flex items-center space-x-4">
            <button
              onClick={onImportGcal}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-700 transition-colors"
            >
              📅 Import Gcal
            </button>
            <button
              onClick={async () => {
                try {
                  const testUrl = `${API_BASE_URL}/api/health`;
                  console.log('🧪 Testing API:', testUrl);
                  const response = await fetch(testUrl);
                  if (!response.ok) throw new Error(`Status ${response.status}`);
                  const data = await response.json();
                  console.log('✅ API Health Result:', data);
                  alert(`API Health: ${data.status}`);
                } catch (error) {
                  console.error('❌ API Test Failed:', error);
                  alert('API Test Failed - Check console for details');
                }
              }}
              className="bg-green-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-600 transition-colors"
            >
              🧪 Test API
            </button>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 px-4 py-2">
              <div className="text-sm text-gray-500">Projected Weekly Earnings</div>
              <div className="text-lg font-bold text-uber-blue">
                ${weeklyEarnings.min} – ${weeklyEarnings.max}
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center justify-center space-x-4">
          <button
            onClick={() => handleWeekNavigation('prev')}
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span className="text-lg font-medium text-gray-700">
            {weekDates[0].toLocaleDateString('en-US', { month: 'long', day: 'numeric' })} - {weekDates[6].toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
          </span>
          <button
            onClick={() => handleWeekNavigation('next')}
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="grid grid-cols-8">
          {/* Time column header */}
          <div className="bg-gray-50 border-r border-gray-200 p-4"></div>
          
          {/* Day headers */}
          {weekDates.map((date, index) => (
            <div key={index} className="bg-gray-50 border-r border-gray-200 p-4 text-center">
              <div className="text-sm font-medium text-gray-900">{days[index].substring(0, 3)}</div>
              <div className="text-xs text-gray-500">{formatDate(date)}</div>
            </div>
          ))}

          {/* Time slots */}
          {hours.map((hour) => (
            <React.Fragment key={hour}>
              {/* Time label */}
              <div className="bg-gray-50 border-r border-gray-200 border-t border-gray-200 p-2 text-center">
                <span className="text-xs text-gray-600">{formatHour(hour)}</span>
              </div>
              
              {/* Day slots */}
              {weekDates.map((date, dayIndex) => {
                const dayName = days[dayIndex];
                const slotKey = `${dayName}-${hour}`;
                const isSelected = selectedSlotKey === slotKey;
                const bookedShift = getBookedShift(dayName, hour);
                const shiftKey = getShiftKey(dayName, hour);
                const isGcalBusy = gcalBusySlotKeys.has(slotKey);
                
                // Debug logging (only log once per render)
                if (dayIndex === 0 && hour === 6 && gcalBusySlotKeys.size > 0) {
                  console.log('📅 Checking GCal busy slots:', {
                    totalBusySlots: gcalBusySlotKeys.size,
                    exampleSlotKeys: Array.from(gcalBusySlotKeys).slice(0, 5),
                    currentSlotKey: slotKey,
                    isGcalBusy: isGcalBusy
                  });
                }
                
                return (
                  <div
                    key={`${dayIndex}-${hour}`}
                    className={`border-r border-gray-200 border-t border-gray-200 h-12 cursor-pointer transition-colors relative ${
                      isGcalBusy
                        ? 'bg-gray-400 hover:bg-gray-500' 
                        : bookedShift 
                          ? 'bg-green-100 hover:bg-green-200' 
                          : isSelected 
                            ? 'bg-blue-100 hover:bg-blue-200' 
                            : 'bg-white hover:bg-blue-50'
                    }`}
                    onClick={() => handleSlotClick(dayName, hour)}
                  >
                    {loading && (
                      <div className="flex items-center justify-center h-full">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-uber-blue"></div>
                      </div>
                    )}
                    
                    {!isGcalBusy && bookedShift && !loading && (
                      <div className="h-full flex flex-col justify-center p-1">
                        <div className="text-xs font-medium text-gray-900 truncate">
                          {bookedShift.service}
                        </div>
                        <div className="text-xs text-gray-600 truncate">
                          {bookedShift.earnings}
                        </div>
                        {shiftKey && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onDeleteShift(shiftKey);
                            }}
                            className="absolute top-0 right-0 w-4 h-4 bg-red-500 text-white text-xs rounded-full hover:bg-red-600 flex items-center justify-center"
                          >
                            ×
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Calendar;
