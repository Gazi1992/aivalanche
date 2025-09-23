"""
Plot Guidelines for LLM Code Generation

This module provides comprehensive guidelines for creating different plot types,
including best practices, metadata structure, and examples.
"""

from typing import Dict, Any, Optional
from .plot_types import PLOT_TYPES, get_plot_capabilities, get_all_plot_types


# General guidelines that apply to all plot types
GENERAL_GUIDELINES = """
## General Guidelines for All Plots

### Required Steps:
1. **Always call `register_plot()`** after creating your figure:
   ```python
   register_plot(fig, plot_id='unique_id', metadata={...})
   ```

2. **Never set explicit height** in the layout. The frontend will handle sizing:
   ```python
   # ❌ DON'T DO THIS:
   fig.update_layout(height=500)

   # ✅ DO THIS INSTEAD:
   fig.update_layout(title="My Plot")  # No height specification
   ```

3. **Import statements** are not needed for standard libraries:
   - `pandas as pd` - already imported
   - `numpy as np` - already imported
   - `plotly.graph_objects as go` - already imported
   - `plotly.express as px` - already imported

4. **Data handling**:
   - Use `datasets` dictionary to access loaded data
   - Use `load_data()` function to load new data files

### Metadata Structure:
The metadata parameter in `register_plot()` can control all visual aspects:

```python
metadata = {
    'appearance': {
        'title': {
            'text': 'Plot Title',
            'visible': True,
            'fontSize': 24,
            'color': '#333333',
            'bold': False,
            'italic': False,
            'alignment': 'center'  # 'left', 'center', 'right'
        },
        'axes': {
            'x': {
                'label': {
                    'text': 'X Axis Label',
                    'visible': True,
                    'fontSize': 14,
                    'color': '#666666'
                },
                'scale': 'linear',  # 'linear', 'log', 'date', 'category'
                'range': [None, None],  # Auto if None
                'ticks': {
                    'visible': True,
                    'color': '#999999',
                    'fontSize': 12
                },
                'grid': {
                    'visible': True,
                    'color': '#e0e0e0'
                }
            },
            'y': {
                # Same structure as x axis
            }
        },
        'legend': {
            'visible': True,
            'position': {
                'x': 0.02,
                'y': 0.98,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            'backgroundColor': 'rgba(255, 255, 255, 0.9)',
            'borderColor': '#cccccc'
        },
        'background': {
            'figure': '#ffffff',
            'plot': '#fafafa'
        }
    },
    'plotType': 'scatter',  # Helps frontend identify plot type
    'xAxisType': 'numeric',  # 'numeric' or 'category'
    'yAxisType': 'numeric'   # 'numeric' or 'category'
}
```

### Best Practices:
- Keep titles concise and descriptive
- Use clear axis labels with units when applicable
- Choose appropriate color schemes for data type
- Consider accessibility (colorblind-friendly palettes)
- Test with both small and large datasets
- **IMPORTANT: Hide legend when only one data series/item is present** - set showlegend=False for single-item plots
"""


# Specific guidelines for each plot type
PLOT_GUIDELINES = {
    "scatter": {
        "description": "Points plotted on X-Y axes to show relationships between variables",
        "when_to_use": "Showing correlation, outliers, clusters, or relationships between two continuous variables",
        "required_data": "Two numeric arrays (x and y coordinates)",
        "optional_data": "Size array for bubble charts, color array for categories, text for hover labels",
        "example": """
# Basic scatter plot
fig = go.Figure(data=[
    go.Scatter(
        x=df['column1'],
        y=df['column2'],
        mode='markers',
        marker=dict(
            size=8,
            color=df['category'],  # Optional: color by category
            colorscale='Viridis',
            showscale=True
        ),
        text=df['label'],  # Optional: hover text
        name='Data Points'
    )
])

fig.update_layout(
    title="Relationship between X and Y",
    xaxis_title="X Variable",
    yaxis_title="Y Variable"
)

register_plot(fig, plot_id='scatter_1')
""",
        "tips": [
            "Use 'markers' mode for points only, 'lines+markers' for connected points",
            "Adjust marker size for better visibility (typically 6-12)",
            "Use opacity (0.5-0.8) when points overlap",
            "Consider log scale for wide-ranging data",
            "Add trendline with a second trace if needed"
        ]
    },

    "line": {
        "description": "Connected points showing trends over continuous domain",
        "when_to_use": "Time series data, trends, continuous functions, comparing multiple series",
        "required_data": "X values (often time/sequence) and Y values",
        "optional_data": "Multiple Y series for comparison, error bars, filled areas",
        "example": """
# Line plot with multiple series
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=dates,
    y=values1,
    mode='lines',
    name='Series 1',
    line=dict(color='blue', width=2)
))

fig.add_trace(go.Scatter(
    x=dates,
    y=values2,
    mode='lines',
    name='Series 2',
    line=dict(color='red', width=2, dash='dash')
))

fig.update_layout(
    title="Trend Comparison",
    xaxis_title="Date",
    yaxis_title="Value",
    hovermode='x unified'
)

register_plot(fig, plot_id='line_trend')
""",
        "tips": [
            "Use 'hovermode=\"x unified\"' for time series",
            "Different line styles (solid, dash, dot) help distinguish series",
            "Consider fill='tozeroy' or fill='tonexty' for area charts",
            "Smooth noisy data before plotting if needed",
            "Use date formatting for time axes"
        ]
    },

    "bar": {
        "description": "Rectangular bars showing categorical comparisons",
        "when_to_use": "Comparing discrete categories, showing counts or sums, ranking data",
        "required_data": "Categories (x) and values (y)",
        "optional_data": "Error bars, multiple series for grouped/stacked bars",
        "example": """
# Grouped bar chart
fig = go.Figure()

fig.add_trace(go.Bar(
    x=categories,
    y=values_group1,
    name='Group 1',
    marker_color='lightblue'
))

fig.add_trace(go.Bar(
    x=categories,
    y=values_group2,
    name='Group 2',
    marker_color='darkblue'
))

fig.update_layout(
    title="Category Comparison",
    xaxis_title="Categories",
    yaxis_title="Values",
    barmode='group'  # or 'stack' for stacked bars
)

register_plot(fig, plot_id='bar_comparison')
""",
        "tips": [
            "Use 'barmode=\"group\"' for side-by-side comparison",
            "Use 'barmode=\"stack\"' for part-to-whole relationships",
            "Add text on bars with 'text' and 'textposition=\"outside\"'",
            "Consider horizontal bars (go.Bar with orientation='h') for long labels",
            "Sort bars by value for better readability"
        ]
    },

    "histogram": {
        "description": "Distribution of a single continuous variable",
        "when_to_use": "Understanding data distribution, frequency, identifying outliers",
        "required_data": "Single array of continuous values",
        "optional_data": "Number of bins, normalization type",
        "example": """
# Histogram with normal distribution overlay
fig = go.Figure()

fig.add_trace(go.Histogram(
    x=data_values,
    nbinsx=30,
    name='Distribution',
    marker_color='lightgreen',
    opacity=0.7,
    histnorm='probability density'  # For normalized histogram
))

# Optional: Add normal distribution curve
from scipy import stats
x_range = np.linspace(data_values.min(), data_values.max(), 100)
normal_curve = stats.norm.pdf(x_range, data_values.mean(), data_values.std())

fig.add_trace(go.Scatter(
    x=x_range,
    y=normal_curve,
    mode='lines',
    name='Normal Curve',
    line=dict(color='red', width=2)
))

fig.update_layout(
    title="Data Distribution",
    xaxis_title="Value",
    yaxis_title="Frequency"
)

register_plot(fig, plot_id='histogram_dist')
""",
        "tips": [
            "Experiment with bin count (20-50 typically works well)",
            "Use 'histnorm' for different normalizations",
            "Consider cumulative histogram for percentiles",
            "Overlay multiple distributions with transparency",
            "Add vertical lines for mean, median, quartiles"
        ]
    },

    "heatmap": {
        "description": "2D grid of values represented as colors",
        "when_to_use": "Correlation matrices, 2D distributions, time-based patterns, spatial data",
        "required_data": "2D array (matrix) of values",
        "optional_data": "X and Y labels, custom colorscale, annotations",
        "example": """
# Correlation heatmap with annotations
fig = go.Figure(data=go.Heatmap(
    z=correlation_matrix,
    x=variable_names,
    y=variable_names,
    colorscale='RdBu',
    zmid=0,  # Center colorscale at 0
    text=correlation_matrix.round(2),
    texttemplate='%{text}',
    textfont={"size": 10},
    colorbar=dict(title="Correlation")
))

fig.update_layout(
    title="Feature Correlation Matrix",
    xaxis_title="Variables",
    yaxis_title="Variables"
)

register_plot(fig, plot_id='correlation_heatmap')
""",
        "tips": [
            "Use diverging colorscales (RdBu) for data with meaningful center",
            "Use sequential colorscales (Viridis) for one-directional data",
            "Add text annotations for precise values",
            "Consider clustering rows/columns for patterns",
            "Adjust colorscale range for better contrast"
        ]
    },

    "box": {
        "description": "Statistical summary showing quartiles, median, and outliers",
        "when_to_use": "Comparing distributions, identifying outliers, statistical summaries",
        "required_data": "Arrays of values for each category",
        "optional_data": "Points overlay, notches for confidence intervals",
        "example": """
# Multiple box plots for comparison
fig = go.Figure()

for category in df['category'].unique():
    fig.add_trace(go.Box(
        y=df[df['category'] == category]['value'],
        name=category,
        boxpoints='outliers',  # Show outlier points
        marker_color=color_map[category],
        boxmean='sd'  # Show mean and standard deviation
    ))

fig.update_layout(
    title="Distribution Comparison by Category",
    yaxis_title="Values",
    showlegend=False
)

register_plot(fig, plot_id='box_comparison')
""",
        "tips": [
            "Use 'boxpoints=\"all\"' to show all points",
            "Use 'boxpoints=\"outliers\"' to show only outliers",
            "Add 'boxmean=\"sd\"' to show mean line",
            "Consider violin plots for more detail",
            "Use notched boxes for confidence intervals"
        ]
    },

    "pie": {
        "description": "Circular chart showing proportions of a whole",
        "when_to_use": "Part-to-whole relationships, percentages, composition",
        "required_data": "Categories and their values",
        "optional_data": "Colors, pull-out slices, hole for donut",
        "example": """
# Pie chart with customization
fig = go.Figure(data=[go.Pie(
    labels=categories,
    values=values,
    hole=0.4,  # Creates donut chart
    marker=dict(
        colors=custom_colors,
        line=dict(color='white', width=2)
    ),
    textinfo='label+percent',
    textposition='outside',
    pull=[0.1 if v == max(values) else 0 for v in values]  # Pull out largest
)])

fig.update_layout(
    title="Market Share Distribution",
    annotations=[dict(
        text='Total<br>$1.2M',
        x=0.5, y=0.5,
        font_size=20,
        showarrow=False
    )]  # Center annotation for donut
)

register_plot(fig, plot_id='pie_distribution')
""",
        "tips": [
            "Limit to 5-7 categories for clarity",
            "Use 'hole' parameter (0.3-0.5) for donut charts",
            "Pull out important slices with 'pull' parameter",
            "Consider treemap or bar chart for many categories",
            "Add center annotation for donut charts"
        ]
    },

    "scatter_3d": {
        "description": "Points in 3D space",
        "when_to_use": "3D relationships, clustering in 3D, spatial data",
        "required_data": "Three numeric arrays (x, y, z coordinates)",
        "optional_data": "Size, color for additional dimensions",
        "example": """
# 3D scatter plot
fig = go.Figure(data=[go.Scatter3d(
    x=df['x'],
    y=df['y'],
    z=df['z'],
    mode='markers',
    marker=dict(
        size=5,
        color=df['value'],  # Color by 4th dimension
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="Value")
    ),
    text=df['label'],
    hovertemplate='X: %{x}<br>Y: %{y}<br>Z: %{z}<extra></extra>'
)])

fig.update_layout(
    title="3D Data Distribution",
    scene=dict(
        xaxis_title="X Axis",
        yaxis_title="Y Axis",
        zaxis_title="Z Axis"
    )
)

register_plot(fig, plot_id='scatter3d_viz')
""",
        "tips": [
            "Use camera controls to set initial view angle",
            "Keep marker size small (3-8) for clarity",
            "Use color for 4th dimension",
            "Consider projection plots for complex data",
            "Test performance with large datasets"
        ]
    },

    "sankey": {
        "description": "Flow diagram showing quantities between nodes",
        "when_to_use": "Process flows, energy/material flows, budget allocations, user journeys",
        "required_data": "Source nodes, target nodes, and flow values",
        "optional_data": "Node colors, labels, positions",
        "example": """
# Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=["Source A", "Source B", "Process 1", "Process 2", "Output"],
        color=["blue", "blue", "green", "green", "orange"]
    ),
    link=dict(
        source=[0, 0, 1, 2, 3],  # indices of source nodes
        target=[2, 3, 3, 4, 4],  # indices of target nodes
        value=[10, 15, 20, 25, 30]  # flow values
    )
)])

fig.update_layout(
    title="Process Flow Diagram",
    font_size=10
)

register_plot(fig, plot_id='sankey_flow')
""",
        "tips": [
            "Order nodes logically (inputs → processes → outputs)",
            "Use consistent color coding for node types",
            "Keep labels concise",
            "Test with different layouts if flows cross",
            "Consider treemap for hierarchical data"
        ]
    },

    "parallel_coordinates": {
        "description": "Multiple vertical axes showing multi-dimensional data",
        "when_to_use": "Multivariate analysis, pattern detection, comparing many parameters",
        "required_data": "Multiple numeric dimensions",
        "optional_data": "Color dimension for categorization",
        "example": """
# Parallel coordinates plot
fig = go.Figure(data=go.Parcoords(
    dimensions=[
        dict(label='Parameter 1', values=df['param1'], range=[df['param1'].min(), df['param1'].max()]),
        dict(label='Parameter 2', values=df['param2'], range=[df['param2'].min(), df['param2'].max()]),
        dict(label='Parameter 3', values=df['param3'], range=[df['param3'].min(), df['param3'].max()]),
        dict(label='Parameter 4', values=df['param4'], range=[df['param4'].min(), df['param4'].max()])
    ],
    line=dict(
        color=df['category_code'],  # Numeric encoding of categories
        colorscale='Viridis',
        showscale=True,
        cmin=0,
        cmax=df['category_code'].max()
    )
))

fig.update_layout(
    title="Multi-Parameter Analysis"
)

register_plot(fig, plot_id='parallel_coords')
""",
        "tips": [
            "Normalize scales if dimensions have different ranges",
            "Use color to highlight categories or clusters",
            "Limit to 5-10 dimensions for readability",
            "Order dimensions to reveal patterns",
            "Consider dimensionality reduction for many parameters"
        ]
    },

    "waterfall": {
        "description": "Sequential positive and negative changes",
        "when_to_use": "Financial flows, cumulative effects, step-by-step changes",
        "required_data": "Categories and change values",
        "optional_data": "Colors for increase/decrease",
        "example": """
# Waterfall chart
fig = go.Figure(go.Waterfall(
    x=["Start", "Revenue", "Costs", "Taxes", "End"],
    y=[1000, 500, -300, -100, 1100],
    text=[f"${v:+.0f}" for v in [1000, 500, -300, -100, 1100]],
    textposition="outside",
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    increasing={"marker": {"color": "green"}},
    decreasing={"marker": {"color": "red"}},
    totals={"marker": {"color": "blue"}}
))

fig.update_layout(
    title="Financial Flow Analysis",
    yaxis_title="Amount ($)",
    showlegend=False
)

register_plot(fig, plot_id='waterfall_finance')
""",
        "tips": [
            "Use clear labels for each step",
            "Color code increases (green) and decreases (red)",
            "Add value labels on bars",
            "Include intermediate totals if needed",
            "Keep sequence logical and chronological"
        ]
    }
}


def get_plot_guidelines(plot_type: str, include_general: bool = True) -> Dict[str, Any]:
    """
    Get comprehensive guidelines for creating a specific plot type.

    Args:
        plot_type: Type of plot (e.g., 'scatter', 'bar', 'heatmap')
        include_general: Whether to include general guidelines

    Returns:
        Dictionary containing guidelines, examples, and best practices
    """
    # Normalize plot type
    plot_type = plot_type.lower().replace(' ', '_').replace('-', '_')

    # Get specific guidelines
    specific = PLOT_GUIDELINES.get(plot_type)

    if not specific:
        # Return general guidelines with warning if plot type not found
        return {
            "error": f"Plot type '{plot_type}' not found in guidelines",
            "available_types": list(PLOT_GUIDELINES.keys()),
            "general_guidelines": GENERAL_GUIDELINES if include_general else None
        }

    # Build response
    response = {
        "plot_type": plot_type,
        "specific_guidelines": specific
    }

    if include_general:
        response["general_guidelines"] = GENERAL_GUIDELINES

    # Add quick reference for metadata
    response["metadata_quick_reference"] = {
        "minimal": {
            "description": "Minimal metadata - let defaults handle most styling",
            "example": "register_plot(fig, plot_id='my_plot')"
        },
        "typical": {
            "description": "Typical metadata - specify plot type and axis types",
            "example": """register_plot(fig, plot_id='my_plot', metadata={
    'plotType': 'scatter',
    'xAxisType': 'numeric',  # or 'category'
    'yAxisType': 'numeric'
})"""
        },
        "detailed": {
            "description": "Detailed metadata - full control over appearance",
            "example": """register_plot(fig, plot_id='my_plot', metadata={
    'plotType': 'scatter',
    'xAxisType': 'numeric',
    'yAxisType': 'numeric',
    'appearance': {
        'title': {
            'text': 'My Custom Title',
            'fontSize': 24,
            'color': '#333333',
            'alignment': 'center'
        },
        'axes': {
            'x': {'label': {'text': 'X Axis Label'}},
            'y': {'label': {'text': 'Y Axis Label'}}
        },
        'legend': {
            'visible': True,
            'position': {'x': 0.02, 'y': 0.98}
        }
    }
})"""
        }
    }

    # Add common pitfalls to avoid
    response["common_mistakes"] = [
        "Setting explicit height in layout - frontend handles sizing",
        "Forgetting to call register_plot() - plot won't be captured",
        "Using too many colors or categories - keep it simple",
        "Not considering mobile/small screen viewing",
        "Overloading plot with too much information",
        "Using inappropriate plot type for data",
        "Not handling missing or invalid data"
    ]

    # Add performance tips
    response["performance_tips"] = [
        "Limit data points for interactive plots (< 10,000 for smooth interaction)",
        "Use data aggregation for large datasets",
        "Consider sampling for exploratory analysis",
        "Use simpler plot types for real-time updates",
        "Test with actual data volumes expected in production"
    ]

    return response


def get_all_plot_types() -> Dict[str, str]:
    """
    Get a list of all available plot types with brief descriptions.

    Returns:
        Dictionary mapping plot types to descriptions
    """
    return {
        plot_type: info["description"]
        for plot_type, info in PLOT_GUIDELINES.items()
    }


def get_plot_recommendation(data_characteristics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recommend appropriate plot types based on data characteristics.

    Args:
        data_characteristics: Dictionary describing the data
            - num_variables: Number of variables
            - variable_types: List of 'numeric', 'categorical', 'datetime'
            - data_size: Number of data points
            - relationship_type: 'correlation', 'distribution', 'comparison', etc.

    Returns:
        Dictionary with recommended plot types and reasons
    """
    recommendations = []

    num_vars = data_characteristics.get('num_variables', 1)
    var_types = data_characteristics.get('variable_types', [])
    relationship = data_characteristics.get('relationship_type', '')
    data_size = data_characteristics.get('data_size', 100)

    # Single variable
    if num_vars == 1:
        if 'numeric' in var_types:
            recommendations.append({
                'type': 'histogram',
                'reason': 'Best for showing distribution of single numeric variable'
            })
            recommendations.append({
                'type': 'box',
                'reason': 'Good for statistical summary and outliers'
            })
        elif 'categorical' in var_types:
            recommendations.append({
                'type': 'bar',
                'reason': 'Best for categorical counts or frequencies'
            })
            recommendations.append({
                'type': 'pie',
                'reason': 'Good for showing proportions (if < 7 categories)'
            })

    # Two variables
    elif num_vars == 2:
        if var_types.count('numeric') == 2:
            recommendations.append({
                'type': 'scatter',
                'reason': 'Best for showing correlation between two numeric variables'
            })
            if relationship == 'time_series' or 'datetime' in var_types:
                recommendations.append({
                    'type': 'line',
                    'reason': 'Ideal for time series or sequential data'
                })
        elif 'categorical' in var_types and 'numeric' in var_types:
            recommendations.append({
                'type': 'bar',
                'reason': 'Compare values across categories'
            })
            recommendations.append({
                'type': 'box',
                'reason': 'Compare distributions across categories'
            })

    # Three or more variables
    elif num_vars >= 3:
        if var_types.count('numeric') >= 3:
            recommendations.append({
                'type': 'scatter_3d',
                'reason': 'Visualize 3D relationships'
            })
            recommendations.append({
                'type': 'parallel_coordinates',
                'reason': 'Compare multiple dimensions simultaneously'
            })
            recommendations.append({
                'type': 'heatmap',
                'reason': 'Show patterns in matrix data'
            })

    # Special cases
    if relationship == 'flow':
        recommendations.append({
            'type': 'sankey',
            'reason': 'Perfect for showing flow between categories'
        })

    if relationship == 'hierarchical':
        recommendations.append({
            'type': 'treemap',
            'reason': 'Good for hierarchical data'
        })
        recommendations.append({
            'type': 'sunburst',
            'reason': 'Alternative for hierarchical relationships'
        })

    if relationship == 'geographic':
        recommendations.append({
            'type': 'choropleth',
            'reason': 'Map-based visualization for geographic data'
        })
        recommendations.append({
            'type': 'scatter_geo',
            'reason': 'Points on a map'
        })

    return {
        'recommendations': recommendations[:5],  # Top 5 recommendations
        'data_summary': data_characteristics
    }


# Example usage for testing
if __name__ == "__main__":
    # Test getting guidelines for scatter plot
    scatter_guidelines = get_plot_guidelines('scatter')
    print("Scatter Plot Guidelines:")
    print(scatter_guidelines['specific_guidelines']['description'])
    print("\nExample:")
    print(scatter_guidelines['specific_guidelines']['example'])

    # Test getting all plot types
    all_types = get_all_plot_types()
    print(f"\nAvailable plot types: {len(all_types)}")

    # Test recommendations
    data_chars = {
        'num_variables': 2,
        'variable_types': ['numeric', 'numeric'],
        'relationship_type': 'correlation',
        'data_size': 1000
    }
    recommendations = get_plot_recommendation(data_chars)
    print(f"\nRecommendations for data: {recommendations}")