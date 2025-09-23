"""
Geospatial Data Demo
Real-world geographic examples including maps, location data, and spatial analysis
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_geospatial_plots():
    """Create geospatial data visualizations"""
    plots = []

    # 1. Choropleth Map - Population Density
    # US state data
    states = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI',
              'NJ', 'VA', 'WA', 'AZ', 'MA', 'TN', 'IN', 'MO', 'MD', 'WI']
    population_density = [253.9, 111.0, 401.4, 421.0, 286.1, 231.1, 282.3, 185.3,
                         218.2, 174.8, 1218.0, 213.5, 107.1, 64.0, 894.5, 167.7,
                         188.0, 89.7, 626.0, 105.7]
    state_names = ['California', 'Texas', 'Florida', 'New York', 'Pennsylvania',
                   'Illinois', 'Ohio', 'Georgia', 'North Carolina', 'Michigan',
                   'New Jersey', 'Virginia', 'Washington', 'Arizona', 'Massachusetts',
                   'Tennessee', 'Indiana', 'Missouri', 'Maryland', 'Wisconsin']

    fig1 = go.Figure(data=go.Choropleth(
        locations=states,
        z=population_density,
        locationmode='USA-states',
        colorscale='Viridis',
        text=state_names,
        colorbar_title="People/sq mile",
        marker_line_color='white',
        marker_line_width=2
    ))

    fig1.update_layout(
        title='US Population Density by State',
        geo_scope='usa',
        geo=dict(
            showlakes=True,
            lakecolor='rgb(255, 255, 255)'
        )
    )
    plots.append(('geo_choropleth', fig1, {
        'appearance': {'title': {'text': 'Population Density Map'}}
    }))

    # 2. Scatter Geo - Global Cities
    cities = ['Tokyo', 'Delhi', 'Shanghai', 'São Paulo', 'Mumbai', 'Cairo',
              'Beijing', 'Dhaka', 'Mexico City', 'Osaka', 'New York', 'London',
              'Paris', 'Moscow', 'Los Angeles', 'Istanbul', 'Lagos', 'Sydney']
    lat = [35.68, 28.61, 31.23, -23.55, 19.08, 30.04,
           39.90, 23.81, 19.43, 34.69, 40.71, 51.51,
           48.86, 55.76, 34.05, 41.01, 6.52, -33.87]
    lon = [139.69, 77.21, 121.47, -46.63, 72.88, 31.24,
           116.41, 90.41, -99.13, 135.50, -74.01, -0.13,
           2.35, 37.62, -118.24, 28.98, 3.38, 151.21]
    population_millions = [37.4, 30.3, 27.1, 22.0, 20.4, 20.1,
                          21.5, 21.0, 21.7, 19.2, 18.8, 9.3,
                          11.0, 12.5, 13.1, 15.5, 14.4, 5.3]

    fig2 = go.Figure(data=go.Scattergeo(
        lon=lon,
        lat=lat,
        text=[f"{c}: {p:.1f}M" for c, p in zip(cities, population_millions)],
        mode='markers',
        marker=dict(
            size=[p*2 for p in population_millions],
            color=population_millions,
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Population (M)"),
            line_width=0.5,
            line_color='white'
        )
    ))

    fig2.update_layout(
        title='Global Megacities Population',
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        )
    )
    plots.append(('geo_scatter', fig2, {
        'appearance': {'title': {'text': 'Global Cities'}}
    }))

    # 3. Density Mapbox - Urban Heat Island
    # Simulate temperature data points in a city
    np.random.seed(42)
    n_points = 500
    # Create clusters of heat
    center_lat, center_lon = 40.7128, -74.0060  # NYC

    # Downtown cluster (hotter)
    downtown_lat = np.random.normal(center_lat, 0.02, n_points//3)
    downtown_lon = np.random.normal(center_lon, 0.02, n_points//3)
    downtown_temp = np.random.normal(85, 3, n_points//3)

    # Parks cluster (cooler)
    park_lat = np.random.normal(center_lat + 0.05, 0.01, n_points//3)
    park_lon = np.random.normal(center_lon - 0.03, 0.01, n_points//3)
    park_temp = np.random.normal(75, 2, n_points//3)

    # Residential (medium)
    res_lat = np.random.normal(center_lat - 0.03, 0.03, n_points//3 + n_points%3)
    res_lon = np.random.normal(center_lon + 0.04, 0.03, n_points//3 + n_points%3)
    res_temp = np.random.normal(80, 2.5, n_points//3 + n_points%3)

    all_lat = np.concatenate([downtown_lat, park_lat, res_lat])
    all_lon = np.concatenate([downtown_lon, park_lon, res_lon])
    all_temp = np.concatenate([downtown_temp, park_temp, res_temp])

    fig3 = go.Figure(go.Densitymapbox(
        lat=all_lat,
        lon=all_lon,
        z=all_temp,
        radius=10,
        colorscale='RdYlBu_r',
        colorbar=dict(title="Temperature (°F)")
    ))

    fig3.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=10
        ),
        title="Urban Heat Island Effect - Temperature Distribution"
    )
    plots.append(('geo_heatmap', fig3, {
        'appearance': {'title': {'text': 'Urban Heat Map'}}
    }))

    # 4. Line Geo - Flight Routes
    # Major flight routes
    routes = [
        {'origin': 'New York', 'dest': 'London', 'o_lat': 40.71, 'o_lon': -74.01,
         'd_lat': 51.51, 'd_lon': -0.13, 'flights': 150},
        {'origin': 'Los Angeles', 'dest': 'Tokyo', 'o_lat': 34.05, 'o_lon': -118.24,
         'd_lat': 35.68, 'd_lon': 139.69, 'flights': 80},
        {'origin': 'Dubai', 'dest': 'London', 'o_lat': 25.25, 'o_lon': 55.36,
         'd_lat': 51.51, 'd_lon': -0.13, 'flights': 120},
        {'origin': 'Singapore', 'dest': 'Sydney', 'o_lat': 1.35, 'o_lon': 103.82,
         'd_lat': -33.87, 'd_lon': 151.21, 'flights': 100},
        {'origin': 'Paris', 'dest': 'New York', 'o_lat': 48.86, 'o_lon': 2.35,
         'd_lat': 40.71, 'd_lon': -74.01, 'flights': 130}
    ]

    fig4 = go.Figure()

    for route in routes:
        fig4.add_trace(go.Scattergeo(
            lon=[route['o_lon'], route['d_lon']],
            lat=[route['o_lat'], route['d_lat']],
            mode='lines+markers',
            line=dict(width=route['flights']/30, color='red'),
            marker=dict(size=10, color='blue'),
            text=[route['origin'], route['dest']],
            textposition='top center',
            name=f"{route['origin']} - {route['dest']}"
        ))

    fig4.update_layout(
        title='International Flight Routes',
        showlegend=False,
        geo=dict(
            projection_type='orthographic',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
            showocean=True,
            oceancolor='rgb(230, 230, 250)'
        )
    )
    plots.append(('geo_routes', fig4, {
        'appearance': {'title': {'text': 'Flight Routes'}}
    }))

    # 5. Scatter Mapbox - Earthquake Events
    # Simulate earthquake data
    n_quakes = 100
    quake_lat = np.random.uniform(30, 50, n_quakes)  # Pacific Ring of Fire region
    quake_lon = np.random.uniform(130, 170, n_quakes)
    magnitude = np.random.exponential(1, n_quakes) + 3  # Magnitude 3-8
    magnitude = np.clip(magnitude, 3, 8)
    depth = np.random.exponential(20, n_quakes)

    fig5 = go.Figure(go.Scattermapbox(
        lat=quake_lat,
        lon=quake_lon,
        mode='markers',
        marker=dict(
            size=magnitude * 3,
            color=depth,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Depth (km)"),
            opacity=0.7
        ),
        text=[f"Magnitude: {m:.1f}<br>Depth: {d:.1f} km"
              for m, d in zip(magnitude, depth)],
        hovertemplate='%{text}<extra></extra>'
    ))

    fig5.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=40, lon=150),
            zoom=2
        ),
        title="Earthquake Activity - Pacific Region"
    )
    plots.append(('geo_earthquakes', fig5, {
        'appearance': {'title': {'text': 'Earthquake Map'}}
    }))

    # 6. Polar Bar - Wind Direction Distribution
    # Wind data for a location
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    wind_freq = [5, 3, 8, 12, 15, 10, 6, 4, 3, 5, 8, 12, 18, 15, 10, 8]
    theta = np.linspace(0, 360, len(directions), endpoint=False)

    fig6 = go.Figure()

    fig6.add_trace(go.Barpolar(
        r=wind_freq,
        theta=theta,
        width=360/len(directions),
        text=directions,
        name='Wind Frequency',
        marker=dict(
            color=wind_freq,
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Frequency (%)")
        )
    ))

    fig6.update_layout(
        title="Wind Direction Distribution - Annual",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(wind_freq)]
            ),
            angularaxis=dict(
                tickmode='array',
                tickvals=theta,
                ticktext=directions
            )
        )
    )
    plots.append(('geo_wind', fig6, {
        'appearance': {'title': {'text': 'Wind Distribution'}}
    }))

    # 7. Isosurface - Underground Water Table
    # 3D visualization of water table depth
    x = np.linspace(0, 10, 20)
    y = np.linspace(0, 10, 20)
    z = np.linspace(-5, 0, 10)
    X, Y, Z = np.meshgrid(x, y, z)

    # Water saturation (higher values = more water)
    values = 100 * np.exp(-((X-5)**2 + (Y-5)**2 + (Z+2.5)**2) / 10)

    fig7 = go.Figure(data=go.Isosurface(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=values.flatten(),
        isomin=10,
        isomax=50,
        surface_count=5,
        colorscale='Blues',
        caps=dict(x=dict(show=False), y=dict(show=False)),
        colorbar=dict(title="Water Saturation (%)")
    ))

    fig7.update_layout(
        title="Underground Water Table - 3D Visualization",
        scene=dict(
            xaxis_title="Distance East (km)",
            yaxis_title="Distance North (km)",
            zaxis_title="Depth (m)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        )
    )
    plots.append(('geo_water_3d', fig7, {
        'appearance': {'title': {'text': 'Water Table 3D'}}
    }))

    # 8. Bubble Map - Resource Distribution
    # Oil/gas fields with production data
    fields = ['Ghawar', 'Burgan', 'Safaniya', 'Rumaila', 'West Qurna',
              'Tengiz', 'Ahvaz', 'Kirkuk', 'Marun', 'Gachsaran']
    field_lat = [25.5, 28.7, 28.2, 30.3, 30.7,
                 46.3, 31.3, 35.5, 30.2, 30.3]
    field_lon = [49.5, 47.8, 48.7, 47.4, 47.6,
                 53.1, 49.0, 44.4, 50.2, 50.4]
    production = [5.0, 1.7, 1.2, 1.5, 1.8,
                  0.7, 0.6, 0.9, 0.5, 0.6]  # Million barrels/day
    reserves = [75, 72, 37, 17, 43,
                26, 37, 9, 22, 28]  # Billion barrels

    fig8 = go.Figure()

    fig8.add_trace(go.Scattergeo(
        lon=field_lon,
        lat=field_lat,
        text=[f"{f}<br>Production: {p} Mb/d<br>Reserves: {r} Gb"
              for f, p, r in zip(fields, production, reserves)],
        mode='markers',
        marker=dict(
            size=[r*0.8 for r in reserves],
            color=production,
            colorscale='YlOrRd',
            showscale=True,
            colorbar=dict(title="Production<br>(Mb/day)"),
            line=dict(width=1, color='white')
        ),
        name='Oil Fields'
    ))

    fig8.update_layout(
        title='Major Oil Fields - Production and Reserves',
        geo=dict(
            resolution=50,
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
            projection=dict(type='mercator'),
            showcountries=True,
            countrycolor='rgb(204, 204, 204)',
            lonaxis=dict(range=[40, 60]),
            lataxis=dict(range=[20, 50])
        )
    )
    plots.append(('geo_resources', fig8, {
        'appearance': {'title': {'text': 'Resource Distribution'}}
    }))

    # Register all plots
    for plot_id, fig, metadata in plots:
        register_plot(fig, plot_id=plot_id, metadata=metadata)

    return f"Created {len(plots)} geospatial data visualizations"

# Execute when imported or run
if __name__ == "__main__" or True:
    result = create_geospatial_plots()
    print(result)