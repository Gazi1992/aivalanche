import React, { useEffect, useRef, useCallback } from 'react';
import Plotly from 'plotly.js-dist-min';
import PlotButton from '../PlotButton';
import { EditIcon, TableIcon, ExpandIcon, ShrinkIcon, DownloadIcon, AutoscaleIcon, LegendToggleIcon } from '../icons';
import { generateLayoutFromMetadata, generateDataFromMetadata } from '../../utils/figureManager';
import { downloadPlotAsImage } from '../../utils/plotUtils';

/**
 * Isolated Plot Container Component
 * Each plot is completely self-contained with its own:
 * - Deep-cloned data and layout
 * - Event handlers
 * - Plotly instance management
 * - Plot control buttons
 * - No shared state or references
 */
const PlotContainer = ({
  figure,
  plotId,
  themedLayout,
  onInteraction,
  onEdit,
  onViewTable,
  onExpand,
  isExpanded = false,
  showExpandButton = true
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

    // Check if this is a 3D plot
    const is3D = layout.scene || (data && data[0] &&
                 (data[0].type === 'scatter3d' ||
                  data[0].type === 'surface' ||
                  data[0].type === 'mesh3d'));

    const config = {
      displaylogo: false,
      displayModeBar: false,
      responsive: true,
      scrollZoom: is3D, // Enable scroll zoom for 3D plots
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

    // Check if this is a special plot type
    const plotData = plotDiv._fullData;
    let isSplom = false;
    if (plotData && plotData.length > 0) {
      const firstTrace = plotData[0];
      isSplom = firstTrace.type === 'splom';
    }

    // Check if this is a 3D plot
    const layout = plotDiv._fullLayout;
    const is3D = layout && (layout.scene || (figure.data && figure.data[0] &&
                 (figure.data[0].type === 'scatter3d' ||
                  figure.data[0].type === 'surface' ||
                  figure.data[0].type === 'mesh3d')));

    // Prevent context menu
    const handleContextMenu = (e) => e.preventDefault();
    plotDiv.addEventListener('contextmenu', handleContextMenu);
    interactionHandlersRef.current.contextMenu = handleContextMenu;

    // Custom wheel handler for zoom (only for 2D plots)
    const handleWheel = (event) => {
      const layout = plotDiv._fullLayout;
      if (!layout) return;

      // Skip custom handling for 3D plots - let Plotly handle it natively
      const is3D = layout.scene || (figure.data && figure.data[0] &&
                   (figure.data[0].type === 'scatter3d' ||
                    figure.data[0].type === 'surface' ||
                    figure.data[0].type === 'mesh3d'));
      if (is3D) return;

      if (event.shiftKey) return;
      event.preventDefault();

      const rect = plotDiv.getBoundingClientRect();

      // Reduced zoom sensitivity for smoother scrolling
      const delta = event.deltaY > 0 ? -0.05 : 0.05;
      const factor = 1 + delta;
      
      // For SPLOM, we need to handle multiple axes
      if (isSplom) {
        const relX = (event.clientX - rect.left) / rect.width;
        const relY = 1 - (event.clientY - rect.top) / rect.height;
        
        // Find which subplot we're hovering over
        const update = {};
        
        // SPLOM uses xaxis, xaxis2, xaxis3, etc.
        Object.keys(layout).forEach(key => {
          if (key.startsWith('xaxis')) {
            const axis = layout[key];
            if (axis && axis.domain && axis.range) {
              // Check if mouse is within this axis domain
              if (relX >= axis.domain[0] && relX <= axis.domain[1]) {
                const xCenter = axis.range[0] + 0.5 * (axis.range[1] - axis.range[0]);
                update[`${key}.range`] = [
                  xCenter - (xCenter - axis.range[0]) * factor,
                  xCenter + (axis.range[1] - xCenter) * factor
                ];
              }
            }
          }
          if (key.startsWith('yaxis')) {
            const axis = layout[key];
            if (axis && axis.domain && axis.range) {
              // Check if mouse is within this axis domain
              if (relY >= axis.domain[0] && relY <= axis.domain[1]) {
                const yCenter = axis.range[0] + 0.5 * (axis.range[1] - axis.range[0]);
                update[`${key}.range`] = [
                  yCenter - (yCenter - axis.range[0]) * factor,
                  yCenter + (axis.range[1] - yCenter) * factor
                ];
              }
            }
          }
        });
        
        if (Object.keys(update).length > 0) {
          Plotly.relayout(plotDiv, update);
        }
      } else {
        // Regular plot handling
        if (!layout.xaxis || !layout.yaxis) return;
        
        const xAxis = layout.xaxis;
        const yAxis = layout.yaxis;
        
        if (!xAxis.range || !yAxis.range) return;

        const relX = (event.clientX - rect.left) / rect.width;
        const relY = 1 - (event.clientY - rect.top) / rect.height;
        
        const xCenter = xAxis.range[0] + relX * (xAxis.range[1] - xAxis.range[0]);
        const yCenter = yAxis.range[0] + relY * (yAxis.range[1] - yAxis.range[0]);
        
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
      }
    };
    
    plotDiv.addEventListener('wheel', handleWheel, { passive: false });
    interactionHandlersRef.current.wheel = handleWheel;

    // For 3D plots, don't attach any custom handlers - use Plotly's native interactions
    if (is3D) {
      return;
    }

    // Middle-click drag for scaling (only for 2D plots)
    let scaleStartX = 0, scaleStartY = 0;
    let scaleInitRanges = {};
    let scaleStartRelX = 0, scaleStartRelY = 0;

    const handleScaleMove = (moveEvt) => {
      if ((moveEvt.buttons & 4) === 0) return; // Check for middle button
      
      const rect = plotDiv.getBoundingClientRect();
      const dx = moveEvt.clientX - scaleStartX;
      const dy = moveEvt.clientY - scaleStartY;
      const sensitivity = 0.2;
      const factorX = 1 - dx / (rect.width * sensitivity);
      const factorY = 1 + dy / (rect.height * sensitivity);

      const clamp = (val, min, max) => Math.max(min, Math.min(max, val));
      const fx = clamp(factorX, 0.1, 10);
      const fy = clamp(factorY, 0.1, 10);

      const update = {};
      
      if (isSplom) {
        // For SPLOM, only scale axes in same row/column based on starting position
        const layout = plotDiv._fullLayout;
        
        Object.keys(scaleInitRanges).forEach(axisName => {
          const axis = layout[axisName];
          if (!axis || !axis.domain) return;
          
          const initRange = scaleInitRanges[axisName];
          const isX = axisName.startsWith('xaxis');
          
          // Check if this axis should be scaled based on initial mouse position
          let shouldScale = false;
          if (isX) {
            // X-axis: scale if mouse started in this column
            if (scaleStartRelX >= axis.domain[0] && scaleStartRelX <= axis.domain[1]) {
              shouldScale = true;
            }
          } else {
            // Y-axis: scale if mouse started in this row
            if (scaleStartRelY >= axis.domain[0] && scaleStartRelY <= axis.domain[1]) {
              shouldScale = true;
            }
          }
          
          if (shouldScale) {
            const center = (initRange[0] + initRange[1]) / 2;
            const factor = isX ? fx : fy;
            const half = (initRange[1] - initRange[0]) / 2 * factor;
            update[`${axisName}.range`] = [center - half, center + half];
          }
        });
      } else {
        // Regular plot
        if (scaleInitRanges.xaxis && scaleInitRanges.yaxis) {
          const xCenter = (scaleInitRanges.xaxis[0] + scaleInitRanges.xaxis[1]) / 2;
          const xHalf = (scaleInitRanges.xaxis[1] - scaleInitRanges.xaxis[0]) / 2 * fx;
          const yCenter = (scaleInitRanges.yaxis[0] + scaleInitRanges.yaxis[1]) / 2;
          const yHalf = (scaleInitRanges.yaxis[1] - scaleInitRanges.yaxis[0]) / 2 * fy;
          
          update['xaxis.range'] = [xCenter - xHalf, xCenter + xHalf];
          update['yaxis.range'] = [yCenter - yHalf, yCenter + yHalf];
        }
      }
      
      if (Object.keys(update).length > 0) {
        Plotly.relayout(plotDiv, update);
      }
    };

    const handleScaleUp = () => {
      window.removeEventListener('pointermove', handleScaleMove);
      window.removeEventListener('pointerup', handleScaleUp);
    };

    const handleScaleDown = (downEvt) => {
      if (downEvt.button !== 1) return; // Middle button
      downEvt.preventDefault();
      
      const rect = plotDiv.getBoundingClientRect();
      scaleStartX = downEvt.clientX;
      scaleStartY = downEvt.clientY;
      scaleStartRelX = (downEvt.clientX - rect.left) / rect.width;
      scaleStartRelY = 1 - (downEvt.clientY - rect.top) / rect.height;
      scaleInitRanges = {};
      
      if (isSplom) {
        // Store all axis ranges for SPLOM
        Object.keys(layout).forEach(key => {
          if ((key.startsWith('xaxis') || key.startsWith('yaxis')) && layout[key].range) {
            scaleInitRanges[key] = [...layout[key].range];
          }
        });
      } else {
        // Regular plot
        if (layout.xaxis && layout.yaxis && layout.xaxis.range && layout.yaxis.range) {
          scaleInitRanges.xaxis = [...layout.xaxis.range];
          scaleInitRanges.yaxis = [...layout.yaxis.range];
        }
      }
      
      if (Object.keys(scaleInitRanges).length > 0) {
        window.addEventListener('pointermove', handleScaleMove);
        window.addEventListener('pointerup', handleScaleUp);
      }
    };

    plotDiv.addEventListener('pointerdown', handleScaleDown);
    interactionHandlersRef.current.scaleDown = handleScaleDown;

    // Right-click drag for panning
    let panStartX = 0, panStartY = 0;
    let panInitRanges = {};

    const handlePanMove = (mvEvt) => {
      if (mvEvt.buttons !== 2) return; // Right button

      const rect = plotDiv.getBoundingClientRect();
      const dx = mvEvt.clientX - panStartX;
      const dy = mvEvt.clientY - panStartY;

      const update = {};

      if (isSplom) {
        // For SPLOM, pan all visible axes
        Object.keys(panInitRanges).forEach(axisName => {
          const initRange = panInitRanges[axisName];
          const isX = axisName.startsWith('xaxis');

          if (isX) {
            const xScale = (initRange[1] - initRange[0]) / rect.width;
            const xOffset = dx * xScale;
            update[`${axisName}.range`] = [initRange[0] - xOffset, initRange[1] - xOffset];
          } else {
            const yScale = (initRange[1] - initRange[0]) / rect.height;
            const yOffset = -dy * yScale;
            update[`${axisName}.range`] = [initRange[0] - yOffset, initRange[1] - yOffset];
          }
        });
      } else {
        // Regular 2D plot
        if (panInitRanges.xaxis && panInitRanges.yaxis) {
          const xScale = (panInitRanges.xaxis[1] - panInitRanges.xaxis[0]) / rect.width;
          const yScale = (panInitRanges.yaxis[1] - panInitRanges.yaxis[0]) / rect.height;
          const xOffset = dx * xScale;
          const yOffset = -dy * yScale;

          update['xaxis.range'] = [panInitRanges.xaxis[0] - xOffset, panInitRanges.xaxis[1] - xOffset];
          update['yaxis.range'] = [panInitRanges.yaxis[0] - yOffset, panInitRanges.yaxis[1] - yOffset];
        }
      }

      if (Object.keys(update).length > 0) {
        Plotly.relayout(plotDiv, update);
      }
    };

    const handlePanUp = () => {
      window.removeEventListener('pointermove', handlePanMove);
      window.removeEventListener('pointerup', handlePanUp);
    };

    const handlePanDown = (pdEvt) => {
      if (pdEvt.button !== 2) return; // Right button
      pdEvt.preventDefault();

      const layout = plotDiv._fullLayout;
      if (!layout) return;

      panStartX = pdEvt.clientX;
      panStartY = pdEvt.clientY;
      panInitRanges = {};

      if (isSplom) {
        // Store all axis ranges for SPLOM
        Object.keys(layout).forEach(key => {
          if ((key.startsWith('xaxis') || key.startsWith('yaxis')) && layout[key].range) {
            panInitRanges[key] = [...layout[key].range];
          }
        });
        if (Object.keys(panInitRanges).length > 0) {
          window.addEventListener('pointermove', handlePanMove);
          window.addEventListener('pointerup', handlePanUp);
        }
      } else {
        // Regular 2D plot
        if (layout.xaxis && layout.yaxis && layout.xaxis.range && layout.yaxis.range) {
          panInitRanges.xaxis = [...layout.xaxis.range];
          panInitRanges.yaxis = [...layout.yaxis.range];
          window.addEventListener('pointermove', handlePanMove);
          window.addEventListener('pointerup', handlePanUp);
        }
      }
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
        if (interactionHandlersRef.current.contextMenu) {
          plotDiv.removeEventListener('contextmenu', interactionHandlersRef.current.contextMenu);
        }
        if (interactionHandlersRef.current.wheel) {
          plotDiv.removeEventListener('wheel', interactionHandlersRef.current.wheel);
        }
        if (interactionHandlersRef.current.scaleDown) {
          plotDiv.removeEventListener('pointerdown', interactionHandlersRef.current.scaleDown);
        }
        if (interactionHandlersRef.current.panDown) {
          plotDiv.removeEventListener('pointerdown', interactionHandlersRef.current.panDown);
        }

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

  // Button handlers
  const handleDownloadClick = () => {
    downloadPlotAsImage(plotId, {
      filename: figure.id || 'plot'
    });
  };

  const handleAutoscaleClick = () => {
    const plotDiv = plotDivRef.current;
    if (plotDiv && plotDiv._fullLayout) {
      const layout = plotDiv._fullLayout;
      const update = {};

      // Check if it's a 3D plot
      const is3D = capabilities.is3D || layout.scene;

      if (is3D) {
        // For 3D plots, reset the camera to default view
        update['scene.camera'] = {
          eye: { x: 1.25, y: 1.25, z: 1.25 },
          center: { x: 0, y: 0, z: 0 },
          up: { x: 0, y: 0, z: 1 }
        };
        // Also reset axis ranges
        update['scene.xaxis.autorange'] = true;
        update['scene.yaxis.autorange'] = true;
        update['scene.zaxis.autorange'] = true;
      } else {
        // Check if it's a SPLOM by looking for multiple axes
        const isSplom = Object.keys(layout).filter(key =>
          key.startsWith('xaxis') || key.startsWith('yaxis')
        ).length > 2;

        if (isSplom) {
          // For SPLOM, autoscale all axes
          Object.keys(layout).forEach(key => {
            if (key.startsWith('xaxis') || key.startsWith('yaxis')) {
              update[`${key}.autorange`] = true;
            }
          });
        } else {
          // Regular 2D plot
          update['xaxis.autorange'] = true;
          update['yaxis.autorange'] = true;
        }
      }

      Plotly.relayout(plotDiv, update);
    }
  };

  const handleLegendToggle = () => {
    const plotDiv = plotDivRef.current;
    if (plotDiv && plotDiv._fullLayout) {
      const currentVisibility = plotDiv._fullLayout.showlegend;
      Plotly.relayout(plotDiv, {
        showlegend: !currentVisibility
      });
    }
  };

  // Get plot capabilities
  const capabilities = figure?.metadata?.capabilities || {};
  const hasLegend = capabilities.hasLegend;
  const supportsZoomPan = capabilities.supportsZoom || capabilities.supportsPan;
  const noEditPane = capabilities.noEditPane;

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Plot buttons */}
      <div className="plot-buttons" style={{
        display: 'flex',
        gap: '4px',
        padding: '4px',
        flexShrink: 0
      }}>
        {/* Show edit button only if EditPane is available */}
        {!noEditPane && (
          <PlotButton
            onClick={onEdit}
            title="Edit plot"
            icon={EditIcon}
          />
        )}
        <PlotButton
          onClick={onViewTable}
          title="View data table"
          icon={TableIcon}
        />
        <PlotButton
          onClick={handleDownloadClick}
          title="Download as PNG"
          icon={DownloadIcon}
        />
        {/* Show autoscale button only for plots that support zoom/pan */}
        {supportsZoomPan && (
          <PlotButton
            onClick={handleAutoscaleClick}
            title="Autoscale"
            icon={AutoscaleIcon}
          />
        )}
        {/* Show legend toggle only for plots that have legend */}
        {hasLegend && (
          <PlotButton
            onClick={handleLegendToggle}
            title="Toggle legend"
            icon={LegendToggleIcon}
          />
        )}
        {/* Show expand/shrink button */}
        {isExpanded ? (
          <PlotButton
            onClick={onExpand}
            title="Shrink plot"
            icon={ShrinkIcon}
          />
        ) : (
          showExpandButton && (
            <PlotButton
              onClick={onExpand}
              title="Expand plot"
              icon={ExpandIcon}
            />
          )
        )}
      </div>

      {/* Plot div */}
      <div
        ref={plotDivRef}
        id={plotId}
        style={{
          width: '100%',
          flex: '1 1 auto',
          position: 'relative',
          minHeight: 0
        }}
      />

      {/* Figure ID label */}
      <div className="figure-id-label" style={{
        position: 'absolute',
        bottom: '4px',
        right: '4px',
        fontSize: '0.75rem',
        color: 'var(--text-color-secondary)',
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        padding: '2px 6px',
        borderRadius: '2px'
      }}>
        {figure.id}
      </div>
    </div>
  );
};

export default PlotContainer;