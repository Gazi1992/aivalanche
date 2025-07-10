import React from 'react';
import './OptimizationSection.css'; // We'll create this CSS file next

const useCases = [
  {
    title: 'Compact Model Calibrations',
    description: 'Extensively used in semiconductors and electronics, providing precise AI-driven calibrations.'
  },
  {
    title: 'Inverse Photonic Taper Design',
    description: 'AI-optimized design for photonics applications, enhancing performance and efficiency.'
  },
  {
    title: 'Airfoil Design Optimization',
    description: 'Advanced AI algorithms for superior aerodynamic designs and performance characteristics.'
  },
  {
    title: 'Water Distribution Network Optimization',
    description: 'Optimizing complex water networks for efficiency, reliability, and resource management.'
  }
];

const OptimizationSection = () => {
  return (
    <section id="optimization" className="optimization-section section-padding">
      <div className="container">
        <h2 className="section-title">Advanced AI for Engineering Optimization</h2>
        <p className="section-intro">
          Our optimization track leverages sophisticated AI methods and tools to tackle complex design, 
          calibration, and optimization challenges across various engineering and technology fields.
        </p>
        
        <div className="grid-container">
          {useCases.map((useCase, index) => (
            <div key={index} className="card use-case-card">
              <h3>{useCase.title}</h3>
              <p>{useCase.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default OptimizationSection; 