"""
Comprehensive Demo Script - Showcasing Various Plot Types
This script demonstrates scatter, bar, heatmap, and scatter matrix plots
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

# Generate synthetic datasets for demonstration
np.random.seed(42)

# 1. SCATTER PLOT - Scientific Data
print("[STATUS:info] Creating scatter plot with scientific data...")
n_points = 500
x_scatter = np.linspace(0, 10, n_points)
y_scatter = 2 * np.sin(x_scatter) + np.random.normal(0, 0.3, n_points)
y_fitted = 2 * np.sin(x_scatter)

fig_scatter = go.Figure()
fig_scatter.add_trace(go.Scatter(
    x=x_scatter,
    y=y_scatter,
    mode='markers',
    name='Experimental Data',
    marker=dict(
        size=4,
        color=y_scatter,
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title='Value'),
        opacity=0.7
    )
))
fig_scatter.add_trace(go.Scatter(
    x=x_scatter,
    y=y_fitted,
    mode='lines',
    name='Theoretical Model',
    line=dict(color='red', width=2, dash='dash')
))
fig_scatter.update_layout(
    title='Scientific Data: Experimental vs Theoretical Model',
    xaxis_title='Time (seconds)',
    yaxis_title='Signal Amplitude',
    hovermode='x unified',
    template='plotly_white'
)
register_plot(fig_scatter, plot_id='scatter_scientific', 
              metadata={'title': 'Scatter Plot with Fitted Model', 
                       'description': 'Comparison of experimental measurements with theoretical predictions'})

# 2. BAR CHART - Categorical Data
print("[STATUS:info] Creating bar chart with categorical data...")
categories = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
quarters = ['Q1', 'Q2', 'Q3', 'Q4']

# Generate sales data for each quarter
np.random.seed(42)
sales_data = {}
for quarter in quarters:
    sales_data[quarter] = np.random.randint(50, 200, size=len(categories))

fig_bar = go.Figure()

# Add bars for each quarter
colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA']
for i, quarter in enumerate(quarters):
    fig_bar.add_trace(go.Bar(
        name=quarter,
        x=categories,
        y=sales_data[quarter],
        marker_color=colors[i],
        text=sales_data[quarter],
        textposition='auto'
    ))

fig_bar.update_layout(
    title='Quarterly Sales by Product Category',
    xaxis_title='Product Category',
    yaxis_title='Sales (in thousands)',
    barmode='group',
    hovermode='x unified',
    template='plotly_white',
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

register_plot(fig_bar, plot_id='bar_categorical',
              metadata={'title': 'Bar Chart with Categories',
                       'description': 'Quarterly sales comparison across product categories'})

# 3. HEATMAP - Both axes categorical
print("[STATUS:info] Creating heatmap with categorical axes...")
# Categories for both axes
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
hours = ['Morning', 'Afternoon', 'Evening', 'Night']

# Generate activity data (e.g., website traffic)
np.random.seed(42)
activity_data = np.random.randint(10, 100, size=(len(hours), len(days)))

# Create heatmap
fig_heatmap = go.Figure(data=go.Heatmap(
    z=activity_data,
    x=days,
    y=hours,
    colorscale='Viridis',
    text=activity_data,
    texttemplate='%{text}',
    textfont={"size": 10},
    colorbar=dict(title='Activity Level')
))

fig_heatmap.update_layout(
    title='Weekly Activity Heatmap',
    xaxis_title='Day of Week',
    yaxis_title='Time of Day',
    xaxis=dict(type='category'),
    yaxis=dict(type='category'),
    template='plotly_white'
)

register_plot(fig_heatmap, plot_id='heatmap_categorical',
              metadata={'title': 'Activity Heatmap',
                       'description': 'Weekly activity patterns with categorical axes',
                       'appearance': {
                           'legend': {
                               'visible': False
                           }
                       }})

# 4. SCATTER MATRIX - Multiple dimensions
print("[STATUS:info] Creating scatter matrix plot...")

# Generate multivariate data
np.random.seed(42)
n_samples = 200

# Create correlated features for interesting patterns
feature_1 = np.random.randn(n_samples)
feature_2 = 0.7 * feature_1 + 0.3 * np.random.randn(n_samples)
feature_3 = -0.5 * feature_1 + 0.5 * np.random.randn(n_samples)
feature_4 = np.random.randn(n_samples)

# Create categories for coloring
categories = np.random.choice(['Type A', 'Type B', 'Type C'], n_samples)

# Create DataFrame
df_scatter_matrix = pd.DataFrame({
    'Feature 1': feature_1,
    'Feature 2': feature_2,
    'Feature 3': feature_3,
    'Feature 4': feature_4,
    'Category': categories
})

# Create scatter matrix
fig_splom = go.Figure(data=go.Splom(
    dimensions=[
        dict(label='Feature 1', values=df_scatter_matrix['Feature 1']),
        dict(label='Feature 2', values=df_scatter_matrix['Feature 2']),
        dict(label='Feature 3', values=df_scatter_matrix['Feature 3']),
        dict(label='Feature 4', values=df_scatter_matrix['Feature 4'])
    ],
    text=df_scatter_matrix['Category'],
    marker=dict(
        color=pd.Categorical(df_scatter_matrix['Category']).codes,
        colorscale='Viridis',
        size=5,
        line=dict(width=0.5, color='white')
    ),
    showupperhalf=False,  # Only show lower triangle
    diagonal=dict(visible=False)  # Hide diagonal
))

fig_splom.update_layout(
    title='Feature Correlation Matrix',
    template='plotly_white',
    dragmode='select',
    hovermode='closest',
    height=600,
    showlegend=False
)

register_plot(fig_splom, plot_id='scatter_matrix',
              metadata={'title': 'Scatter Matrix',
                       'description': 'Multi-dimensional feature correlation analysis',
                       'isSplom': True})

print("[STATUS:success] Demo plots generated successfully!")
print(f"[STATUS:info] Total plots created: 4")