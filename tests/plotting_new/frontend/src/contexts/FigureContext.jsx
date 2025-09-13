/**
 * Figure Context
 * Centralized state management for figures
 */
import React, { createContext, useContext, useState, useCallback } from 'react';
import { createManagedFigure, updateFigureMetadata, syncFigureWithDOM } from '../utils/figureManager';

const FigureContext = createContext();

/**
 * Custom hook to use the figure context
 */
export const useFigures = () => {
  const context = useContext(FigureContext);
  if (!context) {
    throw new Error('useFigures must be used within a FigureProvider');
  }
  return context;
};

/**
 * Figure Provider component
 */
export const FigureProvider = ({ children }) => {
  const [config, setConfig] = useState(null);
  const [figures, setFigures] = useState([]);
  const [activeFigure, setActiveFigure] = useState(null);
  const [editingFigure, setEditingFigure] = useState(null);
  
  /**
   * Load figures from dashboard data
   */
  const loadFigures = useCallback((dashboard) => {
    if (!dashboard) {
      setConfig(null);
      setFigures([]);
      return;
    }
    
    setConfig(dashboard);
    
    // Process figures using the managed figure system
    if (dashboard.figures) {
      const processedFigures = dashboard.figures.map(fig => {
        if (fig.figure && fig.metadata) {
          return fig; // Already a managed figure
        }
        return createManagedFigure(fig.figure || fig, fig.metadata);
      });
      setFigures(processedFigures);
    }
  }, []);
  
  /**
   * Update a single figure
   */
  const updateFigure = useCallback((figureId, updates) => {
    setFigures(prev => prev.map(fig => 
      fig.id === figureId ? { ...fig, ...updates } : fig
    ));
  }, []);
  
  /**
   * Update figure metadata
   */
  const updateMetadata = useCallback((figureId, metadataPath, value) => {
    setFigures(prev => prev.map(fig => {
      if (fig.id === figureId) {
        return updateFigureMetadata(fig, metadataPath, value);
      }
      return fig;
    }));
  }, []);
  
  /**
   * Sync figure with DOM (capture legend position, etc.)
   */
  const syncWithDOM = useCallback((figureId) => {
    const figure = figures.find(f => f.id === figureId);
    if (figure) {
      const plotId = `plot-${figureId}`;
      const syncedFigure = syncFigureWithDOM(figure, plotId);
      updateFigure(figureId, syncedFigure);
      return syncedFigure;
    }
    return figure;
  }, [figures, updateFigure]);
  
  /**
   * Clear all figures
   */
  const clearFigures = useCallback(() => {
    setConfig(null);
    setFigures([]);
    setActiveFigure(null);
    setEditingFigure(null);
  }, []);
  
  /**
   * Set active figure for expanded view
   */
  const setExpandedFigure = useCallback((figure) => {
    setActiveFigure(figure);
  }, []);
  
  /**
   * Set figure for editing
   */
  const setFigureForEdit = useCallback((figure) => {
    // Sync with DOM before editing to capture current state
    const syncedFigure = figure ? syncWithDOM(figure.id) : null;
    setEditingFigure(syncedFigure);
  }, [syncWithDOM]);
  
  const value = {
    // State
    config,
    figures,
    activeFigure,
    editingFigure,
    
    // Actions
    loadFigures,
    updateFigure,
    updateMetadata,
    syncWithDOM,
    clearFigures,
    setExpandedFigure,
    setFigureForEdit,
  };
  
  return (
    <FigureContext.Provider value={value}>
      {children}
    </FigureContext.Provider>
  );
};