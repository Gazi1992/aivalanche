import React, { useState, useEffect, useRef, useMemo } from 'react';
import Sidebar from './components/Sidebar/Sidebar.jsx';
import { ExpandIcon, EditIcon, ChatAssistantIcon, TableIcon, DownloadIcon } from './components/icons';
import PlotButton from './components/PlotButton.jsx';
import axios from 'axios';
import Plotly from 'plotly.js-dist-min';
import EditPane from './components/EditPane/EditPane.jsx';
import TableView from './components/TableView/TableView.jsx';
import { attachPlotInteractions } from './utils/plotInteractions.js';
import ColumnSelector from './components/ColumnSelector.jsx';
import { 
  createManagedFigure, 
  generateLayoutFromMetadata, 
  generateDataFromMetadata,
  updateFigureMetadata, 
  syncFigureWithDOM 
} from './utils/figureManager.js';


const API_BASE = 'http://localhost:8000';

function App() {
  const [config, setConfig] = useState(null);
  const [theme, setTheme] = useState('light');
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  const [sidebarWidth, setSidebarWidth] = useState(() => {
    const computedStyle = getComputedStyle(document.documentElement);
    return parseInt(computedStyle.getPropertyValue('--sidebar-width-expanded')) || 500;
  });
  const [isDragging, setIsDragging] = useState(false);
  const [activeFig, setActiveFig] = useState(null);
  const [sidebarHidden, setSidebarHidden] = useState(false);
  const [editingFig, setEditingFig] = useState(null);
  const [editPaneOpen, setEditPaneOpen] = useState(false);
  const [localFigures, setLocalFigures] = useState(null);
  const [tableViewFig, setTableViewFig] = useState(null);
  const [tableViewOpen, setTableViewOpen] = useState(false);
  const [isLoadingConfig, setIsLoadingConfig] = useState(false);
  const [gridColumns, setGridColumns] = useState(2); // Default to 2 columns
  const [windowHeight, setWindowHeight] = useState(window.innerHeight);

  // Ensure the CSS variables reflect the current theme *before* we read them
  if (typeof document !== 'undefined' && document.body.dataset.theme !== theme) {
    document.body.dataset.theme = theme;
  }

  const collapsedThreshold = 80; // px
  const hiddenThreshold = 30; // px - below this, sidebar is completely hidden

  // Handle sidebar drag resize
  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsDragging(true);
    const startX = e.clientX;
    const startWidth = sidebarWidth;

    let frameId = null;

    const onMouseMove = (moveEvent) => {
      if (frameId) return;
      const { clientX } = moveEvent;
      frameId = requestAnimationFrame(() => {
        const dx = clientX - startX;
        let newWidth = startWidth + dx;
        newWidth = Math.max(0, newWidth); // Allow width to go to 0 for complete hiding
        // Update width directly through state during drag
        setSidebarWidth(newWidth);
        frameId = null;
      });
    };

    const onMouseUp = (upEvent) => {
      if (frameId) cancelAnimationFrame(frameId);
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
      setIsDragging(false);

      const dx = upEvent.clientX - startX;
      let newWidth = startWidth + dx;
      newWidth = Math.max(0, newWidth); // Allow width to go to 0 for complete hiding
      
      // If dragged below hidden threshold, snap to 0 (completely hidden)
      if (newWidth < hiddenThreshold) {
        newWidth = 0;
      }
      
      setSidebarWidth(newWidth);
      setSidebarExpanded(newWidth > collapsedThreshold);
      setSidebarHidden(newWidth === 0);

      // Resize plots after sidebar drag ends
      if (config && localFigures) {
        // Add a small delay to allow the sidebar transition to complete
        const timer = setTimeout(() => {
          localFigures.forEach(fig => {
            if (fig && fig.figure) {
              const plotId = `plot-${fig.id}`;
              const graphDiv = document.getElementById(plotId);
              if (graphDiv) {
                Plotly.Plots.resize(graphDiv);
              }
            }
          });
        }, 150); // Adjusted debounce delay
  
        return () => clearTimeout(timer);
      }
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };

  // Don't load default config automatically - wait for user/LLM to create one
  // useEffect(() => {
  //   axios.get(`${API_BASE}/config`, {
  //     headers: {
  //       'Accept': 'application/json; charset=utf-8'
  //     }
  //   })
  //       .then(res => {
  //       setConfig(res.data);
  //       setLocalFigures(res.data.figures);
  //     })
  //     .catch(err => console.error("Error fetching config:", err));
  // }, []);

  const themedLayout = useMemo(() => {
    const cs = getComputedStyle(document.body);
    const paperBg = cs.getPropertyValue('--plot-paper-bg').trim();
    const plotBg = cs.getPropertyValue('--plot-bg').trim();
    const plotText = cs.getPropertyValue('--plot-text').trim();
    const gridColor = cs.getPropertyValue('--grid-color').trim();
    const legendBg = cs.getPropertyValue('--legend-bg').trim();
    const legendBorder = cs.getPropertyValue('--legend-border').trim();
    const marginLeft = parseInt(cs.getPropertyValue('--plot-margin-left').trim());
    const marginRight = parseInt(cs.getPropertyValue('--plot-margin-right').trim());
    const marginBottom = parseInt(cs.getPropertyValue('--plot-margin-bottom').trim());
    const marginTop = parseInt(cs.getPropertyValue('--plot-margin-top').trim());
    const marginPad = parseInt(cs.getPropertyValue('--plot-margin-pad').trim());
    const legendX = parseFloat(cs.getPropertyValue('--legend-x').trim());
    const legendY = parseFloat(cs.getPropertyValue('--legend-y').trim());
    const legendBorderWidth = parseInt(cs.getPropertyValue('--legend-border-width').trim());

    return {
      margin: {
        l: marginLeft, r: marginRight, b: marginBottom, t: marginTop, pad: marginPad
      },
      legend: {
        x: legendX, y: legendY, xanchor: 'left', yanchor: 'top',
        bgcolor: legendBg, bordercolor: legendBorder, borderwidth: legendBorderWidth,
        font: { color: plotText }
      },
      title: { font: { color: plotText } },
      paper_bgcolor: paperBg,
      plot_bgcolor: plotBg,
      font: { color: plotText },
      xaxis: {
        color: plotText,
        gridcolor: gridColor,
        showline: true,
        mirror: true,
        linecolor: plotText,
        linewidth: 1,
        ticks: 'outside',
        zerolinecolor: gridColor,
        zerolinewidth: 1
      },
      yaxis: {
        color: plotText,
        gridcolor: gridColor,
        showline: true,
        mirror: true,
        linecolor: plotText,
        linewidth: 1,
        ticks: 'outside',
        zerolinecolor: gridColor,
        zerolinewidth: 1
      }
    };
  }, [theme]);


  useEffect(() => {
    if (config && localFigures) {
      const colorScale = [
        getComputedStyle(document.documentElement).getPropertyValue('--color-data-1').trim(),
        getComputedStyle(document.documentElement).getPropertyValue('--color-data-2').trim(),
        getComputedStyle(document.documentElement).getPropertyValue('--color-data-3').trim(),
        getComputedStyle(document.documentElement).getPropertyValue('--color-data-4').trim(),
        getComputedStyle(document.documentElement).getPropertyValue('--color-data-5').trim(),
      ];

      localFigures.forEach(fig => {
        if (fig) {
          const plotId = `plot-${fig.id}`;
          const plotDiv = document.getElementById(plotId);
          if (!plotDiv) return;

          // Use metadata-driven layout generation
          const layout = generateLayoutFromMetadata(fig, themedLayout);
          
          // Use metadata-driven data generation
          const data = generateDataFromMetadata(fig).map((trace, index) => ({
            ...trace,
            marker: { 
              ...trace.marker,
              color: trace.marker?.color || colorScale[index % colorScale.length]
            },
            line: { 
              ...trace.line,
              color: trace.line?.color || colorScale[index % colorScale.length]
            }
          }));

          const plotConfig = {
            displaylogo: false,
            displayModeBar: false,
            responsive: true,
            scrollZoom: false, // Disable Plotly's scroll zoom - we use custom handler
            edits: {
              legendPosition: true,
              titleText: false,
              annotationText: false,
              axisTitleText: false
            }
          };

          // Use Plotly.react for efficient updates, or newPlot if the div is empty
          if (plotDiv.children.length > 0) {
            Plotly.react(plotId, data, layout, plotConfig);
          } else {
            Plotly.newPlot(plotId, data, layout, plotConfig);
          }

          // Attach unified plot interactions
          attachPlotInteractions(plotDiv);
        }
      });
      
      // Trigger resize after initial plot rendering to ensure proper height
      setTimeout(() => {
        localFigures.forEach(fig => {
          if (fig && fig.figure) {
            const plotId = `plot-${fig.id}`;
            const graphDiv = document.getElementById(plotId);
            if (graphDiv) {
              Plotly.Plots.resize(graphDiv);
            }
          }
        });
      }, 100);
    }
  }, [config, localFigures, themedLayout]);

  // === Effect to handle window resize ===
  useEffect(() => {
    const handleResize = () => {
      setWindowHeight(window.innerHeight);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // === Effect to resize plots when grid columns change ===
  useEffect(() => {
    if (localFigures && localFigures.length > 1) {
      // Add a small delay to allow grid layout to update
      const timer = setTimeout(() => {
        localFigures.forEach(fig => {
          if (fig && fig.figure) {
            const plotId = `plot-${fig.id}`;
            const graphDiv = document.getElementById(plotId);
            if (graphDiv) {
              Plotly.Plots.resize(graphDiv);
            }
          }
        });
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [gridColumns, localFigures]);

  // === Effect to render active (zoomed) figure ===
  useEffect(() => {
    if (!activeFig) return;

    const colorScale = [
      getComputedStyle(document.documentElement).getPropertyValue('--color-data-1').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--color-data-2').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--color-data-3').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--color-data-4').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--color-data-5').trim(),
    ];

    const overlayDiv = document.getElementById('overlay-plot');
    if (!overlayDiv) return;

    const layout = generateLayoutFromMetadata(activeFig, themedLayout);
    const data = generateDataFromMetadata(activeFig).map((trace, index) => ({
      ...trace,
      marker: {
        ...trace.marker,
        color: trace.marker?.color || colorScale[index % colorScale.length],
      },
      line: {
        ...trace.line,
        color: trace.line?.color || colorScale[index % colorScale.length],
      },
    }));

    Plotly.newPlot(overlayDiv, data, layout, {
      displaylogo: false,
      displayModeBar: true,
      responsive: true,
      scrollZoom: false, // Disable Plotly's scroll zoom - we use custom handler
      edits: { legendPosition: true },
    });

    // Attach unified plot interactions to overlay
    attachPlotInteractions(overlayDiv);

    return () => {
      Plotly.purge(overlayDiv);
    };
  }, [activeFig, themedLayout]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  const handleConfigUpdateFromChat = async (response) => {
    // Handle null config (e.g., from file upload without visualization request)
    if (response === null) {
      console.log('Received null response - no visualization update needed');
      return;
    }
    
    // Handle Python execution responses
    if (response && response.type === 'python_execution') {
      console.log('Received Python execution response');
      const dashboard = response.dashboard;
      
      if (dashboard && dashboard.figures) {
        try {
          setIsLoadingConfig(true);
          
          // Process figures using the new managed figure system
          const processedFigures = dashboard.figures.map(fig => {
            // Create managed figure with embedded metadata
            return createManagedFigure(fig.figure, fig.metadata);
          });
          
          // Update with the dashboard from Python execution
          const processedDashboard = { ...dashboard, figures: processedFigures };
          setConfig(processedDashboard);
          setLocalFigures(processedFigures);
          
          // Apply theme if specified
          if (dashboard.theme) {
            setTheme(dashboard.theme);
          }
          
          console.log('Python-generated dashboard loaded with', dashboard.figures?.length, 'figures');
          console.log('Execution output:', response.execution_output);
        } finally {
          setIsLoadingConfig(false);
        }
      } else {
        console.error('Python execution response missing dashboard data');
      }
      return;
    }
    
    // Handle traditional config responses (fallback)
    if (response && response.config) {
      const newConfig = response.config;
      
      // Validate the config has required structure
      if (!newConfig || typeof newConfig !== 'object') {
        console.error('Invalid config received from chat');
        return;
      }

      // Ensure config has required properties with defaults
      const validConfig = {
        ...newConfig,
        figures: newConfig.figures || [],
        grid_layout: newConfig.grid_layout || { rows: 1, cols: 1 }
      };

      try {
        setIsLoadingConfig(true);
        // Send the config to backend to build the dashboard with actual data
        const buildResponse = await axios.post(`${API_BASE}/api/build-dashboard`, validConfig);
        const dashboard = buildResponse.data;
        
        // Update with the built dashboard (includes actual plot data)
        setConfig(dashboard);
        setLocalFigures(dashboard.figures);
        
        // Apply theme if specified in config
        if (dashboard.theme) {
          setTheme(dashboard.theme);
        }
        
        console.log('Dashboard built successfully with', dashboard.figures?.length, 'figures');
      } catch (error) {
        console.error('Error building dashboard:', error);
        // Fallback to just setting the config without building
        setConfig(validConfig);
        setLocalFigures(validConfig.figures);
        
        if (validConfig.theme) {
          setTheme(validConfig.theme);
        }
      } finally {
        setIsLoadingConfig(false);
      }
    }
  };

  const restoreSidebar = () => {
    const computedStyle = getComputedStyle(document.documentElement);
    const expandedWidth = parseInt(computedStyle.getPropertyValue('--sidebar-width-expanded')) || 500;
    setSidebarWidth(expandedWidth);
    setSidebarExpanded(true);
    setSidebarHidden(false);
    
    // Resize plots after sidebar is restored
    if (config && localFigures) {
      // Add a small delay to allow the sidebar transition to complete
      const timer = setTimeout(() => {
        localFigures.forEach(fig => {
          if (fig && fig.figure) {
            const plotId = `plot-${fig.id}`;
            const graphDiv = document.getElementById(plotId);
            if (graphDiv) {
              Plotly.Plots.resize(graphDiv);
            }
          }
        });
      }, 350); // Slightly longer delay than the transition duration
      
      return () => clearTimeout(timer);
    }
  };

  const loadDemoPlots = async () => {
    try {
      setIsLoadingConfig(true);
      // Use the new Python demo endpoint instead of the old JSON config
      const response = await axios.post(`${API_BASE}/api/python/demo`, {
        session_id: "demo",
        script_name: "comprehensive_demo"
      });
      
      // Convert the execution result to dashboard format
      const result = response.data;
      if (result.success && result.plots) {
        const dashboard = {
          figures: result.plots.map(plot => {
            // Create managed figure with embedded metadata
            return createManagedFigure(plot.figure, plot.metadata);
          }),
          app_title: "Demo Visualizations",
          theme: "light"
        };
        
        setConfig(dashboard);
        setLocalFigures(dashboard.figures);
        console.log('Python demo loaded with', dashboard.figures.length, 'figures');
        console.log('Demo output:', result.output);
      } else {
        throw new Error("Demo execution failed: " + (result.error?.message || "Unknown error"));
      }
    } catch (err) {
      console.error("Error loading demo plots:", err);
    } finally {
      setIsLoadingConfig(false);
    }
  };

  const clearPlots = () => {
    setConfig(null);
    setLocalFigures(null);
  };

  // Show welcome screen when no config is loaded or loading
  if (!config || isLoadingConfig) {
    const appTitle = "Data Visualization Studio";

    const appStyle = {
      display: 'flex',
      backgroundColor: 'var(--background-color)',
      color: 'var(--text-color)',
      height: '100vh',
      overflow: 'hidden',
    };

    const mainStyle = {
      flex: 1,
      padding: 'var(--main-padding)',
      overflow: 'auto',
      height: '100vh',
      boxSizing: 'border-box',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    };

    const welcomeStyle = {
      textAlign: 'center',
      padding: '60px',
      maxWidth: '600px',
    };

    const welcomeTitleStyle = {
      fontSize: '2.5rem',
      marginBottom: '20px',
      color: 'var(--text-color)',
    };

    const welcomeSubtitleStyle = {
      fontSize: '1.2rem',
      color: 'var(--text-secondary)',
      lineHeight: '1.6',
      marginBottom: '40px',
    };

    const welcomeInstructionsStyle = {
      fontSize: '1rem',
      color: 'var(--text-secondary)',
      backgroundColor: 'var(--card-background-color)',
      padding: '20px',
      borderRadius: '8px',
      border: '1px solid var(--border-color)',
    };

    return (
      <div style={appStyle}>
        <Sidebar 
          theme={theme}
          toggleTheme={toggleTheme}
          sidebarWidth={sidebarWidth}
          sidebarExpanded={sidebarExpanded}
          sidebarHidden={sidebarHidden}
          onDragStart={handleMouseDown}
          appTitle="Data Visualization Studio"
          currentConfig={config}
          onConfigUpdate={handleConfigUpdateFromChat}
          onClearPlots={clearPlots}
          onLoadDemo={loadDemoPlots}
          isLoadingConfig={isLoadingConfig}
        />
        
        {sidebarHidden && (
          <button
            onClick={restoreSidebar}
            style={{
              position: 'fixed',
              top: '20px',
              left: '10px',
              zIndex: 1000,
              background: 'var(--primary-color)',
              color: 'white',
              border: 'none',
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              cursor: 'pointer',
              fontSize: '18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => e.target.style.transform = 'scale(1.1)'}
            onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
            title="Show sidebar"
          >
            <ChatAssistantIcon size={24} />
          </button>
        )}
        
        {isLoadingConfig && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999
          }}>
            <div style={{
              backgroundColor: 'var(--card-background-color)',
              padding: '30px',
              borderRadius: '12px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '20px',
              boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
            }}>
              <div className="loading-spinner" style={{
                width: '50px',
                height: '50px',
                border: '4px solid var(--border-color)',
                borderTop: '4px solid var(--primary-color)',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}></div>
              <div style={{
                fontSize: '1.1rem',
                color: 'var(--text-color)',
                fontWeight: '500'
              }}>
                Loading visualization...
              </div>
            </div>
          </div>
        )}
        
        <main style={mainStyle}>
          <div style={welcomeStyle}>
            <h1 style={welcomeTitleStyle}>📊 Welcome to Data Visualization Studio</h1>
            <p style={welcomeSubtitleStyle}>
              Start by uploading your data and chatting with the AI assistant to create stunning visualizations.
            </p>
            <div style={welcomeInstructionsStyle}>
              <p style={{marginBottom: '10px'}}>
                <strong>Getting Started:</strong>
              </p>
              <ol style={{textAlign: 'left', margin: '0', paddingLeft: '20px'}}>
                <li>Upload a data file using the 📎 button in the chat</li>
                <li>Ask the AI to create visualizations</li>
                <li>Customize and refine your plots interactively</li>
              </ol>
            </div>
            <div style={{marginTop: '30px'}}>
              <button
                onClick={loadDemoPlots}
                style={{
                  padding: '12px 24px',
                  fontSize: '1rem',
                  backgroundColor: 'var(--primary-color)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                }}
              >
                📊 Show Demo Plots
              </button>
              <p style={{marginTop: '10px', fontSize: '0.9rem', color: 'var(--text-secondary)'}}>
                or explore sample visualizations with demo data
              </p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const figures = localFigures || config.figures;
  // Calculate grid dimensions based on number of figures and selected columns
  const figureCount = figures ? figures.length : 0;
  // For single plot, always use 1 column to take full width
  const nCols = figureCount === 1 ? 1 : Math.min(gridColumns, figureCount);
  const nRows = Math.ceil(figureCount / nCols) || 1;
  
  // Get grid spacing from CSS variables
  const vGapPx = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--grid-vertical-spacing').trim()) || 20;
  const hGapPx = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--grid-horizontal-spacing').trim()) || 20;

  const appStyle = {
    display: 'flex',
    backgroundColor: 'var(--background-color)',
    color: 'var(--text-color)',
    height: '100vh',
    overflow: 'hidden',
  };


  // Calculate min height to fit 2 rows in viewport
  // The grid container takes full height minus the column selector (if shown)
  // Column selector total height = content (approx 36px) + bottom margin (15px) = 51px
  const columnSelectorTotalHeight = figureCount > 1 ? 51 : 0; // Only account for selector if shown
  const gridContainerTopPadding = figureCount === 1 ? 20 : 0; // Top padding for single plot
  const gridContainerBottomPadding = 20; // Bottom padding we added
  const gridOwnPaddingBottom = 10; // Grid's paddingBottom
  
  // Available height for the actual grid content
  const availableHeight = windowHeight - columnSelectorTotalHeight - gridContainerTopPadding - gridContainerBottomPadding - gridOwnPaddingBottom;
  
  // Height for each plot when we want exactly 2 rows
  const minPlotHeight = Math.max(300, Math.floor((availableHeight - vGapPx) / 2));

  // Calculate grid row height based on number of rows
  const gridRowHeight = nRows === 1 
    ? '100%' // Single row takes full height
    : nRows === 2
    ? `calc((100% - ${vGapPx}px) / 2)` // For 2 rows, split available height
    : `${minPlotHeight}px`; // For more rows, use fixed height
    
  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: `repeat(${nCols}, 1fr)`,
    gridAutoRows: nRows <= 2 ? gridRowHeight : `minmax(${minPlotHeight}px, 1fr)`,
    gap: `${vGapPx}px ${hGapPx}px`,
    width: '100%',
    maxWidth: '100%',
    height: nRows <= 2 ? '100%' : 'auto', // Fill container height for 1-2 rows
    overflow: 'visible', // Allow shadows to be visible
    paddingBottom: '10px' // Small padding for bottom shadows
  };

  const plotContainerStyle = {
      backgroundColor: 'var(--card-background-color)',
      padding: 'var(--container-padding)',
      borderRadius: 'var(--container-border-radius)',
      borderWidth: '1px',
      borderStyle: 'solid',
      borderColor: 'var(--border-color)',
      boxShadow: `0 2px 8px rgba(0, 0, 0, 0.1)`, // More subtle shadow
      transition: 'background-color 0.2s ease-in-out, border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
      display: 'flex',
      flexDirection: 'column',
      boxSizing: 'border-box'
  };

  const mainStyle = {
    flex: 1,
    padding: 0, // Remove padding from main
    overflow: 'hidden', // Main container doesn't scroll
    height: '100vh',
    boxSizing: 'border-box',
    display: 'flex',
    flexDirection: 'column'
  };

  // Styles for overlay zoom view
  const overlayStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100vw',
    height: '100vh',
    backgroundColor: 'rgba(0,0,0,0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  };

  const overlayInnerStyle = {
    backgroundColor: 'var(--card-background-color)',
    padding: '10px',
    borderRadius: 'var(--container-border-radius)',
    width: '90vw',
    height: '90vh',
    boxSizing: 'border-box',
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
  };

  const closeBtnStyle = {
    alignSelf: 'flex-end',
    background: 'none',
    border: 'none',
    color: 'var(--text-color)',
    fontSize: '1.5rem',
    cursor: 'pointer',
  };

  return (
    <div style={appStyle}>
      <Sidebar 
        theme={theme}
        toggleTheme={toggleTheme}
        sidebarWidth={sidebarWidth}
        sidebarExpanded={sidebarExpanded}
        sidebarHidden={sidebarHidden}
        onDragStart={handleMouseDown}
        appTitle="Data Visualization Studio"
        currentConfig={config}
        onConfigUpdate={handleConfigUpdateFromChat}
        onClearPlots={clearPlots}
        onLoadDemo={loadDemoPlots}
        isLoadingConfig={isLoadingConfig}
      />

      {sidebarHidden && (
        <button
          onClick={restoreSidebar}
          style={{
            position: 'fixed',
            top: '20px',
            left: '10px',
            zIndex: 1000,
            background: 'var(--primary-color)',
            color: 'white',
            border: 'none',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            cursor: 'pointer',
            fontSize: '18px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => e.target.style.transform = 'scale(1.1)'}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
          title="Show sidebar"
        >
          <ChatAssistantIcon size={30} />
        </button>
      )}

      <main style={mainStyle}>
        <ColumnSelector 
          columns={gridColumns}
          onColumnChange={setGridColumns}
          figureCount={figureCount}
        />
        <div className="grid-container" style={{ 
          flex: 1, 
          overflowY: nRows > 2 ? 'auto' : 'hidden', // Only scroll if more than 2 rows
          overflowX: 'hidden',
          padding: figureCount === 1 ? '20px' : '0 20px 20px 20px', // Add top padding for single plot
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={gridStyle}>
          {figures.map(fig => {
            // Create dynamic container style with figure background and border from metadata
            const figureContainerStyle = {
              ...plotContainerStyle,
              // Apply figure background from metadata
              backgroundColor: fig.metadata?.appearance?.background?.figure?.color || 'transparent',
              // Apply figure border from metadata
              borderColor: fig.metadata?.appearance?.background?.figure?.borderColor || 'transparent',
              borderWidth: (fig.metadata?.appearance?.background?.figure?.borderColor && 
                           fig.metadata?.appearance?.background?.figure?.borderColor !== 'transparent' &&
                           fig.metadata?.appearance?.background?.figure?.borderColor !== 'rgba(0,0,0,0)') ? '1px' : '0',
              borderStyle: 'solid'
            };
            
            return (
            <div key={fig.id} className="plot-container" style={figureContainerStyle}>
              <div className="plot-buttons">
                <PlotButton
                  onClick={() => {
                    // Sync figure with current DOM state (captures zoom/pan)
                    const syncedFigure = syncFigureWithDOM(fig, `plot-${fig.id}`);
                    setEditingFig(syncedFigure);
                    setEditPaneOpen(true);
                  }}
                  title="Edit plot"
                  icon={EditIcon}
                />
                <PlotButton
                  onClick={() => {
                    setTableViewFig(fig);
                    setTableViewOpen(true);
                  }}
                  title="View data"
                  icon={TableIcon}
                />
                {figures.length > 1 && (
                  <PlotButton
                    onClick={() => setActiveFig(fig)}
                    title="Expand plot"
                    icon={ExpandIcon}
                  />
                )}
                <PlotButton
                  onClick={() => {
                    const plotId = `plot-${fig.id}`;
                    Plotly.downloadImage(plotId, {
                      format: 'png',
                      width: 1200,
                      height: 800,
                      filename: fig.id || 'plot'
                    });
                  }}
                  title="Download as PNG"
                  icon={DownloadIcon}
                />
              </div>
              <div id={`plot-${fig.id}`} style={{ flex: '1 1 auto', minHeight: 0, width: '100%' }}></div>
              <div className="figure-id-label">{fig.id}</div>
            </div>
            );
          })}
          </div>
        </div>
      </main>

      {/* Edit Pane */}
      <EditPane
        isOpen={editPaneOpen}
        onClose={() => {
          setEditPaneOpen(false);
          setEditingFig(null);
        }}
        figure={editingFig}
        onUpdate={(updatedFigure) => {
          const updatedFigures = localFigures.map(f => 
            f.id === editingFig.id ? updatedFigure : f
          );
          setLocalFigures(updatedFigures);
        }}
      />

      {/* Table View */}
      <TableView
        figure={tableViewFig}
        isOpen={tableViewOpen}
        onClose={() => {
          setTableViewOpen(false);
          setTableViewFig(null);
        }}
      />

      {/* Overlay for enlarged plot */}
      {activeFig && (
        <div style={overlayStyle} onClick={() => setActiveFig(null)}>
          <div style={overlayInnerStyle} onClick={e => e.stopPropagation()}>
            <button style={closeBtnStyle} onClick={() => setActiveFig(null)}>×</button>
            <div id="overlay-plot" style={{ flexGrow:1, width:'100%', height:'100%' }} />
            <div className="figure-id-label" style={{ opacity: 0.4 }}>
              {activeFig.id}
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 

export default App; 