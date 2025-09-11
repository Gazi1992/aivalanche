import React from 'react';

interface LogoVariationProps {
  variant: number;
  size?: 'small' | 'medium' | 'large';
}

const LogoVariation: React.FC<LogoVariationProps> = ({ variant, size = 'medium' }) => {
  const dimensions = {
    small: { width: 'w-20', height: 'h-14', fontSize: '1.125rem' },
    medium: { width: 'w-24', height: 'h-16', fontSize: '1.5rem' },
    large: { width: 'w-32', height: 'h-20', fontSize: '2.25rem' }
  };

  const { width, height, fontSize } = dimensions[size];

  const colorSchemes = [
    // Original - Cyan, Gold, Pink
    { m1: '#60D5FF', m2: '#FFD700', c: '#FF6B9D', name: 'Vibrant Mix' },
    
    // Professional Blues
    { m1: '#4A90E2', m2: '#6BB6FF', c: '#2E5266', name: 'Professional Blues' },
    
    // Sunset
    { m1: '#FF6B6B', m2: '#FFE66D', c: '#FF8E53', name: 'Sunset' },
    
    // Ocean
    { m1: '#00D9FF', m2: '#0693E3', c: '#005082', name: 'Ocean' },
    
    // Forest
    { m1: '#52C41A', m2: '#95DE64', c: '#237804', name: 'Forest' },
    
    // Purple Gradient
    { m1: '#B794F4', m2: '#9F7AEA', c: '#6B46C1', name: 'Purple Gradient' },
    
    // Fire
    { m1: '#FF4757', m2: '#FFA502', c: '#FF6348', name: 'Fire' },
    
    // Monochrome White
    { m1: '#FFFFFF', m2: '#F0F0F0', c: '#E0E0E0', name: 'White Monochrome' },
    
    // Electric
    { m1: '#00FFF0', m2: '#FF00FF', c: '#FFFF00', name: 'Electric' },
    
    // Pastel
    { m1: '#FFB3BA', m2: '#BAE1FF', c: '#FFFFBA', name: 'Pastel' },
    
    // Dark Mode
    { m1: '#818CF8', m2: '#A78BFA', c: '#C084FC', name: 'Dark Mode Purple' },
    
    // Corporate
    { m1: '#1E40AF', m2: '#3B82F6', c: '#60A5FA', name: 'Corporate Blue' }
  ];

  const scheme = colorSchemes[variant] || colorSchemes[0];

  return (
    <div className="text-center">
      <div className={`${width} ${height} bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 rounded-xl flex items-center justify-center shadow-2xl relative overflow-hidden mx-auto`}>
        <div className="flex items-baseline" style={{ fontSize }}>
          <span 
            className="font-bold"
            style={{ 
              fontFamily: "'Montserrat', 'Arial', sans-serif",
              letterSpacing: '-0.05em',
              color: scheme.m1,
              textShadow: `3px 3px 6px rgba(0,0,0,0.7), 0 0 20px ${scheme.m1}40`
            }}
          >
            M
          </span>
          <span 
            className="font-bold -ml-1"
            style={{ 
              fontFamily: "'Montserrat', 'Arial', sans-serif",
              letterSpacing: '-0.05em',
              color: scheme.m2,
              textShadow: `3px 3px 6px rgba(0,0,0,0.7), 0 0 20px ${scheme.m2}40`
            }}
          >
            M
          </span>
          <span 
            className="font-bold -ml-1"
            style={{ 
              fontFamily: "'Montserrat', 'Arial', sans-serif",
              color: scheme.c,
              textShadow: `3px 3px 6px rgba(0,0,0,0.7), 0 0 20px ${scheme.c}40`
            }}
          >
            C
          </span>
        </div>
      </div>
      <p className="text-xs text-gray-600 mt-2">{variant + 1}. {scheme.name}</p>
    </div>
  );
};

export default LogoVariation;