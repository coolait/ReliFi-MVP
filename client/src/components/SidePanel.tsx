import React from 'react';
import { SelectedSlot } from '../App';
import { trackGcalClick, testFirebaseConnection } from '../services/analyticsService';

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
      case 'rideshare':
        return 'bg-uber-blue';
      case 'food delivery':
        return 'bg-doordash-yellow';
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
      case 'rideshare':
        return 'text-white';
      case 'food delivery':
        return 'text-gray-900';
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
    <div className="w-80 bg-gray-50 border-l border-gray-200">
      {/* Spacer to align with calendar grid: LocationInput section + Calendar padding + Calendar header */}
      <div className="p-6">
        {/* Match LocationInput section (p-6) + Calendar header section height */}
        <div className="mb-6" style={{ minHeight: '408px' }}></div>
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
                <div className="text-sm text-gray-900">{opportunity.hotspot || 'Downtown Core'}</div>
              </div>

              <div className="mb-4">
                <div className="text-xs text-gray-500 mb-2">Demand Forecast</div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-uber-blue h-2 rounded-full"
                    style={{ width: `${(opportunity.demandScore || 0.75) * 100}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Low</span>
                  <span className="font-medium text-gray-900">{Math.round((opportunity.demandScore || 0.75) * 100)}%</span>
                  <span>High</span>
                </div>
              </div>

              {opportunity.tripsPerHour && (
                <div className="mb-4 flex justify-between text-sm">
                  <span className="text-gray-500">Est. Trips/Hour:</span>
                  <span className="font-medium text-gray-900">{opportunity.tripsPerHour.toFixed(1)}</span>
                </div>
              )}

              {opportunity.surgeMultiplier && opportunity.surgeMultiplier > 1.0 && (
                <div className="mb-4">
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-2 flex items-center gap-2">
                    <svg className="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    <span className="text-xs text-yellow-800 font-medium">
                      {opportunity.surgeMultiplier.toFixed(1)}x Surge Pricing
                    </span>
                  </div>
                </div>
              )}

              <div className="flex gap-2">
              <button
                onClick={() => onBookSlot(day, hour, opportunity)}
                className="w-full bg-uber-blue text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-600 transition-colors"
              >
                Add to My Schedule
              </button>
                <button
                  onClick={async () => {
                    // Track the click in Firebase
                    await trackGcalClick(opportunity.service, day, hour);
                    
                    const startDate = new Date();
                    const dayOfWeek = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'].indexOf(day.toLowerCase());
                    const currentDay = new Date().getDay();
                    const daysUntilTarget = (dayOfWeek - currentDay + 7) % 7;
                    startDate.setDate(startDate.getDate() + daysUntilTarget);
                    startDate.setHours(parseInt(hour), 0, 0, 0);
                    
                    const endDate = new Date(startDate);
                    endDate.setHours(startDate.getHours() + 1);
                    
                    const startTime = startDate.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
                    const endTime = endDate.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
                    
                    const eventTitle = `${opportunity.service} Drive`;
                    const hotspot = opportunity.hotspot || 'Downtown Core';
                    const eventDetails = `Gig Work - ${opportunity.service}\nProjected Earnings: ${opportunity.projectedEarnings}\nTime: ${opportunity.startTime} - ${opportunity.endTime}\nHotspot: ${hotspot}${opportunity.demandScore ? `\nDemand Score: ${Math.round(opportunity.demandScore * 100)}%` : ''}${opportunity.tripsPerHour ? `\nEst. Trips/Hour: ${opportunity.tripsPerHour.toFixed(1)}` : ''}`;

                    const googleCalendarUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(eventTitle)}&dates=${startTime}/${endTime}&details=${encodeURIComponent(eventDetails)}&location=${encodeURIComponent(hotspot)}`;
                    
                    window.open(googleCalendarUrl, '_blank');
                  }}
                  className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-green-700 transition-colors"
                >
                  Add to Google Calendar
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 text-xs text-gray-500 text-center">
          Note: Recommendations are based on historical data and may vary.
        </div>
        
        {/* Debug Firebase Connection Button */}
        <div className="mt-4 space-y-2">
          <button
            onClick={async () => {
              console.log('🧪 Testing Firebase connection...');
              await testFirebaseConnection();
            }}
            className="w-full bg-gray-500 text-white py-2 px-4 rounded-lg font-medium hover:bg-gray-600 transition-colors text-sm"
          >
            🧪 Test Firebase Connection
          </button>
          {/* <button
            onClick={() => {
              resetSessionTracking();
            }}
            className="w-full bg-orange-500 text-white py-2 px-4 rounded-lg font-medium hover:bg-orange-600 transition-colors text-sm"
          >
            🔄 Reset Session Tracking
          </button> */}
        </div>
        </div>
      </div>
    </div>
  );
};

export default SidePanel;
