"""
Portfolio Risk Analysis
Visualizing return distributions and risk metrics across asset classes
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

# === Generate realistic portfolio data ===
np.random.seed(42)

# Asset classes and their characteristics
asset_classes = {
    'Stocks': {'mean': 0.08, 'std': 0.16, 'skew': -0.5},
    'Bonds': {'mean': 0.04, 'std': 0.05, 'skew': 0.2},
    'Real Estate': {'mean': 0.06, 'std': 0.12, 'skew': -0.3},
    'Commodities': {'mean': 0.05, 'std': 0.20, 'skew': 0.8},
    'Crypto': {'mean': 0.15, 'std': 0.50, 'skew': 1.2},
}

# Generate returns for each asset class (annual returns)
n_years = 10
n_samples = 1000

returns_data = {}
for asset, params in asset_classes.items():
    # Generate returns with skewness
    base_returns = np.random.normal(params['mean'], params['std'], n_samples)
    # Add skewness by mixing with exponential distribution
    if params['skew'] > 0:
        skewed = np.random.exponential(params['std'], n_samples) * params['skew']
        returns = base_returns + skewed - np.mean(skewed)
    else:
        skewed = -np.random.exponential(params['std'], n_samples) * abs(params['skew'])
        returns = base_returns + skewed - np.mean(skewed)

    returns_data[asset] = returns

# === Visualization 1: Violin Plots - Return Distributions ===
fig1 = go.Figure()

colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6']

for i, (asset, returns) in enumerate(returns_data.items()):
    fig1.add_trace(go.Violin(
        y=returns * 100,  # Convert to percentage
        name=asset,
        box_visible=True,
        meanline_visible=True,
        fillcolor=colors[i],
        opacity=0.7,
        line_color=colors[i],
        hovertemplate='<b>%{fullData.name}</b><br>Return: %{y:.2f}%<extra></extra>'
    ))

fig1.update_layout(
    title={
        'text': 'Annual Return Distributions by Asset Class',
        'x': 0.5,
        'xanchor': 'center'
    },
    yaxis=dict(
        title='Annual Return (%)',
        zeroline=True,
        zerolinecolor='rgba(128,128,128,0.2)',
        gridcolor='rgba(128,128,128,0.1)'
    ),
    xaxis=dict(title='Asset Class'),
    showlegend=False,
    hovermode='closest'
)

register_plot(
    fig1,
    plot_id='return_distributions',
    metadata={
        'appearance': {
            'title': {'text': 'Portfolio Return Analysis'}
        }
    }
)

# === Visualization 2: Box Plots - Quarterly Performance by Sector ===
# Generate quarterly data for different sectors
sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer', 'Industrial']
quarters = ['Q1', 'Q2', 'Q3', 'Q4']

quarterly_data = []
for sector in sectors:
    base_return = np.random.uniform(0.02, 0.08)
    volatility = np.random.uniform(0.03, 0.08)
    for quarter in quarters:
        # Add seasonal effects
        seasonal_adj = {'Q1': -0.01, 'Q2': 0.01, 'Q3': -0.005, 'Q4': 0.015}
        returns = np.random.normal(
            base_return + seasonal_adj[quarter],
            volatility,
            100
        )
        for r in returns:
            quarterly_data.append({
                'Sector': sector,
                'Quarter': quarter,
                'Return': r * 100
            })

df_quarterly = pd.DataFrame(quarterly_data)

fig2 = go.Figure()

colors_sectors = {
    'Technology': '#00bcd4',
    'Healthcare': '#4caf50',
    'Finance': '#ff9800',
    'Energy': '#f44336',
    'Consumer': '#9c27b0',
    'Industrial': '#607d8b'
}

for sector in sectors:
    sector_data = df_quarterly[df_quarterly['Sector'] == sector]
    fig2.add_trace(go.Box(
        x=sector_data['Quarter'],
        y=sector_data['Return'],
        name=sector,
        marker_color=colors_sectors[sector],
        boxmean='sd'  # Show mean and standard deviation
    ))

fig2.update_layout(
    title={
        'text': 'Quarterly Returns by Sector',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(title='Quarter'),
    yaxis=dict(
        title='Quarterly Return (%)',
        zeroline=True,
        zerolinecolor='rgba(128,128,128,0.2)'
    ),
    boxmode='group',
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="top",
        y=0.98,
        xanchor="left",
        x=0.02,
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="rgba(0, 0, 0, 0.2)",
        borderwidth=1
    )
)

register_plot(
    fig2,
    plot_id='quarterly_performance',
    metadata={
        'appearance': {
            'title': {'text': 'Sector Performance Analysis'}
        }
    }
)

# === Visualization 3: Correlation Heatmap ===
# Create correlation matrix for assets
assets = list(asset_classes.keys())
n_assets = len(assets)

# Define realistic correlations
correlation_matrix = np.array([
    [1.00, 0.35, 0.45, 0.25, 0.65],  # Stocks
    [0.35, 1.00, 0.30, -0.15, 0.10],  # Bonds
    [0.45, 0.30, 1.00, 0.20, 0.25],   # Real Estate
    [0.25, -0.15, 0.20, 1.00, 0.30],  # Commodities
    [0.65, 0.10, 0.25, 0.30, 1.00],   # Crypto
])

fig3 = go.Figure(data=go.Heatmap(
    z=correlation_matrix,
    x=assets,
    y=assets,
    colorscale='RdBu',
    zmid=0,
    text=np.round(correlation_matrix, 2),
    texttemplate='%{text}',
    textfont={"size": 10},
    colorbar=dict(title='Correlation'),
    hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.3f}<extra></extra>'
))

fig3.update_layout(
    title={
        'text': 'Asset Correlation Matrix',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(title='', side='bottom'),
    yaxis=dict(title='', autorange='reversed')
)

register_plot(
    fig3,
    plot_id='correlation_matrix',
    metadata={
        'appearance': {
            'title': {'text': 'Portfolio Correlation Analysis'}
        }
    }
)