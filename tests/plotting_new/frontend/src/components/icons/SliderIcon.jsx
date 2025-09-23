import React from 'react';

const SliderIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    {/* Horizontal line */}
    <line x1="2" y1="8" x2="14" y2="8" stroke="currentColor" strokeWidth="1.5"/>
    {/* Slider handle */}
    <circle cx="8" cy="8" r="2.5" fill="currentColor"/>
    {/* Tick marks */}
    <line x1="4" y1="6" x2="4" y2="10" stroke="currentColor" strokeWidth="0.5"/>
    <line x1="12" y1="6" x2="12" y2="10" stroke="currentColor" strokeWidth="0.5"/>
  </svg>
);

export default SliderIcon;