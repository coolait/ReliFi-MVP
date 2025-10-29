import React, { useState, useEffect } from 'react';
import { useGeolocation, Coordinates } from '../hooks/useGeolocation';
import MapPicker from './MapPicker';
import { loadGoogleMapsAPI } from '../utils/googleMapsLoader';

export interface LocationState {
  coordinates: Coordinates | null;
  cityName: string;
}

interface LocationInputProps {
  initialLocation: LocationState;
  onLocationChange: (location: LocationState) => void;
  loading?: boolean;
}

const LocationInput: React.FC<LocationInputProps> = ({
  initialLocation,
  onLocationChange,
  loading = false
}) => {
  const [showMapPicker, setShowMapPicker] = useState(false);
  const [showGPSPrompt, setShowGPSPrompt] = useState(false);
  const [googleMapsLoaded, setGoogleMapsLoaded] = useState(false);

  const {
    coordinates: gpsCoordinates,
    cityName: gpsCityName,
    loading: gpsLoading,
    error: gpsError,
    permissionStatus,
    requestLocation,
    clearError
  } = useGeolocation(false); // Don't auto-request

  // Update parent when GPS location is obtained
  useEffect(() => {
    if (gpsCoordinates && gpsCityName && !gpsLoading) {
      console.log('📍 GPS location obtained:', { coordinates: gpsCoordinates, cityName: gpsCityName });
      onLocationChange({
        coordinates: gpsCoordinates,
        cityName: gpsCityName
      });
      setShowGPSPrompt(false);
    }
  }, [gpsCoordinates, gpsCityName, gpsLoading]);

  // Show GPS prompt on first load if permission not yet determined
  useEffect(() => {
    if (permissionStatus === 'prompt' && !initialLocation.coordinates) {
      setShowGPSPrompt(true);
    }
  }, [permissionStatus]);

  const handleUseGPS = () => {
    clearError();
    requestLocation();
  };

  const handleOpenMapPicker = async () => {
    try {
      // Load Google Maps API if not already loaded
      if (!googleMapsLoaded) {
        await loadGoogleMapsAPI();
        setGoogleMapsLoaded(true);
      }
      setShowMapPicker(true);
    } catch (error) {
      console.error('Failed to load Google Maps:', error);
      alert('Failed to load Google Maps. Please check your API key configuration.');
    }
  };

  const handleMapLocationSelect = (coords: Coordinates, cityName: string) => {
    console.log('🗺️ Map location selected:', { coordinates: coords, cityName });
    onLocationChange({
      coordinates: coords,
      cityName: cityName
    });
  };

  const handleQuickSelect = (cityName: string, coords: Coordinates) => {
    onLocationChange({
      coordinates: coords,
      cityName: cityName
    });
    setShowGPSPrompt(false);
  };

  // Quick select cities with approximate coordinates
  const commonLocations = [
    { name: 'San Francisco', coords: { lat: 37.7749, lng: -122.4194 } },
    { name: 'New York', coords: { lat: 40.7128, lng: -74.0060 } },
    { name: 'Los Angeles', coords: { lat: 34.0522, lng: -118.2437 } },
    { name: 'Chicago', coords: { lat: 41.8781, lng: -87.6298 } },
    { name: 'Boston', coords: { lat: 42.3601, lng: -71.0589 } },
    { name: 'Seattle', coords: { lat: 47.6062, lng: -122.3321 } },
    { name: 'Miami', coords: { lat: 25.7617, lng: -80.1918 } },
    { name: 'Austin', coords: { lat: 30.2672, lng: -97.7431 } }
  ];

  return (
    <div className="location-input-container">
      {/* Main Location Display */}
      <div className="flex items-center gap-3 mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-center gap-2 flex-1">
          <svg
            className="w-5 h-5 text-gray-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>

          <div className="flex-1">
            <div className="text-xs text-gray-500 mb-1">Current Location</div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-semibold text-gray-900">
                {initialLocation.cityName}
              </span>
              {initialLocation.coordinates && (
                <span className="text-xs text-gray-400">
                  ({initialLocation.coordinates.lat.toFixed(4)}, {initialLocation.coordinates.lng.toFixed(4)})
                </span>
              )}
            </div>
          </div>
        </div>

        {loading && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <svg
              className="animate-spin h-4 w-4 text-blue-500"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <span>Updating recommendations...</span>
          </div>
        )}
      </div>

      {/* GPS Prompt Banner */}
      {showGPSPrompt && permissionStatus === 'prompt' && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-1">
              <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-blue-900 mb-1">
                Get more accurate earnings predictions
              </h4>
              <p className="text-sm text-blue-700 mb-3">
                Allow location access to see shift recommendations for your exact area
              </p>
              <div className="flex gap-2">
                <button
                  onClick={handleUseGPS}
                  disabled={gpsLoading}
                  className="px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {gpsLoading ? 'Getting location...' : 'Use My Location'}
                </button>
                <button
                  onClick={() => setShowGPSPrompt(false)}
                  className="px-4 py-2 text-blue-700 text-sm font-medium hover:bg-blue-100 rounded-lg transition-colors"
                >
                  No thanks
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* GPS Error */}
      {gpsError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <p className="text-sm text-red-700">{gpsError}</p>
            </div>
            <button
              onClick={clearError}
              className="text-red-400 hover:text-red-600"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Location Change Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
        <button
          onClick={handleUseGPS}
          disabled={gpsLoading || loading}
          className="flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-blue-500 text-blue-500 rounded-lg hover:bg-blue-50 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          {gpsLoading ? 'Getting GPS...' : 'Use GPS Location'}
        </button>

        <button
          onClick={handleOpenMapPicker}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          Choose on Map
        </button>
      </div>

      {/* Quick Select Cities */}
      <div>
        <div className="text-xs text-gray-500 mb-2 font-medium">Quick select city:</div>
        <div className="flex flex-wrap gap-2">
          {commonLocations.map((loc) => (
            <button
              key={loc.name}
              onClick={() => handleQuickSelect(loc.name, loc.coords)}
              className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
                initialLocation.cityName === loc.name
                  ? 'bg-blue-500 text-white'
                  : 'bg-white border border-gray-300 hover:bg-gray-100 hover:border-blue-400 text-gray-700'
              }`}
              disabled={loading}
            >
              {loc.name}
            </button>
          ))}
        </div>
      </div>

      {/* Map Picker Modal */}
      {showMapPicker && (
        <MapPicker
          initialCoordinates={initialLocation.coordinates || { lat: 37.7749, lng: -122.4194 }}
          onLocationSelect={handleMapLocationSelect}
          onClose={() => setShowMapPicker(false)}
        />
      )}
    </div>
  );
};

export default LocationInput;
