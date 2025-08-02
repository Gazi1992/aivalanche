"""
Test script for Differential Evolution perturbation mechanism using Rastrigin function.

The Rastrigin function is highly multimodal with many local minima, making it ideal
for testing perturbation strategies that help escape local optima.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.optimization.differential_evolution.visualizations import _plot_population_animation
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details, generate_parameters_config


def create_test_function_wrapper(func_details):
    """
    Creates a wrapper function that adapts test functions to the format expected by the optimizer.
    
    Args:
        func_details: Dictionary containing function details from get_function_details
        
    Returns:
        A function that accepts parameters DataFrame and returns list of response dicts
    """
    func = func_details['func']
    dim = func_details['dim']
    
    def wrapper(parameters, **kwargs):
        responses = []
        
        for _, row in parameters.iterrows():
            # Extract parameter values in order (x1, x2, ..., xn)
            x_values = []
            for i in range(dim):
                param_name = f'x{i+1}'
                if param_name in row:
                    x_values.append(row[param_name])
            
            # Convert to numpy array
            x = np.array(x_values)
            
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


class PerturbationMonitor:
    """Monitor to track perturbation events and their effects."""
    
    def __init__(self):
        self.perturbation_events = []
        self.param_stats_history = []
        self.current_iteration = 0
        
    def record_stats(self, de_instance):
        """Record parameter statistics at current iteration."""
        stats = {
            'iteration': de_instance.iter,
            'mean': np.mean(de_instance.trials, axis=0).copy(),
            'std': np.std(de_instance.trials, axis=0).copy(),
            'best_metric': de_instance.best_metric,
            'iter_no_improvement': de_instance.iter_no_improvement
        }
        self.param_stats_history.append(stats)
        
    def record_perturbation_event(self, de_instance, perturbed_params):
        """Record when perturbation occurs."""
        event = {
            'iteration': de_instance.iter,
            'perturbed_params': perturbed_params.copy() if len(perturbed_params) > 0 else [],
            'n_params_perturbed': len(perturbed_params),
            'pre_best_metric': de_instance.best_metric,
            'iter_no_improvement': de_instance.iter_no_improvement
        }
        self.perturbation_events.append(event)
        

def test_perturbation_configurations(n_dim=5, max_iterations=200):
    """
    Test different perturbation configurations on Rastrigin function.
    
    Args:
        n_dim: Number of dimensions for the function
        max_iterations: Maximum iterations for each test
    """
    # Get function details
    func_details = get_function_details('rastrigin_nd', n_dim=n_dim)
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Test configurations
    configs = {
        'no_perturbation': {
            'perturbation_mode': 'off',
        },
        'random_selection': {
            'perturbation_mode': 'custom',
            'perturbation_config': {
                'trigger_ratio': 0.3,
                'param_selection': 'random',
                'param_ratio': 0.4,
                'population_ratio': 0.3,
                'scale': 'adaptive',
                'memory_enabled': False,
                'sigma_threshold': 0.01,
            }
        },
        'variance_selection': {
            'perturbation_mode': 'custom',
            'perturbation_config': {
                'trigger_ratio': 0.3,
                'param_selection': 'variance',
                'param_ratio': 0.4,  # Should be ignored
                'population_ratio': 0.3,
                'scale': 'adaptive',
                'memory_enabled': False,
                'sigma_threshold': 0.02,
            }
        },
        'smart_selection': {
            'perturbation_mode': 'custom',
            'perturbation_config': {
                'trigger_ratio': 0.01,  # Trigger early (after 1% of max_iter_without_improvement)
                'param_selection': 'smart',
                'param_ratio': (0.5, 0.8),  # Perturb 50-80% of parameters
                'population_ratio': (0.4, 0.6),  # Perturb 40-60% of population
                'scale': (0.2, 0.4),  # Large perturbations for visibility
                'memory_enabled': True,
                'cooldown_ratio': 0.2,
                'sigma_threshold': 0.01
            }
        },
        'auto_mode': {
            'perturbation_mode': 'auto',
            'perturbation_config': {
                'scale': 'adaptive_strong',  # Large perturbations for visibility
            }
        },
        'aggressive_mode': {
            'perturbation_mode': 'aggressive',
        }
    }
    
    results = {}
    monitors = {}
    
    # Create results directory
    results_dir = os.path.join(os.path.dirname(__file__), 'test_perturbation_results')
    os.makedirs(results_dir, exist_ok=True)
    
    print(f"\nTesting perturbation strategies on {n_dim}D Rastrigin function")
    print("=" * 70)
    
    for config_name, config in configs.items():
        print(f"\nTesting configuration: {config_name}")
        print("-" * 50)
        
        # Create monitor
        monitor = PerturbationMonitor()
        monitors[config_name] = monitor
        
        # Custom callback to track perturbations
        def callback_after_each_iter(optimizer, **kwargs):
            de_instance = optimizer
            monitor.record_stats(de_instance)
            
            # Check if perturbation occurred (simplified check)
            if hasattr(de_instance, 'perturbation_memory'):
                last_perturb_iter = de_instance.perturbation_memory.get('last_perturbation_iter', -1)
                if last_perturb_iter == de_instance.iter:
                    # Get perturbed parameters (simplified)
                    perturbed_params = []
                    if hasattr(de_instance, '_perturbation_active_config'):
                        # This is a simplified way to track - in reality we'd need to intercept the perturbation
                        pass
                    monitor.record_perturbation_event(de_instance, np.array(perturbed_params))
        
        # Create optimizer
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            opt_min_or_max='min',
            pop_size=10,
            max_iterations=max_iterations,
            metric_threshold=1e-20,
            max_iter_without_improvement=1000,
            improvement_threshold=0.001,
            callback_after_each_iter=callback_after_each_iter,
            results_dir=os.path.join(results_dir, config_name),
            **config
        )
        
        # Run optimization
        optimizer.run_optimization()
        
        # Store results
        results[config_name] = {
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'evaluations': optimizer.nr_evaluations,
            'stop_reason': optimizer.stop_reason,
            'distance_from_optimum': abs(optimizer.best_metric - func_details['optimum_val'])
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6f}")
        print(f"  Iterations: {optimizer.iter}")
        print(f"  Distance from optimum: {results[config_name]['distance_from_optimum']:.6f}")
    
    return results, monitors, results_dir


def plot_perturbation_analysis(monitors, results, results_dir, n_dim):
    """Create visualizations for perturbation analysis."""
    
    # 1. Compare convergence curves
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    for config_name, monitor in monitors.items():
        if monitor.param_stats_history:
            iterations = [s['iteration'] for s in monitor.param_stats_history]
            best_metrics = [s['best_metric'] for s in monitor.param_stats_history]
            ax1.plot(iterations, best_metrics, label=config_name, linewidth=2)
    
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Best Metric')
    ax1.set_title(f'Convergence Comparison on {n_dim}D Rastrigin Function')
    ax1.set_yscale('log')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Show standard deviation evolution for each configuration
    for config_name, monitor in monitors.items():
        if monitor.param_stats_history:
            iterations = [s['iteration'] for s in monitor.param_stats_history]
            avg_stds = [np.mean(s['std']) for s in monitor.param_stats_history]
            ax2.plot(iterations, avg_stds, label=config_name, linewidth=2)
    
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Average Parameter Std Dev')
    ax2.set_title('Population Diversity Evolution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'convergence_comparison.png'), dpi=150)
    plt.close()
    
    # 3. Create parameter distribution plots for select iterations
    configs_to_plot = ['no_perturbation', 'smart_selection', 'aggressive_mode']
    iterations_to_plot = [20, 50, 100, 150]
    
    fig, axes = plt.subplots(len(configs_to_plot), len(iterations_to_plot), 
                            figsize=(16, 12))
    
    for i, config_name in enumerate(configs_to_plot):
        monitor = monitors.get(config_name)
        if not monitor or not monitor.param_stats_history:
            continue
            
        for j, target_iter in enumerate(iterations_to_plot):
            ax = axes[i, j] if len(configs_to_plot) > 1 else axes[j]
            
            # Find closest iteration
            closest_idx = min(range(len(monitor.param_stats_history)), 
                            key=lambda idx: abs(monitor.param_stats_history[idx]['iteration'] - target_iter))
            
            if closest_idx < len(monitor.param_stats_history):
                stats = monitor.param_stats_history[closest_idx]
                actual_iter = stats['iteration']
                
                # Plot parameter standard deviations
                param_stds = stats['std']
                param_names = [f'x{k+1}' for k in range(len(param_stds))]
                
                ax.bar(param_names, param_stds, color='skyblue', edgecolor='navy')
                ax.set_title(f'{config_name}\nIter {actual_iter}')
                ax.set_ylabel('Std Dev')
                ax.set_ylim(0, 0.3)
                
                # Add metric value
                ax.text(0.5, 0.95, f"Metric: {stats['best_metric']:.4f}", 
                       transform=ax.transAxes, ha='center', va='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle('Parameter Standard Deviations Across Iterations', fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'parameter_distributions.png'), dpi=150)
    plt.close()
    
    # 4. Summary table
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Create summary data
    summary_data = []
    for config_name, result in results.items():
        summary_data.append([
            config_name,
            f"{result['best_metric']:.6f}",
            f"{result['distance_from_optimum']:.6f}",
            result['iterations'],
            result['evaluations'],
            result['stop_reason']
        ])
    
    table = ax.table(cellText=summary_data,
                    colLabels=['Configuration', 'Best Metric', 'Distance from Optimum', 
                              'Iterations', 'Evaluations', 'Stop Reason'],
                    cellLoc='center',
                    loc='center')
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    # Color best result
    best_idx = min(range(len(summary_data)), key=lambda i: float(summary_data[i][2]))
    for j in range(len(summary_data[0])):
        table[(best_idx + 1, j)].set_facecolor('#90EE90')
    
    plt.title('Perturbation Strategy Comparison Summary', fontsize=14, pad=20)
    plt.savefig(os.path.join(results_dir, 'summary_table.png'), dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\nVisualization saved to {results_dir}")


def test_perturbation_on_2d_rastrigin_comparison():
    """Test perturbation with 2D Rastrigin - compare with and without perturbation."""
    
    print("\n\nComparing optimization on 2D Rastrigin with and without perturbation")
    print("=" * 70)
    
    # Get function details
    func_details = get_function_details('rastrigin_nd', n_dim=2)
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create results directory
    results_dir = os.path.join(os.path.dirname(__file__), 'test_perturbation_2d_results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Test configurations
    configs = {
        'with_perturbation': {
            'perturbation_mode': 'custom',
            'perturbation_config': {
                'trigger_ratio': 0.01,  # Trigger early (after 1% of max_iter_without_improvement)
                'param_selection': 'smart',
                'param_ratio': (0.5, 0.8),  # Perturb 50-80% of parameters
                'population_ratio': (0.4, 0.6),  # Perturb 40-60% of population
                'scale': (0.2, 0.4),  # Large perturbations for visibility
                'memory_enabled': True,
                'cooldown_ratio': 0.2,
                'sigma_threshold': 0.01
            }
        },
        'without_perturbation': {
            'perturbation_mode': 'off'
        }
    }
    
    results = {}
    
    for config_name, config in configs.items():
        print(f"\n--- Testing {config_name.replace('_', ' ')} ---")
        
        # Track events
        history = []
        
        def callback_after_each_iter(optimizer, **kwargs):
            de_instance = optimizer
            # Simple tracking of population state
            state = {
                'iteration': de_instance.iter,
                'trials': de_instance.trials.copy(),
                'trials_metrics': de_instance.trials_metrics.copy() if hasattr(de_instance, 'trials_metrics') else None,
                'best_metric': de_instance.best_metric,
                'iter_no_improvement': de_instance.iter_no_improvement
            }
            history.append(state)
        
        # Create optimizer
        optimizer = DifferentialEvolution(
            seed=42,  # Same seed for fair comparison
            eval_func=eval_func,
            parameters=parameters,
            opt_min_or_max='min',
            pop_size=30,
            max_iterations=1000,  # Shorter for clearer comparison
            metric_threshold=1e-20,
            max_iter_without_improvement=500,  # More reasonable for comparison
            improvement_threshold=0.001,
            callback_after_each_iter=callback_after_each_iter,
            results_dir=os.path.join(results_dir, config_name),
            **config
        )
        
        # Run optimization
        optimizer.run_optimization()
        
        print(f"Best metric: {optimizer.best_metric:.6f}")
        print(f"Iterations: {optimizer.iter}")
        print(f"Distance from optimum: {abs(optimizer.best_metric - func_details['optimum_val']):.6f}")
        
        # Store results
        results[config_name] = {
            'optimizer': optimizer,
            'history': history,
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter
        }
        
        # Create individual visualization
        sub_dir = os.path.join(results_dir, config_name)
        os.makedirs(sub_dir, exist_ok=True)
        
        print(f"\nCreating animation for {config_name}...")
        create_trials_animation(optimizer, func_details, sub_dir)
        
        # Save diversity plot
        plot_diversity_evolution(history, sub_dir, config_name, optimizer)
    
    # Create comparison plot
    create_comparison_plots(results, func_details, results_dir)
    
    return results


def plot_diversity_evolution(history, results_dir, title_prefix, optimizer=None):
    """Plot diversity evolution for a single run."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    iterations = [h['iteration'] for h in history]
    avg_stds = [np.mean(np.std(h['trials'], axis=0)) for h in history]
    best_metrics = [h['best_metric'] for h in history]
    no_improve = [h['iter_no_improvement'] for h in history]
    
    # Get actual perturbation events if perturbations are enabled
    perturbation_iters = []
    if optimizer and hasattr(optimizer, 'perturbation_mode') and optimizer.perturbation_mode != 'off':
        if hasattr(optimizer, 'perturbation_memory'):
            for event in optimizer.perturbation_memory.get('history', []):
                if 'iteration' in event:
                    perturbation_iters.append(event['iteration'])
    
    ax1.plot(iterations, avg_stds, 'b-', linewidth=2, label='Avg Std Dev')
    ax1.set_ylabel('Average Std Dev', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_xlabel('Iteration')
    ax1.grid(True, alpha=0.3)
    
    # Mark perturbation events
    for i, p_iter in enumerate(perturbation_iters):
        if p_iter < len(iterations):
            ax1.axvline(x=p_iter, color='red', linestyle='--', alpha=0.5,
                       label='Perturbation' if i == 0 else '')
    
    ax1_twin = ax1.twinx()
    ax1_twin.plot(iterations, no_improve, 'g-', linewidth=1, alpha=0.7)
    ax1_twin.set_ylabel('Iterations Without Improvement', color='g')
    ax1_twin.tick_params(axis='y', labelcolor='g')
    
    if perturbation_iters:
        ax1.legend(loc='upper left')
    
    ax2.semilogy(iterations, best_metrics, 'r-', linewidth=2)
    ax2.set_ylabel('Best Metric (log scale)')
    ax2.set_xlabel('Iteration')
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(f'{title_prefix.replace("_", " ").title()} - Diversity and Convergence', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'diversity_evolution.png'), dpi=150)
    plt.close()


def create_comparison_plots(results, func_details, results_dir):
    """Create comparison plots between runs with and without perturbation."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Convergence comparison
    for config_name, result in results.items():
        history = result['history']
        iterations = [h['iteration'] for h in history]
        best_metrics = [h['best_metric'] for h in history]
        ax1.semilogy(iterations, best_metrics, linewidth=2, 
                    label=config_name.replace('_', ' ').title())
    
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Best Metric (log scale)')
    ax1.set_title('Convergence Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Diversity comparison
    for config_name, result in results.items():
        history = result['history']
        iterations = [h['iteration'] for h in history]
        avg_stds = [np.mean(np.std(h['trials'], axis=0)) for h in history]
        ax2.plot(iterations, avg_stds, linewidth=2,
                label=config_name.replace('_', ' ').title())
    
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Average Std Dev')
    ax2.set_title('Population Diversity Comparison')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3 & 4: Final population distributions
    for idx, (config_name, result) in enumerate(results.items()):
        ax = ax3 if idx == 0 else ax4
        
        # Get final population
        optimizer = result['optimizer']
        final_survivors = optimizer.survivors
        
        # Get bounds
        bounds = func_details['bounds']
        x_min, x_max = bounds[0]
        y_min, y_max = bounds[1]
        
        # Create landscape
        x = np.linspace(x_min, x_max, 100)
        y = np.linspace(y_min, y_max, 100)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)
        
        func = func_details['func']
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                Z[i, j] = func(np.array([X[i, j], Y[i, j]]))
        
        # Plot landscape
        ax.contourf(X, Y, np.log10(Z + 1e-10), levels=50, cmap='viridis', alpha=0.7)
        ax.contour(X, Y, np.log10(Z + 1e-10), levels=20, colors='black', alpha=0.2, linewidths=0.5)
        
        # Plot final population
        survivors_x = final_survivors[:, 0] * (x_max - x_min) + x_min
        survivors_y = final_survivors[:, 1] * (y_max - y_min) + y_min
        ax.scatter(survivors_x, survivors_y, color='white', s=60, 
                  edgecolor='black', linewidth=1, zorder=5)
        
        # Mark best
        best = optimizer.best_parameters
        best_x = best['x1']
        best_y = best['x2']
        ax.scatter(best_x, best_y, color='yellow', s=200, marker='*',
                  edgecolor='orange', linewidth=2, zorder=10)
        
        # Mark global optimum
        ax.plot(0, 0, 'r*', markersize=20, markeredgewidth=2, 
               markeredgecolor='darkred', zorder=10)
        
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel('x1')
        ax.set_ylabel('x2')
        ax.set_title(f'Final Population - {config_name.replace("_", " ").title()}\n' +
                    f'Best: {result["best_metric"]:.6f}')
        ax.set_aspect('equal')
    
    plt.suptitle('Perturbation vs No Perturbation Comparison on 2D Rastrigin', fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'comparison_summary.png'), dpi=150)
    plt.close()
    
    print(f"\nComparison plots saved to {results_dir}")


def test_perturbation_on_2d_rastrigin():
    """Wrapper for backward compatibility."""
    results = test_perturbation_on_2d_rastrigin_comparison()
    # Return the with_perturbation results for compatibility
    return results['with_perturbation']['optimizer'], results['with_perturbation']['history']


def create_trials_animation(optimizer, func_details, results_dir):
    """Create animation showing trials spreading during perturbations."""
    
    # Check if we have 2D data
    if optimizer.nr_variable_parameters != 2:
        print("Animation only supported for 2D functions")
        return
    
    # Get all trials history
    all_trials = optimizer.all_trials
    all_survivors = optimizer.all_survivors
    all_bests = optimizer.all_bests
    all_bests_metrics = optimizer.all_bests_metrics
    
    # Get parameter names
    param_names = optimizer.variable_parameters_names[:2]
    x_param = param_names[0]
    y_param = param_names[1]
    
    # Get bounds for denormalization
    bounds = func_details['bounds']
    x_min, x_max = bounds[0]
    y_min, y_max = bounds[1]
    
    # Create function landscape
    grid_size = 100
    x = np.linspace(x_min, x_max, grid_size)
    y = np.linspace(y_min, y_max, grid_size)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    
    func = func_details['func']
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i, j] = func(np.array([X[i, j], Y[i, j]]))
    
    # Apply log scale for better visualization
    Z_log = np.log10(Z + 1e-10)
    
    # Track actual perturbation events from the optimizer's perturbation memory
    perturbation_iters = []
    if optimizer.perturbation_mode != 'off' and hasattr(optimizer, 'perturbation_memory'):
        # Get iterations where perturbations were applied from the history
        for event in optimizer.perturbation_memory.get('history', []):
            if 'iteration' in event:
                perturbation_iters.append(event['iteration'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))
    
    def init():
        """Initialize animation."""
        ax.clear()
        
        # Plot heatmap
        ax.contourf(X, Y, Z_log, levels=50, cmap='viridis', alpha=0.7)
        ax.contour(X, Y, Z_log, levels=20, colors='black', alpha=0.2, linewidths=0.5)
        
        # Mark global optimum
        ax.plot(0, 0, 'r*', markersize=20, markeredgewidth=2, markeredgecolor='darkred', 
                label='Global Optimum', zorder=10)
        
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel(f'{x_param}', fontsize=12)
        ax.set_ylabel(f'{y_param}', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        return []
    
    def animate(frame):
        """Animation function for each frame."""
        ax.clear()
        
        # Plot heatmap
        ax.contourf(X, Y, Z_log, levels=50, cmap='viridis', alpha=0.7)
        ax.contour(X, Y, Z_log, levels=20, colors='black', alpha=0.2, linewidths=0.5)
        
        # Mark global optimum
        ax.plot(0, 0, 'r*', markersize=20, markeredgewidth=2, markeredgecolor='darkred', 
                label='Global Optimum', zorder=10)
        
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel(f'{x_param}', fontsize=12)
        ax.set_ylabel(f'{y_param}', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        # Get current trials and survivors
        if frame < len(all_trials):
            current_trials = all_trials[frame]
            # Denormalize positions
            trials_x = current_trials[:, 0] * (x_max - x_min) + x_min
            trials_y = current_trials[:, 1] * (y_max - y_min) + y_min
            
            # Plot trials
            ax.scatter(trials_x, trials_y, 
                      color='cyan', s=40, alpha=0.6, edgecolor='blue', linewidth=0.5,
                      label='Trials', zorder=3)
        
        if frame < len(all_survivors):
            current_survivors = all_survivors[frame]
            # Denormalize positions
            survivors_x = current_survivors[:, 0] * (x_max - x_min) + x_min
            survivors_y = current_survivors[:, 1] * (y_max - y_min) + y_min
            
            # Plot survivors
            ax.scatter(survivors_x, survivors_y, 
                      color='white', s=60, edgecolor='black', linewidth=1,
                      label='Survivors', zorder=5)
        
        # Mark best point
        if frame < len(all_bests):
            best_point = all_bests[frame]
            best_x = best_point[0] * (x_max - x_min) + x_min
            best_y = best_point[1] * (y_max - y_min) + y_min
            ax.scatter(best_x, best_y, 
                      color='yellow', s=200, marker='*', edgecolor='orange', linewidth=2,
                      label=f'Best (metric={all_bests_metrics[frame, 0]:.2e})', zorder=10)
        
        # Calculate diversity
        if frame < len(all_trials):
            trials_std = np.mean(np.std(all_trials[frame], axis=0))
        else:
            trials_std = 0
            
        # Mark if this is a perturbation event
        title_color = 'red' if frame in perturbation_iters else 'black'
        perturbation_text = ' (PERTURBATION!)' if frame in perturbation_iters else ''
        
        # Update title with diversity info
        ax.set_title(f'Differential Evolution - Iteration {frame+1}{perturbation_text}\n' + 
                    f'Trials Diversity (avg std): {trials_std:.4f}', 
                    fontsize=14, color=title_color, fontweight='bold' if frame in perturbation_iters else 'normal')
        
        # Add legend
        ax.legend(loc='upper right')
        
        return []
    
    # Create animation
    n_frames = len(all_trials)
    anim = FuncAnimation(fig, animate, init_func=init, frames=n_frames,
                        interval=150, blit=False, repeat=True)
    
    # Save animation
    save_path = os.path.join(results_dir, 'perturbation_trials_animation.gif')
    writer = PillowWriter(fps=8)
    anim.save(save_path, writer=writer)
    print(f"Animation saved to: {save_path}")
    
    # Also save key frames
    key_frames = [0] + perturbation_iters[:3] + [n_frames-1]
    key_frames = sorted(list(set([f for f in key_frames if 0 <= f < n_frames])))
    
    for frame_idx in key_frames:
        animate(frame_idx)
        plt.savefig(os.path.join(results_dir, f'frame_{frame_idx:04d}.png'), dpi=150, bbox_inches='tight')
    
    plt.close(fig)
    
    return anim


def create_2d_perturbation_visualization(optimizer, history, func_details, results_dir):
    """Create visualization showing perturbation effects on 2D function."""
    
    # Create the animation
    print("\nCreating perturbation animation...")
    create_trials_animation(optimizer, func_details, results_dir)
    
    # Plot diversity evolution
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    iterations = [h['iteration'] for h in history]
    avg_stds = [np.mean(np.std(h['trials'], axis=0)) for h in history]
    best_metrics = [h['best_metric'] for h in history]
    no_improve = [h['iter_no_improvement'] for h in history]
    
    # Get actual perturbation events if perturbations are enabled
    perturbation_iters = []
    if hasattr(optimizer, 'perturbation_mode') and optimizer.perturbation_mode != 'off':
        if hasattr(optimizer, 'perturbation_memory'):
            for event in optimizer.perturbation_memory.get('history', []):
                if 'iteration' in event:
                    perturbation_iters.append(event['iteration'])
    
    ax1.plot(iterations, avg_stds, 'b-', linewidth=2, label='Avg Std Dev')
    ax1.set_ylabel('Average Std Dev', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_xlabel('Iteration')
    ax1.grid(True, alpha=0.3)
    
    # Mark perturbation events
    for i, p_iter in enumerate(perturbation_iters):
        if p_iter < len(iterations):
            ax1.axvline(x=p_iter, color='red', linestyle='--', alpha=0.5, 
                       label='Perturbation' if i == 0 else '')
    
    ax1_twin = ax1.twinx()
    ax1_twin.plot(iterations, no_improve, 'g-', linewidth=1, alpha=0.7, label='Iter No Improvement')
    ax1_twin.set_ylabel('Iterations Without Improvement', color='g')
    ax1_twin.tick_params(axis='y', labelcolor='g')
    
    # Add legend for ax1
    if perturbation_iters:
        ax1.legend(loc='upper left')
    
    ax2.semilogy(iterations, best_metrics, 'r-', linewidth=2)
    ax2.set_ylabel('Best Metric (log scale)')
    ax2.set_xlabel('Iteration')
    ax2.grid(True, alpha=0.3)
    
    # Mark perturbation events on metric plot too
    for p_iter in perturbation_iters:
        if p_iter < len(iterations):
            ax2.axvline(x=p_iter, color='red', linestyle='--', alpha=0.3)
    
    plt.suptitle('Diversity and Convergence Analysis', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'diversity_evolution.png'), dpi=150)
    plt.close()
    
    print(f"\n2D visualization saved to {results_dir}")


if __name__ == "__main__":
    # Test different perturbation configurations on 5D Rastrigin
    results, monitors, results_dir = test_perturbation_configurations(n_dim=5, max_iterations=1000)
    
    # Create analysis plots
    plot_perturbation_analysis(monitors, results, results_dir, n_dim=5)
    
    # Also test on 2D for better visualization
    optimizer_2d, history_2d = test_perturbation_on_2d_rastrigin()
    
    print("\n\nPerturbation testing completed!")
    print(f"Results saved to test_perturbation_results/ and test_perturbation_2d_results/")