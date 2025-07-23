import React from 'react';
import { LabelIcon, AlignLeftIcon, AlignCenterIcon, AlignRightIcon } from '../icons';
import { 
  subsectionStyle, 
  subsectionHeaderStyle, 
  subsectionTitleStyle, 
  chevronStyle,
  inputStyle,
  labelStyle,
  checkboxStyle
} from './styles';

const LabelsSubsection = ({ 
  labelsExpanded, 
  setLabelsExpanded,
  titleVisible,
  setTitleVisible,
  titleText,
  setTitleText,
  titleAlignment,
  setTitleAlignment,
  xAxisLabelVisible,
  setXAxisLabelVisible,
  xAxisLabel,
  setXAxisLabel,
  yAxisLabelVisible,
  setYAxisLabelVisible,
  yAxisLabel,
  setYAxisLabel,
  xAxisTicksVisible,
  setXAxisTicksVisible,
  yAxisTicksVisible,
  setYAxisTicksVisible,
  onBlur
}) => {
  const sectionStyle = {
    marginBottom: '12px'
  };
  
  const sectionTitleStyle = {
    fontSize: '0.85rem',
    fontWeight: '600',
    color: 'var(--text-color)',
    marginBottom: '6px'
  };
  
  const itemStyle = {
    display: 'grid',
    gridTemplateColumns: '20px 1fr',
    gap: '8px',
    alignItems: 'center',
    marginBottom: '6px'
  };
  
  const doubleItemStyle = {
    display: 'grid',
    gridTemplateColumns: '50px 1fr 50px 1fr',
    gap: '8px',
    alignItems: 'center',
    marginBottom: '6px'
  };

  return (
    <div style={subsectionStyle}>
      <div 
        style={subsectionHeaderStyle}
        onClick={() => setLabelsExpanded(!labelsExpanded)}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <LabelIcon size={20} />
          <span style={subsectionTitleStyle}>Labels</span>
        </span>
        <span style={chevronStyle(labelsExpanded)}>›</span>
      </div>
      
      {labelsExpanded && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {/* Title Section */}
          <div style={sectionStyle}>
            <div style={sectionTitleStyle}>Title</div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input
                type="checkbox"
                checked={titleVisible}
                onChange={(e) => setTitleVisible(e.target.checked)}
                style={checkboxStyle}
              />
              <input
                type="text"
                value={titleText}
                onChange={(e) => setTitleText(e.target.value)}
                onBlur={onBlur}
                style={{ ...inputStyle, flex: 1, minWidth: 0 }}
                placeholder="Enter title"
                disabled={!titleVisible}
              />
              <button
                onClick={() => setTitleAlignment('left')}
                style={{
                  padding: '4px',
                  border: '1px solid var(--border-color)',
                  borderRadius: '4px',
                  background: titleAlignment === 'left' ? 'var(--primary-color)' : 'var(--background-color)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title="Align left"
              >
                <AlignLeftIcon size={16} color={titleAlignment === 'left' ? 'white' : 'var(--text-color)'} />
              </button>
              <button
                onClick={() => setTitleAlignment('center')}
                style={{
                  padding: '4px',
                  border: '1px solid var(--border-color)',
                  borderRadius: '4px',
                  background: titleAlignment === 'center' ? 'var(--primary-color)' : 'var(--background-color)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title="Align center"
              >
                <AlignCenterIcon size={16} color={titleAlignment === 'center' ? 'white' : 'var(--text-color)'} />
              </button>
              <button
                onClick={() => setTitleAlignment('right')}
                style={{
                  padding: '4px',
                  border: '1px solid var(--border-color)',
                  borderRadius: '4px',
                  background: titleAlignment === 'right' ? 'var(--primary-color)' : 'var(--background-color)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title="Align right"
              >
                <AlignRightIcon size={16} color={titleAlignment === 'right' ? 'white' : 'var(--text-color)'} />
              </button>
            </div>
          </div>
          
          {/* Axis Labels and Ticks Section */}
          <div style={sectionStyle}>
            <div style={sectionTitleStyle}>Axis Properties</div>
            <div style={{
              display: 'grid',
              gridTemplateColumns: '60px minmax(0, 1fr) minmax(0, 1fr)',
              gap: '8px',
              columnGap: '16px',
              alignItems: 'center'
            }}>
              {/* Headers */}
              <div></div>
              <div style={{ textAlign: 'left', fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-color)' }}>X-Axis</div>
              <div style={{ textAlign: 'left', fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-color)' }}>Y-Axis</div>
              
              {/* Labels Row */}
              <div style={{ textAlign: 'left', fontSize: '0.85rem', display: 'flex', alignItems: 'center' }}>Label</div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', minWidth: 0 }}>
                <input
                  type="checkbox"
                  checked={xAxisLabelVisible}
                  onChange={(e) => setXAxisLabelVisible(e.target.checked)}
                  style={checkboxStyle}
                />
                <input
                  type="text"
                  value={xAxisLabel}
                  onChange={(e) => setXAxisLabel(e.target.value)}
                  onBlur={onBlur}
                  style={{ ...inputStyle, flex: 1, minWidth: 0 }}
                  placeholder="X-axis label"
                  disabled={!xAxisLabelVisible}
                />
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', minWidth: 0 }}>
                <input
                  type="checkbox"
                  checked={yAxisLabelVisible}
                  onChange={(e) => setYAxisLabelVisible(e.target.checked)}
                  style={checkboxStyle}
                />
                <input
                  type="text"
                  value={yAxisLabel}
                  onChange={(e) => setYAxisLabel(e.target.value)}
                  onBlur={onBlur}
                  style={{ ...inputStyle, flex: 1, minWidth: 0 }}
                  placeholder="Y-axis label"
                  disabled={!yAxisLabelVisible}
                />
              </div>
              
              {/* Ticks Row */}
              <div style={{ textAlign: 'left', fontSize: '0.85rem', display: 'flex', alignItems: 'center' }}>Ticks</div>
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <input
                  type="checkbox"
                  checked={xAxisTicksVisible}
                  onChange={(e) => setXAxisTicksVisible(e.target.checked)}
                  style={checkboxStyle}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <input
                  type="checkbox"
                  checked={yAxisTicksVisible}
                  onChange={(e) => setYAxisTicksVisible(e.target.checked)}
                  style={checkboxStyle}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LabelsSubsection;