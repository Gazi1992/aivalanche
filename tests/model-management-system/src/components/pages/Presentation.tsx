import React, { useState, useEffect } from 'react';
import { 
  ChevronRight, ChevronLeft, Play, Pause, Home, Users, 
  TrendingUp, Shield, Zap, Globe, Database, Cpu, 
  GitBranch, Target, Award, Clock, DollarSign, 
  CheckCircle, ArrowRight, Layers, Network, 
  Activity, BarChart3, Package, Send, Bell,
  Briefcase, FlaskConical, LineChart, UserCheck,
  Microscope, Brain, Settings, Eye
} from 'lucide-react';
import Logo from '../Logo';

const Presentation: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Auto-play functionality
  useEffect(() => {
    if (isAutoPlaying) {
      const timer = setTimeout(() => {
        if (currentSlide < slides.length - 1) {
          handleNextSlide();
        } else {
          setIsAutoPlaying(false);
        }
      }, 8000); // 8 seconds per slide
      return () => clearTimeout(timer);
    }
  }, [currentSlide, isAutoPlaying]);

  const handleNextSlide = () => {
    if (currentSlide < slides.length - 1) {
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentSlide(currentSlide + 1);
        setIsTransitioning(false);
      }, 300);
    }
  };

  const handlePrevSlide = () => {
    if (currentSlide > 0) {
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentSlide(currentSlide - 1);
        setIsTransitioning(false);
      }, 300);
    }
  };

  const slides = [
    // Slide 1: Platform Overview
    {
      id: 'overview',
      content: (
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
              <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
                <Database className="w-12 h-12 text-white/80 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2 text-white">Complete Model Library</h3>
                <p className="text-sm text-white/70">BSIM4, PSP, EKV, HiSIM, and more industry-standard compact models</p>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
                <Zap className="w-12 h-12 text-white/80 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2 text-white">Automated Calibration</h3>
                <p className="text-sm text-white/70">AI-powered optimization with real-time visualization and validation</p>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
                <GitBranch className="w-12 h-12 text-white/80 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2 text-white">End-to-End Workflow</h3>
                <p className="text-sm text-white/70">From data acquisition to model deployment in production</p>
              </div>
            </div>
            
            <div className="pt-8">
              <p className="text-lg text-white/80 italic">
                "Everything you need for electronic component modeling - unified in one platform"
              </p>
            </div>
          </div>
        </div>
      )
    },

    // Slide 2: Platform Personas
    {
      id: 'personas',
      content: (
        <div className="h-full px-24 py-12 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
          <h2 className="text-5xl font-bold text-gray-900 mb-12 text-center">Platform Users & Roles</h2>
          
          <div className="grid grid-cols-4 gap-10">
            {/* Requestor */}
            <div className="bg-white rounded-xl p-6 shadow-lg border-t-4 border-orange-500 hover:shadow-xl transition-all">
              <div className="flex flex-col items-center mb-6">
                <div className="w-28 h-28 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center mb-4">
                  <Briefcase className="w-14 h-14 text-white" />
                </div>
                <h3 className="text-3xl font-bold text-orange-700 mb-3">Requestor</h3>
                <p className="text-base text-gray-600 text-center leading-relaxed">Technical Marketing<br/>Project Manager<br/>Application Engineer</p>
              </div>
              <div className="bg-orange-50 rounded-lg p-5">
                <p className="text-lg font-semibold text-orange-800 mb-4">Key Activities:</p>
                <ul className="text-base text-gray-700 space-y-3">
                  <li className="flex items-start"><span className="mr-2">•</span><span>Initiates model requests for new products</span></li>
                  <li className="flex items-start"><span className="mr-2">•</span><span>Defines requirements and specifications</span></li>
                  <li className="flex items-start"><span className="mr-2">•</span><span>Tracks progress and validates deliverables</span></li>
                </ul>
              </div>
            </div>

            {/* Modeling Engineer */}
            <div className="bg-white rounded-xl p-6 shadow-lg border-t-4 border-purple-500 hover:shadow-xl transition-all">
              <div className="flex flex-col items-center mb-6">
                <div className="w-28 h-28 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center mb-4">
                  <Brain className="w-14 h-14 text-white" />
                </div>
                <h3 className="text-3xl font-bold text-purple-700 mb-3">Modeling Engineer</h3>
                <p className="text-base text-gray-600 text-center leading-relaxed">Device Modeling Expert<br/>Calibration Specialist<br/>Parameter Extraction</p>
              </div>
              <div className="bg-purple-50 rounded-lg p-5">
                <p className="text-lg font-semibold text-purple-800 mb-4">Key Activities:</p>
                <ul className="text-base text-gray-700 space-y-3">
                  <li className="flex items-start"><span className="mr-2">•</span><span>Performs model calibration and optimization</span></li>
                  <li className="flex items-start"><span className="mr-2">•</span><span>Validates model accuracy and quality</span></li>
                  <li className="flex items-start"><span className="mr-2">•</span><span>Ensures models meet specifications</span></li>
                </ul>
              </div>
            </div>

            {/* Data Provider */}
            <div className="bg-white rounded-xl p-6 shadow-lg border-t-4 border-green-500 hover:shadow-xl transition-all">
              <div className="flex flex-col items-center mb-6">
                <div className="w-28 h-28 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center mb-4">
                  <Microscope className="w-14 h-14 text-white" />
                </div>
                <h3 className="text-3xl font-bold text-green-700 mb-3">Data Provider</h3>
                <p className="text-base text-gray-600 text-center leading-relaxed">Lab Engineer<br/>TCAD Engineer<br/>Concept Engineer</p>
              </div>
              <div className="bg-green-50 rounded-lg p-5">
                <p className="text-lg font-semibold text-green-800 mb-4">Key Activities:</p>
                <ul className="text-base text-gray-700 space-y-3">
                  <li className="flex items-start"><span className="mr-2">•</span><span>Provides measurement data from lab</span></li>
                  <li className="flex items-start"><span className="mr-2">•</span><span>Supplies TCAD simulation results</span></li>
                  <li className="flex items-start"><span className="mr-2">•</span><span>Validates data quality and formats</span></li>
                </ul>
              </div>
            </div>

            {/* Manager */}
            <div className="bg-white rounded-xl p-6 shadow-lg border-t-4 border-blue-500 hover:shadow-xl transition-all">
              <div className="flex flex-col items-center mb-6">
                <div className="w-28 h-28 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center mb-4">
                  <LineChart className="w-14 h-14 text-white" />
                </div>
                <h3 className="text-3xl font-bold text-blue-700 mb-3">Manager</h3>
                <p className="text-base text-gray-600 text-center leading-relaxed">Team Lead<br/>Department Head<br/>Project Director</p>
              </div>
              <div className="bg-blue-50 rounded-lg p-5">
                <p className="text-lg font-semibold text-blue-800 mb-4">Key Activities:</p>
                <ul className="text-base text-gray-700 space-y-3">
                  <li className="flex items-start"><span className="mr-2">•</span><span>Monitors work progress and KPIs</span></li>
                  <li className="flex items-start"><span className="mr-2">•</span><span>Allocates resources and priorities</span></li>
                  <li className="flex items-start"><span className="mr-2">•</span><span>Reviews reports and metrics</span></li>
                </ul>
              </div>
            </div>
          </div>

          <div className="mt-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-5 text-white text-center">
            <p className="text-xl font-medium">Unified Platform • Seamless Collaboration • Real-time Visibility</p>
          </div>
        </div>
      )
    },

    // Slide 3: The Challenge
    {
      id: 'challenge',
      content: (
        <div className="h-full px-24 py-16 bg-gradient-to-br from-red-50 to-orange-50">
          <h2 className="text-5xl font-bold text-gray-900 mb-12">The Challenge</h2>
          <div className="grid grid-cols-2 gap-12">
            <div className="space-y-8">
              <div className="bg-white rounded-xl p-8 shadow-lg border-l-4 border-red-500 transform hover:scale-105 transition-transform">
                <h3 className="text-2xl font-semibold text-red-700 mb-4">Current Pain Points</h3>
                <ul className="space-y-3 text-lg text-gray-700">
                  <li className="flex items-start gap-3">
                    <span className="text-red-500 mt-1">✗</span>
                    <span>Manual, time-consuming calibration processes</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-red-500 mt-1">✗</span>
                    <span>Lack of standardization across teams</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-red-500 mt-1">✗</span>
                    <span>Scattered data in multiple formats</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-red-500 mt-1">✗</span>
                    <span>No centralized model repository</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-red-500 mt-1">✗</span>
                    <span>Difficult collaboration between teams</span>
                  </li>
                </ul>
              </div>
            </div>
            <div className="space-y-8">
              <div className="bg-gradient-to-br from-red-100 to-orange-100 rounded-xl p-8">
                <h3 className="text-2xl font-semibold text-gray-800 mb-6">Impact on Business</h3>
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <Clock className="w-12 h-12 text-red-600" />
                    <div>
                      <p className="font-semibold text-lg">70% Time Waste</p>
                      <p className="text-gray-600">In repetitive manual tasks</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <DollarSign className="w-12 h-12 text-red-600" />
                    <div>
                      <p className="font-semibold text-lg">$2M+ Annual Loss</p>
                      <p className="text-gray-600">Due to inefficiencies</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Users className="w-12 h-12 text-red-600" />
                    <div>
                      <p className="font-semibold text-lg">Poor Collaboration</p>
                      <p className="text-gray-600">Between departments</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },

    // Slide 3: Our Solution
    {
      id: 'solution',
      content: (
        <div className="h-full px-24 py-16 bg-gradient-to-br from-green-50 to-blue-50">
          <h2 className="text-5xl font-bold text-gray-900 mb-12">Our Solution</h2>
          <div className="grid grid-cols-3 gap-8">
            <div className="bg-white rounded-xl p-8 shadow-lg border-t-4 border-green-500 transform hover:scale-105 transition-transform">
              <div className="flex justify-center mb-6">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
                  <Database className="w-10 h-10 text-green-600" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-center mb-4">Centralized Repository</h3>
              <p className="text-gray-600 text-center">
                Single source of truth for all models, templates, and reference data
              </p>
            </div>
            
            <div className="bg-white rounded-xl p-8 shadow-lg border-t-4 border-blue-500 transform hover:scale-105 transition-transform">
              <div className="flex justify-center mb-6">
                <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
                  <Zap className="w-10 h-10 text-blue-600" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-center mb-4">Automated Calibration</h3>
              <p className="text-gray-600 text-center">
                AI-powered optimization with real-time progress tracking
              </p>
            </div>
            
            <div className="bg-white rounded-xl p-8 shadow-lg border-t-4 border-purple-500 transform hover:scale-105 transition-transform">
              <div className="flex justify-center mb-6">
                <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center">
                  <GitBranch className="w-10 h-10 text-purple-600" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-center mb-4">Seamless Workflow</h3>
              <p className="text-gray-600 text-center">
                End-to-end process from request to delivery
              </p>
            </div>
          </div>
          
          <div className="mt-12 bg-gradient-to-r from-green-600 to-blue-600 rounded-xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-4 text-center">Unified Platform for All Stakeholders</h3>
            <div className="flex justify-around items-center">
              <div className="text-center">
                <Users className="w-8 h-8 mx-auto mb-2" />
                <p>Lab Engineers</p>
              </div>
              <ArrowRight className="w-6 h-6" />
              <div className="text-center">
                <Cpu className="w-8 h-8 mx-auto mb-2" />
                <p>Model Engineers</p>
              </div>
              <ArrowRight className="w-6 h-6" />
              <div className="text-center">
                <Package className="w-8 h-8 mx-auto mb-2" />
                <p>TCAD Engineers</p>
              </div>
              <ArrowRight className="w-6 h-6" />
              <div className="text-center">
                <Target className="w-8 h-8 mx-auto mb-2" />
                <p>App Engineers</p>
              </div>
            </div>
          </div>
        </div>
      )
    },

    // Slide 4: System Architecture
    {
      id: 'architecture',
      content: (
        <div className="h-full px-24 py-16 bg-gradient-to-br from-indigo-50 to-purple-50">
          <h2 className="text-5xl font-bold text-gray-900 mb-12">System Architecture</h2>
          <div className="relative h-[70%]">
            {/* Animated Architecture Diagram */}
            <div className="absolute inset-0 flex flex-col justify-between">
              {/* Layer 4: Users */}
              <div className="bg-white rounded-xl p-6 shadow-lg border-2 border-indigo-300 animate-slideInTop">
                <h3 className="text-lg font-bold text-indigo-700 mb-4">User Interface Layer</h3>
                <div className="flex justify-around">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Users className="w-6 h-6 text-blue-600" />
                    </div>
                    <p className="text-sm">Lab Engineer</p>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Cpu className="w-6 h-6 text-purple-600" />
                    </div>
                    <p className="text-sm">Model Engineer</p>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Activity className="w-6 h-6 text-green-600" />
                    </div>
                    <p className="text-sm">TCAD Engineer</p>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Target className="w-6 h-6 text-orange-600" />
                    </div>
                    <p className="text-sm">App Engineer</p>
                  </div>
                </div>
              </div>

              {/* Layer 3: Application */}
              <div className="bg-white rounded-xl p-6 shadow-lg border-2 border-purple-300 animate-slideInLeft">
                <h3 className="text-lg font-bold text-purple-700 mb-4">Application Layer</h3>
                <div className="grid grid-cols-5 gap-4">
                  <div className="bg-purple-50 rounded p-3 text-center">
                    <BarChart3 className="w-6 h-6 mx-auto mb-1 text-purple-600" />
                    <p className="text-xs">Dashboard</p>
                  </div>
                  <div className="bg-purple-50 rounded p-3 text-center">
                    <Database className="w-6 h-6 mx-auto mb-1 text-purple-600" />
                    <p className="text-xs">Libraries</p>
                  </div>
                  <div className="bg-purple-50 rounded p-3 text-center">
                    <Cpu className="w-6 h-6 mx-auto mb-1 text-purple-600" />
                    <p className="text-xs">Calibration</p>
                  </div>
                  <div className="bg-purple-50 rounded p-3 text-center">
                    <Send className="w-6 h-6 mx-auto mb-1 text-purple-600" />
                    <p className="text-xs">Requests</p>
                  </div>
                  <div className="bg-purple-50 rounded p-3 text-center">
                    <Shield className="w-6 h-6 mx-auto mb-1 text-purple-600" />
                    <p className="text-xs">Auth</p>
                  </div>
                </div>
              </div>

              {/* Layer 2: Services */}
              <div className="bg-white rounded-xl p-6 shadow-lg border-2 border-blue-300 animate-slideInRight">
                <h3 className="text-lg font-bold text-blue-700 mb-4">Service Layer</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-blue-50 rounded p-3 text-center">
                    <Database className="w-6 h-6 mx-auto mb-1 text-blue-600" />
                    <p className="text-xs font-semibold">Data Service</p>
                    <p className="text-xs text-gray-600">CRUD Operations</p>
                  </div>
                  <div className="bg-blue-50 rounded p-3 text-center">
                    <Zap className="w-6 h-6 mx-auto mb-1 text-blue-600" />
                    <p className="text-xs font-semibold">Calibration Engine</p>
                    <p className="text-xs text-gray-600">AI Optimization</p>
                  </div>
                  <div className="bg-blue-50 rounded p-3 text-center">
                    <Package className="w-6 h-6 mx-auto mb-1 text-blue-600" />
                    <p className="text-xs font-semibold">Export Service</p>
                    <p className="text-xs text-gray-600">Multi-format</p>
                  </div>
                </div>
              </div>

              {/* Layer 1: Data */}
              <div className="bg-white rounded-xl p-6 shadow-lg border-2 border-green-300 animate-slideInBottom">
                <h3 className="text-lg font-bold text-green-700 mb-4">Data Storage Layer</h3>
                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-green-50 rounded p-3 text-center">
                    <p className="text-xs font-semibold text-green-700">Model Templates</p>
                    <p className="text-xs text-gray-600">BSIM4, PSP, EKV</p>
                  </div>
                  <div className="bg-green-50 rounded p-3 text-center">
                    <p className="text-xs font-semibold text-green-700">Reference Data</p>
                    <p className="text-xs text-gray-600">Measurements</p>
                  </div>
                  <div className="bg-green-50 rounded p-3 text-center">
                    <p className="text-xs font-semibold text-green-700">Testbenches</p>
                    <p className="text-xs text-gray-600">Circuits</p>
                  </div>
                  <div className="bg-green-50 rounded p-3 text-center">
                    <p className="text-xs font-semibold text-green-700">Calibrated</p>
                    <p className="text-xs text-gray-600">Final Models</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },

    // Slide 5: Workflow Process
    {
      id: 'workflow',
      content: (
        <div className="h-full px-24 py-16 bg-gradient-to-br from-blue-50 to-purple-50">
          <h2 className="text-5xl font-bold text-gray-900 mb-12">End-to-End Workflow</h2>
          <div className="relative">
            {/* Animated Timeline */}
            <div className="absolute top-1/2 left-0 right-0 h-2 bg-gradient-to-r from-blue-400 via-purple-400 to-green-400 rounded-full"></div>
            
            <div className="relative grid grid-cols-4 gap-8 pt-8">
              {/* Step 1 */}
              <div className="text-center animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
                <div className="w-16 h-16 bg-blue-500 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                  1
                </div>
                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <Send className="w-8 h-8 text-blue-500 mx-auto mb-3" />
                  <h3 className="font-bold text-lg mb-2">Request Creation</h3>
                  <p className="text-sm text-gray-600">Application engineer submits model requirements</p>
                  <div className="mt-3 text-xs bg-blue-100 rounded-full px-3 py-1 inline-block">
                    Instant Notification
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className="text-center animate-fadeInUp" style={{ animationDelay: '0.4s' }}>
                <div className="w-16 h-16 bg-purple-500 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                  2
                </div>
                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <Database className="w-8 h-8 text-purple-500 mx-auto mb-3" />
                  <h3 className="font-bold text-lg mb-2">Data Preparation</h3>
                  <p className="text-sm text-gray-600">Lab/TCAD data uploaded and validated</p>
                  <div className="mt-3 text-xs bg-purple-100 rounded-full px-3 py-1 inline-block">
                    Quality Assured
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className="text-center animate-fadeInUp" style={{ animationDelay: '0.6s' }}>
                <div className="w-16 h-16 bg-indigo-500 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                  3
                </div>
                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <Zap className="w-8 h-8 text-indigo-500 mx-auto mb-3" />
                  <h3 className="font-bold text-lg mb-2">Calibration</h3>
                  <p className="text-sm text-gray-600">AI-powered optimization with real-time tracking</p>
                  <div className="mt-3 text-xs bg-indigo-100 rounded-full px-3 py-1 inline-block">
                    85% Faster
                  </div>
                </div>
              </div>

              {/* Step 4 */}
              <div className="text-center animate-fadeInUp" style={{ animationDelay: '0.8s' }}>
                <div className="w-16 h-16 bg-green-500 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                  4
                </div>
                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <Package className="w-8 h-8 text-green-500 mx-auto mb-3" />
                  <h3 className="font-bold text-lg mb-2">Delivery</h3>
                  <p className="text-sm text-gray-600">Export in multiple formats with documentation</p>
                  <div className="mt-3 text-xs bg-green-100 rounded-full px-3 py-1 inline-block">
                    Ready to Use
                  </div>
                </div>
              </div>
            </div>

            {/* Timeline Stats */}
            <div className="mt-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
              <div className="grid grid-cols-3 gap-8 text-center">
                <div>
                  <p className="text-3xl font-bold">6 Days → 1 Day</p>
                  <p className="text-sm opacity-90">Average Turnaround</p>
                </div>
                <div>
                  <p className="text-3xl font-bold">100%</p>
                  <p className="text-sm opacity-90">Process Visibility</p>
                </div>
                <div>
                  <p className="text-3xl font-bold">Zero</p>
                  <p className="text-sm opacity-90">Manual Errors</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },

    // Slide 6: Key Benefits
    {
      id: 'benefits',
      content: (
        <div className="h-full px-24 py-16 bg-gradient-to-br from-purple-50 to-pink-50">
          <h2 className="text-5xl font-bold text-gray-900 mb-12">Key Benefits</h2>
          <div className="grid grid-cols-2 gap-12">
            {/* Left side - For Business */}
            <div>
              <h3 className="text-3xl font-semibold text-purple-700 mb-8">For Business</h3>
              <div className="space-y-6">
                <div className="flex items-start gap-4 bg-white rounded-lg p-6 shadow-md">
                  <TrendingUp className="w-8 h-8 text-green-500 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-lg mb-2">85% Efficiency Gain</h4>
                    <p className="text-gray-600">Automated calibration reduces time from days to hours</p>
                  </div>
                </div>
                <div className="flex items-start gap-4 bg-white rounded-lg p-6 shadow-md">
                  <DollarSign className="w-8 h-8 text-green-500 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-lg mb-2">$3M Annual Savings</h4>
                    <p className="text-gray-600">Reduced manual work and faster time-to-market</p>
                  </div>
                </div>
                <div className="flex items-start gap-4 bg-white rounded-lg p-6 shadow-md">
                  <Shield className="w-8 h-8 text-blue-500 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-lg mb-2">100% Compliance</h4>
                    <p className="text-gray-600">Standardized processes meet all regulatory requirements</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Right side - For Teams */}
            <div>
              <h3 className="text-3xl font-semibold text-pink-700 mb-8">For Teams</h3>
              <div className="space-y-6">
                <div className="flex items-start gap-4 bg-white rounded-lg p-6 shadow-md">
                  <Users className="w-8 h-8 text-purple-500 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-lg mb-2">Seamless Collaboration</h4>
                    <p className="text-gray-600">All teams work on the same platform with real-time updates</p>
                  </div>
                </div>
                <div className="flex items-start gap-4 bg-white rounded-lg p-6 shadow-md">
                  <Globe className="w-8 h-8 text-purple-500 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-lg mb-2">Global Accessibility</h4>
                    <p className="text-gray-600">Cloud-based system accessible from anywhere</p>
                  </div>
                </div>
                <div className="flex items-start gap-4 bg-white rounded-lg p-6 shadow-md">
                  <Award className="w-8 h-8 text-orange-500 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-lg mb-2">Best Practices</h4>
                    <p className="text-gray-600">Built-in industry standards and optimized workflows</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },

    // Slide 7: Success Metrics
    {
      id: 'metrics',
      content: (
        <div className="h-full px-24 py-16 bg-gradient-to-br from-green-50 to-teal-50">
          <h2 className="text-5xl font-bold text-gray-900 mb-12">Success Metrics</h2>
          <div className="grid grid-cols-4 gap-8 mb-12">
            <div className="bg-white rounded-xl p-8 shadow-lg text-center">
              <div className="text-5xl font-bold text-green-600 mb-2">500+</div>
              <p className="text-lg font-semibold text-gray-700">Models Calibrated</p>
              <p className="text-sm text-gray-500 mt-2">Per Month</p>
            </div>
            <div className="bg-white rounded-xl p-8 shadow-lg text-center">
              <div className="text-5xl font-bold text-blue-600 mb-2">99.9%</div>
              <p className="text-lg font-semibold text-gray-700">Accuracy Rate</p>
              <p className="text-sm text-gray-500 mt-2">Model Precision</p>
            </div>
            <div className="bg-white rounded-xl p-8 shadow-lg text-center">
              <div className="text-5xl font-bold text-purple-600 mb-2">24hrs</div>
              <p className="text-lg font-semibold text-gray-700">Average TAT</p>
              <p className="text-sm text-gray-500 mt-2">Request to Delivery</p>
            </div>
            <div className="bg-white rounded-xl p-8 shadow-lg text-center">
              <div className="text-5xl font-bold text-orange-600 mb-2">50+</div>
              <p className="text-lg font-semibold text-gray-700">Active Users</p>
              <p className="text-sm text-gray-500 mt-2">Cross-functional</p>
            </div>
          </div>

          {/* ROI Chart */}
          <div className="bg-white rounded-xl p-8 shadow-lg">
            <h3 className="text-2xl font-semibold mb-6">Return on Investment</h3>
            <div className="relative h-64">
              <div className="absolute bottom-0 left-0 right-0 grid grid-cols-12 gap-2 h-full items-end">
                {[30, 45, 60, 75, 85, 95, 110, 125, 140, 160, 180, 200].map((height, index) => (
                  <div
                    key={index}
                    className="bg-gradient-to-t from-green-500 to-green-300 rounded-t animate-growUp"
                    style={{ 
                      height: `${height / 2}%`,
                      animationDelay: `${index * 0.1}s`
                    }}
                  >
                    <div className="text-xs text-white text-center mt-2">
                      {height}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="mt-4 text-center text-sm text-gray-600">
              Monthly ROI Growth (Past 12 Months)
            </div>
          </div>
        </div>
      )
    },

    // Slide 8: Call to Action
    {
      id: 'cta',
      content: (
        <div className="h-full flex items-center justify-center bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
          <div className="text-center text-white space-y-8 max-w-4xl mx-auto px-24">
            <h2 className="text-6xl font-bold mb-8">Ready to Transform Your Modeling Process?</h2>
            
            <div className="space-y-6 text-xl">
              <p>Join the digital transformation journey</p>
              <p>Standardize your workflows across all teams</p>
              <p>Achieve unprecedented efficiency and accuracy</p>
            </div>

            <div className="pt-8 space-y-6">
              <div className="flex justify-center gap-6">
                <button className="px-8 py-4 bg-white text-purple-900 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors">
                  Schedule a Demo
                </button>
                <button className="px-8 py-4 bg-purple-600 text-white rounded-lg font-semibold text-lg hover:bg-purple-700 transition-colors">
                  Get Started Today
                </button>
              </div>
              
              <div className="pt-8">
                <p className="text-lg text-gray-300">
                  Contact: model-management@company.com
                </p>
              </div>
            </div>

            <div className="pt-12 flex justify-center gap-8 text-sm text-gray-400">
              <span>✓ ISO 27001 Certified</span>
              <span>✓ GDPR Compliant</span>
              <span>✓ 24/7 Support</span>
            </div>
          </div>
        </div>
      )
    }
  ];

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Presentation Header */}
      <div className="bg-gray-800 px-6 py-3 flex items-center justify-between border-b border-gray-700 relative">
        <div className="text-white font-semibold text-lg flex items-center">
          Technical Presentation
        </div>
        <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center gap-4">
          <button
            onClick={() => setCurrentSlide(0)}
            className="p-2 text-gray-400 hover:text-white transition-colors"
            title="Go to first slide"
          >
            <Home className="w-5 h-5" />
          </button>
          <span className="text-white font-medium">
            Slide {currentSlide + 1} of {slides.length}
          </span>
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
        {slides[currentSlide].content}
        
        {/* Left Navigation Arrow - Shows on hover */}
        {currentSlide > 0 && (
          <button
            onClick={handlePrevSlide}
            className="absolute left-6 top-1/2 -translate-y-1/2 p-3 bg-black/20 backdrop-blur-sm text-white rounded-full hover:bg-black/40 transition-all hover:scale-110 z-10 border border-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            aria-label="Previous slide"
          >
            <ChevronLeft className="w-8 h-8" />
          </button>
        )}
        
        {/* Right Navigation Arrow - Shows on hover */}
        {currentSlide < slides.length - 1 && (
          <button
            onClick={handleNextSlide}
            className="absolute right-6 top-1/2 -translate-y-1/2 p-3 bg-black/20 backdrop-blur-sm text-white rounded-full hover:bg-black/40 transition-all hover:scale-110 z-10 border border-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            aria-label="Next slide"
          >
            <ChevronRight className="w-8 h-8" />
          </button>
        )}
      </div>

      {/* Slide Navigator Dots */}
      <div className="bg-gray-800 px-6 py-3 flex justify-center gap-2">
        {slides.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentSlide(index)}
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