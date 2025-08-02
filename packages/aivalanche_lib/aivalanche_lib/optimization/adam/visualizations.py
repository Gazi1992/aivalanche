"""
Visualization functions for ADAM optimizer.

This module provides plotting functions to visualize the optimization
process including metrics evolution, gradient norms, learning rates,
and parameter trajectories.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd


def _plot_metrics_evolution(iterations, metrics, x_scale='linear', y_scale='symlog',
                           fig=None, ax=None, title='Metric evolution',
                           figsize=(10, 6), save_path=None, **kwargs):
    """
    Plot the evolution of metrics over iterations.
    
    Args:
        iterations: Array of iteration numbers
        metrics: Array of metric values
        x_scale: Scale for x-axis ('linear' or 'log')
        y_scale: Scale for y-axis ('linear', 'log', or 'symlog')
        fig: Existing figure (optional)
        ax: Existing axis (optional)
        title: Plot title
        figsize: Figure size if creating new figure
        save_path: Path to save the plot
        **kwargs: Additional plotting arguments
    
    Returns:
        tuple: (fig, ax)
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    
    # Plot metrics
    ax.plot(iterations, metrics, 'b-', linewidth=2, label='Metric', **kwargs)
    
    # Mark best point
    best_idx = np.argmin(metrics)
    ax.scatter(iterations[best_idx], metrics[best_idx], 
               c='red', s=100, zorder=5, label=f'Best: {metrics[best_idx]:.6e}')
    
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Metric')
    ax.set_title(title)
    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig, ax


def _plot_gradient_norm_evolution(iterations, gradient_norms, fig=None, ax=None,
                                 title='Gradient norm evolution', figsize=(10, 6),
                                 save_path=None, gradient_tolerance=None, **kwargs):
    """
    Plot the evolution of gradient norm over iterations.
    
    Args:
        iterations: Array of iteration numbers
        gradient_norms: Array of gradient norm values
        fig: Existing figure (optional)
        ax: Existing axis (optional)
        title: Plot title
        figsize: Figure size if creating new figure
        save_path: Path to save the plot
        gradient_tolerance: Optional gradient tolerance to show as horizontal line
        **kwargs: Additional plotting arguments
    
    Returns:
        tuple: (fig, ax)
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    
    # Plot gradient norms
    ax.semilogy(iterations, gradient_norms, 'g-', linewidth=2, label='Gradient norm', **kwargs)
    
    # Add horizontal line for gradient tolerance (if available)
    if gradient_tolerance is not None:
        ax.axhline(y=gradient_tolerance, color='r', linestyle='--', alpha=0.7, 
                   label=f'Tolerance: {gradient_tolerance:.1e}')
    
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Gradient Norm')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig, ax


def _plot_learning_rate_evolution(iterations, learning_rates, fig=None, ax=None,
                                 title='Learning rate evolution', figsize=(10, 6),
                                 save_path=None, **kwargs):
    """
    Plot the evolution of learning rate over iterations.
    
    Args:
        iterations: Array of iteration numbers
        learning_rates: Array of learning rate values
        fig: Existing figure (optional)
        ax: Existing axis (optional)
        title: Plot title
        figsize: Figure size if creating new figure
        save_path: Path to save the plot
        **kwargs: Additional plotting arguments
    
    Returns:
        tuple: (fig, ax)
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    
    # Plot learning rates
    ax.plot(iterations, learning_rates, 'm-', linewidth=2, label='Learning rate', **kwargs)
    
    # Add initial learning rate line
    if len(learning_rates) > 0:
        initial_lr = learning_rates[0]
        ax.axhline(y=initial_lr, color='gray', linestyle=':', alpha=0.7, 
                   label=f'Initial: {initial_lr:.1e}')
    
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Learning Rate')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Use log scale if there's significant decay
    if len(learning_rates) > 1 and learning_rates[-1] < 0.1 * learning_rates[0]:
        ax.set_yscale('log')
    
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig, ax


def _plot_parameters_evolution(df, parameter_names, fig=None, axes=None,
                              title='Parameters evolution', figsize=(12, 8),
                              save_path=None, **kwargs):
    """
    Plot the evolution of parameters over iterations.
    
    Args:
        df: DataFrame with parameter history
        parameter_names: List of parameter names to plot
        fig: Existing figure (optional)
        axes: Existing axes array (optional)
        title: Overall plot title
        figsize: Figure size if creating new figure
        save_path: Path to save the plot
        **kwargs: Additional plotting arguments
    
    Returns:
        tuple: (fig, axes)
    """
    n_params = len(parameter_names)
    n_cols = min(3, n_params)
    n_rows = (n_params + n_cols - 1) // n_cols
    
    if fig is None or axes is None:
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize, squeeze=False)
    
    axes_flat = axes.flatten()
    
    for i, param_name in enumerate(parameter_names):
        ax = axes_flat[i]
        
        # Plot parameter evolution
        ax.plot(df['iter'], df[param_name], 'b-', linewidth=1.5, **kwargs)
        
        # Mark final value
        final_val = df[param_name].iloc[-1]
        ax.scatter(df['iter'].iloc[-1], final_val, c='red', s=50, zorder=5,
                  label=f'Final: {final_val:.4f}')
        
        ax.set_xlabel('Iteration')
        ax.set_ylabel(param_name)
        ax.set_title(f'{param_name} evolution')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    # Hide unused subplots
    for i in range(n_params, len(axes_flat)):
        axes_flat[i].set_visible(False)
    
    fig.suptitle(title)
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig, axes


def _plot_optimization_summary(adam_instance, figsize=(15, 10), save_path=None):
    """
    Create a comprehensive summary plot of the optimization process.
    
    Args:
        adam_instance: The Adam optimizer instance
        figsize: Figure size
        save_path: Path to save the plot
    
    Returns:
        matplotlib.figure.Figure: The figure object
    """
    fig = plt.figure(figsize=figsize)
    
    # Create grid layout
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1], hspace=0.3, wspace=0.3)
    
    # 1. Metric evolution
    ax1 = fig.add_subplot(gs[0, :])
    adam_instance.plot_metrics(fig=fig, ax=ax1)
    
    # 2. Gradient norm evolution
    ax2 = fig.add_subplot(gs[1, 0])
    if len(adam_instance.all_gradient_norms) > 0:
        adam_instance.plot_gradient_norm(fig=fig, ax=ax2)
    
    # 3. Learning rate evolution
    ax3 = fig.add_subplot(gs[1, 1])
    if len(adam_instance.all_learning_rates) > 0:
        adam_instance.plot_learning_rate(fig=fig, ax=ax3)
    
    # 4. Parameter evolution (first 2 parameters)
    ax4 = fig.add_subplot(gs[2, :])
    if adam_instance.iter > 0:
        df, _ = adam_instance._get_history_as_df('points')
        if not df.empty:
            # Plot first two parameters on same axis
            param_names = adam_instance.parameters_names[:2]
            for i, param in enumerate(param_names):
                ax4.plot(df['iter'], df[param], label=param, linewidth=2)
            ax4.set_xlabel('Iteration')
            ax4.set_ylabel('Parameter Value')
            ax4.set_title('Parameter Evolution (first 2 parameters)')
            ax4.grid(True, alpha=0.3)
            ax4.legend()
    
    # Add optimization info as text
    info_text = f"ADAM Optimization Summary\n"
    info_text += f"Total iterations: {adam_instance.iter}\n"
    info_text += f"Total evaluations: {adam_instance.nr_evaluations}\n"
    info_text += f"Best metric: {adam_instance.best_metric:.6e}\n"
    info_text += f"Stop reason: {adam_instance.stop_reason}\n"
    info_text += f"Final gradient norm: {adam_instance.gradient_norm:.6e}"
    
    fig.text(0.02, 0.02, info_text, transform=fig.transFigure, 
             fontsize=10, verticalalignment='bottom',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle('ADAM Optimization Summary', fontsize=14, fontweight='bold')
    
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def _create_convergence_animation(adam_instance, param_names=None, figsize=(12, 8),
                                 interval=100, fps=10, save_path=None, func_details=None):
    """
    Create an animation showing the convergence process for 2D problems.
    
    Args:
        adam_instance: The Adam optimizer instance
        param_names: Names of parameters to animate (default: first 2)
        figsize: Figure size
        interval: Delay between frames in milliseconds
        fps: Frames per second for saved animation
        save_path: Path to save animation
        func_details: Optional function details for plotting landscape
    
    Returns:
        matplotlib.animation.FuncAnimation: The animation object
    """
    if param_names is None:
        param_names = adam_instance.variable_parameters_names[:2]
    
    if len(param_names) != 2:
        raise ValueError("Animation requires exactly 2 parameters")
    
    # Get parameter history
    df, _ = adam_instance._get_history_as_df('points')
    if df.empty:
        raise ValueError("No optimization history available")
    
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    
    # If function details provided, plot landscape
    if func_details is not None:
        _add_function_landscape(ax, adam_instance.parameters, param_names, func_details)
    
    # Initialize plot elements
    line, = ax.plot([], [], 'b-', linewidth=2, alpha=0.7, label='Path')
    points = ax.scatter([], [], c='red', s=50, zorder=5)
    gradient_arrow = ax.quiver([], [], [], [], scale=1, scale_units='xy', 
                              angles='xy', width=0.003, color='green', alpha=0.7)
    
    # Best point marker
    best_point = ax.scatter([], [], c='gold', s=200, marker='*', zorder=10, 
                           edgecolors='black', linewidth=2, label='Best')
    
    ax.set_xlabel(param_names[0])
    ax.set_ylabel(param_names[1])
    ax.set_title('ADAM Optimization Path')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Set axis limits based on parameter history
    x_margin = 0.1 * (df[param_names[0]].max() - df[param_names[0]].min())
    y_margin = 0.1 * (df[param_names[1]].max() - df[param_names[1]].min())
    ax.set_xlim(df[param_names[0]].min() - x_margin, df[param_names[0]].max() + x_margin)
    ax.set_ylim(df[param_names[1]].min() - y_margin, df[param_names[1]].max() + y_margin)
    
    # Animation update function
    def update(frame):
        # Update path
        x_data = df[param_names[0]].iloc[:frame+1]
        y_data = df[param_names[1]].iloc[:frame+1]
        line.set_data(x_data, y_data)
        
        # Update current point
        if frame >= 0:
            points.set_offsets([[x_data.iloc[-1], y_data.iloc[-1]]])
        
        # Update gradient arrow (if available)
        if frame < len(adam_instance.all_gradients) and frame >= 0:
            # Get parameter indices for the two parameters we're plotting
            param_indices = [adam_instance.variable_parameters_names.index(p) for p in param_names]
            grad_x = adam_instance.all_gradients[frame, param_indices[0]]
            grad_y = adam_instance.all_gradients[frame, param_indices[1]]
            
            # Scale gradient for visibility
            grad_norm = np.sqrt(grad_x**2 + grad_y**2)
            if grad_norm > 0:
                scale = min(0.1, 0.5 / grad_norm)  # Adaptive scaling
                gradient_arrow.set_offsets([[x_data.iloc[-1], y_data.iloc[-1]]])
                gradient_arrow.set_UVC(-grad_x * scale, -grad_y * scale)
        
        # Update best point
        best_idx = np.argmin(df['metric'].iloc[:frame+1])
        best_point.set_offsets([[df[param_names[0]].iloc[best_idx], 
                                df[param_names[1]].iloc[best_idx]]])
        
        # Update title with iteration info
        if frame >= 0:
            ax.set_title(f'ADAM Optimization Path - Iteration {frame+1}, '
                        f'Metric: {df["metric"].iloc[frame]:.6e}')
        
        return line, points, gradient_arrow, best_point
    
    # Create animation
    anim = FuncAnimation(fig, update, frames=len(df), interval=interval,
                        blit=True, repeat=True)
    
    if save_path:
        anim.save(save_path, fps=fps, writer='pillow')
        print(f"Animation saved to: {save_path}")
    
    return anim


def _add_function_landscape(ax, parameters, param_names, func_details):
    """
    Add function landscape as background for 2D plots.
    
    Args:
        ax: Matplotlib axis
        parameters: Parameters object
        param_names: Names of the two parameters to plot
        func_details: Dictionary with function details including 'func'
    """
    # Create grid for evaluation
    grid_size = 100
    
    # Get parameter bounds
    x_param = parameters.get_parameter(param_names[0])
    y_param = parameters.get_parameter(param_names[1])
    
    x_range = np.linspace(x_param.min_val, x_param.max_val, grid_size)
    y_range = np.linspace(y_param.min_val, y_param.max_val, grid_size)
    X, Y = np.meshgrid(x_range, y_range)
    
    # Evaluate function
    Z = np.zeros_like(X)
    func = func_details['func']
    dim = func_details.get('dim', len(parameters.variable_names))
    
    for i in range(grid_size):
        for j in range(grid_size):
            # Create point with all parameters at defaults
            point = np.zeros(dim)
            
            # Get indices for the parameters we're plotting
            try:
                # Try to find parameters by exact name match
                for p_idx in range(dim):
                    param_name = f'x{p_idx+1}'
                    if param_name == param_names[0]:
                        point[p_idx] = X[i, j]
                    elif param_name == param_names[1]:
                        point[p_idx] = Y[i, j]
                    else:
                        # Use default value
                        if param_name in param_info['name'].values:
                            default_val = param_info[param_info['name'] == param_name]['default'].iloc[0]
                            point[p_idx] = default_val
                        else:
                            point[p_idx] = 0.0
            except:
                # Fallback to simple indexing
                point[0] = X[i, j]
                point[1] = Y[i, j]
            
            # Evaluate function
            try:
                Z[i, j] = func(point)
            except:
                Z[i, j] = np.nan
    
    # Apply log scale for better visualization
    Z_log = np.log10(Z + 1e-10)  # Add small value to avoid log(0)
    
    # Plot contours with filled regions
    levels = 50
    contourf = ax.contourf(X, Y, Z_log, levels=levels, cmap='viridis', alpha=0.7)
    contour = ax.contour(X, Y, Z_log, levels=20, colors='black', alpha=0.2, linewidths=0.5)
    
    # Add some contour labels for key levels
    if np.any(np.isfinite(Z_log)):
        try:
            ax.clabel(contour, inline=True, fontsize=6, fmt='%.1f')
        except:
            pass  # Skip labels if there's an issue