"""
Pie charts and related visualizations demonstration script
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

def create_pie_charts():
    """Create comprehensive pie chart and related demonstrations"""
    plots = []

    # 1. Basic Pie Chart
    labels = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    values = [30, 25, 20, 15, 10]

    fig1 = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig1.update_layout(
        title="1. Basic Pie Chart - Market Share"
    )
    plots.append(('pie_1', fig1, {
        'appearance': {
            'title': {'text': 'Basic Pie Chart', 'fontSize': 20}
        }
    }))

    # 2. Donut Chart
    fig2 = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4
    )])
    fig2.update_layout(
        title="2. Donut Chart - Revenue Distribution",
        annotations=[dict(text='Revenue', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    plots.append(('pie_2', fig2, {
        'appearance': {
            'title': {'text': 'Donut Chart', 'fontSize': 20}
        }
    }))

    # 3. Pie Chart with Exploded Slices
    fig3 = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        pull=[0.2, 0, 0, 0, 0]  # Pull out first slice
    )])
    fig3.update_layout(
        title="3. Exploded Pie Chart - Highlighting Top Product"
    )
    plots.append(('pie_3', fig3, {
        'appearance': {
            'title': {'text': 'Exploded Pie Chart', 'fontSize': 20}
        }
    }))

    # 4. Custom Colors Pie Chart
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

    fig4 = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors, line=dict(color='white', width=2))
    )])
    fig4.update_layout(
        title="4. Custom Colored Pie Chart"
    )
    plots.append(('pie_4', fig4, {
        'appearance': {
            'title': {'text': 'Custom Colors Pie', 'fontSize': 20}
        }
    }))

    # 5. Nested Donut Charts
    fig5 = go.Figure()

    # Outer donut
    fig5.add_trace(go.Pie(
        labels=['Q1', 'Q2', 'Q3', 'Q4'],
        values=[25, 30, 35, 40],
        hole=0.6,
        domain=dict(x=[0, 1], y=[0, 1]),
        name='Quarters',
        marker=dict(colors=['#667eea', '#764ba2', '#f093fb', '#fccb90'])
    ))

    # Inner donut
    fig5.add_trace(go.Pie(
        labels=['Target Met', 'Target Missed'],
        values=[75, 25],
        hole=0.3,
        domain=dict(x=[0.2, 0.8], y=[0.2, 0.8]),
        name='Performance',
        marker=dict(colors=['#48bb78', '#f56565'])
    ))

    fig5.update_layout(
        title="5. Nested Donut Charts - Quarterly Performance",
        showlegend=True
    )
    plots.append(('pie_5', fig5, {
        'appearance': {
            'title': {'text': 'Nested Donuts', 'fontSize': 20}
        }
    }))

    # 6. Semi-Circle Pie Chart
    fig6 = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        direction='clockwise',
        rotation=270,
        domain=dict(x=[0, 1], y=[0, 1])
    )])

    fig6.update_traces(
        textposition='outside',
        textinfo='label+percent'
    )

    fig6.update_layout(
        title="6. Semi-Circle Gauge Style",
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    # Limit to 180 degrees
    fig6.add_shape(
        type="rect",
        x0=0, y0=0, x1=1, y1=0.45,
        fillcolor="white",
        layer="above",
        line=dict(width=0)
    )

    plots.append(('pie_6', fig6, {
        'appearance': {
            'title': {'text': 'Semi-Circle Gauge', 'fontSize': 20}
        }
    }))

    # 7. Sunburst Chart
    data = dict(
        labels=["Total", "North America", "Europe", "Asia", "USA", "Canada", "Mexico",
                "UK", "Germany", "France", "China", "Japan", "India"],
        parents=["", "Total", "Total", "Total", "North America", "North America", "North America",
                 "Europe", "Europe", "Europe", "Asia", "Asia", "Asia"],
        values=[0, 0, 0, 0, 30, 15, 10, 20, 25, 15, 35, 25, 20]
    )

    fig7 = go.Figure(go.Sunburst(
        labels=data['labels'],
        parents=data['parents'],
        values=data['values'],
        branchvalues="total",
        marker=dict(colorscale='sunset')
    ))

    fig7.update_layout(
        title="7. Sunburst Chart - Regional Sales Hierarchy"
    )
    plots.append(('pie_7', fig7, {
        'appearance': {
            'title': {'text': 'Sunburst Chart', 'fontSize': 20}
        }
    }))

    # 8. Treemap
    fig8 = go.Figure(go.Treemap(
        labels=data['labels'],
        parents=data['parents'],
        values=data['values'],
        textinfo="label+value+percent parent",
        marker=dict(colorscale='viridis')
    ))

    fig8.update_layout(
        title="8. Treemap - Hierarchical Data Visualization"
    )
    plots.append(('pie_8', fig8, {
        'appearance': {
            'title': {'text': 'Treemap', 'fontSize': 20}
        }
    }))

    # 9. Pie Chart with Custom Text
    fig9 = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        text=[f'${v}M' for v in values],
        texttemplate='%{label}<br>%{text}<br>%{percent}',
        textposition='auto',
        insidetextorientation='radial'
    )])

    fig9.update_layout(
        title="9. Pie with Custom Text Templates"
    )
    plots.append(('pie_9', fig9, {
        'appearance': {
            'title': {'text': 'Custom Text Pie', 'fontSize': 20}
        }
    }))

    # 10. Rose Chart (Polar Bar as Pie Alternative)
    categories = ['Category A', 'Category B', 'Category C', 'Category D',
                  'Category E', 'Category F', 'Category G', 'Category H']
    values_rose = [20, 35, 30, 35, 27, 20, 25, 30]

    fig10 = go.Figure(go.Barpolar(
        r=values_rose,
        theta=categories,
        marker_color=['#e74c3c', '#3498db', '#2ecc71', '#f39c12',
                      '#9b59b6', '#1abc9c', '#34495e', '#e67e22'],
        marker_line_color="white",
        marker_line_width=1,
        opacity=0.8
    ))

    fig10.update_layout(
        title="10. Rose Chart (Polar Bar)",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values_rose)]
            )
        ),
        showlegend=False
    )
    plots.append(('pie_10', fig10, {
        'appearance': {
            'title': {'text': 'Rose Chart', 'fontSize': 20}
        }
    }))

    # 11. Multiple Pie Charts (Subplots)
    from plotly.subplots import make_subplots

    fig11 = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'pie'}, {'type': 'pie'}]],
        subplot_titles=('2023 Sales', '2024 Sales')
    )

    fig11.add_trace(go.Pie(
        labels=labels,
        values=[20, 25, 25, 20, 10],
        name='2023'
    ), row=1, col=1)

    fig11.add_trace(go.Pie(
        labels=labels,
        values=[15, 30, 20, 25, 10],
        name='2024'
    ), row=1, col=2)

    fig11.update_layout(
        title_text="11. Year-over-Year Comparison"
    )
    plots.append(('pie_11', fig11, {
        'appearance': {
            'title': {'text': 'Multiple Pie Charts', 'fontSize': 20}
        }
    }))

    # 12. Icicle Chart
    fig12 = go.Figure(go.Icicle(
        labels=data['labels'],
        parents=data['parents'],
        values=data['values'],
        branchvalues="total",
        marker=dict(colorscale='blues')
    ))

    fig12.update_layout(
        title="12. Icicle Chart - Alternative Hierarchy View"
    )
    plots.append(('pie_12', fig12, {
        'appearance': {
            'title': {'text': 'Icicle Chart', 'fontSize': 20}
        }
    }))

    # 13. Donut with Gradient Colors
    n_slices = 12
    theta = np.linspace(0, 360, n_slices, endpoint=False)
    values_gradient = np.random.randint(10, 50, n_slices)

    fig13 = go.Figure(data=[go.Pie(
        labels=[f'Segment {i+1}' for i in range(n_slices)],
        values=values_gradient,
        hole=0.5,
        marker=dict(
            colors=px.colors.sequential.Plasma,
            line=dict(color='white', width=1)
        )
    )])

    fig13.update_layout(
        title="13. Gradient Donut Chart",
        annotations=[dict(text='Gradient', x=0.5, y=0.5, font_size=18, showarrow=False)]
    )
    plots.append(('pie_13', fig13, {
        'appearance': {
            'title': {'text': 'Gradient Donut', 'fontSize': 20}
        }
    }))

    # 14. Pie Chart with Legend Positioning
    fig14 = go.Figure(data=[go.Pie(
        labels=['Very Long Product Name A', 'Very Long Product Name B',
                'Very Long Product Name C', 'Very Long Product Name D'],
        values=[35, 25, 25, 15],
        textposition='inside',
        textinfo='percent',
        showlegend=True
    )])

    fig14.update_layout(
        title="14. Pie with Custom Legend Position",
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    plots.append(('pie_14', fig14, {
        'appearance': {
            'title': {'text': 'Custom Legend Pie', 'fontSize': 20}
        }
    }))

    # 15. Animated/Rotating Sunburst
    frames = []
    for i in range(4):
        frame_values = [0, 0, 0, 0,
                       30 + i*5, 15 - i*2, 10 + i*3,
                       20 + i*2, 25 - i*3, 15 + i*2,
                       35 - i*4, 25 + i*3, 20 + i*2]
        frames.append(go.Frame(
            data=[go.Sunburst(
                labels=data['labels'],
                parents=data['parents'],
                values=frame_values,
                branchvalues="total"
            )],
            name=f'Quarter {i+1}'
        ))

    fig15 = go.Figure(
        data=[go.Sunburst(
            labels=data['labels'],
            parents=data['parents'],
            values=data['values'],
            branchvalues="total",
            marker=dict(colorscale='rainbow')
        )],
        frames=frames
    )

    fig15.update_layout(
        title="15. Animated Sunburst - Quarterly Evolution",
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {'label': 'Play', 'method': 'animate', 'args': [None]},
                {'label': 'Pause', 'method': 'animate', 'args': [None, {'frame': {'duration': 0}}]}
            ]
        }]
    )
    plots.append(('pie_15', fig15, {
        'appearance': {
            'title': {'text': 'Animated Sunburst', 'fontSize': 20}
        }
    }))

    # 16. Funnel Chart
    stages = ['Visitors', 'Sign-ups', 'Active Users', 'Paid Users', 'Renewals']
    values_funnel = [5000, 3000, 1500, 500, 200]

    fig16 = go.Figure(go.Funnel(
        y=stages,
        x=values_funnel,
        textposition="inside",
        opacity=0.8,
        marker=dict(
            color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6'],
            line=dict(width=2, color='white')
        )
    ))

    fig16.update_layout(
        title="16. Funnel Chart - User Conversion"
    )
    plots.append(('pie_16', fig16, {
        'appearance': {
            'title': {'text': 'Funnel Chart', 'fontSize': 20}
        }
    }))

    # 17. Area Funnel
    fig17 = go.Figure(go.Funnelarea(
        values=values_funnel,
        text=stages,
        marker=dict(
            colors=['#667eea', '#764ba2', '#f093fb', '#fccb90', '#c3f0ca'],
            line=dict(color='white', width=2)
        ),
        textfont=dict(color='white', size=14),
        textinfo="value+percent"
    ))

    fig17.update_layout(
        title="17. Funnel Area Chart - Sales Pipeline"
    )
    plots.append(('pie_17', fig17, {
        'appearance': {
            'title': {'text': 'Funnel Area', 'fontSize': 20}
        }
    }))

    # 18. Packed Bubble Chart (Circle Packing)
    sizes = np.random.randint(10, 100, 30)
    categories_bubble = np.random.choice(['A', 'B', 'C', 'D'], 30)

    fig18 = go.Figure(data=[go.Scatter(
        x=np.random.randn(30),
        y=np.random.randn(30),
        mode='markers',
        marker=dict(
            size=sizes,
            color=pd.Categorical(categories_bubble).codes,
            colorscale='viridis',
            showscale=True,
            sizemode='diameter',
            sizeref=2,
            line=dict(width=1, color='white')
        ),
        text=[f'Item {i+1}<br>Size: {s}<br>Category: {c}'
              for i, (s, c) in enumerate(zip(sizes, categories_bubble))],
        hovertemplate='%{text}<extra></extra>'
    )])

    fig18.update_layout(
        title="18. Packed Bubble Chart",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    plots.append(('pie_18', fig18, {
        'appearance': {
            'title': {'text': 'Packed Bubbles', 'fontSize': 20}
        }
    }))

    # 19. Pie Chart with Patterns
    fig19 = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(
            colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
            pattern=dict(
                shape=['/', '\\', '|', '-', '+'],
                solidity=0.5
            ),
            line=dict(color='black', width=2)
        )
    )])

    fig19.update_layout(
        title="19. Pie Chart with Pattern Fill"
    )
    plots.append(('pie_19', fig19, {
        'appearance': {
            'title': {'text': 'Pattern Fill Pie', 'fontSize': 20}
        }
    }))

    # 20. Radial Tree (Dendrogram style)
    labels_tree = ["Root", "Branch A", "Branch B", "Leaf A1", "Leaf A2",
                   "Leaf B1", "Leaf B2", "Sub A1", "Sub A2"]
    parents_tree = ["", "Root", "Root", "Branch A", "Branch A",
                   "Branch B", "Branch B", "Leaf A1", "Leaf A1"]
    values_tree = [0, 0, 0, 15, 20, 25, 30, 10, 5]

    fig20 = go.Figure(go.Sunburst(
        labels=labels_tree,
        parents=parents_tree,
        values=values_tree,
        branchvalues="total",
        marker=dict(
            colorscale='earth',
            cmid=25
        ),
        hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Parent: %{parent}<extra></extra>'
    ))

    fig20.update_layout(
        title="20. Radial Tree Visualization"
    )
    plots.append(('pie_20', fig20, {
        'appearance': {
            'title': {'text': 'Radial Tree', 'fontSize': 20}
        }
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} pie chart and related demonstrations"

# Execute when module is run
if __name__ == "__main__" or True:  # Always execute when imported
    result = create_pie_charts()
    print(result)