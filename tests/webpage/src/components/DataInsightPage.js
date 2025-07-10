import React from 'react';
import { Link } from 'react-router-dom';
import { Carousel } from 'react-responsive-carousel';
import "react-responsive-carousel/lib/styles/carousel.min.css";
import './LearnMorePages.css';
import './Hero.css'; // For CTA button styles

// Placeholder styles (can be shared or moved to a CSS file)
const pageStyle = {
  padding: '100px 20px 20px',
  minHeight: '100vh',
  backgroundColor: 'var(--charcoal-bg)',
  color: 'var(--white-text-85)'
};

const DataInsightPage = () => {

  const reportTemplates = [
    { id: 1, cover: 'Report Cover 1 Preview', filledFields: 'Auto-filled fields for Report 1' },
    { id: 2, cover: 'Report Cover 2 Preview', filledFields: 'Auto-filled fields for Report 2' },
    { id: 3, cover: 'Report Cover 3 Preview', filledFields: 'Auto-filled fields for Report 3' },
  ];

  const integrations = ['LaTeX', 'Confluence', 'Microsoft Word', 'Google Docs', 'Jupyter'];

  return (
    <div className="learn-more-page">
      {/* 1. Hero Section */}
      <section className="lm-hero-section" style={{ minHeight: '70vh' }}> {/* Slightly less vh than Labflow */}
        <div className="lm-hero-content" style={{textAlign: 'center', width: '100%'}}> {/* Centered hero content */}
          <h1>Insight at the Speed of Thought.</h1>
          <p className="hero-subtitle" style={{fontSize: '22px', maxWidth: '700px', margin: '0 auto 30px auto'}}>
            Transform raw data into actionable intelligence. DataInsight AI offers conversational analytics, advanced visualizations, and automated reporting, all powered by cutting-edge LLMs.
          </p>
          {/* Animated orbiting datapoints placeholder - could be a separate component or CSS animation */}
          <div className="lm-visual-placeholder" style={{height: '150px', width: '60%', margin: '0 auto 30px auto', borderStyle: 'solid', borderColor: 'var(--electric-cyan-accent)'}}>
            Animated orbiting datapoints visual placeholder
          </div>
          <Link to="/try-data-insight-demo" className="cta-button cta-button-primary">Try the Interactive Demo</Link>
        </div>
      </section>

      <div className="lm-container">
        {/* 2. Live Playground */}
        <section className="lm-section">
          <h2 className="lm-section-title">Experience It Live: Your Data, Your Insights</h2>
          <div className="lm-visual-placeholder" style={{ minHeight: '400px', display: 'flex', gap: '20px' }}>
            <div style={{flex:3, background: 'rgba(0,0,0,0.2)', padding:'15px', borderRadius:'5px'}}>Embedded Code Editor / Chat Interface Placeholder</div>
            <div style={{flex:1, background: 'rgba(0,0,0,0.2)', padding:'15px', borderRadius:'5px'}}>Dataset Dropdown / Controls Placeholder</div>
          </div>
          <p style={{textAlign:'center', marginTop:'10px', fontSize:'14px'}}>Note: Hidden API key for demo purposes.</p>
        </section>

        {/* 3. Visual Gallery */}
        <section className="lm-section">
          <h2 className="lm-section-title">Visualize Everything: From Simple Plots to Complex Heatmaps</h2>
          <div className="lm-visual-placeholder" style={{ minHeight: '350px' }}>
            Masonry grid of plot screenshots/GIFs (e.g., line, heatmap, parallel-coords). Lightbox with JSON spec + export option on click. (Placeholder)
          </div>
        </section>

        {/* 4. Report Templates Slider */}
        <section className="lm-section">
          <h2 className="lm-section-title">Automated, Customizable Report Templates</h2>
          <Carousel showThumbs={false} showStatus={false} infiniteLoop useKeyboardArrows autoPlay interval={6000} stopOnHover={true}>
            {reportTemplates.map(template => (
              <div key={template.id} className="lm-card" style={{margin: '0 20px 40px', textAlign: 'center', background: 'rgba(255,255,255,0.08)', minHeight: '250px'}}>
                {/* Basic flip card simulation - actual flip would need more complex CSS/JS */}
                <h3>{template.cover}</h3>
                <p><em>Hover/Click to see auto-filled fields (simulated)</em></p>
                <p style={{marginTop: '20px', color: 'var(--lilac-violet-accent)'}}>{template.filledFields}</p>
              </div>
            ))}
          </Carousel>
        </section>

        {/* 5. Technical Spec */}
        <section className="lm-section">
          <h2 className="lm-section-title">Under the Hood: Powerful & Transparent</h2>
          <div className="lm-cards-grid" style={{gridTemplateColumns: '1fr 1fr'}}>
            <div className="lm-card">
              <h3>Supported Statistical Tests</h3>
              <div className="lm-visual-placeholder" style={{minHeight: '150px'}}>Table of statistical tests Placeholder</div>
            </div>
            <div className="lm-card">
              <h3>LLM-Generated Code Examples</h3>
              <div className="lm-visual-placeholder" style={{minHeight: '150px'}}>Expandable Pandas code example Placeholder</div>
            </div>
          </div>
        </section>

        {/* 6. Integrations */}
        <section className="lm-section">
          <h2 className="lm-section-title">Seamlessly Fits Your Workflow</h2>
          <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '20px', flexWrap: 'wrap'}}>
            {integrations.map(logo => (
              <div key={logo} style={{background: 'rgba(255,255,255,0.1)', padding: '15px 25px', borderRadius: '5px', fontSize: '16px', color: 'var(--electric-cyan-accent)'}}>
                {logo} (Logo)
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* 7. Sticky CTA (Placeholder - Actual stickiness via CSS) */}
      <section className="lm-footer-banner" style={{position: 'sticky', bottom: 0, zIndex: 100, background: 'var(--lilac-violet-accent)'}}>
        <h2 style={{color: 'var(--charcoal-bg)'}}>Ready to Generate Your First Report?</h2>
        <button className="cta-button cta-button-primary" style={{backgroundColor: 'var(--charcoal-bg)', color: 'var(--lilac-violet-accent)', borderColor: 'var(--charcoal-bg)'}} onClick={() => alert('Sign-up drawer placeholder')}>
          Generate My First Report
        </button>
      </section>
    </div>
  );
};

export default DataInsightPage; 