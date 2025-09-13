/**
 * Utility functions for plot operations
 */
import Plotly from 'plotly.js-dist-min';

/**
 * Resize all plots with optional delay
 * @param {Array} figures - Array of figure objects
 * @param {number} delay - Delay in milliseconds before resizing
 */
export const resizePlotsWithDelay = (figures, delay = 100) => {
  if (!figures || figures.length === 0) return;
  
  const timer = setTimeout(() => {
    figures.forEach(fig => {
      if (fig && fig.id) {
        const plotId = `plot-${fig.id}`;
        const graphDiv = document.getElementById(plotId);
        if (graphDiv && Plotly) {
          Plotly.Plots.resize(graphDiv);
        }
      }
    });
  }, delay);
  
  return () => clearTimeout(timer);
};

/**
 * Resize a single plot
 * @param {string} plotId - The plot element ID
 */
export const resizePlot = (plotId) => {
  const graphDiv = document.getElementById(plotId);
  if (graphDiv && Plotly) {
    Plotly.Plots.resize(graphDiv);
  }
};

/**
 * Render a Plotly figure to a DOM element
 * @param {string} plotId - The plot element ID
 * @param {Object} figure - The Plotly figure object
 * @param {Object} config - Plotly config options
 */
export const renderPlot = (plotId, figure, config = {}) => {
  const graphDiv = document.getElementById(plotId);
  if (!graphDiv || !Plotly) return;
  
  const defaultConfig = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['sendDataToCloud'],
    toImageButtonOptions: {
      format: 'png',
      filename: plotId,
      height: 800,
      width: 1200,
      scale: 1
    }
  };
  
  return Plotly.react(
    plotId,
    figure.data || [],
    figure.layout || {},
    { ...defaultConfig, ...config }
  );
};

/**
 * Calculate grid dimensions based on number of figures and columns
 * @param {number} figureCount - Number of figures to display
 * @param {number} gridColumns - Number of columns in grid
 * @param {number} windowHeight - Window height in pixels
 * @returns {Object} Grid dimensions and styles
 */
export const calculateGridDimensions = (figureCount, gridColumns, windowHeight) => {
  const nCols = Math.min(gridColumns, figureCount);
  const nRows = Math.ceil(figureCount / nCols);
  
  // Get values from CSS variables
  const cs = getComputedStyle(document.body);
  const columnSelectorHeight = parseInt(cs.getPropertyValue('--column-selector-height')?.replace('px', '') || '45');
  const columnSelectorMarginBottom = parseInt(cs.getPropertyValue('--column-selector-margin-bottom')?.replace('px', '') || '0');
  const gridContainerPadding = parseInt(cs.getPropertyValue('--grid-container-padding')?.replace('px', '') || '20');
  
  // Calculate plot height based on number of rows
  let plotHeight;
  if (figureCount === 1) {
    // For single plot, use all available height minus grid container padding
    // No column selector is shown for single plot
    plotHeight = windowHeight - (gridContainerPadding * 2);
  } else {
    // For multiple plots, account for column selector height, its margin, and grid container padding
    // Total column selector space = height + bottom margin
    const totalColumnSelectorSpace = columnSelectorHeight + columnSelectorMarginBottom;
    const availableHeight = windowHeight - totalColumnSelectorSpace - (gridContainerPadding * 2);
    
    if (nRows === 1) {
      // Single row uses full available height
      plotHeight = availableHeight;
    } else if (nRows === 2) {
      // Two rows: split available height accounting for gap
      const gridGap = 20;
      plotHeight = (availableHeight - gridGap) / 2;
    } else {
      // More than 2 rows: fixed height with scrolling
      plotHeight = 350;
    }
  }
  
  // Calculate total grid height for fixed layouts
  let gridHeight = 'auto';
  if (nRows === 1) {
    gridHeight = `${plotHeight}px`;
  } else if (nRows === 2) {
    // For 2 rows: height of 2 plots + gap between them
    gridHeight = `${plotHeight * 2 + 20}px`;
  }
  
  return {
    nCols,
    nRows,
    plotHeight,
    gridStyle: {
      display: 'grid',
      gridTemplateColumns: `repeat(${nCols}, 1fr)`,
      gap: '20px',
      width: '100%',
      height: gridHeight,
      alignContent: 'start',
    }
  };
};

/**
 * Download a plot as an image
 * @param {string} plotId - The plot element ID  
 * @param {Object} options - Download options
 */
export const downloadPlotAsImage = (plotId, options = {}) => {
  if (!Plotly) return;
  
  const defaultOptions = {
    format: 'png',
    width: 1200,
    height: 800,
    filename: plotId || 'plot'
  };
  
  Plotly.downloadImage(plotId, { ...defaultOptions, ...options });
};