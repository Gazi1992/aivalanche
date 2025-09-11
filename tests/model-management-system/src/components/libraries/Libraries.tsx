import React, { useState } from 'react';
import { FileText, Database, TestTube, Download, Eye } from 'lucide-react';
import dataService from '../../services/dataService';
import ModelLibrary from './ModelLibrary';
import ReferenceDataLibrary from './ReferenceDataLibrary';
import TestbenchLibrary from './TestbenchLibrary';

type LibraryType = 'models' | 'reference' | 'testbenches';

const Libraries: React.FC = () => {
  const [activeTab, setActiveTab] = useState<LibraryType>('models');
  const [selectedItem, setSelectedItem] = useState<any>(null);

  const models = dataService.getModelTemplates();
  const referenceData = dataService.getReferenceData();
  const testbenchLibraries = dataService.getTestbenchLibraries();



  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Fixed Header */}
      <div className="flex-shrink-0 space-y-6 pb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Model Libraries</h1>
          <p className="text-gray-600 mt-2">Browse and manage model templates, data, and testbenches</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('models')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'models'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <FileText className="w-4 h-4 inline-block mr-2" />
              Model Templates ({models.length})
            </button>
            <button
              onClick={() => setActiveTab('reference')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'reference'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Database className="w-4 h-4 inline-block mr-2" />
              Reference Data ({referenceData.length})
            </button>
            <button
              onClick={() => setActiveTab('testbenches')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'testbenches'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <TestTube className="w-4 h-4 inline-block mr-2" />
              Testbenches ({testbenchLibraries.reduce((acc, lib) => acc + lib.testbenches.length, 0)})
            </button>
          </nav>
        </div>
      </div>

      {/* Scrollable Content Area */}
      <div className="flex-1 overflow-hidden min-h-0">
        {activeTab === 'models' ? (
          <ModelLibrary models={models} />
        ) : activeTab === 'reference' ? (
          <ReferenceDataLibrary referenceData={referenceData} />
        ) : (
          <TestbenchLibrary libraries={testbenchLibraries} />
        )}
      </div>

      {/* Detail Modal */}
      {selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedItem.name}
                </h2>
                <button
                  onClick={() => setSelectedItem(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">Details</h3>
                  <pre className="text-sm text-gray-600 overflow-x-auto">
                    {JSON.stringify(selectedItem, null, 2)}
                  </pre>
                </div>
                
                <div className="flex gap-3">
                  <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2">
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                  <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
                    <Eye className="w-4 h-4" />
                    View Full Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Libraries;