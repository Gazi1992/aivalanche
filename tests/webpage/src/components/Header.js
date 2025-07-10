import React from 'react';
import './Header.css'; // We'll create this CSS file next

const Header = () => {
  return (
    <header className="app-header">
      <div className="container header-container">
        <h1 className="logo">aivalanche</h1>
        <nav className="main-nav">
          {/* Navigation links can be added here later */}
          {/* For example:
          <a href="#home">Home</a>
          <a href="#optimization">Optimization</a>
          <a href="#automation">Automation</a>
          <a href="#about">About Us</a>
          <a href="#contact">Contact</a>
          */}
        </nav>
      </div>
    </header>
  );
};

export default Header; 