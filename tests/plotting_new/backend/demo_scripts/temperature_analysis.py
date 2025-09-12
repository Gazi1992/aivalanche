"""
Demo Script: Temperature Data Analysis
Shows basic plotting, statistics, and outlier detection
"""

# Load temperature data
df = load_data('temperature_data.csv')
print(f"Loaded temperature data: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Columns: {list(df.columns)}")

# Basic statistics
print("\n=== Temperature Statistics ===")
print(show_stats(df, ['sensor1', 'sensor2']))

# Create time series plot with both sensors
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['time'], y=df['sensor1'], 
                         mode='lines', name='Sensor 1',
                         line=dict(color='#FF5733', width=2)))
fig.add_trace(go.Scatter(x=df['time'], y=df['sensor2'], 
                         mode='lines', name='Sensor 2',
                         line=dict(color='#3366FF', width=2)))
fig.update_layout(title='Temperature Sensors Comparison',
                  xaxis_title='Time (s)',
                  yaxis_title='Temperature (°C)',
                  template='plotly_white')
register_plot(fig, plot_id='temp_comparison', 
              metadata={'description': 'Dual sensor temperature over time'})

# Find and visualize outliers for Sensor 1
print("\n=== Outlier Detection (Sensor 1) ===")
outliers = find_outliers(df, 'sensor1', method='iqr')
print(f"Found {len(outliers)} outliers using IQR method")

if len(outliers) > 0:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['time'], y=df['sensor1'],
                              mode='lines', name='Normal',
                              line=dict(color='lightgray')))
    fig2.add_trace(go.Scatter(x=outliers['time'], y=outliers['sensor1'],
                              mode='markers', name='Outliers',
                              marker=dict(color='red', size=10, symbol='x')))
    fig2.update_layout(title='Temperature Outliers - Sensor 1',
                       xaxis_title='Time (s)',
                       yaxis_title='Temperature (°C)')
    register_plot(fig2, plot_id='temp_outliers',
                  metadata={'outlier_count': len(outliers)})

# Distribution analysis
fig3 = px.histogram(df, x='sensor1', nbins=30, 
                    title='Temperature Distribution - Sensor 1')
fig3.update_traces(marker_color='#FF5733', marker_line_color='darkred',
                   marker_line_width=1)
register_plot(fig3, plot_id='temp_distribution')

# Correlation between sensors
correlation = df[['sensor1', 'sensor2']].corr().iloc[0, 1]
print(f"\n=== Correlation Analysis ===")
print(f"Correlation between Sensor 1 and Sensor 2: {correlation:.3f}")

fig4 = px.scatter(df, x='sensor1', y='sensor2', 
                  title=f'Sensor Correlation (r={correlation:.3f})',
                  labels={'sensor1': 'Sensor 1 (°C)', 'sensor2': 'Sensor 2 (°C)'})
fig4.update_traces(marker=dict(size=8, color='#3366FF', opacity=0.6))
register_plot(fig4, plot_id='sensor_correlation')

print(f"\n=== Summary ===")
print(f"✓ Created {len(datasets)} dataset(s)")
print(f"✓ Generated 4 interactive plots")
print(f"✓ Detected {len(outliers)} outliers")
print(f"✓ Correlation coefficient: {correlation:.3f}")