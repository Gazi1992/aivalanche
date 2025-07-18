import React from 'react';
import { 
  subsectionStyle, 
  subsectionHeaderStyle, 
  subsectionTitleStyle, 
  chevronStyle,
  legendItemStyle,
  legendItemInputStyle,
  inputStyle,
  selectStyle,
  checkboxGroupStyle,
  labelStyle
} from './styles';

const AxisSubsection = ({ 
  axis, // 'X' or 'Y'
  expanded,
  setExpanded,
  labelVisible,
  setLabelVisible,
  label,
  setLabel,
  scale,
  setScale,
  ticksVisible,
  setTicksVisible,
  minValue,
  setMinValue,
  maxValue,
  setMaxValue,
  inverted,
  setInverted,
  onBlur
}) => {
  return (
    <div style={subsectionStyle}>
      <div 
        style={subsectionHeaderStyle}
        onClick={() => setExpanded(!expanded)}
      >
        <span style={subsectionTitleStyle}>{axis}-Axis</span>
        <span style={chevronStyle(expanded)}>›</span>
      </div>
      
      {expanded && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Axis Label */}
          <div style={legendItemStyle}>
            <input
              type="checkbox"
              id={`${axis.toLowerCase()}axis-label-visible`}
              checked={labelVisible}
              onChange={(e) => setLabelVisible(e.target.checked)}
            />
            <input
              type="text"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder={`${axis}-Axis Label`}
              style={legendItemInputStyle}
              disabled={!labelVisible}
              onFocus={(e) => e.target.style.borderColor = 'var(--primary-color)'}
              onBlur={(e) => {
                e.target.style.borderColor = 'var(--border-color)';
                onBlur();
              }}
            />
          </div>
          
          {/* Show Tick Labels */}
          <div style={checkboxGroupStyle}>
            <input
              type="checkbox"
              id={`${axis.toLowerCase()}axis-ticks-visible`}
              checked={ticksVisible}
              onChange={(e) => setTicksVisible(e.target.checked)}
            />
            <label htmlFor={`${axis.toLowerCase()}axis-ticks-visible`} style={labelStyle}>Show Tick Labels</label>
          </div>
          
          {/* Scale, Min, Max */}
          <div style={{ display: 'flex', gap: '8px' }}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <label htmlFor={`${axis.toLowerCase()}axis-scale`} style={{ ...labelStyle, display: 'block', marginBottom: '4px' }}>Scale</label>
              <select
                id={`${axis.toLowerCase()}axis-scale`}
                value={scale}
                onChange={(e) => setScale(e.target.value)}
                style={{ ...selectStyle, width: '100%' }}
                onFocus={(e) => e.target.style.borderColor = 'var(--primary-color)'}
                onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
              >
                <option value="linear">Linear</option>
                <option value="log">Logarithmic</option>
              </select>
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <label htmlFor={`${axis.toLowerCase()}axis-min`} style={{ ...labelStyle, display: 'block', marginBottom: '4px' }}>Min</label>
              <input
                type="text"
                id={`${axis.toLowerCase()}axis-min`}
                value={minValue}
                onChange={(e) => setMinValue(e.target.value)}
                placeholder="Auto"
                style={{ ...inputStyle, width: '100%', boxSizing: 'border-box' }}
                onFocus={(e) => e.target.style.borderColor = 'var(--primary-color)'}
                onBlur={(e) => {
                  e.target.style.borderColor = 'var(--border-color)';
                  onBlur();
                }}
              />
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <label htmlFor={`${axis.toLowerCase()}axis-max`} style={{ ...labelStyle, display: 'block', marginBottom: '4px' }}>Max</label>
              <input
                type="text"
                id={`${axis.toLowerCase()}axis-max`}
                value={maxValue}
                onChange={(e) => setMaxValue(e.target.value)}
                placeholder="Auto"
                style={{ ...inputStyle, width: '100%', boxSizing: 'border-box' }}
                onFocus={(e) => e.target.style.borderColor = 'var(--primary-color)'}
                onBlur={(e) => {
                  e.target.style.borderColor = 'var(--border-color)';
                  onBlur();
                }}
              />
            </div>
          </div>
          
          {/* Invert Axis */}
          <div style={checkboxGroupStyle}>
            <input
              type="checkbox"
              id={`${axis.toLowerCase()}axis-inverted`}
              checked={inverted}
              onChange={(e) => setInverted(e.target.checked)}
            />
            <label htmlFor={`${axis.toLowerCase()}axis-inverted`} style={labelStyle}>Reverse Axis</label>
          </div>
        </div>
      )}
    </div>
  );
};

export default AxisSubsection;