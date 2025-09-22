"""
Comprehensive Line Plots Demo
Showcases all different flavors and variations of line plots available in Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Generate sample data
np.random.seed(42)

def create_line_plots():
    plots = []

    # 1. Basic Line Plot
    x_basic = np.linspace(0, 10, 100)
    y_basic = np.sin(x_basic)

    fig1 = go.Figure(data=go.Scatter(
        x=x_basic,
        y=y_basic,
        mode='lines',
        name='Sine Wave',
        line=dict(color='blue', width=2)
    ))
    fig1.update_layout(
        title="1. Basic Line Plot",
        xaxis_title="X Axis",
        yaxis_title="Y Axis"
    )
    plots.append(("line_basic", fig1, {"title": "Basic Line Plot"}))

    # 2. Multiple Line Series
    x_multi = np.linspace(0, 10, 100)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=x_multi, y=np.sin(x_multi),
                    mode='lines', name='sin(x)',
                    line=dict(color='blue', width=2)))
    fig2.add_trace(go.Scatter(x=x_multi, y=np.cos(x_multi),
                    mode='lines', name='cos(x)',
                    line=dict(color='red', width=2)))
    fig2.add_trace(go.Scatter(x=x_multi, y=np.sin(x_multi) * 0.5,
                    mode='lines', name='0.5*sin(x)',
                    line=dict(color='green', width=2)))

    fig2.update_layout(
        title="2. Multiple Line Series",
        xaxis_title="X",
        yaxis_title="Y",
        hovermode='x unified'
    )
    plots.append(("line_multiple", fig2, {"title": "Multiple Lines"}))

    # 3. Line with Different Styles
    x_styles = np.linspace(0, 10, 50)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=x_styles, y=np.sin(x_styles),
                    mode='lines', name='Solid',
                    line=dict(color='blue', width=2, dash='solid')))
    fig3.add_trace(go.Scatter(x=x_styles, y=np.sin(x_styles) + 1,
                    mode='lines', name='Dash',
                    line=dict(color='red', width=2, dash='dash')))
    fig3.add_trace(go.Scatter(x=x_styles, y=np.sin(x_styles) + 2,
                    mode='lines', name='Dot',
                    line=dict(color='green', width=2, dash='dot')))
    fig3.add_trace(go.Scatter(x=x_styles, y=np.sin(x_styles) + 3,
                    mode='lines', name='Dash-Dot',
                    line=dict(color='purple', width=2, dash='dashdot')))

    fig3.update_layout(
        title="3. Line Styles (Solid, Dash, Dot, DashDot)",
        xaxis_title="X",
        yaxis_title="Y"
    )
    plots.append(("line_styles", fig3, {"title": "Line Styles"}))

    # 4. Smoothed Lines (Spline)
    x_smooth = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    y_smooth = np.array([1, 3, 2, 5, 4, 7, 6, 8, 7, 9, 8])

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=x_smooth, y=y_smooth,
                    mode='lines', name='Linear',
                    line=dict(color='blue', width=2)))
    fig4.add_trace(go.Scatter(x=x_smooth, y=y_smooth + 2,
                    mode='lines', name='Spline',
                    line=dict(color='red', width=2, shape='spline')))
    fig4.add_trace(go.Scatter(x=x_smooth, y=y_smooth + 4,
                    name='Linear + Markers',
                    mode='lines+markers',
                    line=dict(color='green', width=2),
                    marker=dict(size=8)))

    fig4.update_layout(
        title="4. Line Interpolation (Linear vs Spline)",
        xaxis_title="X",
        yaxis_title="Y"
    )
    plots.append(("line_smooth", fig4, {"title": "Smoothed Lines"}))

    # 5. Step Lines
    x_step = np.arange(0, 10, 1)
    y_step = np.random.randint(0, 10, 10)

    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=x_step, y=y_step,
                    mode='lines', name='Linear',
                    line=dict(color='blue', width=2)))
    fig5.add_trace(go.Scatter(x=x_step, y=y_step + 5,
                    mode='lines', name='hv Step',
                    line=dict(color='red', width=2, shape='hv')))
    fig5.add_trace(go.Scatter(x=x_step, y=y_step + 10,
                    mode='lines', name='vh Step',
                    line=dict(color='green', width=2, shape='vh')))
    fig5.add_trace(go.Scatter(x=x_step, y=y_step + 15,
                    mode='lines', name='hvh Step',
                    line=dict(color='purple', width=2, shape='hvh')))

    fig5.update_layout(
        title="5. Step Lines (Different Step Modes)",
        xaxis_title="X",
        yaxis_title="Y"
    )
    plots.append(("line_step", fig5, {"title": "Step Lines"}))

    # 6. Area Chart (Filled Lines)
    x_area = np.linspace(0, 10, 100)
    y_area1 = np.sin(x_area) + 2
    y_area2 = np.cos(x_area) + 2

    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=x_area, y=y_area1,
        mode='lines',
        name='Dataset 1',
        fill='tozeroy',
        line=dict(color='blue', width=2)
    ))
    fig6.add_trace(go.Scatter(
        x=x_area, y=y_area2,
        mode='lines',
        name='Dataset 2',
        fill='tozeroy',
        line=dict(color='red', width=2),
        fillcolor='rgba(255,0,0,0.3)'
    ))

    fig6.update_layout(
        title="6. Area Chart (Filled Lines)",
        xaxis_title="X",
        yaxis_title="Y"
    )
    plots.append(("line_area", fig6, {"title": "Area Chart"}))

    # 7. Stacked Area Chart
    x_stacked = np.linspace(0, 10, 50)
    y1_stacked = np.abs(np.sin(x_stacked)) + 0.5
    y2_stacked = np.abs(np.cos(x_stacked)) + 0.5
    y3_stacked = np.abs(np.sin(x_stacked * 2)) + 0.5

    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=x_stacked, y=y1_stacked,
        mode='lines',
        name='Layer 1',
        stackgroup='one',
        fillcolor='rgba(255,0,0,0.5)',
        line=dict(width=0.5, color='rgb(255,0,0)')
    ))
    fig7.add_trace(go.Scatter(
        x=x_stacked, y=y2_stacked,
        mode='lines',
        name='Layer 2',
        stackgroup='one',
        fillcolor='rgba(0,255,0,0.5)',
        line=dict(width=0.5, color='rgb(0,255,0)')
    ))
    fig7.add_trace(go.Scatter(
        x=x_stacked, y=y3_stacked,
        mode='lines',
        name='Layer 3',
        stackgroup='one',
        fillcolor='rgba(0,0,255,0.5)',
        line=dict(width=0.5, color='rgb(0,0,255)')
    ))

    fig7.update_layout(
        title="7. Stacked Area Chart",
        xaxis_title="Time",
        yaxis_title="Value"
    )
    plots.append(("line_stacked_area", fig7, {"title": "Stacked Area"}))

    # 8. Time Series Line Plot
    dates = pd.date_range(start='2024-01-01', periods=365, freq='D')
    values = np.cumsum(np.random.randn(365)) + 100

    fig8 = go.Figure()
    fig8.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        name='Stock Price',
        line=dict(color='darkblue', width=1.5)
    ))

    # Add range slider
    fig8.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    fig8.update_layout(
        title="8. Time Series with Range Slider",
        xaxis_title="Date",
        yaxis_title="Price"
    )
    plots.append(("line_timeseries", fig8, {"title": "Time Series"}))

    # 9. Candlestick Chart (Financial)
    dates_candle = pd.date_range(start='2024-01-01', periods=100, freq='D')
    open_price = np.random.randn(100).cumsum() + 100
    close_price = open_price + np.random.randn(100) * 2
    high_price = np.maximum(open_price, close_price) + np.abs(np.random.randn(100))
    low_price = np.minimum(open_price, close_price) - np.abs(np.random.randn(100))

    fig9 = go.Figure(data=[go.Candlestick(
        x=dates_candle,
        open=open_price,
        high=high_price,
        low=low_price,
        close=close_price,
        name='OHLC'
    )])

    fig9.update_layout(
        title="9. Candlestick Chart (Financial)",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False
    )
    plots.append(("line_candlestick", fig9, {"title": "Candlestick"}))

    # 10. OHLC Chart
    fig10 = go.Figure(data=[go.Ohlc(
        x=dates_candle[:50],
        open=open_price[:50],
        high=high_price[:50],
        low=low_price[:50],
        close=close_price[:50],
        name='OHLC'
    )])

    fig10.update_layout(
        title="10. OHLC Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False
    )
    plots.append(("line_ohlc", fig10, {"title": "OHLC Chart"}))

    # 11. Line Plot with Confidence Bands
    x_conf = np.linspace(0, 10, 100)
    y_mean = np.sin(x_conf)
    y_upper = y_mean + 0.5
    y_lower = y_mean - 0.5

    fig11 = go.Figure()

    # Add confidence band
    fig11.add_trace(go.Scatter(
        x=np.concatenate([x_conf, x_conf[::-1]]),
        y=np.concatenate([y_upper, y_lower[::-1]]),
        fill='toself',
        fillcolor='rgba(0,100,200,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False
    ))

    # Add mean line
    fig11.add_trace(go.Scatter(
        x=x_conf,
        y=y_mean,
        mode='lines',
        name='Mean',
        line=dict(color='rgb(0,100,200)', width=2)
    ))

    fig11.update_layout(
        title="11. Line with Confidence Bands",
        xaxis_title="X",
        yaxis_title="Y"
    )
    plots.append(("line_confidence", fig11, {"title": "Confidence Bands"}))

    # 12. Gradient Line (Color changing along line)
    x_gradient = np.linspace(0, 10, 500)
    y_gradient = np.sin(x_gradient) * np.exp(-x_gradient/10)

    fig12 = go.Figure(data=go.Scatter(
        x=x_gradient,
        y=y_gradient,
        mode='markers+lines',
        marker=dict(
            size=3,
            color=x_gradient,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="X Value")
        ),
        line=dict(width=2, color='darkgray')
    ))

    fig12.update_layout(
        title="12. Gradient Color Line",
        xaxis_title="X",
        yaxis_title="Y"
    )
    plots.append(("line_gradient", fig12, {"title": "Gradient Line"}))

    # 13. Polar Line Plot
    theta = np.linspace(0, 2*np.pi, 100)
    r = 2 * np.sin(4*theta)

    fig13 = go.Figure(data=go.Scatterpolar(
        r=r,
        theta=theta*180/np.pi,
        mode='lines',
        name='Rose Curve',
        line=dict(color='magenta', width=2)
    ))

    fig13.update_layout(
        title="13. Polar Line Plot (Rose Curve)",
        polar=dict(
            radialaxis=dict(visible=True, range=[-2.5, 2.5])
        ),
        showlegend=False
    )
    plots.append(("line_polar", fig13, {"title": "Polar Line"}))

    # 14. 3D Line Plot
    t = np.linspace(0, 10*np.pi, 1000)
    x_3d = np.sin(t)
    y_3d = np.cos(t)
    z_3d = t/10

    fig14 = go.Figure(data=[go.Scatter3d(
        x=x_3d,
        y=y_3d,
        z=z_3d,
        mode='lines',
        line=dict(
            color=z_3d,
            colorscale='Viridis',
            width=4
        )
    )])

    fig14.update_layout(
        title="14. 3D Line Plot (Helix)",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )
    plots.append(("line_3d", fig14, {"title": "3D Line"}))

    # 15. Sparklines (Multiple Small Lines)
    fig15 = go.Figure()

    for i in range(6):
        y_spark = np.random.randn(50).cumsum() + i*10
        fig15.add_trace(go.Scatter(
            x=np.arange(50),
            y=y_spark,
            mode='lines',
            name=f'Series {i+1}',
            line=dict(width=1)
        ))

    fig15.update_layout(
        title="15. Sparklines (Multiple Trends)",
        xaxis_title="Time",
        yaxis_title="Value"
    )
    plots.append(("line_sparklines", fig15, {"title": "Sparklines"}))

    # 16. Connected Scatterplot (Line with Direction)
    t_connected = np.linspace(0, 2*np.pi, 30)
    x_connected = np.sin(t_connected) + np.random.randn(30) * 0.1
    y_connected = np.cos(t_connected) + np.random.randn(30) * 0.1

    fig16 = go.Figure(data=go.Scatter(
        x=x_connected,
        y=y_connected,
        mode='lines+markers+text',
        marker=dict(size=8, color=np.arange(30), colorscale='Plasma', showscale=True),
        text=[f'{i}' for i in range(30)],
        textposition="top center",
        textfont=dict(size=8),
        line=dict(width=1, color='gray')
    ))

    fig16.update_layout(
        title="16. Connected Scatterplot with Sequence",
        xaxis_title="X",
        yaxis_title="Y"
    )
    plots.append(("line_connected", fig16, {"title": "Connected Scatter"}))

    # 17. Waterfall Chart (Cumulative)
    categories = ['Start', 'Q1', 'Q2', 'Q3', 'Q4', 'Total']
    values = [100, 30, -20, 40, -10, None]

    # Calculate cumulative values
    cumulative = [100, 130, 110, 150, 140, 140]

    fig17 = go.Figure(go.Waterfall(
        name="Revenue",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "total"],
        x=categories,
        y=values,
        text=[f"+{v}" if v and v > 0 else str(v) if v else "140" for v in values],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))

    fig17.update_layout(
        title="17. Waterfall Chart",
        xaxis_title="Quarter",
        yaxis_title="Revenue",
        showlegend=False
    )
    plots.append(("line_waterfall", fig17, {"title": "Waterfall Chart"}))

    # 18. Ridgeline Plot (Joy Plot)
    fig18 = go.Figure()

    for i in range(5):
        y_ridge = np.random.randn(100) + i*3
        x_ridge = np.linspace(-3, 3, 100)

        fig18.add_trace(go.Scatter(
            x=x_ridge,
            y=y_ridge,
            mode='lines',
            name=f'Distribution {i+1}',
            fill='tonexty' if i > 0 else 'tozeroy',
            line=dict(width=1.5)
        ))

    fig18.update_layout(
        title="18. Ridgeline Plot (Overlapping Distributions)",
        xaxis_title="Value",
        yaxis_title="Distribution",
        showlegend=True
    )
    plots.append(("line_ridgeline", fig18, {"title": "Ridgeline Plot"}))

    # 19. Logarithmic Scale Line
    x_log = np.linspace(1, 100, 100)
    y_exp = np.exp(x_log/20)
    y_power = x_log**2
    y_log = np.log(x_log) * 100

    fig19 = go.Figure()
    fig19.add_trace(go.Scatter(x=x_log, y=y_exp, mode='lines', name='Exponential'))
    fig19.add_trace(go.Scatter(x=x_log, y=y_power, mode='lines', name='Power'))
    fig19.add_trace(go.Scatter(x=x_log, y=y_log, mode='lines', name='Logarithmic'))

    fig19.update_layout(
        title="19. Lines with Log Scale",
        xaxis_title="X (linear)",
        yaxis_title="Y (log scale)",
        yaxis_type="log"
    )
    plots.append(("line_logscale", fig19, {"title": "Log Scale Lines"}))

    # 20. Dual Axis Line Plot
    x_dual = np.linspace(0, 10, 100)
    y1_dual = np.sin(x_dual) * 100
    y2_dual = np.exp(x_dual/5)

    fig20 = go.Figure()

    fig20.add_trace(go.Scatter(
        x=x_dual,
        y=y1_dual,
        mode='lines',
        name='Sin (left axis)',
        line=dict(color='blue', width=2)
    ))

    fig20.add_trace(go.Scatter(
        x=x_dual,
        y=y2_dual,
        mode='lines',
        name='Exp (right axis)',
        yaxis='y2',
        line=dict(color='red', width=2)
    ))

    fig20.update_layout(
        title="20. Dual Y-Axis Line Plot",
        xaxis_title="X",
        yaxis=dict(
            title=dict(text="Sin Values", font=dict(color="blue")),
            tickfont=dict(color="blue")
        ),
        yaxis2=dict(
            title=dict(text="Exp Values", font=dict(color="red")),
            tickfont=dict(color="red"),
            anchor="x",
            overlaying="y",
            side="right"
        )
    )
    plots.append(("line_dual_axis", fig20, {"title": "Dual Axis"}))

    return plots

# Execute and register plots
if __name__ == "__main__" or True:  # Always execute when imported
    plots = create_line_plots()
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)