import React from 'react';
import './Hero.css'; // We'll create this CSS file next

const Hero = () => {
  return (
    <section className="hero-section section-padding">
      <div className="container">
        <h1 className="hero-title">AI-Powered Engineering Solutions</h1>
        <p className="hero-subtitle">
          Leveraging cutting-edge AI to revolutionize design, optimization, and automation in engineering.
        </p>
        {/* Optional: Add a call to action button */}
        {/* <button className="btn btn-primary">Learn More</button> */}
      </div>
    </section>
  );
};

export default Hero; 