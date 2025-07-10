import React, { useState, useEffect, useRef, useMemo } from 'react';
import ThemeToggle from './components/ThemeToggle.jsx';
import axios from 'axios';
import Plotly from 'plotly.js-dist-min';

const API_BASE = 'http://localhost:8000';

function App() {
  const [config, setConfig] = useState(null);
  const [theme, setTheme] = useState('light');
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  const [sidebarWidth, setSidebarWidth] = useState(220);
  const [isDragging, setIsDragging] = useState(false);
  const [activeFig, setActiveFig] = useState(null);
  const sidebarRef = useRef(null);

  // Ensure the CSS variables reflect the current theme *before* we read them
  if (typeof document !== 'undefined' && document.body.dataset.theme !== theme) {
    document.body.dataset.theme = theme;
  }

  const collapsedThreshold = 80; // px

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
        newWidth = Math.max(60, Math.min(400, newWidth));
        if (sidebarRef.current) {
          sidebarRef.current.style.width = `${newWidth}px`;
        }
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
      newWidth = Math.max(60, Math.min(400, newWidth));
      setSidebarWidth(newWidth);
      setSidebarExpanded(newWidth > collapsedThreshold);

      // Resize plots after sidebar drag ends
      if (config && config.figures) {
        // Add a small delay to allow the sidebar transition to complete
        const timer = setTimeout(() => {
          config.figures.forEach(fig => {
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

  // Removed the useEffect that updated data-theme, handled synchronously above

  useEffect(() => {
    axios.get(`${API_BASE}/config`)
        .then(res => {
        setConfig(res.data);
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
    return {
      ...figLayout,
      ...themeLayout,
      title: { ...figLayout.title, ...themeLayout.title },
      xaxis: { ...figLayout.xaxis, ...themeLayout.xaxis },
      yaxis: { ...figLayout.yaxis, ...themeLayout.yaxis },
    };
  };

  useEffect(() => {
    if (config && config.figures) {
      const colorScale = [
        getComputedStyle(document.documentElement).getPropertyValue('--color-data-1').trim(),
        getComputedStyle(document.documentElement).getPropertyValue('--color-data-2').trim(),
        getComputedStyle(document.documentElement).getPropertyValue('--color-data-3').trim(),
        getComputedStyle(document.documentElement).getPropertyValue('--color-data-4').trim(),
        getComputedStyle(document.documentElement).getPropertyValue('--color-data-5').trim(),
      ];

      config.figures.forEach(fig => {
        if (fig && fig.figure) {
          const plotId = `plot-${fig.id}`;
          const plotDiv = document.getElementById(plotId);
          if (!plotDiv) return;

          const layout = getPlotlyLayout(fig.figure, themedLayout);
          const data = fig.figure.data.map((trace, index) => ({
            ...trace,
            marker: { 
              ...trace.marker,
              color: colorScale[index % colorScale.length]
            },
            line: { 
              ...trace.line,
              color: colorScale[index % colorScale.length]
            }
          }));

          const plotConfig = {
            displaylogo: false,
            displayModeBar: false,
            responsive: true,
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
        }
      });
    }
  }, [config, themedLayout]);

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
        color: colorScale[index % colorScale.length],
      },
      line: {
        ...trace.line,
        color: colorScale[index % colorScale.length],
      },
    }));

    Plotly.newPlot(overlayDiv, data, layout, {
      displaylogo: false,
      displayModeBar: true,
      responsive: true,
    });

    return () => {
      Plotly.purge(overlayDiv);
    };
  }, [activeFig, themedLayout]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  // Removed toggle button – expansion is now drag-only

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

    const sideStyle = {
      width: `${sidebarWidth}px`,
      padding: sidebarExpanded ? 'var(--sidebar-padding)' : '10px',
      boxSizing: 'border-box',
      borderRight: `1px solid var(--border-color)`,
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--sidebar-gap)',
      transition: isDragging ? 'none' : 'width 0.1s ease-in-out',
      overflow: 'hidden',
      position: 'relative',
      backgroundColor: 'var(--sidebar-bg)'
    };

    const resizerStyle = {
      position: 'absolute',
      top: 0,
      right: 0,
      width: '8px',
      height: '100%',
      cursor: 'col-resize',
      backgroundColor: 'var(--border-color)',
      zIndex: 10,
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
      border: `1px solid var(--border-color)`,
      boxShadow: `4px 4px 8px var(--shadow-color)`,
      display: 'flex',
      flexDirection: 'column',
      boxSizing: 'border-box',
    };

    return (
      <div style={appStyle}>
        <div ref={sidebarRef} style={sideStyle}>
          {sidebarExpanded && <h2 style={{ margin: 0, padding: 0, fontSize: '1.2em' }}>{appTitle}</h2>}
          <div onMouseDown={handleMouseDown} style={resizerStyle} />
        </div>
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
  const { grid, figures } = config;
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

  const sideStyle={
    width: `${sidebarWidth}px`,
    padding: sidebarExpanded ? 'var(--sidebar-padding)' : '10px',
    boxSizing: 'border-box',
    borderRight: `1px solid var(--border-color)`,
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--sidebar-gap)',
    transition: isDragging ? 'none' : 'width 0.1s ease-in-out',
    overflow: 'hidden',
    position: 'relative'
  };
  
  const resizerStyle = {
    position: 'absolute',
    top: 0,
    right: 0,
    width: '8px',
    height: '100%',
    cursor: 'col-resize',
    backgroundColor: 'var(--border-color)',
    zIndex: 10,
  };
  
  const buttonStyle = {
    padding: 'var(--button-padding)',
    border: 'none',
    borderRadius: 'var(--button-border-radius)',
    backgroundColor: 'var(--button-bg)',
    color: 'var(--button-text)',
    cursor: 'pointer',
    transition: 'background-color 0.2s ease-in-out',
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
      border: `1px solid var(--border-color)`,
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
      <div ref={sidebarRef} style={sideStyle}>
        {sidebarExpanded ? (
          <>
            <h2 style={{ margin: 0, padding: 0, fontSize: '1.2em' }}>{appTitle}</h2>
            <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
          </>
        ) : (
          <div style={{ textAlign: 'center' }}>
            {/* Collapsed view can be simplified or customized */}
          </div>
        )}
        <div onMouseDown={handleMouseDown} style={resizerStyle} />
      </div>

      <main style={mainStyle}>
        <div style={gridStyle}>
          {figures.map(fig => (
            <div key={fig.id} className="plot-container" style={plotContainerStyle}>
              <button
                className="zoom-btn"
                onClick={() => setActiveFig(fig)}
                title="Expand plot"
              >⧉</button>
              <div id={`plot-${fig.id}`} style={{ flexGrow:1,minHeight:0 }}></div>
            </div>
          ))}
        </div>
        </main>

      {/* Overlay for enlarged plot */}
      {activeFig && (
        <div style={overlayStyle} onClick={() => setActiveFig(null)}>
          <div style={overlayInnerStyle} onClick={e => e.stopPropagation()}>
            <button style={closeBtnStyle} onClick={() => setActiveFig(null)}>×</button>
            <div id="overlay-plot" style={{ flexGrow:1, width:'100%', height:'100%' }} />
          </div>
        </div>
      )}
    </div>
  );
} 

export default App; 