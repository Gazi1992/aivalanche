/**
 * Utility functions for accessing CSS variables from JavaScript
 */

/**
 * Get a CSS variable value from the document root
 * @param {string} variable - CSS variable name (including --)
 * @param {string} defaultValue - Default value if variable not found
 * @returns {string} The CSS variable value or default
 */
export const getCSSVariable = (variable, defaultValue = '') => {
  if (typeof document !== 'undefined') {
    const value = getComputedStyle(document.documentElement)
      .getPropertyValue(variable)
      .trim();
    return value || defaultValue;
  }
  return defaultValue;
};

/**
 * Get all theme-related colors from CSS variables
 * @returns {Object} Object containing all theme colors
 */
export const getThemeColors = () => ({
  dataColor1: getCSSVariable('--color-data-1', '#1f77b4'),
  dataColor2: getCSSVariable('--color-data-2', '#ff7f0e'),
  dataColor3: getCSSVariable('--color-data-3', '#2ca02c'),
  dataColor4: getCSSVariable('--color-data-4', '#d62728'),
  dataColor5: getCSSVariable('--color-data-5', '#9467bd'),
  dataColor6: getCSSVariable('--color-data-6', '#8c564b'),
  dataColor7: getCSSVariable('--color-data-7', '#e377c2'),
  dataColor8: getCSSVariable('--color-data-8', '#7f7f7f'),
  dataColor9: getCSSVariable('--color-data-9', '#bcbd22'),
  dataColor10: getCSSVariable('--color-data-10', '#17becf'),
  primaryColor: getCSSVariable('--primary-color', '#007bff'),
  backgroundColor: getCSSVariable('--background-color', '#ffffff'),
  textColor: getCSSVariable('--text-color', '#333333'),
  borderColor: getCSSVariable('--border-color', '#e0e0e0'),
  cardBackgroundColor: getCSSVariable('--card-background-color', '#ffffff'),
  bgPrimary: getCSSVariable('--bg-primary', '#ffffff'),
  bgSecondary: getCSSVariable('--bg-secondary', '#f5f5f5'),
  bgTertiary: getCSSVariable('--bg-tertiary', '#eeeeee'),
});

/**
 * Get sidebar dimensions from CSS variables
 * @returns {Object} Object containing sidebar dimensions
 */
export const getSidebarDimensions = () => ({
  expandedWidth: parseInt(getCSSVariable('--sidebar-width-expanded', '500')) || 500,
  collapsedWidth: parseInt(getCSSVariable('--sidebar-width-collapsed', '60')) || 60,
});

/**
 * Get plot-specific colors from CSS variables
 * @returns {Object} Object containing plot colors
 */
export const getPlotColors = () => ({
  figureBackground: getCSSVariable('--figure-background', 'transparent'),
  figureBorderColor: getCSSVariable('--figure-border-color', 'rgba(0, 0, 0, 0)'),
  plotBackground: getCSSVariable('--plot-background', 'rgba(255, 255, 255, 0)'),
  plotBorderColor: getCSSVariable('--plot-border-color', 'rgba(128, 128, 128, 0.2)'),
  legendBg: getCSSVariable('--legend-bg', 'rgba(255, 255, 255, 0.95)'),
  legendBorder: getCSSVariable('--legend-border', 'rgba(226, 232, 240, 0.8)'),
  legendText: getCSSVariable('--legend-text', '#444444'),
});

/**
 * Get container dimensions from CSS variables
 * @returns {Object} Object containing container dimensions
 */
export const getContainerDimensions = () => ({
  containerPadding: getCSSVariable('--container-padding', '20px'),
  containerBorderRadius: getCSSVariable('--container-border-radius', '12px'),
  plotPadding: getCSSVariable('--plot-padding', '10px'),
});