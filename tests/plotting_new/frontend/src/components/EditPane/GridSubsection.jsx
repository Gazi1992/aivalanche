import React from 'react';
import { GridIcon, BorderIcon, FillIcon } from '../icons';
import ColorPickerIcon from './ColorPickerIcon';
import { 
  subsectionStyle, 
  subsectionHeaderStyle, 
  chevronStyle,
  fieldContainerStyle,
  labelStyle,
  checkboxStyle
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
  gridColor,
  setGridColor,
  figureBackgroundColor,
  setFigureBackgroundColor,
  figureBorderColor,
  setFigureBorderColor,
  plotBackgroundColor,
  setPlotBackgroundColor,
  plotBorderColor,
  setPlotBorderColor
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
          <span style={{ fontSize: '0.9rem', fontWeight: '600', color: 'var(--text-color)' }}>Grid & Figure</span>
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
          
          {/* All color options in one line */}
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            width: '100%',
            marginTop: '8px'
          }}>
            {/* Grid */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <label style={{ ...labelStyle, fontSize: '0.85rem' }}>Grid:</label>
              <ColorPickerIcon
                icon={BorderIcon}
                color={gridColor || '#808080'}
                onChange={(e) => setGridColor(e.target.value)}
                title="Grid color"
              />
            </div>
            
            {/* Vertical Divider */}
            <div style={{ 
              width: '1px', 
              height: '24px', 
              backgroundColor: 'var(--border-color)',
              marginLeft: 'auto',
              marginRight: 'auto'
            }} />
            
            {/* Figure */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <label style={{ ...labelStyle, fontSize: '0.85rem' }}>Figure:</label>
              <ColorPickerIcon
                icon={FillIcon}
                color={figureBackgroundColor}
                onChange={(e) => setFigureBackgroundColor(e.target.value)}
                title="Figure background color"
              />
              <ColorPickerIcon
                icon={BorderIcon}
                color={figureBorderColor}
                onChange={(e) => setFigureBorderColor(e.target.value)}
                title="Figure border color"
              />
            </div>
            
            {/* Vertical Divider */}
            <div style={{ 
              width: '1px', 
              height: '24px', 
              backgroundColor: 'var(--border-color)',
              marginLeft: 'auto',
              marginRight: 'auto'
            }} />
            
            {/* Plot Area */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <label style={{ ...labelStyle, fontSize: '0.85rem', whiteSpace: 'nowrap' }}>Plot Area:</label>
              <ColorPickerIcon
                icon={FillIcon}
                color={plotBackgroundColor}
                onChange={(e) => setPlotBackgroundColor(e.target.value)}
                title="Plot area background color"
              />
              <ColorPickerIcon
                icon={BorderIcon}
                color={plotBorderColor}
                onChange={(e) => setPlotBorderColor(e.target.value)}
                title="Plot area border color"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GridSubsection;