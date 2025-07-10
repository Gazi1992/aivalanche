"""
Plotting utilities for 1D and 2D optimization test functions.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from typing import Callable, List, Tuple, Union, Optional

def _plot_1d_function(
    func: Callable[[np.ndarray], float],
    bounds: List[Tuple[float, float]],
    optimum_loc: Optional[np.ndarray] = None,
    optimum_val: Optional[float] = None,
    title: str = "1D Test Function",
    n_points: int = 500,
    ax: Optional[plt.Axes] = None,
    figsize: Tuple[int, int] = (8, 5)
) -> Tuple[plt.Figure, plt.Axes]:
    """Plots a 1D optimization test function."""
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    xmin, xmax = bounds[0]
    x = np.linspace(xmin, xmax, n_points)
    y = np.array([func(np.array([xi])) for xi in x]) # Evaluate function point-wise

    ax.plot(x, y, label=title)
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.6)

    # Plot optimum if available
    if optimum_loc is not None and optimum_val is not None:
        ax.scatter(optimum_loc[0], optimum_val, color='red', s=100, marker='*',
                   label=f'Optimum ({optimum_loc[0]:.2f}, {optimum_val:.2f})', zorder=5)
        ax.legend()

    fig.tight_layout()
    return fig, ax

def _plot_2d_function(
    func: Callable[[np.ndarray], float],
    bounds: List[Tuple[float, float]],
    optimum_loc: Optional[Union[np.ndarray, List[np.ndarray]]] = None,
    optimum_val: Optional[float] = None,
    title: str = "2D Test Function",
    n_points_per_dim: int = 100,
    fig: Optional[plt.Figure] = None,
    figsize: Tuple[int, int] = (12, 5),
    cmap: str = cm.viridis
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """Plots a 2D optimization test function using a surface and contour plot."""
    if fig is None:
        fig = plt.figure(figsize=figsize)

    # --- Setup Grid ---
    (x_min, x_max), (y_min, y_max) = bounds
    x = np.linspace(x_min, x_max, n_points_per_dim)
    y = np.linspace(y_min, y_max, n_points_per_dim)
    X, Y = np.meshgrid(x, y)

    # --- Evaluate Function ---
    Z = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i, j] = func(np.array([X[i, j], Y[i, j]]))

    # --- Surface Plot ---
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    surf = ax1.plot_surface(X, Y, Z, cmap=cmap, linewidth=0, antialiased=True, alpha=0.8)
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    ax1.set_zlabel('f(x, y)')
    ax1.set_title(f"{title} (Surface)")
    # fig.colorbar(surf, ax=ax1, shrink=0.5, aspect=10)

    # Plot optimum on surface
    if optimum_loc is not None and optimum_val is not None:
         # Handle multiple optima
        if isinstance(optimum_loc, list):
            for i, loc in enumerate(optimum_loc):
                label = f'Optimum {i+1}' if len(optimum_loc) > 1 else 'Optimum'
                ax1.scatter(loc[0], loc[1], optimum_val, color='red', s=80, marker='*', label=label, depthshade=False, zorder=10)
        else: # Single optimum
             ax1.scatter(optimum_loc[0], optimum_loc[1], optimum_val, color='red', s=80, marker='*', label='Optimum', depthshade=False, zorder=10)
        # ax1.legend() # Legend can be messy on 3D plots


    # --- Contour Plot ---
    ax2 = fig.add_subplot(1, 2, 2)
    n_levels = 20 # Number of contour levels
    # Use log scale for contours if values span large range, common in optimization
    try:
        levels = np.logspace(np.log10(np.min(Z[Z>0])+1e-9), np.log10(np.max(Z)+1e-9), n_levels)
        contour = ax2.contourf(X, Y, Z, levels=levels, cmap=cmap, locator=plt.LogLocator()) # Log scale
        # contour = ax2.contourf(X, Y, Z, levels=n_levels, cmap=cmap) # Linear scale
        cbar = fig.colorbar(contour, ax=ax2)
        cbar.set_label('f(x, y) (log scale)')
    except ValueError: # Handle cases with non-positive values for log scale
        print("Warning: Could not use log scale for contour plot. Using linear scale.")
        contour = ax2.contourf(X, Y, Z, levels=n_levels, cmap=cmap) # Linear scale
        cbar = fig.colorbar(contour, ax=ax2)
        cbar.set_label('f(x, y)')


    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    ax2.set_title(f"{title} (Contour)")
    ax2.set_aspect('equal', adjustable='box') # Make axes scales equal if possible

    # Plot optimum on contour
    if optimum_loc is not None:
        if isinstance(optimum_loc, list):
            for i, loc in enumerate(optimum_loc):
                label = f'Optimum {i+1}' if len(optimum_loc) > 1 else 'Optimum'
                ax2.scatter(loc[0], loc[1], color='red', s=100, marker='x', label=label, zorder=5)
        else: # Single optimum
             ax2.scatter(optimum_loc[0], optimum_loc[1], color='red', s=100, marker='x', label='Optimum', zorder=5)
        ax2.legend()

    fig.suptitle(title, fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent title overlap

    return fig, [ax1, ax2]


def plot_test_function(
    details: dict,
    fig: Optional[plt.Figure] = None,
    axes: Optional[List[plt.Axes]] = None,
    **kwargs # Pass additional args to specific plotters
) -> Tuple[plt.Figure, Union[plt.Axes, List[plt.Axes]]]:
    """
    Plots a test function based on its details dictionary.

    Args:
        details (dict): The dictionary containing function details
                        (obtained from get_function_details).
        fig (Optional[plt.Figure]): Existing Matplotlib Figure.
        axes (Optional[List[plt.Axes]]): Existing Matplotlib Axes.
                                         For 1D, provide one Axes.
                                         For 2D, provide two Axes (surface, contour).
        **kwargs: Additional keyword arguments passed to the underlying
                  plotting functions (_plot_1d_function or _plot_2d_function).

    Returns:
        Tuple[plt.Figure, Union[plt.Axes, List[plt.Axes]]]: The figure and axes used.

    Raises:
        ValueError: If trying to plot a function with dimension > 2.
    """
    dim = details['dim']
    func = details['func']
    bounds = details.get('plot_bounds', details['bounds']) # Use plot_bounds if available
    opt_loc = details.get('optimum_loc')
    opt_val = details.get('optimum_val')
    title = details.get('name', 'Test Function') # Get name from details if possible


    if dim == 1:
        ax = axes[0] if axes else None
        fig, ax_out = _plot_1d_function(func, bounds, opt_loc, opt_val, title, ax=ax, **kwargs)
        return fig, ax_out
    elif dim == 2:
         # 2D plotting expects a figure, not specific axes passed in directly for the subplot creation
         fig_out, axes_out = _plot_2d_function(func, bounds, opt_loc, opt_val, title, fig=fig, **kwargs)
         return fig_out, axes_out
    else:
        raise ValueError(f"Plotting is only supported for 1D and 2D functions. "
                         f"Function '{title}' has dimension {dim}.")
