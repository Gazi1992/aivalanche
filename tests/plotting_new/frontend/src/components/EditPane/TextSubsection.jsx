import React from 'react';
import { TextIcon, FillIcon } from '../icons';
import ColorPickerIcon from './ColorPickerIcon';
import { 
  subsectionStyle, 
  subsectionHeaderStyle, 
  subsectionTitleStyle, 
  chevronStyle,
  inputStyle,
  labelStyle,
  toggleButtonStyle
} from './styles';

const TextSubsection = ({ 
  textExpanded, 
  setTextExpanded,
  titleFontSize,
  setTitleFontSize,
  titleBold,
  setTitleBold,
  titleItalic,
  setTitleItalic,
  titleColor,
  setTitleColor,
  axisLabelFontSize,
  setAxisLabelFontSize,
  axisLabelBold,
  setAxisLabelBold,
  axisLabelItalic,
  setAxisLabelItalic,
  axisLabelColor,
  setAxisLabelColor,
  axisTickFontSize,
  setAxisTickFontSize,
  axisTickColor,
  setAxisTickColor,
  legendFontSize,
  setLegendFontSize,
  legendBold,
  setLegendBold,
  legendItalic,
  setLegendItalic,
  legendColor,
  setLegendColor,
  hasLegend
}) => {
  const textItemStyle = {
    display: 'grid',
    gridTemplateColumns: '100px 60px 10px 30px 30px 32px',
    gap: '8px',
    alignItems: 'center',
    marginBottom: '8px'
  };

  const textLabelStyle = {
    ...labelStyle,
    fontSize: '0.85rem'
  };

  const ToggleButton = ({ active, disabled, onClick, children }) => (
    <button
      style={toggleButtonStyle(active, disabled)}
      onClick={disabled ? undefined : onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );

  return (
    <div style={subsectionStyle}>
      <div 
        style={subsectionHeaderStyle}
        onClick={() => setTextExpanded(!textExpanded)}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <TextIcon size={20} />
          <span style={subsectionTitleStyle}>Text font</span>
        </span>
        <span style={chevronStyle(textExpanded)}>›</span>
      </div>
      
      {textExpanded && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {/* Title */}
          <div style={textItemStyle}>
            <label style={textLabelStyle}>Title</label>
            <input
              type="number"
              value={titleFontSize}
              onChange={(e) => setTitleFontSize(e.target.value)}
              style={{ ...inputStyle, width: '60px' }}
              min="8"
              max="72"
            />
            <div></div>
            <ToggleButton
              active={titleBold}
              onClick={() => setTitleBold(!titleBold)}
            >
              B
            </ToggleButton>
            <ToggleButton
              active={titleItalic}
              onClick={() => setTitleItalic(!titleItalic)}
            >
              <i>I</i>
            </ToggleButton>
            <ColorPickerIcon
              icon={FillIcon}
              color={titleColor || '#000000'}
              onChange={(e) => setTitleColor(e.target.value)}
              title="Title color"
            />
          </div>

          {/* Axis Labels */}
          <div style={textItemStyle}>
            <label style={textLabelStyle}>Axis Labels</label>
            <input
              type="number"
              value={axisLabelFontSize}
              onChange={(e) => setAxisLabelFontSize(e.target.value)}
              style={{ ...inputStyle, width: '60px' }}
              min="8"
              max="48"
            />
            <div></div>
            <ToggleButton
              active={axisLabelBold}
              onClick={() => setAxisLabelBold(!axisLabelBold)}
            >
              B
            </ToggleButton>
            <ToggleButton
              active={axisLabelItalic}
              onClick={() => setAxisLabelItalic(!axisLabelItalic)}
            >
              <i>I</i>
            </ToggleButton>
            <ColorPickerIcon
              icon={FillIcon}
              color={axisLabelColor || '#000000'}
              onChange={(e) => setAxisLabelColor(e.target.value)}
              title="Axis label color"
            />
          </div>

          {/* Axis Ticks */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '100px 60px 10px 30px',
            gap: '8px',
            alignItems: 'center',
            marginBottom: '8px'
          }}>
            <label style={textLabelStyle}>Axis Ticks</label>
            <input
              type="number"
              value={axisTickFontSize}
              onChange={(e) => setAxisTickFontSize(e.target.value)}
              style={{ ...inputStyle, width: '60px' }}
              min="6"
              max="36"
            />
            <div></div>
            <ColorPickerIcon
              icon={FillIcon}
              color={axisTickColor || '#000000'}
              onChange={(e) => setAxisTickColor(e.target.value)}
              title="Axis tick color"
            />
          </div>

          {/* Legend (conditional) */}
          {hasLegend && (
            <div style={textItemStyle}>
              <label style={textLabelStyle}>Legend</label>
              <input
                type="number"
                value={legendFontSize}
                onChange={(e) => setLegendFontSize(e.target.value)}
                style={{ ...inputStyle, width: '60px' }}
                min="8"
                max="36"
              />
              <div></div>
              <ToggleButton
                active={legendBold}
                onClick={() => setLegendBold(!legendBold)}
              >
                B
              </ToggleButton>
              <ToggleButton
                active={legendItalic}
                onClick={() => setLegendItalic(!legendItalic)}
              >
                <i>I</i>
              </ToggleButton>
              <ColorPickerIcon
                icon={FillIcon}
                color={legendColor || '#000000'}
                onChange={(e) => setLegendColor(e.target.value)}
                title="Legend color"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TextSubsection;