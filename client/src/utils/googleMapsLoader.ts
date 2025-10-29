/**
 * Google Maps JavaScript API Loader
 *
 * Dynamically loads the Google Maps API script only when needed
 * Prevents multiple loads and handles loading state
 */

let isLoading = false;
let isLoaded = false;
const callbacks: Array<() => void> = [];

export const loadGoogleMapsAPI = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // Already loaded
    if (isLoaded && window.google && window.google.maps) {
      resolve();
      return;
    }

    // Currently loading - queue the callback
    if (isLoading) {
      callbacks.push(resolve);
      return;
    }

    const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

    if (!GOOGLE_MAPS_API_KEY || GOOGLE_MAPS_API_KEY === 'YOUR_GOOGLE_MAPS_API_KEY_HERE') {
      reject(new Error('Google Maps API key is not configured. Please add REACT_APP_GOOGLE_MAPS_API_KEY to your .env file.'));
      return;
    }

    isLoading = true;

    // Create script element
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=places,geometry`;
    script.async = true;
    script.defer = true;

    // Handle successful load
    script.onload = () => {
      isLoaded = true;
      isLoading = false;
      console.log('✅ Google Maps API loaded successfully');

      // Resolve main promise
      resolve();

      // Resolve queued callbacks
      callbacks.forEach(callback => callback());
      callbacks.length = 0;
    };

    // Handle load error
    script.onerror = () => {
      isLoading = false;
      const error = new Error('Failed to load Google Maps API');
      console.error('❌', error);
      reject(error);
    };

    // Add script to document
    document.head.appendChild(script);
  });
};

/**
 * Check if Google Maps API is loaded
 */
export const isGoogleMapsLoaded = (): boolean => {
  return isLoaded && window.google && window.google.maps !== undefined;
};

/**
 * TypeScript declarations for Google Maps
 */
declare global {
  interface Window {
    google: typeof google;
  }
}
