"""
Animation Demo
Testing Plotly animations through the Python executor
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd

def create_animation_plots():
    """Create animated visualizations to test animation support"""
    plots = []

    # 1. Simple Line Animation - Sine Wave Evolution
    x = np.linspace(0, 4*np.pi, 100)

    # Create frames for animation
    frames = []
    for phase in np.linspace(0, 2*np.pi, 30):
        y = np.sin(x + phase)
        frames.append(go.Frame(
            data=[go.Scatter(x=x, y=y, mode='lines', line=dict(color='blue', width=2))],
            name=str(phase)
        ))

    # Initial frame
    fig1 = go.Figure(
        data=[go.Scatter(x=x, y=np.sin(x), mode='lines', line=dict(color='blue', width=2))],
        frames=frames
    )

    # Add play/pause buttons
    fig1.update_layout(
        title="Animated Sine Wave",
        xaxis_title="X",
        yaxis_title="Y",
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 50, 'redraw': True},
                        'fromcurrent': True,
                        'mode': 'immediate'
                    }]
                },
                {
                    'label': 'Pause',
                    'method': 'animate',
                    'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate'
                    }]
                }
            ]
        }],
        sliders=[{
            'steps': [
                {
                    'args': [[f.name], {'frame': {'duration': 50, 'redraw': True}}],
                    'label': str(i),
                    'method': 'animate'
                } for i, f in enumerate(fig1.frames)
            ],
            'active': 0,
            'y': 0,
            'len': 0.9,
            'x': 0.05,
            'xanchor': 'left',
            'y': 0,
            'yanchor': 'top'
        }]
    )

    plots.append(('animation_sine', fig1, {
        'appearance': {'title': {'text': 'Animated Sine Wave'}},
        'animation': True
    }))

    # 2. Scatter Plot Animation - Particle Movement
    n_frames = 30
    n_points = 50

    # Generate random walk data
    frames_scatter = []
    x_pos = np.random.randn(n_points)
    y_pos = np.random.randn(n_points)

    for i in range(n_frames):
        x_pos += np.random.randn(n_points) * 0.1
        y_pos += np.random.randn(n_points) * 0.1

        frames_scatter.append(go.Frame(
            data=[go.Scatter(
                x=x_pos.copy(),
                y=y_pos.copy(),
                mode='markers',
                marker=dict(
                    size=10,
                    color=np.sqrt(x_pos**2 + y_pos**2),
                    colorscale='Viridis',
                    showscale=True
                )
            )],
            name=str(i)
        ))

    # Initial scatter
    fig2 = go.Figure(
        data=[go.Scatter(
            x=np.random.randn(n_points),
            y=np.random.randn(n_points),
            mode='markers',
            marker=dict(size=10, color='blue')
        )],
        frames=frames_scatter
    )

    fig2.update_layout(
        title="Animated Particle Movement",
        xaxis=dict(range=[-5, 5]),
        yaxis=dict(range=[-5, 5]),
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 100, 'redraw': True},
                        'fromcurrent': True
                    }]
                },
                {
                    'label': 'Pause',
                    'method': 'animate',
                    'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate'
                    }]
                }
            ]
        }]
    )

    plots.append(('animation_scatter', fig2, {
        'appearance': {'title': {'text': 'Particle Animation'}},
        'animation': True
    }))

    # 3. Bar Chart Race Animation
    categories = ['A', 'B', 'C', 'D', 'E']
    frames_bar = []

    for i in range(20):
        values = np.random.randint(10, 100, size=5)
        frames_bar.append(go.Frame(
            data=[go.Bar(x=categories, y=values, marker_color='lightblue')],
            name=str(i)
        ))

    fig3 = go.Figure(
        data=[go.Bar(x=categories, y=np.random.randint(10, 100, size=5))],
        frames=frames_bar
    )

    fig3.update_layout(
        title="Animated Bar Chart",
        xaxis_title="Category",
        yaxis_title="Value",
        yaxis=dict(range=[0, 100]),
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 200, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 100, 'easing': 'cubic-in-out'}
                    }]
                },
                {
                    'label': 'Pause',
                    'method': 'animate',
                    'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate'
                    }]
                }
            ]
        }]
    )

    plots.append(('animation_bar', fig3, {
        'appearance': {'title': {'text': 'Bar Chart Animation'}},
        'animation': True
    }))

    # 4. 3D Surface Animation
    x_3d = np.linspace(-5, 5, 50)
    y_3d = np.linspace(-5, 5, 50)
    X, Y = np.meshgrid(x_3d, y_3d)

    frames_3d = []
    for t in np.linspace(0, 2*np.pi, 20):
        Z = np.sin(np.sqrt(X**2 + Y**2) + t)
        frames_3d.append(go.Frame(
            data=[go.Surface(x=X, y=Y, z=Z, colorscale='Viridis')],
            name=str(t)
        ))

    fig4 = go.Figure(
        data=[go.Surface(x=X, y=Y, z=np.sin(np.sqrt(X**2 + Y**2)), colorscale='Viridis')],
        frames=frames_3d
    )

    fig4.update_layout(
        title="3D Surface Wave Animation",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        ),
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 100, 'redraw': True},
                        'fromcurrent': True
                    }]
                },
                {
                    'label': 'Pause',
                    'method': 'animate',
                    'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate'
                    }]
                }
            ]
        }]
    )

    plots.append(('animation_3d', fig4, {
        'appearance': {'title': {'text': '3D Wave Animation'}},
        'animation': True
    }))

    # Register all animated plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} animated visualizations"

# Execute when imported or run
if __name__ == "__main__" or True:
    result = create_animation_plots()
    print(result)