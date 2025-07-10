import React from 'react';
import { Link } from 'react-router-dom';
import "react-responsive-carousel/lib/styles/carousel.min.css"; // requires a loader
import { Carousel } from 'react-responsive-carousel';
import './Hero.css'; // We'll create this CSS file next

// Helper function for smooth scroll, can be moved to a utils file later
const smoothScrollTo = (elementId) => {
  const element = document.getElementById(elementId);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' });
  }
};

const Hero = () => {
  // Define brand colors from prompt for inline styles if needed quickly
  const charcoalBg = '#0B0D13';
  const lilacVioletAccent = '#A56BFF';

  const slide1Background = {
    background: `linear-gradient(to bottom right, var(--charcoal-bg) 0%, ${lilacVioletAccent} 200%)`,
    // TODO: Add faint engineering grid pattern
  };

  const slide2Background = {
    backgroundColor: '#E8EFF3',
    // Consider a subtle pattern or light texture if needed later
  };

  const slide3Background = {
    backgroundColor: 'var(--charcoal-bg)',
    // TODO: Add animated sparkline sweep
  };

  const slide4Background = {
    background: `radial-gradient(circle at center, #D6EAF8 0%, var(--charcoal-bg) 70%)`,
    // TODO: Add wireframe airfoil in background (e.g. pseudo element or SVG)
  };

  return (
    <section className="hero-section section-padding">
      <Carousel 
        showThumbs={false} 
        showStatus={false} 
        infiniteLoop 
        useKeyboardArrows 
        autoPlay 
        interval={6000} 
        stopOnHover={true} 
        className="hero-carousel"
      >
        {/* Slide 1: Aivalanche Overview */}
        <div className="carousel-slide" style={slide1Background}>
          <div className="container">
            <div className="slide-content-wrapper">
              <div className="slide-text-content">
                <div style={{position: 'absolute', top: '20px', left: 'calc(50% - 550px + 20px)', fontSize: '24px', fontWeight:'bold', color: 'var(--dark-text-full)'}}>ai for engineering</div> {/* Text color updated */} 
                <h1 className="hero-title">Accelerate Engineering with Generative AI.</h1>
                <p className="hero-subtitle">
                  We fuse advanced Large Language Models with deep engineering expertise to tackle your toughest challenges, from lab automation to design optimisation.
                </p>
                <ul className="slide-bullets">
                  <li><span className="bullet-icon">💡</span> LabFlow AI</li>
                  <li><span className="bullet-icon">📊</span> Data Insight AI</li>
                  <li><span className="bullet-icon">🛠️</span> AI-Driven Optimisation</li>
                </ul>
                <Link to="/request-demo" className="cta-button cta-button-primary">Request Demo</Link>
                <button onClick={() => smoothScrollTo('products-section')} className="cta-text-link" style={{marginLeft: '15px'}}>Learn more</button>
              </div>
              <div className="slide-visual-content">
                  <div className="visual-placeholder" style={{height: '350px'}}>
                      3-D composite: robotic arm, oscilloscope UI, swirling data nodes (parallax on cursor)
                  </div>
              </div>
            </div>
          </div>
        </div>

        {/* Slide 2: LabFlow AI */}
        <div className="carousel-slide" style={slide2Background}>
          <div className="container">
            <div className="slide-content-wrapper">
              <div className="slide-text-content">
                <div className="capsule-tag">PRODUCT</div>
                <h2 className="hero-title" style={{fontSize: '48px'}}>LabFlow AI – Automate Every Measurement.</h2> {/* Adjusted title size for H2 */} 
                <ul className="slide-bullets">
                  <li><span className="bullet-icon">💬</span> Natural-language control of test gear</li>
                  <li><span className="bullet-icon">🔄</span> Versioned script templates for instant scale-up</li>
                  <li><span className="bullet-icon">📈</span> Built-in analysis & reporting</li>
                </ul>
                <Link to="/see-live-demo" className="cta-button cta-button-primary">See live demo</Link>
                <Link to="/labflow" className="cta-button cta-button-ghost" style={{marginLeft: '15px'}}>Learn more</Link>
              </div>
              <div className="slide-visual-content">
                <div className="visual-placeholder" style={{height: '300px'}}>
                    Device mock-ups auto-cycling through UI screens (desktop, tablet, phone)
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Slide 3: Data Insight AI */}
        <div className="carousel-slide" style={slide3Background}>
          <div className="container">
            <div className="slide-content-wrapper">
              <div className="slide-text-content">
                <h2 className="hero-title" style={{fontSize: '48px'}}>From Raw Data to Publication-Ready Reports.</h2>
                <ul className="slide-bullets">
                  <li><span className="bullet-icon">🗣️</span> Conversational analytics</li>
                  <li><span className="bullet-icon">⚙️</span> Advanced stats & ML</li>
                  <li><span className="bullet-icon">📄</span> Auto-generated reports + templates</li>
                </ul>
                <Link to="/try-data-insight-demo" className="cta-button cta-button-primary">Try the demo</Link>
                <Link to="/data-insight" className="cta-button cta-button-ghost" style={{marginLeft: '15px'}}>Learn more</Link>
              </div>
              <div className="slide-visual-content">
                <div className="visual-placeholder" style={{height: '300px'}}>
                    Mini slideshow cycling through plot types (line, heatmap, parallel-coords…)
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Slide 4: AI-Driven Optimisation */}
        <div className="carousel-slide" style={slide4Background}>
          <div className="container">
            <div className="slide-content-wrapper">
              <div className="slide-text-content">
                <h2 className="hero-title" style={{fontSize: '48px'}}>Optimise the Impossible.</h2>
                <p className="hero-description" style={{maxWidth:'none', marginBottom: '30px'}}> {/* hero-description class for styling, overridden max-width */} 
                  Our advanced AI toolbox and deep engineering expertise allow us to tackle exceptionally complex challenges. We deliver significant performance and efficiency gains for problems like optical taper design, airfoil optimization, water network management, and transistor calibration.
                </p>
                <Link to="/book-consultation" className="cta-button cta-button-primary">Book consultation</Link>
                <Link to="/optimisation" className="cta-button cta-button-ghost" style={{marginLeft: '15px'}}>Learn more</Link>
              </div>
              <div className="slide-visual-content">
                <div className="visual-placeholder" style={{height: '300px'}}>
                    Animated vignette: Looping morph sequences of use cases (optical taper, airfoil, water network)
                </div>
              </div>
            </div>
          </div>
        </div>
      </Carousel>
    </section>
  );
};

export default Hero; 