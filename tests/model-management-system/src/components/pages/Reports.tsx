import React, { useState, useMemo } from 'react';
import { 
  FileText, Download, X,
  User, CheckCircle, Clock, TrendingUp,
  BarChart3, FileBarChart
} from 'lucide-react';
import dataService from '../../services/dataService';
import { CalibratedModel } from '../../types';
import ModelReport from '../ModelReport';
import { theme } from '../../theme';
import { DataView, Column, ViewMode, ViewToggle } from '../ui';
import { FilterBar } from '../layout';

const Reports: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterUser, setFilterUser] = useState('all');
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const [selectedModel, setSelectedModel] = useState<CalibratedModel | null>(null);
  const [showReport, setShowReport] = useState(false);

  // Get all calibrated models and filter out pending ones (no report for pending tasks)
  const allCalibratedModels = dataService.getCalibratedModels()
    .filter(model => model.status !== 'pending' && model.status !== 'draft');
  
  // Get unique users for filter
  const uniqueUsers = Array.from(new Set(allCalibratedModels.map(m => m.author?.name || 'Unknown')));

  // Filter models
  const filteredModels = allCalibratedModels.filter((model) => {
    const matchesSearch = 
      model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      model.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      model.base_model.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (model.author?.name || '').toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || model.status === filterStatus;
    const matchesUser = filterUser === 'all' || model.author?.name === filterUser;
    
    return matchesSearch && matchesStatus && matchesUser;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'production':
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'validated':
        return 'bg-blue-100 text-blue-800';
      case 'in-review':
      case 'in-progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'production':
      case 'validated':
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'in-review':
      case 'in-progress':
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case 'failed':
        return <X className="w-5 h-5 text-red-600" />;
      default:
        return <FileText className="w-5 h-5 text-gray-600" />;
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const openReport = (model: CalibratedModel) => {
    setSelectedModel(model);
    setShowReport(true);
  };

  // Define table columns
  const tableColumns: Column<CalibratedModel>[] = useMemo(() => [
    {
      key: 'name',
      header: 'Model Name',
      sortable: true,
      render: (value, item) => (
        <div className="flex items-center">
          <FileText className="w-5 h-5 text-purple-500 mr-3" />
          <div>
            <div className="text-sm font-medium text-gray-900">{item.name}</div>
            <div className="text-xs text-gray-500">v{item.version}</div>
          </div>
        </div>
      ),
    },
    {
      key: 'base_model',
      header: 'Base Model',
      sortable: true,
      render: (value) => <span className="text-sm text-gray-900">{value}</span>,
    },
    {
      key: 'category',
      header: 'Category',
      sortable: true,
      render: (value, item) => (
        <span className="text-sm text-gray-900">
          {item.category}
          {item.subcategory && <span className="text-gray-500"> / {item.subcategory}</span>}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (value) => (
        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadge(value)}`}>
          {value}
        </span>
      ),
    },
    {
      key: 'accuracy',
      header: 'Accuracy',
      sortable: false,
      render: (_, item) => (
        <span className="text-sm text-gray-900">
          {item.calibration_info?.metrics?.accuracy ? 
            `${item.calibration_info.metrics.accuracy.toFixed(1)}%` : 
            'N/A'
          }
        </span>
      ),
    },
    {
      key: 'author',
      header: 'Author',
      sortable: true,
      render: (_, item) => (
        <div className="flex items-center">
          <User className="w-4 h-4 text-gray-400 mr-2" />
          <span className="text-sm text-gray-900">{item.author?.name || 'Unknown'}</span>
        </div>
      ),
    },
    {
      key: 'date',
      header: 'Date',
      sortable: false,
      render: (_, item) => (
        <span className="text-sm text-gray-500">{formatDate(item.calibration_info?.timestamp)}</span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      sortable: false,
      render: (_, item) => (
        <div className="flex items-center gap-2 justify-end">
          <button
            onClick={(e) => {
              e.stopPropagation();
              openReport(item);
            }}
            className={theme.iconColors.report}
            title="View Report"
          >
            <FileBarChart className="w-4 h-4" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              // TODO: Implement download
              console.log('Download model:', item.model_id);
            }}
            className="text-green-600 hover:text-green-900"
            title="Download"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ], []);

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
        <p className="text-gray-600 mt-2">View and analyze calibrated models from all users</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Models</p>
              <p className="text-2xl font-bold text-gray-900">{allCalibratedModels.length}</p>
            </div>
            <FileText className="w-8 h-8 text-purple-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-green-600">
                {allCalibratedModels.filter(m => m.status === 'completed' || m.status === 'production' || m.status === 'validated').length}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Contributors</p>
              <p className="text-2xl font-bold text-blue-600">{uniqueUsers.length}</p>
            </div>
            <User className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Accuracy</p>
              <p className="text-2xl font-bold text-purple-600">
                {(allCalibratedModels.reduce((acc, m) => acc + (m.calibration_info?.metrics?.accuracy || 0), 0) / allCalibratedModels.length || 0).toFixed(1)}%
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <FilterBar
        searchValue={searchTerm}
        onSearchChange={setSearchTerm}
        filters={
          <>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="in-progress">In Progress</option>
              <option value="failed">Failed</option>
              <option value="production">Production</option>
              <option value="validated">Validated</option>
            </select>
            <select
              value={filterUser}
              onChange={(e) => setFilterUser(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="all">All Users</option>
              {uniqueUsers.map(user => (
                <option key={user} value={user}>{user}</option>
              ))}
            </select>
          </>
        }
        actions={
          <ViewToggle viewMode={viewMode} onViewChange={setViewMode} />
        }
      />

      {/* Content */}
      <DataView
        data={filteredModels}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        columns={tableColumns}
        onRowClick={(model) => openReport(model)}
        renderCard={(model) => (
          <div className="flex flex-col h-full">
            <div className="flex items-center justify-between mb-3">
              {getStatusIcon(model.status)}
              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(model.status)}`}>
                {model.status}
              </span>
            </div>
            <h3 className="font-semibold text-gray-900 mb-1 truncate" title={model.name}>
              {model.name}
            </h3>
            <p className="text-sm text-gray-500 mb-2">v{model.version}</p>
            <div className="space-y-1 text-xs text-gray-600">
              <div className="flex justify-between">
                <span>Base Model:</span>
                <span className="font-medium truncate ml-2" title={model.base_model}>
                  {model.base_model}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Category:</span>
                <span className="font-medium">{model.category}</span>
              </div>
              <div className="flex justify-between">
                <span>Accuracy:</span>
                <span className="font-medium text-green-600">
                  {model.calibration_info?.metrics?.accuracy ? 
                    `${model.calibration_info.metrics.accuracy.toFixed(1)}%` : 
                    'N/A'
                  }
                </span>
              </div>
              <div className="flex justify-between">
                <span>Author:</span>
                <span className="font-medium truncate ml-2" title={model.author?.name}>
                  {model.author?.name || 'Unknown'}
                </span>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-gray-200 flex justify-between items-center">
              <span className="text-xs text-gray-500">
                {formatDate(model.calibration_info?.timestamp)}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    openReport(model);
                  }}
                  className={theme.iconColors.report}
                  title="View Report"
                >
                  <FileBarChart className="w-4 h-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    // TODO: Implement download
                    console.log('Download model:', model.model_id);
                  }}
                  className="text-green-600 hover:text-green-900"
                  title="Download"
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}
        cardClassName="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer"
        className="flex-1"
        showViewToggle={false}
        emptyMessage={
          <div className="text-center py-12">
            <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No models found matching your criteria</p>
          </div>
        }
      />

      {/* Report Modal */}
      {showReport && selectedModel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] flex flex-col">
            <div className="flex justify-between items-center px-6 py-4 border-b border-gray-200">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Model Report</h2>
                <p className="text-sm text-gray-700 mt-1">
                  {selectedModel.name} - v{selectedModel.version}
                </p>
              </div>
              <button
                onClick={() => {
                  setShowReport(false);
                  setSelectedModel(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-6">
              <ModelReport
                modelData={{
                  model_id: selectedModel.model_id,
                  name: selectedModel.name,
                  version: selectedModel.version,
                  type: 'compact' as const,
                  category: selectedModel.category,
                  subcategory: selectedModel.subcategory,
                  base_model: selectedModel.base_model,
                  status: selectedModel.status as any,
                  author: selectedModel.author as any,
                  timestamps: {
                    created: selectedModel.calibration_info?.timestamp || '',
                    modified: selectedModel.calibration_info?.timestamp || ''
                  },
                  tags: [],
                  files: {} as any,
                  parameters: {} as any,
                  description: selectedModel.description
                }}
                calibrationResults={selectedModel}
                timestamp={selectedModel.calibration_info?.timestamp}
                isGenerated={true}
                showGenerateButton={false}
              />
            </div>
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowReport(false);
                  setSelectedModel(null);
                }}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
              >
                Close
              </button>
              <button
                onClick={() => {
                  // TODO: Export report
                  console.log('Exporting report for:', selectedModel.model_id);
                }}
                className="px-4 py-2 bg-purple-600 text-white hover:bg-purple-700 rounded-lg flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export PDF
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;