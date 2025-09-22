"""
Comprehensive Scatter Plots Demo
Showcases all different flavors and variations of scatter plots available in Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Generate sample data
np.random.seed(42)

def create_scatter_plots():
    plots = []

    # 1. Basic Scatter Plot
    x_basic = np.random.randn(100)
    y_basic = np.random.randn(100)

    fig1 = go.Figure(data=go.Scatter(
        x=x_basic,
        y=y_basic,
        mode='markers',
        name='Random Points',
        marker=dict(size=8, color='blue')
    ))
    fig1.update_layout(
        title="1. Basic Scatter Plot",
        xaxis_title="X Axis",
        yaxis_title="Y Axis"
    )
    plots.append(("scatter_basic", fig1, {"title": "Basic Scatter Plot"}))

    # 2. Scatter with Color Gradient
    x_gradient = np.random.randn(200)
    y_gradient = np.random.randn(200)
    colors = np.random.randn(200)

    fig2 = go.Figure(data=go.Scatter(
        x=x_gradient,
        y=y_gradient,
        mode='markers',
        marker=dict(
            size=10,
            color=colors,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Value")
        ),
        text=[f"Point {i}" for i in range(200)],
        hovertemplate='X: %{x:.2f}<br>Y: %{y:.2f}<br>Color: %{marker.color:.2f}<extra></extra>'
    ))
    fig2.update_layout(
        title="2. Scatter with Color Gradient",
        xaxis_title="X Values",
        yaxis_title="Y Values"
    )
    plots.append(("scatter_gradient", fig2, {"title": "Scatter with Color Gradient"}))

    # 3. Bubble Chart (Size variation)
    x_bubble = np.random.randn(50)
    y_bubble = np.random.randn(50)
    sizes = np.random.randint(5, 50, 50)

    fig3 = go.Figure(data=go.Scatter(
        x=x_bubble,
        y=y_bubble,
        mode='markers',
        marker=dict(
            size=sizes,
            sizemode='diameter',
            color=sizes,
            colorscale='Plasma',
            showscale=True,
            colorbar=dict(title="Size")
        ),
        text=[f"Size: {s}" for s in sizes],
        hovertemplate='X: %{x:.2f}<br>Y: %{y:.2f}<br>%{text}<extra></extra>'
    ))
    fig3.update_layout(
        title="3. Bubble Chart (Variable Size)",
        xaxis_title="X Dimension",
        yaxis_title="Y Dimension"
    )
    plots.append(("scatter_bubble", fig3, {"title": "Bubble Chart"}))

    # 4. Multi-Series Scatter
    categories = ['Category A', 'Category B', 'Category C', 'Category D']
    fig4 = go.Figure()

    for i, cat in enumerate(categories):
        x_cat = np.random.randn(30) + i*2
        y_cat = np.random.randn(30) + i*1.5
        fig4.add_trace(go.Scatter(
            x=x_cat,
            y=y_cat,
            mode='markers',
            name=cat,
            marker=dict(size=10)
        ))

    fig4.update_layout(
        title="4. Multi-Series Scatter Plot",
        xaxis_title="X Coordinate",
        yaxis_title="Y Coordinate",
        hovermode='closest'
    )
    plots.append(("scatter_multi_series", fig4, {"title": "Multi-Series Scatter"}))

    # 5. Scatter with Lines and Markers
    x_line = np.linspace(0, 10, 20)
    y_line = np.sin(x_line) + np.random.randn(20) * 0.1

    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode='lines+markers',
        name='Sine Wave with Noise',
        line=dict(color='firebrick', width=2),
        marker=dict(size=8, color='darkred')
    ))
    fig5.update_layout(
        title="5. Scatter with Lines and Markers",
        xaxis_title="Time",
        yaxis_title="Amplitude"
    )
    plots.append(("scatter_lines_markers", fig5, {"title": "Lines + Markers"}))

    # 6. Scatter with Error Bars
    x_error = np.linspace(0, 5, 10)
    y_error = x_error ** 2
    error_y = np.random.uniform(1, 3, 10)
    error_x = np.random.uniform(0.1, 0.5, 10)

    fig6 = go.Figure(data=go.Scatter(
        x=x_error,
        y=y_error,
        mode='markers',
        name='Measurements',
        error_y=dict(
            type='data',
            array=error_y,
            visible=True
        ),
        error_x=dict(
            type='data',
            array=error_x,
            visible=True
        ),
        marker=dict(size=10, color='purple')
    ))
    fig6.update_layout(
        title="6. Scatter with Error Bars",
        xaxis_title="Independent Variable",
        yaxis_title="Dependent Variable"
    )
    plots.append(("scatter_error_bars", fig6, {"title": "Error Bars"}))

    # 7. 3D Scatter Plot
    x_3d = np.random.randn(100)
    y_3d = np.random.randn(100)
    z_3d = np.random.randn(100)

    fig7 = go.Figure(data=[go.Scatter3d(
        x=x_3d,
        y=y_3d,
        z=z_3d,
        mode='markers',
        marker=dict(
            size=5,
            color=z_3d,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Z Value")
        )
    )])
    fig7.update_layout(
        title="7. 3D Scatter Plot",
        scene=dict(
            xaxis_title="X Axis",
            yaxis_title="Y Axis",
            zaxis_title="Z Axis"
        )
    )
    plots.append(("scatter_3d", fig7, {"title": "3D Scatter"}))

    # 8. Scatter Matrix (Pair Plot)
    df_matrix = pd.DataFrame({
        'Feature 1': np.random.randn(100),
        'Feature 2': np.random.randn(100) * 2,
        'Feature 3': np.random.randn(100) * 0.5,
        'Feature 4': np.random.exponential(2, 100),
        'Category': np.random.choice(['A', 'B', 'C'], 100)
    })

    fig8 = px.scatter_matrix(
        df_matrix,
        dimensions=['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4'],
        color='Category',
        title="8. Scatter Matrix (Pair Plot)"
    )
    plots.append(("scatter_matrix", fig8, {"title": "Scatter Matrix"}))

    # 9. Scatter with Trendline
    x_trend = np.linspace(0, 10, 50)
    y_trend = 2 * x_trend + 1 + np.random.randn(50) * 2

    df_trend = pd.DataFrame({'x': x_trend, 'y': y_trend})
    # Create scatter with manual trendline (no statsmodels dependency)
    z = np.polyfit(x_trend, y_trend, 1)
    p = np.poly1d(z)
    fig9 = go.Figure()
    fig9.add_trace(go.Scatter(x=x_trend, y=y_trend,
                              mode='markers', name='Data',
                              marker=dict(size=8, color='teal')))
    fig9.add_trace(go.Scatter(x=x_trend, y=p(x_trend),
                              mode='lines', name='Trendline',
                              line=dict(color='red', width=2)))
    fig9.update_layout(title="9. Scatter with Trendline")
    plots.append(("scatter_trendline", fig9, {"title": "Scatter with Trendline"}))

    # 10. Scatter on Map (Geo Scatter)
    cities = pd.DataFrame({
        'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
                 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'],
        'lat': [40.7128, 34.0522, 41.8781, 29.7604, 33.4484,
                39.9526, 29.4241, 32.7157, 32.7767, 37.3382],
        'lon': [-74.0060, -118.2437, -87.6298, -95.3698, -112.0740,
                -75.1652, -98.4936, -117.1611, -96.7970, -121.8863],
        'population': [8336817, 3979576, 2693976, 2320268, 1680992,
                      1584064, 1547253, 1423851, 1343573, 1021795]
    })

    fig10 = go.Figure(go.Scattergeo(
        lon=cities['lon'],
        lat=cities['lat'],
        text=cities['city'],
        mode='markers',
        marker=dict(
            size=cities['population']/100000,
            color=cities['population'],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Population"),
            sizemode='diameter'
        )
    ))
    fig10.update_layout(
        title='10. Scatter on Map (US Cities by Population)',
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showland=True,
            landcolor='rgb(243, 243, 243)'
        )
    )
    plots.append(("scatter_geo", fig10, {"title": "Geo Scatter"}))

    # 11. Scatter with Annotations
    x_ann = np.array([1, 2, 3, 4, 5])
    y_ann = np.array([2, 4, 3, 5, 6])
    labels = ['Point A', 'Point B', 'Point C', 'Point D', 'Point E']

    fig11 = go.Figure(data=go.Scatter(
        x=x_ann,
        y=y_ann,
        mode='markers',
        marker=dict(size=15, color='green'),
        text=labels,
        textposition="top center",
        textfont=dict(size=12)
    ))

    # Add annotations for specific points
    fig11.add_annotation(x=3, y=3, text="Important Point",
                         showarrow=True, arrowhead=2,
                         arrowsize=1, arrowwidth=2,
                         arrowcolor="red", ax=-50, ay=-50)

    fig11.update_layout(
        title="11. Scatter with Annotations",
        xaxis_title="X Position",
        yaxis_title="Y Position",
        showlegend=False
    )
    plots.append(("scatter_annotations", fig11, {"title": "Annotated Scatter"}))

    # 12. Scatter with Different Marker Symbols
    symbols = ['circle', 'square', 'diamond', 'cross', 'triangle-up',
               'triangle-down', 'pentagon', 'hexagon', 'star', 'hourglass']

    fig12 = go.Figure()
    for i, symbol in enumerate(symbols):
        fig12.add_trace(go.Scatter(
            x=[i % 5],
            y=[i // 5],
            mode='markers',
            name=symbol,
            marker=dict(size=20, symbol=symbol),
            showlegend=True
        ))

    fig12.update_layout(
        title="12. Scatter with Different Marker Symbols",
        xaxis_title="X Grid",
        yaxis_title="Y Grid",
        showlegend=True
    )
    plots.append(("scatter_symbols", fig12, {"title": "Marker Symbols"}))

    # 13. Time Series Scatter
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    values = np.cumsum(np.random.randn(100)) + 100

    fig13 = go.Figure(data=go.Scatter(
        x=dates,
        y=values,
        mode='markers',
        marker=dict(
            size=8,
            color=values,
            colorscale='Turbo',
            showscale=True,
            colorbar=dict(title="Value")
        ),
        hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}<extra></extra>'
    ))
    fig13.update_layout(
        title="13. Time Series Scatter Plot",
        xaxis_title="Date",
        yaxis_title="Value",
        xaxis=dict(tickformat='%Y-%m-%d')
    )
    plots.append(("scatter_timeseries", fig13, {"title": "Time Series Scatter"}))

    # 14. Scatter with Marginal Distributions
    x_marginal = np.random.randn(500)
    y_marginal = x_marginal * 0.5 + np.random.randn(500) * 0.5

    df_marginal = pd.DataFrame({'x': x_marginal, 'y': y_marginal})
    fig14 = px.scatter(
        df_marginal, x='x', y='y',
        marginal_x="histogram",
        marginal_y="histogram",
        title="14. Scatter with Marginal Histograms"
    )
    # Only update scatter traces, not histogram traces
    fig14.update_traces(marker=dict(size=5, opacity=0.6), selector=dict(type='scatter'))
    plots.append(("scatter_marginal", fig14, {"title": "Marginal Distributions"}))

    # 15. Polar Scatter Plot
    r = np.random.uniform(0, 10, 100)
    theta = np.random.uniform(0, 360, 100)

    fig15 = go.Figure(data=go.Scatterpolar(
        r=r,
        theta=theta,
        mode='markers',
        marker=dict(
            size=8,
            color=r,
            colorscale='HSV',
            showscale=True,
            colorbar=dict(title="Radius")
        )
    ))
    fig15.update_layout(
        title="15. Polar Scatter Plot",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10])
        ),
        showlegend=False
    )
    plots.append(("scatter_polar", fig15, {"title": "Polar Scatter"}))

    # 16. Scatter with Fill Areas
    x_fill = np.linspace(0, 4*np.pi, 50)
    y_upper = np.sin(x_fill) + 0.5
    y_lower = np.sin(x_fill) - 0.5
    y_middle = np.sin(x_fill)

    fig16 = go.Figure()
    fig16.add_trace(go.Scatter(
        x=x_fill, y=y_upper,
        mode='lines',
        name='Upper Bound',
        line=dict(width=0),
        showlegend=False
    ))
    fig16.add_trace(go.Scatter(
        x=x_fill, y=y_lower,
        mode='lines',
        name='Lower Bound',
        line=dict(width=0),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty',
        showlegend=False
    ))
    fig16.add_trace(go.Scatter(
        x=x_fill, y=y_middle,
        mode='markers+lines',
        name='Signal',
        line=dict(color='red', width=2),
        marker=dict(size=8, color='darkred')
    ))

    fig16.update_layout(
        title="16. Scatter with Filled Area",
        xaxis_title="Phase",
        yaxis_title="Amplitude"
    )
    plots.append(("scatter_fill", fig16, {"title": "Scatter with Fill"}))

    # 17. Ternary Scatter Plot
    a = np.random.rand(30)
    b = np.random.rand(30)
    c = 1 - a - b
    # Ensure valid ternary coordinates
    mask = c >= 0
    a, b, c = a[mask], b[mask], c[mask]

    fig17 = go.Figure(go.Scatterternary({
        'mode': 'markers',
        'a': a,
        'b': b,
        'c': c,
        'marker': {
            'size': 10,
            'color': a,
            'colorscale': 'Portland',
            'showscale': True,
            'colorbar': {'title': 'A Component'}
        },
        'text': [f'A:{a[i]:.2f}<br>B:{b[i]:.2f}<br>C:{c[i]:.2f}'
                for i in range(len(a))]
    }))

    fig17.update_layout({
        'title': '17. Ternary Scatter Plot',
        'ternary': {
            'aaxis': {'title': 'Component A'},
            'baxis': {'title': 'Component B'},
            'caxis': {'title': 'Component C'}
        }
    })
    plots.append(("scatter_ternary", fig17, {"title": "Ternary Scatter"}))

    # 18. Scatter with Custom Hover Data
    products = pd.DataFrame({
        'price': np.random.uniform(10, 100, 50),
        'quality': np.random.uniform(1, 10, 50),
        'sales': np.random.randint(100, 1000, 50),
        'product': [f'Product {i+1}' for i in range(50)],
        'category': np.random.choice(['Electronics', 'Clothing', 'Food'], 50)
    })

    fig18 = go.Figure(data=go.Scatter(
        x=products['price'],
        y=products['quality'],
        mode='markers',
        marker=dict(
            size=products['sales']/20,
            color=products['category'].map({'Electronics': 1, 'Clothing': 2, 'Food': 3}),
            colorscale='viridis',
            showscale=False
        ),
        text=products['product'],
        customdata=np.column_stack((products['sales'], products['category'])),
        hovertemplate='<b>%{text}</b><br>' +
                     'Price: $%{x:.2f}<br>' +
                     'Quality: %{y:.1f}/10<br>' +
                     'Sales: %{customdata[0]}<br>' +
                     'Category: %{customdata[1]}<extra></extra>'
    ))
    fig18.update_layout(
        title="18. Scatter with Custom Hover Data",
        xaxis_title="Price ($)",
        yaxis_title="Quality Score"
    )
    plots.append(("scatter_custom_hover", fig18, {"title": "Custom Hover"}))

    # 19. Connected Scatter (Network-like)
    n_nodes = 15
    node_x = np.random.rand(n_nodes) * 10
    node_y = np.random.rand(n_nodes) * 10

    fig19 = go.Figure()

    # Add edges (connections)
    for i in range(n_nodes):
        for j in range(i+1, n_nodes):
            if np.random.random() < 0.2:  # 20% chance of connection
                fig19.add_trace(go.Scatter(
                    x=[node_x[i], node_x[j]],
                    y=[node_y[i], node_y[j]],
                    mode='lines',
                    line=dict(width=1, color='lightgray'),
                    showlegend=False,
                    hoverinfo='skip'
                ))

    # Add nodes
    fig19.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(size=20, color='red'),
        text=[f'N{i+1}' for i in range(n_nodes)],
        textposition="top center",
        name='Nodes'
    ))

    fig19.update_layout(
        title="19. Connected Scatter (Network Graph)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        showlegend=False
    )
    plots.append(("scatter_network", fig19, {"title": "Network Scatter"}))

    # 20. Animated Scatter (Multiple Frames)
    # Creating a simple animation effect with multiple traces
    fig20 = go.Figure()

    for frame in range(5):
        x_anim = np.linspace(0, 10, 30)
        y_anim = np.sin(x_anim + frame * np.pi / 5) + np.random.randn(30) * 0.1

        fig20.add_trace(go.Scatter(
            x=x_anim,
            y=y_anim,
            mode='markers',
            name=f'Frame {frame+1}',
            marker=dict(size=10, opacity=0.6)
        ))

    fig20.update_layout(
        title="20. Multi-Frame Scatter (Animation Frames)",
        xaxis_title="Time Step",
        yaxis_title="Value",
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {'label': 'All', 'method': 'restyle', 'args': ['visible', [True] * 5]},
                {'label': 'Frame 1', 'method': 'restyle', 'args': ['visible', [True, False, False, False, False]]},
                {'label': 'Frame 2', 'method': 'restyle', 'args': ['visible', [False, True, False, False, False]]},
                {'label': 'Frame 3', 'method': 'restyle', 'args': ['visible', [False, False, True, False, False]]},
            ]
        }]
    )
    plots.append(("scatter_animated", fig20, {"title": "Animated Scatter"}))

    return plots

# Execute and register plots
if __name__ == "__main__" or True:  # Always execute when imported
    plots = create_scatter_plots()
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)