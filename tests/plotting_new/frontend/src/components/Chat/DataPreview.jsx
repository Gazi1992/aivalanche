import React, { useState } from 'react';
import './DataPreview.css';

const DataPreview = ({ data, compact = false }) => {
  const [expanded, setExpanded] = useState(!compact);
  
  if (!data) return null;
  
  const renderDataSummary = () => {
    if (data.shape) {
      return (
        <div className="data-summary">
          <div className="summary-item">
            <span className="summary-label">Rows:</span>
            <span className="summary-value">{data.shape.rows}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Columns:</span>
            <span className="summary-value">{data.shape.columns}</span>
          </div>
          {data.missing_percentage !== undefined && (
            <div className="summary-item">
              <span className="summary-label">Missing:</span>
              <span className="summary-value">{data.missing_percentage.toFixed(1)}%</span>
            </div>
          )}
        </div>
      );
    }
    return null;
  };
  
  const renderColumnInfo = () => {
    if (!data.columns || !expanded) return null;
    
    return (
      <div className="columns-info">
        <h4>Column Information</h4>
        <div className="columns-list">
          {data.columns.map((col, index) => (
            <div key={index} className="column-item">
              <span className="column-name">{col.name}</span>
              <span className="column-type">{col.type}</span>
              {col.unique_count && (
                <span className="column-unique">{col.unique_count} unique</span>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  const renderDataQuality = () => {
    if (!data.quality_issues || !expanded) return null;
    
    // Convert quality_issues object to array of issues
    const issues = [];
    
    // Check for missing values
    if (data.quality_issues.missing_values) {
      const missing = data.quality_issues.missing_values;
      if (missing.percentage && missing.percentage > 0) {
        issues.push({
          severity: missing.percentage > 10 ? 'high' : 'low',
          message: `${missing.percentage.toFixed(1)}% missing values across dataset`
        });
      }
      if (missing.columns && Object.keys(missing.columns).length > 0) {
        const cols = Object.keys(missing.columns).slice(0, 3).join(', ');
        issues.push({
          severity: 'low',
          message: `Missing values in columns: ${cols}`
        });
      }
    }
    
    // Check for outliers
    if (data.quality_issues.outliers && Object.keys(data.quality_issues.outliers).length > 0) {
      const outlierCols = Object.keys(data.quality_issues.outliers).slice(0, 3).join(', ');
      issues.push({
        severity: 'low',
        message: `Outliers detected in: ${outlierCols}`
      });
    }
    
    // Check for duplicates
    if (data.quality_issues.duplicates && data.quality_issues.duplicates > 0) {
      issues.push({
        severity: 'high',
        message: `${data.quality_issues.duplicates} duplicate rows found`
      });
    }
    
    if (issues.length === 0) return null;
    
    return (
      <div className="data-quality">
        <h4>Data Quality Issues</h4>
        <ul className="quality-issues">
          {issues.map((issue, index) => (
            <li key={index} className={`quality-issue ${issue.severity}`}>
              <span className="issue-icon">
                {issue.severity === 'high' ? '⚠️' : 'ℹ️'}
              </span>
              <span className="issue-text">{issue.message}</span>
            </li>
          ))}
        </ul>
      </div>
    );
  };
  
  const renderSampleData = () => {
    if (!data.sample || !expanded) return null;
    
    const headers = Object.keys(data.sample[0] || {});
    
    return (
      <div className="sample-data">
        <h4>Sample Data</h4>
        <div className="sample-table-wrapper">
          <table className="sample-table">
            <thead>
              <tr>
                {headers.map((header, index) => (
                  <th key={index}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.sample.slice(0, 5).map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {headers.map((header, cellIndex) => (
                    <td key={cellIndex}>
                      {row[header] !== null && row[header] !== undefined 
                        ? String(row[header]).substring(0, 50)
                        : <span className="null-value">null</span>
                      }
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };
  
  const renderStatistics = () => {
    if (!data.statistics || !expanded) return null;
    
    return (
      <div className="data-statistics">
        <h4>Statistics</h4>
        <div className="stats-grid">
          {Object.entries(data.statistics).map(([key, value]) => (
            <div key={key} className="stat-item">
              <span className="stat-label">{key.replace(/_/g, ' ')}:</span>
              <span className="stat-value">
                {typeof value === 'number' ? value.toFixed(2) : value}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  if (compact) {
    return (
      <div className="data-preview compact">
        <div className="preview-header" onClick={() => setExpanded(!expanded)}>
          <h3>📊 Data Preview</h3>
          <button className="expand-button">
            {expanded ? '▲' : '▼'}
          </button>
        </div>
        {renderDataSummary()}
        {expanded && (
          <div className="preview-details">
            {renderColumnInfo()}
            {renderDataQuality()}
            {renderStatistics()}
            {renderSampleData()}
          </div>
        )}
      </div>
    );
  }
  
  return (
    <div className="data-preview">
      <h3>📊 Data Overview</h3>
      {renderDataSummary()}
      {renderColumnInfo()}
      {renderDataQuality()}
      {renderStatistics()}
      {renderSampleData()}
    </div>
  );
};

export default DataPreview;