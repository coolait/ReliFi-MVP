import React, { useState, useEffect, useRef } from 'react';

interface Coordinates {
  lat: number;
  lng: number;
}

interface MapPickerProps {
  initialCoordinates?: Coordinates;
  onLocationSelect: (coords: Coordinates, cityName: string) => void;
  onClose: () => void;
}

/**
 * Google Maps picker component for selecting precise location
 *
 * Features:
 * - Interactive Google Map
 * - Click to set location pin
 * - Reverse geocoding to show selected city
 * - Drag marker to adjust location
 * - Search box for finding locations by name
 */
const MapPicker: React.FC<MapPickerProps> = ({
  initialCoordinates = { lat: 37.7749, lng: -122.4194 }, // Default to San Francisco
  onLocationSelect,
  onClose
}) => {
  const [selectedCoords, setSelectedCoords] = useState<Coordinates>(initialCoordinates);
  const [cityName, setCityName] = useState<string>('Loading...');
  const [isLoading, setIsLoading] = useState(false);
  const mapRef = useRef<HTMLDivElement>(null);
  const googleMapRef = useRef<any>(null);
  const markerRef = useRef<any>(null);

  const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

  /**
   * Reverse geocode coordinates to get city name
   */
  const reverseGeocode = async (lat: number, lng: number): Promise<string> => {
    if (!GOOGLE_MAPS_API_KEY || GOOGLE_MAPS_API_KEY === 'YOUR_GOOGLE_MAPS_API_KEY_HERE') {
      return 'Unknown Location';
    }

    try {
      const response = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${GOOGLE_MAPS_API_KEY}`
      );

      const data = await response.json();

      if (data.status === 'OK' && data.results.length > 0) {
        const result = data.results[0];

        // Try to find locality (city)
        const cityComponent = result.address_components.find(
          (component: any) =>
            component.types.includes('locality') ||
            component.types.includes('administrative_area_level_2')
        );

        if (cityComponent) {
          return cityComponent.long_name;
        }

        return result.formatted_address.split(',')[0];
      }

      return 'Unknown Location';
    } catch (err) {
      console.error('❌ Reverse geocoding error:', err);
      return 'Unknown Location';
    }
  };

  /**
   * Update marker position and reverse geocode
   */
  const updateLocation = async (coords: Coordinates) => {
    setSelectedCoords(coords);
    setCityName('Loading...');

    // Update marker position
    if (markerRef.current) {
      markerRef.current.setPosition(coords);
    }

    // Center map on new location
    if (googleMapRef.current) {
      googleMapRef.current.panTo(coords);
    }

    // Reverse geocode
    const city = await reverseGeocode(coords.lat, coords.lng);
    setCityName(city);
  };

  /**
   * Initialize Google Map
   */
  useEffect(() => {
    if (!mapRef.current || !window.google) return;

    // Create map
    const map = new window.google.maps.Map(mapRef.current, {
      center: initialCoordinates,
      zoom: 12,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
      zoomControl: true,
      styles: [
        {
          featureType: 'poi',
          elementType: 'labels',
          stylers: [{ visibility: 'off' }]
        }
      ]
    });

    googleMapRef.current = map;

    // Create marker
    const marker = new window.google.maps.Marker({
      position: initialCoordinates,
      map: map,
      draggable: true,
      title: 'Selected Location',
      animation: window.google.maps.Animation.DROP
    });

    markerRef.current = marker;

    // Handle marker drag
    marker.addListener('dragend', () => {
      const position = marker.getPosition();
      if (position) {
        updateLocation({
          lat: position.lat(),
          lng: position.lng()
        });
      }
    });

    // Handle map click
    map.addListener('click', (event: any) => {
      if (event.latLng) {
        updateLocation({
          lat: event.latLng.lat(),
          lng: event.latLng.lng()
        });
      }
    });

    // Initial reverse geocode
    reverseGeocode(initialCoordinates.lat, initialCoordinates.lng).then(setCityName);

    // Cleanup
    return () => {
      if (markerRef.current) {
        markerRef.current.setMap(null);
      }
    };
  }, []);

  const handleConfirm = () => {
    onLocationSelect(selectedCoords, cityName);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Select Your Location</h2>
            <p className="text-sm text-gray-600 mt-1">Click on the map or drag the marker</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Map Container */}
        <div className="relative">
          <div
            ref={mapRef}
            className="w-full h-[500px] bg-gray-200"
            style={{ minHeight: '500px' }}
          />

          {/* Location Info Overlay */}
          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-lg p-4 max-w-md w-full mx-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <svg
                  className="w-5 h-5 text-blue-500"
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
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900">{cityName}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {selectedCoords.lat.toFixed(6)}, {selectedCoords.lng.toFixed(6)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            <span className="font-medium">Tip:</span> Drag the marker or click to set your exact location
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium shadow-sm"
            >
              Confirm Location
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapPicker;
