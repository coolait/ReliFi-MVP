import React from 'react';
import Calendar from './Calendar';
import SidePanel from './SidePanel';
import LocationInput, { LocationState } from './LocationInput';
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
  location: LocationState;
  onLocationChange: (location: LocationState) => void;
  isLocationLoading: boolean;
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
  onBookSlot,
  location,
  onLocationChange,
  isLocationLoading
}) => {
  return (
    <div className="flex">
      <div className="flex-1">
        <div className="p-6">
          <LocationInput
            initialLocation={location}
            onLocationChange={onLocationChange}
            loading={isLocationLoading}
          />
        </div>
        <Calendar
          onSlotClick={onSlotClick}
          bookedShifts={bookedShifts}
          selectedSlotKey={selectedSlotKey}
          currentWeek={currentWeek}
          onWeekChange={onWeekChange}
          onDeleteShift={onDeleteShift}
          weeklyEarnings={weeklyEarnings}
          location={location}
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
