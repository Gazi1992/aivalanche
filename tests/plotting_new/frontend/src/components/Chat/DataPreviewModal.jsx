import React, { useState, useEffect } from 'react';
import './DataPreviewModal.css';

const DataPreviewModal = ({ isOpen, onClose, data }) => {
  const [activeTab, setActiveTab] = useState('overview');
  
  if (!isOpen || !data) return null;
  
  // Extract data from analysis structure
  const shape = data.shape || { rows: 0, columns: 0 };
  const columns = data.columns || [];
  const columnAnalysis = data.column_analysis || {};
  const qualityIssues = data.quality_issues || {};
  const correlations = data.correlations || {};
  const patterns = data.data_patterns || {};
  const suggestedPlots = data.suggested_plots || [];
  const sample = data.sample || [];
  
  // Prepare quality issues for display
  const getQualityIssues = () => {
    const issues = [];
    
    if (qualityIssues.missing_values) {
      const missing = qualityIssues.missing_values;
      if (missing.percentage && missing.percentage > 0) {
        issues.push({
          severity: missing.percentage > 10 ? 'high' : 'low',
          category: 'Missing Data',
          message: `${missing.percentage.toFixed(1)}% missing values across dataset`
        });
      }
      if (missing.columns && Object.keys(missing.columns).length > 0) {
        Object.entries(missing.columns).slice(0, 5).forEach(([col, count]) => {
          issues.push({
            severity: 'low',
            category: 'Missing Data',
            message: `Column "${col}": ${count} missing values`
          });
        });
      }
    }
    
    if (qualityIssues.outliers && Object.keys(qualityIssues.outliers).length > 0) {
      Object.entries(qualityIssues.outliers).slice(0, 3).forEach(([col, info]) => {
        issues.push({
          severity: 'medium',
          category: 'Outliers',
          message: `Column "${col}": ${info.count || 'Multiple'} outliers detected`
        });
      });
    }
    
    if (qualityIssues.duplicates && qualityIssues.duplicates > 0) {
      issues.push({
        severity: 'high',
        category: 'Duplicates',
        message: `${qualityIssues.duplicates} duplicate rows found`
      });
    }
    
    return issues;
  };
  
  // Get column type statistics
  const getColumnStats = () => {
    const stats = {
      numeric: 0,
      categorical: 0,
      temporal: 0,
      text: 0
    };
    
    Object.values(columnAnalysis).forEach(col => {
      const dataType = col.data_type;
      if (dataType?.includes('NUMERIC')) stats.numeric++;
      else if (dataType?.includes('CATEGORICAL')) stats.categorical++;
      else if (dataType?.includes('TEMPORAL')) stats.temporal++;
      else if (dataType?.includes('TEXT')) stats.text++;
    });
    
    return stats;
  };
  
  const columnStats = getColumnStats();
  const issues = getQualityIssues();
  
  return (
    <div className="data-preview-modal-overlay" onClick={onClose}>
      <div className="data-preview-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>📊 Data Analysis Report</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-tabs">
          <button 
            className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab ${activeTab === 'columns' ? 'active' : ''}`}
            onClick={() => setActiveTab('columns')}
          >
            Columns
          </button>
          <button 
            className={`tab ${activeTab === 'quality' ? 'active' : ''}`}
            onClick={() => setActiveTab('quality')}
          >
            Data Quality
          </button>
          <button 
            className={`tab ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('insights')}
          >
            Insights
          </button>
          <button 
            className={`tab ${activeTab === 'sample' ? 'active' : ''}`}
            onClick={() => setActiveTab('sample')}
          >
            Sample Data
          </button>
        </div>
        
        <div className="modal-content">
          {activeTab === 'overview' && (
            <div className="tab-content">
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-value">{shape[0] || shape.rows || 0}</div>
                  <div className="stat-label">Rows</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{shape[1] || shape.columns || columns.length}</div>
                  <div className="stat-label">Columns</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{columnStats.numeric}</div>
                  <div className="stat-label">Numeric</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{columnStats.categorical}</div>
                  <div className="stat-label">Categorical</div>
                </div>
              </div>
              
              {patterns && (
                <div className="patterns-section">
                  <h3>Detected Patterns</h3>
                  <ul>
                    {patterns.has_time_series && <li>✓ Time series data detected</li>}
                    {patterns.has_categorical && <li>✓ Categorical patterns found</li>}
                    {patterns.has_numerical && <li>✓ Numerical data suitable for statistics</li>}
                    {correlations.has_correlations && <li>✓ Strong correlations between columns</li>}
                  </ul>
                </div>
              )}
              
              {suggestedPlots.length > 0 && (
                <div className="suggestions-section">
                  <h3>Recommended Visualizations</h3>
                  <div className="suggestions-list">
                    {suggestedPlots.slice(0, 3).map((plot, idx) => (
                      <div key={idx} className="suggestion-item">
                        <span className="plot-type">{plot.plot_type?.replace('_', ' ')}</span>
                        <span className="plot-reason">{plot.reason}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'columns' && (
            <div className="tab-content">
              <div className="columns-table">
                <table>
                  <thead>
                    <tr>
                      <th>Column Name</th>
                      <th>Type</th>
                      <th>Non-Null</th>
                      <th>Unique</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(columnAnalysis).map(([colName, colInfo]) => (
                      <tr key={colName}>
                        <td className="column-name">{colName}</td>
                        <td>
                          <span className={`type-badge type-${colInfo.data_type?.toLowerCase().replace('_', '-')}`}>
                            {colInfo.data_type?.replace('_', ' ')}
                          </span>
                        </td>
                        <td>{colInfo.non_null_count || '-'}</td>
                        <td>{colInfo.unique_count || '-'}</td>
                        <td className="column-details">
                          {colInfo.statistics && (
                            <span className="detail-text">
                              {colInfo.statistics.mean !== undefined && 
                                `Mean: ${colInfo.statistics.mean.toFixed(2)}`}
                              {colInfo.statistics.min !== undefined && 
                                ` | Range: [${colInfo.statistics.min.toFixed(2)}, ${colInfo.statistics.max.toFixed(2)}]`}
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          
          {activeTab === 'quality' && (
            <div className="tab-content">
              {issues.length > 0 ? (
                <div className="quality-issues-list">
                  {issues.map((issue, idx) => (
                    <div key={idx} className={`quality-issue-item severity-${issue.severity}`}>
                      <span className="issue-icon">
                        {issue.severity === 'high' ? '⚠️' : 
                         issue.severity === 'medium' ? '⚡' : 'ℹ️'}
                      </span>
                      <div className="issue-content">
                        <span className="issue-category">{issue.category}</span>
                        <span className="issue-message">{issue.message}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-issues">
                  <span className="success-icon">✅</span>
                  <p>No significant data quality issues detected</p>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'insights' && (
            <div className="tab-content">
              <div className="insights-section">
                {correlations.strongest_correlations && correlations.strongest_correlations.length > 0 && (
                  <div className="insight-group">
                    <h3>Strong Correlations</h3>
                    {correlations.strongest_correlations.slice(0, 5).map((corr, idx) => (
                      <div key={idx} className="correlation-item">
                        <span className="correlation-pair">
                          {corr.column1} ↔ {corr.column2}
                        </span>
                        <span className={`correlation-value ${Math.abs(corr.correlation) > 0.7 ? 'strong' : ''}`}>
                          {corr.correlation.toFixed(3)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
                
                {patterns.trend_info && (
                  <div className="insight-group">
                    <h3>Trend Analysis</h3>
                    <p>{patterns.trend_info}</p>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {activeTab === 'sample' && (
            <div className="tab-content">
              {sample && sample.length > 0 ? (
                <div className="sample-data-table">
                  <table>
                    <thead>
                      <tr>
                        {Object.keys(sample[0]).map(col => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {sample.slice(0, 10).map((row, idx) => (
                        <tr key={idx}>
                          {Object.values(row).map((val, colIdx) => (
                            <td key={colIdx}>
                              {val !== null && val !== undefined ? 
                                (typeof val === 'number' ? val.toFixed(2) : String(val)) : 
                                <span className="null-value">null</span>}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {sample.length > 10 && (
                    <p className="sample-note">Showing first 10 rows of {sample.length}</p>
                  )}
                </div>
              ) : (
                <p>No sample data available</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DataPreviewModal;