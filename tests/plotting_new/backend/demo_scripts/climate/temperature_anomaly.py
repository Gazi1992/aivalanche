"""
🌍 Global Temperature Anomaly Visualization (1880-2024)
Using NASA GISTEMP data from local file
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from pathlib import Path

# Load NASA GISTEMP data from local file
def load_nasa_temperature_data():
    """Load global temperature anomaly data from local NASA GISTEMP file"""
    try:
        # Path to the data file
        data_file = Path(__file__).parent / 'nasa_temperature_data.csv'

        # Read the CSV file
        with open(data_file, 'r') as f:
            lines = f.readlines()

        # Find where the actual data starts (after header lines)
        data_start = 0
        for i, line in enumerate(lines):
            if line.startswith('Year'):
                data_start = i
                break

        # Parse the data
        years = []
        annual_temps = []

        for line in lines[data_start + 1:]:
            parts = line.strip().split(',')
            if len(parts) >= 14 and parts[0]:  # Ensure we have enough columns and a year value
                try:
                    year = int(parts[0])
                    # Column 13 is 'J-D' (annual mean)
                    if parts[13] and parts[13] != '***':
                        temp_anomaly = float(parts[13])
                        years.append(year)
                        annual_temps.append(temp_anomaly)
                except (ValueError, TypeError):
                    continue

        return pd.DataFrame({
            'Year': years,
            'Temperature_Anomaly': annual_temps
        })
    except Exception as e:
        print(f"Error loading NASA data from file: {e}")
        # Fallback to synthetic data
        np.random.seed(42)
        years = np.arange(1880, 2025)
        temp_anomaly = np.zeros(len(years))
        for i, year in enumerate(years):
            if year < 1940:
                temp_anomaly[i] = -0.3 + 0.003 * (year - 1880)
            elif year < 1980:
                temp_anomaly[i] = -0.1 + 0.002 * (year - 1940)
            else:
                temp_anomaly[i] = 0.1 + 0.02 * (year - 1980)
        temp_anomaly += 0.15 * np.sin(2 * np.pi * years / 3.5)
        temp_anomaly += np.random.normal(0, 0.1, len(years))

        return pd.DataFrame({
            'Year': years,
            'Temperature_Anomaly': temp_anomaly
        })

# Load temperature data
temp_data = load_nasa_temperature_data()

# === Plot 1: Contour Plot - Temperature Gradients Across Latitudes/Time ===

# Create synthetic latitude-based temperature data with realistic patterns
latitudes = np.linspace(-90, 90, 36)  # Every 5 degrees
years_grid = temp_data['Year'].values
lat_grid, year_grid = np.meshgrid(latitudes, years_grid)

# Create temperature grid with Arctic amplification
temp_grid = np.zeros_like(lat_grid)
for i, year in enumerate(years_grid):
    year_anomaly = temp_data[temp_data['Year'] == year]['Temperature_Anomaly'].values[0]
    for j, lat in enumerate(latitudes):
        # Arctic amplification: stronger warming at poles
        amplification = 1.0 + 0.8 * (abs(lat) / 90.0)**1.5
        temp_grid[i, j] = year_anomaly * amplification
        # Add latitude-dependent variation
        temp_grid[i, j] += 0.05 * np.sin(np.radians(lat * 2))

fig1 = go.Figure(data=go.Contour(
    z=temp_grid.T,
    x=years_grid,
    y=latitudes,
    colorscale=[
        [0, '#313695'],
        [0.2, '#4575b4'],
        [0.35, '#74add1'],
        [0.45, '#abd9e9'],
        [0.5, '#e0f3f8'],
        [0.55, '#fee090'],
        [0.65, '#fdae61'],
        [0.8, '#f46d43'],
        [1, '#a50026']
    ],
    contours=dict(
        coloring='heatmap',
        showlabels=True,
        labelfont=dict(size=10, color='white')
    ),
    colorbar=dict(
        title="Temperature<br>Anomaly (°C)",
        thickness=15
        # Removed explicit len to use Plotly default
    ),
    hovertemplate='Year: %{x}<br>Latitude: %{y}°<br>Anomaly: %{z:.2f}°C<extra></extra>'
))

fig1.update_layout(
    title={
        'text': '🌡️ Global Temperature Anomaly by Latitude (1880-2024)',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis_title="Year",
    yaxis_title="Latitude",
    xaxis=dict(
        showgrid=True,
        gridcolor='rgba(128, 128, 128, 0.2)',
        dtick=20
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(128, 128, 128, 0.2)',
        dtick=30,
        ticktext=['90°S', '60°S', '30°S', 'Equator', '30°N', '60°N', '90°N'],
        tickvals=[-90, -60, -30, 0, 30, 60, 90]
    )
)

register_plot(
    fig1,
    plot_id='temperature_contour',
    metadata={
        'appearance': {
            'title': {'text': 'Temperature Anomaly Gradients'}
        }
    }
)

# === Plot 2: Animated Choropleth Map - Global Temperature Changes ===

# Create country temperature data for animation
countries = ['USA', 'BRA', 'RUS', 'CHN', 'IND', 'AUS', 'CAN', 'MEX', 'ARG', 'ZAF',
             'GBR', 'FRA', 'DEU', 'ITA', 'ESP', 'NOR', 'SWE', 'FIN', 'JPN', 'KOR',
             'IDN', 'THA', 'VNM', 'PHL', 'MYS', 'NGA', 'EGY', 'KEN', 'ETH', 'GHA',
             'SAU', 'IRN', 'TUR', 'PAK', 'BGD', 'POL', 'UKR', 'NLD', 'BEL', 'GRC',
             'NZL', 'CHL', 'PER', 'COL', 'VEN', 'MAR', 'DZA', 'LBY', 'SDN', 'TUN']

# Latitude-based amplification factors for each country (approximate)
country_factors = {
    'CAN': 2.0, 'RUS': 1.8, 'NOR': 1.7, 'SWE': 1.7, 'FIN': 1.7,  # Arctic/Northern
    'USA': 1.2, 'CHN': 1.2, 'JPN': 1.2, 'KOR': 1.2, 'GBR': 1.2,  # Mid-latitude North
    'FRA': 1.1, 'DEU': 1.1, 'ITA': 1.1, 'ESP': 1.1, 'POL': 1.1,
    'UKR': 1.1, 'NLD': 1.1, 'BEL': 1.1, 'GRC': 1.0, 'TUR': 1.0,
    'IND': 0.9, 'MEX': 0.9, 'SAU': 0.9, 'EGY': 0.9, 'PAK': 0.9,  # Subtropical
    'BRA': 0.8, 'IDN': 0.8, 'THA': 0.8, 'VNM': 0.8, 'PHL': 0.8,  # Tropical
    'MYS': 0.8, 'NGA': 0.8, 'KEN': 0.8, 'ETH': 0.8, 'GHA': 0.8,
    'COL': 0.8, 'VEN': 0.8, 'BGD': 0.8,
    'AUS': 1.0, 'ZAF': 1.0, 'ARG': 1.0, 'CHL': 1.0, 'NZL': 1.0,  # Southern
    'PER': 0.9, 'MAR': 0.9, 'DZA': 0.9, 'LBY': 0.9, 'SDN': 0.9,
    'TUN': 0.9, 'IRN': 1.0
}

# Create frames for animation
frames = []
frame_years = list(range(1880, 2025, 10))  # Every 10 years

for year in frame_years:
    year_data = temp_data[temp_data['Year'] == year]
    if not year_data.empty:
        base_anomaly = year_data['Temperature_Anomaly'].values[0]

        country_temps = []
        for country in countries:
            factor = country_factors.get(country, 1.0)
            # Add some random variation
            variation = np.random.uniform(-0.1, 0.1)
            country_temps.append(base_anomaly * factor + variation)

        frame_df = pd.DataFrame({
            'iso_alpha': countries,
            'temperature_anomaly': country_temps,
            'year': year
        })

        frames.append(go.Frame(
            data=[go.Choropleth(
                locations=frame_df['iso_alpha'],
                z=frame_df['temperature_anomaly'],
                colorscale='RdBu_r',
                zmid=0,
                zmin=-2,
                zmax=2,
                colorbar=dict(
                    title="Anomaly (°C)",
                    thickness=15
                ),
                hovertemplate='%{z:.2f}°C<extra></extra>'
            )],
            name=str(year),
            layout=go.Layout(
                annotations=[
                    dict(
                        text=str(year),
                        xref="paper",
                        yref="paper",
                        x=0.05,
                        y=0.95,
                        showarrow=False,
                        font=dict(size=20, color="black")
                    )
                ]
            )
        ))

# Create initial frame
initial_year = frame_years[0]
year_data = temp_data[temp_data['Year'] == initial_year]
base_anomaly = year_data['Temperature_Anomaly'].values[0] if not year_data.empty else 0

initial_temps = []
for country in countries:
    factor = country_factors.get(country, 1.0)
    initial_temps.append(base_anomaly * factor)

fig2 = go.Figure(data=go.Choropleth(
    locations=countries,
    z=initial_temps,
    colorscale='RdBu_r',
    zmid=0,
    zmin=-2,
    zmax=2,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    colorbar=dict(
        title="Temperature<br>Anomaly (°C)",
        thickness=15
    ),
    hovertemplate='%{z:.2f}°C<extra></extra>'
))

fig2.frames = frames

# Add year annotation to the initial frame
fig2.add_annotation(
    text=str(initial_year),
    xref="paper",
    yref="paper",
    x=0.05,
    y=0.95,
    showarrow=False,
    font=dict(size=20, color="black")
)

# Add animation controls
fig2.update_layout(
    title={
        'text': '🗺️ Global Temperature Anomaly Animation (1880-2024)',
        'x': 0.5,
        'xanchor': 'center'
    },
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='natural earth'
    ),
    updatemenus=[{
        'type': 'buttons',
        'showactive': False,
        'x': 0.1,
        'y': 0,
        'xanchor': 'left',
        'buttons': [
            {
                'label': 'Play',
                'method': 'animate',
                'args': [None, {
                    'frame': {'duration': 500, 'redraw': True},
                    'fromcurrent': True,
                    'transition': {'duration': 300, 'easing': 'quadratic-in-out'}
                }]
            },
            {
                'label': 'Pause',
                'method': 'animate',
                'args': [[None], {
                    'frame': {'duration': 0, 'redraw': False},
                    'mode': 'immediate',
                    'transition': {'duration': 0}
                }]
            }
        ]
    }],
    sliders=[{
        'active': 0,
        'y': 0,
        'len': 0.8,
        'x': 0.1,
        'xanchor': 'left',
        'steps': [{
            'label': str(year),
            'method': 'animate',
            'args': [[str(year)], {
                'frame': {'duration': 300, 'redraw': True},
                'mode': 'immediate',
                'transition': {'duration': 300}
            }]
        } for year in frame_years]
    }]
)

register_plot(
    fig2,
    plot_id='temperature_map_animation',
    metadata={
        'appearance': {
            'title': {'text': 'Global Temperature Map Animation'}
        }
    }
)

# === Plot 3: Line Plot - Temperature Anomaly Trend with Moving Average ===

# Calculate 5-year moving average
temp_data['Moving_Avg'] = temp_data['Temperature_Anomaly'].rolling(window=5, center=True).mean()

fig3 = go.Figure()

# Annual data
fig3.add_trace(go.Scatter(
    x=temp_data['Year'],
    y=temp_data['Temperature_Anomaly'],
    mode='lines',
    name='Annual',
    line=dict(color='lightgray', width=1),
    hovertemplate='Year: %{x}<br>Anomaly: %{y:.2f}°C<extra></extra>'
))

# Moving average
fig3.add_trace(go.Scatter(
    x=temp_data['Year'],
    y=temp_data['Moving_Avg'],
    mode='lines',
    name='5-Year Average',
    line=dict(color='red', width=3),
    hovertemplate='Year: %{x}<br>5-yr Avg: %{y:.2f}°C<extra></extra>'
))

# Add zero line
fig3.add_hline(
    y=0,
    line_color='black',
    line_width=1.5,
    opacity=0.5
)

# Add detailed annotation for the baseline
fig3.add_annotation(
    text="0°C = 1951-1980 average<br><sub>NASA GISTEMP baseline period</sub>",
    xref="paper",
    yref="y",
    x=0.02,
    y=0.15,  # Higher above 0 line
    showarrow=False,
    font=dict(size=10, color="black"),
    align="left"
)

# Add period annotations
if len(temp_data) > 0:
    min_year = temp_data['Year'].min()
    max_year = temp_data['Year'].max()

    if min_year <= 1940 and max_year >= 1980:
        fig3.add_vrect(x0=max(min_year, 1940), x1=min(max_year, 1980),
                       fillcolor='blue', opacity=0.1,
                       annotation_text="Mid-century pause")
    if max_year >= 1980:
        fig3.add_vrect(x0=max(min_year, 1980), x1=max_year,
                       fillcolor='red', opacity=0.1,
                       annotation_text="Rapid warming")

fig3.update_layout(
    title={
        'text': '📈 Global Temperature Anomaly Trend (NASA GISTEMP)',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis_title="Year",
    yaxis_title="Temperature Anomaly (°C)",
    xaxis=dict(
        showgrid=True,
        gridcolor='rgba(128, 128, 128, 0.2)'
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(128, 128, 128, 0.2)',
        zeroline=True,
        zerolinecolor='rgba(0, 0, 0, 0.3)'
    ),
    hovermode='x unified',
    legend=dict(
        x=0.02,
        y=0.98,
        bgcolor='rgba(255, 255, 255, 0.8)',
        bordercolor='gray',
        borderwidth=1
    )
)

register_plot(
    fig3,
    plot_id='temperature_trend',
    metadata={
        'appearance': {
            'title': {'text': 'Temperature Anomaly Timeline'}
        }
    }
)

# === Plot 4: Violin Plot - Temperature Distribution by Decade ===

# Group data by decade
temp_data['Decade'] = (temp_data['Year'] // 10) * 10
decades_for_violin = temp_data.groupby('Decade').agg({
    'Temperature_Anomaly': list
}).reset_index()

# Create data for violin plot
violin_data = []
for _, row in decades_for_violin.iterrows():
    decade = row['Decade']
    temps = row['Temperature_Anomaly']
    for temp in temps:
        violin_data.append({
            'Decade': f"{decade}s",
            'Temperature': temp
        })

violin_df = pd.DataFrame(violin_data)

# Create color scale based on median temperature
decade_medians = violin_df.groupby('Decade')['Temperature'].median().reset_index()
decade_medians['Color'] = decade_medians['Temperature'].apply(
    lambda x: '#3288bd' if x < -0.2 else '#66c2a5' if x < 0 else '#fdae61' if x < 0.5 else '#d53e4f'
)

fig4 = go.Figure()

# Add violin plots for each decade
for decade in violin_df['Decade'].unique():
    decade_data = violin_df[violin_df['Decade'] == decade]
    color = decade_medians[decade_medians['Decade'] == decade]['Color'].values[0]

    fig4.add_trace(go.Violin(
        x=[decade] * len(decade_data),
        y=decade_data['Temperature'],
        name=decade,
        box_visible=True,
        meanline_visible=True,
        fillcolor=color,
        opacity=0.7,
        line_color='black',
        showlegend=False,
        hovertemplate='%{y:.2f}°C<extra></extra>'
    ))

# Add zero reference line
fig4.add_hline(
    y=0,
    line_color='black',
    line_width=1,
    opacity=0.5
)

# Add detailed annotation in top left
fig4.add_annotation(
    text="<b>Temperature Baseline</b><br>0°C represents the average<br>global temperature from<br>1951-1980 (NASA standard)",
    xref="paper",
    yref="paper",
    x=0.02,
    y=0.98,
    showarrow=False,
    font=dict(size=9, color="black"),
    align="left"
)

fig4.update_layout(
    title={
        'text': '🎻 Temperature Distribution by Decade',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis_title="Decade",
    yaxis_title="Temperature Anomaly (°C)",
    xaxis=dict(
        showgrid=False,
        tickangle=-45
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(128, 128, 128, 0.2)',
        zeroline=True,
        zerolinecolor='rgba(0, 0, 0, 0.3)'
    ),
    showlegend=False,
    violingap=0.3,
    violingroupgap=0.1
)

register_plot(
    fig4,
    plot_id='temperature_violin',
    metadata={
        'appearance': {
            'title': {'text': 'Temperature Distribution Analysis'}
        }
    }
)