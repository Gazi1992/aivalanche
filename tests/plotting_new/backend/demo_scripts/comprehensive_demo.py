"""
Comprehensive Demo Script - Showcasing Various Plot Types
This script demonstrates scatter, bar, heatmap, and scatter matrix plots
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

# Generate synthetic datasets for demonstration
np.random.seed(42)

# 1. SCATTER PLOT - Scientific Data
print("[STATUS:info] Creating scatter plot with scientific data...")
n_points = 500
x_scatter = np.linspace(0, 10, n_points)
y_scatter = 2 * np.sin(x_scatter) + np.random.normal(0, 0.3, n_points)
y_fitted = 2 * np.sin(x_scatter)

fig_scatter = go.Figure()
fig_scatter.add_trace(go.Scatter(
    x=x_scatter,
    y=y_scatter,
    mode='markers',
    name='Experimental Data',
    marker=dict(
        size=4,
        color=y_scatter,
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title='Value'),
        opacity=0.7
    )
))
fig_scatter.add_trace(go.Scatter(
    x=x_scatter,
    y=y_fitted,
    mode='lines',
    name='Theoretical Model',
    line=dict(color='red', width=2, dash='dash')
))
fig_scatter.update_layout(
    title='Scientific Data: Experimental vs Theoretical Model',
    xaxis_title='Time (seconds)',
    yaxis_title='Signal Amplitude',
    hovermode='x unified',
    template='plotly_white'
)
register_plot(fig_scatter, plot_id='scatter_scientific', 
              metadata={'title': 'Scatter Plot with Fitted Model', 
                       'description': 'Comparison of experimental measurements with theoretical predictions'})

# 2. BAR CHART - Categorical Data
print("[STATUS:info] Creating bar chart with categorical data...")
categories = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
quarters = ['Q1', 'Q2', 'Q3', 'Q4']

# Generate sales data for each quarter
np.random.seed(42)
sales_data = {}
for quarter in quarters:
    sales_data[quarter] = np.random.randint(50, 200, size=len(categories))

fig_bar = go.Figure()

# Add bars for each quarter
colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA']
for i, quarter in enumerate(quarters):
    fig_bar.add_trace(go.Bar(
        name=quarter,
        x=categories,
        y=sales_data[quarter],
        marker_color=colors[i],
        text=sales_data[quarter],
        textposition='auto'
    ))

fig_bar.update_layout(
    title='Quarterly Sales by Product Category',
    xaxis_title='Product Category',
    yaxis_title='Sales (in thousands)',
    barmode='group',
    hovermode='x unified',
    template='plotly_white',
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

register_plot(fig_bar, plot_id='bar_categorical',
              metadata={'title': 'Bar Chart with Categories',
                       'description': 'Quarterly sales comparison across product categories'})

# 3. HEATMAP - Both axes categorical
print("[STATUS:info] Creating heatmap with categorical axes...")
# Categories for both axes
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
hours = ['Morning', 'Afternoon', 'Evening', 'Night']

# Generate activity data (e.g., website traffic)
np.random.seed(42)
activity_data = np.random.randint(10, 100, size=(len(hours), len(days)))

# Create heatmap
fig_heatmap = go.Figure(data=go.Heatmap(
    z=activity_data,
    x=days,
    y=hours,
    colorscale='Viridis',
    text=activity_data,
    texttemplate='%{text}',
    textfont={"size": 10},
    colorbar=dict(title='Activity Level')
))

fig_heatmap.update_layout(
    title='Weekly Activity Heatmap',
    xaxis_title='Day of Week',
    yaxis_title='Time of Day',
    xaxis=dict(type='category'),
    yaxis=dict(type='category'),
    template='plotly_white'
)

register_plot(fig_heatmap, plot_id='heatmap_categorical',
              metadata={'title': 'Activity Heatmap',
                       'description': 'Weekly activity patterns with categorical axes',
                       'appearance': {
                           'legend': {
                               'visible': False
                           }
                       }})

# 4. SCATTER MATRIX - Multiple dimensions
print("[STATUS:info] Creating scatter matrix plot...")

# Generate multivariate data
np.random.seed(42)
n_samples = 200

# Create correlated features for interesting patterns
feature_1 = np.random.randn(n_samples)
feature_2 = 0.7 * feature_1 + 0.3 * np.random.randn(n_samples)
feature_3 = -0.5 * feature_1 + 0.5 * np.random.randn(n_samples)
feature_4 = np.random.randn(n_samples)

# Create categories for coloring
categories = np.random.choice(['Type A', 'Type B', 'Type C'], n_samples)

# Create DataFrame
df_scatter_matrix = pd.DataFrame({
    'Feature 1': feature_1,
    'Feature 2': feature_2,
    'Feature 3': feature_3,
    'Feature 4': feature_4,
    'Category': categories
})

# Create scatter matrix
fig_splom = go.Figure(data=go.Splom(
    dimensions=[
        dict(label='Feature 1', values=df_scatter_matrix['Feature 1']),
        dict(label='Feature 2', values=df_scatter_matrix['Feature 2']),
        dict(label='Feature 3', values=df_scatter_matrix['Feature 3']),
        dict(label='Feature 4', values=df_scatter_matrix['Feature 4'])
    ],
    text=df_scatter_matrix['Category'],
    marker=dict(
        color=pd.Categorical(df_scatter_matrix['Category']).codes,
        colorscale='Viridis',
        size=5,
        line=dict(width=0.5, color='white')
    ),
    showupperhalf=False,  # Only show lower triangle
    diagonal=dict(visible=False)  # Hide diagonal
))

fig_splom.update_layout(
    title='Feature Correlation Matrix',
    template='plotly_white',
    dragmode='select',
    hovermode='closest',
    showlegend=False,
    margin=dict(l=100, r=20, t=60, b=80)  # Increased margins for axis labels
)

# Explicitly update axis properties to show labels
fig_splom.update_xaxes(showticklabels=True)
fig_splom.update_yaxes(showticklabels=True)

register_plot(fig_splom, plot_id='scatter_matrix',
              metadata={'title': 'Scatter Matrix',
                       'description': 'Multi-dimensional feature correlation analysis',
                       'isSplom': True})

# 5. BUBBLE PLOT - Three dimensions of data
print("[STATUS:info] Creating bubble plot...")

# Generate data for bubble plot
np.random.seed(42)
n_bubbles = 50

# Create data with correlations
gdp_per_capita = np.random.exponential(30000, n_bubbles) + 10000
life_expectancy = 60 + np.sqrt(gdp_per_capita / 1000) + np.random.normal(0, 3, n_bubbles)
population = np.random.exponential(20, n_bubbles) * 1e6
countries = [f"Country_{i}" for i in range(n_bubbles)]

# Create bubble plot
fig_bubble = go.Figure()

# Add bubble trace
fig_bubble.add_trace(go.Scatter(
    x=gdp_per_capita,
    y=life_expectancy,
    mode='markers',
    marker=dict(
        size=np.sqrt(population / 1e6) * 3,  # Scale population for bubble size
        color=np.log10(population),  # Color by population (log scale)
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(
            title='Population<br>(log10)',
            thickness=20
        ),
        line=dict(width=0.5, color='white'),
        sizemode='diameter',
        opacity=0.7
    ),
    text=[f"{countries[i]}<br>GDP: ${gdp_per_capita[i]:,.0f}<br>Life Exp: {life_expectancy[i]:.1f}<br>Pop: {population[i]/1e6:.1f}M" 
          for i in range(n_bubbles)],
    hovertemplate='%{text}<extra></extra>'
))

fig_bubble.update_layout(
    title='Economic Indicators by Country (Bubble Plot)',
    xaxis=dict(
        title='GDP per Capita (USD)',
        type='log',
        gridcolor='lightgray'
    ),
    yaxis=dict(
        title='Life Expectancy (years)',
        gridcolor='lightgray'
    ),
    template='plotly_white',
    hovermode='closest',
    showlegend=False
)

register_plot(fig_bubble, plot_id='bubble_plot',
              metadata={'title': 'Bubble Plot',
                       'description': 'Multi-dimensional data visualization with bubble sizes'})

# 6. HISTOGRAM - Distribution visualization
print("[STATUS:info] Creating histogram...")

# Generate data for histogram
np.random.seed(42)
n_samples = 1000

# Create mixed distribution (bimodal)
dist1 = np.random.normal(100, 15, n_samples // 2)
dist2 = np.random.normal(130, 20, n_samples // 2)
combined_data = np.concatenate([dist1, dist2])

# Create histogram
fig_histogram = go.Figure()

# Add histogram trace
fig_histogram.add_trace(go.Histogram(
    x=combined_data,
    nbinsx=30,
    name='Measurement Distribution',
    marker=dict(
        color='rgba(100, 150, 250, 0.7)',
        line=dict(
            color='rgba(50, 100, 200, 1)',
            width=1
        )
    ),
    opacity=0.75,
    hovertemplate='Range: %{x}<br>Count: %{y}<extra></extra>'
))

# Add a normal distribution overlay
from scipy import stats
x_range = np.linspace(combined_data.min(), combined_data.max(), 100)
kde = stats.gaussian_kde(combined_data)
y_kde = kde(x_range) * len(combined_data) * (combined_data.max() - combined_data.min()) / 30

fig_histogram.add_trace(go.Scatter(
    x=x_range,
    y=y_kde,
    mode='lines',
    name='KDE',
    line=dict(color='red', width=2),
    hovertemplate='Value: %{x:.1f}<br>Density: %{y:.1f}<extra></extra>'
))

# Add mean line
mean_val = np.mean(combined_data)
fig_histogram.add_vline(
    x=mean_val,
    line_dash="dash",
    line_color="green",
    annotation_text=f"Mean: {mean_val:.1f}"
)

fig_histogram.update_layout(
    title='Bimodal Distribution Analysis',
    xaxis=dict(
        title='Measurement Value',
        showgrid=True,
        gridcolor='lightgray'
    ),
    yaxis=dict(
        title='Frequency',
        showgrid=True,
        gridcolor='lightgray'
    ),
    template='plotly_white',
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
    ),
    bargap=0.05
)

register_plot(fig_histogram, plot_id='histogram',
              metadata={'title': 'Histogram with KDE',
                       'description': 'Distribution analysis with kernel density estimation'})

# 7. PARALLEL COORDINATES PLOT - Multi-dimensional comparison
print("[STATUS:info] Creating parallel coordinates plot...")

# Generate data for parallel coordinates
np.random.seed(42)
n_items = 30

# Create data for different product categories
categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Sports']
category_labels = np.random.choice(categories, n_items)

# Create correlated features
price = np.random.uniform(10, 500, n_items)
quality = 70 + (price / 500) * 20 + np.random.normal(0, 5, n_items)
satisfaction = quality * 0.8 + np.random.normal(0, 5, n_items)
sales_volume = 100 - price/5 + quality/2 + np.random.normal(0, 10, n_items)
return_rate = 100 - quality + np.random.normal(0, 3, n_items)

# Normalize features to 0-1 range for better visualization
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
features = np.column_stack([price, quality, satisfaction, sales_volume, return_rate])
features_normalized = scaler.fit_transform(features)

# Create color mapping for categories
color_map = {cat: i for i, cat in enumerate(categories)}
colors = [color_map[cat] for cat in category_labels]

# Create parallel coordinates plot
fig_pcp = go.Figure(data=
    go.Parcoords(
        line=dict(
            color=colors,
            colorscale='Viridis',
            showscale=True,
            cmin=0,
            cmax=len(categories)-1,
            colorbar=dict(
                title='Category',
                tickmode='array',
                tickvals=list(range(len(categories))),
                ticktext=categories,
                thickness=20
            )
        ),
        labelside='bottom',  # Move labels to bottom
        dimensions=[
            dict(
                range=[0, 1],
                label='Price',
                values=features_normalized[:, 0],
                tickvals=[0, 0.25, 0.5, 0.75, 1],
                ticktext=['Low', '', 'Med', '', 'High']
            ),
            dict(
                range=[0, 1],
                label='Quality',
                values=features_normalized[:, 1],
                tickvals=[0, 0.5, 1],
                ticktext=['Poor', 'Average', 'Excellent']
            ),
            dict(
                range=[0, 1],
                label='Satisfaction',
                values=features_normalized[:, 2],
                tickvals=[0, 0.5, 1],
                ticktext=['Low', 'Medium', 'High']
            ),
            dict(
                range=[0, 1],
                label='Sales Volume',
                values=features_normalized[:, 3],
                tickvals=[0, 0.5, 1],
                ticktext=['Low', 'Medium', 'High']
            ),
            dict(
                range=[0, 1],
                label='Return Rate',
                values=features_normalized[:, 4],
                tickvals=[0, 0.5, 1],
                ticktext=['Low', 'Medium', 'High']
            )
        ]
    )
)

fig_pcp.update_layout(
    title='Product Analysis - Parallel Coordinates',
    template='plotly_white',
    height=None,  # Use default height from container
    margin=dict(l=80, r=80, t=60, b=60)  # Adjusted margins for bottom labels
)

register_plot(fig_pcp, plot_id='parallel_coordinates',
              metadata={'title': 'Parallel Coordinates Plot',
                       'description': 'Multi-dimensional product comparison across categories'})

print("[STATUS:success] Demo plots generated successfully!")
print(f"[STATUS:info] Total plots created: 7")