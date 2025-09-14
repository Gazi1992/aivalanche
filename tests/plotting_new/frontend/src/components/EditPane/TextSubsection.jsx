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
  legendTextColor,
  setLegendTextColor,
  plotCapabilities = {}
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
          {/* Title - Only show if plot has title capability */}
          {plotCapabilities.hasTitle && (
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
          )}

          {/* Axis Labels - Only show if plot has axis labels */}
          {plotCapabilities.hasAxisLabels && (
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
          )}

          {/* Axis Ticks - Only show if plot has axis ticks */}
          {plotCapabilities.hasAxisTicks && (
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
          )}

          {/* Legend - Only show if plot has legend */}
          {plotCapabilities.hasLegend && (
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
                color={legendTextColor || '#000000'}
                onChange={(e) => setLegendTextColor(e.target.value)}
                title="Legend text color"
              />
            </div>
          )}

          {/* Data Labels - For plots like pie, sankey */}
          {plotCapabilities.hasDataLabels && (
            <div style={textItemStyle}>
              <label style={textLabelStyle}>Data Labels</label>
              <input
                type="number"
                value={10}
                style={{ ...inputStyle, width: '60px' }}
                min="8"
                max="36"
                disabled
              />
              <div></div>
              <ToggleButton active={false} disabled>B</ToggleButton>
              <ToggleButton active={false} disabled><i>I</i></ToggleButton>
              <ColorPickerIcon
                icon={FillIcon}
                color={'#444444'}
                onChange={() => {}}
                title="Data label color"
                disabled
              />
            </div>
          )}

          {/* Node Labels - For Sankey diagrams */}
          {plotCapabilities.hasNodeLabels && (
            <div style={textItemStyle}>
              <label style={textLabelStyle}>Node Labels</label>
              <input
                type="number"
                value={12}
                style={{ ...inputStyle, width: '60px' }}
                min="8"
                max="36"
                disabled
              />
              <div></div>
              <ToggleButton active={false} disabled>B</ToggleButton>
              <ToggleButton active={false} disabled><i>I</i></ToggleButton>
              <ColorPickerIcon
                icon={FillIcon}
                color={'#444444'}
                onChange={() => {}}
                title="Node label color"
                disabled
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TextSubsection;