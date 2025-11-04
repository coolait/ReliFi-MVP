import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import ComingSoonPage from './components/ComingSoonPage';
import ShiftsPage from './components/ShiftsPage';
import { LocationState } from './components/LocationInput';

export interface GigOpportunity {
  service: string;
  startTime: string;
  endTime: string;
  projectedEarnings: string;
  color: string;
  min?: number;
  max?: number;
  hotspot?: string;
  demandScore?: number;
  tripsPerHour?: number;
  surgeMultiplier?: number;
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

// Main App component with routing
function App() {
  // Clear session tracking on page load
  useEffect(() => {
    const sessionKey = 'gcal-click-tracked';
    sessionStorage.removeItem(sessionKey);
    console.log('🔄 Page loaded - session tracking cleared');
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <Routes>
          <Route path="/" element={<ShiftsPageWrapper />} />
          <Route path="/shifts" element={<ShiftsPageWrapper />} />
          <Route 
            path="/dashboard" 
            element={
              <ComingSoonPage 
                featureDescription="Get a quick overview of your gig activity and earnings in one place."
                estimatedLaunch="December 2025"
                feedbackUrl="https://forms.gle/eookpghf5diFseE46"
              />
            } 
          />
          <Route 
            path="/analytics" 
            element={
              <ComingSoonPage 
                featureDescription="Dive deep into your performance trends and insights."
                estimatedLaunch="December 2025"
                feedbackUrl="https://forms.gle/eookpghf5diFseE46"
              />
            } 
          />
          <Route 
            path="/reports" 
            element={
              <ComingSoonPage 
                featureDescription="Generate and export detailed reports of your work."
                estimatedLaunch="December 2025"
                feedbackUrl="https://forms.gle/eookpghf5diFseE46"
              />
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

// Wrapper component for ShiftsPage with state management
function ShiftsPageWrapper() {
  const [selectedSlot, setSelectedSlot] = useState<SelectedSlot | null>(null);
  const [selectedSlotKey, setSelectedSlotKey] = useState<string | null>(null);
  const [bookedShiftsByWeek, setBookedShiftsByWeek] = useState<Map<string, Map<string, BookedShift>>>(new Map());
  const [currentWeek, setCurrentWeek] = useState(new Date());
  // Location state now includes coordinates and city name
  const [location, setLocation] = useState<LocationState>({
    coordinates: { lat: 37.7749, lng: -122.4194 }, // Default to SF
    cityName: 'San Francisco'
  });
  const [isLocationLoading, setIsLocationLoading] = useState(false);

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

  const handleLocationChange = async (newLocation: LocationState) => {
    console.log('📍 Location changed:', newLocation);
    setIsLocationLoading(true);
    setLocation(newLocation);
    // Clear selected slot when location changes
    setSelectedSlot(null);
    setSelectedSlotKey(null);
    // The Calendar component will automatically refetch with new location
    setTimeout(() => setIsLocationLoading(false), 1000);
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
    <ShiftsPage
      onSlotClick={handleSlotClick}
      bookedShifts={getCurrentWeekShifts()}
      selectedSlotKey={selectedSlotKey}
      currentWeek={currentWeek}
      onWeekChange={handleWeekChange}
      onDeleteShift={handleDeleteShift}
      weeklyEarnings={weeklyEarnings}
      selectedSlot={selectedSlot}
      onBookSlot={handleBookSlot}
      location={location}
      onLocationChange={handleLocationChange}
      isLocationLoading={isLocationLoading}
    />
  );
}

export default App;
