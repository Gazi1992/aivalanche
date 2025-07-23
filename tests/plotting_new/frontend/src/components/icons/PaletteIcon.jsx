import React from 'react';

const PaletteIcon = ({ size = 16 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 30.640 30.564"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.5"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    {/* Palette shape from drawing.svg */}
    <path d="M 10.376302,17.433437 C 7.1772396,14.182901 1.0125882,21.865423 0.75599282,14.04167 0.37043552,2.2852114 18.936644,-5.0675611 26.965125,6.7031172 36.918293,21.295622 18.931563,33.384428 10.931307,28.84211 3.6049494,24.68242 13.895451,21.00923 10.376302,17.433437 Z" />
    
    {/* Paint spots from drawing.svg */}
    <circle cx="7.5395532" cy="10.958241" r="2.1583977" />
    <circle cx="15.30979" cy="6.0247636" r="2.1583977" />
    <circle cx="23.203367" cy="10.464893" r="2.1583977" />
    <circle cx="23.141684" cy="19.961845" r="2.1583977" />
    <circle cx="14.754779" cy="23.908627" r="2.1583977" />
  </svg>
);

export default PaletteIcon;