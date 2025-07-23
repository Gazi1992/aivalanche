import React from 'react';

const BackgroundIcon = ({ size = 24, color = 'currentColor' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
  >
    {/* Outer rectangle representing the figure background */}
    <rect 
      x="2" 
      y="2" 
      width="20" 
      height="20" 
      stroke={color} 
      strokeWidth="2" 
      fill="none"
      strokeDasharray="2 2"
    />
    {/* Inner rectangle representing the plot area */}
    <rect 
      x="6" 
      y="6" 
      width="12" 
      height="12" 
      stroke={color} 
      strokeWidth="2" 
      fill={color}
      opacity="0.2"
    />
  </svg>
);

export default BackgroundIcon;