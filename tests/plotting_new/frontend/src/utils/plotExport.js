/**
 * Plot export utilities
 * Handles exporting plots in various formats
 */
import Plotly from 'plotly.js-dist-min';

/**
 * Export a plot as an image
 * @param {string} plotId - The plot element ID
 * @param {Object} options - Export options
 * @returns {Promise} Promise that resolves when export is complete
 */
export const exportAsImage = (plotId, options = {}) => {
  const defaultOptions = {
    format: 'png',
    width: 1200,
    height: 800,
    scale: 2,
    filename: `plot-${new Date().toISOString().split('T')[0]}`
  };
  
  const config = { ...defaultOptions, ...options };
  
  return Plotly.downloadImage(plotId, config);
};

/**
 * Export plot as SVG
 * @param {string} plotId - The plot element ID
 * @param {string} filename - Output filename
 */
export const exportAsSVG = (plotId, filename = 'plot') => {
  return exportAsImage(plotId, {
    format: 'svg',
    filename: `${filename}.svg`,
    width: 1200,
    height: 800
  });
};

/**
 * Export plot as high-resolution PNG
 * @param {string} plotId - The plot element ID
 * @param {string} filename - Output filename
 */
export const exportAsHighResPNG = (plotId, filename = 'plot') => {
  return exportAsImage(plotId, {
    format: 'png',
    filename: `${filename}-hires.png`,
    width: 2400,
    height: 1600,
    scale: 2
  });
};

/**
 * Export plot data as CSV
 * @param {Object} figure - The figure object
 * @returns {string} CSV string
 */
export const exportDataAsCSV = (figure) => {
  if (!figure || !figure.data || figure.data.length === 0) {
    return '';
  }
  
  const rows = [];
  const headers = new Set();
  
  // Collect all unique headers
  figure.data.forEach(trace => {
    if (trace.x) headers.add(`${trace.name || 'Series'}_X`);
    if (trace.y) headers.add(`${trace.name || 'Series'}_Y`);
    if (trace.z) headers.add(`${trace.name || 'Series'}_Z`);
  });
  
  // Create header row
  rows.push(Array.from(headers).join(','));
  
  // Find max length of data arrays
  let maxLength = 0;
  figure.data.forEach(trace => {
    if (trace.x) maxLength = Math.max(maxLength, trace.x.length);
    if (trace.y) maxLength = Math.max(maxLength, trace.y.length);
    if (trace.z) maxLength = Math.max(maxLength, trace.z.length);
  });
  
  // Create data rows
  for (let i = 0; i < maxLength; i++) {
    const row = [];
    figure.data.forEach(trace => {
      if (trace.x) row.push(trace.x[i] || '');
      if (trace.y) row.push(trace.y[i] || '');
      if (trace.z) row.push(trace.z[i] || '');
    });
    rows.push(row.join(','));
  }
  
  return rows.join('\n');
};

/**
 * Download CSV data as file
 * @param {Object} figure - The figure object
 * @param {string} filename - Output filename
 */
export const downloadDataAsCSV = (figure, filename = 'plot-data') => {
  const csv = exportDataAsCSV(figure);
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Export plot configuration as JSON
 * @param {Object} figure - The figure object
 * @returns {string} JSON string
 */
export const exportAsJSON = (figure) => {
  return JSON.stringify(figure, null, 2);
};

/**
 * Download plot configuration as JSON file
 * @param {Object} figure - The figure object
 * @param {string} filename - Output filename
 */
export const downloadAsJSON = (figure, filename = 'plot-config') => {
  const json = exportAsJSON(figure);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Copy plot as image to clipboard (if supported)
 * @param {string} plotId - The plot element ID
 * @returns {Promise} Promise that resolves when copy is complete
 */
export const copyImageToClipboard = async (plotId) => {
  if (!navigator.clipboard || !window.ClipboardItem) {
    throw new Error('Clipboard API not supported');
  }
  
  const graphDiv = document.getElementById(plotId);
  if (!graphDiv) {
    throw new Error('Plot element not found');
  }
  
  // Convert plot to blob
  const dataUrl = await Plotly.toImage(graphDiv, {
    format: 'png',
    width: 1200,
    height: 800
  });
  
  const response = await fetch(dataUrl);
  const blob = await response.blob();
  
  // Copy to clipboard
  await navigator.clipboard.write([
    new ClipboardItem({ 'image/png': blob })
  ]);
};

/**
 * Get available export formats
 * @returns {Array} Array of format objects
 */
export const getExportFormats = () => [
  { id: 'png', label: 'PNG Image', extension: 'png', type: 'image' },
  { id: 'svg', label: 'SVG Vector', extension: 'svg', type: 'image' },
  { id: 'jpeg', label: 'JPEG Image', extension: 'jpeg', type: 'image' },
  { id: 'webp', label: 'WebP Image', extension: 'webp', type: 'image' },
  { id: 'csv', label: 'CSV Data', extension: 'csv', type: 'data' },
  { id: 'json', label: 'JSON Config', extension: 'json', type: 'config' }
];