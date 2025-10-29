import { useState, useEffect } from 'react';

export interface Coordinates {
  lat: number;
  lng: number;
}

export interface LocationData {
  coordinates: Coordinates | null;
  cityName: string | null;
  loading: boolean;
  error: string | null;
  permissionStatus: 'prompt' | 'granted' | 'denied' | 'unknown';
}

interface UseGeolocationReturn extends LocationData {
  requestLocation: () => void;
  clearError: () => void;
}

/**
 * Hook to get user's GPS location and reverse geocode to city name
 *
 * Features:
 * - Automatically requests GPS permission on mount (optional)
 * - Reverse geocodes coordinates to city name using Google Maps API
 * - Handles permission states and errors
 * - Caches location to avoid repeated API calls
 */
export const useGeolocation = (autoRequest: boolean = false): UseGeolocationReturn => {
  const [coordinates, setCoordinates] = useState<Coordinates | null>(null);
  const [cityName, setCityName] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [permissionStatus, setPermissionStatus] = useState<'prompt' | 'granted' | 'denied' | 'unknown'>('unknown');

  const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

  /**
   * Reverse geocode coordinates to get city name
   */
  const reverseGeocode = async (lat: number, lng: number): Promise<string> => {
    if (!GOOGLE_MAPS_API_KEY || GOOGLE_MAPS_API_KEY === 'YOUR_GOOGLE_MAPS_API_KEY_HERE') {
      console.warn('⚠️ Google Maps API key not configured');
      return 'Unknown Location';
    }

    try {
      const response = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${GOOGLE_MAPS_API_KEY}`
      );

      if (!response.ok) {
        throw new Error('Geocoding API request failed');
      }

      const data = await response.json();

      if (data.status === 'OK' && data.results.length > 0) {
        // Extract city name from address components
        const result = data.results[0];

        // Try to find locality (city) first
        const cityComponent = result.address_components.find(
          (component: any) =>
            component.types.includes('locality') ||
            component.types.includes('administrative_area_level_2')
        );

        if (cityComponent) {
          return cityComponent.long_name;
        }

        // Fallback to formatted address
        return result.formatted_address.split(',')[0];
      }

      return 'Unknown Location';
    } catch (err) {
      console.error('❌ Reverse geocoding error:', err);
      return 'Unknown Location';
    }
  };

  /**
   * Request user's GPS location
   */
  const requestLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      setPermissionStatus('denied');
      return;
    }

    setLoading(true);
    setError(null);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const coords: Coordinates = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };

        console.log('📍 GPS coordinates obtained:', coords);
        setCoordinates(coords);
        setPermissionStatus('granted');

        // Reverse geocode to get city name
        const city = await reverseGeocode(coords.lat, coords.lng);
        console.log('🏙️ City name:', city);
        setCityName(city);
        setLoading(false);
      },
      (error) => {
        console.error('❌ Geolocation error:', error);

        let errorMessage = 'Unable to retrieve your location';
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location permission denied. Please enable location access in your browser.';
            setPermissionStatus('denied');
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information is unavailable.';
            setPermissionStatus('denied');
            break;
          case error.TIMEOUT:
            errorMessage = 'Location request timed out.';
            setPermissionStatus('denied');
            break;
        }

        setError(errorMessage);
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // Cache for 5 minutes
      }
    );
  };

  const clearError = () => setError(null);

  // Check permission status on mount
  useEffect(() => {
    if ('permissions' in navigator) {
      navigator.permissions.query({ name: 'geolocation' as PermissionName }).then((result) => {
        setPermissionStatus(result.state as 'prompt' | 'granted' | 'denied');

        // Auto-request if permission already granted
        if (result.state === 'granted' && autoRequest) {
          requestLocation();
        }
      });
    } else if (autoRequest) {
      // Fallback: just request if browser doesn't support permissions API
      requestLocation();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoRequest]); // requestLocation is stable, no need to include

  return {
    coordinates,
    cityName,
    loading,
    error,
    permissionStatus,
    requestLocation,
    clearError
  };
};
