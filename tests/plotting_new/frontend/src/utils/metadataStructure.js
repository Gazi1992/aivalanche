/**
 * Fixed Metadata Structure for Plot Configuration
 * 
 * This defines the complete, immutable structure of plot metadata.
 * Every plot MUST have this exact structure with all properties defined.
 * Python scripts and UI updates can only modify VALUES, not the structure itself.
 */

/**
 * Get CSS variable value or default
 * @param {string} variable - CSS variable name
 * @param {string} defaultValue - Default value if CSS variable not found
 * @returns {string} CSS variable value or default
 */
const getCSSVariable = (variable, defaultValue) => {
  if (typeof document !== 'undefined') {
    const value = getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
    return value || defaultValue;
  }
  return defaultValue;
};

/**
 * Create a complete metadata structure with all default values
 * This structure maps directly to the EditPane subsections
 */
export const createMetadataStructure = () => ({
  // Plot identification and capabilities
  id: null,
  plotType: 'scatter', // scatter, bar, histogram, parcoords, splom, etc.
  
  // Capabilities (determined by plot type, but always present)
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
  
  // APPEARANCE SECTION - Maps to EditPane sections
  appearance: {
    // Title Subsection
    title: {
      visible: true,
      text: '',
      alignment: 'center', // left, center, right
      fontSize: 16,
      color: '#000000',
      bold: false,
      italic: false
    },
    
    // Axes Subsection
    axes: {
      x: {
        type: 'linear', // linear, log, date, category
        label: {
          visible: true,
          text: '',
          fontSize: 14,
          color: '#444444',
          bold: false,
          italic: false
        },
        scale: 'linear', // linear, log
        ticks: {
          visible: true,
          fontSize: 11,
          color: '#444444',
          angle: 0
        },
        range: {
          min: null,
          max: null,
          autorange: true,
          reversed: false
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
          visible: true,
          text: '',
          fontSize: 14,
          color: '#444444',
          bold: false,
          italic: false
        },
        scale: 'linear',
        ticks: {
          visible: true,
          fontSize: 11,
          color: '#444444',
          angle: 0
        },
        range: {
          min: null,
          max: null,
          autorange: true,
          reversed: false
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
      z: null // For 3D plots, same structure as x/y when needed
    },
    
    // Legend Subsection
    legend: {
      visible: true,
      position: {
        x: 0.02,  // Inside plot, 2% from left
        y: 0.98,  // Inside plot, 2% from top
        xanchor: 'left',
        yanchor: 'top'
      },
      orientation: 'v', // 'v' or 'h'
      backgroundColor: getCSSVariable('--legend-bg', 'rgba(255, 255, 255, 0.95)'),
      borderColor: getCSSVariable('--legend-border', 'rgba(226, 232, 240, 0.8)'),
      borderWidth: 1,
      fontSize: 12,
      color: getCSSVariable('--legend-text', '#444444'),
      bold: false,
      italic: false,
      items: [] // Array of {id, name, visible}
    },
    
    // Grid & Background Subsection
    grid: {
      // Grid settings (duplicated from axes for EditPane organization)
      x: {
        visible: true,
        color: 'rgba(128, 128, 128, 0.2)',
        minorVisible: false,
        minorColor: 'rgba(128, 128, 128, 0.1)'
      },
      y: {
        visible: true,
        color: 'rgba(128, 128, 128, 0.2)',
        minorVisible: false,
        minorColor: 'rgba(128, 128, 128, 0.1)'
      }
    },
    
    // Background colors
    background: {
      figure: {
        color: getCSSVariable('--figure-background', '#ffffff'),
        borderColor: getCSSVariable('--figure-border-color', 'rgba(0, 0, 0, 0)'),
        borderWidth: 0
      },
      plot: {
        color: getCSSVariable('--plot-background', 'rgba(255, 255, 255, 0)'),
        borderColor: getCSSVariable('--plot-border-color', 'rgba(128, 128, 128, 0.2)'),
        borderWidth: 0
      }
    },
    
    // Text Styling Subsection (consolidated text styles)
    text: {
      title: {
        fontSize: 16,
        color: '#000000',
        bold: false,
        italic: false
      },
      axisLabel: {
        fontSize: 14,
        color: '#444444',
        bold: false,
        italic: false
      },
      axisTick: {
        fontSize: 11,
        color: '#444444'
      },
      legend: {
        fontSize: 12,
        color: '#444444',
        bold: false,
        italic: false
      }
    }
  },
  
  // DATA SECTION - Trace properties
  data: {
    traces: [], // Array of trace configurations
    selectedTraceIndex: 0
  },
  
  // Layout configuration
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
  
  // Metadata about data source
  dataSource: {
    sessionId: null,
    executionTime: null,
    scriptName: null,
    datasets: {} // Named datasets available
  },
  
  // Track what has been customized by user vs Python
  customization: {
    userModified: new Set(), // Paths modified by user
    pythonModified: new Set(), // Paths modified by Python
    originalValues: {} // Store original values for reset
  }
});

/**
 * Initialize metadata from a Plotly figure
 * This extracts values from the figure and puts them into our fixed structure
 */
export const initializeFromFigure = (figure) => {
  const metadata = createMetadataStructure();
  
  if (!figure || !figure.layout) return metadata;
  
  const layout = figure.layout;
  
  // Extract title (handle both string and object formats)
  if (layout.title) {
    if (typeof layout.title === 'string') {
      metadata.appearance.title.text = layout.title;
      metadata.appearance.title.visible = true;
    } else if (typeof layout.title === 'object') {
      metadata.appearance.title.text = layout.title.text || '';
      metadata.appearance.title.visible = !!layout.title.text;
      if (layout.title.font) {
        metadata.appearance.title.fontSize = layout.title.font.size || 16;
        metadata.appearance.title.color = layout.title.font.color || '#000000';
        metadata.appearance.title.bold = layout.title.font.weight === 'bold';
        metadata.appearance.title.italic = layout.title.font.style === 'italic';
      }
      metadata.appearance.title.alignment = layout.title.xanchor || 'center';
    }
  }
  
  // Extract X axis
  if (layout.xaxis) {
    extractAxisIntoMetadata(layout.xaxis, metadata.appearance.axes.x);
    // Also update grid settings
    metadata.appearance.grid.x.visible = layout.xaxis.showgrid !== false;
    metadata.appearance.grid.x.color = layout.xaxis.gridcolor || 'rgba(128, 128, 128, 0.2)';
  }
  
  // Extract Y axis
  if (layout.yaxis) {
    extractAxisIntoMetadata(layout.yaxis, metadata.appearance.axes.y);
    // Also update grid settings
    metadata.appearance.grid.y.visible = layout.yaxis.showgrid !== false;
    metadata.appearance.grid.y.color = layout.yaxis.gridcolor || 'rgba(128, 128, 128, 0.2)';
  }
  
  // Extract legend
  if (layout.showlegend !== undefined) {
    metadata.appearance.legend.visible = layout.showlegend;
  }
  if (layout.legend) {
    const legend = layout.legend;
    if (legend.x !== undefined) metadata.appearance.legend.position.x = legend.x;
    if (legend.y !== undefined) metadata.appearance.legend.position.y = legend.y;
    if (legend.xanchor) metadata.appearance.legend.position.xanchor = legend.xanchor;
    if (legend.yanchor) metadata.appearance.legend.position.yanchor = legend.yanchor;
    if (legend.orientation) metadata.appearance.legend.orientation = legend.orientation;
    if (legend.bgcolor) metadata.appearance.legend.backgroundColor = legend.bgcolor;
    if (legend.bordercolor) metadata.appearance.legend.borderColor = legend.bordercolor;
    if (legend.borderwidth !== undefined) metadata.appearance.legend.borderWidth = legend.borderwidth;
    if (legend.font) {
      metadata.appearance.legend.fontSize = legend.font.size || 12;
      metadata.appearance.legend.color = legend.font.color || '#444444';
      metadata.appearance.legend.bold = legend.font.weight === 'bold';
      metadata.appearance.legend.italic = legend.font.style === 'italic';
    }
  }
  
  // Extract backgrounds
  if (layout.paper_bgcolor) {
    metadata.appearance.background.figure.color = layout.paper_bgcolor;
  }
  if (layout.plot_bgcolor) {
    metadata.appearance.background.plot.color = layout.plot_bgcolor;
  }
  
  // Extract traces
  if (figure.data && Array.isArray(figure.data)) {
    metadata.data.traces = figure.data.map((trace, idx) => ({
      index: idx,
      name: trace.name || `Trace ${idx + 1}`,
      type: trace.type || 'scatter',
      visible: trace.visible !== false,
      showInLegend: trace.showlegend !== false,
      color: extractTraceColor(trace),
      lineWidth: trace.line?.width || 2,
      lineStyle: trace.line?.dash || 'solid',
      markerSize: trace.marker?.size || 6,
      markerSymbol: trace.marker?.symbol || 'circle',
      opacity: trace.opacity || 1
    }));
    
    // Also populate legend items
    metadata.appearance.legend.items = figure.data.map((trace, idx) => ({
      id: idx,
      name: trace.name || `Trace ${idx + 1}`,
      visible: trace.showlegend !== false
    }));
  }
  
  // Determine plot type from first trace
  if (figure.data && figure.data[0]) {
    metadata.plotType = figure.data[0].type || 'scatter';
    metadata.capabilities = determineCapabilities(metadata.plotType);
  }
  
  return metadata;
};

/**
 * Helper to extract axis properties into metadata structure
 */
const extractAxisIntoMetadata = (layoutAxis, metadataAxis) => {
  // Type
  metadataAxis.type = layoutAxis.type || 'linear';
  metadataAxis.scale = layoutAxis.type || 'linear';
  
  // Label
  if (layoutAxis.title) {
    if (typeof layoutAxis.title === 'string') {
      metadataAxis.label.text = layoutAxis.title;
      metadataAxis.label.visible = true;
    } else if (layoutAxis.title.text !== undefined) {
      metadataAxis.label.text = layoutAxis.title.text;
      metadataAxis.label.visible = !!layoutAxis.title.text;
      if (layoutAxis.title.font) {
        metadataAxis.label.fontSize = layoutAxis.title.font.size || 14;
        metadataAxis.label.color = layoutAxis.title.font.color || '#444444';
        metadataAxis.label.bold = layoutAxis.title.font.weight === 'bold';
        metadataAxis.label.italic = layoutAxis.title.font.style === 'italic';
      }
    }
  }
  
  // Ticks
  metadataAxis.ticks.visible = layoutAxis.showticklabels !== false;
  if (layoutAxis.tickfont) {
    metadataAxis.ticks.fontSize = layoutAxis.tickfont.size || 11;
    metadataAxis.ticks.color = layoutAxis.tickfont.color || '#444444';
  }
  if (layoutAxis.tickangle !== undefined) {
    metadataAxis.ticks.angle = layoutAxis.tickangle;
  }
  
  // Range
  if (layoutAxis.range) {
    metadataAxis.range.min = layoutAxis.range[0];
    metadataAxis.range.max = layoutAxis.range[1];
    metadataAxis.range.autorange = false;
  } else if (layoutAxis.autorange) {
    metadataAxis.range.autorange = true;
    metadataAxis.range.reversed = layoutAxis.autorange === 'reversed';
  }
  
  // Grid
  metadataAxis.grid.visible = layoutAxis.showgrid !== false;
  metadataAxis.grid.color = layoutAxis.gridcolor || 'rgba(128, 128, 128, 0.2)';
  metadataAxis.grid.width = layoutAxis.gridwidth || 1;
  
  // Minor grid
  if (layoutAxis.minor) {
    metadataAxis.minorGrid.visible = !!layoutAxis.minor.showgrid;
    metadataAxis.minorGrid.color = layoutAxis.minor.gridcolor || 'rgba(128, 128, 128, 0.1)';
  }
};

/**
 * Helper to extract trace color
 */
const extractTraceColor = (trace) => {
  if (trace.line?.color) return trace.line.color;
  if (trace.marker?.color) return trace.marker.color;
  if (trace.fillcolor) return trace.fillcolor;
  return '#1f77b4'; // Default Plotly color
};

/**
 * Determine plot capabilities based on type
 */
const determineCapabilities = (plotType) => {
  const base = {
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
      return { ...base, hasAxes: false, hasGrid: false };
      
    case 'parcoords':
      return { ...base, hasAxes: false, hasGrid: false, hasLegend: false, isParallelCoordinates: true };
      
    case 'splom':
      return { ...base, hasAxes: false, hasGrid: false, hasLegend: false, isScatterMatrix: true };
      
    case 'scatterpolar':
    case 'barpolar':
      return { ...base, hasAxes: false, isPolar: true };
      
    case 'scatter3d':
    case 'surface':
    case 'mesh3d':
      return { ...base, has3D: true };
      
    case 'heatmap':
      return { ...base, isHeatmap: true };
      
    default:
      return base;
  }
};

/**
 * Update metadata with values from Python or user input
 * This ONLY updates values, never changes the structure
 */
export const updateMetadataValues = (metadata, updates, source = 'user') => {
  const newMetadata = JSON.parse(JSON.stringify(metadata)); // Deep clone
  
  // Restore Sets in customization after JSON serialization
  if (newMetadata.customization) {
    newMetadata.customization.userModified = new Set(
      Array.isArray(metadata.customization?.userModified) 
        ? metadata.customization.userModified 
        : Array.from(metadata.customization?.userModified || [])
    );
    newMetadata.customization.pythonModified = new Set(
      Array.isArray(metadata.customization?.pythonModified) 
        ? metadata.customization.pythonModified 
        : Array.from(metadata.customization?.pythonModified || [])
    );
  }
  
  // Apply updates using a path-based approach
  const applyUpdate = (obj, path, value) => {
    const keys = path.split('.');
    let current = obj;
    
    // Navigate to the parent of the target
    for (let i = 0; i < keys.length - 1; i++) {
      if (!current[keys[i]]) {
        console.warn(`Path ${path} does not exist in metadata structure`);
        return;
      }
      current = current[keys[i]];
    }
    
    // Update the value
    const lastKey = keys[keys.length - 1];
    if (current.hasOwnProperty(lastKey)) {
      // Store original value if not already stored
      if (!newMetadata.customization.originalValues[path]) {
        newMetadata.customization.originalValues[path] = current[lastKey];
      }
      
      // Update the value
      current[lastKey] = value;
      
      // Track the modification source
      if (source === 'user') {
        newMetadata.customization.userModified.add(path);
      } else if (source === 'python') {
        newMetadata.customization.pythonModified.add(path);
      }
    } else {
      console.warn(`Property ${lastKey} does not exist at path ${path}`);
    }
  };
  
  // Process updates
  if (typeof updates === 'object') {
    Object.entries(updates).forEach(([path, value]) => {
      applyUpdate(newMetadata, path, value);
    });
  }
  
  return newMetadata;
};

/**
 * Apply metadata to a Plotly figure
 * Converts our structured metadata back to Plotly format
 */
export const applyMetadataToFigure = (figure, metadata) => {
  if (!figure || !metadata) return figure;
  
  const updatedFigure = JSON.parse(JSON.stringify(figure));
  const layout = updatedFigure.layout || {};
  
  // Apply title
  const title = metadata.appearance.title;
  layout.title = {
    text: title.visible ? title.text : '',
    font: {
      size: title.fontSize,
      color: title.color,
      ...(title.bold && { weight: 'bold' }),
      ...(title.italic && { style: 'italic' })
    },
    xanchor: title.alignment,
    x: title.alignment === 'left' ? 0 : title.alignment === 'right' ? 1 : 0.5
  };
  
  // Apply axes
  if (metadata.capabilities.hasAxes) {
    // X-axis
    const xAxis = metadata.appearance.axes.x;
    layout.xaxis = buildAxisLayout(xAxis, metadata.appearance.grid.x, metadata.appearance.background.plot.borderColor);
    
    // Y-axis
    const yAxis = metadata.appearance.axes.y;
    layout.yaxis = buildAxisLayout(yAxis, metadata.appearance.grid.y, metadata.appearance.background.plot.borderColor);
  }
  
  // Apply legend
  if (metadata.capabilities.hasLegend) {
    const legend = metadata.appearance.legend;
    layout.showlegend = legend.visible;
    if (legend.visible) {
      layout.legend = {
        x: legend.position.x,
        y: legend.position.y,
        xanchor: legend.position.xanchor,
        yanchor: legend.position.yanchor,
        orientation: legend.orientation,
        bgcolor: legend.backgroundColor,
        bordercolor: legend.borderColor,
        borderwidth: legend.borderWidth,
        font: {
          size: legend.fontSize,
          color: legend.color,
          ...(legend.bold && { weight: 'bold' }),
          ...(legend.italic && { style: 'italic' })
        }
      };
    }
  }
  
  // Apply backgrounds
  layout.paper_bgcolor = metadata.appearance.background.figure.color;
  layout.plot_bgcolor = metadata.appearance.background.plot.color;
  
  // Store border colors for custom rendering
  layout.figureBorderColor = metadata.appearance.background.figure.borderColor;
  layout.plotBorderColor = metadata.appearance.background.plot.borderColor;
  
  // Apply layout dimensions
  if (metadata.layout.width) layout.width = metadata.layout.width;
  if (metadata.layout.height) layout.height = metadata.layout.height;
  if (metadata.layout.margin) layout.margin = metadata.layout.margin;
  
  // Apply trace properties
  if (metadata.data.traces && updatedFigure.data) {
    metadata.data.traces.forEach((traceConfig, idx) => {
      if (updatedFigure.data[idx]) {
        applyTraceConfig(updatedFigure.data[idx], traceConfig);
      }
    });
  }
  
  // Apply legend items
  if (metadata.appearance.legend.items && updatedFigure.data) {
    metadata.appearance.legend.items.forEach((item, idx) => {
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
 * Build axis layout from metadata
 */
const buildAxisLayout = (axisMetadata, gridMetadata, borderColor) => {
  const layout = {
    type: axisMetadata.type,
    title: {
      text: axisMetadata.label.visible ? axisMetadata.label.text : '',
      font: {
        size: axisMetadata.label.fontSize,
        color: axisMetadata.label.color,
        ...(axisMetadata.label.bold && { weight: 'bold' }),
        ...(axisMetadata.label.italic && { style: 'italic' })
      }
    },
    showticklabels: axisMetadata.ticks.visible,
    tickfont: {
      size: axisMetadata.ticks.fontSize,
      color: axisMetadata.ticks.color
    },
    tickangle: axisMetadata.ticks.angle,
    showgrid: gridMetadata.visible,
    gridcolor: gridMetadata.color,
    zerolinecolor: gridMetadata.color,
    showline: true,
    linewidth: 1,
    mirror: true,
    linecolor: borderColor
  };
  
  // Handle range
  if (axisMetadata.range.reversed) {
    layout.autorange = 'reversed';
  } else if (axisMetadata.range.min !== null || axisMetadata.range.max !== null) {
    layout.autorange = false;
    layout.range = [
      axisMetadata.range.min ?? 0,
      axisMetadata.range.max ?? 100
    ];
  } else if (axisMetadata.range.autorange) {
    layout.autorange = true;
  }
  
  // Minor grid
  if (gridMetadata.minorVisible) {
    layout.minor = {
      showgrid: true,
      gridcolor: gridMetadata.minorColor
    };
  }
  
  return layout;
};

/**
 * Apply trace configuration
 */
const applyTraceConfig = (trace, config) => {
  if (config.name) trace.name = config.name;
  if (config.visible !== undefined) trace.visible = config.visible;
  if (config.showInLegend !== undefined) trace.showlegend = config.showInLegend;
  if (config.opacity !== undefined) trace.opacity = config.opacity;
  
  // Apply color based on trace type
  if (config.color) {
    if (trace.type === 'scatter' || trace.type === 'line') {
      trace.line = { ...trace.line, color: config.color };
      if (config.lineWidth) trace.line.width = config.lineWidth;
      if (config.lineStyle) trace.line.dash = config.lineStyle;
    }
    if (trace.marker) {
      trace.marker = { ...trace.marker, color: config.color };
      if (config.markerSize) trace.marker.size = config.markerSize;
      if (config.markerSymbol) trace.marker.symbol = config.markerSymbol;
    }
  }
};

/**
 * Reset metadata to original values
 */
export const resetMetadata = (metadata) => {
  const newMetadata = JSON.parse(JSON.stringify(metadata));
  
  // Reset all user-modified values to their originals
  newMetadata.customization.userModified.forEach(path => {
    if (newMetadata.customization.originalValues[path] !== undefined) {
      const keys = path.split('.');
      let current = newMetadata;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = newMetadata.customization.originalValues[path];
    }
  });
  
  // Clear user modifications
  newMetadata.customization.userModified = new Set();
  
  return newMetadata;
};