// Helper functions for color handling
export const extractAlphaFromColor = (color) => {
  if (!color) return 0.3;
  // Handle rgba format
  const rgbaMatch = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+),?\s*([0-9.]+)?\)/);
  if (rgbaMatch) {
    return parseFloat(rgbaMatch[4] || 1);
  }
  // Handle hex with alpha
  if (color.length === 9 && color.startsWith('#')) {
    const alpha = parseInt(color.slice(7, 9), 16) / 255;
    return alpha;
  }
  return 0.3; // default
};

export const extractColorWithoutAlpha = (color) => {
  if (!color) return null;
  // Handle rgba format
  const rgbaMatch = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+),?\s*([0-9.]+)?\)/);
  if (rgbaMatch) {
    const r = parseInt(rgbaMatch[1]);
    const g = parseInt(rgbaMatch[2]);
    const b = parseInt(rgbaMatch[3]);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  }
  // Handle hex with alpha - remove alpha
  if (color.length === 9 && color.startsWith('#')) {
    return color.slice(0, 7);
  }
  return color;
};

export const colorToRgba = (color, opacity) => {
  if (!color) return `rgba(128, 128, 128, ${opacity})`;
  // Convert hex to rgba
  const hex = color.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};