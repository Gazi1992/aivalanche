"""
Bar plots demonstration script with various bar chart types
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_bar_plots():
    """Create comprehensive bar plot demonstrations"""
    plots = []

    # 1. Basic Vertical Bar Chart
    categories = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    values = [23, 17, 35, 29, 12]

    fig1 = go.Figure(data=[
        go.Bar(x=categories, y=values,
               marker_color='#667eea',
               text=values,
               textposition='outside')
    ])
    fig1.update_layout(
        title="Basic Vertical Bar Chart - Product Sales",
        xaxis_title="Products",
        yaxis_title="Sales (units)",
        showlegend=False
    )
    plots.append(('bar_1', fig1, {
        'appearance': {
            'title': {'text': 'Basic Vertical Bar Chart', 'fontSize': 20}
        }
    }))

    # 2. Horizontal Bar Chart
    fig2 = go.Figure(data=[
        go.Bar(y=categories, x=values,
               orientation='h',
               marker_color='#48bb78',
               text=values,
               textposition='outside')
    ])
    fig2.update_layout(
        title="Horizontal Bar Chart - Product Performance",
        xaxis_title="Sales (units)",
        yaxis_title="Products"
    )
    plots.append(('bar_2', fig2, {
        'appearance': {
            'title': {'text': 'Horizontal Bar Chart', 'fontSize': 20}
        }
    }))

    # 3. Grouped Bar Chart
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
    product_a = [20, 14, 23, 25, 22]
    product_b = [15, 18, 19, 22, 20]
    product_c = [10, 12, 15, 18, 21]

    fig3 = go.Figure(data=[
        go.Bar(name='Product A', x=months, y=product_a),
        go.Bar(name='Product B', x=months, y=product_b),
        go.Bar(name='Product C', x=months, y=product_c)
    ])
    fig3.update_layout(
        barmode='group',
        title="Grouped Bar Chart - Monthly Sales Comparison",
        xaxis_title="Month",
        yaxis_title="Sales (units)",
        legend=dict(x=0.02, y=0.98)
    )
    plots.append(('bar_3', fig3, {
        'appearance': {
            'title': {'text': 'Grouped Bar Chart', 'fontSize': 20}
        }
    }))

    # 4. Stacked Bar Chart
    fig4 = go.Figure(data=[
        go.Bar(name='Product A', x=months, y=product_a),
        go.Bar(name='Product B', x=months, y=product_b),
        go.Bar(name='Product C', x=months, y=product_c)
    ])
    fig4.update_layout(
        barmode='stack',
        title="Stacked Bar Chart - Total Monthly Sales",
        xaxis_title="Month",
        yaxis_title="Cumulative Sales",
        legend=dict(x=0.02, y=0.98)
    )
    plots.append(('bar_4', fig4, {
        'appearance': {
            'title': {'text': 'Stacked Bar Chart', 'fontSize': 20}
        }
    }))

    # 5. Relative/Percentage Stacked Bar
    fig5 = go.Figure(data=[
        go.Bar(name='Desktop', x=months, y=[30, 35, 32, 28, 25]),
        go.Bar(name='Mobile', x=months, y=[45, 40, 43, 48, 50]),
        go.Bar(name='Tablet', x=months, y=[25, 25, 25, 24, 25])
    ])
    fig5.update_layout(
        barmode='relative',
        title="100% Stacked Bar - Device Usage Distribution",
        xaxis_title="Month",
        yaxis_title="Percentage",
        yaxis=dict(tickformat='.0%'),
        legend=dict(x=0.02, y=0.98)
    )
    plots.append(('bar_5', fig5, {
        'appearance': {
            'title': {'text': '100% Stacked Bar Chart', 'fontSize': 20}
        }
    }))

    # 6. Bar Chart with Error Bars
    measurements = [23.2, 25.1, 24.8, 26.3, 25.5]
    errors = [1.2, 0.8, 1.5, 1.1, 0.9]

    fig6 = go.Figure(data=[
        go.Bar(x=['Test 1', 'Test 2', 'Test 3', 'Test 4', 'Test 5'],
               y=measurements,
               error_y=dict(type='data', array=errors),
               marker_color='#ed8936')
    ])
    fig6.update_layout(
        title="Bar Chart with Error Bars - Measurement Results",
        xaxis_title="Test Number",
        yaxis_title="Measurement Value",
        showlegend=False
    )
    plots.append(('bar_6', fig6, {
        'appearance': {
            'title': {'text': 'Bar Chart with Error Bars', 'fontSize': 20}
        }
    }))

    # 7. Diverging Bar Chart (Positive/Negative)
    categories_div = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E']
    values_div = [15, -8, 23, -12, 18]
    colors = ['#48bb78' if x > 0 else '#f56565' for x in values_div]

    fig7 = go.Figure(data=[
        go.Bar(x=categories_div, y=values_div,
               marker_color=colors,
               text=[f"{v:+d}" for v in values_div],
               textposition='outside')
    ])
    fig7.update_layout(
        title="Diverging Bar Chart - Profit/Loss by Category",
        xaxis_title="Category",
        yaxis_title="Value ($1000s)",
        yaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black'),
        showlegend=False
    )
    plots.append(('bar_7', fig7, {
        'appearance': {
            'title': {'text': 'Diverging Bar Chart', 'fontSize': 20}
        }
    }))

    # 8. Waterfall Chart
    x_waterfall = ["Start", "Q1", "Q2", "Q3", "Q4", "Total"]
    y_waterfall = [100, 30, -20, 40, -10, None]

    fig8 = go.Figure(go.Waterfall(
        x=x_waterfall,
        y=y_waterfall,
        text=["+100", "+30", "-20", "+40", "-10", "140"],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    fig8.update_layout(
        title="Waterfall Chart - Quarterly Revenue Changes",
        xaxis_title="Quarter",
        yaxis_title="Revenue ($1000s)",
        showlegend=False
    )
    plots.append(('bar_8', fig8, {
        'appearance': {
            'title': {'text': 'Waterfall Chart', 'fontSize': 20}
        }
    }))

    # 9. Histogram
    np.random.seed(42)
    data_hist = np.random.normal(100, 15, 1000)

    fig9 = go.Figure(data=[
        go.Histogram(x=data_hist, nbinsx=30,
                     marker_color='#9f7aea',
                     opacity=0.75)
    ])
    fig9.update_layout(
        title="Histogram - Normal Distribution",
        xaxis_title="Value",
        yaxis_title="Frequency",
        bargap=0.2,
        showlegend=False
    )
    plots.append(('bar_9', fig9, {
        'appearance': {
            'title': {'text': 'Histogram', 'fontSize': 20}
        }
    }))

    # 10. Overlapping Histograms
    data_hist1 = np.random.normal(100, 15, 500)
    data_hist2 = np.random.normal(110, 12, 500)

    fig10 = go.Figure()
    fig10.add_trace(go.Histogram(x=data_hist1, name='Group A',
                                  opacity=0.5, marker_color='blue'))
    fig10.add_trace(go.Histogram(x=data_hist2, name='Group B',
                                  opacity=0.5, marker_color='red'))
    fig10.update_layout(
        barmode='overlay',
        title="Overlapping Histograms - Group Comparison",
        xaxis_title="Value",
        yaxis_title="Frequency",
        legend=dict(x=0.7, y=0.98)
    )
    plots.append(('bar_10', fig10, {
        'appearance': {
            'title': {'text': 'Overlapping Histograms', 'fontSize': 20}
        }
    }))

    # 11. Bidirectional Bar Chart
    categories_bi = ['Category A', 'Category B', 'Category C', 'Category D']
    values_left = [-20, -15, -30, -25]
    values_right = [15, 20, 25, 18]

    fig11 = go.Figure()
    fig11.add_trace(go.Bar(y=categories_bi, x=values_left,
                            name='Losses', orientation='h',
                            marker_color='#f56565'))
    fig11.add_trace(go.Bar(y=categories_bi, x=values_right,
                            name='Gains', orientation='h',
                            marker_color='#48bb78'))
    fig11.update_layout(
        title="Bidirectional Bar Chart - Gains vs Losses",
        xaxis_title="Value ($1000s)",
        yaxis_title="Category",
        barmode='relative',
        legend=dict(x=0.7, y=0.98)
    )
    plots.append(('bar_11', fig11, {
        'appearance': {
            'title': {'text': 'Bidirectional Bar Chart', 'fontSize': 20}
        }
    }))

    # 12. Radial Bar Chart (Polar)
    categories_radial = ['North', 'Northeast', 'East', 'Southeast',
                         'South', 'Southwest', 'West', 'Northwest']
    values_radial = [20, 14, 23, 25, 22, 18, 15, 19]

    fig12 = go.Figure(go.Barpolar(
        r=values_radial,
        theta=categories_radial,
        marker_color=['#667eea', '#9f7aea', '#48bb78', '#68d391',
                      '#ed8936', '#f6ad55', '#fc8181', '#f56565'],
        marker_line_color="black",
        marker_line_width=1,
        opacity=0.8
    ))
    fig12.update_layout(
        title="Radial Bar Chart - Sales by Region",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 30]
            )
        ),
        showlegend=False
    )
    plots.append(('bar_12', fig12, {
        'appearance': {
            'title': {'text': 'Radial Bar Chart', 'fontSize': 20}
        }
    }))

    # 13. Bar Chart with Trendline
    x_trend = list(range(1, 13))
    y_trend = [12, 15, 18, 14, 20, 22, 25, 28, 24, 30, 32, 35]
    z = np.polyfit(x_trend, y_trend, 1)
    p = np.poly1d(z)

    fig13 = go.Figure()
    fig13.add_trace(go.Bar(x=x_trend, y=y_trend, name='Monthly Sales',
                           marker_color='#667eea'))
    fig13.add_trace(go.Scatter(x=x_trend, y=p(x_trend),
                               mode='lines', name='Trend',
                               line=dict(color='red', width=2, dash='dash')))
    fig13.update_layout(
        title="Bar Chart with Trendline - Monthly Sales Trend",
        xaxis_title="Month",
        yaxis_title="Sales (units)",
        legend=dict(x=0.02, y=0.98)
    )
    plots.append(('bar_13', fig13, {
        'appearance': {
            'title': {'text': 'Bar Chart with Trendline', 'fontSize': 20}
        }
    }))

    # 14. Gantt Chart Style Bars
    tasks = ['Task A', 'Task B', 'Task C', 'Task D', 'Task E']
    start_times = [1, 2, 4, 5, 7]
    durations = [3, 2, 2, 4, 2]

    fig14 = go.Figure()
    for i, (task, start, duration) in enumerate(zip(tasks, start_times, durations)):
        fig14.add_trace(go.Bar(
            x=[duration],
            y=[task],
            orientation='h',
            name=task,
            marker_color=px.colors.qualitative.Set3[i],
            base=start,
            showlegend=False,
            text=f"Duration: {duration}",
            textposition='inside'
        ))

    fig14.update_layout(
        title="Gantt-Style Bar Chart - Project Timeline",
        xaxis_title="Time (days)",
        yaxis_title="Task",
        barmode='overlay',
        xaxis=dict(range=[0, 12])
    )
    plots.append(('bar_14', fig14, {
        'appearance': {
            'title': {'text': 'Gantt-Style Bar Chart', 'fontSize': 20}
        }
    }))

    # 15. Bullet Chart
    fig15 = go.Figure()

    # Background ranges
    fig15.add_trace(go.Bar(
        x=[100], y=['Metric'],
        orientation='h',
        marker_color='lightgray',
        name='Maximum',
        showlegend=False
    ))
    fig15.add_trace(go.Bar(
        x=[75], y=['Metric'],
        orientation='h',
        marker_color='silver',
        name='Good',
        showlegend=False
    ))
    fig15.add_trace(go.Bar(
        x=[50], y=['Metric'],
        orientation='h',
        marker_color='gray',
        name='Satisfactory',
        showlegend=False
    ))
    # Actual value
    fig15.add_trace(go.Bar(
        x=[65], y=['Metric'],
        orientation='h',
        marker_color='black',
        name='Actual',
        width=0.3
    ))
    # Target line
    fig15.add_trace(go.Scatter(
        x=[80, 80], y=[-0.4, 0.4],
        mode='lines',
        line=dict(color='red', width=3),
        name='Target'
    ))

    fig15.update_layout(
        title="Bullet Chart - Performance Metric",
        xaxis_title="Value",
        barmode='overlay',
        showlegend=True,
        legend=dict(x=0.7, y=0.5)
    )
    plots.append(('bar_15', fig15, {
        'appearance': {
            'title': {'text': 'Bullet Chart', 'fontSize': 20}
        }
    }))

    # 16. Column Chart with Annotations
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    revenue = [120, 135, 155, 142]

    fig16 = go.Figure(data=[
        go.Bar(x=quarters, y=revenue,
               marker_color=['#667eea', '#48bb78', '#ed8936', '#f56565'])
    ])

    # Add annotations
    for i, (q, r) in enumerate(zip(quarters, revenue)):
        fig16.add_annotation(
            x=q, y=r,
            text=f"${r}M",
            showarrow=True,
            arrowhead=2,
            yshift=10
        )

    fig16.update_layout(
        title="Column Chart with Annotations - Quarterly Revenue",
        xaxis_title="Quarter",
        yaxis_title="Revenue (Millions)",
        showlegend=False
    )
    plots.append(('bar_16', fig16, {
        'appearance': {
            'title': {'text': 'Column Chart with Annotations', 'fontSize': 20}
        }
    }))

    # 17. Clustered Column Chart
    years = ['2019', '2020', '2021', '2022', '2023']

    fig17 = go.Figure()
    fig17.add_trace(go.Bar(name='Region A', x=years, y=[20, 25, 30, 35, 40]))
    fig17.add_trace(go.Bar(name='Region B', x=years, y=[15, 20, 25, 30, 32]))
    fig17.add_trace(go.Bar(name='Region C', x=years, y=[10, 15, 20, 25, 28]))
    fig17.add_trace(go.Bar(name='Region D', x=years, y=[8, 12, 15, 18, 20]))

    fig17.update_layout(
        title="Clustered Column Chart - Regional Sales Growth",
        xaxis_title="Year",
        yaxis_title="Sales (Millions)",
        barmode='group',
        legend=dict(x=0.02, y=0.98)
    )
    plots.append(('bar_17', fig17, {
        'appearance': {
            'title': {'text': 'Clustered Column Chart', 'fontSize': 20}
        }
    }))

    # 18. Bar Chart with Pattern Fill
    categories_pattern = ['Category A', 'Category B', 'Category C', 'Category D']
    values_pattern = [25, 30, 20, 35]
    patterns = ['/', '\\', '|', '-']

    fig18 = go.Figure()
    for cat, val, pattern in zip(categories_pattern, values_pattern, patterns):
        fig18.add_trace(go.Bar(
            x=[cat], y=[val],
            name=cat,
            marker_color='#667eea',
            marker_pattern_shape=pattern,
            showlegend=False
        ))

    fig18.update_layout(
        title="Bar Chart with Pattern Fill - Category Comparison",
        xaxis_title="Category",
        yaxis_title="Value",
        showlegend=False
    )
    plots.append(('bar_18', fig18, {
        'appearance': {
            'title': {'text': 'Bar Chart with Patterns', 'fontSize': 20}
        }
    }))

    # 19. Floating Bar Chart
    categories_float = ['Project A', 'Project B', 'Project C', 'Project D']
    start_values = [10, 25, 15, 30]
    end_values = [25, 45, 35, 55]

    fig19 = go.Figure()
    for i, (cat, start, end) in enumerate(zip(categories_float, start_values, end_values)):
        fig19.add_trace(go.Bar(
            x=[end - start],
            y=[cat],
            orientation='h',
            base=start,
            name=cat,
            marker_color=px.colors.qualitative.Pastel[i],
            text=f"{start}-{end}",
            textposition='inside',
            showlegend=False
        ))

    fig19.update_layout(
        title="Floating Bar Chart - Project Timelines",
        xaxis_title="Timeline (weeks)",
        yaxis_title="Project",
        barmode='overlay'
    )
    plots.append(('bar_19', fig19, {
        'appearance': {
            'title': {'text': 'Floating Bar Chart', 'fontSize': 20}
        }
    }))

    # 20. 3D Bar Chart
    x_3d = ['A', 'B', 'C', 'D', 'E']
    y_3d = ['Type 1', 'Type 2', 'Type 3']
    z_3d = [[20, 15, 25, 30, 22],
            [25, 20, 15, 25, 18],
            [15, 25, 20, 15, 20]]

    fig20 = go.Figure(data=[go.Surface(z=z_3d)])
    fig20.update_layout(
        title="3D Bar Surface - Multi-dimensional Data",
        scene=dict(
            xaxis_title="Category",
            yaxis_title="Type",
            zaxis_title="Value"
        )
    )
    plots.append(('bar_20', fig20, {
        'appearance': {
            'title': {'text': '3D Bar Surface', 'fontSize': 20}
        }
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} bar plot demonstrations"

# Execute when module is run
if __name__ == "__main__" or True:  # Always execute when imported
    result = create_bar_plots()
    print(result)