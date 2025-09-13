/**
 * Loading Spinner Component
 * Displays a loading indicator with optional message
 */
import React from 'react';

const LoadingSpinner = ({ message = 'Loading...', size = 40 }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px',
      gap: '20px'
    }}>
      <div 
        className="loading-spinner"
        style={{
          width: `${size}px`,
          height: `${size}px`,
          border: '4px solid var(--border-color, #e0e0e0)',
          borderTop: '4px solid var(--primary-color, #3b82f6)',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}
      />
      {message && (
        <div style={{
          color: 'var(--text-secondary, #6b7280)',
          fontSize: '14px'
        }}>
          {message}
        </div>
      )}
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default LoadingSpinner;