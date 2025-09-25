"""
Stellar Universe Visualizations
Interactive visualizations of stars, constellations, and cosmic phenomena
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

# === Visualization 1: Stellar Size Comparison ===
# Data for various stars and celestial objects
stellar_objects = [
    {'name': 'Earth', 'radius': 1, 'color': '#4169E1', 'type': 'Planet'},
    {'name': 'Jupiter', 'radius': 11.2, 'color': '#DAA520', 'type': 'Planet'},
    {'name': 'Sun', 'radius': 109, 'color': '#FFD700', 'type': 'Star'},
    {'name': 'Sirius A', 'radius': 173, 'color': '#B0E0E6', 'type': 'Star'},
    {'name': 'Pollux', 'radius': 872, 'color': '#FFA500', 'type': 'Star'},
    {'name': 'Arcturus', 'radius': 2500, 'color': '#FF8C00', 'type': 'Star'},
    {'name': 'Rigel', 'radius': 7800, 'color': '#87CEEB', 'type': 'Star'},
    {'name': 'Betelgeuse', 'radius': 88700, 'color': '#FF4500', 'type': 'Star'},
    {'name': 'VY Canis Majoris', 'radius': 140000, 'color': '#8B0000', 'type': 'Star'},
]

# Create logarithmic scale for better visualization
fig1 = go.Figure()

# Add circular markers for size comparison
for obj in stellar_objects:
    # Use log scale for radius
    log_radius = np.log10(obj['radius']) if obj['radius'] > 0 else 0

    fig1.add_trace(go.Scatter(
        x=[obj['name']],
        y=[1],  # All on same y-level
        mode='markers+text',
        marker=dict(
            size=min(log_radius * 20, 150),  # Scale for visibility
            color=obj['color'],
            line=dict(width=2, color='white'),
            opacity=0.8
        ),
        text=f"{obj['name']}<br>{obj['radius']:,.0f}x Earth",
        textposition='top center',
        textfont=dict(size=10),
        name=obj['name'],
        hovertemplate=f"<b>{obj['name']}</b><br>Type: {obj['type']}<br>Radius: {obj['radius']:,.0f} Earth radii<extra></extra>"
    ))

fig1.update_layout(
    title={
        'text': 'Stellar Size Comparison (Logarithmic Scale)',
        'x': 0.5,
        'xanchor': 'center'
    },
    showlegend=False,
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=True,
        title=''
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        range=[0.5, 1.5],
        title=''
    ),
    height=400
)

register_plot(
    fig1,
    plot_id='stellar_comparison',
    metadata={
        'appearance': {
            'title': {'text': 'Stellar Size Comparison'}
        }
    }
)

# === Visualization 2: Interactive Constellation Map (D3) ===
constellation_code = """
// Constellation Map with interactive stars
const padding = 40;
const centerX = width / 2;
const centerY = height / 2;

// Clear SVG
svg.selectAll('*').remove();

// Create night sky background
svg.append('rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', '#000033');

// Add gradient for milky way effect
const defs = svg.append('defs');
const gradient = defs.append('radialGradient')
    .attr('id', 'milkyway')
    .attr('cx', '50%')
    .attr('cy', '50%')
    .attr('r', '50%');

gradient.append('stop')
    .attr('offset', '0%')
    .attr('stop-color', '#1a1a4a')
    .attr('stop-opacity', 0.3);
gradient.append('stop')
    .attr('offset', '100%')
    .attr('stop-color', '#000033')
    .attr('stop-opacity', 0);

svg.append('ellipse')
    .attr('cx', centerX)
    .attr('cy', centerY)
    .attr('rx', width * 0.8)
    .attr('ry', height * 0.3)
    .attr('fill', 'url(#milkyway)')
    .attr('transform', `rotate(20 ${centerX} ${centerY})`);

// Constellation data (simplified Orion)
const orion = {
    name: 'Orion',
    stars: [
        {name: 'Betelgeuse', x: 0.2, y: 0.25, mag: 0.5, color: '#FF4500'},
        {name: 'Bellatrix', x: 0.8, y: 0.25, mag: 1.6, color: '#B0E0E6'},
        {name: 'Alnitak', x: 0.35, y: 0.6, mag: 1.7, color: '#87CEEB'},
        {name: 'Alnilam', x: 0.5, y: 0.6, mag: 1.7, color: '#87CEEB'},
        {name: 'Mintaka', x: 0.65, y: 0.6, mag: 2.2, color: '#87CEEB'},
        {name: 'Saiph', x: 0.35, y: 0.9, mag: 2.1, color: '#87CEEB'},
        {name: 'Rigel', x: 0.65, y: 0.9, mag: 0.1, color: '#87CEEB'}
    ],
    lines: [
        [0, 1], // Shoulders
        [0, 2], [1, 4], // To belt
        [2, 3], [3, 4], // Belt
        [2, 5], [4, 6] // To feet
    ]
};

// Scale positions to SVG dimensions
const stars = orion.stars.map(star => ({
    ...star,
    x: padding + star.x * (width - 2 * padding),
    y: padding + star.y * (height - 2 * padding),
    size: (3 - star.mag) * 4 + 2
}));

// Draw constellation lines
const lineGroup = svg.append('g').attr('class', 'constellation-lines');
orion.lines.forEach(([i, j]) => {
    lineGroup.append('line')
        .attr('x1', stars[i].x)
        .attr('y1', stars[i].y)
        .attr('x2', stars[j].x)
        .attr('y2', stars[j].y)
        .attr('stroke', 'rgba(255, 255, 255, 0.3)')
        .attr('stroke-width', 1);
});

// Add random background stars
const bgStars = d3.range(300).map(() => ({
    x: Math.random() * width,
    y: Math.random() * height,
    r: Math.random() * 1.5,
    opacity: 0.3 + Math.random() * 0.5
}));

svg.selectAll('.bg-star')
    .data(bgStars)
    .enter().append('circle')
    .attr('class', 'bg-star')
    .attr('cx', d => d.x)
    .attr('cy', d => d.y)
    .attr('r', d => d.r)
    .attr('fill', 'white')
    .attr('opacity', d => d.opacity);

// Draw constellation stars
const starGroup = svg.append('g').attr('class', 'constellation-stars');
stars.forEach(star => {
    // Add glow effect
    starGroup.append('circle')
        .attr('cx', star.x)
        .attr('cy', star.y)
        .attr('r', star.size * 2)
        .attr('fill', star.color)
        .attr('opacity', 0.3);

    // Main star
    const starElement = starGroup.append('circle')
        .attr('cx', star.x)
        .attr('cy', star.y)
        .attr('r', star.size)
        .attr('fill', star.color)
        .style('cursor', 'pointer');

    // Add hover effect
    starElement.on('mouseover', function() {
        d3.select(this)
            .transition()
            .duration(200)
            .attr('r', star.size * 1.5);

        // Show star name
        svg.append('text')
            .attr('id', 'star-label')
            .attr('x', star.x)
            .attr('y', star.y - star.size - 10)
            .attr('text-anchor', 'middle')
            .attr('fill', 'white')
            .attr('font-size', '12px')
            .text(star.name);
    })
    .on('mouseout', function() {
        d3.select(this)
            .transition()
            .duration(200)
            .attr('r', star.size);

        svg.select('#star-label').remove();
    });
});

// Add constellation name
svg.append('text')
    .attr('x', centerX)
    .attr('y', height - 20)
    .attr('text-anchor', 'middle')
    .attr('fill', 'white')
    .attr('font-size', '16px')
    .attr('opacity', 0.8)
    .text('Constellation: Orion');
"""

# Register the D3 constellation map
constellation_viz = d3_custom(constellation_code)
register_d3_visualization(constellation_viz, 'constellation_map')

# === Visualization 3: Meteor Shower Radiant Points ===
# Major meteor showers and their radiant points
meteor_showers = pd.DataFrame({
    'name': ['Quadrantids', 'Lyrids', 'Eta Aquariids', 'Perseids', 'Orionids',
             'Leonids', 'Geminids', 'Ursids'],
    'peak_date': ['Jan 4', 'Apr 22', 'May 6', 'Aug 13', 'Oct 21',
                  'Nov 17', 'Dec 14', 'Dec 22'],
    'ra': [230, 271, 338, 48, 95, 153, 113, 217],  # Right ascension in degrees
    'dec': [49, 34, -1, 58, 16, 22, 33, 76],  # Declination in degrees
    'meteors_per_hour': [120, 18, 60, 100, 20, 15, 120, 10],
    'velocity_km_s': [41, 49, 66, 59, 66, 71, 35, 33],
    'parent_body': ['2003 EH1', 'C/1861 G1', '1P/Halley', '109P/Swift-Tuttle',
                    '1P/Halley', '55P/Tempel-Tuttle', '3200 Phaethon', '8P/Tuttle']
})

# Create polar projection for sky map
fig3 = go.Figure()

# Convert RA/Dec to polar coordinates
theta = meteor_showers['ra'] * np.pi / 180
r = 90 - meteor_showers['dec']  # Convert declination to polar distance

fig3.add_trace(go.Scatterpolar(
    r=r,
    theta=meteor_showers['ra'],
    mode='markers+text',
    marker=dict(
        size=meteor_showers['meteors_per_hour'] / 5,
        color=meteor_showers['velocity_km_s'],
        colorscale='Plasma',
        showscale=True,
        colorbar=dict(title='Velocity (km/s)'),
        line=dict(width=2, color='white')
    ),
    text=meteor_showers['name'],
    textposition='top center',
    hovertemplate='<b>%{text}</b><br>Peak: %{customdata[0]}<br>Rate: %{customdata[1]} meteors/hr<br>Parent: %{customdata[2]}<extra></extra>',
    customdata=np.column_stack((meteor_showers['peak_date'],
                                meteor_showers['meteors_per_hour'],
                                meteor_showers['parent_body']))
))

fig3.update_layout(
    title={
        'text': 'Major Meteor Shower Radiant Points',
        'x': 0.5,
        'xanchor': 'center'
    },
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 90],
            tickmode='array',
            tickvals=[0, 30, 60, 90],
            ticktext=['90°', '60°', '30°', '0°']
        ),
        angularaxis=dict(
            tickmode='array',
            tickvals=[0, 90, 180, 270],
            ticktext=['0h', '6h', '12h', '18h'],
            direction='clockwise',
            rotation=90
        )
    ),
    showlegend=False
)

register_plot(
    fig3,
    plot_id='meteor_showers',
    metadata={
        'appearance': {
            'title': {'text': 'Meteor Shower Radiant Map'}
        }
    }
)

# === Visualization 4: Hertzsprung-Russell Diagram ===
# Stellar evolution and classification
np.random.seed(42)

# Generate realistic stellar data
n_stars = 500
# Main sequence stars
ms_temp = np.random.uniform(3000, 30000, 300)
ms_luminosity = (ms_temp/5800) ** 4 * np.random.uniform(0.5, 2, 300)

# Red giants
rg_temp = np.random.uniform(3000, 5000, 100)
rg_luminosity = np.random.uniform(100, 10000, 100)

# White dwarfs
wd_temp = np.random.uniform(8000, 40000, 50)
wd_luminosity = np.random.uniform(0.001, 0.1, 50)

# Supergiants
sg_temp = np.random.uniform(3000, 20000, 50)
sg_luminosity = np.random.uniform(10000, 100000, 50)

# Combine all stars
temperatures = np.concatenate([ms_temp, rg_temp, wd_temp, sg_temp])
luminosities = np.concatenate([ms_luminosity, rg_luminosity, wd_luminosity, sg_luminosity])
star_types = (['Main Sequence'] * 300 + ['Red Giant'] * 100 +
              ['White Dwarf'] * 50 + ['Supergiant'] * 50)

# Create HR diagram
fig4 = go.Figure()

# Add star data
for star_type in set(star_types):
    mask = [t == star_type for t in star_types]
    temps = temperatures[mask]
    lums = luminosities[mask]

    colors = {
        'Main Sequence': '#FFD700',
        'Red Giant': '#FF4500',
        'White Dwarf': '#E0FFFF',
        'Supergiant': '#FF1493'
    }

    fig4.add_trace(go.Scatter(
        x=temps,
        y=lums,
        mode='markers',
        name=star_type,
        marker=dict(
            size=8 if star_type != 'Supergiant' else 12,
            color=colors[star_type],
            opacity=0.7,
            line=dict(width=1, color='white')
        ),
        hovertemplate='<b>%{text}</b><br>Temperature: %{x:.0f} K<br>Luminosity: %{y:.2e} L☉<extra></extra>',
        text=[star_type] * sum(mask)
    ))

# Add Sun reference point
fig4.add_trace(go.Scatter(
    x=[5800],
    y=[1],
    mode='markers+text',
    name='Sun',
    marker=dict(size=15, color='yellow', symbol='star',
                line=dict(width=2, color='orange')),
    text=['☉ Sun'],
    textposition='top center',
    textfont=dict(size=12),
    hovertemplate='<b>Our Sun</b><br>Temperature: 5,800 K<br>Luminosity: 1 L☉<extra></extra>'
))

fig4.update_layout(
    title={
        'text': 'Hertzsprung-Russell Diagram',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(
        title='Surface Temperature (K)',
        autorange='reversed',  # Hot stars on left
        type='log',
        showgrid=True
    ),
    yaxis=dict(
        title='Luminosity (Solar Units)',
        type='log',
        showgrid=True
    ),
    height=500,
    hovermode='closest'
)

register_plot(
    fig4,
    plot_id='hr_diagram',
    metadata={
        'appearance': {
            'title': {'text': 'Stellar Evolution Map'}
        }
    }
)

# === Visualization 5: Nearby Star Systems ===
# Our stellar neighborhood within 20 light-years
nearby_stars = pd.DataFrame({
    'name': ['Proxima Centauri', 'Alpha Centauri A', 'Alpha Centauri B', "Barnard's Star",
             'Wolf 359', 'Lalande 21185', 'Sirius A', 'Sirius B', 'Luyten 726-8 A',
             'Ross 154', 'Ross 248', 'Epsilon Eridani', 'Lacaille 9352', 'Ross 128',
             'EZ Aquarii A', 'Procyon A', '61 Cygni A', 'Struve 2398 A', 'Groombridge 34 A',
             'Tau Ceti'],
    'distance': [4.24, 4.36, 4.36, 5.96, 7.78, 8.29, 8.58, 8.58, 8.73,
                 9.68, 10.32, 10.52, 10.74, 10.92, 11.27, 11.40, 11.52, 11.62, 11.64, 11.89],
    'x': np.random.uniform(-15, 15, 20),
    'y': np.random.uniform(-15, 15, 20),
    'z': np.random.uniform(-10, 10, 20),
    'spectral_type': ['M5.5V', 'G2V', 'K1V', 'M4V', 'M6V', 'M2V', 'A1V', 'DA2', 'M5.5V',
                      'M3.5V', 'M5.5V', 'K2V', 'M1.5V', 'M4V', 'M5V', 'F5IV', 'K5V', 'M3V', 'M1.5V', 'G8V'],
    'luminosity': [0.00005, 1.52, 0.50, 0.0004, 0.00002, 0.006, 25.4, 0.003, 0.00006,
                   0.0004, 0.0001, 0.34, 0.01, 0.0004, 0.0003, 6.93, 0.15, 0.03, 0.006, 0.52]
})

# Adjust positions based on actual distances
angle = np.random.uniform(0, 2*np.pi, len(nearby_stars))
nearby_stars['x'] = nearby_stars['distance'] * np.cos(angle) * np.random.uniform(0.8, 1.2, len(nearby_stars))
nearby_stars['y'] = nearby_stars['distance'] * np.sin(angle) * np.random.uniform(0.8, 1.2, len(nearby_stars))
nearby_stars['z'] = np.random.uniform(-5, 5, len(nearby_stars))

# Create 3D scatter plot
fig5 = go.Figure()

# Add star systems
fig5.add_trace(go.Scatter3d(
    x=nearby_stars['x'],
    y=nearby_stars['y'],
    z=nearby_stars['z'],
    mode='markers+text',
    marker=dict(
        size=np.maximum(5, np.log10(nearby_stars['luminosity'] + 1) * 5 + 8),
        color=nearby_stars['distance'],
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title='Distance (ly)'),
        line=dict(width=1, color='white'),
        opacity=0.8
    ),
    text=nearby_stars['name'],
    textposition='top center',
    textfont=dict(size=8),
    hovertemplate='<b>%{text}</b><br>Distance: %{customdata[0]:.2f} ly<br>Type: %{customdata[1]}<br>Luminosity: %{customdata[2]:.5f} L☉<extra></extra>',
    customdata=np.column_stack((nearby_stars['distance'],
                                nearby_stars['spectral_type'],
                                nearby_stars['luminosity']))
))

# Add Sun at origin
fig5.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[0],
    mode='markers+text',
    marker=dict(size=20, color='yellow', symbol='diamond',
                line=dict(width=2, color='orange')),
    text=['☉ Sun'],
    textposition='top center',
    name='Sun',
    hovertemplate='<b>Our Solar System</b><extra></extra>'
))

# Add distance spheres
for dist in [5, 10, 15, 20]:
    theta = np.linspace(0, 2*np.pi, 30)
    phi = np.linspace(0, np.pi, 20)
    x_sphere = dist * np.outer(np.cos(theta), np.sin(phi))
    y_sphere = dist * np.outer(np.sin(theta), np.sin(phi))
    z_sphere = dist * np.outer(np.ones(len(theta)), np.cos(phi))

    fig5.add_trace(go.Surface(
        x=x_sphere, y=y_sphere, z=z_sphere,
        opacity=0.1,
        colorscale=[[0, 'rgba(100,100,100,0)'], [1, 'rgba(100,100,100,0)']],
        showscale=False,
        hoverinfo='skip',
        name=f'{dist} ly'
    ))

fig5.update_layout(
    title={
        'text': 'Nearby Star Systems (within 20 light-years)',
        'x': 0.5,
        'xanchor': 'center'
    },
    scene=dict(
        xaxis_title='X (light-years)',
        yaxis_title='Y (light-years)',
        zaxis_title='Z (light-years)',
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
    ),
    showlegend=False,
    height=600
)

register_plot(
    fig5,
    plot_id='nearby_stars',
    metadata={
        'appearance': {
            'title': {'text': 'Our Stellar Neighborhood'}
        }
    }
)

# === Visualization 6: Gravitational Wave Events Timeline ===
# LIGO/Virgo detected events (simplified data)
gw_events = pd.DataFrame({
    'name': ['GW150914', 'GW151226', 'GW170104', 'GW170814', 'GW170817',
             'GW190412', 'GW190521', 'GW200115', 'GW200225', 'GW230529'],
    'date': pd.to_datetime(['2015-09-14', '2015-12-26', '2017-01-04', '2017-08-14', '2017-08-17',
                           '2019-04-12', '2019-05-21', '2020-01-15', '2020-02-25', '2023-05-29']),
    'type': ['BBH', 'BBH', 'BBH', 'BBH', 'BNS',
             'BBH', 'BBH', 'NSBH', 'BBH', 'NSBH'],
    'mass1': [35.6, 14.2, 31.2, 30.5, 1.46,
              30.1, 85, 23, 36, 2.8],
    'mass2': [30.6, 7.5, 19.4, 25.3, 1.27,
              8.3, 66, 1.5, 29, 1.3],
    'distance': [410, 440, 880, 540, 40,
                 720, 5300, 300, 550, 200],  # Mpc
    'description': ['First detection!', 'Boxing Day merger', 'New year discovery', 'Triple detector', 'Neutron star merger with kilonova',
                    'Asymmetric masses', 'Massive black holes', 'Neutron star-black hole', 'Confident detection', 'Recent NSBH merger']
})

# Calculate total mass and event intensity
gw_events['total_mass'] = gw_events['mass1'] + gw_events['mass2']
gw_events['year'] = gw_events['date'].dt.year

# Create timeline
fig6 = go.Figure()

# Color mapping for event types
colors = {'BBH': '#FF6B6B', 'BNS': '#4ECDC4', 'NSBH': '#45B7D1'}
type_names = {'BBH': 'Black Hole-Black Hole', 'BNS': 'Binary Neutron Star', 'NSBH': 'NS-Black Hole'}

for event_type in gw_events['type'].unique():
    events = gw_events[gw_events['type'] == event_type]

    fig6.add_trace(go.Scatter(
        x=events['date'],
        y=events['distance'],
        mode='markers+text',
        name=type_names[event_type],
        marker=dict(
            size=events['total_mass'] * 0.5,
            color=colors[event_type],
            line=dict(width=2, color='white'),
            opacity=0.8
        ),
        text=events['name'],
        textposition='top center',
        textfont=dict(size=10),
        hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Distance: %{y:.0f} Mpc<br>Masses: %{customdata[0]:.1f} + %{customdata[1]:.1f} M☉<br>%{customdata[2]}<extra></extra>',
        customdata=np.column_stack((events['mass1'], events['mass2'], events['description']))
    ))

# Add milestone annotations
fig6.add_annotation(
    x=pd.Timestamp('2015-09-14'),
    y=410,
    text="First Detection<br>GW150914",
    showarrow=True,
    arrowhead=7,
    ax=0,
    ay=-40,
    font=dict(size=10)
)

fig6.add_annotation(
    x=pd.Timestamp('2017-08-17'),
    y=40,
    text="First NS Merger<br>with EM counterpart",
    showarrow=True,
    arrowhead=7,
    ax=0,
    ay=-40,
    font=dict(size=10)
)

fig6.update_layout(
    title={
        'text': 'Gravitational Wave Detections Timeline',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(
        title='Detection Date',
        showgrid=True,
        gridwidth=1,
        gridcolor='LightGray'
    ),
    yaxis=dict(
        title='Distance (Megaparsecs)',
        type='log',
        showgrid=True,
        gridwidth=1,
        gridcolor='LightGray'
    ),
    height=500,
    hovermode='closest'
)

register_plot(
    fig6,
    plot_id='gw_events',
    metadata={
        'appearance': {
            'title': {'text': 'Gravitational Wave Astronomy Era'}
        }
    }
)