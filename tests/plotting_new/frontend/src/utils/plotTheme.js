/**
 * Plot theme management utilities
 * Handles theme-specific plot styling and color schemes
 */

/**
 * Get theme-specific plot layout
 * @param {string} theme - Theme name
 * @returns {Object} Plotly layout object with theme styles
 */
export const getThemedLayout = (theme = 'light') => {
  const cs = getComputedStyle(document.documentElement);
  
  // Get CSS variables for current theme
  const bgPrimary = cs.getPropertyValue('--bg-primary').trim();
  const bgSecondary = cs.getPropertyValue('--bg-secondary').trim();
  const textColor = cs.getPropertyValue('--text-color').trim();
  const textSecondary = cs.getPropertyValue('--text-secondary').trim();
  const borderColor = cs.getPropertyValue('--border-color').trim();
  const gridColor = cs.getPropertyValue('--grid-color').trim() || 'rgba(128, 128, 128, 0.1)';
  
  return {
    paper_bgcolor: 'transparent',
    plot_bgcolor: bgPrimary,
    font: {
      family: cs.getPropertyValue('--font-family').trim() || 'system-ui, -apple-system, sans-serif',
      size: 12,
      color: textColor
    },
    xaxis: {
      gridcolor: gridColor,
      zerolinecolor: borderColor,
      linecolor: borderColor,
      tickfont: { color: textSecondary },
      title: { font: { color: textColor } }
    },
    yaxis: {
      gridcolor: gridColor,
      zerolinecolor: borderColor,
      linecolor: borderColor,
      tickfont: { color: textSecondary },
      title: { font: { color: textColor } }
    },
    legend: {
      bgcolor: 'rgba(255, 255, 255, 0.9)',
      bordercolor: borderColor,
      borderwidth: 1,
      font: { color: textColor }
    },
    hoverlabel: {
      bgcolor: bgPrimary,
      bordercolor: borderColor,
      font: { color: textColor }
    },
    colorway: getThemeColorway(),
    margin: { l: 60, r: 20, t: 40, b: 60 }
  };
};

/**
 * Get theme color palette
 * @returns {Array} Array of color values
 */
export const getThemeColorway = () => {
  const cs = getComputedStyle(document.documentElement);
  const colors = [];
  
  // Try to get data colors from CSS variables
  for (let i = 1; i <= 10; i++) {
    const color = cs.getPropertyValue(`--color-data-${i}`).trim();
    if (color) colors.push(color);
  }
  
  // Fallback to default Plotly colors if no custom colors defined
  if (colors.length === 0) {
    return [
      '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
      '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ];
  }
  
  return colors;
};

/**
 * Apply theme to existing layout
 * @param {Object} layout - Existing layout object
 * @param {string} theme - Theme name
 * @returns {Object} Layout with theme applied
 */
export const applyThemeToLayout = (layout, theme = 'light') => {
  const themedLayout = getThemedLayout(theme);
  
  // Merge theme with existing layout, preserving user settings
  return {
    ...themedLayout,
    ...layout,
    xaxis: {
      ...themedLayout.xaxis,
      ...layout.xaxis
    },
    yaxis: {
      ...themedLayout.yaxis,
      ...layout.yaxis
    },
    legend: {
      ...themedLayout.legend,
      ...layout.legend
    },
    font: {
      ...themedLayout.font,
      ...layout.font
    }
  };
};

/**
 * Get marker colors for theme
 * @param {number} count - Number of colors needed
 * @returns {Array} Array of color values
 */
export const getThemeMarkerColors = (count = 10) => {
  const colorway = getThemeColorway();
  const colors = [];
  
  for (let i = 0; i < count; i++) {
    colors.push(colorway[i % colorway.length]);
  }
  
  return colors;
};

/**
 * Get gradient colors for theme
 * @param {string} baseColor - Base color for gradient
 * @param {number} steps - Number of gradient steps
 * @returns {Array} Array of gradient color values
 */
export const getThemeGradient = (baseColor, steps = 5) => {
  // Simple opacity-based gradient
  const gradients = [];
  for (let i = 0; i < steps; i++) {
    const opacity = 1 - (i * 0.15);
    gradients.push(`rgba(${hexToRgb(baseColor)}, ${opacity})`);
  }
  return gradients;
};

/**
 * Convert hex color to RGB
 * @param {string} hex - Hex color value
 * @returns {string} RGB values as comma-separated string
 */
const hexToRgb = (hex) => {
  // Remove # if present
  hex = hex.replace('#', '');
  
  // Convert to RGB
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  
  return `${r}, ${g}, ${b}`;
};

/**
 * Get theme-specific modebar configuration
 * @returns {Object} Plotly modebar config
 */
export const getThemeModebarConfig = () => {
  const cs = getComputedStyle(document.documentElement);
  const primaryColor = cs.getPropertyValue('--primary-color').trim();
  
  return {
    displaylogo: false,
    displayModeBar: true,
    modeBarButtonsToRemove: ['sendDataToCloud', 'lasso2d', 'select2d'],
    modeBarButtonsToAdd: [],
    toImageButtonOptions: {
      format: 'png',
      height: 800,
      width: 1200,
      scale: 2
    }
  };
};

/**
 * Get axis styling for theme
 * @param {string} axisType - 'x', 'y', or 'z'
 * @returns {Object} Axis configuration object
 */
export const getThemeAxisStyle = (axisType = 'x') => {
  const cs = getComputedStyle(document.documentElement);
  const gridColor = cs.getPropertyValue('--grid-color').trim() || 'rgba(128, 128, 128, 0.1)';
  const borderColor = cs.getPropertyValue('--border-color').trim();
  const textColor = cs.getPropertyValue('--text-color').trim();
  const textSecondary = cs.getPropertyValue('--text-secondary').trim();
  
  return {
    showgrid: true,
    gridcolor: gridColor,
    gridwidth: 1,
    zeroline: true,
    zerolinecolor: borderColor,
    zerolinewidth: 1,
    showline: true,
    linecolor: borderColor,
    linewidth: 1,
    tickfont: {
      color: textSecondary,
      size: 11
    },
    titlefont: {
      color: textColor,
      size: 13
    }
  };
};

/**
 * Get annotation styling for theme
 * @returns {Object} Annotation style configuration
 */
export const getThemeAnnotationStyle = () => {
  const cs = getComputedStyle(document.documentElement);
  const textColor = cs.getPropertyValue('--text-color').trim();
  const bgPrimary = cs.getPropertyValue('--bg-primary').trim();
  const borderColor = cs.getPropertyValue('--border-color').trim();
  
  return {
    font: {
      color: textColor,
      size: 12
    },
    bgcolor: bgPrimary,
    bordercolor: borderColor,
    borderwidth: 1,
    borderpad: 4,
    opacity: 0.9
  };
};

/**
 * Check if dark theme is active
 * @returns {boolean} True if dark theme is active
 */
export const isDarkTheme = () => {
  const theme = document.documentElement.getAttribute('data-theme');
  return theme === 'dark' || theme === 'midnight' || theme === 'forest';
};

/**
 * Get contrasting text color for background
 * @param {string} bgColor - Background color
 * @returns {string} Contrasting text color (black or white)
 */
export const getContrastingColor = (bgColor) => {
  // Simple luminance calculation
  const rgb = hexToRgb(bgColor).split(',').map(v => parseInt(v.trim()));
  const luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255;
  return luminance > 0.5 ? '#000000' : '#ffffff';
};