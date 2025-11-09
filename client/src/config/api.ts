// API configuration for different environments
const getApiBaseUrl = () => {
  // In development, use localhost Python API (port 5002)
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:5002';
  }
  
  // In production, use Railway Python API URL from environment variable
  // Set REACT_APP_PYTHON_API_URL in Vercel environment variables
  // Example: https://your-app-name.railway.app
  return process.env.REACT_APP_PYTHON_API_URL || '';
};

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  recommendations: (day: string, hour: string) => `${API_BASE_URL}/api/recommendations/${day}/${hour}`,
  health: `${API_BASE_URL}/api/health`,
  test: `${API_BASE_URL}/api/test`
};
