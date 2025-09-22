import React, { useState, useEffect, useRef, useMemo } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

// Components
import Sidebar from './components/Sidebar/Sidebar.jsx';
import EditPane from './components/EditPane/EditPane.jsx';
import TableView from './components/TableView/TableView.jsx';
import WelcomeScreen from './components/WelcomeScreen.jsx';
import SidebarButton from './components/SidebarButton.jsx';
import PlotGridContainer from './components/PlotGrid/PlotGridContainer.jsx';
import ExpandedPlotView from './components/PlotGrid/ExpandedPlotView.jsx';

// Hooks
import { useSidebarResize } from './hooks/useSidebarResize';
import { useGridLayout } from './hooks/useGridLayout';
import { usePlotManagement } from './hooks/usePlotManagement';

// Utils
import { resizePlotsWithDelay } from './utils/plotUtils';
import { 
  createManagedFigure, 
  updateFigureMetadata,
  syncFigureWithDOM
} from './utils/figureManager.js';

const API_BASE = 'http://localhost:8000';

function App() {
  const navigate = useNavigate();

  // Core state
  const [config, setConfig] = useState(null);
  const [theme, setTheme] = useState('light');
  const [localFigures, setLocalFigures] = useState(null);
  const [isLoadingConfig, setIsLoadingConfig] = useState(false);
  
  // Custom hooks
  const {
    sidebarWidth,
    sidebarExpanded,
    sidebarHidden,
    isDragging,
    handleMouseDown,
    restoreSidebar
  } = useSidebarResize(localFigures);
  
  const figures = useMemo(() => localFigures || [], [localFigures]);
  const figureCount = figures.length;
  
  const {
    gridColumns,
    setGridColumns,
    windowHeight,
    gridStyle,
    plotContainerStyle,
    nRows
  } = useGridLayout(figureCount);
  
  const {
    activeFig,
    editingFig,
    editPaneOpen,
    tableViewFig,
    tableViewOpen,
    handleEditFigure,
    handleCloseEditPane,
    handleViewTable,
    handleCloseTableView,
    handleExpandFigure,
    handleCloseExpandedView
  } = usePlotManagement();
  
  // Refs for plot management
  const plotRefs = useRef({});
  const lastPlotDataRef = useRef({});
  
  // Ensure theme is applied to document
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.body.dataset.theme = theme;
    }
  }, [theme]);
  
  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (localFigures) {
        resizePlotsWithDelay(localFigures, 100);
      }
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [localFigures]);
  
  // Toggle theme
  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };
  
  // Create themed layout (from original App.jsx)
  const themedLayout = useMemo(() => {
    // Get computed styles from body where theme is applied
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
  
  // Plots are now rendered by individual PlotContainer components
  // No need for centralized rendering
  
  // Effect to resize plots when grid columns change
  useEffect(() => {
    if (localFigures && localFigures.length > 1) {
      resizePlotsWithDelay(localFigures, 100);
    }
  }, [gridColumns, localFigures]);
  
  // Handle config update from chat (from original App.jsx)
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
            // Create managed figure with embedded metadata, preserving the ID
            return createManagedFigure(fig.figure, fig.metadata, fig.id);
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
  
  // Load demo plots
  const loadDemoPlots = async () => {
    try {
      setIsLoadingConfig(true);
      const response = await axios.post(`${API_BASE}/api/python/demo`, {
        session_id: "demo",
        script_name: "comprehensive_demo"
      });

      const result = response.data;
      if (result.success && result.plots) {
        const dashboard = {
          figures: result.plots.map(plot => {
            // Pass the plot ID as a separate parameter to preserve it
            return createManagedFigure(plot.figure, plot.metadata, plot.id);
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

  // Load scatter plots demo
  const loadScatterDemo = async () => {
    try {
      setIsLoadingConfig(true);
      const response = await axios.post(`${API_BASE}/api/python/demo`, {
        session_id: "demo",
        script_name: "scatter_plots_demo"
      });

      const result = response.data;
      if (result.success && result.plots) {
        const dashboard = {
          figures: result.plots.map(plot => {
            return createManagedFigure(plot.figure, plot.metadata, plot.id);
          }),
          app_title: "Scatter Plots Showcase",
          theme: "light"
        };

        setConfig(dashboard);
        setLocalFigures(dashboard.figures);
        console.log('Scatter plots demo loaded with', dashboard.figures.length, 'figures');
      } else {
        throw new Error("Scatter demo execution failed: " + (result.error?.message || "Unknown error"));
      }
    } catch (err) {
      console.error("Error loading scatter plots demo:", err);
    } finally {
      setIsLoadingConfig(false);
    }
  };

  // Load line plots demo
  const loadLineDemo = async () => {
    try {
      setIsLoadingConfig(true);
      const response = await axios.post(`${API_BASE}/api/python/demo`, {
        session_id: "demo",
        script_name: "line_plots_demo"
      });

      const result = response.data;
      if (result.success && result.plots) {
        const dashboard = {
          figures: result.plots.map(plot => {
            return createManagedFigure(plot.figure, plot.metadata, plot.id);
          }),
          app_title: "Line Plots Showcase",
          theme: "light"
        };

        setConfig(dashboard);
        setLocalFigures(dashboard.figures);
        console.log('Line plots demo loaded with', dashboard.figures.length, 'figures');
      } else {
        throw new Error("Line demo execution failed: " + (result.error?.message || "Unknown error"));
      }
    } catch (err) {
      console.error("Error loading line plots demo:", err);
    } finally {
      setIsLoadingConfig(false);
    }
  };

  // Load bar plots demo
  const loadBarDemo = async () => {
    try {
      setIsLoadingConfig(true);
      const response = await axios.post(`${API_BASE}/api/python/demo`, {
        session_id: "demo",
        script_name: "bar_plots_demo"
      });

      const result = response.data;
      if (result.success && result.plots) {
        const dashboard = {
          figures: result.plots.map(plot => {
            return createManagedFigure(plot.figure, plot.metadata, plot.id);
          }),
          app_title: "Bar Charts Showcase",
          theme: "light"
        };

        setConfig(dashboard);
        setLocalFigures(dashboard.figures);
        console.log('Bar plots demo loaded with', dashboard.figures.length, 'figures');
      } else {
        throw new Error("Bar demo execution failed: " + (result.error?.message || "Unknown error"));
      }
    } catch (err) {
      console.error("Error loading bar plots demo:", err);
    } finally {
      setIsLoadingConfig(false);
    }
  };

  // Load heatmap plots demo
  const loadHeatmapDemo = async () => {
    try {
      setIsLoadingConfig(true);
      const response = await axios.post(`${API_BASE}/api/python/demo`, {
        session_id: "demo",
        script_name: "heatmap_plots_demo"
      });

      const result = response.data;
      if (result.success && result.plots) {
        const dashboard = {
          figures: result.plots.map(plot => {
            return createManagedFigure(plot.figure, plot.metadata, plot.id);
          }),
          app_title: "Heatmaps & 2D Density Showcase",
          theme: "light"
        };

        setConfig(dashboard);
        setLocalFigures(dashboard.figures);
        console.log('Heatmap plots demo loaded with', dashboard.figures.length, 'figures');
      } else {
        throw new Error("Heatmap demo execution failed: " + (result.error?.message || "Unknown error"));
      }
    } catch (err) {
      console.error("Error loading heatmap plots demo:", err);
    } finally {
      setIsLoadingConfig(false);
    }
  };

  // Load pie charts demo
  const loadPieDemo = async () => {
    try {
      setIsLoadingConfig(true);
      const response = await axios.post(`${API_BASE}/api/python/demo`, {
        session_id: "demo",
        script_name: "pie_charts_demo"
      });

      const result = response.data;
      if (result.success && result.plots) {
        const dashboard = {
          figures: result.plots.map(plot => {
            return createManagedFigure(plot.figure, plot.metadata, plot.id);
          }),
          app_title: "Pie Charts & Proportional Visualizations",
          theme: "light"
        };

        setConfig(dashboard);
        setLocalFigures(dashboard.figures);
        console.log('Pie charts demo loaded with', dashboard.figures.length, 'figures');
      } else {
        throw new Error("Pie demo execution failed: " + (result.error?.message || "Unknown error"));
      }
    } catch (err) {
      console.error("Error loading pie charts demo:", err);
    } finally {
      setIsLoadingConfig(false);
    }
  };

  // Load statistical plots demo
  const loadStatisticalDemo = async () => {
    try {
      setIsLoadingConfig(true);
      const response = await axios.post(`${API_BASE}/api/python/demo`, {
        session_id: "demo",
        script_name: "statistical_plots_demo"
      });

      const result = response.data;
      if (result.success && result.plots) {
        const dashboard = {
          figures: result.plots.map(plot => {
            return createManagedFigure(plot.figure, plot.metadata, plot.id);
          }),
          app_title: "Statistical Plots & Distributions",
          theme: "light"
        };

        setConfig(dashboard);
        setLocalFigures(dashboard.figures);
        console.log('Statistical plots demo loaded with', dashboard.figures.length, 'figures');
      } else {
        throw new Error("Statistical demo execution failed: " + (result.error?.message || "Unknown error"));
      }
    } catch (err) {
      console.error("Error loading statistical plots demo:", err);
    } finally {
      setIsLoadingConfig(false);
    }
  };

  // Load 3D plots demo
  const load3DDemo = async () => {
    try {
      setIsLoadingConfig(true);
      const response = await axios.post(`${API_BASE}/api/python/demo`, {
        session_id: "demo",
        script_name: "3d_plots_demo"
      });

      const result = response.data;
      if (result.success && result.plots) {
        const dashboard = {
          figures: result.plots.map(plot => {
            return createManagedFigure(plot.figure, plot.metadata, plot.id);
          }),
          app_title: "3D Visualizations",
          theme: "light"
        };

        setConfig(dashboard);
        setLocalFigures(dashboard.figures);
        console.log('3D plots demo loaded with', dashboard.figures.length, 'figures');
      } else {
        throw new Error("3D demo execution failed: " + (result.error?.message || "Unknown error"));
      }
    } catch (err) {
      console.error("Error loading 3D plots demo:", err);
    } finally {
      setIsLoadingConfig(false);
    }
  };

  // Load financial plots demo
  const loadFinancialDemo = async () => {
    try {
      setIsLoadingConfig(true);
      const response = await axios.post(`${API_BASE}/api/python/demo`, {
        session_id: "demo",
        script_name: "financial_plots_demo"
      });

      const result = response.data;
      if (result.success && result.plots) {
        const dashboard = {
          figures: result.plots.map(plot => {
            return createManagedFigure(plot.figure, plot.metadata, plot.id);
          }),
          app_title: "Financial Charts & Technical Indicators",
          theme: "light"
        };

        setConfig(dashboard);
        setLocalFigures(dashboard.figures);
        console.log('Financial plots demo loaded with', dashboard.figures.length, 'figures');
      } else {
        throw new Error("Financial demo execution failed: " + (result.error?.message || "Unknown error"));
      }
    } catch (err) {
      console.error("Error loading financial plots demo:", err);
    } finally {
      setIsLoadingConfig(false);
    }
  };

  // Load specialty plots demo
  const loadSpecialtyDemo = async () => {
    try {
      setIsLoadingConfig(true);
      const response = await axios.post(`${API_BASE}/api/python/demo`, {
        session_id: "demo",
        script_name: "specialty_plots_demo"
      });

      const result = response.data;
      if (result.success && result.plots) {
        const dashboard = {
          figures: result.plots.map(plot => {
            return createManagedFigure(plot.figure, plot.metadata, plot.id);
          }),
          app_title: "Specialty Plots (PCP, Radar, Network & More)",
          theme: "light"
        };

        setConfig(dashboard);
        setLocalFigures(dashboard.figures);
        console.log('Specialty plots demo loaded with', dashboard.figures.length, 'figures');
      } else {
        throw new Error("Specialty demo execution failed: " + (result.error?.message || "Unknown error"));
      }
    } catch (err) {
      console.error("Error loading specialty plots demo:", err);
    } finally {
      setIsLoadingConfig(false);
    }
  };
  
  // Clear plots
  const clearPlots = () => {
    setConfig(null);
    setLocalFigures(null);
  };
  
  // Update figure after edit
  const handleUpdateFigure = (updatedFigure) => {
    console.log('Updating figure:', {
      updatedFigureId: updatedFigure.id,
      editingFigId: editingFig?.id,
      allFigureIds: localFigures.map(f => f.id)
    });
    
    const updatedFigures = localFigures.map(f => 
      f.id === updatedFigure.id ? updatedFigure : f
    );
    setLocalFigures(updatedFigures);
  };

  
  // App styles
  const appStyle = {
    display: 'flex',
    backgroundColor: 'var(--background-color)',
    color: 'var(--text-color)',
    height: '100vh',
    overflow: 'hidden',
  };
  
  const mainStyle = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: 'var(--background-color)',
    color: 'var(--text-color)',
    padding: 0,
    overflow: 'hidden',
    height: '100vh',
    boxSizing: 'border-box',
  };
  
  const welcomeMainStyle = {
    flex: 1,
    padding: 'var(--main-padding)',
    overflow: 'auto',
    height: '100vh',
    boxSizing: 'border-box',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  };
  
  // Show welcome screen when no config
  if (!config) {
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
          onLoadScatterDemo={loadScatterDemo}
          onLoadLineDemo={loadLineDemo}
          onLoadBarDemo={loadBarDemo}
          onLoadHeatmapDemo={loadHeatmapDemo}
          isLoadingConfig={isLoadingConfig}
          showBackButton={true}
        />
        
        <SidebarButton 
          isHidden={sidebarHidden}
          onRestore={restoreSidebar}
        />
        
        <main style={welcomeMainStyle}>
          <WelcomeScreen
            onLoadDemo={loadDemoPlots}
            onLoadScatterDemo={loadScatterDemo}
            onLoadLineDemo={loadLineDemo}
            onLoadBarDemo={loadBarDemo}
            onLoadHeatmapDemo={loadHeatmapDemo}
            onLoadPieDemo={loadPieDemo}
            onLoadStatisticalDemo={loadStatisticalDemo}
            onLoad3DDemo={load3DDemo}
            onLoadFinancialDemo={loadFinancialDemo}
            onLoadSpecialtyDemo={loadSpecialtyDemo}
            isLoadingConfig={isLoadingConfig}
          />
        </main>
      </div>
    );
  }
  
  // Main app with plots
  return (
    <div style={appStyle}>
      <Sidebar
        theme={theme}
        toggleTheme={toggleTheme}
        sidebarWidth={sidebarWidth}
        sidebarExpanded={sidebarExpanded}
        sidebarHidden={sidebarHidden}
        onDragStart={handleMouseDown}
        appTitle={config?.app_title || "Data Visualization Studio"}
        currentConfig={config}
        onConfigUpdate={handleConfigUpdateFromChat}
        onClearPlots={clearPlots}
        onLoadDemo={loadDemoPlots}
        onLoadScatterDemo={loadScatterDemo}
        onLoadLineDemo={loadLineDemo}
        isLoadingConfig={isLoadingConfig}
        showBackButton={true}
      />
      
      <SidebarButton 
        isHidden={sidebarHidden}
        onRestore={restoreSidebar}
      />
      
      <main style={mainStyle}>
        <PlotGridContainer
          figures={figures}
          gridColumns={gridColumns}
          setGridColumns={setGridColumns}
          figureCount={figureCount}
          nRows={nRows}
          gridStyle={gridStyle}
          plotContainerStyle={plotContainerStyle}
          onEditFigure={handleEditFigure}
          onViewTable={handleViewTable}
          onExpandFigure={handleExpandFigure}
          themedLayout={themedLayout}
        />
      </main>
      
      <EditPane
        isOpen={editPaneOpen}
        onClose={handleCloseEditPane}
        figure={editingFig}
        onUpdate={handleUpdateFigure}
      />
      
      <TableView
        isOpen={tableViewOpen}
        onClose={handleCloseTableView}
        figure={tableViewFig}
      />
      
      <ExpandedPlotView
        activeFig={activeFig}
        onClose={handleCloseExpandedView}
        onEditFigure={handleEditFigure}
        onViewTable={handleViewTable}
        themedLayout={themedLayout}
      />
    </div>
  );
}

export default App;