import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const isActive = (path: string) => {
    return location.pathname === path || (path === '/shifts' && location.pathname === '/');
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <img
                src="/logo192.png"
                alt="Revly logo"
                className="w-8 h-8 mr-3 object-contain"
              />
              <span className="text-xl font-bold text-gray-900">Revly</span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <button 
              onClick={() => handleNavigation('/dashboard')}
              className={`px-3 py-2 text-sm font-medium ${
                isActive('/dashboard') 
                  ? 'text-uber-blue border-b-2 border-uber-blue' 
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => handleNavigation('/shifts')}
              className={`px-3 py-2 text-sm font-medium ${
                isActive('/shifts') 
                  ? 'text-uber-blue border-b-2 border-uber-blue' 
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              Shifts
            </button>
            <button 
              onClick={() => handleNavigation('/analytics')}
              className={`px-3 py-2 text-sm font-medium ${
                isActive('/analytics') 
                  ? 'text-uber-blue border-b-2 border-uber-blue' 
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              Analytics
            </button>
            <button 
              onClick={() => handleNavigation('/reports')}
              className={`px-3 py-2 text-sm font-medium ${
                isActive('/reports') 
                  ? 'text-uber-blue border-b-2 border-uber-blue' 
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              Reports
            </button>
          </nav>

          {/* User actions */}
          <div className="flex items-center space-x-4">
            <button className="text-gray-400 hover:text-gray-500">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
            <button className="text-gray-400 hover:text-gray-500">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
