import { useState, useCallback } from 'react';
import { getSidebarDimensions } from '../utils/cssVariables';
import { resizePlotsWithDelay } from '../utils/plotUtils';

/**
 * Custom hook for managing sidebar resize functionality
 */
export const useSidebarResize = (figures) => {
  const { expandedWidth, collapsedWidth } = getSidebarDimensions();
  
  const [sidebarWidth, setSidebarWidth] = useState(expandedWidth);
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  const [sidebarHidden, setSidebarHidden] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  
  const collapsedThreshold = 80; // px
  const hiddenThreshold = 30; // px
  
  const handleMouseDown = useCallback((e) => {
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
        newWidth = Math.max(0, newWidth);
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
      newWidth = Math.max(0, newWidth);
      
      // Snap to hidden if below threshold
      if (newWidth < hiddenThreshold) {
        newWidth = 0;
      }
      
      setSidebarWidth(newWidth);
      setSidebarExpanded(newWidth > collapsedThreshold);
      setSidebarHidden(newWidth === 0);
      
      // Resize plots after sidebar animation
      if (figures) {
        resizePlotsWithDelay(figures, 350);
      }
    };
    
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  }, [sidebarWidth, figures]);
  
  const restoreSidebar = useCallback(() => {
    setSidebarWidth(expandedWidth);
    setSidebarExpanded(true);
    setSidebarHidden(false);
    
    // Resize plots after sidebar animation
    if (figures) {
      return resizePlotsWithDelay(figures, 350);
    }
  }, [expandedWidth, figures]);
  
  const toggleSidebar = useCallback(() => {
    if (sidebarHidden) {
      restoreSidebar();
    } else {
      const newExpanded = !sidebarExpanded;
      const newWidth = newExpanded ? expandedWidth : collapsedWidth;
      setSidebarWidth(newWidth);
      setSidebarExpanded(newExpanded);
      
      // Resize plots after sidebar animation
      if (figures) {
        resizePlotsWithDelay(figures, 350);
      }
    }
  }, [sidebarHidden, sidebarExpanded, expandedWidth, collapsedWidth, figures, restoreSidebar]);
  
  return {
    sidebarWidth,
    sidebarExpanded,
    sidebarHidden,
    isDragging,
    handleMouseDown,
    restoreSidebar,
    toggleSidebar,
    setSidebarWidth,
    setSidebarExpanded,
    setSidebarHidden
  };
};