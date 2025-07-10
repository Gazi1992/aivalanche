import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import Hero from './components/Hero';
import OptimizationSection from './components/OptimizationSection';
import AutomationSection from './components/AutomationSection';
import Footer from './components/Footer';

// Import the new page components
import LabflowPage from './components/LabflowPage';
import DataInsightPage from './components/DataInsightPage';
import OptimizationPage from './components/OptimizationPage';

// Placeholder for sections on the homepage that the hero CTA might scroll to
const ProductsSection = () => (
  <div id="products-section" style={{padding: '40px 20px', backgroundColor: 'var(--charcoal-bg)', color: 'var(--white-text-85)'}}>
    <h2>Our Products & Services (Scroll Target)</h2>
    {/* Content for this section would go here - for now, it combines existing sections */}
    <OptimizationSection />
    <AutomationSection />
  </div>
);

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <Routes>
          <Route path="/" element={
            <>
              <Hero />
              {/* The existing OptimizationSection and AutomationSection might be part of a larger products overview
                  or could be the content for the #products-section scroll target. 
                  For now, wrapping them in a conceptual ProductsSection for the scroll. */}
              <ProductsSection /> 
            </>
          } />
          <Route path="/labflow" element={<LabflowPage />} />
          <Route path="/data-insight" element={<DataInsightPage />} />
          <Route path="/optimisation" element={<OptimizationPage />} />
          {/* Placeholder routes for demo links from Hero carousel */}
          <Route path="/request-demo" element={<div style={{paddingTop:'80px', color: 'white', backgroundColor: 'var(--charcoal-bg)', height: '100vh'}}>Request Demo Page Placeholder</div>} />
          <Route path="/see-live-demo" element={<div style={{paddingTop:'80px', color: 'white', backgroundColor: 'var(--charcoal-bg)', height: '100vh'}}>See Live Demo Page Placeholder</div>} />
          <Route path="/try-data-insight-demo" element={<div style={{paddingTop:'80px', color: 'white', backgroundColor: 'var(--charcoal-bg)', height: '100vh'}}>Try Data Insight Demo Page Placeholder</div>} />
          <Route path="/book-consultation" element={<div style={{paddingTop:'80px', color: 'white', backgroundColor: 'var(--charcoal-bg)', height: '100vh'}}>Book Consultation Page Placeholder</div>} />
        </Routes>
        <Footer />
      </div>
    </Router>
  );
}

export default App; 