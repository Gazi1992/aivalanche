/**
 * Plot layout calculation utilities
 * Handles grid layouts, responsive sizing, and positioning
 */

/**
 * Calculate optimal grid dimensions for multiple plots
 * @param {number} plotCount - Number of plots to display
 * @param {number} maxColumns - Maximum columns allowed
 * @param {Object} containerSize - Container dimensions {width, height}
 * @returns {Object} Grid configuration
 */
export const calculateOptimalGrid = (plotCount, maxColumns = 3, containerSize = {}) => {
  if (plotCount === 0) {
    return { columns: 0, rows: 0 };
  }
  
  // Single plot takes full space
  if (plotCount === 1) {
    return { columns: 1, rows: 1 };
  }
  
  // Calculate based on container aspect ratio if provided
  if (containerSize.width && containerSize.height) {
    const aspectRatio = containerSize.width / containerSize.height;
    
    // Wide container - prefer more columns
    if (aspectRatio > 1.5) {
      const columns = Math.min(plotCount, maxColumns);
      const rows = Math.ceil(plotCount / columns);
      return { columns, rows };
    }
    
    // Tall container - prefer more rows
    if (aspectRatio < 0.75) {
      const columns = Math.min(plotCount, Math.max(1, maxColumns - 1));
      const rows = Math.ceil(plotCount / columns);
      return { columns, rows };
    }
  }
  
  // Default calculation
  const columns = Math.min(plotCount, maxColumns);
  const rows = Math.ceil(plotCount / columns);
  
  return { columns, rows };
};

/**
 * Calculate individual plot dimensions within grid
 * @param {Object} gridConfig - Grid configuration {columns, rows}
 * @param {Object} containerSize - Container dimensions {width, height}
 * @param {Object} spacing - Spacing configuration {gap, padding}
 * @returns {Object} Plot dimensions {width, height}
 */
export const calculatePlotDimensions = (gridConfig, containerSize, spacing = {}) => {
  const { columns, rows } = gridConfig;
  const { width: containerWidth, height: containerHeight } = containerSize;
  const { gap = 20, padding = 20 } = spacing;
  
  if (columns === 0 || rows === 0) {
    return { width: 0, height: 0 };
  }
  
  // Calculate available space
  const totalHorizontalGaps = (columns - 1) * gap;
  const totalVerticalGaps = (rows - 1) * gap;
  const availableWidth = containerWidth - (padding * 2) - totalHorizontalGaps;
  const availableHeight = containerHeight - (padding * 2) - totalVerticalGaps;
  
  // Calculate plot dimensions
  const plotWidth = Math.floor(availableWidth / columns);
  const plotHeight = Math.floor(availableHeight / rows);
  
  return {
    width: Math.max(plotWidth, 300), // Minimum width
    height: Math.max(plotHeight, 250) // Minimum height
  };
};

/**
 * Get responsive plot height based on viewport and row count
 * @param {number} rowCount - Number of rows in grid
 * @param {number} viewportHeight - Viewport height in pixels
 * @param {Object} offsets - Fixed height offsets {header, footer, controls}
 * @returns {number} Plot height in pixels
 */
export const getResponsivePlotHeight = (rowCount, viewportHeight, offsets = {}) => {
  const {
    header = 60,
    footer = 0,
    controls = 40,
    padding = 40,
    gap = 20
  } = offsets;
  
  // Calculate available height
  const totalOffsets = header + footer + controls + padding;
  const availableHeight = viewportHeight - totalOffsets;
  
  // Single row - use most of available height
  if (rowCount === 1) {
    return Math.min(availableHeight, 600);
  }
  
  // Two rows - split evenly with gap
  if (rowCount === 2) {
    return Math.floor((availableHeight - gap) / 2);
  }
  
  // Multiple rows - use fixed height
  return 350;
};

/**
 * Calculate grid template CSS
 * @param {number} columns - Number of columns
 * @param {string} columnWidth - Width per column (e.g., '1fr', '300px')
 * @returns {string} CSS grid-template-columns value
 */
export const getGridTemplate = (columns, columnWidth = '1fr') => {
  if (columns <= 0) return 'none';
  if (columns === 1) return '1fr';
  
  return `repeat(${columns}, ${columnWidth})`;
};

/**
 * Get container padding based on screen size
 * @param {number} screenWidth - Screen width in pixels
 * @returns {Object} Padding values {top, right, bottom, left}
 */
export const getResponsivePadding = (screenWidth) => {
  // Mobile
  if (screenWidth < 768) {
    return { top: 10, right: 10, bottom: 10, left: 10 };
  }
  
  // Tablet
  if (screenWidth < 1024) {
    return { top: 15, right: 15, bottom: 15, left: 15 };
  }
  
  // Desktop
  return { top: 20, right: 20, bottom: 20, left: 20 };
};

/**
 * Calculate plot margins for optimal label display
 * @param {Object} plotConfig - Plot configuration
 * @returns {Object} Plotly margin object
 */
export const calculatePlotMargins = (plotConfig = {}) => {
  const {
    hasTitle = true,
    hasXLabel = true,
    hasYLabel = true,
    hasLegend = true,
    legendPosition = 'right'
  } = plotConfig;
  
  const margins = {
    l: hasYLabel ? 60 : 40,
    r: 20,
    t: hasTitle ? 40 : 20,
    b: hasXLabel ? 60 : 40
  };
  
  // Adjust for legend position
  if (hasLegend) {
    switch (legendPosition) {
      case 'right':
        margins.r = 100;
        break;
      case 'bottom':
        margins.b += 60;
        break;
      case 'top':
        margins.t += 40;
        break;
    }
  }
  
  return margins;
};

/**
 * Get breakpoint-based column count
 * @param {number} screenWidth - Screen width in pixels
 * @param {number} plotCount - Number of plots
 * @returns {number} Recommended column count
 */
export const getBreakpointColumns = (screenWidth, plotCount) => {
  // Single plot always takes full width
  if (plotCount === 1) return 1;
  
  // Mobile - single column
  if (screenWidth < 768) return 1;
  
  // Tablet - up to 2 columns
  if (screenWidth < 1024) return Math.min(plotCount, 2);
  
  // Desktop - up to 3 columns
  if (screenWidth < 1440) return Math.min(plotCount, 3);
  
  // Large desktop - up to 4 columns
  return Math.min(plotCount, 4);
};

/**
 * Calculate aspect ratio for plot
 * @param {string} plotType - Type of plot
 * @param {Object} dataShape - Shape of data {points, series, categories}
 * @returns {number} Recommended aspect ratio (width/height)
 */
export const getPlotAspectRatio = (plotType, dataShape = {}) => {
  const { points = 0, series = 1, categories = 0 } = dataShape;
  
  switch (plotType) {
    case 'scatter':
      // Square for scatter plots
      return 1.0;
      
    case 'line':
      // Wider for time series
      return points > 100 ? 2.0 : 1.5;
      
    case 'bar':
      // Depends on number of categories
      if (categories > 10) return 2.0;
      if (categories > 5) return 1.5;
      return 1.2;
      
    case 'histogram':
      // Standard ratio
      return 1.5;
      
    case 'heatmap':
      // Square for heatmaps
      return 1.0;
      
    case 'pie':
    case 'donut':
      // Square for circular plots
      return 1.0;
      
    default:
      // Default ratio
      return 1.5;
  }
};

/**
 * Get CSS grid styles for plot container
 * @param {Object} gridConfig - Grid configuration
 * @param {Object} spacing - Spacing configuration
 * @returns {Object} CSS style object
 */
export const getGridContainerStyles = (gridConfig, spacing = {}) => {
  const { columns, rows } = gridConfig;
  const { gap = 20, padding = 20 } = spacing;
  
  return {
    display: 'grid',
    gridTemplateColumns: getGridTemplate(columns),
    gridTemplateRows: rows > 0 ? `repeat(${rows}, 1fr)` : 'none',
    gap: `${gap}px`,
    padding: `${padding}px`,
    width: '100%',
    height: '100%',
    boxSizing: 'border-box'
  };
};

/**
 * Check if layout should be stacked (vertical)
 * @param {number} screenWidth - Screen width in pixels
 * @param {number} plotCount - Number of plots
 * @returns {boolean} True if layout should be stacked
 */
export const shouldStackLayout = (screenWidth, plotCount) => {
  // Always stack on mobile
  if (screenWidth < 768) return true;
  
  // Stack if many plots on tablet
  if (screenWidth < 1024 && plotCount > 4) return true;
  
  return false;
};