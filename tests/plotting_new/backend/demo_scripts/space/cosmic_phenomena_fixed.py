"""
Cosmic Phenomena Visualizations
Black holes, cosmic rays, space exploration, and astrophysics
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

# === Visualization 1: Black Hole Schwarzschild Radius ===
# Comparing black hole sizes
black_holes = pd.DataFrame({
    'name': ['Stellar Black Hole (10 M☉)', 'IMBH (1000 M☉)', 'Sgr A* (4M M☉)',
             'M87* (6.5B M☉)', 'TON 618 (66B M☉)'],
    'mass_solar': [10, 1000, 4e6, 6.5e9, 66e9],
    'type': ['Stellar', 'Intermediate', 'Supermassive', 'Supermassive', 'Ultramassive']
})

# Calculate Schwarzschild radius in AU
black_holes['radius_km'] = 2.95 * black_holes['mass_solar']  # in km
black_holes['radius_au'] = black_holes['radius_km'] / 149597870.7  # convert to AU

fig1 = go.Figure()

colors = {'Stellar': '#FFD700', 'Intermediate': '#FF6347',
          'Supermassive': '#9370DB', 'Ultramassive': '#FF1493'}

for bh_type in black_holes['type'].unique():
    df = black_holes[black_holes['type'] == bh_type]

    fig1.add_trace(go.Bar(
        x=df['name'],
        y=df['radius_au'],
        name=bh_type,
        marker_color=colors[bh_type],
        hovertemplate='<b>%{x}</b><br>Event Horizon: %{y:.2e} AU<br>Mass: %{customdata:.2e} M☉<extra></extra>',
        customdata=df['mass_solar']
    ))

# Add reference lines for scale
references = [
    {'name': 'Earth Orbit', 'value': 1, 'color': 'cyan'},
    {'name': 'Neptune Orbit', 'value': 30, 'color': 'blue'},
    {'name': 'Voyager 1 Distance', 'value': 160, 'color': 'green'}
]

for ref in references:
    fig1.add_hline(y=ref['value'], line_dash="dash", line_color=ref['color'],
                   opacity=0.5, annotation_text=ref['name'])

fig1.update_layout(
    title={
        'text': 'Black Hole Event Horizons Comparison',
        'x': 0.5,
        'xanchor': 'center'
    },
    yaxis=dict(
        title='Event Horizon Radius (AU)',
        type='log',
        showgrid=True
    ),
    xaxis=dict(title=''),
    height=500,
    showlegend=True
)

register_plot(
    fig1,
    plot_id='black_hole_sizes',
    metadata={
        'appearance': {
            'title': {'text': 'Black Hole Scale Comparison'}
        }
    }
)

# === Visualization 2: Pulsar Timing Array ===
# Millisecond pulsars used for gravitational wave detection
pulsars = pd.DataFrame({
    'name': ['J0437-4715', 'J1713+0747', 'J1909-3744', 'J0613-0200',
             'J2145-0750', 'J1600-3053', 'J1640+2224', 'J1744-1134'],
    'period_ms': [5.757, 4.570, 2.947, 3.062, 16.052, 3.598, 3.163, 4.075],
    'distance_pc': [156, 1176, 1305, 500, 613, 1600, 1170, 357],
    'timing_precision_ns': [20, 30, 15, 40, 50, 25, 35, 45],
    'discovered': [1993, 2001, 2003, 1999, 1999, 2007, 1995, 2005]
})

fig2 = go.Figure()

# Create bubble chart
fig2.add_trace(go.Scatter(
    x=pulsars['period_ms'],
    y=pulsars['distance_pc'],
    mode='markers+text',
    marker=dict(
        size=100/pulsars['timing_precision_ns'],  # Better precision = larger marker
        color=pulsars['discovered'],
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title='Year Discovered'),
        line=dict(width=2, color='white')
    ),
    text=pulsars['name'],
    textposition='top center',
    hovertemplate='<b>%{text}</b><br>Period: %{x:.3f} ms<br>Distance: %{y:.0f} pc<br>Timing Precision: %{customdata:.0f} ns<extra></extra>',
    customdata=pulsars['timing_precision_ns']
))

fig2.update_layout(
    title={
        'text': 'Millisecond Pulsar Timing Array',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(
        title='Rotation Period (milliseconds)',
        showgrid=True
    ),
    yaxis=dict(
        title='Distance (parsecs)',
        showgrid=True
    ),
    height=500
)

register_plot(
    fig2,
    plot_id='pulsar_array',
    metadata={
        'appearance': {
            'title': {'text': 'Pulsar Timing Array'}
        }
    }
)

# === Visualization 3: Cosmic Ray Energy Spectrum ===
energy = np.logspace(9, 21, 50)
flux = 3e24 * energy**(-2.7) * np.where(energy < 5e15, 1, (energy/5e15)**(-0.3))
flux = flux * np.where(energy < 5e19, 1, np.exp(-(energy - 5e19)/1e20))

fig3 = go.Figure()

fig3.add_trace(go.Scatter(
    x=energy,
    y=flux * energy**2.7,
    mode='lines',
    line=dict(color='#FF69B4', width=3),
    name='Cosmic Ray Flux',
    hovertemplate='Energy: %{x:.2e} eV<br>Scaled Flux: %{y:.2e}<extra></extra>'
))

features = {'Knee': 5e15, 'Second Knee': 5e17, 'Ankle': 5e18, 'GZK Cutoff': 5e19}

for name, e in features.items():
    fig3.add_vline(x=e, line_dash="dash", line_color="gray", opacity=0.5)
    fig3.add_annotation(
        x=np.log10(e),
        y=np.log10(3e24 * e**(-2.7) * e**2.7),
        text=name,
        showarrow=True,
        arrowhead=7,
        ax=0,
        ay=-30
    )

fig3.update_layout(
    title={
        'text': 'Cosmic Ray Energy Spectrum',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(title='Energy (eV)', type='log', showgrid=True),
    yaxis=dict(title='E^2.7 × Flux', type='log', showgrid=True),
    height=500
)

register_plot(
    fig3,
    plot_id='cosmic_rays',
    metadata={
        'appearance': {
            'title': {'text': 'Ultra-High Energy Cosmic Rays'}
        }
    }
)

# === Visualization 4: Space Exploration Milestones ===
missions = pd.DataFrame({
    'name': ['Sputnik', 'Gagarin', 'Apollo 11', 'Voyager 1', 'Voyager 2',
             'Hubble', 'ISS', 'Spirit', 'Cassini', 'Kepler',
             'Curiosity', 'New Horizons', 'Parker Solar', 'JWST', 'Artemis I'],
    'year': [1957, 1961, 1969, 1977, 1977,
             1990, 1998, 2003, 1997, 2009,
             2011, 2006, 2018, 2021, 2022],
    'achievement': ['First satellite', 'First human in space', 'Moon landing',
                   'Interstellar', 'Grand tour', 'Deep space telescope',
                   'Permanent station', 'Mars rover', 'Saturn orbiter',
                   'Exoplanet hunter', 'Active Mars rover', 'Pluto flyby',
                   'Touch the Sun', 'Deep universe', 'Return to Moon'],
    'category': ['Satellite', 'Human', 'Human', 'Probe', 'Probe',
                 'Telescope', 'Station', 'Rover', 'Probe', 'Telescope',
                 'Rover', 'Probe', 'Probe', 'Telescope', 'Human'],
    'impact': [10, 10, 10, 9, 9, 10, 9, 8, 8, 9, 8, 8, 7, 10, 7]
})

fig4 = go.Figure()

colors = {
    'Satellite': '#FFD700', 'Human': '#FF6B6B', 'Probe': '#4ECDC4',
    'Telescope': '#9B59B6', 'Station': '#3498DB', 'Rover': '#E67E22'
}

for cat in missions['category'].unique():
    df = missions[missions['category'] == cat]

    fig4.add_trace(go.Scatter(
        x=df['year'],
        y=df['impact'],
        mode='markers+text',
        marker=dict(
            size=15,
            color=colors[cat],
            line=dict(width=2, color='white')
        ),
        text=df['name'],
        textposition='top center',
        name=cat,
        hovertemplate='<b>%{text}</b><br>Year: %{x}<br>%{customdata}<extra></extra>',
        customdata=df['achievement']
    ))

fig4.update_layout(
    title={
        'text': 'Space Exploration Milestones',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(title='Year', showgrid=True),
    yaxis=dict(title='Historical Impact', range=[6, 11], showgrid=True),
    height=500,
    showlegend=True
)

register_plot(
    fig4,
    plot_id='space_milestones',
    metadata={
        'appearance': {
            'title': {'text': 'Journey to the Stars'}
        }
    }
)

# === Visualization 5: Dark Matter Evidence ===
r_galaxy = np.linspace(0.1, 30, 50)
v_expected = 220 * np.sqrt(1/r_galaxy) * np.where(r_galaxy < 1, r_galaxy, 1)
v_observed = 220 * np.tanh(r_galaxy/3)
v_dark = np.sqrt(np.maximum(0, v_observed**2 - v_expected**2))

fig5 = go.Figure()

fig5.add_trace(go.Scatter(
    x=r_galaxy,
    y=v_expected,
    mode='lines',
    line=dict(color='#FFA500', width=3, dash='dash'),
    name='Expected (Visible)',
    hovertemplate='Distance: %{x:.1f} kpc<br>Velocity: %{y:.0f} km/s<extra></extra>'
))

fig5.add_trace(go.Scatter(
    x=r_galaxy,
    y=v_observed,
    mode='lines',
    line=dict(color='#00CED1', width=3),
    name='Observed',
    hovertemplate='Distance: %{x:.1f} kpc<br>Velocity: %{y:.0f} km/s<extra></extra>'
))

fig5.add_trace(go.Scatter(
    x=r_galaxy,
    y=v_dark,
    mode='lines',
    line=dict(color='#9400D3', width=3, dash='dot'),
    name='Dark Matter',
    fill='tozeroy',
    fillcolor='rgba(148, 0, 211, 0.1)',
    hovertemplate='Distance: %{x:.1f} kpc<br>Velocity: %{y:.0f} km/s<extra></extra>'
))

fig5.update_layout(
    title={
        'text': 'Galaxy Rotation: Dark Matter Evidence',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(title='Distance from Center (kpc)', showgrid=True),
    yaxis=dict(title='Rotation Velocity (km/s)', showgrid=True),
    height=500,
    showlegend=True
)

register_plot(
    fig5,
    plot_id='dark_matter',
    metadata={
        'appearance': {
            'title': {'text': 'Dark Matter Mystery'}
        }
    }
)