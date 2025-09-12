import React, { useState, useEffect } from 'react';
import { ChromePicker } from 'react-color';

const EditPaneSimple = ({ isOpen, onClose, plotData, onUpdate }) => {
  const [localPlotData, setLocalPlotData] = useState(null);
  const [showColorPicker, setShowColorPicker] = useState(null);
  
  useEffect(() => {
    if (plotData) {
      setLocalPlotData(JSON.parse(JSON.stringify(plotData)));
    }
  }, [plotData]);

  if (!isOpen || !localPlotData) return null;

  const handleTitleChange = (e) => {
    const newData = { ...localPlotData };
    if (!newData.layout) newData.layout = {};
    newData.layout.title = { ...newData.layout.title, text: e.target.value };
    setLocalPlotData(newData);
  };

  const handleAxisTitleChange = (axis, value) => {
    const newData = { ...localPlotData };
    if (!newData.layout) newData.layout = {};
    if (!newData.layout[axis]) newData.layout[axis] = {};
    newData.layout[axis].title = { text: value };
    setLocalPlotData(newData);
  };

  const handleColorChange = (traceIndex, color) => {
    const newData = { ...localPlotData };
    if (newData.data && newData.data[traceIndex]) {
      const trace = newData.data[traceIndex];
      if (trace.type === 'scatter' || trace.type === 'line') {
        if (!trace.line) trace.line = {};
        trace.line.color = color.hex;
      } else {
        if (!trace.marker) trace.marker = {};
        trace.marker.color = color.hex;
      }
    }
    setLocalPlotData(newData);
    setShowColorPicker(null);
  };

  const handleApply = () => {
    onUpdate(localPlotData);
    onClose();
  };

  const overlayStyle = {
    position: 'fixed',
    top: 0,
    right: 0,
    bottom: 0,
    width: '400px',
    backgroundColor: 'var(--card-background-color)',
    boxShadow: '-2px 0 10px rgba(0,0,0,0.1)',
    zIndex: 1000,
    display: 'flex',
    flexDirection: 'column',
    transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
    transition: 'transform 0.3s ease-in-out',
  };

  const headerStyle = {
    padding: '20px',
    borderBottom: '1px solid var(--border-color)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  };

  const contentStyle = {
    flex: 1,
    overflowY: 'auto',
    padding: '20px',
  };

  const sectionStyle = {
    marginBottom: '24px',
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '8px',
    color: 'var(--text-secondary)',
    fontSize: '0.85rem',
    fontWeight: '500',
  };

  const inputStyle = {
    width: '100%',
    padding: '8px 12px',
    border: '1px solid var(--border-color)',
    borderRadius: '4px',
    backgroundColor: 'var(--background-color)',
    color: 'var(--text-color)',
    fontSize: '0.9rem',
  };

  const buttonStyle = {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.9rem',
    transition: 'opacity 0.2s',
  };

  const colorSwatchStyle = {
    width: '32px',
    height: '32px',
    borderRadius: '4px',
    border: '2px solid var(--border-color)',
    cursor: 'pointer',
    display: 'inline-block',
    marginRight: '8px',
  };

  return (
    <>
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.3)',
            zIndex: 999,
          }}
          onClick={onClose}
        />
      )}
      
      <div style={overlayStyle}>
        <div style={headerStyle}>
          <h3 style={{ margin: 0 }}>Edit Plot</h3>
          <button
            onClick={onClose}
            style={{
              ...buttonStyle,
              background: 'transparent',
              fontSize: '1.5rem',
              padding: '4px 8px',
            }}
          >
            ×
          </button>
        </div>

        <div style={contentStyle}>
          <div style={sectionStyle}>
            <label style={labelStyle}>Plot Title</label>
            <input
              type="text"
              value={localPlotData.layout?.title?.text || ''}
              onChange={handleTitleChange}
              style={inputStyle}
              placeholder="Enter plot title"
            />
          </div>

          <div style={sectionStyle}>
            <label style={labelStyle}>X Axis Title</label>
            <input
              type="text"
              value={localPlotData.layout?.xaxis?.title?.text || ''}
              onChange={(e) => handleAxisTitleChange('xaxis', e.target.value)}
              style={inputStyle}
              placeholder="Enter X axis title"
            />
          </div>

          <div style={sectionStyle}>
            <label style={labelStyle}>Y Axis Title</label>
            <input
              type="text"
              value={localPlotData.layout?.yaxis?.title?.text || ''}
              onChange={(e) => handleAxisTitleChange('yaxis', e.target.value)}
              style={inputStyle}
              placeholder="Enter Y axis title"
            />
          </div>

          {localPlotData.data && localPlotData.data.length > 0 && (
            <div style={sectionStyle}>
              <label style={labelStyle}>Trace Colors</label>
              {localPlotData.data.map((trace, index) => {
                const color = trace.line?.color || trace.marker?.color || '#1f77b4';
                return (
                  <div key={index} style={{ marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <div
                        style={{ ...colorSwatchStyle, backgroundColor: color }}
                        onClick={() => setShowColorPicker(showColorPicker === index ? null : index)}
                      />
                      <span style={{ fontSize: '0.9rem' }}>
                        {trace.name || `Trace ${index + 1}`}
                      </span>
                    </div>
                    {showColorPicker === index && (
                      <div style={{ position: 'absolute', zIndex: 1001, marginTop: '8px' }}>
                        <div
                          style={{ position: 'fixed', top: 0, right: 0, bottom: 0, left: 0 }}
                          onClick={() => setShowColorPicker(null)}
                        />
                        <ChromePicker
                          color={color}
                          onChange={(color) => handleColorChange(index, color)}
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          <div style={sectionStyle}>
            <label style={labelStyle}>Background Color</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => {
                  const newData = { ...localPlotData };
                  if (!newData.layout) newData.layout = {};
                  newData.layout.paper_bgcolor = 'white';
                  newData.layout.plot_bgcolor = 'white';
                  setLocalPlotData(newData);
                }}
                style={{
                  ...buttonStyle,
                  background: 'white',
                  border: '1px solid var(--border-color)',
                  color: 'black',
                }}
              >
                Light
              </button>
              <button
                onClick={() => {
                  const newData = { ...localPlotData };
                  if (!newData.layout) newData.layout = {};
                  newData.layout.paper_bgcolor = '#1e1e1e';
                  newData.layout.plot_bgcolor = '#1e1e1e';
                  setLocalPlotData(newData);
                }}
                style={{
                  ...buttonStyle,
                  background: '#1e1e1e',
                  color: 'white',
                }}
              >
                Dark
              </button>
            </div>
          </div>
        </div>

        <div style={{ padding: '20px', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '12px' }}>
          <button
            onClick={handleApply}
            style={{
              ...buttonStyle,
              flex: 1,
              background: 'var(--primary-color)',
              color: 'white',
            }}
          >
            Apply Changes
          </button>
          <button
            onClick={onClose}
            style={{
              ...buttonStyle,
              flex: 1,
              background: 'var(--background-color)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-color)',
            }}
          >
            Cancel
          </button>
        </div>
      </div>
    </>
  );
};

export default EditPaneSimple;