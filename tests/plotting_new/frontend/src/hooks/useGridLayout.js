import { useState, useMemo, useEffect } from 'react';
import { calculateGridDimensions } from '../utils/plotUtils';

/**
 * Custom hook for managing grid layout calculations
 */
export const useGridLayout = (figureCount) => {
  const [gridColumns, setGridColumns] = useState(2);
  const [windowHeight, setWindowHeight] = useState(window.innerHeight);
  
  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      setWindowHeight(window.innerHeight);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // Calculate grid dimensions
  const gridDimensions = useMemo(() => {
    return calculateGridDimensions(figureCount, gridColumns, windowHeight);
  }, [figureCount, gridColumns, windowHeight]);
  
  const plotContainerStyle = useMemo(() => ({
    position: 'relative',
    backgroundColor: 'var(--card-background-color)',
    borderRadius: 'var(--container-border-radius)',
    padding: 'var(--plot-padding)',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    height: gridDimensions.plotHeight + 'px',
    minHeight: '300px',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  }), [gridDimensions.plotHeight]);
  
  return {
    gridColumns,
    setGridColumns,
    windowHeight,
    gridDimensions,
    plotContainerStyle,
    nCols: gridDimensions.nCols,
    nRows: gridDimensions.nRows,
    plotHeight: gridDimensions.plotHeight,
    gridStyle: gridDimensions.gridStyle
  };
};