import React from 'react';
import { SunIcon, MoonIcon } from './icons';

const ThemeToggle = ({ theme, toggleTheme }) => {
  return (
    <button
      className={`theme-switch ${theme}`}
      onClick={toggleTheme}
      aria-label="Toggle theme"
    >
      <MoonIcon />
      <SunIcon />
      <span className="switch-knob" />
    </button>
  );
};

export default ThemeToggle; 