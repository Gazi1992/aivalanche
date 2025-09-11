import React, { useState, useRef } from 'react';
import './FileUpload.css';

const FileUpload = ({ onFileSelect, onCancel, acceptedFormats = '.csv,.json,.xlsx,.xls,.parquet' }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);
  
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };
  
  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };
  
  const handleFile = (file) => {
    // Validate file type
    const extension = file.name.split('.').pop().toLowerCase();
    const validExtensions = acceptedFormats.split(',').map(ext => ext.replace('.', ''));
    
    if (!validExtensions.includes(extension)) {
      alert(`Please select a valid file format: ${acceptedFormats}`);
      return;
    }
    
    setSelectedFile(file);
    onFileSelect(file);
  };
  
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };
  
  return (
    <div className="file-upload-overlay">
      <div className="file-upload-modal">
        <div className="file-upload-header">
          <h3>Upload Data File</h3>
          <button className="close-button" onClick={onCancel}>×</button>
        </div>
        
        <div 
          className={`file-upload-dropzone ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="upload-icon">📁</div>
          <p className="upload-text">
            {isDragging ? 'Drop file here...' : 'Drag & drop file here or click to browse'}
          </p>
          <p className="upload-formats">Supported formats: {acceptedFormats}</p>
          
          <input
            ref={fileInputRef}
            type="file"
            accept={acceptedFormats}
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </div>
        
        {selectedFile && (
          <div className="selected-file">
            <div className="file-info">
              <span className="file-name">{selectedFile.name}</span>
              <span className="file-size">{formatFileSize(selectedFile.size)}</span>
            </div>
          </div>
        )}
        
        <div className="file-upload-actions">
          <button className="cancel-button" onClick={onCancel}>Cancel</button>
          {selectedFile && (
            <button className="upload-button" onClick={() => onFileSelect(selectedFile)}>
              Process File
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileUpload;