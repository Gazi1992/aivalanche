import React from 'react';
import './WelcomeScreen.css';

const WelcomeScreen = ({
  onLoadDemo,
  onLoadEngineeringDemo, onLoadBusinessDemo, onLoadFinancialMarketsDemo,
  onLoadScientificDemo, onLoadManufacturingDemo, onLoadHealthcareDemo,
  onLoadGeospatialDemo, onLoadNetworkDemo,
  isLoadingConfig
}) => {
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
        <h1 style={welcomeTitleStyle}>📊 Visualization Demo Hub</h1>
        <p style={welcomeSubtitleStyle}>
          Choose a demo below to explore different visualization types, or upload your data and chat with the AI assistant to create custom visualizations.
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
        <div style={{marginTop: '40px'}}>
          <p style={{marginBottom: '20px', fontSize: '1.1rem', fontWeight: '600', color: 'var(--text-color)'}}>
            🎯 Real-World Demo Categories:
          </p>

          <div style={{display: 'flex', gap: '15px', justifyContent: 'center'}}>
            <button
              onClick={onLoadEngineeringDemo}
              style={{
                ...demoButtonStyle,
                backgroundColor: '#3182ce',
                minWidth: '180px',
                opacity: isLoadingConfig ? 0.6 : 1,
                cursor: isLoadingConfig ? 'not-allowed' : 'pointer'
              }}
              disabled={isLoadingConfig}
              onMouseEnter={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                }
              }}
            >
              ⚙️ Engineering
            </button>

            <button
              onClick={onLoadBusinessDemo}
              style={{
                ...demoButtonStyle,
                backgroundColor: '#48bb78',
                minWidth: '180px',
                opacity: isLoadingConfig ? 0.6 : 1,
                cursor: isLoadingConfig ? 'not-allowed' : 'pointer'
              }}
              disabled={isLoadingConfig}
              onMouseEnter={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                }
              }}
            >
              💼 Business
            </button>

            <button
              onClick={onLoadFinancialMarketsDemo}
              style={{
                ...demoButtonStyle,
                backgroundColor: '#27ae60',
                minWidth: '180px',
                opacity: isLoadingConfig ? 0.6 : 1,
                cursor: isLoadingConfig ? 'not-allowed' : 'pointer'
              }}
              disabled={isLoadingConfig}
              onMouseEnter={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                }
              }}
            >
              💹 Finance
            </button>

            <button
              onClick={onLoadScientificDemo}
              style={{
                ...demoButtonStyle,
                backgroundColor: '#9b59b6',
                minWidth: '180px',
                opacity: isLoadingConfig ? 0.6 : 1,
                cursor: isLoadingConfig ? 'not-allowed' : 'pointer'
              }}
              disabled={isLoadingConfig}
              onMouseEnter={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                }
              }}
            >
              🔬 Scientific
            </button>
          </div>

          <div style={{display: 'flex', gap: '15px', justifyContent: 'center', marginTop: '15px'}}>
            <button
              onClick={onLoadManufacturingDemo}
              style={{
                ...demoButtonStyle,
                backgroundColor: '#ed8936',
                minWidth: '180px',
                opacity: isLoadingConfig ? 0.6 : 1,
                cursor: isLoadingConfig ? 'not-allowed' : 'pointer'
              }}
              disabled={isLoadingConfig}
              onMouseEnter={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                }
              }}
            >
              🏭 Manufacturing
            </button>

            <button
              onClick={onLoadHealthcareDemo}
              style={{
                ...demoButtonStyle,
                backgroundColor: '#e74c3c',
                minWidth: '180px',
                opacity: isLoadingConfig ? 0.6 : 1,
                cursor: isLoadingConfig ? 'not-allowed' : 'pointer'
              }}
              disabled={isLoadingConfig}
              onMouseEnter={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                }
              }}
            >
              🏥 Healthcare
            </button>

            <button
              onClick={onLoadGeospatialDemo}
              style={{
                ...demoButtonStyle,
                backgroundColor: '#16a085',
                minWidth: '180px',
                opacity: isLoadingConfig ? 0.6 : 1,
                cursor: isLoadingConfig ? 'not-allowed' : 'pointer'
              }}
              disabled={isLoadingConfig}
              onMouseEnter={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                }
              }}
            >
              🌍 Geospatial
            </button>

            <button
              onClick={onLoadNetworkDemo}
              style={{
                ...demoButtonStyle,
                backgroundColor: '#667eea',
                minWidth: '180px',
                opacity: isLoadingConfig ? 0.6 : 1,
                cursor: isLoadingConfig ? 'not-allowed' : 'pointer'
              }}
              disabled={isLoadingConfig}
              onMouseEnter={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                }
              }}
            >
              🌐 Network & IT
            </button>
          </div>

          <div style={{display: 'flex', gap: '15px', justifyContent: 'center', marginTop: '20px'}}>
            <button
              onClick={onLoadDemo}
              style={{
                ...demoButtonStyle,
                backgroundColor: '#718096',
                minWidth: '360px',
                opacity: isLoadingConfig ? 0.6 : 1,
                cursor: isLoadingConfig ? 'not-allowed' : 'pointer'
              }}
              disabled={isLoadingConfig}
              onMouseEnter={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoadingConfig) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                }
              }}
            >
              📊 Classic Demo (All Plot Types)
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default WelcomeScreen;