import React from 'react';
import './WelcomeScreen.css';
import './WelcomeScreen/WelcomeScreen.css';

const WelcomeScreen = ({
  onLoadDemo,
  isLoadingConfig
}) => {
  const [hoveredCategory, setHoveredCategory] = React.useState(null);
  const [demoCategories, setDemoCategories] = React.useState([]);
  const [isLoadingCategories, setIsLoadingCategories] = React.useState(true);

  // Fetch demo categories from backend
  React.useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/demo-categories');
        const data = await response.json();
        setDemoCategories(data.categories || []);
      } catch (error) {
        console.error('Failed to load demo categories:', error);
        // Show empty state if API fails
        setDemoCategories([]);
      } finally {
        setIsLoadingCategories(false);
      }
    };
    fetchCategories();
  }, []);

  // Show loading state while fetching categories
  if (isLoadingCategories) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div className="loading-spinner"></div>
          <div style={{ marginTop: '20px', color: 'var(--text-secondary)' }}>
            Loading demo categories...
          </div>
        </div>
      </div>
    );
  }
  const containerStyle = {
    padding: '10px',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    boxSizing: 'border-box',
  };

  const welcomeTitleStyle = {
    fontSize: '1.8rem',
    marginBottom: '8px',
    color: 'var(--text-color)',
    fontWeight: '600',
    textAlign: 'center',
  };

  const welcomeSubtitleStyle = {
    fontSize: '1.1rem',
    color: 'var(--text-secondary)',
    lineHeight: '1.3',
    marginBottom: '12px',
    textAlign: 'center',
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
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          flex: 1
        }}>
          <h1 style={welcomeTitleStyle}>📊 Visualization Demo Gallery</h1>
          <p style={welcomeSubtitleStyle}>
            Explore real-world data visualizations. Click any category to load demo.
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, minmax(260px, 1fr))',
            gap: '12px',
            marginTop: '20px',
            width: '100%',
            maxWidth: '1400px'
          }}>
            {demoCategories.map(category => (
            <div
              key={category.id}
              style={{
                backgroundColor: 'var(--card-background-color)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '12px',
                cursor: isLoadingConfig ? 'not-allowed' : 'pointer',
                transition: 'all 0.3s ease',
                opacity: isLoadingConfig ? 0.6 : 1,
                position: 'relative',
                overflow: 'hidden',
                height: '140px',
                minHeight: '140px',
                minWidth: '260px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center'
              }}
              onMouseEnter={(e) => {
                if (!isLoadingConfig) {
                  e.currentTarget.style.boxShadow = '0 6px 20px rgba(0,0,0,0.12)';
                  e.currentTarget.style.borderColor = category.color;
                  setHoveredCategory(category.id);
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.borderColor = 'var(--border-color)';
                setHoveredCategory(null);
              }}
            >
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '2px',
                backgroundColor: category.color,
                opacity: 0.8
              }} />

              {/* Card header - centered and disappears on hover */}
              {hoveredCategory !== category.id && (
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '100%',
                  gap: '8px',
                  transition: 'opacity 0.3s ease',
                  animation: hoveredCategory === category.id ? 'fadeOut 0.3s ease' : 'fadeIn 0.3s ease'
                }}>
                  <div style={{
                    fontSize: '2rem',
                    transition: 'all 0.3s ease'
                  }}>
                    {category.name.split(' ')[0]}
                  </div>

                  <div style={{ textAlign: 'center' }}>
                    <h3 style={{
                      fontSize: '1.15rem',
                      margin: 0,
                      color: 'var(--text-color)',
                      fontWeight: '600',
                      lineHeight: '1.2'
                    }}>
                      {category.name.split(' ').slice(1).join(' ') || category.name.split(' ')[0].substring(2)}
                    </h3>

                    <p style={{
                      fontSize: '0.9rem',
                      color: 'var(--text-secondary)',
                      margin: '2px 0 0 0',
                      lineHeight: '1.2'
                    }}>
                      {category.description}
                    </p>
                  </div>
                </div>
              )}

              {/* Subcategory list - appears inside card on hover */}
              {hoveredCategory === category.id && category.demos.length > 0 && (
                <div style={{
                  animation: 'fadeIn 0.3s ease',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  width: '100%'
                }}>
                  {category.demos.map((demo, index) => (
                    <div
                      key={demo.id}
                      onClick={(e) => {
                        e.stopPropagation();
                        onLoadDemo(demo.id);
                      }}
                      style={{
                        padding: '6px 8px',
                        marginBottom: index < category.demos.length - 1 ? '4px' : 0,
                        borderRadius: '6px',
                        cursor: 'pointer',
                        backgroundColor: 'rgba(0,0,0,0.03)',
                        transition: 'all 0.2s',
                        borderLeft: `3px solid ${category.color}`,
                        marginLeft: '4px'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'rgba(139, 146, 232, 0.15)';
                        e.currentTarget.style.transform = 'translateX(4px)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.03)';
                        e.currentTarget.style.transform = 'translateX(0)';
                      }}
                    >
                      <div style={{
                        fontSize: '0.95rem',
                        fontWeight: '500',
                        color: 'var(--text-color)',
                        marginBottom: '1px'
                      }}>
                        {demo.name}
                      </div>
                      <div style={{
                        fontSize: '0.8rem',
                        color: 'var(--text-secondary)',
                        lineHeight: '1.2'
                      }}>
                        {demo.description}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

export default WelcomeScreen;