/**
 * Plot rendering utilities
 * Handles Plotly plot rendering and updates
 */
import Plotly from 'plotly.js-dist-min';
import { generateLayoutFromMetadata, generateDataFromMetadata } from './figureManager';
import { attachPlotInteractions } from './plotInteractions';

/**
 * Get color scale from CSS variables
 */
export const getColorScale = () => {
  const cs = getComputedStyle(document.body);
  return [
    cs.getPropertyValue('--color-data-1').trim(),
    cs.getPropertyValue('--color-data-2').trim(),
    cs.getPropertyValue('--color-data-3').trim(),
    cs.getPropertyValue('--color-data-4').trim(),
    cs.getPropertyValue('--color-data-5').trim(),
  ];
};

/**
 * Apply color scale to plot data
 */
export const applyColorScale = (data, colorScale) => {
  return data.map((trace, index) => {
    const updatedTrace = { ...trace };
    const defaultColor = colorScale[index % colorScale.length];
    
    // Only modify marker if it exists and doesn't have a color
    if (trace.marker) {
      updatedTrace.marker = {
        ...trace.marker,
        color: trace.marker.color || defaultColor
      };
    }
    
    // Only modify line if it exists and doesn't have a color
    if (trace.line) {
      updatedTrace.line = {
        ...trace.line,
        color: trace.line.color || defaultColor
      };
    }
    
    return updatedTrace;
  });
};

/**
 * Default plot configuration
 */
export const getDefaultPlotConfig = () => ({
  displaylogo: false,
  displayModeBar: false,
  responsive: true,
  scrollZoom: false,
  edits: {
    legendPosition: true,
    titleText: false,
    axisTitleText: false,
  },
});

/**
 * Render a single plot
 */
export const renderPlot = (figure, plotId, themedLayout) => {
  const plotDiv = document.getElementById(plotId);
  if (!plotDiv) return false;

  // Apply metadata transformations to data (for legend visibility, colors, etc.)
  // This returns new trace objects without modifying the original data values
  const data = figure.metadata ? generateDataFromMetadata(figure) : figure.data;
  
  // Apply theme and metadata to layout only
  const baseLayout = { ...figure.layout, ...themedLayout };
  const layout = figure.metadata ? generateLayoutFromMetadata(figure, baseLayout) : baseLayout;
  
  const config = getDefaultPlotConfig();
  
  if (plotDiv.children.length > 0) {
    Plotly.react(plotId, data, layout, config);
  } else {
    Plotly.newPlot(plotId, data, layout, config);
  }

  // Attach unified plot interactions
  attachPlotInteractions(plotDiv);
  
  // Force a reset of the plot to ensure correct range is set
  // This prevents cross-contamination between multiple plots
  setTimeout(() => {
    if (window.Plotly && plotDiv._fullLayout) {
      try {
        // Method 1: Try using Plotly.relayout with autorange
        console.log(`Attempting to reset plot ${plotId}`);
        
        // Build the reset update - this is what the home button does
        const resetUpdate = {
          'xaxis.autorange': true,
          'yaxis.autorange': true
        };
        
        // Apply the reset
        window.Plotly.relayout(plotDiv, resetUpdate).then(() => {
          console.log(`Successfully reset plot ${plotId} to autorange`);
        });
        
      } catch (error) {
        console.error('Error resetting plot:', error);
      }
    }
  }, 300);
  
  return true;
};

/**
 * Render all plots in figures array
 */
export const renderAllPlots = (figures, themedLayout) => {
  if (!figures || !figures.length) return;

  figures.forEach(fig => {
    if (fig) {
      renderPlot(fig, `plot-${fig.id}`, themedLayout);
    }
  });

  // Trigger resize after initial plot rendering
  setTimeout(() => {
    figures.forEach(fig => {
      if (fig) {
        const plotId = `plot-${fig.id}`;
        const graphDiv = document.getElementById(plotId);
        if (graphDiv) {
          Plotly.Plots.resize(graphDiv);
        }
      }
    });
  }, 100);
};

/**
 * Render expanded plot in overlay
 */
export const renderExpandedPlot = (figure, overlayDivId, themedLayout) => {
  const overlayDiv = document.getElementById(overlayDivId);
  if (!overlayDiv || !figure) return;

  // Apply metadata transformations to data (for legend visibility, colors, etc.)
  // This returns new trace objects without modifying the original data values
  const data = figure.metadata ? generateDataFromMetadata(figure) : figure.data;
  
  // Apply theme and metadata to layout only
  const baseLayout = { ...figure.layout, ...themedLayout };
  const layout = figure.metadata ? generateLayoutFromMetadata(figure, baseLayout) : baseLayout;
  
  Plotly.newPlot(overlayDiv, data, layout, {
    displaylogo: false,
    displayModeBar: true,
    responsive: true,
    scrollZoom: false,
    edits: { legendPosition: true },
  });

  // Attach unified plot interactions to overlay
  attachPlotInteractions(overlayDiv);

  return () => {
    Plotly.purge(overlayDiv);
  };
};