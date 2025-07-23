import React from 'react';

const ChatAssistantIcon = ({ size = 20 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    {/* Robot head */}
    <rect x="5" y="7" width="14" height="11" rx="2" />
    
    {/* Robot eyes */}
    <circle cx="9" cy="11.5" r="1.2" fill="currentColor" />
    <circle cx="15" cy="11.5" r="1.2" fill="currentColor" />
    
    {/* Robot mouth */}
    <line x1="9" y1="14.5" x2="15" y2="14.5" />
    
    {/* Antenna */}
    <line x1="12" y1="7" x2="12" y2="4" />
    <circle cx="12" cy="3.5" r="1.2" fill="currentColor" />
    
    {/* Robot arms */}
    <line x1="5" y1="10" x2="3" y2="10" />
    <line x1="19" y1="10" x2="21" y2="10" />
    
    {/* Robot body detail */}
    <rect x="8" y="19" width="8" height="2" rx="1" />
  </svg>
);

export default ChatAssistantIcon;