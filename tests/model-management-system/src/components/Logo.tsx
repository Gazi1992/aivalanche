import React from 'react';

interface LogoProps {
  size?: 'small' | 'medium' | 'large' | 'xlarge' | 'xxlarge';
}

const Logo: React.FC<LogoProps> = ({ size = 'medium' }) => {
  const dimensions = {
    small: { width: 'w-20', height: 'h-14', fontSize: '1.375rem' },
    medium: { width: 'w-24', height: 'h-16', fontSize: '1.875rem' },
    large: { width: 'w-32', height: 'h-20', fontSize: '2.75rem' },
    xlarge: { width: 'w-40', height: 'h-24', fontSize: '3.5rem' },
    xxlarge: { width: 'w-56', height: 'h-32', fontSize: '4.5rem' }
  };

  const { width, height, fontSize } = dimensions[size];

  return (
    <div className={`${width} ${height} bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 rounded-xl flex items-center justify-center shadow-2xl relative overflow-hidden`}>
      {/* Subtle background circuit pattern filling entire background */}
      <svg className="absolute inset-0 w-full h-full opacity-10" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice">
        <defs>
          <pattern id="circuit" x="0" y="0" width="15" height="15" patternUnits="userSpaceOnUse">
            <circle cx="7.5" cy="7.5" r="0.5" fill="white"/>
            <circle cx="2" cy="13" r="1" fill="white"/>
            <circle cx="13" cy="2" r="1" fill="white"/>
            <path d="M 2,2 L 7.5,7.5 M 7.5,7.5 L 13,13" stroke="white" strokeWidth="0.3" fill="none"/>
            <path d="M 2,13 L 7.5,7.5 M 7.5,7.5 L 13,2" stroke="white" strokeWidth="0.3" fill="none"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#circuit)" />
      </svg>
      
      {/* MMC letters with subtle white variations */}
      <div className="flex items-baseline relative z-10" style={{ fontSize }}>
        <span 
          className="text-white font-bold"
          style={{ 
            fontFamily: "'Montserrat', 'Arial', sans-serif",
            letterSpacing: '-0.05em',
            textShadow: '3px 3px 6px rgba(0,0,0,0.7), 0 0 20px rgba(255,255,255,0.3)'
          }}
        >
          M
        </span>
        <span 
          className="text-white/95 font-bold -ml-1"
          style={{ 
            fontFamily: "'Montserrat', 'Arial', sans-serif",
            letterSpacing: '-0.05em',
            textShadow: '3px 3px 6px rgba(0,0,0,0.7), 0 0 20px rgba(255,255,255,0.3)'
          }}
        >
          M
        </span>
        <span 
          className="text-white font-bold -ml-1"
          style={{ 
            fontFamily: "'Montserrat', 'Arial', sans-serif",
            textShadow: '3px 3px 6px rgba(0,0,0,0.7), 0 0 20px rgba(255,255,255,0.3)'
          }}
        >
          C
        </span>
      </div>
    </div>
  );
};

export default Logo;