import React from 'react';

const LegendIcon = ({ size = 16 }) => (
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
    <rect x="1" y="2.5" width="5" height="5" />
    <line x1="9" y1="5" x2="23" y2="5" />
    <rect x="1" y="9.5" width="5" height="5" />
    <line x1="9" y1="12" x2="23" y2="12" />
    <rect x="1" y="16.5" width="5" height="5" />
    <line x1="9" y1="19" x2="23" y2="19" />
  </svg>
);

export default LegendIcon;