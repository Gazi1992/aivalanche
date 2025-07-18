import React from 'react';
import TitleSubsection from './TitleSubsection';
import AxisSubsection from './AxisSubsection';
import LegendSubsection from './LegendSubsection';
import { 
  sectionStyle, 
  sectionHeaderStyle, 
  sectionContentStyle,
  chevronStyle 
} from './styles';

const AppearanceSection = ({
  appearanceExpanded,
  setAppearanceExpanded,
  hasAxes,
  hasLegend,
  titleState,
  xAxisState,
  yAxisState,
  legendState,
  onTextBlur,
  updateLegendItem
}) => {
  return (
    <div style={sectionStyle}>
      <div 
        style={sectionHeaderStyle}
        onClick={() => setAppearanceExpanded(!appearanceExpanded)}
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--background-color)'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
      >
        <span style={{ fontWeight: '600', color: 'var(--text-color)' }}>Appearance</span>
        <span style={chevronStyle(appearanceExpanded)}>›</span>
      </div>
      
      {appearanceExpanded && (
        <div style={sectionContentStyle}>
          <TitleSubsection 
            titleExpanded={titleState.expanded}
            setTitleExpanded={titleState.setExpanded}
            titleVisible={titleState.visible}
            setTitleVisible={titleState.setVisible}
            titleText={titleState.text}
            setTitleText={titleState.setText}
            onBlur={onTextBlur}
          />

          {hasAxes && (
            <>
              <AxisSubsection
                axis="X"
                expanded={xAxisState.expanded}
                setExpanded={xAxisState.setExpanded}
                labelVisible={xAxisState.labelVisible}
                setLabelVisible={xAxisState.setLabelVisible}
                label={xAxisState.label}
                setLabel={xAxisState.setLabel}
                scale={xAxisState.scale}
                setScale={xAxisState.setScale}
                ticksVisible={xAxisState.ticksVisible}
                setTicksVisible={xAxisState.setTicksVisible}
                minValue={xAxisState.minValue}
                setMinValue={xAxisState.setMinValue}
                maxValue={xAxisState.maxValue}
                setMaxValue={xAxisState.setMaxValue}
                inverted={xAxisState.inverted}
                setInverted={xAxisState.setInverted}
                onBlur={onTextBlur}
              />

              <AxisSubsection
                axis="Y"
                expanded={yAxisState.expanded}
                setExpanded={yAxisState.setExpanded}
                labelVisible={yAxisState.labelVisible}
                setLabelVisible={yAxisState.setLabelVisible}
                label={yAxisState.label}
                setLabel={yAxisState.setLabel}
                scale={yAxisState.scale}
                setScale={yAxisState.setScale}
                ticksVisible={yAxisState.ticksVisible}
                setTicksVisible={yAxisState.setTicksVisible}
                minValue={yAxisState.minValue}
                setMinValue={yAxisState.setMinValue}
                maxValue={yAxisState.maxValue}
                setMaxValue={yAxisState.setMaxValue}
                inverted={yAxisState.inverted}
                setInverted={yAxisState.setInverted}
                onBlur={onTextBlur}
              />
            </>
          )}

          {hasLegend && (
            <LegendSubsection
              legendExpanded={legendState.expanded}
              setLegendExpanded={legendState.setExpanded}
              legendVisible={legendState.visible}
              setLegendVisible={legendState.setVisible}
              legendItems={legendState.items}
              updateLegendItem={updateLegendItem}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default AppearanceSection;