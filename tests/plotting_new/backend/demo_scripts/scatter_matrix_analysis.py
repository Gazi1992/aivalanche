"""
Demo Script: Scatter Matrix and Parallel Coordinates Analysis
Advanced multi-dimensional data visualization and pattern discovery
"""

# Load scatter matrix data
df = load_data('scatter_matrix_data.csv')
print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Basic statistics for numerical columns
data_cols = ['A', 'B', 'C', 'D']
print("\n=== Data Statistics ===")
print(df[data_cols].describe())

# Check PassFail distribution
pass_fail_counts = df['PassFail'].value_counts()
print(f"\n=== Pass/Fail Distribution ===")
print(f"Pass: {pass_fail_counts.get(1, 0)} samples")
print(f"Fail: {pass_fail_counts.get(0, 0)} samples")

# Create scatter matrix with color coding
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Custom scatter matrix with Pass/Fail color coding
n_vars = len(data_cols)
fig = make_subplots(rows=n_vars, cols=n_vars,
                    subplot_titles=[f'{col1} vs {col2}' if i == 0 else ''
                                   for i in range(n_vars) 
                                   for col1 in data_cols 
                                   for col2 in data_cols][:n_vars*n_vars],
                    horizontal_spacing=0.02,
                    vertical_spacing=0.02)

# Color map for pass/fail
colors = df['PassFail'].map({0: 'red', 1: 'green'})

for i, col1 in enumerate(data_cols):
    for j, col2 in enumerate(data_cols):
        if i == j:
            # Diagonal: histograms
            for pf_val, color in [(0, 'red'), (1, 'green')]:
                df_subset = df[df['PassFail'] == pf_val]
                fig.add_trace(
                    go.Histogram(x=df_subset[col1], 
                               marker_color=color,
                               opacity=0.5,
                               showlegend=False,
                               nbinsx=20),
                    row=i+1, col=j+1
                )
        else:
            # Off-diagonal: scatter plots
            for pf_val, color, name in [(0, 'red', 'Fail'), (1, 'green', 'Pass')]:
                df_subset = df[df['PassFail'] == pf_val]
                fig.add_trace(
                    go.Scatter(x=df_subset[col2], y=df_subset[col1],
                             mode='markers',
                             marker=dict(size=4, color=color, opacity=0.6),
                             showlegend=(i == 0 and j == 1),
                             name=name),
                    row=i+1, col=j+1
                )

# Update axes labels
for i, col in enumerate(data_cols):
    fig.update_xaxes(title_text=col, row=n_vars, col=i+1)
    fig.update_yaxes(title_text=col, row=i+1, col=1)

fig.update_layout(title='Scatter Matrix: Multi-dimensional Analysis',
                 height=800, width=800,
                 showlegend=True)
register_plot(fig, plot_id='scatter_matrix_custom',
              metadata={'dimensions': len(data_cols), 'samples': len(df)})

# Parallel coordinates plot
fig_parallel = go.Figure(data=
    go.Parcoords(
        line=dict(color=df['PassFail'],
                 colorscale=[[0, 'red'], [1, 'green']],
                 showscale=True,
                 cmin=0,
                 cmax=1,
                 colorbar=dict(
                     title='Pass/Fail',
                     tickvals=[0, 1],
                     ticktext=['Fail', 'Pass']
                 )),
        dimensions=[dict(range=[df[col].min(), df[col].max()],
                        label=col,
                        values=df[col])
                   for col in data_cols]
    )
)

fig_parallel.update_layout(
    title='Parallel Coordinates: Pattern Detection',
    height=500
)
register_plot(fig_parallel, plot_id='parallel_coords',
              metadata={'interactive': True, 'dimensions': len(data_cols)})

# Correlation analysis
print("\n=== Correlation Matrix ===")
corr_matrix = df[data_cols].corr()
print(corr_matrix)

# Heatmap for correlations
fig_heatmap = go.Figure(data=go.Heatmap(
    z=corr_matrix.values,
    x=corr_matrix.columns,
    y=corr_matrix.columns,
    colorscale='RdBu',
    zmid=0,
    text=np.round(corr_matrix.values, 2),
    texttemplate='%{text}',
    colorbar=dict(title='Correlation')
))

fig_heatmap.update_layout(
    title='Feature Correlation Heatmap',
    width=500,
    height=500
)
register_plot(fig_heatmap, plot_id='correlation_heatmap')

# Pass/Fail analysis by feature
print("\n=== Pass/Fail Feature Analysis ===")
for col in data_cols:
    pass_mean = df[df['PassFail'] == 1][col].mean()
    fail_mean = df[df['PassFail'] == 0][col].mean()
    diff_pct = ((pass_mean - fail_mean) / fail_mean) * 100 if fail_mean != 0 else 0
    print(f"{col}: Pass avg={pass_mean:.2f}, Fail avg={fail_mean:.2f}, Diff={diff_pct:+.1f}%")

# Box plots for each feature by Pass/Fail
fig_box = make_subplots(rows=1, cols=len(data_cols),
                        subplot_titles=data_cols)

for i, col in enumerate(data_cols):
    for pf_val, color, name in [(0, 'red', 'Fail'), (1, 'green', 'Pass')]:
        df_subset = df[df['PassFail'] == pf_val]
        fig_box.add_trace(
            go.Box(y=df_subset[col],
                  name=name,
                  marker_color=color,
                  showlegend=(i == 0)),
            row=1, col=i+1
        )

fig_box.update_layout(
    title='Feature Distributions by Pass/Fail Status',
    height=400,
    showlegend=True
)
register_plot(fig_box, plot_id='feature_boxplots')

# PCA for dimensionality reduction
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[data_cols])

# Apply PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Create PCA visualization
fig_pca = go.Figure()
for pf_val, color, name in [(0, 'red', 'Fail'), (1, 'green', 'Pass')]:
    mask = df['PassFail'] == pf_val
    fig_pca.add_trace(go.Scatter(
        x=X_pca[mask, 0],
        y=X_pca[mask, 1],
        mode='markers',
        marker=dict(size=8, color=color, opacity=0.7),
        name=name
    ))

fig_pca.update_layout(
    title=f'PCA Visualization (Explained Variance: {pca.explained_variance_ratio_.sum():.1%})',
    xaxis_title=f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)',
    yaxis_title=f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)',
    template='plotly_white'
)
register_plot(fig_pca, plot_id='pca_visualization',
              metadata={'variance_explained': pca.explained_variance_ratio_.tolist()})

print(f"\n=== PCA Results ===")
print(f"PC1 explains {pca.explained_variance_ratio_[0]:.1%} of variance")
print(f"PC2 explains {pca.explained_variance_ratio_[1]:.1%} of variance")
print(f"Total variance explained: {pca.explained_variance_ratio_.sum():.1%}")

# Feature importance based on PCA components
print("\n=== Feature Importance (PCA) ===")
feature_importance = pd.DataFrame(
    pca.components_.T,
    columns=['PC1', 'PC2'],
    index=data_cols
)
print(feature_importance)

print(f"\n=== Analysis Summary ===")
print(f"✓ Analyzed {len(df)} samples with {len(data_cols)} features")
print(f"✓ Created scatter matrix and parallel coordinates")
print(f"✓ Performed PCA dimensionality reduction")
print(f"✓ Generated {len(datasets)} interactive visualizations")