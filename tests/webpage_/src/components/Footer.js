import React from 'react';
import './Footer.css'; // We'll create this CSS file next

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer section-padding">
      <div className="container">
        <p>&copy; {currentYear} aivalanche. All rights reserved.</p>
        <p>Pioneering AI in Engineering</p>
        {/* Optional: Add social media links or other footer content here */}
      </div>
    </footer>
  );
};

export default Footer; 