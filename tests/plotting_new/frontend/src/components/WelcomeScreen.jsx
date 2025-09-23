import React from 'react';
import './WelcomeScreen.css';
import './WelcomeScreen/WelcomeScreen.css';

const WelcomeScreen = ({
  onLoadDemo,
  onLoadEngineeringDemo, onLoadBusinessDemo, onLoadFinancialMarketsDemo,
  onLoadScientificDemo, onLoadManufacturingDemo, onLoadHealthcareDemo,
  onLoadGeospatialDemo, onLoadNetworkDemo, onLoadAnimationsDemo, onLoadD3Demo,
  onLoadD3AnimationsDemo,
  isLoadingConfig
}) => {
  const containerStyle = {
    display: 'flex',
    gap: '40px',
    padding: '40px',
    maxWidth: '1200px',
    margin: '0 auto',
  };

  const contentStyle = {
    flex: '1',
    paddingRight: '20px',
  };

  const welcomeTitleStyle = {
    fontSize: '2.8rem',
    marginBottom: '24px',
    color: 'var(--text-color)',
    fontWeight: '600',
  };

  const welcomeSubtitleStyle = {
    fontSize: '1.15rem',
    color: 'var(--text-secondary)',
    lineHeight: '1.6',
    marginBottom: '32px',
  };

  const welcomeInstructionsStyle = {
    fontSize: '0.95rem',
    color: 'var(--text-secondary)',
    backgroundColor: 'var(--card-background-color)',
    padding: '24px',
    borderRadius: '12px',
    border: '1px solid var(--border-color)',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
  };

  const demoPanelStyle = {
    width: '280px',
    backgroundColor: 'var(--card-background-color)',
    padding: '24px',
    borderRadius: '12px',
    border: '1px solid var(--border-color)',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
  };

  const demoPanelTitleStyle = {
    fontSize: '1.2rem',
    fontWeight: '600',
    marginBottom: '20px',
    color: 'var(--text-color)',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  };

  const demoButtonStyle = {
    padding: '10px 16px',
    fontSize: '0.95rem',
    backgroundColor: 'var(--primary-color)',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    width: '100%',
    textAlign: 'left',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '8px',
  };

  const demoCategoryStyle = {
    fontSize: '0.85rem',
    fontWeight: '600',
    color: 'var(--text-secondary)',
    marginTop: '16px',
    marginBottom: '8px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
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
      
      <div style={containerStyle}>
        <div style={contentStyle}>
          <h1 style={welcomeTitleStyle}>📊 Visualization Demo Hub</h1>
          <p style={welcomeSubtitleStyle}>
            Create stunning data visualizations with our AI-powered platform. Upload your data and use natural language to generate interactive charts, or explore our demo collection.
          </p>

          <div style={welcomeInstructionsStyle}>
            <h3 style={{marginTop: '0', marginBottom: '16px', fontSize: '1.1rem', fontWeight: '600'}}>
              🚀 Getting Started
            </h3>
            <ol style={{margin: '0', paddingLeft: '24px', lineHeight: '1.8'}}>
              <li>Upload a data file using the 📎 button in the chat</li>
              <li>Ask the AI to create visualizations in natural language</li>
              <li>Customize and refine your plots interactively</li>
              <li>Export your visualizations in multiple formats</li>
            </ol>
          </div>

          <div style={{marginTop: '32px', padding: '24px', backgroundColor: 'var(--bg-secondary)', borderRadius: '12px'}}>
            <h3 style={{marginTop: '0', marginBottom: '16px', fontSize: '1.1rem', fontWeight: '600'}}>
              💡 Pro Tips
            </h3>
            <ul style={{margin: '0', paddingLeft: '24px', lineHeight: '1.8', fontSize: '0.95rem', color: 'var(--text-secondary)'}}>
              <li>Use specific chart types in your requests (e.g., "Create a scatter plot")</li>
              <li>Mention the columns you want to visualize</li>
              <li>Ask for specific customizations like colors, labels, or themes</li>
              <li>Try animation demos for dynamic data visualization</li>
            </ul>
          </div>
        </div>

        <div style={demoPanelStyle}>
          <div style={demoPanelTitleStyle}>
            <span>🎯</span>
            <span>Demo Gallery</span>
          </div>

          <div className="demo-category">Industry Demos</div>

          <button
            className="demo-button"
            onClick={onLoadEngineeringDemo}
            disabled={isLoadingConfig}
          >
            ⚙️ Engineering
          </button>

          <button
            className="demo-button"
            onClick={onLoadBusinessDemo}
            disabled={isLoadingConfig}
          >
            💼 Business
          </button>

          <button
            className="demo-button"
            onClick={onLoadFinancialMarketsDemo}
            disabled={isLoadingConfig}
          >
            💹 Finance
          </button>

          <button
            className="demo-button"
            onClick={onLoadScientificDemo}
            disabled={isLoadingConfig}
          >
            🔬 Scientific
          </button>

          <button
            className="demo-button"
            onClick={onLoadManufacturingDemo}
            disabled={isLoadingConfig}
          >
            🏭 Manufacturing
          </button>

          <button
            className="demo-button"
            onClick={onLoadHealthcareDemo}
            disabled={isLoadingConfig}
          >
            🏥 Healthcare
          </button>

          <button
            className="demo-button"
            onClick={onLoadGeospatialDemo}
            disabled={isLoadingConfig}
          >
            🌍 Geospatial
          </button>

          <button
            className="demo-button"
            onClick={onLoadNetworkDemo}
            disabled={isLoadingConfig}
          >
            🌐 Network & IT
          </button>

          <div className="demo-category">Interactive Demos</div>

          <button
            className="demo-button"
            onClick={onLoadAnimationsDemo}
            disabled={isLoadingConfig}
          >
            ✨ Plotly Animations
          </button>

          <button
            className="demo-button"
            onClick={onLoadD3Demo}
            disabled={isLoadingConfig}
          >
            🎨 D3 Visualizations
          </button>

          <button
            className="demo-button"
            onClick={onLoadD3AnimationsDemo}
            disabled={isLoadingConfig}
          >
            🎬 D3 Animations
          </button>

          <div className="demo-category">Complete Collection</div>

          <button
            className="demo-button"
            onClick={onLoadDemo}
            disabled={isLoadingConfig}
          >
            📊 All Plot Types
          </button>
        </div>
      </div>
    </>
  );
};

export default WelcomeScreen;