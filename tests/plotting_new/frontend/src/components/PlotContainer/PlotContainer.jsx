import React, { useEffect, useRef, useCallback } from 'react';
import Plotly from 'plotly.js-dist-min';
import { generateLayoutFromMetadata, generateDataFromMetadata } from '../../utils/figureManager';

/**
 * Isolated Plot Container Component
 * Each plot is completely self-contained with its own:
 * - Deep-cloned data and layout
 * - Event handlers
 * - Plotly instance management
 * - No shared state or references
 */
const PlotContainer = ({ 
  figure, 
  plotId, 
  themedLayout,
  onInteraction 
}) => {
  const plotDivRef = useRef(null);
  const plotInstanceRef = useRef(null);
  const interactionHandlersRef = useRef({});

  // Deep clone the themed layout to prevent shared reference issues
  const getIsolatedLayout = useCallback(() => {
    const baseLayout = JSON.parse(JSON.stringify({
      ...figure.layout,
      ...themedLayout
    }));
    return figure.metadata ? 
      generateLayoutFromMetadata(figure, baseLayout) : 
      baseLayout;
  }, [figure, themedLayout]);

  // Get isolated data
  const getIsolatedData = useCallback(() => {
    const data = figure.metadata ? 
      generateDataFromMetadata(figure) : 
      figure.data;
    // Deep clone to ensure complete isolation
    return JSON.parse(JSON.stringify(data));
  }, [figure]);

  // Initialize plot
  const initializePlot = useCallback(() => {
    if (!plotDivRef.current) return;

    const data = getIsolatedData();
    const layout = getIsolatedLayout();
    
    const config = {
      displaylogo: false,
      displayModeBar: false,
      responsive: true,
      scrollZoom: false,
      edits: {
        legendPosition: true,
        titleText: false,
        axisTitleText: false,
      },
    };

    // Clean up any existing plot
    if (plotInstanceRef.current) {
      Plotly.purge(plotDivRef.current);
    }

    // Create new plot with isolated data
    Plotly.newPlot(plotDivRef.current, data, layout, config)
      .then(() => {
        plotInstanceRef.current = plotDivRef.current;
        attachIsolatedInteractions();
      })
      .catch(error => {
        console.error(`Error creating plot ${plotId}:`, error);
      });
  }, [plotId, getIsolatedData, getIsolatedLayout]);

  // Attach isolated interaction handlers
  const attachIsolatedInteractions = useCallback(() => {
    if (!plotDivRef.current) return;

    const plotDiv = plotDivRef.current;
    
    // Prevent context menu
    const handleContextMenu = (e) => e.preventDefault();
    plotDiv.addEventListener('contextmenu', handleContextMenu);
    interactionHandlersRef.current.contextMenu = handleContextMenu;

    // Custom wheel handler for zoom
    const handleWheel = (event) => {
      if (event.shiftKey) return;
      event.preventDefault();
      
      const rect = plotDiv.getBoundingClientRect();
      const layout = plotDiv._fullLayout;
      if (!layout || !layout.xaxis || !layout.yaxis) return;

      const xAxis = layout.xaxis;
      const yAxis = layout.yaxis;
      
      if (!xAxis.range || !yAxis.range) return;

      const relX = (event.clientX - rect.left) / rect.width;
      const relY = 1 - (event.clientY - rect.top) / rect.height;
      
      const xCenter = xAxis.range[0] + relX * (xAxis.range[1] - xAxis.range[0]);
      const yCenter = yAxis.range[0] + relY * (yAxis.range[1] - yAxis.range[0]);
      
      // Reduced zoom sensitivity for smoother scrolling
      const delta = event.deltaY > 0 ? -0.05 : 0.05;
      const factor = 1 + delta;
      
      const newXRange = [
        xCenter - (xCenter - xAxis.range[0]) * factor,
        xCenter + (xAxis.range[1] - xCenter) * factor
      ];
      const newYRange = [
        yCenter - (yCenter - yAxis.range[0]) * factor,
        yCenter + (yAxis.range[1] - yCenter) * factor
      ];
      
      // Update only this plot's ranges
      Plotly.relayout(plotDiv, {
        'xaxis.range': newXRange,
        'yaxis.range': newYRange
      });

      if (onInteraction) {
        onInteraction({ type: 'zoom', plotId, xRange: newXRange, yRange: newYRange });
      }
    };
    
    plotDiv.addEventListener('wheel', handleWheel, { passive: false });
    interactionHandlersRef.current.wheel = handleWheel;

    // Right-click drag for scaling
    let scaleStartX = 0, scaleStartY = 0;
    let scaleInitXRange = null, scaleInitYRange = null;
    
    const handleScaleMove = (moveEvt) => {
      if (moveEvt.buttons !== 2) return;
      
      const rect = plotDiv.getBoundingClientRect();
      const dx = moveEvt.clientX - scaleStartX;
      const dy = moveEvt.clientY - scaleStartY;
      const sensitivity = 0.2;
      const factorX = 1 - dx / (rect.width * sensitivity);
      const factorY = 1 + dy / (rect.height * sensitivity);

      const clamp = (val, min, max) => Math.max(min, Math.min(max, val));
      const fx = clamp(factorX, 0.1, 10);
      const fy = clamp(factorY, 0.1, 10);

      if (scaleInitXRange && scaleInitYRange) {
        const xCenter = (scaleInitXRange[0] + scaleInitXRange[1]) / 2;
        const xHalf = (scaleInitXRange[1] - scaleInitXRange[0]) / 2 * fx;
        const yCenter = (scaleInitYRange[0] + scaleInitYRange[1]) / 2;
        const yHalf = (scaleInitYRange[1] - scaleInitYRange[0]) / 2 * fy;
        
        const newXRange = [xCenter - xHalf, xCenter + xHalf];
        const newYRange = [yCenter - yHalf, yCenter + yHalf];
        
        Plotly.relayout(plotDiv, {
          'xaxis.range': newXRange,
          'yaxis.range': newYRange
        });
      }
    };

    const handleScaleUp = () => {
      window.removeEventListener('pointermove', handleScaleMove);
      window.removeEventListener('pointerup', handleScaleUp);
    };

    const handleScaleDown = (downEvt) => {
      if (downEvt.button !== 2) return;
      downEvt.preventDefault();
      
      const layout = plotDiv._fullLayout;
      if (!layout || !layout.xaxis || !layout.yaxis) return;
      
      scaleStartX = downEvt.clientX;
      scaleStartY = downEvt.clientY;
      scaleInitXRange = [...layout.xaxis.range];
      scaleInitYRange = [...layout.yaxis.range];
      
      window.addEventListener('pointermove', handleScaleMove);
      window.addEventListener('pointerup', handleScaleUp);
    };

    plotDiv.addEventListener('pointerdown', handleScaleDown);
    interactionHandlersRef.current.scaleDown = handleScaleDown;

    // Middle-click drag for panning
    let panStartX = 0, panStartY = 0;
    let panInitXRange = null, panInitYRange = null;

    const handlePanMove = (mvEvt) => {
      if ((mvEvt.buttons & 4) === 0) return;
      
      const rect = plotDiv.getBoundingClientRect();
      const dx = mvEvt.clientX - panStartX;
      const dy = mvEvt.clientY - panStartY;
      
      if (panInitXRange && panInitYRange) {
        const xScale = (panInitXRange[1] - panInitXRange[0]) / rect.width;
        const yScale = (panInitYRange[1] - panInitYRange[0]) / rect.height;
        const xOffset = dx * xScale;
        const yOffset = -dy * yScale;

        const newXRange = [panInitXRange[0] - xOffset, panInitXRange[1] - xOffset];
        const newYRange = [panInitYRange[0] - yOffset, panInitYRange[1] - yOffset];

        Plotly.relayout(plotDiv, {
          'xaxis.range': newXRange,
          'yaxis.range': newYRange
        });
      }
    };

    const handlePanUp = () => {
      window.removeEventListener('pointermove', handlePanMove);
      window.removeEventListener('pointerup', handlePanUp);
    };

    const handlePanDown = (pdEvt) => {
      if (pdEvt.button !== 1) return;
      pdEvt.preventDefault();
      
      const layout = plotDiv._fullLayout;
      if (!layout || !layout.xaxis || !layout.yaxis) return;
      
      panStartX = pdEvt.clientX;
      panStartY = pdEvt.clientY;
      panInitXRange = [...layout.xaxis.range];
      panInitYRange = [...layout.yaxis.range];
      
      window.addEventListener('pointermove', handlePanMove);
      window.addEventListener('pointerup', handlePanUp);
    };

    plotDiv.addEventListener('pointerdown', handlePanDown);
    interactionHandlersRef.current.panDown = handlePanDown;
  }, [plotId, onInteraction]);

  // Update plot when figure changes
  const updatePlot = useCallback(() => {
    if (!plotDivRef.current || !plotInstanceRef.current) {
      initializePlot();
      return;
    }

    const data = getIsolatedData();
    const layout = getIsolatedLayout();

    Plotly.react(plotDivRef.current, data, layout)
      .catch(error => {
        console.error(`Error updating plot ${plotId}:`, error);
      });
  }, [plotId, initializePlot, getIsolatedData, getIsolatedLayout]);

  // Initialize on mount
  useEffect(() => {
    initializePlot();

    // Cleanup on unmount
    return () => {
      const plotDiv = plotDivRef.current;
      if (plotDiv) {
        // Remove all event listeners
        Object.values(interactionHandlersRef.current).forEach(handler => {
          if (handler) {
            plotDiv.removeEventListener('contextmenu', interactionHandlersRef.current.contextMenu);
            plotDiv.removeEventListener('wheel', interactionHandlersRef.current.wheel);
            plotDiv.removeEventListener('pointerdown', interactionHandlersRef.current.scaleDown);
            plotDiv.removeEventListener('pointerdown', interactionHandlersRef.current.panDown);
          }
        });
        
        // Purge Plotly instance
        if (plotInstanceRef.current) {
          Plotly.purge(plotDiv);
        }
      }
    };
  }, []); // Only run on mount/unmount

  // Update when figure or theme changes
  useEffect(() => {
    updatePlot();
  }, [figure, themedLayout]);

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      if (plotDivRef.current && plotInstanceRef.current) {
        Plotly.Plots.resize(plotDivRef.current);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div 
      ref={plotDivRef}
      id={plotId}
      style={{ 
        width: '100%', 
        height: '100%',
        position: 'relative'
      }}
    />
  );
};

export default PlotContainer;