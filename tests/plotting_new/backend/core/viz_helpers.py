"""
Visualization Helper Functions

Collection of helper functions to simplify common data visualization tasks.
These functions are available in the Python execution environment.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Optional, Union, Tuple, Dict, Any
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def create_statistical_summary(df: pd.DataFrame, column: str) -> go.Figure:
    """Create a comprehensive statistical summary visualization for a column."""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            f'{column} Distribution',
            'Box Plot with Outliers',
            'Q-Q Plot',
            'Statistical Summary'
        ],
        specs=[
            [{'type': 'histogram'}, {'type': 'box'}],
            [{'type': 'scatter'}, {'type': 'table'}]
        ]
    )
    
    # Histogram
    fig.add_trace(
        go.Histogram(x=df[column], nbinsx=30, name='Distribution'),
        row=1, col=1
    )
    
    # Box plot
    fig.add_trace(
        go.Box(y=df[column], name=column, boxpoints='outliers'),
        row=1, col=2
    )
    
    # Q-Q plot
    theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(df[column])))
    sample_quantiles = np.sort(df[column].dropna())
    
    fig.add_trace(
        go.Scatter(x=theoretical_quantiles, y=sample_quantiles, mode='markers', name='Q-Q'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=[-3, 3], y=[-3, 3], mode='lines', line=dict(dash='dash'), name='Normal'),
        row=2, col=1
    )
    
    # Statistical summary table
    summary_stats = df[column].describe()
    stats_data = {
        'Statistic': ['Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max'],
        'Value': [
            f"{summary_stats['count']:.0f}",
            f"{summary_stats['mean']:.2f}",
            f"{summary_stats['std']:.2f}",
            f"{summary_stats['min']:.2f}",
            f"{summary_stats['25%']:.2f}",
            f"{summary_stats['50%']:.2f}",
            f"{summary_stats['75%']:.2f}",
            f"{summary_stats['max']:.2f}"
        ]
    }
    
    fig.add_trace(
        go.Table(
            header=dict(values=list(stats_data.keys())),
            cells=dict(values=list(stats_data.values()))
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text=f"Statistical Analysis of {column}",
        showlegend=False,
        height=800
    )
    
    return fig


def highlight_outliers(df: pd.DataFrame, x_col: str, y_col: str, 
                       method: str = 'iqr', threshold: float = 1.5) -> go.Figure:
    """Create a scatter plot with outliers highlighted."""
    
    # Detect outliers
    if method == 'iqr':
        Q1 = df[y_col].quantile(0.25)
        Q3 = df[y_col].quantile(0.75)
        IQR = Q3 - Q1
        outlier_mask = (df[y_col] < Q1 - threshold * IQR) | (df[y_col] > Q3 + threshold * IQR)
    elif method == 'zscore':
        z_scores = np.abs(stats.zscore(df[y_col].dropna()))
        outlier_mask = z_scores > threshold
    else:
        raise ValueError(f"Unknown outlier method: {method}")
    
    # Create figure
    fig = go.Figure()
    
    # Normal points
    normal_data = df[~outlier_mask]
    fig.add_trace(go.Scatter(
        x=normal_data[x_col],
        y=normal_data[y_col],
        mode='markers',
        name='Normal',
        marker=dict(color='blue', size=6)
    ))
    
    # Outliers
    outlier_data = df[outlier_mask]
    fig.add_trace(go.Scatter(
        x=outlier_data[x_col],
        y=outlier_data[y_col],
        mode='markers',
        name='Outliers',
        marker=dict(color='red', size=10, symbol='x')
    ))
    
    # Add mean and std bands
    mean_val = df[y_col].mean()
    std_val = df[y_col].std()
    
    fig.add_hline(y=mean_val, line_dash="dash", line_color="green", 
                  annotation_text=f"Mean: {mean_val:.2f}")
    fig.add_hrect(y0=mean_val-std_val, y1=mean_val+std_val,
                  fillcolor="green", opacity=0.1,
                  annotation_text="±1 STD", annotation_position="right")
    
    fig.update_layout(
        title=f"Outlier Detection ({method.upper()} method)",
        xaxis_title=x_col,
        yaxis_title=y_col
    )
    
    return fig


def create_correlation_heatmap(df: pd.DataFrame, columns: Optional[List[str]] = None) -> go.Figure:
    """Create an interactive correlation heatmap."""
    
    if columns is None:
        # Use all numeric columns
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    corr_matrix = df[columns].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Correlation Matrix",
        width=800,
        height=800
    )
    
    return fig


def create_time_series_with_trend(df: pd.DataFrame, time_col: str, 
                                  value_cols: Union[str, List[str]],
                                  add_trend: bool = True,
                                  add_rolling: bool = True,
                                  window: int = 10) -> go.Figure:
    """Create time series plot with optional trend and rolling average."""
    
    if isinstance(value_cols, str):
        value_cols = [value_cols]
    
    fig = go.Figure()
    
    for col in value_cols:
        # Main time series
        fig.add_trace(go.Scatter(
            x=df[time_col],
            y=df[col],
            mode='lines',
            name=col,
            opacity=0.7
        ))
        
        if add_rolling:
            # Rolling average
            rolling_mean = df[col].rolling(window=window, center=True).mean()
            fig.add_trace(go.Scatter(
                x=df[time_col],
                y=rolling_mean,
                mode='lines',
                name=f'{col} ({window}-pt avg)',
                line=dict(width=3)
            ))
        
        if add_trend:
            # Linear trend
            x_numeric = np.arange(len(df))
            z = np.polyfit(x_numeric, df[col].fillna(method='ffill'), 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=df[time_col],
                y=p(x_numeric),
                mode='lines',
                name=f'{col} trend',
                line=dict(dash='dash')
            ))
    
    fig.update_layout(
        title="Time Series Analysis",
        xaxis_title=time_col,
        yaxis_title="Value",
        hovermode='x unified'
    )
    
    return fig


def create_pca_visualization(df: pd.DataFrame, 
                            features: Optional[List[str]] = None,
                            color_by: Optional[str] = None,
                            n_components: int = 2) -> go.Figure:
    """Create PCA visualization of multi-dimensional data."""
    
    if features is None:
        features = df.select_dtypes(include=[np.number]).columns.tolist()
        if color_by and color_by in features:
            features.remove(color_by)
    
    # Standardize features
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[features].fillna(df[features].mean()))
    
    # Perform PCA
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(scaled_data)
    
    # Create visualization
    if n_components == 2:
        fig = px.scatter(
            x=pca_result[:, 0],
            y=pca_result[:, 1],
            color=df[color_by] if color_by else None,
            title=f"PCA Analysis (Explained Variance: {pca.explained_variance_ratio_.sum():.2%})",
            labels={'x': f'PC1 ({pca.explained_variance_ratio_[0]:.2%})',
                   'y': f'PC2 ({pca.explained_variance_ratio_[1]:.2%})'}
        )
    else:  # 3D
        fig = px.scatter_3d(
            x=pca_result[:, 0],
            y=pca_result[:, 1],
            z=pca_result[:, 2] if n_components >= 3 else 0,
            color=df[color_by] if color_by else None,
            title=f"PCA Analysis (Explained Variance: {pca.explained_variance_ratio_.sum():.2%})",
            labels={'x': f'PC1 ({pca.explained_variance_ratio_[0]:.2%})',
                   'y': f'PC2 ({pca.explained_variance_ratio_[1]:.2%})',
                   'z': f'PC3 ({pca.explained_variance_ratio_[2]:.2%})' if n_components >= 3 else 'PC3'}
        )
    
    # Add loadings as annotations
    if n_components == 2:
        loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
        for i, feature in enumerate(features):
            fig.add_annotation(
                ax=0, ay=0,
                axref="x", ayref="y",
                x=loadings[i, 0],
                y=loadings[i, 1],
                showarrow=True,
                arrowsize=2,
                arrowhead=2,
                text=feature,
                font=dict(size=10)
            )
    
    return fig


def create_distribution_comparison(df: pd.DataFrame, column: str, 
                                  group_by: str) -> go.Figure:
    """Compare distributions across different groups."""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=['Overlaid Histograms', 'Box Plots', 
                       'Violin Plots', 'KDE Plots'],
        specs=[[{'type': 'histogram'}, {'type': 'box'}],
               [{'type': 'violin'}, {'type': 'scatter'}]]
    )
    
    groups = df[group_by].unique()
    colors = px.colors.qualitative.Plotly
    
    for i, group in enumerate(groups):
        group_data = df[df[group_by] == group][column]
        color = colors[i % len(colors)]
        
        # Histogram
        fig.add_trace(
            go.Histogram(x=group_data, name=str(group), opacity=0.7,
                        marker_color=color, nbinsx=20),
            row=1, col=1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(y=group_data, name=str(group), marker_color=color),
            row=1, col=2
        )
        
        # Violin plot
        fig.add_trace(
            go.Violin(y=group_data, name=str(group), marker_color=color),
            row=2, col=1
        )
        
        # KDE approximation
        kde_x = np.linspace(group_data.min(), group_data.max(), 100)
        kde = stats.gaussian_kde(group_data.dropna())
        kde_y = kde(kde_x)
        
        fig.add_trace(
            go.Scatter(x=kde_x, y=kde_y, name=str(group), 
                      line=dict(color=color, width=2)),
            row=2, col=2
        )
    
    fig.update_layout(
        title=f"Distribution Comparison: {column} by {group_by}",
        showlegend=True,
        height=800
    )
    
    # Update axes
    fig.update_xaxes(title_text=column, row=1, col=1)
    fig.update_yaxes(title_text=column, row=1, col=2)
    fig.update_yaxes(title_text=column, row=2, col=1)
    fig.update_xaxes(title_text=column, row=2, col=2)
    fig.update_yaxes(title_text="Density", row=2, col=2)
    
    return fig


def add_regression_line(fig: go.Figure, df: pd.DataFrame, 
                        x_col: str, y_col: str, 
                        degree: int = 1) -> go.Figure:
    """Add a regression line to an existing figure."""
    
    # Remove NaN values
    clean_df = df[[x_col, y_col]].dropna()
    
    # Fit polynomial
    z = np.polyfit(clean_df[x_col], clean_df[y_col], degree)
    p = np.poly1d(z)
    
    # Generate smooth line
    x_range = np.linspace(clean_df[x_col].min(), clean_df[x_col].max(), 100)
    y_pred = p(x_range)
    
    # Calculate R²
    y_pred_points = p(clean_df[x_col])
    ss_res = np.sum((clean_df[y_col] - y_pred_points) ** 2)
    ss_tot = np.sum((clean_df[y_col] - clean_df[y_col].mean()) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    
    # Add regression line
    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_pred,
        mode='lines',
        name=f'Regression (degree={degree}, R²={r_squared:.3f})',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    # Add equation as annotation
    if degree == 1:
        equation = f"y = {z[0]:.2f}x + {z[1]:.2f}"
    else:
        equation = f"Polynomial (degree {degree})"
    
    fig.add_annotation(
        text=f"{equation}<br>R² = {r_squared:.3f}",
        xref="paper", yref="paper",
        x=0.05, y=0.95,
        showarrow=False,
        bgcolor="white",
        bordercolor="black",
        borderwidth=1
    )
    
    return fig


def create_interactive_dashboard(df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
    """
    Create an interactive dashboard based on configuration.
    
    Config example:
    {
        'title': 'My Dashboard',
        'layout': {'rows': 2, 'cols': 2},
        'plots': [
            {'type': 'scatter', 'x': 'col1', 'y': 'col2', 'position': [1, 1]},
            {'type': 'histogram', 'column': 'col3', 'position': [1, 2]},
            ...
        ]
    }
    """
    
    rows = config.get('layout', {}).get('rows', 1)
    cols = config.get('layout', {}).get('cols', 1)
    
    # Create subplot specs
    specs = [[{} for _ in range(cols)] for _ in range(rows)]
    subplot_titles = [['' for _ in range(cols)] for _ in range(rows)]
    
    for plot in config.get('plots', []):
        pos = plot.get('position', [1, 1])
        row_idx, col_idx = pos[0] - 1, pos[1] - 1
        
        plot_type = plot.get('type', 'scatter')
        if plot_type in ['scatter', 'line']:
            specs[row_idx][col_idx] = {'type': 'scatter'}
        elif plot_type == 'histogram':
            specs[row_idx][col_idx] = {'type': 'histogram'}
        elif plot_type == 'heatmap':
            specs[row_idx][col_idx] = {'type': 'heatmap'}
        elif plot_type == 'box':
            specs[row_idx][col_idx] = {'type': 'box'}
            
        subplot_titles[row_idx][col_idx] = plot.get('title', '')
    
    # Flatten subplot titles
    flat_titles = [title for row in subplot_titles for title in row]
    
    # Create subplots
    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=flat_titles,
        specs=specs
    )
    
    # Add plots
    for plot in config.get('plots', []):
        pos = plot.get('position', [1, 1])
        plot_type = plot.get('type', 'scatter')
        
        if plot_type == 'scatter':
            fig.add_trace(
                go.Scatter(
                    x=df[plot['x']],
                    y=df[plot['y']],
                    mode='markers',
                    name=plot.get('name', 'Scatter')
                ),
                row=pos[0], col=pos[1]
            )
        elif plot_type == 'line':
            fig.add_trace(
                go.Scatter(
                    x=df[plot['x']],
                    y=df[plot['y']],
                    mode='lines',
                    name=plot.get('name', 'Line')
                ),
                row=pos[0], col=pos[1]
            )
        elif plot_type == 'histogram':
            fig.add_trace(
                go.Histogram(
                    x=df[plot['column']],
                    nbinsx=plot.get('bins', 30),
                    name=plot.get('name', 'Histogram')
                ),
                row=pos[0], col=pos[1]
            )
        elif plot_type == 'box':
            fig.add_trace(
                go.Box(
                    y=df[plot['column']],
                    name=plot.get('name', 'Box')
                ),
                row=pos[0], col=pos[1]
            )
    
    fig.update_layout(
        title=config.get('title', 'Dashboard'),
        showlegend=True,
        height=config.get('height', 800)
    )
    
    return fig