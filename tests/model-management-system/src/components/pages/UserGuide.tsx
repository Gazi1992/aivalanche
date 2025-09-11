import React, { useState } from 'react';
import { 
  BookOpen, Users, Database, Settings, ArrowRight, ChevronRight, 
  FileText, Upload, FlaskConical, Cpu, CheckCircle, AlertCircle,
  Package, GitBranch, Server, Cloud, Lock, Bell, BarChart3,
  Workflow, Target, Zap, Shield, Download, Send
} from 'lucide-react';
import { Card } from '../ui';
import { PageHeader } from '../layout';

const UserGuide: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'architecture' | 'personas' | 'workflows' | 'data-management'>('architecture');
  const [selectedPersona, setSelectedPersona] = useState<string>('lab-engineer');

  const personas = [
    {
      id: 'lab-engineer',
      title: 'Lab Engineer',
      icon: FlaskConical,
      color: 'blue',
      responsibilities: [
        'Perform device measurements',
        'Upload measurement data',
        'Validate data quality',
        'Create reference datasets'
      ]
    },
    {
      id: 'model-engineer',
      title: 'Model Engineer',
      icon: Cpu,
      color: 'purple',
      responsibilities: [
        'Select model templates',
        'Calibrate models',
        'Validate model accuracy',
        'Export calibrated models'
      ]
    },
    {
      id: 'tcad-engineer',
      title: 'TCAD Engineer',
      icon: GitBranch,
      color: 'green',
      responsibilities: [
        'Generate simulation data',
        'Upload TCAD results',
        'Create virtual experiments',
        'Validate against measurements'
      ]
    },
    {
      id: 'app-engineer',
      title: 'Application Engineer',
      icon: Target,
      color: 'orange',
      responsibilities: [
        'Create model requests',
        'Define requirements',
        'Review delivered models',
        'Provide feedback'
      ]
    }
  ];

  return (
    <div className="h-full flex flex-col p-4 gap-4">
      <PageHeader
        title="User Guide & System Architecture"
        description="Comprehensive guide to the Model Management System"
      />

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('architecture')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'architecture'
              ? 'border-purple-600 text-purple-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4" />
            System Architecture
          </div>
        </button>
        <button
          onClick={() => setActiveTab('personas')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'personas'
              ? 'border-purple-600 text-purple-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            User Personas
          </div>
        </button>
        <button
          onClick={() => setActiveTab('workflows')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'workflows'
              ? 'border-purple-600 text-purple-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center gap-2">
            <Workflow className="w-4 h-4" />
            Process Workflows
          </div>
        </button>
        <button
          onClick={() => setActiveTab('data-management')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'data-management'
              ? 'border-purple-600 text-purple-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4" />
            Data Management
          </div>
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto">
        {activeTab === 'architecture' && (
          <div className="space-y-6">
            {/* System Overview Diagram */}
            <Card>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Server className="w-5 h-5 text-purple-600" />
                System Architecture Overview
              </h2>
              
              <div className="relative bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-8">
                {/* Data Storage Layer */}
                <div className="absolute top-4 left-4 right-4 bg-white rounded-lg border-2 border-gray-300 p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <Database className="w-4 h-4" />
                    Data Storage Layer
                  </h3>
                  <div className="grid grid-cols-4 gap-3">
                    <div className="bg-blue-50 border border-blue-200 rounded p-2">
                      <div className="text-xs font-medium text-blue-700">Model Templates</div>
                      <div className="text-xs text-blue-600 mt-1">JSON Files</div>
                      <div className="text-xs text-gray-500">src/data/model-templates/</div>
                    </div>
                    <div className="bg-green-50 border border-green-200 rounded p-2">
                      <div className="text-xs font-medium text-green-700">Reference Data</div>
                      <div className="text-xs text-green-600 mt-1">Measurement/TCAD</div>
                      <div className="text-xs text-gray-500">src/data/reference-data/</div>
                    </div>
                    <div className="bg-purple-50 border border-purple-200 rounded p-2">
                      <div className="text-xs font-medium text-purple-700">Testbenches</div>
                      <div className="text-xs text-purple-600 mt-1">Circuit Configs</div>
                      <div className="text-xs text-gray-500">src/data/testbenches/</div>
                    </div>
                    <div className="bg-orange-50 border border-orange-200 rounded p-2">
                      <div className="text-xs font-medium text-orange-700">Calibrated Models</div>
                      <div className="text-xs text-orange-600 mt-1">Final Models</div>
                      <div className="text-xs text-gray-500">src/data/calibrated-models/</div>
                    </div>
                  </div>
                </div>

                {/* Service Layer */}
                <div className="absolute top-36 left-4 right-4 bg-white rounded-lg border-2 border-gray-300 p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <Settings className="w-4 h-4" />
                    Service Layer
                  </h3>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="bg-indigo-50 border border-indigo-200 rounded p-2">
                      <div className="text-xs font-medium text-indigo-700">Data Service</div>
                      <div className="text-xs text-indigo-600 mt-1">CRUD Operations</div>
                      <div className="text-xs text-gray-500">dataService.ts</div>
                    </div>
                    <div className="bg-pink-50 border border-pink-200 rounded p-2">
                      <div className="text-xs font-medium text-pink-700">Calibration Engine</div>
                      <div className="text-xs text-pink-600 mt-1">Optimization & Fitting</div>
                      <div className="text-xs text-gray-500">PSO, L-M, GA</div>
                    </div>
                    <div className="bg-cyan-50 border border-cyan-200 rounded p-2">
                      <div className="text-xs font-medium text-cyan-700">Export Service</div>
                      <div className="text-xs text-cyan-600 mt-1">Format Conversion</div>
                      <div className="text-xs text-gray-500">JSON, SPICE, Verilog-A</div>
                    </div>
                  </div>
                </div>

                {/* Application Layer */}
                <div className="absolute top-64 left-4 right-4 bg-white rounded-lg border-2 border-gray-300 p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <Package className="w-4 h-4" />
                    Application Layer
                  </h3>
                  <div className="grid grid-cols-5 gap-2">
                    <div className="bg-gray-50 border border-gray-200 rounded p-2 text-center">
                      <BarChart3 className="w-4 h-4 mx-auto text-gray-600" />
                      <div className="text-xs font-medium text-gray-700 mt-1">Dashboard</div>
                    </div>
                    <div className="bg-gray-50 border border-gray-200 rounded p-2 text-center">
                      <Database className="w-4 h-4 mx-auto text-gray-600" />
                      <div className="text-xs font-medium text-gray-700 mt-1">Libraries</div>
                    </div>
                    <div className="bg-gray-50 border border-gray-200 rounded p-2 text-center">
                      <Target className="w-4 h-4 mx-auto text-gray-600" />
                      <div className="text-xs font-medium text-gray-700 mt-1">Calibration</div>
                    </div>
                    <div className="bg-gray-50 border border-gray-200 rounded p-2 text-center">
                      <FileText className="w-4 h-4 mx-auto text-gray-600" />
                      <div className="text-xs font-medium text-gray-700 mt-1">Requests</div>
                    </div>
                    <div className="bg-gray-50 border border-gray-200 rounded p-2 text-center">
                      <Shield className="w-4 h-4 mx-auto text-gray-600" />
                      <div className="text-xs font-medium text-gray-700 mt-1">Auth</div>
                    </div>
                  </div>
                </div>

                {/* User Layer */}
                <div className="absolute bottom-4 left-4 right-4 bg-white rounded-lg border-2 border-gray-300 p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    User Interface Layer
                  </h3>
                  <div className="flex justify-around items-center">
                    {personas.map(persona => (
                      <div key={persona.id} className="text-center">
                        <div className={`w-10 h-10 bg-${persona.color}-100 rounded-full flex items-center justify-center mx-auto`}>
                          <persona.icon className={`w-5 h-5 text-${persona.color}-600`} />
                        </div>
                        <div className="text-xs font-medium text-gray-700 mt-1">{persona.title}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Vertical Flow Arrows */}
                <div className="absolute top-24 left-1/2 transform -translate-x-1/2">
                  <ArrowRight className="w-6 h-6 text-gray-400 rotate-90" />
                </div>
                <div className="absolute top-52 left-1/2 transform -translate-x-1/2">
                  <ArrowRight className="w-6 h-6 text-gray-400 rotate-90" />
                </div>
                <div className="absolute bottom-24 left-1/2 transform -translate-x-1/2">
                  <ArrowRight className="w-6 h-6 text-gray-400 rotate-90" />
                </div>
              </div>
            </Card>

            {/* Data Flow Diagram */}
            <Card>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <GitBranch className="w-5 h-5 text-purple-600" />
                Data Flow & Processing Pipeline
              </h2>
              
              <div className="relative bg-gradient-to-r from-blue-50 via-purple-50 to-green-50 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  {/* Input Sources */}
                  <div className="bg-white rounded-lg border-2 border-blue-300 p-4 w-48">
                    <h4 className="text-sm font-semibold text-blue-700 mb-2">Data Sources</h4>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-xs">
                        <FlaskConical className="w-3 h-3 text-blue-600" />
                        <span>Lab Measurements</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <Cpu className="w-3 h-3 text-blue-600" />
                        <span>TCAD Simulations</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <Upload className="w-3 h-3 text-blue-600" />
                        <span>External Data Import</span>
                      </div>
                    </div>
                  </div>

                  <ArrowRight className="w-8 h-8 text-gray-400" />

                  {/* Processing */}
                  <div className="bg-white rounded-lg border-2 border-purple-300 p-4 w-48">
                    <h4 className="text-sm font-semibold text-purple-700 mb-2">Processing</h4>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-xs">
                        <Shield className="w-3 h-3 text-purple-600" />
                        <span>Data Validation</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <Zap className="w-3 h-3 text-purple-600" />
                        <span>Model Calibration</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <Target className="w-3 h-3 text-purple-600" />
                        <span>Optimization</span>
                      </div>
                    </div>
                  </div>

                  <ArrowRight className="w-8 h-8 text-gray-400" />

                  {/* Output */}
                  <div className="bg-white rounded-lg border-2 border-green-300 p-4 w-48">
                    <h4 className="text-sm font-semibold text-green-700 mb-2">Outputs</h4>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-xs">
                        <Package className="w-3 h-3 text-green-600" />
                        <span>Calibrated Models</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <FileText className="w-3 h-3 text-green-600" />
                        <span>SPICE Netlists</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <Download className="w-3 h-3 text-green-600" />
                        <span>Export Packages</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'personas' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Persona Cards */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold">User Personas</h2>
              {personas.map(persona => (
                <Card
                  key={persona.id}
                  className={`cursor-pointer transition-all ${
                    selectedPersona === persona.id
                      ? 'ring-2 ring-purple-600 bg-purple-50'
                      : 'hover:shadow-lg'
                  }`}
                  onClick={() => setSelectedPersona(persona.id)}
                >
                  <div className="flex items-start gap-4">
                    <div className={`p-3 bg-${persona.color}-100 rounded-lg`}>
                      <persona.icon className={`w-6 h-6 text-${persona.color}-600`} />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{persona.title}</h3>
                      <div className="mt-2 space-y-1">
                        {persona.responsibilities.map((resp, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                            <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                            <span>{resp}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>

            {/* Workflow for Selected Persona */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold">Workflow Details</h2>
              <Card>
                {selectedPersona === 'lab-engineer' && (
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                      <FlaskConical className="w-5 h-5 text-blue-600" />
                      Lab Engineer Workflow
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-blue-600">1</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Perform Measurements</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Use lab equipment to measure device characteristics (I-V curves, C-V curves, S-parameters)
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-blue-600">2</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Format Data</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Convert measurement data to system-compatible JSON format with metadata
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-blue-600">3</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Upload to Reference Library</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Navigate to Libraries → Reference Data → Upload New Dataset
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-blue-600">4</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Validate Data Quality</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Review plots, check for outliers, ensure data completeness
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {selectedPersona === 'model-engineer' && (
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                      <Cpu className="w-5 h-5 text-purple-600" />
                      Model Engineer Workflow
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-purple-600">1</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Review Model Request</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Check Requests page for new model requirements from application engineers
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-purple-600">2</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Select Model Template</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Choose appropriate model from Libraries → Model Templates (BSIM, PSP, etc.)
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-purple-600">3</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Load Reference Data</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Select measurement or TCAD data for target device from Reference Library
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-purple-600">4</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Calibrate Model</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Go to My Models → New Calibration, adjust parameters, run optimization
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-purple-600">5</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Validate & Export</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Check accuracy metrics, export to SPICE/Verilog-A, update request status
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {selectedPersona === 'tcad-engineer' && (
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                      <GitBranch className="w-5 h-5 text-green-600" />
                      TCAD Engineer Workflow
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-green-600">1</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Run TCAD Simulations</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Simulate device physics using Sentaurus, Silvaco, or similar tools
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-green-600">2</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Extract Electrical Data</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Generate I-V, C-V characteristics from simulation results
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-green-600">3</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Format as Reference Data</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Convert TCAD output to JSON format matching measurement structure
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-green-600">4</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Upload & Tag</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Upload to Reference Library with "TCAD" tag for traceability
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {selectedPersona === 'app-engineer' && (
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                      <Target className="w-5 h-5 text-orange-600" />
                      Application Engineer Workflow
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-orange-600">1</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Create Model Request</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Go to Requests → New Request, specify device type, technology, requirements
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-orange-600">2</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Define Specifications</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Set accuracy targets, corner requirements, temperature ranges
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-orange-600">3</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Track Progress</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Monitor request status, receive notifications on updates
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-sm font-semibold text-orange-600">4</span>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">Review & Accept</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            Validate delivered model, provide feedback, download for use
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </Card>
            </div>
          </div>
        )}

        {activeTab === 'workflows' && (
          <div className="space-y-6">
            {/* End-to-End Process Flow */}
            <Card>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Workflow className="w-5 h-5 text-purple-600" />
                End-to-End Model Development Process
              </h2>
              
              <div className="relative">
                <div className="flex items-center justify-between mb-8">
                  {/* Timeline Steps */}
                  <div className="absolute top-0 left-0 right-0 h-1 bg-gray-200 rounded-full"></div>
                  <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-green-500 rounded-full" 
                       style={{ width: '100%' }}></div>
                  
                  {/* Process Steps */}
                  <div className="relative z-10 bg-white rounded-lg border-2 border-blue-300 p-3 w-40">
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-xs text-white font-bold">1</span>
                    </div>
                    <h4 className="text-xs font-semibold text-blue-700 mt-2">Request Created</h4>
                    <p className="text-xs text-gray-600 mt-1">App Engineer submits model request</p>
                    <div className="flex items-center gap-1 mt-2">
                      <Bell className="w-3 h-3 text-blue-500" />
                      <span className="text-xs text-blue-600">Notify Model Team</span>
                    </div>
                  </div>

                  <ChevronRight className="text-gray-400" />

                  <div className="relative z-10 bg-white rounded-lg border-2 border-purple-300 p-3 w-40">
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center">
                      <span className="text-xs text-white font-bold">2</span>
                    </div>
                    <h4 className="text-xs font-semibold text-purple-700 mt-2">Data Preparation</h4>
                    <p className="text-xs text-gray-600 mt-1">Lab/TCAD data uploaded</p>
                    <div className="flex items-center gap-1 mt-2">
                      <Upload className="w-3 h-3 text-purple-500" />
                      <span className="text-xs text-purple-600">Validate Quality</span>
                    </div>
                  </div>

                  <ChevronRight className="text-gray-400" />

                  <div className="relative z-10 bg-white rounded-lg border-2 border-indigo-300 p-3 w-40">
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 w-6 h-6 bg-indigo-500 rounded-full flex items-center justify-center">
                      <span className="text-xs text-white font-bold">3</span>
                    </div>
                    <h4 className="text-xs font-semibold text-indigo-700 mt-2">Calibration</h4>
                    <p className="text-xs text-gray-600 mt-1">Model fitting & optimization</p>
                    <div className="flex items-center gap-1 mt-2">
                      <Zap className="w-3 h-3 text-indigo-500" />
                      <span className="text-xs text-indigo-600">Auto-optimize</span>
                    </div>
                  </div>

                  <ChevronRight className="text-gray-400" />

                  <div className="relative z-10 bg-white rounded-lg border-2 border-green-300 p-3 w-40">
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                      <span className="text-xs text-white font-bold">4</span>
                    </div>
                    <h4 className="text-xs font-semibold text-green-700 mt-2">Delivery</h4>
                    <p className="text-xs text-gray-600 mt-1">Model exported & delivered</p>
                    <div className="flex items-center gap-1 mt-2">
                      <Send className="w-3 h-3 text-green-500" />
                      <span className="text-xs text-green-600">Notify Requester</span>
                    </div>
                  </div>
                </div>

                {/* Status Timeline */}
                <div className="mt-8 bg-gray-50 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">Typical Timeline</h4>
                  <div className="grid grid-cols-4 gap-4 text-xs">
                    <div>
                      <div className="font-medium text-gray-700">Day 1</div>
                      <div className="text-gray-600">Request submitted</div>
                    </div>
                    <div>
                      <div className="font-medium text-gray-700">Day 2-3</div>
                      <div className="text-gray-600">Data collection</div>
                    </div>
                    <div>
                      <div className="font-medium text-gray-700">Day 4-5</div>
                      <div className="text-gray-600">Model calibration</div>
                    </div>
                    <div>
                      <div className="font-medium text-gray-700">Day 6</div>
                      <div className="text-gray-600">Delivery & validation</div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Notification System */}
            <Card>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Bell className="w-5 h-5 text-purple-600" />
                Notification & Communication Flow
              </h2>
              
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Automated Notifications</h3>
                  <div className="space-y-2">
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5"></div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">New Request</div>
                        <div className="text-xs text-gray-600">Model engineers notified when request created</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-purple-500 rounded-full mt-1.5"></div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">Status Update</div>
                        <div className="text-xs text-gray-600">Requester notified on progress changes</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5"></div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">Model Ready</div>
                        <div className="text-xs text-gray-600">Final notification with download link</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-orange-500 rounded-full mt-1.5"></div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">Issues Found</div>
                        <div className="text-xs text-gray-600">Alert on validation failures</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Communication Channels</h3>
                  <div className="space-y-2">
                    <div className="bg-blue-50 border border-blue-200 rounded p-2">
                      <div className="text-sm font-medium text-blue-700">In-App Messages</div>
                      <div className="text-xs text-blue-600">Real-time notifications in dashboard</div>
                    </div>
                    <div className="bg-purple-50 border border-purple-200 rounded p-2">
                      <div className="text-sm font-medium text-purple-700">Email Alerts</div>
                      <div className="text-xs text-purple-600">Critical updates sent to registered email</div>
                    </div>
                    <div className="bg-green-50 border border-green-200 rounded p-2">
                      <div className="text-sm font-medium text-green-700">Request Comments</div>
                      <div className="text-xs text-green-600">Discussion thread on each request</div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'data-management' && (
          <div className="space-y-6">
            {/* Data Structure */}
            <Card>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Database className="w-5 h-5 text-purple-600" />
                Data Structure & Storage
              </h2>
              
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">File Organization</h3>
                  <div className="bg-gray-50 rounded-lg p-3 font-mono text-xs">
                    <div className="text-gray-600">src/data/</div>
                    <div className="ml-4">
                      <div className="text-blue-600">├── model-templates/</div>
                      <div className="ml-4 text-gray-500">
                        <div>├── bsim4/</div>
                        <div>│   └── metadata.json</div>
                        <div>├── psp/</div>
                        <div>│   └── metadata.json</div>
                        <div>└── ...</div>
                      </div>
                      <div className="text-green-600 mt-2">├── reference-data/</div>
                      <div className="ml-4 text-gray-500">
                        <div>├── nmos_65nm.json</div>
                        <div>├── pmos_65nm.json</div>
                        <div>└── ...</div>
                      </div>
                      <div className="text-purple-600 mt-2">├── testbenches/</div>
                      <div className="ml-4 text-gray-500">
                        <div>├── dc_sweep.json</div>
                        <div>├── ac_analysis.json</div>
                        <div>└── ...</div>
                      </div>
                      <div className="text-orange-600 mt-2">└── calibrated-models/</div>
                      <div className="ml-4 text-gray-500">
                        <div>├── model_001/</div>
                        <div>│   ├── metadata.json</div>
                        <div>│   └── parameters.json</div>
                        <div>└── ...</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Data Formats</h3>
                  <div className="space-y-3">
                    <div>
                      <h4 className="text-xs font-semibold text-gray-600 mb-1">Reference Data JSON</h4>
                      <div className="bg-gray-50 rounded p-2 font-mono text-xs">
                        <pre>{`{
  "data_id": "unique_id",
  "name": "Device Name",
  "device_info": {...},
  "data": [
    {
      "page": "id_vg",
      "curves": [...]
    }
  ]
}`}</pre>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-xs font-semibold text-gray-600 mb-1">Model Template JSON</h4>
                      <div className="bg-gray-50 rounded p-2 font-mono text-xs">
                        <pre>{`{
  "model_id": "bsim4",
  "name": "BSIM4",
  "parameters": [
    {
      "name": "VTH0",
      "default": 0.7,
      "range": [0.3, 1.2]
    }
  ]
}`}</pre>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* How to Add New Data */}
            <Card>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Upload className="w-5 h-5 text-purple-600" />
                How to Add New Data
              </h2>
              
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-blue-700">New Model Template</h3>
                  <ol className="space-y-2 text-xs">
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-blue-600">1.</span>
                      <span>Create folder in src/data/model-templates/</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-blue-600">2.</span>
                      <span>Add metadata.json with model structure</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-blue-600">3.</span>
                      <span>Define all parameters with defaults</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-blue-600">4.</span>
                      <span>Import in dataService.ts</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-blue-600">5.</span>
                      <span>Template appears in Libraries</span>
                    </li>
                  </ol>
                </div>
                
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-green-700">New Reference Data</h3>
                  <ol className="space-y-2 text-xs">
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-green-600">1.</span>
                      <span>Format data as JSON structure</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-green-600">2.</span>
                      <span>Include device metadata</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-green-600">3.</span>
                      <span>Use Libraries → Upload modal</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-green-600">4.</span>
                      <span>Or save to reference-data/</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-green-600">5.</span>
                      <span>Data ready for calibration</span>
                    </li>
                  </ol>
                </div>
                
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-purple-700">New Testbench</h3>
                  <ol className="space-y-2 text-xs">
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-purple-600">1.</span>
                      <span>Define circuit configuration</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-purple-600">2.</span>
                      <span>Specify analysis type</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-purple-600">3.</span>
                      <span>Set sweep parameters</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-purple-600">4.</span>
                      <span>Save as JSON in testbenches/</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-semibold text-purple-600">5.</span>
                      <span>Available in simulation tab</span>
                    </li>
                  </ol>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserGuide;