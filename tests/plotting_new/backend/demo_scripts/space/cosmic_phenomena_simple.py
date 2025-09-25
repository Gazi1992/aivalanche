"""
Cosmic Phenomena Visualizations (Simplified)
Testing version with reduced complexity
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd

# === Visualization 1: Cosmic Ray Energy Spectrum ===
# Real cosmic ray data (simplified)
energy = np.logspace(9, 21, 50)  # Energy in eV
flux = 3e24 * energy**(-2.7) * np.where(energy < 5e15, 1, (energy/5e15)**(-0.3))  # Flux with knee

# Add GZK cutoff
flux = flux * np.where(energy < 5e19, 1, np.exp(-(energy - 5e19)/1e20))

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=energy,
    y=flux * energy**2.7,  # Scale for better visualization
    mode='lines',
    line=dict(color='#FF69B4', width=3),
    name='Cosmic Ray Flux',
    hovertemplate='Energy: %{x:.2e} eV<br>Scaled Flux: %{y:.2e}<extra></extra>'
))

# Mark important features
features = {
    'Knee': 5e15,
    'Second Knee': 5e17,
    'Ankle': 5e18,
    'GZK Cutoff': 5e19
}

for name, e in features.items():
    fig1.add_vline(x=e, line_dash="dash", line_color="gray", opacity=0.5)
    fig1.add_annotation(
        x=np.log10(e),
        y=np.log10(3e24 * e**(-2.7) * e**2.7),
        text=name,
        showarrow=True,
        arrowhead=7,
        ax=0,
        ay=-30
    )

fig1.update_layout(
    title={
        'text': 'Cosmic Ray Energy Spectrum',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(
        title='Energy (eV)',
        type='log',
        showgrid=True
    ),
    yaxis=dict(
        title='E^2.7 × Flux (arbitrary units)',
        type='log',
        showgrid=True
    ),
    height=500
)

register_plot(
    fig1,
    plot_id='cosmic_ray_spectrum',
    metadata={
        'appearance': {
            'title': {'text': 'Ultra-High Energy Cosmic Rays'}
        }
    }
)

# === Visualization 2: Galaxy Rotation Curve Mystery ===
# Demonstrating dark matter evidence
r_galaxy = np.linspace(0.1, 30, 50)  # Distance from galactic center (kpc)

# Expected rotation curve (Keplerian)
v_expected = 220 * np.sqrt(1/r_galaxy) * np.where(r_galaxy < 1, r_galaxy, 1)

# Observed rotation curve (flat due to dark matter)
v_observed = 220 * np.tanh(r_galaxy/3)

# Dark matter contribution
v_dark = np.sqrt(np.maximum(0, v_observed**2 - v_expected**2))

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=r_galaxy,
    y=v_expected,
    mode='lines',
    line=dict(color='#FFA500', width=3, dash='dash'),
    name='Expected (Visible Matter)',
    hovertemplate='Distance: %{x:.1f} kpc<br>Velocity: %{y:.0f} km/s<extra></extra>'
))

fig2.add_trace(go.Scatter(
    x=r_galaxy,
    y=v_observed,
    mode='lines',
    line=dict(color='#00CED1', width=3),
    name='Observed',
    hovertemplate='Distance: %{x:.1f} kpc<br>Velocity: %{y:.0f} km/s<extra></extra>'
))

fig2.add_trace(go.Scatter(
    x=r_galaxy,
    y=v_dark,
    mode='lines',
    line=dict(color='#9400D3', width=3, dash='dot'),
    name='Dark Matter Contribution',
    fill='tozeroy',
    fillcolor='rgba(148, 0, 211, 0.1)',
    hovertemplate='Distance: %{x:.1f} kpc<br>Velocity: %{y:.0f} km/s<extra></extra>'
))

fig2.update_layout(
    title={
        'text': 'Galaxy Rotation Curves: Evidence for Dark Matter',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(
        title='Distance from Galactic Center (kpc)',
        showgrid=True
    ),
    yaxis=dict(
        title='Rotation Velocity (km/s)',
        showgrid=True
    ),
    height=500,
    showlegend=True
)

register_plot(
    fig2,
    plot_id='galaxy_rotation',
    metadata={
        'appearance': {
            'title': {'text': 'Dark Matter Mystery'}
        }
    }
)

# === Visualization 3: Space Missions Timeline ===
missions = pd.DataFrame({
    'name': ['Sputnik 1', 'Yuri Gagarin', 'Apollo 11', 'Voyager 1',
             'Hubble', 'ISS', 'Curiosity', 'JWST'],
    'launch': pd.to_datetime(['1957-10-04', '1961-04-12', '1969-07-16', '1977-09-05',
                              '1990-04-24', '1998-11-20', '2011-11-26', '2021-12-25']),
    'type': ['Satellite', 'Human', 'Human', 'Probe',
             'Telescope', 'Station', 'Rover', 'Telescope'],
    'distance': [400, 400, 384400, 23000000000,
                 550, 400, 225000000, 1500000]  # km from Earth
})

fig3 = go.Figure()

# Color by mission type
colors = {
    'Satellite': '#FFD700',
    'Human': '#FF6B6B',
    'Probe': '#4ECDC4',
    'Telescope': '#9B59B6',
    'Station': '#3498DB',
    'Rover': '#E67E22'
}

for mission_type in missions['type'].unique():
    df = missions[missions['type'] == mission_type]

    fig3.add_trace(go.Scatter(
        x=df['launch'],
        y=np.log10(df['distance'] + 1),
        mode='markers+text',
        marker=dict(
            size=15,
            color=colors[mission_type],
            line=dict(width=2, color='white')
        ),
        text=df['name'],
        textposition='top center',
        textfont=dict(size=9),
        name=mission_type
    ))

fig3.update_layout(
    title={
        'text': 'Historic Space Missions Timeline',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(
        title='Launch Date',
        showgrid=True
    ),
    yaxis=dict(
        title='Log Distance from Earth',
        showgrid=True
    ),
    height=500,
    showlegend=True
)

register_plot(
    fig3,
    plot_id='space_missions',
    metadata={
        'appearance': {
            'title': {'text': 'Journey to the Stars'}
        }
    }
)