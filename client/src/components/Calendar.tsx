import React, { useState } from 'react';
import { GigOpportunity, BookedShift } from '../App';

interface CalendarProps {
  onSlotClick: (day: string, hour: string, recommendations: GigOpportunity[]) => void;
  bookedShifts: Map<string, BookedShift>;
  selectedSlotKey: string | null;
  currentWeek: Date;
  onWeekChange: (newWeek: Date) => void;
  onDeleteShift: (shiftKey: string) => void;
  weeklyEarnings: { min: number; max: number };
}

const Calendar: React.FC<CalendarProps> = ({ 
  onSlotClick, 
  bookedShifts, 
  selectedSlotKey, 
  currentWeek, 
  onWeekChange, 
  onDeleteShift,
  weeklyEarnings 
}) => {
  const [loading, setLoading] = useState(false);

  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const hours = Array.from({ length: 18 }, (_, i) => i + 6); // 6 AM to 11 PM

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
      const response = await fetch(`http://localhost:5001/api/recommendations/${day.toLowerCase()}/${hour}`);
      const data = await response.json();
      onSlotClick(day, hour.toString(), data.recommendations);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      // Fallback mock data
      const mockRecommendations: GigOpportunity[] = [
        { service: 'Uber', startTime: `${hour}:00 AM`, endTime: `${hour + 1}:00 AM`, projectedEarnings: '$25 - $35', color: '#4285F4' },
        { service: 'Lyft', startTime: `${hour}:00 AM`, endTime: `${hour + 1}:00 AM`, projectedEarnings: '$22 - $32', color: '#4285F4' },
        { service: 'DoorDash', startTime: `${hour}:00 AM`, endTime: `${hour + 1}:00 AM`, projectedEarnings: '$18 - $28', color: '#FFD700' }
      ];
      onSlotClick(day, hour.toString(), mockRecommendations);
    } finally {
      setLoading(false);
    }
  };

  const getBookedShift = (day: string, hour: number): BookedShift | null => {
    const entries = Array.from(bookedShifts.entries());
    for (let i = 0; i < entries.length; i++) {
      const [key, shift] = entries[i];
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
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 px-4 py-2">
            <div className="text-sm text-gray-500">Projected Weekly Earnings</div>
            <div className="text-lg font-bold text-uber-blue">
              ${weeklyEarnings.min} – ${weeklyEarnings.max}
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
