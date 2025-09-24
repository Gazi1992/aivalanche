"""
Plotly Animations Demo
Demonstrates various animation types that work with our executor
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd

def create_plotly_animations():
    """Create Plotly native animations"""

    # 1. Simple Sine Wave Animation
    x = np.linspace(0, 4*np.pi, 100)

    # Create frames for animation
    frames = []
    for phase in np.linspace(0, 2*np.pi, 30):
        y = np.sin(x + phase)
        frames.append(go.Frame(
            data=[go.Scatter(x=x, y=y, mode='lines', line=dict(color='blue', width=2))],
            name=str(phase)
        ))

    # Create figure with initial frame
    fig1 = go.Figure(
        data=[go.Scatter(x=x, y=np.sin(x), mode='lines', line=dict(color='blue', width=2))],
        frames=frames
    )

    # Add animation controls
    fig1.update_layout(
        title="Animated Sine Wave",
        xaxis_title="X",
        yaxis_title="Y",
        showlegend=False
    )

    register_plot(fig1, plot_id='sine_wave_animation', metadata={
        'appearance': {'title': {'text': 'Sine Wave Animation'}},
        'animationSpeed': 50
    })

    # 2. Animated Scatter Plot - Bubbles
    n_frames = 20
    n_points = 30

    frames_scatter = []
    for i in range(n_frames):
        # Create random data for each frame
        x = np.random.randn(n_points)
        y = np.random.randn(n_points)
        size = np.random.randint(10, 50, n_points)
        color = np.random.rand(n_points)

        frames_scatter.append(go.Frame(
            data=[go.Scatter(
                x=x,
                y=y,
                mode='markers',
                marker=dict(
                    size=size,
                    color=color,
                    colorscale='Viridis',
                    showscale=True
                )
            )],
            name=f'frame_{i}'
        ))

    fig2 = go.Figure(
        data=[go.Scatter(
            x=np.random.randn(n_points),
            y=np.random.randn(n_points),
            mode='markers',
            marker=dict(size=20, color='blue')
        )],
        frames=frames_scatter
    )

    fig2.update_layout(
        title="Animated Bubble Chart",
        xaxis=dict(range=[-4, 4]),
        yaxis=dict(range=[-4, 4]),
        showlegend=False
    )

    register_plot(fig2, plot_id='bubble_animation', metadata={
        'appearance': {'title': {'text': 'Bubble Animation'}},
        'animationSpeed': 100
    })

    # 3. Bar Chart Race
    categories = ['Product A', 'Product B', 'Product C', 'Product D']
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

    frames_bar = []
    cumulative_values = np.zeros(4)

    for month_idx, month in enumerate(months):
        # Simulate growing sales data
        month_sales = np.random.randint(10, 50, 4)
        cumulative_values += month_sales

        frames_bar.append(go.Frame(
            data=[go.Bar(
                x=categories,
                y=cumulative_values.copy(),
                text=[f'${v:,.0f}' for v in cumulative_values],
                textposition='outside',
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            )],
            name=month,
            layout=go.Layout(title_text=f"Sales Through {month}")
        ))

    fig3 = go.Figure(
        data=[go.Bar(
            x=categories,
            y=[0, 0, 0, 0],
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        )],
        frames=frames_bar
    )

    fig3.update_layout(
        title="Animated Sales Bar Chart",
        xaxis_title="Product",
        yaxis_title="Cumulative Sales ($)",
        yaxis=dict(range=[0, 300]),
        showlegend=False
    )

    register_plot(fig3, plot_id='bar_race_animation', metadata={
        'appearance': {'title': {'text': 'Bar Chart Race'}},
        'animationSpeed': 500,
        'transitionSpeed': 300
    })

    # 4. 3D Surface Animation
    x = np.linspace(-5, 5, 30)
    y = np.linspace(-5, 5, 30)
    X, Y = np.meshgrid(x, y)

    frames_3d = []
    for t in np.linspace(0, 2*np.pi, 15):
        Z = np.sin(np.sqrt(X**2 + Y**2) - t) * np.exp(-0.1 * np.sqrt(X**2 + Y**2))
        frames_3d.append(go.Frame(
            data=[go.Surface(x=X, y=Y, z=Z, colorscale='Viridis')],
            name=f't_{t:.2f}'
        ))

    fig4 = go.Figure(
        data=[go.Surface(
            x=X, y=Y,
            z=np.sin(np.sqrt(X**2 + Y**2)) * np.exp(-0.1 * np.sqrt(X**2 + Y**2)),
            colorscale='Viridis'
        )],
        frames=frames_3d
    )

    fig4.update_layout(
        title="3D Wave Animation",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        ),
        showlegend=False
    )

    register_plot(fig4, plot_id='wave_3d_animation', metadata={
        'appearance': {'title': {'text': '3D Wave Animation'}},
        'animationSpeed': 100
    })

    return "Created 4 Plotly animations"

# Execute when imported or run
if __name__ == "__main__" or True:
    result = create_plotly_animations()
    print(result)