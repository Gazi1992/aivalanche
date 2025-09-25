"""
Cosmic Phenomena Visualizations
Black holes, pulsars, cosmic rays, and deep space exploration
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

# === Visualization 1: Black Hole Accretion Disk (D3 Animation) ===
black_hole_animation = '''
// Black hole with accretion disk animation
const centerX = width / 2;
const centerY = height / 2;
const maxRadius = Math.min(width, height) / 2 - 50;

// Clear and setup
svg.selectAll('*').remove();

// Deep space background
const bgGradient = svg.append('defs').append('radialGradient')
    .attr('id', 'space-gradient');
bgGradient.append('stop')
    .attr('offset', '0%')
    .attr('stop-color', '#000033')
    .attr('stop-opacity', 1);
bgGradient.append('stop')
    .attr('offset', '100%')
    .attr('stop-color', '#000000')
    .attr('stop-opacity', 1);

svg.append('rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', 'url(#space-gradient)');

// Add title
svg.append('text')
    .attr('x', width / 2)
    .attr('y', 30)
    .attr('text-anchor', 'middle')
    .attr('font-size', '18px')
    .attr('font-weight', 'bold')
    .attr('fill', '#FFFFFF')
    .text('Supermassive Black Hole');

svg.append('text')
    .attr('x', width / 2)
    .attr('y', 55)
    .attr('text-anchor', 'middle')
    .attr('font-size', '14px')
    .attr('fill', '#CCCCCC')
    .text('Accretion disk and relativistic jets');

// Create accretion disk layers (from outer to inner)
const diskGroup = svg.append('g')
    .attr('transform', `translate(${centerX}, ${centerY})`);

// Disk colors from cool (outer) to hot (inner)
const diskColors = [
    {r: 120, color: '#FF0000', opacity: 0.3},  // Outer - red
    {r: 100, color: '#FF4500', opacity: 0.4},
    {r: 80, color: '#FF8C00', opacity: 0.5},   // Orange
    {r: 60, color: '#FFD700', opacity: 0.6},   // Yellow
    {r: 40, color: '#FFFF00', opacity: 0.7},   // Bright yellow
    {r: 25, color: '#FFFFFF', opacity: 0.8}    // Inner - white hot
];

// Create rotating disk rings
diskColors.forEach((ring, i) => {
    const ellipse = diskGroup.append('ellipse')
        .attr('cx', 0)
        .attr('cy', 0)
        .attr('rx', ring.r)
        .attr('ry', ring.r * 0.3)  // Flatten for disk appearance
        .attr('fill', 'none')
        .attr('stroke', ring.color)
        .attr('stroke-width', 15)
        .attr('opacity', ring.opacity)
        .attr('class', `disk-ring-${i}`);
});

// Event horizon (black hole shadow)
const eventHorizon = diskGroup.append('circle')
    .attr('cx', 0)
    .attr('cy', 0)
    .attr('r', 20)
    .attr('fill', '#000000');

// Gravitational lensing effect (Einstein ring)
const lensingRing = diskGroup.append('circle')
    .attr('cx', 0)
    .attr('cy', 0)
    .attr('r', 22)
    .attr('fill', 'none')
    .attr('stroke', '#4169E1')
    .attr('stroke-width', 2)
    .attr('opacity', 0.8);

// Relativistic jets
const jetGroup = svg.append('g')
    .attr('transform', `translate(${centerX}, ${centerY})`);

// Upper jet
const upperJet = jetGroup.append('path')
    .attr('d', `M -5,0 L -15,-150 L 0,-180 L 15,-150 L 5,0 Z`)
    .attr('fill', 'url(#jet-gradient-up)')
    .attr('opacity', 0.7);

// Lower jet
const lowerJet = jetGroup.append('path')
    .attr('d', `M -5,0 L -15,150 L 0,180 L 15,150 L 5,0 Z`)
    .attr('fill', 'url(#jet-gradient-down)')
    .attr('opacity', 0.7);

// Jet gradients
const jetGradientUp = svg.select('defs').append('linearGradient')
    .attr('id', 'jet-gradient-up')
    .attr('x1', '0%').attr('y1', '100%')
    .attr('x2', '0%').attr('y2', '0%');
jetGradientUp.append('stop')
    .attr('offset', '0%')
    .attr('stop-color', '#00FFFF')
    .attr('stop-opacity', 0.9);
jetGradientUp.append('stop')
    .attr('offset', '100%')
    .attr('stop-color', '#0080FF')
    .attr('stop-opacity', 0.1);

const jetGradientDown = svg.select('defs').append('linearGradient')
    .attr('id', 'jet-gradient-down')
    .attr('x1', '0%').attr('y1', '0%')
    .attr('x2', '0%').attr('y2', '100%');
jetGradientDown.append('stop')
    .attr('offset', '0%')
    .attr('stop-color', '#00FFFF')
    .attr('stop-opacity', 0.9);
jetGradientDown.append('stop')
    .attr('offset', '100%')
    .attr('stop-color', '#0080FF')
    .attr('stop-opacity', 0.1);

// Add legend
svg.append('text')
    .attr('x', 20)
    .attr('y', height - 60)
    .attr('font-size', '12px')
    .attr('fill', '#FFFFFF')
    .text('• Black circle: Event horizon');
svg.append('text')
    .attr('x', 20)
    .attr('y', height - 40)
    .attr('font-size', '12px')
    .attr('fill', '#FFD700')
    .text('• Yellow-Red rings: Accretion disk');
svg.append('text')
    .attr('x', 20)
    .attr('y', height - 20)
    .attr('font-size', '12px')
    .attr('fill', '#00FFFF')
    .text('• Cyan beams: Relativistic jets');

// Particle effects for accretion
const particlesGroup = diskGroup.append('g');
const particles = [];
for (let i = 0; i < 20; i++) {
    const angle = Math.random() * Math.PI * 2;
    const radius = 30 + Math.random() * 90;
    particles.push({
        x: radius * Math.cos(angle),
        y: radius * Math.sin(angle) * 0.3,
        r: radius,
        angle: angle,
        speed: 1 / Math.sqrt(radius) * 5  // Orbital velocity
    });
}

particles.forEach(p => {
    particlesGroup.append('circle')
        .attr('cx', p.x)
        .attr('cy', p.y)
        .attr('r', 2)
        .attr('fill', '#FFFF00')
        .attr('opacity', 0.8)
        .attr('class', 'particle');
});

// Animation
let rotation = 0;
let jetPulse = 0;
let isPaused = false;

const animation = {
    play: () => {
        function animate() {
            rotation += 0.5;
            jetPulse += 0.1;

            // Rotate disk
            diskGroup.attr('transform', `translate(${centerX}, ${centerY}) rotate(${rotation})`);

            // Pulse jets
            const jetOpacity = 0.7 + 0.3 * Math.sin(jetPulse);
            upperJet.attr('opacity', jetOpacity);
            lowerJet.attr('opacity', jetOpacity);

            // Pulse event horizon edge (gravitational lensing)
            const ringOpacity = 0.5 + 0.3 * Math.sin(jetPulse * 2);
            lensingRing.attr('opacity', ringOpacity);

            // Update particles (orbital motion)
            particles.forEach((p, i) => {
                p.angle += p.speed * 0.02;
                p.r -= 0.1;  // Slowly spiral inward
                if (p.r < 20) {
                    // Reset particle when it reaches event horizon
                    p.r = 30 + Math.random() * 90;
                    p.angle = Math.random() * Math.PI * 2;
                }
                p.x = p.r * Math.cos(p.angle);
                p.y = p.r * Math.sin(p.angle) * 0.3;
            });

            particlesGroup.selectAll('.particle')
                .data(particles)
                .attr('cx', d => d.x)
                .attr('cy', d => d.y)
                .attr('opacity', d => Math.max(0.1, (d.r - 20) / 100));

            if (!isPaused) {
                requestAnimationFrame(animate);
            }
        }
        isPaused = false;
        animate();
    },
    pause: () => { isPaused = true; },
    stop: () => {
        isPaused = true;
        rotation = 0;
        jetPulse = 0;
        diskGroup.attr('transform', `translate(${centerX}, ${centerY})`);
    }
};

animation.play();
return animation;
'''

# Register the black hole animation
black_hole_viz = d3_animation(black_hole_animation, data=None, auto_play=True)
register_d3_visualization(black_hole_viz, 'black_hole_accretion')

# === Visualization 2: Pulsar Timing Array (D3 Animation) ===
pulsar_animation = '''
// Pulsar lighthouse effect animation
const centerX = width / 2;
const centerY = height / 2;
const maxRadius = Math.min(width, height) / 2 - 40;

// Clear and setup
svg.selectAll('*').remove();

// Dark space background
svg.append('rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', '#000011');

// Add stars
const stars = d3.range(200).map(() => ({
    x: Math.random() * width,
    y: Math.random() * height,
    r: Math.random() * 2,
    twinkle: Math.random() * 2000 + 1000
}));

svg.selectAll('.star')
    .data(stars)
    .enter().append('circle')
    .attr('class', 'star')
    .attr('cx', d => d.x)
    .attr('cy', d => d.y)
    .attr('r', d => d.r)
    .attr('fill', 'white')
    .attr('opacity', 0.8);

// Create gradient for pulsar
const gradient = svg.append('defs')
    .append('radialGradient')
    .attr('id', 'pulsar-gradient');

gradient.append('stop')
    .attr('offset', '0%')
    .attr('stop-color', '#FFFFFF')
    .attr('stop-opacity', 1);
gradient.append('stop')
    .attr('offset', '30%')
    .attr('stop-color', '#87CEEB')
    .attr('stop-opacity', 0.8);
gradient.append('stop')
    .attr('offset', '100%')
    .attr('stop-color', '#000033')
    .attr('stop-opacity', 0);

// Pulsar body
const pulsar = svg.append('circle')
    .attr('cx', centerX)
    .attr('cy', centerY)
    .attr('r', 15)
    .attr('fill', 'url(#pulsar-gradient)');

// Create rotating beams
const beamGroup = svg.append('g')
    .attr('transform', `translate(${centerX}, ${centerY})`);

// Beam paths
const beamWidth = 30;
const beamData = [
    {angle: 0, color: '#00FFFF', opacity: 0.7},
    {angle: 180, color: '#00FFFF', opacity: 0.7}
];

beamData.forEach(beam => {
    const beamPath = beamGroup.append('path')
        .attr('d', `M 0,0 L ${maxRadius * Math.cos((beam.angle - beamWidth/2) * Math.PI/180)},${maxRadius * Math.sin((beam.angle - beamWidth/2) * Math.PI/180)} A ${maxRadius},${maxRadius} 0 0,1 ${maxRadius * Math.cos((beam.angle + beamWidth/2) * Math.PI/180)},${maxRadius * Math.sin((beam.angle + beamWidth/2) * Math.PI/180)} Z`)
        .attr('fill', beam.color)
        .attr('opacity', beam.opacity);
});

// Add explanatory text
svg.append('text')
    .attr('x', width / 2)
    .attr('y', 30)
    .attr('text-anchor', 'middle')
    .attr('font-size', '18px')
    .attr('font-weight', 'bold')
    .attr('fill', '#FFFFFF')
    .text('Pulsar: Cosmic Lighthouse');

svg.append('text')
    .attr('x', width / 2)
    .attr('y', 55)
    .attr('text-anchor', 'middle')
    .attr('font-size', '14px')
    .attr('fill', '#CCCCCC')
    .text('Rotating neutron star emitting radio beams');

// Add legend
const legendY = height - 60;
svg.append('text')
    .attr('x', 20)
    .attr('y', legendY)
    .attr('font-size', '12px')
    .attr('fill', '#00FFFF')
    .text('• Cyan beams: Radio emission');

svg.append('text')
    .attr('x', 20)
    .attr('y', legendY + 20)
    .attr('font-size', '12px')
    .attr('fill', '#00FFFF')
    .text('• Expanding circles: Radio waves');

svg.append('text')
    .attr('x', 20)
    .attr('y', legendY + 40)
    .attr('font-size', '12px')
    .attr('fill', '#FFFFFF')
    .text('• Rotation period: ~33ms (typical millisecond pulsar)');

// Radio wave circles
const waves = svg.append('g')
    .attr('transform', `translate(${centerX}, ${centerY})`);

function createWave() {
    waves.append('circle')
        .attr('r', 15)
        .attr('fill', 'none')
        .attr('stroke', '#00FFFF')
        .attr('stroke-width', 2)
        .attr('opacity', 1)
        .transition()
        .duration(2000)
        .attr('r', maxRadius)
        .attr('opacity', 0)
        .remove();
}

// Animation
let rotation = 0;
let lastWave = Date.now();

const animation = {
    play: () => {
        function animate() {
            rotation += 2;
            beamGroup.attr('transform', `translate(${centerX}, ${centerY}) rotate(${rotation})`);

            // Pulse the pulsar
            const scale = 1 + 0.2 * Math.sin(rotation * Math.PI / 30);
            pulsar.attr('r', 15 * scale);

            // Create radio waves periodically
            const now = Date.now();
            if (now - lastWave > 500) {
                createWave();
                lastWave = now;
            }

            if (!isPaused) {
                requestAnimationFrame(animate);
            }
        }
        isPaused = false;
        animate();
    },
    pause: () => { isPaused = true; },
    stop: () => {
        isPaused = true;
        rotation = 0;
        beamGroup.attr('transform', `translate(${centerX}, ${centerY}) rotate(0)`);
    }
};

let isPaused = false;
animation.play();
return animation;
'''

# Register the pulsar animation
pulsar_viz = d3_animation(pulsar_animation, data=None, auto_play=True)
register_d3_visualization(pulsar_viz, 'pulsar_lighthouse')

# === Visualization 3: Cosmic Ray Energy Spectrum ===
# Real cosmic ray data (simplified)
energy = np.logspace(9, 21, 50)  # Energy in eV - reduced points
flux = 3e24 * energy**(-2.7) * np.where(energy < 5e15, 1, (energy/5e15)**(-0.3))  # Flux with knee

# Add GZK cutoff
flux = flux * np.where(energy < 5e19, 1, np.exp(-(energy - 5e19)/1e20))

fig3 = go.Figure()

fig3.add_trace(go.Scatter(
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
    xaxis=dict(
        title='Energy (eV)',
        type='log',
        showgrid=True,
        gridcolor='rgba(255,255,255,0.1)'
    ),
    yaxis=dict(
        title='E^2.7 × Flux (arbitrary units)',
        type='log',
        showgrid=True,
        gridcolor='rgba(255,255,255,0.1)'
    )
)

register_plot(
    fig3,
    plot_id='cosmic_ray_spectrum',
    metadata={
        'appearance': {
            'title': {'text': 'Ultra-High Energy Cosmic Rays'}
        }
    }
)

# === Visualization 4: Space Missions Timeline ===
"""
missions = pd.DataFrame({
    'name': ['Sputnik 1', 'Yuri Gagarin', 'Apollo 11', 'Voyager 1', 'Voyager 2',
             'Hubble', 'ISS First Module', 'Spirit/Opportunity', 'Cassini-Huygens',
             'Kepler', 'Curiosity', 'New Horizons', 'Parker Solar Probe',
             'JWST', 'Artemis I', 'Europa Clipper'],
    'launch': pd.to_datetime(['1957-10-04', '1961-04-12', '1969-07-16', '1977-09-05', '1977-08-20',
                              '1990-04-24', '1998-11-20', '2003-06-10', '1997-10-15',
                              '2009-03-07', '2011-11-26', '2006-01-19', '2018-08-12',
                              '2021-12-25', '2022-11-16', '2024-10-14']),
    'type': ['Satellite', 'Human', 'Human', 'Probe', 'Probe',
             'Telescope', 'Station', 'Rover', 'Probe',
             'Telescope', 'Rover', 'Probe', 'Probe',
             'Telescope', 'Human', 'Probe'],
    'destination': ['Earth Orbit', 'Earth Orbit', 'Moon', 'Outer Solar System', 'Outer Solar System',
                   'Earth Orbit', 'Earth Orbit', 'Mars', 'Saturn',
                   'Earth Orbit', 'Mars', 'Pluto', 'Sun',
                   'L2 Point', 'Moon', 'Jupiter'],
    'achievement': ['First artificial satellite', 'First human in space', 'First Moon landing',
                   'Interstellar space', 'Grand tour of planets',
                   'Deep space observation', 'Permanent presence', 'Mars exploration',
                   'Saturn system study', 'Exoplanet discoveries', 'Active Mars rover',
                   'Pluto flyby', 'Touch the Sun', 'Deep universe observation',
                   'Return to Moon', 'Europa exploration'],
    'distance': [400, 400, 384400, 23000000000, 19000000000,
                 550, 400, 225000000, 1500000000,
                 550, 225000000, 7500000000, 7000000,
                 1500000, 384400, 778000000]  # km from Earth
})

fig4 = go.Figure()

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

    fig4.add_trace(go.Scatter(
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
        name=mission_type,
        hovertemplate='<b>%{text}</b><br>Launch: %{x}<br>Destination: %{customdata[0]}<br>Achievement: %{customdata[1]}<extra></extra>',
        customdata=np.column_stack((df['destination'], df['achievement']))
    ))

# Add era annotations
eras = [
    {'name': 'Space Race', 'start': '1957-01-01', 'end': '1975-12-31', 'y': 0.5},
    {'name': 'Shuttle Era', 'start': '1981-01-01', 'end': '2011-12-31', 'y': 0.3},
    {'name': 'Commercial Space', 'start': '2012-01-01', 'end': '2024-12-31', 'y': 0.1}
]

for era in eras:
    fig4.add_shape(
        type="rect",
        x0=era['start'], x1=era['end'],
        y0=0, y1=10,
        fillcolor="gray",
        opacity=0.1,
        layer="below",
        line_width=0
    )

    fig4.add_annotation(
        x=pd.Timestamp(era['start']) + (pd.Timestamp(era['end']) - pd.Timestamp(era['start'])) / 2,
        y=era['y'],
        text=era['name'],
        showarrow=False,
        font=dict(size=12, color='gray')
    )

fig4.update_layout(
    title={
        'text': 'Historic Space Missions Timeline',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(
        title='Launch Date',
        showgrid=True,
        gridcolor='rgba(128,128,128,0.2)'
    ),
    yaxis=dict(
        title='Log Distance from Earth',
        ticktext=['Earth Orbit', 'Moon', 'Inner Planets', 'Outer Planets', 'Interstellar'],
        tickvals=[2.6, 5.5, 8, 9.5, 10.5],
        showgrid=True,
        gridcolor='rgba(128,128,128,0.2)'
    ),
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

register_plot(
    fig4,
    plot_id='space_missions',
    metadata={
        'appearance': {
            'title': {'text': 'Journey to the Stars'}
        }
    }
)
"""

# === Visualization 5: Galaxy Rotation Curve Mystery ===
# Demonstrating dark matter evidence
r_galaxy = np.linspace(0.1, 30, 50)  # Distance from galactic center (kpc) - reduced points

# Expected rotation curve (Keplerian)
v_expected = 220 * np.sqrt(1/r_galaxy) * np.where(r_galaxy < 1, r_galaxy, 1)

# Observed rotation curve (flat due to dark matter)
v_observed = 220 * np.tanh(r_galaxy/3)

# Dark matter contribution
v_dark = np.sqrt(np.maximum(0, v_observed**2 - v_expected**2))

fig5 = go.Figure()

fig5.add_trace(go.Scatter(
    x=r_galaxy,
    y=v_expected,
    mode='lines',
    line=dict(color='#FFA500', width=3, dash='dash'),
    name='Expected (Visible Matter)',
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
    name='Dark Matter Contribution',
    fill='tozeroy',
    fillcolor='rgba(148, 0, 211, 0.1)',
    hovertemplate='Distance: %{x:.1f} kpc<br>Velocity: %{y:.0f} km/s<extra></extra>'
))

# Add galaxy structure annotations
fig5.add_vrect(x0=0, x1=3, fillcolor="yellow", opacity=0.1, annotation_text="Bulge")
fig5.add_vrect(x0=3, x1=15, fillcolor="cyan", opacity=0.1, annotation_text="Disk")
fig5.add_vrect(x0=15, x1=30, fillcolor="purple", opacity=0.1, annotation_text="Halo")

fig5.update_layout(
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
    showlegend=True
)

register_plot(
    fig5,
    plot_id='galaxy_rotation',
    metadata={
        'appearance': {
            'title': {'text': 'Dark Matter Mystery'}
        }
    }
)