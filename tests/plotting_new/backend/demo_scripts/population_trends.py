"""
Demo Script: Population and Economic Trends Analysis
Multi-bar charts, stacked visualizations, and trend analysis
"""

# Load multiple related datasets
df_multi = load_data('multi_bar_data.csv')
df_stacked = load_data('stacked_bar_data.csv')
df_multi_stacked = load_data('multi_stacked_bar_data.csv')

print("=== Loaded Datasets ===")
print(f"Multi-year data: {df_multi.shape}")
print(f"Gender data: {df_stacked.shape}")
print(f"Population & GDP data: {df_multi_stacked.shape}")

# Multi-year population trends
print("\n=== Multi-Year Population Analysis ===")
countries = df_multi['country'].values
years = ['year2021', 'year2022', 'year2023']

fig_trends = go.Figure()

colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
for i, year in enumerate(years):
    fig_trends.add_trace(go.Bar(
        x=countries,
        y=df_multi[year],
        name=year.replace('year', ''),
        marker_color=colors[i]
    ))

fig_trends.update_layout(
    title='Population Trends by Country (2021-2023)',
    xaxis_title='Country',
    yaxis_title='Population (millions)',
    barmode='group',
    hovermode='x unified'
)
register_plot(fig_trends, plot_id='population_trends')

# Calculate growth rates
df_multi['growth_21_22'] = ((df_multi['year2022'] - df_multi['year2021']) / df_multi['year2021']) * 100
df_multi['growth_22_23'] = ((df_multi['year2023'] - df_multi['year2022']) / df_multi['year2022']) * 100
df_multi['avg_growth'] = (df_multi['growth_21_22'] + df_multi['growth_22_23']) / 2

print("\n=== Growth Rate Analysis ===")
print(df_multi[['country', 'avg_growth']].sort_values('avg_growth', ascending=False))

# Visualize growth rates
fig_growth = go.Figure()
fig_growth.add_trace(go.Bar(
    x=df_multi['country'],
    y=df_multi['avg_growth'],
    marker_color=df_multi['avg_growth'],
    marker_colorscale='RdYlGn',
    marker_cmid=0,
    text=[f'{g:.1f}%' for g in df_multi['avg_growth']],
    textposition='outside'
))

fig_growth.update_layout(
    title='Average Population Growth Rate (2021-2023)',
    xaxis_title='Country',
    yaxis_title='Growth Rate (%)',
    showlegend=False
)
register_plot(fig_growth, plot_id='growth_rates')

# Gender distribution analysis
print("\n=== Gender Distribution ===")
df_stacked['total'] = df_stacked['male'] + df_stacked['female']
df_stacked['male_pct'] = (df_stacked['male'] / df_stacked['total']) * 100
df_stacked['female_pct'] = (df_stacked['female'] / df_stacked['total']) * 100

fig_gender = go.Figure()
fig_gender.add_trace(go.Bar(
    x=df_stacked['country'],
    y=df_stacked['male'],
    name='Male',
    marker_color='#4A90E2'
))
fig_gender.add_trace(go.Bar(
    x=df_stacked['country'],
    y=df_stacked['female'],
    name='Female',
    marker_color='#E91E63'
))

fig_gender.update_layout(
    title='Population by Gender',
    xaxis_title='Country',
    yaxis_title='Population (millions)',
    barmode='stack',
    hovermode='x unified'
)
register_plot(fig_gender, plot_id='gender_distribution')

# Gender ratio analysis
fig_ratio = px.scatter(df_stacked, x='male_pct', y='country',
                      title='Male Population Percentage by Country',
                      labels={'male_pct': 'Male %', 'country': 'Country'},
                      color='male_pct',
                      color_continuous_scale='RdBu',
                      range_color=[45, 55],
                      size_max=15)

fig_ratio.add_vline(x=50, line_dash='dash', line_color='gray', opacity=0.5)
fig_ratio.update_traces(marker=dict(size=12))
register_plot(fig_ratio, plot_id='gender_ratio')

# Economic vs Population Analysis
print("\n=== Population & GDP Components ===")
df_eco = df_multi_stacked.copy()
df_eco['total_pop'] = df_eco['male'] + df_eco['female']
df_eco['total_gdp'] = df_eco['gdp_agri'] + df_eco['gdp_ind']

# Create subplots for population and GDP
fig_eco = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Population by Gender', 'GDP by Sector'),
    shared_xaxes=True,
    vertical_spacing=0.15
)

# Population subplot
fig_eco.add_trace(go.Bar(x=df_eco['country'], y=df_eco['male'],
                         name='Male Population', marker_color='#4A90E2',
                         showlegend=True), row=1, col=1)
fig_eco.add_trace(go.Bar(x=df_eco['country'], y=df_eco['female'],
                         name='Female Population', marker_color='#E91E63',
                         showlegend=True), row=1, col=1)

# GDP subplot
fig_eco.add_trace(go.Bar(x=df_eco['country'], y=df_eco['gdp_agri'],
                         name='GDP Agriculture', marker_color='#66BB6A',
                         showlegend=True), row=2, col=1)
fig_eco.add_trace(go.Bar(x=df_eco['country'], y=df_eco['gdp_ind'],
                         name='GDP Industry', marker_color='#FFA726',
                         showlegend=True), row=2, col=1)

fig_eco.update_layout(
    title='Population and Economic Analysis',
    height=600,
    barmode='stack',
    hovermode='x unified'
)
fig_eco.update_xaxes(title_text='Country', row=2, col=1)
fig_eco.update_yaxes(title_text='Population (M)', row=1, col=1)
fig_eco.update_yaxes(title_text='GDP (B$)', row=2, col=1)

register_plot(fig_eco, plot_id='population_economy',
              metadata={'analysis': 'comparative', 'datasets': 2})

# Correlation between population and GDP
if len(df_eco) > 2:
    correlation = df_eco['total_pop'].corr(df_eco['total_gdp'])
    
    fig_corr = px.scatter(df_eco, x='total_pop', y='total_gdp',
                         text='country',
                         title=f'Population vs GDP Correlation (r={correlation:.2f})',
                         labels={'total_pop': 'Total Population (millions)',
                                'total_gdp': 'Total GDP (billions)'},
                         trendline='ols')
    
    fig_corr.update_traces(textposition='top center',
                          marker=dict(size=12, color='#9C27B0'))
    register_plot(fig_corr, plot_id='pop_gdp_correlation')
    
    print(f"\n=== Economic Insights ===")
    print(f"Population-GDP Correlation: {correlation:.3f}")
    
    # GDP per capita
    df_eco['gdp_per_capita'] = (df_eco['total_gdp'] * 1000) / df_eco['total_pop']
    print("\nGDP per capita (thousands):")
    print(df_eco[['country', 'gdp_per_capita']].sort_values('gdp_per_capita', ascending=False))

print(f"\n=== Analysis Complete ===")
print(f"✓ Analyzed {len(countries)} countries")
print(f"✓ Tracked 3 years of population data")
print(f"✓ Compared population and economic indicators")
print(f"✓ Generated {len(datasets)} comprehensive visualizations")