import React, { useRef } from 'react';
import ThemeToggle from '../ThemeToggle.jsx';
import ChatInterface from '../ChatInterface.jsx';
import { Logo } from '../icons';
import './Sidebar.css';

const Sidebar = ({ 
  theme, 
  toggleTheme,
  sidebarWidth,
  sidebarExpanded,
  sidebarHidden,
  onDragStart,
  appTitle,
  currentConfig,
  onConfigUpdate
}) => {
  const sidebarRef = useRef(null);

  return (
    <aside 
      ref={sidebarRef}
      className={`sidebar ${!sidebarExpanded ? 'collapsed' : ''} ${sidebarHidden ? 'hidden' : ''}`}
      style={{ width: `${sidebarWidth}px` }}
    >
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <Logo size={40} />
          <span className="sidebar-title">
            aivalanche
          </span>
        </div>
        <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
      </div>

      <div className="sidebar-content">
        <ChatInterface 
          expanded={sidebarExpanded} 
          currentConfig={currentConfig}
          onConfigUpdate={onConfigUpdate}
        />
      </div>

      <div 
        className="sidebar-resize-handle"
        onMouseDown={onDragStart}
      />
    </aside>
  );
};

export default Sidebar;