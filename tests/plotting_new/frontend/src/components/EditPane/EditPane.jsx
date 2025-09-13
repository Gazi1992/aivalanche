import React from 'react';
import { useFixedMetadata } from './useFixedMetadata';
import AppearanceSection from './AppearanceSection';
import { 
  overlayStyle, 
  headerStyle, 
  contentStyle,
  closeButtonStyle,
  backdropStyle 
} from './styles';

const EditPane = ({ isOpen, onClose, figure, onUpdate }) => {
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
  
  // Determine plot capabilities
  const hasAxes = capabilities.hasAxes !== false;
  const hasLegend = capabilities.hasLegend !== false;
  const hasData = figure?.data?.length > 0 && !capabilities.isParallelCoordinates && !capabilities.isScatterMatrix;
  
  // Add axis type info to metadata for AxisSubsection
  const enhancedMetadata = {
    ...metadata,
    xAxisType: figure?.xAxisType,
    yAxisType: figure?.yAxisType
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
            hasAxes={hasAxes}
            hasLegend={hasLegend}
            hasData={hasData}
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