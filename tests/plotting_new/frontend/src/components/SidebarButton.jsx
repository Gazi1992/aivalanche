import React from 'react';
import { ChatAssistantIcon } from './icons';

const SidebarButton = ({ isHidden, onRestore }) => {
  if (!isHidden) return null;

  return (
    <button
      onClick={onRestore}
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
  );
};

export default SidebarButton;