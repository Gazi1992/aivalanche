"""
Test Differential Evolution on a complex high-dimensional problem.

This test evaluates DE performance on 20D Rastrigin function with:
- Visualization of the global optimum vs found solution
- Parameter evolution plots
- 2D projection animation
- Comprehensive performance metrics
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
from aivalanche_lib.test_functions import get_function_details

from test_utils import create_test_results_dir, save_test_summary, create_test_function_wrapper


def test_complex_rastrigin_20d():
    """Test DE on 20D Rastrigin function."""
    print("\n" + "="*60)
    print("Testing DE on Complex 20D Rastrigin Function")
    print("="*60)
    
    n_dim = 20
    func_details = get_function_details('rastrigin_nd', n_dim=n_dim)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create 20D parameters
    params_list = []
    for i in range(n_dim):
        params_list.append({
            'name': f'x{i}',
            'type': 'continuous',
            'min': -5.12,
            'max': 5.12,
            'default': 0.0
        })
    parameters = Parameters(params_list)
    
    # Define callback for better solution found
    def on_better_solution(optimizer, iteration, best_metric, **kwargs):
        """Callback when a better solution is found."""
        print(f"  Iteration {iteration}: New best = {best_metric:.6f}")
    
    # Run DE with appropriate settings for high dimensions
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        pop_size=20,  # 5x dimensions
        max_iterations=20000,
        max_iter_without_improvement=2000,
        adaptive_boundaries=True,
        callback_after_better_solution=on_better_solution
    )
    
    print(f"\nConfiguration:")
    print(f"  Population size: {optimizer.pop_size}")
    print(f"  Max iterations: {optimizer.max_iterations}")
    print(f"  Adaptive boundaries: {optimizer.adaptive_boundaries}")
    
    # Run optimization
    optimizer.run_optimization()
    
    print(f"\nOptimization Results:")
    print(f"  Best metric found: {optimizer.best_metric:.6f}")
    print(f"  Global optimum: 0.0")
    print(f"  Distance from optimum: {optimizer.best_metric:.6f}")
    print(f"  Iterations: {optimizer.iter}")
    print(f"  Stop reason: {optimizer.stop_reason}")
    
    # Calculate distance of each parameter from optimum (0.0)
    param_distances = []
    for i, param_name in enumerate(optimizer.variable_parameters_names):
        value = optimizer.best_parameters[param_name]
        distance = abs(value - 0.0)  # Optimum is at 0.0 for all parameters
        param_distances.append((param_name, value, distance))
    
    # Sort by distance to see which parameters are furthest from optimum
    param_distances.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\nParameter Analysis (top 5 furthest from optimum):")
    for param_name, value, distance in param_distances[:5]:
        print(f"  {param_name}: {value:8.4f} (distance: {distance:.4f})")
    
    return optimizer, param_distances


def create_complex_problem_visualization(optimizer, param_distances, results_dir):
    """Create comprehensive visualization for complex problem."""
    
    history = optimizer.history
    bests = history['bests']
    trials = history['trials']
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 15))
    
    # Layout: 3x3 grid
    # Row 1: Convergence, Parameter distances, Parameter values
    # Row 2: 2D projection plots (3 different pairs)
    # Row 3: Parameter evolution, All parameters evolution, Summary
    
    # 1. Convergence plot
    ax1 = plt.subplot(3, 3, 1)
    ax1.plot(bests['iter'], bests['metric'], 'b-', linewidth=2)
    ax1.axhline(y=0, color='red', linestyle='--', linewidth=2, label='Global Optimum')
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Best Metric')
    ax1.set_title('Convergence to Global Optimum')
    ax1.set_yscale('log')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Parameter distances from optimum
    ax2 = plt.subplot(3, 3, 2)
    param_names = [p[0] for p in param_distances]
    distances = [p[2] for p in param_distances]
    colors = ['red' if d > 1.0 else 'orange' if d > 0.5 else 'green' for d in distances]
    
    bars = ax2.bar(range(len(param_names)), distances, color=colors)
    ax2.set_xticks(range(len(param_names)))
    ax2.set_xticklabels(param_names, rotation=90)
    ax2.set_ylabel('Distance from Optimum (0.0)')
    ax2.set_title('Parameter Distances from Global Optimum')
    ax2.grid(True, alpha=0.3)
    
    # 3. Parameter values with optimum line
    ax3 = plt.subplot(3, 3, 3)
    values = [p[1] for p in param_distances]
    ax3.scatter(range(len(param_names)), values, s=50, c='blue', alpha=0.6)
    ax3.axhline(y=0, color='red', linestyle='--', linewidth=2, label='Optimum')
    ax3.set_xticks(range(len(param_names)))
    ax3.set_xticklabels(param_names, rotation=90)
    ax3.set_ylabel('Parameter Value')
    ax3.set_title('Found Parameter Values vs Optimum')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4-6. 2D projections at final iteration
    final_iter = optimizer.iter
    final_trials = trials[trials['iter'] == final_iter]
    
    projections = [(0, 1), (0, 10), (10, 19)]  # Different parameter pairs
    
    for idx, (i, j) in enumerate(projections):
        ax = plt.subplot(3, 3, 4 + idx)
        
        # Plot population
        ax.scatter(final_trials[f'x{i}'], final_trials[f'x{j}'], 
                  c='blue', alpha=0.5, s=30, label='Population')
        
        # Plot best solution
        ax.scatter(optimizer.best_parameters[f'x{i}'], 
                  optimizer.best_parameters[f'x{j}'],
                  c='green', s=200, marker='*', edgecolor='black', 
                  linewidth=2, label='Best Found', zorder=10)
        
        # Plot global optimum
        ax.scatter(0, 0, c='red', s=200, marker='X', edgecolor='black',
                  linewidth=2, label='Global Optimum', zorder=11)
        
        ax.set_xlabel(f'x{i}')
        ax.set_ylabel(f'x{j}')
        ax.set_title(f'2D Projection: x{i} vs x{j}')
        ax.set_xlim(-5.12, 5.12)
        ax.set_ylim(-5.12, 5.12)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # 7. Parameter evolution (first 5 parameters)
    ax7 = plt.subplot(3, 3, 7)
    # Plot parameter evolution manually
    iterations = sorted(trials['iter'].unique())
    params_to_plot = [f'x{i}' for i in range(5)]
    for param in params_to_plot:
        if param in trials.columns:
            means = []
            for iter_num in iterations[::10]:  # Sample every 10th iteration
                iter_data = trials[trials['iter'] == iter_num]
                means.append(iter_data[param].mean())
            ax7.plot(iterations[::10], means, label=param, linewidth=1.5)
    ax7.set_xlabel('Iteration')
    ax7.set_ylabel('Mean Parameter Value')
    ax7.set_title('Parameter Evolution (First 5)')
    ax7.legend(fontsize=8)
    ax7.grid(True, alpha=0.3)
    
    # 8. All parameters boxplot
    ax8 = plt.subplot(3, 3, 8)
    # Show final parameter distribution
    final_trials = trials[trials['iter'] == optimizer.iter]
    param_cols = [col for col in final_trials.columns if col.startswith('x')]
    final_values = []
    param_labels = []
    for col in param_cols:
        final_values.append(final_trials[col].values)
        param_labels.append(col)
    
    bp = ax8.boxplot(final_values, labels=param_labels, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
    ax8.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.7)
    ax8.set_ylabel('Parameter Value')
    ax8.set_title('Final Parameter Distribution')
    ax8.tick_params(axis='x', rotation=90)
    ax8.grid(True, alpha=0.3)
    
    # 9. Summary statistics
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    # Calculate statistics
    avg_distance = np.mean([p[2] for p in param_distances])
    max_distance = max([p[2] for p in param_distances])
    params_near_optimum = sum(1 for p in param_distances if p[2] < 0.1)
    
    summary_text = f"""20D Rastrigin Optimization Summary
    
Global Optimum: f(0, 0, ..., 0) = 0.0
Found Solution: f({optimizer.best_metric:.4f})

Performance Metrics:
  Final Best: {optimizer.best_metric:.4f}
  Iterations: {optimizer.iter}
  Evaluations: {optimizer.nr_evaluations}
  
Parameter Analysis:
  Avg distance from optimum: {avg_distance:.4f}
  Max distance from optimum: {max_distance:.4f}
  Parameters near optimum (<0.1): {params_near_optimum}/{len(param_distances)}
  
Convergence:
  Initial best: {bests['metric'].iloc[0]:.4f}
  Final best: {optimizer.best_metric:.4f}
  Improvement: {(bests['metric'].iloc[0] - optimizer.best_metric) / bests['metric'].iloc[0] * 100:.1f}%
"""
    
    ax9.text(0.05, 0.95, summary_text, transform=ax9.transAxes,
             fontsize=11, va='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.suptitle('DE Performance on 20D Rastrigin Function', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'complex_problem_analysis.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\nVisualization saved to: {plot_file}")


def create_2d_animation(optimizer, param_indices=(0, 1), results_dir=None):
    """Create 2D animation for selected parameter pair."""
    
    print(f"\nCreating 2D animation for parameters x{param_indices[0]} and x{param_indices[1]}...")
    
    history = optimizer.history
    trials = history['trials']
    bests = history['bests']
    
    # Setup figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    # Left plot: 2D parameter space
    ax1.set_xlim(-5.12, 5.12)
    ax1.set_ylim(-5.12, 5.12)
    ax1.set_xlabel(f'x{param_indices[0]}')
    ax1.set_ylabel(f'x{param_indices[1]}')
    ax1.set_title('Population in 2D Projection')
    ax1.grid(True, alpha=0.3)
    
    # Plot global optimum (fixed)
    ax1.scatter(0, 0, c='red', s=200, marker='X', edgecolor='black',
               linewidth=2, label='Global Optimum', zorder=5)
    
    # Initialize scatter plots
    pop_scatter = ax1.scatter([], [], c='blue', alpha=0.5, s=30, label='Population')
    best_scatter = ax1.scatter([], [], c='green', s=150, marker='*', 
                              edgecolor='black', linewidth=2, label='Current Best', zorder=10)
    
    ax1.legend()
    
    # Right plot: Convergence
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Best Metric')
    ax2.set_title('Convergence')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    
    line, = ax2.plot([], [], 'b-', linewidth=2)
    
    # Text elements
    iter_text = ax1.text(0.02, 0.98, '', transform=ax1.transAxes, 
                        va='top', bbox=dict(boxstyle='round', facecolor='wheat'))
    
    # Get iterations
    iterations = sorted(trials['iter'].unique())
    
    def init():
        pop_scatter.set_offsets(np.empty((0, 2)))
        best_scatter.set_offsets(np.empty((0, 2)))
        line.set_data([], [])
        iter_text.set_text('')
        return pop_scatter, best_scatter, line, iter_text
    
    def animate(frame_idx):
        if frame_idx >= len(iterations):
            return pop_scatter, best_scatter, line, iter_text
            
        current_iter = iterations[frame_idx]
        
        # Get current population
        iter_trials = trials[trials['iter'] == current_iter]
        
        # Update population scatter
        pop_data = np.c_[iter_trials[f'x{param_indices[0]}'], 
                        iter_trials[f'x{param_indices[1]}']]
        pop_scatter.set_offsets(pop_data)
        
        # Update best point
        best_up_to = bests[bests['iter'] <= current_iter]
        if not best_up_to.empty:
            last_best = best_up_to.iloc[-1]
            best_x = last_best[f'x{param_indices[0]}']
            best_y = last_best[f'x{param_indices[1]}']
            best_scatter.set_offsets([[best_x, best_y]])
            
            # Update convergence plot
            line.set_data(best_up_to['iter'], best_up_to['metric'])
            ax2.set_xlim(0, max(10, current_iter))
            y_min = best_up_to['metric'].min() * 0.5
            y_max = best_up_to['metric'].max() * 2
            ax2.set_ylim(y_min, y_max)
            
            # Update text
            iter_text.set_text(f'Iteration: {current_iter}\nBest: {last_best["metric"]:.4f}')
        
        return pop_scatter, best_scatter, line, iter_text
    
    # Create animation
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                  frames=len(iterations), interval=50,
                                  blit=True, repeat=True)
    
    # Save animation
    anim_file = os.path.join(results_dir, 'complex_problem_2d.gif')
    anim.save(anim_file, writer='pillow', fps=10)
    plt.close()
    
    print(f"Animation saved to: {anim_file}")


def main():
    """Run complex problem test."""
    print("Differential Evolution Complex Problem Test")
    print("=" * 60)
    
    # Create results directory
    results_dir = create_test_results_dir('complex_problem')
    
    # Run test
    optimizer, param_distances = test_complex_rastrigin_20d()
    
    # Save history
    history = optimizer.history
    for key, df in history.items():
        if isinstance(df, pd.DataFrame):
            df.to_csv(os.path.join(results_dir, f'history_{key}.csv'), index=False)
    
    # Create visualizations
    create_complex_problem_visualization(optimizer, param_distances, results_dir)
    
    # Create parameter evolution plots using DE's visualization functions
    print("\nCreating parameter evolution plots...")
    
    from aivalanche_lib.optimization.differential_evolution.visualizations import (
        _plot_metrics_evolution, _plot_parameters_evolution, _plot_all_parameters_evolution
    )
    
    # Plot metric evolution
    bests_df = optimizer.history['bests']
    fig_metric, _ = _plot_metrics_evolution(
        iterations=bests_df['iter'].values,
        metrics=bests_df['metric'].values,
        title='20D Rastrigin - Metric Evolution'
    )
    fig_metric.savefig(os.path.join(results_dir, 'metric_evolution.png'), dpi=150, bbox_inches='tight')
    plt.close(fig_metric)
    
    # Plot parameters evolution (using trials for better visibility)
    # Select a subset of parameters to plot (first 5)
    trials_df = optimizer.history['trials']
    param_names = [f'x{i}' for i in range(5)]
    fig_params, _ = _plot_parameters_evolution(
        df=trials_df,
        parameter_names=param_names,
        title='20D Rastrigin - Parameters Evolution (x0-x4)'
    )
    fig_params.savefig(os.path.join(results_dir, 'parameters_evolution.png'), dpi=150, bbox_inches='tight')
    plt.close(fig_params)
    
    # Plot all parameters evolution
    fig_all_params, _ = _plot_all_parameters_evolution(
        df=trials_df,
        title='20D Rastrigin - All Parameters Evolution'
    )
    fig_all_params.savefig(os.path.join(results_dir, 'all_parameters_evolution.png'), dpi=150, bbox_inches='tight')
    plt.close(fig_all_params)
    
    # Create 2D animation for first two parameters
    create_2d_animation(optimizer, param_indices=(0, 1), results_dir=results_dir)
    
    # Save test summary
    summary = {
        'test_name': 'DE Complex Problem Test - 20D Rastrigin',
        'timestamp': datetime.now().isoformat(),
        'configuration': {
            'dimensions': 20,
            'population_size': optimizer.pop_size,
            'max_iterations': optimizer.max_iterations,
            'adaptive_boundaries': optimizer.adaptive_boundaries
        },
        'results': {
            'best_metric': optimizer.best_metric,
            'global_optimum': 0.0,
            'distance_from_optimum': optimizer.best_metric,
            'iterations': optimizer.iter,
            'evaluations': optimizer.nr_evaluations,
            'stop_reason': optimizer.stop_reason
        },
        'parameter_analysis': {
            'average_distance_from_optimum': np.mean([p[2] for p in param_distances]),
            'max_distance_from_optimum': max([p[2] for p in param_distances]),
            'parameters_near_optimum': sum(1 for p in param_distances if p[2] < 0.1),
            'best_parameters': optimizer.best_parameters
        }
    }
    save_test_summary(results_dir, summary)
    
    print(f"\n{'='*60}")
    print("Test completed successfully!")
    print(f"Results saved to: {results_dir}")


if __name__ == "__main__":
    main()