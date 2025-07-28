import React from 'react';
import AppearanceSection from './AppearanceSection';
import GridSubsection from './GridSubsection';
import { 
  overlayStyle, 
  headerStyle, 
  contentStyle,
  closeButtonStyle,
  backdropStyle 
} from './styles';
import { useEditPaneState } from './useEditPaneState';
import { useEditPaneUpdates } from './useEditPaneUpdates';

const EditPane = ({ isOpen, onClose, plotData, metadata, onUpdate }) => {
  // Use custom hooks for state management
  const state = useEditPaneState(plotData, isOpen);
  const { handleTextBlur } = useEditPaneUpdates(state, plotData, onUpdate);

  // Use metadata to determine plot capabilities
  const hasAxes = metadata?.hasAxes !== false;
  const hasLegend = !metadata?.isPcp && !metadata?.isSplom;

  const updateLegendItem = (id, field, value) => {
    state.setLegendItems(prev => prev.map(item => 
      item.id === id ? { ...item, [field]: value } : item
    ));
  };

  // Create state objects for subsections
  const titleState = {
    expanded: state.labelsExpanded,
    setExpanded: state.setLabelsExpanded,
    visible: state.titleVisible,
    setVisible: state.setTitleVisible,
    text: state.titleText,
    setText: state.setTitleText,
    alignment: state.titleAlignment,
    setAlignment: state.setTitleAlignment
  };

  const xAxisState = {
    expanded: state.axisExpanded,
    setExpanded: state.setAxisExpanded,
    labelVisible: state.xAxisLabelVisible,
    setLabelVisible: state.setXAxisLabelVisible,
    label: state.xAxisLabel,
    setLabel: state.setXAxisLabel,
    scale: state.xAxisScale,
    setScale: state.setXAxisScale,
    ticksVisible: state.xAxisTicksVisible,
    setTicksVisible: state.setXAxisTicksVisible,
    minValue: state.xAxisMin,
    setMinValue: state.setXAxisMin,
    maxValue: state.xAxisMax,
    setMaxValue: state.setXAxisMax,
    inverted: state.xAxisInverted,
    setInverted: state.setXAxisInverted
  };

  const yAxisState = {
    expanded: state.axisExpanded,
    setExpanded: state.setAxisExpanded,
    labelVisible: state.yAxisLabelVisible,
    setLabelVisible: state.setYAxisLabelVisible,
    label: state.yAxisLabel,
    setLabel: state.setYAxisLabel,
    scale: state.yAxisScale,
    setScale: state.setYAxisScale,
    ticksVisible: state.yAxisTicksVisible,
    setTicksVisible: state.setYAxisTicksVisible,
    minValue: state.yAxisMin,
    setMinValue: state.setYAxisMin,
    maxValue: state.yAxisMax,
    setMaxValue: state.setYAxisMax,
    inverted: state.yAxisInverted,
    setInverted: state.setYAxisInverted
  };

  const legendState = {
    expanded: state.legendExpanded,
    setExpanded: state.setLegendExpanded,
    visible: state.legendVisible,
    setVisible: state.setLegendVisible,
    items: state.legendItems,
    backgroundColor: state.legendBackgroundColor,
    setBackgroundColor: state.setLegendBackgroundColor,
    borderColor: state.legendBorderColor,
    setBorderColor: state.setLegendBorderColor
  };

  const gridState = {
    expanded: state.gridExpanded,
    setExpanded: state.setGridExpanded,
    xGridVisible: state.xGridVisible,
    setXGridVisible: state.setXGridVisible,
    yGridVisible: state.yGridVisible,
    setYGridVisible: state.setYGridVisible,
    xMinorGridVisible: state.xMinorGridVisible,
    setXMinorGridVisible: state.setXMinorGridVisible,
    yMinorGridVisible: state.yMinorGridVisible,
    setYMinorGridVisible: state.setYMinorGridVisible,
    gridColor: state.gridColor,
    setGridColor: state.setGridColor
  };
  
  const backgroundState = {
    figureBackgroundColor: state.figureBackgroundColor,
    setFigureBackgroundColor: state.setFigureBackgroundColor,
    figureBorderColor: state.figureBorderColor,
    setFigureBorderColor: state.setFigureBorderColor,
    plotBackgroundColor: state.plotBackgroundColor,
    setPlotBackgroundColor: state.setPlotBackgroundColor,
    plotBorderColor: state.plotBorderColor,
    setPlotBorderColor: state.setPlotBorderColor
  };
  
  const textState = {
    expanded: state.textExpanded,
    setExpanded: state.setTextExpanded,
    titleFontSize: state.titleFontSize,
    setTitleFontSize: state.setTitleFontSize,
    titleBold: state.titleBold,
    setTitleBold: state.setTitleBold,
    titleItalic: state.titleItalic,
    setTitleItalic: state.setTitleItalic,
    titleColor: state.titleColor,
    setTitleColor: state.setTitleColor,
    axisLabelFontSize: state.axisLabelFontSize,
    setAxisLabelFontSize: state.setAxisLabelFontSize,
    axisLabelBold: state.axisLabelBold,
    setAxisLabelBold: state.setAxisLabelBold,
    axisLabelItalic: state.axisLabelItalic,
    setAxisLabelItalic: state.setAxisLabelItalic,
    axisLabelColor: state.axisLabelColor,
    setAxisLabelColor: state.setAxisLabelColor,
    axisTickFontSize: state.axisTickFontSize,
    setAxisTickFontSize: state.setAxisTickFontSize,
    axisTickColor: state.axisTickColor,
    setAxisTickColor: state.setAxisTickColor,
    legendFontSize: state.legendFontSize,
    setLegendFontSize: state.setLegendFontSize,
    legendBold: state.legendBold,
    setLegendBold: state.setLegendBold,
    legendItalic: state.legendItalic,
    setLegendItalic: state.setLegendItalic,
    legendTextColor: state.legendTextColor,
    setLegendTextColor: state.setLegendTextColor,
    hasLegend
  };
  
  // Extract traces and columns for data subsection
  const traces = plotData?.data || [];
  const hasData = traces.length > 0 && !metadata?.isPcp && !metadata?.isSplom;
  
  // Get available columns from the first dataset
  const availableColumns = [];
  if (metadata?.datasets) {
    const firstDataset = Object.values(metadata.datasets)[0];
    if (firstDataset?.columns) {
      availableColumns.push(...firstDataset.columns);
    }
  }
  
  const dataState = {
    expanded: state.dataExpanded,
    setExpanded: state.setDataExpanded,
    traces: traces,
    selectedTraceIndex: state.selectedTraceIndex,
    setSelectedTraceIndex: state.setSelectedTraceIndex,
    traceProperties: state.traceProperties,
    availableColumns: availableColumns
  };
  
  const updateTraceProperty = (traceIndex, property, value) => {
    state.setTraceProperties(prev => ({
      ...prev,
      [traceIndex]: {
        ...prev[traceIndex],
        [property]: value
      }
    }));
  };

  return (
    <>
      <div style={{ ...overlayStyle, left: isOpen ? 0 : '-500px' }}>
        <div style={headerStyle}>
          <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--text-color)' }}>
            Edit Plot
          </h3>
          <button onClick={onClose} style={closeButtonStyle}>
            ×
          </button>
        </div>
        
        <div style={contentStyle}>
          <AppearanceSection
            appearanceExpanded={state.appearanceExpanded}
            setAppearanceExpanded={state.setAppearanceExpanded}
            hasAxes={hasAxes}
            hasLegend={hasLegend}
            hasData={hasData}
            titleState={titleState}
            xAxisState={xAxisState}
            yAxisState={yAxisState}
            legendState={legendState}
            gridState={gridState}
            backgroundState={backgroundState}
            textState={textState}
            dataState={dataState}
            onTextBlur={handleTextBlur}
            updateLegendItem={updateLegendItem}
            updateTraceProperty={updateTraceProperty}
          />
        </div>
      </div>
      
      {isOpen && <div style={backdropStyle} onClick={onClose} />}
    </>
  );
};

export default EditPane;