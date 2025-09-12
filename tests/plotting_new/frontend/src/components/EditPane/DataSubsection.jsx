import React, { useState, useEffect } from 'react';
import { DataIcon, FillIcon, BorderIcon } from '../icons';
import ColorPickerIcon from './ColorPickerIcon';
import { 
  subsectionStyle, 
  subsectionHeaderStyle, 
  subsectionTitleStyle, 
  chevronStyle,
  inputStyle,
  selectStyle,
  labelStyle,
  dataContainerStyle,
  rowStyle,
  traceOptionsContainerStyle,
  traceSectionHeaderStyle,
  flexRowStyle,
  flexGroupStyle,
  smallInputStyle,
  dropdownTriggerStyle,
  dropdownStyle,
  dropdownItemStyle
} from './styles';

// Constants
const LINE_STYLES = [
  { value: 'solid', label: 'Solid' },
  { value: 'dash', label: 'Dashed' },
  { value: 'dot', label: 'Dotted' },
  { value: 'dashdot', label: 'Dash Dot' }
];

const SYMBOLS = [
  { value: null, label: 'None' },
  { value: 'circle', label: 'Circle' },
  { value: 'square', label: 'Square' },
  { value: 'diamond', label: 'Diamond' },
  { value: 'cross', label: 'Cross' },
  { value: 'x', label: 'X' },
  { value: 'triangle-up', label: 'Triangle Up' },
  { value: 'triangle-down', label: 'Triangle Down' },
  { value: 'star', label: 'Star' },
  { value: 'hexagon', label: 'Hexagon' }
];

// Helper components
const LineStylePreview = ({ style }) => (
  <svg width="60" height="10">
    <line
      x1="0" y1="5" x2="60" y2="5"
      stroke="var(--text-color)"
      strokeWidth="2"
      strokeDasharray={
        style === 'dash' ? '8,4' :
        style === 'dot' ? '2,4' :
        style === 'dashdot' ? '8,4,2,4' :
        'none'
      }
    />
  </svg>
);

const SymbolPreview = ({ symbol }) => (
  <svg width="24" height="24" viewBox="0 0 24 24">
    {symbol === 'circle' && (
      <circle cx="12" cy="12" r="6" fill="var(--text-color)" />
    )}
    {symbol === 'square' && (
      <rect x="6" y="6" width="12" height="12" fill="var(--text-color)" />
    )}
    {symbol === 'diamond' && (
      <path d="M12 2 L22 12 L12 22 L2 12 Z" fill="var(--text-color)" />
    )}
    {symbol === 'cross' && (
      <path d="M12 6 L12 18 M6 12 L18 12" stroke="var(--text-color)" strokeWidth="2" fill="none" />
    )}
    {symbol === 'x' && (
      <path d="M6 6 L18 18 M18 6 L6 18" stroke="var(--text-color)" strokeWidth="2" fill="none" />
    )}
    {symbol === 'triangle-up' && (
      <path d="M12 6 L18 16 L6 16 Z" fill="var(--text-color)" />
    )}
    {symbol === 'triangle-down' && (
      <path d="M12 18 L18 8 L6 8 Z" fill="var(--text-color)" />
    )}
    {symbol === 'star' && (
      <path d="M12 2 L14.5 9 L22 9 L16 14 L18.5 21 L12 16 L5.5 21 L8 14 L2 9 L9.5 9 Z" fill="var(--text-color)" />
    )}
    {symbol === 'hexagon' && (
      <path d="M12 4 L18 8 L18 16 L12 20 L6 16 L6 8 Z" fill="var(--text-color)" />
    )}
    {symbol === null && (
      <text x="12" y="16" textAnchor="middle" fontSize="12" fill="var(--text-color)">None</text>
    )}
  </svg>
);

const StyleDropdown = ({ 
  currentStyle, 
  styles, 
  isOpen, 
  setIsOpen, 
  onSelect, 
  renderPreview 
}) => {
  return (
    <div style={{ position: 'relative' }}>
      <div style={dropdownTriggerStyle} onClick={() => setIsOpen(!isOpen)}>
        {renderPreview(currentStyle)}
      </div>
      {isOpen && (
        <div
          style={dropdownStyle}
          onMouseLeave={() => setIsOpen(false)}
        >
          {styles.map(style => (
            <div
              key={style.value || 'none'}
              style={dropdownItemStyle}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--background-secondary)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              onClick={() => {
                onSelect(style.value);
                setIsOpen(false);
              }}
            >
              {renderPreview(style.value || style)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const DataSubsection = ({ 
  dataExpanded, 
  setDataExpanded,
  traces = [],
  selectedTraceIndex = 0,
  setSelectedTraceIndex,
  traceProperties = {},
  updateTraceProperty,
  onBlur
}) => {
  const [showLineStyleDropdown, setShowLineStyleDropdown] = useState(false);
  const [showSymbolDropdown, setShowSymbolDropdown] = useState(false);
  
  // Ensure we have valid data
  const safeSelectedIndex = Math.min(selectedTraceIndex, traces.length - 1);
  const currentTrace = traces[safeSelectedIndex] || {};
  const currentProps = traceProperties ? (traceProperties[safeSelectedIndex] || {}) : {};
  
  // Determine trace type
  const isLineTrace = currentTrace?.mode?.includes('lines');
  const isScatterTrace = currentTrace?.mode?.includes('markers');
  
  // Get current values with defaults
  const getLineStyle = () => currentProps.lineStyle || currentTrace?.line?.dash || 'solid';
  const getLineWidth = () => currentProps.lineWidth ?? currentTrace?.line?.width ?? 2;
  const getLineColor = () => currentProps.color || currentTrace?.line?.color || '#1f77b4';
  
  const getSymbol = () => currentProps.symbol ?? currentTrace?.marker?.symbol ?? (isScatterTrace ? 'circle' : null);
  const getSymbolSize = () => currentProps.symbolSize ?? currentTrace?.marker?.size ?? (isScatterTrace ? 6 : 0);
  const getSymbolColor = () => currentProps.symbolColor || currentTrace?.marker?.color || '#1f77b4';
  const getSymbolBorderColor = () => currentProps.symbolBorderColor || currentTrace?.marker?.line?.color || '#000000';

  return (
    <div style={subsectionStyle}>
      <div 
        style={subsectionHeaderStyle}
        onClick={() => setDataExpanded(!dataExpanded)}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <DataIcon size={20} />
          <span style={subsectionTitleStyle}>Data</span>
        </span>
        <span style={chevronStyle(dataExpanded)}>›</span>
      </div>
      
      {dataExpanded && (
        <div style={dataContainerStyle}>
          {/* Trace selector - only show if more than one trace */}
          {traces.length > 1 && (
            <div style={rowStyle}>
              <label style={labelStyle}>Trace</label>
              <select
                value={safeSelectedIndex}
                onChange={(e) => setSelectedTraceIndex && setSelectedTraceIndex(Number(e.target.value))}
                style={selectStyle}
              >
                {traces.map((trace, index) => (
                  <option key={index} value={index}>
                    {trace.name || `Trace ${index + 1}`}
                  </option>
                ))}
              </select>
            </div>
          )}
          
          {/* Trace options container */}
          <div style={traceOptionsContainerStyle}>
            {/* Trace name */}
            <div style={rowStyle}>
              <label style={labelStyle}>Name</label>
              <input
                type="text"
                value={currentProps.name || currentTrace?.name || ''}
                onChange={(e) => updateTraceProperty && updateTraceProperty(safeSelectedIndex, 'name', e.target.value)}
                onBlur={onBlur}
                style={{ ...inputStyle, backgroundColor: '#ECEEF0' }}
                placeholder="Trace name"
              />
            </div>
            
            {/* Line properties - only show if trace has lines */}
            {isLineTrace && (
              <>
                <div style={traceSectionHeaderStyle}>Line Appearance</div>
                <div style={rowStyle}>
                  <label style={labelStyle}>Style</label>
                  <div style={flexRowStyle}>
                    <div style={flexGroupStyle}>
                      <input
                        type="number"
                        value={getLineWidth()}
                        onChange={(e) => updateTraceProperty && updateTraceProperty(safeSelectedIndex, 'lineWidth', Number(e.target.value))}
                        onBlur={onBlur}
                        style={smallInputStyle}
                        min="0"
                        max="10"
                        step="0.5"
                        title="Line width"
                      />
                      <span style={{ color: 'var(--text-secondary)' }}>px</span>
                    </div>
                    
                    <StyleDropdown
                      currentStyle={getLineStyle()}
                      styles={LINE_STYLES}
                      isOpen={showLineStyleDropdown}
                      setIsOpen={setShowLineStyleDropdown}
                      onSelect={(value) => updateTraceProperty && updateTraceProperty(safeSelectedIndex, 'lineStyle', value)}
                      renderPreview={(style) => <LineStylePreview style={style} />}
                    />
                    
                    <ColorPickerIcon
                      icon={FillIcon}
                      color={getLineColor()}
                      onChange={(e) => updateTraceProperty && updateTraceProperty(safeSelectedIndex, 'color', e.target.value)}
                      title="Line color"
                    />
                  </div>
                </div>
                
                {/* Symbol options for line traces */}
                <div style={traceSectionHeaderStyle}>Marker Options</div>
                <div style={rowStyle}>
                  <label style={labelStyle}>Symbol</label>
                  <div style={flexRowStyle}>
                    <div style={flexGroupStyle}>
                      <input
                        type="number"
                        value={getSymbolSize()}
                        onChange={(e) => updateTraceProperty && updateTraceProperty(safeSelectedIndex, 'symbolSize', Number(e.target.value))}
                        onBlur={onBlur}
                        style={smallInputStyle}
                        min="0"
                        max="20"
                        step="1"
                        title="Symbol size"
                      />
                      <span style={{ color: 'var(--text-secondary)' }}>px</span>
                    </div>
                    
                    <StyleDropdown
                      currentStyle={getSymbol()}
                      styles={SYMBOLS}
                      isOpen={showSymbolDropdown}
                      setIsOpen={setShowSymbolDropdown}
                      onSelect={(value) => updateTraceProperty && updateTraceProperty(safeSelectedIndex, 'symbol', value)}
                      renderPreview={(symbol) => <SymbolPreview symbol={symbol} />}
                    />
                    
                    <ColorPickerIcon
                      icon={FillIcon}
                      color={getSymbolColor()}
                      onChange={(e) => updateTraceProperty && updateTraceProperty(safeSelectedIndex, 'symbolColor', e.target.value)}
                      title="Symbol fill color"
                    />
                    
                    <ColorPickerIcon
                      icon={BorderIcon}
                      color={getSymbolBorderColor()}
                      onChange={(e) => updateTraceProperty && updateTraceProperty(safeSelectedIndex, 'symbolBorderColor', e.target.value)}
                      title="Symbol border color"
                    />
                  </div>
                </div>
              </>
            )}
            
            {/* Scatter trace properties */}
            {isScatterTrace && !isLineTrace && (
              <>
                <div style={traceSectionHeaderStyle}>Marker Appearance</div>
                <div style={rowStyle}>
                  <label style={labelStyle}>Symbol</label>
                  <div style={flexRowStyle}>
                    <div style={flexGroupStyle}>
                      <input
                        type="number"
                        value={getSymbolSize()}
                        onChange={(e) => updateTraceProperty && updateTraceProperty(safeSelectedIndex, 'symbolSize', Number(e.target.value))}
                        onBlur={onBlur}
                        style={smallInputStyle}
                        min="0"
                        max="50"
                        step="1"
                        title="Symbol size"
                      />
                      <span style={{ color: 'var(--text-secondary)' }}>px</span>
                    </div>
                    
                    <StyleDropdown
                      currentStyle={getSymbol()}
                      styles={SYMBOLS}
                      isOpen={showSymbolDropdown}
                      setIsOpen={setShowSymbolDropdown}
                      onSelect={(value) => updateTraceProperty && updateTraceProperty(safeSelectedIndex, 'symbol', value)}
                      renderPreview={(symbol) => <SymbolPreview symbol={symbol} />}
                    />
                    
                    <ColorPickerIcon
                      icon={FillIcon}
                      color={getSymbolColor()}
                      onChange={(e) => updateTraceProperty && updateTraceProperty(safeSelectedIndex, 'symbolColor', e.target.value)}
                      title="Symbol fill color"
                    />
                    
                    <ColorPickerIcon
                      icon={BorderIcon}
                      color={getSymbolBorderColor()}
                      onChange={(e) => updateTraceProperty && updateTraceProperty(safeSelectedIndex, 'symbolBorderColor', e.target.value)}
                      title="Symbol border color"
                    />
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DataSubsection;