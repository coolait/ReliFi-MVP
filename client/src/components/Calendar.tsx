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
}

const Calendar: React.FC<CalendarProps> = ({
  onSlotClick,
  bookedShifts,
  selectedSlotKey,
  currentWeek,
  onWeekChange,
  onDeleteShift,
  weeklyEarnings,
  location
}) => {
  const [loading, setLoading] = useState(false);
  const [earningsCache, setEarningsCache] = useState<Map<string, GigOpportunity[]>>(new Map());

  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const hours = Array.from({ length: 18 }, (_, i) => i + 6); // 6 AM to 11 PM

  // Clear cache when location changes
  useEffect(() => {
    console.log('📍 Location changed to:', location);
    setEarningsCache(new Map());
  }, [location]);

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
      // Generate cache key using coordinates if available
      const locationKey = location.coordinates
        ? `${location.coordinates.lat.toFixed(4)},${location.coordinates.lng.toFixed(4)}`
        : location.cityName;
      const cacheKey = `${locationKey}-${day}-${hour}`;

      // Check cache first
      if (earningsCache.has(cacheKey)) {
        console.log('📦 Using cached earnings data for', cacheKey);
        onSlotClick(day, hour.toString(), earningsCache.get(cacheKey)!);
        setLoading(false);
        return;
      }

      // Format time for API call
      const formatTime = (h: number) => {
        if (h === 0) return '12:00 AM';
        if (h < 12) return `${h}:00 AM`;
        if (h === 12) return '12:00 PM';
        return `${h - 12}:00 PM`;
      };

      const startTime = formatTime(hour);
      const endTime = formatTime(hour + 1);

      // Calculate the date for this specific day
      const dayIndex = days.indexOf(day);
      const slotDate = weekDates[dayIndex];
      const dateStr = slotDate.toISOString().split('T')[0];

      // Build base URL params
      const buildUrl = (endpoint: string) => {
        let url = `${API_BASE_URL}${endpoint}?`;
        if (location.coordinates) {
          url += `lat=${location.coordinates.lat}&lng=${location.coordinates.lng}&`;
        } else {
          url += `location=${encodeURIComponent(location.cityName)}&`;
        }
        url += `date=${dateStr}&startTime=${encodeURIComponent(startTime)}&endTime=${encodeURIComponent(endTime)}`;
        return url;
      };

      // TWO-PHASE LOADING: Fast preview → Accurate data

      // PHASE 1: Fetch lightweight data first (< 50ms)
      console.log('⚡ Phase 1: Fetching lightweight preview...');
      const lightweightUrl = buildUrl('/api/earnings/lightweight');

      try {
        const lightResponse = await fetch(lightweightUrl);
        if (lightResponse.ok) {
          const lightData = await lightResponse.json();
          const lightRecommendations: GigOpportunity[] = lightData.predictions.map((pred: any) => ({
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

          // Show lightweight data immediately
          onSlotClick(day, hour.toString(), lightRecommendations);
          setLoading(false);
          console.log('✅ Phase 1 complete: Showing lightweight preview');
        }
      } catch (err) {
        console.log('⚠️ Phase 1 failed, skipping to Phase 2');
      }

      // PHASE 2: Fetch full scraper data in background (3-10s)
      console.log('🔍 Phase 2: Fetching full scraper data...');
      const scraperUrl = buildUrl('/api/earnings');

      const response = await fetch(scraperUrl);
      console.log('📡 Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Phase 2 complete: Full scraper data received');

      // Transform the predictions into GigOpportunity format
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

      // Cache the full scraper results
      setEarningsCache(prev => {
        const newCache = new Map(prev);
        newCache.set(cacheKey, recommendations);
        return newCache;
      });

      // Update UI with accurate scraper data
      onSlotClick(day, hour.toString(), recommendations);
      console.log('🎯 Updated UI with accurate scraper predictions');
    } catch (error) {
      console.error('❌ Error fetching earnings:', error);
      console.log('🔄 Using fallback mock data for hour:', hour);

      // Fallback mock data with proper time formatting
      const formatTime = (h: number) => {
        if (h === 0) return '12:00 AM';
        if (h < 12) return `${h}:00 AM`;
        if (h === 12) return '12:00 PM';
        return `${h - 12}:00 PM`;
      };

      const mockRecommendations: GigOpportunity[] = [
        { service: 'Uber', startTime: formatTime(hour), endTime: formatTime(hour + 1), projectedEarnings: '$25 - $35', color: '#4285F4', min: 25, max: 35, hotspot: 'Downtown Core', demandScore: 0.75 },
        { service: 'Lyft', startTime: formatTime(hour), endTime: formatTime(hour + 1), projectedEarnings: '$22 - $32', color: '#FF00BF', min: 22, max: 32, hotspot: 'Downtown Core', demandScore: 0.72 },
        { service: 'DoorDash', startTime: formatTime(hour), endTime: formatTime(hour + 1), projectedEarnings: '$18 - $28', color: '#FFD700', min: 18, max: 28, hotspot: 'Restaurant Districts', demandScore: 0.70 }
      ];
      console.log('🎭 Mock recommendations:', mockRecommendations);
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
                
                return (
                  <div
                    key={`${dayIndex}-${hour}`}
                    className={`border-r border-gray-200 border-t border-gray-200 h-12 cursor-pointer transition-colors relative ${
                      bookedShift 
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
                    
                    {bookedShift && !loading && (
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
