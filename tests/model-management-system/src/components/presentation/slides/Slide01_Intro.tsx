import React from 'react';
import { Database, Brain, GitBranch } from 'lucide-react';
import Logo from '../../Logo';

const Slide01_Intro: React.FC = () => {
  return (
    <div className="h-full flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900">
      <div className="text-center text-white space-y-8 max-w-7xl px-24 animate-fadeIn">
        <div className="flex justify-center mb-10">
          <Logo size="xxlarge" />
        </div>
        <div className="space-y-4">
          <h1 className="text-6xl font-bold tracking-tight mb-6 text-white">
            Model Management & Calibration
          </h1>
          <p className="text-2xl text-white/90 leading-relaxed whitespace-nowrap">
            A comprehensive ecosystem providing everything required for modeling electronic components
          </p>
        </div>
        
        <div className="grid grid-cols-3 gap-6 mt-12">
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20 transition-all duration-300 hover:bg-white/20 hover:shadow-xl hover:-translate-y-1 cursor-pointer">
            <Database className="w-12 h-12 text-white/80 mx-auto mb-4 transition-transform duration-300 hover:rotate-12" />
            <h3 className="text-xl font-semibold mb-2 text-white">Complete Model Library</h3>
            <p className="text-sm text-white/70 transition-colors duration-300 hover:text-white/90">BSIM4, PSP, EKV, HiSIM, and more industry-standard compact models</p>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20 transition-all duration-300 hover:bg-white/20 hover:shadow-xl hover:-translate-y-1 cursor-pointer">
            <Brain className="w-12 h-12 text-white/80 mx-auto mb-4 transition-transform duration-300 hover:rotate-12" />
            <h3 className="text-xl font-semibold mb-2 text-white">Automated Calibration</h3>
            <p className="text-sm text-white/70 transition-colors duration-300 hover:text-white/90">AI-powered optimization with real-time visualization and validation</p>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20 transition-all duration-300 hover:bg-white/20 hover:shadow-xl hover:-translate-y-1 cursor-pointer">
            <GitBranch className="w-12 h-12 text-white/80 mx-auto mb-4 transition-transform duration-300 hover:rotate-12" />
            <h3 className="text-xl font-semibold mb-2 text-white">End-to-End Workflow</h3>
            <p className="text-sm text-white/70 transition-colors duration-300 hover:text-white/90">From data acquisition to model deployment in production</p>
          </div>
        </div>
        
        <div className="pt-8">
          <p className="text-lg text-white/80 italic transition-all duration-300 hover:text-white hover:scale-105">
            "Everything you need for electronic component modeling - unified in one platform"
          </p>
        </div>
      </div>
    </div>
  );
};

export default Slide01_Intro;