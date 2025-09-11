import React, { useState } from 'react';
import { 
  Download, Filter, Plus,
  X, BarChart3, TrendingUp, Database, Zap, HelpCircle, AlertTriangle, FileText,
  ChevronDown, Info, Tag, Package
} from 'lucide-react';
import { ReferenceData } from '../../types';
import DataStructureGuide from '../DataStructureGuide';
import ReportIssue from '../ReportIssue';
import FileViewer from '../FileViewer';
import ReferenceDataViewer from '../shared/ReferenceDataViewer';
import ReferenceDataUploadModal from '../modals/ReferenceDataUploadModal';
import { Button, ViewToggle } from '../ui';
import { FilterBar } from '../layout';
import { Modal } from '../ui';

interface ReferenceDataLibraryProps {
  referenceData: ReferenceData[];
}

interface DataPage {
  type: string;
  name: string;
  page: string;  // Unique ID for each page
  testbench_type: string;
  x_name: string;
  y_name: string;
  extra_var_name?: string;
  x_unit: string;
  y_unit: string;
  extra_var_unit?: string;
  operating_conditions: Record<string, any>;
  instance_parameters: Record<string, any>;
  curves: Array<{
    x_values: number[];
    y_values: number[];
    extra_var_value?: number;
  }>;
}

const ReferenceDataLibrary: React.FC<ReferenceDataLibraryProps> = ({ referenceData: initialData }) => {
  const [referenceData, setReferenceData] = useState<ReferenceData[]>(initialData);
  const [selectedData, setSelectedData] = useState<ReferenceData | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showVisualization, setShowVisualization] = useState(false);
  const [visualizationData, setVisualizationData] = useState<ReferenceData | null>(null);
  const [libraryViewMode, setLibraryViewMode] = useState<'table' | 'cards'>('table');
  const [showGuide, setShowGuide] = useState(false);
  const [showReportIssue, setShowReportIssue] = useState(false);
  const [dataToReport, setDataToReport] = useState<ReferenceData | null>(null);
  const [fileViewerOpen, setFileViewerOpen] = useState(false);
  const [fileViewerData, setFileViewerData] = useState<ReferenceData | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  
  // Collapsible sections state
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    specifications: true,
    dataPages: true,
    deviceInfo: true,
    metadata: true,
    qualityMetrics: true,
    tags: true
  });
  
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };


  const filteredData = referenceData.filter(data => {
    const matchesSearch = (data as any).name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (data as any).device_info?.device_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (data as any).tags?.some((tag: string) => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = filterType === 'all' || (data as any).data_type === filterType;
    const matchesStatus = filterStatus === 'all' || (data as any).data_quality?.validated === (filterStatus === 'validated');
    return matchesSearch && matchesType && matchesStatus;
  });

  const getStatusBadge = (data: ReferenceData) => {
    const isValidated = (data as any).data_quality?.validated;
    return isValidated ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800';
  };

  const getDeviceIcon = (deviceType: string) => {
    switch (deviceType) {
      case 'mosfet':
        return <Zap className="w-5 h-5 text-blue-500" />;
      case 'bjt':
        return <TrendingUp className="w-5 h-5 text-orange-500" />;
      default:
        return <Database className="w-5 h-5 text-gray-500" />;
    }
  };

  const openVisualization = (data: ReferenceData) => {
    setVisualizationData(data);
    setShowVisualization(true);
  };

  const handleDataUpload = (newData: any) => {
    setReferenceData([...referenceData, newData]);
    // Optionally show a success message
    console.log('New data uploaded:', newData);
  };

  const renderVisualization = () => {
    if (!visualizationData) return null;

    return (
      <Modal
        isOpen={showVisualization}
        onClose={() => {
          setShowVisualization(false);
          setVisualizationData(null);
        }}
        title={`Data Visualization: ${(visualizationData as any).name}`}
        size="full"
        noScroll={true}
      >
        <div className="h-full w-full">
          <ReferenceDataViewer
            referenceData={[visualizationData]}
            showAddButton={false}
            allowRemove={false}
            showValidation={true}
            className="h-full"
          />
        </div>
      </Modal>
    );
  };


  return (
    <div className="h-full">
      {/* Main Content Area */}
      <div className={`${selectedData ? 'mr-[500px]' : ''} h-full flex flex-col overflow-hidden transition-all duration-300`}>
        {/* Filters Bar */}
        <FilterBar
          searchValue={searchTerm}
          onSearchChange={setSearchTerm}
          filters={
            <>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Types</option>
                <option value="measurement">Measurement</option>
                <option value="simulation">Simulation</option>
              </select>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Status</option>
                <option value="validated">Validated</option>
                <option value="pending">Pending</option>
              </select>
              <Button variant="secondary" size="md" icon={<Filter className="w-4 h-4" />}>
                More Filters
              </Button>
              <Button 
                onClick={() => setShowGuide(true)}
                variant="secondary"
                size="md"
                icon={<HelpCircle className="w-4 h-4" />}
                title="Reference Data Structure Guide"
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
                Upload Data
              </Button>
              <ViewToggle viewMode={libraryViewMode} onViewChange={setLibraryViewMode} />
            </div>
          }
        />

        {/* Content View */}
        <div className="bg-white rounded-lg shadow flex-1 overflow-auto">
          {libraryViewMode === 'table' ? (
            <table className="w-full border-collapse" style={{ tableLayout: 'fixed' }}>
            <colgroup>
              <col style={{ width: '30%' }} />
              <col style={{ width: '12%' }} />
              <col style={{ width: '15%' }} />
              <col style={{ width: '10%' }} />
              <col style={{ width: '10%' }} />
              <col style={{ width: '13%' }} />
              <col style={{ width: '10%' }} />
            </colgroup>
            <thead className="bg-gray-50 border-b border-gray-200 sticky top-0">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Data Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Device
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Points
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
              {filteredData.map((data) => (
                <tr 
                  key={(data as any).data_id}
                  className={`hover:bg-gray-50 cursor-pointer ${selectedData?.data_id === (data as any).data_id ? 'bg-purple-50' : ''}`}
                  onClick={() => {
                    setSelectedData(data);
                    // Reset all sections to expanded when opening details
                    setExpandedSections({
                      specifications: true,
                      dataPages: true,
                      deviceInfo: true,
                      metadata: true,
                      qualityMetrics: true,
                      tags: true
                    });
                  }}
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        {getDeviceIcon((data as any).device_info?.device_type || 'unknown')}
                      </div>
                      <div className="ml-3 min-w-0 flex-1">
                        <div className="text-sm font-medium text-gray-900 truncate" title={(data as any).name}>{(data as any).name}</div>
                        <div className="text-sm text-gray-500 truncate" title={(data as any).data_id}>{(data as any).data_id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 capitalize truncate" title={data.type}>
                    {data.type}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div className="truncate" title={data.device?.type?.toUpperCase()}>
                      {data.device?.type?.toUpperCase()}
                    </div>
                    <div className="text-xs text-gray-500 truncate" title={data.device?.technology}>{data.device?.technology}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadge(data)}`}>
                      {data.data_quality?.validated ? 'Validated' : 'Pending'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 truncate">
                    {Math.round((data.data_quality?.completeness || 0) * 1000) || 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 truncate">
                    {new Date(data.timestamps.modified).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      <button 
                        className="text-blue-600 hover:text-blue-900"
                        onClick={(e) => {
                          e.stopPropagation();
                          setFileViewerData(data);
                          setFileViewerOpen(true);
                        }}
                        title="View File"
                      >
                        <FileText className="w-4 h-4" />
                      </button>
                      <button 
                        className="text-purple-600 hover:text-purple-900"
                        onClick={(e) => {
                          e.stopPropagation();
                          openVisualization(data);
                        }}
                        title="Visualize Data"
                      >
                        <BarChart3 className="w-4 h-4" />
                      </button>
                      <button 
                        className="text-orange-600 hover:text-orange-700"
                        onClick={(e) => {
                          e.stopPropagation();
                          setDataToReport(data);
                          setShowReportIssue(true);
                        }}
                        title="Report Issue"
                      >
                        <AlertTriangle className="w-4 h-4" />
                      </button>
                      <button 
                        className="text-green-600 hover:text-green-900"
                        onClick={(e) => {
                          e.stopPropagation();
                          const fileName = `${(data as any).data_id}.json`;
                          const fileContent = JSON.stringify(data, null, 2);
                          const blob = new Blob([fileContent], { type: 'application/json' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = fileName;
                          a.click();
                        }}
                        title="Download Data"
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
              {filteredData.map((data) => (
                <div
                  key={data.data_id}
                  className={`bg-white border rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer ${
                    selectedData?.data_id === data.data_id ? 'border-purple-500 bg-purple-50' : 'border-gray-200'
                  }`}
                  onClick={() => {
                    setSelectedData(data);
                    // Reset all sections to expanded when opening details
                    setExpandedSections({
                      specifications: true,
                      dataPages: true,
                      deviceInfo: true,
                      metadata: true,
                      qualityMetrics: true,
                      tags: true
                    });
                  }}
                >
                  <div className="flex items-center justify-between mb-3">
                    {getDeviceIcon(data.device?.type || 'unknown')}
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(data)}`}>
                      {data.data_quality?.validated ? 'Validated' : 'Pending'}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-1 truncate" title={data.name}>
                    {data.name}
                  </h3>
                  <p className="text-sm text-gray-500 mb-2 truncate" title={data.data_id}>
                    {data.data_id}
                  </p>
                  <div className="space-y-1 text-xs text-gray-600">
                    <div className="flex justify-between">
                      <span>Type:</span>
                      <span className="font-medium capitalize">{data.type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Device:</span>
                      <span className="font-medium">
                        {data.device?.type?.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Tech:</span>
                      <span className="font-medium">{data.device?.technology || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Points:</span>
                      <span className="font-medium">
                        {Math.round((data.data_quality?.completeness || 0) * 1000) || 'N/A'}
                      </span>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-200 flex justify-between items-center">
                    <span className="text-xs text-gray-500">
                      {new Date(data.timestamps.modified).toLocaleDateString()}
                    </span>
                    <div className="flex gap-2">
                      <button
                        className="text-blue-600 hover:text-blue-900"
                        onClick={(e) => {
                          e.stopPropagation();
                          setFileViewerData(data);
                          setFileViewerOpen(true);
                        }}
                        title="View File"
                      >
                        <FileText className="w-4 h-4" />
                      </button>
                      <button
                        className="text-purple-600 hover:text-purple-900"
                        onClick={(e) => {
                          e.stopPropagation();
                          openVisualization(data);
                        }}
                        title="Visualize Data"
                      >
                        <BarChart3 className="w-4 h-4" />
                      </button>
                      <button
                        className="text-orange-600 hover:text-orange-700"
                        onClick={(e) => {
                          e.stopPropagation();
                          setDataToReport(data);
                          setShowReportIssue(true);
                        }}
                        title="Report Issue"
                      >
                        <AlertTriangle className="w-4 h-4" />
                      </button>
                      <button
                        className="text-green-600 hover:text-green-900"
                        onClick={(e) => {
                          e.stopPropagation();
                          const fileName = `${data.data_id}.json`;
                          const fileContent = JSON.stringify(data, null, 2);
                          const blob = new Blob([fileContent], { type: 'application/json' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = fileName;
                          a.click();
                        }}
                        title="Download Data"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Side Panel */}
      {selectedData && (
        <div className="fixed right-0 top-0 bottom-0 w-[500px] bg-white border-l border-gray-200 flex flex-col z-40 shadow-xl">
          {/* Fixed Header */}
          <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between flex-shrink-0">
            <h2 className="text-lg font-semibold text-gray-900">Data Details</h2>
            <button
              onClick={() => {
                setSelectedData(null);
                // Reset sections to expanded for next time
                setExpandedSections({
                  specifications: true,
                  dataPages: true,
                  deviceInfo: true,
                  metadata: true,
                  qualityMetrics: true
                });
              }}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
            {/* Header Card - Gradient style like MyModels */}
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-3 border border-purple-100">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h2 className="text-lg font-bold text-gray-900">{(selectedData as any).name}</h2>
                  <p className="text-xs text-gray-500 font-mono mt-0.5">{(selectedData as any).data_id}</p>
                </div>
                <div className="flex flex-col items-end gap-1.5">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(selectedData)}`}>
                    {(selectedData as any).data_quality?.validated ? 'Validated' : 'Pending'}
                  </span>
                  <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-700">
                    v{(selectedData as any).version}
                  </span>
                </div>
              </div>
              {(selectedData as any).description && (
                <p className="text-sm text-gray-700 bg-white/50 rounded p-2 italic">
                  "{(selectedData as any).description}"
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
                    <span className="text-xs text-gray-500">Type:</span> <span className="text-sm font-medium text-gray-700">{(selectedData as any).type || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Source:</span> <span className="text-sm font-medium text-gray-700">{(selectedData as any).source?.equipment || (selectedData as any).source?.simulator || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Device Type:</span> <span className="text-sm font-medium text-gray-700">{(selectedData as any).device?.type || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Technology:</span> <span className="text-sm font-medium text-gray-700">{(selectedData as any).device?.technology || 'N/A'}</span>
                  </div>
                </div>
              </div>
              )}
            </div>

            {/* Data Pages */}
            {(selectedData as any).data && (selectedData as any).data.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('dataPages')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Database className="w-4 h-4 text-gray-500" />
                    Data Pages ({(selectedData as any).data?.length || 0})
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.dataPages ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.dataPages && (
              <div className="p-3">
                <div className="space-y-2">
                  {(selectedData as any).data?.map((page: DataPage) => (
                    <div key={page.page} className="border border-gray-200 rounded-lg p-2.5 bg-gray-50">
                      <div className="text-sm font-medium text-gray-900">{page.name}</div>
                      <div className="text-xs text-gray-500">ID: {page.page} • {page.curves.length} curves</div>
                      <div className="text-xs text-gray-500 mt-1">{page.x_name} vs {page.y_name}</div>
                    </div>
                  ))}
                </div>
              </div>
              )}
            </div>
            )}

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
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-xs text-gray-500">Author</p>
                    <p className="text-sm font-medium text-gray-900">{(selectedData as any).author?.name || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Department</p>
                    <p className="text-sm font-medium text-gray-900">{(selectedData as any).author?.department || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Quality Score</p>
                    <p className="text-sm font-medium text-gray-900">{((selectedData as any).data_quality?.quality_score * 100).toFixed(1)}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Created</p>
                    <p className="text-sm font-medium text-gray-900">
                      {(selectedData as any).timestamps?.created ? new Date((selectedData as any).timestamps.created).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
              )}
            </div>

            {/* Tags */}
            {(selectedData as any).tags && (selectedData as any).tags.length > 0 && (
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
                  <div className="flex flex-wrap gap-1">
                    {(selectedData as any).tags.map((tag: string, idx: number) => (
                      <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex gap-2">
                <button 
                  onClick={() => openVisualization(selectedData)}
                  className="flex-1 px-3 py-2 bg-purple-50 text-purple-700 border border-purple-300 rounded-lg text-sm hover:bg-purple-100 hover:border-purple-400 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <BarChart3 className="w-4 h-4" />
                  Visualize
                </button>
                <button 
                  onClick={() => {
                    setFileViewerData(selectedData);
                    setFileViewerOpen(true);
                  }}
                  className="flex-1 px-3 py-2 bg-blue-50 text-blue-700 border border-blue-300 rounded-lg text-sm hover:bg-blue-100 hover:border-blue-400 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <FileText className="w-4 h-4" />
                  View File
                </button>
                <button 
                  onClick={() => {
                    setDataToReport(selectedData);
                    setShowReportIssue(true);
                  }}
                  className="flex-1 px-3 py-2 bg-orange-50 text-orange-700 border border-orange-300 rounded-lg text-sm hover:bg-orange-100 hover:border-orange-400 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <AlertTriangle className="w-4 h-4" />
                  Report
                </button>
                <button 
                  onClick={() => {
                    const fileName = `${(selectedData as any).data_id}.json`;
                    const fileContent = JSON.stringify(selectedData, null, 2);
                    const blob = new Blob([fileContent], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = fileName;
                    a.click();
                  }}
                  className="flex-1 px-3 py-2 bg-green-50 text-green-700 border border-green-300 rounded-lg text-sm hover:bg-green-100 hover:border-green-400 flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Download
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Visualization Modal */}
      {showVisualization && renderVisualization()}

      {/* Data Structure Guide Modal */}
      <DataStructureGuide
        isOpen={showGuide}
        onClose={() => setShowGuide(false)}
        type="reference"
      />

      {/* File Viewer Modal */}
      {fileViewerData && (
        <FileViewer
          isOpen={fileViewerOpen}
          onClose={() => {
            setFileViewerOpen(false);
            setFileViewerData(null);
          }}
          fileType="info"
          fileName={`${fileViewerData.data_id}.json`}
          modelName={fileViewerData.name}
          content={fileViewerData}
        />
      )}
      {/* Report Issue Modal */}
      {dataToReport && (
        <ReportIssue
          isOpen={showReportIssue}
          onClose={() => {
            setShowReportIssue(false);
            setDataToReport(null);
          }}
          itemType="reference-data"
          itemName={dataToReport.name}
          itemId={dataToReport.data_id}
        />
      )}
      {/* Upload Modal */}
      <ReferenceDataUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUpload={handleDataUpload}
      />
    </div>
  );
};

export default ReferenceDataLibrary;