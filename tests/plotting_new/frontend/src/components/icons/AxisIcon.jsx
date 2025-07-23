import React from 'react';

const AxisIcon = ({ size = 16 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    {/* Y axis - vertical line */}
    <line x1="3" y1="21" x2="3" y2="3" />
    
    {/* X axis - horizontal line */}
    <line x1="3" y1="21" x2="21" y2="21" />
    
    {/* Z axis - diagonal line */}
    <line x1="3" y1="21" x2="15" y2="9" />
  </svg>
);

export default AxisIcon;