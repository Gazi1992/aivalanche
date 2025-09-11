import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/pages/Dashboard';
import Libraries from './components/libraries/Libraries';
import MyModels from './components/pages/MyModels';
import UserProfile from './components/auth/UserProfile';
import Login from './components/auth/Login';
import Reports from './components/pages/Reports';
import Requests from './components/pages/Requests';
import IntroAnimation from './components/feedback/IntroAnimation';
import UserGuide from './components/UserGuide';
import ContactSupport from './components/ContactSupport';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './App.css';

function AppContent() {
  const { isAuthenticated, user } = useAuth();
  const [activeSection, setActiveSection] = useState('dashboard');
  const [showNewRequestModal, setShowNewRequestModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showIntro, setShowIntro] = useState(false);
  const [showUserGuide, setShowUserGuide] = useState(false);
  const [showSupport, setShowSupport] = useState(false);

  useEffect(() => {
    // Always show intro on page load/refresh
    // We'll use a timestamp to detect refresh vs navigation
    const lastIntroTime = sessionStorage.getItem('lastIntroTime');
    const currentTime = Date.now();
    
    // If no intro shown yet, or if it's been more than 2 seconds since last intro
    // (2 seconds accounts for React's double render in dev mode)
    if (!lastIntroTime || (currentTime - parseInt(lastIntroTime)) > 2000) {
      setShowIntro(true);
      sessionStorage.setItem('lastIntroTime', currentTime.toString());
    }
    
    // For development: You can add ?skip to URL to skip intro
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('skip') === 'true') {
      setShowIntro(false);
    }
  }, []);

  const handleProgressUpdate = (taskId: string, progress: number, status: string, data: any) => {
    // Handle progress updates from MyModels component
    // This function is passed to MyModels but currently just logs the updates
    console.log('Progress update:', { taskId, progress, status, data });
  };

  const handleIntroComplete = () => {
    setShowIntro(false);
    // Update the timestamp when intro completes
    sessionStorage.setItem('lastIntroTime', Date.now().toString());
  };

  // Show intro animation first
  if (showIntro) {
    return <IntroAnimation onComplete={handleIntroComplete} />;
  }
  
  if (!isAuthenticated) {
    return <Login />;
  }

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <Dashboard />;
      case 'libraries':
        return <Libraries />;
      case 'my-models':
        return user?.role !== 'viewer' ? <MyModels onProgressUpdate={handleProgressUpdate} /> : (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <p className="text-yellow-800">You don't have permission to access model calibration.</p>
          </div>
        );
      case 'profile':
        return <UserProfile />;
      case 'requests':
        return <Requests />;
      case 'reports':
        return <Reports />;
      case 'settings':
        return (
          <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600">Configure system preferences and parameters</p>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-500">Settings interface coming soon...</p>
            </div>
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <Sidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        onNewRequest={() => setShowNewRequestModal(true)}
        onUploadData={() => setShowUploadModal(true)}
        onShowUserGuide={() => setShowUserGuide(true)}
        onShowSupport={() => setShowSupport(true)}
      />
      
      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="p-8 flex-1 flex flex-col overflow-hidden">
          {renderContent()}
        </div>
      </main>

      {/* New Request Modal */}
      {showNewRequestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">New Model Request</h2>
              <button
                onClick={() => setShowNewRequestModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
            
            <form className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Model Type
                  </label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg">
                    <option>Compact Model</option>
                    <option>Behavioral Model</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Component Type
                  </label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg">
                    <option>NMOS Transistor</option>
                    <option>PMOS Transistor</option>
                    <option>Diode</option>
                    <option>Amplifier</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Technology Node
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., 28nm, 65nm"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg">
                    <option>High</option>
                    <option>Medium</option>
                    <option>Low</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reference Data
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg">
                  <option>Select existing dataset...</option>
                  <option>REF-MEAS-001: 28nm NMOS measurements</option>
                  <option>REF-SIM-015: 40nm PMOS simulation</option>
                  <option>Upload new data...</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  rows={4}
                  placeholder="Describe your requirements..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowNewRequestModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                  onClick={(e) => {
                    e.preventDefault();
                    alert('Request submitted successfully!');
                    setShowNewRequestModal(false);
                  }}
                >
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Upload Data Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Upload Reference Data</h2>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
            
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data Type
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg">
                  <option>Measurement Data</option>
                  <option>Simulation Data</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Device Information
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <input
                    type="text"
                    placeholder="Device Type (e.g., NMOS)"
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <input
                    type="text"
                    placeholder="Technology (e.g., 28nm)"
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  File Upload
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <input type="file" className="hidden" id="file-upload" accept=".csv,.json,.h5" />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <div className="text-gray-600">
                      <p className="mb-2">Drop files here or click to upload</p>
                      <p className="text-xs text-gray-500">Supported formats: CSV, JSON, HDF5</p>
                    </div>
                  </label>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  rows={3}
                  placeholder="Describe the data..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                  onClick={(e) => {
                    e.preventDefault();
                    alert('Data uploaded successfully!');
                    setShowUploadModal(false);
                  }}
                >
                  Upload
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* User Guide Modal */}
      <UserGuide isOpen={showUserGuide} onClose={() => setShowUserGuide(false)} />
      
      {/* Contact Support Modal */}
      <ContactSupport isOpen={showSupport} onClose={() => setShowSupport(false)} />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
