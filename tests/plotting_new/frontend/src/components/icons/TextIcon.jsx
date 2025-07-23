import React from 'react';

const TextIcon = ({ size = 24, color = 'currentColor' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
  >
    <text 
      x="50%" 
      y="50%" 
      textAnchor="middle" 
      dominantBaseline="middle" 
      fontSize="28" 
      fontFamily="Algerian"
      fill={color}
    >
      A
    </text>
  </svg>
);

export default TextIcon;