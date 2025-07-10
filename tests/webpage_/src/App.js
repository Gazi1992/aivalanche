import React from 'react';
import './App.css';
import Header from './components/Header';
import Hero from './components/Hero';
import OptimizationSection from './components/OptimizationSection';
import AutomationSection from './components/AutomationSection';
import Footer from './components/Footer';

function App() {
  return (
    <div className="App">
      <Header />
      <Hero />
      <OptimizationSection />
      <AutomationSection />
      <Footer />
    </div>
  );
}

export default App; 