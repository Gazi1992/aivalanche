import React, { useState } from 'react';
import { X, ChevronRight, Search, Home, Database, Cpu, FileText, Settings, HelpCircle, Zap, BarChart3, AlertCircle, Info, Users, GitBranch, Package, Layers, Shield, ZoomIn, ZoomOut, Presentation, Play } from 'lucide-react';
import { Icon } from './ui/Icons';
import PresentationComponent from './presentation/Presentation';

interface UserGuideProps {
  isOpen: boolean;
  onClose: () => void;
}

const UserGuide: React.FC<UserGuideProps> = ({ isOpen, onClose }) => {
  const [activeSection, setActiveSection] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [showZoomedView, setShowZoomedView] = useState(false);
  const [showPresentation, setShowPresentation] = useState(false);

  // User Journey Content Component
  const UserJourneyContent = () => (
    <div className="min-w-[1400px]">
      {/* Timeline Header */}
      <div className="flex items-center justify-between mb-4 px-4">
        <div className="text-sm font-bold text-gray-700">START</div>
        <div className="flex-1 mx-4 h-2 bg-gradient-to-r from-blue-400 via-purple-400 to-green-400 rounded-full"></div>
        <div className="text-sm font-bold text-gray-700">END</div>
      </div>
      
      {/* Swimlanes for each persona */}
      <div className="space-y-3">
        {/* Application Engineer Lane */}
        <div className="flex items-center gap-3">
          <div className="w-32 bg-orange-100 rounded-lg p-3 border-2 border-orange-300">
            <div className="text-center">
              <div className="text-2xl mb-1">🎯</div>
              <div className="text-xs font-bold text-orange-700">APP ENGINEER</div>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-1">
            <div className="bg-white rounded-lg border-2 border-orange-300 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-orange-700">1. Identify Need</div>
              <div className="text-xs text-gray-600 mt-1">• New product design</div>
              <div className="text-xs text-gray-600">• Model requirement</div>
            </div>
            <ChevronRight className="text-gray-400" />
            <div className="bg-white rounded-lg border-2 border-orange-300 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-orange-700">2. Create Request</div>
              <div className="text-xs text-gray-600 mt-1">• Specify device type</div>
              <div className="text-xs text-gray-600">• Set requirements</div>
              <div className="text-xs bg-orange-100 rounded px-1 py-0.5 mt-1">→ Requests Page</div>
            </div>
            <div className="flex-1"></div>
            <div className="bg-white rounded-lg border-2 border-orange-300 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-orange-700">10. Review Model</div>
              <div className="text-xs text-gray-600 mt-1">• Validate results</div>
              <div className="text-xs text-gray-600">• Accept/Reject</div>
            </div>
            <ChevronRight className="text-gray-400" />
            <div className="bg-orange-200 rounded-lg border-2 border-orange-400 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-orange-800">11. Use in Design</div>
              <div className="text-xs text-gray-700 mt-1">• Download model</div>
              <div className="text-xs text-gray-700">• Integrate in flow</div>
              <div className="text-xs font-bold mt-1">✅ COMPLETE</div>
            </div>
          </div>
        </div>
        
        {/* Model Engineer Lane */}
        <div className="flex items-center gap-3">
          <div className="w-32 bg-purple-100 rounded-lg p-3 border-2 border-purple-300">
            <div className="text-center">
              <div className="text-2xl mb-1">💻</div>
              <div className="text-xs font-bold text-purple-700">MODEL ENGINEER</div>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-1">
            <div className="flex-1"></div>
            <div className="bg-purple-200 rounded-lg border-2 border-purple-400 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-purple-800">3. Receive Request</div>
              <div className="text-xs text-gray-700 mt-1">🔔 Notification</div>
              <div className="text-xs text-gray-700">• Review specs</div>
            </div>
            <ChevronRight className="text-gray-400" />
            <div className="bg-white rounded-lg border-2 border-purple-300 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-purple-700">4. Select Template</div>
              <div className="text-xs text-gray-600 mt-1">• Choose BSIM4/PSP</div>
              <div className="text-xs bg-purple-100 rounded px-1 py-0.5 mt-1">→ Libraries</div>
            </div>
            <ChevronRight className="text-gray-400" />
            <div className="bg-white rounded-lg border-2 border-purple-300 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-purple-700">7. Load Data</div>
              <div className="text-xs text-gray-600 mt-1">• Select reference</div>
              <div className="text-xs text-gray-600">• Validate quality</div>
            </div>
            <ChevronRight className="text-gray-400" />
            <div className="bg-white rounded-lg border-2 border-purple-300 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-purple-700">8. Calibrate</div>
              <div className="text-xs text-gray-600 mt-1">• Set parameters</div>
              <div className="text-xs text-gray-600">• Run optimization</div>
              <div className="text-xs bg-purple-100 rounded px-1 py-0.5 mt-1">→ My Models</div>
            </div>
            <ChevronRight className="text-gray-400" />
            <div className="bg-white rounded-lg border-2 border-purple-300 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-purple-700">9. Export</div>
              <div className="text-xs text-gray-600 mt-1">• Generate SPICE</div>
              <div className="text-xs text-gray-600">• Create package</div>
              <div className="text-xs bg-purple-100 rounded px-1 py-0.5 mt-1">📦 Deliver</div>
            </div>
          </div>
        </div>
        
        {/* Lab Engineer Lane */}
        <div className="flex items-center gap-3">
          <div className="w-32 bg-blue-100 rounded-lg p-3 border-2 border-blue-300">
            <div className="text-center">
              <div className="text-2xl mb-1">🧪</div>
              <div className="text-xs font-bold text-blue-700">LAB ENGINEER</div>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-1">
            <div className="flex-1"></div>
            <div className="bg-white rounded-lg border-2 border-blue-300 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-blue-700">5. Measure Device</div>
              <div className="text-xs text-gray-600 mt-1">• I-V curves</div>
              <div className="text-xs text-gray-600">• C-V curves</div>
              <div className="text-xs text-gray-600">• S-parameters</div>
            </div>
            <ChevronRight className="text-gray-400" />
            <div className="bg-white rounded-lg border-2 border-blue-300 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-blue-700">6. Upload Data</div>
              <div className="text-xs text-gray-600 mt-1">• Format JSON</div>
              <div className="text-xs text-gray-600">• Add metadata</div>
              <div className="text-xs bg-blue-100 rounded px-1 py-0.5 mt-1">→ Reference Data</div>
            </div>
            <div className="flex items-center gap-2">
              <div className="text-xs text-gray-500 mx-2">OR</div>
            </div>
            <div className="flex-1"></div>
          </div>
        </div>
        
        {/* TCAD Engineer Lane */}
        <div className="flex items-center gap-3">
          <div className="w-32 bg-green-100 rounded-lg p-3 border-2 border-green-300">
            <div className="text-center">
              <div className="text-2xl mb-1">🔬</div>
              <div className="text-xs font-bold text-green-700">TCAD ENGINEER</div>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-1">
            <div className="flex-1"></div>
            <div className="bg-white rounded-lg border-2 border-green-300 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-green-700">5. Run TCAD</div>
              <div className="text-xs text-gray-600 mt-1">• Device physics</div>
              <div className="text-xs text-gray-600">• Sentaurus/Silvaco</div>
              <div className="text-xs text-gray-600">• Extract data</div>
            </div>
            <ChevronRight className="text-gray-400" />
            <div className="bg-white rounded-lg border-2 border-green-300 p-3 min-w-[140px]">
              <div className="text-xs font-bold text-green-700">6. Upload Sims</div>
              <div className="text-xs text-gray-600 mt-1">• Convert format</div>
              <div className="text-xs text-gray-600">• Tag as TCAD</div>
              <div className="text-xs bg-green-100 rounded px-1 py-0.5 mt-1">→ Reference Data</div>
            </div>
            <div className="flex-1"></div>
          </div>
        </div>
      </div>
      
      {/* Interaction Arrows and Notes */}
      <div className="mt-6 p-4 bg-yellow-50 rounded-lg border-2 border-yellow-300">
        <h4 className="text-sm font-bold text-yellow-800 mb-2">Key Interaction Points:</h4>
        <div className="grid grid-cols-4 gap-4 text-xs">
          <div>
            <div className="font-semibold text-yellow-700">Step 2→3:</div>
            <div className="text-gray-600">Request triggers notification to Model Engineer</div>
          </div>
          <div>
            <div className="font-semibold text-yellow-700">Step 5→6:</div>
            <div className="text-gray-600">Lab/TCAD data becomes available in system</div>
          </div>
          <div>
            <div className="font-semibold text-yellow-700">Step 6→7:</div>
            <div className="text-gray-600">Model Engineer accesses uploaded data</div>
          </div>
          <div>
            <div className="font-semibold text-yellow-700">Step 9→10:</div>
            <div className="text-gray-600">Delivery notification to App Engineer</div>
          </div>
        </div>
      </div>
    </div>
  );

  const sections = [
    {
      category: 'Getting Started',
      items: [
        { id: 'overview', title: 'Overview', icon: Home },
        { id: 'presentation', title: 'Technical Presentation', icon: Presentation },
        { id: 'architecture', title: 'System Architecture', icon: Layers },
        { id: 'personas', title: 'User Personas', icon: Users },
        { id: 'quickstart', title: 'Quick Start', icon: Zap },
        { id: 'requirements', title: 'Requirements', icon: AlertCircle },
      ]
    },
    {
      category: 'Data Management',
      items: [
        { id: 'datastructure', title: 'Data Structure', icon: Database },
        { id: 'adddata', title: 'Adding New Data', icon: Package },
        { id: 'templates', title: 'Model Templates', icon: Cpu },
        { id: 'testbenches', title: 'Testbenches', icon: Settings },
      ]
    },
    {
      category: 'Core Features',
      items: [
        { id: 'dashboard', title: 'Dashboard', icon: BarChart3 },
        { id: 'libraries', title: 'Libraries', icon: Database },
        { id: 'mymodels', title: 'My Models', icon: Cpu },
        { id: 'calibration', title: 'Calibration', icon: Settings },
      ]
    },
    {
      category: 'Advanced',
      items: [
        { id: 'workflow', title: 'Workflows', icon: FileText },
        { id: 'reports', title: 'Reports', icon: FileText },
        { id: 'optimization', title: 'Optimization', icon: Zap },
      ]
    },
    {
      category: 'Reference',
      items: [
        { id: 'tips', title: 'Tips & Tricks', icon: Info },
        { id: 'shortcuts', title: 'Shortcuts', icon: HelpCircle },
        { id: 'troubleshooting', title: 'Troubleshooting', icon: AlertCircle },
        { id: 'faq', title: 'FAQ', icon: HelpCircle },
      ]
    }
  ];

  const content: Record<string, React.ReactElement> = {
    overview: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">System Overview</h2>
        <p className="text-gray-600 mb-6">
          The Model Management System is a comprehensive platform designed for managing, calibrating, and deploying electronic component models. 
          It provides engineers with powerful tools to work with compact and behavioral models, enabling efficient calibration against reference data and generation of production-ready outputs.
        </p>
        
        <div className="bg-purple-50 border-l-4 border-purple-600 p-4 mb-6">
          <p className="text-purple-900 font-medium">Welcome!</p>
          <p className="text-purple-700">This guide will help you understand and use all features of the Model Management System effectively.</p>
        </div>

        <h3 className="text-xl font-semibold text-gray-800 mb-4">Key Capabilities</h3>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">📚 Model Library</h4>
            <p className="text-sm text-gray-600">Comprehensive library of model templates including BSIM4, PSP, EKV for MOSFETs.</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">📊 Data Management</h4>
            <p className="text-sm text-gray-600">Import, visualize, and validate measurement data from multiple sources.</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">🎯 Calibration Engine</h4>
            <p className="text-sm text-gray-600">Advanced optimization algorithms including Differential Evolution and Adam.</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">📈 Real-time Visualization</h4>
            <p className="text-sm text-gray-600">Interactive plots with Plotly.js for comprehensive data analysis.</p>
          </div>
        </div>

        <h3 className="text-xl font-semibold text-gray-800 mb-4">Technology Stack</h3>
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
              <th className="p-3 text-left text-sm font-medium">Component</th>
              <th className="p-3 text-left text-sm font-medium">Technology</th>
              <th className="p-3 text-left text-sm font-medium">Purpose</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="p-3 text-sm">Frontend Framework</td>
              <td className="p-3 text-sm">React 19 with TypeScript</td>
              <td className="p-3 text-sm">Core application framework</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm">Styling</td>
              <td className="p-3 text-sm">Tailwind CSS</td>
              <td className="p-3 text-sm">Utility-first CSS framework</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm">Visualization</td>
              <td className="p-3 text-sm">Plotly.js & Recharts</td>
              <td className="p-3 text-sm">Interactive data plotting</td>
            </tr>
          </tbody>
        </table>
      </div>
    ),
    presentation: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Technical Presentation</h2>
        <p className="text-gray-600 mb-6">
          Launch a technical presentation to explain the Electronic Component Modeling Platform to various stakeholders including requestors, modeling engineers, data providers, and managers.
        </p>
        
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-xl p-8 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Technical Presentation Mode</h3>
              <p className="text-gray-600">
                A comprehensive presentation showcasing:
              </p>
              <ul className="mt-3 space-y-1 text-sm text-gray-600">
                <li>• Platform overview and capabilities</li>
                <li>• User personas and their roles</li>
                <li>• System challenges and solutions</li>
                <li>• Technical architecture and workflow</li>
                <li>• Success metrics and benefits</li>
              </ul>
            </div>
            <div className="flex-shrink-0">
              <Presentation className="w-24 h-24 text-purple-400" />
            </div>
          </div>
          
          <button
            onClick={() => setShowPresentation(true)}
            className="flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl"
          >
            <Play className="w-5 h-5" />
            <span className="font-semibold">Launch Presentation</span>
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-purple-600 mb-2">📊 For Managers</h4>
            <p className="text-sm text-gray-600">ROI metrics, efficiency gains, and standardization benefits</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-600 mb-2">👨‍💻 For Engineers</h4>
            <p className="text-sm text-gray-600">Technical architecture, workflows, and automation capabilities</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-green-600 mb-2">🔬 For Lab Teams</h4>
            <p className="text-sm text-gray-600">Data integration, validation, and collaboration features</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-orange-600 mb-2">🎯 For App Teams</h4>
            <p className="text-sm text-gray-600">Model delivery, formats, and integration support</p>
          </div>
        </div>

        <div className="bg-blue-50 border-l-4 border-blue-600 p-4">
          <p className="text-blue-900 font-medium">Presentation Features:</p>
          <ul className="text-blue-700 text-sm mt-2 space-y-1">
            <li>• Auto-play mode with 8-second intervals</li>
            <li>• Manual navigation controls</li>
            <li>• Professional animations and transitions</li>
            <li>• Full-screen optimized layout</li>
          </ul>
        </div>
      </div>
    ),
    architecture: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Complete User Journey & System Architecture</h2>
        
        {/* User Journey Flowchart */}
        <div className="bg-gradient-to-br from-blue-50 via-purple-50 to-green-50 rounded-xl p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Multi-User Interaction Journey</h3>
            <button
              onClick={() => setShowZoomedView(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <ZoomIn className="w-4 h-4" />
              <span className="text-sm">View Full Size</span>
            </button>
          </div>
          
          {/* Journey Flow - Scaled Down Overview */}
          <div className="w-full overflow-hidden">
            <div className="transform scale-[0.6] origin-top-left" style={{ width: '166.67%' }}>
            {/* Timeline Header */}
            <div className="flex items-center justify-between mb-4 px-4">
              <div className="text-sm font-bold text-gray-700">START</div>
              <div className="flex-1 mx-4 h-2 bg-gradient-to-r from-blue-400 via-purple-400 to-green-400 rounded-full"></div>
              <div className="text-sm font-bold text-gray-700">END</div>
            </div>
            
            {/* Swimlanes for each persona */}
            <div className="space-y-3">
              {/* Application Engineer Lane */}
              <div className="flex items-center gap-3">
                <div className="w-32 bg-orange-100 rounded-lg p-3 border-2 border-orange-300">
                  <div className="text-center">
                    <div className="text-2xl mb-1">🎯</div>
                    <div className="text-xs font-bold text-orange-700">APP ENGINEER</div>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-1">
                  <div className="bg-white rounded-lg border-2 border-orange-300 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-orange-700">1. Identify Need</div>
                    <div className="text-xs text-gray-600 mt-1">• New product design</div>
                    <div className="text-xs text-gray-600">• Model requirement</div>
                  </div>
                  <ChevronRight className="text-gray-400" />
                  <div className="bg-white rounded-lg border-2 border-orange-300 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-orange-700">2. Create Request</div>
                    <div className="text-xs text-gray-600 mt-1">• Specify device type</div>
                    <div className="text-xs text-gray-600">• Set requirements</div>
                    <div className="text-xs bg-orange-100 rounded px-1 py-0.5 mt-1">→ Requests Page</div>
                  </div>
                  <div className="flex-1"></div>
                  <div className="bg-white rounded-lg border-2 border-orange-300 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-orange-700">10. Review Model</div>
                    <div className="text-xs text-gray-600 mt-1">• Validate results</div>
                    <div className="text-xs text-gray-600">• Accept/Reject</div>
                  </div>
                  <ChevronRight className="text-gray-400" />
                  <div className="bg-orange-200 rounded-lg border-2 border-orange-400 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-orange-800">11. Use in Design</div>
                    <div className="text-xs text-gray-700 mt-1">• Download model</div>
                    <div className="text-xs text-gray-700">• Integrate in flow</div>
                    <div className="text-xs font-bold mt-1">✅ COMPLETE</div>
                  </div>
                </div>
              </div>
              
              {/* Model Engineer Lane */}
              <div className="flex items-center gap-3">
                <div className="w-32 bg-purple-100 rounded-lg p-3 border-2 border-purple-300">
                  <div className="text-center">
                    <div className="text-2xl mb-1">💻</div>
                    <div className="text-xs font-bold text-purple-700">MODEL ENGINEER</div>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-1">
                  <div className="flex-1"></div>
                  <div className="bg-purple-200 rounded-lg border-2 border-purple-400 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-purple-800">3. Receive Request</div>
                    <div className="text-xs text-gray-700 mt-1">🔔 Notification</div>
                    <div className="text-xs text-gray-700">• Review specs</div>
                  </div>
                  <ChevronRight className="text-gray-400" />
                  <div className="bg-white rounded-lg border-2 border-purple-300 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-purple-700">4. Select Template</div>
                    <div className="text-xs text-gray-600 mt-1">• Choose BSIM4/PSP</div>
                    <div className="text-xs bg-purple-100 rounded px-1 py-0.5 mt-1">→ Libraries</div>
                  </div>
                  <ChevronRight className="text-gray-400" />
                  <div className="bg-white rounded-lg border-2 border-purple-300 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-purple-700">7. Load Data</div>
                    <div className="text-xs text-gray-600 mt-1">• Select reference</div>
                    <div className="text-xs text-gray-600">• Validate quality</div>
                  </div>
                  <ChevronRight className="text-gray-400" />
                  <div className="bg-white rounded-lg border-2 border-purple-300 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-purple-700">8. Calibrate</div>
                    <div className="text-xs text-gray-600 mt-1">• Set parameters</div>
                    <div className="text-xs text-gray-600">• Run optimization</div>
                    <div className="text-xs bg-purple-100 rounded px-1 py-0.5 mt-1">→ My Models</div>
                  </div>
                  <ChevronRight className="text-gray-400" />
                  <div className="bg-white rounded-lg border-2 border-purple-300 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-purple-700">9. Export</div>
                    <div className="text-xs text-gray-600 mt-1">• Generate SPICE</div>
                    <div className="text-xs text-gray-600">• Create package</div>
                    <div className="text-xs bg-purple-100 rounded px-1 py-0.5 mt-1">📦 Deliver</div>
                  </div>
                </div>
              </div>
              
              {/* Lab Engineer Lane */}
              <div className="flex items-center gap-3">
                <div className="w-32 bg-blue-100 rounded-lg p-3 border-2 border-blue-300">
                  <div className="text-center">
                    <div className="text-2xl mb-1">🧪</div>
                    <div className="text-xs font-bold text-blue-700">LAB ENGINEER</div>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-1">
                  <div className="flex-1"></div>
                  <div className="bg-white rounded-lg border-2 border-blue-300 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-blue-700">5. Measure Device</div>
                    <div className="text-xs text-gray-600 mt-1">• I-V curves</div>
                    <div className="text-xs text-gray-600">• C-V curves</div>
                    <div className="text-xs text-gray-600">• S-parameters</div>
                  </div>
                  <ChevronRight className="text-gray-400" />
                  <div className="bg-white rounded-lg border-2 border-blue-300 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-blue-700">6. Upload Data</div>
                    <div className="text-xs text-gray-600 mt-1">• Format JSON</div>
                    <div className="text-xs text-gray-600">• Add metadata</div>
                    <div className="text-xs bg-blue-100 rounded px-1 py-0.5 mt-1">→ Reference Data</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-xs text-gray-500 mx-2">OR</div>
                  </div>
                  <div className="flex-1"></div>
                </div>
              </div>
              
              {/* TCAD Engineer Lane */}
              <div className="flex items-center gap-3">
                <div className="w-32 bg-green-100 rounded-lg p-3 border-2 border-green-300">
                  <div className="text-center">
                    <div className="text-2xl mb-1">🔬</div>
                    <div className="text-xs font-bold text-green-700">TCAD ENGINEER</div>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-1">
                  <div className="flex-1"></div>
                  <div className="bg-white rounded-lg border-2 border-green-300 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-green-700">5. Run TCAD</div>
                    <div className="text-xs text-gray-600 mt-1">• Device physics</div>
                    <div className="text-xs text-gray-600">• Sentaurus/Silvaco</div>
                    <div className="text-xs text-gray-600">• Extract data</div>
                  </div>
                  <ChevronRight className="text-gray-400" />
                  <div className="bg-white rounded-lg border-2 border-green-300 p-3 min-w-[140px]">
                    <div className="text-xs font-bold text-green-700">6. Upload Sims</div>
                    <div className="text-xs text-gray-600 mt-1">• Convert format</div>
                    <div className="text-xs text-gray-600">• Tag as TCAD</div>
                    <div className="text-xs bg-green-100 rounded px-1 py-0.5 mt-1">→ Reference Data</div>
                  </div>
                  <div className="flex-1"></div>
                </div>
              </div>
            </div>
            
            {/* Interaction Arrows and Notes */}
            <div className="mt-6 p-4 bg-yellow-50 rounded-lg border-2 border-yellow-300">
              <h4 className="text-sm font-bold text-yellow-800 mb-2">Key Interaction Points:</h4>
              <div className="grid grid-cols-4 gap-4 text-xs">
                <div>
                  <div className="font-semibold text-yellow-700">Step 2→3:</div>
                  <div className="text-gray-600">Request triggers notification to Model Engineer</div>
                </div>
                <div>
                  <div className="font-semibold text-yellow-700">Step 5→6:</div>
                  <div className="text-gray-600">Lab/TCAD data becomes available in system</div>
                </div>
                <div>
                  <div className="font-semibold text-yellow-700">Step 6→7:</div>
                  <div className="text-gray-600">Model Engineer accesses uploaded data</div>
                </div>
                <div>
                  <div className="font-semibold text-yellow-700">Step 9→10:</div>
                  <div className="text-gray-600">Delivery notification to App Engineer</div>
                </div>
              </div>
            </div>
            </div>
          </div>
        </div>

        <h2 className="text-xl font-bold text-gray-900 mb-4">System Architecture - Complete Block Diagram</h2>
        
        {/* Main Architecture Block Diagram */}
        <div className="bg-gradient-to-br from-blue-50 via-purple-50 to-green-50 rounded-xl p-8 mb-6 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-full opacity-5">
            <div className="absolute top-10 left-10 w-32 h-32 bg-purple-600 rounded-full blur-3xl"></div>
            <div className="absolute bottom-10 right-10 w-40 h-40 bg-blue-600 rounded-full blur-3xl"></div>
          </div>
          
          <div className="relative">
            {/* User Personas Row */}
            <div className="mb-6">
              <div className="bg-white/90 backdrop-blur rounded-lg border-2 border-gray-300 p-4">
                <h3 className="text-sm font-bold text-gray-700 mb-3 text-center">USER PERSONAS & ENTRY POINTS</h3>
                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-blue-100 rounded-lg p-3 text-center border-2 border-blue-300">
                    <div className="text-2xl mb-1">🧪</div>
                    <div className="text-xs font-bold text-blue-700">LAB ENGINEER</div>
                    <div className="text-xs text-gray-600 mt-1">Uploads Measurements</div>
                    <div className="mt-2 text-xs bg-blue-200 rounded px-2 py-1">→ Reference Data</div>
                  </div>
                  <div className="bg-purple-100 rounded-lg p-3 text-center border-2 border-purple-300">
                    <div className="text-2xl mb-1">💻</div>
                    <div className="text-xs font-bold text-purple-700">MODEL ENGINEER</div>
                    <div className="text-xs text-gray-600 mt-1">Calibrates Models</div>
                    <div className="mt-2 text-xs bg-purple-200 rounded px-2 py-1">→ My Models</div>
                  </div>
                  <div className="bg-green-100 rounded-lg p-3 text-center border-2 border-green-300">
                    <div className="text-2xl mb-1">🔬</div>
                    <div className="text-xs font-bold text-green-700">TCAD ENGINEER</div>
                    <div className="text-xs text-gray-600 mt-1">Provides Simulations</div>
                    <div className="mt-2 text-xs bg-green-200 rounded px-2 py-1">→ Reference Data</div>
                  </div>
                  <div className="bg-orange-100 rounded-lg p-3 text-center border-2 border-orange-300">
                    <div className="text-2xl mb-1">🎯</div>
                    <div className="text-xs font-bold text-orange-700">APP ENGINEER</div>
                    <div className="text-xs text-gray-600 mt-1">Requests Models</div>
                    <div className="mt-2 text-xs bg-orange-200 rounded px-2 py-1">→ Requests</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Flow Arrows */}
            <div className="flex justify-center mb-2">
              <div className="text-gray-400">
                <ChevronRight className="w-6 h-6 rotate-90" />
              </div>
            </div>

            {/* Application Layer */}
            <div className="mb-6">
              <div className="bg-white/90 backdrop-blur rounded-lg border-2 border-indigo-400 p-4">
                <h3 className="text-sm font-bold text-indigo-700 mb-3 text-center">APPLICATION LAYER (React Components)</h3>
                <div className="grid grid-cols-5 gap-3">
                  <div className="bg-indigo-50 rounded p-2 text-center border border-indigo-200">
                    <BarChart3 className="w-5 h-5 mx-auto mb-1 text-indigo-600" />
                    <div className="text-xs font-semibold">Dashboard</div>
                    <div className="text-xs text-gray-500">Metrics & Activity</div>
                  </div>
                  <div className="bg-indigo-50 rounded p-2 text-center border border-indigo-200">
                    <Database className="w-5 h-5 mx-auto mb-1 text-indigo-600" />
                    <div className="text-xs font-semibold">Libraries</div>
                    <div className="text-xs text-gray-500">Templates & Data</div>
                  </div>
                  <div className="bg-indigo-50 rounded p-2 text-center border border-indigo-200">
                    <Cpu className="w-5 h-5 mx-auto mb-1 text-indigo-600" />
                    <div className="text-xs font-semibold">My Models</div>
                    <div className="text-xs text-gray-500">Calibration UI</div>
                  </div>
                  <div className="bg-indigo-50 rounded p-2 text-center border border-indigo-200">
                    <FileText className="w-5 h-5 mx-auto mb-1 text-indigo-600" />
                    <div className="text-xs font-semibold">Requests</div>
                    <div className="text-xs text-gray-500">Task Queue</div>
                  </div>
                  <div className="bg-indigo-50 rounded p-2 text-center border border-indigo-200">
                    <Shield className="w-5 h-5 mx-auto mb-1 text-indigo-600" />
                    <div className="text-xs font-semibold">Auth</div>
                    <div className="text-xs text-gray-500">Access Control</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Flow Arrows */}
            <div className="flex justify-center mb-2">
              <div className="text-gray-400">
                <ChevronRight className="w-6 h-6 rotate-90" />
              </div>
            </div>

            {/* Service/Processing Layer */}
            <div className="mb-6">
              <div className="bg-white/90 backdrop-blur rounded-lg border-2 border-purple-400 p-4">
                <h3 className="text-sm font-bold text-purple-700 mb-3 text-center">PROCESSING & SERVICE LAYER</h3>
                <div className="grid grid-cols-3 gap-4">
                  {/* Data Service */}
                  <div className="bg-purple-50 rounded-lg p-3 border border-purple-300">
                    <div className="text-center mb-2">
                      <Settings className="w-6 h-6 mx-auto text-purple-600" />
                      <div className="text-xs font-bold text-purple-700 mt-1">DATA SERVICE</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-xs bg-white rounded px-2 py-1">• CRUD Operations</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• Data Validation</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• Format Conversion</div>
                      <div className="text-xs font-mono bg-gray-100 rounded px-2 py-1 mt-2">dataService.ts</div>
                    </div>
                  </div>

                  {/* Calibration Engine */}
                  <div className="bg-pink-50 rounded-lg p-3 border border-pink-300">
                    <div className="text-center mb-2">
                      <Zap className="w-6 h-6 mx-auto text-pink-600" />
                      <div className="text-xs font-bold text-pink-700 mt-1">CALIBRATION ENGINE</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-xs bg-white rounded px-2 py-1">• Differential Evolution</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• Adam Optimizer</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• Nelder-Mead</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• Real-time Fitting</div>
                    </div>
                  </div>

                  {/* Export Service */}
                  <div className="bg-cyan-50 rounded-lg p-3 border border-cyan-300">
                    <div className="text-center mb-2">
                      <Package className="w-6 h-6 mx-auto text-cyan-600" />
                      <div className="text-xs font-bold text-cyan-700 mt-1">EXPORT SERVICE</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-xs bg-white rounded px-2 py-1">• SPICE Netlist</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• Verilog-A</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• JSON/CSV</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• ZIP Packages</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Flow Arrows */}
            <div className="flex justify-center mb-2">
              <div className="text-gray-400">
                <ChevronRight className="w-6 h-6 rotate-90" />
              </div>
            </div>

            {/* Data Storage Layer */}
            <div className="mb-6">
              <div className="bg-white/90 backdrop-blur rounded-lg border-2 border-green-400 p-4">
                <h3 className="text-sm font-bold text-green-700 mb-3 text-center">DATA STORAGE LAYER (JSON Files)</h3>
                <div className="grid grid-cols-4 gap-3">
                  <div className="bg-blue-50 rounded-lg p-3 border border-blue-300">
                    <div className="text-center">
                      <div className="text-xl mb-1">📘</div>
                      <div className="text-xs font-bold text-blue-700">MODEL TEMPLATES</div>
                    </div>
                    <div className="mt-2 space-y-1">
                      <div className="text-xs bg-white rounded px-2 py-1">• BSIM4</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• PSP</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• EKV</div>
                      <div className="text-xs font-mono bg-gray-100 rounded px-1 py-1 mt-2">model-templates/</div>
                    </div>
                  </div>
                  
                  <div className="bg-green-50 rounded-lg p-3 border border-green-300">
                    <div className="text-center">
                      <div className="text-xl mb-1">📊</div>
                      <div className="text-xs font-bold text-green-700">REFERENCE DATA</div>
                    </div>
                    <div className="mt-2 space-y-1">
                      <div className="text-xs bg-white rounded px-2 py-1">• Measurements</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• TCAD Sims</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• I-V/C-V Data</div>
                      <div className="text-xs font-mono bg-gray-100 rounded px-1 py-1 mt-2">reference-data/</div>
                    </div>
                  </div>
                  
                  <div className="bg-purple-50 rounded-lg p-3 border border-purple-300">
                    <div className="text-center">
                      <div className="text-xl mb-1">🔧</div>
                      <div className="text-xs font-bold text-purple-700">TESTBENCHES</div>
                    </div>
                    <div className="mt-2 space-y-1">
                      <div className="text-xs bg-white rounded px-2 py-1">• DC Sweep</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• AC Analysis</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• Transient</div>
                      <div className="text-xs font-mono bg-gray-100 rounded px-1 py-1 mt-2">testbenches/</div>
                    </div>
                  </div>
                  
                  <div className="bg-orange-50 rounded-lg p-3 border border-orange-300">
                    <div className="text-center">
                      <div className="text-xl mb-1">✅</div>
                      <div className="text-xs font-bold text-orange-700">CALIBRATED</div>
                    </div>
                    <div className="mt-2 space-y-1">
                      <div className="text-xs bg-white rounded px-2 py-1">• Final Models</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• Parameters</div>
                      <div className="text-xs bg-white rounded px-2 py-1">• Metadata</div>
                      <div className="text-xs font-mono bg-gray-100 rounded px-1 py-1 mt-2">calibrated-models/</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Process Flow Timeline */}
            <div className="bg-white/90 backdrop-blur rounded-lg border-2 border-yellow-400 p-4">
              <h3 className="text-sm font-bold text-yellow-700 mb-3 text-center">END-TO-END PROCESS FLOW</h3>
              <div className="relative">
                {/* Timeline Bar */}
                <div className="absolute top-8 left-0 right-0 h-2 bg-gradient-to-r from-blue-400 via-purple-400 to-green-400 rounded-full"></div>
                
                {/* Process Steps */}
                <div className="relative grid grid-cols-4 gap-4 pt-4">
                  <div className="text-center">
                    <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mx-auto mb-2 font-bold text-sm">1</div>
                    <div className="bg-blue-50 rounded p-2 border border-blue-200">
                      <div className="text-xs font-bold text-blue-700">REQUEST</div>
                      <div className="text-xs text-gray-600 mt-1">App Engineer creates request</div>
                      <div className="text-xs bg-blue-100 rounded px-1 py-0.5 mt-1">🔔 Notify team</div>
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <div className="w-8 h-8 bg-purple-500 text-white rounded-full flex items-center justify-center mx-auto mb-2 font-bold text-sm">2</div>
                    <div className="bg-purple-50 rounded p-2 border border-purple-200">
                      <div className="text-xs font-bold text-purple-700">DATA PREP</div>
                      <div className="text-xs text-gray-600 mt-1">Upload & validate data</div>
                      <div className="text-xs bg-purple-100 rounded px-1 py-0.5 mt-1">✓ Quality check</div>
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <div className="w-8 h-8 bg-indigo-500 text-white rounded-full flex items-center justify-center mx-auto mb-2 font-bold text-sm">3</div>
                    <div className="bg-indigo-50 rounded p-2 border border-indigo-200">
                      <div className="text-xs font-bold text-indigo-700">CALIBRATE</div>
                      <div className="text-xs text-gray-600 mt-1">Optimize parameters</div>
                      <div className="text-xs bg-indigo-100 rounded px-1 py-0.5 mt-1">⚡ Auto-fit</div>
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center mx-auto mb-2 font-bold text-sm">4</div>
                    <div className="bg-green-50 rounded p-2 border border-green-200">
                      <div className="text-xs font-bold text-green-700">DELIVER</div>
                      <div className="text-xs text-gray-600 mt-1">Export & download</div>
                      <div className="text-xs bg-green-100 rounded px-1 py-0.5 mt-1">📦 Complete</div>
                    </div>
                  </div>
                </div>
                
                {/* Timeline */}
                <div className="grid grid-cols-4 gap-4 mt-3 text-center">
                  <div className="text-xs text-gray-500">Day 1</div>
                  <div className="text-xs text-gray-500">Day 2-3</div>
                  <div className="text-xs text-gray-500">Day 4-5</div>
                  <div className="text-xs text-gray-500">Day 6</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Key Features Summary */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-blue-50 border-l-4 border-blue-600 p-3">
            <p className="text-blue-900 font-medium text-sm">Data Management</p>
            <p className="text-blue-700 text-xs mt-1">Centralized storage with JSON-based configuration for all model templates, reference data, and testbenches.</p>
          </div>
          <div className="bg-purple-50 border-l-4 border-purple-600 p-3">
            <p className="text-purple-900 font-medium text-sm">Automated Workflow</p>
            <p className="text-purple-700 text-xs mt-1">End-to-end automation from request creation to model delivery with real-time notifications.</p>
          </div>
          <div className="bg-green-50 border-l-4 border-green-600 p-3">
            <p className="text-green-900 font-medium text-sm">Multi-Format Export</p>
            <p className="text-green-700 text-xs mt-1">Support for SPICE, Verilog-A, JSON, and CSV formats for maximum compatibility.</p>
          </div>
        </div>
      </div>
    ),
    personas: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">User Personas & Workflows</h2>
        
        <div className="space-y-6">
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-700 mb-3">🧪 Lab Engineer</h3>
            <p className="text-sm text-gray-600 mb-3">Responsible for device measurements and data quality</p>
            <h4 className="font-semibold text-gray-800 mb-2">Workflow:</h4>
            <ol className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="font-bold text-blue-600 mr-2">1.</span>
                <div>
                  <strong>Perform Measurements:</strong> Use lab equipment to measure device characteristics (I-V, C-V, S-parameters)
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-blue-600 mr-2">2.</span>
                <div>
                  <strong>Format Data:</strong> Convert to JSON format with device metadata
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-blue-600 mr-2">3.</span>
                <div>
                  <strong>Upload:</strong> Go to Libraries → Reference Data → Upload New Dataset
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-blue-600 mr-2">4.</span>
                <div>
                  <strong>Validate:</strong> Review plots, check for outliers, ensure completeness
                </div>
              </li>
            </ol>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-purple-700 mb-3">💻 Model Engineer</h3>
            <p className="text-sm text-gray-600 mb-3">Performs model calibration and optimization</p>
            <h4 className="font-semibold text-gray-800 mb-2">Workflow:</h4>
            <ol className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="font-bold text-purple-600 mr-2">1.</span>
                <div>
                  <strong>Review Request:</strong> Check Requests page for new model requirements
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-purple-600 mr-2">2.</span>
                <div>
                  <strong>Select Template:</strong> Choose model from Libraries → Model Templates
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-purple-600 mr-2">3.</span>
                <div>
                  <strong>Load Data:</strong> Select reference data for target device
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-purple-600 mr-2">4.</span>
                <div>
                  <strong>Calibrate:</strong> My Models → New Calibration, run optimization
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-purple-600 mr-2">5.</span>
                <div>
                  <strong>Export:</strong> Generate SPICE/Verilog-A, update request status
                </div>
              </li>
            </ol>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-green-700 mb-3">🔬 TCAD Engineer</h3>
            <p className="text-sm text-gray-600 mb-3">Provides simulation data from TCAD tools</p>
            <h4 className="font-semibold text-gray-800 mb-2">Workflow:</h4>
            <ol className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="font-bold text-green-600 mr-2">1.</span>
                <div>
                  <strong>Run Simulations:</strong> Use Sentaurus/Silvaco for device physics
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-green-600 mr-2">2.</span>
                <div>
                  <strong>Extract Data:</strong> Generate I-V, C-V characteristics
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-green-600 mr-2">3.</span>
                <div>
                  <strong>Format:</strong> Convert to JSON matching measurement structure
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-green-600 mr-2">4.</span>
                <div>
                  <strong>Upload:</strong> Add to Reference Library with "TCAD" tag
                </div>
              </li>
            </ol>
          </div>
          
          <div className="bg-orange-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-orange-700 mb-3">🎯 Application Engineer</h3>
            <p className="text-sm text-gray-600 mb-3">Requests models and validates deliverables</p>
            <h4 className="font-semibold text-gray-800 mb-2">Workflow:</h4>
            <ol className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="font-bold text-orange-600 mr-2">1.</span>
                <div>
                  <strong>Create Request:</strong> Specify device type, technology, requirements
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-orange-600 mr-2">2.</span>
                <div>
                  <strong>Define Specs:</strong> Set accuracy targets, corners, temperature ranges
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-orange-600 mr-2">3.</span>
                <div>
                  <strong>Track Progress:</strong> Monitor status, receive notifications
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-orange-600 mr-2">4.</span>
                <div>
                  <strong>Review & Accept:</strong> Validate model, provide feedback, download
                </div>
              </li>
            </ol>
          </div>
        </div>
      </div>
    ),
    process: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">End-to-End Process Flow</h2>
        
        <div className="bg-gradient-to-r from-blue-50 via-purple-50 to-green-50 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Model Development Pipeline</h3>
          
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">1</div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-800">Request Created</h4>
                <p className="text-sm text-gray-600">Application engineer submits model request with specifications</p>
                <p className="text-xs text-blue-600 mt-1">🔔 Model team notified automatically</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="bg-purple-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">2</div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-800">Data Preparation</h4>
                <p className="text-sm text-gray-600">Lab/TCAD engineer uploads reference data</p>
                <p className="text-xs text-purple-600 mt-1">✓ Data validated for quality and completeness</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="bg-indigo-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">3</div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-800">Model Calibration</h4>
                <p className="text-sm text-gray-600">Model engineer performs fitting and optimization</p>
                <p className="text-xs text-indigo-600 mt-1">⚡ Automated optimization with real-time progress</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="bg-green-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold">4</div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-800">Delivery & Validation</h4>
                <p className="text-sm text-gray-600">Calibrated model exported and delivered to requester</p>
                <p className="text-xs text-green-600 mt-1">📦 Multiple export formats available</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-md font-semibold text-gray-700 mb-3">Typical Timeline</h3>
          <div className="grid grid-cols-4 gap-4 text-sm">
            <div>
              <div className="font-semibold text-gray-700">Day 1</div>
              <div className="text-xs text-gray-600">Request submitted</div>
            </div>
            <div>
              <div className="font-semibold text-gray-700">Day 2-3</div>
              <div className="text-xs text-gray-600">Data collection</div>
            </div>
            <div>
              <div className="font-semibold text-gray-700">Day 4-5</div>
              <div className="text-xs text-gray-600">Model calibration</div>
            </div>
            <div>
              <div className="font-semibold text-gray-700">Day 6</div>
              <div className="text-xs text-gray-600">Delivery & validation</div>
            </div>
          </div>
        </div>
        
        <div className="bg-yellow-50 border-l-4 border-yellow-600 p-4 mt-6">
          <p className="text-yellow-900 font-medium">Notification System</p>
          <ul className="text-yellow-700 text-sm mt-2 space-y-1">
            <li>• New requests trigger immediate notifications to model engineers</li>
            <li>• Status updates automatically sent to requesters</li>
            <li>• Completion alerts include download links</li>
            <li>• Issues or delays communicated through request comments</li>
          </ul>
        </div>
      </div>
    ),
    datastructure: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Data Structure & Storage</h2>
        
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">File Organization</h3>
          <pre className="font-mono text-sm text-gray-700">
src/data/
├── model-templates/
│   ├── bsim4/
│   │   └── metadata.json
│   ├── psp/
│   │   └── metadata.json
│   └── ekv/
│       └── metadata.json
├── reference-data/
│   ├── nmos_65nm.json
│   ├── pmos_65nm.json
│   └── ...
├── testbenches/
│   ├── dc_sweep.json
│   ├── ac_analysis.json
│   └── ...
└── calibrated-models/
    ├── model_001/
    │   ├── metadata.json
    │   └── parameters.json
    └── ...
          </pre>
        </div>
        
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">JSON Data Formats</h3>
            
            <div className="bg-white border border-gray-300 rounded-lg p-3 mb-3">
              <h4 className="font-semibold text-gray-700 mb-2">Reference Data Structure</h4>
              <pre className="font-mono text-xs bg-gray-50 p-2 rounded">{`{
  "data_id": "unique_identifier",
  "name": "Device Name",
  "device_info": {
    "type": "NMOS",
    "technology": "65nm",
    "temperature": 25
  },
  "data": [
    {
      "page": "id_vg",
      "curves": [...]
    }
  ]
}`}</pre>
            </div>
            
            <div className="bg-white border border-gray-300 rounded-lg p-3">
              <h4 className="font-semibold text-gray-700 mb-2">Model Template Structure</h4>
              <pre className="font-mono text-xs bg-gray-50 p-2 rounded">{`{
  "model_id": "bsim4",
  "name": "BSIM4",
  "version": "4.8.2",
  "parameters": [
    {
      "name": "VTH0",
      "default": 0.7,
      "min": 0.3,
      "max": 1.2,
      "unit": "V"
    }
  ]
}`}</pre>
            </div>
          </div>
        </div>
      </div>
    ),
    adddata: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Adding New Data to the System</h2>
        
        <div className="space-y-6">
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-700 mb-3">📝 Adding a New Model Template</h3>
            <ol className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="font-bold text-blue-600 mr-2">1.</span>
                <div>
                  <strong>Create folder:</strong> Add new directory in <code className="bg-white px-1 rounded">src/data/model-templates/</code>
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-blue-600 mr-2">2.</span>
                <div>
                  <strong>Add metadata.json:</strong> Define model structure with all parameters
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-blue-600 mr-2">3.</span>
                <div>
                  <strong>Set defaults:</strong> Include default values and valid ranges for each parameter
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-blue-600 mr-2">4.</span>
                <div>
                  <strong>Import in dataService:</strong> Add import statement in <code className="bg-white px-1 rounded">dataService.ts</code>
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-blue-600 mr-2">5.</span>
                <div>
                  <strong>Verify:</strong> Template automatically appears in Libraries → Model Templates
                </div>
              </li>
            </ol>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-green-700 mb-3">📊 Adding Reference Data</h3>
            <h4 className="font-semibold text-gray-700 mb-2">Option 1: Via UI Upload</h4>
            <ol className="space-y-2 text-sm mb-4">
              <li className="flex items-start">
                <span className="font-bold text-green-600 mr-2">1.</span>
                <div>Navigate to Libraries → Reference Data</div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-green-600 mr-2">2.</span>
                <div>Click "Upload New Dataset"</div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-green-600 mr-2">3.</span>
                <div>Select file (CSV, JSON, S2P supported)</div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-green-600 mr-2">4.</span>
                <div>Add metadata and validate</div>
              </li>
            </ol>
            
            <h4 className="font-semibold text-gray-700 mb-2">Option 2: Direct File Addition</h4>
            <ol className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="font-bold text-green-600 mr-2">1.</span>
                <div>Format data as JSON following the structure</div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-green-600 mr-2">2.</span>
                <div>Save to <code className="bg-white px-1 rounded">src/data/reference-data/</code></div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-green-600 mr-2">3.</span>
                <div>Import in dataService.ts</div>
              </li>
            </ol>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-purple-700 mb-3">🔧 Adding a New Testbench</h3>
            <ol className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="font-bold text-purple-600 mr-2">1.</span>
                <div>
                  <strong>Define circuit:</strong> Create circuit configuration JSON
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-purple-600 mr-2">2.</span>
                <div>
                  <strong>Specify analysis:</strong> Set analysis type (DC, AC, transient)
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-purple-600 mr-2">3.</span>
                <div>
                  <strong>Configure sweeps:</strong> Define parameter sweep ranges
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-purple-600 mr-2">4.</span>
                <div>
                  <strong>Save file:</strong> Add to <code className="bg-white px-1 rounded">src/data/testbenches/</code>
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-bold text-purple-600 mr-2">5.</span>
                <div>
                  <strong>Use in calibration:</strong> Available in Simulations tab
                </div>
              </li>
            </ol>
          </div>
        </div>
        
        <div className="bg-yellow-50 border-l-4 border-yellow-600 p-4 mt-6">
          <p className="text-yellow-900 font-medium">Important Notes</p>
          <ul className="text-yellow-700 text-sm mt-2 space-y-1">
            <li>• Always validate JSON syntax before adding files</li>
            <li>• Include comprehensive metadata for traceability</li>
            <li>• Follow existing naming conventions</li>
            <li>• Test data import after adding new files</li>
          </ul>
        </div>
      </div>
    ),
    templates: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Model Templates</h2>
        <p className="text-gray-600 mb-6">Pre-configured model structures for various component types.</p>
        
        <div className="space-y-4">
          <div className="bg-white border border-gray-300 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-purple-700 mb-3">Available Templates</h3>
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 text-sm font-semibold text-gray-700">Model</th>
                  <th className="text-left py-2 text-sm font-semibold text-gray-700">Version</th>
                  <th className="text-left py-2 text-sm font-semibold text-gray-700">Parameters</th>
                  <th className="text-left py-2 text-sm font-semibold text-gray-700">Use Case</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="py-2 text-sm">BSIM4</td>
                  <td className="py-2 text-sm">4.8.2</td>
                  <td className="py-2 text-sm">400+</td>
                  <td className="py-2 text-sm">Industry standard for digital/analog</td>
                </tr>
                <tr className="border-b">
                  <td className="py-2 text-sm">PSP</td>
                  <td className="py-2 text-sm">103.4</td>
                  <td className="py-2 text-sm">200+</td>
                  <td className="py-2 text-sm">Surface potential based</td>
                </tr>
                <tr className="border-b">
                  <td className="py-2 text-sm">EKV</td>
                  <td className="py-2 text-sm">3.0</td>
                  <td className="py-2 text-sm">50+</td>
                  <td className="py-2 text-sm">All-region continuous model</td>
                </tr>
                <tr className="border-b">
                  <td className="py-2 text-sm">BSIM-CMG</td>
                  <td className="py-2 text-sm">110.0</td>
                  <td className="py-2 text-sm">300+</td>
                  <td className="py-2 text-sm">FinFET and multi-gate</td>
                </tr>
                <tr className="border-b">
                  <td className="py-2 text-sm">HiSIM</td>
                  <td className="py-2 text-sm">2.8.0</td>
                  <td className="py-2 text-sm">150+</td>
                  <td className="py-2 text-sm">High-speed applications</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div className="bg-blue-50 border-l-4 border-blue-600 p-4">
            <p className="text-blue-900 font-medium">Template Selection Guide</p>
            <ul className="text-blue-700 text-sm mt-2 space-y-1">
              <li>• <strong>BSIM4:</strong> Best for planar CMOS, widely supported</li>
              <li>• <strong>PSP:</strong> Accurate for RF and analog design</li>
              <li>• <strong>EKV:</strong> Excellent for low-power applications</li>
              <li>• <strong>BSIM-CMG:</strong> Required for FinFET technologies</li>
            </ul>
          </div>
        </div>
      </div>
    ),
    testbenches: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Testbench Configuration</h2>
        <p className="text-gray-600 mb-6">Predefined circuit setups for model validation and calibration.</p>
        
        <div className="space-y-4">
          <div className="bg-white border border-gray-300 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-purple-700 mb-3">Standard Testbenches</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 p-3 rounded">
                <h4 className="font-semibold text-gray-700 mb-2">DC Analysis</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Id-Vg sweep (transfer characteristics)</li>
                  <li>• Id-Vd sweep (output characteristics)</li>
                  <li>• Threshold voltage extraction</li>
                  <li>• Subthreshold slope measurement</li>
                </ul>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <h4 className="font-semibold text-gray-700 mb-2">AC Analysis</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• C-V measurements</li>
                  <li>• S-parameter extraction</li>
                  <li>• Frequency response</li>
                  <li>• Noise figure analysis</li>
                </ul>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <h4 className="font-semibold text-gray-700 mb-2">Transient Analysis</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Ring oscillator simulation</li>
                  <li>• Inverter delay measurement</li>
                  <li>• Rise/fall time extraction</li>
                  <li>• Power consumption analysis</li>
                </ul>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <h4 className="font-semibold text-gray-700 mb-2">Temperature Sweep</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• -40°C to 125°C range</li>
                  <li>• Temperature coefficients</li>
                  <li>• Thermal stability</li>
                  <li>• Parameter variation</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 border-l-4 border-green-600 p-4">
            <p className="text-green-900 font-medium">Custom Testbench Creation</p>
            <p className="text-green-700 text-sm mt-2">You can create custom testbenches by defining circuit topology, bias conditions, and sweep parameters in JSON format. Upload through the Testbench Library interface.</p>
          </div>
        </div>
      </div>
    ),
    quickstart: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Start Guide</h2>
        <p className="text-gray-600 mb-6">Get up and running with the Model Management System in just a few minutes.</p>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Initial Setup</h3>
        <ol className="space-y-4 mb-6">
          <li className="flex">
            <span className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold mr-3">1</span>
            <div>
              <p className="font-semibold text-gray-800">Login to the System</p>
              <p className="text-gray-600">Access the application and login with your credentials.</p>
            </div>
          </li>
          <li className="flex">
            <span className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold mr-3">2</span>
            <div>
              <p className="font-semibold text-gray-800">Navigate to Dashboard</p>
              <p className="text-gray-600">Review system statistics and recent activities.</p>
            </div>
          </li>
          <li className="flex">
            <span className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold mr-3">3</span>
            <div>
              <p className="font-semibold text-gray-800">Import Reference Data</p>
              <p className="text-gray-600">Go to Libraries → Reference Data and upload your measurement files.</p>
            </div>
          </li>
          <li className="flex">
            <span className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold mr-3">4</span>
            <div>
              <p className="font-semibold text-gray-800">Create Calibration Task</p>
              <p className="text-gray-600">Navigate to My Models and click "New Calibration Task" to start.</p>
            </div>
          </li>
        </ol>

        <div className="bg-green-50 border-l-4 border-green-600 p-4">
          <p className="text-green-900 font-medium">Quick Tip</p>
          <p className="text-green-700">Use the sample data provided in the system to familiarize yourself with the calibration process before working with actual data.</p>
        </div>
      </div>
    ),
    requirements: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">System Requirements</h2>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Browser Requirements</h3>
        <table className="w-full border-collapse mb-6">
          <thead>
            <tr className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
              <th className="p-3 text-left text-sm font-medium">Browser</th>
              <th className="p-3 text-left text-sm font-medium">Minimum Version</th>
              <th className="p-3 text-left text-sm font-medium">Recommended</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="p-3 text-sm">Google Chrome</td>
              <td className="p-3 text-sm">90+</td>
              <td className="p-3 text-sm">Latest stable</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm">Mozilla Firefox</td>
              <td className="p-3 text-sm">88+</td>
              <td className="p-3 text-sm">Latest stable</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm">Microsoft Edge</td>
              <td className="p-3 text-sm">90+</td>
              <td className="p-3 text-sm">Latest stable</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm">Safari</td>
              <td className="p-3 text-sm">14+</td>
              <td className="p-3 text-sm">Latest stable</td>
            </tr>
          </tbody>
        </table>

        <h3 className="text-xl font-semibold text-gray-800 mb-4">Hardware Requirements</h3>
        <ul className="space-y-2 text-gray-600">
          <li className="flex items-start">
            <ChevronRight className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            <div><strong>Processor:</strong> Dual-core 2GHz or better</div>
          </li>
          <li className="flex items-start">
            <ChevronRight className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            <div><strong>Memory:</strong> 4GB RAM minimum, 8GB recommended</div>
          </li>
          <li className="flex items-start">
            <ChevronRight className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            <div><strong>Display:</strong> 1280x720 minimum, 1920x1080 recommended</div>
          </li>
          <li className="flex items-start">
            <ChevronRight className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            <div><strong>Network:</strong> Stable broadband connection</div>
          </li>
        </ul>
      </div>
    ),
    dashboard: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h2>
        <p className="text-gray-600 mb-6">The dashboard is your central hub for monitoring and managing modeling activities.</p>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Key Metrics</h3>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">📊 Total Models</h4>
            <p className="text-sm text-gray-600">Total number of calibrated models in your workspace</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">⚡ Active Tasks</h4>
            <p className="text-sm text-gray-600">Currently running calibration processes</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">✅ Completed Tasks</h4>
            <p className="text-sm text-gray-600">Successfully finished calibrations</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">🎯 Accuracy Rate</h4>
            <p className="text-sm text-gray-600">Average calibration accuracy across all models</p>
          </div>
        </div>

        <h3 className="text-xl font-semibold text-gray-800 mb-4">Activity Timeline</h3>
        <p className="text-gray-600 mb-4">The activity timeline shows recent events in chronological order:</p>
        <ul className="space-y-2 text-gray-600">
          <li className="flex items-center"><ChevronRight className="w-4 h-4 mr-2 text-purple-600" />New model creations</li>
          <li className="flex items-center"><ChevronRight className="w-4 h-4 mr-2 text-purple-600" />Calibration completions</li>
          <li className="flex items-center"><ChevronRight className="w-4 h-4 mr-2 text-purple-600" />Data imports</li>
          <li className="flex items-center"><ChevronRight className="w-4 h-4 mr-2 text-purple-600" />Report generations</li>
        </ul>
      </div>
    ),
    libraries: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Libraries</h2>
        <p className="text-gray-600 mb-6">Centralized repository for all modeling resources including templates, data, and testbenches.</p>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Model Templates</h3>
        <p className="text-gray-600 mb-4">Pre-configured model structures for various component types.</p>
        
        <table className="w-full border-collapse mb-6">
          <thead>
            <tr className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
              <th className="p-3 text-left text-sm font-medium">Model</th>
              <th className="p-3 text-left text-sm font-medium">Version</th>
              <th className="p-3 text-left text-sm font-medium">Parameters</th>
              <th className="p-3 text-left text-sm font-medium">Use Case</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="p-3 text-sm">BSIM4</td>
              <td className="p-3 text-sm">4.8.2</td>
              <td className="p-3 text-sm">400+</td>
              <td className="p-3 text-sm">Industry standard for digital/analog</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm">PSP</td>
              <td className="p-3 text-sm">103.4</td>
              <td className="p-3 text-sm">200+</td>
              <td className="p-3 text-sm">Surface potential based</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm">EKV</td>
              <td className="p-3 text-sm">3.0</td>
              <td className="p-3 text-sm">50+</td>
              <td className="p-3 text-sm">All-region continuous model</td>
            </tr>
          </tbody>
        </table>

        <h3 className="text-xl font-semibold text-gray-800 mb-4">Reference Data Management</h3>
        <div className="bg-blue-50 border-l-4 border-blue-600 p-4 mb-6">
          <p className="text-blue-900 font-medium">Supported Formats</p>
          <p className="text-blue-700">JSON, CSV, S2P (Touchstone), MDIF, and custom formats via adapters.</p>
        </div>
      </div>
    ),
    mymodels: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">My Models</h2>
        <p className="text-gray-600 mb-6">Personal workspace for managing calibrated models and active tasks.</p>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Task Management Interface</h3>
        <p className="text-gray-600 mb-4">The main table displays all your calibration tasks with the following information:</p>
        
        <table className="w-full border-collapse mb-6">
          <thead>
            <tr className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
              <th className="p-3 text-left text-sm font-medium">Column</th>
              <th className="p-3 text-left text-sm font-medium">Description</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="p-3 text-sm font-medium">Task ID</td>
              <td className="p-3 text-sm">Unique identifier for the calibration task</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm font-medium">Model</td>
              <td className="p-3 text-sm">Template name and type being calibrated</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm font-medium">Status</td>
              <td className="p-3 text-sm">Current state (Pending, In Progress, Completed, Failed)</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm font-medium">Progress</td>
              <td className="p-3 text-sm">Completion percentage with live updates</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm font-medium">Accuracy</td>
              <td className="p-3 text-sm">Final calibration accuracy percentage</td>
            </tr>
          </tbody>
        </table>

        <h3 className="text-xl font-semibold text-gray-800 mb-4">Task Status Indicators</h3>
        <div className="flex gap-2 flex-wrap">
          <span className="px-3 py-1 bg-blue-600 text-white rounded-full text-sm">Pending</span>
          <span className="px-3 py-1 bg-purple-600 text-white rounded-full text-sm">In Progress</span>
          <span className="px-3 py-1 bg-green-600 text-white rounded-full text-sm">Completed</span>
          <span className="px-3 py-1 bg-red-600 text-white rounded-full text-sm">Failed</span>
          <span className="px-3 py-1 bg-yellow-600 text-white rounded-full text-sm">Paused</span>
        </div>
      </div>
    ),
    calibration: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Calibration Interface</h2>
        <p className="text-gray-600 mb-6">Comprehensive environment for model parameter optimization with real-time visualization.</p>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Interface Tabs</h3>
        
        <div className="space-y-4 mb-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">1. Model Tab</h4>
            <p className="text-sm text-gray-600">Configure model parameters for optimization: parameter list, optimization toggles, initial values, and bounds setting.</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">2. Reference Data Tab</h4>
            <p className="text-sm text-gray-600">View and select measurement data: interactive plots, multi-page selection, and data quality indicators.</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">3. Simulations Tab</h4>
            <p className="text-sm text-gray-600">Run simulations with current parameters and compare results with reference data.</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">4. Calibration Tab</h4>
            <p className="text-sm text-gray-600">Configure and run optimization: algorithm selection, hyperparameters, and progress monitoring.</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">5. Documentation Tab</h4>
            <p className="text-sm text-gray-600">Generate reports and documentation with customizable templates and multiple export formats.</p>
          </div>
        </div>

        <h3 className="text-xl font-semibold text-gray-800 mb-4">Optimization Algorithms</h3>
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
              <th className="p-3 text-left text-sm font-medium">Algorithm</th>
              <th className="p-3 text-left text-sm font-medium">Type</th>
              <th className="p-3 text-left text-sm font-medium">Best For</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="p-3 text-sm">Differential Evolution</td>
              <td className="p-3 text-sm">Global</td>
              <td className="p-3 text-sm">Complex search spaces</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm">Nelder-Mead</td>
              <td className="p-3 text-sm">Local</td>
              <td className="p-3 text-sm">Fine-tuning</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm">Adam</td>
              <td className="p-3 text-sm">Gradient</td>
              <td className="p-3 text-sm">Large parameter sets</td>
            </tr>
          </tbody>
        </table>
      </div>
    ),
    workflow: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Workflow Management</h2>
        <p className="text-gray-600 mb-6">Create automated pipelines for batch processing and complex calibration scenarios.</p>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Workflow Builder Features</h3>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">Drag & Drop Interface</h4>
            <p className="text-sm text-gray-600">Intuitive visual workflow creation with node-based editor</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">Conditional Logic</h4>
            <p className="text-sm text-gray-600">Add decision points based on calibration results</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">Parallel Processing</h4>
            <p className="text-sm text-gray-600">Run multiple calibrations simultaneously</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">Error Handling</h4>
            <p className="text-sm text-gray-600">Define fallback actions for failed steps</p>
          </div>
        </div>
      </div>
    ),
    reports: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Reports & Documentation</h2>
        <p className="text-gray-600 mb-6">Generate professional documentation for calibrated models.</p>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Report Types</h3>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">📋 Calibration Report</h4>
            <p className="text-sm text-gray-600">Complete record of calibration process, parameters, and results</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">✅ Validation Report</h4>
            <p className="text-sm text-gray-600">Model accuracy assessment with statistical analysis</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">📦 Release Notes</h4>
            <p className="text-sm text-gray-600">Production-ready documentation with usage guidelines</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-600 mb-2">📊 Comparison Report</h4>
            <p className="text-sm text-gray-600">Side-by-side analysis of multiple model versions</p>
          </div>
        </div>

        <h3 className="text-xl font-semibold text-gray-800 mb-4">Export Formats</h3>
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
              <th className="p-3 text-left text-sm font-medium">Format</th>
              <th className="p-3 text-left text-sm font-medium">Best For</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="p-3 text-sm">PDF</td>
              <td className="p-3 text-sm">Formal documentation, print-ready</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm">HTML</td>
              <td className="p-3 text-sm">Web sharing, interactive plots</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm">Markdown</td>
              <td className="p-3 text-sm">Version control, Git-friendly</td>
            </tr>
          </tbody>
        </table>
      </div>
    ),
    optimization: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Optimization Strategies</h2>
        <p className="text-gray-600 mb-6">Best practices for efficient and accurate model calibration.</p>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Parameter Selection Strategy</h3>
        <ol className="space-y-4 mb-6">
          <li className="flex">
            <span className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold mr-3">1</span>
            <div>
              <p className="font-semibold text-gray-800">Identify Key Parameters</p>
              <p className="text-gray-600">Start with the most sensitive parameters that significantly affect model behavior.</p>
            </div>
          </li>
          <li className="flex">
            <span className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold mr-3">2</span>
            <div>
              <p className="font-semibold text-gray-800">Set Physical Bounds</p>
              <p className="text-gray-600">Use realistic physical limits to constrain the search space.</p>
            </div>
          </li>
          <li className="flex">
            <span className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold mr-3">3</span>
            <div>
              <p className="font-semibold text-gray-800">Group Related Parameters</p>
              <p className="text-gray-600">Optimize related parameters together for better convergence.</p>
            </div>
          </li>
          <li className="flex">
            <span className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold mr-3">4</span>
            <div>
              <p className="font-semibold text-gray-800">Stage Optimization</p>
              <p className="text-gray-600">Use multiple stages: global search → local refinement.</p>
            </div>
          </li>
        </ol>
      </div>
    ),
    tips: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Tips & Best Practices</h2>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Data Preparation</h3>
        <ul className="space-y-2 text-gray-600 mb-6">
          <li className="flex items-start">
            <ChevronRight className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            Remove obvious outliers before calibration
          </li>
          <li className="flex items-start">
            <ChevronRight className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            Ensure sufficient coverage of operating regions
          </li>
          <li className="flex items-start">
            <ChevronRight className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            Weight critical regions more heavily in the cost function
          </li>
          <li className="flex items-start">
            <ChevronRight className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            Use multiple datasets for robust calibration
          </li>
        </ul>

        <h3 className="text-xl font-semibold text-gray-800 mb-4">Performance Optimization</h3>
        <ul className="space-y-2 text-gray-600 mb-6">
          <li className="flex items-start">
            <ChevronRight className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            Start with coarse grid, then refine
          </li>
          <li className="flex items-start">
            <ChevronRight className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            Use parallel processing for independent tasks
          </li>
          <li className="flex items-start">
            <ChevronRight className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            Cache intermediate results
          </li>
          <li className="flex items-start">
            <ChevronRight className="w-5 h-5 text-purple-600 mr-2 flex-shrink-0 mt-0.5" />
            Monitor memory usage for large datasets
          </li>
        </ul>

        <div className="bg-yellow-50 border-l-4 border-yellow-600 p-4">
          <p className="text-yellow-900 font-medium">Common Pitfalls to Avoid</p>
          <ul className="text-yellow-700 mt-2 space-y-1">
            <li>• Don't optimize all parameters at once</li>
            <li>• Avoid using default bounds without verification</li>
            <li>• Don't ignore warning messages from validators</li>
            <li>• Never skip the validation step</li>
          </ul>
        </div>
      </div>
    ),
    shortcuts: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Keyboard Shortcuts</h2>
        <p className="text-gray-600 mb-6">Speed up your workflow with these keyboard shortcuts.</p>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Global Shortcuts</h3>
        <table className="w-full border-collapse mb-6">
          <thead>
            <tr className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
              <th className="p-3 text-left text-sm font-medium">Shortcut</th>
              <th className="p-3 text-left text-sm font-medium">Action</th>
              <th className="p-3 text-left text-sm font-medium">Context</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="p-3 text-sm"><kbd className="px-2 py-1 bg-gray-200 rounded">Ctrl</kbd> + <kbd className="px-2 py-1 bg-gray-200 rounded">N</kbd></td>
              <td className="p-3 text-sm">New calibration task</td>
              <td className="p-3 text-sm">Any page</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm"><kbd className="px-2 py-1 bg-gray-200 rounded">Ctrl</kbd> + <kbd className="px-2 py-1 bg-gray-200 rounded">O</kbd></td>
              <td className="p-3 text-sm">Open file/import</td>
              <td className="p-3 text-sm">Libraries</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm"><kbd className="px-2 py-1 bg-gray-200 rounded">Ctrl</kbd> + <kbd className="px-2 py-1 bg-gray-200 rounded">S</kbd></td>
              <td className="p-3 text-sm">Save current work</td>
              <td className="p-3 text-sm">Calibration</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm"><kbd className="px-2 py-1 bg-gray-200 rounded">F5</kbd></td>
              <td className="p-3 text-sm">Refresh data</td>
              <td className="p-3 text-sm">Any page</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm"><kbd className="px-2 py-1 bg-gray-200 rounded">Esc</kbd></td>
              <td className="p-3 text-sm">Close modal/dialog</td>
              <td className="p-3 text-sm">Modals</td>
            </tr>
          </tbody>
        </table>

        <h3 className="text-xl font-semibold text-gray-800 mb-4">Calibration Interface</h3>
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
              <th className="p-3 text-left text-sm font-medium">Shortcut</th>
              <th className="p-3 text-left text-sm font-medium">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="p-3 text-sm"><kbd className="px-2 py-1 bg-gray-200 rounded">Tab</kbd></td>
              <td className="p-3 text-sm">Next tab</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm"><kbd className="px-2 py-1 bg-gray-200 rounded">Shift</kbd> + <kbd className="px-2 py-1 bg-gray-200 rounded">Tab</kbd></td>
              <td className="p-3 text-sm">Previous tab</td>
            </tr>
            <tr className="border-b">
              <td className="p-3 text-sm"><kbd className="px-2 py-1 bg-gray-200 rounded">Space</kbd></td>
              <td className="p-3 text-sm">Start/Pause calibration</td>
            </tr>
          </tbody>
        </table>
      </div>
    ),
    troubleshooting: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Troubleshooting Guide</h2>
        <p className="text-gray-600 mb-6">Solutions to common issues and error messages.</p>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Common Issues</h3>
        
        <div className="space-y-4">
          <div className="bg-yellow-50 border-l-4 border-yellow-600 p-4">
            <h4 className="text-yellow-900 font-semibold mb-2">Import Errors</h4>
            <p className="text-yellow-800 mb-2"><strong>Problem:</strong> "Invalid file format" when importing</p>
            <p className="text-yellow-800"><strong>Solutions:</strong></p>
            <ul className="text-yellow-700 mt-2 space-y-1 ml-4">
              <li>• Verify file format matches expected structure</li>
              <li>• Check for UTF-8 encoding</li>
              <li>• Validate JSON syntax</li>
              <li>• Ensure all required fields present</li>
            </ul>
          </div>

          <div className="bg-yellow-50 border-l-4 border-yellow-600 p-4">
            <h4 className="text-yellow-900 font-semibold mb-2">Calibration Failures</h4>
            <p className="text-yellow-800 mb-2"><strong>Problem:</strong> Optimization doesn't converge</p>
            <p className="text-yellow-800"><strong>Solutions:</strong></p>
            <ul className="text-yellow-700 mt-2 space-y-1 ml-4">
              <li>• Check initial parameter values</li>
              <li>• Review parameter bounds</li>
              <li>• Increase iterations</li>
              <li>• Try different algorithm</li>
              <li>• Reduce parameter count</li>
            </ul>
          </div>

          <div className="bg-yellow-50 border-l-4 border-yellow-600 p-4">
            <h4 className="text-yellow-900 font-semibold mb-2">Performance Issues</h4>
            <p className="text-yellow-800 mb-2"><strong>Problem:</strong> Application runs slowly</p>
            <p className="text-yellow-800"><strong>Solutions:</strong></p>
            <ul className="text-yellow-700 mt-2 space-y-1 ml-4">
              <li>• Clear browser cache</li>
              <li>• Close unnecessary tabs</li>
              <li>• Disable extensions</li>
              <li>• Update browser</li>
              <li>• Check network speed</li>
            </ul>
          </div>
        </div>
      </div>
    ),
    faq: (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>
        
        <h3 className="text-xl font-semibold text-gray-800 mb-4">General Questions</h3>
        
        <div className="space-y-4 mb-6">
          <div>
            <p className="font-semibold text-gray-800 mb-2">Q: How long does a typical calibration take?</p>
            <p className="text-gray-600">A: Calibration time varies based on model complexity, parameter count, and algorithm choice. Simple models may take 5-10 minutes, while complex models with many parameters can take several hours.</p>
          </div>
          
          <div>
            <p className="font-semibold text-gray-800 mb-2">Q: Can I run multiple calibrations simultaneously?</p>
            <p className="text-gray-600">A: Yes, the system supports parallel processing. You can run multiple calibration tasks at the same time, limited only by available system resources.</p>
          </div>
          
          <div>
            <p className="font-semibold text-gray-800 mb-2">Q: What file formats are supported for data import?</p>
            <p className="text-gray-600">A: The system supports JSON, CSV, S-parameter (S2P), MDIF, and can be extended with custom adapters for proprietary formats.</p>
          </div>
        </div>

        <h3 className="text-xl font-semibold text-gray-800 mb-4">Technical Questions</h3>
        
        <div className="space-y-4">
          <div>
            <p className="font-semibold text-gray-800 mb-2">Q: What's the difference between global and local optimization?</p>
            <p className="text-gray-600">A: Global optimization (like Differential Evolution) searches the entire parameter space for the best solution, while local optimization (like Nelder-Mead) refines a solution in a specific region.</p>
          </div>
          
          <div>
            <p className="font-semibold text-gray-800 mb-2">Q: How do I choose the right optimizer?</p>
            <p className="text-gray-600">A: Start with Differential Evolution for unknown parameter spaces, use Nelder-Mead for refinement when you have a good initial guess, and consider Adam for very large parameter sets.</p>
          </div>
        </div>

        <div className="bg-green-50 border-l-4 border-green-600 p-4 mt-6">
          <p className="text-green-900 font-medium">Need More Help?</p>
          <p className="text-green-700">Contact support with your question and include relevant error messages, screenshots, and steps to reproduce the issue.</p>
        </div>
      </div>
    ),
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Zoomed View Modal */}
      {showZoomedView && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-[60] p-8">
          <div className="bg-white rounded-lg w-full h-full max-w-[90vw] max-h-[90vh] flex flex-col">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gradient-to-r from-blue-50 to-purple-50">
              <h2 className="text-xl font-semibold text-gray-900">User Journey - Full View</h2>
              <button
                onClick={() => setShowZoomedView(false)}
                className="p-2 hover:bg-white/50 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            {/* Modal Content */}
            <div className="flex-1 overflow-auto p-8 bg-gradient-to-br from-blue-50 via-purple-50 to-green-50">
              <UserJourneyContent />
            </div>
          </div>
        </div>
      )}
      
      {/* Main UserGuide Modal */}
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg w-full max-w-7xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Icon name="userGuide" size="lg" className="text-purple-600" />
            <h2 className="text-xl font-semibold text-gray-900">User Guide</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <div className="w-64 bg-gray-50 border-r border-gray-200 overflow-y-auto">
            {/* Search */}
            <div className="p-4 border-b border-gray-200">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search guide..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                />
              </div>
            </div>

            {/* Navigation */}
            <nav className="p-4">
              {sections.map((section) => (
                <div key={section.category} className="mb-6">
                  <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                    {section.category}
                  </h3>
                  <div className="space-y-1">
                    {section.items.map((item) => {
                      const Icon = item.icon;
                      return (
                        <button
                          key={item.id}
                          onClick={() => setActiveSection(item.id)}
                          className={`w-full px-3 py-2 text-left text-sm rounded-lg flex items-center gap-2 transition-colors ${
                            activeSection === item.id
                              ? 'bg-purple-100 text-purple-700 font-medium'
                              : 'text-gray-600 hover:bg-gray-100'
                          }`}
                        >
                          <Icon className="w-4 h-4" />
                          {item.title}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1 overflow-y-auto p-8">
            {content[activeSection] || (
              <div className="text-center text-gray-500">
                <p>Content not available</p>
              </div>
            )}
          </div>
        </div>
      </div>
      </div>

      {/* Presentation Modal */}
      {showPresentation && (
        <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-[70]">
          <div className="bg-gray-900 rounded-lg w-full h-full max-w-[95vw] max-h-[95vh] flex flex-col relative">
            {/* Close button overlay */}
            <button
              onClick={() => setShowPresentation(false)}
              className="absolute top-2 right-4 z-10 text-gray-400 hover:text-white p-2 transition-colors"
              aria-label="Close presentation"
            >
              <X className="w-6 h-6" />
            </button>
            <div className="flex-1 overflow-hidden">
              <PresentationComponent />
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default UserGuide;