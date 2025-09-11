import React from 'react';
import { RefreshCw, Brain, X } from 'lucide-react';

interface ProgressTask {
  id: string;
  type: 'simulation' | 'calibration';
  name: string;
  progress: number;
  status: string;
}

interface GlobalProgressProps {
  tasks: ProgressTask[];
  onStop: (taskId: string) => void;
}

const GlobalProgress: React.FC<GlobalProgressProps> = ({ tasks, onStop }) => {
  if (tasks.length === 0) return null;

  return (
    <div className="fixed top-0 left-64 right-0 z-40 bg-white border-b border-gray-200 shadow-sm">
      <div className="px-8 py-2 space-y-1">
        {tasks.map((task) => (
          <div key={task.id} className="flex items-center gap-3">
            <div className={`flex items-center gap-2 ${
              task.type === 'simulation' ? 'text-blue-600' : 'text-purple-600'
            }`}>
              {task.type === 'simulation' ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Brain className="w-3.5 h-3.5 animate-pulse" />
              )}
              <span className="text-xs font-medium">
                {task.type === 'simulation' ? 'Simulating' : 'Calibrating'}: {task.name}
              </span>
            </div>
            
            <div className="flex-1 max-w-md">
              <div className={`h-1.5 rounded-full ${
                task.type === 'simulation' ? 'bg-blue-100' : 'bg-purple-100'
              }`}>
                <div 
                  className={`h-1.5 rounded-full transition-all duration-500 ${
                    task.type === 'simulation' ? 'bg-blue-500' : 'bg-purple-500'
                  }`}
                  style={{ width: `${task.progress}%` }}
                />
              </div>
            </div>
            
            <span className="text-xs text-gray-500 min-w-[40px]">
              {task.progress}%
            </span>
            
            <span className={`text-xs px-2 py-0.5 rounded-full ${
              task.status === 'running' 
                ? 'bg-green-100 text-green-700'
                : task.status === 'completed'
                ? 'bg-gray-100 text-gray-700'
                : 'bg-yellow-100 text-yellow-700'
            }`}>
              {task.status}
            </span>
            
            <button
              onClick={() => onStop(task.id)}
              className="p-1 hover:bg-gray-100 rounded text-gray-500 hover:text-red-600 transition-colors"
              title={`Stop ${task.type}`}
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GlobalProgress;