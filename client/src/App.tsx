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

function App() {
  const [selectedSlot, setSelectedSlot] = useState<SelectedSlot | null>(null);
  const [bookedSlots, setBookedSlots] = useState<Set<string>>(new Set());

  const handleSlotClick = (day: string, hour: string, recommendations: GigOpportunity[]) => {
    setSelectedSlot({ day, hour, recommendations });
  };

  const handleBookSlot = (day: string, hour: string, service: string) => {
    const slotKey = `${day}-${hour}-${service}`;
    setBookedSlots(prev => new Set(Array.from(prev).concat(slotKey)));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <div className="flex-1">
          <Calendar 
            onSlotClick={handleSlotClick}
            bookedSlots={bookedSlots}
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
