import React, { useState } from 'react';
import { 
  Wrench, Plus, TrendingUp, FileText, 
  Download, X, RefreshCw, CheckCircle, Clock, AlertCircle,
  List, Grid3X3, Filter, Search, Share2, FileBarChart,
  Calendar, User, Sliders, Trash2, Database, ChevronDown
} from 'lucide-react';
import { StatusBadge, PriorityBadge, TaskStatus, TaskPriority } from '../ui/StatusBadge';
import { StatusIcon } from '../ui/Icons';
import dataService from '../../services/dataService';
import { Model, ReferenceData, CalibratedModel } from '../../types';
import CalibrationInterface from './CalibrationInterface';
import { useAuth } from '../../contexts/AuthContext';
import ModelReport from '../ModelReport';
import { statsCardStyles } from '../../theme';

interface CalibrationTask {
  id: string;
  modelTemplate?: Model;
  referenceData?: ReferenceData;
  status: TaskStatus;
  progress: number;
  startedAt?: string;
  completedAt?: string;
  releasedAt?: string;
  accuracy?: number;
  iterations?: number;
  currentIteration?: number;
  maxIterations?: number;
  bestMetric?: number;
  optimizer?: string;
  error?: string;
  assignedTo?: string;
  priority: TaskPriority;
  dueDate?: string;
  description?: string;
  calibratedModel?: CalibratedModel;
}

interface MyModelsProps {
  onProgressUpdate?: (taskId: string, progress: number, status: string, data: any) => void;
}

const MyModels: React.FC<MyModelsProps> = ({ onProgressUpdate }) => {
  const { user } = useAuth();
  const [selectedTask, setSelectedTask] = useState<CalibrationTask | null>(null);
  const [showNewTaskModal, setShowNewTaskModal] = useState(false);
  const [showCalibrationInterface, setShowCalibrationInterface] = useState(false);
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [selectedRefData, setSelectedRefData] = useState<ReferenceData | null>(null);
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [showShareModal, setShowShareModal] = useState(false);
  const [taskToShare, setTaskToShare] = useState<CalibrationTask | null>(null);
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [showDocumentationModal, setShowDocumentationModal] = useState(false);
  const [taskToDocument, setTaskToDocument] = useState<CalibrationTask | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<CalibrationTask | null>(null);
  
  // Collapsible sections state
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    taskInfo: true,
    modelTemplate: true,
    referenceData: true,
    calibrationProgress: true,
    calibrationResults: true
  });
  
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  
  // Get data from service
  const allModels = dataService.getModelTemplates();
  const referenceData = dataService.getReferenceData();
  const calibratedModels = dataService.getCalibratedModels();
  
  // Filter calibrated models by current user (John Doe)
  const userCalibratedModels = user ? calibratedModels.filter(cm => 
    cm.author?.email === user.email || 
    cm.author?.name === user.name ||
    cm.calibration_info?.engineer === user.name
  ) : calibratedModels;
  
  // Create calibration tasks from calibrated models
  const [calibrationTasks, setCalibrationTasks] = useState<CalibrationTask[]>(() => {
    const tasks: CalibrationTask[] = userCalibratedModels.map((calModel, index) => {
      // Find matching model template and reference data
      const modelTemplate = allModels.find(m => m.model_id === calModel.model_template_id) || allModels[index % allModels.length];
      const refData = referenceData.find(r => r.data_id === calModel.reference_data?.data_id) || referenceData[index % referenceData.length];
      
      // Map status from calibrated model metadata
      let taskStatus: CalibrationTask['status'] = 'pending';
      if (calModel.status === 'completed') taskStatus = 'completed';
      else if (calModel.status === 'in-progress') taskStatus = 'in-progress';
      else if (calModel.status === 'failed') taskStatus = 'failed';
      else if (calModel.status === 'pending') taskStatus = 'pending';
      
      // Map priority based on accuracy from metadata
      let priority: CalibrationTask['priority'] = 'medium';
      if (calModel.calibration_info?.accuracy && calModel.calibration_info.accuracy > 95) priority = 'high';
      else if (calModel.calibration_info?.accuracy && calModel.calibration_info.accuracy < 80) priority = 'low';
      
      return {
        id: calModel.calibration_info?.task_id || calModel.model_id,
        modelTemplate: modelTemplate,
        referenceData: refData,
        status: taskStatus,
        progress: calModel.calibration_info?.progress || (taskStatus === 'completed' ? 100 : taskStatus === 'pending' ? 0 : 50),
        startedAt: calModel.calibration_info?.start_date || undefined,
        completedAt: calModel.calibration_info?.completion_date || undefined,
        accuracy: calModel.calibration_info?.accuracy || undefined,
        iterations: calModel.calibration_info?.iterations || 0,
        currentIteration: undefined, // Will be updated during calibration
        maxIterations: undefined, // Will be updated during calibration
        bestMetric: calModel.calibration_info?.rms_metric || undefined,
        optimizer: calModel.calibration_info?.algorithm || undefined,
        assignedTo: calModel.calibration_info?.engineer || calModel.author?.name || user?.name || 'Current User',
        priority: priority,
        dueDate: calModel.calibration_info?.completion_date ? 
          new Date(calModel.calibration_info.completion_date).toISOString().split('T')[0] : 
          new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        description: calModel.description || `${calModel.name} calibration`,
        error: calModel.calibration_info?.error_message,
        calibratedModel: calModel
      };
    });
    
    return tasks;
  });

  const filteredTasks = calibrationTasks.filter(task => {
    const matchesSearch = 
      task.modelTemplate?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.referenceData?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.description?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || task.status === filterStatus;
    const matchesPriority = filterPriority === 'all' || task.priority === filterPriority;
    
    return matchesSearch && matchesStatus && matchesPriority;
  });


  const createNewTask = () => {
    if (!selectedModel || !selectedRefData) return;
    
    const newTask: CalibrationTask = {
      id: `TASK-${String(calibrationTasks.length + 1).padStart(3, '0')}`,
      modelTemplate: selectedModel,
      referenceData: selectedRefData,
      status: 'pending',
      progress: 0,
      priority: 'medium',
      assignedTo: user?.name || 'Current User',
      dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    };
    
    setCalibrationTasks([...calibrationTasks, newTask]);
    setShowNewTaskModal(false);
    setSelectedModel(null);
    setSelectedRefData(null);
  };

  const openCalibrationInterface = (task: CalibrationTask) => {
    setSelectedTask(task);
    setShowCalibrationInterface(true);
  };

  const handleDeleteTask = (task: CalibrationTask) => {
    setCalibrationTasks(tasks => tasks.filter(t => t.id !== task.id));
    setShowDeleteConfirm(false);
    setTaskToDelete(null);
    // Close the details panel if the deleted task was selected
    if (selectedTask?.id === task.id) {
      setSelectedTask(null);
    }
    // You might want to add a toast notification here
    console.log(`Task ${task.id} deleted successfully`);
  };
  
  const handleCalibrationProgress = (taskId: string, progress: number, status: string, data?: any) => {
    setCalibrationTasks(tasks => {
      const updatedTasks = tasks.map(task => {
        if (task.id === taskId) {
          // Update global progress
          if (onProgressUpdate) {
            const taskName = task.modelTemplate?.name || 'Unknown Model';
            onProgressUpdate(taskId, progress, status, { name: taskName, type: 'calibration' });
          }
          
          return {
            ...task,
            status: status as CalibrationTask['status'],
            progress: progress,
            currentIteration: data?.currentIteration,
            maxIterations: data?.maxIterations,
            bestMetric: data?.bestMetric,
            optimizer: data?.optimizer,
            accuracy: data?.accuracy,
            iterations: data?.iterations,
            startedAt: status === 'in-progress' && !task.startedAt ? new Date().toISOString() : task.startedAt,
            completedAt: status === 'completed' ? new Date().toISOString() : task.completedAt,
            releasedAt: status === 'released' ? data?.releasedAt || new Date().toISOString() : task.releasedAt
          };
        }
        return task;
      });
      return updatedTasks;
    });
  };

  return (
    <div className="h-full flex flex-col">
      <style>{`
        @container (max-width: 250px) {
          .task-date {
            display: none;
          }
        }
        @supports not (container-type: inline-size) {
          @media (max-width: 640px) {
            .task-date {
              display: none;
            }
          }
        }
      `}</style>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Models</h1>
            <p className="text-gray-600 mt-2">
              {user ? `Manage and calibrate models where you are the author (${user.name})` : 'Manage and calibrate your models'}
            </p>
          </div>
          <button
            onClick={() => setShowNewTaskModal(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            New Calibration
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className={statsCardStyles.containerPurple}>
          <div className={statsCardStyles.content}>
            <div>
              <p className={statsCardStyles.label}>Total Tasks</p>
              <p className={statsCardStyles.value}>{calibrationTasks.length}</p>
            </div>
            <div className={statsCardStyles.iconContainerPurple}>
              <Wrench className={statsCardStyles.iconPurple} />
            </div>
          </div>
        </div>
        <div className={statsCardStyles.containerBlue}>
          <div className={statsCardStyles.content}>
            <div>
              <p className={statsCardStyles.label}>In Progress</p>
              <p className={statsCardStyles.value}>
                {calibrationTasks.filter(t => t.status === 'in-progress').length}
              </p>
            </div>
            <div className={statsCardStyles.iconContainerBlue}>
              <RefreshCw className={statsCardStyles.iconBlue} />
            </div>
          </div>
        </div>
        <div className={statsCardStyles.containerGreen}>
          <div className={statsCardStyles.content}>
            <div>
              <p className={statsCardStyles.label}>Completed</p>
              <p className={statsCardStyles.value}>
                {calibrationTasks.filter(t => t.status === 'completed').length}
              </p>
            </div>
            <div className={statsCardStyles.iconContainerGreen}>
              <CheckCircle className={statsCardStyles.iconGreen} />
            </div>
          </div>
        </div>
        <div className={statsCardStyles.containerOrange}>
          <div className={statsCardStyles.content}>
            <div>
              <p className={statsCardStyles.label}>Avg Accuracy</p>
              <p className={statsCardStyles.value}>
                {calibrationTasks.filter(t => t.accuracy).length > 0
                  ? `${(calibrationTasks
                      .filter(t => t.accuracy)
                      .reduce((acc, t) => acc + (t.accuracy || 0), 0) / 
                      calibrationTasks.filter(t => t.accuracy).length
                    ).toFixed(1)}%`
                  : 'N/A'}
              </p>
            </div>
            <div className={statsCardStyles.iconContainerOrange}>
              <TrendingUp className={statsCardStyles.iconOrange} />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className={`${selectedTask && !showCalibrationInterface ? 'mr-[600px]' : ''} flex-1 flex flex-col overflow-hidden transition-all duration-300`}>
        {/* Filters and View Toggle */}
        <div className="bg-white rounded-lg shadow mb-4 p-4">
          <div className="flex gap-4 items-center">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="in-progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="all">All Priorities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
            <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
              <Filter className="w-4 h-4" />
              More Filters
            </button>
            <div className="flex items-center border border-gray-300 rounded-lg">
              <button
                onClick={() => setViewMode('table')}
                className={`px-3 py-2 flex items-center gap-2 rounded-l-lg transition-colors ${
                  viewMode === 'table' 
                    ? 'bg-purple-600 text-white' 
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
                title="Table View"
              >
                <List className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('cards')}
                className={`px-3 py-2 flex items-center gap-2 rounded-r-lg transition-colors ${
                  viewMode === 'cards' 
                    ? 'bg-purple-600 text-white' 
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
                title="Card View"
              >
                <Grid3X3 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Calibration Tasks */}
        <div className="flex-1 bg-white rounded-lg shadow overflow-auto">
          {viewMode === 'table' ? (
            <>
              {filteredTasks.length === 0 ? (
                <div className="px-6 py-12 text-center">
                  <p className="text-gray-500">No calibration tasks found</p>
                  <button
                    onClick={() => setShowNewTaskModal(true)}
                    className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                  >
                    Create First Task
                  </button>
                </div>
              ) : (
                <table className="min-w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Task ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Model / Data
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Priority
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Progress
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Assigned To
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Due Date
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredTasks.map((task) => (
                      <tr 
                        key={task.id}
                        className={`hover:bg-gray-50 cursor-pointer ${
                          selectedTask?.id === task.id && !showCalibrationInterface ? 'bg-purple-50' : ''
                        }`}
                        onClick={() => {
                          setSelectedTask(task);
                          // Reset all sections to expanded when opening details
                          setExpandedSections({
                            taskInfo: true,
                            modelTemplate: true,
                            referenceData: true,
                            calibrationProgress: true,
                            calibrationResults: true
                          });
                        }}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <StatusIcon status={task.status} size="md" className="mr-2" />
                            <span className="text-sm font-medium text-gray-900">{task.id}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">{task.modelTemplate?.name || 'Unknown Model'}</div>
                          <div className="text-sm text-gray-500">{task.referenceData?.name || 'Unknown Data'}</div>
                        </td>
                        <td className="px-6 py-4">
                          <StatusBadge status={task.status} showIcon={false} />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <PriorityBadge priority={task.priority} showLabel={false} />
                        </td>
                        <td className="px-6 py-4">
                          {task.status === 'in-progress' ? (
                            <div className="w-full">
                              <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                                <span>{Math.round(task.progress)}%</span>
                                {task.currentIteration && task.maxIterations && (
                                  <span className="text-gray-500">
                                    Iter: {task.currentIteration}/{task.maxIterations}
                                  </span>
                                )}
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                                  style={{ width: `${task.progress}%` }}
                                />
                              </div>
                              {task.bestMetric && (
                                <div className="text-xs text-gray-500 mt-1">
                                  Best Metric: {task.bestMetric.toExponential(2)}
                                </div>
                              )}
                            </div>
                          ) : task.status === 'completed' && task.accuracy ? (
                            <div>
                              <span className="text-sm text-green-600 font-medium">
                                {task.accuracy.toFixed(1)}% accuracy
                              </span>
                              {task.iterations && (
                                <div className="text-xs text-gray-500">
                                  {task.iterations} iterations
                                </div>
                              )}
                            </div>
                          ) : (
                            <span className="text-sm text-gray-400">—</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {task.assignedTo || '—'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {task.dueDate || '—'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                openCalibrationInterface(task);
                              }}
                              className="text-purple-600 hover:text-purple-900"
                              title="Open Calibration Interface"
                            >
                              <Sliders className="w-4 h-4" />
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setTaskToShare(task);
                                setShowShareModal(true);
                              }}
                              className="text-blue-600 hover:text-blue-900"
                              title="Share Model"
                            >
                              <Share2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setTaskToDocument(task);
                                setShowDocumentationModal(true);
                              }}
                              className="text-orange-600 hover:text-orange-900"
                              title="View Report"
                            >
                              <FileBarChart className="w-4 h-4" />
                            </button>
                            {task.status === 'completed' && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                }}
                                className="text-green-600 hover:text-green-900"
                                title="Download Results"
                              >
                                <Download className="w-4 h-4" />
                              </button>
                            )}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setTaskToDelete(task);
                                setShowDeleteConfirm(true);
                              }}
                              className="text-red-600 hover:text-red-900"
                              title="Delete Task"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </>
          ) : (
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredTasks.map((task) => (
                <div
                  key={task.id}
                  className={`task-card bg-white border rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer flex flex-col h-full ${
                    selectedTask?.id === task.id && !showCalibrationInterface
                      ? 'border-purple-500 bg-purple-50' 
                      : 'border-gray-200'
                  }`}
                  onClick={() => {
                    setSelectedTask(task);
                    // Reset all sections to expanded when opening details
                    setExpandedSections({
                      taskInfo: true,
                      modelTemplate: true,
                      referenceData: true,
                      calibrationProgress: true,
                      calibrationResults: true
                    });
                  }}
                  style={{ minHeight: '280px', containerType: 'inline-size' }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-semibold text-gray-900">{task.id}</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-1 truncate">
                    {task.modelTemplate?.name || 'Unknown Model'}
                  </h3>
                  <p className="text-sm text-gray-500 mb-3 truncate">
                    {task.referenceData?.name || 'Unknown Data'}
                  </p>
                  {task.description && (
                    <p className="text-xs text-gray-600 mb-3 line-clamp-2">
                      {task.description}
                    </p>
                  )}
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center justify-between">
                      <StatusBadge status={task.status} />
                      <PriorityBadge priority={task.priority} />
                    </div>
                    <div className="w-full">
                      <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span>{Math.round(task.progress)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-500 ${
                            task.status === 'completed' ? 'bg-green-500' :
                            task.status === 'in-progress' ? 'bg-blue-500' :
                            task.status === 'failed' ? 'bg-red-500' :
                            'bg-gray-400'
                          }`}
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                    </div>
                    {task.accuracy && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-500">Accuracy</span>
                        <span className="font-medium text-green-600">{task.accuracy.toFixed(1)}%</span>
                      </div>
                    )}
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <User className="w-3 h-3" />
                        {task.assignedTo || 'Unassigned'}
                      </span>
                      {task.dueDate && (
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {task.dueDate}
                        </span>
                      )}
                    </div>
                  </div>
                  {/* Action Buttons */}
                  <div className="mt-3 pt-3 border-t border-gray-200 flex items-center justify-between gap-2">
                    <span className="task-date text-xs text-gray-500 truncate">
                      {new Date(task.startedAt || task.completedAt || Date.now()).toLocaleDateString()}
                    </span>
                    <div className="flex items-center gap-1 flex-wrap justify-end flex-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          openCalibrationInterface(task);
                        }}
                        className="p-1.5 bg-purple-100 text-purple-600 hover:bg-purple-200 rounded transition-colors"
                        title="Open Calibration Interface"
                      >
                        <Sliders className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setTaskToShare(task);
                          setShowShareModal(true);
                        }}
                        className="p-1.5 bg-blue-100 text-blue-600 hover:bg-blue-200 rounded transition-colors"
                        title="Share Model"
                      >
                        <Share2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setTaskToDocument(task);
                          setShowDocumentationModal(true);
                        }}
                        className="p-1.5 bg-orange-100 text-orange-600 hover:bg-orange-200 rounded transition-colors"
                        title="View Report"
                      >
                        <FileBarChart className="w-4 h-4" />
                      </button>
                      {task.status === 'completed' && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            // TODO: Download results
                          }}
                          className="p-1.5 bg-green-100 text-green-600 hover:bg-green-200 rounded transition-colors"
                          title="Download Results"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setTaskToDelete(task);
                          setShowDeleteConfirm(true);
                        }}
                        className="p-1.5 bg-red-100 text-red-600 hover:bg-red-200 rounded transition-colors"
                        title="Delete Task"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Task Details Side Panel */}
      {selectedTask && !showCalibrationInterface && (
        <div className="fixed right-0 top-0 bottom-0 w-[600px] bg-white border-l border-gray-200 flex flex-col z-40 shadow-xl">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Task Details</h2>
            <button
              onClick={() => {
                setSelectedTask(null);
                // Reset sections to expanded for next time
                setExpandedSections({
                  taskInfo: true,
                  modelTemplate: true,
                  referenceData: true,
                  calibrationProgress: true,
                  calibrationResults: true
                });
              }}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {/* Header Card - Similar to Requests panel */}
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-3 border border-purple-100">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h2 className="text-lg font-bold text-gray-900">
                    {selectedTask.modelTemplate?.name || 'Unknown Model'}
                  </h2>
                  <p className="text-xs text-gray-500 font-mono mt-0.5">Task ID: {selectedTask.id}</p>
                </div>
                <div className="flex flex-col items-end gap-1.5">
                  <StatusBadge status={selectedTask.status} size="md" />
                  <PriorityBadge priority={selectedTask.priority} className="border" />
                </div>
              </div>
              {selectedTask.description && (
                <p className="text-sm text-gray-700 bg-white/50 rounded p-2 italic">
                  "{selectedTask.description}"
                </p>
              )}
            </div>

            {/* Task Information */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('taskInfo')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Clock className="w-4 h-4 text-gray-500" />
                    Task Information
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.taskInfo ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.taskInfo && (
              <div className="p-3">
                <div className="grid grid-cols-3 gap-2">
                  <div className="bg-gray-50 rounded-lg p-2.5 border border-gray-200">
                    <p className="text-xs font-medium text-gray-600 mb-0.5">Assigned To</p>
                    <p className="text-sm font-semibold text-gray-900">{selectedTask.assignedTo || 'Unassigned'}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2.5 border border-gray-200">
                    <p className="text-xs font-medium text-gray-600 mb-0.5">Due Date</p>
                    <p className="text-sm font-semibold text-gray-900">{selectedTask.dueDate || 'Not set'}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2.5 border border-gray-200">
                    <p className="text-xs font-medium text-gray-600 mb-0.5">Started At</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {selectedTask.startedAt ? new Date(selectedTask.startedAt).toLocaleDateString() : 'Not started'}
                    </p>
                  </div>
                </div>
              </div>
              )}
            </div>

            {/* Model Template */}
            {selectedTask.modelTemplate && (
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div 
                  className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => toggleSection('modelTemplate')}
                >
                  <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <FileText className="w-4 h-4 text-gray-500" />
                      Model Template
                    </span>
                    <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.modelTemplate ? '' : '-rotate-90'}`} />
                  </h3>
                </div>
                {expandedSections.modelTemplate && (
                <div className="p-3">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-semibold text-gray-900">{selectedTask.modelTemplate.name}</p>
                    <span className="text-xs text-gray-500">v{selectedTask.modelTemplate.version || '1.0'}</span>
                  </div>
                  {selectedTask.modelTemplate.description && (
                    <p className="text-xs text-gray-600 mb-2">{selectedTask.modelTemplate.description}</p>
                  )}
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-gray-500">Type:</span> <span className="font-medium text-gray-700">{selectedTask.modelTemplate.type || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Category:</span> <span className="font-medium text-gray-700">{selectedTask.modelTemplate.category || 'N/A'}</span>
                    </div>
                  </div>
                </div>
                )}
              </div>
            )}

            {/* Reference Data */}
            {selectedTask.referenceData && (
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div 
                  className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => toggleSection('referenceData')}
                >
                  <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <Database className="w-4 h-4 text-gray-500" />
                      Reference Data
                    </span>
                    <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.referenceData ? '' : '-rotate-90'}`} />
                  </h3>
                </div>
                {expandedSections.referenceData && (
                <div className="p-3">
                  <p className="text-sm font-semibold text-gray-900">{selectedTask.referenceData.name}</p>
                  <p className="text-xs text-gray-600 mt-1">ID: {selectedTask.referenceData.data_id}</p>
                  <div className="grid grid-cols-2 gap-2 text-xs mt-2">
                    <div>
                      <span className="text-gray-500">Device:</span> <span className="font-medium text-gray-700">{selectedTask.referenceData.device?.type || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Technology:</span> <span className="font-medium text-gray-700">{selectedTask.referenceData.device?.technology || 'N/A'}</span>
                    </div>
                  </div>
                </div>
                )}
              </div>
            )}

            {/* Calibration Progress - Only for in-progress tasks */}
            {selectedTask.status === 'in-progress' && (
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div 
                  className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => toggleSection('calibrationProgress')}
                >
                  <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <TrendingUp className="w-4 h-4 text-gray-500" />
                      Calibration Progress
                    </span>
                    <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.calibrationProgress ? '' : '-rotate-90'}`} />
                  </h3>
                </div>
                {expandedSections.calibrationProgress && (
                <div className="p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">Overall Progress</span>
                    <span className="text-sm font-bold text-purple-600">{selectedTask.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-blue-500 h-2.5 rounded-full transition-all duration-300"
                      style={{ width: `${selectedTask.progress}%` }}
                    />
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-2">
                    {selectedTask.optimizer && (
                      <div className="bg-gray-50 rounded p-2 border border-gray-100">
                        <p className="text-xs text-gray-500">Optimizer</p>
                        <p className="text-xs font-semibold text-gray-700">
                          {selectedTask.optimizer === 'differentialEvolution' ? 'Differential Evolution' :
                           selectedTask.optimizer === 'nelderMead' ? 'Nelder-Mead' :
                           selectedTask.optimizer === 'adam' ? 'Adam' : selectedTask.optimizer}
                        </p>
                      </div>
                    )}
                    {selectedTask.currentIteration && selectedTask.maxIterations && (
                      <div className="bg-orange-50 rounded p-2 border border-orange-100">
                        <p className="text-xs text-orange-600">Iterations</p>
                        <p className="text-xs font-semibold text-gray-700">{selectedTask.currentIteration}/{selectedTask.maxIterations}</p>
                      </div>
                    )}
                  </div>
                  {selectedTask.bestMetric && (
                    <div className="mt-2 bg-blue-50 rounded p-2 border border-blue-100">
                      <p className="text-xs text-blue-600">Best Metric</p>
                      <p className="text-xs font-semibold text-gray-700">{selectedTask.bestMetric.toExponential(3)}</p>
                    </div>
                  )}
                </div>
                )}
              </div>
            )}

            {/* Calibration Results - Only for completed tasks */}
            {selectedTask.status === 'completed' && selectedTask.accuracy && (
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div 
                  className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => toggleSection('calibrationResults')}
                >
                  <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <CheckCircle className="w-4 h-4 text-gray-500" />
                      Calibration Results
                    </span>
                    <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.calibrationResults ? '' : '-rotate-90'}`} />
                  </h3>
                </div>
                {expandedSections.calibrationResults && (
                <div className="p-3">
                  <div className="grid grid-cols-2 gap-2 mb-3">
                    <div className="bg-green-50 rounded-lg p-2.5 border border-green-100">
                      <p className="text-xs font-medium text-green-600 mb-0.5">Fitness Score</p>
                      <p className="text-xl font-bold text-gray-900">{selectedTask.accuracy.toFixed(1)}%</p>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-2.5 border border-blue-100">
                      <p className="text-xs font-medium text-blue-600 mb-0.5">Iterations</p>
                      <p className="text-xl font-bold text-gray-900">{selectedTask.iterations || 0}</p>
                    </div>
                  </div>
                  {(selectedTask.optimizer || selectedTask.bestMetric) && (
                    <div className="bg-gray-50 rounded-lg p-2.5 border border-gray-100">
                      <p className="text-xs font-semibold text-gray-700 mb-2">Performance Metrics</p>
                      <div className="space-y-1.5">
                        {selectedTask.optimizer && (
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-gray-600">Optimizer:</span>
                            <span className="text-xs font-bold text-gray-900 bg-white px-2 py-0.5 rounded">
                              {selectedTask.optimizer === 'differentialEvolution' ? 'Differential Evolution' :
                               selectedTask.optimizer === 'nelderMead' ? 'Nelder-Mead' :
                               selectedTask.optimizer === 'adam' ? 'Adam' : selectedTask.optimizer}
                            </span>
                          </div>
                        )}
                        {selectedTask.bestMetric && (
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-gray-600">Final Metric:</span>
                            <span className="text-xs font-bold text-gray-900 bg-white px-2 py-0.5 rounded">{selectedTask.bestMetric.toExponential(3)}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
                )}
              </div>
            )}

            {/* Error Message */}
            {selectedTask.status === 'failed' && selectedTask.error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-red-800">Calibration Failed</h4>
                    <p className="text-sm text-red-700 mt-1">{selectedTask.error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex gap-2">
                <button
                  onClick={() => openCalibrationInterface(selectedTask)}
                  className="flex-1 px-3 py-2 bg-purple-50 text-purple-700 border border-purple-300 rounded-lg text-sm hover:bg-purple-100 hover:border-purple-400 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Sliders className="w-4 h-4" />
                  Calibration
                </button>
                <button
                  onClick={() => {
                    setTaskToShare(selectedTask);
                    setShowShareModal(true);
                  }}
                  className="flex-1 px-3 py-2 bg-blue-50 text-blue-700 border border-blue-300 rounded-lg text-sm hover:bg-blue-100 hover:border-blue-400 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Share2 className="w-4 h-4" />
                  Share
                </button>
                <button
                  onClick={() => {
                    setTaskToDocument(selectedTask);
                    setShowDocumentationModal(true);
                  }}
                  className="flex-1 px-3 py-2 bg-orange-50 text-orange-700 border border-orange-300 rounded-lg text-sm hover:bg-orange-100 hover:border-orange-400 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <FileBarChart className="w-4 h-4" />
                  Report
                </button>
                {selectedTask.status === 'completed' && (
                  <button
                    onClick={() => {
                      // TODO: Download results
                    }}
                    className="flex-1 px-3 py-2 bg-green-50 text-green-700 border border-green-300 rounded-lg text-sm hover:bg-green-100 hover:border-green-400 flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                )}
                <button
                  onClick={() => {
                    setTaskToDelete(selectedTask);
                    setShowDeleteConfirm(true);
                  }}
                  className="flex-1 px-3 py-2 bg-red-50 text-red-700 border border-red-300 rounded-lg text-sm hover:bg-red-100 hover:border-red-400 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* New Task Modal */}
      {showNewTaskModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Create New Calibration Task</h2>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Model Template
                </label>
                <select
                  value={selectedModel?.model_id || ''}
                  onChange={(e) => setSelectedModel(allModels.find(m => m.model_id === e.target.value) || null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">Choose a model template...</option>
                  {allModels.map(model => (
                    <option key={model.model_id} value={model.model_id}>
                      {model.name || 'Unknown'} - {model.type || 'Unknown'} ({model.category || 'Unknown'})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Reference Data
                </label>
                <select
                  value={selectedRefData?.data_id || ''}
                  onChange={(e) => setSelectedRefData(referenceData.find(r => r.data_id === e.target.value) || null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">Choose reference data...</option>
                  {referenceData.map(ref => (
                    <option key={ref.data_id} value={ref.data_id}>
                      {ref.name} - {ref.device?.type || 'Unknown'} ({ref.device?.technology || 'Unknown'})
                    </option>
                  ))}
                </select>
              </div>

              {(selectedModel || selectedRefData) && (
                <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                  {selectedModel && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">Model Template:</p>
                      <p className="text-sm text-gray-600">{selectedModel.name}</p>
                    </div>
                  )}
                  {selectedRefData && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">Reference Data:</p>
                      <p className="text-sm text-gray-600">{selectedRefData.name}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
            <div className="px-6 py-4 border-t border-gray-200 flex gap-3">
              <button
                onClick={() => {
                  setShowNewTaskModal(false);
                  setSelectedModel(null);
                  setSelectedRefData(null);
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={createNewTask}
                disabled={!selectedModel || !selectedRefData}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Create Task
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Calibration Interface - Render as full page */}
      {showCalibrationInterface && selectedTask && (
        <div className="fixed inset-0 bg-white z-50">
          <CalibrationInterface
            modelTemplate={selectedTask.modelTemplate}
            referenceData={selectedTask.referenceData}
            taskId={selectedTask.id}
            onClose={() => {
              setShowCalibrationInterface(false);
              setSelectedTask(null);
            }}
            onProgressUpdate={handleCalibrationProgress}
          />
        </div>
      )}

      {/* Share Modal */}
      {showShareModal && taskToShare && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">Share Model</h2>
              <button
                onClick={() => {
                  setShowShareModal(false);
                  setTaskToShare(null);
                  setSelectedUsers([]);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                Share <span className="font-semibold">{taskToShare.modelTemplate?.name || 'Model'}</span> with:
              </p>
            </div>
            
            <div className="space-y-2 max-h-64 overflow-y-auto mb-4">
              {[
                { id: 'jane.smith', name: 'Jane Smith', email: 'jane.smith@company.com', role: 'Engineer' },
                { id: 'mike.johnson', name: 'Mike Johnson', email: 'mike.johnson@company.com', role: 'Manager' },
                { id: 'sarah.wilson', name: 'Sarah Wilson', email: 'sarah.wilson@company.com', role: 'Engineer' },
                { id: 'david.brown', name: 'David Brown', email: 'david.brown@company.com', role: 'Analyst' },
                { id: 'emily.davis', name: 'Emily Davis', email: 'emily.davis@company.com', role: 'Engineer' },
                { id: 'alex.martinez', name: 'Alex Martinez', email: 'alex.martinez@company.com', role: 'Viewer' }
              ].map((user) => (
                <label
                  key={user.id}
                  className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedUsers.includes(user.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedUsers([...selectedUsers, user.id]);
                      } else {
                        setSelectedUsers(selectedUsers.filter(id => id !== user.id));
                      }
                    }}
                    className="mr-3"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-gray-400" />
                      <span className="text-sm font-medium text-gray-900">{user.name}</span>
                      <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                        {user.role}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{user.email}</p>
                  </div>
                </label>
              ))}
            </div>
            
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowShareModal(false);
                  setTaskToShare(null);
                  setSelectedUsers([]);
                }}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  // Handle share action
                  console.log('Sharing with:', selectedUsers);
                  setShowShareModal(false);
                  setTaskToShare(null);
                  setSelectedUsers([]);
                }}
                disabled={selectedUsers.length === 0}
                className={`px-4 py-2 rounded-lg ${
                  selectedUsers.length > 0
                    ? 'bg-purple-600 text-white hover:bg-purple-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                Share with {selectedUsers.length} user{selectedUsers.length !== 1 ? 's' : ''}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Report Modal - Using ModelReport Component */}
      {showDocumentationModal && taskToDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-h-[90vh] flex flex-col" style={{ maxWidth: '95vw', width: '1600px' }}>
            {/* Header */}
            <div className="flex justify-between items-center px-6 py-4 border-b border-gray-200">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Model Report</h2>
                <p className="text-sm text-gray-700 mt-1">
                  Comprehensive report about the model, reference data, and calibration results
                </p>
              </div>
              <button
                onClick={() => {
                  setShowDocumentationModal(false);
                  setTaskToDocument(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              <ModelReport
                modelData={taskToDocument.modelTemplate}
                referenceData={taskToDocument.referenceData}
                parameters={undefined} // Parameters would need to be loaded from file
                calibrationResults={taskToDocument.calibratedModel}
                timestamp={taskToDocument.completedAt || new Date().toISOString()}
                isGenerated={true}
                showGenerateButton={false}
              />
            </div>
            
            {/* Footer */}
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
              <button
                onClick={() => {
                  setShowDocumentationModal(false);
                  setTaskToDocument(null);
                }}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && taskToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-red-100 rounded-full">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Delete Task</h2>
                <p className="text-sm text-gray-600">This action cannot be undone</p>
              </div>
            </div>
            
            <div className="mb-6">
              <p className="text-gray-700">
                Are you sure you want to delete this calibration task?
              </p>
              <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm font-medium text-gray-900">
                  {taskToDelete.modelTemplate?.name || 'Unknown Model'}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  Task ID: {taskToDelete.id}
                </p>
                <p className="text-xs text-gray-600">
                  Status: {taskToDelete.status}
                </p>
                {taskToDelete.progress > 0 && (
                  <p className="text-xs text-gray-600">
                    Progress: {Math.round(taskToDelete.progress)}%
                  </p>
                )}
              </div>
            </div>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setTaskToDelete(null);
                }}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteTask(taskToDelete)}
                className="px-4 py-2 bg-red-600 text-white hover:bg-red-700 rounded-lg flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Delete Task
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyModels;