import React from 'react';
import { Link } from 'react-router-dom';
import { Carousel } from 'react-responsive-carousel';
import "react-responsive-carousel/lib/styles/carousel.min.css"; // Import carousel styles
import './LearnMorePages.css'; // Import shared styles
import './Hero.css'; // For CTA button styles, review if they should be in a global/shared CSS

// Placeholder styles, these can be moved to a CSS file
const pageStyle = {
  padding: '100px 20px 20px', // Adjust top padding to account for fixed header
  minHeight: '100vh',
  backgroundColor: 'var(--charcoal-bg)',
  color: 'var(--white-text-85)'
};

const sectionStyle = {
  marginBottom: '40px',
  padding: '20px',
  border: '1px solid var(--electric-cyan-accent)',
  borderRadius: '8px'
};

const LabflowPage = () => {
  const painPoints = [
    { title: 'Manual Scripting Nightmare', description: 'Endless hours writing and debugging instrument scripts. Errors delay critical project timelines.' },
    { title: 'Scattered & Inconsistent Data', description: 'Data from different tests stored in various formats and locations, making analysis a major hurdle.' },
    { title: 'Slow Iteration Cycles', description: 'Setting up new experiments or modifying existing ones is cumbersome, stifling innovation and discovery.' },
  ];

  const features = [
    { 
      title: 'Natural Language Orchestration', 
      description: 'Simply tell LabFlow AI what you want to test. Our intelligent agents understand your intent and automatically configure and run your instruments.', 
      visual: 'NL Orchestration Visual Placeholder' 
    },
    { 
      title: 'Reusable Template Library', 
      description: 'Access a growing library of pre-built test sequences or create and version your own. Scale complex testing protocols instantly across your team.', 
      visual: 'Template Library Visual Placeholder' 
    },
    { 
      title: 'Integrated Analysis & Reporting', 
      description: 'Data is automatically collated, analyzed, and visualized. Generate consistent, shareable reports moments after your tests conclude.', 
      visual: 'Integrated Analysis Visual Placeholder' 
    },
    { 
      title: 'Collaborative Team Workspace', 
      description: 'Share test protocols, data, and insights seamlessly. Enhance collaboration and ensure knowledge continuity within your research group or company.', 
      visual: 'Team Workspace Visual Placeholder' 
    },
  ];

  const caseStudies = [
    { id: 1, title: 'Pharma R&D Acceleration', metric: 'Time-to-test for new compounds ↓ 78%', details: 'Placeholder for case study 1 details.' },
    { id: 2, title: 'Materials Science Discovery', metric: 'Experimental throughput ↑ 3x', details: 'Placeholder for case study 2 details.' },
    { id: 3, title: 'Academic Lab Efficiency', metric: 'Reduced manual effort by 15 hours/week', details: 'Placeholder for case study 3 details.' },
  ];

  return (
    <div className="learn-more-page">
      {/* 1. Hero Section */}
      <section className="lm-hero-section" style={{minHeight: '80vh'}}> {/* Use minHeight for flexibility */}
        <div className="lm-hero-content">
          <h1>LabFlow AI</h1>
          <p className="hero-subtitle" style={{fontSize: '22px', maxWidth: '600px'}}>The future of laboratory automation is here. Command your instruments with natural language, streamline complex workflows, and accelerate your research cycles.</p>
          <Link to="/request-pilot-install" className="cta-button cta-button-primary" style={{marginTop: '30px'}}>Request Pilot Install</Link>
        </div>
        <div className="lm-hero-visual">
          <div className="lm-visual-placeholder" style={{height: '400px'}}>
            15s looping video: natural-language command triggering synchronized instruments.
          </div>
        </div>
      </section>

      <div className="lm-container">
        {/* 2. Problem Framing */}
        <section className="lm-section">
          <h2 className="lm-section-title">Stop Fighting Your Lab, Start Discovering</h2>
          <div className="lm-cards-grid">
            {painPoints.map((point, index) => (
              <div className="lm-card" key={index}>
                <h3>{point.title}</h3>
                <p>{point.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* 3. Feature Deep Dive (Zig-Zag) */}
        <section className="lm-section">
          <h2 className="lm-section-title">How LabFlow AI Transforms Your Workflow</h2>
          {features.map((feature, index) => (
            <div className="lm-zigzag-row" key={index}>
              <div className="lm-zigzag-text">
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
              <div className="lm-zigzag-visual">
                <div className="lm-visual-placeholder" style={{minHeight: '200px'}}>{feature.visual}</div>
              </div>
            </div>
          ))}
        </section>

        {/* 4. Architecture Diagram */}
        <section className="lm-section">
          <h2 className="lm-section-title">Intelligent & Seamless Integration</h2>
          <div className="lm-visual-placeholder" style={{minHeight: '350px', backgroundColor: '#000'}}>
            Dark block SVG: User &lt;-&gt; LLM agents &lt;-&gt; Driver API &lt;-&gt; Instruments (with hotspots)
          </div>
        </section>

        {/* 5. Case Studies Carousel */}
        <section className="lm-section">
          <h2 className="lm-section-title">Proven Results, Accelerated Timelines</h2>
          <Carousel showThumbs={false} showStatus={false} infiniteLoop useKeyboardArrows autoPlay interval={7000} stopOnHover={true}>
            {caseStudies.map(study => (
              <div key={study.id} className="lm-card" style={{margin: '0 20px 40px', textAlign: 'center', background: 'rgba(255,255,255,0.08)'}}> {/* Added margin for carousel items */} 
                <h3>{study.title}</h3>
                <p style={{fontSize: '24px', color: 'var(--electric-cyan-accent)', fontWeight: 'bold'}}>{study.metric}</p>
                <p>{study.details}</p>
              </div>
            ))}
          </Carousel>
        </section>

        {/* 6. Pricing Table (Placeholder) */}
        <section className="lm-section">
          <h2 className="lm-section-title">Flexible Plans for Every Team</h2>
          <div className="lm-visual-placeholder" style={{minHeight: '300px'}}>
            Pricing Table: Free Lite / Pro / Enterprise, with FAQ accordion
          </div>
        </section>
      </div>

      {/* 7. Footer Banner */}
      <section className="lm-footer-banner">
        <h2>Ready to Revolutionize Your Lab?</h2>
        <button className="cta-button cta-button-primary" style={{backgroundColor: 'var(--charcoal-bg)', color: 'var(--electric-cyan-accent)', borderColor: 'var(--charcoal-bg)'}} onClick={() => alert('Calendly Modal Placeholder')}>
          Talk to an Engineer
        </button>
      </section>
    </div>
  );
};

export default LabflowPage; 