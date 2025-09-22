"""
Specialty and unique plots demonstration script
Including Parallel Coordinates Plot (PCP), Radar charts, and more
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

def create_specialty_plots():
    """Create comprehensive specialty plot demonstrations"""
    plots = []

    # 1. Parallel Coordinates Plot (PCP)
    np.random.seed(42)
    df_pcp = pd.DataFrame({
        'Car Model': ['Model A', 'Model B', 'Model C', 'Model D', 'Model E'] * 20,
        'Price': np.random.randint(20000, 80000, 100),
        'MPG': np.random.randint(15, 40, 100),
        'Horsepower': np.random.randint(150, 400, 100),
        'Weight': np.random.randint(2500, 4500, 100),
        'Safety Rating': np.random.uniform(3, 5, 100)
    })

    fig1 = go.Figure(data=
        go.Parcoords(
            line=dict(color=df_pcp['Price'],
                     colorscale='viridis',
                     showscale=True),
            dimensions=list([
                dict(range=[20000, 80000],
                     label='Price', values=df_pcp['Price']),
                dict(range=[15, 40],
                     label='MPG', values=df_pcp['MPG']),
                dict(range=[150, 400],
                     label='Horsepower', values=df_pcp['Horsepower']),
                dict(range=[2500, 4500],
                     label='Weight', values=df_pcp['Weight']),
                dict(range=[3, 5],
                     label='Safety', values=df_pcp['Safety Rating'])
            ])
        )
    )

    fig1.update_layout(
        title="1. Parallel Coordinates Plot - Multi-dimensional Car Analysis"
    )
    plots.append(('spec_1', fig1, {
        'appearance': {
            'title': {'text': 'Parallel Coordinates Plot', 'fontSize': 20}
        }
    }))

    # 2. Radar Chart (Spider Plot)
    categories_radar = ['Speed', 'Reliability', 'Comfort', 'Safety', 'Efficiency']

    fig2 = go.Figure()

    # Add multiple traces for comparison
    for i, model in enumerate(['Model A', 'Model B', 'Model C']):
        values = np.random.uniform(3, 5, len(categories_radar))
        values = np.append(values, values[0])  # Close the polygon

        fig2.add_trace(go.Scatterpolar(
            r=values,
            theta=categories_radar + [categories_radar[0]],
            fill='toself',
            name=model,
            opacity=0.6
        ))

    fig2.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        title="2. Radar Chart - Product Comparison",
        showlegend=True
    )
    plots.append(('spec_2', fig2, {
        'appearance': {
            'title': {'text': 'Radar Chart', 'fontSize': 20}
        }
    }))

    # 3. Parallel Categories Plot
    df_parcat = pd.DataFrame({
        'Gender': np.random.choice(['Male', 'Female'], 100),
        'Age Group': np.random.choice(['18-25', '26-35', '36-45', '46+'], 100),
        'Product': np.random.choice(['A', 'B', 'C'], 100),
        'Satisfaction': np.random.choice(['Low', 'Medium', 'High'], 100)
    })

    # Create numeric mapping for coloring
    satisfaction_map = {'Low': 0, 'Medium': 1, 'High': 2}
    colors = df_parcat['Satisfaction'].map(satisfaction_map)

    fig3 = go.Figure(data=[go.Parcats(
        dimensions=[
            {'label': 'Gender', 'values': df_parcat['Gender']},
            {'label': 'Age Group', 'values': df_parcat['Age Group']},
            {'label': 'Product', 'values': df_parcat['Product']},
            {'label': 'Satisfaction', 'values': df_parcat['Satisfaction']}
        ],
        line={'color': colors, 'colorscale': 'rdylgn'},
        hoveron='color',
        hoverinfo='count+probability',
        labelfont={'size': 12},
        tickfont={'size': 11},
        arrangement='freeform'
    )])

    fig3.update_layout(
        title="3. Parallel Categories - Customer Journey Analysis"
    )
    plots.append(('spec_3', fig3, {
        'appearance': {
            'title': {'text': 'Parallel Categories', 'fontSize': 20}
        }
    }))

    # 4. Sankey Diagram
    fig4 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=["Source A", "Source B", "Process 1", "Process 2", "Process 3",
                   "Output X", "Output Y", "Output Z"],
            color=["blue", "blue", "green", "green", "green", "red", "red", "red"]
        ),
        link=dict(
            source=[0, 1, 0, 1, 2, 3, 3, 4, 4],
            target=[2, 2, 3, 4, 5, 5, 6, 6, 7],
            value=[8, 4, 2, 8, 8, 4, 2, 6, 4]
        )
    )])

    fig4.update_layout(
        title="4. Sankey Diagram - Process Flow",
        font_size=10
    )
    plots.append(('spec_4', fig4, {
        'appearance': {
            'title': {'text': 'Sankey Diagram', 'fontSize': 20}
        }
    }))

    # 5. Chord Diagram (using plotly's alternative - circular layout)
    # Create correlation-like data
    n_nodes = 8
    node_names = [f'Node {chr(65+i)}' for i in range(n_nodes)]

    # Create circular layout
    theta = np.linspace(0, 2*np.pi, n_nodes, endpoint=False)
    x_pos = np.cos(theta)
    y_pos = np.sin(theta)

    fig5 = go.Figure()

    # Add connections (simplified chord diagram)
    for i in range(n_nodes):
        for j in range(i+1, n_nodes):
            if np.random.random() > 0.6:  # Random connections
                weight = np.random.uniform(0.2, 1)
                fig5.add_trace(go.Scatter(
                    x=[x_pos[i], x_pos[j]],
                    y=[y_pos[i], y_pos[j]],
                    mode='lines',
                    line=dict(width=weight*5, color='rgba(125, 125, 125, 0.5)'),
                    showlegend=False
                ))

    # Add nodes
    fig5.add_trace(go.Scatter(
        x=x_pos,
        y=y_pos,
        mode='markers+text',
        marker=dict(size=30, color=list(range(n_nodes)), colorscale='rainbow'),
        text=node_names,
        textposition='top center'
    ))

    fig5.update_layout(
        title="5. Circular Network (Chord-like) Diagram",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        showlegend=False
    )
    plots.append(('spec_5', fig5, {
        'appearance': {
            'title': {'text': 'Circular Network', 'fontSize': 20}
        }
    }))

    # 6. Dendogram
    from scipy.cluster import hierarchy
    from scipy.spatial.distance import pdist

    # Generate sample data for clustering
    X = np.random.randn(30, 5)

    # Calculate dendrogram
    dendrogram = hierarchy.dendrogram(hierarchy.linkage(pdist(X), method='ward'), no_plot=True)

    fig6 = go.Figure()

    # Add dendrogram lines
    for i in range(len(dendrogram['icoord'])):
        fig6.add_trace(go.Scatter(
            x=dendrogram['icoord'][i],
            y=dendrogram['dcoord'][i],
            mode='lines',
            line=dict(color='black', width=1),
            showlegend=False
        ))

    fig6.update_layout(
        title="6. Dendrogram - Hierarchical Clustering",
        xaxis_title="Sample Index",
        yaxis_title="Distance"
    )
    plots.append(('spec_6', fig6, {
        'appearance': {
            'title': {'text': 'Dendrogram', 'fontSize': 20}
        }
    }))

    # 7. Network Graph
    # Create network data
    n_network = 15
    edges = []
    for i in range(n_network):
        for j in range(i+1, n_network):
            if np.random.random() > 0.8:
                edges.append((i, j))

    # Create positions using spring layout simulation
    pos = {}
    for i in range(n_network):
        angle = 2 * np.pi * i / n_network
        pos[i] = (np.cos(angle) + np.random.randn()*0.1,
                 np.sin(angle) + np.random.randn()*0.1)

    fig7 = go.Figure()

    # Add edges
    for edge in edges:
        fig7.add_trace(go.Scatter(
            x=[pos[edge[0]][0], pos[edge[1]][0]],
            y=[pos[edge[0]][1], pos[edge[1]][1]],
            mode='lines',
            line=dict(width=1, color='gray'),
            showlegend=False
        ))

    # Add nodes
    node_x = [pos[i][0] for i in range(n_network)]
    node_y = [pos[i][1] for i in range(n_network)]

    fig7.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=20,
            color=list(range(n_network)),
            colorscale='viridis',
            showscale=False
        ),
        text=[f'N{i}' for i in range(n_network)],
        textposition='top center'
    ))

    fig7.update_layout(
        title="7. Network Graph",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        showlegend=False
    )
    plots.append(('spec_7', fig7, {
        'appearance': {
            'title': {'text': 'Network Graph', 'fontSize': 20}
        }
    }))

    # 8. Wind Rose Chart
    wind_directions = np.random.choice([0, 45, 90, 135, 180, 225, 270, 315], 100)
    wind_speeds = np.random.exponential(10, 100)

    fig8 = go.Figure()

    for direction in [0, 45, 90, 135, 180, 225, 270, 315]:
        speeds = wind_speeds[wind_directions == direction]
        if len(speeds) > 0:
            fig8.add_trace(go.Barpolar(
                r=[len(speeds)],
                theta=[direction],
                width=40,
                name=f'{direction}°',
                marker_color=px.colors.sequential.Viridis[direction//45]
            ))

    fig8.update_layout(
        title="8. Wind Rose - Wind Direction Distribution",
        polar=dict(
            angularaxis=dict(
                tickmode='array',
                tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                ticktext=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            ),
            radialaxis=dict(title="Frequency")
        ),
        showlegend=False
    )
    plots.append(('spec_8', fig8, {
        'appearance': {
            'title': {'text': 'Wind Rose Chart', 'fontSize': 20}
        }
    }))

    # 9. Ternary Plot
    a = np.random.uniform(0, 1, 50)
    b = np.random.uniform(0, 1-a, 50)
    c = 1 - a - b

    fig9 = go.Figure(go.Scatterternary(
        a=a,
        b=b,
        c=c,
        mode='markers',
        marker=dict(
            size=10,
            color=a+b*2+c*3,
            colorscale='viridis',
            showscale=True,
            colorbar=dict(title="Composition")
        ),
        text=[f'A:{a[i]:.2f}<br>B:{b[i]:.2f}<br>C:{c[i]:.2f}'
              for i in range(len(a))]
    ))

    fig9.update_layout(
        title="9. Ternary Plot - Three Component System",
        ternary=dict(
            aaxis=dict(title='Component A'),
            baxis=dict(title='Component B'),
            caxis=dict(title='Component C')
        )
    )
    plots.append(('spec_9', fig9, {
        'appearance': {
            'title': {'text': 'Ternary Plot', 'fontSize': 20}
        }
    }))

    # 10. Indicator/Number Cards
    fig10 = go.Figure()

    fig10.add_trace(go.Indicator(
        mode="number+gauge+delta",
        value=85,
        delta={'reference': 70},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "darkblue"},
               'steps': [
                   {'range': [0, 50], 'color': "lightgray"},
                   {'range': [50, 80], 'color': "gray"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 90}},
        title={'text': "Performance Score"},
        domain={'x': [0, 0.45], 'y': [0.5, 1]}
    ))

    fig10.add_trace(go.Indicator(
        mode="number+delta",
        value=450,
        delta={'reference': 400, 'position': "top"},
        title={'text': "Revenue<br><span style='font-size:0.8em'>Thousands</span>"},
        domain={'x': [0.55, 1], 'y': [0.5, 1]}
    ))

    fig10.add_trace(go.Indicator(
        mode="gauge",
        value=65,
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "green"}},
        title={'text': "Efficiency"},
        domain={'x': [0, 0.45], 'y': [0, 0.45]}
    ))

    fig10.add_trace(go.Indicator(
        mode="delta",
        value=40,
        delta={'reference': 60, 'increasing': {'color': "red"}},
        title={'text': "Cost Reduction"},
        domain={'x': [0.55, 1], 'y': [0, 0.45]}
    ))

    fig10.update_layout(
        title="10. KPI Dashboard with Multiple Indicators"
    )
    plots.append(('spec_10', fig10, {
        'appearance': {
            'title': {'text': 'KPI Indicators', 'fontSize': 20}
        }
    }))

    # 11. Word Cloud (Simulated with Scatter)
    words = ['Data', 'Science', 'Machine', 'Learning', 'AI', 'Python', 'Analysis',
             'Visualization', 'Statistics', 'Algorithm', 'Model', 'Neural', 'Deep',
             'Computer', 'Pattern', 'Insight', 'Business', 'Decision', 'Prediction', 'Cloud']

    frequencies = np.random.randint(10, 100, len(words))

    fig11 = go.Figure()

    # Random positioning
    x_pos = np.random.uniform(-10, 10, len(words))
    y_pos = np.random.uniform(-5, 5, len(words))

    fig11.add_trace(go.Scatter(
        x=x_pos,
        y=y_pos,
        mode='text',
        text=words,
        textfont=dict(
            size=frequencies/3,
            color=np.random.choice(px.colors.qualitative.Set3, len(words))
        ),
        showlegend=False
    ))

    fig11.update_layout(
        title="11. Word Cloud (Scatter Text)",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False)
    )
    plots.append(('spec_11', fig11, {
        'appearance': {
            'title': {'text': 'Word Cloud', 'fontSize': 20}
        }
    }))

    # 12. Smith Chart (Simplified)
    theta = np.linspace(0, 2*np.pi, 100)

    fig12 = go.Figure()

    # Add constant resistance circles
    for r in [0.2, 0.5, 1.0, 2.0]:
        x = r/(1+r) + (1/(1+r)) * np.cos(theta)
        y = (1/(1+r)) * np.sin(theta)
        fig12.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            line=dict(color='gray', width=1),
            showlegend=False
        ))

    # Add constant reactance arcs
    for x_val in [-2, -1, -0.5, 0.5, 1, 2]:
        if x_val != 0:
            center = 1/x_val
            radius = abs(1/x_val)
            y_arc = np.linspace(-radius, radius, 50)
            x_arc = center + np.sqrt(radius**2 - y_arc**2)
            fig12.add_trace(go.Scatter(
                x=x_arc, y=y_arc,
                mode='lines',
                line=dict(color='lightgray', width=1),
                showlegend=False
            ))

    fig12.update_layout(
        title="12. Smith Chart (Simplified)",
        xaxis=dict(showgrid=False, zeroline=False, range=[-1, 1]),
        yaxis=dict(showgrid=False, zeroline=False, range=[-1, 1], scaleanchor='x'),
        showlegend=False
    )
    plots.append(('spec_12', fig12, {
        'appearance': {
            'title': {'text': 'Smith Chart', 'fontSize': 20}
        }
    }))

    # 13. Bullet Graph
    fig13 = go.Figure()

    # Background ranges
    fig13.add_trace(go.Bar(
        x=['Metric 1', 'Metric 2', 'Metric 3'],
        y=[100, 100, 100],
        marker_color='lightgray',
        showlegend=False
    ))

    fig13.add_trace(go.Bar(
        x=['Metric 1', 'Metric 2', 'Metric 3'],
        y=[75, 75, 75],
        marker_color='gray',
        showlegend=False
    ))

    fig13.add_trace(go.Bar(
        x=['Metric 1', 'Metric 2', 'Metric 3'],
        y=[50, 50, 50],
        marker_color='darkgray',
        showlegend=False
    ))

    # Actual values
    fig13.add_trace(go.Bar(
        x=['Metric 1', 'Metric 2', 'Metric 3'],
        y=[65, 85, 45],
        marker_color='black',
        width=0.3,
        name='Actual'
    ))

    # Target lines
    for i, (metric, target) in enumerate(zip(['Metric 1', 'Metric 2', 'Metric 3'], [80, 70, 60])):
        fig13.add_shape(
            type="line",
            x0=i-0.4, x1=i+0.4,
            y0=target, y1=target,
            line=dict(color="red", width=3)
        )

    fig13.update_layout(
        title="13. Bullet Graphs",
        yaxis_title="Performance",
        barmode='overlay'
    )
    plots.append(('spec_13', fig13, {
        'appearance': {
            'title': {'text': 'Bullet Graphs', 'fontSize': 20}
        }
    }))

    # 14. Sparklines (Mini Charts)
    from plotly.subplots import make_subplots

    fig14 = make_subplots(
        rows=5, cols=1,
        subplot_titles=('Metric A', 'Metric B', 'Metric C', 'Metric D', 'Metric E'),
        vertical_spacing=0.08,
        row_heights=[0.2]*5
    )

    for i in range(5):
        values = np.cumsum(np.random.randn(50))
        fig14.add_trace(
            go.Scatter(x=list(range(50)), y=values,
                      mode='lines',
                      line=dict(width=2, color=px.colors.qualitative.Set2[i]),
                      showlegend=False),
            row=i+1, col=1
        )

    fig14.update_xaxes(showticklabels=False, showgrid=False)
    fig14.update_yaxes(showticklabels=False, showgrid=False)
    fig14.update_layout(
        title="14. Sparklines - Trend Overview",
        showlegend=False
    )
    plots.append(('spec_14', fig14, {
        'appearance': {
            'title': {'text': 'Sparklines', 'fontSize': 20}
        }
    }))

    # 15. Dumbbell Chart
    categories_db = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    start_values = [20, 35, 15, 45, 30]
    end_values = [45, 55, 35, 65, 50]

    fig15 = go.Figure()

    # Add lines connecting start to end
    for i, cat in enumerate(categories_db):
        fig15.add_trace(go.Scatter(
            x=[start_values[i], end_values[i]],
            y=[cat, cat],
            mode='lines',
            line=dict(color='gray', width=2),
            showlegend=False
        ))

    # Add start points
    fig15.add_trace(go.Scatter(
        x=start_values,
        y=categories_db,
        mode='markers',
        marker=dict(size=12, color='red'),
        name='Before'
    ))

    # Add end points
    fig15.add_trace(go.Scatter(
        x=end_values,
        y=categories_db,
        mode='markers',
        marker=dict(size=12, color='green'),
        name='After'
    ))

    fig15.update_layout(
        title="15. Dumbbell Chart - Before/After Comparison",
        xaxis_title="Value"
    )
    plots.append(('spec_15', fig15, {
        'appearance': {
            'title': {'text': 'Dumbbell Chart', 'fontSize': 20}
        }
    }))

    # 16. Slope Chart
    years = ['2020', '2023']
    companies = ['Company A', 'Company B', 'Company C', 'Company D', 'Company E']
    values_2020 = [45, 38, 52, 41, 44]
    values_2023 = [52, 35, 58, 48, 40]

    fig16 = go.Figure()

    for i, company in enumerate(companies):
        color = 'green' if values_2023[i] > values_2020[i] else 'red'
        fig16.add_trace(go.Scatter(
            x=years,
            y=[values_2020[i], values_2023[i]],
            mode='lines+markers+text',
            line=dict(color=color, width=2),
            marker=dict(size=8),
            text=[f'{company}: {values_2020[i]}', f'{company}: {values_2023[i]}'],
            textposition=['middle left', 'middle right'],
            showlegend=False
        ))

    fig16.update_layout(
        title="16. Slope Chart - Change Over Time",
        xaxis=dict(tickmode='array', tickvals=years),
        yaxis_title="Market Share (%)",
        showlegend=False
    )
    plots.append(('spec_16', fig16, {
        'appearance': {
            'title': {'text': 'Slope Chart', 'fontSize': 20}
        }
    }))

    # 17. Bump Chart (Ranking Over Time)
    months_bump = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    teams = ['Team A', 'Team B', 'Team C', 'Team D', 'Team E']

    fig17 = go.Figure()

    for team in teams:
        rankings = np.random.permutation(range(1, 6))
        rankings = np.concatenate([rankings, [rankings[-1]]])[:6]

        fig17.add_trace(go.Scatter(
            x=months_bump,
            y=rankings,
            mode='lines+markers',
            name=team,
            line=dict(width=3),
            marker=dict(size=10)
        ))

    fig17.update_layout(
        title="17. Bump Chart - Ranking Changes",
        xaxis_title="Month",
        yaxis=dict(
            title="Ranking",
            autorange='reversed',
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=['1st', '2nd', '3rd', '4th', '5th']
        )
    )
    plots.append(('spec_17', fig17, {
        'appearance': {
            'title': {'text': 'Bump Chart', 'fontSize': 20}
        }
    }))

    # 18. Mosaic Plot (Simplified with rectangles)
    fig18 = go.Figure()

    # Create mosaic-like rectangles
    categories_x = ['Cat A', 'Cat B', 'Cat C']
    categories_y = ['Type 1', 'Type 2']

    x_widths = [0.4, 0.35, 0.25]
    y_heights = [0.6, 0.4]

    x_pos = 0
    colors = px.colors.qualitative.Set3

    for i, (cat_x, width) in enumerate(zip(categories_x, x_widths)):
        y_pos = 0
        for j, (cat_y, height) in enumerate(zip(categories_y, y_heights)):
            fig18.add_trace(go.Scatter(
                x=[x_pos, x_pos + width, x_pos + width, x_pos, x_pos],
                y=[y_pos, y_pos, y_pos + height, y_pos + height, y_pos],
                fill='toself',
                fillcolor=colors[i*2 + j],
                line=dict(color='white', width=2),
                showlegend=False,
                text=f'{cat_x}<br>{cat_y}',
                mode='lines+text'
            ))
            y_pos += height
        x_pos += width

    fig18.update_layout(
        title="18. Mosaic Plot - Categorical Proportions",
        xaxis=dict(showgrid=False, showticklabels=False, range=[0, 1]),
        yaxis=dict(showgrid=False, showticklabels=False, range=[0, 1]),
        showlegend=False
    )
    plots.append(('spec_18', fig18, {
        'appearance': {
            'title': {'text': 'Mosaic Plot', 'fontSize': 20}
        }
    }))

    # 19. Hive Plot (Simplified)
    fig19 = go.Figure()

    # Create three axes at 120-degree angles
    angles = [0, 120, 240]
    axis_names = ['Axis A', 'Axis B', 'Axis C']

    # Draw axes
    for angle, name in zip(angles, axis_names):
        rad = np.radians(angle)
        fig19.add_trace(go.Scatter(
            x=[0, np.cos(rad)],
            y=[0, np.sin(rad)],
            mode='lines+text',
            line=dict(color='black', width=2),
            text=['', name],
            textposition='top center',
            showlegend=False
        ))

    # Add some connections
    for _ in range(20):
        source_axis = np.random.choice(3)
        target_axis = np.random.choice(3)
        if source_axis != target_axis:
            source_pos = np.random.uniform(0.2, 0.8)
            target_pos = np.random.uniform(0.2, 0.8)

            source_rad = np.radians(angles[source_axis])
            target_rad = np.radians(angles[target_axis])

            fig19.add_trace(go.Scatter(
                x=[source_pos * np.cos(source_rad), target_pos * np.cos(target_rad)],
                y=[source_pos * np.sin(source_rad), target_pos * np.sin(target_rad)],
                mode='lines',
                line=dict(color='rgba(100, 100, 255, 0.3)', width=1),
                showlegend=False
            ))

    fig19.update_layout(
        title="19. Hive Plot - Network on Radial Axes",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.2, 1.2]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.2, 1.2]),
        showlegend=False
    )
    plots.append(('spec_19', fig19, {
        'appearance': {
            'title': {'text': 'Hive Plot', 'fontSize': 20}
        }
    }))

    # 20. Stream Graph (Stacked Area with Smoothing)
    x_stream = np.linspace(0, 10, 100)
    n_streams = 5

    fig20 = go.Figure()

    # Generate smooth data for streams
    y_accumulated = np.zeros(len(x_stream))

    for i in range(n_streams):
        y_values = np.abs(np.sin(x_stream + i) * np.cos(x_stream * 0.5 + i) * 10 +
                         np.random.randn(len(x_stream)) * 2)

        fig20.add_trace(go.Scatter(
            x=x_stream,
            y=y_accumulated + y_values/2,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

        fig20.add_trace(go.Scatter(
            x=x_stream,
            y=y_accumulated - y_values/2,
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor=px.colors.qualitative.Pastel[i],
            name=f'Stream {i+1}',
            hoverinfo='text',
            text=[f'Stream {i+1}: {val:.1f}' for val in y_values]
        ))

        y_accumulated = y_accumulated + y_values/2

    fig20.update_layout(
        title="20. Stream Graph - Flow Over Time",
        xaxis_title="Time",
        yaxis_title="Value",
        showlegend=True
    )
    plots.append(('spec_20', fig20, {
        'appearance': {
            'title': {'text': 'Stream Graph', 'fontSize': 20}
        }
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} specialty plot demonstrations"

# Execute when module is run
if __name__ == "__main__" or True:  # Always execute when imported
    result = create_specialty_plots()
    print(result)