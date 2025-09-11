import React, { useState, useMemo } from 'react';
import { 
  FileText, Code2, Grid3x3, Info, Search,
  Edit, X
} from 'lucide-react';
import { Model, ModelParameter } from '../../types';
import dataService from '../../services/dataService';
import FileViewer from '../FileViewer';
import { SortableTable, Column } from '../ui';

interface ModelTabProps {
  selectedModelTemplate?: Model;
  onModelSelect: (model: Model) => void;
  parameters: (ModelParameter & { optimize: boolean; value?: number })[];
  onParameterChange: (index: number, field: string, value: any) => void;
  onParametersChange?: (params: (ModelParameter & { optimize: boolean; value?: number })[]) => void;
  parameterFilter: string;
  onParameterFilterChange: (filter: string) => void;
  parameterSort: 'name' | 'value' | 'subckt';
  onParameterSortChange: (sort: 'name' | 'value' | 'subckt') => void;
  parameterSortOrder: 'asc' | 'desc';
  onParameterSortOrderChange: (order: 'asc' | 'desc') => void;
}

const ModelTab: React.FC<ModelTabProps> = ({
  selectedModelTemplate,
  onModelSelect,
  parameters,
  onParameterChange,
  onParametersChange,
  parameterFilter,
  onParameterFilterChange,
  parameterSort,
  onParameterSortChange,
  parameterSortOrder,
  onParameterSortOrderChange
}) => {
  const [showModelSelector, setShowModelSelector] = useState(false);
  const [fileViewerOpen, setFileViewerOpen] = useState(false);
  const [fileViewerType, setFileViewerType] = useState<'cir' | 'parameters' | 'info' | 'documentation'>('cir');
  const [fileViewerName, setFileViewerName] = useState('');
  const [modelSearchTerm, setModelSearchTerm] = useState('');
  const [modelFilterCategory, setModelFilterCategory] = useState('all');
  const [modelFilterStatus, setModelFilterStatus] = useState('all');

  const availableModels = dataService.getModelTemplates();

  const filteredModels = availableModels.filter(model => {
    const matchesSearch = modelSearchTerm === '' || 
      model.name.toLowerCase().includes(modelSearchTerm.toLowerCase()) ||
      model.base_model.toLowerCase().includes(modelSearchTerm.toLowerCase());
    const matchesCategory = modelFilterCategory === 'all' || model.category === modelFilterCategory;
    const matchesStatus = modelFilterStatus === 'all' || model.status === modelFilterStatus;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const openFileViewer = (type: 'cir' | 'parameters' | 'info' | 'documentation', fileName: string) => {
    setFileViewerType(type);
    setFileViewerName(fileName);
    setFileViewerOpen(true);
  };

  const filteredParameters = parameters.filter(param => 
    param.name.toLowerCase().includes(parameterFilter.toLowerCase()) ||
    param.subckt?.toLowerCase().includes(parameterFilter.toLowerCase())
  );

  const sortedParameters = filteredParameters;

  // Define columns for the sortable table
  const parameterColumns: Column<any>[] = useMemo(() => [
    {
      key: 'index',
      header: '#',
      sortable: false,
      render: (_, __, index) => <span className="text-gray-500">{index + 1}</span>,
      className: 'w-8',
    },
    {
      key: 'optimize',
      header: (
        <input
          type="checkbox"
          className="rounded"
          checked={filteredParameters.length > 0 && filteredParameters.every(p => p.optimize)}
          onChange={(e) => {
            const newParams = parameters.map(p => ({ ...p, optimize: e.target.checked }));
            if (onParametersChange) {
              onParametersChange(newParams);
            }
          }}
        />
      ),
      sortable: false,
      render: (value, item) => {
        const originalIdx = parameters.findIndex(p => p.name === item.name && p.subckt === item.subckt);
        return (
          <input
            type="checkbox"
            checked={item.optimize}
            onChange={(e) => onParameterChange(originalIdx, 'optimize', e.target.checked)}
            className="rounded"
            onClick={(e) => e.stopPropagation()}
          />
        );
      },
      className: 'w-8',
      headerClassName: 'w-8',
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
      render: (value, item) => {
        const originalIdx = parameters.findIndex(p => p.name === item.name && p.subckt === item.subckt);
        return (
          <input
            type="text"
            value={value || ''}
            onChange={(e) => onParameterChange(originalIdx, 'subckt', e.target.value)}
            className="w-24 px-1 py-0.5 border border-gray-300 rounded text-xs"
            placeholder="-"
          />
        );
      },
    },
    {
      key: 'value',
      header: 'Value',
      sortable: false,
      render: (value, item) => {
        const originalIdx = parameters.findIndex(p => p.name === item.name && p.subckt === item.subckt);
        const displayValue = item.value !== undefined ? item.value : (typeof item.default === 'number' ? item.default : parseFloat(item.default as string));
        return (
          <input
            type="number"
            value={displayValue}
            onChange={(e) => onParameterChange(originalIdx, 'value', parseFloat(e.target.value))}
            className="w-20 px-1 py-0.5 border border-gray-300 rounded text-xs"
            step="any"
          />
        );
      },
    },
    {
      key: 'min',
      header: 'Min',
      sortable: false,
      render: (value, item) => {
        const originalIdx = parameters.findIndex(p => p.name === item.name && p.subckt === item.subckt);
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => onParameterChange(originalIdx, 'min', parseFloat(e.target.value))}
            className="w-20 px-1 py-0.5 border border-gray-300 rounded text-xs"
            step="any"
          />
        );
      },
    },
    {
      key: 'max',
      header: 'Max',
      sortable: false,
      render: (value, item) => {
        const originalIdx = parameters.findIndex(p => p.name === item.name && p.subckt === item.subckt);
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => onParameterChange(originalIdx, 'max', parseFloat(e.target.value))}
            className="w-20 px-1 py-0.5 border border-gray-300 rounded text-xs"
            step="any"
          />
        );
      },
    },
    {
      key: 'unit',
      header: 'Unit',
      sortable: false,
      render: (value) => <span className="text-gray-600">{value}</span>,
    },
    {
      key: 'description',
      header: 'Description',
      sortable: false,
      render: (value) => <span className="text-gray-600 text-xs">{value}</span>,
    },
  ], [parameters, onParameterChange, filteredParameters, onParametersChange]);

  return (
    <div className="h-full">
      {selectedModelTemplate ? (
        <div className="h-full grid grid-cols-[400px_1fr] gap-4">
          {/* Left Side - Model Information */}
          <div className="bg-white rounded-lg border-2 border-gray-200 flex flex-col h-full overflow-hidden">
            <div className="flex items-center justify-between p-4 pb-2 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-900">Model Information</h3>
              <button
                onClick={() => setShowModelSelector(true)}
                className="px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700 flex items-center gap-2"
              >
                <Edit className="w-3 h-3" />
                Change Model
              </button>
            </div>
            
            {/* Scrollable content area */}
            <div className="flex-1 overflow-y-auto p-4">
              <div className="space-y-4">
                {/* Model Header */}
                <div>
                  <h4 className="text-base font-bold text-gray-900">{selectedModelTemplate.name}</h4>
                  <p className="text-sm text-gray-500 mt-1">ID: {selectedModelTemplate.model_id}</p>
                  <div className="flex gap-2 mt-2">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      selectedModelTemplate.status === 'production' ? 'bg-green-100 text-green-800' :
                      selectedModelTemplate.status === 'validated' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {selectedModelTemplate.status}
                    </span>
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                      v{selectedModelTemplate.version}
                    </span>
                  </div>
                </div>

                {/* Description */}
                {selectedModelTemplate.description && (
                  <div>
                    <h5 className="text-sm font-semibold text-gray-700 mb-1">Description</h5>
                    <p className="text-sm text-gray-600">{selectedModelTemplate.description}</p>
                  </div>
                )}

                {/* Model Actions - Highlighted Section */}
                <div className="bg-gray-50 rounded-lg p-3">
                  <h5 className="text-sm font-semibold text-gray-700 mb-2">Quick Actions</h5>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => openFileViewer('cir', selectedModelTemplate.files?.entry_point || 'main.cir')}
                      className="flex-1 px-2 py-1.5 bg-blue-50 text-blue-600 rounded text-xs hover:bg-blue-100 flex items-center justify-center gap-1 border border-blue-200"
                    >
                      <Code2 className="w-3 h-3" />
                      Circuit
                    </button>
                    <button 
                      onClick={() => openFileViewer('parameters', selectedModelTemplate.files?.parameters_file || 'parameters.csv')}
                      className="flex-1 px-2 py-1.5 bg-green-50 text-green-600 rounded text-xs hover:bg-green-100 flex items-center justify-center gap-1 border border-green-200"
                    >
                      <Grid3x3 className="w-3 h-3" />
                      Parameters
                    </button>
                    <button 
                      onClick={() => openFileViewer('info', selectedModelTemplate.files?.metadata_file || 'metadata.json')}
                      className="flex-1 px-2 py-1.5 bg-yellow-50 text-yellow-600 rounded text-xs hover:bg-yellow-100 flex items-center justify-center gap-1 border border-yellow-200"
                    >
                      <Info className="w-3 h-3" />
                      Info
                    </button>
                  </div>
                </div>
                
                {/* Files Section */}
                <div>
                  <h5 className="text-sm font-semibold text-gray-700 mb-2">Files</h5>
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2 text-sm">
                      <Code2 className="w-4 h-4 text-blue-500" />
                      <span className="font-medium">Entry Point:</span>
                      <button 
                        onClick={() => openFileViewer('cir', selectedModelTemplate.files?.entry_point || 'main.cir')}
                        className="text-blue-600 hover:underline text-sm"
                      >
                        {selectedModelTemplate.files?.entry_point || 'main.cir'}
                      </button>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Grid3x3 className="w-4 h-4 text-green-500" />
                      <span className="font-medium">Parameters:</span>
                      <button 
                        onClick={() => openFileViewer('parameters', selectedModelTemplate.files?.parameters_file || 'parameters.csv')}
                        className="text-blue-600 hover:underline text-sm"
                      >
                        {selectedModelTemplate.files?.parameters_file || 'parameters.csv'}
                      </button>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Info className="w-4 h-4 text-yellow-500" />
                      <span className="font-medium">Metadata:</span>
                      <button 
                        onClick={() => openFileViewer('info', selectedModelTemplate.files?.metadata_file || 'metadata.json')}
                        className="text-blue-600 hover:underline text-sm"
                      >
                        {selectedModelTemplate.files?.metadata_file || 'metadata.json'}
                      </button>
                    </div>
                    {selectedModelTemplate.files?.documentation && (
                      <div className="flex items-center gap-2 text-sm">
                        <FileText className="w-4 h-4 text-indigo-500" />
                        <span className="font-medium">Documentation:</span>
                        <button 
                          onClick={() => openFileViewer('documentation', selectedModelTemplate.files.documentation!)}
                          className="text-blue-600 hover:underline text-sm"
                        >
                          {selectedModelTemplate.files.documentation}
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Metadata */}
                <div>
                  <h5 className="text-sm font-semibold text-gray-700 mb-2">Metadata</h5>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Type:</span>
                      <span className="text-gray-900">{selectedModelTemplate.type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Category:</span>
                      <span className="text-gray-900">{selectedModelTemplate.category}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Base Model:</span>
                      <span className="text-gray-900">{selectedModelTemplate.base_model}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Author:</span>
                      <span className="text-gray-900">{selectedModelTemplate.author?.name}</span>
                    </div>
                  </div>
                </div>

                {/* Tags */}
                {selectedModelTemplate.tags && selectedModelTemplate.tags.length > 0 && (
                  <div>
                    <h5 className="text-sm font-semibold text-gray-700 mb-2">Tags</h5>
                    <div className="flex flex-wrap gap-1">
                      {selectedModelTemplate.tags.map((tag, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Side - Parameters */}
          <div className="bg-white rounded-lg border-2 border-gray-200 p-4 flex flex-col">
            <div className="flex items-center justify-between mb-2 pb-2 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-900">Model Parameters</h3>
              <div className="flex gap-2">
                <button className="px-2 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700">
                  Import CSV
                </button>
                <button className="px-2 py-1 border border-gray-300 rounded text-xs hover:bg-gray-50">
                  Export
                </button>
              </div>
            </div>
            
            {/* Filter Bar */}
            <div className="mb-2">
              <div className="relative">
                <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-400 w-3 h-3" />
                <input
                  type="text"
                  placeholder="Filter parameters..."
                  value={parameterFilter}
                  onChange={(e) => onParameterFilterChange(e.target.value)}
                  className="w-full pl-7 pr-3 py-1 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-purple-500"
                />
              </div>
            </div>
            
            <div className="flex-1 overflow-auto" style={{ maxHeight: 'calc(100vh - 280px)' }}>
              <SortableTable
                data={sortedParameters.map((param, idx) => ({ ...param, idx }))}
                columns={parameterColumns}
                compact={true}
                stickyHeader={true}
                hoverable={true}
                className="text-xs"
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="h-full flex items-center justify-center">
          <div className="text-center">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Model Selected</h3>
            <p className="text-sm text-gray-500 mb-4">Select a model template to begin calibration</p>
            <button
              onClick={() => setShowModelSelector(true)}
              className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
            >
              Select Model Template
            </button>
          </div>
        </div>
      )}

      {/* Model Selector Modal */}
      {showModelSelector && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg w-[90%] max-w-6xl h-[80vh] flex flex-col">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Select Model Template</h2>
              <button
                onClick={() => setShowModelSelector(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Search and Filters */}
            <div className="px-6 py-3 border-b border-gray-200">
              <div className="flex gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search models..."
                    value={modelSearchTerm}
                    onChange={(e) => setModelSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <select 
                  value={modelFilterCategory}
                  onChange={(e) => setModelFilterCategory(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="all">All Categories</option>
                  <option value="transistor">Transistor</option>
                  <option value="diode">Diode</option>
                  <option value="passive">Passive</option>
                </select>
                <select 
                  value={modelFilterStatus}
                  onChange={(e) => setModelFilterStatus(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="all">All Status</option>
                  <option value="production">Production</option>
                  <option value="validated">Validated</option>
                  <option value="draft">Draft</option>
                </select>
              </div>
            </div>

            {/* Model Table */}
            <div className="flex-1 overflow-auto px-6">
              <table className="w-full">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Model Name</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Version</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Parameters</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredModels.map((model) => (
                    <tr key={model.model_id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{model.name}</div>
                          <div className="text-xs text-gray-500">{model.base_model}</div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">{model.type}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{model.category}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">v{model.version}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          model.status === 'production' ? 'bg-green-100 text-green-800' :
                          model.status === 'validated' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {model.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">{(model as any).parameters?.count || 0}</td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => {
                            onModelSelect(model);
                            setShowModelSelector(false);
                          }}
                          className="px-3 py-1 bg-purple-600 text-white rounded text-xs hover:bg-purple-700"
                        >
                          Select
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {filteredModels.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <p className="text-sm">No models found matching your criteria</p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
              <div className="text-sm text-gray-500">
                {filteredModels.length} of {availableModels.length} models shown
              </div>
              <button
                onClick={() => setShowModelSelector(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* File Viewer */}
      {fileViewerOpen && (
        <FileViewer
          isOpen={fileViewerOpen}
          fileName={fileViewerName}
          fileType={fileViewerType}
          modelName={selectedModelTemplate?.name || ''}
          onClose={() => setFileViewerOpen(false)}
        />
      )}
    </div>
  );
};

export default ModelTab;