import React from 'react';
import './WelcomeScreen.css';

const WelcomeScreen = ({ onLoadDemo, isLoadingConfig }) => {
  const welcomeStyle = {
    textAlign: 'center',
    padding: '60px',
    maxWidth: '600px',
  };

  const welcomeTitleStyle = {
    fontSize: '2.5rem',
    marginBottom: '20px',
    color: 'var(--text-color)',
  };

  const welcomeSubtitleStyle = {
    fontSize: '1.2rem',
    color: 'var(--text-secondary)',
    lineHeight: '1.6',
    marginBottom: '40px',
  };

  const welcomeInstructionsStyle = {
    fontSize: '1rem',
    color: 'var(--text-secondary)',
    backgroundColor: 'var(--card-background-color)',
    padding: '20px',
    borderRadius: '8px',
    border: '1px solid var(--border-color)',
  };

  const demoButtonStyle = {
    padding: '12px 24px',
    fontSize: '1rem',
    backgroundColor: 'var(--primary-color)',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
  };

  return (
    <>
      {isLoadingConfig && (
        <div className="loading-overlay">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <div className="loading-text">
              Loading visualization...
            </div>
          </div>
        </div>
      )}
      
      <div style={welcomeStyle}>
        <h1 style={welcomeTitleStyle}>📊 Welcome to Data Visualization Studio</h1>
        <p style={welcomeSubtitleStyle}>
          Start by uploading your data and chatting with the AI assistant to create stunning visualizations.
        </p>
        <div style={welcomeInstructionsStyle}>
          <p style={{marginBottom: '10px'}}>
            <strong>Getting Started:</strong>
          </p>
          <ol style={{textAlign: 'left', margin: '0', paddingLeft: '20px'}}>
            <li>Upload a data file using the 📎 button in the chat</li>
            <li>Ask the AI to create visualizations</li>
            <li>Customize and refine your plots interactively</li>
          </ol>
        </div>
        <div style={{marginTop: '30px'}}>
          <button
            onClick={onLoadDemo}
            style={demoButtonStyle}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
            }}
          >
            Load Demo Visualizations
          </button>
        </div>
      </div>
    </>
  );
};

export default WelcomeScreen;