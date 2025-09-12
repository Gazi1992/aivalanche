"""
Enhanced AI Service: Orchestrates data analysis, transformation, and visualization
"""
import json
import logging
import os
from typing import Dict, List, Any, Optional, Tuple
import google.generativeai as genai
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from backend.core.data.data_analyzer import DataAnalyzer, DataType, PlotType
from backend.core.data.data_processor import DataProcessor
from backend.core.data_handler import load_dataset
from backend.core.ai.visualization_prompts import VISUALIZATION_SYSTEM_PROMPT, get_plot_config_template
from backend.core.execution_service import execution_service

logger = logging.getLogger(__name__)

# Set up LLM conversation logger
llm_logger = logging.getLogger('llm_conversations')
llm_handler = logging.FileHandler('logs/llm_conversations.log', mode='a', encoding='utf-8')
llm_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
llm_logger.addHandler(llm_handler)
llm_logger.setLevel(logging.INFO)

# Python Code Generation System Prompt
PYTHON_VIZ_SYSTEM_PROMPT = """
You are an expert data visualization assistant. Your task is to generate Python code that creates Plotly visualizations based on user requests and data analysis.

## CRITICAL RULES FOR CODE GENERATION:

1. **ALWAYS use the available helper functions** like load_data(), register_plot(), quick_plot()
2. **Data loading** should use load_data('filename.csv') which handles the data directory automatically
3. **Plot registration** must use register_plot(fig, plot_id='unique_id', metadata={}) for each plot
4. **Code must be complete and executable** without imports (pd, np, go, px are available)
5. **Use meaningful plot IDs** that describe the visualization

## AVAILABLE FUNCTIONS AND VARIABLES:

### Data Functions:
- load_data(path) -> DataFrame: Load data from file (CSV, Excel, JSON supported)
- datasets: Dict of cached datasets
- show_stats(df, columns=None): Display statistical summary
- find_outliers(df, column, method='iqr'): Find outliers in data

### Plotting Functions:
- register_plot(fig, plot_id=None, metadata=None): Register a plot for display
- quick_plot(df, x, y, plot_type='scatter', **kwargs): Create quick plots
- go: Plotly graph objects module
- px: Plotly express module
- make_subplots: Create subplot layouts

### Standard Libraries:
- pd: pandas for data manipulation
- np: numpy for numerical operations

## PLOT CREATION PATTERNS:

### Basic Scatter Plot:
```python
# Load and analyze data
df = load_data('data.csv')
print(f"Loaded {len(df)} rows with columns: {list(df.columns)}")

# Create scatter plot
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['x_column'], 
    y=df['y_column'],
    mode='markers',
    name='Data Points'
))
fig.update_layout(
    title='Scatter Plot Analysis',
    xaxis_title='X Variable',
    yaxis_title='Y Variable'
)

# Register the plot
register_plot(fig, plot_id='scatter_analysis', 
              metadata={'title': 'Scatter Plot', 'description': 'Analysis of X vs Y relationship'})
```

### Time Series Plot:
```python
df = load_data('time_series.csv')

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['time'], 
    y=df['value'],
    mode='lines',
    name='Time Series'
))
fig.update_layout(
    title='Time Series Analysis',
    xaxis_title='Time',
    yaxis_title='Value'
)

register_plot(fig, plot_id='time_series', 
              metadata={'title': 'Time Series', 'description': 'Temporal data analysis'})
```

### Multiple Plots Dashboard:
```python
df = load_data('dataset.csv')

# Plot 1: Distribution
fig1 = go.Figure()
fig1.add_trace(go.Histogram(x=df['column1'], nbinsx=30))
fig1.update_layout(title='Distribution Analysis')
register_plot(fig1, plot_id='distribution', metadata={'title': 'Distribution'})

# Plot 2: Correlation
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df['column1'], y=df['column2'], mode='markers'))
fig2.update_layout(title='Correlation Analysis')
register_plot(fig2, plot_id='correlation', metadata={'title': 'Correlation'})
```

### Advanced Analysis:
```python
df = load_data('complex_data.csv')

# Statistical summary
stats = show_stats(df)
print("Statistical Summary:")
print(stats)

# Outlier detection
outliers = find_outliers(df, 'value_column')
print(f"Found {len(outliers)} outliers")

# Create visualization with outliers highlighted
fig = go.Figure()
# Normal points
normal_data = df[~df.index.isin(outliers.index)]
fig.add_trace(go.Scatter(
    x=normal_data['x'], y=normal_data['y'],
    mode='markers', name='Normal'
))
# Outliers
fig.add_trace(go.Scatter(
    x=outliers['x'], y=outliers['y'],
    mode='markers', name='Outliers', 
    marker=dict(color='red', size=10)
))

register_plot(fig, plot_id='outlier_analysis')
```

## IMPORTANT GUIDELINES:

1. **Always load data first** using load_data() function
2. **Print useful information** about the data (shape, columns, summary stats)
3. **Create meaningful titles and labels** based on actual column names
4. **Use register_plot()** for every figure you want to display
5. **Handle missing data** appropriately (dropna(), fillna())
6. **Use appropriate plot types** based on data characteristics
7. **Add informative metadata** to help users understand the visualization

## CODE STRUCTURE:

1. Load data and print basic info
2. Perform any data analysis or preprocessing
3. Create visualization(s)
4. Register each plot with descriptive metadata
5. Print summary of what was created

Always generate **complete, executable Python code** that will create beautiful, informative visualizations.
"""

class AIService:
    """Enhanced AI service with data processing capabilities"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI service with Gemini and data processing components"""
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            logger.warning("AI Service initialized without Gemini API key")
            
        self.data_analyzer = DataAnalyzer()
        self.data_processor = DataProcessor()
        self.conversation_history = []
        self.data_cache = {}  # Cache loaded and processed data
        
        logger.info("Enhanced AI service initialized")
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user message with intelligent routing
        
        Args:
            message: User's message
            context: Optional context including current config, data, etc.
            
        Returns:
            Response with type, message, and optional config/data
        """
        # Log the incoming message
        llm_logger.info(f"{'='*60}")
        llm_logger.info(f"USER MESSAGE: {message}")
        if context:
            llm_logger.info(f"CONTEXT: {json.dumps(context, indent=2)[:500]}...")  # Truncate large context
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Check if message mentions a data file
        file_mention = self._extract_file_mention(message)
        
        response = None
        if file_mention:
            # Load and analyze the data
            llm_logger.info(f"DETECTED: Data file request for '{file_mention}'")
            response = self._handle_data_request(message, file_mention, context)
        
        # Check if it's a summary request
        elif self._is_summary_request(message):
            llm_logger.info("DETECTED: Summary request")
            response = self._handle_summary_request(message, context)
        
        # Check if it's a visualization request
        elif self._is_visualization_request(message):
            llm_logger.info("DETECTED: Visualization request")
            response = self._handle_visualization_request(message, context)
        
        # Check if it's a transformation request
        elif self._is_transformation_request(message):
            llm_logger.info("DETECTED: Transformation request")
            response = self._handle_transformation_request(message, context)
        
        # Default to general chat
        else:
            llm_logger.info("DETECTED: General chat")
            response = self._handle_general_chat(message, context)
        
        # Log the response
        self._log_response(response)
        return response
    
    def _extract_file_mention(self, message: str) -> Optional[str]:
        """Extract file path or name from message"""
        # Look for common file patterns
        import re
        
        # Match file paths with extensions
        patterns = [
            r'["\']?([a-zA-Z0-9_\-/\\]+\.(csv|xlsx?|json|parquet|tsv))["\']?',
            r'file[:\s]+([a-zA-Z0-9_\-/\\]+)',
            r'data[:\s]+([a-zA-Z0-9_\-/\\]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Check if message contains known data files
        data_dir = Path("data")
        if data_dir.exists():
            for file in data_dir.glob("**/*"):
                if file.is_file() and file.stem in message:
                    return str(file)
        
        return None
    
    def _is_visualization_request(self, message: str) -> bool:
        """Check if message is requesting visualization"""
        message_lower = message.lower()
        
        # Exclude summary requests
        if 'summary' in message_lower or 'summarize' in message_lower:
            return False
            
        # Check for visualization keywords
        viz_keywords = [
            'plot', 'chart', 'graph', 'visualiz',
            'histogram', 'scatter', 'line', 'bar', 'heatmap',
            'dashboard', 'figure', 'diagram'
        ]
        
        # Also check for phrases that indicate visualization
        viz_phrases = [
            'show.*chart', 'show.*plot', 'show.*graph',
            'display.*chart', 'display.*plot', 'display.*graph',
            'create.*visualization', 'make.*plot', 'draw.*chart'
        ]
        
        # Check keywords
        if any(keyword in message_lower for keyword in viz_keywords):
            return True
            
        # Check phrases with regex
        import re
        for phrase in viz_phrases:
            if re.search(phrase, message_lower):
                return True
                
        return False
    
    def _is_summary_request(self, message: str) -> bool:
        """Check if message is requesting data summary"""
        summary_keywords = [
            'summary', 'summarize', 'describe', 'overview',
            'statistics', 'stats', 'info about', 'tell me about'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in summary_keywords)
    
    def _is_transformation_request(self, message: str) -> bool:
        """Check if message is requesting data transformation"""
        transform_keywords = [
            'calculate', 'compute', 'transform', 'convert', 'aggregate',
            'group', 'filter', 'clean', 'fill', 'missing', 'outlier',
            'normalize', 'scale', 'pivot', 'melt', 'merge', 'join'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in transform_keywords)
    
    def _handle_data_request(self, message: str, file_path: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle request involving data file"""
        try:
            # Load the data
            df = self._load_data(file_path)
            
            if df is None:
                return {
                    "type": "error",
                    "message": f"Could not load file: {file_path}"
                }
            
            # Analyze the data
            analysis = self.data_analyzer.analyze_dataframe(df, file_path)
            
            # Cache the data
            self.data_cache[file_path] = {
                "df": df,
                "analysis": analysis
            }
            
            # Generate response based on analysis
            response = self._generate_data_analysis_response(analysis, file_path)
            
            # If user wants visualization, create config
            if self._is_visualization_request(message):
                config = self._generate_config_from_analysis(analysis, df, file_path)
                response["config"] = config
                response["type"] = "config_with_analysis"
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling data request: {e}")
            return {
                "type": "error",
                "message": f"Error processing data: {str(e)}"
            }
    
    def _handle_summary_request(self, message: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle data summary request"""
        try:
            # Check if we have cached data
            if not self.data_cache:
                return {
                    "type": "need_data",
                    "message": "Please load a data file first. You can upload a file or specify a file path."
                }
            
            # Get the most recent data
            file_path, cache_data = list(self.data_cache.items())[-1]
            df = cache_data["df"]
            analysis = cache_data.get("analysis", {})
            
            # Build comprehensive summary
            summary_parts = []
            
            # Basic info
            summary_parts.append(f"📊 **Data Summary for {file_path}**\n")
            summary_parts.append(f"• Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            summary_parts.append(f"• Columns: {', '.join(df.columns[:10])}{'...' if len(df.columns) > 10 else ''}")
            
            # Data types
            if analysis and "column_analysis" in analysis:
                col_analysis = analysis["column_analysis"]
                numeric_cols = [col for col, info in col_analysis.items() if 'NUMERIC' in str(info.get("data_type", ""))]
                categorical_cols = [col for col, info in col_analysis.items() if 'CATEGORICAL' in str(info.get("data_type", ""))]
                temporal_cols = [col for col, info in col_analysis.items() if 'TEMPORAL' in str(info.get("data_type", ""))]
                
                summary_parts.append("\n**Column Types:**")
                if numeric_cols:
                    summary_parts.append(f"• Numeric ({len(numeric_cols)}): {', '.join(numeric_cols[:5])}{'...' if len(numeric_cols) > 5 else ''}")
                if categorical_cols:
                    summary_parts.append(f"• Categorical ({len(categorical_cols)}): {', '.join(categorical_cols[:5])}{'...' if len(categorical_cols) > 5 else ''}")
                if temporal_cols:
                    summary_parts.append(f"• Temporal ({len(temporal_cols)}): {', '.join(temporal_cols[:5])}{'...' if len(temporal_cols) > 5 else ''}")
            
            # Quality issues
            if analysis and "quality_issues" in analysis:
                quality = analysis["quality_issues"]
                if quality.get("missing_values"):
                    missing_pct = quality["missing_values"].get("percentage", 0)
                    if missing_pct > 0:
                        summary_parts.append(f"\n**Data Quality:**")
                        summary_parts.append(f"• Missing values: {missing_pct:.1f}%")
                        if quality["missing_values"].get("columns"):
                            cols_with_missing = list(quality["missing_values"]["columns"].keys())[:3]
                            summary_parts.append(f"• Columns with missing data: {', '.join(cols_with_missing)}")
            
            # Statistics for numeric columns
            numeric_stats = []
            for col in df.select_dtypes(include=[np.number]).columns[:3]:  # First 3 numeric columns
                stats = df[col].describe()
                numeric_stats.append(f"• {col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}")
            
            if numeric_stats:
                summary_parts.append("\n**Key Statistics:**")
                summary_parts.extend(numeric_stats)
            
            # Patterns detected
            if analysis and "data_patterns" in analysis:
                patterns = analysis["data_patterns"]
                pattern_notes = []
                if patterns.get("has_time_series"):
                    pattern_notes.append("• Time series data detected")
                if patterns.get("has_categorical"):
                    pattern_notes.append("• Categorical patterns found")
                if analysis.get("correlations", {}).get("has_correlations"):
                    pattern_notes.append("• Strong correlations detected between columns")
                
                if pattern_notes:
                    summary_parts.append("\n**Patterns Detected:**")
                    summary_parts.extend(pattern_notes)
            
            # Sample data
            sample_data = df.head(3).to_dict('records')
            
            return {
                "type": "data_summary",
                "message": "\n".join(summary_parts),
                "data_summary": {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "sample": sample_data,
                    "dtypes": df.dtypes.astype(str).to_dict()
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling summary request: {e}")
            return {
                "type": "error",
                "message": f"Error generating summary: {str(e)}"
            }
    
    def _handle_visualization_request(self, message: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle visualization request by generating and executing Python code"""
        try:
            # Check if we have cached data
            if self.data_cache:
                # Use the most recent data
                file_path, cache_data = list(self.data_cache.items())[-1]
                df = cache_data["df"]
                analysis = cache_data.get("analysis", {})
                
                # If analysis is missing, generate it
                if not analysis:
                    analysis = self.data_analyzer.analyze_dataframe(df, file_path)
                    cache_data["analysis"] = analysis
                
                # Generate Python code based on request
                python_code = self._generate_python_code_from_request(message, analysis, df, file_path)
                
                if python_code:
                    # Execute the Python code
                    session_id = "ai_generated"  # Use a consistent session for AI-generated code
                    result = execution_service.execute_in_session(session_id, python_code)
                    
                    if result['success'] and result['plots']:
                        # Return the execution result with plots
                        return {
                            "type": "python_execution",
                            "message": f"I've created {len(result['plots'])} visualization{'s' if len(result['plots']) > 1 else ''} based on your request.",
                            "code": python_code,
                            "execution_result": result,
                            "session_id": session_id
                        }
                    else:
                        # Execution failed, return error
                        error_msg = result.get('error', {}).get('message', 'Unknown error')
                        return {
                            "type": "error",
                            "message": f"Error executing visualization code: {error_msg}",
                            "code": python_code,
                            "execution_result": result
                        }
                else:
                    return {
                        "type": "error",
                        "message": "Could not generate visualization code for your request."
                    }
            
            # No data loaded, ask for data
            return {
                "type": "need_data",
                "message": "Please provide a data file first. You can upload a file using the 📎 button or describe which file to load."
            }
            
        except Exception as e:
            logger.error(f"Error handling visualization request: {e}")
            return {
                "type": "error",
                "message": f"Error creating visualization: {str(e)}"
            }
    
    def _handle_transformation_request(self, message: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle data transformation request"""
        try:
            # Check if we have cached data
            if not self.data_cache:
                return {
                    "type": "need_data",
                    "message": "Please load a data file first before applying transformations."
                }
            
            # Get the most recent data
            file_path, cache_data = list(self.data_cache.items())[-1]
            df = cache_data["df"]
            
            # Parse transformation from message
            transformations = self._parse_transformations_from_message(message, df)
            
            if not transformations:
                return {
                    "type": "error",
                    "message": "I couldn't understand the transformation you want. Please be more specific."
                }
            
            # Apply transformations
            df_transformed = self.data_processor.apply_transformations(df, transformations)
            
            # Re-analyze transformed data
            analysis_new = self.data_analyzer.analyze_dataframe(df_transformed)
            
            # Update cache
            transformed_path = f"{file_path}_transformed"
            self.data_cache[transformed_path] = {
                "df": df_transformed,
                "analysis": analysis_new
            }
            
            # Generate response
            return {
                "type": "transformation_complete",
                "message": f"Applied {len(transformations)} transformation(s). The data now has {df_transformed.shape[0]} rows and {df_transformed.shape[1]} columns.",
                "transformations": transformations,
                "data_summary": {
                    "shape": df_transformed.shape,
                    "columns": list(df_transformed.columns),
                    "sample": df_transformed.head(5).to_dict('records')
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling transformation request: {e}")
            return {
                "type": "error",
                "message": f"Error applying transformation: {str(e)}"
            }
    
    def _handle_general_chat(self, message: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle general conversation"""
        if not self.model:
            return {
                "type": "chat",
                "message": "AI chat is not available. Please configure the Gemini API key."
            }
        
        try:
            # Build context from conversation history
            context_str = self._build_conversation_context()
            
            prompt = f"""
            You are a helpful data visualization assistant. You can help users:
            1. Load and analyze data files
            2. Create visualizations (plots, charts, dashboards)
            3. Transform and clean data
            4. Understand patterns and insights in their data
            
            {context_str}
            
            User: {message}
            
            Respond helpfully and concisely. If they're asking about capabilities, mention you can:
            - Automatically analyze data and suggest best visualizations
            - Perform calculations and transformations
            - Handle messy data with missing values and outliers
            """
            
            llm_logger.info(f"CALLING GEMINI API with prompt length: {len(prompt)} chars")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            llm_logger.info(f"GEMINI RESPONSE: {response_text[:500]}...")
            
            # Add to history
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return {
                "type": "chat",
                "message": response_text
            }
            
        except Exception as e:
            logger.error(f"Error in general chat: {e}")
            return {
                "type": "error",
                "message": "I had trouble processing your message. Please try again."
            }
    
    def _load_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load data from file"""
        try:
            # Try different base paths
            possible_paths = [
                file_path,
                f".temp/{file_path}",
                f"data/{file_path}",
                f"../data/{file_path}",
                f"../../data/{file_path}"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    # Use the existing data handler
                    df = load_dataset(os.path.basename(path))
                    logger.info(f"Loaded data from {path}: shape {df.shape}")
                    return df
            
            # Try to load directly with pandas
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            else:
                return None
                
            logger.info(f"Loaded data from {file_path}: shape {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            return None
    
    def _generate_data_analysis_response(self, analysis: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Generate response describing data analysis"""
        shape = analysis["shape"]
        columns = analysis["columns"]
        patterns = analysis["data_patterns"]
        quality = analysis["quality_issues"]
        suggestions = analysis["suggested_plots"]
        
        # Build response message
        message_parts = [
            f"I've analyzed the data from {os.path.basename(file_path)}:",
            f"- Shape: {shape[0]} rows × {shape[1]} columns",
            f"- Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}"
        ]
        
        # Add data type summary
        col_analysis = analysis["column_analysis"]
        numeric_cols = sum(1 for c in col_analysis.values() if 'NUMERIC' in str(c["data_type"]))
        categorical_cols = sum(1 for c in col_analysis.values() if 'CATEGORICAL' in str(c["data_type"]))
        temporal_cols = sum(1 for c in col_analysis.values() if 'TEMPORAL' in str(c["data_type"]))
        
        if numeric_cols:
            message_parts.append(f"- {numeric_cols} numeric column(s)")
        if categorical_cols:
            message_parts.append(f"- {categorical_cols} categorical column(s)")
        if temporal_cols:
            message_parts.append(f"- {temporal_cols} temporal column(s)")
        
        # Add quality issues
        if quality["missing_values"]:
            missing_pct = quality["missing_values"]["percentage"]
            message_parts.append(f"- Missing values: {missing_pct:.1f}%")
        
        # Add patterns
        if patterns["has_time_series"]:
            message_parts.append("- Time series data detected")
        if analysis["correlations"]["has_correlations"]:
            message_parts.append("- Strong correlations found between columns")
        
        # Add suggestions
        if suggestions:
            message_parts.append(f"\nI suggest creating:")
            for i, sugg in enumerate(suggestions[:3], 1):
                message_parts.append(f"{i}. {sugg['plot_type'].replace('_', ' ').title()} - {sugg['reason']}")
        
        return {
            "type": "data_analysis",
            "message": "\n".join(message_parts),
            "analysis": analysis
        }
    
    def _generate_config_from_analysis(self, analysis: Dict[str, Any], df: pd.DataFrame, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate visualization config from data analysis"""
        suggestions = analysis["suggested_plots"]
        
        # Determine the data source
        if file_path:
            # Use just the filename, not the full path
            source = Path(file_path).name
        else:
            # Try to find the file in cache
            for cached_path, cache_data in self.data_cache.items():
                if cache_data.get("df") is df:
                    source = Path(cached_path).name
                    break
            else:
                source = "processed_data"  # Fallback
        
        if not suggestions:
            # Default to simple scatter plot
            numeric_cols = [col for col, info in analysis["column_analysis"].items()
                          if 'NUMERIC' in str(info["data_type"])]
            
            if len(numeric_cols) >= 2:
                suggestions = [{
                    "plot_type": "scatter",
                    "config": {
                        "x_column": numeric_cols[0],
                        "y_column": numeric_cols[1],
                        "title": f"{numeric_cols[0]} vs {numeric_cols[1]}"
                    }
                }]
            else:
                suggestions = [{
                    "plot_type": "histogram",
                    "config": {
                        "column": numeric_cols[0] if numeric_cols else df.columns[0],
                        "title": f"Distribution of {numeric_cols[0] if numeric_cols else df.columns[0]}"
                    }
                }]
        
        # Build config
        config = {
            "app_title": "Data Analysis Dashboard",
            "theme": "light",
            "grid_layout": {
                "rows": min(2, len(suggestions)),
                "cols": min(2, (len(suggestions) + 1) // 2)
            },
            "figures": []
        }
        
        # Add suggested plots
        for i, suggestion in enumerate(suggestions[:4]):  # Limit to 4 plots
            plot_config = suggestion.get("config", {})
            plot_type = suggestion["plot_type"]
            
            figure = {
                "id": f"figure_{i+1}",
                "visibility": True,
                "x_label": plot_config.get("x_column", ""),
                "y_label": plot_config.get("y_column", "") if plot_type != "histogram" else "Frequency",
                "items": []
            }
            
            # Add plot item based on type
            if plot_type == "line":
                y_columns = plot_config.get("y_columns", [plot_config.get("y_column")])
                for y_col in y_columns[:3]:  # Limit to 3 lines
                    figure["items"].append({
                        "id": f"plot_{i+1}_{y_col}",
                        "type": "line",
                        "source": source,
                        "x_column": plot_config.get("x_column"),
                        "y_column": y_col,
                        "legend_name": y_col
                    })
            
            elif plot_type == "scatter":
                figure["items"].append({
                    "id": f"plot_{i+1}",
                    "type": "scatter",
                    "source": source,
                    "x_column": plot_config.get("x_column"),
                    "y_column": plot_config.get("y_column"),
                    "legend_name": f"{plot_config.get('x_column')} vs {plot_config.get('y_column')}"
                })
            
            elif plot_type == "bar":
                figure["items"].append({
                    "id": f"plot_{i+1}",
                    "type": "bar",
                    "source": source,
                    "x_column": plot_config.get("x_column"),
                    "y_column": plot_config.get("y_column"),
                    "legend_name": plot_config.get("title", "Bar Chart")
                })
            
            elif plot_type == "histogram":
                figure["items"].append({
                    "id": f"plot_{i+1}",
                    "type": "histogram",
                    "source": source,
                    "column": plot_config.get("column"),
                    "bins": plot_config.get("bins", 30),
                    "legend_name": plot_config.get("column")
                })
            
            config["figures"].append(figure)
        
        return config
    
    def _generate_python_code_from_request(self, message: str, analysis: Dict[str, Any], df: pd.DataFrame, file_path: Optional[str] = None) -> Optional[str]:
        """Generate Python code based on specific user request"""
        if not self.model:
            # Return a fallback code if no Gemini
            return self._generate_fallback_python_code(analysis, df, file_path)
        
        try:
            # Get the actual source filename
            source = Path(file_path).name if file_path else "data.csv"
            
            # Build detailed prompt for Gemini
            prompt = f"""{PYTHON_VIZ_SYSTEM_PROMPT}
            
            USER REQUEST: {message}
            
            DATA INFORMATION:
            - Source file: {source}
            - Shape: {df.shape[0]} rows × {df.shape[1]} columns
            - Columns: {list(df.columns)}
            - Data types: {df.dtypes.to_dict()}
            
            COLUMN DETAILS:
            """
            
            # Add column analysis
            for col_name, col_info in analysis.get("column_analysis", {}).items():
                prompt += f"\n- {col_name}: {col_info.get('data_type', 'unknown')}"
                if col_info.get('unique_count'):
                    prompt += f", {col_info['unique_count']} unique values"
                if col_info.get('min') is not None and col_info.get('max') is not None:
                    prompt += f", range [{col_info['min']:.2f}, {col_info['max']:.2f}]"
            
            prompt += f"""
            
            ANALYSIS INSIGHTS:
            - Suggested plots: {[p['plot_type'] for p in analysis.get('suggested_plots', [])[:3]]}
            - Has time series: {analysis.get('data_patterns', {}).get('has_time_series', False)}
            - Has correlations: {analysis.get('correlations', {}).get('has_correlations', False)}
            
            Based on the user request and data analysis, generate COMPLETE Python code that:
            1. Loads the data using load_data('{source}')
            2. Creates appropriate visualizations based on the request
            3. Uses register_plot() for each figure created
            4. Includes meaningful plot IDs and metadata
            5. Prints useful information about the data and analysis
            
            Return ONLY the Python code, no explanation text or markdown formatting.
            """
            
            llm_logger.info(f"GENERATING PYTHON CODE with Gemini, prompt length: {len(prompt)}")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up the response - remove markdown code blocks if present
            import re
            # Remove ```python and ``` markers
            code_match = re.search(r'```(?:python)?\s*(.*?)\s*```', response_text, re.DOTALL)
            if code_match:
                python_code = code_match.group(1).strip()
            else:
                python_code = response_text.strip()
            
            llm_logger.info(f"GENERATED PYTHON CODE: {python_code[:500]}...")
            return python_code
                
        except Exception as e:
            logger.error(f"Error generating Python code with Gemini: {e}")
            llm_logger.error(f"PYTHON CODE GENERATION ERROR: {e}")
            # Fallback to simple code generation
            return self._generate_fallback_python_code(analysis, df, file_path)
    
    def _generate_fallback_python_code(self, analysis: Dict[str, Any], df: pd.DataFrame, file_path: Optional[str] = None) -> str:
        """Generate fallback Python code when AI is not available"""
        source = Path(file_path).name if file_path else "data.csv"
        suggestions = analysis.get("suggested_plots", [])
        
        # Generate basic code based on first suggestion
        if suggestions:
            suggestion = suggestions[0]
            plot_type = suggestion["plot_type"]
            config = suggestion.get("config", {})
            
            if plot_type == "scatter":
                code = f"""
# Load and analyze data
df = load_data('{source}')
print(f"Loaded {{len(df)}} rows with columns: {{list(df.columns)}}")

# Create scatter plot
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['{config.get('x_column', df.columns[0])}'], 
    y=df['{config.get('y_column', df.columns[1] if len(df.columns) > 1 else df.columns[0])}'],
    mode='markers',
    name='Data Points'
))
fig.update_layout(
    title='Scatter Plot Analysis',
    xaxis_title='{config.get('x_column', 'X')}',
    yaxis_title='{config.get('y_column', 'Y')}'
)

register_plot(fig, plot_id='scatter_analysis', 
              metadata={{'title': 'Scatter Plot', 'description': 'Data analysis visualization'}})
"""
            elif plot_type == "histogram":
                col = config.get("column", df.columns[0])
                code = f"""
# Load and analyze data
df = load_data('{source}')
print(f"Loaded {{len(df)}} rows with columns: {{list(df.columns)}}")

# Create histogram
fig = go.Figure()
fig.add_trace(go.Histogram(x=df['{col}'], nbinsx=30))
fig.update_layout(
    title='{col} Distribution',
    xaxis_title='{col}',
    yaxis_title='Frequency'
)

register_plot(fig, plot_id='histogram_analysis', 
              metadata={{'title': '{col} Distribution', 'description': 'Distribution analysis'}})
"""
            else:
                # Default to simple data overview
                code = f"""
# Load and analyze data
df = load_data('{source}')
print(f"Loaded {{len(df)}} rows with columns: {{list(df.columns)}}")
print(f"Data shape: {{df.shape}}")
print("\\nFirst few rows:")
print(df.head())

# Simple visualization
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if len(numeric_cols) >= 2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[numeric_cols[0]], 
        y=df[numeric_cols[1]],
        mode='markers',
        name='Data Points'
    ))
    fig.update_layout(
        title='Data Visualization',
        xaxis_title=numeric_cols[0],
        yaxis_title=numeric_cols[1]
    )
    register_plot(fig, plot_id='data_overview')
"""
        else:
            # Very basic fallback
            code = f"""
# Load and analyze data
df = load_data('{source}')
print(f"Loaded {{len(df)}} rows with columns: {{list(df.columns)}}")

# Basic data overview
print("\\nData Summary:")
print(df.describe())

# Simple plot if possible
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if len(numeric_cols) > 0:
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df[numeric_cols[0]], nbinsx=30))
    fig.update_layout(
        title=f'{{numeric_cols[0]}} Distribution',
        xaxis_title=numeric_cols[0],
        yaxis_title='Frequency'
    )
    register_plot(fig, plot_id='data_overview')
"""
        
        return code.strip()

    def _generate_config_from_request(self, message: str, analysis: Dict[str, Any], df: pd.DataFrame, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate config based on specific user request"""
        if not self.model:
            # Fallback to analysis-based generation if no Gemini
            return self._generate_config_from_analysis(analysis, df, file_path)
        
        try:
            # Get the actual source filename
            source = Path(file_path).name if file_path else "data.csv"
            
            # Build detailed prompt for Gemini
            prompt = f"""{VISUALIZATION_SYSTEM_PROMPT}
            
            USER REQUEST: {message}
            
            DATA INFORMATION:
            - Source file: {source}
            - Shape: {df.shape[0]} rows × {df.shape[1]} columns
            - Columns: {list(df.columns)}
            - Data types: {df.dtypes.to_dict()}
            
            COLUMN DETAILS:
            """
            
            # Add column analysis
            for col_name, col_info in analysis.get("column_analysis", {}).items():
                prompt += f"\n- {col_name}: {col_info.get('data_type', 'unknown')}"
                if col_info.get('unique_count'):
                    prompt += f", {col_info['unique_count']} unique values"
                if col_info.get('min') is not None and col_info.get('max') is not None:
                    prompt += f", range [{col_info['min']:.2f}, {col_info['max']:.2f}]"
            
            prompt += f"""
            
            ANALYSIS INSIGHTS:
            - Suggested plots: {[p['plot_type'] for p in analysis.get('suggested_plots', [])[:3]]}
            - Has time series: {analysis.get('data_patterns', {}).get('has_time_series', False)}
            - Has correlations: {analysis.get('correlations', {}).get('has_correlations', False)}
            
            Based on the user request and data analysis, generate a COMPLETE dashboard configuration JSON.
            The configuration must:
            1. Use the exact source filename: {source}
            2. Use exact column names from the data
            3. Choose appropriate plot types for the user's request
            4. Include proper grid layout
            5. Set meaningful titles and labels
            
            Return ONLY valid JSON configuration, no explanation text.
            """
            
            llm_logger.info(f"GENERATING CONFIG with Gemini, prompt length: {len(prompt)}")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                config_str = json_match.group(0)
                config = json.loads(config_str)
                llm_logger.info(f"GENERATED CONFIG: {json.dumps(config, indent=2)[:1000]}...")
                return config
            else:
                llm_logger.warning("Failed to extract JSON from Gemini response, falling back")
                return self._generate_config_from_analysis(analysis, df, file_path)
                
        except Exception as e:
            logger.error(f"Error generating config with Gemini: {e}")
            llm_logger.error(f"CONFIG GENERATION ERROR: {e}")
            # Fallback to analysis-based generation
            return self._generate_config_from_analysis(analysis, df, file_path)
    
    def _parse_transformations_from_message(self, message: str, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Parse transformation requests from natural language"""
        transformations = []
        message_lower = message.lower()
        
        # Check for compute requests
        if "calculate" in message_lower or "compute" in message_lower:
            # Look for common calculations
            if "resistance" in message_lower and "voltage" in df.columns and "current" in df.columns:
                transformations.append({
                    "type": "compute_column",
                    "name": "resistance",
                    "formula": "voltage / current"
                })
            elif "power" in message_lower and "voltage" in df.columns and "current" in df.columns:
                transformations.append({
                    "type": "compute_column",
                    "name": "power",
                    "formula": "voltage * current"
                })
            elif "ratio" in message_lower or "divide" in message_lower:
                # Use Gemini to parse if available
                if self.model:
                    formula = self._extract_formula_with_ai(message, list(df.columns))
                    if formula:
                        transformations.append({
                            "type": "compute_column",
                            "name": "computed_value",
                            "formula": formula
                        })
        
        # Check for missing value handling
        if "fill" in message_lower and "missing" in message_lower:
            method = "mean"  # Default
            if "median" in message_lower:
                method = "median"
            elif "forward" in message_lower:
                method = "forward"
            elif "zero" in message_lower or "0" in message:
                method = "value"
                
            transformations.append({
                "type": "fill_missing",
                "method": method,
                "value": 0 if method == "value" else None
            })
        
        # Check for outlier handling
        if "outlier" in message_lower:
            method = "clip" if "clip" in message_lower else "remove"
            transformations.append({
                "type": "handle_outliers",
                "method": method,
                "threshold": 1.5
            })
        
        # Check for filtering
        if "filter" in message_lower or "where" in message_lower or "only" in message_lower:
            # Try to extract condition
            if self.model:
                condition = self._extract_condition_with_ai(message, list(df.columns))
                if condition:
                    transformations.append({
                        "type": "filter",
                        "condition": condition
                    })
        
        # Check for aggregation
        if "group" in message_lower or "aggregate" in message_lower or "sum" in message_lower or "average" in message_lower:
            # Use AI to parse grouping
            if self.model:
                agg_spec = self._extract_aggregation_with_ai(message, list(df.columns))
                if agg_spec:
                    transformations.append(agg_spec)
        
        return transformations
    
    def _extract_formula_with_ai(self, message: str, columns: List[str]) -> Optional[str]:
        """Use AI to extract formula from message"""
        if not self.model:
            return None
            
        try:
            prompt = f"""
            Extract a mathematical formula from this message: "{message}"
            Available columns: {columns}
            
            Return ONLY the formula using column names, like: "column1 / column2"
            If no clear formula can be extracted, return "NONE"
            """
            
            llm_logger.info(f"EXTRACTING FORMULA with Gemini")
            response = self.model.generate_content(prompt)
            formula = response.text.strip()
            llm_logger.info(f"EXTRACTED FORMULA: {formula}")
            
            if formula and formula != "NONE":
                return formula
                
        except Exception as e:
            logger.error(f"Error extracting formula with AI: {e}")
            
        return None
    
    def _extract_condition_with_ai(self, message: str, columns: List[str]) -> Optional[str]:
        """Use AI to extract filter condition from message"""
        if not self.model:
            return None
            
        try:
            prompt = f"""
            Extract a filter condition from this message: "{message}"
            Available columns: {columns}
            
            Return ONLY the condition as a Python expression, like: "column > 10"
            If no clear condition can be extracted, return "NONE"
            """
            
            llm_logger.info(f"EXTRACTING CONDITION with Gemini")
            response = self.model.generate_content(prompt)
            condition = response.text.strip()
            llm_logger.info(f"EXTRACTED CONDITION: {condition}")
            
            if condition and condition != "NONE":
                return condition
                
        except Exception as e:
            logger.error(f"Error extracting condition with AI: {e}")
            
        return None
    
    def _extract_aggregation_with_ai(self, message: str, columns: List[str]) -> Optional[Dict[str, Any]]:
        """Use AI to extract aggregation specification from message"""
        if not self.model:
            return None
            
        try:
            prompt = f"""
            Extract aggregation specification from this message: "{message}"
            Available columns: {columns}
            
            Return a JSON object with:
            - group_by: list of columns to group by
            - aggregations: dict of column to operation (mean, sum, count, min, max)
            
            Example: {{"group_by": ["category"], "aggregations": {{"sales": "sum", "price": "mean"}}}}
            
            If no clear aggregation can be extracted, return "NONE"
            """
            
            llm_logger.info(f"EXTRACTING AGGREGATION with Gemini")
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            llm_logger.info(f"EXTRACTED AGGREGATION: {result}")
            
            if result and result != "NONE":
                agg_spec = json.loads(result)
                return {
                    "type": "aggregate",
                    "group_by": agg_spec.get("group_by", []),
                    "aggregations": agg_spec.get("aggregations", {})
                }
                
        except Exception as e:
            logger.error(f"Error extracting aggregation with AI: {e}")
            
        return None
    
    def _build_conversation_context(self) -> str:
        """Build conversation context string"""
        if not self.conversation_history:
            return ""
            
        context_parts = ["Previous conversation:"]
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content'][:200]}...")  # Truncate long messages
            
        return "\n".join(context_parts)
    
    def clear_cache(self):
        """Clear data cache"""
        self.data_cache = {}
        logger.info("Data cache cleared")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def _log_response(self, response: Dict[str, Any]):
        """Log AI response for debugging"""
        llm_logger.info(f"RESPONSE TYPE: {response.get('type', 'unknown')}")
        llm_logger.info(f"RESPONSE MESSAGE: {response.get('message', '')[:500]}...")  # Truncate long messages
        
        # Log specific response data
        if 'config' in response and response['config']:
            llm_logger.info(f"CONFIG GENERATED: {json.dumps(response['config'], indent=2)[:1000]}...")
        
        if 'transformations' in response:
            llm_logger.info(f"TRANSFORMATIONS: {json.dumps(response['transformations'], indent=2)}")
        
        if 'data_summary' in response:
            llm_logger.info(f"DATA SUMMARY: Shape={response['data_summary'].get('shape')}, Columns={len(response['data_summary'].get('columns', []))}")
        
        if 'analysis' in response:
            analysis = response['analysis']
            if isinstance(analysis, dict):
                llm_logger.info(f"ANALYSIS: {len(analysis.get('suggested_plots', []))} plot suggestions")
        
        llm_logger.info(f"{'='*60}\n")