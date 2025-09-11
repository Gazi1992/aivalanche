import React, { useState } from 'react';
import { Play, Pause, RotateCw, Settings, Save, FileDown } from 'lucide-react';
import WorkflowVisualization from '../WorkflowVisualization';
import dataService from '../../services/dataService';

const Workflow: React.FC = () => {
  const [workflowSteps, setWorkflowSteps] = useState(dataService.getWorkflowSteps());
  const [isRunning, setIsRunning] = useState(false);
  const [selectedStep, setSelectedStep] = useState<number | null>(null);

  const handleStartWorkflow = () => {
    setIsRunning(true);
    // Simulate workflow progression
    let currentStep = 2; // Start from calibration
    const interval = setInterval(() => {
      setWorkflowSteps(prev => {
        const updated = [...prev];
        if (currentStep < updated.length) {
          updated[currentStep].status = 'in-progress';
          updated[currentStep].progress = Math.min((updated[currentStep].progress || 0) + 10, 100);
          
          if (updated[currentStep].progress === 100) {
            updated[currentStep].status = 'completed';
            currentStep++;
          }
        } else {
          clearInterval(interval);
          setIsRunning(false);
        }
        return updated;
      });
    }, 500);
  };

  const handlePauseWorkflow = () => {
    setIsRunning(false);
  };

  const handleResetWorkflow = () => {
    setWorkflowSteps(dataService.getWorkflowSteps());
    setIsRunning(false);
  };

  const workflowTemplates = [
    {
      name: 'Standard Calibration',
      description: 'Full calibration workflow with validation',
      steps: 6,
      estimatedTime: '4-6 hours'
    },
    {
      name: 'Quick Validation',
      description: 'Fast validation for minor updates',
      steps: 3,
      estimatedTime: '1-2 hours'
    },
    {
      name: 'Corner Analysis',
      description: 'Process corner and temperature analysis',
      steps: 5,
      estimatedTime: '3-4 hours'
    }
  ];

  const stepConfigurations = {
    1: {
      name: 'Request Configuration',
      parameters: [
        { label: 'Model Type', value: 'Compact Model', type: 'select' },
        { label: 'Component', value: 'NMOS Transistor', type: 'select' },
        { label: 'Technology', value: '28nm', type: 'text' },
        { label: 'Priority', value: 'High', type: 'select' }
      ]
    },
    2: {
      name: 'Data Preparation',
      parameters: [
        { label: 'Data Validation', value: 'Enabled', type: 'checkbox' },
        { label: 'Outlier Removal', value: 'Automatic', type: 'select' },
        { label: 'Normalization', value: 'Standard', type: 'select' },
        { label: 'Format Conversion', value: 'Auto-detect', type: 'select' }
      ]
    },
    3: {
      name: 'Calibration Settings',
      parameters: [
        { label: 'Algorithm', value: 'PSO + Levenberg-Marquardt', type: 'select' },
        { label: 'Max Iterations', value: '150', type: 'number' },
        { label: 'Convergence Tolerance', value: '1e-6', type: 'number' },
        { label: 'Parameter Bounds', value: 'Physical', type: 'select' }
      ]
    },
    4: {
      name: 'Validation Configuration',
      parameters: [
        { label: 'Cross-Validation', value: 'K-Fold (k=5)', type: 'select' },
        { label: 'Test Data Split', value: '20%', type: 'number' },
        { label: 'Accuracy Target', value: '95%', type: 'number' },
        { label: 'Corner Testing', value: 'Enabled', type: 'checkbox' }
      ]
    },
    5: {
      name: 'Report Generation',
      parameters: [
        { label: 'Report Format', value: 'HTML + PDF', type: 'select' },
        { label: 'Include Plots', value: 'All', type: 'select' },
        { label: 'Statistics Level', value: 'Detailed', type: 'select' },
        { label: 'Auto-Email', value: 'Enabled', type: 'checkbox' }
      ]
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Workflow Designer</h1>
        <p className="text-gray-600 mt-2">Configure and monitor calibration workflows</p>
      </div>

      {/* Workflow Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Active Workflow</h2>
          <div className="flex gap-3">
            {!isRunning ? (
              <button
                onClick={handleStartWorkflow}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <Play className="w-4 h-4" />
                Start
              </button>
            ) : (
              <button
                onClick={handlePauseWorkflow}
                className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 flex items-center gap-2"
              >
                <Pause className="w-4 h-4" />
                Pause
              </button>
            )}
            <button
              onClick={handleResetWorkflow}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center gap-2"
            >
              <RotateCw className="w-4 h-4" />
              Reset
            </button>
          </div>
        </div>
        
        <WorkflowVisualization steps={workflowSteps} />
      </div>

      {/* Workflow Templates */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Workflow Templates</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {workflowTemplates.map((template, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-purple-500 cursor-pointer transition-colors">
              <h3 className="font-medium text-gray-900 mb-2">{template.name}</h3>
              <p className="text-sm text-gray-600 mb-3">{template.description}</p>
              <div className="flex justify-between text-xs text-gray-500">
                <span>{template.steps} steps</span>
                <span>{template.estimatedTime}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Step Configuration */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Step Configuration</h2>
          <div className="flex gap-2">
            <button className="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700 flex items-center gap-1">
              <Save className="w-3 h-3" />
              Save Template
            </button>
            <button className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 flex items-center gap-1">
              <FileDown className="w-3 h-3" />
              Export
            </button>
          </div>
        </div>
        
        <div className="space-y-4">
          {workflowSteps.map((step) => (
            <div
              key={step.id}
              className={`border rounded-lg p-4 cursor-pointer transition-all ${
                selectedStep === step.id
                  ? 'border-purple-500 bg-purple-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedStep(selectedStep === step.id ? null : step.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-medium ${
                    step.status === 'completed' ? 'bg-green-500' :
                    step.status === 'in-progress' ? 'bg-blue-500' :
                    'bg-gray-400'
                  }`}>
                    {step.id}
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{step.name}</h3>
                    <p className="text-sm text-gray-500">{step.description}</p>
                  </div>
                </div>
                <Settings className="w-5 h-5 text-gray-400" />
              </div>
              
              {selectedStep === step.id && stepConfigurations[step.id as keyof typeof stepConfigurations] && (
                <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-2 gap-4">
                  {stepConfigurations[step.id as keyof typeof stepConfigurations].parameters.map((param, idx) => (
                    <div key={idx}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {param.label}
                      </label>
                      {param.type === 'select' ? (
                        <select className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm">
                          <option>{param.value}</option>
                        </select>
                      ) : param.type === 'checkbox' ? (
                        <input type="checkbox" defaultChecked className="mt-1" />
                      ) : (
                        <input
                          type={param.type}
                          defaultValue={param.value}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                        />
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Workflow;