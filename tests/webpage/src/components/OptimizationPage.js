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

const OptimizationPage = () => {

  const useCases = [
    { id: 1, title: 'Optical Taper Design', visual: '3D Asset: Optical Taper', metric: 'Efficiency increased by 25%' },
    { id: 2, title: 'Airfoil Shape Optimization', visual: '3D Asset: Airfoil', metric: 'Drag reduced by 12%' },
    { id: 3, title: 'Water Network Calibration', visual: '3D Asset: Water Network', metric: 'Leakage prediction accuracy improved to 98%' },
    { id: 4, title: 'Transistor Sizing & Calibration', visual: '3D Asset: Transistor', metric: 'Performance yield up by 18%' },
  ];

  const engagementModels = [
    { title: 'Turn-Key AI Solver', description: 'Provide us with your problem, we deliver a ready-to-use AI-powered optimization solution.' },
    { title: 'Collaborative R&D', description: 'Work alongside our AI experts to co-create and integrate bespoke optimisation tools into your workflows.' },
    { title: 'Strategic AI Consulting', description: 'Leverage our deep expertise for strategic guidance, feasibility studies, and AI roadmap development for optimisation.' },
  ];

  return (
    <div className="learn-more-page">
      {/* 1. Hero Section */}
      <section className="lm-hero-section" style={{ minHeight: '75vh', background: 'radial-gradient(ellipse at center, var(--lilac-violet-accent) 0%, var(--charcoal-bg) 70%)' }}>
        <div className="lm-hero-content" style={{textAlign: 'center', width: '100%'}}>
           {/* Placeholder for morphing generative mesh */}
           <div className="lm-visual-placeholder" style={{height: '200px', width: '70%', margin: '0 auto 30px auto', borderStyle: 'solid', borderColor: 'var(--electric-cyan-accent)'}}>
            Morphing Generative Mesh Visual Placeholder
          </div>
          <h1>Custom AI Optimisers for Complex Engineering.</h1>
          <p className="hero-subtitle" style={{fontSize: '22px', maxWidth: '750px', margin: '0 auto 30px auto'}}>
            When off-the-shelf solutions fall short, our bespoke AI-driven optimisers find novel solutions to your most challenging engineering problems, delivering significant performance and efficiency gains.
          </p>
          <Link to="/book-consultation" className="cta-button cta-button-primary">Discuss Your Challenge</Link>
        </div>
      </section>

      <div className="lm-container">
        {/* 2. Use-Case Carousel */}
        <section className="lm-section">
          <h2 className="lm-section-title">Real-World Impact: Optimisation Across Domains</h2>
          <Carousel 
            showThumbs={false} 
            showStatus={false} 
            infiniteLoop 
            useKeyboardArrows 
            autoPlay 
            interval={6500} 
            stopOnHover={true}
            centerMode={true}
            centerSlidePercentage={50} // Shows 2 items if wide enough, adjust as needed
          >
            {useCases.map(uc => (
              <div key={uc.id} className="lm-card" style={{margin: '0 15px 40px', textAlign: 'center', minHeight: '300px'}}>
                <h3 style={{fontSize: '20px'}}>{uc.title}</h3>
                <div className="lm-visual-placeholder" style={{minHeight: '120px', fontSize: '14px', marginBottom: '15px'}}>{uc.visual}</div>
                <p style={{fontSize: '18px', color: 'var(--electric-cyan-accent)', fontWeight: 'bold'}}>{uc.metric}</p>
              </div>
            ))}
          </Carousel>
        </section>

        {/* 3. Capability Matrix (Interactive Placeholder) */}
        <section className="lm-section">
          <h2 className="lm-section-title">Our Expertise: Methods & Domains</h2>
          <div className="lm-visual-placeholder" style={{ minHeight: '350px' }}>
            Interactive Capability Matrix: Rows (Bayesian opt, GNN surrogate, RL, GA…) x Columns (Domains). Hover reveals example. (Placeholder)
          </div>
        </section>

        {/* 4. Toolbox Explorer (Accordion Placeholder) */}
        <section className="lm-section">
          <h2 className="lm-section-title">Explore Our AI Optimisation Toolbox</h2>
          <div className="lm-visual-placeholder" style={{ minHeight: '300px' }}>
            Accordion: Each stack shows description & convergence plot. (Placeholder)
          </div>
        </section>

        {/* 5. Engagement Models */}
        <section className="lm-section">
          <h2 className="lm-section-title">How We Work With You</h2>
          <div className="lm-cards-grid">
            {engagementModels.map((model, index) => (
              <div className="lm-card" key={index}>
                <h3>{model.title}</h3>
                <p>{model.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* 6. Proof-of-Concept Video */}
        <section className="lm-section">
          <h2 className="lm-section-title">See It In Action</h2>
          <div className="lm-visual-placeholder" style={{minHeight: '400px'}}>
            2-min montage video (airfoil CFD, taper FOM…). Placeholder
          </div>
        </section>
      </div>

      {/* 7. Sticky Contact Form (Placeholder) */}
      <section className="lm-footer-banner" style={{position: 'sticky', bottom: 0, zIndex: 100, background: 'var(--electric-cyan-accent)'}}>
        <h2 style={{color: 'var(--charcoal-bg)'}}>Ready to Optimise the Impossible?</h2>
        <Link to="/contact-optimisation-expert" className="cta-button cta-button-primary" style={{backgroundColor: 'var(--charcoal-bg)', color: 'var(--electric-cyan-accent)', borderColor: 'var(--charcoal-bg)'}}>
          Contact an Optimisation Expert
        </Link>
      </section>
    </div>
  );
};

export default OptimizationPage; 