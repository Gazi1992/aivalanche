import React from 'react';
import './PlotsHeader.css';

const PlotsHeader = ({ columns, onColumnChange, figureCount, onClearPlots, onRefreshPlots }) => {
  const handleColumnSelect = (value) => {
    if (onColumnChange) {
      onColumnChange(value);
    }
  };

  // Determine max columns based on figure count
  const maxColumns = Math.min(4, figureCount);
  const columnOptions = Array.from({length: maxColumns}, (_, i) => i + 1);

  return (
    <div className="column-selector-container">
      <div className="column-selector-header">
        <div className="plot-action-buttons">
          <button
            className="clear-plots-btn"
            onClick={onClearPlots}
            title="Clear all plots"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              <line x1="10" y1="11" x2="10" y2="17"></line>
              <line x1="14" y1="11" x2="14" y2="17"></line>
            </svg>
            Clear
          </button>
          <button
            className="refresh-plots-btn"
            onClick={onRefreshPlots}
            title="Refresh all plots"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="23 4 23 10 17 10"></polyline>
              <polyline points="1 20 1 14 7 14"></polyline>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
            Refresh
          </button>
        </div>
        {figureCount > 1 && (
          <div className="column-selector">
            <span className="column-selector-label">Columns:</span>
            <div className="column-buttons">
              {columnOptions.map(num => (
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
        )}
      </div>
    </div>
  );
};

export default PlotsHeader;