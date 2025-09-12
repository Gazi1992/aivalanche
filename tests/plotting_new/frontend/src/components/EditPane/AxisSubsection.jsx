import React from 'react';
import { AxisIcon } from '../icons';
import { 
  subsectionStyle, 
  subsectionHeaderStyle, 
  subsectionTitleStyle, 
  chevronStyle,
  inputStyle,
  labelStyle,
  selectStyle,
  checkboxStyle
} from './styles';

const AxisSubsection = ({ 
  axisExpanded, 
  setAxisExpanded,
  xAxisScale,
  setXAxisScale,
  xAxisMin,
  setXAxisMin,
  xAxisMax,
  setXAxisMax,
  xAxisInverted,
  setXAxisInverted,
  yAxisScale,
  setYAxisScale,
  yAxisMin,
  setYAxisMin,
  yAxisMax,
  setYAxisMax,
  yAxisInverted,
  setYAxisInverted,
  xAxisLabelVisible,
  setXAxisLabelVisible,
  xAxisLabel,
  setXAxisLabel,
  yAxisLabelVisible,
  setYAxisLabelVisible,
  yAxisLabel,
  setYAxisLabel,
  xAxisTicksVisible,
  setXAxisTicksVisible,
  yAxisTicksVisible,
  setYAxisTicksVisible,
  onBlur,
  metadata = {}
}) => {
  // Check if axes are categorical from metadata
  const xAxisCategorical = metadata.xAxisCategorical || metadata.xAxisType === 'category';
  const yAxisCategorical = metadata.yAxisCategorical || metadata.yAxisType === 'category';
  const containerStyle = {
    display: 'grid',
    gridTemplateColumns: '60px minmax(0, 1fr) minmax(0, 1fr)',
    gap: '8px',
    columnGap: '16px'
  };
  
  const columnHeaderStyle = {
    fontSize: '0.9rem',
    fontWeight: '600',
    color: 'var(--text-color)',
    textAlign: 'left',
    paddingBottom: '8px'
  };
  
  const rowLabelStyle = {
    fontSize: '0.85rem',
    color: 'var(--text-color)',
    textAlign: 'left',
    display: 'flex',
    alignItems: 'center'
  };

  return (
    <div style={subsectionStyle}>
      <div 
        style={subsectionHeaderStyle}
        onClick={() => setAxisExpanded(!axisExpanded)}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <AxisIcon size={20} />
          <span style={subsectionTitleStyle}>Axes</span>
        </span>
        <span style={chevronStyle(axisExpanded)}>›</span>
      </div>
      
      {axisExpanded && (
        <div style={containerStyle}>
          {/* Headers */}
          <div></div>
          <div style={columnHeaderStyle}>X-Axis</div>
          <div style={columnHeaderStyle}>Y-Axis</div>
          
          {/* Labels Row */}
          <div style={rowLabelStyle}>Label</div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', minWidth: 0 }}>
            <input
              type="checkbox"
              checked={xAxisLabelVisible}
              onChange={(e) => setXAxisLabelVisible(e.target.checked)}
              style={checkboxStyle}
            />
            <input
              type="text"
              value={xAxisLabel}
              onChange={(e) => setXAxisLabel(e.target.value)}
              onBlur={onBlur}
              style={{ ...inputStyle, flex: 1, minWidth: 0 }}
              placeholder="X-axis label"
              disabled={!xAxisLabelVisible}
            />
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', minWidth: 0 }}>
            <input
              type="checkbox"
              checked={yAxisLabelVisible}
              onChange={(e) => setYAxisLabelVisible(e.target.checked)}
              style={checkboxStyle}
            />
            <input
              type="text"
              value={yAxisLabel}
              onChange={(e) => setYAxisLabel(e.target.value)}
              onBlur={onBlur}
              style={{ ...inputStyle, flex: 1, minWidth: 0 }}
              placeholder="Y-axis label"
              disabled={!yAxisLabelVisible}
            />
          </div>
          
          {/* Ticks Row */}
          <div style={rowLabelStyle}>Ticks</div>
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <input
              type="checkbox"
              checked={xAxisTicksVisible}
              onChange={(e) => setXAxisTicksVisible(e.target.checked)}
              style={checkboxStyle}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <input
              type="checkbox"
              checked={yAxisTicksVisible}
              onChange={(e) => setYAxisTicksVisible(e.target.checked)}
              style={checkboxStyle}
            />
          </div>
          
          {/* Scale Row */}
          <div style={rowLabelStyle}>Scale</div>
          <select
            value={xAxisScale}
            onChange={(e) => setXAxisScale(e.target.value)}
            style={selectStyle}
          >
            <option value="linear">Linear</option>
            <option value="log">Log</option>
          </select>
          <select
            value={yAxisScale}
            onChange={(e) => setYAxisScale(e.target.value)}
            style={selectStyle}
          >
            <option value="linear">Linear</option>
            <option value="log">Log</option>
          </select>
          
          {/* Min Row */}
          <div style={rowLabelStyle}>Min</div>
          <input
            type="text"
            value={xAxisMin}
            onChange={(e) => setXAxisMin(e.target.value)}
            onBlur={onBlur}
            style={{ 
              ...inputStyle, 
              width: '100%', 
              boxSizing: 'border-box',
              ...(xAxisCategorical && { 
                opacity: 0.5, 
                cursor: 'not-allowed',
                backgroundColor: 'var(--disabled-bg-color, #f5f5f5)'
              })
            }}
            placeholder={xAxisCategorical ? "N/A" : "Auto"}
            disabled={xAxisCategorical}
            title={xAxisCategorical ? "Min/Max not applicable for categorical axis" : ""}
          />
          <input
            type="text"
            value={yAxisMin}
            onChange={(e) => setYAxisMin(e.target.value)}
            onBlur={onBlur}
            style={{ 
              ...inputStyle, 
              width: '100%', 
              boxSizing: 'border-box',
              ...(yAxisCategorical && { 
                opacity: 0.5, 
                cursor: 'not-allowed',
                backgroundColor: 'var(--disabled-bg-color, #f5f5f5)'
              })
            }}
            placeholder={yAxisCategorical ? "N/A" : "Auto"}
            disabled={yAxisCategorical}
            title={yAxisCategorical ? "Min/Max not applicable for categorical axis" : ""}
          />
          
          {/* Max Row */}
          <div style={rowLabelStyle}>Max</div>
          <input
            type="text"
            value={xAxisMax}
            onChange={(e) => setXAxisMax(e.target.value)}
            onBlur={onBlur}
            style={{ 
              ...inputStyle, 
              width: '100%', 
              boxSizing: 'border-box',
              ...(xAxisCategorical && { 
                opacity: 0.5, 
                cursor: 'not-allowed',
                backgroundColor: 'var(--disabled-bg-color, #f5f5f5)'
              })
            }}
            placeholder={xAxisCategorical ? "N/A" : "Auto"}
            disabled={xAxisCategorical}
            title={xAxisCategorical ? "Min/Max not applicable for categorical axis" : ""}
          />
          <input
            type="text"
            value={yAxisMax}
            onChange={(e) => setYAxisMax(e.target.value)}
            onBlur={onBlur}
            style={{ 
              ...inputStyle, 
              width: '100%', 
              boxSizing: 'border-box',
              ...(yAxisCategorical && { 
                opacity: 0.5, 
                cursor: 'not-allowed',
                backgroundColor: 'var(--disabled-bg-color, #f5f5f5)'
              })
            }}
            placeholder={yAxisCategorical ? "N/A" : "Auto"}
            disabled={yAxisCategorical}
            title={yAxisCategorical ? "Min/Max not applicable for categorical axis" : ""}
          />
          
          {/* Reverse Row */}
          <div style={rowLabelStyle}>Reverse</div>
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <input
              type="checkbox"
              checked={xAxisInverted}
              onChange={(e) => setXAxisInverted(e.target.checked)}
              style={checkboxStyle}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <input
              type="checkbox"
              checked={yAxisInverted}
              onChange={(e) => setYAxisInverted(e.target.checked)}
              style={checkboxStyle}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default AxisSubsection;