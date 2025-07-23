import React from 'react';

const AlignRightIcon = ({ size = 24, color = 'currentColor' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
  >
    <rect x="5" y="6" width="14" height="2" fill={color} />
    <rect x="9" y="11" width="10" height="2" fill={color} />
    <rect x="7" y="16" width="12" height="2" fill={color} />
  </svg>
);

export default AlignRightIcon;