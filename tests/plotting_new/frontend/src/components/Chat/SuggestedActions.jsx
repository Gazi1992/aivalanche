import React from 'react';
import './SuggestedActions.css';

const SuggestedActions = ({ suggestions, onActionClick }) => {
  if (!suggestions || suggestions.length === 0) return null;
  
  return (
    <div className="suggested-actions">
      <div className="actions-header">Suggested Actions</div>
      <div className="actions-list">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            className="action-button"
            onClick={() => onActionClick(suggestion.action)}
            title={suggestion.description || suggestion.text}
          >
            {suggestion.text}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SuggestedActions;