import React, { useMemo, useState } from 'react';
import './TableView.css';
import { decodeBinaryData } from '../../utils/binaryDecoder';
import { DownloadIcon } from '../icons';

const TableView = ({ figure, isOpen, onClose }) => {
  const [selectedDataset, setSelectedDataset] = useState(0);
  
  const tableData = useMemo(() => {
    if (!figure) return null;
    
    // First check if we have dataframe data in metadata
    if (figure.metadata && figure.metadata.datasets) {
      const datasets = Object.entries(figure.metadata.datasets);
      if (datasets.length > 0) {
        // If multiple datasets (like in histogram), combine them
        if (datasets.length > 1) {
          // Combine all datasets into one view
          const allData = [];
          const allColumns = new Set(['Dataset']);
          
          // Collect all unique columns
          datasets.forEach(([name, info]) => {
            info.columns.forEach(col => allColumns.add(col));
          });
          
          // Add data from each dataset
          datasets.forEach(([name, info]) => {
            info.data.forEach(row => {
              const newRow = { Dataset: name };
              allColumns.forEach(col => {
                if (col !== 'Dataset') {
                  newRow[col] = row[col] !== undefined ? row[col] : null;
                }
              });
              allData.push(newRow);
            });
          });
          
          return {
            type: 'dataframe',
            multiple: true,
            datasets: datasets.map(([name, info]) => ({
              name,
              columns: info.columns,
              data: info.data,
              totalRows: info.totalRows,
              truncated: info.truncated
            })),
            columns: Array.from(allColumns),
            data: allData,
            totalRows: allData.length,
            truncated: datasets.some(([, info]) => info.truncated)
          };
        } else {
          // Single dataset
          const [datasetName, datasetInfo] = datasets[selectedDataset] || datasets[0];
          return {
            type: 'dataframe',
            multiple: false,
            name: datasetName,
            columns: datasetInfo.columns,
            data: datasetInfo.data,
            totalRows: datasetInfo.totalRows,
            truncated: datasetInfo.truncated
          };
        }
      }
    }
    
    // Fallback to trace data if no dataframe available
    // Check both figure.figure.data and figure.data for compatibility
    const figureData = (figure.figure && figure.figure.data) || figure.data;
    if (figureData && figureData.length > 0) {
      // Combine all traces into a single table
      const allRows = [];
      const traces = figureData;
      
      // Decode binary data for all traces first
      const decodedTraces = traces.map(trace => ({
        ...trace,
        x: decodeBinaryData(trace.x),
        y: decodeBinaryData(trace.y),
        z: trace.z ? decodeBinaryData(trace.z) : undefined,
        marker: trace.marker ? {
          ...trace.marker,
          color: decodeBinaryData(trace.marker.color)
        } : trace.marker
      }));
      
      // Find the maximum length across all traces
      let maxLength = 0;
      decodedTraces.forEach(trace => {
        const xLen = trace.x ? trace.x.length : 0;
        const yLen = trace.y ? trace.y.length : 0;

        // Handle special plot types
        let specialLen = 0;
        if (trace.type === 'pie' && trace.labels) {
          specialLen = trace.labels.length;
        } else if (trace.type === 'scatterpolar' && trace.r) {
          specialLen = trace.r.length;
        } else if (trace.type === 'sankey') {
          const nodeLen = trace.node && trace.node.label ? trace.node.label.length : 0;
          const linkLen = trace.link && trace.link.source ? trace.link.source.length : 0;
          specialLen = Math.max(nodeLen, linkLen);
        }

        maxLength = Math.max(maxLength, xLen, yLen, specialLen);
      });
      
      // Build combined rows
      for (let i = 0; i < maxLength; i++) {
        const row = { index: i + 1 };

        decodedTraces.forEach((trace, traceIndex) => {
          const traceName = trace.name || `Trace ${traceIndex + 1}`;

          if (trace.x && i < trace.x.length) {
            row[`${traceName}_X`] = trace.x[i];
          }

          if (trace.y && i < trace.y.length) {
            row[`${traceName}_Y`] = trace.y[i];
          }

          if (trace.z && i < trace.z.length) {
            row[`${traceName}_Z`] = trace.z[i];
          }

          // Handle pie charts
          if (trace.type === 'pie' && trace.labels && trace.values) {
            if (i < trace.labels.length) {
              row[`${traceName}_Label`] = trace.labels[i];
              row[`${traceName}_Value`] = trace.values[i];
            }
          }

          // Handle radar/polar charts
          if (trace.type === 'scatterpolar' && trace.r && trace.theta) {
            if (i < trace.r.length) {
              row[`${traceName}_Category`] = trace.theta[i];
              row[`${traceName}_Value`] = trace.r[i];
            }
          }

          // Handle Sankey diagrams - create a more readable format
          if (trace.type === 'sankey') {
            // For Sankey, we'll create a different row structure
            if (trace.link && i < trace.link.source.length) {
              row['Flow_Source'] = trace.node.label[trace.link.source[i]];
              row['Flow_Target'] = trace.node.label[trace.link.target[i]];
              row['Flow_Value'] = trace.link.value[i];
            }
          }
        });

        allRows.push(row);
      }
      
      // Extract column names
      const columns = allRows.length > 0 ? Object.keys(allRows[0]).filter(key => key !== 'index') : [];
      
      return {
        type: 'traces',
        columns,
        data: allRows,
        totalRows: allRows.length,
        truncated: false
      };
    }
    
    return null;
  }, [figure]);
  
  const exportToCSV = () => {
    if (!tableData || !tableData.data || tableData.data.length === 0) return;
    
    const headers = tableData.columns;
    const csvContent = [
      headers.join(','),
      ...tableData.data.map(row => 
        headers.map(header => {
          const value = tableData.type === 'dataframe' ? row[header] : (row[header] !== undefined ? row[header] : '');
          // Handle null/undefined
          if (value === null || value === undefined) return '';
          // Escape quotes and wrap in quotes if contains comma or quotes
          const stringValue = String(value);
          if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
            return `"${stringValue.replace(/"/g, '""')}"`;
          }
          return stringValue;
        }).join(',')
      )
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${figure.id || figure.metadata?.title || 'plot'}_data.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };
  
  const formatCellValue = (value) => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'number') {
      // Format numbers with appropriate precision
      if (Number.isInteger(value)) return value.toString();
      return value.toFixed(4);
    }
    return String(value);
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="table-view-overlay" onClick={onClose}>
      <div className="table-view-container" onClick={(e) => e.stopPropagation()}>
        <div className="table-view-header">
          <h3>
            {figure.metadata?.title || figure.id || 'Plot Data'} 
            {figure.id && <span style={{ opacity: 0.6, fontSize: '0.9em', marginLeft: '8px' }}>({figure.id})</span>}
          </h3>
          <div className="table-view-info">
            {tableData && tableData.type === 'traces' && (
              <span className="data-source-notice">
                Showing plot trace data (dataframe not available)
              </span>
            )}
            {tableData && tableData.truncated && (
              <span className="truncation-notice">
                Showing first 1000 of {tableData.totalRows} rows
              </span>
            )}
          </div>
          <div className="table-view-actions">
            <button className="export-btn" onClick={exportToCSV} title="Export CSV">
              <DownloadIcon size={16} />
            </button>
            <button className="close-btn" onClick={onClose}>
              ×
            </button>
          </div>
        </div>
        
        <div className="table-view-content">
          {tableData && tableData.data && tableData.data.length > 0 ? (
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    {tableData.type === 'traces' || tableData.type === 'dataframe' ? (
                      <th className="row-number-header">#</th>
                    ) : null}
                    {tableData.columns.map(col => (
                      <th key={col}>{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tableData.data.map((row, index) => (
                    <tr key={index}>
                      {tableData.type === 'traces' ? (
                        <td className="row-number">{row.index}</td>
                      ) : tableData.type === 'dataframe' ? (
                        <td className="row-number">{index + 1}</td>
                      ) : null}
                      {tableData.columns.map(col => (
                        <td key={col}>
                          {formatCellValue(tableData.type === 'traces' ? row[col] : row[col])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="no-data">No data available</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TableView;