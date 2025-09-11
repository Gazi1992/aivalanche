import React from 'react';
import './ColumnSelector.css';

const ColumnSelector = ({ columns, onColumnChange, figureCount }) => {
  // Only show selector if there are multiple figures
  if (figureCount <= 1) {
    return null;
  }

  const handleColumnSelect = (value) => {
    if (onColumnChange) {
      onColumnChange(value);
    }
  };

  return (
    <div className="column-selector-container">
      <div className="column-selector-header">
        <h3>Plot Layout</h3>
        <div className="column-selector">
          <span className="column-selector-label">Columns:</span>
          <div className="column-buttons">
            {[1, 2, 3, 4].map(num => (
              <button
                key={num}
                className={`column-btn ${columns === num ? 'active' : ''}`}
                onClick={() => handleColumnSelect(num)}
                title={`${num} column${num > 1 ? 's' : ''}`}
              >
                {num}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ColumnSelector;