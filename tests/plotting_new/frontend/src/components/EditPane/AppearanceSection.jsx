import React from 'react';
import LabelsSubsection from './LabelsSubsection';
import AxisSubsection from './AxisSubsection';
import LegendSubsection from './LegendSubsection';
import GridSubsection from './GridSubsection';
import BackgroundSubsection from './BackgroundSubsection';
import TextSubsection from './TextSubsection';
import { PaletteIcon } from '../icons';
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
  gridState,
  backgroundState,
  textState,
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
        <span style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '600', color: 'var(--text-color)' }}>
          <PaletteIcon size={20} />
          Appearance
        </span>
        <span style={chevronStyle(appearanceExpanded)}>›</span>
      </div>
      
      {appearanceExpanded && (
        <div style={sectionContentStyle}>
          <LabelsSubsection 
            labelsExpanded={titleState.expanded}
            setLabelsExpanded={titleState.setExpanded}
            titleVisible={titleState.visible}
            setTitleVisible={titleState.setVisible}
            titleText={titleState.text}
            setTitleText={titleState.setText}
            titleAlignment={titleState.alignment}
            setTitleAlignment={titleState.setAlignment}
            xAxisLabelVisible={xAxisState.labelVisible}
            setXAxisLabelVisible={xAxisState.setLabelVisible}
            xAxisLabel={xAxisState.label}
            setXAxisLabel={xAxisState.setLabel}
            yAxisLabelVisible={yAxisState.labelVisible}
            setYAxisLabelVisible={yAxisState.setLabelVisible}
            yAxisLabel={yAxisState.label}
            setYAxisLabel={yAxisState.setLabel}
            xAxisTicksVisible={xAxisState.ticksVisible}
            setXAxisTicksVisible={xAxisState.setTicksVisible}
            yAxisTicksVisible={yAxisState.ticksVisible}
            setYAxisTicksVisible={yAxisState.setTicksVisible}
            onBlur={onTextBlur}
          />

          {hasAxes && (
            <>
              <AxisSubsection
                axisExpanded={xAxisState.expanded}
                setAxisExpanded={xAxisState.setExpanded}
                xAxisScale={xAxisState.scale}
                setXAxisScale={xAxisState.setScale}
                xAxisMin={xAxisState.minValue}
                setXAxisMin={xAxisState.setMinValue}
                xAxisMax={xAxisState.maxValue}
                setXAxisMax={xAxisState.setMaxValue}
                xAxisInverted={xAxisState.inverted}
                setXAxisInverted={xAxisState.setInverted}
                yAxisScale={yAxisState.scale}
                setYAxisScale={yAxisState.setScale}
                yAxisMin={yAxisState.minValue}
                setYAxisMin={yAxisState.setMinValue}
                yAxisMax={yAxisState.maxValue}
                setYAxisMax={yAxisState.setMaxValue}
                yAxisInverted={yAxisState.inverted}
                setYAxisInverted={yAxisState.setInverted}
                onBlur={onTextBlur}
              />

              <GridSubsection
                gridExpanded={gridState.expanded}
                setGridExpanded={gridState.setExpanded}
                xGridVisible={gridState.xGridVisible}
                setXGridVisible={gridState.setXGridVisible}
                yGridVisible={gridState.yGridVisible}
                setYGridVisible={gridState.setYGridVisible}
                xMinorGridVisible={gridState.xMinorGridVisible}
                setXMinorGridVisible={gridState.setXMinorGridVisible}
                yMinorGridVisible={gridState.yMinorGridVisible}
                setYMinorGridVisible={gridState.setYMinorGridVisible}
                gridOpacity={gridState.gridOpacity}
                setGridOpacity={gridState.setGridOpacity}
                gridColor={gridState.gridColor}
                setGridColor={gridState.setGridColor}
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
              legendBackgroundColor={legendState.backgroundColor}
              setLegendBackgroundColor={legendState.setBackgroundColor}
              legendBorderColor={legendState.borderColor}
              setLegendBorderColor={legendState.setBorderColor}
              legendBackgroundOpacity={legendState.backgroundOpacity}
              setLegendBackgroundOpacity={legendState.setBackgroundOpacity}
            />
          )}

          <BackgroundSubsection
            backgroundExpanded={backgroundState.expanded}
            setBackgroundExpanded={backgroundState.setExpanded}
            figureBackgroundColor={backgroundState.figureBackgroundColor}
            setFigureBackgroundColor={backgroundState.setFigureBackgroundColor}
            figureBorderColor={backgroundState.figureBorderColor}
            setFigureBorderColor={backgroundState.setFigureBorderColor}
            plotBackgroundColor={backgroundState.plotBackgroundColor}
            setPlotBackgroundColor={backgroundState.setPlotBackgroundColor}
            plotBorderColor={backgroundState.plotBorderColor}
            setPlotBorderColor={backgroundState.setPlotBorderColor}
          />

          <TextSubsection
            textExpanded={textState.expanded}
            setTextExpanded={textState.setExpanded}
            titleFontSize={textState.titleFontSize}
            setTitleFontSize={textState.setTitleFontSize}
            titleBold={textState.titleBold}
            setTitleBold={textState.setTitleBold}
            titleItalic={textState.titleItalic}
            setTitleItalic={textState.setTitleItalic}
            titleColor={textState.titleColor}
            setTitleColor={textState.setTitleColor}
            axisLabelFontSize={textState.axisLabelFontSize}
            setAxisLabelFontSize={textState.setAxisLabelFontSize}
            axisLabelBold={textState.axisLabelBold}
            setAxisLabelBold={textState.setAxisLabelBold}
            axisLabelItalic={textState.axisLabelItalic}
            setAxisLabelItalic={textState.setAxisLabelItalic}
            axisLabelColor={textState.axisLabelColor}
            setAxisLabelColor={textState.setAxisLabelColor}
            axisTickFontSize={textState.axisTickFontSize}
            setAxisTickFontSize={textState.setAxisTickFontSize}
            axisTickColor={textState.axisTickColor}
            setAxisTickColor={textState.setAxisTickColor}
            legendFontSize={textState.legendFontSize}
            setLegendFontSize={textState.setLegendFontSize}
            legendBold={textState.legendBold}
            setLegendBold={textState.setLegendBold}
            legendItalic={textState.legendItalic}
            setLegendItalic={textState.setLegendItalic}
            legendColor={textState.legendColor}
            setLegendColor={textState.setLegendColor}
            hasLegend={textState.hasLegend}
          />
        </div>
      )}
    </div>
  );
};

export default AppearanceSection;