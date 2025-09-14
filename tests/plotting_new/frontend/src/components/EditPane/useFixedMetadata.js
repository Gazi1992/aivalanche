import { useReducer, useEffect, useRef, useCallback } from 'react';
import { 
  createMetadataStructure,
  updateMetadataValues,
  resetMetadata
} from '../../utils/metadataStructure';

// Action types
const ACTIONS = {
  INIT_METADATA: 'INIT_METADATA',
  UPDATE_VALUE: 'UPDATE_VALUE',
  TOGGLE_EXPANSION: 'TOGGLE_EXPANSION',
  RESET_TO_ORIGINAL: 'RESET_TO_ORIGINAL'
};

// Initial state
const createInitialState = () => ({
  metadata: createMetadataStructure(),
  originalMetadata: null, // Store the original metadata from Python
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
        metadata: action.payload,
        originalMetadata: JSON.parse(JSON.stringify(action.payload)) // Deep copy to preserve original
      };
      
    case ACTIONS.UPDATE_VALUE:
      return {
        ...state,
        metadata: updateMetadataValues(
          state.metadata, 
          { [action.payload.path]: action.payload.value },
          'user'
        )
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
        metadata: resetMetadata(state.metadata)
      };
      
    default:
      return state;
  }
};

// Main hook
export const useFixedMetadata = (figure, isOpen, onUpdate) => {
  const [state, dispatch] = useReducer(metadataReducer, null, createInitialState);
  const updateTimer = useRef(null);
  const isInitialMount = useRef(true);
  const lastFigureId = useRef(null);

  // Early return with default values if no figure
  if (!figure) {
    return {
      metadata: state.metadata,
      expansions: state.expansions,
      capabilities: state.metadata?.capabilities || {},
      toggleExpansion: () => {},
      resetAppearance: () => {},
      handleBlur: () => {},
      createSubsectionProps: () => ({}),
      updateLegendItem: () => {},
      updateTraceProperty: () => {}
    };
  }
  
  // Initialize metadata when EditPane opens
  useEffect(() => {
    if (isOpen && figure) {
      const figureId = figure.id;
      
      if (figureId !== lastFigureId.current) {
        // Use the metadata embedded in the figure
        let metadata = figure.metadata;
        
        // Ensure Sets are restored if they were serialized
        if (metadata?.customization) {
          if (Array.isArray(metadata.customization.userModified)) {
            metadata.customization.userModified = new Set(metadata.customization.userModified);
          }
          if (Array.isArray(metadata.customization.pythonModified)) {
            metadata.customization.pythonModified = new Set(metadata.customization.pythonModified);
          }
        }
        
        dispatch({ type: ACTIONS.INIT_METADATA, payload: metadata });
        lastFigureId.current = figureId;
        
        // Mark as initialized after a delay
        setTimeout(() => {
          isInitialMount.current = false;
        }, 500);
      }
    } else if (!isOpen) {
      isInitialMount.current = true;
      lastFigureId.current = null;
    }
  }, [isOpen, figure]);
  
  // Apply metadata changes to figure
  const applyChanges = useCallback(() => {
    if (!figure || !state.metadata || isInitialMount.current) return;
    
    // Update the figure with the new metadata
    const updatedFigure = {
      ...figure,
      metadata: state.metadata
    };
    onUpdate(updatedFigure);
  }, [state.metadata, figure, onUpdate]);
  
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
  const updateValue = useCallback((path, value) => {
    dispatch({ type: ACTIONS.UPDATE_VALUE, payload: { path, value } });
  }, []);
  
  const toggleExpansion = useCallback((section) => {
    dispatch({ type: ACTIONS.TOGGLE_EXPANSION, payload: section });
  }, []);
  
  const reset = useCallback(() => {
    dispatch({ type: ACTIONS.RESET_TO_ORIGINAL });
  }, []);
  
  const resetAppearance = useCallback(() => {
    // Reset all appearance values to original (from Python/initial load)
    if (!state.originalMetadata) return;
    
    const original = state.originalMetadata.appearance;
    const updates = {};
    
    // Reset title
    Object.keys(original.title).forEach(key => {
      updates[`appearance.title.${key}`] = original.title[key];
    });
    
    // Reset axes
    ['x', 'y'].forEach(axis => {
      if (original.axes[axis]) {
        Object.keys(original.axes[axis]).forEach(key => {
          if (typeof original.axes[axis][key] === 'object') {
            Object.keys(original.axes[axis][key]).forEach(subKey => {
              updates[`appearance.axes.${axis}.${key}.${subKey}`] = original.axes[axis][key][subKey];
            });
          } else {
            updates[`appearance.axes.${axis}.${key}`] = original.axes[axis][key];
          }
        });
      }
    });
    
    // Reset legend (except items which are data-specific)
    Object.keys(original.legend).forEach(key => {
      if (key === 'position') {
        Object.keys(original.legend.position).forEach(posKey => {
          updates[`appearance.legend.position.${posKey}`] = original.legend.position[posKey];
        });
      } else if (key !== 'items') {
        updates[`appearance.legend.${key}`] = original.legend[key];
      }
    });
    
    // Reset grid
    Object.keys(original.grid).forEach(axis => {
      Object.keys(original.grid[axis]).forEach(key => {
        updates[`appearance.grid.${axis}.${key}`] = original.grid[axis][key];
      });
    });
    
    // Reset background
    Object.keys(original.background).forEach(key => {
      Object.keys(original.background[key]).forEach(subKey => {
        updates[`appearance.background.${key}.${subKey}`] = original.background[key][subKey];
      });
    });
    
    // Reset text
    Object.keys(original.text).forEach(key => {
      Object.keys(original.text[key]).forEach(subKey => {
        updates[`appearance.text.${key}.${subKey}`] = original.text[key][subKey];
      });
    });
    
    // Apply all updates at once
    Object.entries(updates).forEach(([path, value]) => {
      updateValue(path, value);
    });
  }, [state.originalMetadata, updateValue]);
  
  // Create props for subsections based on fixed metadata structure
  const createSubsectionProps = () => {
    const m = state.metadata;
    const app = m.appearance;
    
    return {
      // Title subsection
      titleState: {
        expanded: state.expansions.labels,
        setExpanded: () => toggleExpansion('labels'),
        visible: app.title.visible,
        setVisible: (v) => updateValue('appearance.title.visible', v),
        text: app.title.text,
        setText: (v) => updateValue('appearance.title.text', v),
        alignment: app.title.alignment,
        setAlignment: (v) => updateValue('appearance.title.alignment', v)
      },
      
      // X-Axis subsection
      xAxisState: {
        expanded: state.expansions.axis,
        setExpanded: () => toggleExpansion('axis'),
        labelVisible: app.axes.x.label.visible,
        setLabelVisible: (v) => updateValue('appearance.axes.x.label.visible', v),
        label: app.axes.x.label.text,
        setLabel: (v) => updateValue('appearance.axes.x.label.text', v),
        scale: app.axes.x.scale,
        setScale: (v) => updateValue('appearance.axes.x.scale', v),
        ticksVisible: app.axes.x.ticks.visible,
        setTicksVisible: (v) => updateValue('appearance.axes.x.ticks.visible', v),
        minValue: app.axes.x.range.min?.toString() || '',
        setMinValue: (v) => {
          const newMin = v ? parseFloat(v) : null;
          updateValue('appearance.axes.x.range.min', newMin);
          // Only set autorange false if BOTH min and max are set
          if (newMin !== null && app.axes.x.range.max !== null) {
            updateValue('appearance.axes.x.range.autorange', false);
          } else if (newMin === null && app.axes.x.range.max === null) {
            updateValue('appearance.axes.x.range.autorange', true);
          }
        },
        maxValue: app.axes.x.range.max?.toString() || '',
        setMaxValue: (v) => {
          const newMax = v ? parseFloat(v) : null;
          updateValue('appearance.axes.x.range.max', newMax);
          // Only set autorange false if BOTH min and max are set
          if (app.axes.x.range.min !== null && newMax !== null) {
            updateValue('appearance.axes.x.range.autorange', false);
          } else if (app.axes.x.range.min === null && newMax === null) {
            updateValue('appearance.axes.x.range.autorange', true);
          }
        },
        inverted: app.axes.x.range.reversed,
        setInverted: (v) => updateValue('appearance.axes.x.range.reversed', v)
      },
      
      // Y-Axis subsection
      yAxisState: {
        expanded: state.expansions.axis,
        setExpanded: () => toggleExpansion('axis'),
        labelVisible: app.axes.y.label.visible,
        setLabelVisible: (v) => updateValue('appearance.axes.y.label.visible', v),
        label: app.axes.y.label.text,
        setLabel: (v) => updateValue('appearance.axes.y.label.text', v),
        scale: app.axes.y.scale,
        setScale: (v) => updateValue('appearance.axes.y.scale', v),
        ticksVisible: app.axes.y.ticks.visible,
        setTicksVisible: (v) => updateValue('appearance.axes.y.ticks.visible', v),
        minValue: app.axes.y.range.min?.toString() || '',
        setMinValue: (v) => {
          const newMin = v ? parseFloat(v) : null;
          updateValue('appearance.axes.y.range.min', newMin);
          // Only set autorange false if BOTH min and max are set
          if (newMin !== null && app.axes.y.range.max !== null) {
            updateValue('appearance.axes.y.range.autorange', false);
          } else if (newMin === null && app.axes.y.range.max === null) {
            updateValue('appearance.axes.y.range.autorange', true);
          }
        },
        maxValue: app.axes.y.range.max?.toString() || '',
        setMaxValue: (v) => {
          const newMax = v ? parseFloat(v) : null;
          updateValue('appearance.axes.y.range.max', newMax);
          // Only set autorange false if BOTH min and max are set
          if (app.axes.y.range.min !== null && newMax !== null) {
            updateValue('appearance.axes.y.range.autorange', false);
          } else if (app.axes.y.range.min === null && newMax === null) {
            updateValue('appearance.axes.y.range.autorange', true);
          }
        },
        inverted: app.axes.y.range.reversed,
        setInverted: (v) => updateValue('appearance.axes.y.range.reversed', v)
      },
      
      // Legend subsection
      legendState: {
        expanded: state.expansions.legend,
        setExpanded: () => toggleExpansion('legend'),
        visible: app.legend.visible,
        setVisible: (v) => updateValue('appearance.legend.visible', v),
        items: app.legend.items,
        backgroundColor: app.legend.backgroundColor,
        setBackgroundColor: (v) => updateValue('appearance.legend.backgroundColor', v),
        borderColor: app.legend.borderColor,
        setBorderColor: (v) => updateValue('appearance.legend.borderColor', v)
      },
      
      // Grid subsection
      gridState: {
        expanded: state.expansions.grid,
        setExpanded: () => toggleExpansion('grid'),
        xGridVisible: app.grid.x.visible,
        setXGridVisible: (v) => {
          updateValue('appearance.grid.x.visible', v);
          updateValue('appearance.axes.x.grid.visible', v);
        },
        yGridVisible: app.grid.y.visible,
        setYGridVisible: (v) => {
          updateValue('appearance.grid.y.visible', v);
          updateValue('appearance.axes.y.grid.visible', v);
        },
        xMinorGridVisible: app.grid.x.minorVisible,
        setXMinorGridVisible: (v) => {
          updateValue('appearance.grid.x.minorVisible', v);
          updateValue('appearance.axes.x.minorGrid.visible', v);
        },
        yMinorGridVisible: app.grid.y.minorVisible,
        setYMinorGridVisible: (v) => {
          updateValue('appearance.grid.y.minorVisible', v);
          updateValue('appearance.axes.y.minorGrid.visible', v);
        },
        gridColor: app.grid.x.color,
        setGridColor: (v) => {
          updateValue('appearance.grid.x.color', v);
          updateValue('appearance.grid.y.color', v);
          updateValue('appearance.axes.x.grid.color', v);
          updateValue('appearance.axes.y.grid.color', v);
        }
      },
      
      // Background subsection
      backgroundState: {
        figureBackgroundColor: app.background.figure.color,
        setFigureBackgroundColor: (v) => updateValue('appearance.background.figure.color', v),
        figureBorderColor: app.background.figure.borderColor,
        setFigureBorderColor: (v) => updateValue('appearance.background.figure.borderColor', v),
        plotBackgroundColor: app.background.plot.color,
        setPlotBackgroundColor: (v) => updateValue('appearance.background.plot.color', v),
        plotBorderColor: app.background.plot.borderColor,
        setPlotBorderColor: (v) => updateValue('appearance.background.plot.borderColor', v)
      },
      
      // Text subsection
      textState: {
        expanded: state.expansions.text,
        setExpanded: () => toggleExpansion('text'),
        titleFontSize: app.text.title.fontSize,
        setTitleFontSize: (v) => {
          updateValue('appearance.text.title.fontSize', v);
          updateValue('appearance.title.fontSize', v);
        },
        titleBold: app.text.title.bold,
        setTitleBold: (v) => {
          updateValue('appearance.text.title.bold', v);
          updateValue('appearance.title.bold', v);
        },
        titleItalic: app.text.title.italic,
        setTitleItalic: (v) => {
          updateValue('appearance.text.title.italic', v);
          updateValue('appearance.title.italic', v);
        },
        titleColor: app.text.title.color,
        setTitleColor: (v) => {
          updateValue('appearance.text.title.color', v);
          updateValue('appearance.title.color', v);
        },
        axisLabelFontSize: app.text.axisLabel.fontSize,
        setAxisLabelFontSize: (v) => {
          updateValue('appearance.text.axisLabel.fontSize', v);
          updateValue('appearance.axes.x.label.fontSize', v);
          updateValue('appearance.axes.y.label.fontSize', v);
        },
        axisLabelBold: app.text.axisLabel.bold,
        setAxisLabelBold: (v) => {
          updateValue('appearance.text.axisLabel.bold', v);
          updateValue('appearance.axes.x.label.bold', v);
          updateValue('appearance.axes.y.label.bold', v);
        },
        axisLabelItalic: app.text.axisLabel.italic,
        setAxisLabelItalic: (v) => {
          updateValue('appearance.text.axisLabel.italic', v);
          updateValue('appearance.axes.x.label.italic', v);
          updateValue('appearance.axes.y.label.italic', v);
        },
        axisLabelColor: app.text.axisLabel.color,
        setAxisLabelColor: (v) => {
          updateValue('appearance.text.axisLabel.color', v);
          updateValue('appearance.axes.x.label.color', v);
          updateValue('appearance.axes.y.label.color', v);
        },
        axisTickFontSize: app.text.axisTick.fontSize,
        setAxisTickFontSize: (v) => {
          updateValue('appearance.text.axisTick.fontSize', v);
          updateValue('appearance.axes.x.ticks.fontSize', v);
          updateValue('appearance.axes.y.ticks.fontSize', v);
        },
        axisTickColor: app.text.axisTick.color,
        setAxisTickColor: (v) => {
          updateValue('appearance.text.axisTick.color', v);
          updateValue('appearance.axes.x.ticks.color', v);
          updateValue('appearance.axes.y.ticks.color', v);
        },
        legendFontSize: app.text.legend.fontSize,
        setLegendFontSize: (v) => {
          updateValue('appearance.text.legend.fontSize', v);
          updateValue('appearance.legend.fontSize', v);
        },
        legendBold: app.text.legend.bold,
        setLegendBold: (v) => {
          updateValue('appearance.text.legend.bold', v);
          updateValue('appearance.legend.bold', v);
        },
        legendItalic: app.text.legend.italic,
        setLegendItalic: (v) => {
          updateValue('appearance.text.legend.italic', v);
          updateValue('appearance.legend.italic', v);
        },
        legendTextColor: app.text.legend.color,
        setLegendTextColor: (v) => {
          updateValue('appearance.text.legend.color', v);
          updateValue('appearance.legend.color', v);
        },
        hasLegend: m.capabilities.hasLegend
      },
      
      // Data subsection
      dataState: {
        expanded: state.expansions.data,
        setExpanded: () => toggleExpansion('data'),
        traces: m.data.traces,
        selectedTraceIndex: m.data.selectedTraceIndex,
        setSelectedTraceIndex: (v) => updateValue('data.selectedTraceIndex', v),
        traceProperties: m.data.traces.reduce((acc, trace, idx) => {
          acc[idx] = trace;
          return acc;
        }, {}),
        availableColumns: Object.values(m.dataSource.datasets)[0]?.columns || []
      }
    };
  };
  
  // Helper functions for complex updates
  const updateLegendItem = useCallback((id, field, value) => {
    const items = [...state.metadata.appearance.legend.items];
    const index = items.findIndex(item => item.id === id);
    if (index !== -1) {
      items[index] = { ...items[index], [field]: value };
      updateValue('appearance.legend.items', items);
    }
  }, [state.metadata, updateValue]);
  
  const updateTraceProperty = useCallback((traceIndex, property, value) => {
    const traces = [...state.metadata.data.traces];
    if (!traces[traceIndex]) {
      traces[traceIndex] = {};
    }
    traces[traceIndex] = {
      ...traces[traceIndex],
      [property]: value
    };
    updateValue('data.traces', traces);
  }, [state.metadata, updateValue]);
  
  return {
    metadata: state.metadata,
    expansions: state.expansions,
    capabilities: state.metadata.capabilities,
    updateValue,
    toggleExpansion,
    reset,
    resetAppearance,
    handleBlur,
    createSubsectionProps,
    updateLegendItem,
    updateTraceProperty
  };
};