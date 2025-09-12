import React from 'react';
import './PlotButton.css';

const PlotButton = ({ onClick, title, icon: Icon, iconSize = 16, className = '' }) => {
  return (
    <button 
      className={`plot-button ${className}`}
      onClick={onClick}
      title={title}
    >
      <Icon size={iconSize} />
    </button>
  );
};

export default PlotButton;