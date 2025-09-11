import React, { useState, useEffect, useMemo } from 'react';
import { 
  Database, FileText, TrendingUp, CheckCircle, AlertCircle,
  ChevronDown, ChevronRight, Plus, Trash2, CircleDot, Shield, Loader2,
  Play, RefreshCw, Eye, X, Table, Settings, ChevronLeft
} from 'lucide-react';
import PlotGrid from '../PlotGrid';
import { ReferenceData } from '../../types';
import { statsCardStyles } from '../../theme';
import { SortableTable, Column } from '../ui';


interface ValidationError {
  page: string;
  curve?: number;
  issue: string;
}

interface ValidationResult {
  dataId: string;
  isValid: boolean;
  errors?: ValidationError[];
  warnings?: string[];
}

interface ReferenceDataViewerProps {
  referenceData: ReferenceData[];
  onAddData?: () => void;
  onRemoveData?: (dataId: string) => void;
  showAddButton?: boolean;
  allowRemove?: boolean;
  showValidation?: boolean;
  className?: string;
  plotColumns?: 1 | 2 | 3;
  simulationData?: Record<string, any[]>; // Simulation results keyed by pageId
  onRunSimulation?: () => void;
  isSimulating?: boolean;
  simulationProgress?: number;
  showParametersPanel?: boolean;
  parameters?: any[];
  onParameterChange?: (index: number, field: string, value: any) => void;
  compactDataView?: boolean; // Use compact view for data section
  plotTitleInfo?: React.ReactNode; // Custom content for plot title area (for calibration metrics)
  plotTitle?: string; // Custom title for the plot grid
  selectedDataPages?: string[]; // Controlled selected pages
  onSelectedDataPagesChange?: (pages: string[]) => void; // Callback for selection changes
  expandedDatasets?: string[]; // Controlled expanded datasets
  onExpandedDatasetsChange?: (datasets: string[]) => void; // Callback for expansion changes
}

const ReferenceDataViewer: React.FC<ReferenceDataViewerProps> = ({
  referenceData,
  onAddData,
  onRemoveData,
  showAddButton = false,
  allowRemove = false,
  showValidation = false,
  className = '',
  plotColumns: initialColumns = 2,
  simulationData,
  onRunSimulation,
  isSimulating = false,
  simulationProgress = 0,
  showParametersPanel = false,
  parameters = [],
  onParameterChange,
  compactDataView = false,
  plotTitleInfo,
  plotTitle,
  selectedDataPages: controlledSelectedPages,
  onSelectedDataPagesChange,
  expandedDatasets: controlledExpandedDatasets,
  onExpandedDatasetsChange
}) => {
  // Use internal state if not controlled
  const [internalExpandedDatasets, setInternalExpandedDatasets] = useState<string[]>([]);
  const [internalSelectedDataPages, setInternalSelectedDataPages] = useState<string[]>([]);
  
  // Determine which state to use
  const expandedDatasets = controlledExpandedDatasets !== undefined ? controlledExpandedDatasets : internalExpandedDatasets;
  const setExpandedDatasets = onExpandedDatasetsChange || setInternalExpandedDatasets;
  const selectedDataPages = controlledSelectedPages !== undefined ? controlledSelectedPages : internalSelectedDataPages;
  const setSelectedDataPages = onSelectedDataPagesChange || setInternalSelectedDataPages;
  const [plotColumns, setPlotColumns] = useState<1 | 2 | 3>(initialColumns);
  const [validationResults, setValidationResults] = useState<Record<string, ValidationResult>>({});
  const [validatingDataId, setValidatingDataId] = useState<string | null>(null);
  const [validationProgress, setValidationProgress] = useState(0);
  const [isDataPanelCollapsed, setIsDataPanelCollapsed] = useState(false);
  const [isParametersPanelCollapsed, setIsParametersPanelCollapsed] = useState(false);

  // Define columns for the parameters table
  const parameterColumns: Column<any>[] = useMemo(() => {
    // Helper component for value input with scientific notation
    const ValueInput: React.FC<{ value: number; index: number }> = ({ value: initialValue, index }) => {
      const [inputValue, setInputValue] = useState(initialValue.toString());
      const [isFocused, setIsFocused] = useState(false);
      
      // Format number for display: use scientific notation for very large or very small numbers
      const formatNumber = (num: number) => {
        if (isNaN(num)) return '0';
        const absNum = Math.abs(num);
        // Use scientific notation for numbers outside the range 0.0001 to 999999
        if (absNum !== 0 && (absNum < 0.0001 || absNum > 999999)) {
          return num.toExponential(3);
        }
        // For regular numbers, limit decimal places
        return Number(num.toPrecision(6)).toString();
      };
      
      useEffect(() => {
        if (!isFocused) {
          setInputValue(formatNumber(initialValue));
        }
      }, [initialValue, isFocused]);
      
      return (
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onFocus={() => {
            setIsFocused(true);
            setInputValue(initialValue.toString());
          }}
          onBlur={() => {
            setIsFocused(false);
            const parsed = parseFloat(inputValue);
            if (!isNaN(parsed)) {
              onParameterChange?.(index, 'value', parsed);
            }
            setInputValue(formatNumber(parsed || initialValue));
          }}
          className="w-full px-1 py-0.5 border border-gray-300 rounded text-xs font-mono"
        />
      );
    };

    return [
    {
      key: 'index',
      header: '#',
      sortable: false,
      render: (_, __, index) => <span className="text-gray-500">{index + 1}</span>,
      className: 'w-8',
    },
    {
      key: 'name',
      header: 'Name',
      sortable: true,
      render: (value) => <span className="font-mono">{value}</span>,
    },
    {
      key: 'subckt',
      header: 'Subckt',
      sortable: true,
      render: (value) => <span className="text-gray-600">{value || '-'}</span>,
    },
    {
      key: 'value',
      header: 'Value',
      sortable: false,
      render: (value, item, index) => {
        const numValue = item.value !== undefined ? item.value : (typeof item.default === 'number' ? item.default : parseFloat(item.default as string));
        return <ValueInput value={numValue} index={index} />;
      },
    },
  ];
  }, [onParameterChange]);
  const [showDataViewerModal, setShowDataViewerModal] = useState(false);
  const [selectedDataForViewing, setSelectedDataForViewing] = useState<any>(null);
  const [expandedPagesInModal, setExpandedPagesInModal] = useState<string[]>([]);

  // Auto-expand first dataset on mount (only once, not when user manually collapses)
  const [hasAutoExpanded, setHasAutoExpanded] = useState(false);
  useEffect(() => {
    if (referenceData.length > 0 && expandedDatasets.length === 0 && !hasAutoExpanded) {
      setExpandedDatasets([referenceData[0].data_id]);
      setHasAutoExpanded(true);
    }
  }, [referenceData, expandedDatasets.length, hasAutoExpanded, setExpandedDatasets]);

  // Trigger resize event when panel collapses/expands to update Plotly plots
  useEffect(() => {
    // Small delay to allow CSS transition to complete
    const timer = setTimeout(() => {
      window.dispatchEvent(new Event('resize'));
    }, 350);
    
    return () => clearTimeout(timer);
  }, [isDataPanelCollapsed]);

  // Calculate statistics
  const totalPages = referenceData.reduce((acc, data) => acc + ((data as any).data?.length || 0), 0);
  const totalCurves = referenceData.reduce((acc, data) => {
    const pages = (data as any).data || [];
    return acc + pages.reduce((pageAcc: number, page: any) => 
      pageAcc + (page.curves?.length || 0), 0);
  }, 0);
  const totalPoints = referenceData.reduce((acc, data) => {
    const pages = (data as any).data || [];
    return acc + pages.reduce((pageAcc: number, page: any) => {
      const curves = page.curves || [];
      return pageAcc + curves.reduce((curveAcc: number, curve: any) => 
        curveAcc + (curve.x_values?.length || 0), 0);
    }, 0);
  }, 0);

  // Validation function
  const validateDataset = async (dataId: string) => {
    setValidatingDataId(dataId);
    setValidationProgress(0);
    
    // Simulate validation with progress
    const totalSteps = 5;
    for (let i = 0; i <= totalSteps; i++) {
      setValidationProgress((i / totalSteps) * 100);
      await new Promise(resolve => setTimeout(resolve, 400));
    }

    // Find the dataset
    const dataset = referenceData.find(d => d.data_id === dataId);
    if (!dataset) return;

    // Randomly determine if data is valid (70% chance of being valid)
    const isValid = Math.random() > 0.3;
    
    let result: ValidationResult;
    
    if (isValid) {
      result = {
        dataId,
        isValid: true,
        warnings: ['Some curves show minor noise in subthreshold region']
      };
    } else {
      // Generate random validation errors
      const errors: ValidationError[] = [];
      const dataPages = (dataset as any).data || [];
      
      if (dataPages.length > 0) {
        // Random page errors
        const numErrors = Math.floor(Math.random() * 3) + 1;
        for (let i = 0; i < numErrors && i < dataPages.length; i++) {
          const page = dataPages[i];
          const errorTypes = [
            'Non-monotonic data detected',
            'Outliers in measurement values',
            'Discontinuity detected in curves',
            'Invalid parameter range',
            'Missing critical data points'
          ];
          
          errors.push({
            page: page.page || page.name || `page_${i}`,
            curve: Math.random() > 0.5 ? Math.floor(Math.random() * 3) : undefined,
            issue: errorTypes[Math.floor(Math.random() * errorTypes.length)]
          });
        }
      }
      
      result = {
        dataId,
        isValid: false,
        errors,
        warnings: ['Validation failed. Please review the issues.']
      };
    }

    setValidationResults(prev => ({ ...prev, [dataId]: result }));
    setValidatingDataId(null);
    setValidationProgress(0);
  };

  return (
    <div className={`h-full flex gap-3 ${className}`}>
      {/* Parameters Panel - Only shown when showParametersPanel is true */}
      {showParametersPanel && (
        <div className={`${isParametersPanelCollapsed ? 'w-12' : 'w-[360px]'} bg-white rounded border border-gray-200 flex flex-col transition-all duration-300`}>
          {isParametersPanelCollapsed ? (
            // Collapsed state - vertical button with text
            <button
              onClick={() => setIsParametersPanelCollapsed(false)}
              className="h-full flex flex-col items-center justify-between hover:bg-gray-50 transition-colors group p-2"
              title="Expand Parameters Panel"
            >
              <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-gray-800" />
              <div className="flex-1 flex items-center justify-center">
                <div className="text-xs text-gray-500 group-hover:text-gray-700 font-medium tracking-wider transform rotate-90 whitespace-nowrap">
                  PARAMETERS
                </div>
              </div>
              <Settings className="w-4 h-4 text-gray-400 group-hover:text-gray-600" />
            </button>
          ) : (
            // Expanded state - full panel
            <div className="p-3 flex flex-col h-full">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold">Parameters</h3>
                <div className="flex items-center gap-2">
                  {onRunSimulation && (
                    <button
                      onClick={onRunSimulation}
                      disabled={isSimulating}
                      className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
                        isSimulating 
                          ? 'bg-gray-400 cursor-not-allowed' 
                          : 'bg-green-600 hover:bg-green-700 text-white'
                      }`}
                    >
                      {isSimulating ? (
                        <>
                          <RefreshCw className="w-3 h-3 animate-spin" />
                          {simulationProgress}%
                        </>
                      ) : (
                        <>
                          <Play className="w-3 h-3" />
                          Simulate
                        </>
                      )}
                    </button>
                  )}
                  <button
                    onClick={() => setIsParametersPanelCollapsed(true)}
                    className="p-1 hover:bg-gray-100 rounded transition-colors"
                    title="Collapse Parameters Panel"
                  >
                    <ChevronLeft className="w-4 h-4 text-gray-600" />
                  </button>
                </div>
              </div>
          
              {/* Parameters Table */}
              <div className="flex-1 overflow-auto">
                <SortableTable
                  data={parameters}
                  columns={parameterColumns}
                  compact={true}
                  stickyHeader={true}
                  hoverable={true}
                  className="text-xs"
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Data Panel - Adjusted width based on compact view */}
      <div className={`${isDataPanelCollapsed ? 'w-12' : (compactDataView ? 'w-[320px]' : 'w-1/3')} bg-white rounded border border-gray-200 flex flex-col transition-all duration-300`}>
        {isDataPanelCollapsed ? (
          // Collapsed state - vertical button with text
          <button
            onClick={() => setIsDataPanelCollapsed(false)}
            className="h-full flex flex-col items-center justify-between hover:bg-gray-50 transition-colors group p-2"
            title="Expand Data Panel"
          >
            <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-gray-800" />
            <div className="flex-1 flex items-center justify-center">
              <div className="text-xs text-gray-500 group-hover:text-gray-700 font-medium tracking-wider transform rotate-90 whitespace-nowrap">
                DATA
              </div>
            </div>
            <Database className="w-4 h-4 text-gray-400 group-hover:text-gray-600" />
          </button>
        ) : (
          // Expanded state - full panel
          <div className="p-3 flex flex-col h-full">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold">Data</h3>
              <div className="flex items-center gap-2">
                {showAddButton && onAddData && (
                  <button
                    onClick={onAddData}
                    className="px-2 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 flex items-center gap-1"
                  >
                    <Plus className="w-3 h-3" />
                    Add Data
                  </button>
                )}
                <button
                  onClick={() => setIsDataPanelCollapsed(true)}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                  title="Collapse Data Panel"
                >
                  <ChevronLeft className="w-4 h-4 text-gray-600" />
                </button>
              </div>
            </div>

            {/* Data Pages Table with Collapsible Groups */}
            {referenceData.length > 0 ? (
          <div className="flex-1 overflow-auto">
            {/* Stats Cards - Always show, with mini size when in compact view */}
            <div className={`mb-3 grid grid-cols-4 ${compactDataView ? 'gap-1' : 'gap-2'}`}>
              <div className={`${compactDataView ? statsCardStyles.mini.container : `${statsCardStyles.container} ${statsCardStyles.compactPadding}`} hover:border-purple-200`}>
                {compactDataView ? (
                  <div className={statsCardStyles.mini.content}>
                    <div className={statsCardStyles.mini.iconContainerPurple}>
                      <Database className={statsCardStyles.mini.iconPurple} />
                    </div>
                    <p className={statsCardStyles.mini.label}>Datasets</p>
                    <p className={statsCardStyles.mini.value}>{referenceData.length}</p>
                  </div>
                ) : (
                  <div className={statsCardStyles.content}>
                    <div>
                      <p className={statsCardStyles.label}>Datasets</p>
                      <p className={statsCardStyles.value}>{referenceData.length}</p>
                    </div>
                    <div className={statsCardStyles.iconContainerPurple}>
                      <Database className={statsCardStyles.iconPurple} />
                    </div>
                  </div>
                )}
              </div>
              <div className={`${compactDataView ? statsCardStyles.mini.container : `${statsCardStyles.container} ${statsCardStyles.compactPadding}`} hover:border-blue-200`}>
                {compactDataView ? (
                  <div className={statsCardStyles.mini.content}>
                    <div className={statsCardStyles.mini.iconContainerBlue}>
                      <FileText className={statsCardStyles.mini.iconBlue} />
                    </div>
                    <p className={statsCardStyles.mini.label}>Pages</p>
                    <p className={statsCardStyles.mini.value}>{totalPages}</p>
                  </div>
                ) : (
                  <div className={statsCardStyles.content}>
                    <div>
                      <p className={statsCardStyles.label}>Pages</p>
                      <p className={statsCardStyles.value}>{totalPages}</p>
                    </div>
                    <div className={statsCardStyles.iconContainerBlue}>
                      <FileText className={statsCardStyles.iconBlue} />
                    </div>
                  </div>
                )}
              </div>
              <div className={`${compactDataView ? statsCardStyles.mini.container : `${statsCardStyles.container} ${statsCardStyles.compactPadding}`} hover:border-green-200`}>
                {compactDataView ? (
                  <div className={statsCardStyles.mini.content}>
                    <div className={statsCardStyles.mini.iconContainerGreen}>
                      <TrendingUp className={statsCardStyles.mini.iconGreen} />
                    </div>
                    <p className={statsCardStyles.mini.label}>Curves</p>
                    <p className={statsCardStyles.mini.value}>{totalCurves}</p>
                  </div>
                ) : (
                  <div className={statsCardStyles.content}>
                    <div>
                      <p className={statsCardStyles.label}>Curves</p>
                      <p className={statsCardStyles.value}>{totalCurves}</p>
                    </div>
                    <div className={statsCardStyles.iconContainerGreen}>
                      <TrendingUp className={statsCardStyles.iconGreen} />
                    </div>
                  </div>
                )}
              </div>
              <div className={`${compactDataView ? statsCardStyles.mini.container : `${statsCardStyles.container} ${statsCardStyles.compactPadding}`} hover:border-orange-200`}>
                {compactDataView ? (
                  <div className={statsCardStyles.mini.content}>
                    <div className={statsCardStyles.mini.iconContainerOrange}>
                      <CircleDot className={statsCardStyles.mini.iconOrange} />
                    </div>
                    <p className={statsCardStyles.mini.label}>Points</p>
                    <p className={statsCardStyles.mini.value}>
                      {totalPoints > 1000 ? `${(totalPoints/1000).toFixed(1)}k` : totalPoints}
                    </p>
                  </div>
                ) : (
                  <div className={statsCardStyles.content}>
                    <div>
                      <p className={statsCardStyles.label}>Points</p>
                      <p className={statsCardStyles.value}>
                        {totalPoints > 1000 ? `${(totalPoints/1000).toFixed(1)}k` : totalPoints}
                      </p>
                    </div>
                    <div className={statsCardStyles.iconContainerOrange}>
                      <CircleDot className={statsCardStyles.iconOrange} />
                    </div>
                  </div>
                )}
              </div>
            </div>
            
            {!compactDataView && (
              <h4 className="text-xs font-semibold text-gray-700 mb-2">Available Data Pages</h4>
            )}
            
            {/* Dataset Groups */}
            <div className="space-y-2">
              {referenceData.map((refData) => {
                const isExpanded = expandedDatasets.includes(refData.data_id);
                const dataPages = (refData as any).data || [];
                const selectedPagesCount = dataPages.filter((page: any, idx: number) => {
                  const pageId = `${refData.data_id}_${page.page || idx}`;
                  return selectedDataPages.includes(pageId);
                }).length;

                // Compact View for Simulation Tab
                if (compactDataView) {
                  return (
                    <div key={refData.data_id} className="mb-3">
                      <div 
                        className="bg-gray-50 px-2 py-1.5 rounded flex items-center justify-between cursor-pointer hover:bg-gray-100"
                        onClick={() => {
                          if (isExpanded) {
                            setExpandedDatasets(expandedDatasets.filter(id => id !== refData.data_id));
                          } else {
                            setExpandedDatasets([...expandedDatasets, refData.data_id]);
                          }
                        }}
                      >
                        <div className="flex-1">
                          <div className="text-xs font-medium">{(refData as any).name || refData.data_id}</div>
                          <div className="text-xs text-gray-500">
                            {(refData as any).device?.type || 'Unknown'} • {(refData as any).device?.technology || 'N/A'}
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          {/* View Dataset Button */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedDataForViewing({
                                dataset: refData,
                                datasetName: (refData as any).name || refData.data_id,
                                simulationData: simulationData
                              });
                              setShowDataViewerModal(true);
                            }}
                            className="p-1 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded transition-colors"
                            title="View Dataset"
                          >
                            <Eye className="w-3 h-3" />
                          </button>
                          {/* Collapse/Expand Arrow */}
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-gray-500" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-gray-500" />
                          )}
                        </div>
                      </div>
                      {isExpanded && (
                        <div className="mt-2 space-y-1">
                          {dataPages.map((page: any, idx: number) => {
                            const pageId = `${refData.data_id}_${page.page || idx}`;
                            const isSelected = selectedDataPages.includes(pageId);
                            return (
                              <div key={idx} className="flex items-center gap-2 px-2 py-1 border border-gray-100 rounded">
                                <div className="flex-1 text-xs">
                                  <div className="font-medium">{page.name || `Page ${idx + 1}`}</div>
                                  <div className="text-gray-500">
                                    {page.curves?.length || 0} curves • {page.curves?.[0]?.x_values?.length || 0} pts
                                  </div>
                                </div>
                                <span className="text-gray-400 text-xs">
                                  {page.type || 'measurement'}
                                </span>
                                {/* Toggle Switch on the right */}
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    if (!isSelected) {
                                      setSelectedDataPages([...selectedDataPages, pageId]);
                                    } else {
                                      setSelectedDataPages(selectedDataPages.filter(id => id !== pageId));
                                    }
                                  }}
                                  className={`relative inline-flex h-4 w-8 items-center rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-1 ${
                                    isSelected 
                                      ? 'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700' 
                                      : 'bg-gray-200 hover:bg-gray-300'
                                  }`}
                                >
                                  <span
                                    className={`inline-block h-3 w-3 transform rounded-full bg-white transition-all duration-200 shadow-sm ${
                                      isSelected ? 'translate-x-4' : 'translate-x-0.5'
                                    }`}
                                  />
                                </button>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                }

                // Full View (Default)
                return (
                  <div key={refData.data_id} className="border border-gray-200 rounded-lg overflow-hidden">
                    {/* Dataset Header */}
                    <div className="bg-gray-50 px-3 py-2 flex items-center justify-between">
                      <button
                        onClick={() => {
                          if (isExpanded) {
                            setExpandedDatasets(expandedDatasets.filter(id => id !== refData.data_id));
                          } else {
                            setExpandedDatasets([...expandedDatasets, refData.data_id]);
                          }
                        }}
                        className="flex-1 text-left hover:text-purple-600"
                      >
                        <div>
                          <div className="text-xs font-medium">{(refData as any).name || refData.data_id}</div>
                          <div className="text-xs text-gray-500">
                            {(refData as any).device_info?.device_type || 'Unknown'} • 
                            {(refData as any).device_info?.technology || 'N/A'} • 
                            {dataPages.length} pages • {selectedPagesCount} selected
                          </div>
                        </div>
                      </button>
                      <div className="flex items-center gap-2">
                        {/* View Dataset Button */}
                        <button
                          onClick={() => {
                            setSelectedDataForViewing({
                              dataset: refData,
                              datasetName: (refData as any).name || refData.data_id,
                              simulationData: simulationData
                            });
                            setShowDataViewerModal(true);
                          }}
                          className="p-1 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded transition-colors"
                          title="View Dataset"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        
                        {showValidation && (
                          <>
                            {validationResults[refData.data_id] && (
                              <div className={`flex items-center gap-1 px-2 py-1 rounded text-xs ${
                                validationResults[refData.data_id].isValid 
                                  ? 'bg-green-100 text-green-700' 
                                  : 'bg-red-100 text-red-700'
                              }`}>
                                {validationResults[refData.data_id].isValid ? (
                                  <>
                                    <CheckCircle className="w-3 h-3" />
                                    Valid
                                  </>
                                ) : (
                                  <>
                                    <AlertCircle className="w-3 h-3" />
                                    {validationResults[refData.data_id].errors?.length} issues
                                  </>
                                )}
                              </div>
                            )}
                            <button
                              onClick={() => validateDataset(refData.data_id)}
                              disabled={validatingDataId === refData.data_id}
                              className="px-2 py-1 bg-purple-600 text-white rounded text-xs hover:bg-purple-700 disabled:bg-gray-400 flex items-center gap-1"
                              title="Validate dataset"
                            >
                              {validatingDataId === refData.data_id ? (
                                <>
                                  <Loader2 className="w-3 h-3 animate-spin" />
                                  {Math.round(validationProgress)}%
                                </>
                              ) : (
                                <>
                                  <Shield className="w-3 h-3" />
                                  Validate
                                </>
                              )}
                            </button>
                          </>
                        )}
                        {allowRemove && onRemoveData && (
                          <button
                            onClick={() => onRemoveData(refData.data_id)}
                            className="p-1 hover:bg-red-100 rounded group"
                            title="Remove dataset"
                          >
                            <Trash2 className="w-3 h-3 text-gray-400 group-hover:text-red-500" />
                          </button>
                        )}
                        {/* Collapse/Expand Arrow */}
                        <button
                          onClick={() => {
                            if (isExpanded) {
                              setExpandedDatasets(expandedDatasets.filter(id => id !== refData.data_id));
                            } else {
                              setExpandedDatasets([...expandedDatasets, refData.data_id]);
                            }
                          }}
                          className="p-1 hover:bg-gray-100 rounded transition-colors"
                          title={isExpanded ? "Collapse" : "Expand"}
                        >
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-gray-500" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-gray-500" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Dataset Pages Table */}
                    {isExpanded && (
                      <div className="bg-white">
                        <table className="w-full text-xs">
                          <thead className="bg-gray-100">
                            <tr>
                              <th className="px-2 py-1 text-left">Page Name</th>
                              <th className="px-2 py-1 text-left">Type</th>
                              <th className="px-2 py-1 text-left">Axes</th>
                              <th className="px-2 py-1 text-left">Data</th>
                              <th className="px-2 py-1 text-left">Conditions</th>
                              <th className="px-2 py-1 text-center w-12">Plot</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-100">
                            {dataPages.map((page: any, idx: number) => {
                              const pageId = `${refData.data_id}_${page.page || idx}`;
                              const isSelected = selectedDataPages.includes(pageId);
                              const validationResult = validationResults[refData.data_id];
                              const pageErrors = validationResult?.errors?.filter(
                                e => e.page === (page.page || page.name || `page_${idx}`)
                              );
                              const hasErrors = pageErrors && pageErrors.length > 0;
                              
                              return (
                                <tr key={pageId} className={`hover:bg-gray-50 ${hasErrors ? 'bg-red-50' : ''}`}>
                                  <td className="px-2 py-1 font-medium">
                                    <div className="flex items-center gap-1">
                                      {page.name || `Page ${idx + 1}`}
                                      {hasErrors && (
                                        <div className="group relative">
                                          <AlertCircle className="w-3 h-3 text-red-500" />
                                          <div className="absolute left-0 bottom-full mb-1 hidden group-hover:block z-10 w-64 p-2 bg-white border border-red-200 rounded shadow-lg">
                                            <div className="text-xs text-red-700">
                                              {pageErrors.map((error, i) => (
                                                <div key={i} className="mb-1">
                                                  {error.curve !== undefined && `Curve ${error.curve + 1}: `}
                                                  {error.issue}
                                                </div>
                                              ))}
                                            </div>
                                          </div>
                                        </div>
                                      )}
                                    </div>
                                  </td>
                                  <td className="px-2 py-1">
                                    <span className="px-1 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                                      {page.type || page.testbench_type || 'measurement'}
                                    </span>
                                  </td>
                                  <td className="px-2 py-1">
                                    <div className="text-xs">
                                      <div>X: {page.x_name} ({page.x_unit || '-'})</div>
                                      <div>Y: {page.y_name} ({page.y_unit || '-'})</div>
                                      {page.extra_var_name && (
                                        <div>Sweep: {page.extra_var_name} ({page.extra_var_unit || '-'})</div>
                                      )}
                                    </div>
                                  </td>
                                  <td className="px-2 py-1">
                                    <div className="text-xs">
                                      <div>{page.curves ? page.curves.length : 0} curves</div>
                                      <div>{page.curves && page.curves[0] ? page.curves[0].x_values.length : 0} pts</div>
                                    </div>
                                  </td>
                                  <td className="px-2 py-1 text-xs">
                                    {page.operating_conditions ? (
                                      <div className="text-gray-600">
                                        <div>T={page.operating_conditions.temp || 25}°C</div>
                                        {page.operating_conditions.vbs !== undefined && (
                                          <div>VBS={page.operating_conditions.vbs}V</div>
                                        )}
                                        {page.operating_conditions.vds !== undefined && (
                                          <div>VDS={page.operating_conditions.vds}V</div>
                                        )}
                                      </div>
                                    ) : '-'}
                                  </td>
                                  <td className="px-2 py-2 text-center">
                                    {/* Toggle Switch */}
                                    <button
                                      onClick={() => {
                                        if (!isSelected) {
                                          setSelectedDataPages([...selectedDataPages, pageId]);
                                        } else {
                                          setSelectedDataPages(selectedDataPages.filter(id => id !== pageId));
                                        }
                                      }}
                                      className={`relative inline-flex h-4 w-8 items-center rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-1 ${
                                        isSelected 
                                          ? 'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700' 
                                          : 'bg-gray-200 hover:bg-gray-300'
                                      }`}
                                    >
                                      <span
                                        className={`inline-block h-3 w-3 transform rounded-full bg-white transition-all duration-200 shadow-sm ${
                                          isSelected ? 'translate-x-4' : 'translate-x-0.5'
                                        }`}
                                      />
                                      <span className="sr-only">
                                        {isSelected ? 'Deselect' : 'Select'} for plotting
                                      </span>
                                    </button>
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <Database className="w-12 h-12 mx-auto mb-2" />
                  <p className="text-sm">No reference data selected</p>
                  {showAddButton && (
                    <p className="text-xs mt-1">Click "Add Data" to select datasets</p>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right Panel - Data Visualization */}
      <div className="flex-1 bg-white rounded border border-gray-200 p-3 flex flex-col">
        <PlotGrid
          key={`plot-grid-${simulationData ? 'sim' : 'ref'}`}
          title={plotTitle || (simulationData ? "Simulation Results" : "Data Visualization")}
          titleInfo={plotTitleInfo}
          plots={(() => {
            const plotsData: any[] = [];
            const colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown', 'pink', 'gray'];
            
            referenceData.forEach((refData) => {
              const dataPages = (refData as any).data || [];
              dataPages.forEach((page: any, idx: number) => {
                const pageId = `${refData.data_id}_${page.page || idx}`;
                if (selectedDataPages.includes(pageId)) {
                  // Reference data curves (markers)
                  const refCurves = (page.curves || []).map((curve: any, curveIdx: number) => ({
                    x: curve.x_values || [],
                    y: curve.y_values || [],
                    name: curve.extra_var_value !== undefined 
                      ? `${page.extra_var_name}=${curve.extra_var_value}${page.extra_var_unit || ''}`
                      : `Curve ${curveIdx + 1}`,
                    mode: simulationData ? 'markers' : 'lines+markers',
                    color: colors[curveIdx % colors.length],
                    lineWidth: 1.5,
                    markerSize: simulationData ? 4 : 3,
                    showlegend: !simulationData // Hide reference curves in legend when simulation data exists
                  }));
                  
                  // Simulation data curves (lines) - if available
                  const simCurves = simulationData?.[pageId] ? 
                    (simulationData[pageId] || []).map((simCurve: any, curveIdx: number) => ({
                      x: simCurve.x || [],
                      y: simCurve.y || [],
                      name: (page.curves?.[curveIdx] && page.curves[curveIdx].extra_var_value !== undefined)
                        ? `${page.extra_var_name}=${page.curves[curveIdx].extra_var_value}${page.extra_var_unit || ''}`
                        : `Curve ${curveIdx + 1}`,
                      mode: 'lines',
                      color: colors[curveIdx % colors.length],
                      lineWidth: 2,
                      dash: 'solid',
                      showlegend: true
                    })) : [];
                  
                  plotsData.push({
                    pageId,
                    pageName: page.name || `Page ${idx + 1}`,
                    datasetName: (refData as any).name || refData.data_id,
                    xName: page.x_name,
                    xUnit: page.x_unit,
                    yName: page.y_name,
                    yUnit: page.y_unit,
                    curves: [...refCurves, ...simCurves]
                  });
                }
              });
            });
            
            return plotsData;
          })()}
          columns={plotColumns}
          onColumnsChange={setPlotColumns}
          showColumnSelector={true}
          maxHeight="calc(100vh - 200px)"
        />
      </div>
      
      {/* Data Viewer Modal */}
      {showDataViewerModal && selectedDataForViewing && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
          {/* Modal Header */}
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Table className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Dataset Viewer</h2>
                <p className="text-sm text-gray-500">
                  {selectedDataForViewing.datasetName}
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                setShowDataViewerModal(false);
                setSelectedDataForViewing(null);
                setExpandedPagesInModal([]);
              }}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Modal Content - Split Layout */}
          <div className="flex-1 flex min-h-0">
            {/* Left Panel - Navigation */}
            <div className="w-80 bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto">
              {/* Dataset Information */}
              <div className="mb-6">
                {((selectedDataForViewing.dataset as any).device_info?.device_type || (selectedDataForViewing.dataset as any).device_info?.technology) && (
                  <div className="bg-white rounded-lg p-3 border border-gray-200 mb-3">
                    <div className="text-xs text-gray-500">
                      {[
                        (selectedDataForViewing.dataset as any).device_info?.device_type,
                        (selectedDataForViewing.dataset as any).device_info?.technology
                      ].filter(Boolean).join(' • ')}
                    </div>
                  </div>
                )}
                
                {/* Stats Cards */}
                <div className="grid grid-cols-3 gap-1">
                  <div className={statsCardStyles.mini.container}>
                    <div className={statsCardStyles.mini.content}>
                      <div className={statsCardStyles.mini.iconContainerBlue}>
                        <FileText className={statsCardStyles.mini.iconBlue} />
                      </div>
                      <p className={statsCardStyles.mini.label}>Pages</p>
                      <p className={statsCardStyles.mini.value}>
                        {((selectedDataForViewing.dataset as any).data || []).length}
                      </p>
                    </div>
                  </div>
                  <div className={statsCardStyles.mini.container}>
                    <div className={statsCardStyles.mini.content}>
                      <div className={statsCardStyles.mini.iconContainerGreen}>
                        <TrendingUp className={statsCardStyles.mini.iconGreen} />
                      </div>
                      <p className={statsCardStyles.mini.label}>Curves</p>
                      <p className={statsCardStyles.mini.value}>
                        {((selectedDataForViewing.dataset as any).data || []).reduce((acc: number, page: any) => acc + (page.curves?.length || 0), 0)}
                      </p>
                    </div>
                  </div>
                  <div className={statsCardStyles.mini.container}>
                    <div className={statsCardStyles.mini.content}>
                      <div className={statsCardStyles.mini.iconContainerOrange}>
                        <CircleDot className={statsCardStyles.mini.iconOrange} />
                      </div>
                      <p className={statsCardStyles.mini.label}>Points</p>
                      <p className={statsCardStyles.mini.value}>
                        {(() => {
                          const totalPoints = ((selectedDataForViewing.dataset as any).data || []).reduce((acc: number, page: any) => 
                            acc + (page.curves || []).reduce((curveAcc: number, curve: any) => curveAcc + (curve.x_values?.length || 0), 0), 0
                          );
                          return totalPoints > 1000 ? `${(totalPoints/1000).toFixed(1)}k` : totalPoints;
                        })()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Page Navigation - PDF Bookmark Style */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Navigation</h3>
                <div className="space-y-1">
                  {((selectedDataForViewing.dataset as any).data || []).map((page: any, idx: number) => {
                    const pageId = `${selectedDataForViewing.dataset.data_id}_${page.page || idx}`;
                    const isPageExpanded = expandedPagesInModal.includes(pageId);
                    
                    return (
                      <div key={pageId} className="border-l-2 border-gray-200">
                        {/* Page Header - Bookmark Style */}
                        <div className="flex items-center">
                          <button
                            onClick={() => {
                              if (isPageExpanded) {
                                setExpandedPagesInModal(expandedPagesInModal.filter(id => id !== pageId));
                              } else {
                                setExpandedPagesInModal([...expandedPagesInModal, pageId]);
                              }
                            }}
                            className="p-1 hover:bg-gray-100 rounded"
                          >
                            {isPageExpanded ? (
                              <ChevronDown className="w-3 h-3 text-gray-500" />
                            ) : (
                              <ChevronRight className="w-3 h-3 text-gray-500" />
                            )}
                          </button>
                          <button
                            onClick={() => {
                              const element = document.getElementById(`page-${pageId}`);
                              element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            }}
                            className="flex-1 p-2 text-left hover:bg-blue-50 rounded text-sm font-medium text-gray-700 hover:text-blue-600"
                          >
                            📄 {page.name || `Page ${idx + 1}`}
                          </button>
                        </div>
                        
                        {/* Curves List - Sub-bookmarks */}
                        {isPageExpanded && (
                          <div className="ml-4 border-l-2 border-gray-100">
                            {(page.curves || []).map((curve: any, curveIdx: number) => (
                              <button
                                key={curveIdx}
                                onClick={() => {
                                  const element = document.getElementById(`curve-${pageId}-${curveIdx}`);
                                  element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                }}
                                className="w-full p-2 pl-4 text-left hover:bg-blue-50 rounded text-xs text-gray-600 hover:text-blue-600 flex items-center"
                              >
                                <span className="text-gray-400 mr-2">📈</span>
                                Curve {curveIdx + 1}
                                {curve.extra_var_value !== undefined && (
                                  <span className="text-purple-600 ml-1">
                                    ({page.extra_var_name} = {curve.extra_var_value}{page.extra_var_unit || ''})
                                  </span>
                                )}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Right Panel - Data Tables */}
            <div className="flex-1 p-6 overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">All Pages Data</h3>
                <button
                  onClick={() => {
                    // Export entire dataset as CSV
                    let csv = `Dataset: ${selectedDataForViewing.datasetName}\n\n`;
                    
                    ((selectedDataForViewing.dataset as any).data || []).forEach((page: any, pageIdx: number) => {
                      csv += `Page: ${page.name || `Page ${pageIdx + 1}`}\n`;
                      csv += `X-Axis: ${page.x_name} (${page.x_unit || '-'})\n`;
                      csv += `Y-Axis: ${page.y_name} (${page.y_unit || '-'})\n\n`;
                      
                      (page.curves || []).forEach((curve: any, curveIdx: number) => {
                        csv += `Curve ${curveIdx + 1}`;
                        if (curve.extra_var_value !== undefined) {
                          csv += ` (${page.extra_var_name} = ${curve.extra_var_value}${page.extra_var_unit || ''})`;
                        }
                        csv += '\n';
                        csv += `${page.x_name},${page.y_name}\n`;
                        
                        (curve.x_values || []).forEach((x: number, idx: number) => {
                          csv += `${x},${curve.y_values[idx]}\n`;
                        });
                        csv += '\n';
                      });
                      csv += '\n';
                    });
                    
                    const blob = new Blob([csv], { type: 'text/csv' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${selectedDataForViewing.datasetName}_complete_dataset.csv`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="px-3 py-1.5 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-sm flex items-center gap-2"
                >
                  <FileText className="w-4 h-4" />
                  Export Dataset CSV
                </button>
              </div>

              {/* All Pages with Expandable Curves */}
              {((selectedDataForViewing.dataset as any).data || []).map((page: any, pageIdx: number) => {
                const pageId = `${selectedDataForViewing.dataset.data_id}_${page.page || pageIdx}`;
                
                return (
                  <div key={pageId} id={`page-${pageId}`} className="mb-8">
                    {/* Page Header */}
                    <div className="mb-4">
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">
                        {page.name || `Page ${pageIdx + 1}`}
                      </h4>
                      <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
                        <span><strong>X-Axis:</strong> {page.x_name} {page.x_unit && `(${page.x_unit})`}</span>
                        <span><strong>Y-Axis:</strong> {page.y_name} {page.y_unit && `(${page.y_unit})`}</span>
                        {page.extra_var_name && (
                          <span><strong>Sweep:</strong> {page.extra_var_name} {page.extra_var_unit && `(${page.extra_var_unit})`}</span>
                        )}
                        <span><strong>Curves:</strong> {(page.curves || []).length}</span>
                      </div>
                    </div>

                    {/* Operating Conditions */}
                    {page.operating_conditions && (
                      <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <h5 className="text-sm font-semibold text-blue-800 mb-2">Operating Conditions</h5>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                          {page.operating_conditions.temp !== undefined && (
                            <span className="text-blue-700"><strong>Temp:</strong> {page.operating_conditions.temp}°C</span>
                          )}
                          {page.operating_conditions.vbs !== undefined && (
                            <span className="text-blue-700"><strong>VBS:</strong> {page.operating_conditions.vbs}V</span>
                          )}
                          {page.operating_conditions.vds !== undefined && (
                            <span className="text-blue-700"><strong>VDS:</strong> {page.operating_conditions.vds}V</span>
                          )}
                          {page.operating_conditions.vgs !== undefined && (
                            <span className="text-blue-700"><strong>VGS:</strong> {page.operating_conditions.vgs}V</span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Curves */}
                    {(page.curves || []).map((curve: any, curveIdx: number) => (
                      <div key={curveIdx} id={`curve-${pageId}-${curveIdx}`} className="mb-6">
                        <div className="flex items-center justify-between mb-3">
                          <h5 className="text-md font-medium text-gray-800">
                            Curve {curveIdx + 1}
                            {curve.extra_var_value !== undefined && (
                              <span className="ml-2 text-purple-600">
                                ({page.extra_var_name} = {curve.extra_var_value}{page.extra_var_unit || ''})
                              </span>
                            )}
                          </h5>
                          <span className="text-xs text-gray-500">
                            {(curve.x_values || []).length} data points
                          </span>
                        </div>
                        
                        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                          <table className="w-full text-sm">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 border-b border-gray-200">
                                  Index
                                </th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 border-b border-gray-200">
                                  {page.x_name} {page.x_unit && `(${page.x_unit})`}
                                </th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 border-b border-gray-200">
                                  {page.y_name} (Reference) {page.y_unit && `(${page.y_unit})`}
                                </th>
                                {selectedDataForViewing.simulationData && selectedDataForViewing.simulationData[pageId] && selectedDataForViewing.simulationData[pageId][curveIdx] && (
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 border-b border-gray-200">
                                    {page.y_name} (Simulation) {page.y_unit && `(${page.y_unit})`}
                                  </th>
                                )}
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                              {(curve.x_values || []).map((xVal: number, idx: number) => (
                                <tr key={idx} className="hover:bg-gray-50">
                                  <td className="px-4 py-2 text-gray-600">{idx + 1}</td>
                                  <td className="px-4 py-2 font-mono text-gray-900">
                                    {typeof xVal === 'number' ? xVal.toExponential(3) : xVal}
                                  </td>
                                  <td className="px-4 py-2 font-mono text-gray-900">
                                    {typeof curve.y_values[idx] === 'number' 
                                      ? curve.y_values[idx].toExponential(3) 
                                      : curve.y_values[idx]}
                                  </td>
                                  {selectedDataForViewing.simulationData && selectedDataForViewing.simulationData[pageId] && selectedDataForViewing.simulationData[pageId][curveIdx] && (
                                    <td className="px-4 py-2 font-mono text-green-700">
                                      {typeof selectedDataForViewing.simulationData[pageId][curveIdx].y[idx] === 'number' 
                                        ? selectedDataForViewing.simulationData[pageId][curveIdx].y[idx].toExponential(3) 
                                        : selectedDataForViewing.simulationData[pageId][curveIdx].y[idx]}
                                    </td>
                                  )}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
      )}
    </div>
  );
};

export default ReferenceDataViewer;