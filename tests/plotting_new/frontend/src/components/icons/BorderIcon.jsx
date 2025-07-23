import React from 'react';

const BorderIcon = ({ size = 24, color = 'currentColor' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
  >
    {/* Simple stroke square */}
    <rect 
      x="4" 
      y="4" 
      width="16" 
      height="16" 
      stroke={color} 
      strokeWidth="2" 
      fill="none"
    />
  </svg>
);

export default BorderIcon;