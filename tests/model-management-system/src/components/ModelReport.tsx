import React from 'react';
import { 
  Code2, Database, Grid3x3, BarChart3, Download, FileText, RefreshCw, Rocket
} from 'lucide-react';
import PlotGrid from './PlotGrid';
import { Model, ReferenceData, ModelParameter } from '../types';

interface ModelReportProps {
  modelData?: Model;
  referenceData?: ReferenceData | ReferenceData[];
  parameters?: (ModelParameter & { optimize?: boolean; value?: number })[];
  calibrationResults?: any;
  timestamp?: string;
  onGenerateReport?: () => void;
  isGenerated?: boolean;
  showGenerateButton?: boolean;
  className?: string;
  isGenerating?: boolean;
  generationProgress?: number;
  onReleaseModel?: () => void;
  isReleased?: boolean;
}

const ModelReport: React.FC<ModelReportProps> = ({
  modelData,
  referenceData,
  parameters,
  calibrationResults,
  timestamp,
  onGenerateReport,
  isGenerated = true,
  showGenerateButton = false,
  className = '',
  isGenerating = false,
  generationProgress = 0,
  onReleaseModel,
  isReleased = false
}) => {
  const refDataArray = Array.isArray(referenceData) ? referenceData : referenceData ? [referenceData] : [];
  const [showReleaseConfirm, setShowReleaseConfirm] = React.useState(false);

  const handleReleaseClick = () => {
    setShowReleaseConfirm(true);
  };

  const confirmRelease = () => {
    if (onReleaseModel) {
      onReleaseModel();
    }
    setShowReleaseConfirm(false);
  };

  return (
    <div className={`flex gap-6 h-full ${className}`}>
      {/* Left Sidebar - Controls and Actions */}
      <div className="w-80 flex-shrink-0">
        <div className="bg-white rounded-lg border border-gray-200 p-6 sticky top-0">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Report Controls</h2>
          
          <div className="space-y-4">
            {/* Report Status */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Report Status</h3>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${
                  isGenerating ? 'bg-blue-500 animate-pulse' : 
                  isGenerated ? 'bg-green-500' : 'bg-gray-400'
                }`}></div>
                <span className="text-sm text-gray-600">
                  {isGenerating ? `Generating... ${generationProgress}%` : 
                   isGenerated ? 'Report Generated' : 'No Report'}
                </span>
              </div>
              {timestamp && !isGenerating && (
                <p className="text-xs text-gray-500 mt-2">
                  Last generated: {new Date(timestamp).toLocaleString()}
                </p>
              )}
            </div>

            {/* Generate/Refresh Button */}
            {showGenerateButton && onGenerateReport && (
              <button
                onClick={onGenerateReport}
                disabled={isGenerating}
                className={`w-full px-4 py-3 ${isGenerating ? 'bg-blue-500' : 'bg-blue-600 hover:bg-blue-700'} text-white rounded-lg text-sm flex items-center justify-center gap-2 transition-colors`}
              >
                {isGenerating ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4" />
                    {isGenerated ? 'Refresh Report' : 'Generate Report'}
                  </>
                )}
              </button>
            )}

            {/* Export Options */}
            {isGenerated && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-gray-700">Export Options</h3>
                <button className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                  Export as PDF
                </button>
                <button className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg text-sm hover:bg-gray-700 flex items-center justify-center gap-2">
                  <FileText className="w-4 h-4" />
                  Export as Markdown
                </button>
                <button className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50 flex items-center justify-center gap-2">
                  <Code2 className="w-4 h-4" />
                  Export as JSON
                </button>
              </div>
            )}

            {/* Quick Info */}
            {isGenerated && modelData && (
              <div className="p-4 bg-blue-50 rounded-lg">
                <h3 className="text-sm font-semibold text-blue-900 mb-2">Model Info</h3>
                <div className="space-y-1">
                  <p className="text-xs text-blue-700">
                    <span className="font-medium">Model:</span> {modelData.name}
                  </p>
                  <p className="text-xs text-blue-700">
                    <span className="font-medium">Version:</span> {modelData.version || 'N/A'}
                  </p>
                  <p className="text-xs text-blue-700">
                    <span className="font-medium">Parameters:</span> {parameters?.length || 0}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Release Model Button - Positioned below Report Controls */}
          {isGenerated && onReleaseModel && !isReleased && (
            <div className="mt-6">
              <button
                onClick={handleReleaseClick}
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg px-5 py-3 font-medium transition-all duration-200 shadow-sm hover:shadow-md transform hover:-translate-y-0.5 flex items-center justify-center gap-2.5"
              >
                <Rocket className="w-4 h-4" />
                <span>Release to Production</span>
              </button>
              <p className="text-xs text-gray-500 text-center mt-2">
                Mark as production-ready
              </p>
            </div>
          )}

          {/* Released Status */}
          {isReleased && (
            <div className="mt-4 p-4 bg-gradient-to-r from-green-100 to-emerald-100 rounded-lg border-2 border-green-500">
              <div className="flex items-center gap-2 text-green-700">
                <Rocket className="w-5 h-5" />
                <span className="font-bold text-lg">Model Released</span>
              </div>
              <p className="text-sm text-green-600 mt-1">
                This model is in production and ready for use
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Release Confirmation Modal */}
      {showReleaseConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mx-auto mb-4">
                <Rocket className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 text-center mb-2">
                Release Model to Production?
              </h3>
              <p className="text-gray-600 text-center mb-6">
                This action will mark the model as production-ready. Once released, 
                the model will be available for deployment and use in production environments.
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-6">
                <p className="text-sm text-yellow-800">
                  <strong>Note:</strong> Please ensure all validation tests have passed 
                  and documentation is complete before releasing.
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowReleaseConfirm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmRelease}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all font-semibold"
                >
                  Confirm Release
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Right Content Area - Report Display */}
      <div className="flex-1 overflow-y-auto">
        {!isGenerated && showGenerateButton ? (
          <div className="bg-gray-50 rounded-lg border border-gray-200 p-12 text-center">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Report Generated</h3>
            <p className="text-sm text-gray-600 mb-4">
              Click the "Generate Report" button to create a report based on the current model configuration.
            </p>
          </div>
        ) : isGenerated ? (
          <div className="space-y-6">
            {/* Model Information */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Code2 className="w-5 h-5 text-purple-600" />
              Model Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500 mb-1">Model Name</p>
                <p className="text-sm font-medium">{modelData?.name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Version</p>
                <p className="text-sm font-medium">{modelData?.version || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Technology</p>
                <p className="text-sm font-medium">{modelData?.base_model || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Category</p>
                <p className="text-sm font-medium">{modelData?.category || 'N/A'}</p>
              </div>
              <div className="col-span-2">
                <p className="text-xs text-gray-500 mb-1">Description</p>
                <p className="text-sm">{modelData?.description || 'No description available'}</p>
              </div>
              <div className="col-span-2">
                <p className="text-xs text-gray-500 mb-1">Report Generated</p>
                <p className="text-sm font-medium">{timestamp ? new Date(timestamp).toLocaleString() : new Date().toLocaleString()}</p>
              </div>
            </div>
          </div>

          {/* Reference Data Information */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Database className="w-5 h-5 text-blue-600" />
              Reference Data
            </h3>
            <div className="space-y-3">
              {refDataArray.length > 0 ? (
                refDataArray.map((refData: ReferenceData, idx: number) => (
                  <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <p className="text-xs text-gray-500">Dataset Name</p>
                        <p className="text-sm font-medium">{refData.name}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Type</p>
                        <p className="text-sm font-medium">{refData.type}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Technology</p>
                        <p className="text-sm font-medium">{refData.device?.technology || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Device Type</p>
                        <p className="text-sm font-medium">{refData.device?.type || 'N/A'}</p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">No reference data selected</p>
              )}
            </div>
          </div>

          {/* Key Parameters */}
          {parameters && parameters.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Grid3x3 className="w-5 h-5 text-green-600" />
                Key Parameters
              </h3>
              <div className="grid grid-cols-3 gap-3">
                {parameters.slice(0, 12).map((param: ModelParameter & { optimize?: boolean; value?: number }, idx: number) => (
                  <div key={idx} className="p-2 bg-gray-50 rounded">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-medium text-gray-700">{param.name}</span>
                      <span className="text-xs text-gray-900 font-mono">
                        {param.value ?? (param as any).default_value ?? 'N/A'}
                      </span>
                    </div>
                    {param.unit && (
                      <span className="text-xs text-gray-500">{param.unit}</span>
                    )}
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-3">
                Showing {Math.min(12, parameters.length)} of {parameters.length} parameters
              </p>
            </div>
          )}

          {/* Example Characteristic Curves */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 flex flex-col">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-600" />
              Example Characteristic Curves
            </h3>
            <div style={{ height: '500px' }}>
              <PlotGrid
                plots={[
                  {
                    pageId: 'output-char',
                    pageName: 'Output Characteristics',
                    xName: 'Vds',
                    xUnit: 'V',
                    yName: 'Ids',
                    yUnit: 'A',
                    curves: [
                      {
                        x: [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2],
                        y: [0, 1e-6, 4e-6, 9e-6, 1.6e-5, 2.5e-5, 3.6e-5],
                        name: 'Vgs=0.6V',
                        mode: 'lines' as const,
                        color: 'blue'
                      },
                      {
                        x: [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2],
                        y: [0, 2e-6, 8e-6, 1.8e-5, 3.2e-5, 5e-5, 7.2e-5],
                        name: 'Vgs=0.8V',
                        mode: 'lines' as const,
                        color: 'red'
                      },
                      {
                        x: [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2],
                        y: [0, 3e-6, 1.2e-5, 2.7e-5, 4.8e-5, 7.5e-5, 1.08e-4],
                        name: 'Vgs=1.0V',
                        mode: 'lines' as const,
                        color: 'green'
                      }
                    ]
                  },
                  {
                    pageId: 'transfer-char',
                    pageName: 'Transfer Characteristics',
                    xName: 'Vgs',
                    xUnit: 'V',
                    yName: 'Ids',
                    yUnit: 'A',
                    curves: [
                      {
                        x: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                        y: [1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 5e-8, 2e-7, 1e-6, 5e-6, 2e-5, 5e-5],
                        name: 'Vds=1.0V',
                        mode: 'lines' as const,
                        color: 'purple'
                      }
                    ]
                  }
                ]}
                columns={2}
                showColumnSelector={false}
              />
            </div>
          </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default ModelReport;