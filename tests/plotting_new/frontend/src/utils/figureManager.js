/**
 * Figure Manager - Centralized figure and metadata management
 * 
 * This module ensures that metadata is the single source of truth for all plot rendering.
 * Every figure has an embedded metadata structure that completely controls its appearance.
 */

import { createMetadataStructure, initializeFromFigure, updateMetadataValues } from './metadataStructure';

/**
 * Create a managed figure with embedded metadata
 * @param {Object} plotlyFigure - Raw Plotly figure object
 * @param {Object} pythonMetadata - Optional metadata from Python
 * @returns {Object} Managed figure with embedded metadata
 */
export const createManagedFigure = (plotlyFigure, pythonMetadata = null) => {
  // Initialize metadata from the Plotly figure
  let metadata = initializeFromFigure(plotlyFigure);
  
  // If Python provided metadata, update specific values
  if (pythonMetadata) {
    const flattenMetadata = (obj, prefix = '') => {
      const paths = {};
      Object.entries(obj).forEach(([key, value]) => {
        const path = prefix ? `${prefix}.${key}` : key;
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
          Object.assign(paths, flattenMetadata(value, path));
        } else {
          paths[path] = value;
        }
      });
      return paths;
    };
    
    const pythonPaths = flattenMetadata(pythonMetadata);
    metadata = updateMetadataValues(metadata, pythonPaths, 'python');
  }
  
  // Return managed figure with embedded metadata
  return {
    id: plotlyFigure.id || `plot-${Date.now()}`,
    data: plotlyFigure.data || [],
    layout: plotlyFigure.layout || {},
    metadata: metadata,
    visibility: true
  };
};

/**
 * Generate Plotly layout from metadata
 * This is the ONLY function that should be used to get layout for rendering
 * @param {Object} figure - Managed figure with metadata
 * @param {Object} themeLayout - Theme-specific layout overrides
 * @returns {Object} Complete Plotly layout object
 */
export const generateLayoutFromMetadata = (figure, themeLayout = {}) => {
  const { metadata, layout: baseLayout } = figure;
  const m = metadata.appearance;
  
  // Start with theme layout as base
  const layout = { ...themeLayout };
  
  // Apply title from metadata
  if (m.title.visible && m.title.text) {
    layout.title = {
      text: m.title.text,
      font: {
        size: m.title.fontSize,
        color: m.title.color,
        weight: m.title.bold ? 'bold' : 'normal',
        style: m.title.italic ? 'italic' : 'normal'
      },
      xanchor: m.title.alignment,
      // Set x position based on alignment to ensure proper positioning
      x: m.title.alignment === 'left' ? 0 : m.title.alignment === 'right' ? 1 : 0.5
    };
  } else {
    layout.title = { text: '' };
  }
  
  // Apply X axis from metadata
  layout.xaxis = layout.xaxis || {};
  if (m.axes.x.label.visible) {
    layout.xaxis.title = {
      text: m.axes.x.label.text,
      font: {
        size: m.axes.x.label.fontSize,
        color: m.axes.x.label.color,
        weight: m.axes.x.label.bold ? 'bold' : 'normal',
        style: m.axes.x.label.italic ? 'italic' : 'normal'
      }
    };
  }
  
  layout.xaxis.showticklabels = m.axes.x.ticks.visible;
  if (m.axes.x.ticks.visible) {
    layout.xaxis.tickfont = {
      size: m.axes.x.ticks.fontSize,
      color: m.axes.x.ticks.color
    };
  }
  
  // Apply X axis range
  if (!m.axes.x.range.autorange && (m.axes.x.range.min !== null || m.axes.x.range.max !== null)) {
    layout.xaxis.autorange = false;
    layout.xaxis.range = [m.axes.x.range.min, m.axes.x.range.max];
  } else if (m.axes.x.range.reversed) {
    layout.xaxis.autorange = 'reversed';
  } else {
    layout.xaxis.autorange = true;
  }
  
  // Apply X axis scale
  layout.xaxis.type = m.axes.x.scale;
  
  // Apply X grid
  layout.xaxis.showgrid = m.axes.x.grid.visible;
  if (m.axes.x.grid.visible) {
    layout.xaxis.gridcolor = m.axes.x.grid.color;
    layout.xaxis.gridwidth = m.axes.x.grid.width;
  }
  
  // Apply X minor grid
  if (m.axes.x.minorGrid && m.axes.x.minorGrid.visible) {
    layout.xaxis.minor = {
      showgrid: true,
      gridcolor: m.axes.x.minorGrid.color || 'rgba(128, 128, 128, 0.1)',
      gridwidth: 1
    };
  }
  
  // Apply Y axis from metadata (similar to X)
  layout.yaxis = layout.yaxis || {};
  if (m.axes.y.label.visible) {
    layout.yaxis.title = {
      text: m.axes.y.label.text,
      font: {
        size: m.axes.y.label.fontSize,
        color: m.axes.y.label.color,
        weight: m.axes.y.label.bold ? 'bold' : 'normal',
        style: m.axes.y.label.italic ? 'italic' : 'normal'
      }
    };
  }
  
  layout.yaxis.showticklabels = m.axes.y.ticks.visible;
  if (m.axes.y.ticks.visible) {
    layout.yaxis.tickfont = {
      size: m.axes.y.ticks.fontSize,
      color: m.axes.y.ticks.color
    };
  }
  
  // Apply Y axis range
  if (!m.axes.y.range.autorange && (m.axes.y.range.min !== null || m.axes.y.range.max !== null)) {
    layout.yaxis.autorange = false;
    layout.yaxis.range = [m.axes.y.range.min, m.axes.y.range.max];
  } else if (m.axes.y.range.reversed) {
    layout.yaxis.autorange = 'reversed';
  } else {
    layout.yaxis.autorange = true;
  }
  
  // Apply Y axis scale
  layout.yaxis.type = m.axes.y.scale;
  
  // Apply Y grid
  layout.yaxis.showgrid = m.axes.y.grid.visible;
  if (m.axes.y.grid.visible) {
    layout.yaxis.gridcolor = m.axes.y.grid.color;
    layout.yaxis.gridwidth = m.axes.y.grid.width;
  }
  
  // Apply Y minor grid
  if (m.axes.y.minorGrid && m.axes.y.minorGrid.visible) {
    layout.yaxis.minor = {
      showgrid: true,
      gridcolor: m.axes.y.minorGrid.color || 'rgba(128, 128, 128, 0.1)',
      gridwidth: 1
    };
  }
  
  // Apply legend from metadata
  layout.showlegend = m.legend.visible;
  if (m.legend.visible) {
    layout.legend = {
      // Position inside the plot
      x: m.legend.position?.x ?? 0.02,
      y: m.legend.position?.y ?? 0.98,
      xanchor: m.legend.position?.xanchor ?? 'left',
      yanchor: m.legend.position?.yanchor ?? 'top',
      bgcolor: m.legend.backgroundColor,
      bordercolor: m.legend.borderColor,
      borderwidth: m.legend.borderColor ? 1 : 0,
      font: {
        size: m.legend.fontSize,
        color: m.legend.color,
        weight: m.legend.bold ? 'bold' : 'normal',
        style: m.legend.italic ? 'italic' : 'normal'
      }
    };
  }
  
  // Apply background colors from metadata
  // paper_bgcolor is the figure (outer) background
  // plot_bgcolor is the plot area (inner) background
  layout.paper_bgcolor = m.background.figure.color;
  layout.plot_bgcolor = m.background.plot.color;
  
  // Remove any default borders by setting line width to 0
  // Plotly adds borders via axis lines, so we need to control them
  layout.xaxis.showline = m.background.plot.borderColor && m.background.plot.borderColor !== 'transparent' && m.background.plot.borderColor !== 'rgba(0,0,0,0)';
  layout.yaxis.showline = m.background.plot.borderColor && m.background.plot.borderColor !== 'transparent' && m.background.plot.borderColor !== 'rgba(0,0,0,0)';
  
  if (layout.xaxis.showline || layout.yaxis.showline) {
    layout.xaxis.linecolor = m.background.plot.borderColor;
    layout.xaxis.linewidth = 1;
    layout.yaxis.linecolor = m.background.plot.borderColor;
    layout.yaxis.linewidth = 1;
    // Also set mirror to draw all 4 sides of the plot border
    layout.xaxis.mirror = true;
    layout.yaxis.mirror = true;
  } else {
    // Explicitly disable axis lines when no border
    layout.xaxis.linewidth = 0;
    layout.yaxis.linewidth = 0;
    layout.xaxis.mirror = false;
    layout.yaxis.mirror = false;
  }
  
  // Get margins from CSS variables (theme-aware)
  const getMarginFromCSS = (variable, defaultValue) => {
    if (typeof document !== 'undefined') {
      const value = getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
      return value ? parseInt(value) : defaultValue;
    }
    return defaultValue;
  };
  
  // Set appropriate margins for the plot from theme
  layout.margin = {
    l: getMarginFromCSS('--plot-margin-left', 80),
    r: getMarginFromCSS('--plot-margin-right', 50),
    t: getMarginFromCSS('--plot-margin-top', 60),
    b: getMarginFromCSS('--plot-margin-bottom', 60),
    pad: getMarginFromCSS('--plot-margin-pad', 10)
  };
  
  // Set autosize to true to make plot responsive
  layout.autosize = true;
  
  // Merge with any base layout properties not covered by metadata
  // But metadata always takes precedence
  Object.keys(baseLayout).forEach(key => {
    if (!layout.hasOwnProperty(key) && key !== 'xaxis' && key !== 'yaxis' && key !== 'margin') {
      layout[key] = baseLayout[key];
    }
  });
  
  return layout;
};

/**
 * Update figure metadata and return new figure
 * @param {Object} figure - Current figure
 * @param {Object} updates - Path-based updates to apply
 * @param {string} source - Source of updates ('user' or 'python')
 * @returns {Object} New figure with updated metadata
 */
export const updateFigureMetadata = (figure, updates, source = 'user') => {
  const updatedMetadata = updateMetadataValues(figure.metadata, updates, source);
  
  return {
    ...figure,
    metadata: updatedMetadata
  };
};

/**
 * Read current plot state from DOM and update figure
 * This captures zoom/pan state from Plotly's internal layout
 * @param {Object} figure - Current figure
 * @param {string} plotId - DOM element ID of the plot
 * @returns {Object} Updated figure with current DOM state
 */
export const syncFigureWithDOM = (figure, plotId) => {
  const plotDiv = document.getElementById(plotId);
  
  if (!plotDiv || !plotDiv._fullLayout) {
    return figure;
  }
  
  const fullLayout = plotDiv._fullLayout;
  let updates = {};
  
  // Capture current axis ranges
  if (fullLayout.xaxis && fullLayout.xaxis.range) {
    updates['appearance.axes.x.range.min'] = fullLayout.xaxis.range[0];
    updates['appearance.axes.x.range.max'] = fullLayout.xaxis.range[1];
    updates['appearance.axes.x.range.autorange'] = false;
  }
  
  if (fullLayout.yaxis && fullLayout.yaxis.range) {
    updates['appearance.axes.y.range.min'] = fullLayout.yaxis.range[0];
    updates['appearance.axes.y.range.max'] = fullLayout.yaxis.range[1];
    updates['appearance.axes.y.range.autorange'] = false;
  }
  
  // Capture current legend position if it has been moved
  if (fullLayout.legend) {
    if (fullLayout.legend.x !== undefined) {
      updates['appearance.legend.position.x'] = fullLayout.legend.x;
    }
    if (fullLayout.legend.y !== undefined) {
      updates['appearance.legend.position.y'] = fullLayout.legend.y;
    }
    if (fullLayout.legend.xanchor) {
      updates['appearance.legend.position.xanchor'] = fullLayout.legend.xanchor;
    }
    if (fullLayout.legend.yanchor) {
      updates['appearance.legend.position.yanchor'] = fullLayout.legend.yanchor;
    }
  }
  
  // Apply updates if any
  if (Object.keys(updates).length > 0) {
    return updateFigureMetadata(figure, updates, 'user');
  }
  
  return figure;
};

/**
 * Apply metadata-driven data transformations
 * @param {Object} figure - Managed figure
 * @returns {Array} Transformed data traces
 */
export const generateDataFromMetadata = (figure) => {
  const { data, metadata } = figure;
  
  // Apply any data-specific transformations from metadata
  return data.map((trace, index) => {
    const traceMetadata = metadata.data.traces[index];
    const legendItem = metadata.appearance.legend.items[index];
    
    // Apply trace-specific metadata (color, visibility, etc.)
    const updatedTrace = { ...trace };
    
    // Apply legend item visibility (whether to show in legend)
    if (legendItem) {
      updatedTrace.showlegend = legendItem.visible;
      if (legendItem.name) {
        updatedTrace.name = legendItem.name;
      }
    }
    
    // Apply trace metadata if available
    if (traceMetadata) {
      if (traceMetadata.visible !== undefined) {
        updatedTrace.visible = traceMetadata.visible;
      }
      
      if (traceMetadata.color) {
        if (updatedTrace.marker) {
          updatedTrace.marker = { ...updatedTrace.marker, color: traceMetadata.color };
        }
        if (updatedTrace.line) {
          updatedTrace.line = { ...updatedTrace.line, color: traceMetadata.color };
        }
      }
      
      if (traceMetadata.name && !legendItem?.name) {
        updatedTrace.name = traceMetadata.name;
      }
    }
    
    return updatedTrace;
  });
};