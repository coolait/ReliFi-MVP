import React from 'react';
import { SelectedSlot } from '../App';

interface SidePanelProps {
  selectedSlot: SelectedSlot;
  onBookSlot: (day: string, hour: string, opportunity: any) => void;
}

const SidePanel: React.FC<SidePanelProps> = ({ selectedSlot, onBookSlot }) => {
  const { day, hour, recommendations } = selectedSlot;

  const formatHour = (hour: string) => {
    const hourNum = parseInt(hour);
    if (hourNum === 0) return '12 AM';
    if (hourNum < 12) return `${hourNum} AM`;
    if (hourNum === 12) return '12 PM';
    return `${hourNum - 12} PM`;
  };

  const formatTimeRange = (startTime: string, endTime: string) => {
    return `${startTime} - ${endTime}`;
  };

  const getServiceColor = (service: string) => {
    switch (service.toLowerCase()) {
      case 'uber':
      case 'lyft':
        return 'bg-uber-blue';
      case 'doordash':
        return 'bg-doordash-yellow';
      case 'grubhub':
        return 'bg-grubhub-orange';
      case 'uber eats':
        return 'bg-ubereats-gray';
      default:
        return 'bg-gray-500';
    }
  };

  const getServiceTextColor = (service: string) => {
    switch (service.toLowerCase()) {
      case 'uber':
      case 'lyft':
        return 'text-white';
      case 'doordash':
        return 'text-gray-900';
      case 'grubhub':
        return 'text-white';
      case 'uber eats':
        return 'text-gray-900';
      default:
        return 'text-white';
    }
  };

  return (
    <div className="w-80 bg-gray-50 border-l border-gray-200 p-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">
          {recommendations[0]?.service || 'Gig'} Shift
        </h2>
        <p className="text-sm text-gray-600 mb-6">
          {day}, {formatHour(hour)} - {formatHour((parseInt(hour) + 1).toString())}
        </p>

        <div className="space-y-4">
          {recommendations.map((opportunity, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${getServiceColor(opportunity.service)} ${getServiceTextColor(opportunity.service)}`}>
                  {opportunity.service}
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-500">Projected Earnings</div>
                  <div className="text-lg font-bold text-gray-900">{opportunity.projectedEarnings}</div>
                </div>
              </div>
              
              <div className="text-sm text-gray-600 mb-3">
                {formatTimeRange(opportunity.startTime, opportunity.endTime)}
              </div>

              <div className="mb-4">
                <div className="text-xs text-gray-500 mb-1">Hotspot Area</div>
                <div className="text-sm text-gray-900">Downtown Core</div>
              </div>

              <div className="mb-4">
                <div className="text-xs text-gray-500 mb-2">Demand Forecast</div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-uber-blue h-2 rounded-full" 
                    style={{ width: `${Math.random() * 40 + 60}%` }}
                  ></div>
                </div>
              </div>

              <button
                onClick={() => onBookSlot(day, hour, opportunity)}
                className="w-full bg-uber-blue text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-600 transition-colors"
              >
                Add to My Schedule
              </button>
            </div>
          ))}
        </div>

        <div className="mt-6 text-xs text-gray-500 text-center">
          Note: Recommendations are based on historical data and may vary.
        </div>
      </div>
    </div>
  );
};

export default SidePanel;
