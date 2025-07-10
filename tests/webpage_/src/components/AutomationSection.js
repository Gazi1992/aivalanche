import React from 'react';
import './AutomationSection.css'; // We'll create this CSS file next

const productFeatures = [
  {
    title: 'LLM-Powered Lab Instrument Control',
    description: 'Program and manage lab instruments using natural language commands through advanced AI agents.'
  },
  {
    title: 'Intelligent Data Organization',
    description: 'Automatically organize experimental data for easy access and analysis.'
  },
  {
    title: 'Complex Analysis Simplified',
    description: 'Perform simple and complex data analyses with AI assistance, no coding required.'
  },
  {
    title: 'Multi-Instrument Synchronization',
    description: 'Seamlessly synchronize multiple lab instruments for complex experimental setups.'
  },
  {
    title: 'Dynamic Data Visualization',
    description: 'Generate insightful visualizations of your data on the fly.'
  },
  {
    title: 'Automated Report Generation',
    description: 'Create comprehensive reports from your experimental data and analyses automatically.'
  }
];

const AutomationSection = () => {
  return (
    <section id="automation" className="automation-section section-padding">
      <div className="container">
        <h2 className="section-title">AI-Driven Automation for Laboratories</h2>
        <p className="section-intro">
          Our automation solutions revolutionize lab work. We've developed a product that uses Large Language Models (LLMs) 
          to program lab instruments. Talk to your lab in natural language to organize data, run analyses, 
          synchronize instruments, visualize results, and generate reports.
        </p>
        
        <div className="grid-container">
          {productFeatures.map((feature, index) => (
            <div key={index} className="card feature-card">
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>

        <div className="subsection">
          <h3 className="subsection-title">Standalone Tools</h3>
          <p className="subsection-text">
            We also offer our powerful visualization, data analysis, and report generation capabilities as a separate tool, 
            providing flexible solutions for your data handling needs.
          </p>
        </div>
      </div>
    </section>
  );
};

export default AutomationSection; 