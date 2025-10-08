import React, { useState } from 'react';
import Calendar from './Calendar';
import SidePanel from './SidePanel';
import { GigOpportunity, BookedShift } from '../App';

interface ShiftsPageProps {
  onSlotClick: (day: string, hour: string, recommendations: GigOpportunity[]) => void;
  bookedShifts: Map<string, BookedShift>;
  selectedSlotKey: string | null;
  currentWeek: Date;
  onWeekChange: (newWeek: Date) => void;
  onDeleteShift: (shiftKey: string) => void;
  weeklyEarnings: { min: number; max: number };
  selectedSlot: any;
  onBookSlot: (day: string, hour: string, opportunity: any) => void;
}

const ShiftsPage: React.FC<ShiftsPageProps> = ({
  onSlotClick,
  bookedShifts,
  selectedSlotKey,
  currentWeek,
  onWeekChange,
  onDeleteShift,
  weeklyEarnings,
  selectedSlot,
  onBookSlot
}) => {
  return (
    <div className="flex">
      <div className="flex-1">
        <Calendar 
          onSlotClick={onSlotClick}
          bookedShifts={bookedShifts}
          selectedSlotKey={selectedSlotKey}
          currentWeek={currentWeek}
          onWeekChange={onWeekChange}
          onDeleteShift={onDeleteShift}
          weeklyEarnings={weeklyEarnings}
        />
      </div>
      {selectedSlot && (
        <SidePanel 
          selectedSlot={selectedSlot}
          onBookSlot={onBookSlot}
        />
      )}
    </div>
  );
};

export default ShiftsPage;
