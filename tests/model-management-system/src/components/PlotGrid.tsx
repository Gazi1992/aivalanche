import React, { useState } from 'react';
import Plot from 'react-plotly.js';
import { Maximize2, Download, BarChart3, X } from 'lucide-react';

interface PlotData {
  pageId: string;
  pageName: string;
  datasetName?: string;
  xName: string;
  xUnit: string;
  yName: string;
  yUnit: string;
  curves: Array<{
    x: number[];
    y: number[];
    name: string;
    mode: 'lines' | 'markers' | 'lines+markers';
    type?: 'scatter' | 'bar';  // Added support for bar charts
    color?: string;
    lineWidth?: number;
    markerSize?: number;
    dash?: 'solid' | 'dot' | 'dash' | 'longdash' | 'dashdot' | 'longdashdot';  // Proper Plotly dash types
    showlegend?: boolean;  // Control legend visibility per curve
  }>;
}

interface PlotGridProps {
  plots: PlotData[];
  columns?: 1 | 2 | 3;
  onColumnsChange?: (columns: 1 | 2 | 3) => void;
  showColumnSelector?: boolean;
  title?: string;
  titleInfo?: React.ReactNode;
  emptyMessage?: string;
  emptySubMessage?: string;
  maxHeight?: string;
}

const PlotGrid: React.FC<PlotGridProps> = ({
  plots,
  columns = 2,
  onColumnsChange,
  showColumnSelector = true,
  title,
  titleInfo,
  emptyMessage = "No data to visualize",
  emptySubMessage = "Select data to plot",
  maxHeight = 'calc(100vh - 200px)'
}) => {
  const [yAxisScales, setYAxisScales] = useState<{ [key: string]: 'log' | 'linear' }>({});
  const [expandedPlot, setExpandedPlot] = useState<PlotData | null>(null);
  const [localColumns, setLocalColumns] = useState(columns);
  const [showLegends, setShowLegends] = useState<{ [key: string]: boolean }>({});

  const handleColumnsChange = (cols: 1 | 2 | 3) => {
    setLocalColumns(cols);
    onColumnsChange?.(cols);
  };

  // Automatically adjust columns based on number of plots
  const maxColumns = Math.min(plots.length, 3) as 1 | 2 | 3;
  const baseColumns = onColumnsChange ? columns : localColumns;
  const effectiveColumns = plots.length === 1 ? 1 : Math.min(baseColumns, maxColumns) as 1 | 2 | 3;
  const actualColumns = effectiveColumns;

  if (plots.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        <div className="text-center">
          <BarChart3 className="w-12 h-12 mx-auto mb-2" />
          <p className="text-sm">{emptyMessage}</p>
          <p className="text-xs mt-1">{emptySubMessage}</p>
        </div>
      </div>
    );
  }

  // Calculate plot height based on number of plots and columns
  const numPlots = plots.length;
  
  // Calculate actual number of rows based on plots and columns
  const actualRows = Math.ceil(numPlots / actualColumns);
  
  // Determine grid template rows based on number of rows
  let gridTemplateRows: string;
  let containerClass: string;
  
  if (actualRows === 1) {
    // Single row: fill container height
    gridTemplateRows = '1fr';
    containerClass = 'grid gap-3 h-full';
  } else if (actualRows === 2) {
    // Two rows: each takes 50% of container
    gridTemplateRows = 'repeat(2, minmax(0, 1fr))';
    containerClass = 'grid gap-3 h-full';
  } else {
    // Three or more rows: fixed height rows with scrolling
    // Each row gets a fixed height to fit 2 rows in viewport
    const rowHeight = 'minmax(300px, 1fr)';
    gridTemplateRows = `repeat(${actualRows}, ${rowHeight})`;
    containerClass = 'grid gap-3 overflow-y-auto pb-4';
  }
  
  // Determine grid template columns
  const gridTemplateColumns = actualColumns === 1 ? '1fr' : 
                              actualColumns === 2 ? '1fr 1fr' : 
                              '1fr 1fr 1fr';

  const renderPlot = (plot: PlotData) => {
    const defaultScale = 'linear'; // Always use linear scale by default
    const currentScale = yAxisScales[plot.pageId] || defaultScale;
    const showLegend = showLegends[plot.pageId] !== false; // Default to true

    const plotData = plot.curves.map((curve, idx) => {
      const plotType = curve.type || 'scatter';
      
      // Handle bar charts
      if (plotType === 'bar') {
        return {
          x: curve.x,
          y: curve.y,
          type: 'bar' as const,
          name: curve.name,
          showlegend: curve.showlegend !== undefined ? curve.showlegend : curve.name !== '',
          marker: {
            color: curve.color || `hsl(${idx * 360 / plot.curves.length}, 70%, 50%)`,
            line: {
              color: curve.color || `hsl(${idx * 360 / plot.curves.length}, 70%, 50%)`,
              width: 0.5
            }
          },
        };
      }

      // Handle scatter/line charts
      return {
        x: curve.x,
        y: curve.y,
        type: 'scatter' as const,
        mode: curve.mode,
        name: curve.name,
        showlegend: curve.showlegend !== undefined ? curve.showlegend : curve.name !== '',
        ...(curve.mode === 'lines' || curve.mode === 'lines+markers' ? {
          line: { 
            color: curve.color || `hsl(${idx * 360 / plot.curves.length}, 70%, 50%)`, 
            width: curve.lineWidth || 1.5,
            ...(curve.dash ? { dash: curve.dash } : {})
          }
        } : {}),
        ...(curve.mode === 'markers' || curve.mode === 'lines+markers' ? {
          marker: { 
            color: curve.color || `hsl(${idx * 360 / plot.curves.length}, 70%, 50%)`, 
            size: curve.markerSize || 4 
          }
        } : {})
      };
    });

    return (
      <Plot
        divId={`plot-${plot.pageId}`}
        data={plotData}
        layout={{
          autosize: true,
          margin: { t: 10, r: 20, b: 40, l: 60 },
          xaxis: { 
            title: { text: `${plot.xName} (${plot.xUnit || '-'})`, font: { size: 10 } },
            gridcolor: '#e0e0e0',
            tickfont: { size: 9 }
          },
          yaxis: { 
            title: { text: `${plot.yName} (${plot.yUnit || '-'})`, font: { size: 10 } }, 
            type: currentScale,
            gridcolor: '#e0e0e0',
            tickfont: { size: 9 }
          },
          showlegend: showLegend,
          legend: { 
            x: 0.02, 
            y: 0.98, 
            font: { size: 9 },
            bgcolor: 'rgba(255,255,255,0.9)',
            bordercolor: '#444',
            borderwidth: 1,
            xanchor: 'left',
            yanchor: 'top'
          },
          dragmode: 'zoom',
          plot_bgcolor: '#fafafa',
          // Add bargap for bar charts
          ...(plot.curves.some(c => c.type === 'bar') ? { bargap: 0.05 } : {})
        }}
        config={{ 
          displayModeBar: false,
          displaylogo: false,
          responsive: true,
          editable: true,
          edits: {
            legendPosition: true,
            legendText: false,
            titleText: false,
            axisTitleText: false,
            colorbarTitleText: false,
            annotationPosition: false,
            annotationTail: false,
            annotationText: false
          }
        }}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
        className="h-full"
      />
    );
  };

  return (
    <>
      {/* Header with column selector */}
      {(showColumnSelector || title || titleInfo) && (
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-4">
            {title && <h3 className="text-sm font-semibold">{title}</h3>}
            {titleInfo}
          </div>
          {showColumnSelector && plots.length > 1 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">Columns:</span>
            <div className="flex gap-1 bg-gray-100 rounded-lg p-0.5">
              {[1, 2, 3].filter(cols => cols <= Math.min(plots.length, 3)).map((cols) => (
                <button
                  key={cols}
                  onClick={() => handleColumnsChange(cols as 1 | 2 | 3)}
                  className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                    actualColumns === cols
                      ? 'bg-white text-purple-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {cols}
                </button>
              ))}
            </div>
          </div>
          )}
        </div>
      )}

      {/* Plot Grid Container */}
      <div 
        className="flex-1 flex flex-col overflow-hidden h-full"
        style={{ maxHeight }}
      >
        <div 
          className={containerClass}
          style={{ 
            gridTemplateColumns,
            gridTemplateRows,
            height: '100%'
          }}
        >
          {plots.map((plot) => {
            const currentScale = yAxisScales[plot.pageId] || 'linear'; // Always use linear scale by default
            const showLegend = showLegends[plot.pageId] !== false;

            return (
              <div 
                key={plot.pageId} 
                className="group relative border border-gray-200 rounded-lg p-2 flex flex-col h-full"
              >
                <div className="flex items-center justify-between mb-1 flex-shrink-0">
                  <div className="text-xs font-medium text-gray-700">
                    {plot.pageName}
                    {plot.datasetName && (
                      <span className="ml-2 text-gray-500">({plot.datasetName})</span>
                    )}
                  </div>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    <button
                      onClick={() => {
                        setShowLegends(prev => ({
                          ...prev,
                          [plot.pageId]: !(prev[plot.pageId] !== false)
                        }));
                      }}
                      className="p-1.5 bg-white/90 hover:bg-gray-100 rounded shadow-sm border border-gray-200"
                      title={showLegend ? 'Hide legend' : 'Show legend'}
                    >
                      <svg className="w-3.5 h-3.5" viewBox="0 0 16 16" fill="currentColor">
                        {showLegend ? (
                          // Eye open icon
                          <path d="M8 3C3 3 0 8 0 8s3 5 8 5 8-5 8-5-3-5-8-5zm0 8c-1.657 0-3-1.343-3-3s1.343-3 3-3 3 1.343 3 3-1.343 3-3 3zm0-5c-1.103 0-2 .897-2 2s.897 2 2 2 2-.897 2-2-.897-2-2-2z"/>
                        ) : (
                          // Eye closed icon
                          <path d="M13.354 2.646a.5.5 0 010 .708l-10 10a.5.5 0 01-.708-.708l10-10a.5.5 0 01.708 0zM8 3C3 3 0 8 0 8s1.5 2.5 4 3.5l1.5-1.5C4.5 9.5 4 8.5 4 8c0-1.657 1.343-3 3-3 .5 0 1 .15 1.5.4L10 4c-1-.6-2-1-2-1zm0 10c5 0 8-5 8-5s-1.5-2.5-4-3.5l-1.5 1.5c1 .5 1.5 1.5 1.5 2 0 1.657-1.343 3-3 3-.5 0-1-.15-1.5-.4L6 12c1 .6 2 1 2 1z"/>
                        )}
                      </svg>
                    </button>
                    <button
                      onClick={() => {
                        setYAxisScales(prev => ({
                          ...prev,
                          [plot.pageId]: currentScale === 'log' ? 'linear' : 'log'
                        }));
                      }}
                      className="p-1.5 bg-white/90 hover:bg-gray-100 rounded shadow-sm border border-gray-200"
                      title={`Switch to ${currentScale === 'log' ? 'linear' : 'logarithmic'} scale`}
                    >
                      <svg className="w-3.5 h-3.5" viewBox="0 0 16 16" fill="currentColor">
                        {currentScale === 'log' ? (
                          <path d="M2 13h12v1H2v-1zm0-3h2v2H2v-2zm3-2h2v4H5V8zm3-3h2v7H8V5zm3-3h2v10h-2V2z"/>
                        ) : (
                          <path d="M2 13h12v1H2v-1zm0-2h2v1H2v-1zm3-2h2v3H5V9zm3-2h2v5H8V7zm3-2h2v7h-2V5z"/>
                        )}
                      </svg>
                    </button>
                    <button
                      onClick={() => setExpandedPlot(plot)}
                      className="p-1.5 bg-white/90 hover:bg-gray-100 rounded shadow-sm border border-gray-200"
                      title="Expand plot"
                    >
                      <Maximize2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => {
                        const plotElement = document.getElementById(`plot-${plot.pageId}`);
                        if (plotElement) {
                          (window as any).Plotly.downloadImage(plotElement, {
                            format: 'png',
                            filename: plot.pageName || 'plot',
                            height: 500,
                            width: 700,
                            scale: 1
                          });
                        }
                      }}
                      className="p-1.5 bg-white/90 hover:bg-gray-100 rounded shadow-sm border border-gray-200"
                      title="Save as image"
                    >
                      <Download className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
                <div className="flex-1 relative" style={{ minHeight: '200px' }}>
                  {renderPlot(plot)}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Expanded Plot Modal */}
      {expandedPlot && (() => {
        const currentScale = yAxisScales[expandedPlot.pageId] || 'linear'; // Always use linear scale by default
        const showLegend = showLegends[expandedPlot.pageId] !== false;

        return (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <div className="bg-white rounded-lg w-full h-full max-w-7xl max-h-[90vh] flex flex-col">
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-gray-900">{expandedPlot.pageName}</h2>
                  {expandedPlot.datasetName && (
                    <p className="text-sm text-gray-500">{expandedPlot.datasetName}</p>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      setShowLegends(prev => ({
                        ...prev,
                        [expandedPlot.pageId]: !showLegend
                      }));
                    }}
                    className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded flex items-center gap-2 text-sm"
                  >
                    <svg className="w-4 h-4" viewBox="0 0 16 16" fill="currentColor">
                      {showLegend ? (
                        // Eye open icon
                        <path d="M8 3C3 3 0 8 0 8s3 5 8 5 8-5 8-5-3-5-8-5zm0 8c-1.657 0-3-1.343-3-3s1.343-3 3-3 3 1.343 3 3-1.343 3-3 3zm0-5c-1.103 0-2 .897-2 2s.897 2 2 2 2-.897 2-2-.897-2-2-2z"/>
                      ) : (
                        // Eye closed icon
                        <path d="M13.354 2.646a.5.5 0 010 .708l-10 10a.5.5 0 01-.708-.708l10-10a.5.5 0 01.708 0zM8 3C3 3 0 8 0 8s1.5 2.5 4 3.5l1.5-1.5C4.5 9.5 4 8.5 4 8c0-1.657 1.343-3 3-3 .5 0 1 .15 1.5.4L10 4c-1-.6-2-1-2-1zm0 10c5 0 8-5 8-5s-1.5-2.5-4-3.5l-1.5 1.5c1 .5 1.5 1.5 1.5 2 0 1.657-1.343 3-3 3-.5 0-1-.15-1.5-.4L6 12c1 .6 2 1 2 1z"/>
                      )}
                    </svg>
                    <span>{showLegend ? 'Hide Legend' : 'Show Legend'}</span>
                  </button>
                  <button
                    onClick={() => {
                      setYAxisScales(prev => ({
                        ...prev,
                        [expandedPlot.pageId]: currentScale === 'log' ? 'linear' : 'log'
                      }));
                    }}
                    className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded flex items-center gap-2 text-sm"
                  >
                    <svg className="w-4 h-4" viewBox="0 0 16 16" fill="currentColor">
                      {currentScale === 'log' ? (
                        <path d="M2 13h12v1H2v-1zm0-3h2v2H2v-2zm3-2h2v4H5V8zm3-3h2v7H8V5zm3-3h2v10h-2V2z"/>
                      ) : (
                        <path d="M2 13h12v1H2v-1zm0-2h2v1H2v-1zm3-2h2v3H5V9zm3-2h2v5H8V7zm3-2h2v7h-2V5z"/>
                      )}
                    </svg>
                    <span>{currentScale === 'log' ? 'Log Scale' : 'Linear Scale'}</span>
                  </button>
                  <button
                    onClick={() => {
                      const plotElement = document.getElementById(`expanded-plot-${expandedPlot.pageId}`);
                      if (plotElement) {
                        (window as any).Plotly.downloadImage(plotElement, {
                          format: 'png',
                          filename: expandedPlot.pageName || 'plot',
                          height: 1000,
                          width: 1400,
                          scale: 1
                        });
                      }
                    }}
                    className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded flex items-center gap-2 text-sm"
                  >
                    <Download className="w-4 h-4" />
                    Save Image
                  </button>
                  <button
                    onClick={() => setExpandedPlot(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
              <div className="flex-1 p-6 flex flex-col">
                <div id={`expanded-plot-${expandedPlot.pageId}`} className="flex-1" style={{ height: '100%' }}>
                  {renderPlot(expandedPlot)}
                </div>
              </div>
            </div>
          </div>
        );
      })()}
    </>
  );
};

export default PlotGrid;