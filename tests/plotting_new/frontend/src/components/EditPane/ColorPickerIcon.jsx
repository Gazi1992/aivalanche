import React, { useRef } from 'react';

const ColorPickerIcon = ({ icon: Icon, color, onChange, title }) => {
  const inputRef = useRef(null);
  
  const containerStyle = {
    position: 'relative',
    width: '32px',
    height: '32px',
    cursor: 'pointer',
    border: '1px solid var(--border-color)',
    borderRadius: '3px',
    backgroundColor: 'var(--background-color)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.2s ease',
  };
  
  const hiddenInputStyle = {
    position: 'absolute',
    opacity: 0,
    width: 0,
    height: 0,
    pointerEvents: 'none',
  };
  
  const handleClick = () => {
    inputRef.current?.click();
  };
  
  return (
    <div 
      style={containerStyle} 
      onClick={handleClick}
      title={title}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = 'var(--background-secondary)';
        e.currentTarget.style.borderColor = 'var(--primary-color)';
        e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'var(--background-color)';
        e.currentTarget.style.borderColor = 'var(--border-color)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      <Icon size={20} color={color || '#000000'} />
      <input
        ref={inputRef}
        type="color"
        value={color || '#000000'}
        onChange={onChange}
        style={hiddenInputStyle}
      />
    </div>
  );
};

export default ColorPickerIcon;