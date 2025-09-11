import React, { useState, useEffect, useRef, useMemo } from 'react';
import Sidebar from './components/Sidebar/Sidebar.jsx';
import { ExpandIcon, EditIcon, ChatAssistantIcon, TableIcon } from './components/icons';
import axios from 'axios';
import Plotly from 'plotly.js-dist-min';
import EditPane from './components/EditPane/EditPane.jsx';
import TableView from './components/TableView/TableView.jsx';
import { attachPlotInteractions } from './utils/plotInteractions.js';
import ColumnSelector from './components/ColumnSelector.jsx';


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

  const getPlotlyLayout = (figData, themeLayout) => {
    const figLayout = figData.layout || {};
    
    // Check if this is a parallel coordinates plot
    const isParallelCoords = figData.data && figData.data.some(trace => trace.type === 'parcoords');
    
    // Create a new layout object, starting with the theme settings,
    // then overriding with figure-specific settings (figure takes precedence).
    const newLayout = { ...themeLayout, ...figLayout };

    // For parallel coordinates plots, preserve custom margins if they exist
    if (isParallelCoords && figLayout.margin) {
      newLayout.margin = { ...themeLayout.margin, ...figLayout.margin };
    }

    // The previous spread only handles top-level keys. We need to dive into
    // all axis objects and apply the theme to them, which is crucial for
    // matrix plots with many axes (xaxis, xaxis2, yaxis, yaxis2, etc.).
    for (const key in figLayout) {
        if (key.startsWith('xaxis')) {
            // Merge theme axis settings with the specific axis settings from the figure.
            // The figure's settings take precedence.
            newLayout[key] = { ...themeLayout.xaxis, ...figLayout[key] };
        }
        if (key.startsWith('yaxis')) {
            newLayout[key] = { ...themeLayout.yaxis, ...figLayout[key] };
        }
    }

    // Ensure the title is also properly merged.
    newLayout.title = { ...themeLayout.title, ...figLayout.title };
    
    // Ensure legend settings are properly merged (figure settings take precedence)
    if (figLayout.legend) {
      newLayout.legend = { ...themeLayout.legend, ...figLayout.legend };
    }

    // Ensure background colors from figure take precedence
    // Note: paper_bgcolor is handled by EditPane setting both paper_bgcolor and figureBackgroundColor
    if (figLayout.paper_bgcolor !== undefined) {
      newLayout.paper_bgcolor = figLayout.paper_bgcolor;
    }
    if (figLayout.plot_bgcolor !== undefined) {
      newLayout.plot_bgcolor = figLayout.plot_bgcolor;
    }

    return newLayout;
  };

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
        if (fig && fig.figure) {
          const plotId = `plot-${fig.id}`;
          const plotDiv = document.getElementById(plotId);
          if (!plotDiv) return;

          const layout = getPlotlyLayout(fig.figure, themedLayout);
          const data = fig.figure.data.map((trace, index) => ({
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

    const layout = getPlotlyLayout(activeFig.figure, themedLayout);
    const data = activeFig.figure.data.map((trace, index) => ({
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

  const handleConfigUpdateFromChat = async (newConfig) => {
    // Handle null config (e.g., from file upload without visualization request)
    if (newConfig === null) {
      console.log('Received null config - no visualization update needed');
      return;
    }
    
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
      const response = await axios.post(`${API_BASE}/api/build-dashboard`, validConfig);
      const dashboard = response.data;
      
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
      const response = await axios.get(`${API_BASE}/dashboard/default_config.json`, {
        headers: {
          'Accept': 'application/json; charset=utf-8'
        }
      });
      setConfig(response.data);
      setLocalFigures(response.data.figures);
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
  const nCols = Math.min(gridColumns, figureCount); // Don't use more columns than figures
  const nRows = Math.ceil(figureCount / nCols) || 1;
  const vGapPx = 20; // Use default spacing
  const hGapPx = 20; // Use default spacing

  const appStyle = {
    display: 'flex',
    backgroundColor: 'var(--background-color)',
    color: 'var(--text-color)',
    height: '100vh',
    overflow: 'hidden',
  };


  // Calculate min height to fit 2 rows in viewport
  // The grid container takes full height minus the column selector
  // Column selector total height = content (approx 36px) + bottom margin (15px) = 51px
  const columnSelectorTotalHeight = 51;
  const gridContainerBottomPadding = 20; // Bottom padding we added
  const gridOwnPaddingBottom = 10; // Grid's paddingBottom
  
  // Available height for the actual grid content
  const availableHeight = windowHeight - columnSelectorTotalHeight - gridContainerBottomPadding - gridOwnPaddingBottom;
  
  // Height for each plot when we want exactly 2 rows
  const minPlotHeight = Math.max(300, Math.floor((availableHeight - vGapPx) / 2));

  // For exactly 2 rows, use calc to fill available space
  const gridRowHeight = nRows <= 2 
    ? `calc((100% - ${vGapPx}px) / 2)` // For 2 or fewer rows, split available height
    : `${minPlotHeight}px`; // For more rows, use fixed height
    
  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: `repeat(${nCols}, 1fr)`,
    gridAutoRows: nRows <= 2 ? gridRowHeight : `minmax(${minPlotHeight}px, 1fr)`,
    gap: `${vGapPx}px ${hGapPx}px`,
    width: '100%',
    maxWidth: '100%',
    height: nRows <= 2 ? '100%' : 'auto', // Fill container height for 2 rows
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
          padding: '0 20px 20px 20px', // Add padding on sides and bottom
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={gridStyle}>
          {figures.map(fig => {
            // Create dynamic container style with figure background and border
            const figureContainerStyle = {
              ...plotContainerStyle,
              ...(fig.figure?.layout?.figureBackgroundColor && { 
                backgroundColor: fig.figure.layout.figureBackgroundColor 
              }),
              ...(fig.figure?.layout?.figureBorderColor && { 
                borderColor: fig.figure.layout.figureBorderColor 
              }),
            };
            
            return (
            <div key={fig.id} className="plot-container" style={figureContainerStyle}>
              <div className="plot-buttons">
                <button className="edit-btn" onClick={() => {
                  setEditingFig(fig);
                  setEditPaneOpen(true);
                }} title="Edit plot">
                  <EditIcon size={16} />
                </button>
                <button className="table-btn" onClick={() => {
                  setTableViewFig(fig);
                  setTableViewOpen(true);
                }} title="View data">
                  <TableIcon size={16} />
                </button>
                {figures.length > 1 && (
                <button className="zoom-btn" onClick={() => setActiveFig(fig)} title="Expand plot">
                  <ExpandIcon size={16} />
                </button>
                )}
              </div>
              <div id={`plot-${fig.id}`} style={{ flexGrow:1,minHeight:0 }}></div>
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
        plotData={editingFig?.figure}
        metadata={editingFig?.metadata}
        onUpdate={(updatedFigure) => {
          const updatedFigures = localFigures.map(f => 
            f.id === editingFig.id ? { ...f, figure: updatedFigure } : f
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