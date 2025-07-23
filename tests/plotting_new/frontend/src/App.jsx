import React, { useState, useEffect, useRef, useMemo } from 'react';
import Sidebar from './components/Sidebar/Sidebar.jsx';
import { ExpandIcon, EditIcon, ChatAssistantIcon, TableIcon } from './components/icons';
import axios from 'axios';
import Plotly from 'plotly.js-dist-min';
import EditPane from './components/EditPane/EditPane.jsx';
import TableView from './components/TableView/TableView.jsx';
import { attachPlotInteractions } from './utils/plotInteractions.js';


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

  useEffect(() => {
    axios.get(`${API_BASE}/config`)
        .then(res => {
        setConfig(res.data);
        setLocalFigures(res.data.figures);
      })
      .catch(err => console.error("Error fetching config:", err));
  }, []);

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

  // Show placeholder containers (identical styling) during initial load
  if (!config) {
    const placeholderFigures = Array.from({ length: 4 }).map((_, i) => ({ id: i }));

    const appTitle = "Loading…";
    const nCols = 2;
    const nRows = 2;
    const vGapPx = 20;
    const hGapPx = 20;

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
    };

    const gridStyle = {
      display: 'grid',
      gridTemplateColumns: `repeat(${nCols}, 1fr)`,
      gridTemplateRows: `repeat(${nRows}, 1fr)`,
      gap: `${vGapPx}px ${hGapPx}px`,
      height: 'calc(100vh - calc(var(--main-padding) * 2))',
    };

    const plotContainerStyle = {
      backgroundColor: 'var(--card-background-color)',
      padding: 'var(--container-padding)',
      borderRadius: 'var(--container-border-radius)',
      borderWidth: '1px',
      borderStyle: 'solid',
      borderColor: 'var(--border-color)',
      boxShadow: `4px 4px 8px var(--shadow-color)`,
      display: 'flex',
      flexDirection: 'column',
      boxSizing: 'border-box',
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
          appTitle="Loading…"
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
        
        <main style={mainStyle}>
          <div style={gridStyle}>
            {placeholderFigures.map(fig => (
              <div key={fig.id} className="plot-container" style={plotContainerStyle}>
                <div className="skeleton" style={{ flexGrow: 1, borderRadius: '4px' }} />
              </div>
            ))}
          </div>
        </main>
      </div>
    );
  }

  const appTitle = config.app_title || "Data Visualization";
  const { grid } = config;
  const figures = localFigures || config.figures;
  const nRows = grid.rows || 1;
  const nCols = grid.cols || 2;
  const vGapPx = grid.v_gap || 20;
  const hGapPx = grid.h_gap || 20;

  const appStyle = {
    display: 'flex',
    backgroundColor: 'var(--background-color)',
    color: 'var(--text-color)',
    height: '100vh',
    overflow: 'hidden',
  };


  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: `repeat(${nCols}, 1fr)`,
    gridTemplateRows: `repeat(${nRows}, 1fr)`,
    gap: `${vGapPx}px ${hGapPx}px`,
    height: 'calc(100vh - calc(var(--main-padding) * 2))', // Account for main container padding
  };

  const plotContainerStyle = {
      backgroundColor: 'var(--card-background-color)',
      padding: 'var(--container-padding)',
      borderRadius: 'var(--container-border-radius)',
      borderWidth: '1px',
      borderStyle: 'solid',
      borderColor: 'var(--border-color)',
      boxShadow: `4px 4px 8px var(--shadow-color)`,
      transition: 'background-color 0.2s ease-in-out, border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
      display: 'flex',
      flexDirection: 'column',
      boxSizing: 'border-box'
  };

  const mainStyle = {
    flex: 1,
    padding: 'var(--main-padding)',
    overflow: 'auto',
    height: '100vh',
    boxSizing: 'border-box'
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
        appTitle={appTitle}
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