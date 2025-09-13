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
  return data.map((trace, index) => ({
    ...trace,
    marker: {
      ...trace.marker,
      color: trace.marker?.color || colorScale[index % colorScale.length],
    },
    line: {
      ...trace.line,
      color: trace.line?.color || colorScale[index % colorScale.length],
    },
  }));
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

  const colorScale = getColorScale();
  const layout = generateLayoutFromMetadata(figure, themedLayout);
  const data = applyColorScale(generateDataFromMetadata(figure), colorScale);
  const config = getDefaultPlotConfig();
  

  // Use Plotly.react for efficient updates, or newPlot if the div is empty
  if (plotDiv.children.length > 0) {
    Plotly.react(plotId, data, layout, config);
  } else {
    Plotly.newPlot(plotId, data, layout, config);
  }

  // Attach unified plot interactions
  attachPlotInteractions(plotDiv);
  
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

  const colorScale = getColorScale();
  const layout = generateLayoutFromMetadata(figure, themedLayout);
  const data = applyColorScale(generateDataFromMetadata(figure), colorScale);

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