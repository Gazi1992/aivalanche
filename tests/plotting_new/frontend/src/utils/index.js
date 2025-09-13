/**
 * Central export point for all plot utilities
 */

// Core plot utilities
export * from './plotUtils';
export * from './plotRenderer';
export * from './plotInteractions';
export * from './figureManager';

// CSS and theme utilities
export * from './cssVariables';
export * from './plotTheme';

// Layout and grid utilities
export * from './plotLayout';

// Export utilities
export * from './plotExport';

// Re-export commonly used functions for convenience
export { 
  resizePlotsWithDelay,
  resizePlot,
  renderPlot as renderSinglePlot
} from './plotUtils';

export {
  renderPlot as renderThemedPlot,
  renderAllPlots,
  renderExpandedPlot
} from './plotRenderer';

export {
  createManagedFigure,
  syncFigureWithDOM,
  generateLayoutFromMetadata,
  generateDataFromMetadata
} from './figureManager';

export {
  getThemeColors,
  getSidebarDimensions,
  getPlotColors
} from './cssVariables';

export {
  getThemedLayout,
  applyThemeToLayout,
  isDarkTheme
} from './plotTheme';

export {
  calculateOptimalGrid,
  calculatePlotDimensions,
  getResponsivePlotHeight
} from './plotLayout';

export {
  exportAsImage,
  exportAsSVG,
  downloadDataAsCSV,
  downloadAsJSON
} from './plotExport';