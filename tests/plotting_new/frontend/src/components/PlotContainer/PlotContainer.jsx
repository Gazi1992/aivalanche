import React, { useEffect, useRef, useCallback, useState } from 'react';
import Plotly from 'plotly.js-dist-min';
import PlotButton from '../PlotButton';
import { EditIcon, TableIcon, ExpandIcon, ShrinkIcon, DownloadIcon, AutoscaleIcon, LegendToggleIcon, PlayIcon, PauseIcon, GifIcon, SliderIcon } from '../icons';
import { generateLayoutFromMetadata, generateDataFromMetadata } from '../../utils/figureManager';
import { downloadPlotAsImage } from '../../utils/plotUtils';
import { exportStaticFramesAsGIF, downloadGIF } from '../../utils/gifExport';
import './PlotContainer.css';

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
  const [isAnimationPlaying, setIsAnimationPlaying] = useState(false);
  const isAnimationPlayingRef = useRef(false);
  const [showSlider, setShowSlider] = useState(false);

  // Check if this is an animation (either has frames or marked as animation in metadata)
  const isAnimation = (figure?.frames && figure.frames.length > 0) || figure?.metadata?.isAnimation;

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

  // Animation control functions
  const handlePlayAnimation = useCallback(() => {
    if (!plotDivRef.current || !isAnimation) return;

    console.log('Starting animation playback');
    setIsAnimationPlaying(true);
    isAnimationPlayingRef.current = true;

    // Function to continuously loop the animation
    const startContinuousAnimation = () => {
      if (!plotDivRef.current || !isAnimationPlayingRef.current) {
        console.log('Animation stopped or div not available');
        return;
      }

      // Get all frame names or indices
      const frameNames = figure.frames.map((frame, i) => {
        if (typeof frame === 'object' && frame.name) {
          return frame.name;
        }
        return i;
      });

      console.log('Animating frames:', frameNames);
      Plotly.animate(plotDivRef.current, frameNames, {
        frame: {
          duration: 100,
          redraw: true
        },
        transition: {
          duration: 0
        },
        fromcurrent: false, // Start from beginning of sequence
        mode: 'immediate',
        direction: 'forward'
      }).then(() => {
        // When animation completes, restart if still playing
        console.log('Animation cycle complete, playing:', isAnimationPlayingRef.current);
        if (isAnimationPlayingRef.current && plotDivRef.current) {
          console.log('Restarting animation loop');
          startContinuousAnimation();
        }
      }).catch(error => {
        console.error('Animation error:', error);
        setIsAnimationPlaying(false);
        isAnimationPlayingRef.current = false;
      });
    };

    startContinuousAnimation();
  }, [isAnimation, figure.frames]);

  const handlePauseAnimation = useCallback(() => {
    if (!plotDivRef.current || !isAnimation) return;

    console.log('Pausing animation');
    setIsAnimationPlaying(false);
    isAnimationPlayingRef.current = false;

    // Pause by calling animate with null frames and 0 duration
    Plotly.animate(plotDivRef.current, [null], {
      frame: {
        duration: 0,
        redraw: false
      },
      mode: 'immediate'
    });
  }, [isAnimation]);

  // Initialize plot
  const initializePlot = useCallback(() => {
    if (!plotDivRef.current) return;

    const data = getIsolatedData();
    let layout = getIsolatedLayout();

    // Handle animation controls if this is an animation
    if (figure.frames && figure.frames.length > 0) {
      console.log(`Plot ${plotId}: Has ${figure.frames.length} frames`);
      console.log(`Plot ${plotId}: Slider visible: ${showSlider}`);

      // Always remove updatemenus (play/pause buttons)
      layout = {
        ...layout,
        updatemenus: undefined  // Remove play/pause buttons
      };

      // Add or remove slider based on state
      if (showSlider) {
        // Create slider configuration
        layout.sliders = [{
          steps: figure.frames.map((frame, i) => ({
            args: [[frame.name || i], {
              frame: { duration: 100, redraw: true },
              mode: 'immediate'
            }],
            label: frame.name || `${i}`,
            method: 'animate'
          })),
          active: 0,
          y: -0.15,
          len: 0.9,
          x: 0.05,
          xanchor: 'left',
          pad: { t: 50, b: 10 }
        }];
      } else {
        layout.sliders = undefined;
      }
    }

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
        // Special handling for SPLOM to ensure axis labels are visible
        if (data && data[0] && data[0].type === 'splom') {
          const plotDiv = plotDivRef.current;
          const dimensions = data[0].dimensions || [];
          const showupperhalf = data[0].showupperhalf !== false; // Default is true

          // For SPLOM, ensure grid is visible on all subplots
          // and axis labels are properly displayed
          const fullLayout = plotDiv._fullLayout;
          const updateObj = {};

          // Find all x and y axes
          const xAxes = [];
          const yAxes = [];
          Object.keys(fullLayout).forEach(key => {
            if (key.match(/^xaxis\d*$/)) {
              xAxes.push(key);
            } else if (key.match(/^yaxis\d*$/)) {
              yAxes.push(key);
            }
          });

          // Get text styles and border color from metadata
          const axisLabelStyles = figure.metadata?.appearance?.text?.axisLabel || {};
          const axisTickStyles = figure.metadata?.appearance?.text?.axisTick || {};
          const borderColor = figure.metadata?.appearance?.background?.plot?.borderColor || 'rgba(128, 128, 128, 0.3)';

          // For SPLOM, determine which axes are on the bottom row and left column
          const numDimensions = dimensions.length;

          // Enable grid for all axes and ensure consistent styling from metadata
          [...xAxes, ...yAxes].forEach(axisKey => {
            updateObj[`${axisKey}.showgrid`] = true;
            updateObj[`${axisKey}.gridcolor`] = 'rgba(128, 128, 128, 0.2)';

            // Add plot box (axis lines) for each subplot using metadata border color
            updateObj[`${axisKey}.showline`] = true;
            updateObj[`${axisKey}.linecolor`] = borderColor;
            updateObj[`${axisKey}.linewidth`] = 1;
            updateObj[`${axisKey}.mirror`] = true;  // Show lines on all four sides but NO ticks on mirror
            updateObj[`${axisKey}.zeroline`] = false;  // Hide zero lines

            // Determine if this axis should show ticks
            // For SPLOM lower triangle:
            // - Bottom row x-axes: xaxis, xaxis2, xaxis3, xaxis4 (first n-1 for n dimensions)
            // - Left column y-axes: specific pattern based on triangular structure
            let showTicks = false;

            if (axisKey.startsWith('xaxis')) {
              // Extract axis number (empty string for 'xaxis' means 1)
              const axisNum = axisKey === 'xaxis' ? 1 : parseInt(axisKey.replace('xaxis', ''));
              // For lower triangle: show ticks on bottom row
              // Bottom row x-axes are the first (numDimensions-1) axes
              showTicks = axisNum < numDimensions;
            } else if (axisKey.startsWith('yaxis')) {
              // Extract axis number
              const axisNum = axisKey === 'yaxis' ? 1 : parseInt(axisKey.replace('yaxis', ''));

              // For SPLOM lower triangle, just show ticks for ALL y-axes
              // Let Plotly handle which ones are actually on the left
              // This is simpler and should work
              showTicks = true;
            }

            if (showTicks) {
              updateObj[`${axisKey}.ticks`] = 'outside';
              updateObj[`${axisKey}.showticklabels`] = true;
            } else {
              updateObj[`${axisKey}.ticks`] = '';
              updateObj[`${axisKey}.showticklabels`] = false;
            }

            // Apply consistent font styles from metadata to all axes
            // Axis label font
            updateObj[`${axisKey}.title.font.size`] = axisLabelStyles.fontSize || 14;
            updateObj[`${axisKey}.title.font.color`] = axisLabelStyles.color || '#444444';
            if (axisLabelStyles.bold !== undefined) {
              updateObj[`${axisKey}.title.font.weight`] = axisLabelStyles.bold ? 'bold' : 'normal';
            }
            if (axisLabelStyles.italic !== undefined) {
              updateObj[`${axisKey}.title.font.style`] = axisLabelStyles.italic ? 'italic' : 'normal';
            }

            // Axis tick font
            updateObj[`${axisKey}.tickfont.size`] = axisTickStyles.fontSize || 11;
            updateObj[`${axisKey}.tickfont.color`] = axisTickStyles.color || '#444444';
          });

          // For lower triangle SPLOM, ensure the bottom-left subplot has its x-axis label
          // The first x-axis often corresponds to the bottom-left plot
          if (!showupperhalf && xAxes.length > 0 && dimensions.length > 0) {
            // The bottom-left plot typically uses xaxis (not xaxis2, etc)
            updateObj['xaxis.title.text'] = dimensions[0].label;
            updateObj['xaxis.title.standoff'] = 15;
          }

          // Add spacing between subplots
          const spacing = 0.02; // 2% spacing between subplots
          xAxes.forEach(xKey => {
            const currentDomain = fullLayout[xKey]?.domain;
            if (currentDomain) {
              updateObj[`${xKey}.domain`] = [
                currentDomain[0] + spacing/2,
                currentDomain[1] - spacing/2
              ];
            }
          });

          yAxes.forEach(yKey => {
            const currentDomain = fullLayout[yKey]?.domain;
            if (currentDomain) {
              updateObj[`${yKey}.domain`] = [
                currentDomain[0] + spacing/2,
                currentDomain[1] - spacing/2
              ];
            }
          });

          // Apply the updates if any
          if (Object.keys(updateObj).length > 0) {
            Plotly.relayout(plotDiv, updateObj).catch(err => {
              console.log('SPLOM update failed:', err);
            });
          }
        }

        // If the figure has frames (animation), add them
        if (figure.frames && figure.frames.length > 0) {
          console.log(`Plot ${plotId}: Adding ${figure.frames.length} animation frames`);
          // Deep clone frames to ensure isolation
          const isolatedFrames = JSON.parse(JSON.stringify(figure.frames));

          return Plotly.addFrames(plotDivRef.current, isolatedFrames).then(() => {
            const plotDiv = plotDivRef.current;
            // Set up animation event listeners for looping
            plotDiv.on('plotly_animationinterrupted', () => {
              setIsAnimationPlaying(false);
            });

            plotDiv.on('plotly_animated', () => {
              // Animation completed - loop if still playing
              if (isAnimationPlaying) {
                setTimeout(() => {
                  handlePlayAnimation();
                }, 100);
              }
            });
          });
        }
      })
      .then(() => {
        plotInstanceRef.current = plotDivRef.current;
        attachIsolatedInteractions();
      })
      .catch(error => {
        console.error(`Error creating plot ${plotId}:`, error);
      });
  }, [plotId, getIsolatedData, getIsolatedLayout, figure, isAnimationPlaying, handlePlayAnimation, showSlider]);

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
      downEvt.preventDefault(); // Always prevent Plotly's default middle-click behavior

      // Get the CURRENT layout, not the captured one
      const currentLayout = plotDiv._fullLayout;
      if (!currentLayout) return;

      const rect = plotDiv.getBoundingClientRect();
      scaleStartX = downEvt.clientX;
      scaleStartY = downEvt.clientY;
      scaleStartRelX = (downEvt.clientX - rect.left) / rect.width;
      scaleStartRelY = 1 - (downEvt.clientY - rect.top) / rect.height;
      scaleInitRanges = {};

      let hasMoved = false;
      const moveThreshold = 3; // pixels

      if (isSplom) {
        // Store all axis ranges for SPLOM
        Object.keys(currentLayout).forEach(key => {
          if ((key.startsWith('xaxis') || key.startsWith('yaxis')) && currentLayout[key].range) {
            scaleInitRanges[key] = [...currentLayout[key].range];
          }
        });
      } else {
        // Regular plot - use current ranges
        if (currentLayout.xaxis && currentLayout.yaxis && currentLayout.xaxis.range && currentLayout.yaxis.range) {
          scaleInitRanges.xaxis = [...currentLayout.xaxis.range];
          scaleInitRanges.yaxis = [...currentLayout.yaxis.range];
        }
      }

      // Modified move handler that tracks movement
      const handleScaleMoveTracked = (moveEvt) => {
        if ((moveEvt.buttons & 4) === 0) return; // Check for middle button

        const dx = moveEvt.clientX - scaleStartX;
        const dy = moveEvt.clientY - scaleStartY;

        // Check if moved beyond threshold
        if (Math.abs(dx) > moveThreshold || Math.abs(dy) > moveThreshold) {
          hasMoved = true;
          handleScaleMove(moveEvt);
        }
      };

      // Modified up handler that resets axes if no movement
      const handleScaleUpTracked = () => {
        window.removeEventListener('pointermove', handleScaleMoveTracked);
        window.removeEventListener('pointerup', handleScaleUpTracked);

        // If user didn't move, reset axes (our own implementation)
        if (!hasMoved) {
          const update = {};

          // Get current layout for proper reset
          const resetLayout = plotDiv._fullLayout;

          if (isSplom) {
            // Reset all axes for SPLOM
            Object.keys(resetLayout).forEach(key => {
              if (key.startsWith('xaxis') || key.startsWith('yaxis')) {
                update[`${key}.autorange`] = true;
              }
            });
          } else {
            // Reset axes for regular plot
            update['xaxis.autorange'] = true;
            update['yaxis.autorange'] = true;
          }

          if (Object.keys(update).length > 0) {
            Plotly.relayout(plotDiv, update);
          }
        }
      };

      if (Object.keys(scaleInitRanges).length > 0) {
        window.addEventListener('pointermove', handleScaleMoveTracked);
        window.addEventListener('pointerup', handleScaleUpTracked);
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

  // Re-render plot when slider visibility changes
  useEffect(() => {
    if (isAnimation && plotDivRef.current) {
      initializePlot();
    }
  }, [showSlider]);

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

  const handleSliderToggle = () => {
    setShowSlider(prev => !prev);
  };

  const handleGifExport = async () => {
    if (!plotDivRef.current || !isAnimation) return;

    // Show loading state (could add a loading indicator)
    console.log('Starting GIF export...');

    try {
      const blob = await exportStaticFramesAsGIF(plotDivRef.current, figure, {
        width: 640,
        height: 480,
        fps: 10,
        quality: 10,
        onProgress: (progress) => {
          console.log(`GIF export progress: ${(progress * 100).toFixed(0)}%`);
        }
      });

      // Download the GIF
      downloadGIF(blob, `${figure.id || 'animation'}.gif`);
      console.log('GIF export complete!');
    } catch (error) {
      console.error('Failed to export GIF:', error);
      alert('Failed to export animation as GIF. Please try again.');
    }
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
        {/* Animation controls first if this is an animation */}
        {isAnimation && (
          <>
            <PlotButton
              onClick={isAnimationPlaying ? handlePauseAnimation : handlePlayAnimation}
              title={isAnimationPlaying ? "Pause animation" : "Play animation"}
              icon={isAnimationPlaying ? PauseIcon : PlayIcon}
            />
            <PlotButton
              onClick={handleGifExport}
              title="Export as GIF"
              icon={GifIcon}
            />
            <PlotButton
              onClick={handleSliderToggle}
              title={showSlider ? "Hide slider" : "Show slider"}
              icon={SliderIcon}
              style={showSlider ? { backgroundColor: 'var(--primary-color)', color: 'white' } : {}}
            />
            <div className="plot-button-separator" style={{
              width: '1px',
              height: '20px',
              backgroundColor: 'var(--border-color)',
              margin: '0 4px',
              alignSelf: 'center'
            }} />
          </>
        )}
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