import React from 'react';
import { BackgroundIcon, BorderIcon, FillIcon } from '../icons';
import ColorPickerIcon from './ColorPickerIcon';
import { 
  subsectionStyle, 
  subsectionHeaderStyle, 
  subsectionTitleStyle, 
  chevronStyle,
  labelStyle
} from './styles';

const BackgroundSubsection = ({ 
  backgroundExpanded, 
  setBackgroundExpanded,
  figureBackgroundColor,
  setFigureBackgroundColor,
  figureBorderColor,
  setFigureBorderColor,
  plotBackgroundColor,
  setPlotBackgroundColor,
  plotBorderColor,
  setPlotBorderColor
}) => {
  const itemStyle = {
    display: 'grid',
    gridTemplateColumns: '80px 1fr 32px 32px',
    gap: '8px',
    alignItems: 'center',
    marginBottom: '10px'
  };

  return (
    <div style={subsectionStyle}>
      <div 
        style={subsectionHeaderStyle}
        onClick={() => setBackgroundExpanded(!backgroundExpanded)}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <BackgroundIcon size={20} />
          <span style={subsectionTitleStyle}>Background</span>
        </span>
        <span style={chevronStyle(backgroundExpanded)}>›</span>
      </div>
      
      {backgroundExpanded && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {/* Figure Row */}
          <div style={itemStyle}>
            <label style={labelStyle}>Figure</label>
            <div></div>
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
          
          {/* Plot Area Row */}
          <div style={itemStyle}>
            <label style={labelStyle}>Plot Area</label>
            <div></div>
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
      )}
    </div>
  );
};

export default BackgroundSubsection;