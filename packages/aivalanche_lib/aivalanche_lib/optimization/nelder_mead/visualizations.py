"""
Visualization functions for Nelder-Mead optimization.

This module provides plotting functions to visualize optimization progress,
simplex evolution, and parameter distributions.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.animation import FuncAnimation

def _plot_metrics_evolution(iterations, metrics, x_scale='linear', y_scale='symlog',
                           fig=None, ax=None, title=None, figsize=(10, 6),
                           save_path=None, **kwargs):
    """
    Plot the evolution of metrics over iterations.
    
    Args:
        iterations: Array of iteration numbers
        metrics: Array of metric values
        x_scale: Scale for x-axis ('linear' or 'log')
        y_scale: Scale for y-axis ('linear', 'log', or 'symlog')
        fig: Existing figure (optional)
        ax: Existing axes (optional)
        title: Plot title
        figsize: Figure size if creating new figure
        save_path: Path to save the figure
        **kwargs: Additional matplotlib plotting arguments
    
    Returns:
        tuple: (fig, ax)
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Plot metrics
    ax.plot(iterations, metrics, 'o-', markersize=4, **kwargs)
    
    # Set scales
    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)
    
    # Labels and title
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Metric')
    if title:
        ax.set_title(title)
    
    # Grid
    ax.grid(True, alpha=0.3)
    
    # Save if path provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig, ax

def _plot_simplex_evolution(optimizer, parameter_names=None, fig=None, axes=None,
                           figsize=(10, 6), title=None, save_path=None, **kwargs):
    """
    Plot the evolution of the simplex in 2D parameter space.
    
    Args:
        optimizer: The NelderMead optimizer instance
        parameter_names: List of 1-2 parameter names to visualize
        fig: Existing figure (optional)
        axes: Existing axes (optional)
        figsize: Figure size if creating new figure
        title: Plot title
        save_path: Path to save the figure
        **kwargs: Additional matplotlib plotting arguments
    
    Returns:
        tuple: (fig, ax)
    """
    if parameter_names is None:
        parameter_names = optimizer.variable_parameters_names[:2]
    
    n_params = len(parameter_names)
    if n_params > 2:
        raise ValueError("Can only visualize up to 2 parameters")
    
    # Get parameter indices
    param_indices = [optimizer.variable_parameters_names.index(p) for p in parameter_names]
    
    if fig is None or axes is None:
        if n_params == 1:
            fig, ax = plt.subplots(figsize=figsize)
            axes = [ax]
        else:
            fig, ax = plt.subplots(figsize=figsize)
            axes = ax
    
    # Get history
    simplexes_history = optimizer.all_simplexes
    n_iterations = simplexes_history.shape[0]
    
    if n_params == 1:
        # 1D visualization - plot simplex vertices over iterations
        ax = axes if not isinstance(axes, list) else axes[0]
        
        for i in range(n_iterations):
            simplex = simplexes_history[i, :, param_indices[0]]
            y_values = np.full_like(simplex, i)
            
            # Color based on iteration progress
            color = plt.cm.viridis(i / max(n_iterations - 1, 1))
            ax.scatter(simplex, y_values, color=color, s=30, alpha=0.6)
            
            # Connect vertices
            if i > 0:
                for j in range(optimizer.simplex_size):
                    prev_x = simplexes_history[i-1, j, param_indices[0]]
                    curr_x = simplexes_history[i, j, param_indices[0]]
                    ax.plot([prev_x, curr_x], [i-1, i], 'k-', alpha=0.2, linewidth=0.5)
        
        ax.set_xlabel(f'{parameter_names[0]} (normalized)')
        ax.set_ylabel('Iteration')
        ax.set_xlim(-0.1, 1.1)
        
    else:  # 2D visualization
        ax = axes
        
        # Plot simplex evolution
        for i in range(n_iterations):
            simplex = simplexes_history[i, :, :][:, param_indices]
            
            # Create polygon for simplex
            polygon = Polygon(simplex, fill=False, 
                            edgecolor=plt.cm.viridis(i / max(n_iterations - 1, 1)),
                            linewidth=1, alpha=0.6)
            ax.add_patch(polygon)
            
            # Mark vertices
            ax.scatter(simplex[:, 0], simplex[:, 1], 
                      color=plt.cm.viridis(i / max(n_iterations - 1, 1)),
                      s=20, alpha=0.6)
        
        # Mark initial and final simplexes
        initial_simplex = simplexes_history[0, :, :][:, param_indices]
        final_simplex = simplexes_history[-1, :, :][:, param_indices]
        
        initial_polygon = Polygon(initial_simplex, fill=False, edgecolor='green', 
                                linewidth=2, label='Initial')
        final_polygon = Polygon(final_simplex, fill=False, edgecolor='red', 
                              linewidth=2, label='Final')
        ax.add_patch(initial_polygon)
        ax.add_patch(final_polygon)
        
        # Mark best point
        best_point = optimizer.best[param_indices]
        ax.scatter(best_point[0], best_point[1], color='red', s=100, 
                  marker='*', label='Best', zorder=10)
        
        ax.set_xlabel(f'{parameter_names[0]} (normalized)')
        ax.set_ylabel(f'{parameter_names[1]} (normalized)')
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.1)
        ax.legend()
    
    if title:
        ax.set_title(title)
    else:
        ax.set_title(f'Simplex Evolution ({n_iterations} iterations)')
    
    ax.grid(True, alpha=0.3)
    
    # Save if path provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig, ax

def _plot_parameters_evolution(df, parameter_names, iter_start=None, iter_end=None,
                             iter_step=1, fig=None, axes=None, bins=100,
                             figsize=(10, 6), title=None, save_path=None,
                             nr_rows=1, **kwargs):
    """
    Plot the evolution of parameter distributions as histograms.
    
    Args:
        df: DataFrame with parameter values and iterations
        parameter_names: List of parameter names to plot
        iter_start: Starting iteration
        iter_end: Ending iteration
        iter_step: Step size for iterations
        fig: Existing figure (optional)
        axes: Existing axes (optional)
        bins: Number of bins for histograms
        figsize: Figure size if creating new figure
        title: Plot title
        save_path: Path to save the figure
        nr_rows: Number of rows for subplots
        **kwargs: Additional matplotlib plotting arguments
    
    Returns:
        tuple: (fig, axes)
    """
    # Determine iteration range
    min_iter = df['iter'].min()
    max_iter = df['iter'].max()
    
    if iter_start is None:
        iter_start = min_iter
    if iter_end is None:
        iter_end = max_iter
    
    # Create iteration range
    iterations = range(iter_start, iter_end + 1, iter_step)
    n_iterations = len(list(iterations))
    
    # Create subplots
    n_params = len(parameter_names)
    n_cols = int(np.ceil(n_params / nr_rows))
    
    if fig is None or axes is None:
        fig, axes = plt.subplots(nr_rows, n_cols, figsize=figsize, squeeze=False)
    
    axes = axes.flatten()
    
    # Plot each parameter
    for idx, param_name in enumerate(parameter_names):
        ax = axes[idx]
        
        # Create 2D histogram data
        hist_data = []
        
        for iter_num in iterations:
            iter_data = df[df['iter'] == iter_num][param_name].values
            if len(iter_data) > 0:
                hist, _ = np.histogram(iter_data, bins=bins, range=(0, 1))
                hist_data.append(hist)
        
        if hist_data:
            hist_data = np.array(hist_data).T
            
            # Plot as image
            extent = [iter_start, iter_end, 0, 1]
            im = ax.imshow(hist_data, aspect='auto', origin='lower', extent=extent,
                         cmap='viridis', interpolation='nearest')
            
            ax.set_xlabel('Iteration')
            ax.set_ylabel(f'{param_name} (normalized)')
            ax.set_title(param_name)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Count')
    
    # Hide unused subplots
    for idx in range(n_params, len(axes)):
        axes[idx].set_visible(False)
    
    if title:
        fig.suptitle(title)
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig, axes

def create_animation(optimizer, parameter_names=None, interval=200, save_path=None):
    """
    Create an animation of the simplex evolution.
    
    Args:
        optimizer: The NelderMead optimizer instance
        parameter_names: List of 2 parameter names to visualize
        interval: Delay between frames in milliseconds
        save_path: Path to save the animation
    
    Returns:
        matplotlib.animation.FuncAnimation object
    """
    if parameter_names is None:
        parameter_names = optimizer.variable_parameters_names[:2]
    
    if len(parameter_names) != 2:
        raise ValueError("Animation requires exactly 2 parameters")
    
    # Get parameter indices
    param_indices = [optimizer.variable_parameters_names.index(p) for p in parameter_names]
    
    # Get history
    simplexes_history = optimizer.all_simplexes
    n_iterations = simplexes_history.shape[0]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel(f'{parameter_names[0]} (normalized)')
    ax.set_ylabel(f'{parameter_names[1]} (normalized)')
    ax.grid(True, alpha=0.3)
    
    # Initialize plot elements
    simplex_line, = ax.plot([], [], 'b-', linewidth=2)
    vertices_scatter = ax.scatter([], [], color='blue', s=50)
    best_scatter = ax.scatter([], [], color='red', s=100, marker='*')
    title = ax.text(0.5, 1.05, '', transform=ax.transAxes, ha='center')
    
    def init():
        simplex_line.set_data([], [])
        vertices_scatter.set_offsets(np.empty((0, 2)))
        best_scatter.set_offsets(np.empty((0, 2)))
        title.set_text('')
        return simplex_line, vertices_scatter, best_scatter, title
    
    def animate(frame):
        simplex = simplexes_history[frame, :, :][:, param_indices]
        
        # Close the polygon
        simplex_closed = np.vstack([simplex, simplex[0]])
        
        # Update simplex
        simplex_line.set_data(simplex_closed[:, 0], simplex_closed[:, 1])
        
        # Update vertices
        vertices_scatter.set_offsets(simplex)
        
        # Update best point (if available)
        if frame < len(optimizer.all_bests):
            best_point = optimizer.all_bests[frame][param_indices]
            best_scatter.set_offsets([best_point])
        
        # Update title
        title.set_text(f'Iteration {frame + 1}/{n_iterations}')
        
        return simplex_line, vertices_scatter, best_scatter, title
    
    anim = FuncAnimation(fig, animate, init_func=init, frames=n_iterations,
                        interval=interval, blit=True)
    
    if save_path:
        anim.save(save_path, writer='pillow')
    
    return anim


def _plot_simplex_animation(nm_instance, param_names=None, figsize=(10, 10), 
                           interval=100, fps=10, save_path=None):
    """
    Create an animation showing the evolution of the simplex in 2D parameter space.
    
    Args:
        nm_instance: The NelderMead optimizer instance
        param_names: List of two parameter names to plot. If None, uses first two parameters.
        figsize: Figure size as (width, height) tuple
        interval: Delay between frames in milliseconds
        fps: Frames per second for saved animation
        save_path: Path to save the animation (as .gif or .mp4)
        
    Returns:
        tuple: (figure, animation) objects
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.animation import FuncAnimation, PillowWriter
    
    # Check if we have 2D data
    if param_names is None:
        if len(nm_instance.variable_parameters_names) >= 2:
            param_names = nm_instance.variable_parameters_names[:2]
        else:
            print("Warning: Less than 2 variable parameters, cannot create 2D animation")
            return None, None
    
    if len(param_names) != 2:
        print("Warning: Animation requires exactly 2 parameters")
        return None, None
    
    # Get parameter indices
    x_param = param_names[0]
    y_param = param_names[1]
    try:
        x_idx = nm_instance.variable_parameters_names.index(x_param)
        y_idx = nm_instance.variable_parameters_names.index(y_param)
    except ValueError:
        print(f"Warning: Parameters {param_names} not found in variable parameters")
        return None, None
    
    # Get simplex history
    simplexes_history = nm_instance.all_simplexes
    n_iterations = simplexes_history.shape[0]
    
    if n_iterations == 0:
        print("Warning: No optimization history available")
        return None, None
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Set up the axes
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel(f'{x_param} (normalized)', fontsize=12)
    ax.set_ylabel(f'{y_param} (normalized)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Initialize patches list for simplex trails
    trail_patches = []
    
    # Text for iteration info
    text = ax.text(0.02, 0.98, '', transform=ax.transAxes, 
                   verticalalignment='top', fontsize=12,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    def init():
        """Initialize animation."""
        # Clear any existing patches
        for patch in trail_patches:
            patch.remove()
        trail_patches.clear()
        text.set_text('')
        return trail_patches + [text]
    
    def animate(frame):
        """Animation function for each frame."""
        # Remove old trail patches that are too old
        while len(trail_patches) > 5:
            old_patch = trail_patches.pop(0)
            old_patch.remove()
        
        # Add trail simplexes with fading effect
        for j in range(max(0, frame-5), frame):
            alpha = 0.1 + 0.3 * (j - max(0, frame-5)) / 5
            simplex = simplexes_history[j, :, :]
            simplex_2d = simplex[:, [x_idx, y_idx]]
            triangle = patches.Polygon(simplex_2d, fill=False, 
                                     edgecolor='gray', alpha=alpha, 
                                     linewidth=1)
            ax.add_patch(triangle)
            trail_patches.append(triangle)
        
        # Plot current simplex
        current_simplex = simplexes_history[frame, :, :]
        current_simplex_2d = current_simplex[:, [x_idx, y_idx]]
        
        # Remove previous current simplex if exists
        if hasattr(animate, 'current_triangle') and animate.current_triangle:
            animate.current_triangle.remove()
        
        animate.current_triangle = patches.Polygon(current_simplex_2d, fill=False, 
                                                 edgecolor='blue', linewidth=3,
                                                 linestyle='-')
        ax.add_patch(animate.current_triangle)
        
        # Update vertices
        if hasattr(animate, 'vertices_scatter'):
            animate.vertices_scatter.remove()
        animate.vertices_scatter = ax.scatter(current_simplex_2d[:, 0], current_simplex_2d[:, 1], 
                                            color='white', s=80, zorder=5, 
                                            edgecolor='black', linewidth=1)
        
        # Update best point
        if frame < len(nm_instance.all_bests):
            if hasattr(animate, 'best_scatter'):
                animate.best_scatter.remove()
            best_point = nm_instance.all_bests[frame, [x_idx, y_idx]]
            best_metric = nm_instance.all_bests_metrics[frame, 0]
            animate.best_scatter = ax.scatter(best_point[0], best_point[1], 
                                            color='red', s=200, marker='*', 
                                            edgecolor='black', linewidth=1, zorder=10,
                                            label=f'Best (metric={best_metric:.2e})')
        
        # Update text
        text.set_text(f'Iteration: {frame+1}/{n_iterations}\\n' +
                     f'Simplex size: {nm_instance.simplex_size}')
        
        # Update title
        ax.set_title(f'Nelder-Mead - Simplex Evolution', fontsize=14)
        
        # Update legend
        ax.legend(loc='upper right')
        
        return trail_patches + [animate.current_triangle, animate.vertices_scatter, 
                               getattr(animate, 'best_scatter', None), text]
    
    # Create animation
    anim = FuncAnimation(fig, animate, init_func=init, frames=n_iterations,
                        interval=interval, blit=False, repeat=True)
    
    # Save animation if path provided
    if save_path:
        if save_path.endswith('.gif'):
            writer = PillowWriter(fps=fps)
            anim.save(save_path, writer=writer)
            print(f"Animation saved as GIF to: {save_path}")
        elif save_path.endswith('.mp4'):
            try:
                from matplotlib.animation import FFMpegWriter
                writer = FFMpegWriter(fps=fps, bitrate=1800)
                anim.save(save_path, writer=writer)
                print(f"Animation saved as MP4 to: {save_path}")
            except:
                print("Warning: FFmpeg not available, saving as GIF instead")
                gif_path = save_path.replace('.mp4', '.gif')
                writer = PillowWriter(fps=fps)
                anim.save(gif_path, writer=writer)
                print(f"Animation saved as GIF to: {gif_path}")
        else:
            print(f"Warning: Unsupported file format. Use .gif or .mp4")
    
    return fig, anim