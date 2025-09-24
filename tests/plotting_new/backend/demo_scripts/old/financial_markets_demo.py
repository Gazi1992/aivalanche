"""
Financial Markets Demo
Real-world financial examples including stock prices, portfolio analysis, and risk metrics
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_financial_plots():
    """Create financial market visualizations"""
    plots = []

    # 1. Candlestick Chart - Stock Prices
    dates = pd.date_range('2024-01-01', periods=90, freq='D')
    # Simulate stock price data
    np.random.seed(42)
    price_walk = 100 + np.cumsum(np.random.randn(90) * 2)

    open_prices = price_walk + np.random.randn(90) * 0.5
    close_prices = open_prices + np.random.randn(90) * 2
    high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.randn(90) * 1)
    low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.randn(90) * 1)

    fig1 = go.Figure(data=[go.Candlestick(
        x=dates,
        open=open_prices,
        high=high_prices,
        low=low_prices,
        close=close_prices,
        name='TECH Corp',
        increasing_line_color='green',
        decreasing_line_color='red'
    )])

    # Add moving average
    ma20 = pd.Series(close_prices).rolling(window=20).mean()
    fig1.add_trace(go.Scatter(
        x=dates, y=ma20,
        mode='lines',
        name='20-day MA',
        line=dict(color='blue', width=1)
    ))

    fig1.update_layout(
        title="TECH Corp Stock Price (with 20-day Moving Average)",
        yaxis_title="Price ($)",
        xaxis_rangeslider_visible=False
    )
    plots.append(('fin_candlestick', fig1, {
        'appearance': {'title': {'text': 'Stock Price Chart'}}
    }))

    # 2. Portfolio Composition - Donut Chart
    assets = ['Stocks', 'Bonds', 'Real Estate', 'Commodities', 'Cash']
    allocation = [45, 25, 15, 10, 5]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']

    fig2 = go.Figure(data=[go.Pie(
        labels=assets,
        values=allocation,
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textinfo='label+percent',
        textposition='outside'
    )])

    fig2.update_layout(
        title="Portfolio Asset Allocation",
        annotations=[dict(
            text='$1.2M<br>Total',
            x=0.5, y=0.5,
            font_size=20,
            showarrow=False
        )]
    )
    plots.append(('fin_portfolio', fig2, {
        'appearance': {'title': {'text': 'Portfolio Allocation'}}
    }))

    # 3. Risk Correlation Heatmap
    assets_corr = ['S&P 500', 'NASDAQ', 'Bonds', 'Gold', 'Oil', 'EUR/USD', 'Real Estate', 'Bitcoin']
    # Create realistic correlation matrix
    corr_matrix = np.array([
        [1.00, 0.95, -0.20, 0.15, 0.35, 0.10, 0.65, 0.30],  # S&P 500
        [0.95, 1.00, -0.25, 0.10, 0.30, 0.05, 0.60, 0.40],  # NASDAQ
        [-0.20, -0.25, 1.00, 0.30, -0.15, -0.10, 0.20, -0.35],  # Bonds
        [0.15, 0.10, 0.30, 1.00, 0.25, -0.40, 0.30, 0.20],  # Gold
        [0.35, 0.30, -0.15, 0.25, 1.00, 0.20, 0.40, 0.15],  # Oil
        [0.10, 0.05, -0.10, -0.40, 0.20, 1.00, 0.15, 0.10],  # EUR/USD
        [0.65, 0.60, 0.20, 0.30, 0.40, 0.15, 1.00, 0.25],  # Real Estate
        [0.30, 0.40, -0.35, 0.20, 0.15, 0.10, 0.25, 1.00],  # Bitcoin
    ])

    fig3 = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=assets_corr,
        y=assets_corr,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))

    fig3.update_layout(
        title="Asset Correlation Matrix",
        xaxis_title="Assets",
        yaxis_title="Assets"
    )
    plots.append(('fin_correlation', fig3, {
        'appearance': {'title': {'text': 'Risk Correlation'}}
    }))

    # 4. Trading Volume Area Chart
    dates_volume = pd.date_range('2024-01-01', periods=30, freq='D')
    volume = np.abs(np.random.randn(30) * 1000000 + 5000000)
    price = 100 + np.cumsum(np.random.randn(30) * 1.5)

    fig4 = go.Figure()

    # Volume as area chart
    fig4.add_trace(go.Scatter(
        x=dates_volume,
        y=volume,
        mode='lines',
        fill='tozeroy',
        name='Volume',
        line=dict(color='lightblue', width=1),
        yaxis='y2'
    ))

    # Price as line
    fig4.add_trace(go.Scatter(
        x=dates_volume,
        y=price,
        mode='lines+markers',
        name='Price',
        line=dict(color='darkblue', width=2),
        marker=dict(size=4),
        yaxis='y'
    ))

    fig4.update_layout(
        title="Price & Volume Analysis",
        xaxis_title="Date",
        yaxis=dict(title="Price ($)", side="left"),
        yaxis2=dict(title="Volume", overlaying="y", side="right"),
        hovermode='x unified'
    )
    plots.append(('fin_volume', fig4, {
        'appearance': {'title': {'text': 'Price & Volume'}}
    }))

    # 5. OHLC Chart - Currency Exchange
    dates_fx = pd.date_range('2024-01-01', periods=60, freq='D')
    # Simulate EUR/USD exchange rate
    fx_walk = 1.10 + np.cumsum(np.random.randn(60) * 0.005)

    open_fx = fx_walk + np.random.randn(60) * 0.002
    close_fx = open_fx + np.random.randn(60) * 0.003
    high_fx = np.maximum(open_fx, close_fx) + np.abs(np.random.randn(60) * 0.002)
    low_fx = np.minimum(open_fx, close_fx) - np.abs(np.random.randn(60) * 0.002)

    fig5 = go.Figure(data=[go.Ohlc(
        x=dates_fx,
        open=open_fx,
        high=high_fx,
        low=low_fx,
        close=close_fx,
        name='EUR/USD'
    )])

    fig5.update_layout(
        title="EUR/USD Exchange Rate",
        yaxis_title="Exchange Rate",
        xaxis_rangeslider_visible=False
    )
    plots.append(('fin_forex', fig5, {
        'appearance': {'title': {'text': 'Currency Exchange'}}
    }))

    # 6. Market Performance Indicators
    fig6 = go.Figure()

    # Market sentiment gauge
    fig6.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=72,
        title={'text': "Market Sentiment"},
        delta={'reference': 65, 'increasing': {'color': "green"}},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "darkgreen"},
               'steps': [
                   {'range': [0, 25], 'color': "red"},
                   {'range': [25, 50], 'color': "orange"},
                   {'range': [50, 75], 'color': "yellow"},
                   {'range': [75, 100], 'color': "green"}],
               'threshold': {'line': {'color': "black", 'width': 4},
                           'thickness': 0.75, 'value': 50}},
        domain={'x': [0, 0.45], 'y': [0.5, 1]}
    ))

    # VIX volatility indicator
    fig6.add_trace(go.Indicator(
        mode="number+delta",
        value=18.5,
        title={'text': "VIX Volatility Index"},
        delta={'reference': 22.0, 'decreasing': {'color': "green"}},
        domain={'x': [0.55, 1], 'y': [0.5, 1]}
    ))

    # P/E Ratio indicator
    fig6.add_trace(go.Indicator(
        mode="number+delta",
        value=21.3,
        title={'text': "S&P 500 P/E Ratio"},
        delta={'reference': 19.5},
        domain={'x': [0, 0.45], 'y': [0, 0.45]}
    ))

    # Yield indicator
    fig6.add_trace(go.Indicator(
        mode="number+delta",
        value=4.25,
        title={'text': "10-Year Treasury Yield (%)"},
        delta={'reference': 3.80, 'suffix': "%"},
        domain={'x': [0.55, 1], 'y': [0, 0.45]}
    ))

    fig6.update_layout(
        title="Market Indicators Dashboard",
    )
    plots.append(('fin_indicators', fig6, {
        'appearance': {'title': {'text': 'Market Indicators'}}
    }))

    # 7. Sector Performance Scatter
    sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer',
               'Industrial', 'Utilities', 'Real Estate', 'Materials', 'Telecom']
    returns = [15.2, 8.5, 12.3, -5.2, 6.7, 9.1, 3.2, 4.5, 7.8, 1.2]
    volatility = [22.5, 18.3, 20.1, 28.5, 15.2, 19.8, 12.3, 16.5, 21.2, 14.7]
    market_cap = [500, 350, 400, 250, 300, 280, 180, 200, 220, 150]

    fig7 = go.Figure(data=[go.Scatter(
        x=volatility,
        y=returns,
        mode='markers+text',
        text=sectors,
        textposition='top center',
        marker=dict(
            size=[m/10 for m in market_cap],
            color=returns,
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Return (%)"),
            line=dict(width=1, color='white')
        )
    )])

    # Add quadrant lines
    fig7.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig7.add_vline(x=20, line_dash="dash", line_color="gray", opacity=0.5)

    fig7.update_layout(
        title="Sector Risk-Return Analysis",
        xaxis_title="Volatility (%)",
        yaxis_title="Return (%)",
    )
    plots.append(('fin_sectors', fig7, {
        'appearance': {'title': {'text': 'Sector Performance'}}
    }))

    # 8. Options Strategy - Ternary Plot
    # Showing portfolio allocation between stocks, options, and bonds
    n_portfolios = 50
    stocks_pct = np.random.dirichlet([2, 1, 1], n_portfolios)
    returns_sim = stocks_pct[:, 0] * 12 + stocks_pct[:, 1] * 8 + stocks_pct[:, 2] * 4

    fig8 = go.Figure(go.Scatterternary(
        a=stocks_pct[:, 0] * 100,
        b=stocks_pct[:, 1] * 100,
        c=stocks_pct[:, 2] * 100,
        mode='markers',
        marker=dict(
            size=8,
            color=returns_sim,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Expected Return (%)")
        ),
        text=[f"Return: {r:.1f}%" for r in returns_sim],
        hovertemplate='Stocks: %{a:.0f}%<br>Options: %{b:.0f}%<br>Bonds: %{c:.0f}%<extra></extra>'
    ))

    fig8.update_layout(
        title="Portfolio Optimization - Risk Assets Mix",
        ternary=dict(
            aaxis=dict(title='Stocks %', min=0, linewidth=2),
            baxis=dict(title='Options %', min=0, linewidth=2),
            caxis=dict(title='Bonds %', min=0, linewidth=2),
        )
    )
    plots.append(('fin_portfolio_ternary', fig8, {
        'appearance': {'title': {'text': 'Portfolio Mix'}}
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} financial market visualizations"

# Execute when imported or run
if __name__ == "__main__" or True:
    result = create_financial_plots()
    print(result)