"""
Shared utilities for Differential Evolution tests.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details


def create_test_function_wrapper(func_details):
    """
    Creates a wrapper function that adapts test functions to the format expected by the optimizer.
    
    Args:
        func_details: Dictionary containing function details from get_function_details
        
    Returns:
        A function that accepts parameters DataFrame and returns list of response dicts
    """
    func = func_details['func']
    dim = func_details.get('dim', 2)  # Default to 2D if not specified
    
    def wrapper(parameters, **kwargs):
        responses = []
        
        for _, row in parameters.iterrows():
            # Handle different parameter naming conventions
            x_values = []
            
            # Try x, y naming first (common for 2D)
            if 'x' in row and 'y' in row:
                x_values = [row['x'], row['y']]
                # Add more dimensions if they exist (z, w, etc.)
                for param in ['z', 'w']:
                    if param in row:
                        x_values.append(row[param])
            else:
                # Try x1, x2, ... naming
                for i in range(dim):
                    param_name = f'x{i+1}'
                    if param_name in row:
                        x_values.append(row[param_name])
                    elif f'x{i}' in row:  # Also try 0-indexed
                        x_values.append(row[f'x{i}'])
            
            # If we still don't have enough values, try to get any numeric columns
            if len(x_values) < dim:
                for col in row.index:
                    if col not in ['metric', 'iter'] and isinstance(row[col], (int, float)):
                        if len(x_values) < dim:
                            x_values.append(row[col])
            
            # Convert to numpy array
            x = np.array(x_values[:dim])  # Ensure we don't exceed expected dimensions
            
            # Evaluate function
            value = func(x)
            
            # Create response dict
            response = {
                'metric': value,
                'data': {f'x{i+1}': x_values[i] for i in range(len(x_values))}
            }
            responses.append(response)
        
        return responses
    
    return wrapper


def create_test_results_dir(test_name: str) -> str:
    """Create a results directory for the test."""
    base_dir = os.path.join(os.path.dirname(__file__), 'results')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = os.path.join(base_dir, f"{test_name}_{timestamp}")
    os.makedirs(test_dir, exist_ok=True)
    return test_dir


def save_test_summary(results_dir: str, summary: Dict[str, Any]):
    """Save test summary to JSON file."""
    summary_file = os.path.join(results_dir, 'test_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Test summary saved to: {summary_file}")


def create_2d_function_animation(optimizer, function_name: str, results_dir: str, 
                                include_3d: bool = True, fps: int = 10):
    """
    Create animation for 2D function optimization with optional 3D view.
    
    Args:
        optimizer: DifferentialEvolution instance after optimization
        function_name: Name of the test function
        results_dir: Directory to save results
        include_3d: Whether to include 3D surface view
        fps: Frames per second for animation
    """
    import matplotlib.animation as animation
    from mpl_toolkits.mplot3d import Axes3D
    
    # Get function details
    func_details = get_function_details(function_name)
    func = func_details['func']
    bounds = func_details.get('plot_bounds', func_details['bounds'])
    
    # Create figure
    if include_3d:
        fig = plt.figure(figsize=(18, 8))
        # 3D surface plot
        ax1 = fig.add_subplot(121, projection='3d')
        # 2D contour plot
        ax2 = fig.add_subplot(122)
    else:
        fig, ax2 = plt.subplots(figsize=(10, 8))
        ax1 = None
    
    # Create meshgrid for plotting
    x_range = np.linspace(bounds[0][0], bounds[0][1], 100)
    y_range = np.linspace(bounds[1][0], bounds[1][1], 100)
    X, Y = np.meshgrid(x_range, y_range)
    
    # Evaluate function on grid
    Z = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i, j] = func(np.array([X[i, j], Y[i, j]]))
    
    # Setup 3D plot if included
    if ax1:
        # Plot surface
        surf = ax1.plot_surface(X, Y, Z, cmap='viridis', alpha=0.6, 
                               linewidth=0, antialiased=True)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('f(X, Y)')
        ax1.set_title(f'{function_name} - 3D View')
        
        # Set viewing angle
        ax1.view_init(elev=30, azim=45)
    
    # Setup 2D contour plot
    contour = ax2.contourf(X, Y, Z, levels=20, cmap='viridis', alpha=0.7)
    ax2.contour(X, Y, Z, levels=20, colors='black', alpha=0.3, linewidths=0.5)
    plt.colorbar(contour, ax=ax2)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_title(f'{function_name} - Optimization Progress')
    
    # Get optimization history
    history = optimizer.history
    trials = history['trials']
    bests = history['bests']
    
    # Initialize scatter plots
    if ax1:
        pop_scatter_3d = ax1.scatter([], [], [], c='red', s=50, alpha=0.6)
        best_scatter_3d = ax1.scatter([], [], [], c='yellow', s=200, marker='*')
    
    pop_scatter_2d = ax2.scatter([], [], c='red', s=50, alpha=0.6, label='Population')
    best_scatter_2d = ax2.scatter([], [], c='yellow', s=200, marker='*', 
                                 edgecolors='black', linewidths=2, label='Best')
    ax2.legend()
    
    # Animation update function
    def update(frame):
        # Get data for current iteration
        iter_data = trials[trials['iter'] == frame]
        best_data = bests[bests['iter'] == frame]
        
        if not iter_data.empty:
            # Get parameter columns
            param_cols = [col for col in iter_data.columns if col not in ['iter', 'metric']]
            x_col, y_col = param_cols[0], param_cols[1]
            
            # Update 2D scatter
            pop_scatter_2d.set_offsets(np.c_[iter_data[x_col], iter_data[y_col]])
            
            if not best_data.empty:
                best_scatter_2d.set_offsets(np.c_[best_data[x_col], best_data[y_col]])
            
            # Update 3D scatter if included
            if ax1:
                # Calculate Z values for population
                z_vals = []
                for _, row in iter_data.iterrows():
                    z_vals.append(func(np.array([row[x_col], row[y_col]])))
                
                # Update 3D population scatter
                pop_scatter_3d._offsets3d = (iter_data[x_col], iter_data[y_col], z_vals)
                
                # Update 3D best scatter
                if not best_data.empty:
                    best_z = func(np.array([best_data[x_col].iloc[0], best_data[y_col].iloc[0]]))
                    best_scatter_3d._offsets3d = ([best_data[x_col].iloc[0]], 
                                                  [best_data[y_col].iloc[0]], 
                                                  [best_z])
        
        # Update title with iteration info
        ax2.set_title(f'{function_name} - Iteration {frame}/{optimizer.iter}')
        
        if ax1:
            return [pop_scatter_2d, best_scatter_2d, pop_scatter_3d, best_scatter_3d]
        else:
            return [pop_scatter_2d, best_scatter_2d]
    
    # Create animation
    max_frames = trials['iter'].max() + 1
    anim = animation.FuncAnimation(fig, update, frames=range(0, max_frames, max(1, max_frames//100)), 
                                  interval=1000/fps, blit=True)
    
    # Save animation
    animation_file = os.path.join(results_dir, f'{function_name}_optimization.gif')
    anim.save(animation_file, writer='pillow', fps=fps)
    print(f"Animation saved to: {animation_file}")
    
    # Save final frame as static image
    plt.figure(figsize=(12, 5))
    
    # Plot final population
    final_iter = trials['iter'].max()
    final_trials = trials[trials['iter'] == final_iter]
    final_best = bests[bests['iter'] == final_iter]
    
    # Contour plot
    plt.contourf(X, Y, Z, levels=20, cmap='viridis', alpha=0.7)
    plt.contour(X, Y, Z, levels=20, colors='black', alpha=0.3, linewidths=0.5)
    
    # Plot population and best
    if not final_trials.empty:
        param_cols = [col for col in final_trials.columns if col not in ['iter', 'metric']]
        x_col, y_col = param_cols[0], param_cols[1]
        plt.scatter(final_trials[x_col], final_trials[y_col], c='red', s=50, alpha=0.6, label='Final Population')
        
        if not final_best.empty:
            plt.scatter(final_best[x_col], final_best[y_col], c='yellow', s=200, marker='*', 
                       edgecolors='black', linewidths=2, label=f'Best (metric={final_best["metric"].iloc[0]:.6f})')
    
    plt.colorbar(label='Function Value')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(f'{function_name} - Final Result')
    plt.legend()
    plt.tight_layout()
    
    final_plot_file = os.path.join(results_dir, f'{function_name}_final.png')
    plt.savefig(final_plot_file, dpi=150, bbox_inches='tight')
    plt.close('all')
    print(f"Final plot saved to: {final_plot_file}")


def plot_convergence_comparison(results_dict: Dict[str, Any], results_dir: str, 
                               title: str = "Convergence Comparison"):
    """
    Plot convergence curves for multiple optimization runs.
    
    Args:
        results_dict: Dictionary with keys as labels and values as optimizer instances or histories
        results_dir: Directory to save the plot
        title: Plot title
    """
    plt.figure(figsize=(10, 6))
    
    for label, data in results_dict.items():
        # Extract history
        if hasattr(data, 'history'):
            history = data.history
        else:
            history = data
            
        # Get best metric evolution
        bests = history['bests']
        iterations = bests['iter'].values
        metrics = bests['metric'].values
        
        plt.plot(iterations, metrics, label=label, linewidth=2)
    
    plt.xlabel('Iteration')
    plt.ylabel('Best Metric')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.yscale('log')  # Log scale often helpful for convergence plots
    
    # Save plot
    plot_file = os.path.join(results_dir, 'convergence_comparison.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Convergence comparison saved to: {plot_file}")


def create_parameter_bounds_plot(optimizer, param_name: str, results_dir: str):
    """
    Create a plot showing how parameter bounds evolve during optimization.
    
    Args:
        optimizer: DifferentialEvolution instance after optimization
        param_name: Name of the parameter to plot
        results_dir: Directory to save results
    """
    # This will be particularly useful for adaptive boundaries test
    # Implementation depends on how boundaries are stored in history
    pass  # TODO: Implement when we have access to boundary history