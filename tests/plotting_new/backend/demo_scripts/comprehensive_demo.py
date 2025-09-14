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
                values=features_normalized[:, 0]
            ),
            dict(
                range=[0, 1],
                label='Quality',
                values=features_normalized[:, 1]
            ),
            dict(
                range=[0, 1],
                label='Satisfaction',
                values=features_normalized[:, 2]
            ),
            dict(
                range=[0, 1],
                label='Sales Volume',
                values=features_normalized[:, 3]
            ),
            dict(
                range=[0, 1],
                label='Return Rate',
                values=features_normalized[:, 4]
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

# 8. FILLED AREA PLOT - Showing area between curves
print("[STATUS:info] Creating filled area plot...")

# Generate data for area plot
np.random.seed(42)
x = np.linspace(0, 10, 100)

# Create base signal
base_signal = np.sin(x) + 0.5 * np.sin(3 * x)

# Create upper and lower bounds (confidence interval style)
confidence_band = 0.3 + 0.2 * np.sin(2 * x)
upper_bound = base_signal + confidence_band
lower_bound = base_signal - confidence_band

# Create another pair of curves for comparison
comparison_signal = np.cos(x) + 0.3 * np.cos(4 * x) - 0.5
comparison_upper = comparison_signal + 0.2
comparison_lower = comparison_signal - 0.2

# Create the filled area plot
fig_area = go.Figure()

# Add the main confidence band (blue)
fig_area.add_trace(go.Scatter(
    x=x,
    y=upper_bound,
    mode='lines',
    name='Upper Bound',
    line=dict(color='rgba(31, 119, 180, 0.3)', width=1),
    showlegend=False
))

fig_area.add_trace(go.Scatter(
    x=x,
    y=lower_bound,
    mode='lines',
    name='Lower Bound',
    line=dict(color='rgba(31, 119, 180, 0.3)', width=1),
    fill='tonexty',
    fillcolor='rgba(31, 119, 180, 0.2)',
    showlegend=False
))

# Add the main signal line
fig_area.add_trace(go.Scatter(
    x=x,
    y=base_signal,
    mode='lines',
    name='Primary Signal',
    line=dict(color='rgb(31, 119, 180)', width=2)
))

# Add comparison band (orange)
fig_area.add_trace(go.Scatter(
    x=x,
    y=comparison_upper,
    mode='lines',
    name='Comparison Upper',
    line=dict(color='rgba(255, 127, 14, 0.3)', width=1),
    showlegend=False
))

fig_area.add_trace(go.Scatter(
    x=x,
    y=comparison_lower,
    mode='lines',
    name='Comparison Lower',
    line=dict(color='rgba(255, 127, 14, 0.3)', width=1),
    fill='tonexty',
    fillcolor='rgba(255, 127, 14, 0.2)',
    showlegend=False
))

# Add the comparison signal line
fig_area.add_trace(go.Scatter(
    x=x,
    y=comparison_signal,
    mode='lines',
    name='Comparison Signal',
    line=dict(color='rgb(255, 127, 14)', width=2)
))

# Add areas where primary > comparison (green fill)
mask_positive = base_signal > comparison_signal
x_positive = x[mask_positive]

if len(x_positive) > 0:
    # For each continuous segment where primary > comparison
    segments = []
    start_idx = None
    
    for i, is_positive in enumerate(mask_positive):
        if is_positive and start_idx is None:
            start_idx = i
        elif not is_positive and start_idx is not None:
            segments.append((start_idx, i))
            start_idx = None
    if start_idx is not None:
        segments.append((start_idx, len(mask_positive)))
    
    for seg_start, seg_end in segments:
        x_seg = x[seg_start:seg_end]
        y1_seg = base_signal[seg_start:seg_end]
        y2_seg = comparison_signal[seg_start:seg_end]
        
        fig_area.add_trace(go.Scatter(
            x=np.concatenate([x_seg, x_seg[::-1]]),
            y=np.concatenate([y1_seg, y2_seg[::-1]]),
            fill='toself',
            fillcolor='rgba(44, 160, 44, 0.15)',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

# Add areas where comparison > primary (red fill)
mask_negative = comparison_signal > base_signal
if mask_negative.any():
    segments = []
    start_idx = None
    
    for i, is_negative in enumerate(mask_negative):
        if is_negative and start_idx is None:
            start_idx = i
        elif not is_negative and start_idx is not None:
            segments.append((start_idx, i))
            start_idx = None
    if start_idx is not None:
        segments.append((start_idx, len(mask_negative)))
    
    for seg_start, seg_end in segments:
        x_seg = x[seg_start:seg_end]
        y1_seg = comparison_signal[seg_start:seg_end]
        y2_seg = base_signal[seg_start:seg_end]
        
        fig_area.add_trace(go.Scatter(
            x=np.concatenate([x_seg, x_seg[::-1]]),
            y=np.concatenate([y1_seg, y2_seg[::-1]]),
            fill='toself',
            fillcolor='rgba(214, 39, 40, 0.15)',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

# Add zero line for reference
fig_area.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)

fig_area.update_layout(
    title='Signal Analysis with Confidence Bands and Difference Areas',
    xaxis=dict(
        title='Time',
        showgrid=True,
        gridcolor='lightgray'
    ),
    yaxis=dict(
        title='Amplitude',
        showgrid=True,
        gridcolor='lightgray',
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor='gray'
    ),
    template='plotly_white',
    hovermode='x unified',
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ),
    annotations=[
        dict(
            x=2.5,
            y=1.8,
            text="Primary > Comparison",
            showarrow=False,
            font=dict(size=10, color='green'),
            opacity=0.7
        ),
        dict(
            x=7.5,
            y=-1.8,
            text="Comparison > Primary",
            showarrow=False,
            font=dict(size=10, color='red'),
            opacity=0.7
        )
    ]
)

register_plot(fig_area, plot_id='filled_area',
              metadata={'title': 'Filled Area Plot',
                       'description': 'Signal comparison with confidence bands and difference highlighting'})

# 9. FUNNEL PLOT - Sales/Conversion Pipeline
print("[STATUS:info] Creating funnel plot...")

# Create data for funnel plot
stages = ['Website Visits', 'Sign-ups', 'Trial Users', 'Paid Customers', 'Premium Users']
values = [15000, 7500, 3200, 1800, 450]
conversion_rates = [f"{(values[i+1]/values[i]*100):.1f}%" for i in range(len(values)-1)]

# Create the funnel plot
fig_funnel = go.Figure(go.Funnel(
    y=stages,
    x=values,
    textposition="inside",
    textinfo="value+percent initial",
    opacity=0.85,
    marker=dict(
        color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6'],
        line=dict(width=2, color='white')
    ),
    connector=dict(
        line=dict(color='gray', dash='dot', width=2)
    )
))

# Add annotations for conversion rates
annotations = []
for i, rate in enumerate(conversion_rates):
    annotations.append(
        dict(
            x=1.15,  # Position to the right of the funnel
            y=i + 0.5,  # Between stages
            text=f"→ {rate}",
            showarrow=False,
            font=dict(size=11, color='gray'),
            xref='paper',
            yref='y'
        )
    )

fig_funnel.update_layout(
    title='Sales Funnel Analysis',
    template='plotly_white',
    showlegend=False,
    annotations=annotations,
    margin=dict(l=120, r=100, t=60, b=60),
    yaxis=dict(
        showticklabels=True,
        side='left'
    )
)

register_plot(fig_funnel, plot_id='funnel',
              metadata={'title': 'Funnel Plot',
                       'description': 'Sales pipeline conversion analysis'})

# 10. HORIZONTAL BAR CHART - Performance Metrics
print("[STATUS:info] Creating horizontal bar chart...")

# Create data for horizontal bar chart
np.random.seed(42)
departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'R&D', 'Customer Support']
performance_scores = np.random.uniform(65, 95, len(departments))
sorted_indices = np.argsort(performance_scores)
departments_sorted = [departments[i] for i in sorted_indices]
scores_sorted = performance_scores[sorted_indices]

# Define colors based on performance thresholds
colors = ['#e74c3c' if score < 70 else '#f39c12' if score < 80 else '#2ecc71' for score in scores_sorted]

# Create horizontal bar chart
fig_hbar = go.Figure()

# Add the bars
fig_hbar.add_trace(go.Bar(
    x=scores_sorted,
    y=departments_sorted,
    orientation='h',
    marker=dict(
        color=colors,
        line=dict(color='rgba(50, 50, 50, 0.2)', width=1)
    ),
    text=[f'{score:.1f}%' for score in scores_sorted],
    textposition='outside',
    textfont=dict(size=10),
    name='Performance Score',
    hovertemplate='<b>%{y}</b><br>Performance: %{x:.1f}%<extra></extra>'
))

# Add threshold lines
fig_hbar.add_vline(x=70, line_dash="dash", line_color="red", opacity=0.3,
                   annotation_text="Min Acceptable", annotation_position="top")
fig_hbar.add_vline(x=80, line_dash="dash", line_color="orange", opacity=0.3,
                   annotation_text="Target", annotation_position="top")
fig_hbar.add_vline(x=90, line_dash="dash", line_color="green", opacity=0.3,
                   annotation_text="Excellent", annotation_position="top")

# Update layout
fig_hbar.update_layout(
    title='Department Performance Dashboard',
    xaxis=dict(
        title='Performance Score (%)',
        range=[0, 105],
        showgrid=True,
        gridcolor='lightgray',
        dtick=10
    ),
    yaxis=dict(
        title='',
        showgrid=False,
        automargin=True
    ),
    template='plotly_white',
    showlegend=False,
    height=None,  # Use container height
    margin=dict(l=150, r=80, t=60, b=60),
    bargap=0.2
)

register_plot(fig_hbar, plot_id='horizontal_bar',
              metadata={'title': 'Horizontal Bar Chart',
                       'description': 'Department performance metrics with thresholds'})

print("[STATUS:success] Demo plots generated successfully!")
print(f"[STATUS:info] Total plots created: 10")