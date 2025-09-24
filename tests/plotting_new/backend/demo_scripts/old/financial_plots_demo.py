"""
Financial and time series plots demonstration script
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_financial_plots():
    """Create comprehensive financial plot demonstrations"""
    plots = []

    # Generate sample financial data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')

    # Generate stock price data
    price = 100
    prices = []
    for _ in range(len(dates)):
        change = np.random.randn() * 2
        price = max(price + change, 20)  # Prevent negative prices
        prices.append(price)

    # Generate OHLC data
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []

    for p in prices:
        daily_volatility = np.random.uniform(1, 5)
        open_price = p + np.random.uniform(-daily_volatility, daily_volatility)
        close_price = p + np.random.uniform(-daily_volatility, daily_volatility)
        high_price = max(open_price, close_price) + np.random.uniform(0, daily_volatility)
        low_price = min(open_price, close_price) - np.random.uniform(0, daily_volatility)

        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
        closes.append(close_price)
        volumes.append(np.random.randint(1000000, 10000000))

    # 1. Basic Candlestick Chart
    fig1 = go.Figure(data=[go.Candlestick(
        x=dates[:90],
        open=opens[:90],
        high=highs[:90],
        low=lows[:90],
        close=closes[:90]
    )])

    fig1.update_layout(
        title="1. Candlestick Chart - Stock Price Q1 2023",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        xaxis_rangeslider_visible=False
    )
    plots.append(('fin_1', fig1, {
        'appearance': {
            'title': {'text': 'Candlestick Chart', 'fontSize': 20}
        }
    }))

    # 2. OHLC Chart
    fig2 = go.Figure(data=[go.Ohlc(
        x=dates[90:180],
        open=opens[90:180],
        high=highs[90:180],
        low=lows[90:180],
        close=closes[90:180]
    )])

    fig2.update_layout(
        title="2. OHLC Chart - Stock Price Q2 2023",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        xaxis_rangeslider_visible=False
    )
    plots.append(('fin_2', fig2, {
        'appearance': {
            'title': {'text': 'OHLC Chart', 'fontSize': 20}
        }
    }))

    # 3. Candlestick with Volume
    fig3 = go.Figure()

    fig3.add_trace(go.Candlestick(
        x=dates[:60],
        open=opens[:60],
        high=highs[:60],
        low=lows[:60],
        close=closes[:60],
        name='Price'
    ))

    fig3.add_trace(go.Bar(
        x=dates[:60],
        y=volumes[:60],
        name='Volume',
        yaxis='y2',
        marker_color='lightblue',
        opacity=0.3
    ))

    fig3.update_layout(
        title="3. Candlestick with Volume",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        yaxis2=dict(
            title="Volume",
            overlaying='y',
            side='right'
        ),
        xaxis_rangeslider_visible=False
    )
    plots.append(('fin_3', fig3, {
        'appearance': {
            'title': {'text': 'Candlestick + Volume', 'fontSize': 20}
        }
    }))

    # 4. Waterfall Chart
    x_waterfall = ["Start", "Q1", "Q2", "Q3", "Q4", "Adjustments", "Total"]
    y_waterfall = [100, 30, -20, 45, -15, -10, None]

    fig4 = go.Figure(go.Waterfall(
        x=x_waterfall,
        y=y_waterfall,
        text=["100", "+30", "-20", "+45", "-15", "-10", "130"],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "green"}},
        decreasing={"marker": {"color": "red"}},
        totals={"marker": {"color": "blue"}}
    ))

    fig4.update_layout(
        title="4. Waterfall Chart - Annual Revenue Changes",
        xaxis_title="Period",
        yaxis_title="Revenue ($ Millions)",
        showlegend=False
    )
    plots.append(('fin_4', fig4, {
        'appearance': {
            'title': {'text': 'Waterfall Chart', 'fontSize': 20}
        }
    }))

    # 5. Time Series with Moving Averages
    fig5 = go.Figure()

    # Price line
    fig5.add_trace(go.Scatter(
        x=dates,
        y=prices,
        mode='lines',
        name='Daily Price',
        line=dict(color='blue', width=1)
    ))

    # 20-day moving average
    ma20 = pd.Series(prices).rolling(window=20).mean()
    fig5.add_trace(go.Scatter(
        x=dates,
        y=ma20,
        mode='lines',
        name='20-day MA',
        line=dict(color='orange', width=2)
    ))

    # 50-day moving average
    ma50 = pd.Series(prices).rolling(window=50).mean()
    fig5.add_trace(go.Scatter(
        x=dates,
        y=ma50,
        mode='lines',
        name='50-day MA',
        line=dict(color='red', width=2)
    ))

    fig5.update_layout(
        title="5. Time Series with Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price ($)"
    )
    plots.append(('fin_5', fig5, {
        'appearance': {
            'title': {'text': 'Moving Averages', 'fontSize': 20}
        }
    }))

    # 6. Bollinger Bands
    fig6 = go.Figure()

    # Calculate Bollinger Bands
    rolling_mean = pd.Series(prices).rolling(window=20).mean()
    rolling_std = pd.Series(prices).rolling(window=20).std()
    upper_band = rolling_mean + (rolling_std * 2)
    lower_band = rolling_mean - (rolling_std * 2)

    # Add bands
    fig6.add_trace(go.Scatter(
        x=dates,
        y=upper_band,
        mode='lines',
        name='Upper Band',
        line=dict(color='rgba(250, 128, 114, 0.3)'),
        showlegend=False
    ))

    fig6.add_trace(go.Scatter(
        x=dates,
        y=lower_band,
        mode='lines',
        name='Lower Band',
        line=dict(color='rgba(250, 128, 114, 0.3)'),
        fill='tonexty',
        fillcolor='rgba(250, 128, 114, 0.2)',
        showlegend=False
    ))

    # Add price and moving average
    fig6.add_trace(go.Scatter(
        x=dates,
        y=prices,
        mode='lines',
        name='Price',
        line=dict(color='blue', width=1)
    ))

    fig6.add_trace(go.Scatter(
        x=dates,
        y=rolling_mean,
        mode='lines',
        name='20-day MA',
        line=dict(color='orange', width=2)
    ))

    fig6.update_layout(
        title="6. Bollinger Bands",
        xaxis_title="Date",
        yaxis_title="Price ($)"
    )
    plots.append(('fin_6', fig6, {
        'appearance': {
            'title': {'text': 'Bollinger Bands', 'fontSize': 20}
        }
    }))

    # 7. Range Slider Chart
    fig7 = go.Figure()

    fig7.add_trace(go.Scatter(
        x=dates,
        y=prices,
        mode='lines',
        name='Price'
    ))

    fig7.update_layout(
        title="7. Time Series with Range Slider",
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        yaxis_title="Price ($)"
    )
    plots.append(('fin_7', fig7, {
        'appearance': {
            'title': {'text': 'Range Slider Chart', 'fontSize': 20}
        }
    }))

    # 8. Renko Chart (Simplified)
    # Simulate Renko-like data
    brick_size = 5
    renko_dates = []
    renko_values = []
    current_price = 100

    for i in range(50):
        renko_dates.append(dates[i*5])
        if np.random.random() > 0.5:
            current_price += brick_size
        else:
            current_price -= brick_size
        renko_values.append(current_price)

    fig8 = go.Figure()

    for i in range(1, len(renko_values)):
        color = 'green' if renko_values[i] > renko_values[i-1] else 'red'
        fig8.add_trace(go.Bar(
            x=[renko_dates[i]],
            y=[abs(renko_values[i] - renko_values[i-1])],
            base=min(renko_values[i], renko_values[i-1]),
            marker_color=color,
            showlegend=False,
            width=86400000  # 1 day in milliseconds
        ))

    fig8.update_layout(
        title="8. Renko-Style Chart",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        bargap=0.1
    )
    plots.append(('fin_8', fig8, {
        'appearance': {
            'title': {'text': 'Renko Chart', 'fontSize': 20}
        }
    }))

    # 9. Point and Figure (Simplified visualization)
    fig9 = go.Figure()

    # Create a simplified point and figure pattern
    x_pf = []
    y_pf = []
    symbols = []

    for i in range(10):
        for j in range(5):
            x_pf.append(i)
            y_pf.append(j * 5 + 80)
            symbols.append('X' if (i + j) % 2 == 0 else 'O')

    fig9.add_trace(go.Scatter(
        x=x_pf,
        y=y_pf,
        mode='text',
        text=symbols,
        textfont=dict(size=20),
        showlegend=False
    ))

    fig9.update_layout(
        title="9. Point & Figure Chart (Stylized)",
        xaxis=dict(showticklabels=False, showgrid=True),
        yaxis_title="Price Level ($)",
        plot_bgcolor='white'
    )
    plots.append(('fin_9', fig9, {
        'appearance': {
            'title': {'text': 'Point & Figure', 'fontSize': 20}
        }
    }))

    # 10. Funnel Chart for Sales Pipeline
    stages = ['Leads', 'Qualified', 'Proposal', 'Negotiation', 'Closed']
    values = [1000, 600, 400, 250, 100]

    fig10 = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        opacity=0.8,
        marker=dict(
            color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6']
        )
    ))

    fig10.update_layout(
        title="10. Sales Funnel - Pipeline Analysis"
    )
    plots.append(('fin_10', fig10, {
        'appearance': {
            'title': {'text': 'Sales Funnel', 'fontSize': 20}
        }
    }))

    # 11. Area Chart - Revenue Streams
    fig11 = go.Figure()

    revenue_streams = ['Product A', 'Product B', 'Product C', 'Services']
    months = pd.date_range(start='2023-01-01', periods=12, freq='M')

    for i, stream in enumerate(revenue_streams):
        values = np.random.randint(20, 100, 12) + i * 20
        fig11.add_trace(go.Scatter(
            x=months,
            y=values,
            mode='lines',
            name=stream,
            stackgroup='one',
            fillcolor=px.colors.qualitative.Set2[i]
        ))

    fig11.update_layout(
        title="11. Stacked Area - Revenue Streams",
        xaxis_title="Month",
        yaxis_title="Revenue ($1000s)"
    )
    plots.append(('fin_11', fig11, {
        'appearance': {
            'title': {'text': 'Stacked Area Chart', 'fontSize': 20}
        }
    }))

    # 12. Gauge Chart - KPI Dashboard
    fig12 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=75,
        delta={'reference': 60},
        title={'text': "Performance Score"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig12.update_layout(
        title="12. Gauge Chart - KPI Metric"
    )
    plots.append(('fin_12', fig12, {
        'appearance': {
            'title': {'text': 'Gauge Chart', 'fontSize': 20}
        }
    }))

    # 13. Indicator Cards
    fig13 = go.Figure()

    fig13.add_trace(go.Indicator(
        mode="number+delta",
        value=492,
        delta={'reference': 450, 'relative': True},
        title={'text': "Revenue<br><span style='font-size:0.8em'>Q1 2023</span>"},
        domain={'x': [0, 0.3], 'y': [0.5, 1]}
    ))

    fig13.add_trace(go.Indicator(
        mode="number+delta",
        value=325,
        delta={'reference': 300},
        title={'text': "Costs<br><span style='font-size:0.8em'>Q1 2023</span>"},
        domain={'x': [0.35, 0.65], 'y': [0.5, 1]}
    ))

    fig13.add_trace(go.Indicator(
        mode="number+delta",
        value=167,
        delta={'reference': 150},
        title={'text': "Profit<br><span style='font-size:0.8em'>Q1 2023</span>"},
        domain={'x': [0.7, 1], 'y': [0.5, 1]}
    ))

    fig13.update_layout(
        title="13. Financial KPI Dashboard"
    )
    plots.append(('fin_13', fig13, {
        'appearance': {
            'title': {'text': 'KPI Dashboard', 'fontSize': 20}
        }
    }))

    # 14. Heikin-Ashi Chart (Modified Candlestick)
    # Calculate Heikin-Ashi values
    ha_close = [(opens[i] + highs[i] + lows[i] + closes[i]) / 4 for i in range(len(opens))]
    ha_open = [(opens[0] + closes[0]) / 2]

    for i in range(1, len(opens)):
        ha_open.append((ha_open[i-1] + ha_close[i-1]) / 2)

    ha_high = [max(highs[i], ha_open[i], ha_close[i]) for i in range(len(highs))]
    ha_low = [min(lows[i], ha_open[i], ha_close[i]) for i in range(len(lows))]

    fig14 = go.Figure(data=[go.Candlestick(
        x=dates[:60],
        open=ha_open[:60],
        high=ha_high[:60],
        low=ha_low[:60],
        close=ha_close[:60]
    )])

    fig14.update_layout(
        title="14. Heikin-Ashi Chart - Smoothed Price Action",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        xaxis_rangeslider_visible=False
    )
    plots.append(('fin_14', fig14, {
        'appearance': {
            'title': {'text': 'Heikin-Ashi Chart', 'fontSize': 20}
        }
    }))

    # 15. MACD Indicator
    fig15 = go.Figure()

    # Calculate MACD
    exp12 = pd.Series(prices).ewm(span=12, adjust=False).mean()
    exp26 = pd.Series(prices).ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal

    # Price subplot
    fig15.add_trace(go.Scatter(
        x=dates,
        y=prices,
        mode='lines',
        name='Price',
        yaxis='y2'
    ))

    # MACD subplot
    fig15.add_trace(go.Scatter(
        x=dates,
        y=macd,
        mode='lines',
        name='MACD',
        line=dict(color='blue')
    ))

    fig15.add_trace(go.Scatter(
        x=dates,
        y=signal,
        mode='lines',
        name='Signal',
        line=dict(color='red')
    ))

    fig15.add_trace(go.Bar(
        x=dates,
        y=histogram,
        name='Histogram',
        marker_color='gray',
        opacity=0.3
    ))

    fig15.update_layout(
        title="15. MACD Indicator",
        yaxis=dict(title="MACD", side="right"),
        yaxis2=dict(title="Price ($)", overlaying='y', side='left'),
        xaxis_title="Date"
    )
    plots.append(('fin_15', fig15, {
        'appearance': {
            'title': {'text': 'MACD Indicator', 'fontSize': 20}
        }
    }))

    # 16. RSI Indicator
    fig16 = go.Figure()

    # Calculate RSI
    delta = pd.Series(prices).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    fig16.add_trace(go.Scatter(
        x=dates,
        y=rsi,
        mode='lines',
        name='RSI',
        line=dict(color='purple', width=2)
    ))

    # Add overbought/oversold lines
    fig16.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig16.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")

    fig16.update_layout(
        title="16. RSI (Relative Strength Index)",
        xaxis_title="Date",
        yaxis_title="RSI",
        yaxis=dict(range=[0, 100])
    )
    plots.append(('fin_16', fig16, {
        'appearance': {
            'title': {'text': 'RSI Indicator', 'fontSize': 20}
        }
    }))

    # 17. Correlation Heatmap
    # Generate correlated asset returns
    n_assets = 8
    asset_names = [f'Asset {chr(65+i)}' for i in range(n_assets)]
    returns = np.random.multivariate_normal(
        np.zeros(n_assets),
        np.eye(n_assets) + np.random.rand(n_assets, n_assets) * 0.3,
        250
    )

    correlation_matrix = np.corrcoef(returns.T)

    fig17 = go.Figure(data=go.Heatmap(
        z=correlation_matrix,
        x=asset_names,
        y=asset_names,
        colorscale='RdBu',
        zmid=0,
        text=np.round(correlation_matrix, 2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))

    fig17.update_layout(
        title="17. Asset Correlation Matrix",
        xaxis_title="Assets",
        yaxis_title="Assets"
    )
    plots.append(('fin_17', fig17, {
        'appearance': {
            'title': {'text': 'Correlation Matrix', 'fontSize': 20}
        }
    }))

    # 18. Portfolio Allocation Pie
    allocations = {
        'Stocks': 40,
        'Bonds': 30,
        'Real Estate': 15,
        'Commodities': 10,
        'Cash': 5
    }

    fig18 = go.Figure(data=[go.Pie(
        labels=list(allocations.keys()),
        values=list(allocations.values()),
        hole=.4,
        marker=dict(colors=px.colors.qualitative.Set3)
    )])

    fig18.update_layout(
        title="18. Portfolio Allocation",
        annotations=[dict(text='Portfolio', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    plots.append(('fin_18', fig18, {
        'appearance': {
            'title': {'text': 'Portfolio Allocation', 'fontSize': 20}
        }
    }))

    # 19. Cumulative Returns
    fig19 = go.Figure()

    # Generate multiple asset returns
    for i in range(3):
        returns = np.random.randn(len(dates)) * 0.02
        cumulative = (1 + pd.Series(returns)).cumprod() * 100

        fig19.add_trace(go.Scatter(
            x=dates,
            y=cumulative,
            mode='lines',
            name=f'Strategy {i+1}',
            line=dict(width=2)
        ))

    # Add benchmark
    benchmark = (1 + pd.Series(np.random.randn(len(dates)) * 0.015)).cumprod() * 100
    fig19.add_trace(go.Scatter(
        x=dates,
        y=benchmark,
        mode='lines',
        name='Benchmark',
        line=dict(color='black', width=2, dash='dash')
    ))

    fig19.update_layout(
        title="19. Cumulative Returns Comparison",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (%)"
    )
    plots.append(('fin_19', fig19, {
        'appearance': {
            'title': {'text': 'Cumulative Returns', 'fontSize': 20}
        }
    }))

    # 20. Risk-Return Scatter
    np.random.seed(42)
    n_assets = 15
    expected_returns = np.random.uniform(0.05, 0.20, n_assets)
    risk = np.random.uniform(0.10, 0.30, n_assets)
    sharpe_ratio = expected_returns / risk

    fig20 = go.Figure()

    fig20.add_trace(go.Scatter(
        x=risk,
        y=expected_returns,
        mode='markers+text',
        text=[f'Asset {i+1}' for i in range(n_assets)],
        textposition='top center',
        marker=dict(
            size=sharpe_ratio * 50,
            color=sharpe_ratio,
            colorscale='viridis',
            showscale=True,
            colorbar=dict(title="Sharpe Ratio")
        )
    ))

    # Add efficient frontier curve (simplified)
    eff_risk = np.linspace(min(risk), max(risk), 50)
    eff_return = 0.05 + (eff_risk - 0.1) ** 2 * 0.8

    fig20.add_trace(go.Scatter(
        x=eff_risk,
        y=eff_return,
        mode='lines',
        name='Efficient Frontier',
        line=dict(color='red', width=2, dash='dash')
    ))

    fig20.update_layout(
        title="20. Risk-Return Analysis",
        xaxis_title="Risk (Standard Deviation)",
        yaxis_title="Expected Return",
        xaxis=dict(tickformat='.0%'),
        yaxis=dict(tickformat='.0%')
    )
    plots.append(('fin_20', fig20, {
        'appearance': {
            'title': {'text': 'Risk-Return Analysis', 'fontSize': 20}
        }
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} financial plot demonstrations"

# Execute when module is run
if __name__ == "__main__" or True:  # Always execute when imported
    result = create_financial_plots()
    print(result)