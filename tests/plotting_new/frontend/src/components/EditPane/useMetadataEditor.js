import { useReducer, useEffect, useRef, useCallback } from 'react';
import { 
  extractMetadataFromFigure, 
  applyMetadataToFigure,
  trackUserCustomization,
  resetToOriginal 
} from '../../utils/plotMetadata';

// Action types
const ACTIONS = {
  INIT_METADATA: 'INIT_METADATA',
  UPDATE_METADATA: 'UPDATE_METADATA',
  TOGGLE_EXPANSION: 'TOGGLE_EXPANSION',
  RESET_TO_ORIGINAL: 'RESET_TO_ORIGINAL'
};

// Initial state
const createInitialState = () => ({
  metadata: null,
  expansions: {
    appearance: true,
    labels: false,
    axis: false,
    legend: false,
    grid: false,
    text: false,
    data: false
  }
});

// Reducer function
const metadataReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.INIT_METADATA:
      return {
        ...state,
        metadata: action.payload
      };
      
    case ACTIONS.UPDATE_METADATA:
      return {
        ...state,
        metadata: updateMetadataPath(state.metadata, action.payload.path, action.payload.value)
      };
      
    case ACTIONS.TOGGLE_EXPANSION:
      return {
        ...state,
        expansions: {
          ...state.expansions,
          [action.payload]: !state.expansions[action.payload]
        }
      };
      
    case ACTIONS.RESET_TO_ORIGINAL:
      return {
        ...state,
        metadata: resetToOriginal(state.metadata)
      };
      
    default:
      return state;
  }
};

// Helper to update a specific path in metadata
const updateMetadataPath = (metadata, path, value) => {
  if (!metadata) return metadata;
  
  const updated = JSON.parse(JSON.stringify(metadata));
  const parts = path.split('.');
  let current = updated;
  
  for (let i = 0; i < parts.length - 1; i++) {
    if (!current[parts[i]]) {
      current[parts[i]] = {};
    }
    current = current[parts[i]];
  }
  
  current[parts[parts.length - 1]] = value;
  
  // Track this as a user customization
  return trackUserCustomization(updated, path);
};

// Main hook
export const useMetadataEditor = (plotData, initialMetadata, isOpen, onUpdate) => {
  const [state, dispatch] = useReducer(metadataReducer, null, createInitialState);
  const updateTimer = useRef(null);
  const isInitialMount = useRef(true);
  const lastPlotId = useRef(null);
  
  // Initialize metadata when EditPane opens
  useEffect(() => {
    if (isOpen && plotData) {
      const plotId = plotData.id || JSON.stringify(plotData.layout?.title);
      
      if (plotId !== lastPlotId.current) {
        // Extract metadata from the figure or use provided metadata
        const metadata = initialMetadata || extractMetadataFromFigure(plotData);
        dispatch({ type: ACTIONS.INIT_METADATA, payload: metadata });
        lastPlotId.current = plotId;
        
        // Mark as initialized after a delay
        setTimeout(() => {
          isInitialMount.current = false;
        }, 500);
      }
    } else if (!isOpen) {
      isInitialMount.current = true;
      lastPlotId.current = null;
    }
  }, [isOpen, plotData, initialMetadata]);
  
  // Apply metadata changes to figure
  const applyChanges = useCallback(() => {
    if (!plotData || !state.metadata || isInitialMount.current) return;
    
    const updatedFigure = applyMetadataToFigure(plotData, state.metadata);
    onUpdate(updatedFigure, state.metadata);
  }, [state.metadata, plotData, onUpdate]);
  
  // Debounced update effect
  useEffect(() => {
    if (isInitialMount.current) return;
    
    if (updateTimer.current) {
      clearTimeout(updateTimer.current);
    }
    
    updateTimer.current = setTimeout(() => {
      applyChanges();
    }, 300);
    
    return () => {
      if (updateTimer.current) {
        clearTimeout(updateTimer.current);
      }
    };
  }, [state.metadata, applyChanges]);
  
  // Immediate update on blur
  const handleBlur = useCallback(() => {
    if (updateTimer.current) {
      clearTimeout(updateTimer.current);
    }
    applyChanges();
  }, [applyChanges]);
  
  // Update functions
  const updateMetadata = useCallback((path, value) => {
    dispatch({ type: ACTIONS.UPDATE_METADATA, payload: { path, value } });
  }, []);
  
  const toggleExpansion = useCallback((section) => {
    dispatch({ type: ACTIONS.TOGGLE_EXPANSION, payload: section });
  }, []);
  
  const reset = useCallback(() => {
    dispatch({ type: ACTIONS.RESET_TO_ORIGINAL });
  }, []);
  
  // Create props for subsections based on metadata
  const createSubsectionProps = () => {
    if (!state.metadata) {
      return {
        titleState: {},
        xAxisState: {},
        yAxisState: {},
        legendState: {},
        gridState: {},
        backgroundState: {},
        textState: {},
        dataState: {}
      };
    }
    
    const m = state.metadata;
    
    return {
      // Title subsection
      titleState: {
        expanded: state.expansions.labels,
        setExpanded: () => toggleExpansion('labels'),
        visible: m.title?.visible ?? true,
        setVisible: (v) => updateMetadata('title.visible', v),
        text: m.title?.text ?? '',
        setText: (v) => updateMetadata('title.text', v),
        alignment: m.title?.alignment ?? 'center',
        setAlignment: (v) => updateMetadata('title.alignment', v)
      },
      
      // X-Axis subsection
      xAxisState: {
        expanded: state.expansions.axis,
        setExpanded: () => toggleExpansion('axis'),
        labelVisible: m.axes?.x?.label?.visible ?? true,
        setLabelVisible: (v) => updateMetadata('axes.x.label.visible', v),
        label: m.axes?.x?.label?.text ?? '',
        setLabel: (v) => updateMetadata('axes.x.label.text', v),
        scale: m.axes?.x?.type ?? 'linear',
        setScale: (v) => updateMetadata('axes.x.type', v),
        ticksVisible: m.axes?.x?.ticks?.visible ?? true,
        setTicksVisible: (v) => updateMetadata('axes.x.ticks.visible', v),
        minValue: m.axes?.x?.range?.min?.toString() ?? '',
        setMinValue: (v) => updateMetadata('axes.x.range.min', v ? parseFloat(v) : null),
        maxValue: m.axes?.x?.range?.max?.toString() ?? '',
        setMaxValue: (v) => updateMetadata('axes.x.range.max', v ? parseFloat(v) : null),
        inverted: m.axes?.x?.range?.reversed ?? false,
        setInverted: (v) => updateMetadata('axes.x.range.reversed', v)
      },
      
      // Y-Axis subsection
      yAxisState: {
        expanded: state.expansions.axis,
        setExpanded: () => toggleExpansion('axis'),
        labelVisible: m.axes?.y?.label?.visible ?? true,
        setLabelVisible: (v) => updateMetadata('axes.y.label.visible', v),
        label: m.axes?.y?.label?.text ?? '',
        setLabel: (v) => updateMetadata('axes.y.label.text', v),
        scale: m.axes?.y?.type ?? 'linear',
        setScale: (v) => updateMetadata('axes.y.type', v),
        ticksVisible: m.axes?.y?.ticks?.visible ?? true,
        setTicksVisible: (v) => updateMetadata('axes.y.ticks.visible', v),
        minValue: m.axes?.y?.range?.min?.toString() ?? '',
        setMinValue: (v) => updateMetadata('axes.y.range.min', v ? parseFloat(v) : null),
        maxValue: m.axes?.y?.range?.max?.toString() ?? '',
        setMaxValue: (v) => updateMetadata('axes.y.range.max', v ? parseFloat(v) : null),
        inverted: m.axes?.y?.range?.reversed ?? false,
        setInverted: (v) => updateMetadata('axes.y.range.reversed', v)
      },
      
      // Legend subsection
      legendState: {
        expanded: state.expansions.legend,
        setExpanded: () => toggleExpansion('legend'),
        visible: m.legend?.visible ?? true,
        setVisible: (v) => updateMetadata('legend.visible', v),
        items: m.legend?.items ?? [],
        backgroundColor: m.legend?.backgroundColor ?? 'rgba(255, 255, 255, 0)',
        setBackgroundColor: (v) => updateMetadata('legend.backgroundColor', v),
        borderColor: m.legend?.borderColor ?? '#444',
        setBorderColor: (v) => updateMetadata('legend.borderColor', v)
      },
      
      // Grid subsection
      gridState: {
        expanded: state.expansions.grid,
        setExpanded: () => toggleExpansion('grid'),
        xGridVisible: m.axes?.x?.grid?.visible ?? true,
        setXGridVisible: (v) => updateMetadata('axes.x.grid.visible', v),
        yGridVisible: m.axes?.y?.grid?.visible ?? true,
        setYGridVisible: (v) => updateMetadata('axes.y.grid.visible', v),
        xMinorGridVisible: m.axes?.x?.minorGrid?.visible ?? false,
        setXMinorGridVisible: (v) => updateMetadata('axes.x.minorGrid.visible', v),
        yMinorGridVisible: m.axes?.y?.minorGrid?.visible ?? false,
        setYMinorGridVisible: (v) => updateMetadata('axes.y.minorGrid.visible', v),
        gridColor: m.axes?.x?.grid?.color ?? 'rgba(128, 128, 128, 0.2)',
        setGridColor: (v) => {
          updateMetadata('axes.x.grid.color', v);
          updateMetadata('axes.y.grid.color', v);
        }
      },
      
      // Background subsection
      backgroundState: {
        figureBackgroundColor: m.appearance?.figure?.backgroundColor ?? '#ffffff',
        setFigureBackgroundColor: (v) => updateMetadata('appearance.figure.backgroundColor', v),
        figureBorderColor: m.appearance?.figure?.borderColor ?? '#000000',
        setFigureBorderColor: (v) => updateMetadata('appearance.figure.borderColor', v),
        plotBackgroundColor: m.appearance?.plot?.backgroundColor ?? 'rgba(255, 255, 255, 0)',
        setPlotBackgroundColor: (v) => updateMetadata('appearance.plot.backgroundColor', v),
        plotBorderColor: m.appearance?.plot?.borderColor ?? '#444',
        setPlotBorderColor: (v) => updateMetadata('appearance.plot.borderColor', v)
      },
      
      // Text subsection
      textState: {
        expanded: state.expansions.text,
        setExpanded: () => toggleExpansion('text'),
        titleFontSize: m.title?.fontSize ?? 16,
        setTitleFontSize: (v) => updateMetadata('title.fontSize', v),
        titleBold: m.title?.bold ?? false,
        setTitleBold: (v) => updateMetadata('title.bold', v),
        titleItalic: m.title?.italic ?? false,
        setTitleItalic: (v) => updateMetadata('title.italic', v),
        titleColor: m.title?.color ?? '#000000',
        setTitleColor: (v) => updateMetadata('title.color', v),
        axisLabelFontSize: m.axes?.x?.label?.fontSize ?? 14,
        setAxisLabelFontSize: (v) => {
          updateMetadata('axes.x.label.fontSize', v);
          updateMetadata('axes.y.label.fontSize', v);
        },
        axisLabelBold: m.axes?.x?.label?.bold ?? false,
        setAxisLabelBold: (v) => {
          updateMetadata('axes.x.label.bold', v);
          updateMetadata('axes.y.label.bold', v);
        },
        axisLabelItalic: m.axes?.x?.label?.italic ?? false,
        setAxisLabelItalic: (v) => {
          updateMetadata('axes.x.label.italic', v);
          updateMetadata('axes.y.label.italic', v);
        },
        axisLabelColor: m.axes?.x?.label?.color ?? '#444',
        setAxisLabelColor: (v) => {
          updateMetadata('axes.x.label.color', v);
          updateMetadata('axes.y.label.color', v);
        },
        axisTickFontSize: m.axes?.x?.ticks?.fontSize ?? 11,
        setAxisTickFontSize: (v) => {
          updateMetadata('axes.x.ticks.fontSize', v);
          updateMetadata('axes.y.ticks.fontSize', v);
        },
        axisTickColor: m.axes?.x?.ticks?.color ?? '#444',
        setAxisTickColor: (v) => {
          updateMetadata('axes.x.ticks.color', v);
          updateMetadata('axes.y.ticks.color', v);
        },
        legendFontSize: m.legend?.font?.size ?? 12,
        setLegendFontSize: (v) => updateMetadata('legend.font.size', v),
        legendBold: m.legend?.font?.bold ?? false,
        setLegendBold: (v) => updateMetadata('legend.font.bold', v),
        legendItalic: m.legend?.font?.italic ?? false,
        setLegendItalic: (v) => updateMetadata('legend.font.italic', v),
        legendTextColor: m.legend?.font?.color ?? '#444',
        setLegendTextColor: (v) => updateMetadata('legend.font.color', v),
        hasLegend: m.capabilities?.hasLegend ?? true
      },
      
      // Data subsection
      dataState: {
        expanded: state.expansions.data,
        setExpanded: () => toggleExpansion('data'),
        traces: m.traces ?? [],
        selectedTraceIndex: 0,
        setSelectedTraceIndex: () => {},
        traceProperties: {},
        availableColumns: m.dataSource?.datasets ? 
          Object.values(m.dataSource.datasets)[0]?.columns ?? [] : []
      }
    };
  };
  
  // Helper functions for updating complex structures
  const updateLegendItem = useCallback((id, field, value) => {
    if (!state.metadata?.legend?.items) return;
    
    const updatedItems = state.metadata.legend.items.map(item =>
      item.id === id ? { ...item, [field]: value } : item
    );
    updateMetadata('legend.items', updatedItems);
  }, [state.metadata, updateMetadata]);
  
  const updateTraceProperty = useCallback((traceIndex, property, value) => {
    if (!state.metadata?.traces) return;
    
    const traces = [...(state.metadata.traces || [])];
    if (!traces[traceIndex]) {
      traces[traceIndex] = {};
    }
    traces[traceIndex] = {
      ...traces[traceIndex],
      [property]: value
    };
    updateMetadata('traces', traces);
  }, [state.metadata, updateMetadata]);
  
  return {
    state: state.metadata,
    metadata: state.metadata,
    expansions: state.expansions,
    capabilities: state.metadata?.capabilities || {},
    updateMetadata,
    toggleExpansion,
    reset,
    handleBlur,
    createSubsectionProps,
    updateLegendItem,
    updateTraceProperty
  };
};