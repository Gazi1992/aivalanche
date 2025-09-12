import React from 'react';
import TitleSubsection from './TitleSubsection';
import AxisSubsection from './AxisSubsection';
import LegendSubsection from './LegendSubsection';
import GridSubsection from './GridSubsection';
import TextSubsection from './TextSubsection';
import DataSubsection from './DataSubsection';
import { PaletteIcon, ResetIcon } from '../icons';
import PlotButton from '../PlotButton';
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
  hasData,
  metadata,
  titleState,
  xAxisState,
  yAxisState,
  legendState,
  gridState,
  backgroundState,
  textState,
  dataState,
  onTextBlur,
  updateLegendItem,
  updateTraceProperty,
  onResetAppearance
}) => {
  return (
    <div style={sectionStyle}>
      <div style={{ position: 'relative' }}>
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {appearanceExpanded && onResetAppearance && (
              <div style={{ marginRight: '8px' }}>
                <PlotButton
                  onClick={(e) => {
                    e.stopPropagation();
                    onResetAppearance();
                  }}
                  title="Reset to Original"
                  icon={ResetIcon}
                  className="reset-button"
                />
              </div>
            )}
            <span style={chevronStyle(appearanceExpanded)}>›</span>
          </div>
        </div>
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
            titleAlignment={titleState.alignment}
            setTitleAlignment={titleState.setAlignment}
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
                metadata={metadata}
                yAxisScale={yAxisState.scale}
                setYAxisScale={yAxisState.setScale}
                yAxisMin={yAxisState.minValue}
                setYAxisMin={yAxisState.setMinValue}
                yAxisMax={yAxisState.maxValue}
                setYAxisMax={yAxisState.setMaxValue}
                yAxisInverted={yAxisState.inverted}
                setYAxisInverted={yAxisState.setInverted}
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
                gridColor={gridState.gridColor}
                setGridColor={gridState.setGridColor}
                figureBackgroundColor={backgroundState.figureBackgroundColor}
                setFigureBackgroundColor={backgroundState.setFigureBackgroundColor}
                figureBorderColor={backgroundState.figureBorderColor}
                setFigureBorderColor={backgroundState.setFigureBorderColor}
                plotBackgroundColor={backgroundState.plotBackgroundColor}
                setPlotBackgroundColor={backgroundState.setPlotBackgroundColor}
                plotBorderColor={backgroundState.plotBorderColor}
                setPlotBorderColor={backgroundState.setPlotBorderColor}
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
            />
          )}

          {hasData && (
            <DataSubsection
              dataExpanded={dataState.expanded}
              setDataExpanded={dataState.setExpanded}
              traces={dataState.traces}
              selectedTraceIndex={dataState.selectedTraceIndex}
              setSelectedTraceIndex={dataState.setSelectedTraceIndex}
              traceProperties={dataState.traceProperties}
              updateTraceProperty={updateTraceProperty}
              availableColumns={dataState.availableColumns}
              onBlur={onTextBlur}
            />
          )}

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
            legendTextColor={textState.legendTextColor}
            setLegendTextColor={textState.setLegendTextColor}
            hasLegend={textState.hasLegend}
          />
        </div>
      )}
    </div>
  );
};

export default AppearanceSection;