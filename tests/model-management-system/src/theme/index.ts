// Central theme configuration for the Model Management System
export const theme = {
  colors: {
    // Brand colors
    primary: {
      50: 'bg-purple-50',
      100: 'bg-purple-100',
      200: 'bg-purple-200',
      500: 'bg-purple-500',
      600: 'bg-purple-600',
      700: 'bg-purple-700',
      800: 'bg-purple-800',
      900: 'bg-purple-900',
      text: 'text-purple-600',
      textDark: 'text-purple-700',
      textLight: 'text-purple-200',
      border: 'border-purple-200',
      borderDark: 'border-purple-600',
    },
    // Status colors
    success: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      icon: 'text-green-600',
      border: 'border-green-200',
    },
    info: {
      bg: 'bg-blue-100',
      text: 'text-blue-800',
      icon: 'text-blue-600',
      border: 'border-blue-200',
    },
    warning: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800',
      icon: 'text-yellow-600',
      border: 'border-yellow-200',
    },
    error: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      icon: 'text-red-600',
      border: 'border-red-200',
    },
    // Neutral colors
    gray: {
      50: 'bg-gray-50',
      100: 'bg-gray-100',
      200: 'bg-gray-200',
      300: 'bg-gray-300',
      400: 'bg-gray-400',
      500: 'bg-gray-500',
      600: 'bg-gray-600',
      700: 'bg-gray-700',
      800: 'bg-gray-800',
      900: 'bg-gray-900',
      text: {
        primary: 'text-gray-900',
        secondary: 'text-gray-700',
        tertiary: 'text-gray-600',
        muted: 'text-gray-500',
        placeholder: 'text-gray-400',
      },
      border: 'border-gray-200',
      borderDark: 'border-gray-300',
    },
  },
  
  typography: {
    // Headings
    h1: 'text-3xl font-bold text-gray-900',
    h2: 'text-2xl font-bold text-gray-900',
    h3: 'text-xl font-semibold text-gray-900',
    h4: 'text-lg font-semibold text-gray-900',
    h5: 'text-base font-semibold text-gray-900',
    
    // Body text
    body: 'text-sm text-gray-700',
    bodySmall: 'text-xs text-gray-600',
    bodyLarge: 'text-base text-gray-700',
    
    // Labels
    label: 'text-sm font-medium text-gray-700',
    labelSmall: 'text-xs font-medium text-gray-600',
    
    // Special
    metric: 'text-2xl font-bold text-gray-900',
    metricLabel: 'text-sm font-medium text-gray-600',
    caption: 'text-xs text-gray-500',
  },
  
  spacing: {
    xs: 'p-2',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
    xl: 'p-8',
    
    gap: {
      xs: 'gap-2',
      sm: 'gap-3',
      md: 'gap-4',
      lg: 'gap-6',
      xl: 'gap-8',
    },
  },
  
  borderRadius: {
    sm: 'rounded',
    md: 'rounded-lg',
    lg: 'rounded-xl',
    full: 'rounded-full',
  },
  
  shadows: {
    sm: 'shadow-sm',
    md: 'shadow',
    lg: 'shadow-lg',
    xl: 'shadow-xl',
  },
  
  transitions: {
    default: 'transition-colors duration-200',
    all: 'transition-all duration-200',
    slow: 'transition-all duration-300',
  },
  
  icons: {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
    xl: 'w-8 h-8',
    xxl: 'w-12 h-12',
  },
  
  // Standardized icon colors for actions
  iconColors: {
    download: 'text-green-600 hover:text-green-900',
    share: 'text-blue-600 hover:text-blue-900',
    edit: 'text-purple-600 hover:text-purple-900',
    report: 'text-orange-600 hover:text-orange-900',
    delete: 'text-red-600 hover:text-red-900',
    view: 'text-blue-600 hover:text-blue-900',
    issue: 'text-orange-600 hover:text-orange-700',
    primary: 'text-purple-600 hover:text-purple-900',
    // Status colors
    success: 'text-green-600',
    info: 'text-blue-600',
    warning: 'text-yellow-600',
    error: 'text-red-600',
    neutral: 'text-gray-600',
  },
  
  gradients: {
    brand: 'bg-gradient-to-r from-purple-600 to-blue-600',
    brandSubtle: 'bg-gradient-to-r from-purple-500 to-indigo-500',
    purple: 'bg-gradient-to-r from-purple-400 to-pink-400',
  },
};

// Status color mappings
export const statusColors = {
  production: 'bg-green-100 text-green-800',
  validated: 'bg-blue-100 text-blue-800',
  development: 'bg-yellow-100 text-yellow-800',
  testing: 'bg-orange-100 text-orange-800',
  failed: 'bg-red-100 text-red-800',
  pending: 'bg-gray-100 text-gray-800',
  completed: 'bg-green-100 text-green-800',
  'in-progress': 'bg-blue-100 text-blue-800',
  calibrating: 'bg-purple-100 text-purple-800',
};

// Common button styles
export const buttonStyles = {
  base: 'inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
  
  sizes: {
    xs: 'px-2 py-1 text-xs rounded',
    sm: 'px-3 py-1.5 text-sm rounded-md',
    md: 'px-4 py-2 text-sm rounded-lg',
    lg: 'px-6 py-3 text-base rounded-lg',
  },
  
  variants: {
    primary: 'bg-purple-600 text-white hover:bg-purple-700 focus:ring-purple-500',
    secondary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 focus:ring-purple-500',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    ghost: 'text-gray-600 hover:bg-gray-100 focus:ring-gray-500',
    link: 'text-purple-600 hover:text-purple-700 underline-offset-4 hover:underline',
  },
  
  disabled: 'opacity-50 cursor-not-allowed pointer-events-none',
};

// Card styles
export const cardStyles = {
  base: 'bg-white rounded-lg shadow',
  bordered: 'bg-white rounded-lg border border-gray-200',
  elevated: 'bg-white rounded-lg shadow-lg',
  interactive: 'bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer',
};

// Modal styles
export const modalStyles = {
  overlay: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50',
  container: 'bg-white rounded-lg max-h-[90vh] flex flex-col',
  header: 'px-6 py-4 border-b border-gray-200 flex items-center justify-between flex-shrink-0',
  body: 'flex-1 overflow-y-auto px-6 py-4',
  footer: 'px-6 py-4 border-t border-gray-200 flex justify-end gap-3 flex-shrink-0',
};

// Input styles
export const inputStyles = {
  base: 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500',
  error: 'border-red-300 focus:ring-red-500 focus:border-red-500',
  disabled: 'bg-gray-50 text-gray-500 cursor-not-allowed',
};

// Table styles
export const tableStyles = {
  container: 'overflow-x-auto',
  table: 'min-w-full divide-y divide-gray-200',
  header: 'bg-gray-50',
  headerCell: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
  body: 'bg-white divide-y divide-gray-200',
  cell: 'px-6 py-4 whitespace-nowrap text-sm text-gray-900',
};

// Stats Card styles
export const statsCardStyles = {
  container: 'bg-white rounded-lg shadow-sm hover:shadow-lg transition-all duration-200 border border-gray-100',
  containerPurple: 'bg-white rounded-lg shadow-sm hover:shadow-lg transition-all duration-200 p-4 border border-gray-100 hover:border-purple-200',
  containerBlue: 'bg-white rounded-lg shadow-sm hover:shadow-lg transition-all duration-200 p-4 border border-gray-100 hover:border-blue-200',
  containerGreen: 'bg-white rounded-lg shadow-sm hover:shadow-lg transition-all duration-200 p-4 border border-gray-100 hover:border-green-200',
  containerOrange: 'bg-white rounded-lg shadow-sm hover:shadow-lg transition-all duration-200 p-4 border border-gray-100 hover:border-orange-200',
  content: 'flex items-center justify-between',
  label: 'text-xs font-medium text-gray-500 uppercase tracking-wider',
  value: 'text-2xl font-bold text-gray-900 mt-1',
  iconContainer: 'p-2.5 rounded-lg',
  iconContainerPurple: 'p-2.5 bg-purple-50 rounded-lg',
  iconContainerBlue: 'p-2.5 bg-blue-50 rounded-lg',
  iconContainerGreen: 'p-2.5 bg-green-50 rounded-lg',
  iconContainerOrange: 'p-2.5 bg-orange-50 rounded-lg',
  icon: 'w-6 h-6',
  iconPurple: 'w-6 h-6 text-purple-600',
  iconBlue: 'w-6 h-6 text-blue-600',
  iconGreen: 'w-6 h-6 text-green-600',
  iconOrange: 'w-6 h-6 text-orange-600',
  // Mini variant for compact views - vertical center-aligned layout
  mini: {
    container: 'bg-white rounded shadow-sm hover:shadow-md transition-all duration-200 p-2 border border-gray-100',
    content: 'flex flex-col items-center justify-center text-center',
    label: 'text-[10px] font-medium text-gray-500 uppercase tracking-wide mt-1',
    value: 'text-lg font-bold text-gray-900',
    iconContainer: 'p-1.5 rounded-lg mb-1',
    iconContainerPurple: 'p-1.5 bg-purple-50 rounded-lg mb-1',
    iconContainerBlue: 'p-1.5 bg-blue-50 rounded-lg mb-1',
    iconContainerGreen: 'p-1.5 bg-green-50 rounded-lg mb-1',
    iconContainerOrange: 'p-1.5 bg-orange-50 rounded-lg mb-1',
    icon: 'w-4 h-4',
    iconPurple: 'w-4 h-4 text-purple-600',
    iconBlue: 'w-4 h-4 text-blue-600',
    iconGreen: 'w-4 h-4 text-green-600',
    iconOrange: 'w-4 h-4 text-orange-600',
  },
  // For reference data viewer specific styles
  compactPadding: 'p-3',
  normalPadding: 'p-4',
};