// API configuration for different environments
const getApiBaseUrl = () => {
  // In development, use localhost
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:5001';
  }
  
  // In production (Vercel), use relative URLs for API routes
  return '';
};

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  recommendations: (day: string, hour: string) => `/api/recommendations/${day}/${hour}`,
  health: '/api/health',
  test: '/api/test'
};
