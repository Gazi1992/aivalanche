import React from 'react';
import { LabelIcon, AlignLeftIcon, AlignCenterIcon, AlignRightIcon } from '../icons';
import { 
  subsectionStyle, 
  subsectionHeaderStyle, 
  subsectionTitleStyle, 
  chevronStyle,
  inputStyle,
  checkboxStyle
} from './styles';

const TitleSubsection = ({ 
  titleExpanded, 
  setTitleExpanded,
  titleVisible,
  setTitleVisible,
  titleText,
  setTitleText,
  titleAlignment,
  setTitleAlignment,
  onBlur
}) => {

  return (
    <div style={subsectionStyle}>
      <div 
        style={subsectionHeaderStyle}
        onClick={() => setTitleExpanded(!titleExpanded)}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <LabelIcon size={20} />
          <span style={subsectionTitleStyle}>Title</span>
        </span>
        <span style={chevronStyle(titleExpanded)}>›</span>
      </div>
      
      {titleExpanded && (
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
      )}
    </div>
  );
};

export default TitleSubsection;