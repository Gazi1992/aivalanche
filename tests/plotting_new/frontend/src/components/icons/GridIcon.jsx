import React from 'react';

const GridIcon = ({ size = 16 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.5"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    {/* Vertical lines */}
    <line x1="6" y1="0" x2="6" y2="24" />
    <line x1="12" y1="0" x2="12" y2="24" />
    <line x1="18" y1="0" x2="18" y2="24" />
    
    {/* Horizontal lines */}
    <line x1="0" y1="6" x2="24" y2="6" />
    <line x1="0" y1="12" x2="24" y2="12" />
    <line x1="0" y1="18" x2="24" y2="18" />
  </svg>
);

export default GridIcon;