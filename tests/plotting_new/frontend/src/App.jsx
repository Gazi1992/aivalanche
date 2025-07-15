import React, { useState, useEffect, useRef, useMemo } from 'react';
import ThemeToggle from './components/ThemeToggle.jsx';
import ChatInterface from './components/ChatInterface.jsx';
import Logo from './components/Logo.jsx';
import axios from 'axios';
import Plotly from 'plotly.js-dist-min';
import ExpandIcon from './components/ExpandIcon.jsx';

// Set global config for smoother wheel zoom
Plotly.setPlotConfig({
  scrollZoom: {
    debounce: 40,   // 40 ms between redraws  (try 30–50)
    speed: 0.5      // zoom delta per wheel-tick (0.5 is Plotly’s default)
  }
});

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
  const sidebarRef = useRef(null);

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
      newWidth = Math.max(0, newWidth); // Allow width to go to 0 for complete hiding
      
      // If dragged below hidden threshold, snap to 0 (completely hidden)
      if (newWidth < hiddenThreshold) {
        newWidth = 0;
      }
      
      setSidebarWidth(newWidth);
      setSidebarExpanded(newWidth > collapsedThreshold);
      setSidebarHidden(newWidth === 0);

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
    
    // Check if this is a parallel coordinates plot
    const isParallelCoords = figData.data && figData.data.some(trace => trace.type === 'parcoords');
    
    // Create a new layout object, starting with the figure-specific layout,
    // then overriding it with general theme settings.
    const newLayout = { ...figLayout, ...themeLayout };

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

    return newLayout;
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
            scrollZoom: true, // Enable mouse wheel zoom
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

          // Attach custom right-click drag scaling
          if (!plotDiv.__scaleHandlerAttached) {
            plotDiv.__scaleHandlerAttached = true;
            plotDiv.addEventListener('contextmenu', e => e.preventDefault()); // disable context menu

            let startX = 0, startY = 0;
            let initXRange = null, initYRange = null;
            let activeXAxis = 'xaxis';  // will be resolved per-pointerdown
            let activeYAxis = 'yaxis';
            let rect = null;
            const onPointerMove = (moveEvt) => {
              if (moveEvt.buttons !== 2) return; // ensure right button still pressed
              const dx = moveEvt.clientX - startX;
              const dy = moveEvt.clientY - startY;
              const sensitivity = 0.2; // lower value = higher sensitivity
              const factorX = 1 - dx / (rect.width * sensitivity);  // horizontal scale
              const factorY = 1 + dy / (rect.height * sensitivity); // vertical scale (drag down -> zoom in)

              // Clamp factors to reasonable range to avoid inversion/overflow
              const clamp = (val, min, max) => Math.max(min, Math.min(max, val));
              const fx = clamp(factorX, 0.1, 10);
              const fy = clamp(factorY, 0.1, 10);

              if (initXRange && initYRange) {
                const xCenter = (initXRange[0] + initXRange[1]) / 2;
                const xHalf = (initXRange[1] - initXRange[0]) / 2 * fx;
                const yCenter = (initYRange[0] + initYRange[1]) / 2;
                const yHalf = (initYRange[1] - initYRange[0]) / 2 * fy;
                const isXAsc = initXRange[0] < initXRange[1];
                const isYAsc = initYRange[0] < initYRange[1];
                const xMin = xCenter - xHalf;
                const xMax = xCenter + xHalf;
                const yMin = yCenter - yHalf;
                const yMax = yCenter + yHalf;
                const update = {
                  [`${activeXAxis}.range`]: isXAsc ? [xMin, xMax] : [xMax, xMin],
                  [`${activeYAxis}.range`]: isYAsc ? [yMin, yMax] : [yMax, yMin]
                };
                Plotly.relayout(plotDiv, update);
              }
            };
            const onPointerUp = () => {
              window.removeEventListener('pointermove', onPointerMove);
              window.removeEventListener('pointerup', onPointerUp);
            };
            plotDiv.addEventListener('pointerdown', downEvt => {
              if (downEvt.button !== 2) return; // only right-click
              downEvt.preventDefault();
              rect = plotDiv.getBoundingClientRect();
              startX = downEvt.clientX;
              startY = downEvt.clientY;
              const layout = plotDiv._fullLayout;
              const relX = (downEvt.clientX - rect.left) / rect.width;
              const relY = 1 - (downEvt.clientY - rect.top) / rect.height; // 0=bottom,1=top

              const xAxes = Object.keys(layout).filter(k => k.startsWith('xaxis'));
              
              let finalXAxis = 'xaxis';
              let finalYAxis = 'yaxis';

              for (const xName of xAxes) {
                  const yName = xName.replace('xaxis', 'yaxis');
                  const xAxis = layout[xName];
                  const yAxis = layout[yName];

                  if (xAxis && yAxis && xAxis.domain && yAxis.domain) {
                      if (relX >= xAxis.domain[0] && relX <= xAxis.domain[1] &&
                          relY >= yAxis.domain[0] && relY <= yAxis.domain[1]) {
                          finalXAxis = xName;
                          finalYAxis = yName;
                          break;
                      }
                  }
              }
              
              activeXAxis = finalXAxis;
              activeYAxis = finalYAxis;

              initXRange = [...layout[activeXAxis].range];
              initYRange = [...layout[activeYAxis].range];
              window.addEventListener('pointermove', onPointerMove);
              window.addEventListener('pointerup', onPointerUp);
            });
          }
          // Attach custom middle-click drag panning
          if (!plotDiv.__panHandlerAttached) {
            plotDiv.__panHandlerAttached = true;
            let pStartX = 0, pStartY = 0;
            let pInitXRange = null, pInitYRange = null;
            let pActiveXAxis = 'xaxis';
            let pActiveYAxis = 'yaxis';
            let pRect = null;
            const onPanMove = (mvEvt) => {
              if ((mvEvt.buttons & 4) === 0) return; // middle button not pressed
              const dx = mvEvt.clientX - pStartX;
              const dy = mvEvt.clientY - pStartY;
              if (pInitXRange && pInitYRange) {
                const xScale = (pInitXRange[1] - pInitXRange[0]) / pRect.width;
                const yScale = (pInitYRange[1] - pInitYRange[0]) / pRect.height;
                const xOffset = dx * xScale;
                const yOffset = -dy * yScale; // invert because screen Y grows downward

                const newX0 = pInitXRange[0] - xOffset;
                const newX1 = pInitXRange[1] - xOffset;
                const newY0 = pInitYRange[0] - yOffset;
                const newY1 = pInitYRange[1] - yOffset;

                const update = {
                  [`${pActiveXAxis}.range`]: [newX0, newX1],
                  [`${pActiveYAxis}.range`]: [newY0, newY1]
                };
                Plotly.relayout(plotDiv, update);
              }
            };
            const onPanUp = () => {
              window.removeEventListener('pointermove', onPanMove);
              window.removeEventListener('pointerup', onPanUp);
            };
            plotDiv.addEventListener('pointerdown', (pdEvt) => {
              if (pdEvt.button !== 1) return; // middle mouse only
              pdEvt.preventDefault();
              pRect = plotDiv.getBoundingClientRect();
              pStartX = pdEvt.clientX;
              pStartY = pdEvt.clientY;
              const layout = plotDiv._fullLayout;
              const relX = (pdEvt.clientX - pRect.left) / pRect.width;
              const relY = 1 - (pdEvt.clientY - pRect.top) / pRect.height;

              const xAxes = Object.keys(layout).filter(k=>k.startsWith('xaxis'));
              
              let finalXAxis = 'xaxis';
              let finalYAxis = 'yaxis';

              for (const xName of xAxes) {
                  const yName = xName.replace('xaxis', 'yaxis');
                  const xAxis = layout[xName];
                  const yAxis = layout[yName];

                  if (xAxis && yAxis && xAxis.domain && yAxis.domain) {
                      if (relX >= xAxis.domain[0] && relX <= xAxis.domain[1] &&
                          relY >= yAxis.domain[0] && relY <= yAxis.domain[1]) {
                          finalXAxis = xName;
                          finalYAxis = yName;
                          break;
                      }
                  }
              }

              pActiveXAxis = finalXAxis;
              pActiveYAxis = finalYAxis;

              pInitXRange = [...layout[pActiveXAxis].range];
              pInitYRange = [...layout[pActiveYAxis].range];
              window.addEventListener('pointermove', onPanMove);
              window.addEventListener('pointerup', onPanUp);
            });
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
      scrollZoom: true,
      edits: { legendPosition: true },
    });

    // Attach the same custom interactions to overlay plot
    if (!overlayDiv.__scaleHandlerAttached) {
      // === copy of scale handler ===
      overlayDiv.__scaleHandlerAttached = true;
      overlayDiv.addEventListener('contextmenu', e => e.preventDefault());
      let startX = 0, startY = 0, rect = null;
      let initXRange = null, initYRange = null;
      let activeXAxis = 'xaxis';
      let activeYAxis = 'yaxis';
      const onMove = mv => {
        if (mv.buttons !== 2) return;
        const dx = mv.clientX - startX;
        const dy = mv.clientY - startY;
        const sensitivity = 0.2;
        const factorX = 1 - dx / (rect.width * sensitivity);
        const factorY = 1 + dy / (rect.height * sensitivity);
        const clamp = (v,min,max)=>Math.max(min,Math.min(max,v));
        const fx = clamp(factorX,0.1,10);
        const fy = clamp(factorY,0.1,10);
        if(initXRange&&initYRange){
          const xCenter=(initXRange[0]+initXRange[1])/2;
          const xHalf=(initXRange[1]-initXRange[0])/2*fx;
          const yCenter=(initYRange[0]+initYRange[1])/2;
          const yHalf=(initYRange[1]-initYRange[0])/2*fy;
          const isXAsc=initXRange[0]<initXRange[1];
          const isYAsc=initYRange[0]<initYRange[1];
          const xMin=xCenter-xHalf,xMax=xCenter+xHalf;
          const yMin=yCenter-yHalf,yMax=yCenter+yHalf;
          Plotly.relayout(overlayDiv, {
            [`${activeXAxis}.range`]: isXAsc?[xMin,xMax]:[xMax,xMin],
            [`${activeYAxis}.range`]: isYAsc?[yMin,yMax]:[yMax,yMin]
          });
        }
      };
      const onUp=()=>{
        window.removeEventListener('pointermove',onMove);
        window.removeEventListener('pointerup',onUp);
      };
      overlayDiv.addEventListener('pointerdown', ev=>{
        if(ev.button!==2) return;
        ev.preventDefault();
        rect=overlayDiv.getBoundingClientRect();
        startX=ev.clientX;startY=ev.clientY;
        const layout=overlayDiv._fullLayout;
        const relX=(ev.clientX-rect.left)/rect.width;
        const relY=1-(ev.clientY-rect.top)/rect.height;
        const xAxes=Object.keys(layout).filter(k=>k.startsWith('xaxis'));
        
        let finalXAxis = 'xaxis';
        let finalYAxis = 'yaxis';
      
        for (const xName of xAxes) {
            const yName = xName.replace('xaxis', 'yaxis');
            const xAxis = layout[xName];
            const yAxis = layout[yName];
      
            if (xAxis && yAxis && xAxis.domain && yAxis.domain) {
                if (relX >= xAxis.domain[0] && relX <= xAxis.domain[1] &&
                    relY >= yAxis.domain[0] && relY <= yAxis.domain[1]) {
                    finalXAxis = xName;
                    finalYAxis = yName;
                    break;
                }
            }
        }

        activeXAxis=finalXAxis;
        activeYAxis=finalYAxis;
        initXRange=[...layout[activeXAxis].range];
        initYRange=[...layout[activeYAxis].range];
        window.addEventListener('pointermove',onMove);
        window.addEventListener('pointerup',onUp);
      });
    }

    if(!overlayDiv.__panHandlerAttached){
      overlayDiv.__panHandlerAttached = true;
      let pStartX=0,pStartY=0,pRect=null,pInitX=null,pInitY=null;
      const onPanMove=mv=>{
        if((mv.buttons&4)===0) return;
        const dx=mv.clientX-pStartX;
        const dy=mv.clientY-pStartY;
        if(pInitX&&pInitY){
          const xScale=(pInitX[1]-pInitX[0])/pRect.width;
          const yScale=(pInitY[1]-pInitY[0])/pRect.height;
          const xOffset=dx*xScale;
          const yOffset=-dy*yScale;
          const newX0=pInitX[0]-xOffset;
          const newX1=pInitX[1]-xOffset;
          const newY0=pInitY[0]-yOffset;
          const newY1=pInitY[1]-yOffset;
          Plotly.relayout(overlayDiv, {
            [`${pActiveXAxis}.range`]:[newX0,newX1],
            [`${pActiveYAxis}.range`]:[newY0,newY1]
          });
        }
      };
      const onPanUp=()=>{
        window.removeEventListener('pointermove',onPanMove);
        window.removeEventListener('pointerup',onPanUp);
      };
      overlayDiv.addEventListener('pointerdown',ev=>{
        if(ev.button!==1) return;
        ev.preventDefault();
        pRect=overlayDiv.getBoundingClientRect();
        pStartX=ev.clientX;pStartY=ev.clientY;
        const layout=overlayDiv._fullLayout;
        const relX=(ev.clientX-pRect.left)/pRect.width;
        const relY=1-(ev.clientY-pRect.top)/pRect.height;
        const xAxes=Object.keys(layout).filter(k=>k.startsWith('xaxis'));
        
        let finalXAxisPan = 'xaxis';
        let finalYAxisPan = 'yaxis';

        for (const xName of xAxes) {
          const yName = xName.replace('xaxis', 'yaxis');
          const xAxis = layout[xName];
          const yAxis = layout[yName];
    
          if (xAxis && yAxis && xAxis.domain && yAxis.domain) {
              if (relX >= xAxis.domain[0] && relX <= xAxis.domain[1] &&
                  relY >= yAxis.domain[0] && relY <= yAxis.domain[1]) {
                  finalXAxisPan = xName;
                  finalYAxisPan = yName;
                  break;
              }
          }
        }

        pActiveXAxis=finalXAxisPan;
        pActiveYAxis=finalYAxisPan;
        pInitX=[...layout[pActiveXAxis].range];
        pInitY=[...layout[pActiveYAxis].range];
        window.addEventListener('pointermove',onPanMove);
        window.addEventListener('pointerup',onPanUp);
      });
    }

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
        {!sidebarHidden && (
        <div ref={sidebarRef} style={sideStyle}>
            {sidebarExpanded ? (
              <>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  marginBottom: '16px',
                  padding: '0'
                }}>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '8px',
                    minWidth: 0
                  }}>
                    <Logo size={32} />
                    <span style={{ 
                      fontSize: '1.1em', 
                      fontWeight: '600', 
                      color: 'var(--text-color)',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    }}>
                      aivalanche
                    </span>
                  </div>
                  <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
                </div>
                <div style={{ 
                  flex: 1, 
                  display: 'flex', 
                  flexDirection: 'column', 
                  justifyContent: 'flex-end',
                  minHeight: 0,
                  marginBottom: '16px'
                }}>
                  <ChatInterface expanded={sidebarExpanded} />
                </div>
              </>
            ) : (
              <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '10px', alignItems: 'center' }}>
                <Logo size={28} />
                <ChatInterface expanded={sidebarExpanded} />
              </div>
            )}
            <div onMouseDown={handleMouseDown} className="sidebar-resizer" />
        </div>
        )}
        
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
            ☰
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
    position: 'relative',
    backgroundColor: 'var(--sidebar-bg)'
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
      {!sidebarHidden && (
      <div ref={sidebarRef} style={sideStyle}>
        {sidebarExpanded ? (
          <>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                marginBottom: '16px',
                padding: '0'
              }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '8px',
                  minWidth: 0
                }}>
                                     <Logo size={32} />
                  <span style={{ 
                    fontSize: '1.1em', 
                    fontWeight: '600', 
                    color: 'var(--text-color)',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    aivalanche
                  </span>
                </div>
            <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
              </div>
                              <div style={{ 
                  flex: 1, 
                  display: 'flex', 
                  flexDirection: 'column', 
                  justifyContent: 'flex-end',
                  minHeight: 0,
                  marginBottom: '16px'
                }}>
                  <ChatInterface expanded={sidebarExpanded} />
                </div>
          </>
        ) : (
            <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '10px', alignItems: 'center' }}>
                                <Logo size={28} />
              <ChatInterface expanded={sidebarExpanded} />
          </div>
        )}
          <div onMouseDown={handleMouseDown} className="sidebar-resizer" />
      </div>
      )}

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
          ☰
        </button>
      )}

      <main style={mainStyle}>
        <div style={gridStyle}>
          {figures.map(fig => (
            <div key={fig.id} className="plot-container" style={plotContainerStyle}>
              {figures.length > 1 && (
              <button className="zoom-btn" onClick={() => setActiveFig(fig)} title="Expand plot">
                <ExpandIcon size={16} />
              </button>
              )}
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