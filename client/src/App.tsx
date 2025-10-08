import React, { useState } from 'react';
import Calendar from './components/Calendar';
import SidePanel from './components/SidePanel';
import Header from './components/Header';

export interface GigOpportunity {
  service: string;
  startTime: string;
  endTime: string;
  projectedEarnings: string;
  color: string;
}

export interface SelectedSlot {
  day: string;
  hour: string;
  recommendations: GigOpportunity[];
}

export interface BookedShift {
  day: string;
  hour: string;
  service: string;
  earnings: string;
  color: string;
}

function App() {
  const [selectedSlot, setSelectedSlot] = useState<SelectedSlot | null>(null);
  const [selectedSlotKey, setSelectedSlotKey] = useState<string | null>(null);
  const [bookedShiftsByWeek, setBookedShiftsByWeek] = useState<Map<string, Map<string, BookedShift>>>(new Map());
  const [currentWeek, setCurrentWeek] = useState(new Date());

  const getWeekKey = (date: Date): string => {
    const startOfWeek = new Date(date);
    startOfWeek.setDate(date.getDate() - date.getDay());
    return startOfWeek.toISOString().split('T')[0];
  };

  const getCurrentWeekShifts = (): Map<string, BookedShift> => {
    const weekKey = getWeekKey(currentWeek);
    return bookedShiftsByWeek.get(weekKey) || new Map();
  };

  const handleSlotClick = (day: string, hour: string, recommendations: GigOpportunity[]) => {
    const slotKey = `${day}-${hour}`;
    setSelectedSlot({ day, hour, recommendations });
    setSelectedSlotKey(slotKey);
  };

  const handleBookSlot = (day: string, hour: string, opportunity: GigOpportunity) => {
    const shiftKey = `${day}-${hour}-${opportunity.service}`;
    const shift: BookedShift = {
      day,
      hour,
      service: opportunity.service,
      earnings: opportunity.projectedEarnings,
      color: opportunity.color
    };
    
    const weekKey = getWeekKey(currentWeek);
    setBookedShiftsByWeek(prev => {
      const newMap = new Map(prev);
      const weekShifts = newMap.get(weekKey) || new Map();
      weekShifts.set(shiftKey, shift);
      newMap.set(weekKey, weekShifts);
      return newMap;
    });
  };

  const handleDeleteShift = (shiftKey: string) => {
    const weekKey = getWeekKey(currentWeek);
    setBookedShiftsByWeek(prev => {
      const newMap = new Map(prev);
      const weekShifts = newMap.get(weekKey);
      if (weekShifts) {
        const newWeekShifts = new Map(weekShifts);
        newWeekShifts.delete(shiftKey);
        newMap.set(weekKey, newWeekShifts);
      }
      return newMap;
    });
  };

  const handleWeekChange = (newWeek: Date) => {
    setCurrentWeek(newWeek);
    setSelectedSlot(null);
    setSelectedSlotKey(null);
  };

  const calculateWeeklyEarnings = (): { min: number; max: number } => {
    let totalMin = 0;
    let totalMax = 0;

    const currentWeekShifts = getCurrentWeekShifts();
    const shifts = Array.from(currentWeekShifts.values());
    for (let i = 0; i < shifts.length; i++) {
      const shift = shifts[i];
      // Parse earnings range like "$35 - $45" or "$25 – $35"
      const earningsRange = shift.earnings.replace(/\$/g, '').replace(/\s/g, '');
      const parts = earningsRange.split(/[–-]/);
      
      if (parts.length === 2) {
        const min = parseInt(parts[0]) || 0;
        const max = parseInt(parts[1]) || min;
        totalMin += min;
        totalMax += max;
      } else {
        // Fallback if format is unexpected
        const singleValue = parseInt(earningsRange) || 0;
        totalMin += singleValue;
        totalMax += singleValue;
      }
    }

    return { min: totalMin, max: totalMax };
  };

  const weeklyEarnings = calculateWeeklyEarnings();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <div className="flex-1">
          <Calendar 
            onSlotClick={handleSlotClick}
            bookedShifts={getCurrentWeekShifts()}
            selectedSlotKey={selectedSlotKey}
            currentWeek={currentWeek}
            onWeekChange={handleWeekChange}
            onDeleteShift={handleDeleteShift}
            weeklyEarnings={weeklyEarnings}
          />
        </div>
        {selectedSlot && (
          <SidePanel 
            selectedSlot={selectedSlot}
            onBookSlot={handleBookSlot}
          />
        )}
      </div>
    </div>
  );
}

export default App;
