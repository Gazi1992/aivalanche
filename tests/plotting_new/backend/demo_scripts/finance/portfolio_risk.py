"""
💹 Portfolio Risk Analysis
Comprehensive risk visualization using statistical plots
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

# Generate realistic portfolio data
np.random.seed(42)

# Asset classes and their characteristics
asset_classes = {
    'Stocks': {'mean': 0.08, 'std': 0.16, 'skew': -0.5},
    'Bonds': {'mean': 0.04, 'std': 0.05, 'skew': 0.1},
    'Real Estate': {'mean': 0.06, 'std': 0.12, 'skew': -0.3},
    'Commodities': {'mean': 0.05, 'std': 0.20, 'skew': 0.2},
    'Crypto': {'mean': 0.15, 'std': 0.40, 'skew': -0.8},
    'Cash': {'mean': 0.02, 'std': 0.01, 'skew': 0.0}
}

# Generate returns data
returns_data = []
for asset, params in asset_classes.items():
    # Generate returns with specified characteristics
    base_returns = np.random.normal(params['mean'], params['std'], 1000)
    # Add skewness
    if params['skew'] != 0:
        base_returns = base_returns + params['skew'] * np.abs(base_returns) * np.random.choice([-1, 1], 1000, p=[0.3, 0.7])

    for i, ret in enumerate(base_returns):
        returns_data.append({
            'Asset': asset,
            'Return': ret,
            'Quarter': f"Q{(i % 4) + 1}",
            'Year': 2020 + (i // 250)
        })

df_returns = pd.DataFrame(returns_data)

# === Plot 1: Violin Plots - Return Distributions ===
fig1 = go.Figure()

# Add violin plot for each asset class
for i, asset in enumerate(asset_classes.keys()):
    asset_data = df_returns[df_returns['Asset'] == asset]['Return']

    fig1.add_trace(go.Violin(
        y=asset_data,
        x=[asset] * len(asset_data),
        name=asset,
        box_visible=True,
        meanline_visible=True,
        fillcolor=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'][i],
        opacity=0.7,
        line_color='rgba(0,0,0,0.5)',
    ))

fig1.update_layout(
    title={
        'text': "📊 Asset Class Return Distributions",
        'x': 0.5,
        'xanchor': 'center'
    },
    yaxis_title="Annual Return",
    xaxis_title="Asset Class",
    showlegend=False,
    violinmode='group',
    height=500,
    yaxis=dict(tickformat='.0%', zeroline=True, zerolinewidth=2, zerolinecolor='gray')
)

# Add risk levels
fig1.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Zero Return")
fig1.add_hline(y=0.10, line_dash="dot", line_color="green", annotation_text="Target: 10%")

register_plot(
    fig1,
    plot_id='return_distributions',
    metadata={'title': 'Asset Return Distributions'}
)

# === Plot 2: Box Plots - Quarterly Performance by Sector ===
# Generate sector data
sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer', 'Industrial']
quarters = ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023']

sector_data = []
for sector in sectors:
    for quarter in quarters:
        # Different sectors have different seasonal patterns
        base_return = np.random.normal(0.03, 0.08, 50)
        if sector == 'Technology':
            base_return += 0.02  # Tech outperformance
        elif sector == 'Energy' and 'Q3' in quarter:
            base_return += 0.03  # Summer driving season

        sector_data.extend([{
            'Sector': sector,
            'Quarter': quarter,
            'Return': ret
        } for ret in base_return])

df_sectors = pd.DataFrame(sector_data)

fig2 = go.Figure()

colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33']

for i, sector in enumerate(sectors):
    sector_df = df_sectors[df_sectors['Sector'] == sector]

    fig2.add_trace(go.Box(
        y=sector_df['Return'],
        x=sector_df['Quarter'],
        name=sector,
        marker_color=colors[i],
        boxmean='sd',  # Show mean and standard deviation
        whiskerwidth=0.2,
    ))

fig2.update_layout(
    title={
        'text': "📈 Quarterly Earnings by Sector",
        'x': 0.5,
        'xanchor': 'center'
    },
    yaxis_title="Quarterly Return",
    xaxis_title="Quarter",
    boxmode='group',
    height=500,
    yaxis=dict(tickformat='.1%'),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

register_plot(
    fig2,
    plot_id='sector_performance',
    metadata={'title': 'Sector Performance Analysis'}
)