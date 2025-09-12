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

print("[STATUS:success] Demo plots generated successfully!")
print(f"[STATUS:info] Total plots created: 1")