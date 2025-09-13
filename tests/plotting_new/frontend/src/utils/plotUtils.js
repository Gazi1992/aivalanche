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
  const mainPadding = parseInt(cs.getPropertyValue('--main-padding')?.replace('px', '') || '20');
  const columnSelectorHeight = parseInt(cs.getPropertyValue('--column-selector-height')?.replace('px', '') || '40');
  
  // Calculate plot height based on number of rows
  let plotHeight;
  if (figureCount === 1) {
    // For single plot, use all available height (no column selector shown)
    plotHeight = windowHeight - (mainPadding * 2);
  } else {
    // For multiple plots, account for column selector
    const availableHeight = windowHeight - (mainPadding * 2) - columnSelectorHeight;
    
    if (nRows === 1) {
      plotHeight = availableHeight;  // Use full available height for single row
    } else if (nRows === 2) {
      // Account for gap between rows (20px from grid gap)
      const gridGap = 20;
      plotHeight = (availableHeight - gridGap) / 2;  // Split available height evenly
    } else {
      plotHeight = 350;
    }
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
      height: nRows <= 2 ? '100%' : 'auto',
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