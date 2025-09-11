import React, { useState } from 'react';
import { 
  Cpu, Download, Filter, X, Code, 
  FileText, Tag, ChevronRight, ChevronDown, 
  CheckCircle, AlertCircle, HelpCircle,
  Zap, Activity, BarChart3, AlertTriangle, Plus, Package, Database
} from 'lucide-react';
import { TestbenchLibrary as TestbenchLibraryType, Testbench } from '../../types';
import DataStructureGuide from '../DataStructureGuide';
import TestbenchSchematic from '../TestbenchSchematic';
import ReportIssue from '../ReportIssue';
import FileViewer from '../FileViewer';
import TestbenchUploadModal from '../modals/TestbenchUploadModal';
import { FilterBar } from '../layout';
import { Button, ViewToggle } from '../ui';

interface TestbenchLibraryProps {
  libraries: TestbenchLibraryType[];
}

const TestbenchLibrary: React.FC<TestbenchLibraryProps> = ({ libraries }) => {
  const [selectedTestbench, setSelectedTestbench] = useState<{library: TestbenchLibraryType, testbench: Testbench} | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterValidated, setFilterValidated] = useState('all');
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table');
  const [expandedLibraries, setExpandedLibraries] = useState<Set<string>>(new Set());
  const [showGuide, setShowGuide] = useState(false);
  const [showExample, setShowExample] = useState<number>(0);
  const [showReportIssue, setShowReportIssue] = useState(false);
  const [testbenchToReport, setTestbenchToReport] = useState<{library: TestbenchLibraryType, testbench: Testbench} | null>(null);
  const [fileViewerOpen, setFileViewerOpen] = useState(false);
  const [fileViewerTestbench, setFileViewerTestbench] = useState<{library: TestbenchLibraryType, testbench: Testbench} | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  
  // Collapsible sections state
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    specifications: true,
    schematic: true,
    netlist: true,
    parameters: true,
    examples: true,
    metadata: true
  });
  
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Flatten all testbenches with their library info
  const allTestbenches = libraries.flatMap(lib => 
    lib.testbenches.map(tb => ({ library: lib, testbench: tb }))
  );

  const filteredTestbenches = allTestbenches.filter(({ testbench }) => {
    const matchesSearch = 
      testbench.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      testbench.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      testbench.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = filterType === 'all' || testbench.type === filterType;
    const matchesValidated = filterValidated === 'all' || 
      (filterValidated === 'validated' ? testbench.validated : !testbench.validated);
    return matchesSearch && matchesType && matchesValidated;
  });

  // Get unique types for filter
  const types = Array.from(new Set(allTestbenches.map(({ testbench }) => testbench.type)));

  const getTypeIcon = (type: string) => {
    switch(type) {
      case 'dc_sweep': return <Zap className="w-4 h-4" />;
      case 'ac_analysis': return <Activity className="w-4 h-4" />;
      case 'transient': return <BarChart3 className="w-4 h-4" />;
      case 'noise': return <Activity className="w-4 h-4" />;
      case 'sp_analysis': return <Cpu className="w-4 h-4" />;
      case 'hb_analysis': return <Activity className="w-4 h-4" />;
      case 'pnoise': return <Activity className="w-4 h-4" />;
      default: return <Cpu className="w-4 h-4" />;
    }
  };

  const toggleLibrary = (libraryName: string) => {
    const newExpanded = new Set(expandedLibraries);
    if (newExpanded.has(libraryName)) {
      newExpanded.delete(libraryName);
    } else {
      newExpanded.add(libraryName);
    }
    setExpandedLibraries(newExpanded);
  };

  const handleTestbenchUpload = (newTestbench: any) => {
    // In a real application, this would update the testbench list
    console.log('New testbench uploaded:', newTestbench);
    // You could update the libraries array here or call a parent handler
  };

  const downloadTestbench = (library: TestbenchLibraryType, testbench: Testbench) => {
    const testbenchData = {
      library_info: {
        name: library.library_name,
        version: library.version,
        organization: library.organization
      },
      testbench: testbench
    };
    
    const blob = new Blob([JSON.stringify(testbenchData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${testbench.testbench_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-full">
      {/* Main Content Area */}
      <div className={`${selectedTestbench ? 'mr-[600px]' : ''} h-full flex flex-col overflow-hidden transition-all duration-300`}>
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
                {types.map(type => (
                  <option key={type} value={type}>{type.replace(/_/g, ' ').toUpperCase()}</option>
                ))}
              </select>
              <select
                value={filterValidated}
                onChange={(e) => setFilterValidated(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Status</option>
                <option value="validated">Validated</option>
                <option value="not-validated">Not Validated</option>
              </select>
              <Button variant="secondary" size="md" icon={<Filter className="w-4 h-4" />}>
                More Filters
              </Button>
              <Button 
                onClick={() => setShowGuide(true)}
                variant="secondary"
                size="md"
                icon={<HelpCircle className="w-4 h-4" />}
                title="Testbench Structure Guide"
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
                Upload Testbench
              </Button>
              <ViewToggle viewMode={viewMode} onViewChange={setViewMode} />
            </div>
          }
        />

        {/* Content View */}
        <div className="bg-white rounded-lg shadow flex-1 overflow-auto">
          {viewMode === 'table' ? (
            <div className="divide-y divide-gray-200">
              {libraries.map((library) => (
                <div key={library.library_name}>
                  {/* Library Header */}
                  <div 
                    className="px-6 py-3 bg-gray-50 hover:bg-gray-100 cursor-pointer flex items-center justify-between"
                    onClick={() => toggleLibrary(library.library_name)}
                  >
                    <div className="flex items-center gap-3">
                      {expandedLibraries.has(library.library_name) ? (
                        <ChevronDown className="w-5 h-5 text-gray-500" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-500" />
                      )}
                      <div>
                        <h3 className="font-semibold text-gray-900">{library.library_name}</h3>
                        <p className="text-sm text-gray-500">{library.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>{library.testbenches.length} testbenches</span>
                      <span>v{library.version}</span>
                    </div>
                  </div>

                  {/* Testbenches Table */}
                  {expandedLibraries.has(library.library_name) && (
                    <table className="w-full">
                      <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Testbench
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Type
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Compatible Devices
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Measurements
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {library.testbenches
                          .filter(tb => {
                            const matchesSearch = 
                              tb.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                              tb.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                              tb.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
                            const matchesType = filterType === 'all' || tb.type === filterType;
                            const matchesValidated = filterValidated === 'all' || 
                              (filterValidated === 'validated' ? tb.validated : !tb.validated);
                            return matchesSearch && matchesType && matchesValidated;
                          })
                          .map((testbench) => (
                          <tr 
                            key={testbench.testbench_id}
                            className={`hover:bg-gray-50 cursor-pointer ${
                              selectedTestbench?.testbench.testbench_id === testbench.testbench_id ? 'bg-purple-50' : ''
                            }`}
                            onClick={() => {
                              setSelectedTestbench({ library, testbench });
                              // Reset all sections to expanded when opening details
                              setExpandedSections({
                                specifications: true,
                                schematic: true,
                                netlist: true,
                                parameters: true,
                                examples: true,
                                metadata: true
                              });
                            }}
                          >
                            <td className="px-6 py-4">
                              <div className="flex items-center">
                                {getTypeIcon(testbench.type)}
                                <div className="ml-3">
                                  <div className="text-sm font-medium text-gray-900">{testbench.name}</div>
                                  <div className="text-sm text-gray-500">{testbench.testbench_id}</div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {testbench.type.replace(/_/g, ' ')}
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex flex-wrap gap-1">
                                {testbench.compatible_devices.slice(0, 3).map((device, idx) => (
                                  <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                                    {device}
                                  </span>
                                ))}
                                {testbench.compatible_devices.length > 3 && (
                                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                                    +{testbench.compatible_devices.length - 3}
                                  </span>
                                )}
                              </div>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {testbench.measurements.length} measurements
                            </td>
                            <td className="px-6 py-4">
                              {testbench.validated ? (
                                <span className="flex items-center gap-1 text-green-600">
                                  <CheckCircle className="w-4 h-4" />
                                  <span className="text-sm">Validated</span>
                                </span>
                              ) : (
                                <span className="flex items-center gap-1 text-yellow-600">
                                  <AlertCircle className="w-4 h-4" />
                                  <span className="text-sm">Pending</span>
                                </span>
                              )}
                            </td>
                            <td className="px-6 py-4 text-right text-sm font-medium">
                              <div className="flex items-center justify-end gap-2">
                                <button 
                                  className="text-blue-600 hover:text-blue-900"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setFileViewerTestbench({ library, testbench });
                                    setFileViewerOpen(true);
                                  }}
                                  title="View File"
                                >
                                  <FileText className="w-4 h-4" />
                                </button>
                                <button 
                                  className="text-orange-600 hover:text-orange-700"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setTestbenchToReport({ library, testbench });
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
                                    downloadTestbench(library, testbench);
                                  }}
                                  title="Download Testbench"
                                >
                                  <Download className="w-4 h-4" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredTestbenches.map(({ library, testbench }) => (
                <div
                  key={`${library.library_name}-${testbench.testbench_id}`}
                  className={`bg-white border rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer ${
                    selectedTestbench?.testbench.testbench_id === testbench.testbench_id 
                      ? 'border-purple-500 bg-purple-50' 
                      : 'border-gray-200'
                  }`}
                  onClick={() => setSelectedTestbench({ library, testbench })}
                >
                  <div className="flex items-center justify-between mb-3">
                    {getTypeIcon(testbench.type)}
                    {testbench.validated ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-yellow-500" />
                    )}
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-1 truncate" title={testbench.name}>
                    {testbench.name}
                  </h3>
                  <p className="text-xs text-gray-500 mb-2">{library.library_name}</p>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {testbench.description}
                  </p>
                  <div className="space-y-1 text-xs text-gray-600">
                    <div className="flex justify-between">
                      <span>Type:</span>
                      <span className="font-medium">{testbench.type.replace(/_/g, ' ')}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Outputs:</span>
                      <span className="font-medium">{Object.keys(testbench.outputs).length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Examples:</span>
                      <span className="font-medium">{testbench.examples.length}</span>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex flex-wrap gap-1">
                      {testbench.tags.slice(0, 3).map((tag, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          {tag}
                        </span>
                      ))}
                      {testbench.tags.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          +{testbench.tags.length - 3}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="mt-3 flex justify-between items-center">
                    <span className="text-xs text-gray-500">
                      {new Date(library.modified).toLocaleDateString()}
                    </span>
                    <div className="flex items-center gap-2">
                      <button
                        className="text-blue-600 hover:text-blue-900"
                        onClick={(e) => {
                          e.stopPropagation();
                          setFileViewerTestbench({ library, testbench });
                          setFileViewerOpen(true);
                        }}
                        title="View File"
                      >
                        <FileText className="w-4 h-4" />
                      </button>
                      <button
                        className="text-orange-600 hover:text-orange-700"
                        onClick={(e) => {
                          e.stopPropagation();
                          setTestbenchToReport({ library, testbench });
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
                          downloadTestbench(library, testbench);
                        }}
                        title="Download Testbench"
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
      {selectedTestbench && (
        <div className="fixed right-0 top-0 bottom-0 w-[600px] bg-white border-l border-gray-200 flex flex-col z-40 shadow-xl">
          {/* Fixed Header */}
          <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between flex-shrink-0">
            <h2 className="text-lg font-semibold text-gray-900">Testbench Details</h2>
            <button
              onClick={() => {
                setSelectedTestbench(null);
                setShowExample(0);
                // Reset sections to expanded for next time
                setExpandedSections({
                  specifications: true,
                  schematic: true,
                  netlist: true,
                  parameters: true,
                  examples: true,
                  metadata: true
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
                  <h2 className="text-lg font-bold text-gray-900">{selectedTestbench.testbench.name}</h2>
                  <p className="text-xs text-gray-500 font-mono mt-0.5">{selectedTestbench.testbench.testbench_id}</p>
                </div>
                <div className="flex flex-col items-end gap-1.5">
                  {selectedTestbench.testbench.validated ? (
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />
                      Validated
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      Not Validated
                    </span>
                  )}
                  <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-700">
                    {selectedTestbench.testbench.type.replace(/_/g, ' ').toUpperCase()}
                  </span>
                </div>
              </div>
              {selectedTestbench.testbench.description && (
                <p className="text-sm text-gray-700 bg-white/50 rounded p-2 italic">
                  "{selectedTestbench.testbench.description}"
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
                    <span className="text-xs text-gray-500">Library:</span> <span className="text-sm font-medium text-gray-700">{selectedTestbench.library.library_name}</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Version:</span> <span className="text-sm font-medium text-gray-700">{selectedTestbench.library.version}</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Type:</span> <span className="text-sm font-medium text-gray-700">{selectedTestbench.testbench.type}</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Organization:</span> <span className="text-sm font-medium text-gray-700">{selectedTestbench.library.organization}</span>
                  </div>
                </div>
              </div>
              )}
            </div>

            {/* Schematic Image */}
            {selectedTestbench.testbench.schematic && (
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div 
                  className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => toggleSection('schematic')}
                >
                  <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <Cpu className="w-4 h-4 text-gray-500" />
                      Circuit Schematic
                    </span>
                    <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.schematic ? '' : '-rotate-90'}`} />
                  </h3>
                </div>
                {expandedSections.schematic && (
                <div className="p-3">
                  <TestbenchSchematic 
                    schematicPath={selectedTestbench.testbench.schematic}
                    altText={`${selectedTestbench.testbench.name} schematic`}
                  />
                </div>
                )}
              </div>
            )}

            {/* Circuit Netlist */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('netlist')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Code className="w-4 h-4 text-gray-500" />
                    Circuit Netlist
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.netlist ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.netlist && (
              <div className="p-3">
                <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-xs overflow-x-auto">
                  {selectedTestbench.testbench.circuit.netlist.map((line, idx) => (
                    <div key={idx} className="flex">
                      <span className="text-gray-500 mr-3 select-none">{(idx + 1).toString().padStart(2, '0')}</span>
                      <span>{line}</span>
                    </div>
                  ))}
                </div>
              </div>
              )}
            </div>

            {/* Parameters */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('parameters')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Database className="w-4 h-4 text-gray-500" />
                    Parameters ({Object.keys(selectedTestbench.testbench.circuit.parameters).length})
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
                      <th className="px-3 py-2 text-left">Parameter</th>
                      <th className="px-3 py-2 text-left">Default</th>
                      <th className="px-3 py-2 text-left">Unit</th>
                      <th className="px-3 py-2 text-left">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {Object.entries(selectedTestbench.testbench.circuit.parameters).map(([name, param]) => (
                      <tr key={name}>
                        <td className="px-3 py-2 font-mono">{name}</td>
                        <td className="px-3 py-2">{param.default}</td>
                        <td className="px-3 py-2">{param.unit || '-'}</td>
                        <td className="px-3 py-2">{param.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
              )}
            </div>

            {/* Measurements */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('measurements')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Activity className="w-4 h-4 text-gray-500" />
                    Measurements ({selectedTestbench.testbench.measurements.length})
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.measurements ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.measurements && (
              <div className="p-3">
                <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-xs space-y-1">
                  {selectedTestbench.testbench.measurements.map((measurement, idx) => (
                    <div key={idx}>{measurement}</div>
                  ))}
                </div>
              </div>
              )}
            </div>

            {/* Outputs */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('outputs')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Database className="w-4 h-4 text-gray-500" />
                    Output Parameters ({Object.keys(selectedTestbench.testbench.outputs).length})
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.outputs ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.outputs && (
              <div className="p-3">
                <div className="bg-gray-50 rounded-lg overflow-hidden">
                  <table className="min-w-full text-xs">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-3 py-2 text-left">Output</th>
                        <th className="px-3 py-2 text-left">Unit</th>
                        <th className="px-3 py-2 text-left">Description</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {Object.entries(selectedTestbench.testbench.outputs).map(([name, output]) => (
                        <tr key={name}>
                          <td className="px-3 py-2 font-mono">{name}</td>
                          <td className="px-3 py-2">{output.unit || '-'}</td>
                          <td className="px-3 py-2">{output.description}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              )}
            </div>

            {/* Compatible Devices */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('devices')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Cpu className="w-4 h-4 text-gray-500" />
                    Compatible Devices
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.devices ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.devices && (
              <div className="p-3">
                <div className="flex flex-wrap gap-2">
                  {selectedTestbench.testbench.compatible_devices.map((device, idx) => (
                    <span key={idx} className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">
                      {device}
                    </span>
                  ))}
                </div>
              </div>
              )}
            </div>

            {/* Examples */}
            {selectedTestbench.testbench.examples.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">
                  Examples ({selectedTestbench.testbench.examples.length})
                </h4>
                <div className="space-y-2">
                  {selectedTestbench.testbench.examples.map((example, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg">
                      <button
                        onClick={() => setShowExample(showExample === idx + 1 ? 0 : idx + 1)}
                        className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center justify-between"
                      >
                        <div>
                          <div className="font-medium text-sm">{example.name}</div>
                          <div className="text-xs text-gray-500">{example.description}</div>
                        </div>
                        {showExample === idx + 1 ? (
                          <ChevronDown className="w-4 h-4 text-gray-400" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-gray-400" />
                        )}
                      </button>
                      {showExample === idx + 1 && (
                        <div className="p-4 border-t border-gray-200">
                          <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-xs overflow-x-auto">
                            {example.netlist.map((line, lineIdx) => (
                              <div key={lineIdx} className="flex">
                                <span className="text-gray-500 mr-3 select-none">
                                  {(lineIdx + 1).toString().padStart(3, '0')}
                                </span>
                                <span>{line}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tags */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Tags</h4>
              <div className="flex flex-wrap gap-2">
                {selectedTestbench.testbench.tags.map((tag, idx) => (
                  <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                    <Tag className="w-3 h-3 inline mr-1" />
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Library Info */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Library Information</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Library:</span>
                  <span className="text-gray-900">{selectedTestbench.library.library_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Version:</span>
                  <span className="text-gray-900">v{selectedTestbench.library.version}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Organization:</span>
                  <span className="text-gray-900">{selectedTestbench.library.organization}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">License:</span>
                  <span className="text-gray-900">{selectedTestbench.library.license}</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="pt-4 border-t border-gray-200 space-y-3">
              <div className="flex gap-3">
                <button 
                  onClick={() => {
                    setFileViewerTestbench(selectedTestbench);
                    setFileViewerOpen(true);
                  }}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                >
                  <FileText className="w-4 h-4" />
                  View File
                </button>
                <button className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center justify-center gap-2">
                  <Code className="w-4 h-4" />
                  Export as SPICE
                </button>
              </div>
              <button 
                onClick={() => downloadTestbench(selectedTestbench.library, selectedTestbench.testbench)}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download Testbench
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Data Structure Guide Modal */}
      <DataStructureGuide
        isOpen={showGuide}
        onClose={() => setShowGuide(false)}
        type="testbench"
      />

      {/* File Viewer Modal */}
      {fileViewerTestbench && (
        <FileViewer
          isOpen={fileViewerOpen}
          onClose={() => {
            setFileViewerOpen(false);
            setFileViewerTestbench(null);
          }}
          fileType="info"
          fileName={`${fileViewerTestbench.testbench.testbench_id}.json`}
          modelName={fileViewerTestbench.testbench.name}
          content={fileViewerTestbench}
        />
      )}
      {/* Report Issue Modal */}
      {testbenchToReport && (
        <ReportIssue
          isOpen={showReportIssue}
          onClose={() => {
            setShowReportIssue(false);
            setTestbenchToReport(null);
          }}
          itemType="testbench"
          itemName={`${testbenchToReport.testbench.name} (${testbenchToReport.library.library_name})`}
          itemId={testbenchToReport.testbench.testbench_id}
        />
      )}

      {/* Upload Modal */}
      <TestbenchUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUpload={handleTestbenchUpload}
      />
    </div>
  );
};

export default TestbenchLibrary;