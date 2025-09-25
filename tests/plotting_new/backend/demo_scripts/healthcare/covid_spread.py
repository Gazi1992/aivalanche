"""
COVID-19 Global Spread
Visualizing pandemic progression with multi-axis charts and animated spread
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# === Load real COVID-19 timeline data ===
np.random.seed(2020)

# Load the COVID timeline data
covid_data_path = os.path.join(os.path.dirname(__file__) if '__file__' in globals() else 'demo_scripts/healthcare',
                               'covid_timeline_data.json')

try:
    with open(covid_data_path, 'r') as f:
        covid_timeline = json.load(f)
    print(f"Loaded COVID-19 timeline data with {len(covid_timeline['countries'])} countries")
except FileNotFoundError:
    print(f"Warning: Could not find COVID-19 timeline data at {covid_data_path}")
    covid_timeline = None

# Timeline from early 2020 to mid-2021
dates = pd.date_range('2020-01-15', '2021-06-30', freq='D')

# Simulate wave patterns
def generate_waves(dates, peak_dates, peak_values):
    """Generate realistic pandemic waves"""
    values = np.zeros(len(dates))
    for peak_date, peak_value in zip(peak_dates, peak_values):
        peak_idx = (dates == pd.to_datetime(peak_date)).argmax()
        for i, date in enumerate(dates):
            days_from_peak = abs(i - peak_idx)
            # Gaussian-like wave
            values[i] += peak_value * np.exp(-days_from_peak**2 / (2 * 30**2))
    return values

# Define pandemic waves
case_peaks = ['2020-04-10', '2020-07-20', '2020-11-25', '2021-01-10', '2021-04-15']
case_magnitudes = [100000, 75000, 150000, 200000, 120000]

death_peaks = ['2020-04-25', '2020-08-05', '2020-12-10', '2021-01-25', '2021-04-30']
death_magnitudes = [2000, 1500, 3000, 4000, 2500]

# Generate data
daily_cases = generate_waves(dates, case_peaks, case_magnitudes)
daily_deaths = generate_waves(dates, death_peaks, death_magnitudes)

# Add noise
daily_cases += np.random.normal(0, daily_cases * 0.1)
daily_deaths += np.random.normal(0, daily_deaths * 0.1)

# Ensure non-negative
daily_cases = np.maximum(daily_cases, 0)
daily_deaths = np.maximum(daily_deaths, 0)

# Calculate cumulative values
cumulative_cases = np.cumsum(daily_cases)
cumulative_deaths = np.cumsum(daily_deaths)

# Vaccination data (starts March 2021)
vacc_start = pd.to_datetime('2020-12-15')
vacc_start_idx = (dates >= vacc_start).argmax()
daily_vaccinations = np.zeros(len(dates))
if vacc_start_idx > 0:
    # Ramp up vaccinations
    vacc_days = len(dates) - vacc_start_idx
    ramp = np.linspace(0, 1, min(90, vacc_days))
    steady = np.ones(max(0, vacc_days - 90))
    vacc_profile = np.concatenate([ramp, steady])[:vacc_days]
    daily_vaccinations[vacc_start_idx:] = vacc_profile * 3000000  # 3M per day peak

cumulative_vaccinations = np.cumsum(daily_vaccinations)

# === Visualization 1: Regional Impact Heatmap ===
# Create a heatmap showing impact across different regions over time

# Generate regional data for different continents/regions
regions = ['North America', 'Europe', 'Asia', 'South America', 'Africa', 'Oceania', 'Middle East']
months = pd.date_range('2020-01', '2021-12', freq='ME')

# Create severity matrix (normalized 0-1)
np.random.seed(42)
severity_matrix = np.zeros((len(regions), len(months)))

for i, region in enumerate(regions):
    # Different peak timing for different regions
    peak_month = 3 + i * 2  # Staggered peaks
    for j in range(len(months)):
        # Create wave patterns with different intensities
        base = np.sin(j * np.pi / 6 + i) * 0.3 + 0.5
        if j == peak_month or j == peak_month + 12:
            base *= 1.5  # Peak months
        severity_matrix[i, j] = np.clip(base + np.random.normal(0, 0.1), 0, 1)

# Custom colorscale from green (low) to red (high)
colorscale = [
    [0, 'rgb(26, 152, 80)'],     # Green
    [0.25, 'rgb(255, 237, 111)'], # Light yellow
    [0.5, 'rgb(254, 178, 76)'],   # Orange
    [0.75, 'rgb(240, 59, 32)'],   # Red-orange
    [1, 'rgb(189, 0, 38)']        # Dark red
]

fig1 = go.Figure(data=go.Heatmap(
    z=severity_matrix,
    x=[month.strftime('%b %Y') for month in months],
    y=regions,
    colorscale=colorscale,
    colorbar=dict(
        title=dict(text='Severity<br>Index', side='right'),
        tickmode='array',
        ticktext=['Low', 'Moderate', 'High', 'Severe', 'Critical'],
        tickvals=[0, 0.25, 0.5, 0.75, 1],
        len=0.5,
        y=0.5
    ),
    hovertemplate='<b>%{y}</b><br>%{x}<br>Severity: %{z:.2f}<extra></extra>'
))

# Add text annotations for significant events
annotations = []
# Mark vaccine rollout
vaccine_month = 12  # Dec 2020
for i, region in enumerate(regions):
    if severity_matrix[i, vaccine_month] > 0.5:
        annotations.append(dict(
            x=months[vaccine_month].strftime('%b %Y'),
            y=region,
            text='💉',
            showarrow=False,
            font=dict(size=16)
        ))

fig1.update_layout(
    title={
        'text': 'COVID-19 Regional Impact Heatmap',
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(size=20)
    },
    xaxis=dict(
        title='Timeline',
        tickangle=45,
        side='bottom'
    ),
    yaxis=dict(
        title='Region',
        tickmode='array',
        ticktext=regions,
        tickvals=list(range(len(regions)))
    ),
    annotations=annotations,
    height=500,
    margin=dict(l=120, r=120, t=80, b=100)
)

# Register plot (register_plot function will be available in execution context)
if 'register_plot' in globals():
    register_plot(
        fig1,
        plot_id='covid_timeline',
        metadata={
            'appearance': {
                'title': {'text': 'Regional COVID-19 Impact'}
            }
        }
    )

# === Visualization 2: D3 Animated World Map - Global Spread ===
# Load the world topology data
if '__file__' in globals():
    current_dir = os.path.dirname(os.path.abspath(__file__))
else:
    # When running in execution context, use relative path
    current_dir = 'demo_scripts/healthcare'

world_topo_path = os.path.join(current_dir, 'world-110m.json')

# Read the topology data
world_topo_data = None
try:
    with open(world_topo_path, 'r') as f:
        world_topo_data = json.load(f)
    print(f"Successfully loaded topology data from {world_topo_path}")
except FileNotFoundError:
    print(f"Warning: Could not find topology file at {world_topo_path}")
    # Try alternative paths
    alt_paths = [
        'backend/demo_scripts/healthcare/world-110m.json',
        './world-110m.json',
        os.path.join(os.getcwd(), 'demo_scripts/healthcare/world-110m.json')
    ]
    for alt_path in alt_paths:
        if os.path.exists(alt_path):
            print(f"Found topology file at {alt_path}")
            with open(alt_path, 'r') as f:
                world_topo_data = json.load(f)
            break

    if world_topo_data is None:
        print(f"Error: Could not find world-110m.json in any expected location")
        world_topo_data = {}
except Exception as e:
    print(f"Error loading topology data: {e}")
    world_topo_data = {}

# Pass the topology data to the D3 visualization
spread_animation = '''
// COVID-19 animated world map using real world topology
// Reserve space for colorbar on the right
const colorbarSpace = 100;  // Space for colorbar and labels
const padding = 20;
const mapWidth = width - colorbarSpace - padding;  // Reduce map width to make room for colorbar
const mapHeight = height - 60;  // Leave space for title and bottom text
const mapOffsetY = 40;  // Offset from top for title

// Clear previous content
svg.selectAll('*').remove();

// Full background - light blue for entire SVG
svg.append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', width)
    .attr('height', height)
    .attr('fill', '#e6f3ff');

// Title
svg.append('text')
    .attr('x', width / 2)
    .attr('y', 25)
    .attr('text-anchor', 'middle')
    .attr('font-size', '18px')
    .attr('font-weight', 'bold')
    .attr('fill', '#333333')
    .text('COVID-19 Global Spread - World Map');

// Setup projection - adjust scale for smaller map
const projection = d3.geoNaturalEarth1()
    .scale((mapWidth / 640) * 100)
    .translate([mapWidth / 2, mapOffsetY + mapHeight / 2]);

const path = d3.geoPath()
    .projection(projection);

// World topology data passed from Python
const world = data.world_topo;

// Log what we received
console.log("Received data:", data);
console.log("World topology:", world);
if (world) {
    console.log("World type:", world.type);
    console.log("Has arcs:", !!world.arcs);
    console.log("Has objects:", !!world.objects);
    if (world.objects) {
        console.log("Objects available:", Object.keys(world.objects));
    }
}

// Check if topojson library is available
if (typeof topojson === 'undefined') {
    console.error("topojson library is not available!");
    svg.append("text")
        .attr("x", mapWidth / 2)
        .attr("y", mapHeight / 2)
        .attr("text-anchor", "middle")
        .attr("fill", "red")
        .text("Error: topojson library not loaded");
    return;
}

console.log("topojson library is available:", topojson);

// Use the real topojson library that's now available
// (topojson is passed as a parameter from D3Container)

// Check if we have valid topology data
if (!world || !world.arcs || !world.objects) {
    console.error("Invalid topology data - missing required properties");
    console.error("World:", world);
    console.error("Has arcs:", world ? !!world.arcs : false);
    console.error("Has objects:", world ? !!world.objects : false);

    svg.append("text")
        .attr("x", mapWidth / 2)
        .attr("y", mapHeight / 2)
        .attr("text-anchor", "middle")
        .attr("fill", "red")
        .text("Error: Invalid topology data");
    return;
}


// Draw graticule
const graticule = d3.geoGraticule();
svg.append("path")
    .datum(graticule())
    .attr("d", path)
    .style("fill", "none")
    .style("stroke", "#cccccc")
    .style("stroke-width", 0.5)
    .style("stroke-opacity", 0.5);

// Draw world outline
svg.append("path")
    .datum({type: "Sphere"})
    .attr("d", path)
    .attr("fill", "none")
    .attr("stroke", "#999999")
    .attr("stroke-width", 1);

// Try to use topojson data if available
let countries = null;
let landFeatures = null;

if (world && world.objects) {
    try {
        // First try to get countries for better detail
        if (world.objects.countries) {
            countries = topojson.feature(world, world.objects.countries);
            console.log("Loaded", countries.features.length, "countries");
        }
        // Also try to get land masses
        if (world.objects.land) {
            landFeatures = topojson.feature(world, world.objects.land);
            console.log("Loaded land features");
        }
    } catch(e) {
        console.log("Could not parse topojson:", e);
    }
}

// Draw countries if we have them
if (countries && countries.features && countries.features.length > 0) {
    // Log first few country features to see structure
    console.log("Sample country features:");
    countries.features.slice(0, 5).forEach(f => {
        console.log("Country:", f.properties, "ID field:", f.properties?.id || f.id);
    });

    const countryPaths = svg.append("g")
        .attr("class", "countries")
        .selectAll("path")
        .data(countries.features)
        .enter().append("path")
        .attr("d", path)
        .attr("fill", "#d3d3d3")
        .attr("stroke", "#ffffff")
        .attr("stroke-width", 0.5)
        .attr("class", d => {
            // Use the numeric ID from properties for matching with countryData
            const countryId = d.properties?.id || d.id || "unknown";
            return "country-path country-" + countryId;
        })
        .attr("data-country-id", d => d.properties?.id || d.id || "unknown")
        .attr("data-country-name", d => d.properties?.name || "");

    console.log("Created country paths:", countryPaths.size(), "countries");
} else if (landFeatures && landFeatures.features) {
    // Fallback to land features if no countries
    svg.append("g")
        .attr("class", "land")
        .selectAll("path")
        .data(landFeatures.features)
        .enter().append("path")
        .attr("d", path)
        .attr("fill", "#d3d3d3")
        .attr("stroke", "#ffffff")
        .attr("stroke-width", 0.5);
} else {
    // Fallback: Simple continent outlines
    const continents = [
        // North America
        {coords: [[-130, 50], [-130, 25], [-100, 15], [-80, 10], [-75, 25], [-60, 45], [-80, 60], [-130, 60], [-130, 50]]},
        // South America
        {coords: [[-80, 10], [-75, -5], [-70, -20], [-75, -40], [-70, -55], [-55, -55], [-40, -20], [-35, -5], [-45, 0], [-50, 5], [-80, 10]]},
        // Europe
        {coords: [[-10, 36], [-5, 43], [0, 50], [10, 55], [30, 60], [40, 65], [30, 70], [15, 70], [5, 58], [-5, 55], [-10, 48], [-10, 36]]},
        // Africa
        {coords: [[-17, 35], [-5, 36], [10, 37], [30, 30], [35, 28], [40, 15], [50, 10], [40, -10], [35, -30], [20, -35], [10, -30], [0, -5], [-10, 5], [-17, 15], [-17, 35]]},
        // Asia
        {coords: [[30, 30], [40, 30], [50, 40], [70, 40], [90, 50], [120, 50], [140, 45], [145, 35], [130, 20], [100, 10], [80, 5], [70, 20], [50, 25], [30, 30]]},
        // Australia
        {coords: [[115, -10], [130, -12], [145, -15], [150, -25], [145, -38], [130, -35], [115, -35], [115, -20], [115, -10]]}
    ];

    continents.forEach(continent => {
        svg.append("path")
            .datum({type: "Polygon", coordinates: [continent.coords]})
            .attr("d", path)
            .attr("fill", "#d3d3d3")
            .attr("stroke", "#999999")
            .attr("stroke-width", 0.5);
    });
}

// Country infection data - passed from Python with real timeline data
const countryData = data.country_timeline || [
    // Fallback data if not provided
    {name: 'China', id: 156, coords: [104.2, 35.9], startDay: 0},
    {name: 'Thailand', id: 764, coords: [100.99, 15.87], startDay: 43},
    {name: 'Japan', id: 392, coords: [138.25, 36.20], startDay: 46},
    {name: 'South Korea', id: 410, coords: [127.77, 35.91], startDay: 50},
    {name: 'United States', id: 840, coords: [-95.71, 37.09], startDay: 51},
    {name: 'Singapore', id: 702, coords: [103.82, 1.35], startDay: 53},
    {name: 'France', id: 250, coords: [2.21, 46.23], startDay: 54},
    {name: 'Germany', id: 276, coords: [10.45, 51.17], startDay: 57},
    {name: 'Italy', id: 380, coords: [12.57, 41.87], startDay: 61},
    {name: 'Spain', id: 724, coords: [-3.75, 40.46], startDay: 61},
    {name: 'United Kingdom', id: 826, coords: [-3.44, 55.38], startDay: 61},
    {name: 'Russia', id: 643, coords: [105.32, 61.52], startDay: 61},
    {name: 'India', id: 356, coords: [78.96, 20.59], startDay: 60},
    {name: 'Iran', id: 364, coords: [53.69, 32.43], startDay: 80},
    {name: 'Brazil', id: 76, coords: [-51.93, -14.24], startDay: 87},
    {name: 'Canada', id: 124, coords: [-106.35, 56.13], startDay: 55},
    {name: 'Australia', id: 36, coords: [133.78, -25.27], startDay: 55},
    {name: 'Mexico', id: 484, coords: [-102.55, 23.63], startDay: 89},
    {name: 'South Africa', id: 710, coords: [22.94, -30.56], startDay: 95},
    {name: 'Turkey', id: 792, coords: [35.24, 38.96], startDay: 101}
];

// Color scale for infection levels
const colorScale = d3.scaleSequential()
    .domain([0, 100])
    .interpolator(d3.interpolateReds);

// Add country infection overlay
const infectionLayer = svg.append('g').attr('class', 'infections');

// Add country markers for key locations
const markers = svg.append('g').attr('class', 'markers');

countryData.forEach(country => {
    const coords = projection(country.coords);

    markers.append('circle')
        .attr('cx', coords[0])
        .attr('cy', coords[1])
        .attr('r', 3)
        .attr('fill', '#ff0000')
        .attr('stroke', '#ffffff')
        .attr('stroke-width', 1)
        .attr('opacity', 0)
        .attr('class', `marker-${country.id}`);
});

// Day counter - positioned below title
let currentDay = 0;
const dayText = svg.append('text')
    .attr('x', mapWidth / 2)
    .attr('y', mapOffsetY + 20)
    .attr('text-anchor', 'middle')
    .attr('font-size', '14px')
    .attr('fill', '#333333')
    .text('Day 0');

// Status text - positioned at bottom of map
const statusText = svg.append('text')
    .attr('x', mapWidth / 2)
    .attr('y', mapOffsetY + mapHeight - 10)
    .attr('text-anchor', 'middle')
    .attr('font-size', '12px')
    .attr('fill', '#333333')
    .text('');

// Create a continuous color bar legend - aligned with the map
const legendWidth = 20;
const legendHeight = mapHeight * 0.8;  // 80% of map height for better proportions
const legendX = mapWidth + 30;  // Position to the right of the map with some spacing
const legendY = mapOffsetY + (mapHeight - legendHeight) / 2;  // Center vertically within map area

// Create gradient for the colorbar
const defs = svg.append('defs');
const linearGradient = defs.append('linearGradient')
    .attr('id', 'infection-gradient')
    .attr('x1', '0%')
    .attr('y1', '100%')
    .attr('x2', '0%')
    .attr('y2', '0%');

// Add gradient stops (matching the Reds color scale)
const nStops = 10;
for (let i = 0; i <= nStops; i++) {
    linearGradient.append('stop')
        .attr('offset', `${(i / nStops) * 100}%`)
        .attr('stop-color', colorScale(i * 10));
}

// Draw the colorbar
const legendGroup = svg.append('g')
    .attr('transform', `translate(${legendX}, ${legendY})`);

legendGroup.append('rect')
    .attr('width', legendWidth)
    .attr('height', legendHeight)
    .attr('fill', 'url(#infection-gradient)')
    .attr('stroke', '#333')
    .attr('stroke-width', 1);

// Add title
legendGroup.append('text')
    .attr('x', legendWidth / 2)
    .attr('y', -10)
    .attr('text-anchor', 'middle')
    .attr('font-size', '12px')
    .attr('font-weight', 'bold')
    .attr('fill', '#333')
    .text('Infection Level');

// Add scale labels with Low, Medium, High
const scaleLabels = [
    {label: 'None', pos: 0},
    {label: 'Low', pos: 0.25},
    {label: 'Medium', pos: 0.5},
    {label: 'High', pos: 0.75},
    {label: 'Critical', pos: 1.0}
];

scaleLabels.forEach(item => {
    const y = legendHeight - (item.pos * legendHeight);

    // Tick marks
    legendGroup.append('line')
        .attr('x1', legendWidth)
        .attr('y1', y)
        .attr('x2', legendWidth + 5)
        .attr('y2', y)
        .attr('stroke', '#333')
        .attr('stroke-width', 1);

    // Labels
    legendGroup.append('text')
        .attr('x', legendWidth + 8)
        .attr('y', y + 4)
        .attr('font-size', '10px')
        .attr('fill', '#333')
        .text(item.label);
});

// Animate infection spread
function animateSpread() {
    const animationSpeed = 100;
    let infectedCountries = new Set();

    // Log which country paths we can find
    console.log("Checking country paths availability:");
    countryData.forEach(country => {
        const countryPath = svg.select(`.country-${country.id}`);
        console.log(`Country ${country.name} (ID: ${country.id}):`, !countryPath.empty() ? "Found" : "Not found");
    });

    const interval = setInterval(() => {
        currentDay += 2;

        // Update day counter - just show the day number
        dayText.text(`Day ${currentDay}`);

        // Update countries
        countryData.forEach(country => {
            if (currentDay >= country.startDay) {
                if (!infectedCountries.has(country.id)) {
                    infectedCountries.add(country.id);

                    // Show marker
                    svg.select(`.marker-${country.id}`)
                        .transition()
                        .duration(500)
                        .attr('opacity', 1)
                        .attr('r', 5)
                        .transition()
                        .duration(1000)
                        .attr('r', 3);
                }

                // Update country color on the map
                const level = Math.min(100, (currentDay - country.startDay) * 2);

                // Update the actual country path color
                svg.select(`.country-${country.id}`)
                    .transition()
                    .duration(500)
                    .attr('fill', colorScale(level));

                // Also update marker for visual emphasis
                svg.select(`.marker-${country.id}`)
                    .transition()
                    .duration(500)
                    .attr('fill', colorScale(level))
                    .attr('r', 4 + level/20);
            }
        });

        // Update status
        statusText.text(`Infected Countries: ${infectedCountries.size} / ${countryData.length}`);

        // Reset animation
        if (currentDay >= 150) {
            clearInterval(interval);
            setTimeout(() => {
                // Reset all countries and markers
                countryData.forEach(country => {
                    // Reset country color on map
                    svg.select(`.country-${country.id}`)
                        .transition()
                        .duration(500)
                        .attr('fill', '#d3d3d3');

                    // Reset marker
                    svg.select(`.marker-${country.id}`)
                        .transition()
                        .duration(500)
                        .attr('opacity', 0)
                        .attr('fill', '#ff0000')
                        .attr('r', 3);
                });

                currentDay = 0;
                infectedCountries.clear();
                dayText.text('Day 0');
                statusText.text('');

                // Restart animation
                setTimeout(animateSpread, 1000);
            }, 2000);
        }
    }, animationSpeed);
}

// Start animation
setTimeout(animateSpread, 1000);

const animation = {
    play: () => { },
    pause: () => { },
    stop: () => { }
};

return animation;
'''

# Prepare country timeline data for D3 visualization
country_timeline_data = []
if covid_timeline and 'countries' in covid_timeline:
    for country in covid_timeline['countries']:  # Use all available countries
        country_timeline_data.append({
            'name': country['name'],
            'id': country['iso_code'],
            'coords': country['coords'],
            'startDay': country['days_from_reference']
        })
    print(f"Passing {len(country_timeline_data)} countries to D3 visualization")
else:
    # Use default data if timeline not loaded
    country_timeline_data = None

# Register the spread animation with world topology data and timeline (functions available in execution context)
if 'd3_custom' in globals() and 'register_d3_visualization' in globals():
    spread_viz = d3_custom(spread_animation, data={
        'world_topo': world_topo_data,
        'country_timeline': country_timeline_data
    })
    register_d3_visualization(spread_viz, 'covid_spread_map')

# === Visualization 3: Comparison Chart - Waves Analysis ===
# Compare different waves
waves_data = []
for i, (peak_date, peak_value) in enumerate(zip(case_peaks, case_magnitudes)):
    wave_num = i + 1
    waves_data.append({
        'Wave': f'Wave {wave_num}',
        'Peak Date': peak_date,
        'Peak Cases': peak_value,
        'Duration': 60 + i * 10,  # Waves get longer
        'Severity': peak_value / 1000
    })

df_waves = pd.DataFrame(waves_data)

fig3 = go.Figure()

# Bar chart for peak cases with gradient colors
colors_gradient = ['#3498db', '#5499d4', '#749acc', '#949bc3', '#b49cbb']

fig3.add_trace(go.Bar(
    x=df_waves['Wave'],
    y=df_waves['Peak Cases'],
    name='Peak Daily Cases',
    marker_color=colors_gradient,
    text=df_waves['Peak Cases'].apply(lambda x: f'{x/1000:.0f}K'),
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Peak Cases: %{y:,.0f}<extra></extra>'
))

# Add annotations for key metrics
for i, row in df_waves.iterrows():
    fig3.add_annotation(
        x=row['Wave'],
        y=row['Peak Cases'],
        text=f"Duration: {row['Duration']}d",
        showarrow=False,
        yshift=20,
        font=dict(size=9, color='gray')
    )

fig3.update_layout(
    title={
        'text': 'COVID-19 Wave Comparison',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(title='Pandemic Wave'),
    yaxis=dict(
        title='Peak Daily Cases',
        showgrid=True
    ),
    hovermode='x unified',
    showlegend=False
)

# Register plot (register_plot function will be available in execution context)
if 'register_plot' in globals():
    register_plot(
        fig3,
        plot_id='wave_comparison',
        metadata={
            'appearance': {
                'title': {'text': 'Pandemic Waves Analysis'}
            }
        }
    )