import React, { useState, useEffect } from 'react';
import { 
  X, ArrowLeft, FileText, Database, Play, Brain, RefreshCw, Search,
  Shuffle, CheckCircle2, Shield
} from 'lucide-react';
import { Model, ReferenceData, ModelParameter } from '../../types';
import dataService from '../../services/dataService';
import { getModelParameters } from '../../data/parametersData';
import PlotGrid from '../PlotGrid';
import { 
  ModelTab, 
  ReferenceDataTab, 
  SimulationsTab, 
  CalibrationTab, 
  DocumentationTab,
  MonteCarloTab,
  ValidationTab,
  EncryptionTab
} from '../calibration-tabs';

interface CalibrationInterfaceProps {
  modelTemplate?: Model;
  referenceData?: ReferenceData;
  taskId?: string;
  onClose: () => void;
  onProgressUpdate?: (taskId: string, progress: number, status: string, data?: any) => void;
}

type TabType = 'model' | 'reference' | 'simulations' | 'calibration' | 'montecarlo' | 'validation' | 'encryption' | 'documentation';

interface OptimizerParams {
  differentialEvolution: {
    populationSize: number;
    F: number;
    CR: number;
    strategy: 'best1bin' | 'rand1bin' | 'currenttobest1bin';
    maxGenerations: number;
    tolerance: number;
  };
  nelderMead: {
    alpha: number;
    gamma: number;
    rho: number;
    sigma: number;
    maxIterations: number;
    tolerance: number;
  };
  adam: {
    learningRate: number;
    beta1: number;
    beta2: number;
    epsilon: number;
    maxIterations: number;
    tolerance: number;
  };
}

const CalibrationInterface: React.FC<CalibrationInterfaceProps> = ({
  modelTemplate: initialModelTemplate,
  referenceData: initialReferenceData,
  taskId,
  onClose,
  onProgressUpdate
}) => {
  // Tab state
  const [activeTab, setActiveTab] = useState<TabType>('model');
  
  // Model and Reference Data state
  const [selectedModelTemplate, setSelectedModelTemplate] = useState<Model | undefined>(initialModelTemplate);
  const [selectedReferenceData, setSelectedReferenceData] = useState<ReferenceData[]>(
    initialReferenceData ? [initialReferenceData] : []
  );
  
  // Parameters state with optimization flags
  const [parameters, setParameters] = useState<(ModelParameter & { optimize: boolean; value?: number })[]>([]);
  const [parameterFilter, setParameterFilter] = useState('');
  const [parameterSort, setParameterSort] = useState<'name' | 'value' | 'subckt'>('name');
  const [parameterSortOrder, setParameterSortOrder] = useState<'asc' | 'desc'>('asc');
  
  // Separate states for each tab's data selection
  const [refDataSelectedPages, setRefDataSelectedPages] = useState<string[]>([]);
  const [refDataExpandedDatasets, setRefDataExpandedDatasets] = useState<string[]>([]);
  const [simulationSelectedPages, setSimulationSelectedPages] = useState<string[]>([]);
  const [simulationExpandedDatasets, setSimulationExpandedDatasets] = useState<string[]>([]);
  const [calibrationSelectedPages, setCalibrationSelectedPages] = useState<string[]>([]);
  const [calibrationExpandedDatasets, setCalibrationExpandedDatasets] = useState<string[]>([]);
  
  // Common UI state
  const [plotColumns] = useState<1 | 2 | 3>(2);
  const [showAddDataModal, setShowAddDataModal] = useState(false);
  const [dataSearchTerm, setDataSearchTerm] = useState('');
  const [dataFilterType, setDataFilterType] = useState('all');
  const [dataFilterDevice, setDataFilterDevice] = useState('all');
  
  // Calibration state
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentIteration, setCurrentIteration] = useState(0);
  const [selectedOptimizer, setSelectedOptimizer] = useState<'differentialEvolution' | 'nelderMead' | 'adam'>('differentialEvolution');
  const [calibrationView, setCalibrationView] = useState<'refDataPlots' | 'optimizationProgress'>('optimizationProgress');
  const [optimizationStartTime, setOptimizationStartTime] = useState<Date | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [bestCalibrationResults, setBestCalibrationResults] = useState<any>(null);
  const [hasNewBestSolution, setHasNewBestSolution] = useState(false);
  const [displayedCalibrationResults, setDisplayedCalibrationResults] = useState<any>(null);
  const [showParamEvolution, setShowParamEvolution] = useState(false);
  
  // Simulation state
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationProgress, setSimulationProgress] = useState(0);
  const [simulationResults, setSimulationResults] = useState<any>(null);
  
  // Documentation state
  const [documentationData, setDocumentationData] = useState<any>(null);
  const [documentationGenerated, setDocumentationGenerated] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [reportGenerationProgress, setReportGenerationProgress] = useState(0);
  const [calibParamSort, setCalibParamSort] = useState<'name' | 'subckt'>('name');
  const [isModelReleased, setIsModelReleased] = useState(false);
  
  // Results state
  const [results] = useState({
    finalMetric: 0.0023,
    convergenceHistory: Array.from({ length: 100 }, (_, i) => ({
      iteration: i,
      error: Math.exp(-i / 20) * 0.1 + 0.002 + Math.random() * 0.001
    })),
    parameterHistory: {},
    fitQuality: {
      rmse: 0.0023,
      r2: 0.9987,
      maxMetric: 0.0089,
      meanMetric: 0.0012
    }
  });
  
  // Optimizer parameters state
  const [optimizerParams, setOptimizerParams] = useState<OptimizerParams>({
    differentialEvolution: {
      populationSize: 50,
      F: 0.8,
      CR: 0.9,
      strategy: 'best1bin',
      maxGenerations: 100,
      tolerance: 1e-6
    },
    nelderMead: {
      alpha: 1.0,
      gamma: 2.0,
      rho: 0.5,
      sigma: 0.5,
      maxIterations: 500,
      tolerance: 1e-6
    },
    adam: {
      learningRate: 0.001,
      beta1: 0.9,
      beta2: 0.999,
      epsilon: 1e-8,
      maxIterations: 1000,
      tolerance: 1e-6
    }
  });
  
  const calibrationIntervalRef = React.useRef<NodeJS.Timeout | null>(null);
  
  // Load parameters when model template changes
  useEffect(() => {
    if (selectedModelTemplate?.model_id) {
      const modelParams = getModelParameters(selectedModelTemplate.model_id);
      if (modelParams.length > 0) {
        setParameters(modelParams.map(p => ({ 
          ...p, 
          optimize: true, 
          value: typeof p.default === 'number' ? p.default : parseFloat(p.default as string) 
        })));
      } else {
        console.warn(`No parameters found for model ${selectedModelTemplate.model_id}, using defaults`);
        setParameters([]);
      }
    }
  }, [selectedModelTemplate]);
  
  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (calibrationIntervalRef.current) {
        clearInterval(calibrationIntervalRef.current);
      }
    };
  }, []);
  
  // Timer for elapsed time
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning) {
      interval = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRunning]);
  
  const handleParameterChange = (index: number, field: string, value: any) => {
    const updatedParams = [...parameters];
    updatedParams[index] = { ...updatedParams[index], [field]: value };
    setParameters(updatedParams);
  };

  const availableReferenceData = dataService.getReferenceData();
  
  const addReferenceData = (data: ReferenceData) => {
    if (!selectedReferenceData.find(d => d.data_id === data.data_id)) {
      setSelectedReferenceData([...selectedReferenceData, data]);
    }
  };
  
  const removeReferenceData = (dataId: string) => {
    setSelectedReferenceData(selectedReferenceData.filter(d => d.data_id !== dataId));
  };
  
  const startCalibration = () => {
    setIsRunning(true);
    setProgress(0);
    setCurrentIteration(0);
    setOptimizationStartTime(new Date());
    setElapsedTime(0);
    
    // Start progress simulation
    calibrationIntervalRef.current = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          setIsRunning(false);
          if (calibrationIntervalRef.current) {
            clearInterval(calibrationIntervalRef.current);
          }
          if (onProgressUpdate && taskId) {
            onProgressUpdate(taskId, 100, 'completed', {
              accuracy: 94 + Math.random() * 5,
              iterations: currentIteration,
              bestMetric: results.finalMetric,
              optimizer: selectedOptimizer
            });
          }
          return 100;
        }
        
        const newProgress = prev + 2;
        if (onProgressUpdate && taskId) {
          onProgressUpdate(taskId, newProgress, 'in-progress', {
            currentIteration: currentIteration + 10,
            bestMetric: results.finalMetric,
            optimizer: selectedOptimizer
          });
        }
        
        // Simulate finding a better solution periodically
        if (prev % 20 === 0 && prev > 0) {
          // Generate new best results for ALL pages
          const newResults: any = {};
          selectedReferenceData.forEach((refData) => {
            const dataPages = (refData as any).data || [];
            dataPages.forEach((page: any, idx: number) => {
              const pageId = `${refData.data_id}_${page.page || idx}`;
              // Generate results for ALL pages, not just selected ones
              newResults[pageId] = (page.curves || []).map((curve: any) => ({
                x: curve.x_values || [],
                // Simulate improved fit with each iteration
                y: (curve.y_values || []).map((y: number) => 
                  y * (0.98 + Math.random() * 0.04 - (prev / 500))
                )
              }));
            });
          });
          setBestCalibrationResults(newResults);
          setHasNewBestSolution(true);
        }
        
        return newProgress;
      });
      
      setCurrentIteration(prev => prev + 10);
    }, 1000);
    
    if (onProgressUpdate && taskId) {
      onProgressUpdate(taskId, progress, 'pending', {
        currentIteration: currentIteration,
        bestMetric: results.finalMetric,
        optimizer: selectedOptimizer
      });
    }
  };
  
  const stopCalibration = () => {
    setIsRunning(false);
    if (calibrationIntervalRef.current) {
      clearInterval(calibrationIntervalRef.current);
    }
    if (onProgressUpdate && taskId) {
      onProgressUpdate(taskId, progress, 'paused', {
        currentIteration: currentIteration,
        bestMetric: results.finalMetric,
        optimizer: selectedOptimizer
      });
    }
  };
  
  const runSimulation = () => {
    setIsSimulating(true);
    setSimulationProgress(0);
    
    // Report simulation start to parent
    if (onProgressUpdate && taskId) {
      const modelName = selectedModelTemplate?.name || 'Unknown Model';
      onProgressUpdate(`sim-${taskId}`, 0, 'running', { name: modelName, type: 'simulation' });
    }
    
    // Simulate running a simulation with progress updates
    const interval = setInterval(() => {
      setSimulationProgress(prev => {
        const newProgress = Math.min(prev + 20, 100);
        
        // Report progress to parent
        if (onProgressUpdate && taskId) {
          const modelName = selectedModelTemplate?.name || 'Unknown Model';
          onProgressUpdate(`sim-${taskId}`, newProgress, newProgress >= 100 ? 'completed' : 'running', { name: modelName, type: 'simulation' });
        }
        
        if (prev >= 100) {
          clearInterval(interval);
          setIsSimulating(false);
          
          // Generate and store simulation results for ALL pages
          const results: any = {};
          selectedReferenceData.forEach((refData) => {
            const dataPages = (refData as any).data || [];
            dataPages.forEach((page: any, idx: number) => {
              const pageId = `${refData.data_id}_${page.page || idx}`;
              // Generate simulation data for ALL pages, not just selected ones
              results[pageId] = (page.curves || []).map((curve: any) => ({
                x: curve.x_values || [],
                y: (curve.y_values || []).map((y: number) => y * (0.95 + Math.random() * 0.1))
              }));
            });
          });
          setSimulationResults(results);
          
          return 100;
        }
        return prev + 20;
      });
    }, 500); // Update every 500ms for a total of 2.5 seconds
  };
  
  const generateDocumentation = () => {
    // Start the generation progress
    setIsGeneratingReport(true);
    setReportGenerationProgress(0);
    
    // Simulate report generation with progress updates
    const interval = setInterval(() => {
      setReportGenerationProgress(prev => {
        const newProgress = Math.min(prev + 20, 100);
        
        if (newProgress >= 100) {
          clearInterval(interval);
          setIsGeneratingReport(false);
          // Set the actual documentation data
          setDocumentationData({
            model: selectedModelTemplate,
            refData: selectedReferenceData,
            params: parameters,
            calibrationResults: displayedCalibrationResults,
            timestamp: new Date().toISOString()
          });
          setDocumentationGenerated(true);
        }
        
        return newProgress;
      });
    }, 500); // Update every 500ms for a ~2.5s total generation time
  };

  const handleReleaseModel = () => {
    setIsModelReleased(true);
    // Update the task status to 'released' if we have a taskId
    if (onProgressUpdate && taskId) {
      onProgressUpdate(taskId, 100, 'released', {
        releasedAt: new Date().toISOString(),
        modelName: selectedModelTemplate?.name,
        accuracy: results.fitQuality.r2,
        finalMetric: results.finalMetric
      });
    }
  };
  
  const updatePlots = () => {
    setDisplayedCalibrationResults(bestCalibrationResults);
    setHasNewBestSolution(false);
  };

  const tabs = [
    { id: 'model' as TabType, name: 'Model & Parameters', icon: FileText },
    { id: 'reference' as TabType, name: 'Reference Data', icon: Database },
    { id: 'simulations' as TabType, name: 'Single Simulations', icon: Play },
    { id: 'calibration' as TabType, name: 'Calibration', icon: Brain },
    { id: 'montecarlo' as TabType, name: 'Monte Carlo Centering', icon: Shuffle },
    { id: 'validation' as TabType, name: 'Simulator Validation', icon: CheckCircle2 },
    { id: 'encryption' as TabType, name: 'Encryption/Obfuscation', icon: Shield },
    { id: 'documentation' as TabType, name: 'Report', icon: FileText }
  ];
  
  return (
    <div className="flex flex-col h-screen bg-gray-50 overflow-hidden">
      {/* Compact Header */}
      <div className="bg-white px-3 py-2 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <button 
            onClick={onClose} 
            className="p-1.5 hover:bg-gray-100 rounded transition-colors"
            title="Back to My Models"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Simulation & Calibration Interface</h1>
            <p className="text-gray-600 mt-2">
              Configure and run model calibration with reference data
            </p>
          </div>
        </div>
        <button onClick={onClose} className="p-1.5 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Tabs with Progress Indicators */}
      <div className="border-b border-gray-200 flex-shrink-0">
        <div className="flex items-center justify-between px-3">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-purple-500 text-purple-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4 inline-block mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
          
          {/* Progress Indicators on the right - visible from any tab */}
          <div className="flex items-center gap-3">
            {/* Simulation Progress - Changed to green theme to match Simulate button */}
            {isSimulating && (
              <div className="flex items-center gap-2 bg-green-50 px-3 py-1 rounded border border-green-200 animate-pulse">
                <RefreshCw className="w-3 h-3 text-green-600 animate-spin" />
                <span className="text-xs font-medium text-green-900">Simulating...</span>
                <div className="w-20 bg-green-200 rounded-full h-1.5 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-green-600 h-1.5 rounded-full transition-all duration-500 relative"
                    style={{ width: `${simulationProgress}%` }}
                  >
                    <div className="absolute inset-0 bg-white opacity-30 animate-shimmer"></div>
                  </div>
                </div>
                <span className="text-xs font-bold text-green-700">{simulationProgress}%</span>
                <button
                  onClick={() => {
                    setIsSimulating(false);
                    setSimulationProgress(0);
                  }}
                  className="ml-1 p-0.5 hover:bg-green-100 rounded transition-colors"
                  title="Stop Simulation"
                >
                  <X className="w-3 h-3 text-green-700" />
                </button>
              </div>
            )}
            
            {/* Calibration Progress - Purple theme to match Calibration button */}
            {isRunning && (
              <div className="flex items-center gap-2 bg-purple-50 px-3 py-1 rounded border border-purple-200 animate-pulse">
                <RefreshCw className="w-3 h-3 text-purple-600 animate-spin" />
                <span className="text-xs font-medium text-purple-900">Calibrating...</span>
                <div className="w-20 bg-purple-200 rounded-full h-1.5 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-purple-500 to-purple-600 h-1.5 rounded-full transition-all duration-500 relative"
                    style={{ width: `${progress}%` }}
                  >
                    <div className="absolute inset-0 bg-white opacity-30 animate-shimmer"></div>
                  </div>
                </div>
                <span className="text-xs font-bold text-purple-700">{progress}%</span>
                <button
                  onClick={stopCalibration}
                  className="ml-1 p-0.5 hover:bg-purple-100 rounded transition-colors"
                  title="Stop Calibration"
                >
                  <X className="w-3 h-3 text-purple-700" />
                </button>
              </div>
            )}
            
            {/* Documentation Generation Progress */}
            {isGeneratingReport && (
              <div className="flex items-center gap-2 bg-blue-50 px-3 py-1 rounded border border-blue-200 animate-pulse">
                <RefreshCw className="w-3 h-3 text-blue-600 animate-spin" />
                <span className="text-xs font-medium text-blue-900">Generating Report...</span>
                <div className="w-20 bg-blue-200 rounded-full h-1.5 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-blue-600 h-1.5 rounded-full transition-all duration-500 relative"
                    style={{ width: `${reportGenerationProgress}%` }}
                  >
                    <div className="absolute inset-0 bg-white opacity-30 animate-shimmer"></div>
                  </div>
                </div>
                <span className="text-xs font-bold text-blue-700">{reportGenerationProgress}%</span>
                <button
                  onClick={() => {
                    setIsGeneratingReport(false);
                    setReportGenerationProgress(0);
                  }}
                  className="ml-1 p-0.5 hover:bg-blue-100 rounded transition-colors"
                  title="Stop Generation"
                >
                  <X className="w-3 h-3 text-blue-700" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Tab Content */}
      <div className="flex-1 overflow-hidden p-4 bg-gray-50">
        {activeTab === 'model' && (
          <ModelTab
            selectedModelTemplate={selectedModelTemplate}
            onModelSelect={setSelectedModelTemplate}
            parameters={parameters}
            onParameterChange={handleParameterChange}
            onParametersChange={setParameters}
            parameterFilter={parameterFilter}
            onParameterFilterChange={setParameterFilter}
            parameterSort={parameterSort}
            onParameterSortChange={setParameterSort}
            parameterSortOrder={parameterSortOrder}
            onParameterSortOrderChange={setParameterSortOrder}
          />
        )}
        
        {activeTab === 'reference' && (
          <ReferenceDataTab
            selectedReferenceData={selectedReferenceData}
            onAddData={() => setShowAddDataModal(true)}
            onRemoveData={removeReferenceData}
            plotColumns={plotColumns}
            selectedDataPages={refDataSelectedPages}
            onSelectedDataPagesChange={setRefDataSelectedPages}
            expandedDatasets={refDataExpandedDatasets}
            onExpandedDatasetsChange={setRefDataExpandedDatasets}
          />
        )}
        
        {activeTab === 'simulations' && (
          <SimulationsTab
            selectedReferenceData={selectedReferenceData}
            simulationResults={simulationResults}
            onRunSimulation={runSimulation}
            isSimulating={isSimulating}
            simulationProgress={simulationProgress}
            parameters={parameters}
            onParameterChange={handleParameterChange}
            plotColumns={plotColumns}
            selectedDataPages={simulationSelectedPages}
            onSelectedDataPagesChange={setSimulationSelectedPages}
            expandedDatasets={simulationExpandedDatasets}
            onExpandedDatasetsChange={setSimulationExpandedDatasets}
          />
        )}
        
        {activeTab === 'calibration' && (
          <CalibrationTab
            calibrationView={calibrationView}
            onCalibrationViewChange={setCalibrationView}
            isRunning={isRunning}
            onStartCalibration={startCalibration}
            onStopCalibration={stopCalibration}
            selectedReferenceData={selectedReferenceData}
            onAddData={() => setShowAddDataModal(true)}
            plotColumns={plotColumns}
            displayedCalibrationResults={displayedCalibrationResults}
            hasNewBestSolution={hasNewBestSolution}
            bestCalibrationResults={bestCalibrationResults}
            onUpdatePlots={updatePlots}
            currentIteration={currentIteration}
            results={results}
            selectedDataPages={calibrationSelectedPages}
            onSelectedDataPagesChange={setCalibrationSelectedPages}
            expandedDatasets={calibrationExpandedDatasets}
            onExpandedDatasetsChange={setCalibrationExpandedDatasets}
            optimizationStartTime={optimizationStartTime}
            elapsedTime={elapsedTime}
            progress={progress}
            selectedOptimizer={selectedOptimizer}
            onOptimizerChange={setSelectedOptimizer}
            optimizerParams={optimizerParams}
            onOptimizerParamsChange={setOptimizerParams}
            showParamEvolution={showParamEvolution}
            onShowParamEvolutionChange={setShowParamEvolution}
            parameters={parameters}
            calibParamSort={calibParamSort}
            onCalibParamSortChange={setCalibParamSort}
          />
        )}
        
        {/* Monte Carlo Centering Tab */}
        {activeTab === 'montecarlo' && <MonteCarloTab />}

        {/* Simulator Validation Tab */}
        {activeTab === 'validation' && <ValidationTab />}

        {/* Encryption/Obfuscation Tab */}
        {activeTab === 'encryption' && <EncryptionTab />}
        
        {activeTab === 'documentation' && (
          <DocumentationTab
            selectedModelTemplate={selectedModelTemplate}
            selectedReferenceData={selectedReferenceData}
            parameters={parameters}
            displayedCalibrationResults={displayedCalibrationResults}
            documentationData={documentationData}
            documentationGenerated={documentationGenerated}
            isGeneratingReport={isGeneratingReport}
            reportGenerationProgress={reportGenerationProgress}
            onGenerateDocumentation={generateDocumentation}
            onReleaseModel={handleReleaseModel}
            isReleased={isModelReleased}
          />
        )}
      </div>
      
      {/* Add Reference Data Modal */}
      {showAddDataModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg w-[90%] max-w-5xl h-[70vh] flex flex-col">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Add Reference Data</h2>
              <button
                onClick={() => setShowAddDataModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Search Bar and Filters */}
            <div className="px-6 py-3 border-b border-gray-200">
              <div className="flex gap-3">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search reference data..."
                    value={dataSearchTerm}
                    onChange={(e) => setDataSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <select
                  value={dataFilterType}
                  onChange={(e) => setDataFilterType(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                >
                  <option value="all">All Types</option>
                  <option value="measurement">Measurement</option>
                  <option value="simulation">Simulation</option>
                  <option value="hybrid">Hybrid</option>
                </select>
                <select
                  value={dataFilterDevice}
                  onChange={(e) => setDataFilterDevice(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                >
                  <option value="all">All Devices</option>
                  <option value="mosfet">MOSFET</option>
                  <option value="nmos">NMOS</option>
                  <option value="pmos">PMOS</option>
                  <option value="finfet">FinFET</option>
                  <option value="bjt">BJT</option>
                  <option value="diode">Diode</option>
                  <option value="resistor">Resistor</option>
                </select>
                <button 
                  onClick={() => {
                    setDataSearchTerm('');
                    setDataFilterType('all');
                    setDataFilterDevice('all');
                  }}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
                >
                  Clear
                </button>
              </div>
            </div>

            {/* Data Table */}
            <div className="flex-1 overflow-auto px-6">
              <table className="w-full">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dataset</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Device</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Technology</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pages</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {availableReferenceData
                    .filter(data => {
                      const matchesSearch = dataSearchTerm === '' || 
                        data.name.toLowerCase().includes(dataSearchTerm.toLowerCase()) ||
                        data.type.toLowerCase().includes(dataSearchTerm.toLowerCase()) ||
                        data.device.technology.toLowerCase().includes(dataSearchTerm.toLowerCase());
                      const matchesType = dataFilterType === 'all' || data.type === dataFilterType;
                      const matchesDevice = dataFilterDevice === 'all' || 
                        data.device.type?.toLowerCase() === dataFilterDevice.toLowerCase();
                      const notSelected = !selectedReferenceData.find(selected => selected.data_id === data.data_id);
                      return matchesSearch && matchesType && matchesDevice && notSelected;
                    })
                    .map((data) => (
                      <tr key={data.data_id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{data.name}</div>
                            <div className="text-xs text-gray-500">ID: {data.data_id}</div>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">{data.type}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{data.device.type}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{data.device.technology}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{(data as any).data?.length || 0}</td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => {
                              addReferenceData(data);
                              setShowAddDataModal(false);
                              // Auto-expand newly added dataset
                              const expandedDatasets = refDataExpandedDatasets;
                              if (!expandedDatasets.includes(data.data_id)) {
                                setRefDataExpandedDatasets([...expandedDatasets, data.data_id]);
                              }
                            }}
                            className="px-3 py-1 bg-purple-600 text-white rounded text-xs hover:bg-purple-700"
                          >
                            Add
                          </button>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
              
              {availableReferenceData
                .filter(data => {
                  const matchesSearch = dataSearchTerm === '' || 
                    data.name.toLowerCase().includes(dataSearchTerm.toLowerCase()) ||
                    data.type.toLowerCase().includes(dataSearchTerm.toLowerCase()) ||
                    data.device.technology.toLowerCase().includes(dataSearchTerm.toLowerCase());
                  const matchesType = dataFilterType === 'all' || data.type === dataFilterType;
                  const matchesDevice = dataFilterDevice === 'all' || 
                    data.device.type?.toLowerCase() === dataFilterDevice.toLowerCase();
                  const notSelected = !selectedReferenceData.find(selected => selected.data_id === data.data_id);
                  return matchesSearch && matchesType && matchesDevice && notSelected;
                })
                .length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Database className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                    <p className="text-sm">No available reference data to add</p>
                    <p className="text-xs mt-1">All available datasets have been added or filtered out</p>
                  </div>
                )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
              <div className="text-sm text-gray-500">
                {availableReferenceData.filter(data => {
                  const matchesSearch = dataSearchTerm === '' || 
                    data.name.toLowerCase().includes(dataSearchTerm.toLowerCase()) ||
                    data.type.toLowerCase().includes(dataSearchTerm.toLowerCase()) ||
                    data.device.technology.toLowerCase().includes(dataSearchTerm.toLowerCase());
                  const matchesType = dataFilterType === 'all' || data.type === dataFilterType;
                  const matchesDevice = dataFilterDevice === 'all' || 
                    data.device.type?.toLowerCase() === dataFilterDevice.toLowerCase();
                  const notSelected = !selectedReferenceData.find(selected => selected.data_id === data.data_id);
                  return matchesSearch && matchesType && matchesDevice && notSelected;
                }).length} datasets found
              </div>
              <button
                onClick={() => setShowAddDataModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Parameter Evolution Modal */}
      {showParamEvolution && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg w-full max-w-7xl max-h-[90vh] flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Parameter Evolution</h2>
                <p className="text-sm text-gray-600 mt-1">
                  {selectedOptimizer === 'differentialEvolution' ? 
                    'Population distribution over generations (Histograms)' : 
                    'Parameter values over iterations (Line plots)'}
                </p>
              </div>
              <button
                onClick={() => setShowParamEvolution(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {/* Modal Content */}
            <div className="flex-1 p-6 flex flex-col min-h-0">
              <PlotGrid
                plots={parameters
                  .filter(p => p.optimize)
                  .map((param, idx) => {
                    // Generate demo data based on optimizer type
                    if (selectedOptimizer === 'differentialEvolution') {
                      // Create histogram for population-based algorithm
                      const generations = 50;
                      const populationSize = 30;
                      const center = param.value || 1.0;
                      const bestValue = center;
                      
                      const allValues = [];
                      for (let gen = 0; gen < generations; gen++) {
                        const spread = 0.5 * Math.pow(0.95, gen);
                        for (let i = 0; i < populationSize; i++) {
                          const value = center + (Math.random() - 0.5) * 2 * spread * center;
                          allValues.push(value);
                        }
                      }
                      
                      // Create histogram bins
                      const numBins = 25;
                      const minVal = Math.min(...allValues);
                      const maxVal = Math.max(...allValues);
                      const binWidth = (maxVal - minVal) / numBins;
                      
                      const binCounts = new Array(numBins).fill(0);
                      const binCenters = [];
                      
                      allValues.forEach(value => {
                        const binIndex = Math.min(
                          Math.floor((value - minVal) / binWidth),
                          numBins - 1
                        );
                        binCounts[binIndex]++;
                      });
                      
                      for (let i = 0; i < numBins; i++) {
                        binCenters.push(minVal + (i + 0.5) * binWidth);
                      }
                      
                      const maxCount = Math.max(...binCounts);
                      
                      return {
                        pageId: `param-${idx}`,
                        pageName: `${param.name}${param.unit ? ` [${param.unit}]` : ''}`,
                        xName: 'Parameter Value',
                        xUnit: param.unit || '',
                        yName: 'Frequency',
                        yUnit: '',
                        curves: [
                          {
                            x: binCenters,
                            y: binCounts,
                            name: '',
                            mode: 'lines' as const,
                            type: 'bar' as const,
                            color: 'rgba(147, 51, 234, 0.6)'
                          },
                          {
                            x: [bestValue, bestValue],
                            y: [0, maxCount * 1.1],
                            name: '',
                            mode: 'lines' as const,
                            color: 'rgba(220, 38, 38, 0.8)',
                            lineWidth: 2,
                            dash: 'dash'
                          }
                        ]
                      };
                    } else {
                      // Line plot for gradient-based optimizers
                      const iterations = 50;
                      const initialValue = param.value || 1.0;
                      const finalValue = initialValue * (1 + (Math.random() - 0.5) * 0.4);
                      
                      const evolutionData = [];
                      for (let i = 0; i <= iterations; i++) {
                        const progress = i / iterations;
                        const noise = (Math.random() - 0.5) * 0.1 * initialValue;
                        evolutionData.push(initialValue + (finalValue - initialValue) * progress + noise);
                      }
                      
                      return {
                        pageId: `param-${idx}`,
                        pageName: `${param.name}${param.unit ? ` [${param.unit}]` : ''}`,
                        xName: 'Iteration',
                        xUnit: '',
                        yName: 'Parameter Value',
                        yUnit: param.unit || '',
                        curves: [{
                          x: Array.from({ length: iterations + 1 }, (_, i) => i),
                          y: evolutionData,
                          name: '',
                          mode: 'lines' as const,
                          color: 'rgba(59, 130, 246, 0.8)',
                          lineWidth: 2
                        }]
                      };
                    }
                  })}
                columns={2}
                showColumnSelector={true}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CalibrationInterface;