"""
Mixed Plots and Animations Demo
Shows both static plots and animations in the same grid
"""

import plotly.graph_objects as go
import numpy as np

def create_mixed_visualizations():
    """Create a mix of static plots and animations"""

    # 1. Static Scatter Plot
    x_scatter = np.random.randn(100)
    y_scatter = x_scatter * 2 + np.random.randn(100) * 0.5

    fig_scatter = go.Figure(data=[
        go.Scatter(
            x=x_scatter,
            y=y_scatter,
            mode='markers',
            marker=dict(
                size=8,
                color=y_scatter,
                colorscale='Viridis',
                showscale=True
            )
        )
    ])
    fig_scatter.update_layout(title="Static Scatter Plot")

    register_plot(fig_scatter, plot_id='static_scatter', metadata={
        'appearance': {'title': {'text': 'Static Scatter'}}
    })

    # 2. Animated Sine Wave
    x = np.linspace(0, 4*np.pi, 100)
    frames = []
    for phase in np.linspace(0, 2*np.pi, 20):
        y = np.sin(x + phase)
        frames.append(go.Frame(
            data=[go.Scatter(x=x, y=y, mode='lines', line=dict(color='red', width=3))],
            name=str(phase)
        ))

    fig_animated = go.Figure(
        data=[go.Scatter(x=x, y=np.sin(x), mode='lines', line=dict(color='red', width=3))],
        frames=frames
    )

    fig_animated.update_layout(
        title="Animated Sine Wave",
        showlegend=False
    )

    register_plot(fig_animated, plot_id='animated_sine', metadata={
        'appearance': {'title': {'text': 'Animated Wave'}},
        'isAnimation': True
    })

    # 3. Static Bar Chart
    categories = ['A', 'B', 'C', 'D', 'E']
    values = np.random.randint(10, 100, 5)

    fig_bar = go.Figure(data=[
        go.Bar(x=categories, y=values, marker_color='lightblue')
    ])
    fig_bar.update_layout(title="Static Bar Chart")

    register_plot(fig_bar, plot_id='static_bar', metadata={
        'appearance': {'title': {'text': 'Static Bar Chart'}}
    })

    # 4. Animated Bubble Chart
    n_frames = 15
    n_points = 20
    frames_bubble = []

    for i in range(n_frames):
        x = np.random.randn(n_points) * (1 + i * 0.1)
        y = np.random.randn(n_points) * (1 + i * 0.1)
        size = np.random.randint(10, 40, n_points)

        frames_bubble.append(go.Frame(
            data=[go.Scatter(
                x=x, y=y,
                mode='markers',
                marker=dict(
                    size=size,
                    color=np.sqrt(x**2 + y**2),
                    colorscale='Rainbow',
                    showscale=True
                )
            )],
            name=f'frame_{i}'
        ))

    fig_bubble = go.Figure(
        data=[go.Scatter(
            x=np.random.randn(n_points),
            y=np.random.randn(n_points),
            mode='markers',
            marker=dict(size=20)
        )],
        frames=frames_bubble
    )

    fig_bubble.update_layout(
        title="Animated Bubbles",
        xaxis=dict(range=[-5, 5]),
        yaxis=dict(range=[-5, 5]),
        showlegend=False
    )

    register_plot(fig_bubble, plot_id='animated_bubbles', metadata={
        'appearance': {'title': {'text': 'Animated Bubbles'}},
        'isAnimation': True
    })

    # 5. Static Heatmap
    z = np.random.randn(20, 20)
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=z,
        colorscale='RdBu',
        zmid=0
    ))
    fig_heatmap.update_layout(title="Static Heatmap")

    register_plot(fig_heatmap, plot_id='static_heatmap', metadata={
        'appearance': {'title': {'text': 'Static Heatmap'}}
    })

    # 6. Static Line Plot
    x_line = np.linspace(0, 10, 100)
    y_line = np.cumsum(np.random.randn(100) * 0.1)

    fig_line = go.Figure(data=[
        go.Scatter(x=x_line, y=y_line, mode='lines', line=dict(color='green', width=2))
    ])
    fig_line.update_layout(title="Static Line Plot")

    register_plot(fig_line, plot_id='static_line', metadata={
        'appearance': {'title': {'text': 'Static Line Plot'}}
    })

    return "Created 6 visualizations: 4 static plots and 2 animations"

# Execute when imported or run
if __name__ == "__main__" or True:
    result = create_mixed_visualizations()
    print(result)