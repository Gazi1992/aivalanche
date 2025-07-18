import React from 'react';
import { 
  subsectionStyle, 
  subsectionHeaderStyle, 
  subsectionTitleStyle, 
  chevronStyle,
  legendItemStyle,
  legendItemInputStyle
} from './styles';

const TitleSubsection = ({ 
  titleExpanded, 
  setTitleExpanded,
  titleVisible,
  setTitleVisible,
  titleText,
  setTitleText,
  onBlur
}) => {
  return (
    <div style={subsectionStyle}>
      <div 
        style={subsectionHeaderStyle}
        onClick={() => setTitleExpanded(!titleExpanded)}
      >
        <span style={subsectionTitleStyle}>Title</span>
        <span style={chevronStyle(titleExpanded)}>›</span>
      </div>
      
      {titleExpanded && (
        <div style={legendItemStyle}>
          <input
            type="checkbox"
            id="title-visible"
            checked={titleVisible}
            onChange={(e) => setTitleVisible(e.target.checked)}
          />
          <input
            type="text"
            value={titleText}
            onChange={(e) => setTitleText(e.target.value)}
            placeholder="Plot Title"
            style={legendItemInputStyle}
            disabled={!titleVisible}
            onFocus={(e) => e.target.style.borderColor = 'var(--primary-color)'}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--border-color)';
              onBlur();
            }}
          />
        </div>
      )}
    </div>
  );
};

export default TitleSubsection;