"""
Comprehensive test suite for metamodel functionality across various test functions.
Tests range from simple (sphere) to complex (rastrigin) optimization problems.
"""

import numpy as np
import pandas as pd
import sys
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import cm
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details
from test_utils import create_test_function_wrapper, create_test_results_dir


def create_landscape_plot(de_no_mm, de_with_mm, func_name, parameters, results_dir):
    """Create a comparison plot showing trial points on the function landscape."""
    
    print(f"  Creating landscape comparison plot for {func_name}...")
    
    # Only create landscape plots for 2D functions
    if len(parameters.variable_names) != 2:
        print(f"  Skipping landscape plot - not a 2D function")
        return
    
    # Get parameter names and bounds
    param1_name = parameters.variable_names[0]
    param2_name = parameters.variable_names[1]
    param1 = parameters.get_parameter(param1_name)
    param2 = parameters.get_parameter(param2_name)
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 7))
    
    # Get parameter bounds
    x_min = param1.min
    x_max = param1.max
    y_min = param2.min
    y_max = param2.max
    
    # Create meshgrid for function landscape
    x_range = np.linspace(x_min, x_max, 150)
    y_range = np.linspace(y_min, y_max, 150)
    X, Y = np.meshgrid(x_range, y_range)
    
    # Evaluate function on grid
    Z = np.zeros_like(X)
    # Get function details to create eval_func
    if func_name in ['ackley_nd', 'rastrigin_nd', 'griewank_nd', 'sphere_nd']:
        func_details = get_function_details(func_name, n_dim=2)  # Use 2D for visualization
    else:
        func_details = get_function_details(func_name)
    eval_func = create_test_function_wrapper(func_details)
    
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            params_df = pd.DataFrame({
                param1_name: [X[i, j]],
                param2_name: [Y[i, j]]
            })
            result = eval_func(params_df)
            Z[i, j] = result[0]['metric']
    
    # Plot 1: Without Metamodel
    ax1 = fig.add_subplot(121)
    
    # Plot contour
    if func_name in ['rastrigin_2d', 'ackley_2d', 'griewank_2d']:
        # For highly oscillatory functions, use fewer contour levels
        levels = 20
    else:
        levels = 30
    
    contour1 = ax1.contour(X, Y, Z, levels=levels, colors='gray', alpha=0.3, linewidths=0.5)
    contourf1 = ax1.contourf(X, Y, Z, levels=levels, cmap='viridis', alpha=0.4)
    
    # Get all trial points for no metamodel run
    all_trials_no_mm = []
    if hasattr(de_no_mm, 'all_trials') and de_no_mm.all_trials is not None:
        for i in range(de_no_mm.all_trials.shape[0]):
            for j in range(de_no_mm.pop_size):
                if not np.isnan(de_no_mm.all_trials_metrics[i, j]):
                    point_norm = de_no_mm.all_trials[i, j, :]
                    point_df = pd.DataFrame([point_norm], columns=de_no_mm.parameters.variable_names)
                    point_denorm = de_no_mm.parameters.unnorm_all(point_df)
                    all_trials_no_mm.append([
                        point_denorm[param1_name].iloc[0],
                        point_denorm[param2_name].iloc[0]
                    ])
    
    all_trials_no_mm = np.array(all_trials_no_mm)
    
    # Plot trial points
    if len(all_trials_no_mm) > 0:
        ax1.scatter(all_trials_no_mm[:, 0], all_trials_no_mm[:, 1], 
                   c='red', s=15, alpha=0.5, edgecolors='darkred', linewidth=0.5,
                   label=f'Trials (n={len(all_trials_no_mm)})', zorder=5)
    
    # Mark optimum if known
    if 'optimum_loc' in func_details:
        opt = func_details['optimum_loc']
        if len(opt) >= 2:
            ax1.plot(opt[0], opt[1], 'g*', markersize=15, markeredgecolor='darkgreen',
                    markeredgewidth=1, label='Global optimum', zorder=10)
    
    # Mark best found point
    best_no_mm = de_no_mm.best_parameters
    ax1.plot(best_no_mm[param1_name], 
            best_no_mm[param2_name], 
            'ro', markersize=8, markeredgecolor='darkred', markeredgewidth=2,
            label=f'Best found', zorder=15)
    
    ax1.set_xlabel(param1_name, fontsize=11)
    ax1.set_ylabel(param2_name, fontsize=11)
    ax1.set_title(f'Without Metamodel\n{len(all_trials_no_mm)} evaluations', 
                 fontsize=12, fontweight='bold')
    ax1.set_xlim(x_min, x_max)
    ax1.set_ylim(y_min, y_max)
    ax1.grid(True, alpha=0.2)
    ax1.legend(loc='upper right', fontsize=8)
    ax1.set_aspect('equal')
    
    # Plot 2: With Metamodel
    ax2 = fig.add_subplot(122)
    
    # Plot contour
    contour2 = ax2.contour(X, Y, Z, levels=levels, colors='gray', alpha=0.3, linewidths=0.5)
    contourf2 = ax2.contourf(X, Y, Z, levels=levels, cmap='viridis', alpha=0.4)
    
    # Get all trial points for metamodel run
    all_trials_with_mm = []
    if hasattr(de_with_mm, 'all_trials') and de_with_mm.all_trials is not None:
        for i in range(de_with_mm.all_trials.shape[0]):
            for j in range(de_with_mm.pop_size):
                if not np.isnan(de_with_mm.all_trials_metrics[i, j]):
                    point_norm = de_with_mm.all_trials[i, j, :]
                    point_df = pd.DataFrame([point_norm], columns=de_with_mm.parameters.variable_names)
                    point_denorm = de_with_mm.parameters.unnorm_all(point_df)
                    all_trials_with_mm.append([
                        point_denorm[param1_name].iloc[0],
                        point_denorm[param2_name].iloc[0]
                    ])
    
    all_trials_with_mm = np.array(all_trials_with_mm)
    
    # Plot trial points
    if len(all_trials_with_mm) > 0:
        ax2.scatter(all_trials_with_mm[:, 0], all_trials_with_mm[:, 1], 
                   c='blue', s=15, alpha=0.5, edgecolors='darkblue', linewidth=0.5,
                   label=f'Trials (n={len(all_trials_with_mm)})', zorder=5)
    
    # Mark optimum if known
    if 'optimum_loc' in func_details:
        opt = func_details['optimum_loc']
        if len(opt) >= 2:
            ax2.plot(opt[0], opt[1], 'g*', markersize=15, markeredgecolor='darkgreen',
                    markeredgewidth=1, label='Global optimum', zorder=10)
    
    # Mark best found point
    best_with_mm = de_with_mm.best_parameters
    ax2.plot(best_with_mm[param1_name], 
            best_with_mm[param2_name], 
            'bo', markersize=8, markeredgecolor='darkblue', markeredgewidth=2,
            label=f'Best found', zorder=15)
    
    ax2.set_xlabel(param1_name, fontsize=11)
    ax2.set_ylabel(param2_name, fontsize=11)
    ax2.set_title(f'With Metamodel\n{len(all_trials_with_mm)} evaluations', 
                 fontsize=12, fontweight='bold')
    ax2.set_xlim(x_min, x_max)
    ax2.set_ylim(y_min, y_max)
    ax2.grid(True, alpha=0.2)
    ax2.legend(loc='upper right', fontsize=8)
    ax2.set_aspect('equal')
    
    # Add colorbar
    fig.subplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(contourf1, cax=cbar_ax, label='Function Value')
    
    # Main title
    reduction = (1 - len(all_trials_with_mm) / len(all_trials_no_mm)) * 100 if len(all_trials_no_mm) > 0 else 0
    plt.suptitle(f'{func_name.replace("_", " ").title()}: Trial Points Comparison\n'
                f'Evaluation reduction: {reduction:.1f}%', 
                fontsize=14, fontweight='bold', y=0.98)
    
    # Save plot
    save_path = os.path.join(results_dir, f'{func_name}_landscape.png')
    print(f"  Saving landscape plot to: {save_path}")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Landscape plot saved successfully!")
    
    # Verify file exists
    if os.path.exists(save_path):
        print(f"  Verified: File exists at {save_path}")
    else:
        print(f"  WARNING: File was not created at {save_path}")


def create_convergence_plot(de_no_mm, de_with_mm, func_name, results_dir):
    """Create a plot comparing convergence rates."""
    print(f"  Creating convergence comparison plot for {func_name}...")
    
    # Get the best metrics history from both runs
    no_mm_best_history = de_no_mm.all_bests_metrics.flatten()
    with_mm_best_history = de_with_mm.all_bests_metrics.flatten()
    
    # Create iteration arrays
    no_mm_iters = np.arange(1, len(no_mm_best_history) + 1)
    with_mm_iters = np.arange(1, len(with_mm_best_history) + 1)
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot best metric evolution
    ax.semilogy(no_mm_iters, no_mm_best_history, 'r-', linewidth=2, 
               label=f'Without Metamodel ({de_no_mm.iter} iterations)', alpha=0.8)
    ax.semilogy(with_mm_iters, with_mm_best_history, 'b-', linewidth=2, 
               label=f'With Metamodel ({de_with_mm.iter} iterations)', alpha=0.8)
    
    # Mark threshold if applicable
    if hasattr(de_no_mm, 'metric_threshold') and de_no_mm.metric_threshold is not None:
        ax.axhline(y=de_no_mm.metric_threshold, color='g', linestyle='--', alpha=0.5, 
                  label=f'Threshold ({de_no_mm.metric_threshold})')
    
    ax.set_xlabel('Iteration', fontsize=11)
    ax.set_ylabel('Best Metric (log scale)', fontsize=11)
    ax.set_title(f'Convergence Comparison: {func_name.replace("_", " ").title()}', 
                fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    # Add text box with speedup info
    speedup = de_no_mm.iter / de_with_mm.iter if de_with_mm.iter > 0 else float('inf')
    eval_reduction = 1 - (de_with_mm.nr_evaluations / de_no_mm.nr_evaluations)
    
    textstr = f'Performance Comparison:\n'
    textstr += f'Iterations: {de_no_mm.iter} → {de_with_mm.iter} ({speedup:.1f}x speedup)\n'
    textstr += f'Evaluations: {de_no_mm.nr_evaluations} → {de_with_mm.nr_evaluations} '
    textstr += f'({eval_reduction*100:.1f}% reduction)'
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.02, textstr, transform=ax.transAxes, fontsize=10,
           verticalalignment='bottom', bbox=props)
    
    plt.tight_layout()
    
    # Save the plot
    save_path = os.path.join(results_dir, f'{func_name}_convergence.png')
    print(f"  Saving convergence plot to: {save_path}")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Convergence plot saved successfully!")


def test_function(func_name, main_results_dir=None, config_overrides=None):
    """Test metamodel on a specific function."""
    
    print(f"\n{'='*70}")
    print(f"Testing: {func_name.replace('_', ' ').upper()}")
    print(f"{'='*70}")
    
    # Get function details with n_dim for nD functions
    if func_name in ['ackley_nd', 'rastrigin_nd', 'griewank_nd', 'sphere_nd']:
        func_details = get_function_details(func_name, n_dim=5)  # Use 5D for nD functions
    else:
        func_details = get_function_details(func_name)
    
    eval_func = create_test_function_wrapper(func_details)
    
    # Create parameters directly based on function name (similar to himmelblau test)
    if func_name == 'sphere_2d':
        parameters = Parameters([
            {'name': 'x', 'min': -5.0, 'max': 5.0},
            {'name': 'y', 'min': -5.0, 'max': 5.0}
        ])
    elif func_name == 'himmelblau_2d':
        parameters = Parameters([
            {'name': 'x', 'min': -5.0, 'max': 5.0},
            {'name': 'y', 'min': -5.0, 'max': 5.0}
        ])
    elif func_name == 'rosenbrock_2d':
        parameters = Parameters([
            {'name': 'x', 'min': -2.0, 'max': 2.0},
            {'name': 'y', 'min': -2.0, 'max': 2.0}
        ])
    elif func_name == 'beale_2d':
        parameters = Parameters([
            {'name': 'x', 'min': -4.5, 'max': 4.5},
            {'name': 'y', 'min': -4.5, 'max': 4.5}
        ])
    elif func_name == 'ackley_2d':
        parameters = Parameters([
            {'name': 'x', 'min': -5.0, 'max': 5.0},
            {'name': 'y', 'min': -5.0, 'max': 5.0}
        ])
    elif func_name == 'rastrigin_2d':
        parameters = Parameters([
            {'name': 'x', 'min': -5.12, 'max': 5.12},
            {'name': 'y', 'min': -5.12, 'max': 5.12}
        ])
    elif func_name == 'griewank_2d':
        parameters = Parameters([
            {'name': 'x', 'min': -600.0, 'max': 600.0},
            {'name': 'y', 'min': -600.0, 'max': 600.0}
        ])
    elif func_name in ['sphere_3d', 'sphere_nd']:
        n_dim = 3 if func_name == 'sphere_3d' else 5
        param_list = []
        for i in range(n_dim):
            param_list.append({'name': f'x{i}', 'min': -5.0, 'max': 5.0})
        parameters = Parameters(param_list)
    elif func_name in ['ackley_nd']:
        param_list = []
        for i in range(5):
            param_list.append({'name': f'x{i}', 'min': -5.0, 'max': 5.0})
        parameters = Parameters(param_list)
    elif func_name in ['rastrigin_nd']:
        param_list = []
        for i in range(5):
            param_list.append({'name': f'x{i}', 'min': -5.12, 'max': 5.12})
        parameters = Parameters(param_list)
    elif func_name in ['griewank_nd']:
        param_list = []
        for i in range(5):
            param_list.append({'name': f'x{i}', 'min': -600.0, 'max': 600.0})
        parameters = Parameters(param_list)
    else:
        # Default case - try to extract from bounds
        if 'bounds' in func_details:
            bounds = func_details['bounds']
            param_list = []
            for i, (min_val, max_val) in enumerate(bounds):
                param_list.append({
                    'name': f'x{i}' if len(bounds) > 1 else 'x',
                    'min': min_val,
                    'max': max_val
                })
            parameters = Parameters(param_list)
        else:
            raise ValueError(f"Cannot determine parameters for function {func_name}")
    
    # Function info
    print(f"Dimension: {len(parameters.variable_names)}D")
    if 'optimum_loc' in func_details:
        print(f"Global optimum location: {func_details['optimum_loc']}")
    if 'optimum_val' in func_details:
        print(f"Global optimum value: {func_details['optimum_val']}")
    
    # Create results directory for this function (as subfolder if main_results_dir provided)
    if main_results_dir:
        import os
        results_dir = os.path.join(main_results_dir, func_name)
        os.makedirs(results_dir, exist_ok=True)
        # Also create metamodel_accuracy_plots subfolder
        os.makedirs(os.path.join(results_dir, 'metamodel_accuracy_plots'), exist_ok=True)
    else:
        results_dir = create_test_results_dir(f'metamodel_{func_name}')
    
    # Use same configuration as test_metamodel_himmelblau.py for all functions
    base_config = {
        'seed': 42,
        'opt_min_or_max': 'min',
        'pop_size': 20,  # Same as himmelblau test
        'max_iterations': 100,  # Same as himmelblau test
        'metric_threshold': 0.1,  # Same as himmelblau test
    }
    
    # Metamodel configuration - same for all functions
    config = {
        'mm_min_training_points': 20,  # Same as himmelblau test
        'mm_min_accuracy': 0.7,  # Same as himmelblau test
    }
    
    # Apply any overrides
    if config_overrides:
        config.update(config_overrides)
    
    # Merge with base config
    config.update(base_config)
    
    print(f"\nConfiguration:")
    print(f"  Population size: {config['pop_size']}")
    print(f"  Metric threshold: {config['metric_threshold']}")
    print(f"  MM min training points: {config['mm_min_training_points']}")
    print(f"  MM min accuracy: {config['mm_min_accuracy']}")
    
    # Run without metamodel
    print(f"\n1. Running WITHOUT metamodel...")
    print("-" * 50)
    
    de_no_mm = DifferentialEvolution(
        seed=config['seed'],
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max=config['opt_min_or_max'],
        pop_size=config['pop_size'],
        max_iterations=config['max_iterations'],
        metric_threshold=config['metric_threshold'],
        metamodel_mode='off'
    )
    
    de_no_mm.run_optimization()
    
    print(f"\nResults without metamodel:")
    print(f"  Best metric: {de_no_mm.best_metric:.6f}")
    print(f"  Iterations: {de_no_mm.iter}")
    print(f"  Evaluations: {de_no_mm.nr_evaluations}")
    
    # Run with metamodel
    print(f"\n2. Running WITH metamodel...")
    print("-" * 50)
    
    de_with_mm = DifferentialEvolution(
        seed=config['seed'],
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max=config['opt_min_or_max'],
        pop_size=config['pop_size'],
        max_iterations=config['max_iterations'],
        metric_threshold=config['metric_threshold'],
        metamodel_mode='on',
        metamodel_config={
            'verbose': True,  # Enable verbose output
            'min_training_points': config['mm_min_training_points'],
            'min_accuracy': config['mm_min_accuracy'],
            'show_plots': False,  # Don't block with interactive plots
            'save_plots': True,  # Save plots to files
            'plot_dir': results_dir,  # Directory for saving plots
            'nested_de_config': {
                'max_iterations': 1000,  # More iterations for complex landscape (same as himmelblau)
                'verbose': False,
                'adaptive_iterations': True  # Scale with accuracy (same as himmelblau)
            }
        }
    )
    
    de_with_mm.run_optimization()
    
    print(f"\nResults with metamodel:")
    print(f"  Best metric: {de_with_mm.best_metric:.6f}")
    print(f"  Iterations: {de_with_mm.iter}")
    print(f"  Evaluations: {de_with_mm.nr_evaluations}")
    
    # Get metamodel statistics
    mm_stats = None
    if hasattr(de_with_mm, 'metamodel_manager') and de_with_mm.metamodel_manager:
        mm_stats = de_with_mm.get_metamodel_statistics()
        if mm_stats and mm_stats['is_trained']:
            print(f"  Final MM accuracy: {mm_stats.get('current_accuracy', 0):.3f}")
            print(f"  MM training points: {mm_stats.get('n_training_points', 0)}")
    
    # Calculate improvements
    eval_reduction = (1 - de_with_mm.nr_evaluations / de_no_mm.nr_evaluations) * 100
    iter_speedup = de_no_mm.iter / de_with_mm.iter if de_with_mm.iter > 0 else float('inf')
    
    print(f"\nImprovement:")
    print(f"  Evaluation reduction: {eval_reduction:.1f}%")
    print(f"  Iteration speedup: {iter_speedup:.1f}x")
    
    # Create landscape plot for 2D functions
    if len(parameters.variable_names) == 2:
        print(f"\nCreating plots for {func_name}...")
        try:
            create_landscape_plot(de_no_mm, de_with_mm, func_name, parameters, results_dir)
            print(f"Landscape plot created successfully!")
        except Exception as e:
            print(f"Error creating landscape plot: {e}")
            import traceback
            traceback.print_exc()
        
        # Also create convergence plot
        try:
            create_convergence_plot(de_no_mm, de_with_mm, func_name, results_dir)
            print(f"Convergence plot created successfully!")
        except Exception as e:
            print(f"Error creating convergence plot: {e}")
            import traceback
            traceback.print_exc()
    
    # Return results for summary
    return {
        'function': func_name,
        'dimension': len(parameters.variable_names),
        'no_mm_iters': de_no_mm.iter,
        'no_mm_evals': de_no_mm.nr_evaluations,
        'no_mm_best': de_no_mm.best_metric,
        'with_mm_iters': de_with_mm.iter,
        'with_mm_evals': de_with_mm.nr_evaluations,
        'with_mm_best': de_with_mm.best_metric,
        'eval_reduction': eval_reduction,
        'iter_speedup': iter_speedup,
        'final_mm_accuracy': mm_stats.get('current_accuracy', 0) if mm_stats else 0
    }


def create_summary_plot(results, save_dir):
    """Create a summary plot comparing all functions."""
    
    print("\nCreating summary plots...")
    
    # Prepare data
    functions = [r['function'].replace('_', ' ').title() for r in results]
    eval_reductions = [r['eval_reduction'] for r in results]
    iter_speedups = [r['iter_speedup'] for r in results]
    mm_accuracies = [r['final_mm_accuracy'] for r in results]
    
    # Create figure with subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    
    # Plot 1: Evaluation reduction
    colors = ['green' if r > 50 else 'orange' if r > 0 else 'red' for r in eval_reductions]
    bars1 = ax1.bar(functions, eval_reductions, color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    ax1.set_ylabel('Evaluation Reduction (%)', fontsize=11)
    ax1.set_title('Function Evaluation Reduction with Metamodel', fontsize=12, fontweight='bold')
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax1.axhline(y=50, color='green', linestyle='--', alpha=0.3, label='50% reduction')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(-10, 100)
    ax1.legend()
    
    # Add value labels on bars
    for bar, val in zip(bars1, eval_reductions):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val:.0f}%', ha='center', va='bottom', fontsize=9)
    
    # Plot 2: Iteration speedup
    colors = ['green' if s > 2 else 'orange' if s > 1 else 'red' for s in iter_speedups]
    bars2 = ax2.bar(functions, iter_speedups, color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    ax2.set_ylabel('Iteration Speedup (x)', fontsize=11)
    ax2.set_title('Convergence Speedup with Metamodel', fontsize=12, fontweight='bold')
    ax2.axhline(y=1, color='black', linestyle='-', linewidth=0.5, label='No speedup')
    ax2.axhline(y=2, color='green', linestyle='--', alpha=0.3, label='2x speedup')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.legend()
    
    # Add value labels on bars
    for bar, val in zip(bars2, iter_speedups):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{val:.1f}x', ha='center', va='bottom', fontsize=9)
    
    # Plot 3: Final metamodel accuracy
    colors = ['green' if a > 0.8 else 'orange' if a > 0.6 else 'red' for a in mm_accuracies]
    bars3 = ax3.bar(functions, mm_accuracies, color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    ax3.set_ylabel('Final Metamodel R² Score', fontsize=11)
    ax3.set_xlabel('Test Function', fontsize=11)
    ax3.set_title('Final Metamodel Accuracy', fontsize=12, fontweight='bold')
    ax3.axhline(y=0.8, color='green', linestyle='--', alpha=0.3, label='Good accuracy (0.8)')
    ax3.axhline(y=0.6, color='orange', linestyle='--', alpha=0.3, label='Fair accuracy (0.6)')
    ax3.set_ylim(0, 1.1)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.legend()
    
    # Add value labels on bars
    for bar, val in zip(bars3, mm_accuracies):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{val:.2f}', ha='center', va='bottom', fontsize=9)
    
    # Rotate x-axis labels
    for ax in [ax1, ax2, ax3]:
        ax.set_xticklabels(functions, rotation=45, ha='right')
    
    plt.suptitle('Metamodel Performance Summary Across Test Functions', 
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save plot
    save_path = os.path.join(save_dir, 'metamodel_summary.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Summary plot saved to: {save_path}")


def save_results_json(results, save_dir):
    """Save results to JSON file."""
    save_path = os.path.join(save_dir, 'metamodel_results.json')
    with open(save_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {save_path}")


def main():
    """Run comprehensive metamodel tests."""
    
    print("=" * 70)
    print("COMPREHENSIVE METAMODEL TESTING SUITE")
    print("=" * 70)
    
    # Create main results directory
    main_results_dir = create_test_results_dir('metamodel_comprehensive')
    print(f"\nMain results directory: {main_results_dir}")
    
    # List of test functions from simple to complex
    test_functions = [
        # Simple unimodal functions
        'sphere_2d',
        'rosenbrock_2d',
        
        # Multi-modal functions
        'himmelblau_2d',
        'beale_2d',
        
        # Complex multi-modal functions  
        'griewank_2d',
        
        # Higher dimensional (commented out for faster testing)
        # 'sphere_3d',
        # 'ackley_nd',  # 5D version
        # 'rastrigin_nd',  # 5D version
    ]
    
    # Run tests
    all_results = []
    for func_name in test_functions:
        try:
            result = test_function(func_name, main_results_dir)
            all_results.append(result)
        except Exception as e:
            print(f"\nError testing {func_name}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Create summary
    print("\n" + "=" * 70)
    print("SUMMARY OF RESULTS")
    print("=" * 70)
    
    print("\n{:<20} {:<5} {:<12} {:<12} {:<12} {:<12}".format(
        "Function", "Dim", "Evals w/o MM", "Evals w/ MM", "Reduction", "Speedup"
    ))
    print("-" * 85)
    
    for r in all_results:
        print("{:<20} {:<5} {:<12} {:<12} {:<11.1f}% {:<11.1f}x".format(
            r['function'].replace('_', ' ').title(),
            r['dimension'],
            r['no_mm_evals'],
            r['with_mm_evals'],
            r['eval_reduction'],
            r['iter_speedup']
        ))
    
    # Calculate overall statistics
    avg_reduction = np.mean([r['eval_reduction'] for r in all_results])
    avg_speedup = np.mean([r['iter_speedup'] for r in all_results])
    
    print("-" * 85)
    print(f"\nOverall Performance:")
    print(f"  Average evaluation reduction: {avg_reduction:.1f}%")
    print(f"  Average iteration speedup: {avg_speedup:.1f}x")
    
    # Create summary plots
    create_summary_plot(all_results, main_results_dir)
    
    # Save results to JSON
    save_results_json(all_results, main_results_dir)
    
    print("\n" + "=" * 70)
    print("TESTING COMPLETED!")
    print("=" * 70)
    print(f"\nAll results saved to: {main_results_dir}")


if __name__ == "__main__":
    main()