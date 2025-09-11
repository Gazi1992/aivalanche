import React, { useState, useMemo, useCallback } from 'react';
import { 
  Clock, CheckCircle, XCircle, AlertCircle, Filter, 
  Calendar, User, Tag, FileText, MessageSquare,
  Check, X, Send, 
  Archive, Download, Plus, HelpCircle, ChevronDown
} from 'lucide-react';
import { PageHeader, FilterBar, SidePanel } from '../layout';
import { Button, ViewToggle, DataView, Column, ViewMode } from '../ui';
import dataService from '../../services/dataService';
import { ModelRequest } from '../../types';
import { useAuth } from '../../contexts/AuthContext';
import { statsCardStyles } from '../../theme';

type FilterStatus = 'all' | ModelRequest['status'];
type FilterPriority = 'all' | ModelRequest['priority'];

interface RequestAction {
  type: 'accept' | 'reject' | 'request-info' | 'view';
  requestId: string;
  comment?: string;
}

const Requests: React.FC = () => {
  const { user } = useAuth();
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const [selectedRequest, setSelectedRequest] = useState<ModelRequest | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [filterPriority, setFilterPriority] = useState<FilterPriority>('all');
  const [showActionModal, setShowActionModal] = useState(false);
  const [currentAction, setCurrentAction] = useState<RequestAction | null>(null);
  const [actionComment, setActionComment] = useState('');
  
  // Collapsible sections state
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    technicalSpecs: true,
    timeline: true,
    requester: true,
    attachments: true,
    comments: true
  });
  
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Get requests from data service
  const allRequests = dataService.getModelRequests();

  // Filter requests based on search and filters
  const filteredRequests = useMemo(() => {
    return allRequests.filter(request => {
      const matchesSearch = searchQuery === '' || 
        request.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        request.requester.toLowerCase().includes(searchQuery.toLowerCase()) ||
        request.technology.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesStatus = filterStatus === 'all' || request.status === filterStatus;
      const matchesPriority = filterPriority === 'all' || request.priority === filterPriority;
      
      return matchesSearch && matchesStatus && matchesPriority;
    });
  }, [allRequests, searchQuery, filterStatus, filterPriority]);

  // Calculate statistics
  const stats = useMemo(() => {
    const total = allRequests.length;
    const pending = allRequests.filter(r => r.status === 'pending').length;
    const awaitingInfo = allRequests.filter(r => r.status === 'awaiting-info').length;
    const rejected = allRequests.filter(r => r.status === 'rejected').length;
    const accepted = allRequests.filter(r => r.status === 'accepted').length;
    const highPriority = allRequests.filter(r => r.status === 'pending' && r.priority === 'high').length;
    const overdue = allRequests.filter(r => r.status === 'pending' && new Date(r.due_date) < new Date()).length;
    
    return { total, pending, awaitingInfo, rejected, accepted, highPriority, overdue };
  }, [allRequests]);

  const handleAction = useCallback((action: RequestAction['type'], request: ModelRequest) => {
    setCurrentAction({ type: action, requestId: request.request_id });
    setSelectedRequest(request);
    if (action === 'view') {
      // Just open the details panel
      return;
    }
    setShowActionModal(true);
  }, []);

  const confirmAction = () => {
    if (!currentAction) return;
    
    // Here you would normally make an API call
    console.log('Action confirmed:', currentAction, 'Comment:', actionComment);
    
    // Close modal and reset
    setShowActionModal(false);
    setActionComment('');
    setCurrentAction(null);
  };

  const getStatusIcon = useCallback((status: ModelRequest['status']) => {
    switch (status) {
      case 'accepted': return <CheckCircle className="w-4 h-4" />;
      case 'awaiting-info': return <HelpCircle className="w-4 h-4" />;
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'rejected': return <XCircle className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  }, []);

  const getStatusColor = useCallback((status: ModelRequest['status']) => {
    switch (status) {
      case 'accepted': return 'text-green-600 bg-green-50 border-green-200';
      case 'awaiting-info': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'pending': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'rejected': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  }, []);

  const getPriorityColor = useCallback((priority: ModelRequest['priority']) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  }, []);

  // Define table columns
  const tableColumns: Column<ModelRequest>[] = useMemo(() => [
    {
      key: 'title',
      header: 'Request',
      sortable: true,
      render: (value, item) => (
        <div>
          <div className="font-medium text-gray-900">{item.title}</div>
          <div className="text-sm text-gray-500">{item.technology}</div>
        </div>
      ),
    },
    {
      key: 'type',
      header: 'Type',
      sortable: true,
      render: (value) => <span className="text-sm text-gray-600">{value}</span>,
    },
    {
      key: 'requester',
      header: 'Requester',
      sortable: true,
      render: (value) => <span className="text-sm text-gray-600">{value}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (value, item) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)} border inline-flex items-center gap-1`}>
          {getStatusIcon(item.status)}
          {item.status.replace('-', ' ')}
        </span>
      ),
    },
    {
      key: 'priority',
      header: 'Priority',
      sortable: true,
      render: (value, item) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(item.priority)} border`}>
          {item.priority}
        </span>
      ),
    },
    {
      key: 'due_date',
      header: 'Due Date',
      sortable: true,
      render: (value) => <span className="text-sm text-gray-600">{new Date(value).toLocaleDateString()}</span>,
    },
    {
      key: 'actions',
      header: 'Actions',
      sortable: false,
      render: (_, item) => (
        <>
          {(item.status === 'pending' || item.status === 'awaiting-info') && user?.role !== 'viewer' && (
            <div className="flex items-center gap-1">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleAction('accept', item);
                }}
                className="p-1 text-green-600 hover:bg-green-50 rounded"
                title="Accept"
              >
                <Check className="w-4 h-4" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleAction('reject', item);
                }}
                className="p-1 text-red-600 hover:bg-red-50 rounded"
                title="Reject"
              >
                <X className="w-4 h-4" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleAction('request-info', item);
                }}
                className="p-1 text-yellow-600 hover:bg-yellow-50 rounded"
                title="Request Info"
              >
                <HelpCircle className="w-4 h-4" />
              </button>
            </div>
          )}
        </>
      ),
    },
  ], [user, handleAction, getStatusColor, getStatusIcon, getPriorityColor]);

  return (
    <div className="h-full">
      {/* Main Content Area */}
      <div className={`${selectedRequest ? 'mr-[500px]' : ''} h-full flex flex-col overflow-hidden transition-all duration-300`}>
        {/* Header */}
        <div className="mb-4">
          <PageHeader
            title="Model Calibration Requests"
            description="Review and manage incoming calibration requests"
          />
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-6 gap-4 mb-6">
          <div className={`${statsCardStyles.containerBlue}`}>
            <div className={statsCardStyles.content}>
              <div>
                <p className={statsCardStyles.label}>New Requests</p>
                <p className={`${statsCardStyles.value} text-blue-600`}>{stats.pending}</p>
              </div>
              <div className={statsCardStyles.iconContainerBlue}>
                <Clock className={statsCardStyles.iconBlue} />
              </div>
            </div>
          </div>
          
          <div className={`${statsCardStyles.containerOrange}`}>
            <div className={statsCardStyles.content}>
              <div>
                <p className={statsCardStyles.label}>Awaiting Info</p>
                <p className={`${statsCardStyles.value} text-orange-600`}>{stats.awaitingInfo}</p>
              </div>
              <div className={statsCardStyles.iconContainerOrange}>
                <HelpCircle className={statsCardStyles.iconOrange} />
              </div>
            </div>
          </div>
          
          <div className={`${statsCardStyles.containerGreen}`}>
            <div className={statsCardStyles.content}>
              <div>
                <p className={statsCardStyles.label}>Accepted</p>
                <p className={`${statsCardStyles.value} text-green-600`}>{stats.accepted}</p>
              </div>
              <div className={statsCardStyles.iconContainerGreen}>
                <CheckCircle className={statsCardStyles.iconGreen} />
              </div>
            </div>
          </div>
          
          <div className={`${statsCardStyles.container} p-4 hover:border-red-200`}>
            <div className={statsCardStyles.content}>
              <div>
                <p className={statsCardStyles.label}>Rejected</p>
                <p className={`${statsCardStyles.value} text-red-600`}>{stats.rejected}</p>
              </div>
              <div className="p-2.5 bg-red-50 rounded-lg">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </div>
          
          <div className={`${statsCardStyles.container} p-4 hover:border-red-200`}>
            <div className={statsCardStyles.content}>
              <div>
                <p className={statsCardStyles.label}>High Priority</p>
                <p className={`${statsCardStyles.value} text-red-600`}>{stats.highPriority}</p>
              </div>
              <div className="p-2.5 bg-red-50 rounded-lg">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </div>
          
          <div className={`${statsCardStyles.containerPurple}`}>
            <div className={statsCardStyles.content}>
              <div>
                <p className={statsCardStyles.label}>Total Active</p>
                <p className={statsCardStyles.value}>{stats.pending + stats.awaitingInfo}</p>
              </div>
              <div className={statsCardStyles.iconContainerPurple}>
                <Archive className={statsCardStyles.iconPurple} />
              </div>
            </div>
          </div>
        </div>

        {/* Filters Bar */}
        <FilterBar
          searchValue={searchQuery}
          onSearchChange={setSearchQuery}
          filters={
            <>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as FilterStatus)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="awaiting-info">Awaiting Info</option>
                <option value="accepted">Accepted</option>
                <option value="rejected">Rejected</option>
              </select>
              
              <select
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value as FilterPriority)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Priority</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
              
              <Button variant="secondary" size="md" icon={<Filter className="w-4 h-4" />}>
                More Filters
              </Button>
            </>
          }
          actions={
            <div className="flex items-center gap-3">
              <Button
                variant="primary"
                size="md"
                icon={<Plus className="w-4 h-4" />}
              >
                New Request
              </Button>
              <ViewToggle viewMode={viewMode} onViewChange={setViewMode} />
            </div>
          }
        />

        {/* Content View */}
        <DataView
          data={filteredRequests}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
          columns={tableColumns}
          onRowClick={(request) => {
            setSelectedRequest(request);
            setCurrentAction({ type: 'view', requestId: request.request_id });
            // Reset all sections to expanded when opening details
            setExpandedSections({
              technicalSpecs: true,
              timeline: true,
              requester: true,
              attachments: true,
              comments: true
            });
          }}
          renderCard={(request) => (
            <div className="flex flex-col h-full">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-gray-900 line-clamp-2">{request.title}</h3>
                </div>
                <div className="ml-2">
                  {getStatusIcon(request.status)}
                </div>
              </div>
              
              <div className="flex gap-2 mb-3">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(request.status)} border`}>
                  {request.status.replace('-', ' ')}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(request.priority)} border`}>
                  {request.priority}
                </span>
              </div>
              
              <div className="flex-1 space-y-2 text-xs text-gray-600">
                <div className="flex items-center gap-1">
                  <User className="w-3 h-3" />
                  <span className="truncate">{request.requester}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Tag className="w-3 h-3" />
                  <span className="truncate">{request.technology}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  <span>{new Date(request.due_date).toLocaleDateString()}</span>
                </div>
              </div>
              
              {(request.status === 'pending' || request.status === 'awaiting-info') && user?.role !== 'viewer' && (
                <div className="flex gap-1 mt-3 pt-3 border-t border-gray-100">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAction('accept', request);
                    }}
                    className="flex-1 p-1.5 bg-green-50 text-green-600 border border-green-200 rounded text-xs hover:bg-green-100 flex items-center justify-center"
                    title="Accept"
                  >
                    <Check className="w-3 h-3" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAction('reject', request);
                    }}
                    className="flex-1 p-1.5 bg-red-50 text-red-600 border border-red-200 rounded text-xs hover:bg-red-100 flex items-center justify-center"
                    title="Reject"
                  >
                    <X className="w-3 h-3" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAction('request-info', request);
                    }}
                    className="flex-1 p-1.5 bg-yellow-50 text-yellow-600 border border-yellow-200 rounded text-xs hover:bg-yellow-100 flex items-center justify-center"
                    title="Request Info"
                  >
                    <HelpCircle className="w-3 h-3" />
                  </button>
                </div>
              )}
            </div>
          )}
          cardClassName={(request) => `bg-white border rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer ${
            selectedRequest?.request_id === request.request_id ? 'border-purple-500 bg-purple-50' : 'border-gray-200'
          }`}
          className="flex-1"
          showViewToggle={false}
        />
      </div>

      {/* Side Panel */}
      <SidePanel
        isOpen={!!selectedRequest}
        onClose={() => {
          setSelectedRequest(null);
          // Reset sections to expanded for next time
          setExpandedSections({
            technicalSpecs: true,
            timeline: true,
            requester: true,
            attachments: true,
            comments: true
          });
        }}
        title="Request Details"
        width="md"
      >
        {selectedRequest && (
          <div className="space-y-4">
            {/* Header Section */}
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-3 border border-purple-100">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h2 className="text-lg font-bold text-gray-900">{selectedRequest.title}</h2>
                  <p className="text-xs text-gray-500 font-mono mt-0.5">{selectedRequest.request_id}</p>
                </div>
                <div className="flex flex-col items-end gap-1.5">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedRequest.status)} border inline-flex items-center gap-1`}>
                    {getStatusIcon(selectedRequest.status)}
                    {selectedRequest.status.replace('-', ' ').toUpperCase()}
                  </span>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getPriorityColor(selectedRequest.priority)} border`}>
                    {selectedRequest.priority.toUpperCase()} PRIORITY
                  </span>
                </div>
              </div>
              {selectedRequest.description && (
                <p className="text-sm text-gray-700 bg-white/50 rounded p-2 italic">
                  "{selectedRequest.description}"
                </p>
              )}
            </div>

            {/* Technical Specifications */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('technicalSpecs')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <FileText className="w-4 h-4 text-gray-500" />
                    Technical Specifications
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.technicalSpecs ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.technicalSpecs && (
              <div className="p-3">
                <div className="grid grid-cols-3 gap-2">
                  <div className="bg-gray-50 rounded-lg p-2.5 border border-gray-200">
                    <p className="text-xs font-medium text-gray-600 mb-0.5">Model Type</p>
                    <p className="text-sm font-semibold text-gray-900 capitalize">{selectedRequest.type}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2.5 border border-gray-200">
                    <p className="text-xs font-medium text-gray-600 mb-0.5">Component</p>
                    <p className="text-sm font-semibold text-gray-900">{selectedRequest.component_type}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2.5 border border-gray-200">
                    <p className="text-xs font-medium text-gray-600 mb-0.5">Technology</p>
                    <p className="text-sm font-semibold text-gray-900">{selectedRequest.technology}</p>
                  </div>
                </div>
              </div>
              )}
            </div>

            {/* Timeline */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('timeline')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Calendar className="w-4 h-4 text-gray-500" />
                    Timeline
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.timeline ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.timeline && (
              <div className="p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <div className="w-9 h-9 bg-gray-100 rounded-full flex items-center justify-center">
                      <Clock className="w-4 h-4 text-gray-600" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Requested</p>
                      <p className="text-sm font-semibold text-gray-900">
                        {new Date(selectedRequest.request_date).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </p>
                    </div>
                  </div>
                  <div className="flex-1 px-3">
                    <div className="h-0.5 bg-gray-300 relative">
                      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white px-2">
                        <span className="text-sm font-bold text-gray-700">
                          {Math.max(0, Math.ceil((new Date(selectedRequest.due_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)))} days
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div>
                      <p className="text-xs text-gray-500 text-right">Due Date</p>
                      <p className="text-sm font-semibold text-gray-900">
                        {new Date(selectedRequest.due_date).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </p>
                    </div>
                    <div className="w-9 h-9 bg-gray-100 rounded-full flex items-center justify-center">
                      <AlertCircle className="w-4 h-4 text-gray-600" />
                    </div>
                  </div>
                </div>
              </div>
              )}
            </div>

            {/* Requester Card */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('requester')}
              >
                <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <User className="w-4 h-4 text-gray-500" />
                    Requester
                  </span>
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.requester ? '' : '-rotate-90'}`} />
                </h3>
              </div>
              {expandedSections.requester && (
              <div className="p-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                    <User className="w-5 h-5 text-gray-600" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-900">{selectedRequest.requester}</p>
                    <p className="text-xs text-gray-500">Submitted {new Date(selectedRequest.request_date).toLocaleDateString()}</p>
                  </div>
                </div>
              </div>
              )}
            </div>

            {/* Attachments */}
            {selectedRequest.attachments && selectedRequest.attachments.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div 
                  className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => toggleSection('attachments')}
                >
                  <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <FileText className="w-4 h-4 text-gray-500" />
                      Attachments ({selectedRequest.attachments.length})
                    </span>
                    <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.attachments ? '' : '-rotate-90'}`} />
                  </h3>
                </div>
                {expandedSections.attachments && (
                <div className="p-3">
                  <div className="space-y-1.5">
                    {selectedRequest.attachments.map((attachment, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-gray-500" />
                          <span className="text-sm font-medium text-gray-700">{attachment}</span>
                        </div>
                        <button className="p-1 hover:bg-gray-200 rounded transition-colors">
                          <Download className="w-4 h-4 text-gray-600" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
                )}
              </div>
            )}
            
            {/* Comments */}
            {selectedRequest.comments && selectedRequest.comments.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div 
                  className="bg-gray-50 px-3 py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => toggleSection('comments')}
                >
                  <h3 className="text-sm font-semibold text-gray-700 flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <MessageSquare className="w-4 h-4 text-gray-500" />
                      Comments ({selectedRequest.comments.length})
                    </span>
                    <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${expandedSections.comments ? '' : '-rotate-90'}`} />
                  </h3>
                </div>
                {expandedSections.comments && (
                <div className="p-3">
                  <div className="space-y-2">
                    {selectedRequest.comments.map((comment, index) => (
                      <div key={index} className="p-2 bg-gray-50 rounded">
                        <div className="flex items-start gap-2">
                          <MessageSquare className="w-4 h-4 text-gray-500 mt-0.5" />
                          <div className="flex-1">
                            <p className="text-sm">{comment.text}</p>
                            <p className="text-xs text-gray-500 mt-1">
                              {comment.author} - {new Date(comment.date).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                )}
              </div>
            )}
            
            
            {/* Actions */}
            {(selectedRequest.status === 'pending' || selectedRequest.status === 'awaiting-info') && user?.role !== 'viewer' && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex gap-2">
                  <button
                    onClick={() => handleAction('accept', selectedRequest)}
                    className="flex-1 px-3 py-2 bg-green-50 text-green-700 border border-green-300 rounded-lg text-sm hover:bg-green-100 hover:border-green-400 flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Check className="w-4 h-4" />
                    Accept
                  </button>
                  <button
                    onClick={() => handleAction('reject', selectedRequest)}
                    className="flex-1 px-3 py-2 bg-red-50 text-red-700 border border-red-300 rounded-lg text-sm hover:bg-red-100 hover:border-red-400 flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <X className="w-4 h-4" />
                    Reject
                  </button>
                  <button
                    onClick={() => handleAction('request-info', selectedRequest)}
                    className="flex-1 px-3 py-2 bg-yellow-50 text-yellow-700 border border-yellow-300 rounded-lg text-sm hover:bg-yellow-100 hover:border-yellow-400 flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <HelpCircle className="w-4 h-4" />
                    Request Info
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </SidePanel>

      {/* Action Modal */}
      {showActionModal && currentAction && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg w-96 p-6">
            <h3 className="text-lg font-semibold mb-4">
              {currentAction.type === 'accept' && 'Accept Request'}
              {currentAction.type === 'reject' && 'Reject Request'}
              {currentAction.type === 'request-info' && 'Request Additional Information'}
            </h3>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                Request: <span className="font-medium">{selectedRequest.title}</span>
              </p>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {currentAction.type === 'request-info' ? 'Information Needed' : 'Comment'} (Required)
              </label>
              <textarea
                value={actionComment}
                onChange={(e) => setActionComment(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                rows={4}
                placeholder={
                  currentAction.type === 'request-info' 
                    ? 'Please describe what additional information is needed...'
                    : 'Add a comment...'
                }
              />
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setShowActionModal(false);
                  setActionComment('');
                  setCurrentAction(null);
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmAction}
                disabled={!actionComment.trim()}
                className={`flex-1 px-4 py-2 rounded-lg text-white flex items-center justify-center gap-2 ${
                  actionComment.trim()
                    ? currentAction.type === 'accept' 
                      ? 'bg-green-600 hover:bg-green-700'
                      : currentAction.type === 'reject'
                      ? 'bg-red-600 hover:bg-red-700'
                      : 'bg-yellow-600 hover:bg-yellow-700'
                    : 'bg-gray-400 cursor-not-allowed'
                }`}
              >
                <Send className="w-4 h-4" />
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Requests;