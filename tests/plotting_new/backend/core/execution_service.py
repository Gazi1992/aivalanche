"""
Python Execution Service for Data Analysis and Visualization

This service provides a sandboxed environment for executing Python code
with built-in support for data analysis and Plotly visualizations.
"""

import sys
import io
import json
import traceback
import uuid
from typing import Dict, List, Any, Optional
from contextlib import redirect_stdout, redirect_stderr
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import logging
from pathlib import Path
from scipy import stats
from .plot_types import get_plot_capabilities, is_plot_editable

logger = logging.getLogger(__name__)


class PlotRegistry:
    """Registry for managing Plotly figures and their metadata."""
    
    def __init__(self):
        self.figures: Dict[str, Dict[str, Any]] = {}
        self.counter = 0
        
    def register(self, fig: Any, plot_id: Optional[str] = None,
                 editable_properties: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> str:
        """Register a Plotly figure or D3 config with metadata for edit pane integration."""
        if plot_id is None:
            plot_id = f"plot_{self.counter}"
            self.counter += 1
            
        # Check if this is a D3 visualization
        if isinstance(fig, dict) and fig.get('type') == 'd3':
            # Handle D3 visualization
            logger.info(f"Registering D3 visualization: {plot_id}")

            # Get capabilities for D3 plots
            capabilities = get_plot_capabilities('d3')

            # Initialize metadata if not provided
            if metadata is None:
                metadata = {}

            # Add capabilities to metadata
            metadata['plot_type'] = 'd3'
            metadata['capabilities'] = capabilities
            metadata['isEditable'] = capabilities.get('is_editable', False)

            self.figures[plot_id] = {
                'id': plot_id,
                'type': 'd3',
                'd3Config': fig.get('d3Config', {}),
                'metadata': metadata
            }

            return plot_id

        # Convert Plotly figure to dict for analysis
        fig_dict = json.loads(fig.to_json())
        layout = fig_dict.get('layout', {})

        # Initialize metadata if not provided
        if metadata is None:
            metadata = {}

        # Check if this is an animation (has frames)
        is_animation = False
        if hasattr(fig, 'frames') and fig.frames:
            is_animation = True
            metadata['isAnimation'] = True
            metadata['frameCount'] = len(fig.frames)
            # Include frames in the figure dict
            fig_dict['frames'] = json.loads(fig.to_json())['frames']
            logger.info(f"Detected animation with {len(fig.frames)} frames")
            
        # Auto-detect axis types and plot characteristics
        # Note: axis type is 'numeric' or 'category' (not 'linear' which is a scale)
        x_axis_type = 'numeric'  # Default to numeric
        y_axis_type = 'numeric'  # Default to numeric
        
        # Log what the layout contains for debugging
        logger.info(f"Plot {plot_id}: Layout xaxis type = {layout.get('xaxis', {}).get('type', 'not set')}")
        logger.info(f"Plot {plot_id}: Layout yaxis type = {layout.get('yaxis', {}).get('type', 'not set')}")
        
        # Check if layout already specifies categorical axes
        if layout.get('xaxis', {}).get('type') == 'category':
            x_axis_type = 'category'
        if layout.get('yaxis', {}).get('type') == 'category':
            y_axis_type = 'category'
        
        # Check if axes are categorical by examining data
        if fig_dict.get('data') and len(fig_dict['data']) > 0:
            first_trace = fig_dict['data'][0]
            plot_type = first_trace.get('type', 'scatter')
            logger.info(f"Plot {plot_id}: Detecting axis types for {plot_type} plot")
            
            # Check X axis for categorical data
            if 'x' in first_trace and first_trace['x']:
                x_data = first_trace['x']
                logger.info(f"Plot {plot_id}: X data type = {type(x_data)}, is dict = {isinstance(x_data, dict)}, is list = {isinstance(x_data, list)}")
                
                # Handle binary encoded numpy arrays (they appear as dicts with 'dtype' and 'bdata')
                if isinstance(x_data, dict) and 'dtype' in x_data:
                    # This is a binary-encoded numpy array - check the dtype
                    dtype = x_data['dtype']
                    logger.info(f"Plot {plot_id}: X axis dtype = {dtype}")
                    if dtype.startswith('f') or dtype.startswith('i'):
                        # Float or integer type - it's numeric
                        x_axis_type = 'numeric'
                        logger.info(f"Plot {plot_id}: X axis detected as numeric from dtype")
                    else:
                        # Other types might be categorical
                        x_axis_type = 'category'
                        logger.info(f"Plot {plot_id}: X axis detected as category from dtype")
                elif isinstance(x_data, list):
                    # Check if data is categorical
                    logger.info(f"Plot {plot_id}: X data is a list with {len(x_data)} items")
                    if len(x_data) > 0:
                        # Check first few items to understand data type
                        sample_items = x_data[:5]
                        logger.info(f"Plot {plot_id}: X data sample: {sample_items}")
                    
                    if all(isinstance(x, str) for x in x_data):
                        # All values are strings - check if they're numeric strings or categories
                        logger.info(f"Plot {plot_id}: X data contains all strings")
                        try:
                            # Try to convert to float - if it succeeds, they're numeric strings
                            [float(x) for x in x_data]
                            # Successfully converted - it's numeric data as strings
                            x_axis_type = 'numeric'
                            logger.info(f"Plot {plot_id}: X strings are numeric values")
                        except (ValueError, TypeError):
                            # Can't convert to numbers - it's categorical
                            x_axis_type = 'category'
                            logger.info(f"Plot {plot_id}: X strings are categorical")
                    else:
                        # Mixed types or all numbers - it's numeric
                        x_axis_type = 'numeric'
                        logger.info(f"Plot {plot_id}: X data is numeric (not all strings)")
                else:
                    # Default to numeric for unknown formats
                    x_axis_type = 'numeric'
                    logger.info(f"Plot {plot_id}: X data defaulting to numeric (unknown format)")
            else:
                logger.info(f"Plot {plot_id}: No X data found in trace, keeping default numeric")
            
            # Log final X axis type after detection
            logger.info(f"Plot {plot_id}: Final X axis type after detection = {x_axis_type}")
            
            # Check Y axis (less common to be categorical)
            if 'y' in first_trace and first_trace['y']:
                y_data = first_trace['y']
                
                # Handle binary encoded numpy arrays (they appear as dicts with 'dtype' and 'bdata')
                if isinstance(y_data, dict) and 'dtype' in y_data:
                    # This is a binary-encoded numpy array - check the dtype
                    if y_data['dtype'].startswith('f') or y_data['dtype'].startswith('i'):
                        # Float or integer type - it's numeric
                        y_axis_type = 'numeric'
                    else:
                        # Other types might be categorical
                        y_axis_type = 'category'
                elif isinstance(y_data, list):
                    # Check if data is categorical
                    if all(isinstance(y, str) for y in y_data):
                        # All values are strings - check if they're numeric strings or categories
                        try:
                            # Try to convert to float - if it succeeds, they're numeric strings
                            [float(y) for y in y_data]
                            # Successfully converted - it's numeric data as strings
                            y_axis_type = 'numeric'
                        except (ValueError, TypeError):
                            # Can't convert to numbers - it's categorical
                            y_axis_type = 'category'
                    else:
                        # Mixed types or all numbers - it's numeric
                        y_axis_type = 'numeric'
                else:
                    # Default to numeric for unknown formats
                    y_axis_type = 'numeric'
            else:
                logger.info(f"Plot {plot_id}: No Y data found in trace, keeping default numeric")
            
            # Log final Y axis type after detection
            logger.info(f"Plot {plot_id}: Final Y axis type after detection = {y_axis_type}")
            
            # Store plot type and capabilities
            metadata['plot_type'] = plot_type

            # Get capabilities for this plot type
            capabilities = get_plot_capabilities(plot_type)
            metadata['capabilities'] = capabilities
            metadata['isEditable'] = capabilities.get('is_editable', True)

            # Special handling for plots without traditional axes
            if plot_type in ['pie', 'sunburst', 'treemap', 'indicator', 'icicle']:
                metadata['hasAxes'] = False
            elif plot_type == 'parcoords':
                metadata['hasAxes'] = False
                metadata['isPcp'] = True
            elif plot_type == 'splom':
                metadata['hasAxes'] = False
                metadata['isSplom'] = True
            elif plot_type in ['scatterpolar', 'barpolar']:
                metadata['hasAxes'] = False
                metadata['isPolar'] = True
            elif plot_type in ['scatter3d', 'surface', 'mesh3d']:
                metadata['is3D'] = True
            elif plot_type == 'heatmap':
                metadata['isHeatmap'] = True
        
        # Log the axis types right before storing them
        logger.info(f"Plot {plot_id}: About to store axis types - X={x_axis_type}, Y={y_axis_type}")
        
        # Add axis type information to metadata only if not already provided
        if 'xAxisType' not in metadata:
            metadata['xAxisType'] = x_axis_type
            metadata['xAxisCategorical'] = (x_axis_type == 'category')
        else:
            # Use the provided axis type
            logger.info(f"Plot {plot_id}: Metadata already has xAxisType={metadata['xAxisType']}")
            metadata['xAxisCategorical'] = (metadata['xAxisType'] == 'category')
            
        if 'yAxisType' not in metadata:
            metadata['yAxisType'] = y_axis_type
            metadata['yAxisCategorical'] = (y_axis_type == 'category')
        else:
            # Use the provided axis type  
            logger.info(f"Plot {plot_id}: Metadata already has yAxisType={metadata['yAxisType']}")
            metadata['yAxisCategorical'] = (metadata['yAxisType'] == 'category')
        
        # Extract figure data for edit pane
        figure_data = {
            'id': plot_id,
            'figure': fig_dict,
            'editable_properties': editable_properties or ['all'],
            'metadata': metadata,
            'created_at': datetime.now().isoformat()
        }
        
        # Store additional metadata for edit pane
        if hasattr(fig, 'data') and len(fig.data) > 0:
            figure_data['metadata']['trace_count'] = len(fig.data)
            figure_data['metadata']['trace_types'] = [trace.type for trace in fig.data]
            
        self.figures[plot_id] = figure_data
        logger.info(f"Registered plot {plot_id} with axis types: X={metadata.get('xAxisType', 'unknown')}, Y={metadata.get('yAxisType', 'unknown')}")
        return plot_id
        
    def get(self, plot_id: str) -> Optional[Dict[str, Any]]:
        """Get a registered figure by ID."""
        return self.figures.get(plot_id)
        
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all registered figures."""
        return list(self.figures.values())
        
    def clear(self):
        """Clear all registered figures."""
        self.figures.clear()
        self.counter = 0


class ExecutionSession:
    """Manages a Python execution session with persistent state."""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.plot_registry = PlotRegistry()
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.namespace = self._create_namespace()  # Create namespace after initializing attributes
        
    def _create_namespace(self) -> Dict[str, Any]:
        """Create the execution namespace with pre-imported libraries and helpers."""

        # Add backend to path so demos can import from core
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parent.parent
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))

        # Helper functions that will be available in the execution environment
        def load_data(path: str, **kwargs) -> pd.DataFrame:
            """Load data from file path."""
            file_path = Path(path)
            if not file_path.is_absolute():
                # Assume relative to data directory
                file_path = Path('data') / file_path
                
            if file_path.suffix == '.csv':
                # Try UTF-8 first, then fallback to latin-1 for compatibility
                try:
                    df = pd.read_csv(file_path, encoding='utf-8', **kwargs)
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, encoding='latin-1', **kwargs)
            elif file_path.suffix in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, **kwargs)
            elif file_path.suffix == '.json':
                df = pd.read_json(file_path, **kwargs)
            else:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
                
            # Store in datasets for later reference
            self.datasets[file_path.stem] = df
            return df
            
        def register_plot(fig: Any, **kwargs) -> str:
            """Register a plot (Plotly or D3) with the plot registry."""
            return self.plot_registry.register(fig, **kwargs)

        def register_d3(d3_config: Dict, viz_id: str, metadata: Optional[Dict] = None) -> str:
            """Register a D3 visualization with the plot registry."""
            d3_figure = {
                'type': 'd3',
                'd3Config': d3_config,
                'metadata': metadata or {}
            }
            return self.plot_registry.register(d3_figure, plot_id=viz_id, metadata=metadata)
            
        def quick_plot(df: pd.DataFrame, x: str, y: str, 
                      plot_type: str = 'scatter', **kwargs) -> go.Figure:
            """Create a quick plot from dataframe columns."""
            if plot_type == 'scatter':
                fig = px.scatter(df, x=x, y=y, **kwargs)
            elif plot_type == 'line':
                fig = px.line(df, x=x, y=y, **kwargs)
            elif plot_type == 'bar':
                fig = px.bar(df, x=x, y=y, **kwargs)
            elif plot_type == 'histogram':
                fig = px.histogram(df, x=x, **kwargs)
            else:
                raise ValueError(f"Unsupported plot type: {plot_type}")
                
            # Auto-register the plot
            register_plot(fig)
            return fig
            
        def show_stats(df: pd.DataFrame, columns: Optional[List[str]] = None):
            """Display statistical summary of dataframe."""
            if columns:
                return df[columns].describe()
            return df.describe()
            
        def find_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.DataFrame:
            """Find outliers in a column using specified method."""
            if method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                return df[(df[column] < Q1 - 1.5 * IQR) | (df[column] > Q3 + 1.5 * IQR)]
            elif method == 'zscore':
                from scipy import stats
                z_scores = np.abs(stats.zscore(df[column]))
                return df[z_scores > 3]
            else:
                raise ValueError(f"Unknown outlier method: {method}")
        
        # Import D3 helpers
        from .d3_helpers import (
            create_d3_viz, d3_force_graph, d3_hierarchy, d3_custom, d3_animation,
            register_d3_visualization
        )

        # Create namespace with all available tools
        namespace = {
            # Data libraries
            'pd': pd,
            'np': np,

            # Plotting libraries
            'go': go,
            'px': px,
            'make_subplots': make_subplots,

            # Helper functions
            'load_data': load_data,
            'register_plot': register_plot,
            'register_d3': register_d3,
            'quick_plot': quick_plot,
            'show_stats': show_stats,
            'find_outliers': find_outliers,

            # D3 visualization helpers
            'create_d3_viz': create_d3_viz,
            'd3_force_graph': d3_force_graph,
            'd3_hierarchy': d3_hierarchy,
            'd3_custom': d3_custom,
            'd3_animation': d3_animation,
            'register_d3_visualization': register_d3_visualization,

            # Session data
            'datasets': self.datasets,
            
            # Python builtins we want to keep
            'print': print,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
        }
        
        return namespace
        
    def execute(self, code: str, timeout: Optional[int] = 30) -> Dict[str, Any]:
        """
        Execute Python code in the session namespace.
        
        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Dictionary containing execution results, output, and any registered plots
        """
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        result = {
            'session_id': self.session_id,
            'success': False,
            'output': '',
            'error': None,
            'plots': [],
            'datasets': list(self.datasets.keys()),
            'execution_time': None
        }
        
        start_time = datetime.now()
        
        try:
            # Clear any previous plots before executing new code  
            self.plot_registry.clear()
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Execute the code in our namespace
                exec(code, self.namespace)
                
            # Capture output
            result['output'] = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            if stderr_output:
                result['output'] += f"\n[stderr]:\n{stderr_output}"
                
            # Get all registered plots
            result['plots'] = self.plot_registry.get_all()
            logger.info(f"Returning {len(result['plots'])} plots: {[p['id'] for p in result['plots']]}")
            
            result['success'] = True
            
        except Exception as e:
            # Capture the error
            result['error'] = {
                'type': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc()
            }
            result['output'] = stdout_capture.getvalue()
            
        finally:
            result['execution_time'] = (datetime.now() - start_time).total_seconds()
            
            # Store in history
            self.execution_history.append({
                'code': code,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
        return result
        
    def clear_session(self):
        """Clear the session state."""
        self.namespace = self._create_namespace()
        self.plot_registry.clear()
        self.datasets.clear()
        self.execution_history.clear()
        
    def get_variables(self) -> Dict[str, str]:
        """Get a list of user-defined variables in the namespace."""
        # Filter out built-ins and imports
        excluded = {'pd', 'np', 'go', 'px', 'make_subplots', 'load_data', 
                   'register_plot', 'quick_plot', 'show_stats', 'find_outliers',
                   'datasets', '__builtins__'}
        
        variables = {}
        for name, value in self.namespace.items():
            if name not in excluded and not name.startswith('_'):
                try:
                    variables[name] = f"{type(value).__name__}: {str(value)[:100]}"
                except:
                    variables[name] = type(value).__name__
                    
        return variables


class ExecutionService:
    """Main service for managing execution sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, ExecutionSession] = {}
        
    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new execution session."""
        session = ExecutionSession(session_id)
        self.sessions[session.session_id] = session
        logger.info(f"Created session {session.session_id}")
        return session.session_id
        
    def get_session(self, session_id: str) -> Optional[ExecutionSession]:
        """Get an existing session."""
        return self.sessions.get(session_id)
        
    def execute_in_session(self, session_id: str, code: str) -> Dict[str, Any]:
        """Execute code in a specific session."""
        session = self.get_session(session_id)
        if not session:
            # Create new session if it doesn't exist
            session = ExecutionSession(session_id)
            self.sessions[session_id] = session
            
        return session.execute(code)
        
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            self.sessions[session_id].clear_session()
            del self.sessions[session_id]
            logger.info(f"Deleted session {session_id}")
            return True
        return False
        
    def list_sessions(self) -> List[str]:
        """List all active sessions."""
        return list(self.sessions.keys())


# Global service instance
execution_service = ExecutionService()