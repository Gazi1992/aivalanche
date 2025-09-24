"""
Engineering Analysis Demo
Real-world engineering examples including stress analysis, sensor data, and system performance
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_engineering_plots():
    """Create engineering analysis visualizations"""
    plots = []

    # 1. Stress-Strain Curve (Scatter + Line)
    strain = np.linspace(0, 0.3, 100)
    # Typical steel stress-strain curve
    yield_point = 0.002
    stress = np.where(strain < yield_point,
                     strain * 200e9 / 1000,  # Elastic region (Hooke's law) in MPa
                     250 + 100 * np.log(1 + (strain - yield_point) * 50))  # Plastic region

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=strain,
        y=stress,
        mode='lines',
        name='Steel A36',
        line=dict(color='blue', width=3)
    ))
    # Add yield point marker
    fig1.add_trace(go.Scatter(
        x=[yield_point],
        y=[250],
        mode='markers',
        name='Yield Point',
        marker=dict(size=12, color='red', symbol='diamond')
    ))
    fig1.update_layout(
        title="Material Stress-Strain Analysis",
        xaxis_title="Strain (mm/mm)",
        yaxis_title="Stress (MPa)",
        hovermode='x unified'
    )
    plots.append(('eng_stress_strain', fig1, {
        'appearance': {'title': {'text': 'Stress-Strain Curve'}}
    }))

    # 2. Temperature Distribution Heatmap
    # Simulate 2D temperature distribution on a plate
    x = np.linspace(0, 1, 50)
    y = np.linspace(0, 1, 50)
    X, Y = np.meshgrid(x, y)
    # Heat source at center with cooling at edges
    Z = 100 * np.exp(-((X-0.5)**2 + (Y-0.5)**2) * 10) + 20  # Temperature in Celsius

    fig2 = go.Figure(data=go.Heatmap(
        z=Z,
        x=x * 100,  # Convert to cm
        y=y * 100,
        colorscale='Jet',
        colorbar=dict(title="Temperature (°C)")
    ))
    fig2.update_layout(
        title="Thermal Distribution on Heated Plate",
        xaxis_title="Width (cm)",
        yaxis_title="Height (cm)"
    )
    plots.append(('eng_thermal_dist', fig2, {
        'appearance': {'title': {'text': 'Temperature Distribution'}}
    }))

    # 3. Vibration Analysis (Multi-line Time Series)
    time = np.linspace(0, 2, 1000)  # 2 seconds
    # Multiple frequency components (machine vibration)
    freq1, freq2, freq3 = 50, 120, 180  # Hz
    signal1 = 2 * np.sin(2 * np.pi * freq1 * time) + np.random.normal(0, 0.1, len(time))
    signal2 = 1.5 * np.sin(2 * np.pi * freq2 * time + np.pi/4) + np.random.normal(0, 0.1, len(time))
    signal3 = 0.8 * np.sin(2 * np.pi * freq3 * time + np.pi/2) + np.random.normal(0, 0.1, len(time))

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=time, y=signal1, mode='lines', name='Sensor 1', line=dict(width=1)))
    fig3.add_trace(go.Scatter(x=time, y=signal2, mode='lines', name='Sensor 2', line=dict(width=1)))
    fig3.add_trace(go.Scatter(x=time, y=signal3, mode='lines', name='Sensor 3', line=dict(width=1)))
    fig3.update_layout(
        title="Vibration Analysis - Multi-Sensor Data",
        xaxis_title="Time (seconds)",
        yaxis_title="Amplitude (mm)",
        hovermode='x unified'
    )
    plots.append(('eng_vibration', fig3, {
        'appearance': {'title': {'text': 'Vibration Analysis'}}
    }))

    # 4. 3D Surface - Pressure Distribution
    x = np.linspace(-5, 5, 50)
    y = np.linspace(-5, 5, 50)
    X, Y = np.meshgrid(x, y)
    # Pressure field around airfoil
    Z = 101325 + 1000 * (np.sin(np.sqrt(X**2 + Y**2)) / np.sqrt(X**2 + Y**2 + 0.1))  # Pressure in Pa

    fig4 = go.Figure(data=[go.Surface(
        z=Z/1000,  # Convert to kPa
        x=X,
        y=Y,
        colorscale='Viridis',
        colorbar=dict(title="Pressure (kPa)")
    )])
    fig4.update_layout(
        title="3D Pressure Field Simulation",
        scene=dict(
            xaxis_title="X Position (m)",
            yaxis_title="Y Position (m)",
            zaxis_title="Pressure (kPa)"
        )
    )
    plots.append(('eng_pressure_3d', fig4, {
        'appearance': {'title': {'text': '3D Pressure Field'}}
    }))

    # 5. Flow Rate Waterfall Chart
    categories = ['Initial Flow', 'Pump 1', 'Pump 2', 'Valve Loss', 'Friction Loss', 'Branch 1', 'Branch 2', 'Final Flow']
    values = [100, 50, 30, -15, -8, -40, -35, 82]

    fig5 = go.Figure(go.Waterfall(
        x=categories,
        y=values,
        text=[f"{v:+.0f}" if v != 100 and v != 82 else f"{v:.0f}" for v in values],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}}
    ))
    fig5.update_layout(
        title="Fluid System Flow Rate Analysis",
        yaxis_title="Flow Rate (L/min)",
        showlegend=False
    )
    plots.append(('eng_flow_waterfall', fig5, {
        'appearance': {'title': {'text': 'Flow Rate Analysis'}}
    }))

    # 6. Contour Plot - Electric Field
    x = np.linspace(-10, 10, 100)
    y = np.linspace(-10, 10, 100)
    X, Y = np.meshgrid(x, y)
    # Electric potential from two charges
    V1 = 1 / np.sqrt((X - 3)**2 + Y**2 + 0.1)
    V2 = -1 / np.sqrt((X + 3)**2 + Y**2 + 0.1)
    Z = V1 + V2

    fig6 = go.Figure(data=go.Contour(
        z=Z,
        x=x,
        y=y,
        colorscale='RdBu',
        contours=dict(
            start=-2,
            end=2,
            size=0.2,
            showlabels=True,
            labelfont=dict(size=12, color='white')
        ),
        colorbar=dict(title="Electric Potential (V)")
    ))
    fig6.update_layout(
        title="Electric Field Distribution - Dipole",
        xaxis_title="X Position (cm)",
        yaxis_title="Y Position (cm)"
    )
    plots.append(('eng_electric_field', fig6, {
        'appearance': {'title': {'text': 'Electric Field'}}
    }))

    # 7. 3D Scatter - Particle Distribution
    n_particles = 200
    # Particles in a cylindrical chamber with some clustering
    theta = np.random.uniform(0, 2*np.pi, n_particles)
    r = np.random.normal(3, 1, n_particles)
    r = np.clip(r, 0, 5)  # Limit to cylinder radius
    x_particles = r * np.cos(theta)
    y_particles = r * np.sin(theta)
    z_particles = np.random.uniform(0, 10, n_particles)
    velocities = np.sqrt(x_particles**2 + y_particles**2) + np.random.normal(0, 0.5, n_particles)

    fig7 = go.Figure(data=[go.Scatter3d(
        x=x_particles,
        y=y_particles,
        z=z_particles,
        mode='markers',
        marker=dict(
            size=5,
            color=velocities,
            colorscale='Turbo',
            showscale=True,
            colorbar=dict(title="Velocity (m/s)")
        )
    )])
    fig7.update_layout(
        title="Particle Distribution in Reaction Chamber",
        scene=dict(
            xaxis_title="X (cm)",
            yaxis_title="Y (cm)",
            zaxis_title="Height (cm)"
        )
    )
    plots.append(('eng_particles_3d', fig7, {
        'appearance': {'title': {'text': 'Particle Distribution'}}
    }))

    # 8. System Performance Mesh3D
    # Create a simple 3D mesh (turbine blade)
    phi = np.linspace(0, 2*np.pi, 20)
    r_mesh = np.linspace(1, 3, 10)
    PHI, R = np.meshgrid(phi, r_mesh)

    x_mesh = R * np.cos(PHI)
    y_mesh = R * np.sin(PHI)
    z_mesh = R * 0.5 + np.sin(3*PHI) * 0.3

    # Flatten for mesh3d
    x_flat = x_mesh.flatten()
    y_flat = y_mesh.flatten()
    z_flat = z_mesh.flatten()

    # Create simple triangulation
    i = []
    j = []
    k = []
    for row in range(9):
        for col in range(19):
            idx = row * 20 + col
            next_idx = row * 20 + (col + 1) % 20
            bottom_idx = (row + 1) * 20 + col
            bottom_next = (row + 1) * 20 + (col + 1) % 20

            # Two triangles per quad
            i.extend([idx, idx])
            j.extend([next_idx, bottom_idx])
            k.extend([bottom_idx, bottom_next])

    fig8 = go.Figure(data=[go.Mesh3d(
        x=x_flat,
        y=y_flat,
        z=z_flat,
        i=i, j=j, k=k,
        colorscale='Viridis',
        intensity=z_flat,
        showscale=True,
        colorbar=dict(title="Height (m)")
    )])
    fig8.update_layout(
        title="3D Turbine Blade Geometry",
        scene=dict(
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="Z (m)"
        )
    )
    plots.append(('eng_turbine_mesh', fig8, {
        'appearance': {'title': {'text': 'Turbine Blade Mesh'}}
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} engineering analysis visualizations"

# Execute when imported or run
if __name__ == "__main__" or True:
    result = create_engineering_plots()
    print(result)