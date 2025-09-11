import React from 'react';
import { CheckCircle, Circle, Clock } from 'lucide-react';
import { WorkflowStep } from '../types';

interface WorkflowVisualizationProps {
  steps: WorkflowStep[];
}

const WorkflowVisualization: React.FC<WorkflowVisualizationProps> = ({ steps }) => {
  const getStepIcon = (status: WorkflowStep['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-8 h-8 text-green-500" />;
      case 'in-progress':
        return <Clock className="w-8 h-8 text-blue-500 animate-pulse" />;
      default:
        return <Circle className="w-8 h-8 text-gray-300" />;
    }
  };

  const getStepColor = (status: WorkflowStep['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'in-progress':
        return 'bg-blue-500';
      default:
        return 'bg-gray-300';
    }
  };

  const totalProgress = steps.reduce((acc, step) => acc + (step.progress || 0), 0) / steps.length;

  return (
    <div className="space-y-6">
      <div className="relative">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.id} className="flex flex-col items-center flex-1">
              <div className="relative z-10 bg-white p-2">
                {getStepIcon(step.status)}
              </div>
              <h3 className="mt-2 text-sm font-medium text-gray-900">{step.name}</h3>
              <p className="mt-1 text-xs text-gray-500 text-center max-w-[120px]">
                {step.description}
              </p>
              {step.status === 'in-progress' && step.progress !== undefined && (
                <div className="mt-2 w-full max-w-[100px]">
                  <div className="bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${step.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 text-center mt-1">{step.progress}%</p>
                </div>
              )}
            </div>
          ))}
        </div>
        
        {/* Progress Line */}
        <div className="absolute top-6 left-0 right-0 h-1 bg-gray-200 -z-10" style={{ margin: '0 40px' }}>
          <div
            className={`h-full transition-all duration-500 ${
              totalProgress > 0 ? 'bg-gradient-to-r from-green-500 to-blue-500' : ''
            }`}
            style={{ width: `${totalProgress}%` }}
          />
        </div>
      </div>

      {/* Overall Progress */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Progress</span>
          <span className="text-sm font-bold text-gray-900">{Math.round(totalProgress)}%</span>
        </div>
        <div className="bg-gray-200 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-500"
            style={{ width: `${totalProgress}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default WorkflowVisualization;