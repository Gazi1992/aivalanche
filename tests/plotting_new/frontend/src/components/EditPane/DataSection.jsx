import React from 'react';
import { 
  sectionStyle, 
  sectionHeaderStyle, 
  sectionContentStyle,
  chevronStyle 
} from './styles';

const DataSection = ({ dataExpanded, setDataExpanded }) => {
  return (
    <div style={sectionStyle}>
      <div 
        style={sectionHeaderStyle}
        onClick={() => setDataExpanded(!dataExpanded)}
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--background-color)'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
      >
        <span style={{ fontWeight: '600', color: 'var(--text-color)' }}>Data</span>
        <span style={chevronStyle(dataExpanded)}>›</span>
      </div>
      
      {dataExpanded && (
        <div style={sectionContentStyle}>
          <p style={{ margin: 0, color: 'var(--text-color)', opacity: 0.7, fontSize: '0.85rem' }}>
            Data editing options will be available here
          </p>
        </div>
      )}
    </div>
  );
};

export default DataSection;