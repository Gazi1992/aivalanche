# Python Execution Demo Scripts

This directory contains demonstration scripts showing the capabilities of the new Python execution service for data analysis and visualization.

## Available Scripts

### 1. temperature_analysis.py
- **Data**: Temperature sensor data over time
- **Analysis**: Basic statistics, outlier detection, correlation analysis
- **Visualizations**: Time series, distributions, scatter plots
- **Key Features**: IQR-based outlier detection, sensor correlation

### 2. mosfet_characterization.py
- **Data**: MOSFET electrical characteristics (I-V curves)
- **Analysis**: Device parameter extraction, transconductance analysis
- **Visualizations**: Family curves, 3D surface plots, transfer characteristics
- **Key Features**: Small-signal parameter extraction, threshold voltage estimation

### 3. cars_analysis.py
- **Data**: Comprehensive cars dataset with multiple features
- **Analysis**: Correlation analysis, price distributions, brand statistics
- **Visualizations**: Correlation heatmap, parallel coordinates, regression plots
- **Key Features**: Multi-dimensional analysis, outlier detection, trend analysis

### 4. population_trends.py
- **Data**: Multi-year population and economic data
- **Analysis**: Growth rate calculations, gender distribution, GDP correlation
- **Visualizations**: Grouped/stacked bar charts, trend analysis, comparative plots
- **Key Features**: Time series analysis, economic indicators, demographic insights

### 5. scatter_matrix_analysis.py
- **Data**: Multi-dimensional data with pass/fail classification
- **Analysis**: Feature correlations, PCA dimensionality reduction
- **Visualizations**: Scatter matrix, parallel coordinates, box plots
- **Key Features**: Pattern detection, classification analysis, feature importance

## How to Use

These scripts are designed to be executed through the Python execution service API:

```python
# Example API call
POST /api/python/execute
{
    "session_id": "my-session",
    "code": "<script content here>"
}
```

Each script demonstrates different aspects of data analysis:
- Data loading and preprocessing
- Statistical analysis and outlier detection
- Interactive visualizations with Plotly
- Advanced techniques (PCA, regression, correlation)
- Multi-dimensional data exploration

## Available Helper Functions

The execution environment provides these built-in helpers:
- `load_data(path)`: Load CSV, Excel, or JSON files
- `register_plot(fig)`: Register Plotly figures for display
- `quick_plot(df, x, y)`: Create quick visualizations
- `show_stats(df)`: Display statistical summaries
- `find_outliers(df, column)`: Detect outliers using IQR or z-score

## Session Management

Scripts run in persistent sessions, allowing for:
- Incremental analysis building
- Data persistence between executions
- Variable and plot accumulation
- Interactive exploration workflow