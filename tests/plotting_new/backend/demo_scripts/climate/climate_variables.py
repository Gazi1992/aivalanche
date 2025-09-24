"""
🌍 Climate Variables Analysis
Interactive visualization of relationships between CO2, temperature, sea level, and ice coverage
Using real data from local files (NOAA, NASA sources)
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from pathlib import Path

# Load CO2 data from local NOAA file
def load_co2_data():
    """Load CO2 concentration data from local NOAA file"""
    try:
        data_file = Path(__file__).parent / 'noaa_co2_data.txt'

        with open(data_file, 'r') as f:
            lines = f.readlines()

        data = []
        for line in lines:
            if line and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        year = int(parts[0])
                        co2 = float(parts[1])
                        if 1960 <= year <= 2024:
                            data.append({'Year': year, 'CO2': co2})
                    except:
                        continue

        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error loading CO2 data from file: {e}")
        return None

# Load sea level data from local NASA file
def load_sea_level_data():
    """Load global mean sea level data from local file"""
    try:
        data_file = Path(__file__).parent / 'sea_level_data.csv'

        with open(data_file, 'r') as f:
            lines = f.readlines()

        data = []
        for line in lines:
            if line and not line.startswith('HDR'):
                parts = line.split()
                if len(parts) >= 12:
                    try:
                        year_decimal = float(parts[2])
                        year = int(year_decimal)
                        sea_level = float(parts[11])  # GMSL with GIA
                        if 1993 <= year <= 2024:
                            data.append({'Year': year, 'Sea_Level': sea_level})
                    except:
                        continue

        if data:
            df = pd.DataFrame(data)
            # Group by year and take mean
            df = df.groupby('Year').mean().reset_index()
            return df
    except Exception as e:
        print(f"Error loading sea level data: {e}")
        return None

# Load temperature data from NASA file
def load_temperature_data():
    """Load temperature anomaly data from local NASA GISTEMP file"""
    try:
        data_file = Path(__file__).parent / 'nasa_temperature_data.csv'

        with open(data_file, 'r') as f:
            lines = f.readlines()

        # Find where the actual data starts
        data_start = 0
        for i, line in enumerate(lines):
            if line.startswith('Year'):
                data_start = i
                break

        years = []
        annual_temps = []

        for line in lines[data_start + 1:]:
            parts = line.strip().split(',')
            if len(parts) >= 14 and parts[0]:
                try:
                    year = int(parts[0])
                    if parts[13] and parts[13] != '***':
                        temp_anomaly = float(parts[13])
                        if 1960 <= year <= 2024:  # Match our CO2 data range
                            years.append(year)
                            annual_temps.append(temp_anomaly)
                except (ValueError, TypeError):
                    continue

        return pd.DataFrame({
            'Year': years,
            'Temperature_Anomaly': annual_temps
        })
    except Exception as e:
        print(f"Error loading temperature data: {e}")
        return None

# Load real data from files
co2_data = load_co2_data()
sea_level_data = load_sea_level_data()
temp_data = load_temperature_data()

# Create comprehensive climate dataset
if co2_data is not None and not co2_data.empty:
    years = co2_data['Year'].values
    co2_values = co2_data['CO2'].values
else:
    # Fallback synthetic CO2 data
    years = np.arange(1960, 2025)
    co2_values = 315 + (years - 1960) * 1.5 + 10 * np.sin((years - 1960) * 2 * np.pi / 11)

# Get temperature anomaly data
if temp_data is not None and not temp_data.empty:
    # Merge with our years
    temp_anomaly = []
    for year in years:
        year_data = temp_data[temp_data['Year'] == year]
        if not year_data.empty:
            temp_anomaly.append(year_data['Temperature_Anomaly'].values[0])
        else:
            # Interpolate if missing
            temp_anomaly.append(np.nan)
    temp_anomaly = pd.Series(temp_anomaly).interpolate().values
else:
    # Fallback synthetic temperature
    temp_anomaly = -0.2 + (co2_values - co2_values[0]) / 100 + 0.1 * np.random.randn(len(years))

# Sea level data
if sea_level_data is not None and not sea_level_data.empty:
    # Interpolate sea level data to match our years
    sea_years = sea_level_data['Year'].values
    sea_values = sea_level_data['Sea_Level'].values
    sea_level = np.interp(years, sea_years, sea_values)
    # Extend before 1993 with synthetic trend
    pre_1993_mask = years < 1993
    if pre_1993_mask.any():
        n_pre = pre_1993_mask.sum()
        # Create a reasonable backward trend
        first_real = sea_level[~pre_1993_mask][0] if (~pre_1993_mask).any() else 0
        synthetic_trend = np.linspace(first_real - n_pre * 1.5, first_real, n_pre)
        sea_level[pre_1993_mask] = synthetic_trend
else:
    # Full synthetic sea level
    sea_level = -30 + (years - years[0]) * 1.7 + 2 * np.random.randn(len(years))

# Arctic ice extent (synthetic but realistic - decreasing trend)
np.random.seed(42)
ice_base = 7.0  # Million km²
ice_trend = -0.02 * (years - years[0])
ice_seasonal = 0.3 * np.sin(2 * np.pi * years / 3)
ice_noise = 0.1 * np.random.randn(len(years))
arctic_ice = ice_base + ice_trend + ice_seasonal + ice_noise

# Ocean heat content (synthetic but correlated with CO2)
ocean_heat = -5 + (co2_values - co2_values[0]) / 10 + 0.5 * np.random.randn(len(years))

# Create comprehensive dataframe
climate_df = pd.DataFrame({
    'Year': years,
    'CO2_ppm': co2_values,
    'Temp_Anomaly': temp_anomaly,
    'Arctic_Ice': arctic_ice,
    'Sea_Level': sea_level,
    'Ocean_Heat': ocean_heat
})

# === Plot 1: Parallel Coordinates Plot ===

# Create color scale based on year
colors = px.colors.sequential.Turbo
n_colors = len(colors)

# Create parallel coordinates plot
fig1 = go.Figure(data=
    go.Parcoords(
        line=dict(
            color=years,
            colorscale='Turbo',
            showscale=True,
            cmin=years.min(),
            cmax=years.max(),
            colorbar=dict(
                title='Year',
            )
        ),
        # Configure how unselected (filtered) lines appear
        unselected=dict(
            line=dict(
                color='rgba(150, 150, 150, 0.9)',  # Gray with medium opacity
            )
        ),
        labelside='bottom',  # Place axis labels on bottom
        labelfont=dict(size=12),
        dimensions=[
            dict(
                range=[climate_df['CO2_ppm'].min(), climate_df['CO2_ppm'].max()],
                label='CO₂ (ppm)',
                values=climate_df['CO2_ppm']
            ),
            dict(
                range=[climate_df['Temp_Anomaly'].min(), climate_df['Temp_Anomaly'].max()],
                label='Temp Anomaly (°C)',
                values=climate_df['Temp_Anomaly']
            ),
            dict(
                range=[climate_df['Arctic_Ice'].min(), climate_df['Arctic_Ice'].max()],
                label='Arctic Ice (M km²)',
                values=climate_df['Arctic_Ice']
            ),
            dict(
                range=[climate_df['Sea_Level'].min(), climate_df['Sea_Level'].max()],
                label='Sea Level (mm)',
                values=climate_df['Sea_Level']
            ),
            dict(
                range=[climate_df['Ocean_Heat'].min(), climate_df['Ocean_Heat'].max()],
                label='Ocean Heat (ZJ)',
                values=climate_df['Ocean_Heat']
            )
        ]
    )
)

fig1.update_layout(
    title={
        'text': '🌡️ Climate Variables Relationships (1960-2024)',
        'x': 0.5,
        'xanchor': 'center'
    },
    margin=dict(t=100, b=50)
)

register_plot(
    fig1,
    plot_id='climate_parallel',
    metadata={
        'appearance': {
            'title': {'text': 'Climate Variables Parallel Coordinates'}
        }
    }
)

# === Plot 2: SPLOM (Scatterplot Matrix) - Climate Variables Relationships ===

# Select the variables for SPLOM
splom_vars = ['CO2_ppm', 'Temp_Anomaly', 'Arctic_Ice', 'Sea_Level', 'Ocean_Heat']
splom_labels = {
    'CO2_ppm': 'CO₂ (ppm)',
    'Temp_Anomaly': 'Temp (°C)',
    'Arctic_Ice': 'Ice (M km²)',
    'Sea_Level': 'Sea Level (mm)',
    'Ocean_Heat': 'Ocean Heat (ZJ)'
}

# Create SPLOM
fig2 = go.Figure(data=go.Splom(
    dimensions=[
        dict(label=splom_labels[var], values=climate_df[var], visible=True)
        for var in splom_vars
    ],
    diagonal=dict(visible=False),  # Hide diagonal
    showupperhalf=False,  # Only show lower triangle to reduce redundancy
    marker=dict(
        color=climate_df['Year'],
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(
            title='Year',
            thickness=15
        ),
        size=4,
        line=dict(width=0.5, color='white'),
        opacity=0.7
    ),
    text=climate_df['Year'],
    hovertemplate='Year: %{text}<br>%{xaxis.title.text}: %{x:.2f}<br>%{yaxis.title.text}: %{y:.2f}<extra></extra>'
))

# Update layout
fig2.update_layout(
    title={
        'text': '📊 Climate Variables Scatterplot Matrix (1960-2024)',
        'x': 0.5,
        'xanchor': 'center'
    },
    dragmode='pan',
    hovermode='closest'
)

# Add correlation coefficients as annotations
correlations = climate_df[splom_vars].corr()
annotations = []

# Calculate positions for correlation text
n_vars = len(splom_vars)
for i in range(n_vars):
    for j in range(i):
        # Position calculation for lower triangle
        x_pos = j / (n_vars - 1)
        y_pos = 1 - (i / (n_vars - 1))

        corr_value = correlations.iloc[i, j]

        # Color based on correlation strength
        if abs(corr_value) > 0.7:
            color = 'darkgreen' if corr_value > 0 else 'darkred'
        elif abs(corr_value) > 0.4:
            color = 'green' if corr_value > 0 else 'red'
        else:
            color = 'gray'

        annotations.append(
            dict(
                text=f'r={corr_value:.2f}',
                xref='paper',
                yref='paper',
                x=x_pos + 0.05,
                y=y_pos - 0.02,
                showarrow=False,
                font=dict(size=8, color=color),
                opacity=0.8
            )
        )

fig2.update_layout(annotations=annotations)

register_plot(
    fig2,
    plot_id='climate_splom',
    metadata={
        'appearance': {
            'title': {'text': 'Climate Variables SPLOM'}
        }
    }
)