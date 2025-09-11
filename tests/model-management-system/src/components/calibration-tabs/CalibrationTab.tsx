import React, { useState } from 'react';
import { 
  Play, Pause, RefreshCw, Clock, Timer, Hourglass, 
  Activity, Target, ArrowUpDown, LineChart, ChevronRight, ChevronLeft
} from 'lucide-react';
import ReferenceDataViewer from '../shared/ReferenceDataViewer';
import PlotGrid from '../PlotGrid';
import { ReferenceData, ModelParameter } from '../../types';

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

interface CalibrationTabProps {
  calibrationView: 'refDataPlots' | 'optimizationProgress';
  onCalibrationViewChange: (view: 'refDataPlots' | 'optimizationProgress') => void;
  isRunning: boolean;
  onStartCalibration: () => void;
  onStopCalibration: () => void;
  selectedReferenceData: ReferenceData[];
  onAddData: () => void;
  plotColumns: 1 | 2 | 3;
  displayedCalibrationResults: any;
  hasNewBestSolution: boolean;
  bestCalibrationResults: any;
  onUpdatePlots: () => void;
  currentIteration: number;
  results: any;
  selectedDataPages: string[];
  onSelectedDataPagesChange: (pages: string[]) => void;
  expandedDatasets: string[];
  onExpandedDatasetsChange: (datasets: string[]) => void;
  // Progress view props
  optimizationStartTime: Date | null;
  elapsedTime: number;
  progress: number;
  selectedOptimizer: 'differentialEvolution' | 'nelderMead' | 'adam';
  onOptimizerChange?: (optimizer: 'differentialEvolution' | 'nelderMead' | 'adam') => void;
  optimizerParams?: OptimizerParams;
  onOptimizerParamsChange?: (params: OptimizerParams) => void;
  parameterEvolution?: any;
  showParamEvolution: boolean;
  onShowParamEvolutionChange: (show: boolean) => void;
  parameters?: (ModelParameter & { optimize: boolean; value?: number })[];
  calibParamSort?: 'name' | 'subckt';
  onCalibParamSortChange?: (sort: 'name' | 'subckt') => void;
}

export const CalibrationTab: React.FC<CalibrationTabProps> = ({
  calibrationView,
  onCalibrationViewChange,
  isRunning,
  onStartCalibration,
  onStopCalibration,
  selectedReferenceData,
  onAddData,
  plotColumns,
  displayedCalibrationResults,
  hasNewBestSolution,
  bestCalibrationResults,
  onUpdatePlots,
  currentIteration,
  results,
  selectedDataPages,
  onSelectedDataPagesChange,
  expandedDatasets,
  onExpandedDatasetsChange,
  optimizationStartTime,
  elapsedTime,
  progress,
  selectedOptimizer,
  onOptimizerChange,
  optimizerParams = {
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
  },
  onOptimizerParamsChange,
  showParamEvolution,
  onShowParamEvolutionChange,
  parameters = [],
  calibParamSort = 'name',
  onCalibParamSortChange
}) => {
  const [isAlgorithmCollapsed, setIsAlgorithmCollapsed] = useState(false);
  
  // Trigger resize event when panel collapses/expands to update Plotly plots
  const handleAlgorithmCollapseToggle = (collapsed: boolean) => {
    setIsAlgorithmCollapsed(collapsed);
    // Small delay to allow CSS transition to complete
    setTimeout(() => {
      window.dispatchEvent(new Event('resize'));
    }, 300);
  };
  
  const handleOptimizerParamsUpdate = (optimizer: string, field: string, value: any) => {
    if (onOptimizerParamsChange) {
      onOptimizerParamsChange({
        ...optimizerParams,
        [optimizer]: {
          ...optimizerParams[optimizer as keyof OptimizerParams],
          [field]: value
        }
      });
    }
  };

  return (
    <div className="h-full flex gap-3">
      {/* Left Panel - Optimizer Selection */}
      <div className={`${isAlgorithmCollapsed ? 'w-12' : 'w-[350px]'} bg-white rounded border border-gray-200 flex flex-col transition-all duration-300`}>
        {isAlgorithmCollapsed ? (
          // Collapsed state - vertical button with text
          <button
            onClick={() => handleAlgorithmCollapseToggle(false)}
            className="h-full flex flex-col items-center justify-between hover:bg-gray-50 transition-colors group p-2"
            title="Expand Calibration Panel"
          >
            <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-gray-800" />
            <div className="flex-1 flex items-center justify-center">
              <div className="text-xs text-gray-500 group-hover:text-gray-700 font-medium tracking-wider transform rotate-90 whitespace-nowrap">
                OPTIMIZER
              </div>
            </div>
            <Target className="w-4 h-4 text-gray-400 group-hover:text-gray-600" />
          </button>
        ) : (
          // Expanded state - full panel
          <div className="p-3 flex flex-col h-full">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold">Calibration Configuration</h3>
              <button
                onClick={() => handleAlgorithmCollapseToggle(true)}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
                title="Collapse Calibration Panel"
              >
                <ChevronLeft className="w-4 h-4 text-gray-600" />
              </button>
            </div>
        {/* Optimizer Selection Tabs */}
        <div className="flex gap-1 bg-gray-100 rounded-lg p-0.5 mb-3">
          <button
            onClick={() => onOptimizerChange?.('differentialEvolution')}
            className={`flex-1 px-2 py-1.5 rounded text-xs font-medium transition-colors ${
              selectedOptimizer === 'differentialEvolution'
                ? 'bg-white text-purple-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Differential Evolution
          </button>
          <button
            onClick={() => onOptimizerChange?.('nelderMead')}
            className={`flex-1 px-2 py-1.5 rounded text-xs font-medium transition-colors ${
              selectedOptimizer === 'nelderMead'
                ? 'bg-white text-purple-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Nelder-Mead
          </button>
          <button
            onClick={() => onOptimizerChange?.('adam')}
            className={`flex-1 px-2 py-1.5 rounded text-xs font-medium transition-colors ${
              selectedOptimizer === 'adam'
                ? 'bg-white text-purple-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Adam
          </button>
        </div>
        
        {/* Optimizer Parameters */}
        <div className="flex-1 overflow-y-auto">
          {selectedOptimizer === 'differentialEvolution' && (
            <div className="space-y-3">
              <div className="bg-blue-50 p-2 rounded">
                <p className="text-xs text-blue-700">
                  Differential Evolution is a population-based optimizer ideal for non-linear, non-convex problems.
                </p>
              </div>
              
              <div>
                <label className="text-xs font-medium text-gray-700">Population Size</label>
                <input
                  type="number"
                  value={optimizerParams.differentialEvolution.populationSize}
                  onChange={(e) => handleOptimizerParamsUpdate('differentialEvolution', 'populationSize', parseInt(e.target.value))}
                  className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-medium text-gray-700">F (Differential Weight)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={optimizerParams.differentialEvolution.F}
                    onChange={(e) => handleOptimizerParamsUpdate('differentialEvolution', 'F', parseFloat(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-700">CR (Crossover Prob)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={optimizerParams.differentialEvolution.CR}
                    onChange={(e) => handleOptimizerParamsUpdate('differentialEvolution', 'CR', parseFloat(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
              </div>
              
              <div>
                <label className="text-xs font-medium text-gray-700">Strategy</label>
                <select
                  value={optimizerParams.differentialEvolution.strategy}
                  onChange={(e) => handleOptimizerParamsUpdate('differentialEvolution', 'strategy', e.target.value)}
                  className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                >
                  <option value="best1bin">best/1/bin</option>
                  <option value="rand1bin">rand/1/bin</option>
                  <option value="currenttobest1bin">current-to-best/1/bin</option>
                </select>
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-medium text-gray-700">Max Generations</label>
                  <input
                    type="number"
                    value={optimizerParams.differentialEvolution.maxGenerations}
                    onChange={(e) => handleOptimizerParamsUpdate('differentialEvolution', 'maxGenerations', parseInt(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-700">Tolerance</label>
                  <input
                    type="number"
                    step="0.000001"
                    value={optimizerParams.differentialEvolution.tolerance}
                    onChange={(e) => handleOptimizerParamsUpdate('differentialEvolution', 'tolerance', parseFloat(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
              </div>
            </div>
          )}
          
          {selectedOptimizer === 'nelderMead' && (
            <div className="space-y-3">
              <div className="bg-green-50 p-2 rounded">
                <p className="text-xs text-green-700">
                  Nelder-Mead is a simplex-based optimizer that doesn't require gradient information.
                </p>
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-medium text-gray-700">α (Reflection)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={optimizerParams.nelderMead.alpha}
                    onChange={(e) => handleOptimizerParamsUpdate('nelderMead', 'alpha', parseFloat(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-700">γ (Expansion)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={optimizerParams.nelderMead.gamma}
                    onChange={(e) => handleOptimizerParamsUpdate('nelderMead', 'gamma', parseFloat(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-medium text-gray-700">ρ (Contraction)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={optimizerParams.nelderMead.rho}
                    onChange={(e) => handleOptimizerParamsUpdate('nelderMead', 'rho', parseFloat(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-700">σ (Shrink)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={optimizerParams.nelderMead.sigma}
                    onChange={(e) => handleOptimizerParamsUpdate('nelderMead', 'sigma', parseFloat(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-medium text-gray-700">Max Iterations</label>
                  <input
                    type="number"
                    value={optimizerParams.nelderMead.maxIterations}
                    onChange={(e) => handleOptimizerParamsUpdate('nelderMead', 'maxIterations', parseInt(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-700">Tolerance</label>
                  <input
                    type="number"
                    step="0.000001"
                    value={optimizerParams.nelderMead.tolerance}
                    onChange={(e) => handleOptimizerParamsUpdate('nelderMead', 'tolerance', parseFloat(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
              </div>
            </div>
          )}
          
          {selectedOptimizer === 'adam' && (
            <div className="space-y-3">
              <div className="bg-purple-50 p-2 rounded">
                <p className="text-xs text-purple-700">
                  Adam is an adaptive learning rate optimization algorithm ideal for neural networks and gradient-based optimization.
                </p>
              </div>
              
              <div>
                <label className="text-xs font-medium text-gray-700">Learning Rate</label>
                <input
                  type="number"
                  step="0.0001"
                  value={optimizerParams.adam.learningRate}
                  onChange={(e) => handleOptimizerParamsUpdate('adam', 'learningRate', parseFloat(e.target.value))}
                  className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-medium text-gray-700">β₁ (First Moment)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={optimizerParams.adam.beta1}
                    onChange={(e) => handleOptimizerParamsUpdate('adam', 'beta1', parseFloat(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-700">β₂ (Second Moment)</label>
                  <input
                    type="number"
                    step="0.001"
                    value={optimizerParams.adam.beta2}
                    onChange={(e) => handleOptimizerParamsUpdate('adam', 'beta2', parseFloat(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
              </div>
              
              <div>
                <label className="text-xs font-medium text-gray-700">ε (Epsilon)</label>
                <input
                  type="number"
                  step="0.00000001"
                  value={optimizerParams.adam.epsilon}
                  onChange={(e) => handleOptimizerParamsUpdate('adam', 'epsilon', parseFloat(e.target.value))}
                  className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-medium text-gray-700">Max Iterations</label>
                  <input
                    type="number"
                    value={optimizerParams.adam.maxIterations}
                    onChange={(e) => handleOptimizerParamsUpdate('adam', 'maxIterations', parseInt(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-700">Tolerance</label>
                  <input
                    type="number"
                    step="0.000001"
                    value={optimizerParams.adam.tolerance}
                    onChange={(e) => handleOptimizerParamsUpdate('adam', 'tolerance', parseFloat(e.target.value))}
                    className="w-full mt-0.5 px-2 py-1 border border-gray-300 rounded text-xs"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Algorithm Stats / Configuration Summary */}
        <div className="mt-3 p-2 bg-gray-50 rounded">
          <h4 className="text-xs font-semibold text-gray-700 mb-2">Configuration Summary</h4>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-600">Optimizer:</span>
              <span className="font-medium text-gray-900">
                {selectedOptimizer === 'differentialEvolution' ? 'Differential Evolution' :
                 selectedOptimizer === 'nelderMead' ? 'Nelder-Mead' : 'Adam'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Parameters to Optimize:</span>
              <span className="font-medium text-gray-900">
                {parameters.filter(p => p.optimize).length} / {parameters.length}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Reference Data Points:</span>
              <span className="font-medium text-gray-900">
                {selectedReferenceData.reduce((acc, data) => {
                  const pages = (data as any).data || [];
                  return acc + pages.reduce((pageAcc: number, page: any) => {
                    if (selectedDataPages.includes(`${data.data_id}_${page.page || pages.indexOf(page)}`)) {
                      const curves = page.curves || [];
                      return pageAcc + curves.reduce((curveAcc: number, curve: any) => 
                        curveAcc + (curve.x_values?.length || 0), 0);
                    }
                    return pageAcc;
                  }, 0);
                }, 0)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Selected Data Pages:</span>
              <span className="font-medium text-gray-900">
                {selectedDataPages.length}
              </span>
            </div>
          </div>
        </div>
          </div>
        )}
      </div>

      {/* Right Panel - Switchable View */}
      <div className="flex-1 bg-white rounded border border-gray-200 p-3 flex flex-col">
        {/* View Switcher and Controls */}
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold">
            {calibrationView === 'refDataPlots' ? 'Data & Plots' : 'Calibration Progress'}
          </h3>
          <div className="flex items-center gap-4">
            {/* View Switcher - moved before button with separator */}
            <div className="flex gap-1 bg-gray-100 rounded-lg p-0.5">
              <button
                onClick={() => onCalibrationViewChange('refDataPlots')}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  calibrationView === 'refDataPlots'
                    ? 'bg-white text-purple-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Data & Plots
              </button>
              <button
                onClick={() => onCalibrationViewChange('optimizationProgress')}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  calibrationView === 'optimizationProgress'
                    ? 'bg-white text-purple-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Progress
              </button>
            </div>
            
            {/* Separator */}
            <div className="h-6 w-px bg-gray-300" />
            
            {/* Start/Stop Calibration Button - moved after view switcher */}
            {!isRunning ? (
              <button
                onClick={onStartCalibration}
                className="px-3 py-1.5 bg-purple-600 text-white rounded text-xs hover:bg-purple-700 flex items-center gap-1"
              >
                <Play className="w-3 h-3" />
                Start Calibration
              </button>
            ) : (
              <button
                onClick={onStopCalibration}
                className="px-3 py-1.5 bg-red-600 text-white rounded text-xs hover:bg-red-700 flex items-center gap-1"
              >
                <Pause className="w-3 h-3" />
                Stop
              </button>
            )}
          </div>
        </div>
        
        {/* Content Area */}
        <div className="flex-1 overflow-hidden">
          {calibrationView === 'refDataPlots' ? (
            /* Reference Data and Plots View */
            <div className="h-full">
              <ReferenceDataViewer
                referenceData={selectedReferenceData}
                onAddData={onAddData}
                showAddButton={selectedReferenceData.length === 0}
                allowRemove={false}
                showValidation={false}
                plotColumns={plotColumns}
                simulationData={displayedCalibrationResults}
                compactDataView={true}
                className="h-full"
                plotTitle="Calibration Results"
                selectedDataPages={selectedDataPages}
                onSelectedDataPagesChange={onSelectedDataPagesChange}
                expandedDatasets={expandedDatasets}
                onExpandedDatasetsChange={onExpandedDatasetsChange}
                plotTitleInfo={
                  <div className="flex items-center gap-3">
                    {hasNewBestSolution && (
                      <button
                        onClick={onUpdatePlots}
                        className="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 flex items-center gap-1 animate-pulse"
                      >
                        <RefreshCw className="w-3 h-3" />
                        Update Plots
                      </button>
                    )}
                    {displayedCalibrationResults && (
                      <>
                        <div className="flex items-center gap-1 bg-gray-50 rounded px-2 py-1">
                          <span className="text-xs text-gray-500">Iteration:</span>
                          <span className="text-xs font-bold text-gray-900">
                            {currentIteration}
                          </span>
                        </div>
                        <div className="flex items-center gap-1 bg-gray-50 rounded px-2 py-1">
                          <span className="text-xs text-gray-500">Best Metric:</span>
                          <span className="text-xs font-bold text-gray-900">
                            {results.finalMetric.toExponential(3)}
                          </span>
                        </div>
                        <div className="flex items-center gap-1 bg-gray-50 rounded px-2 py-1">
                          <span className="text-xs text-gray-500">R²:</span>
                          <span className="text-xs font-bold text-gray-900">
                            {results.fitQuality.r2.toFixed(4)}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                }
              />
            </div>
          ) : (
            /* Calibration Progress View */
            <div className="h-full flex gap-3">
              {/* Left: Metrics and Info */}
              <div className="w-[380px] flex flex-col gap-2">
                {/* Status Cards Grid */}
                <div className="grid grid-cols-2 gap-2 flex-shrink-0">
                  {/* Start Time Card */}
                  <div className="bg-white rounded-lg border border-gray-200 p-3 relative">
                    <Clock className="w-8 h-8 text-gray-200 absolute right-2 top-2" />
                    <div className="text-xs text-gray-500 mb-1">Start Time</div>
                    <div className="text-sm font-bold text-gray-900">
                      {optimizationStartTime ? optimizationStartTime.toLocaleTimeString() : '-'}
                    </div>
                  </div>
                  
                  {/* Time Elapsed Card */}
                  <div className="bg-white rounded-lg border border-gray-200 p-3 relative">
                    <Timer className="w-8 h-8 text-gray-200 absolute right-2 top-2" />
                    <div className="text-xs text-gray-500 mb-1">Time Elapsed</div>
                    <div className="text-sm font-bold text-gray-900">
                      {Math.floor(elapsedTime / 60)}m {elapsedTime % 60}s
                    </div>
                  </div>
                  
                  {/* Time Remaining Card */}
                  <div className="bg-white rounded-lg border border-gray-200 p-3 relative">
                    <Hourglass className="w-8 h-8 text-gray-200 absolute right-2 top-2" />
                    <div className="text-xs text-gray-500 mb-1">Time Remaining</div>
                    <div className="text-sm font-bold text-gray-900">
                      {isRunning ? `~${Math.max(0, 50 - elapsedTime)}s` : '-'}
                    </div>
                  </div>
                  
                  {/* Iterations Card */}
                  <div className="bg-white rounded-lg border border-gray-200 p-3 relative">
                    <Activity className="w-8 h-8 text-gray-200 absolute right-2 top-2" />
                    <div className="text-xs text-gray-500 mb-1">Iterations</div>
                    <div className="text-sm font-bold text-gray-900">
                      {currentIteration} / {
                        selectedOptimizer === 'differentialEvolution' ? optimizerParams?.differentialEvolution.maxGenerations :
                        selectedOptimizer === 'nelderMead' ? optimizerParams?.nelderMead.maxIterations :
                        optimizerParams?.adam.maxIterations
                      }
                    </div>
                  </div>
                  
                  {/* Calibration Metric Card - Full Width */}
                  <div className="col-span-2 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200 p-3 relative">
                    <Target className="w-8 h-8 text-purple-200 absolute right-2 top-2" />
                    <div className="text-xs text-purple-600 mb-1">Best Metric</div>
                    <div className="text-lg font-bold text-purple-900">
                      {results.finalMetric.toExponential(3)}
                    </div>
                  </div>
                </div>
                
                {/* Calibrated Parameters - takes remaining height */}
                <div className="bg-white rounded-lg border border-gray-200 p-3 flex-1 flex flex-col min-h-0">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-2 flex-shrink-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-gray-700">Calibrated Parameters</span>
                      <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
                        {parameters.filter(p => p.optimize).length}
                      </span>
                    </div>
                    <button
                      onClick={() => onShowParamEvolutionChange(true)}
                      className="flex items-center gap-1 px-2 py-1 text-xs bg-purple-100 hover:bg-purple-200 text-purple-700 rounded transition-colors"
                      title="View Parameter Evolution"
                    >
                      <LineChart className="w-3 h-3" />
                      Evolution
                    </button>
                  </div>
                  
                  {/* Parameters Table */}
                  <div className="flex-1 min-h-0 overflow-auto">
                    <table className="w-full text-xs">
                      <thead className="bg-gray-50 sticky top-0 border-b border-gray-200">
                        <tr>
                          <th 
                            className="px-2 py-1.5 text-left text-gray-700 font-semibold cursor-pointer hover:bg-gray-100"
                            onClick={() => onCalibParamSortChange?.('name')}
                          >
                            <div className="flex items-center gap-1">
                              Name
                              {calibParamSort === 'name' && <ArrowUpDown className="w-3 h-3" />}
                            </div>
                          </th>
                          <th 
                            className="px-2 py-1.5 text-left text-gray-700 font-semibold cursor-pointer hover:bg-gray-100"
                            onClick={() => onCalibParamSortChange?.('subckt')}
                          >
                            <div className="flex items-center gap-1">
                              Subckt
                              {calibParamSort === 'subckt' && <ArrowUpDown className="w-3 h-3" />}
                            </div>
                          </th>
                          <th className="px-2 py-1.5 text-right text-gray-700 font-semibold">Value</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {parameters
                          .filter(p => p.optimize)
                          .sort((a, b) => {
                            if (calibParamSort === 'name') {
                              return a.name.localeCompare(b.name);
                            } else {
                              return (a.subckt || '').localeCompare(b.subckt || '');
                            }
                          })
                          .map((param, idx) => (
                            <tr key={`${param.name}-${param.subckt}`} className="hover:bg-gray-50">
                              <td className="px-2 py-2 font-mono text-xs">{param.name}</td>
                              <td className="px-2 py-2 text-gray-600">{param.subckt || '-'}</td>
                              <td className="px-2 py-2 text-right font-mono">
                                {param.value?.toExponential?.(3) || param.value || 'N/A'}
                              </td>
                            </tr>
                          ))
                        }
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              
              {/* Right: Convergence Plot (takes all remaining space) */}
              <div className="flex-1 h-full">
                <PlotGrid
                  plots={[{
                    pageId: 'convergence',
                    pageName: 'Convergence History',
                    xName: 'Iteration',
                    xUnit: '',
                    yName: 'Metric',
                    yUnit: '',
                    curves: [{
                      x: results.convergenceHistory.slice(0, Math.max(1, currentIteration / 5)).map((h: any) => h.iteration),
                      y: results.convergenceHistory.slice(0, Math.max(1, currentIteration / 5)).map((h: any) => h.error),
                      name: 'Metric',
                      mode: 'lines' as const,
                      color: 'red',
                      lineWidth: 2
                    }]
                  }]}
                  columns={1}
                  showColumnSelector={false}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};