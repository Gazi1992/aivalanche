"""
Simple Demo Script with Status Updates
A streamlined demo that works with available data
"""

import time

# Status update helper
def status(message, type='info'):
    print(f"[STATUS:{type}] {message}")
    time.sleep(0.3)  # Small delay for visual effect

# Start analysis
status("Starting data analysis...")

# Load temperature data
status("Loading sensor data...")
df_temp = load_data('temperature_data.csv')
status(f"✓ Loaded {len(df_temp)} measurements", 'success')

# Basic statistics
status("Computing statistics...")
stats = df_temp[['sensor1', 'sensor2']].describe()
mean_temp1 = df_temp['sensor1'].mean()
mean_temp2 = df_temp['sensor2'].mean()
status(f"Sensor 1 avg: {mean_temp1:.1f}°C, Sensor 2 avg: {mean_temp2:.1f}°C", 'info')

# Create temperature comparison plot
status("Creating temperature visualization...")
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df_temp['time'], 
    y=df_temp['sensor1'],
    mode='lines',
    name='Sensor 1',
    line=dict(color='#FF6B35', width=2)
))
fig1.add_trace(go.Scatter(
    x=df_temp['time'], 
    y=df_temp['sensor2'],
    mode='lines',
    name='Sensor 2',
    line=dict(color='#4ECDC4', width=2)
))
fig1.update_layout(
    title='Temperature Sensors Over Time',
    xaxis_title='Time (s)',
    yaxis_title='Temperature (°C)',
    hovermode='x unified',
    template='plotly_white',
    height=500
)
register_plot(fig1, plot_id='temp_comparison', 
              metadata={'title': 'Dual Sensor Temperature Monitoring', 
                       'description': 'Real-time comparison of temperature readings from two sensors'})
status("✓ Temperature plot created", 'success')

# Outlier detection
status("Detecting anomalies...")
outliers = find_outliers(df_temp, 'sensor1', method='iqr')
outlier_count = len(outliers)

if outlier_count > 0:
    status(f"⚠ Found {outlier_count} anomalies", 'warning')
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_temp['time'], 
        y=df_temp['sensor1'],
        mode='lines',
        name='Normal',
        line=dict(color='#E0E0E0', width=1)
    ))
    fig2.add_trace(go.Scatter(
        x=outliers['time'], 
        y=outliers['sensor1'],
        mode='markers',
        name='Anomalies',
        marker=dict(color='#FF0000', size=12, symbol='x-thin-open', line=dict(width=2))
    ))
    fig2.update_layout(
        title='Anomaly Detection Results',
        xaxis_title='Time (s)',
        yaxis_title='Temperature (°C)',
        template='plotly_white',
        height=400
    )
    register_plot(fig2, plot_id='anomalies',
                  metadata={'title': 'Anomaly Detection',
                           'description': f'Detected {outlier_count} anomalous readings using IQR method'})
else:
    status("✓ No anomalies detected", 'success')

# Temperature distribution
status("Analyzing distributions...")
fig3 = go.Figure()
fig3.add_trace(go.Histogram(
    x=df_temp['sensor1'],
    name='Sensor 1',
    marker_color='#FF6B35',
    opacity=0.7,
    nbinsx=20
))
fig3.add_trace(go.Histogram(
    x=df_temp['sensor2'],
    name='Sensor 2',
    marker_color='#4ECDC4',
    opacity=0.7,
    nbinsx=20
))
fig3.update_layout(
    title='Temperature Distribution Analysis',
    xaxis_title='Temperature (°C)',
    yaxis_title='Frequency',
    barmode='overlay',
    template='plotly_white',
    height=400
)
register_plot(fig3, plot_id='distributions',
              metadata={'title': 'Temperature Distributions',
                       'description': 'Statistical distribution of temperature readings'})
status("✓ Distribution analysis complete", 'success')

# Correlation analysis
status("Computing correlations...")
correlation = df_temp[['sensor1', 'sensor2']].corr().iloc[0, 1]
status(f"Sensor correlation: {correlation:.3f}", 'info')

fig4 = px.scatter(df_temp, x='sensor1', y='sensor2',
                  title=f'Sensor Correlation (r={correlation:.3f})',
                  labels={'sensor1': 'Sensor 1 (°C)', 'sensor2': 'Sensor 2 (°C)'},
                  trendline='ols',
                  template='plotly_white',
                  height=450)
fig4.update_traces(marker=dict(size=10, color='#9C27B0', opacity=0.6))
register_plot(fig4, plot_id='correlation',
              metadata={'title': 'Sensor Correlation Analysis',
                       'description': f'Linear correlation coefficient: {correlation:.3f}'})
status("✓ Correlation analysis complete", 'success')

# Load population data
status("Loading demographic data...")
df_pop = load_data('multi_bar_data.csv')
status(f"✓ Loaded data for {len(df_pop)} countries", 'success')

# Population trends
status("Creating population visualization...")
fig5 = go.Figure()
years = ['2021', '2022', '2023']
colors = ['#3498db', '#2ecc71', '#e74c3c']

for i, (year, col) in enumerate(zip(years, ['year2021', 'year2022', 'year2023'])):
    fig5.add_trace(go.Bar(
        x=df_pop['country'],
        y=df_pop[col],
        name=year,
        marker_color=colors[i]
    ))

fig5.update_layout(
    title='Global Population Trends (2021-2023)',
    xaxis_title='Country',
    yaxis_title='Population (millions)',
    barmode='group',
    hovermode='x unified',
    template='plotly_white',
    height=500
)
register_plot(fig5, plot_id='population',
              metadata={'title': 'Population Trends',
                       'description': 'Multi-year population comparison across countries'})
status("✓ Population visualization complete", 'success')

# Growth analysis
status("Calculating growth rates...")
df_pop['growth'] = ((df_pop['year2023'] - df_pop['year2021']) / df_pop['year2021'] * 100).round(2)
avg_growth = df_pop['growth'].mean()
status(f"Average growth rate: {avg_growth:.1f}%", 'info')

fig6 = go.Figure()
fig6.add_trace(go.Bar(
    x=df_pop['country'],
    y=df_pop['growth'],
    marker=dict(
        color=df_pop['growth'],
        colorscale='RdYlGn',
        cmid=0,
        colorbar=dict(title='Growth %', thickness=15)
    ),
    text=[f'{g:.1f}%' for g in df_pop['growth']],
    textposition='outside'
))

fig6.update_layout(
    title='Population Growth Rates (2021-2023)',
    xaxis_title='Country',
    yaxis_title='Growth Rate (%)',
    template='plotly_white',
    showlegend=False,
    height=450
)
register_plot(fig6, plot_id='growth',
              metadata={'title': 'Growth Rate Analysis',
                       'description': f'Average global growth: {avg_growth:.1f}%'})
status("✓ Growth analysis complete", 'success')

# Summary
total_plots = 6
status(f"Analysis complete! Generated {total_plots} interactive visualizations", 'success')
status("All plots ready for exploration", 'success')