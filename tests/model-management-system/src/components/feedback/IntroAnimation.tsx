import React, { useEffect, useState } from 'react';
import { Activity, Database, Brain, Zap, BarChart3 } from 'lucide-react';
import Logo from '../Logo';

interface IntroAnimationProps {
  onComplete: () => void;
}

const IntroAnimation: React.FC<IntroAnimationProps> = ({ onComplete }) => {
  const [stage, setStage] = useState(0);
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    const timers: NodeJS.Timeout[] = [];

    // Stage 1: Logo fade in
    timers.push(setTimeout(() => setStage(1), 300));
    
    // Stage 2: Title fade in
    timers.push(setTimeout(() => setStage(2), 1200));
    
    // Stage 3: Icons appear
    timers.push(setTimeout(() => setStage(3), 2100));
    
    // Stage 4: Tagline fade in
    timers.push(setTimeout(() => setStage(4), 3200));
    
    // Stage 5: Loading bar
    timers.push(setTimeout(() => setStage(5), 4100));
    
    // Stage 6: Mark as ready
    timers.push(setTimeout(() => setStage(6), 6500));
    
    // Start fade out of content
    timers.push(setTimeout(() => setFadeOut(true), 7000));
    
    // Complete animation
    timers.push(setTimeout(() => onComplete(), 7800));

    return () => {
      timers.forEach(timer => clearTimeout(timer));
    };
  }, [onComplete]);

  return (
    <div className={`fixed inset-0 flex items-center justify-center z-[100] overflow-hidden bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 transition-opacity duration-1000 ${
      fadeOut ? 'opacity-0' : 'opacity-100'
    }`}>
      {/* Animated background particles */}
      <div className={`absolute inset-0 transition-opacity duration-500 ${
        fadeOut ? 'opacity-0' : 'opacity-100'
      }`}>
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
        <div className="absolute top-40 right-20 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className={`relative z-10 text-center w-full flex flex-col items-center justify-center px-8 transition-opacity duration-500 ${
        fadeOut ? 'opacity-0' : 'opacity-100'
      }`}>
        {/* Logo */}
        <div className={`mb-16 transition-all duration-1000 transform ${
          stage >= 1 ? 'opacity-100 scale-100' : 'opacity-0 scale-75'
        }`}>
          <div className="transform scale-150 md:scale-175 lg:scale-200 inline-block">
            <Logo size="large" />
          </div>
        </div>

        {/* Title */}
        <div className={`mb-16 transition-all duration-1000 transform ${
          stage >= 2 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
        }`}>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-10 text-center whitespace-nowrap">
            Model Management & Calibration
          </h1>
          <div className="relative h-1 w-64 mx-auto mt-12 overflow-hidden rounded-full">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-purple-400 via-pink-400 to-transparent"></div>
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-shimmer"></div>
          </div>
        </div>

        {/* Feature Icons */}
        <div className={`flex justify-center gap-8 mb-12 transition-all duration-1000 ${
          stage >= 3 ? 'opacity-100' : 'opacity-0'
        }`}>
          {[
            { Icon: Database, delay: 0 },
            { Icon: Brain, delay: 200 },
            { Icon: Activity, delay: 400 },
            { Icon: Zap, delay: 600 },
            { Icon: BarChart3, delay: 800 }
          ].map(({ Icon, delay }, index) => (
            <div
              key={index}
              className={`transform transition-all duration-700 ${
                stage >= 3 ? 'scale-100 opacity-100' : 'scale-0 opacity-0'
              }`}
              style={{ transitionDelay: `${delay}ms` }}
            >
              <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20">
                <Icon className="w-6 h-6 text-white" />
              </div>
            </div>
          ))}
        </div>

        {/* Tagline */}
        <div className={`mb-16 transition-all duration-1000 ${
          stage >= 4 ? 'opacity-100' : 'opacity-0'
        }`}>
          <p className="text-xl text-purple-100">
            Advanced calibration and optimization for electronic component models
          </p>
        </div>

        {/* Loading Animation */}
        <div className={`mt-8 transition-all duration-700 ${
          stage >= 5 ? 'opacity-100' : 'opacity-0'
        }`}>
          <div className="flex flex-col items-center gap-4">
            {/* Animated dots */}
            <div className="flex gap-2">
              {[0, 1, 2, 3, 4].map((index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full bg-gradient-to-r from-purple-400 to-pink-400 ${
                    stage >= 5 ? 'animate-pulse' : ''
                  }`}
                  style={{
                    animationDelay: `${index * 200}ms`,
                    animationDuration: '1.5s'
                  }}
                />
              ))}
            </div>
            <p className="text-sm text-purple-200 font-medium tracking-wider">
              {stage >= 6 ? (
                <span className="text-purple-300 font-semibold">Ready!</span>
              ) : (
                <span className="animate-pulse">Initializing...</span>
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntroAnimation;