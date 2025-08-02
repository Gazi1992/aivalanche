"""
Test pure Differential Evolution performance on various test functions.

This test evaluates DE on different function types from the test_functions module,
creating animations with both 2D and 3D views for better visualization.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details, ALL_FUNCTIONS

from test_utils import create_test_results_dir, save_test_summary, create_test_function_wrapper


def create_enhanced_animation(optimizer, function_name: str, results_dir: str, n_dim: int = None, fps: int = 10):
    """
    Create enhanced animation with both 2D contour and 3D surface views.
    """
    # Get function details
    func_details = get_function_details(function_name, n_dim)
    func = func_details['func']
    bounds = func_details.get('plot_bounds', func_details['bounds'])
    
    # Create figure with 2 subplots - make 3D plot larger
    fig = plt.figure(figsize=(20, 10))
    
    # 3D surface plot - make it same height as 2D
    ax1 = fig.add_subplot(121, projection='3d')
    
    # 2D contour plot
    ax2 = fig.add_subplot(122)
    
    # Create meshgrid for plotting
    # Handle different bound types and check for categorical
    x_categorical = False
    y_categorical = False
    x_categories = None
    y_categories = None
    
    # Handle X bounds
    if isinstance(bounds[0], list):
        if all(isinstance(v, str) for v in bounds[0]):
            # Categorical X
            x_categorical = True
            x_categories = bounds[0]
            x_min, x_max = 0, len(x_categories) - 1
        else:
            # Discrete values - use min and max of the list
            x_min, x_max = min(bounds[0]), max(bounds[0])
    elif isinstance(bounds[0], tuple) and len(bounds[0]) == 2:
        # Continuous range
        x_min, x_max = bounds[0]
    elif isinstance(bounds[0], tuple) and len(bounds[0]) == 3:
        # Discrete with step (min, max, step)
        x_min, x_max = bounds[0][0], bounds[0][1]
    else:
        x_min, x_max = bounds[0], bounds[0]
    
    # Handle Y bounds
    if isinstance(bounds[1], list):
        if all(isinstance(v, str) for v in bounds[1]):
            # Categorical Y
            y_categorical = True
            y_categories = bounds[1]
            y_min, y_max = 0, len(y_categories) - 1
        else:
            # Discrete values - use min and max of the list
            y_min, y_max = min(bounds[1]), max(bounds[1])
    elif isinstance(bounds[1], tuple) and len(bounds[1]) == 2:
        # Continuous range
        y_min, y_max = bounds[1]
    elif isinstance(bounds[1], tuple) and len(bounds[1]) == 3:
        # Discrete with step (min, max, step)
        y_min, y_max = bounds[1][0], bounds[1][1]
    else:
        y_min, y_max = bounds[1], bounds[1]
    
    # Create appropriate meshgrid
    if x_categorical:
        x_range = np.arange(len(x_categories))
    else:
        x_range = np.linspace(x_min, x_max, 100)
        
    if y_categorical:
        y_range = np.arange(len(y_categories))
    else:
        y_range = np.linspace(y_min, y_max, 100)
        
    X, Y = np.meshgrid(x_range, y_range)
    
    # Evaluate function on grid
    Z = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            # Prepare input values
            x_val = X[i, j]
            y_val = Y[i, j]
            
            # Convert categorical indices back to categories
            if x_categorical:
                x_val = x_categories[int(round(x_val))]
            if y_categorical:
                y_val = y_categories[int(round(y_val))]
                
            Z[i, j] = func(np.array([x_val, y_val]))
    
    # Setup 3D plot - use jet colormap to match 2D
    surf = ax1.plot_surface(X, Y, Z, cmap='jet', alpha=0.7, 
                           linewidth=0, antialiased=True, 
                           vmin=np.min(Z), vmax=np.max(Z))
    ax1.set_xlabel('X', fontsize=12)
    ax1.set_ylabel('Y', fontsize=12)
    ax1.set_zlabel('f(X, Y)', fontsize=12)
    ax1.set_title(f'{function_name} - 3D Surface', fontsize=14)
    ax1.view_init(elev=30, azim=45)
    
    # Set categorical ticks for 3D plot
    if x_categorical:
        ax1.set_xticks(range(len(x_categories)))
        ax1.set_xticklabels(x_categories)
    if y_categorical:
        ax1.set_yticks(range(len(y_categories)))
        ax1.set_yticklabels(y_categories)
    
    # Add colorbar for 3D plot
    cbar1 = plt.colorbar(surf, ax=ax1, shrink=0.5, aspect=10)
    cbar1.set_label('Function Value', fontsize=10)
    
    # Setup 2D contour plot - use log scale for better visualization
    # Use log scale if all values are positive
    if np.all(Z > 0):
        # Include the full range from min to max
        contour_levels = np.logspace(np.log10(np.min(Z) + 1e-10), np.log10(np.max(Z)), 30)
        contour = ax2.contourf(X, Y, Z, levels=contour_levels, cmap='jet', alpha=0.7, extend='both')
        ax2.contour(X, Y, Z, levels=contour_levels[::3], colors='black', alpha=0.3, linewidths=0.5)
    else:
        # Use full range from min to max instead of percentiles to avoid white patches
        contour_levels = np.linspace(np.min(Z), np.max(Z), 30)
        contour = ax2.contourf(X, Y, Z, levels=contour_levels, cmap='jet', alpha=0.7, extend='both')
        ax2.contour(X, Y, Z, levels=contour_levels[::3], colors='black', alpha=0.3, linewidths=0.5)
    cbar2 = plt.colorbar(contour, ax=ax2)
    cbar2.set_label('Function Value', fontsize=10)
    ax2.set_xlabel('X', fontsize=12)
    ax2.set_ylabel('Y', fontsize=12)
    ax2.set_title(f'{function_name} - Optimization Progress', fontsize=14)
    
    # Set categorical ticks for 2D plot
    if x_categorical:
        ax2.set_xticks(range(len(x_categories)))
        ax2.set_xticklabels(x_categories)
    if y_categorical:
        ax2.set_yticks(range(len(y_categories)))
        ax2.set_yticklabels(y_categories)
    
    # Initialize scatter plots first (empty) with high z-order to be on top
    pop_scatter_3d = ax1.scatter([], [], [], c='red', s=30, alpha=0.6, zorder=10)
    best_scatter_3d = ax1.scatter([], [], [], c='yellow', s=150, marker='*', 
                                 edgecolors='black', linewidths=2, zorder=11)
    
    pop_scatter_2d = ax2.scatter([], [], c='red', s=30, alpha=0.6, label='Population', zorder=10)
    best_scatter_2d = ax2.scatter([], [], c='yellow', s=150, marker='*', 
                                 edgecolors='black', linewidths=2, label='Current Best', zorder=11)
    
    # Mark optimum if available - plot BEFORE population so it's in background
    if 'optimum_loc' in func_details:
        opt_loc = func_details['optimum_loc']
        if isinstance(opt_loc, list):
            # Multiple optima
            for loc in opt_loc:
                # Convert categorical values to indices
                plot_x = loc[0]
                plot_y = loc[1]
                if x_categorical and isinstance(plot_x, str):
                    plot_x = x_categories.index(plot_x) if plot_x in x_categories else 0
                if y_categorical and isinstance(plot_y, str):
                    plot_y = y_categories.index(plot_y) if plot_y in y_categories else 0
                    
                ax2.plot(plot_x, plot_y, 'g*', markersize=20, markeredgecolor='black', 
                        markeredgewidth=2, zorder=1)  # Low zorder to be in background
                if len(opt_loc) == 1:  # Only show in 3D if single optimum
                    opt_val = func(loc)
                    ax1.scatter([plot_x], [plot_y], [opt_val], color='green', s=300, 
                               marker='*', edgecolors='black', linewidths=2, zorder=1)
        else:
            # Single optimum
            plot_x = opt_loc[0]
            plot_y = opt_loc[1]
            if x_categorical and isinstance(plot_x, str):
                plot_x = x_categories.index(plot_x) if plot_x in x_categories else 0
            if y_categorical and isinstance(plot_y, str):
                plot_y = y_categories.index(plot_y) if plot_y in y_categories else 0
                
            ax2.plot(plot_x, plot_y, 'g*', markersize=20, markeredgecolor='black', 
                    markeredgewidth=2, label='Global Optimum', zorder=1)
            opt_val = func(opt_loc)
            ax1.scatter([plot_x], [plot_y], [opt_val], color='green', s=300, 
                       marker='*', edgecolors='black', linewidths=2, zorder=1)
    
    # Get optimization history
    history = optimizer.history
    trials = history['trials']
    bests = history['bests']
    
    # Re-initialize scatter plots with proper zorder
    pop_scatter_3d._offsets3d = ([], [], [])
    best_scatter_3d._offsets3d = ([], [], [])
    pop_scatter_2d.set_offsets(np.empty((0, 2)))
    best_scatter_2d.set_offsets(np.empty((0, 2)))
    
    # Add text for iteration and metric info
    info_text = fig.text(0.5, 0.02, '', ha='center', fontsize=12, 
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    ax2.legend(loc='upper right')
    
    # Animation update function
    def update(frame):
        # Get data for current iteration
        iter_data = trials[trials['iter'] == frame]
        best_data = bests[bests['iter'] == frame]
        
        if not iter_data.empty:
            # Get parameter columns - handle different naming conventions
            param_cols = [col for col in iter_data.columns if col not in ['iter', 'metric']]
            if len(param_cols) >= 2:
                # We know we use 'x' and 'y' for 2D functions
                x_col, y_col = param_cols[0], param_cols[1]
                
                # Convert categorical values to indices for plotting
                x_data = iter_data[x_col].copy()
                y_data = iter_data[y_col].copy()
                
                if x_categorical:
                    x_data = x_data.map({cat: idx for idx, cat in enumerate(x_categories)})
                if y_categorical:
                    y_data = y_data.map({cat: idx for idx, cat in enumerate(y_categories)})
                
                # Update 2D scatter
                pop_scatter_2d.set_offsets(np.c_[x_data, y_data])
                
                if not best_data.empty:
                    best_x = best_data[x_col].iloc[0]
                    best_y = best_data[y_col].iloc[0]
                    
                    if x_categorical:
                        best_x = x_categories.index(best_x) if best_x in x_categories else 0
                    if y_categorical:
                        best_y = y_categories.index(best_y) if best_y in y_categories else 0
                        
                    best_scatter_2d.set_offsets(np.c_[[best_x], [best_y]])
                    
                    # Update info text
                    best_metric = best_data['metric'].iloc[0]
                    pop_std = iter_data['metric'].std()
                    info_text.set_text(f'Iteration: {frame} | Best Metric: {best_metric:.6e} | Population Std: {pop_std:.6e}')
                
                # Update 3D scatter
                # Calculate Z values for population
                z_vals = []
                for _, row in iter_data.iterrows():
                    z_vals.append(row['metric'])  # Use metric directly
                
                # Update 3D population scatter
                pop_scatter_3d._offsets3d = (x_data, y_data, z_vals)
                
                # Update 3D best scatter
                if not best_data.empty:
                    best_z = best_data['metric'].iloc[0]
                    best_scatter_3d._offsets3d = ([best_x], [best_y], [best_z])
        
        # Rotate 3D view slightly for dynamic effect
        ax1.view_init(elev=30, azim=45 + frame * 0.5)
        
        return [pop_scatter_2d, best_scatter_2d, pop_scatter_3d, best_scatter_3d, info_text]
    
    # Create animation
    max_frames = trials['iter'].max() + 1
    # Sample frames to keep animation reasonable length
    frame_step = max(1, max_frames // 100)
    frames = range(0, max_frames, frame_step)
    
    anim = animation.FuncAnimation(fig, update, frames=frames, 
                                  interval=1000/fps, blit=True)
    
    # Save animation
    animation_file = os.path.join(results_dir, f'{function_name}_optimization.gif')
    anim.save(animation_file, writer='pillow', fps=fps)
    plt.close(fig)
    print(f"  Animation saved to: {animation_file}")
    print(f"  Animation complete for {function_name}")


def create_evolution_plots(optimizer, function_name: str, results_dir: str):
    """Create metric and parameter evolution plots using DE's built-in functions."""
    from aivalanche_lib.optimization.differential_evolution.visualizations import (
        _plot_metrics_evolution, _plot_parameters_evolution, _plot_all_parameters_evolution
    )
    
    # Create metric evolution plot using bests
    bests_df = optimizer.history['bests']
    fig_metric, _ = _plot_metrics_evolution(
        iterations=bests_df['iter'].values,
        metrics=bests_df['metric'].values,
        title=f"{function_name} - Metric Evolution",
        save_path=os.path.join(results_dir, f'{function_name}_metric_evolution.png')
    )
    plt.close(fig_metric)
    print(f"  Metric evolution saved")
    
    # Create parameters evolution plot using trials (shows all population)
    trials_df = optimizer.history['trials']
    try:
        fig_params, _ = _plot_parameters_evolution(
            df=trials_df,
            parameter_names=optimizer.variable_parameters_names,
            title=f"{function_name} - Parameters Evolution (Population)",
            save_path=os.path.join(results_dir, f'{function_name}_parameters_evolution.png')
        )
        plt.close(fig_params)
        print(f"  Parameters evolution saved")
    except Exception as e:
        print(f"  Warning: Could not create parameters evolution plot: {type(e).__name__}: {str(e)}")
    
    # Create all parameters evolution plot (now supports categorical)
    try:
        fig_all_params, _ = _plot_all_parameters_evolution(
            df=trials_df,
            title=f"{function_name} - All Parameters Evolution",
            save_path=os.path.join(results_dir, f'{function_name}_all_parameters_evolution.png')
        )
        plt.close(fig_all_params)
        print(f"  All parameters evolution saved")
    except Exception as e:
        print(f"  Warning: Could not create all parameters evolution plot: {type(e).__name__}: {str(e)}")


def test_function_optimization(function_name: str, results_dir: str, n_dim: int = None, 
                             pop_size_multiplier: int = 10, max_iter: int = 100):
    """Test DE on a specific function."""
    print(f"\nTesting on {function_name}...")
    
    # Get function details
    func_details = get_function_details(function_name, n_dim)
    
    # Skip if not suitable for DE testing
    if func_details['dim'] == 'nD' and n_dim is None:
        print(f"  Skipping {function_name} - requires dimension specification")
        return None
    
    if func_details['dim'] not in [1, 2]:
        print(f"  Skipping {function_name} - only testing 1D and 2D functions")
        return None
    
    # Note if function contains categorical parameters
    param_types = func_details.get('param_types', [])
    has_categorical = 'categorical' in param_types
    
    # Create parameters from bounds
    params_list = []
    bounds = func_details['bounds']
    
    # Use 'x' and 'y' for 2D functions, 'x' for 1D
    if len(bounds) == 1:
        param_names = ['x']
    elif len(bounds) == 2:
        param_names = ['x', 'y']
    else:
        param_names = [f'x{i}' for i in range(len(bounds))]
    
    for i, (bound, param_name) in enumerate(zip(bounds, param_names)):
        if isinstance(bound, tuple) and len(bound) == 2:
            # Continuous parameter
            params_list.append({
                'name': param_name,
                'type': 'continuous',
                'min': bound[0],
                'max': bound[1],
                'default': (bound[0] + bound[1]) / 2
            })
        elif isinstance(bound, tuple) and len(bound) == 3:
            # Discrete with step
            params_list.append({
                'name': param_name,
                'type': 'discrete',
                'min': bound[0],
                'max': bound[1],
                'step': bound[2],
                'default': bound[0]
            })
        elif isinstance(bound, list):
            # Check if it's categorical (all strings) or discrete (numbers)
            if all(isinstance(v, str) for v in bound):
                # Categorical with string values
                params_list.append({
                    'name': param_name,
                    'type': 'categorical',
                    'values': bound,
                    'default': bound[0]
                })
            else:
                # Discrete with numeric values
                params_list.append({
                    'name': param_name,
                    'type': 'discrete',
                    'values': bound,
                    'default': bound[0]
                })
        else:
            print(f"  Warning: Unknown bound type for {param_name}: {bound}")
    
    parameters = Parameters(params_list)
    
    # Create evaluation function using wrapper
    eval_func = create_test_function_wrapper(func_details)
    
    # Create function-specific results directory
    func_results_dir = os.path.join(results_dir, function_name)
    os.makedirs(func_results_dir, exist_ok=True)
    
    # Determine population size
    # pop_size = max(20, len(params_list) * pop_size_multiplier)
    pop_size = 20
    
    # Create and run optimizer
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        pop_size=pop_size,
        max_iterations=max_iter,
        max_iter_without_improvement=100
    )
    
    optimizer.run_optimization()
    
    # Save history files
    for history_type in ['bests', 'trials', 'survivors']:
        history_file = optimizer.write_history_to_file(
            which=history_type,
            file_path=os.path.join(func_results_dir, f'history_{history_type}.csv')
        )
        print(f"  {history_type.capitalize()} history saved")
    
    # Calculate distance to optimum if available
    distance_to_optimum = None
    if 'optimum_loc' in func_details and 'optimum_val' in func_details:
        opt_loc = func_details['optimum_loc']
        if not isinstance(opt_loc, list):
            # Single optimum - only calculate distance for non-categorical parameters
            best_params = [optimizer.best_parameters[param['name']] for param in params_list]
            # Check if all parameters are numeric (not categorical)
            if all(not isinstance(val, str) for val in best_params):
                distance_to_optimum = np.linalg.norm(np.array(best_params) - opt_loc)
    
    result = {
        'optimizer': optimizer,
        'best_metric': optimizer.best_metric,
        'optimum_val': func_details.get('optimum_val', None),
        'error': abs(optimizer.best_metric - func_details.get('optimum_val', 0)) if 'optimum_val' in func_details else None,
        'iterations': optimizer.iter,
        'evaluations': optimizer.nr_evaluations,
        'distance_to_optimum': distance_to_optimum,
        'stop_reason': optimizer.stop_reason,
        'has_categorical': has_categorical
    }
    
    print(f"  Best found: {optimizer.best_metric:.6e}")
    if 'optimum_val' in func_details:
        print(f"  True optimum: {func_details['optimum_val']:.6e}")
        print(f"  Error: {result['error']:.6e}")
    print(f"  Iterations: {optimizer.iter}")
    
    return result


def main():
    """Run DE performance tests on various functions."""
    print("Differential Evolution Performance Test")
    print("=" * 60)
    
    # Create results directory
    results_dir = create_test_results_dir('de_performance')
    
    # Select test functions (1D and 2D, non-categorical)
    test_functions = [
        # 1D functions
        'parabola_1d',
        'sine_1d',
        # 2D continuous functions
        'sphere_2d',
        'rosenbrock_2d',
        'himmelblau_2d',
        'beale_2d',
        'griewank_2d',
        'rastrigin_nd',  # Will test as 2D
        'ackley_nd',     # Will test as 2D
        # Discrete functions
        'discrete_rastrigin_2d',
        'step_function_2d',
        'integer_quadratic_2d',
        # Mixed/Categorical functions
        'string_categorical_mixed_2d',
        'integer_categorical_2d',
        'discrete_categorical_2d',
        'mixed_discrete_continuous_2d',
        'categorical_interaction_2d'
    ]
    
    results = {}
    
    # Test each function
    for func_name in test_functions:
        # Determine dimension for nD functions
        n_dim = 2 if func_name.endswith('_nd') else None
        
        result = test_function_optimization(func_name, results_dir, n_dim)
        
        if result is not None:
            results[func_name] = result
            
            # Create visualizations for 2D functions
            func_details = get_function_details(func_name, n_dim)
            func_results_dir = os.path.join(results_dir, func_name)
            
            # Always create evolution plots (works for all functions)
            create_evolution_plots(result['optimizer'], func_name, func_results_dir)
            
            # Create animation for 2D functions (now supports categorical)
            if result['optimizer'].nr_variable_parameters == 2:
                create_enhanced_animation(result['optimizer'], func_name, func_results_dir, n_dim)
            else:
                print(f"  Skipping animation for {func_name} (not 2D)")
    
    # Create summary plots
    create_performance_summary(results, results_dir)
    
    # Save test summary
    summary = {
        'test_name': 'DE Performance Test',
        'timestamp': datetime.now().isoformat(),
        'functions_tested': list(results.keys()),
        'results': {
            name: {
                'best_metric': res['best_metric'],
                'optimum_val': res['optimum_val'],
                'error': res['error'],
                'iterations': res['iterations'],
                'evaluations': res['evaluations'],
                'distance_to_optimum': res['distance_to_optimum'],
                'stop_reason': res['stop_reason']
            }
            for name, res in results.items()
        }
    }
    save_test_summary(results_dir, summary)
    
    print(f"\n{'='*60}")
    print("Test completed!")
    print(f"Results saved to: {results_dir}")


def create_performance_summary(results: Dict[str, Any], results_dir: str):
    """Create summary plots for all tested functions."""
    # Prepare data
    func_names = list(results.keys())
    errors = []
    iterations = []
    evaluations = []
    
    for name in func_names:
        res = results[name]
        errors.append(res['error'] if res['error'] is not None else np.nan)
        iterations.append(res['iterations'])
        evaluations.append(res['evaluations'])
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Errors (log scale)
    ax1 = axes[0, 0]
    valid_errors = [(n, e) for n, e in zip(func_names, errors) if not np.isnan(e)]
    if valid_errors:
        names, errs = zip(*valid_errors)
        bars1 = ax1.bar(range(len(names)), errs)
        ax1.set_xticks(range(len(names)))
        ax1.set_xticklabels(names, rotation=45, ha='right')
        ax1.set_ylabel('Error (log scale)')
        ax1.set_title('Optimization Error by Function')
        ax1.set_yscale('log')
        ax1.grid(True, alpha=0.3)
        
        # Color bars by error magnitude
        for bar, err in zip(bars1, errs):
            if err < 1e-6:
                bar.set_color('green')
            elif err < 1e-3:
                bar.set_color('yellow')
            else:
                bar.set_color('red')
    
    # Plot 2: Iterations
    ax2 = axes[0, 1]
    bars2 = ax2.bar(range(len(func_names)), iterations)
    ax2.set_xticks(range(len(func_names)))
    ax2.set_xticklabels(func_names, rotation=45, ha='right')
    ax2.set_ylabel('Iterations')
    ax2.set_title('Iterations Required by Function')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Evaluations
    ax3 = axes[1, 0]
    bars3 = ax3.bar(range(len(func_names)), evaluations)
    ax3.set_xticks(range(len(func_names)))
    ax3.set_xticklabels(func_names, rotation=45, ha='right')
    ax3.set_ylabel('Function Evaluations')
    ax3.set_title('Total Evaluations by Function')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Efficiency (evaluations per iteration)
    ax4 = axes[1, 1]
    efficiency = [e/i for e, i in zip(evaluations, iterations)]
    bars4 = ax4.bar(range(len(func_names)), efficiency)
    ax4.set_xticks(range(len(func_names)))
    ax4.set_xticklabels(func_names, rotation=45, ha='right')
    ax4.set_ylabel('Evaluations per Iteration')
    ax4.set_title('Optimization Efficiency')
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('DE Performance Summary', fontsize=16)
    plt.tight_layout()
    
    summary_file = os.path.join(results_dir, 'performance_summary.png')
    plt.savefig(summary_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nPerformance summary saved to: {summary_file}")


if __name__ == "__main__":
    main()