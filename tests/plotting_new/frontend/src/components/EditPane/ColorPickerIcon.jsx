import React, { useState, useRef, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { SketchPicker } from 'react-color';

const ColorPickerIcon = ({ icon: Icon, color, onChange, title }) => {
  const [displayPicker, setDisplayPicker] = useState(false);
  const [localColor, setLocalColor] = useState(() => {
    // Parse initial color to extract RGB and alpha
    if (!color || typeof color !== 'string') return { r: 31, g: 119, b: 180, a: 1 };
    
    // Handle rgba format
    const rgbaMatch = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+),?\s*([0-9.]+)?\)/);
    if (rgbaMatch) {
      return {
        r: parseInt(rgbaMatch[1]),
        g: parseInt(rgbaMatch[2]),
        b: parseInt(rgbaMatch[3]),
        a: parseFloat(rgbaMatch[4] || 1)
      };
    }
    
    // Handle hex format
    if (color.startsWith('#')) {
      const hex = color.replace('#', '');
      const r = parseInt(hex.substr(0, 2), 16) || 0;
      const g = parseInt(hex.substr(2, 2), 16) || 0;
      const b = parseInt(hex.substr(4, 2), 16) || 0;
      const a = hex.length === 8 ? parseInt(hex.substr(6, 2), 16) / 255 : 1;
      return { r, g, b, a };
    }
    
    return { r: 31, g: 119, b: 180, a: 1 };
  });
  
  const pickerRef = useRef(null);
  const buttonRef = useRef(null);
  
  useEffect(() => {
    // Update local color when prop changes
    if (!color || typeof color !== 'string') {
      setLocalColor({ r: 31, g: 119, b: 180, a: 1 });
      return;
    }
    
    // Handle rgba format
    const rgbaMatch = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+),?\s*([0-9.]+)?\)/);
    if (rgbaMatch) {
      setLocalColor({
        r: parseInt(rgbaMatch[1]),
        g: parseInt(rgbaMatch[2]),
        b: parseInt(rgbaMatch[3]),
        a: parseFloat(rgbaMatch[4] || 1)
      });
      return;
    }
    
    // Handle hex format
    if (color.startsWith('#')) {
      const hex = color.replace('#', '');
      const r = parseInt(hex.substr(0, 2), 16) || 0;
      const g = parseInt(hex.substr(2, 2), 16) || 0;
      const b = parseInt(hex.substr(4, 2), 16) || 0;
      const a = hex.length === 8 ? parseInt(hex.substr(6, 2), 16) / 255 : 1;
      setLocalColor({ r, g, b, a });
    }
  }, [color]);
  
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target) &&
          buttonRef.current && !buttonRef.current.contains(event.target)) {
        setDisplayPicker(false);
      }
    };
    
    if (displayPicker) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [displayPicker]);
  
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
  
  const [pickerPosition, setPickerPosition] = useState({ top: 0, left: 0, showAbove: false });
  
  useEffect(() => {
    if (displayPicker && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      const pickerHeight = 250; // Approximate height of SketchPicker
      const pickerWidth = 220; // Approximate width of SketchPicker
      const viewportHeight = window.innerHeight;
      const viewportWidth = window.innerWidth;
      const spaceBelow = viewportHeight - rect.bottom;
      const spaceAbove = rect.top;
      const spaceRight = viewportWidth - rect.left;
      
      // Check if there's enough space below, otherwise show above
      const showAbove = spaceBelow < pickerHeight && spaceAbove > pickerHeight;
      
      // Check if there's enough space on the right, otherwise align to the right edge
      let leftPosition = rect.left;
      if (spaceRight < pickerWidth) {
        leftPosition = Math.max(0, viewportWidth - pickerWidth - 10);
      }
      
      setPickerPosition({
        top: showAbove ? rect.top - pickerHeight - 64 : rect.bottom + 4,
        left: leftPosition,
        showAbove
      });
    }
  }, [displayPicker]);
  
  const popoverStyle = {
    position: 'fixed',
    zIndex: 10000,
    top: `${pickerPosition.top}px`,
    left: `${pickerPosition.left}px`,
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    borderRadius: '4px',
  };
  
  const handleClick = () => {
    setDisplayPicker(!displayPicker);
  };
  
  const handleChange = (color) => {
    setLocalColor(color.rgb);
    // Convert to rgba string
    const rgbaString = `rgba(${color.rgb.r}, ${color.rgb.g}, ${color.rgb.b}, ${color.rgb.a})`;
    onChange({ target: { value: rgbaString } });
  };
  
  // Convert localColor to hex for icon display
  const colorForIcon = `#${localColor.r.toString(16).padStart(2, '0')}${localColor.g.toString(16).padStart(2, '0')}${localColor.b.toString(16).padStart(2, '0')}`;
  
  return (
    <>
      <div 
        ref={buttonRef}
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
        <Icon size={20} color={colorForIcon} style={{ opacity: localColor.a }} />
      </div>
      {displayPicker && ReactDOM.createPortal(
        <div style={popoverStyle} ref={pickerRef}>
          <SketchPicker 
            color={localColor} 
            onChange={handleChange}
            presetColors={[
              '#D0021B', '#F5A623', '#F8E71C', '#8B572A', '#7ED321',
              '#417505', '#BD10E0', '#9013FE', '#4A90E2', '#50E3C2',
              '#B8E986', '#000000', '#4A4A4A', '#9B9B9B', '#FFFFFF',
            ]}
          />
        </div>,
        document.body
      )}
    </>
  );
};

export default ColorPickerIcon;