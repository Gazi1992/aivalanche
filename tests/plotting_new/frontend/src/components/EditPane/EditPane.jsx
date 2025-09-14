import React from 'react';
import { useFixedMetadata } from './useFixedMetadata';
import AppearanceSection from './AppearanceSection';
import { detectPlotType, getPlotCapabilities } from '../../utils/plotCapabilities';
import {
  overlayStyle,
  headerStyle,
  contentStyle,
  closeButtonStyle,
  backdropStyle
} from './styles';

const EditPane = ({ isOpen, onClose, figure, onUpdate }) => {
  // Early return if no figure
  if (!figure) {
    return null;
  }

  const {
    metadata,
    expansions,
    capabilities,
    toggleExpansion,
    resetAppearance,
    handleBlur,
    createSubsectionProps,
    updateLegendItem,
    updateTraceProperty
  } = useFixedMetadata(figure, isOpen, onUpdate);

  // Detect plot type and get comprehensive capabilities
  const plotType = detectPlotType(figure);
  const plotCapabilities = getPlotCapabilities(plotType);

  // Use the comprehensive capabilities
  const hasTitle = plotCapabilities.hasTitle;
  const hasAxes = plotCapabilities.hasAxes;
  const hasLegend = plotCapabilities.hasLegend;
  const hasGrid = plotCapabilities.hasGrid;
  const hasData = figure?.data?.length > 0 && !plotCapabilities.isParallelCoordinates && !plotCapabilities.isScatterMatrix;
  
  // Add axis type info and capabilities to metadata
  const enhancedMetadata = {
    ...metadata,
    xAxisType: figure?.xAxisType,
    yAxisType: figure?.yAxisType,
    plotCapabilities
  };
  
  // Get subsection props from the hook
  const props = createSubsectionProps();
  
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
            appearanceExpanded={expansions.appearance}
            setAppearanceExpanded={() => toggleExpansion('appearance')}
            hasTitle={hasTitle}
            hasAxes={hasAxes}
            hasLegend={hasLegend}
            hasGrid={hasGrid}
            hasData={hasData}
            plotCapabilities={plotCapabilities}
            metadata={enhancedMetadata}
            titleState={props.titleState}
            xAxisState={props.xAxisState}
            yAxisState={props.yAxisState}
            legendState={props.legendState}
            gridState={props.gridState}
            backgroundState={props.backgroundState}
            textState={props.textState}
            dataState={props.dataState}
            onTextBlur={handleBlur}
            updateLegendItem={updateLegendItem}
            updateTraceProperty={updateTraceProperty}
            onResetAppearance={resetAppearance}
          />
        </div>
      </div>
      
      {isOpen && <div style={backdropStyle} onClick={onClose} />}
    </>
  );
};

export default EditPane;