import { useState, useCallback } from 'react';
import { resizePlotsWithDelay } from '../utils/plotUtils';

/**
 * Custom hook for managing plot-related state and operations
 */
export const usePlotManagement = () => {
  const [activeFig, setActiveFig] = useState(null);
  const [editingFig, setEditingFig] = useState(null);
  const [editPaneOpen, setEditPaneOpen] = useState(false);
  const [tableViewFig, setTableViewFig] = useState(null);
  const [tableViewOpen, setTableViewOpen] = useState(false);

  const handleEditFigure = useCallback((figure) => {
    setEditingFig(figure);
    setEditPaneOpen(true);
  }, []);

  const handleCloseEditPane = useCallback(() => {
    setEditPaneOpen(false);
    setEditingFig(null);
  }, []);

  const handleViewTable = useCallback((figure) => {
    setTableViewFig(figure);
    setTableViewOpen(true);
  }, []);

  const handleCloseTableView = useCallback(() => {
    setTableViewOpen(false);
    setTableViewFig(null);
  }, []);

  const handleExpandFigure = useCallback((figure) => {
    // Deep clone the figure to ensure complete isolation
    const clonedFigure = JSON.parse(JSON.stringify(figure));
    setActiveFig(clonedFigure);
  }, []);

  const handleCloseExpandedView = useCallback(() => {
    setActiveFig(null);
    // No need to resize plots - expanded view is independent
  }, []);
  
  return {
    // State
    activeFig,
    editingFig,
    editPaneOpen,
    tableViewFig,
    tableViewOpen,
    
    // Actions
    handleEditFigure,
    handleCloseEditPane,
    handleViewTable,
    handleCloseTableView,
    handleExpandFigure,
    handleCloseExpandedView,
    
    // Direct setters (if needed)
    setActiveFig,
    setEditingFig,
    setEditPaneOpen,
    setTableViewFig,
    setTableViewOpen
  };
};