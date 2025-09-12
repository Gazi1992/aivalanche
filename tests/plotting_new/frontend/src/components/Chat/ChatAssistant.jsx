import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import FileUpload from './FileUpload';
import DataPreviewModal from './DataPreviewModal';
import SuggestedActions from './SuggestedActions';
import MessageList from './MessageList';
import './ChatAssistant.css';

const ChatAssistant = ({ onConfigUpdate, onDataLoad, onClearPlots, onLoadDemo, isLoadingConfig }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "Hello! I'm your AI data visualization assistant. I can help you:\n\n• 📊 Analyze and visualize your data\n• 🔄 Transform and clean datasets\n• 📈 Create interactive dashboards\n• 💡 Discover insights and patterns\n\nGet started by uploading a data file or describing what you'd like to visualize!",
      timestamp: new Date(),
      suggestions: [
        { text: "Upload my file", action: "upload" },
        { text: "What can you do?", action: "help" }
      ]
    }
  ]);
  
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [currentData, setCurrentData] = useState(null);
  const [showDataPreview, setShowDataPreview] = useState(false);
  const [transformationHistory, setTransformationHistory] = useState([]);
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const inputRef = useRef(null);
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const handleSendMessage = async (text = null) => {
    const messageText = text || inputText.trim();
    if (!messageText) return;
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messageText,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsProcessing(true);
    
    try {
      // Send to backend
      const response = await axios.post('http://localhost:8000/api/chat', {
        message: messageText,
        current_config: null  // Could pass current config if needed
      });
      
      const data = response.data;
      
      // Create bot response
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.message || 'Processing your request...',
        timestamp: new Date(),
        responseType: data.type,
        data: data
      };
      
      // Add suggested actions based on response type
      if (data.type === 'data_analysis') {
        botMessage.suggestions = [
          { text: "View full analysis", action: "view_analysis" },
          { text: "Create visualization", action: "visualize" },
          { text: "Show data summary", action: "summary" },
          { text: "Apply transformations", action: "transform" }
        ];
        
        // Store analysis
        if (data.analysis) {
          setCurrentData(data.analysis);
        }
      } else if (data.type === 'need_data') {
        botMessage.suggestions = [
          { text: "Upload file", action: "upload" }
        ];
      } else if (data.type === 'transformation_complete') {
        botMessage.suggestions = [
          { text: "Visualize results", action: "visualize" },
          { text: "Apply more transformations", action: "transform" },
          { text: "Export data", action: "export" }
        ];
        
        // Add to transformation history
        if (data.transformations) {
          setTransformationHistory(prev => [...prev, ...data.transformations]);
        }
      }
      
      // Handle Python execution responses
      if (data.type === 'python_execution') {
        onConfigUpdate(data);  // Pass the entire response to handle Python execution
        
        botMessage.suggestions = [
          { text: "Modify plots", action: "modify" },
          { text: "Add more data", action: "upload" },
          { text: "Clear plots", action: "clear" }
        ];
        
        // Add execution output if available
        if (data.execution_output) {
          botMessage.executionOutput = data.execution_output;
        }
      }
      
      // Handle traditional config updates (fallback)
      else if (data.config && (data.type === 'config_new' || data.type === 'config_update' || data.type === 'config_with_analysis')) {
        onConfigUpdate(data);  // Pass the entire response object
        
        botMessage.suggestions = [
          { text: "Change theme", action: "theme" },
          { text: "Add another plot", action: "add_plot" },
          { text: "Modify layout", action: "layout" }
        ];
      }
      
      // Add data preview if available
      if (data.data_summary) {
        botMessage.dataPreview = data.data_summary;
      }
      
      setMessages(prev => [...prev, botMessage]);
      
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };
  
  const handleFileUpload = async (file) => {
    setShowFileUpload(false);
    
    // Add a message about the file
    const fileMessage = {
      id: Date.now(),
      type: 'user',
      content: `📎 Uploaded file: ${file.name}`,
      timestamp: new Date(),
      isFile: true
    };
    
    setMessages(prev => [...prev, fileMessage]);
    setIsProcessing(true);
    
    try {
      // Read file content - use different methods based on file type
      const fileExt = file.name.split('.').pop().toLowerCase();
      let fileContent;
      
      if (fileExt === 'csv' || fileExt === 'json' || fileExt === 'txt') {
        // Text files - read as text
        const reader = new FileReader();
        fileContent = await new Promise((resolve, reject) => {
          reader.onload = (e) => resolve(e.target.result);
          reader.onerror = reject;
          reader.readAsText(file);
        });
      } else {
        // Binary files (Excel, Parquet) - read as base64
        const reader = new FileReader();
        const arrayBuffer = await new Promise((resolve, reject) => {
          reader.onload = (e) => resolve(e.target.result);
          reader.onerror = reject;
          reader.readAsArrayBuffer(file);
        });
        // Convert to base64
        const bytes = new Uint8Array(arrayBuffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
          binary += String.fromCharCode(bytes[i]);
        }
        fileContent = btoa(binary);
      }
      
      // Send to backend for analysis
      const response = await axios.post('http://localhost:8000/api/upload-data', {
        filename: file.name,
        content: fileContent,
        file_type: file.name.split('.').pop().toLowerCase()
      });
      
      const data = response.data;
      
      // Create bot response with analysis
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.message || `Successfully loaded ${file.name}`,
        timestamp: new Date(),
        responseType: 'data_analysis',
        dataPreview: data.analysis,
        suggestions: [
          { text: "View full analysis", action: "view_analysis" },
          { text: "Create visualization", action: "visualize" },
          { text: "Show data summary", action: "summary" },
          { text: "Apply transformations", action: "transform" }
        ]
      };
      
      setMessages(prev => [...prev, botMessage]);
      
      if (data.analysis) {
        setCurrentData(data.analysis);
      }
      
      // If there's a config, update it
      if (data.config) {
        onConfigUpdate(data.config);
      }
      
    } catch (error) {
      console.error('Error uploading file:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: `Error uploading file: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };
  
  const handleSuggestedAction = (action) => {
    switch (action) {
      case 'upload':
        setShowFileUpload(true);
        break;
      case 'view_analysis':
        setShowDataPreview(true);
        break;
      case 'visualize':
        handleSendMessage('Create a visualization from the current data');
        break;
      case 'transform':
        handleSendMessage('What transformations would you like to apply?');
        break;
      case 'summary':
        handleSendMessage('Show me a summary of the data');
        break;
      case 'help':
        handleSendMessage('What can you help me with?');
        break;
      case 'theme':
        handleSendMessage('Change the theme to dark');
        break;
      case 'add_plot':
        handleSendMessage('Add another plot to the dashboard');
        break;
      case 'layout':
        handleSendMessage('Change to a 2x2 grid layout');
        break;
      case 'export':
        handleSendMessage('Export the transformed data');
        break;
      default:
        console.log('Unknown action:', action);
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  return (
    <div className="chat-assistant">
      <div className="chat-header">
        <div className="chat-title">
          <span className="chat-icon">🤖</span>
          <h2>AI Data Assistant</h2>
        </div>
        <div className="chat-status">
          {isProcessing && <span className="processing-indicator">Processing...</span>}
        </div>
      </div>
      
      <div className="chat-messages">
        <MessageList 
          messages={messages}
          onActionClick={handleSuggestedAction}
        />
        <div ref={messagesEndRef} />
      </div>
      
      {showFileUpload && (
        <FileUpload 
          onFileSelect={handleFileUpload}
          onCancel={() => setShowFileUpload(false)}
        />
      )}
      
      {currentData && (
        <div className="data-loaded-indicator">
          <span className="data-icon">📊</span>
          <span className="data-text">Data loaded</span>
          <button 
            className="view-data-button"
            onClick={() => setShowDataPreview(true)}
          >
            View Analysis
          </button>
        </div>
      )}
      
      <DataPreviewModal 
        isOpen={showDataPreview}
        onClose={() => setShowDataPreview(false)}
        data={currentData}
      />
      
      {transformationHistory.length > 0 && (
        <div className="transformation-history">
          <h4>Applied Transformations ({transformationHistory.length})</h4>
          <ul>
            {transformationHistory.slice(-3).map((t, i) => (
              <li key={i}>{t.type}: {t.reason || ''}</li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Quick Actions Bar */}
      <div className="quick-actions-bar">
        {onLoadDemo && (
          <button 
            className="quick-action-button"
            onClick={onLoadDemo}
            disabled={isLoadingConfig}
            title="Load demo plots with sample data"
            style={{
              opacity: isLoadingConfig ? 0.5 : 1,
              cursor: isLoadingConfig ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoadingConfig ? '⏳ Loading...' : '📊 Demo Plots'}
          </button>
        )}
        {onClearPlots && (
          <button 
            className="quick-action-button"
            onClick={onClearPlots}
            disabled={isLoadingConfig}
            title="Clear all plots"
            style={{
              opacity: isLoadingConfig ? 0.5 : 1,
              cursor: isLoadingConfig ? 'not-allowed' : 'pointer'
            }}
          >
            🗑️ Clear Plots
          </button>
        )}
      </div>
      
      <div className="chat-input-container">
        <button 
          className="attach-button"
          onClick={() => setShowFileUpload(true)}
          title="Upload file"
        >
          📎
        </button>
        
        <textarea
          ref={inputRef}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me anything about your data..."
          className="chat-input"
          disabled={isProcessing}
          rows={1}
        />
        
        <button 
          className="send-button"
          onClick={() => handleSendMessage()}
          disabled={!inputText.trim() || isProcessing}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatAssistant;