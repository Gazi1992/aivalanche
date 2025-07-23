import React from 'react';
import { GridIcon, FillIcon } from '../icons';
import ColorPickerIcon from './ColorPickerIcon';
import { 
  subsectionStyle, 
  subsectionHeaderStyle, 
  chevronStyle,
  fieldContainerStyle,
  labelStyle,
  checkboxStyle,
  sliderStyle
} from './styles';

const GridSubsection = ({
  gridExpanded,
  setGridExpanded,
  xGridVisible,
  setXGridVisible,
  yGridVisible,
  setYGridVisible,
  xMinorGridVisible,
  setXMinorGridVisible,
  yMinorGridVisible,
  setYMinorGridVisible,
  gridOpacity,
  setGridOpacity,
  gridColor,
  setGridColor
}) => {
  return (
    <div style={subsectionStyle}>
      <div 
        style={subsectionHeaderStyle}
        onClick={() => setGridExpanded(!gridExpanded)}
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--hover-background)'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <GridIcon size={20} />
          <span style={{ fontSize: '0.9rem', fontWeight: '600', color: 'var(--text-color)' }}>Grid</span>
        </span>
        <span style={chevronStyle(gridExpanded)}>›</span>
      </div>
      
      {gridExpanded && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {/* X-axis Grid Lines */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <label style={{ ...labelStyle, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <input
                type="checkbox"
                checked={xGridVisible}
                onChange={(e) => setXGridVisible(e.target.checked)}
                style={checkboxStyle}
              />
              X-axis major
            </label>
            <label style={{ ...labelStyle, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <input
                type="checkbox"
                checked={xMinorGridVisible}
                onChange={(e) => setXMinorGridVisible(e.target.checked)}
                style={checkboxStyle}
              />
              X-axis minor
            </label>
          </div>
          
          {/* Y-axis Grid Lines */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <label style={{ ...labelStyle, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <input
                type="checkbox"
                checked={yGridVisible}
                onChange={(e) => setYGridVisible(e.target.checked)}
                style={checkboxStyle}
              />
              Y-axis major
            </label>
            <label style={{ ...labelStyle, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <input
                type="checkbox"
                checked={yMinorGridVisible}
                onChange={(e) => setYMinorGridVisible(e.target.checked)}
                style={checkboxStyle}
              />
              Y-axis minor
            </label>
          </div>
          
          {/* Grid Opacity and Color */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
              <label style={labelStyle}>Opacity:</label>
              <input
                type="range"
                min="0"
                max="100"
                value={Math.round(gridOpacity * 100)}
                onChange={(e) => setGridOpacity(e.target.value / 100)}
                style={{ ...sliderStyle, flex: 1 }}
              />
              <span style={{ minWidth: '40px', color: 'var(--text-color)', fontSize: '0.85rem' }}>
                {Math.round(gridOpacity * 100)}%
              </span>
            </div>
            <ColorPickerIcon
              icon={FillIcon}
              color={gridColor || '#808080'}
              onChange={(e) => setGridColor(e.target.value)}
              title="Grid color"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default GridSubsection;