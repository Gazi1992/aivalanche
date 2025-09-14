/**
 * Plot Capabilities Definition
 * Centralized system for determining what UI elements and features are available for each plot type
 */

/**
 * Comprehensive plot capabilities by type
 * This defines exactly what features each plot type supports
 */
export const PLOT_CAPABILITIES = {
  // Standard 2D plots with full axes
  scatter: {
    hasTitle: true,
    hasLegend: true,
    hasAxes: true,
    hasGrid: true,
    hasPlotArea: true,
    hasXAxis: true,
    hasYAxis: true,
    hasZAxis: false,
    hasAxisLabels: true,
    hasAxisTicks: true,
    hasDataLabels: false,
    supportsPan: true,
    supportsZoom: true,
    supportsHover: true
  },

  bar: {
    hasTitle: true,
    hasLegend: true,
    hasAxes: true,
    hasGrid: true,
    hasPlotArea: true,
    hasXAxis: true,
    hasYAxis: true,
    hasZAxis: false,
    hasAxisLabels: true,
    hasAxisTicks: true,
    hasDataLabels: false,
    supportsPan: true,
    supportsZoom: true,
    supportsHover: true
  },

  histogram: {
    hasTitle: true,
    hasLegend: true,
    hasAxes: true,
    hasGrid: true,
    hasPlotArea: true,
    hasXAxis: true,
    hasYAxis: true,
    hasZAxis: false,
    hasAxisLabels: true,
    hasAxisTicks: true,
    hasDataLabels: false,
    supportsPan: true,
    supportsZoom: true,
    supportsHover: true
  },

  heatmap: {
    hasTitle: true,
    hasLegend: false, // Has colorbar instead
    hasAxes: true,
    hasGrid: false, // Grid doesn't make sense for heatmap
    hasPlotArea: true,
    hasXAxis: true,
    hasYAxis: true,
    hasZAxis: false,
    hasAxisLabels: true,
    hasAxisTicks: true,
    hasDataLabels: false,
    hasColorbar: true,
    supportsPan: true,
    supportsZoom: true,
    supportsHover: true
  },

  box: {
    hasTitle: true,
    hasLegend: true,
    hasAxes: true,
    hasGrid: true,
    hasPlotArea: true,
    hasXAxis: true,
    hasYAxis: true,
    hasZAxis: false,
    hasAxisLabels: true,
    hasAxisTicks: true,
    hasDataLabels: false,
    supportsPan: true,
    supportsZoom: true,
    supportsHover: true
  },

  violin: {
    hasTitle: true,
    hasLegend: true,
    hasAxes: true,
    hasGrid: true,
    hasPlotArea: true,
    hasXAxis: true,
    hasYAxis: true,
    hasZAxis: false,
    hasAxisLabels: true,
    hasAxisTicks: true,
    hasDataLabels: false,
    supportsPan: true,
    supportsZoom: true,
    supportsHover: true
  },

  // Special 2D plots without standard axes
  pie: {
    hasTitle: true,
    hasLegend: true,
    hasAxes: false,
    hasGrid: false,
    hasPlotArea: false, // Pie doesn't have distinct plot area
    hasXAxis: false,
    hasYAxis: false,
    hasZAxis: false,
    hasAxisLabels: false,
    hasAxisTicks: false,
    hasDataLabels: true, // Pie slices have labels
    supportsPan: false,
    supportsZoom: false,
    supportsHover: true
  },

  sunburst: {
    hasTitle: true,
    hasLegend: false, // Sunburst doesn't use traditional legend
    hasAxes: false,
    hasGrid: false,
    hasPlotArea: false,
    hasXAxis: false,
    hasYAxis: false,
    hasZAxis: false,
    hasAxisLabels: false,
    hasAxisTicks: false,
    hasDataLabels: true,
    supportsPan: false,
    supportsZoom: false,
    supportsHover: true
  },

  treemap: {
    hasTitle: true,
    hasLegend: false, // Treemap doesn't use traditional legend
    hasAxes: false,
    hasGrid: false,
    hasPlotArea: false,
    hasXAxis: false,
    hasYAxis: false,
    hasZAxis: false,
    hasAxisLabels: false,
    hasAxisTicks: false,
    hasDataLabels: true,
    supportsPan: false,
    supportsZoom: false,
    supportsHover: true
  },

  funnel: {
    hasTitle: true,
    hasLegend: true,
    hasAxes: false,
    hasGrid: false,
    hasPlotArea: false,
    hasXAxis: false,
    hasYAxis: false,
    hasZAxis: false,
    hasAxisLabels: false,
    hasAxisTicks: false,
    hasDataLabels: true,
    supportsPan: false,
    supportsZoom: false,
    supportsHover: true
  },

  // Polar plots
  scatterpolar: {
    hasTitle: true,
    hasLegend: true,
    hasAxes: false, // Has polar axes, not cartesian
    hasGrid: true, // Polar grid
    hasPlotArea: true, // Has polar plot area
    hasXAxis: false,
    hasYAxis: false,
    hasZAxis: false,
    hasPolarAxes: true,
    hasAxisLabels: true, // Radial and angular labels
    hasAxisTicks: true,
    hasDataLabels: false,
    supportsPan: false,
    supportsZoom: false,
    supportsHover: true
  },

  barpolar: {
    hasTitle: true,
    hasLegend: true,
    hasAxes: false,
    hasGrid: true,
    hasPlotArea: true,
    hasXAxis: false,
    hasYAxis: false,
    hasZAxis: false,
    hasPolarAxes: true,
    hasAxisLabels: true,
    hasAxisTicks: true,
    hasDataLabels: false,
    supportsPan: false,
    supportsZoom: false,
    supportsHover: true
  },

  // Special multi-dimensional plots
  parcoords: {
    hasTitle: true,
    hasLegend: false, // PCP doesn't use standard legend
    hasAxes: false, // Has its own axis system
    hasGrid: false,
    hasPlotArea: true,
    hasXAxis: false,
    hasYAxis: false,
    hasZAxis: false,
    hasParallelAxes: true,
    hasAxisLabels: true, // Each dimension has labels
    hasAxisTicks: true,
    hasDataLabels: false,
    supportsPan: false,
    supportsZoom: false,
    supportsHover: true,
    supportsBrushing: true
  },

  parcats: {
    hasTitle: true,
    hasLegend: false,
    hasAxes: false,
    hasGrid: false,
    hasPlotArea: true,
    hasXAxis: false,
    hasYAxis: false,
    hasZAxis: false,
    hasParallelAxes: true,
    hasAxisLabels: true,
    hasAxisTicks: false,
    hasDataLabels: true,
    supportsPan: false,
    supportsZoom: false,
    supportsHover: true,
    supportsBrushing: true
  },

  splom: {
    hasTitle: true,
    hasLegend: false, // SPLOM doesn't use standard legend
    hasAxes: false, // Has matrix of axes
    hasGrid: true, // SPLOM should have grid controls for all subplots
    hasPlotArea: true, // SPLOM has a plot area
    hasXAxis: false,
    hasYAxis: false,
    hasZAxis: false,
    hasMatrixAxes: true,
    hasAxisLabels: false, // SPLOM axis labels are handled differently
    hasAxisTicks: false, // SPLOM axis ticks are handled differently
    hasDataLabels: false,
    supportsPan: false, // Individual subplots might support it
    supportsZoom: false,
    supportsHover: true
  },

  // Flow diagrams
  sankey: {
    hasTitle: true,
    hasLegend: false, // Sankey doesn't use standard legend
    hasAxes: false,
    hasGrid: false,
    hasPlotArea: false, // Sankey doesn't have distinct plot area
    hasXAxis: false,
    hasYAxis: false,
    hasZAxis: false,
    hasAxisLabels: false,
    hasAxisTicks: false,
    hasDataLabels: true, // Node and link labels
    hasNodeLabels: true,
    hasLinkLabels: true,
    supportsPan: false,
    supportsZoom: false,
    supportsHover: true
  },

  // 3D plots
  scatter3d: {
    hasTitle: true,
    hasLegend: true,
    hasAxes: true,
    hasGrid: true,
    hasPlotArea: true,
    hasXAxis: true,
    hasYAxis: true,
    hasZAxis: true,
    hasAxisLabels: true,
    hasAxisTicks: true,
    hasDataLabels: false,
    supportsPan: true,
    supportsZoom: true,
    supportsHover: true,
    supportsRotation: true,
    is3D: true
  },

  surface: {
    hasTitle: true,
    hasLegend: false, // Has colorbar
    hasAxes: true,
    hasGrid: true,
    hasPlotArea: true,
    hasXAxis: true,
    hasYAxis: true,
    hasZAxis: true,
    hasAxisLabels: true,
    hasAxisTicks: true,
    hasDataLabels: false,
    hasColorbar: true,
    supportsPan: true,
    supportsZoom: true,
    supportsHover: true,
    supportsRotation: true,
    is3D: true
  },

  mesh3d: {
    hasTitle: true,
    hasLegend: true,
    hasAxes: true,
    hasGrid: true,
    hasPlotArea: true,
    hasXAxis: true,
    hasYAxis: true,
    hasZAxis: true,
    hasAxisLabels: true,
    hasAxisTicks: true,
    hasDataLabels: false,
    supportsPan: true,
    supportsZoom: true,
    supportsHover: true,
    supportsRotation: true,
    is3D: true
  }
};

/**
 * Get capabilities for a plot type
 * @param {string} plotType - The type of plot
 * @returns {object} Capabilities object
 */
export function getPlotCapabilities(plotType) {
  // Return specific capabilities or default to scatter capabilities
  return PLOT_CAPABILITIES[plotType] || PLOT_CAPABILITIES.scatter;
}

/**
 * Determine plot type from figure data
 * @param {object} figure - Plotly figure object
 * @returns {string} Detected plot type
 */
export function detectPlotType(figure) {
  // Null check
  if (!figure) {
    return 'scatter';
  }

  // First check if metadata explicitly specifies plot type
  if (figure.metadata?.plotType) {
    return figure.metadata.plotType;
  }

  // Then check the first trace type
  if (figure.data && figure.data.length > 0) {
    const firstTrace = figure.data[0];
    return firstTrace.type || 'scatter';
  }

  // Default to scatter
  return 'scatter';
}

/**
 * Get text font subsection items based on capabilities
 * @param {object} capabilities - Plot capabilities
 * @returns {array} Array of text font items to show
 */
export function getTextFontItems(capabilities) {
  const items = [];

  // Title is always available if hasTitle is true
  if (capabilities.hasTitle) {
    items.push({
      key: 'title',
      label: 'Title',
      path: 'appearance.text.title'
    });
  }

  // Axis labels only if has axes
  if (capabilities.hasAxisLabels) {
    items.push({
      key: 'axisLabel',
      label: 'Axis Labels',
      path: 'appearance.text.axisLabel'
    });
  }

  // Axis ticks only if has axes
  if (capabilities.hasAxisTicks) {
    items.push({
      key: 'axisTick',
      label: 'Axis Ticks',
      path: 'appearance.text.axisTick'
    });
  }

  // Legend text only if has legend
  if (capabilities.hasLegend) {
    items.push({
      key: 'legend',
      label: 'Legend',
      path: 'appearance.text.legend'
    });
  }

  // Data labels for plots that support them
  if (capabilities.hasDataLabels) {
    items.push({
      key: 'dataLabels',
      label: 'Data Labels',
      path: 'appearance.text.dataLabels'
    });
  }

  // Node labels for Sankey
  if (capabilities.hasNodeLabels) {
    items.push({
      key: 'nodeLabels',
      label: 'Node Labels',
      path: 'appearance.text.nodeLabels'
    });
  }

  return items;
}

/**
 * Check if a specific UI section should be visible
 * @param {string} section - Section name (e.g., 'axes', 'legend', 'grid')
 * @param {object} capabilities - Plot capabilities
 * @returns {boolean} Whether the section should be visible
 */
export function isSectionVisible(section, capabilities) {
  switch (section) {
    case 'title':
      return capabilities.hasTitle;
    case 'axes':
      return capabilities.hasAxes;
    case 'legend':
      return capabilities.hasLegend;
    case 'grid':
      return capabilities.hasGrid;
    case 'background':
      return true; // Always show background options
    case 'text':
      return true; // Always show text options (contents vary)
    default:
      return true;
  }
}

/**
 * Get grid options based on capabilities
 * @param {object} capabilities - Plot capabilities
 * @returns {object} Grid options configuration
 */
export function getGridOptions(capabilities) {
  if (!capabilities.hasGrid) {
    return null;
  }

  const options = {
    showXGrid: capabilities.hasXAxis,
    showYGrid: capabilities.hasYAxis,
    showZGrid: capabilities.hasZAxis,
    showPolarGrid: capabilities.hasPolarAxes
  };

  return options;
}

/**
 * Update metadata structure with capabilities
 * @param {object} metadata - Current metadata
 * @param {string} plotType - Plot type
 * @returns {object} Updated metadata with capabilities
 */
export function updateMetadataCapabilities(metadata, plotType) {
  const capabilities = getPlotCapabilities(plotType);

  return {
    ...metadata,
    plotType,
    capabilities: {
      ...capabilities,
      // Preserve any custom capabilities that might have been set
      ...metadata.capabilities
    }
  };
}