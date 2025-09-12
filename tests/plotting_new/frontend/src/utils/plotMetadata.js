/**
 * Centralized Plot Metadata System
 * 
 * This module provides a unified metadata structure for all plot configurations.
 * The metadata acts as an intermediate layer between:
 * - Python execution (provides initial data and config)
 * - EditPane UI (reads and modifies appearance)
 * - Plotly figure (final rendered output)
 */

// Default metadata structure with all possible configuration options
export const createDefaultMetadata = () => ({
  // Plot identification
  id: null,
  type: 'scatter', // scatter, bar, histogram, parcoords, splom, etc.
  
  // Plot capabilities (determined by plot type)
  capabilities: {
    hasAxes: true,
    hasLegend: true,
    hasGrid: true,
    has3D: false,
    isPolar: false,
    isParallelCoordinates: false,
    isScatterMatrix: false,
    isHeatmap: false
  },
  
  // Axis configuration
  axes: {
    x: {
      type: 'linear', // linear, log, date, category, multicategory
      label: {
        text: '',
        visible: true,
        fontSize: 14,
        color: '#444444',
        bold: false,
        italic: false
      },
      range: {
        min: null,
        max: null,
        autorange: true,
        reversed: false
      },
      ticks: {
        visible: true,
        fontSize: 11,
        color: '#444444',
        angle: 0
      },
      grid: {
        visible: true,
        color: 'rgba(128, 128, 128, 0.2)',
        width: 1
      },
      minorGrid: {
        visible: false,
        color: 'rgba(128, 128, 128, 0.1)'
      }
    },
    y: {
      type: 'linear',
      label: {
        text: '',
        visible: true,
        fontSize: 14,
        color: '#444444',
        bold: false,
        italic: false
      },
      range: {
        min: null,
        max: null,
        autorange: true,
        reversed: false
      },
      ticks: {
        visible: true,
        fontSize: 11,
        color: '#444444',
        angle: 0
      },
      grid: {
        visible: true,
        color: 'rgba(128, 128, 128, 0.2)',
        width: 1
      },
      minorGrid: {
        visible: false,
        color: 'rgba(128, 128, 128, 0.1)'
      }
    },
    z: null // For 3D plots
  },
  
  // Title configuration
  title: {
    text: '',
    visible: true,
    fontSize: 16,
    color: '#000000',
    bold: false,
    italic: false,
    alignment: 'center' // left, center, right
  },
  
  // Legend configuration
  legend: {
    visible: true,
    position: {
      x: 1.02,
      y: 1,
      xanchor: 'left',
      yanchor: 'top'
    },
    orientation: 'v', // 'v' or 'h'
    backgroundColor: 'rgba(255, 255, 255, 0)',
    borderColor: '#444444',
    borderWidth: 1,
    font: {
      size: 12,
      color: '#444444',
      bold: false,
      italic: false
    },
    items: [] // Will be populated with trace names
  },
  
  // Background and colors
  appearance: {
    figure: {
      backgroundColor: '#ffffff',
      borderColor: '#000000',
      borderWidth: 0
    },
    plot: {
      backgroundColor: 'rgba(255, 255, 255, 0)',
      borderColor: '#444444',
      borderWidth: 1
    }
  },
  
  // Trace-specific properties
  traces: [],
  
  // Layout dimensions
  layout: {
    width: null, // null means responsive
    height: null,
    margin: {
      l: 60,
      r: 30,
      t: 40,
      b: 40
    }
  },
  
  // Data source information (from Python execution)
  dataSource: {
    sessionId: null,
    executionTime: null,
    datasets: {} // Named datasets available for this plot
  },
  
  // User customizations (tracks what user has explicitly set)
  userCustomizations: new Set(),
  
  // Original values from Python execution (for reset functionality)
  originalConfig: null
});

/**
 * Merge metadata from Python execution with default structure
 * @param {Object} pythonMetadata - Metadata from Python execution service
 * @param {Object} existingMetadata - Existing metadata to merge with
 * @returns {Object} Complete metadata object
 */
export const mergeMetadata = (pythonMetadata = {}, existingMetadata = null) => {
  const base = existingMetadata || createDefaultMetadata();
  
  // Deep merge function that preserves structure
  const deepMerge = (target, source, path = '') => {
    for (const key in source) {
      if (source[key] === null || source[key] === undefined) continue;
      
      if (typeof source[key] === 'object' && !Array.isArray(source[key])) {
        if (!target[key]) target[key] = {};
        deepMerge(target[key], source[key], path ? `${path}.${key}` : key);
      } else {
        target[key] = source[key];
        // Track this as coming from Python (not user customization)
        if (path && !base.userCustomizations.has(`${path}.${key}`)) {
          // This is from Python, not user
        }
      }
    }
    return target;
  };
  
  // Merge Python metadata into base structure
  const merged = deepMerge(JSON.parse(JSON.stringify(base)), pythonMetadata);
  
  // Store original config for reset functionality
  if (!merged.originalConfig) {
    merged.originalConfig = JSON.parse(JSON.stringify(pythonMetadata));
  }
  
  // Update capabilities based on plot type
  merged.capabilities = determineCapabilities(merged.type);
  
  return merged;
};

/**
 * Determine plot capabilities based on plot type
 */
const determineCapabilities = (plotType) => {
  const capabilities = {
    hasAxes: true,
    hasLegend: true,
    hasGrid: true,
    has3D: false,
    isPolar: false,
    isParallelCoordinates: false,
    isScatterMatrix: false,
    isHeatmap: false
  };
  
  switch (plotType) {
    case 'pie':
    case 'sunburst':
    case 'treemap':
    case 'indicator':
    case 'icicle':
      capabilities.hasAxes = false;
      capabilities.hasGrid = false;
      break;
      
    case 'parcoords':
      capabilities.hasAxes = false;
      capabilities.hasGrid = false;
      capabilities.isParallelCoordinates = true;
      capabilities.hasLegend = false;
      break;
      
    case 'splom':
      capabilities.hasAxes = false;
      capabilities.hasGrid = false;
      capabilities.isScatterMatrix = true;
      capabilities.hasLegend = false;
      break;
      
    case 'scatterpolar':
    case 'barpolar':
      capabilities.isPolar = true;
      capabilities.hasAxes = false;
      break;
      
    case 'scatter3d':
    case 'surface':
    case 'mesh3d':
      capabilities.has3D = true;
      break;
      
    case 'heatmap':
      capabilities.isHeatmap = true;
      break;
  }
  
  return capabilities;
};

/**
 * Apply metadata to a Plotly figure
 * @param {Object} figure - Original Plotly figure
 * @param {Object} metadata - Complete metadata object
 * @returns {Object} Updated Plotly figure
 */
export const applyMetadataToFigure = (figure, metadata) => {
  if (!figure || !metadata) return figure;
  
  const updatedFigure = JSON.parse(JSON.stringify(figure));
  const layout = updatedFigure.layout || {};
  
  // Apply title
  if (metadata.title) {
    layout.title = {
      text: metadata.title.visible ? metadata.title.text : '',
      font: {
        size: metadata.title.fontSize,
        color: metadata.title.color,
        ...(metadata.title.bold && { weight: 'bold' }),
        ...(metadata.title.italic && { style: 'italic' })
      },
      xanchor: metadata.title.alignment,
      x: metadata.title.alignment === 'left' ? 0 : 
         metadata.title.alignment === 'right' ? 1 : 0.5
    };
  }
  
  // Apply axes configuration
  if (metadata.capabilities.hasAxes && metadata.axes) {
    // X-axis
    if (metadata.axes.x) {
      layout.xaxis = buildAxisConfig(metadata.axes.x, layout.xaxis);
    }
    
    // Y-axis
    if (metadata.axes.y) {
      layout.yaxis = buildAxisConfig(metadata.axes.y, layout.yaxis);
    }
    
    // Z-axis for 3D plots
    if (metadata.axes.z && metadata.capabilities.has3D) {
      layout.scene = layout.scene || {};
      layout.scene.zaxis = buildAxisConfig(metadata.axes.z, layout.scene.zaxis);
    }
  }
  
  // Apply legend configuration
  if (metadata.capabilities.hasLegend && metadata.legend) {
    layout.showlegend = metadata.legend.visible;
    if (metadata.legend.visible) {
      layout.legend = {
        x: metadata.legend.position.x,
        y: metadata.legend.position.y,
        xanchor: metadata.legend.position.xanchor,
        yanchor: metadata.legend.position.yanchor,
        orientation: metadata.legend.orientation,
        bgcolor: metadata.legend.backgroundColor,
        bordercolor: metadata.legend.borderColor,
        borderwidth: metadata.legend.borderWidth,
        font: {
          size: metadata.legend.font.size,
          color: metadata.legend.font.color,
          ...(metadata.legend.font.bold && { weight: 'bold' }),
          ...(metadata.legend.font.italic && { style: 'italic' })
        }
      };
    }
  }
  
  // Apply appearance/backgrounds
  if (metadata.appearance) {
    layout.paper_bgcolor = metadata.appearance.figure.backgroundColor;
    layout.plot_bgcolor = metadata.appearance.plot.backgroundColor;
    
    // Store border colors for custom rendering
    layout.figureBorderColor = metadata.appearance.figure.borderColor;
    layout.plotBorderColor = metadata.appearance.plot.borderColor;
  }
  
  // Apply layout dimensions
  if (metadata.layout) {
    if (metadata.layout.width) layout.width = metadata.layout.width;
    if (metadata.layout.height) layout.height = metadata.layout.height;
    if (metadata.layout.margin) layout.margin = metadata.layout.margin;
  }
  
  // Apply trace-specific properties
  if (metadata.traces && updatedFigure.data) {
    metadata.traces.forEach((traceConfig, idx) => {
      if (updatedFigure.data[idx]) {
        applyTraceConfig(updatedFigure.data[idx], traceConfig);
      }
    });
  }
  
  // Update legend items
  if (metadata.legend?.items && updatedFigure.data) {
    metadata.legend.items.forEach((item, idx) => {
      if (updatedFigure.data[idx]) {
        updatedFigure.data[idx].name = item.name;
        updatedFigure.data[idx].showlegend = item.visible;
      }
    });
  }
  
  updatedFigure.layout = layout;
  return updatedFigure;
};

/**
 * Build axis configuration from metadata
 */
const buildAxisConfig = (axisMetadata, existingAxis = {}) => {
  const config = { ...existingAxis };
  
  // Label
  if (axisMetadata.label) {
    config.title = {
      text: axisMetadata.label.visible ? axisMetadata.label.text : '',
      font: {
        size: axisMetadata.label.fontSize,
        color: axisMetadata.label.color,
        ...(axisMetadata.label.bold && { weight: 'bold' }),
        ...(axisMetadata.label.italic && { style: 'italic' })
      }
    };
  }
  
  // Type
  config.type = axisMetadata.type;
  
  // Range
  if (axisMetadata.range) {
    if (axisMetadata.range.reversed) {
      config.autorange = 'reversed';
    } else if (axisMetadata.range.min !== null || axisMetadata.range.max !== null) {
      config.autorange = false;
      config.range = [
        axisMetadata.range.min ?? existingAxis.range?.[0] ?? 0,
        axisMetadata.range.max ?? existingAxis.range?.[1] ?? 100
      ];
    } else if (axisMetadata.range.autorange) {
      config.autorange = true;
    }
  }
  
  // Ticks
  if (axisMetadata.ticks) {
    config.showticklabels = axisMetadata.ticks.visible;
    config.tickfont = {
      size: axisMetadata.ticks.fontSize,
      color: axisMetadata.ticks.color
    };
    if (axisMetadata.ticks.angle) {
      config.tickangle = axisMetadata.ticks.angle;
    }
  }
  
  // Grid
  if (axisMetadata.grid) {
    config.showgrid = axisMetadata.grid.visible;
    config.gridcolor = axisMetadata.grid.color;
    config.gridwidth = axisMetadata.grid.width;
    config.zerolinecolor = axisMetadata.grid.color;
  }
  
  // Minor grid
  if (axisMetadata.minorGrid && axisMetadata.minorGrid.visible) {
    config.minor = {
      showgrid: true,
      gridcolor: axisMetadata.minorGrid.color
    };
  }
  
  // Axis line
  config.showline = true;
  config.linewidth = 1;
  config.mirror = true;
  
  return config;
};

/**
 * Apply trace-specific configuration
 */
const applyTraceConfig = (trace, traceConfig) => {
  if (!traceConfig) return;
  
  // Color
  if (traceConfig.color) {
    if (trace.type === 'scatter' || trace.type === 'line') {
      trace.line = { ...trace.line, color: traceConfig.color };
      if (trace.marker) {
        trace.marker = { ...trace.marker, color: traceConfig.color };
      }
    } else if (trace.type === 'bar' || trace.type === 'histogram') {
      trace.marker = { ...trace.marker, color: traceConfig.color };
    }
  }
  
  // Line properties
  if (traceConfig.lineWidth !== undefined && (trace.type === 'scatter' || trace.type === 'line')) {
    trace.line = { ...trace.line, width: traceConfig.lineWidth };
  }
  
  if (traceConfig.lineStyle && (trace.type === 'scatter' || trace.type === 'line')) {
    trace.line = { ...trace.line, dash: traceConfig.lineStyle };
  }
  
  // Marker properties
  if (traceConfig.markerSize !== undefined) {
    trace.marker = { ...trace.marker, size: traceConfig.markerSize };
  }
  
  // Opacity
  if (traceConfig.opacity !== undefined) {
    trace.opacity = traceConfig.opacity;
  }
  
  // Name
  if (traceConfig.name) {
    trace.name = traceConfig.name;
  }
  
  // Visibility
  if (traceConfig.visible !== undefined) {
    trace.visible = traceConfig.visible;
  }
};

/**
 * Track user customization
 * @param {Object} metadata - Current metadata
 * @param {String} path - Path to the property being customized
 * @returns {Object} Updated metadata with tracked customization
 */
export const trackUserCustomization = (metadata, path) => {
  const updated = { ...metadata };
  updated.userCustomizations = new Set(updated.userCustomizations);
  updated.userCustomizations.add(path);
  return updated;
};

/**
 * Reset metadata to original Python configuration
 * @param {Object} metadata - Current metadata
 * @returns {Object} Reset metadata
 */
export const resetToOriginal = (metadata) => {
  if (!metadata.originalConfig) return metadata;
  
  const reset = mergeMetadata(metadata.originalConfig);
  reset.userCustomizations = new Set();
  return reset;
};

/**
 * Extract metadata from existing Plotly figure
 * @param {Object} figure - Plotly figure object
 * @returns {Object} Extracted metadata
 */
export const extractMetadataFromFigure = (figure) => {
  if (!figure || !figure.layout) return createDefaultMetadata();
  
  const layout = figure.layout;
  const metadata = createDefaultMetadata();
  
  // Extract title (handle both string and object formats)
  if (layout.title) {
    if (typeof layout.title === 'string') {
      // Simple string title
      metadata.title = {
        text: layout.title,
        visible: !!layout.title,
        fontSize: 16,
        color: '#000000',
        bold: false,
        italic: false,
        alignment: 'center'
      };
    } else if (typeof layout.title === 'object') {
      // Object format title
      metadata.title = {
        text: layout.title.text || '',
        visible: !!layout.title.text,
        fontSize: layout.title.font?.size || 16,
        color: layout.title.font?.color || '#000000',
        bold: layout.title.font?.weight === 'bold',
        italic: layout.title.font?.style === 'italic',
        alignment: layout.title.xanchor || 'center'
      };
    }
  }
  
  // Extract axes
  if (layout.xaxis) {
    metadata.axes.x = extractAxisMetadata(layout.xaxis);
  }
  if (layout.yaxis) {
    metadata.axes.y = extractAxisMetadata(layout.yaxis);
  }
  
  // Extract legend
  if (layout.legend) {
    metadata.legend = {
      visible: layout.showlegend !== false,
      position: {
        x: layout.legend.x || 1.02,
        y: layout.legend.y || 1,
        xanchor: layout.legend.xanchor || 'left',
        yanchor: layout.legend.yanchor || 'top'
      },
      orientation: layout.legend.orientation || 'v',
      backgroundColor: layout.legend.bgcolor || 'rgba(255, 255, 255, 0)',
      borderColor: layout.legend.bordercolor || '#444444',
      borderWidth: layout.legend.borderwidth || 1,
      font: {
        size: layout.legend.font?.size || 12,
        color: layout.legend.font?.color || '#444444',
        bold: layout.legend.font?.weight === 'bold',
        italic: layout.legend.font?.style === 'italic'
      },
      items: []
    };
  }
  
  // Extract appearance
  metadata.appearance = {
    figure: {
      backgroundColor: layout.paper_bgcolor || '#ffffff',
      borderColor: layout.figureBorderColor || '#000000',
      borderWidth: 0
    },
    plot: {
      backgroundColor: layout.plot_bgcolor || 'rgba(255, 255, 255, 0)',
      borderColor: layout.plotBorderColor || layout.xaxis?.linecolor || '#444444',
      borderWidth: 1
    }
  };
  
  // Extract traces
  if (figure.data) {
    metadata.traces = figure.data.map((trace, idx) => ({
      name: trace.name || `Trace ${idx + 1}`,
      visible: trace.visible !== false,
      color: trace.line?.color || trace.marker?.color,
      lineWidth: trace.line?.width,
      lineStyle: trace.line?.dash,
      markerSize: trace.marker?.size,
      opacity: trace.opacity
    }));
    
    // Update legend items
    metadata.legend.items = figure.data.map((trace, idx) => ({
      id: idx,
      name: trace.name || `Trace ${idx + 1}`,
      visible: trace.showlegend !== false
    }));
  }
  
  // Determine plot type from first trace
  if (figure.data && figure.data[0]) {
    metadata.type = figure.data[0].type || 'scatter';
    metadata.capabilities = determineCapabilities(metadata.type);
  }
  
  return metadata;
};

/**
 * Extract axis metadata from layout axis
 */
const extractAxisMetadata = (layoutAxis) => {
  return {
    type: layoutAxis.type || 'linear',
    label: {
      text: layoutAxis.title?.text || '',
      visible: !!layoutAxis.title?.text,
      fontSize: layoutAxis.title?.font?.size || 14,
      color: layoutAxis.title?.font?.color || '#444444',
      bold: layoutAxis.title?.font?.weight === 'bold',
      italic: layoutAxis.title?.font?.style === 'italic'
    },
    range: {
      min: layoutAxis.range?.[0] ?? null,
      max: layoutAxis.range?.[1] ?? null,
      autorange: layoutAxis.autorange === true || layoutAxis.autorange === 'reversed',
      reversed: layoutAxis.autorange === 'reversed'
    },
    ticks: {
      visible: layoutAxis.showticklabels !== false,
      fontSize: layoutAxis.tickfont?.size || 11,
      color: layoutAxis.tickfont?.color || '#444444',
      angle: layoutAxis.tickangle || 0
    },
    grid: {
      visible: layoutAxis.showgrid !== false,
      color: layoutAxis.gridcolor || 'rgba(128, 128, 128, 0.2)',
      width: layoutAxis.gridwidth || 1
    },
    minorGrid: {
      visible: !!layoutAxis.minor?.showgrid,
      color: layoutAxis.minor?.gridcolor || 'rgba(128, 128, 128, 0.1)'
    }
  };
};