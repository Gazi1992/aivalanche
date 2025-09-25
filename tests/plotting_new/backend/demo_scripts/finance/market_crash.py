"""
Market Crash Cascade - 2008 Financial Crisis
Visualizing the domino effect of bank failures and market collapse
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# === Generate 2008 Financial Crisis Data ===
np.random.seed(2008)

# Key dates in the 2008 crisis
crisis_dates = pd.date_range('2008-01-01', '2009-06-30', freq='D')

# Major events
events = [
    {'date': '2008-03-16', 'event': 'Bear Stearns Collapse', 'impact': -5},
    {'date': '2008-09-07', 'event': 'Fannie Mae/Freddie Mac', 'impact': -8},
    {'date': '2008-09-15', 'event': 'Lehman Brothers Bankruptcy', 'impact': -15},
    {'date': '2008-09-16', 'event': 'AIG Bailout', 'impact': -10},
    {'date': '2008-10-03', 'event': 'TARP Signed', 'impact': 5},
    {'date': '2009-03-09', 'event': 'Market Bottom', 'impact': 0},
]

# === Visualization 1: Candlestick Chart with Volume ===
# Generate realistic market data
base_price = 14000  # Dow Jones starting level
prices = []
volumes = []
current_price = base_price

for date in crisis_dates:
    # Add event impacts
    daily_impact = 0
    for event in events:
        if date == pd.to_datetime(event['date']):
            daily_impact = event['impact'] * base_price / 100

    # Normal market volatility increases during crisis
    if date < pd.to_datetime('2008-09-01'):
        volatility = 0.015  # Normal volatility
    elif date < pd.to_datetime('2009-03-09'):
        volatility = 0.04   # Crisis volatility
    else:
        volatility = 0.02   # Recovery volatility

    # Calculate OHLC
    daily_change = np.random.normal(-0.001, volatility) * current_price + daily_impact
    open_price = current_price
    close_price = current_price + daily_change
    high_price = max(open_price, close_price) + abs(np.random.normal(0, volatility * 0.5)) * current_price
    low_price = min(open_price, close_price) - abs(np.random.normal(0, volatility * 0.5)) * current_price

    # Volume spikes during crisis events
    base_volume = 4e9  # 4 billion shares
    if abs(daily_impact) > 0:
        volume = base_volume * (1 + abs(daily_impact) / 5)
    else:
        volume = base_volume * (1 + np.random.uniform(-0.2, 0.3))

    prices.append({
        'Date': date,
        'Open': open_price,
        'High': high_price,
        'Low': low_price,
        'Close': close_price
    })
    volumes.append(volume)

    current_price = close_price

df_market = pd.DataFrame(prices)

fig1 = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.7, 0.3]
)

# Candlestick chart
fig1.add_trace(
    go.Candlestick(
        x=df_market['Date'],
        open=df_market['Open'],
        high=df_market['High'],
        low=df_market['Low'],
        close=df_market['Close'],
        name='DJIA',
        increasing_line_color='green',
        decreasing_line_color='red'
    ),
    row=1, col=1
)

# Volume bars
colors = ['red' if df_market['Close'].iloc[i] < df_market['Open'].iloc[i] else 'green'
          for i in range(len(df_market))]

fig1.add_trace(
    go.Bar(
        x=df_market['Date'],
        y=volumes,
        name='Volume',
        marker_color=colors,
        showlegend=False
    ),
    row=2, col=1
)

# Add event annotations
for event in events:
    fig1.add_annotation(
        x=event['date'],
        y=df_market[df_market['Date'] == pd.to_datetime(event['date'])]['High'].values[0] if len(df_market[df_market['Date'] == pd.to_datetime(event['date'])]) > 0 else base_price,
        text=event['event'],
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40,
        font=dict(size=9),
        row=1, col=1
    )

fig1.update_xaxes(rangeslider_visible=False, row=1, col=1)
fig1.update_yaxes(title_text="Price ($)", row=1, col=1)
fig1.update_yaxes(title_text="Volume", row=2, col=1)
fig1.update_xaxes(title_text="Date", row=2, col=1)

fig1.update_layout(
    title={
        'text': '2008 Financial Crisis - Market Collapse',
        'x': 0.5,
        'xanchor': 'center'
    },
    showlegend=False,
    hovermode='x unified'
)

register_plot(
    fig1,
    plot_id='market_crash_candlestick',
    metadata={
        'appearance': {
            'title': {'text': '2008 Market Crash Timeline'}
        }
    }
)

# === Visualization 2: Systemic Risk Heatmap Over Time ===
# Create a heatmap showing how risk spread across financial sectors
sectors = ['Investment Banks', 'Commercial Banks', 'Insurance', 'Mortgage Lenders', 'Hedge Funds', 'Money Markets']
months = pd.date_range('2008-01', '2009-06', freq='M').strftime('%b %Y')

# Generate risk levels (0-100 scale)
risk_matrix = np.zeros((len(sectors), len(months)))

# Set baseline risk
risk_matrix[:, :] = 20  # Normal risk level

# Add crisis progression
crisis_timeline = {
    3: {'Investment Banks': 60, 'Mortgage Lenders': 70},  # March 2008 - Bear Stearns
    8: {'Investment Banks': 90, 'Insurance': 80, 'Mortgage Lenders': 95},  # Sept 2008 - Lehman/AIG
    9: {'Investment Banks': 95, 'Commercial Banks': 70, 'Insurance': 85, 'Mortgage Lenders': 100, 'Money Markets': 60},  # Oct 2008
    10: {'Investment Banks': 85, 'Commercial Banks': 75, 'Insurance': 70, 'Hedge Funds': 65, 'Money Markets': 55},  # Nov 2008
    11: {'Investment Banks': 80, 'Commercial Banks': 70, 'Insurance': 65, 'Hedge Funds': 60},  # Dec 2008
    12: {'Investment Banks': 75, 'Commercial Banks': 65, 'Insurance': 60, 'Hedge Funds': 55},  # Jan 2009
    13: {'Investment Banks': 70, 'Commercial Banks': 60, 'Insurance': 55},  # Feb 2009
    14: {'Investment Banks': 65, 'Commercial Banks': 55, 'Insurance': 50},  # Mar 2009 - Market bottom
}

for month_idx, risks in crisis_timeline.items():
    for sector, risk in risks.items():
        sector_idx = sectors.index(sector)
        risk_matrix[sector_idx, month_idx] = risk
        # Smooth transitions
        if month_idx > 0:
            risk_matrix[sector_idx, month_idx-1] = (risk_matrix[sector_idx, month_idx-1] + risk) / 2
        if month_idx < len(months) - 1:
            risk_matrix[sector_idx, month_idx+1] = (risk_matrix[sector_idx, month_idx+1] + risk) / 2

fig2 = go.Figure(data=go.Heatmap(
    z=risk_matrix,
    x=list(months),
    y=sectors,
    colorscale=[
        [0, '#00FF00'],      # Green - Low risk
        [0.3, '#FFFF00'],    # Yellow - Medium risk
        [0.6, '#FFA500'],    # Orange - High risk
        [1, '#FF0000']       # Red - Critical risk
    ],
    text=np.round(risk_matrix, 0),
    texttemplate='%{text}',
    textfont={"size": 10},
    colorbar=dict(
        title='Systemic Risk<br>Level',
        ticktext=['Low', 'Medium', 'High', 'Critical'],
        tickvals=[20, 40, 60, 80]
    ),
    hovertemplate='%{y}<br>%{x}<br>Risk Level: %{z:.0f}%<extra></extra>'
))

# Add annotations for major events
annotations = [
    {'x': 'Mar 2008', 'y': 'Investment Banks', 'text': 'Bear Stearns'},
    {'x': 'Sep 2008', 'y': 'Investment Banks', 'text': 'Lehman'},
    {'x': 'Sep 2008', 'y': 'Insurance', 'text': 'AIG'},
    {'x': 'Mar 2009', 'y': 'Investment Banks', 'text': 'Market Bottom'}
]

for ann in annotations:
    fig2.add_annotation(
        x=ann['x'],
        y=ann['y'],
        text=ann['text'],
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1,
        arrowcolor="white",
        ax=20,
        ay=-20,
        font=dict(size=9, color="white"),
        bgcolor="rgba(0,0,0,0.5)"
    )

fig2.update_layout(
    title={
        'text': 'Systemic Risk Propagation During 2008 Crisis',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(title='Month', tickangle=45),
    yaxis=dict(title='Financial Sector')
)

register_plot(
    fig2,
    plot_id='systemic_risk_heatmap',
    metadata={
        'appearance': {
            'title': {'text': 'Crisis Contagion Spread'}
        }
    }
)

# === Visualization 3: Waterfall Chart - Losses Cascade ===
# Financial institutions losses (in billions)
losses_data = [
    {'entity': 'Starting Capital', 'value': 0, 'measure': 'absolute'},
    {'entity': 'Lehman Brothers', 'value': -691, 'measure': 'relative'},
    {'entity': 'AIG', 'value': -182, 'measure': 'relative'},
    {'entity': 'Fannie Mae', 'value': -100, 'measure': 'relative'},
    {'entity': 'Freddie Mac', 'value': -79, 'measure': 'relative'},
    {'entity': 'Bank of America', 'value': -56, 'measure': 'relative'},
    {'entity': 'Citigroup', 'value': -45, 'measure': 'relative'},
    {'entity': 'JPMorgan Chase', 'value': -31, 'measure': 'relative'},
    {'entity': 'Wells Fargo', 'value': -25, 'measure': 'relative'},
    {'entity': 'TARP Injection', 'value': 426, 'measure': 'relative'},
    {'entity': 'Total Impact', 'value': 0, 'measure': 'total'}
]

# Calculate cumulative values for waterfall
cumulative = 0
for i, item in enumerate(losses_data):
    if item['measure'] == 'absolute':
        cumulative = item['value']
        item['cumulative'] = cumulative
    elif item['measure'] == 'relative':
        item['base'] = cumulative
        cumulative += item['value']
        item['cumulative'] = cumulative
    else:  # total
        item['value'] = cumulative
        item['cumulative'] = cumulative

fig3 = go.Figure()

for i, item in enumerate(losses_data):
    if item['measure'] == 'absolute':
        fig3.add_trace(go.Bar(
            x=[item['entity']],
            y=[item['value']],
            marker_color='blue',
            name=item['entity'],
            showlegend=False
        ))
    elif item['measure'] == 'relative':
        color = 'red' if item['value'] < 0 else 'green'
        fig3.add_trace(go.Bar(
            x=[item['entity']],
            y=[abs(item['value'])],
            base=item['base'] if item['value'] > 0 else item['cumulative'],
            marker_color=color,
            name=item['entity'],
            text=f"${item['value']:+.0f}B",
            textposition='outside',
            showlegend=False
        ))
    else:  # total
        fig3.add_trace(go.Bar(
            x=[item['entity']],
            y=[item['value']],
            marker_color='purple',
            name=item['entity'],
            text=f"${item['value']:.0f}B",
            textposition='outside',
            showlegend=False
        ))

fig3.update_layout(
    title={
        'text': 'Financial Crisis Losses Waterfall (Billions USD)',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(title='Institution/Event'),
    yaxis=dict(title='Cumulative Loss/Gain ($B)'),
    showlegend=False,
    hovermode='x'
)

# Add a zero line
fig3.add_hline(y=0, line_dash="dash", line_color="gray")

register_plot(
    fig3,
    plot_id='losses_waterfall',
    metadata={
        'appearance': {
            'title': {'text': 'Crisis Losses Cascade'}
        }
    }
)