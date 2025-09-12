import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import Plotly from 'plotly.js-dist-min';
import { PlayIcon, StopIcon, ClearIcon, EditIcon, ExpandIcon } from './icons';
import EditPaneSimple from './EditPane/EditPaneSimple.jsx';

const PythonExecutor = ({ sessionId, onSessionChange }) => {
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [plots, setPlots] = useState([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentSession, setCurrentSession] = useState(sessionId || 'default');
  const [variables, setVariables] = useState({});
  const [executionTime, setExecutionTime] = useState(null);
  const [editingPlot, setEditingPlot] = useState(null);
  const [editPaneOpen, setEditPaneOpen] = useState(false);
  const [expandedPlot, setExpandedPlot] = useState(null);
  const codeEditorRef = useRef(null);

  // Render plots when they update
  useEffect(() => {
    if (plots && plots.length > 0) {
      plots.forEach((plot, index) => {
        const plotDiv = document.getElementById(`python-plot-${plot.id || index}`);
        if (plotDiv && plot.figure) {
          // Apply theme-aware layout
          const layout = {
            ...plot.figure.layout,
            autosize: true,
            margin: { l: 50, r: 50, t: 50, b: 50 },
            paper_bgcolor: plot.figure.layout?.paper_bgcolor || getComputedStyle(document.body).getPropertyValue('--plot-paper-bg').trim(),
            plot_bgcolor: plot.figure.layout?.plot_bgcolor || getComputedStyle(document.body).getPropertyValue('--plot-bg').trim(),
            font: {
              color: getComputedStyle(document.body).getPropertyValue('--plot-text').trim(),
              ...plot.figure.layout?.font
            }
          };

          const config = {
            responsive: true,
            displayModeBar: false,  // Disable default Plotly toolbar
            displaylogo: false,
            scrollZoom: true,
            editable: false
          };

          Plotly.newPlot(plotDiv, plot.figure.data, layout, config);
        }
      });
    }

    // Cleanup
    return () => {
      if (plots && plots.length > 0) {
        plots.forEach((plot, index) => {
          const plotDiv = document.getElementById(`python-plot-${plot.id || index}`);
          if (plotDiv) {
            Plotly.purge(plotDiv);
          }
        });
      }
    };
  }, [plots]);

  // Render expanded plot
  useEffect(() => {
    if (expandedPlot) {
      const plotDiv = document.getElementById('expanded-plot');
      if (plotDiv && expandedPlot.figure) {
        const layout = {
          ...expandedPlot.figure.layout,
          autosize: true,
          paper_bgcolor: expandedPlot.figure.layout?.paper_bgcolor || getComputedStyle(document.body).getPropertyValue('--plot-paper-bg').trim(),
          plot_bgcolor: expandedPlot.figure.layout?.plot_bgcolor || getComputedStyle(document.body).getPropertyValue('--plot-bg').trim(),
          font: {
            color: getComputedStyle(document.body).getPropertyValue('--plot-text').trim(),
            ...expandedPlot.figure.layout?.font
          }
        };

        const config = {
          responsive: true,
          displayModeBar: true,  // Show toolbar for expanded view
          displaylogo: false,
          scrollZoom: true
        };

        Plotly.newPlot(plotDiv, expandedPlot.figure.data, layout, config);
      }
    }

    return () => {
      if (expandedPlot) {
        const plotDiv = document.getElementById('expanded-plot');
        if (plotDiv) {
          Plotly.purge(plotDiv);
        }
      }
    };
  }, [expandedPlot]);

  // Sample code snippets for quick start - focused on demo plots
  const sampleSnippets = {
    'Demo Plots': `# Create multiple demo plots
import numpy as np

# Generate sample data
x = np.linspace(0, 10, 100)
y1 = np.sin(x) + np.random.normal(0, 0.1, 100)
y2 = np.cos(x) + np.random.normal(0, 0.1, 100)
y3 = np.sin(x) * np.exp(-x/10)

# Create line plot
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=x, y=y1, mode='lines', name='Sin Wave', line=dict(color='blue', width=2)))
fig1.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='Cos Wave', line=dict(color='red', width=2)))
fig1.update_layout(title='Trigonometric Functions', xaxis_title='X', yaxis_title='Y')
register_plot(fig1, metadata={'description': 'Sine and Cosine waves with noise'})

# Create scatter plot
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=x, y=y3, mode='markers+lines', name='Damped Sine',
                         marker=dict(size=5, color=x, colorscale='Viridis')))
fig2.update_layout(title='Damped Oscillation', xaxis_title='Time', yaxis_title='Amplitude')
register_plot(fig2, metadata={'description': 'Exponentially damped sine wave'})

# Create histogram
data = np.random.normal(100, 15, 1000)
fig3 = go.Figure(data=[go.Histogram(x=data, nbinsx=30, marker_color='green')])
fig3.update_layout(title='Normal Distribution', xaxis_title='Value', yaxis_title='Frequency')
register_plot(fig3, metadata={'description': 'Random normal distribution'})

print("3 demo plots created successfully!")`,

    'Interactive 3D': `# Create 3D surface plot
import numpy as np

# Generate mesh grid
x = np.linspace(-5, 5, 50)
y = np.linspace(-5, 5, 50)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

# Create 3D surface
fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z, colorscale='Viridis')])
fig.update_layout(
    title='3D Surface: Ripple Effect',
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    ),
    height=600
)
register_plot(fig, metadata={'description': 'Interactive 3D surface plot'})
print("3D plot created! Use mouse to rotate and zoom.")`,

    'Time Series': `# Simulate time series data
import numpy as np
from datetime import datetime, timedelta

# Generate time series data
start_time = datetime.now()
times = [start_time + timedelta(seconds=i) for i in range(100)]
values = np.cumsum(np.random.randn(100)) + 50

# Create animated line chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=times, y=values,
    mode='lines+markers',
    name='Stock Price',
    line=dict(color='blue', width=2),
    marker=dict(size=4)
))

# Add range slider
fig.update_xaxes(rangeslider_visible=True)
fig.update_layout(
    title='Time Series with Range Slider',
    xaxis_title='Time',
    yaxis_title='Value',
    hovermode='x unified'
)
register_plot(fig, metadata={'description': 'Interactive time series with range slider'})
print("Time series plot created with range slider!")`,

    'Statistical': `# Create statistical plots
import numpy as np

# Generate data for different groups
np.random.seed(42)
group_a = np.random.normal(100, 10, 200)
group_b = np.random.normal(130, 15, 200)
group_c = np.random.normal(90, 20, 200)

# Create box plot
fig1 = go.Figure()
fig1.add_trace(go.Box(y=group_a, name='Group A', marker_color='lightblue'))
fig1.add_trace(go.Box(y=group_b, name='Group B', marker_color='lightgreen'))
fig1.add_trace(go.Box(y=group_c, name='Group C', marker_color='lightcoral'))
fig1.update_layout(title='Distribution Comparison', yaxis_title='Values')
register_plot(fig1, metadata={'description': 'Box plot comparing three groups'})

# Create violin plot
fig2 = go.Figure()
fig2.add_trace(go.Violin(y=group_a, name='Group A', box_visible=True, meanline_visible=True))
fig2.add_trace(go.Violin(y=group_b, name='Group B', box_visible=True, meanline_visible=True))
fig2.add_trace(go.Violin(y=group_c, name='Group C', box_visible=True, meanline_visible=True))
fig2.update_layout(title='Distribution Shape Analysis', yaxis_title='Values')
register_plot(fig2, metadata={'description': 'Violin plot with box and mean'})

print("Statistical plots created!")`
  };

  const executeCode = async () => {
    if (!code.trim()) return;
    
    setIsExecuting(true);
    setOutput('');
    setPlots([]);
    setExecutionTime(null);

    try {
      const response = await axios.post('http://localhost:8000/api/python/execute', {
        session_id: currentSession,
        code: code
      });

      const result = response.data;
      
      // Update output
      if (result.output) {
        setOutput(result.output);
      }
      
      // Handle error
      if (result.error) {
        setOutput(prev => prev + '\n[ERROR]\n' + result.error.message);
      }
      
      // Update plots
      if (result.plots && result.plots.length > 0) {
        setPlots(result.plots);
      }
      
      // Update variables (if endpoint provides them)
      if (result.variables) {
        setVariables(result.variables);
      }
      
      // Show execution time
      if (result.execution_time) {
        setExecutionTime(result.execution_time);
      }
      
    } catch (error) {
      console.error('Execution error:', error);
      setOutput(`Execution failed: ${error.message}`);
    } finally {
      setIsExecuting(false);
    }
  };

  const clearSession = async () => {
    try {
      await axios.delete(`http://localhost:8000/api/python/session/${currentSession}`);
      setCode('');
      setOutput('');
      setPlots([]);
      setVariables({});
      setExecutionTime(null);
    } catch (error) {
      console.error('Failed to clear session:', error);
    }
  };

  const insertSnippet = (snippet) => {
    setCode(snippet);
    codeEditorRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    // Ctrl/Cmd + Enter to execute
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      executeCode();
    }
    
    // Tab for indentation
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const newCode = code.substring(0, start) + '    ' + code.substring(end);
      setCode(newCode);
      // Set cursor position after the tab
      setTimeout(() => {
        e.target.selectionStart = e.target.selectionEnd = start + 4;
      }, 0);
    }
  };

  const handleEditPlot = (plot, index) => {
    setEditingPlot({ ...plot, index });
    setEditPaneOpen(true);
  };

  const handleUpdatePlot = (updatedFigure) => {
    const newPlots = [...plots];
    if (editingPlot && editingPlot.index !== undefined) {
      newPlots[editingPlot.index] = {
        ...newPlots[editingPlot.index],
        figure: updatedFigure
      };
      setPlots(newPlots);
    }
  };

  // Auto-load demo on mount
  useEffect(() => {
    if (!code) {
      insertSnippet(sampleSnippets['Demo Plots']);
    }
  }, []);

  return (
    <div className="python-executor">
      <div className="executor-header">
        <h3>Python Code Execution</h3>
        <div className="session-info">
          Session: <span className="session-id">{currentSession}</span>
        </div>
      </div>

      <div className="snippets-bar">
        <span className="snippets-label">Demo Code:</span>
        {Object.entries(sampleSnippets).map(([name, snippet]) => (
          <button
            key={name}
            className="snippet-btn"
            onClick={() => insertSnippet(snippet)}
            title="Click to load code"
          >
            {name}
          </button>
        ))}
      </div>

      <div className="code-editor-container">
        <textarea
          ref={codeEditorRef}
          className="code-editor"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="# Enter Python code here...
# Available libraries: pandas (pd), numpy (np), plotly.graph_objects (go), plotly.express (px)
# 
# Key functions:
#   register_plot(fig) - Display a Plotly figure
#   load_data(path) - Load CSV/Excel/JSON files
#   quick_plot(df, x, y, plot_type) - Create quick plots
#   show_stats(df) - Display statistics
#   find_outliers(df, column) - Detect outliers
#
# Try the demo buttons above for examples!
# Press Ctrl+Enter to execute"
          spellCheck={false}
          disabled={isExecuting}
        />
      </div>

      <div className="executor-controls">
        <button
          className="control-btn execute"
          onClick={executeCode}
          disabled={isExecuting || !code.trim()}
        >
          <PlayIcon size={16} />
          {isExecuting ? 'Executing...' : 'Execute (Ctrl+Enter)'}
        </button>
        <button
          className="control-btn clear"
          onClick={clearSession}
          disabled={isExecuting}
        >
          <ClearIcon size={16} />
          Clear Session
        </button>
        {executionTime && (
          <span className="execution-time">
            Executed in {executionTime.toFixed(3)}s
          </span>
        )}
      </div>

      {output && (
        <div className="output-container">
          <h4>Output</h4>
          <pre className="output-text">{output}</pre>
        </div>
      )}

      {plots.length > 0 && (
        <div className="plots-container">
          <h4>Visualizations ({plots.length})</h4>
          <div className="plots-grid">
            {plots.map((plot, index) => (
              <div key={plot.id || index} className="plot-container">
                <div className="plot-buttons">
                  <button 
                    className="edit-btn" 
                    onClick={() => handleEditPlot(plot, index)}
                    title="Edit plot"
                  >
                    <EditIcon size={16} />
                  </button>
                  {plots.length > 1 && (
                    <button 
                      className="zoom-btn" 
                      onClick={() => setExpandedPlot(plot)}
                      title="Expand plot"
                    >
                      <ExpandIcon size={16} />
                    </button>
                  )}
                </div>
                {plot.metadata?.description && (
                  <div className="plot-description">{plot.metadata.description}</div>
                )}
                <div 
                  id={`python-plot-${plot.id || index}`}
                  style={{ width: '100%', height: '400px' }}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {Object.keys(variables).length > 0 && (
        <div className="variables-container">
          <h4>Variables</h4>
          <div className="variables-list">
            {Object.entries(variables).map(([name, info]) => (
              <div key={name} className="variable-item">
                <span className="var-name">{name}</span>
                <span className="var-info">{info}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Edit Pane */}
      <EditPaneSimple
        isOpen={editPaneOpen}
        onClose={() => {
          setEditPaneOpen(false);
          setEditingPlot(null);
        }}
        plotData={editingPlot?.figure}
        onUpdate={handleUpdatePlot}
      />

      {/* Expanded Plot Overlay */}
      {expandedPlot && (
        <div className="plot-overlay" onClick={() => setExpandedPlot(null)}>
          <div className="plot-overlay-inner" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setExpandedPlot(null)}>×</button>
            <div id="expanded-plot" style={{ width: '100%', height: '100%' }} />
          </div>
        </div>
      )}

      <style jsx>{`
        .python-executor {
          display: flex;
          flex-direction: column;
          height: 100%;
          background: var(--bg-secondary);
          border-radius: 8px;
          padding: 1rem;
        }

        .executor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .executor-header h3 {
          margin: 0;
          color: var(--text-primary);
        }

        .session-info {
          color: var(--text-secondary);
          font-size: 0.9rem;
        }

        .session-id {
          font-family: monospace;
          background: var(--bg-primary);
          padding: 2px 8px;
          border-radius: 4px;
        }

        .snippets-bar {
          display: flex;
          gap: 0.5rem;
          align-items: center;
          margin-bottom: 0.5rem;
          padding: 0.5rem;
          background: var(--bg-primary);
          border-radius: 4px;
        }

        .snippets-label {
          color: var(--text-secondary);
          font-size: 0.85rem;
        }

        .snippet-btn {
          padding: 4px 12px;
          background: var(--primary-color);
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.85rem;
          cursor: pointer;
          transition: opacity 0.2s;
        }

        .snippet-btn:hover {
          opacity: 0.8;
        }

        .code-editor-container {
          flex: 1;
          min-height: 200px;
          margin-bottom: 1rem;
        }

        .code-editor {
          width: 100%;
          height: 100%;
          padding: 1rem;
          font-family: 'Consolas', 'Monaco', monospace;
          font-size: 13px;
          background: var(--bg-primary);
          color: var(--text-primary);
          border: 1px solid var(--border-color);
          border-radius: 4px;
          resize: vertical;
        }

        .code-editor:focus {
          outline: none;
          border-color: var(--primary-color);
        }

        .executor-controls {
          display: flex;
          gap: 1rem;
          align-items: center;
          margin-bottom: 1rem;
        }

        .control-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: opacity 0.2s;
        }

        .control-btn.execute {
          background: var(--success-color, #10b981);
          color: white;
        }

        .control-btn.clear {
          background: var(--danger-color, #ef4444);
          color: white;
        }

        .control-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .execution-time {
          color: var(--text-secondary);
          font-size: 0.85rem;
          margin-left: auto;
        }

        .output-container,
        .plots-container,
        .variables-container {
          margin-top: 1rem;
          padding: 1rem;
          background: var(--bg-primary);
          border-radius: 4px;
        }

        .output-container h4,
        .plots-container h4,
        .variables-container h4 {
          margin: 0 0 0.5rem 0;
          color: var(--text-primary);
        }

        .output-text {
          margin: 0;
          padding: 0.5rem;
          background: var(--bg-secondary);
          border-radius: 4px;
          font-family: monospace;
          font-size: 12px;
          color: var(--text-primary);
          white-space: pre-wrap;
          max-height: 300px;
          overflow-y: auto;
        }

        .plots-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
          gap: 1rem;
        }

        .plot-container {
          background: var(--card-background-color);
          border-radius: 8px;
          padding: 1rem;
          border: 1px solid var(--border-color);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          position: relative;
        }

        .plot-buttons {
          position: absolute;
          top: 8px;
          right: 8px;
          display: flex;
          gap: 4px;
          z-index: 10;
        }

        .edit-btn,
        .zoom-btn {
          padding: 6px;
          background: rgba(255, 255, 255, 0.9);
          border: 1px solid var(--border-color);
          border-radius: 4px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .edit-btn:hover,
        .zoom-btn:hover {
          background: var(--primary-color);
          color: white;
          transform: scale(1.1);
        }

        .plot-description {
          margin-bottom: 0.5rem;
          color: var(--text-secondary);
          font-size: 0.9rem;
        }

        .variables-list {
          display: grid;
          gap: 0.25rem;
        }

        .variable-item {
          display: flex;
          gap: 1rem;
          padding: 4px 8px;
          background: var(--bg-secondary);
          border-radius: 3px;
          font-family: monospace;
          font-size: 12px;
        }

        .var-name {
          font-weight: bold;
          color: var(--primary-color);
        }

        .var-info {
          color: var(--text-secondary);
        }

        .plot-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          background: rgba(0, 0, 0, 0.7);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .plot-overlay-inner {
          background: var(--card-background-color);
          padding: 10px;
          border-radius: 8px;
          width: 90vw;
          height: 90vh;
          display: flex;
          flex-direction: column;
          position: relative;
        }

        .close-btn {
          position: absolute;
          top: 10px;
          right: 10px;
          background: none;
          border: none;
          color: var(--text-color);
          font-size: 2rem;
          cursor: pointer;
          z-index: 1001;
        }
      `}</style>
    </div>
  );
};

export default PythonExecutor;