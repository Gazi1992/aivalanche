import React from 'react';
import { 
  FileText, Bell, Upload, CheckCircle, 
  User, Users, Database, Brain,
  Clock, Send, UserPlus, GitBranch,
  XCircle, Info, Package, AlertCircle,
  Mail, Activity, Shield, Zap, FileCheck,
  ArrowRight, Settings, ChevronRight
} from 'lucide-react';
import SlideTemplate from '../SlideTemplate';
import { RequestorIcon, ManagerIcon, DataProviderIcon, EngineerIcon, personaColors } from '../../ui/Icons';

const Slide03_UserJourney: React.FC = () => {
  return (
    <SlideTemplate 
      title="User Journey & Request Workflow"
      backgroundColor="bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50"
    >
      <div className="h-full w-full relative overflow-hidden">
        <svg 
          viewBox="0 0 1500 600" 
          className="w-full h-full"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            {/* Define arrow markers */}
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#6b7280" />
            </marker>
            <marker
              id="arrowhead-green"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#10b981" />
            </marker>
            <marker
              id="arrowhead-red"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#ef4444" />
            </marker>
            
            {/* Gradient definitions */}
            <linearGradient id="orangeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#fb923c" />
              <stop offset="100%" stopColor="#f97316" />
            </linearGradient>
            <linearGradient id="blueGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#60a5fa" />
              <stop offset="100%" stopColor="#3b82f6" />
            </linearGradient>
            <linearGradient id="greenGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#34d399" />
              <stop offset="100%" stopColor="#10b981" />
            </linearGradient>
            <linearGradient id="purpleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#c084fc" />
              <stop offset="100%" stopColor="#a855f7" />
            </linearGradient>
            <linearGradient id="completionGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10b981" />
              <stop offset="100%" stopColor="#3b82f6" />
            </linearGradient>
            
            {/* Drop shadow filter */}
            <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
              <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.1"/>
            </filter>
          </defs>
          
          {/* Background swimlanes */}
          <rect x="0" y="100" width="1500" height="120" fill="#fff7ed" opacity="0.3" />
          <rect x="0" y="220" width="1500" height="120" fill="#eff6ff" opacity="0.3" />
          <rect x="0" y="340" width="1500" height="120" fill="#f0fdf4" opacity="0.3" />
          <rect x="0" y="460" width="1500" height="120" fill="#faf5ff" opacity="0.3" />
          
          {/* Phase headers */}
          <rect x="20" y="50" width="200" height="30" fill="#f3f4f6" rx="5" />
          <text x="120" y="70" textAnchor="middle" fontSize="11" fill="#374151" fontWeight="bold">INITIATION</text>
          
          <rect x="240" y="50" width="200" height="30" fill="#f3f4f6" rx="5" />
          <text x="340" y="70" textAnchor="middle" fontSize="11" fill="#374151" fontWeight="bold">NOTIFICATION</text>
          
          <rect x="460" y="50" width="200" height="30" fill="#f3f4f6" rx="5" />
          <text x="560" y="70" textAnchor="middle" fontSize="11" fill="#374151" fontWeight="bold">ASSIGNMENT</text>
          
          <rect x="680" y="50" width="200" height="30" fill="#f3f4f6" rx="5" />
          <text x="780" y="70" textAnchor="middle" fontSize="11" fill="#374151" fontWeight="bold">DATA COLLECTION</text>
          
          <rect x="900" y="50" width="200" height="30" fill="#f3f4f6" rx="5" />
          <text x="1000" y="70" textAnchor="middle" fontSize="11" fill="#374151" fontWeight="bold">PROCESSING</text>
          
          <rect x="1120" y="50" width="200" height="30" fill="#f3f4f6" rx="5" />
          <text x="1220" y="70" textAnchor="middle" fontSize="11" fill="#374151" fontWeight="bold">DELIVERY</text>
          
          {/* Connection lines */}
          {/* Requestor to System */}
          <line 
            x1="200" y1="300" 
            x2="280" y2="300" 
            stroke="#fb923c" 
            strokeWidth="2" 
            markerEnd="url(#arrowhead)"
            strokeDasharray="5,5"
            className="animate-pulse"
          />
          <text x="240" y="295" fontSize="10" fill="#fb923c">Submit</text>
          
          {/* System to Manager */}
          <line 
            x1="420" y1="300" 
            x2="500" y2="300" 
            stroke="#6b7280" 
            strokeWidth="2" 
            markerEnd="url(#arrowhead)"
          />
          <text x="460" y="295" fontSize="10" fill="#6b7280">Notify</text>
          
          {/* Manager to Decision */}
          <line 
            x1="660" y1="300" 
            x2="730" y2="300" 
            stroke="#3b82f6" 
            strokeWidth="2" 
            markerEnd="url(#arrowhead)"
          />
          <text x="690" y="295" fontSize="10" fill="#3b82f6">Review</text>
          
          {/* Decision to Data Provider (NO path) */}
          <path 
            d="M 830 280 Q 890 200 950 180" 
            fill="none"
            stroke="#ef4444" 
            strokeWidth="2" 
            markerEnd="url(#arrowhead-red)"
          />
          <text x="870" y="220" fontSize="10" fill="#ef4444" fontWeight="bold">NO DATA</text>
          
          {/* Decision to Engineer (YES path) */}
          <path 
            d="M 830 320 Q 890 400 950 420" 
            fill="none"
            stroke="#10b981" 
            strokeWidth="2" 
            markerEnd="url(#arrowhead-green)"
          />
          <text x="860" y="380" fontSize="10" fill="#10b981" fontWeight="bold">DATA EXISTS</text>
          
          {/* Data Provider to Processing */}
          <path 
            d="M 1110 180 Q 1150 240 1150 300" 
            fill="none"
            stroke="#10b981" 
            strokeWidth="2" 
            strokeDasharray="5,5"
            className="animate-pulse"
          />
          <text x="1125" y="240" fontSize="10" fill="#10b981">Upload</text>
          
          {/* Engineer to Processing */}
          <path 
            d="M 1110 420 Q 1150 360 1150 300" 
            fill="none"
            stroke="#a855f7" 
            strokeWidth="2" 
          />
          <text x="1125" y="380" fontSize="10" fill="#a855f7">Accept</text>
          
          {/* Processing to Completion */}
          <line 
            x1="1230" y1="300" 
            x2="1310" y2="300" 
            stroke="#6b7280" 
            strokeWidth="3" 
            strokeDasharray="5,5"
            className="animate-pulse"
          />
          <text x="1260" y="295" fontSize="10" fill="#6b7280">Deliver</text>
          
          {/* Process Nodes */}
          {/* Requestor */}
          <g transform="translate(40, 260)" filter="url(#shadow)">
            <rect x="0" y="0" width="160" height="80" rx="8" fill="white" stroke="#fb923c" strokeWidth="2" />
            <rect x="0" y="0" width="160" height="25" rx="8" fill="url(#orangeGradient)" />
            <text x="80" y="17" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">REQUESTOR</text>
            <foreignObject x="10" y="30" width="140" height="45">
              <div className="text-xs text-gray-700">
                <div className="flex items-center gap-2 mb-1">
                  <FileText className="w-4 h-4 text-orange-500" />
                  <span className="font-semibold">Create Request</span>
                </div>
                <div className="text-[10px] text-gray-600 ml-6">
                  • Product specifications<br/>
                  • Priority & deadline<br/>
                  • Assign to manager
                </div>
              </div>
            </foreignObject>
          </g>
          
          {/* System */}
          <g transform="translate(280, 260)" filter="url(#shadow)">
            <rect x="0" y="0" width="140" height="80" rx="8" fill="#f9fafb" stroke="#9ca3af" strokeWidth="2" />
            <foreignObject x="10" y="10" width="120" height="60">
              <div className="flex flex-col justify-center h-full">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="w-5 h-5 text-gray-600" />
                  <span className="text-xs font-semibold text-gray-800">System Process</span>
                </div>
                <div className="text-[10px] text-gray-600">
                  • Register request<br/>
                  • Generate ID<br/>
                  • Send notifications<br/>
                  • Update dashboard
                </div>
              </div>
            </foreignObject>
          </g>
          
          {/* Manager */}
          <g transform="translate(500, 260)" filter="url(#shadow)">
            <rect x="0" y="0" width="160" height="80" rx="8" fill="white" stroke="#3b82f6" strokeWidth="2" />
            <rect x="0" y="0" width="160" height="25" rx="8" fill="url(#blueGradient)" />
            <text x="80" y="17" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">MANAGER</text>
            <foreignObject x="10" y="30" width="140" height="45">
              <div className="text-xs text-gray-700">
                <div className="flex items-center gap-2 mb-1">
                  <Shield className="w-4 h-4 text-blue-500" />
                  <span className="font-semibold">Review & Assign</span>
                </div>
                <div className="text-[10px] text-gray-600 ml-6">
                  • Validate requirements<br/>
                  • Check data availability<br/>
                  • Allocate resources
                </div>
              </div>
            </foreignObject>
          </g>
          
          {/* Decision Diamond */}
          <g transform="translate(780, 300)" filter="url(#shadow)">
            <rect x="-50" y="-40" width="100" height="80" rx="8" fill="#fef3c7" stroke="#facc15" strokeWidth="2" />
            <foreignObject x="-45" y="-35" width="90" height="70">
              <div className="flex flex-col items-center justify-center h-full">
                <GitBranch className="w-6 h-6 text-yellow-600 mb-1" />
                <div className="text-xs font-bold text-gray-800">Data</div>
                <div className="text-xs font-bold text-gray-800">Available?</div>
                <div className="flex gap-2 mt-1">
                  <span className="text-[10px] text-red-600">No ↑</span>
                  <span className="text-[10px] text-green-600">Yes ↓</span>
                </div>
              </div>
            </foreignObject>
          </g>
          
          {/* Data Provider */}
          <g transform="translate(950, 140)" filter="url(#shadow)">
            <rect x="0" y="0" width="160" height="80" rx="8" fill="white" stroke="#10b981" strokeWidth="2" />
            <rect x="0" y="0" width="160" height="25" rx="8" fill="url(#greenGradient)" />
            <text x="80" y="17" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">DATA PROVIDER</text>
            <foreignObject x="10" y="30" width="140" height="45">
              <div className="text-xs text-gray-700">
                <div className="flex items-center gap-2 mb-1">
                  <Database className="w-4 h-4 text-green-500" />
                  <span className="font-semibold">Provide Data</span>
                </div>
                <div className="text-[10px] text-gray-600 ml-6">
                  • Lab measurements<br/>
                  • TCAD simulations<br/>
                  • Quality validation
                </div>
              </div>
            </foreignObject>
          </g>
          
          {/* Engineer */}
          <g transform="translate(950, 380)" filter="url(#shadow)">
            <rect x="0" y="0" width="160" height="80" rx="8" fill="white" stroke="#a855f7" strokeWidth="2" />
            <rect x="0" y="0" width="160" height="25" rx="8" fill="url(#purpleGradient)" />
            <text x="80" y="17" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">MODEL ENGINEER</text>
            <foreignObject x="10" y="30" width="140" height="45">
              <div className="text-xs text-gray-700">
                <div className="flex items-center gap-2 mb-1">
                  <Brain className="w-4 h-4 text-purple-500" />
                  <span className="font-semibold">Review Task</span>
                </div>
                <div className="text-[10px] text-gray-600 ml-6">
                  • Check feasibility<br/>
                  • Accept/Reject/Info<br/>
                  • Prepare workflow
                </div>
              </div>
            </foreignObject>
          </g>
          
          {/* Processing Status */}
          <g transform="translate(1150, 260)" filter="url(#shadow)">
            <rect x="0" y="0" width="80" height="80" rx="40" fill="#fef3c7" stroke="#f59e0b" strokeWidth="2" />
            <foreignObject x="10" y="15" width="60" height="50">
              <div className="flex flex-col items-center justify-center text-center">
                <Clock className="w-6 h-6 text-orange-600 animate-pulse mb-1" />
                <div className="text-xs font-bold text-gray-800">PENDING</div>
                <div className="text-[9px] text-gray-600">Calibration</div>
                <div className="text-[9px] text-gray-600">In Progress</div>
              </div>
            </foreignObject>
          </g>
          
          {/* Completion */}
          <g transform="translate(1310, 260)" filter="url(#shadow)">
            <rect x="0" y="0" width="160" height="80" rx="8" fill="url(#completionGradient)" />
            <foreignObject x="10" y="10" width="140" height="60">
              <div className="flex flex-col items-center justify-center h-full text-white">
                <Package className="w-8 h-8 mb-2" />
                <div className="text-sm font-bold">MODEL DELIVERED</div>
                <div className="text-[10px] opacity-90 mt-1">
                  • Report generated<br/>
                  • All notified<br/>
                  • Files available
                </div>
              </div>
            </foreignObject>
          </g>
          
          {/* Status indicators at bottom */}
          <g transform="translate(50, 520)">
            <rect x="0" y="0" width="1400" height="40" rx="5" fill="#f3f4f6" opacity="0.8" />
            <foreignObject x="10" y="5" width="1380" height="30">
              <div className="flex items-center justify-around text-[10px] text-gray-600">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
                  <span>Active Flow</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>Average TAT: 24-48 hours</span>
                </div>
                <div className="flex items-center gap-1">
                  <Mail className="w-3 h-3" />
                  <span>Real-time notifications</span>
                </div>
                <div className="flex items-center gap-1">
                  <Shield className="w-3 h-3" />
                  <span>Quality gates at each step</span>
                </div>
                <div className="flex items-center gap-1">
                  <Zap className="w-3 h-3" />
                  <span>Automated workflow</span>
                </div>
              </div>
            </foreignObject>
          </g>
          
          {/* Animated dots on paths */}
          <circle r="4" fill="#fb923c">
            <animateMotion
              dur="2s"
              repeatCount="indefinite"
              path="M 200 300 L 280 300"
            />
          </circle>
          
          <circle r="4" fill="#10b981">
            <animateMotion
              dur="3s"
              repeatCount="indefinite"
              path="M 1110 180 Q 1150 240 1150 300"
            />
          </circle>
          
          <circle r="4" fill="#6b7280">
            <animateMotion
              dur="2s"
              repeatCount="indefinite"
              path="M 1230 300 L 1310 300"
            />
          </circle>
        </svg>
      </div>
    </SlideTemplate>
  );
};

export default Slide03_UserJourney;