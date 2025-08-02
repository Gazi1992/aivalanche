"""
Test initial population handling in Differential Evolution.

This test demonstrates different ways to initialize the population:
- Random initialization (default)
- From CSV/JSON files
- From DataFrame
- With default values
- Halton/Sobol sequences
- Handling of out-of-range values
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details

from test_utils import create_test_results_dir, save_test_summary, create_test_function_wrapper


def create_initial_population_files(results_dir):
    """Create sample initial population files for testing."""
    # Create a good initial population (near optimum)
    good_pop = pd.DataFrame({
        'x': np.random.normal(1.0, 0.5, 10),  # Near Rosenbrock optimum
        'y': np.random.normal(1.0, 0.5, 10)
    })
    good_pop_file = os.path.join(results_dir, 'good_initial_pop.csv')
    good_pop.to_csv(good_pop_file, index=False)
    
    # Create a bad initial population (far from optimum)
    bad_pop = pd.DataFrame({
        'x': np.random.uniform(-5, -3, 10),  # Far from optimum
        'y': np.random.uniform(-5, -3, 10)
    })
    bad_pop_file = os.path.join(results_dir, 'bad_initial_pop.csv')
    bad_pop.to_csv(bad_pop_file, index=False)
    
    # Create population with out-of-range values
    out_of_range_pop = pd.DataFrame({
        'x': np.random.uniform(-10, 10, 10),  # Some values outside [-5, 5]
        'y': np.random.uniform(-10, 10, 10)
    })
    out_of_range_file = os.path.join(results_dir, 'out_of_range_pop.csv')
    out_of_range_pop.to_csv(out_of_range_file, index=False)
    
    # Create JSON file with mixed parameters
    mixed_pop = {
        'x': [0.5, 1.0, 1.5, 2.0],
        'y': [0.5, 1.0, 1.5, 2.0],
        'scale': [1.0, 2.0, 1.0, 2.0],
        'mode': ['A', 'B', 'A', 'B']
    }
    mixed_pop_file = os.path.join(results_dir, 'mixed_initial_pop.json')
    pd.DataFrame(mixed_pop).to_json(mixed_pop_file, orient='records')
    
    return {
        'good': good_pop_file,
        'bad': bad_pop_file,
        'out_of_range': out_of_range_file,
        'mixed': mixed_pop_file
    }


def plot_initial_populations(optimizers_dict, results_dir):
    """Plot initial populations from different initialization methods."""
    n_optimizers = len(optimizers_dict)
    fig, axes = plt.subplots(2, (n_optimizers + 1) // 2, figsize=(15, 10))
    axes = axes.flatten()
    
    # Get Rosenbrock function for contour plot
    func_details = get_function_details('rosenbrock_2d')
    func = func_details['func']
    bounds = func_details['bounds']
    
    # Create meshgrid
    x_range = np.linspace(bounds[0][0], bounds[0][1], 100)
    y_range = np.linspace(bounds[1][0], bounds[1][1], 100)
    X, Y = np.meshgrid(x_range, y_range)
    Z = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i, j] = func(np.array([X[i, j], Y[i, j]]))
    
    for idx, (label, optimizer) in enumerate(optimizers_dict.items()):
        ax = axes[idx]
        
        # Plot contours
        contour = ax.contourf(X, Y, Z, levels=20, cmap='viridis', alpha=0.5)
        ax.contour(X, Y, Z, levels=20, colors='black', alpha=0.3, linewidths=0.5)
        
        # Get initial population (first iteration)
        trials = optimizer.history['trials']
        initial_pop = trials[trials['iter'] == 0]
        
        if not initial_pop.empty and 'x' in initial_pop.columns and 'y' in initial_pop.columns:
            scatter = ax.scatter(initial_pop['x'], initial_pop['y'], 
                               c='red', s=50, alpha=0.8, edgecolors='black')
            
            # Add statistics
            mean_x, mean_y = initial_pop['x'].mean(), initial_pop['y'].mean()
            std_x, std_y = initial_pop['x'].std(), initial_pop['y'].std()
            
            ax.scatter(mean_x, mean_y, c='yellow', s=200, marker='*', 
                      edgecolors='black', linewidths=2, label='Mean')
            
            # Add ellipse showing standard deviation
            from matplotlib.patches import Ellipse
            ellipse = Ellipse((mean_x, mean_y), 2*std_x, 2*std_y, 
                            fill=False, edgecolor='yellow', linewidth=2, 
                            linestyle='--', label='2σ')
            ax.add_patch(ellipse)
        
        # Mark optimum
        ax.scatter([1], [1], c='green', s=200, marker='*', 
                  edgecolors='black', linewidths=2, label='Optimum')
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'{label}\n({len(initial_pop)} points)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(bounds[0])
        ax.set_ylim(bounds[1])
    
    # Hide unused subplots
    for idx in range(len(optimizers_dict), len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plot_file = os.path.join(results_dir, 'initial_populations_comparison.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Initial populations plot saved to: {plot_file}")


def test_random_initialization():
    """Test default random initialization."""
    print("\n" + "="*60)
    print("Testing Random Initialization (Default)")
    print("="*60)
    
    params = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # Get Rosenbrock function details and create wrapper
    func_details = get_function_details('rosenbrock_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=params,
        pop_size=30,
        max_iterations=100
    )
    
    optimizer.run_optimization()
    
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Iterations: {optimizer.iter}")
    
    return optimizer


def test_halton_initialization():
    """Test Halton sequence initialization."""
    print("\n" + "="*60)
    print("Testing Halton Sequence Initialization")
    print("="*60)
    
    params = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # Get Rosenbrock function details and create wrapper
    func_details = get_function_details('rosenbrock_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=params,
        pop_size=30,
        max_iterations=100,
        init_pop='halton'  # Use Halton sequence
    )
    
    optimizer.run_optimization()
    
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Iterations: {optimizer.iter}")
    
    return optimizer


def test_csv_initialization(csv_file):
    """Test initialization from CSV file."""
    print("\n" + "="*60)
    print(f"Testing CSV Initialization: {os.path.basename(csv_file)}")
    print("="*60)
    
    params = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # Get Rosenbrock function details and create wrapper
    func_details = get_function_details('rosenbrock_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=params,
        pop_size=30,
        max_iterations=100,
        init_pop=csv_file
    )
    
    optimizer.run_optimization()
    
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Iterations: {optimizer.iter}")
    
    return optimizer


def test_out_of_range_handling(csv_file):
    """Test handling of out-of-range initial values."""
    print("\n" + "="*60)
    print("Testing Out-of-Range Value Handling")
    print("="*60)
    
    params = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # Get Rosenbrock function details and create wrapper
    func_details = get_function_details('rosenbrock_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    # Test with 'keep' strategy
    print("\nStrategy: 'keep' (default)")
    optimizer_keep = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=params,
        pop_size=30,
        max_iterations=100,
        init_pop=csv_file,
        init_pop_out_of_range_param='keep'
    )
    optimizer_keep.run_optimization()
    print(f"Best metric: {optimizer_keep.best_metric:.6f}")
    
    # Test with 'random' strategy
    print("\nStrategy: 'random'")
    optimizer_random = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=params,
        pop_size=30,
        max_iterations=100,
        init_pop=csv_file,
        init_pop_out_of_range_param='random'
    )
    optimizer_random.run_optimization()
    print(f"Best metric: {optimizer_random.best_metric:.6f}")
    
    return optimizer_keep, optimizer_random


def test_default_values_initialization():
    """Test initialization with default parameter values."""
    print("\n" + "="*60)
    print("Testing Default Values in Initial Population")
    print("="*60)
    
    params = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 1.0},  # Default at optimum
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 1.0}
    ])
    
    # Get Rosenbrock function details and create wrapper
    func_details = get_function_details('rosenbrock_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=params,
        pop_size=30,
        max_iterations=100,
        defaults_in_init_pop=True,
        defaults_in_init_pop_ratio=0.3  # 30% of population uses defaults
    )
    
    optimizer.run_optimization()
    
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Iterations: {optimizer.iter}")
    
    return optimizer


def main():
    """Run all initial population tests."""
    print("Initial Population Test Suite")
    print("=" * 60)
    
    # Create results directory
    results_dir = create_test_results_dir('initial_population')
    
    # Create test files
    test_files = create_initial_population_files(results_dir)
    
    # Run tests
    optimizers = {}
    results = {}
    
    # Test 1: Random initialization
    opt_random = test_random_initialization()
    optimizers['Random'] = opt_random
    results['random'] = {
        'best_metric': opt_random.best_metric,
        'iterations': opt_random.iter
    }
    
    # Test 2: Halton sequence
    opt_halton = test_halton_initialization()
    optimizers['Halton'] = opt_halton
    results['halton'] = {
        'best_metric': opt_halton.best_metric,
        'iterations': opt_halton.iter
    }
    
    # Test 3: Good initial population from CSV
    opt_good = test_csv_initialization(test_files['good'])
    optimizers['Good Initial'] = opt_good
    results['good_initial'] = {
        'best_metric': opt_good.best_metric,
        'iterations': opt_good.iter
    }
    
    # Test 4: Bad initial population from CSV
    opt_bad = test_csv_initialization(test_files['bad'])
    optimizers['Bad Initial'] = opt_bad
    results['bad_initial'] = {
        'best_metric': opt_bad.best_metric,
        'iterations': opt_bad.iter
    }
    
    # Test 5: Default values
    opt_defaults = test_default_values_initialization()
    optimizers['With Defaults'] = opt_defaults
    results['with_defaults'] = {
        'best_metric': opt_defaults.best_metric,
        'iterations': opt_defaults.iter
    }
    
    # Test 6: Out-of-range handling
    opt_keep, opt_random_oor = test_out_of_range_handling(test_files['out_of_range'])
    results['out_of_range_keep'] = {
        'best_metric': opt_keep.best_metric,
        'iterations': opt_keep.iter
    }
    results['out_of_range_random'] = {
        'best_metric': opt_random_oor.best_metric,
        'iterations': opt_random_oor.iter
    }
    
    # Create visualizations
    plot_initial_populations(optimizers, results_dir)
    
    # Create convergence comparison plot
    plt.figure(figsize=(12, 6))
    
    for label, optimizer in optimizers.items():
        bests = optimizer.history['bests']
        plt.plot(bests['iter'], bests['metric'], label=label, linewidth=2)
    
    plt.xlabel('Iteration')
    plt.ylabel('Best Metric')
    plt.title('Convergence Comparison - Different Initial Populations')
    plt.legend()
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
    
    convergence_plot = os.path.join(results_dir, 'convergence_comparison.png')
    plt.savefig(convergence_plot, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Create bar chart of final results
    plt.figure(figsize=(10, 6))
    
    labels = list(results.keys())
    metrics = [results[key]['best_metric'] for key in labels]
    colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))
    
    bars = plt.bar(labels, metrics, color=colors)
    plt.xlabel('Initialization Method')
    plt.ylabel('Best Metric (log scale)')
    plt.title('Final Optimization Results by Initialization Method')
    plt.yscale('log')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on bars
    for bar, metric in zip(bars, metrics):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{metric:.2e}', ha='center', va='bottom')
    
    plt.tight_layout()
    bar_plot = os.path.join(results_dir, 'results_comparison.png')
    plt.savefig(bar_plot, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Save test summary
    summary = {
        'test_name': 'Initial Population Test',
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'conclusions': {
            'best_method': min(results.items(), key=lambda x: x[1]['best_metric'])[0],
            'worst_method': max(results.items(), key=lambda x: x[1]['best_metric'])[0],
            'halton_vs_random': (results['random']['best_metric'] - results['halton']['best_metric']) / results['random']['best_metric'] * 100,
            'good_vs_bad_initial': (results['bad_initial']['best_metric'] - results['good_initial']['best_metric']) / results['bad_initial']['best_metric'] * 100
        }
    }
    save_test_summary(results_dir, summary)
    
    print(f"\n{'='*60}")
    print("Test Summary:")
    print(f"Best initialization method: {summary['conclusions']['best_method']}")
    print(f"Worst initialization method: {summary['conclusions']['worst_method']}")
    print(f"Halton vs Random improvement: {summary['conclusions']['halton_vs_random']:.2f}%")
    print(f"Good vs Bad initial improvement: {summary['conclusions']['good_vs_bad_initial']:.2f}%")
    print(f"\nResults saved to: {results_dir}")


if __name__ == "__main__":
    main()