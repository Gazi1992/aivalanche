"""
3D plots demonstration script
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

def create_3d_plots():
    """Create comprehensive 3D plot demonstrations"""
    plots = []

    # 1. Basic 3D Surface Plot
    x = np.linspace(-5, 5, 50)
    y = np.linspace(-5, 5, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(np.sqrt(X**2 + Y**2))

    fig1 = go.Figure(data=[go.Surface(z=Z, x=x, y=y)])
    fig1.update_layout(
        title="1. Basic 3D Surface - Ripple Effect",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )
    plots.append(('3d_1', fig1, {
        'appearance': {
            'title': {'text': '3D Surface Plot', 'fontSize': 20}
        }
    }))

    # 2. 3D Scatter Plot
    np.random.seed(42)
    n_points = 100
    x_scatter = np.random.randn(n_points)
    y_scatter = np.random.randn(n_points)
    z_scatter = np.random.randn(n_points)
    colors = np.random.randn(n_points)

    fig2 = go.Figure(data=[go.Scatter3d(
        x=x_scatter,
        y=y_scatter,
        z=z_scatter,
        mode='markers',
        marker=dict(
            size=8,
            color=colors,
            colorscale='viridis',
            showscale=True,
            opacity=0.8
        )
    )])

    fig2.update_layout(
        title="2. 3D Scatter Plot - Random Distribution",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )
    plots.append(('3d_2', fig2, {
        'appearance': {
            'title': {'text': '3D Scatter Plot', 'fontSize': 20}
        }
    }))

    # 3. 3D Line Plot
    t = np.linspace(0, 20, 100)
    x_line = t * np.cos(t)
    y_line = t * np.sin(t)
    z_line = t

    fig3 = go.Figure(data=[go.Scatter3d(
        x=x_line,
        y=y_line,
        z=z_line,
        mode='lines',
        line=dict(
            color=z_line,
            colorscale='rainbow',
            width=4
        )
    )])

    fig3.update_layout(
        title="3. 3D Line Plot - Spiral",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )
    plots.append(('3d_3', fig3, {
        'appearance': {
            'title': {'text': '3D Line Plot', 'fontSize': 20}
        }
    }))

    # 4. 3D Mesh Plot
    # Create vertices
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # Bottom
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]   # Top
    ])

    # Define the triangles
    i = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
    j = [1, 2, 3, 4, 2, 5, 3, 6, 0, 7, 5, 7]
    k = [2, 3, 4, 1, 5, 2, 6, 3, 7, 4, 7, 6]

    fig4 = go.Figure(data=[go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=i, j=j, k=k,
        color='cyan',
        opacity=0.7
    )])

    fig4.update_layout(
        title="4. 3D Mesh Plot - Cube",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )
    plots.append(('3d_4', fig4, {
        'appearance': {
            'title': {'text': '3D Mesh Plot', 'fontSize': 20}
        }
    }))

    # 5. Multiple 3D Surfaces
    fig5 = go.Figure()

    # First surface
    Z1 = np.sin(np.sqrt(X**2 + Y**2))
    fig5.add_trace(go.Surface(z=Z1, x=x, y=y, colorscale='viridis', showscale=False, opacity=0.9))

    # Second surface
    Z2 = np.cos(np.sqrt(X**2 + Y**2)) - 2
    fig5.add_trace(go.Surface(z=Z2, x=x, y=y, colorscale='plasma', showscale=False, opacity=0.9))

    fig5.update_layout(
        title="5. Multiple 3D Surfaces",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )
    plots.append(('3d_5', fig5, {
        'appearance': {
            'title': {'text': 'Multiple Surfaces', 'fontSize': 20}
        }
    }))

    # 6. 3D Contour Plot
    fig6 = go.Figure(data=[go.Surface(
        z=Z,
        x=x,
        y=y,
        contours=dict(
            z=dict(
                show=True,
                usecolormap=True,
                highlightcolor="limegreen",
                project=dict(z=True)
            )
        )
    )])

    fig6.update_layout(
        title="6. 3D Surface with Contours",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )
    plots.append(('3d_6', fig6, {
        'appearance': {
            'title': {'text': '3D Contour Surface', 'fontSize': 20}
        }
    }))

    # 7. 3D Parametric Surface
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    U, V = np.meshgrid(u, v)

    # Sphere parametrization
    X_sphere = np.cos(U) * np.sin(V)
    Y_sphere = np.sin(U) * np.sin(V)
    Z_sphere = np.cos(V)

    fig7 = go.Figure(data=[go.Surface(
        x=X_sphere,
        y=Y_sphere,
        z=Z_sphere,
        colorscale='earth'
    )])

    fig7.update_layout(
        title="7. 3D Parametric Surface - Sphere",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            aspectmode='cube'
        )
    )
    plots.append(('3d_7', fig7, {
        'appearance': {
            'title': {'text': 'Parametric Sphere', 'fontSize': 20}
        }
    }))

    # 8. 3D Bar Plot
    x_bar = ['A', 'B', 'C', 'D', 'E']
    y_bar = ['Type 1', 'Type 2', 'Type 3']
    z_bar = [[20, 15, 25, 30, 22],
             [25, 20, 15, 25, 18],
             [15, 25, 20, 15, 20]]

    fig8 = go.Figure(data=[go.Surface(z=z_bar)])
    fig8.update_traces(
        contours_z=dict(
            show=True, usecolormap=True,
            highlightcolor="limegreen", project_z=True
        )
    )

    fig8.update_layout(
        title="8. 3D Bar Surface",
        scene=dict(
            xaxis=dict(ticktext=x_bar, tickvals=list(range(len(x_bar))), title="Category"),
            yaxis=dict(ticktext=y_bar, tickvals=list(range(len(y_bar))), title="Type"),
            zaxis_title="Value"
        )
    )
    plots.append(('3d_8', fig8, {
        'appearance': {
            'title': {'text': '3D Bar Surface', 'fontSize': 20}
        }
    }))

    # 9. 3D Isosurface
    X_vol = np.linspace(-5, 5, 40)
    Y_vol = np.linspace(-5, 5, 40)
    Z_vol = np.linspace(-5, 5, 40)

    values = []
    for z in Z_vol:
        for y in Y_vol:
            for x in X_vol:
                values.append(x**2 + y**2 + z**2)

    fig9 = go.Figure(data=go.Isosurface(
        x=X_vol.flatten(),
        y=Y_vol.flatten(),
        z=Z_vol.flatten(),
        value=values,
        isomin=10,
        isomax=40,
        surface_count=3,
        colorscale='viridis'
    ))

    fig9.update_layout(
        title="9. 3D Isosurface - Nested Spheres",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )
    plots.append(('3d_9', fig9, {
        'appearance': {
            'title': {'text': '3D Isosurface', 'fontSize': 20}
        }
    }))

    # 10. 3D Ribbon Plot
    n_ribbons = 5
    fig10 = go.Figure()

    for i in range(n_ribbons):
        t = np.linspace(0, 10, 100)
        x_ribbon = t
        y_ribbon = np.sin(t + i) * (i + 1)
        z_ribbon = np.cos(t) * (i + 1)

        fig10.add_trace(go.Scatter3d(
            x=x_ribbon,
            y=[i] * len(x_ribbon),
            z=z_ribbon,
            mode='lines',
            line=dict(
                color=z_ribbon,
                colorscale='rainbow',
                width=6
            ),
            name=f'Ribbon {i+1}'
        ))

    fig10.update_layout(
        title="10. 3D Ribbon Plot",
        scene=dict(
            xaxis_title="Time",
            yaxis_title="Series",
            zaxis_title="Value"
        )
    )
    plots.append(('3d_10', fig10, {
        'appearance': {
            'title': {'text': '3D Ribbon Plot', 'fontSize': 20}
        }
    }))

    # 11. 3D Bubble Chart
    np.random.seed(42)
    df_bubble = pd.DataFrame({
        'x': np.random.randn(50),
        'y': np.random.randn(50),
        'z': np.random.randn(50),
        'size': np.random.randint(10, 50, 50),
        'category': np.random.choice(['A', 'B', 'C'], 50)
    })

    fig11 = px.scatter_3d(df_bubble, x='x', y='y', z='z',
                          size='size', color='category',
                          title="11. 3D Bubble Chart")
    plots.append(('3d_11', fig11, {
        'appearance': {
            'title': {'text': '3D Bubble Chart', 'fontSize': 20}
        }
    }))

    # 12. 3D Wireframe
    # Re-create x and y arrays as they might have been overwritten
    x_wire = np.linspace(-5, 5, 50)
    y_wire = np.linspace(-5, 5, 50)
    fig12 = go.Figure(data=[go.Surface(
        z=Z,
        x=x_wire,
        y=y_wire,
        hidesurface=True,
        contours=dict(
            x=dict(show=True, color="white", width=1, usecolormap=False),
            y=dict(show=True, color="white", width=1, usecolormap=False),
            z=dict(show=True, color="white", width=1, usecolormap=False)
        )
    )])

    # Add the wireframe
    for i in range(0, len(x_wire), 2):
        fig12.add_trace(go.Scatter3d(
            x=[x_wire[i]] * len(y_wire),
            y=y_wire,
            z=Z[:, i],
            mode='lines',
            line=dict(color='blue', width=2),
            showlegend=False
        ))

    fig12.update_layout(
        title="12. 3D Wireframe",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )
    plots.append(('3d_12', fig12, {
        'appearance': {
            'title': {'text': '3D Wireframe', 'fontSize': 20}
        }
    }))

    # 13. 3D Cone Plot (Vector Field)
    x_cone = np.linspace(-2, 2, 6)
    y_cone = np.linspace(-2, 2, 6)
    z_cone = np.linspace(-2, 2, 6)

    X_cone, Y_cone, Z_cone = np.meshgrid(x_cone, y_cone, z_cone)

    # Vector field components
    U = np.sin(np.pi * X_cone) * np.cos(np.pi * Y_cone) * np.cos(np.pi * Z_cone)
    V = -np.cos(np.pi * X_cone) * np.sin(np.pi * Y_cone) * np.cos(np.pi * Z_cone)
    W = np.sqrt(2/3) * np.cos(np.pi * X_cone) * np.cos(np.pi * Y_cone) * np.sin(np.pi * Z_cone)

    fig13 = go.Figure(data=go.Cone(
        x=X_cone.flatten(),
        y=Y_cone.flatten(),
        z=Z_cone.flatten(),
        u=U.flatten(),
        v=V.flatten(),
        w=W.flatten(),
        sizemode="absolute",
        sizeref=0.5,
        colorscale='rainbow'
    ))

    fig13.update_layout(
        title="13. 3D Vector Field (Cone Plot)",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            aspectmode='cube'
        )
    )
    plots.append(('3d_13', fig13, {
        'appearance': {
            'title': {'text': '3D Vector Field', 'fontSize': 20}
        }
    }))

    # 14. 3D Streamtube
    # Create a simple vector field
    x_stream = np.linspace(-3, 3, 10)
    y_stream = np.linspace(-3, 3, 10)
    z_stream = np.linspace(0, 3, 5)

    X_stream, Y_stream, Z_stream = np.meshgrid(x_stream, y_stream, z_stream)

    # Circular flow field
    U_stream = -Y_stream
    V_stream = X_stream
    W_stream = np.zeros_like(X_stream)

    fig14 = go.Figure(data=go.Streamtube(
        x=X_stream.flatten(),
        y=Y_stream.flatten(),
        z=Z_stream.flatten(),
        u=U_stream.flatten(),
        v=V_stream.flatten(),
        w=W_stream.flatten(),
        starts=dict(
            x=[0, 0.5, 1],
            y=[0, 0.5, 1],
            z=[0, 0, 0]
        ),
        sizeref=0.2,
        colorscale='portland'
    ))

    fig14.update_layout(
        title="14. 3D Streamtube - Flow Visualization",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )
    plots.append(('3d_14', fig14, {
        'appearance': {
            'title': {'text': '3D Streamtube', 'fontSize': 20}
        }
    }))

    # 15. 3D Torus
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, 2 * np.pi, 50)
    U, V = np.meshgrid(u, v)

    # Torus parametrization
    R = 3  # Major radius
    r = 1  # Minor radius
    X_torus = (R + r * np.cos(V)) * np.cos(U)
    Y_torus = (R + r * np.cos(V)) * np.sin(U)
    Z_torus = r * np.sin(V)

    fig15 = go.Figure(data=[go.Surface(
        x=X_torus,
        y=Y_torus,
        z=Z_torus,
        colorscale='sunset',
        showscale=False
    )])

    fig15.update_layout(
        title="15. 3D Torus",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            aspectmode='data'
        )
    )
    plots.append(('3d_15', fig15, {
        'appearance': {
            'title': {'text': '3D Torus', 'fontSize': 20}
        }
    }))

    # 16. 3D Terrain Map
    # Simulate terrain data
    x_terrain = np.linspace(0, 10, 100)
    y_terrain = np.linspace(0, 10, 100)
    X_terrain, Y_terrain = np.meshgrid(x_terrain, y_terrain)

    # Create terrain-like surface
    Z_terrain = (np.sin(X_terrain * 0.5) * np.cos(Y_terrain * 0.5) * 2 +
                 np.sin(X_terrain * 0.2) * 3 +
                 np.cos(Y_terrain * 0.3) * 2 +
                 np.random.randn(100, 100) * 0.5)

    fig16 = go.Figure(data=[go.Surface(
        z=Z_terrain,
        x=x_terrain,
        y=y_terrain,
        colorscale='earth',
        contours=dict(
            z=dict(show=True, start=-5, end=5, size=0.5, color="white", width=1)
        )
    )])

    fig16.update_layout(
        title="16. 3D Terrain Map",
        scene=dict(
            xaxis_title="East-West (km)",
            yaxis_title="North-South (km)",
            zaxis_title="Elevation (m)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        )
    )
    plots.append(('3d_16', fig16, {
        'appearance': {
            'title': {'text': '3D Terrain Map', 'fontSize': 20}
        }
    }))

    # 17. 3D Scatter with Lines
    # Create connected scatter plot
    t = np.linspace(0, 10, 50)
    fig17 = go.Figure()

    # Add multiple trajectories
    for i in range(3):
        x_traj = t * np.cos(t + i)
        y_traj = t * np.sin(t + i)
        z_traj = t + i * 2

        fig17.add_trace(go.Scatter3d(
            x=x_traj,
            y=y_traj,
            z=z_traj,
            mode='lines+markers',
            marker=dict(size=4, color=z_traj, colorscale='viridis'),
            line=dict(color='darkblue', width=2),
            name=f'Trajectory {i+1}'
        ))

    fig17.update_layout(
        title="17. 3D Trajectories",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )
    plots.append(('3d_17', fig17, {
        'appearance': {
            'title': {'text': '3D Trajectories', 'fontSize': 20}
        }
    }))

    # 18. 3D Density Plot (Volume)
    # Create 3D gaussian distribution
    x_dens = np.linspace(-3, 3, 30)
    y_dens = np.linspace(-3, 3, 30)
    z_dens = np.linspace(-3, 3, 30)
    X_dens, Y_dens, Z_dens = np.meshgrid(x_dens, y_dens, z_dens)

    values_dens = np.exp(-(X_dens**2 + Y_dens**2 + Z_dens**2))

    fig18 = go.Figure(data=go.Volume(
        x=X_dens.flatten(),
        y=Y_dens.flatten(),
        z=Z_dens.flatten(),
        value=values_dens.flatten(),
        opacity=0.2,
        surface_count=5,
        colorscale='jet'
    ))

    fig18.update_layout(
        title="18. 3D Volume Density Plot",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        )
    )
    plots.append(('3d_18', fig18, {
        'appearance': {
            'title': {'text': '3D Volume Density', 'fontSize': 20}
        }
    }))

    # 19. 3D Klein Bottle (Complex Surface)
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, 2 * np.pi, 50)
    U, V = np.meshgrid(u, v)

    # Klein bottle parametrization (immersed in 3D)
    a = 2
    X_klein = (a + np.cos(U/2) * np.sin(V) - np.sin(U/2) * np.sin(2*V)) * np.cos(U)
    Y_klein = (a + np.cos(U/2) * np.sin(V) - np.sin(U/2) * np.sin(2*V)) * np.sin(U)
    Z_klein = np.sin(U/2) * np.sin(V) + np.cos(U/2) * np.sin(2*V)

    fig19 = go.Figure(data=[go.Surface(
        x=X_klein,
        y=Y_klein,
        z=Z_klein,
        colorscale='twilight',
        showscale=False
    )])

    fig19.update_layout(
        title="19. 3D Klein Bottle",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            aspectmode='data'
        )
    )
    plots.append(('3d_19', fig19, {
        'appearance': {
            'title': {'text': '3D Klein Bottle', 'fontSize': 20}
        }
    }))

    # 20. 3D Animation (Rotating Surface)
    # Re-create x and y arrays for the animation
    x_anim = np.linspace(-5, 5, 50)
    y_anim = np.linspace(-5, 5, 50)
    frames = []
    for k in range(10):
        Z_anim = np.sin(np.sqrt(X**2 + Y**2) - k * 0.5)
        frames.append(go.Frame(data=[go.Surface(z=Z_anim, x=x_anim, y=y_anim)], name=str(k)))

    fig20 = go.Figure(
        data=[go.Surface(z=Z, x=x_anim, y=y_anim, colorscale='viridis')],
        frames=frames
    )

    fig20.update_layout(
        title="20. 3D Animated Wave",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        ),
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {'label': 'Play', 'method': 'animate', 'args': [None, {'frame': {'duration': 100}}]},
                {'label': 'Pause', 'method': 'animate', 'args': [[None], {'frame': {'duration': 0}}]}
            ]
        }]
    )
    plots.append(('3d_20', fig20, {
        'appearance': {
            'title': {'text': '3D Animated Wave', 'fontSize': 20}
        }
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} 3D plot demonstrations"

# Execute when module is run
if __name__ == "__main__" or True:  # Always execute when imported
    result = create_3d_plots()
    print(result)