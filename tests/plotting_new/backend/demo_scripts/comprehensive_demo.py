"""
Comprehensive Demo Script - Showcasing Various Plot Types
This script demonstrates scatter, bar, histogram, PCP, and scatter matrix plots
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

print("[STATUS:success] Demo plots generated successfully!")
print(f"[STATUS:info] Total plots created: 2")