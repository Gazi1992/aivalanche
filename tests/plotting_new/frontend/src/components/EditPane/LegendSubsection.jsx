import React from 'react';
import { 
  subsectionStyle, 
  subsectionHeaderStyle, 
  subsectionTitleStyle, 
  chevronStyle,
  checkboxGroupStyle,
  labelStyle,
  legendItemStyle,
  legendItemInputStyle
} from './styles';

const LegendSubsection = ({ 
  legendExpanded,
  setLegendExpanded,
  legendVisible,
  setLegendVisible,
  legendItems,
  updateLegendItem
}) => {
  return (
    <div style={subsectionStyle}>
      <div 
        style={subsectionHeaderStyle}
        onClick={() => setLegendExpanded(!legendExpanded)}
      >
        <span style={subsectionTitleStyle}>Legend</span>
        <span style={chevronStyle(legendExpanded)}>›</span>
      </div>
      
      {legendExpanded && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={checkboxGroupStyle}>
            <input
              type="checkbox"
              id="legend-visible"
              checked={legendVisible}
              onChange={(e) => setLegendVisible(e.target.checked)}
            />
            <label htmlFor="legend-visible" style={labelStyle}>Show Legend</label>
          </div>
          
          {legendVisible && legendItems.length > 0 && (
            <div style={{ marginTop: '8px' }}>
              <label style={{ ...labelStyle, marginBottom: '8px', display: 'block' }}>
                Legend Items
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {legendItems.map(item => (
                  <div key={item.id} style={legendItemStyle}>
                    <input
                      type="checkbox"
                      checked={item.visible}
                      onChange={(e) => updateLegendItem(item.id, 'visible', e.target.checked)}
                    />
                    <input
                      type="text"
                      value={item.name}
                      onChange={(e) => updateLegendItem(item.id, 'name', e.target.value)}
                      style={legendItemInputStyle}
                      onFocus={(e) => e.target.style.borderColor = 'var(--primary-color)'}
                      onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LegendSubsection;