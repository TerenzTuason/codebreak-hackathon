'use client';

import React from 'react';

interface AILoaderProps {
  size?: 'sm' | 'md' | 'lg';
}

const AILoader: React.FC<AILoaderProps> = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32'
  };

  return (
    <div className="flex items-center justify-center w-full h-full">
      <div className={`relative ${sizeClasses[size]}`}>
        {/* Neural network nodes */}
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-4 h-4 bg-blue-500 rounded-full animate-pulse" />
          <div className="absolute top-1/2 left-0 -translate-y-1/2 w-4 h-4 bg-blue-400 rounded-full animate-pulse [animation-delay:200ms]" />
          <div className="absolute top-1/2 right-0 -translate-y-1/2 w-4 h-4 bg-blue-400 rounded-full animate-pulse [animation-delay:400ms]" />
          <div className="absolute bottom-0 left-1/4 w-4 h-4 bg-blue-300 rounded-full animate-pulse [animation-delay:600ms]" />
          <div className="absolute bottom-0 right-1/4 w-4 h-4 bg-blue-300 rounded-full animate-pulse [animation-delay:800ms]" />
          
          {/* Connection lines */}
          <svg className="absolute inset-0 w-full h-full">
            <line x1="50%" y1="15%" x2="15%" y2="50%" className="stroke-blue-200 stroke-2" />
            <line x1="50%" y1="15%" x2="85%" y2="50%" className="stroke-blue-200 stroke-2" />
            <line x1="15%" y1="50%" x2="25%" y2="85%" className="stroke-blue-200 stroke-2" />
            <line x1="85%" y1="50%" x2="75%" y2="85%" className="stroke-blue-200 stroke-2" />
            <line x1="50%" y1="15%" x2="25%" y2="85%" className="stroke-blue-200 stroke-2" />
            <line x1="50%" y1="15%" x2="75%" y2="85%" className="stroke-blue-200 stroke-2" />
          </svg>
        </div>
      </div>
      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(0.9); }
        }
        .animate-pulse {
          animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
      `}</style>
    </div>
  );
};

export default AILoader; 