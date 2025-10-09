import React from 'react';
import { useNavigate } from 'react-router-dom';

interface ComingSoonPageProps {
  featureDescription: string;
  estimatedLaunch?: string;
  feedbackUrl?: string;
}

const ComingSoonPage: React.FC<ComingSoonPageProps> = ({ 
  featureDescription, 
  estimatedLaunch, 
  feedbackUrl = "https://example.com/feedback" 
}) => {
  const navigate = useNavigate();

  const handleReturnToShifts = () => {
    navigate('/shifts');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-2xl mx-auto text-center">
        {/* Logo */}
        <div className="mb-8">
          <div className="flex items-center justify-center mb-4">
            <img
              src="/logo192.png"
              alt="Revly logo"
              className="w-12 h-12 mr-3 object-contain"
            />
            <span className="text-3xl font-bold text-gray-900">Revly</span>
          </div>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-2xl shadow-lg p-8 md:p-12">
          {/* Headline */}
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Coming Soon 🚀
          </h1>

          {/* Subtext */}
          <p className="text-lg text-gray-600 mb-6">
            We're working hard to bring you this feature. Check back soon!
          </p>

          {/* Feature Description */}
          <p className="text-base text-gray-700 mb-8 max-w-lg mx-auto">
            {featureDescription}
          </p>

          {/* Illustration */}
          <div className="mb-8">
            <svg 
              className="w-64 h-48 md:w-80 md:h-60 mx-auto text-gray-300" 
              fill="none" 
              viewBox="0 0 400 300"
            >
              {/* Rocket illustration */}
              <path 
                d="M200 50 L180 120 L220 120 Z" 
                fill="#E5E7EB" 
                className="opacity-60"
              />
              <rect 
                x="190" 
                y="120" 
                width="20" 
                height="40" 
                fill="#E5E7EB" 
                className="opacity-60"
              />
              <circle 
                cx="200" 
                cy="160" 
                r="15" 
                fill="#E5E7EB" 
                className="opacity-60"
              />
              {/* Stars */}
              <circle cx="100" cy="80" r="2" fill="#E5E7EB" className="opacity-40" />
              <circle cx="300" cy="60" r="2" fill="#E5E7EB" className="opacity-40" />
              <circle cx="80" cy="150" r="2" fill="#E5E7EB" className="opacity-40" />
              <circle cx="320" cy="140" r="2" fill="#E5E7EB" className="opacity-40" />
              <circle cx="120" cy="200" r="2" fill="#E5E7EB" className="opacity-40" />
              <circle cx="280" cy="180" r="2" fill="#E5E7EB" className="opacity-40" />
            </svg>
          </div>

          {/* Estimated Launch Date */}
          {estimatedLaunch && (
            <div className="mb-6">
              <p className="text-sm text-gray-500">
                Expected launch: <span className="font-medium text-uber-blue">{estimatedLaunch}</span>
              </p>
            </div>
          )}

          {/* Call to Action */}
          <button
            onClick={handleReturnToShifts}
            className="bg-uber-blue text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-600 transition-colors mb-6"
          >
            Return to Shifts
          </button>

          {/* Footer */}
          <div className="pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Tell us what you'd like to see here!{' '}
              <a 
                href={feedbackUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-uber-blue hover:text-blue-600 underline"
              >
                Send feedback
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComingSoonPage;
