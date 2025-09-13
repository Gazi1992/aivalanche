# Frontend Utilities Documentation

This document describes the utility modules available in the frontend for plot management and operations.

## Overview

The frontend utilities are organized into specialized modules that handle different aspects of plot functionality. All utilities are available through a central export point at `utils/index.js`.

## Core Utilities

### figureManager.js
Manages figures with embedded metadata, providing the core functionality for the metadata-driven architecture.

**Key Functions:**
- `createManagedFigure(plotlyFigure, pythonMetadata, figureId)` - Creates a managed figure with complete metadata structure
- `generateLayoutFromMetadata(figure, baseLayout)` - Generates Plotly layout from metadata
- `generateDataFromMetadata(figure)` - Extracts data configuration from metadata
- `syncFigureWithDOM(figure, plotId)` - Synchronizes figure with DOM state (zoom, pan)
- `updateFigureMetadata(figure, path, value)` - Updates nested metadata values

**Grid Rendering Features:**
- Applies grid colors to main grid, minor grid, and zero lines
- Properly handles minor grid visibility toggling
- Supports categorical vs numeric axis detection

### metadataStructure.js
Defines the fixed metadata structure that serves as the single source of truth for all visual properties.

**Structure:**
```javascript
{
  appearance: {
    title: { text, visible, fontSize, color, bold, italic, alignment },
    axes: {
      x: { label, scale, range, ticks, grid, minorGrid },
      y: { label, scale, range, ticks, grid, minorGrid }
    },
    legend: { visible, position, backgroundColor, borderColor, items },
    background: { figure, plot }
  },
  data: { traces, selectedTraceIndex },
  capabilities: { hasAxes, hasLegend, isScatterMatrix, isParallelCoordinates },
  customization: { userModified, pythonModified }
}
```

## Plot Operation Utilities

### plotUtils.js
Basic plot operations and utility functions.

**Key Functions:**
- `resizePlotsWithDelay(figures, delay)` - Resizes all plots with optional delay
- `resizePlot(plotId)` - Resizes a single plot
- `renderPlot(plotId, figure, config)` - Renders a Plotly figure to DOM
- `calculateGridDimensions(figureCount, gridColumns, windowHeight)` - Calculates optimal grid layout
- `downloadPlotAsImage(plotId, options)` - Downloads plot as image

### plotRenderer.js
Handles themed plot rendering with color management.

**Key Functions:**
- `renderPlot(figure, plotId, themedLayout)` - Renders a single plot with theme
- `renderAllPlots(figures, themedLayout)` - Renders all plots in grid
- `renderExpandedPlot(figure, overlayDivId, themedLayout)` - Renders expanded view
- `getColorScale()` - Gets theme color scale from CSS variables
- `applyColorScale(data, colorScale)` - Applies colors to plot data

### plotInteractions.js
Manages unified plot interaction handling.

**Key Functions:**
- `attachPlotInteractions(plotDiv)` - Attaches interaction handlers to plot
- `handlePlotClick(event)` - Handles click events on plot
- `handlePlotHover(event)` - Handles hover events
- `handlePlotZoom(event)` - Handles zoom events
- `handlePlotPan(event)` - Handles pan events

## Export Utilities

### plotExport.js
Comprehensive export functionality for various formats.

**Key Functions:**
- `exportAsImage(plotId, options)` - Exports plot as image (PNG, JPEG, etc.)
- `exportAsSVG(plotId, filename)` - Exports as vector SVG
- `exportAsHighResPNG(plotId, filename)` - Exports high-resolution PNG
- `exportDataAsCSV(figure)` - Converts plot data to CSV format
- `downloadDataAsCSV(figure, filename)` - Downloads data as CSV file
- `exportAsJSON(figure)` - Exports plot configuration as JSON
- `downloadAsJSON(figure, filename)` - Downloads configuration as JSON
- `copyImageToClipboard(plotId)` - Copies plot image to clipboard
- `getExportFormats()` - Returns available export formats

**Supported Formats:**
- Images: PNG, SVG, JPEG, WebP
- Data: CSV
- Configuration: JSON

## Theme Utilities

### plotTheme.js
Manages theme-specific plot styling and color schemes.

**Key Functions:**
- `getThemedLayout(theme)` - Gets theme-specific Plotly layout
- `getThemeColorway()` - Returns array of theme colors
- `applyThemeToLayout(layout, theme)` - Applies theme to existing layout
- `getThemeMarkerColors(count)` - Gets marker colors for data series
- `getThemeGradient(baseColor, steps)` - Generates gradient colors
- `getThemeModebarConfig()` - Gets themed modebar configuration
- `getThemeAxisStyle(axisType)` - Returns axis styling for theme
- `getThemeAnnotationStyle()` - Returns annotation styling
- `isDarkTheme()` - Checks if dark theme is active
- `getContrastingColor(bgColor)` - Gets contrasting text color

### cssVariables.js
Utilities for accessing CSS variables from JavaScript.

**Key Functions:**
- `getCSSVariable(variable, defaultValue)` - Gets CSS variable value
- `getThemeColors()` - Returns all theme colors object
- `getSidebarDimensions()` - Gets sidebar width values
- `getPlotColors()` - Returns plot-specific colors
- `getContainerDimensions()` - Gets container dimensions

## Layout Utilities

### plotLayout.js
Handles grid layouts, responsive sizing, and positioning.

**Key Functions:**
- `calculateOptimalGrid(plotCount, maxColumns, containerSize)` - Calculates optimal grid configuration
- `calculatePlotDimensions(gridConfig, containerSize, spacing)` - Calculates individual plot dimensions
- `getResponsivePlotHeight(rowCount, viewportHeight, offsets)` - Gets responsive height
- `getGridTemplate(columns, columnWidth)` - Returns CSS grid template
- `getResponsivePadding(screenWidth)` - Returns responsive padding values
- `calculatePlotMargins(plotConfig)` - Calculates plot margins for labels
- `getBreakpointColumns(screenWidth, plotCount)` - Returns column count for breakpoint
- `getPlotAspectRatio(plotType, dataShape)` - Calculates recommended aspect ratio
- `getGridContainerStyles(gridConfig, spacing)` - Returns grid container CSS
- `shouldStackLayout(screenWidth, plotCount)` - Determines if layout should stack

**Responsive Breakpoints:**
- Mobile: < 768px (1 column)
- Tablet: < 1024px (up to 2 columns)
- Desktop: < 1440px (up to 3 columns)
- Large Desktop: 4 columns max

## Usage Examples

### Importing Utilities

```javascript
// Import specific utilities
import { createManagedFigure, syncFigureWithDOM } from './utils/figureManager';
import { exportAsImage, downloadDataAsCSV } from './utils/plotExport';
import { getThemedLayout, isDarkTheme } from './utils/plotTheme';

// Or import from central export
import { 
  createManagedFigure,
  exportAsImage,
  getThemedLayout,
  calculateOptimalGrid 
} from './utils';
```

### Creating a Managed Figure

```javascript
const managedFigure = createManagedFigure(
  plotlyFigure,
  pythonMetadata,
  'unique-plot-id'
);
```

### Exporting a Plot

```javascript
// Export as high-resolution PNG
await exportAsHighResPNG('plot-id', 'my-plot');

// Export data as CSV
const figure = getFigureById('plot-id');
downloadDataAsCSV(figure, 'plot-data');

// Copy to clipboard
await copyImageToClipboard('plot-id');
```

### Applying Theme

```javascript
const themedLayout = getThemedLayout('dark');
const layout = applyThemeToLayout(existingLayout, 'dark');
```

### Calculating Grid Layout

```javascript
const gridConfig = calculateOptimalGrid(4, 3, {
  width: 1200,
  height: 800
});

const plotDimensions = calculatePlotDimensions(
  gridConfig,
  { width: 1200, height: 800 },
  { gap: 20, padding: 20 }
);
```

## Recent Updates

### Grid Rendering Fixes (Latest)
- Fixed minor grid not disappearing when unchecked
- Grid color now applies to minor grid lines and zero lines
- Improved grid consistency across all grid elements

### New Utility Modules
- Added `plotExport.js` for comprehensive export functionality
- Added `plotTheme.js` for theme management
- Added `plotLayout.js` for layout calculations
- Created `index.js` as central export point

### Architecture Improvements
- Metadata-driven rendering for all visual properties
- Fixed metadata structure that never changes
- Proper axis type detection (numeric vs categorical)