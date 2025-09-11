import React, { useState, useEffect } from 'react';
import { 
  FileText, Download, Filter,
  Code2, Folder, Database,
  Tag, Code, Table, Info, HelpCircle, AlertTriangle, Plus, ChevronDown, Package, X
} from 'lucide-react';
import { Model, ModelParameter } from '../../types';
import FileViewer from '../FileViewer';
import DataStructureGuide from '../DataStructureGuide';
import ReportIssue from '../ReportIssue';
import ModelTemplateUploadModal from '../modals/ModelTemplateUploadModal';
import { downloadModelAsZip } from '../../utils/downloadUtils';
import { getModelParameters } from '../../data/parametersData';
import { Card, Badge, Button, ViewToggle } from '../ui';
import { FilterBar } from '../layout';
import { theme } from '../../theme';

interface ModelLibraryProps {
  models: Model[];
}

const ModelLibrary: React.FC<ModelLibraryProps> = ({ models }) => {
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [fileViewerOpen, setFileViewerOpen] = useState(false);
  const [fileViewerType, setFileViewerType] = useState<'cir' | 'parameters' | 'info' | 'documentation'>('cir');
  const [fileViewerName, setFileViewerName] = useState('');
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table');
  const [showGuide, setShowGuide] = useState(false);
  const [modelParameters, setModelParameters] = useState<ModelParameter[]>([]);
  const [showReportIssue, setShowReportIssue] = useState(false);
  const [modelToReport, setModelToReport] = useState<Model | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  
  // Collapsible sections state
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    specifications: true,
    files: true,
    parameters: true,
    metadata: true
  });
  
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  
  // Load parameters when selected model changes
  useEffect(() => {
    if (selectedModel?.model_id) {
      const params = getModelParameters(selectedModel.model_id);
      setModelParameters(params);
    }
  }, [selectedModel]);

  const filteredModels = models.filter(model => {
    const matchesSearch = model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         model.base_model.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         model.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = filterCategory === 'all' || model.category === filterCategory;
    const matchesStatus = filterStatus === 'all' || model.status === filterStatus;
    return matchesSearch && matchesCategory && matchesStatus;
  });


  const categories = Array.from(new Set(models.map(m => m.category)));

  const openFileViewer = (type: 'cir' | 'parameters' | 'info' | 'documentation', fileName: string) => {
    setFileViewerType(type);
    setFileViewerName(fileName);
    setFileViewerOpen(true);
  };

  const handleTemplateUpload = (newTemplate: any) => {
    // In a real application, this would update the models list
    console.log('New template uploaded:', newTemplate);
    // You could update the models array here or call a parent handler
  };

  return (
    <div className="h-full">
      {/* Main Content Area */}
      <div className={`${selectedModel ? 'mr-[500px]' : ''} h-full flex flex-col overflow-hidden transition-all duration-300`}>
        {/* Filters Bar */}
        <FilterBar
          searchValue={searchTerm}
          onSearchChange={setSearchTerm}
          filters={
            <>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Status</option>
                <option value="production">Production</option>
                <option value="validated">Validated</option>
                <option value="in-review">In Review</option>
                <option value="draft">Draft</option>
                <option value="deprecated">Deprecated</option>
              </select>
              <Button variant="secondary" size="md" icon={<Filter className="w-4 h-4" />}>
                More Filters
              </Button>
              <Button 
                onClick={() => setShowGuide(true)}
                variant="secondary"
                size="md"
                icon={<HelpCircle className="w-4 h-4" />}
                title="Model Structure Guide"
              >
                Guide
              </Button>
            </>
          }
          actions={
            <div className="flex items-center gap-3">
              <Button
                onClick={() => setShowUploadModal(true)}
                variant="primary"
                size="md"
                icon={<Plus className="w-4 h-4" />}
              >
                Upload Template
              </Button>
              <ViewToggle viewMode={viewMode} onViewChange={setViewMode} />
            </div>
          }
        />

        {/* Content View */}
        <Card padding="none" className="flex-1 overflow-auto">
          {viewMode === 'table' ? (
            <table className="w-full border-collapse" style={{ tableLayout: 'fixed' }}>
              <colgroup>
                <col style={{ width: '30%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '10%' }} />
              </colgroup>
              <thead className="bg-gray-50 border-b border-gray-200 sticky top-0">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Model Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Version
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Parameters
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Modified
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredModels.map((model) => (
                  <tr 
                    key={model.model_id}
                    className={`hover:bg-gray-50 cursor-pointer ${selectedModel?.model_id === model.model_id ? 'bg-purple-50' : ''}`}
                    onClick={() => {
                      setSelectedModel(model);
                      // Reset all sections to expanded when opening details
                      setExpandedSections({
                        specifications: true,
                        files: true,
                        parameters: true,
                        metadata: true
                      });
                    }}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <FileText className="w-5 h-5 text-gray-400 mr-3 flex-shrink-0" />
                        <div className="min-w-0 flex-1">
                          <div className="text-sm font-medium text-gray-900 truncate" title={model.name}>{model.name}</div>
                          <div className="text-sm text-gray-500 truncate" title={model.base_model}>{model.base_model}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 truncate" title={model.type}>
                      {model.type}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="truncate" title={`${model.category}${model.subcategory ? ' / ' + model.subcategory : ''}`}>
                        {model.category}
                        {model.subcategory && <span className="text-gray-500"> / {model.subcategory}</span>}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      v{model.version}
                    </td>
                    <td className="px-6 py-4">
                      <Badge status={model.status as any} size="sm">
                        {model.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {model.parameters.count}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 truncate">
                      {new Date(model.timestamps.modified).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <button 
                          className="text-orange-600 hover:text-orange-700"
                          onClick={(e) => {
                            e.stopPropagation();
                            setModelToReport(model);
                            setShowReportIssue(true);
                          }}
                          title="Report Issue"
                        >
                          <AlertTriangle className="w-4 h-4" />
                        </button>
                        <button 
                          className={theme.iconColors.download}
                          onClick={(e) => {
                            e.stopPropagation();
                            downloadModelAsZip(model);
                          }}
                          title="Download Model"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredModels.map((model) => (
                <div
                  key={model.model_id}
                  className={`bg-white border rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer ${
                    selectedModel?.model_id === model.model_id ? 'border-purple-500 bg-purple-50' : 'border-gray-200'
                  }`}
                  onClick={() => setSelectedModel(model)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <FileText className="w-8 h-8 text-purple-500" />
                    <Badge status={model.status as any} size="sm">
                      {model.status}
                    </Badge>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-1 truncate" title={model.name}>
                    {model.name}
                  </h3>
                  <p className="text-sm text-gray-500 mb-2 truncate" title={model.base_model}>
                    {model.base_model}
                  </p>
                  <div className="space-y-1 text-xs text-gray-600">
                    <div className="flex justify-between">
                      <span>Type:</span>
                      <span className="font-medium">{model.type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Category:</span>
                      <span className="font-medium truncate ml-2" title={model.category}>
                        {model.category}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Version:</span>
                      <span className="font-medium">v{model.version}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Parameters:</span>
                      <span className="font-medium">{model.parameters.count}</span>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex flex-wrap gap-1">
                      {model.tags.slice(0, 3).map((tag, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          {tag}
                        </span>
                      ))}
                      {model.tags.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          +{model.tags.length - 3}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="mt-3 flex justify-between items-center">
                    <span className="text-xs text-gray-500">
                      {new Date(model.timestamps.modified).toLocaleDateString()}
                    </span>
                    <div className="flex items-center gap-2">
                      <button
                        className="text-orange-600 hover:text-orange-700"
                        onClick={(e) => {
                          e.stopPropagation();
                          setModelToReport(model);
                          setShowReportIssue(true);
                        }}
                        title="Report Issue"
                      >
                        <AlertTriangle className="w-4 h-4" />
                      </button>
                      <button
                        className={theme.iconColors.download}
                        onClick={(e) => {
                          e.stopPropagation();
                          downloadModelAsZip(model);
                        }}
                        title="Download Model"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Side Panel */}
      {selectedModel && (
        <div className="fixed right-0 top-0 bottom-0 w-[500px] bg-white border-l border-gray-200 flex flex-col z-40 shadow-xl">
          {/* Fixed Header */}
          <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between flex-shrink-0">
            <h2 className="text-lg font-semibold text-gray-900">Model Template Details</h2>
            <button
              onClick={() => {
                setSelectedModel(null);
                // Reset sections to expanded for next time
                setExpandedSections({
                  specifications: true,
                  files: true,
                  parameters: true,
                  metadata: true,
                  tags: true
                });
              }}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            <div className="space-y-4">
            {/* Header Card - Gradient style like MyModels */}
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-3 border border-purple-100">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h2 className="text-lg font-bold text-gray-900">{selectedModel.name}</h2>
                  <p className="text-xs text-gray-500 font-mono mt-0.5">{selectedModel.model_id}</p>
                </div>
                <div className="flex flex-col items-end gap-1.5">
                  <Badge status={selectedModel.status as any} size="sm">
                    {selectedModel.status}
                  </Badge>
                  <Badge size="sm">
                    v{selectedModel.version}
                  </Badge>
                </div>
              </div>
              {selectedModel.description && (
                <p className="text-sm text-gray-700 bg-white/50 rounded p-2 italic">
                  "{selectedModel.description}"
                </p>
              )}
            </div>

            {/* Technical Specifications */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('specifications')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Package className="w-4 h-4 text-gray-500" />
                    Technical Specifications
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.specifications ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.specifications && (
              <div className="p-3">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-xs text-gray-500">Type:</span> <span className="text-sm font-medium text-gray-700">{selectedModel.type}</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Category:</span> <span className="text-sm font-medium text-gray-700">{selectedModel.category}</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Subcategory:</span> <span className="text-sm font-medium text-gray-700">{selectedModel.subcategory || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Base Model:</span> <span className="text-sm font-medium text-gray-700">{selectedModel.base_model}</span>
                  </div>
                </div>
              </div>
              )}
            </div>

            {/* File Structure */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('files')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Folder className="w-4 h-4 text-gray-500" />
                    Files
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.files ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.files && (
              <div className="p-3">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Code2 className="w-4 h-4 text-blue-500" />
                  <span className="font-medium">Entry Point:</span>
                  <button
                    onClick={() => openFileViewer('cir', selectedModel.files.entry_point)}
                    className="text-blue-600 hover:text-blue-700 hover:underline"
                  >
                    {selectedModel.files.entry_point}
                  </button>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Database className="w-4 h-4 text-green-500" />
                  <span className="font-medium">Parameters:</span>
                  <button
                    onClick={() => openFileViewer('parameters', selectedModel.files.parameters_file)}
                    className="text-blue-600 hover:text-blue-700 hover:underline"
                  >
                    {selectedModel.files.parameters_file}
                  </button>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <FileText className="w-4 h-4 text-yellow-500" />
                  <span className="font-medium">Metadata:</span>
                  <button
                    onClick={() => openFileViewer('info', selectedModel.files.metadata_file)}
                    className="text-blue-600 hover:text-blue-700 hover:underline"
                  >
                    {selectedModel.files.metadata_file}
                  </button>
                </div>
                {selectedModel.files.documentation && (
                  <div className="flex items-center gap-2 text-sm">
                    <FileText className="w-4 h-4 text-indigo-500" />
                    <span className="font-medium">Documentation:</span>
                    <button
                      onClick={() => openFileViewer('documentation', selectedModel.files.documentation!)}
                      className="text-blue-600 hover:text-blue-700 hover:underline"
                    >
                      {selectedModel.files.documentation}
                    </button>
                  </div>
                )}
                {selectedModel.files.lib_directory && (
                  <div className="flex items-center gap-2 text-sm">
                    <Folder className="w-4 h-4 text-purple-500" />
                    <span className="font-medium">Lib Directory:</span>
                    <span className="text-gray-600">{selectedModel.files.lib_directory}</span>
                  </div>
                )}
              </div>
              </div>
              )}
            </div>

            {/* Parameters Preview */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('parameters')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Database className="w-4 h-4 text-gray-500" />
                    Parameters ({selectedModel.parameters.count} total)
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.parameters ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.parameters && (
              <div className="p-3">
              <div className="bg-gray-50 rounded-lg overflow-hidden">
                <table className="min-w-full text-xs">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-3 py-2 text-left">Name</th>
                      <th className="px-3 py-2 text-left">Subckt</th>
                      <th className="px-3 py-2 text-left">Default</th>
                      <th className="px-3 py-2 text-left">Unit</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {modelParameters.slice(0, 5).map((param, idx) => (
                      <tr key={idx}>
                        <td className="px-3 py-2 font-mono">{param.name}</td>
                        <td className="px-3 py-2">{param.subckt}</td>
                        <td className="px-3 py-2">{param.default}</td>
                        <td className="px-3 py-2">{param.unit}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div className="px-3 py-2 bg-gray-100 text-center">
                  <button 
                    onClick={() => openFileViewer('parameters', selectedModel.files.parameters_file)}
                    className="text-xs text-purple-600 hover:text-purple-700"
                  >
                    View all {selectedModel.parameters.count} parameters →
                  </button>
                </div>
              </div>
              </div>
              )}
            </div>

            {/* Metadata */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('metadata')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Info className="w-4 h-4 text-gray-500" />
                    Metadata
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.metadata ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.metadata && (
              <div className="p-3">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Author:</span>
                  <span className="text-gray-900">{selectedModel.author.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Department:</span>
                  <span className="text-gray-900">{selectedModel.author.department}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Created:</span>
                  <span className="text-gray-900">
                    {new Date(selectedModel.timestamps.created).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Last Modified:</span>
                  <span className="text-gray-900">
                    {new Date(selectedModel.timestamps.modified).toLocaleDateString()}
                  </span>
                </div>
              </div>
              </div>
              )}
            </div>

            {/* Tags */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('tags')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Tag className="w-4 h-4 text-gray-500" />
                    Tags
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.tags ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.tags && (
              <div className="p-3">
              <div className="flex flex-wrap gap-2">
                {selectedModel.tags.map((tag, idx) => (
                  <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                    <Tag className="w-3 h-3 inline mr-1" />
                    {tag}
                  </span>
                ))}
              </div>
              </div>
              )}
            </div>

            {/* Actions */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex gap-2">
                <button 
                  onClick={() => openFileViewer('cir', selectedModel.files.entry_point)}
                  className="flex-1 px-3 py-2 bg-blue-50 text-blue-700 border border-blue-300 rounded-lg text-sm hover:bg-blue-100 hover:border-blue-400 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Code className="w-4 h-4" />
                  Circuit
                </button>
                <button 
                  onClick={() => openFileViewer('parameters', selectedModel.files.parameters_file)}
                  className="flex-1 px-3 py-2 bg-green-50 text-green-700 border border-green-300 rounded-lg text-sm hover:bg-green-100 hover:border-green-400 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Table className="w-4 h-4" />
                  Params
                </button>
                <button 
                  onClick={() => {
                    setModelToReport(selectedModel);
                    setShowReportIssue(true);
                  }}
                  className="flex-1 px-3 py-2 bg-orange-50 text-orange-700 border border-orange-300 rounded-lg text-sm hover:bg-orange-100 hover:border-orange-400 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <AlertTriangle className="w-4 h-4" />
                  Report
                </button>
                <button 
                  onClick={() => downloadModelAsZip(selectedModel)}
                  className="flex-1 px-3 py-2 bg-purple-50 text-purple-700 border border-purple-300 rounded-lg text-sm hover:bg-purple-100 hover:border-purple-400 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Download
                </button>
              </div>
            </div>
            </div>
          </div>
        </div>
      )}

      {/* File Viewer Modal */}
      {selectedModel && (
        <FileViewer
          isOpen={fileViewerOpen}
          onClose={() => setFileViewerOpen(false)}
          fileType={fileViewerType}
          fileName={fileViewerName}
          modelName={selectedModel.name}
          modelData={selectedModel}
        />
      )}

      {/* Data Structure Guide Modal */}
      <DataStructureGuide
        isOpen={showGuide}
        onClose={() => setShowGuide(false)}
        type="model"
      />

      {/* Report Issue Modal */}
      {modelToReport && (
        <ReportIssue
          isOpen={showReportIssue}
          onClose={() => {
            setShowReportIssue(false);
            setModelToReport(null);
          }}
          itemType="model"
          itemName={modelToReport.name}
          itemId={modelToReport.model_id}
        />
      )}

      {/* Upload Modal */}
      <ModelTemplateUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUpload={handleTemplateUpload}
      />
    </div>
  );
};

export default ModelLibrary;