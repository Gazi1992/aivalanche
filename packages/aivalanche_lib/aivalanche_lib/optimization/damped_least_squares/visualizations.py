"""
Visualization functions for the DampedLeastSquares class.

This module provides plotting functions to visualize the optimization progress
and results.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, List, Tuple
import matplotlib.pyplot as plt


def _plot_metrics_evolution(dls_instance, fig=None, ax=None, figsize=(10, 6),
                          x_scale='linear', y_scale='log',
                          save_path=None, title=None, **kwargs):
    """
    Plot the evolution of metrics throughout the optimization process.
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        fig: Optional existing figure
        ax: Optional existing axes
        figsize: Figure size
        x_scale: Scale for x-axis ('linear' or 'log')
        y_scale: Scale for y-axis ('linear' or 'log')
        save_path: Path to save the figure
        title: Custom title
        **kwargs: Additional plotting arguments
        
    Returns:
        tuple: (fig, ax)
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Get data
    iterations = range(1, len(dls_instance.all_metrics) + 1)
    metrics = dls_instance.all_metrics
    
    # Plot metrics
    ax.plot(iterations, metrics, 'b-', linewidth=2, label='Current', **kwargs)
    
    # Mark best point
    best_iter = np.argmin(metrics) + 1 if dls_instance.opt_min_or_max == 'min' else np.argmax(metrics) + 1
    best_metric = dls_instance.best_metric
    ax.plot(best_iter, best_metric, 'r*', markersize=15, label=f'Best: {best_metric:.6f}')
    
    # Formatting
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Metric')
    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    if title is None:
        title = f'DLS Optimization Progress ({dls_instance.opt_min_or_max}imization)'
    ax.set_title(title)
    
    # Save if requested
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig, ax


def _plot_damping_evolution(dls_instance, fig=None, ax=None, figsize=(10, 6),
                          save_path=None, title=None, **kwargs):
    """
    Plot the evolution of damping factor.
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        fig: Optional existing figure
        ax: Optional existing axes
        figsize: Figure size
        save_path: Path to save the figure
        title: Custom title
        **kwargs: Additional plotting arguments
        
    Returns:
        tuple: (fig, ax)
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Get data
    iterations = range(1, len(dls_instance.all_damping_factors) + 1)
    damping = dls_instance.all_damping_factors
    
    # Plot damping factor
    ax.semilogy(iterations, damping, 'g-', linewidth=2, **kwargs)
    
    # Add horizontal lines for min/max damping
    ax.axhline(y=dls_instance.min_damping, color='r', linestyle='--', alpha=0.5, label='Min damping')
    ax.axhline(y=dls_instance.max_damping, color='r', linestyle='--', alpha=0.5, label='Max damping')
    
    # Formatting
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Damping Factor (λ)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    if title is None:
        title = 'Damping Factor Evolution'
    ax.set_title(title)
    
    # Save if requested
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig, ax


def _plot_residuals_evolution(dls_instance, fig=None, ax=None, figsize=(10, 6),
                            save_path=None, title=None, **kwargs):
    """
    Plot the evolution of residuals norm.
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        fig: Optional existing figure
        ax: Optional existing axes
        figsize: Figure size
        save_path: Path to save the figure
        title: Custom title
        **kwargs: Additional plotting arguments
        
    Returns:
        tuple: (fig, ax)
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Compute residual norms
    residual_norms = []
    for residuals in dls_instance.all_residuals:
        if residuals is not None:
            residual_norms.append(np.linalg.norm(residuals))
    
    if len(residual_norms) == 0:
        print("No residuals to plot")
        return fig, ax
    
    iterations = range(1, len(residual_norms) + 1)
    
    # Plot residual norms
    ax.semilogy(iterations, residual_norms, 'r-', linewidth=2, **kwargs)
    
    # Formatting
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Residual Norm')
    ax.grid(True, alpha=0.3)
    
    if title is None:
        title = 'Residual Norm Evolution'
    ax.set_title(title)
    
    # Save if requested
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig, ax


def _plot_parameters_evolution(dls_instance, parameter_names=None, 
                             fig=None, ax=None, figsize=(10, 6),
                             save_path=None, title=None, **kwargs):
    """
    Plot the evolution of parameters.
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        parameter_names: List of parameter names to plot (None for all)
        fig: Optional existing figure
        ax: Optional existing axes
        figsize: Figure size
        save_path: Path to save the figure
        title: Custom title
        **kwargs: Additional plotting arguments
        
    Returns:
        tuple: (fig, ax)
    """
    # Get history
    df, _ = dls_instance.history['points'], dls_instance.history['points_normed']
    
    if parameter_names is None:
        parameter_names = dls_instance.variable_parameters_names
    
    # Validate parameter names
    for param in parameter_names:
        if param not in dls_instance.variable_parameters_names:
            raise ValueError(f"Parameter '{param}' not found")
    
    # Create subplots if needed
    n_params = len(parameter_names)
    if n_params > 1:
        n_cols = min(3, n_params)
        n_rows = (n_params + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(figsize[0]*n_cols/2, figsize[1]*n_rows/2))
        axes = axes.flatten() if n_params > 1 else [axes]
    else:
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        axes = [ax]
    
    # Plot each parameter
    for i, param_name in enumerate(parameter_names):
        ax = axes[i]
        
        # Plot parameter evolution
        ax.plot(df['iter'], df[param_name], 'b-', linewidth=2, **kwargs)
        
        # Mark final value
        final_value = df[param_name].iloc[-1]
        ax.axhline(y=final_value, color='r', linestyle='--', alpha=0.5)
        ax.text(df['iter'].iloc[-1], final_value, f'{final_value:.4f}', 
                ha='right', va='bottom', color='r')
        
        # Formatting
        ax.set_xlabel('Iteration')
        ax.set_ylabel(param_name)
        ax.grid(True, alpha=0.3)
        ax.set_title(f'{param_name} Evolution')
    
    # Hide extra subplots
    if n_params > 1:
        for i in range(n_params, len(axes)):
            axes[i].set_visible(False)
    
    if title and n_params == 1:
        axes[0].set_title(title)
    elif title:
        fig.suptitle(title)
    
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig, axes[0] if n_params == 1 else axes