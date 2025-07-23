import React from 'react';

const AppearanceIcon = ({ size = 16 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2.5"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="3" />
    <path d="M12 1v6m0 6v6m4.22-15.22l4.24 4.24m-4.24 9.74l4.24 4.24M20 12h-6m-6 0H2m15.22 4.22l-4.24-4.24m-9.74 4.24l4.24-4.24" />
  </svg>
);

export default AppearanceIcon;