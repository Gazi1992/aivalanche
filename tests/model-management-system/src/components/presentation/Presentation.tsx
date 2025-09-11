import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Home } from 'lucide-react';
import {
  Slide01_Intro,
  Slide02_Personas,
  Slide03_UserJourney
} from './slides';

const Presentation: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const slides = [
    { id: 'intro', component: <Slide01_Intro /> },
    { id: 'personas', component: <Slide02_Personas /> },
    { id: 'user-journey', component: <Slide03_UserJourney /> }
  ];

  const handleSlideChange = (newSlide: number) => {
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentSlide(newSlide);
      setIsTransitioning(false);
    }, 300);
  };

  const handleNextSlide = () => {
    if (currentSlide < slides.length - 1) {
      handleSlideChange(currentSlide + 1);
    }
  };

  const handlePrevSlide = () => {
    if (currentSlide > 0) {
      handleSlideChange(currentSlide - 1);
    }
  };

  const handleKeyPress = (e: KeyboardEvent) => {
    if (e.key === 'ArrowRight') handleNextSlide();
    if (e.key === 'ArrowLeft') handlePrevSlide();
    if (e.key === 'Home') handleSlideChange(0);
    if (e.key === 'End') handleSlideChange(slides.length - 1);
  };

  React.useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentSlide]);

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Presentation Header */}
      <div className="bg-gray-800 px-6 py-3 flex items-center justify-between border-b border-gray-700 relative">
        <div className="text-white font-semibold text-lg flex items-center">
          Technical Presentation
        </div>
        <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center gap-3">
          <button
            onClick={() => setCurrentSlide(0)}
            className="p-2 text-gray-400 hover:text-white transition-colors"
            title="Go to first slide"
          >
            <Home className="w-5 h-5" />
          </button>
          <button
            onClick={handlePrevSlide}
            className={`p-1 text-gray-400 hover:text-white transition-colors ${currentSlide === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={currentSlide === 0}
            title="Previous slide"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <span className="text-white font-medium px-2">
            Slide {currentSlide + 1} of {slides.length}
          </span>
          <button
            onClick={handleNextSlide}
            className={`p-1 text-gray-400 hover:text-white transition-colors ${currentSlide === slides.length - 1 ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={currentSlide === slides.length - 1}
            title="Next slide"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
        <div></div>
      </div>

      {/* Slide Progress Bar */}
      <div className="h-1 bg-gray-700">
        <div 
          className="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-500"
          style={{ width: `${((currentSlide + 1) / slides.length) * 100}%` }}
        />
      </div>

      {/* Slide Content with Side Navigation */}
      <div className={`flex-1 overflow-hidden transition-opacity duration-300 relative group ${isTransitioning ? 'opacity-0' : 'opacity-100'}`}>
        {slides[currentSlide].component}
        
        {/* Left Navigation Arrow - Shows on hover */}
        {currentSlide > 0 && (
          <button
            onClick={handlePrevSlide}
            className="absolute left-6 top-1/2 -translate-y-1/2 p-2 bg-black/20 backdrop-blur-sm text-white rounded-full hover:bg-black/40 transition-all hover:scale-110 z-10 border border-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            aria-label="Previous slide"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
        )}
        
        {/* Right Navigation Arrow - Shows on hover */}
        {currentSlide < slides.length - 1 && (
          <button
            onClick={handleNextSlide}
            className="absolute right-6 top-1/2 -translate-y-1/2 p-2 bg-black/20 backdrop-blur-sm text-white rounded-full hover:bg-black/40 transition-all hover:scale-110 z-10 border border-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            aria-label="Next slide"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Slide Navigator Dots */}
      <div className="bg-gray-800 px-6 py-3 flex justify-center gap-2">
        {slides.map((_, index) => (
          <button
            key={index}
            onClick={() => handleSlideChange(index)}
            className={`w-2 h-2 rounded-full transition-all ${
              index === currentSlide 
                ? 'w-8 bg-purple-500' 
                : 'bg-gray-600 hover:bg-gray-500'
            }`}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>
    </div>
  );
};

export default Presentation;