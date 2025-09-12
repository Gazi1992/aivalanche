import { useReducer, useEffect, useRef, useCallback } from 'react';
import { extractColorWithoutAlpha } from './colorUtils';

// Action types
const ACTIONS = {
  INIT_FROM_PLOT: 'INIT_FROM_PLOT',
  UPDATE_FIELD: 'UPDATE_FIELD',
  UPDATE_SECTION: 'UPDATE_SECTION',
  TOGGLE_EXPANSION: 'TOGGLE_EXPANSION',
  RESET: 'RESET'
};

// Initial state factory
const createInitialState = () => ({
  // Section expansions
  expansions: {
    appearance: true,
    labels: false,
    axis: false,
    legend: false,
    grid: false,
    text: false,
    data: false
  },
  
  // Plot properties organized by section
  title: {
    visible: true,
    text: '',
    alignment: 'center'
  },
  
  xAxis: {
    labelVisible: true,
    label: '',
    scale: 'linear',
    ticksVisible: true,
    min: '',
    max: '',
    inverted: false
  },
  
  yAxis: {
    labelVisible: true,
    label: '',
    scale: 'linear',
    ticksVisible: true,
    min: '',
    max: '',
    inverted: false
  },
  
  legend: {
    visible: true,
    items: [],
    backgroundColor: 'rgba(255, 255, 255, 0)',
    borderColor: '#444'
  },
  
  grid: {
    xVisible: true,
    yVisible: true,
    xMinorVisible: false,
    yMinorVisible: false,
    color: 'rgba(128, 128, 128, 0.2)'
  },
  
  background: {
    figureColor: '#ffffff',
    figureBorderColor: '#000000',
    plotColor: 'rgba(255, 255, 255, 0)',
    plotBorderColor: '#444'
  },
  
  text: {
    titleSize: 16,
    titleBold: false,
    titleItalic: false,
    titleColor: '#000000',
    axisLabelSize: 14,
    axisLabelBold: false,
    axisLabelItalic: false,
    axisLabelColor: '#444',
    axisTickSize: 11,
    axisTickColor: '#444',
    legendSize: 12,
    legendBold: false,
    legendItalic: false,
    legendColor: '#444'
  },
  
  traceProperties: {},
  selectedTraceIndex: 0,
  
  // Metadata
  originalRanges: {
    x: null,
    y: null
  }
});

// Reducer function
const editPaneReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.INIT_FROM_PLOT:
      return initializeFromPlot(state, action.payload);
      
    case ACTIONS.UPDATE_FIELD:
      return updateField(state, action.payload);
      
    case ACTIONS.UPDATE_SECTION:
      return updateSection(state, action.payload);
      
    case ACTIONS.TOGGLE_EXPANSION:
      return {
        ...state,
        expansions: {
          ...state.expansions,
          [action.payload]: !state.expansions[action.payload]
        }
      };
      
    case ACTIONS.RESET:
      return createInitialState();
      
    default:
      return state;
  }
};

// Helper to initialize state from plot data
const initializeFromPlot = (state, plotData) => {
  if (!plotData || !plotData.layout) return state;
  
  const layout = plotData.layout;
  const newState = { ...state };
  
  // Initialize title
  if (layout.title) {
    newState.title = {
      visible: !!layout.title.text,
      text: layout.title.text || '',
      alignment: layout.title.xanchor || 'center'
    };
  }
  
  // Initialize X axis
  if (layout.xaxis) {
    const xaxis = layout.xaxis;
    newState.xAxis = {
      labelVisible: !!xaxis.title?.text,
      label: xaxis.title?.text || '',
      scale: xaxis.type || 'linear',
      ticksVisible: xaxis.showticklabels !== false,
      min: xaxis.range?.[0]?.toString() || '',
      max: xaxis.range?.[1]?.toString() || '',
      inverted: xaxis.autorange === 'reversed'
    };
    
    // Store original range
    if (xaxis.range) {
      newState.originalRanges.x = [...xaxis.range];
    }
  }
  
  // Initialize Y axis
  if (layout.yaxis) {
    const yaxis = layout.yaxis;
    newState.yAxis = {
      labelVisible: !!yaxis.title?.text,
      label: yaxis.title?.text || '',
      scale: yaxis.type || 'linear',
      ticksVisible: yaxis.showticklabels !== false,
      min: yaxis.range?.[0]?.toString() || '',
      max: yaxis.range?.[1]?.toString() || '',
      inverted: yaxis.autorange === 'reversed'
    };
    
    // Store original range
    if (yaxis.range) {
      newState.originalRanges.y = [...yaxis.range];
    }
  }
  
  // Initialize legend
  newState.legend = {
    visible: layout.showlegend !== false,
    items: plotData.data?.map((trace, idx) => ({
      id: idx,
      name: trace.name || `Trace ${idx + 1}`,
      visible: trace.showlegend !== false
    })) || [],
    backgroundColor: layout.legend?.bgcolor || 'rgba(255, 255, 255, 0)',
    borderColor: layout.legend?.bordercolor || '#444'
  };
  
  // Initialize grid
  newState.grid = {
    xVisible: layout.xaxis?.showgrid !== false,
    yVisible: layout.yaxis?.showgrid !== false,
    xMinorVisible: !!layout.xaxis?.minor?.showgrid,
    yMinorVisible: !!layout.yaxis?.minor?.showgrid,
    color: layout.xaxis?.gridcolor || 'rgba(128, 128, 128, 0.2)'
  };
  
  // Initialize backgrounds
  newState.background = {
    figureColor: layout.paper_bgcolor || '#ffffff',
    figureBorderColor: layout.figureBorderColor || '#000000',
    plotColor: layout.plot_bgcolor || 'rgba(255, 255, 255, 0)',
    plotBorderColor: layout.xaxis?.linecolor || '#444'
  };
  
  // Initialize text styles
  const titleFont = layout.title?.font || {};
  const axisFont = layout.xaxis?.title?.font || {};
  const tickFont = layout.xaxis?.tickfont || {};
  const legendFont = layout.legend?.font || {};
  
  newState.text = {
    titleSize: titleFont.size || 16,
    titleBold: titleFont.weight === 'bold',
    titleItalic: titleFont.style === 'italic',
    titleColor: titleFont.color || '#000000',
    axisLabelSize: axisFont.size || 14,
    axisLabelBold: axisFont.weight === 'bold',
    axisLabelItalic: axisFont.style === 'italic',
    axisLabelColor: axisFont.color || '#444',
    axisTickSize: tickFont.size || 11,
    axisTickColor: tickFont.color || '#444',
    legendSize: legendFont.size || 12,
    legendBold: legendFont.weight === 'bold',
    legendItalic: legendFont.style === 'italic',
    legendColor: legendFont.color || '#444'
  };
  
  return newState;
};

// Helper to update a single field
const updateField = (state, { section, field, value }) => {
  return {
    ...state,
    [section]: {
      ...state[section],
      [field]: value
    }
  };
};

// Helper to update an entire section
const updateSection = (state, { section, data }) => {
  return {
    ...state,
    [section]: {
      ...state[section],
      ...data
    }
  };
};

// Build Plotly layout from state
const buildPlotlyLayout = (state, originalLayout) => {
  const layout = { ...originalLayout };
  
  // Update title
  layout.title = {
    ...layout.title,
    text: state.title.visible ? state.title.text : '',
    xanchor: state.title.alignment,
    x: state.title.alignment === 'left' ? 0 : state.title.alignment === 'right' ? 1 : 0.5,
    font: {
      size: state.text.titleSize,
      color: state.text.titleColor,
      ...(state.text.titleBold && { weight: 'bold' }),
      ...(state.text.titleItalic && { style: 'italic' })
    }
  };
  
  // Update X axis
  layout.xaxis = {
    ...layout.xaxis,
    title: {
      text: state.xAxis.labelVisible ? state.xAxis.label : '',
      font: {
        size: state.text.axisLabelSize,
        color: state.text.axisLabelColor,
        ...(state.text.axisLabelBold && { weight: 'bold' }),
        ...(state.text.axisLabelItalic && { style: 'italic' })
      }
    },
    type: state.xAxis.scale,
    showticklabels: state.xAxis.ticksVisible,
    showgrid: state.grid.xVisible,
    gridcolor: state.grid.color,
    zerolinecolor: state.grid.color,
    tickfont: {
      size: state.text.axisTickSize,
      color: state.text.axisTickColor
    },
    showline: true,
    linewidth: 1,
    mirror: true,
    linecolor: state.background.plotBorderColor,
    ...(state.grid.xMinorVisible && {
      minor: {
        showgrid: true,
        gridcolor: state.grid.color
      }
    })
  };
  
  // Handle X axis range
  if (state.xAxis.inverted) {
    layout.xaxis.autorange = 'reversed';
  } else if (state.xAxis.min || state.xAxis.max) {
    layout.xaxis.autorange = false;
    layout.xaxis.range = [
      state.xAxis.min || state.originalRanges.x?.[0] || 0,
      state.xAxis.max || state.originalRanges.x?.[1] || 100
    ];
  } else if (!layout.xaxis.range && state.originalRanges.x) {
    layout.xaxis.range = state.originalRanges.x;
    layout.xaxis.autorange = false;
  }
  
  // Update Y axis (similar to X axis)
  layout.yaxis = {
    ...layout.yaxis,
    title: {
      text: state.yAxis.labelVisible ? state.yAxis.label : '',
      font: {
        size: state.text.axisLabelSize,
        color: state.text.axisLabelColor,
        ...(state.text.axisLabelBold && { weight: 'bold' }),
        ...(state.text.axisLabelItalic && { style: 'italic' })
      }
    },
    type: state.yAxis.scale,
    showticklabels: state.yAxis.ticksVisible,
    showgrid: state.grid.yVisible,
    gridcolor: state.grid.color,
    zerolinecolor: state.grid.color,
    tickfont: {
      size: state.text.axisTickSize,
      color: state.text.axisTickColor
    },
    showline: true,
    linewidth: 1,
    mirror: true,
    linecolor: state.background.plotBorderColor,
    ...(state.grid.yMinorVisible && {
      minor: {
        showgrid: true,
        gridcolor: state.grid.color
      }
    })
  };
  
  // Handle Y axis range
  if (state.yAxis.inverted) {
    layout.yaxis.autorange = 'reversed';
  } else if (state.yAxis.min || state.yAxis.max) {
    layout.yaxis.autorange = false;
    layout.yaxis.range = [
      state.yAxis.min || state.originalRanges.y?.[0] || 0,
      state.yAxis.max || state.originalRanges.y?.[1] || 100
    ];
  } else if (!layout.yaxis.range && state.originalRanges.y) {
    layout.yaxis.range = state.originalRanges.y;
    layout.yaxis.autorange = false;
  }
  
  // Update legend
  layout.showlegend = state.legend.visible;
  if (state.legend.visible) {
    layout.legend = {
      ...layout.legend,
      bgcolor: state.legend.backgroundColor,
      bordercolor: state.legend.borderColor,
      borderwidth: 1,
      font: {
        size: state.text.legendSize,
        color: state.text.legendColor,
        ...(state.text.legendBold && { weight: 'bold' }),
        ...(state.text.legendItalic && { style: 'italic' })
      }
    };
  }
  
  // Update backgrounds
  layout.paper_bgcolor = state.background.figureColor;
  layout.plot_bgcolor = state.background.plotColor;
  layout.figureBorderColor = state.background.figureBorderColor;
  
  return layout;
};

// Build Plotly data from state
const buildPlotlyData = (state, originalData) => {
  if (!originalData) return [];
  
  const data = [...originalData];
  
  // Update legend items
  state.legend.items.forEach((item, idx) => {
    if (data[idx]) {
      data[idx].showlegend = item.visible;
      data[idx].name = item.name;
    }
  });
  
  // Update trace properties
  Object.entries(state.traceProperties).forEach(([traceIndex, props]) => {
    const idx = parseInt(traceIndex);
    if (data[idx]) {
      // Update trace colors, styles, etc.
      if (props.color) {
        if (data[idx].type === 'scatter' || data[idx].type === 'line') {
          data[idx].line = { ...data[idx].line, color: props.color };
          if (data[idx].marker) {
            data[idx].marker = { ...data[idx].marker, color: props.color };
          }
        } else if (data[idx].type === 'bar' || data[idx].type === 'histogram') {
          data[idx].marker = { ...data[idx].marker, color: props.color };
        }
      }
      
      if (props.lineWidth !== undefined && (data[idx].type === 'scatter' || data[idx].type === 'line')) {
        data[idx].line = { ...data[idx].line, width: props.lineWidth };
      }
      
      if (props.lineStyle) {
        data[idx].line = { ...data[idx].line, dash: props.lineStyle };
      }
      
      if (props.markerSize !== undefined) {
        data[idx].marker = { ...data[idx].marker, size: props.markerSize };
      }
      
      if (props.opacity !== undefined) {
        data[idx].opacity = props.opacity;
      }
    }
  });
  
  return data;
};

// Main hook
export const useEditPaneReducer = (plotData, metadata, isOpen, onUpdate) => {
  const [state, dispatch] = useReducer(editPaneReducer, null, createInitialState);
  const updateTimer = useRef(null);
  const isInitialMount = useRef(true);
  const lastPlotId = useRef(null);
  
  // Initialize from plot data when opened
  useEffect(() => {
    if (isOpen && plotData) {
      // Only initialize if it's a different plot
      const plotId = plotData.id || JSON.stringify(plotData.layout?.title);
      if (plotId !== lastPlotId.current) {
        dispatch({ type: ACTIONS.INIT_FROM_PLOT, payload: plotData });
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
  }, [isOpen, plotData]);
  
  // Apply updates with debouncing
  const applyUpdates = useCallback(() => {
    if (!plotData || isInitialMount.current) return;
    
    const updatedLayout = buildPlotlyLayout(state, plotData.layout);
    const updatedData = buildPlotlyData(state, plotData.data);
    
    onUpdate({ ...plotData, layout: updatedLayout, data: updatedData });
  }, [state, plotData, onUpdate]);
  
  // Debounced update effect
  useEffect(() => {
    if (isInitialMount.current) return;
    
    if (updateTimer.current) {
      clearTimeout(updateTimer.current);
    }
    
    updateTimer.current = setTimeout(() => {
      applyUpdates();
    }, 300);
    
    return () => {
      if (updateTimer.current) {
        clearTimeout(updateTimer.current);
      }
    };
  }, [state, applyUpdates]);
  
  // Immediate update on blur
  const handleBlur = useCallback(() => {
    if (updateTimer.current) {
      clearTimeout(updateTimer.current);
    }
    applyUpdates();
  }, [applyUpdates]);
  
  // Action creators
  const updateField = useCallback((section, field, value) => {
    dispatch({ type: ACTIONS.UPDATE_FIELD, payload: { section, field, value } });
  }, []);
  
  const updateSection = useCallback((section, data) => {
    dispatch({ type: ACTIONS.UPDATE_SECTION, payload: { section, data } });
  }, []);
  
  const toggleExpansion = useCallback((section) => {
    dispatch({ type: ACTIONS.TOGGLE_EXPANSION, payload: section });
  }, []);
  
  const reset = useCallback(() => {
    dispatch({ type: ACTIONS.RESET });
  }, []);
  
  return {
    state,
    updateField,
    updateSection,
    toggleExpansion,
    reset,
    handleBlur,
    metadata
  };
};