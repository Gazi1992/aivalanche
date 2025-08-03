"""
Test adaptive boundaries feature of Differential Evolution.

This test demonstrates how adaptive boundaries help when the population
converges near parameter boundaries, dynamically extending the search space.
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


def create_shifted_rosenbrock():
    """Create a Rosenbrock function shifted so optimum is OUTSIDE initial boundaries."""
    def shifted_rosenbrock(parameters, **kwargs):
        """Rosenbrock shifted to have optimum at (7.0, 7.0) - outside [-5, 5] bounds"""
        responses = []
        for _, row in parameters.iterrows():
            x = row['x'] - 6.0  # Shift optimum from (1,1) to (7.0, 7.0)
            y = row['y'] - 6.0
            value = (1 - x)**2 + 100 * (y - x**2)**2
            responses.append({'metric': value})
        return responses
    
    return shifted_rosenbrock


def plot_boundary_evolution(optimizer, results_dir):
    """Plot how boundaries evolve during optimization using the DE visualization format."""
    from aivalanche_lib.optimization.differential_evolution.visualizations import _plot_boundaries_evolution
    
    # Get the boundaries DataFrame from history
    all_boundaries = optimizer.all_boundaries
    
    if all_boundaries.empty:
        print("No boundary history available")
        return
    
    # Create the plot using the DE visualization function
    fig, axes = _plot_boundaries_evolution(
        df=all_boundaries,
        parameter_names=optimizer.variable_parameters_names[:4],  # Plot up to 4 parameters
        title="Adaptive Boundaries Evolution",
        save_path=os.path.join(results_dir, 'boundary_evolution.png'),
        nr_rows=2 if len(optimizer.variable_parameters_names) > 2 else 1,
        normalized=False  # Use original units
    )
    
    print(f"Boundary evolution plot saved to: {os.path.join(results_dir, 'boundary_evolution.png')}")
    
    # Also create a custom plot showing population distribution
    fig2, axes2 = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot convergence with boundary changes marked
    ax1 = axes2[0]
    bests = optimizer.history['bests']
    ax1.plot(bests['iter'], bests['metric'], 'b-', linewidth=2)
    
    # Mark iterations where boundaries were extended
    boundary_changes = all_boundaries.index.get_level_values('iter').unique()[1:]  # Skip initial
    for iter_change in boundary_changes:
        ax1.axvline(iter_change, color='red', linestyle='--', alpha=0.5)
    
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Best Metric')
    ax1.set_title('Convergence with Boundary Extensions')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Plot final population distribution
    ax2 = axes2[1]
    trials = optimizer.history['trials']
    final_iter = trials['iter'].max()
    final_pop = trials[trials['iter'] == final_iter]
    
    if 'x' in final_pop.columns and 'y' in final_pop.columns:
        scatter = ax2.scatter(final_pop['x'], final_pop['y'], c='blue', s=50, alpha=0.6, label='Final Population')
        
        # Show initial and final boundaries
        initial_min_x = all_boundaries.loc[(0, 'min'), 'x']
        initial_max_x = all_boundaries.loc[(0, 'max'), 'x']
        initial_min_y = all_boundaries.loc[(0, 'min'), 'y']
        initial_max_y = all_boundaries.loc[(0, 'max'), 'y']
        
        # Get the last iteration with boundary data
        all_iters = all_boundaries.index.get_level_values('iter').unique()
        last_boundary_iter = max(all_iters)
        
        final_min_x = all_boundaries.loc[(last_boundary_iter, 'min'), 'x']
        final_max_x = all_boundaries.loc[(last_boundary_iter, 'max'), 'x']
        final_min_y = all_boundaries.loc[(last_boundary_iter, 'min'), 'y']
        final_max_y = all_boundaries.loc[(last_boundary_iter, 'max'), 'y']
        
        # Draw boundary rectangles
        from matplotlib.patches import Rectangle
        
        # Initial boundaries
        initial_rect = Rectangle((initial_min_x, initial_min_y), 
                                initial_max_x - initial_min_x,
                                initial_max_y - initial_min_y,
                                fill=False, edgecolor='gray', linestyle='--', linewidth=2, label='Initial Bounds')
        ax2.add_patch(initial_rect)
        
        # Final boundaries (if different from initial)
        if (final_min_x != initial_min_x or final_max_x != initial_max_x or 
            final_min_y != initial_min_y or final_max_y != initial_max_y):
            final_rect = Rectangle((final_min_x, final_min_y), 
                                  final_max_x - final_min_x,
                                  final_max_y - final_min_y,
                                  fill=False, edgecolor='red', linestyle='-', linewidth=2, label='Final Bounds')
            ax2.add_patch(final_rect)
        
        # Mark the true optimum
        ax2.scatter([7.0], [7.0], c='green', s=200, marker='*', 
                   edgecolors='black', linewidths=2, label='True Optimum')
        
        # Set axis limits to show both initial and final boundaries plus some margin
        margin = 0.5
        ax2.set_xlim(min(initial_min_x, final_min_x) - margin, max(initial_max_x, final_max_x) + margin)
        ax2.set_ylim(min(initial_min_y, final_min_y) - margin, max(initial_max_y, final_max_y) + margin)
        
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_title('Population Distribution with Boundaries')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'boundary_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Boundary analysis plot saved to: {os.path.join(results_dir, 'boundary_analysis.png')}")


def test_adaptive_boundaries_disabled():
    """Test optimization without adaptive boundaries (baseline)."""
    print("\n" + "="*60)
    print("Testing WITHOUT Adaptive Boundaries")
    print("="*60)
    
    # Create parameters with bounds that will constrain the optimum
    params = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # Create optimizer without adaptive boundaries
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=create_shifted_rosenbrock(),
        parameters=params,
        pop_size=30,
        max_iterations=100,
        adaptive_boundaries_mode='off',  # Disabled
        mutation_factor_1=(0.5, 0.9),
        recombination_factor=(0.7, 0.95)
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    print(f"\nOptimization completed:")
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Best parameters: {optimizer.best_parameters}")
    print(f"Stop reason: {optimizer.stop_reason}")
    
    return optimizer


def test_adaptive_boundaries_enabled():
    """Test optimization with adaptive boundaries."""
    print("\n" + "="*60)
    print("Testing WITH Adaptive Boundaries")
    print("="*60)
    
    # Same parameters
    params = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # Create optimizer with adaptive boundaries
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=create_shifted_rosenbrock(),
        parameters=params,
        pop_size=30,
        max_iterations=100,
        adaptive_boundaries_mode='on',  # Enabled
        adaptive_boundaries_config={
            'edge_threshold': 0.1,     # 10% from edge considered "at boundary"
            'pop_quantile': 0.5,       # Extend if 50% of pop is at edge
            'extension': 0.2,          # Extend by 20% of range
            'check_period': 10         # Check every 10 iterations
        },
        mutation_factor_1=(0.5, 0.9),
        recombination_factor=(0.7, 0.95)
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    print(f"\nOptimization completed:")
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Best parameters: {optimizer.best_parameters}")
    print(f"Stop reason: {optimizer.stop_reason}")
    
    return optimizer


def test_adaptive_boundaries_mixed_parameters():
    """Test adaptive boundaries with mixed parameter types."""
    print("\n" + "="*60)
    print("Testing Adaptive Boundaries with Mixed Parameters")
    print("="*60)
    
    # Create parameters with different types
    params = Parameters([
        {'name': 'x_cont', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y_cont', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'scale', 'type': 'discrete', 'values': [0.1, 0.5, 1.0, 2.0, 5.0]},
        {'name': 'mode', 'type': 'categorical', 'values': ['A', 'B', 'C']}
    ])
    
    def mixed_eval_func(parameters, **kwargs):
        """Evaluation function that uses all parameter types."""
        responses = []
        for _, row in parameters.iterrows():
            # Shifted Rosenbrock with scale factor
            x = (row['x_cont'] - 3.5) * row['scale']
            y = (row['y_cont'] - 3.5) * row['scale']
            
            # Add penalty based on mode
            mode_penalties = {'A': 0, 'B': 10, 'C': 20}
            penalty = mode_penalties.get(row['mode'], 0)
            
            value = (1 - x)**2 + 100 * (y - x**2)**2 + penalty
            responses.append({'metric': value})
        return responses
    
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=mixed_eval_func,
        parameters=params,
        pop_size=40,
        max_iterations=100,
        adaptive_boundaries_mode='on',
        adaptive_boundaries_config={
            'edge_threshold': 0.1,
            'pop_quantile': 0.6,
            'extension': 0.15,
            'check_period': 15
        }
    )
    
    optimizer.run_optimization()
    
    print(f"\nOptimization completed:")
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Best parameters: {optimizer.best_parameters}")
    print(f"Stop reason: {optimizer.stop_reason}")
    
    return optimizer


def test_boundary_tracking():
    """Test that boundary changes are properly tracked."""
    print("\n" + "="*60)
    print("Testing Boundary Change Tracking")
    print("="*60)
    
    # Import the get_boundary_statistics function
    from aivalanche_lib.optimization.differential_evolution.adaptive_boundaries import get_boundary_statistics
    
    # Create parameters with tight bounds
    params = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -2.0, 'max': 2.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -2.0, 'max': 2.0, 'default': 0.0}
    ])
    
    # Create optimizer with frequent boundary checks
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=create_shifted_rosenbrock(),  # Optimum at (7,7) - way outside bounds
        parameters=params,
        pop_size=20,
        max_iterations=50,
        adaptive_boundaries_mode='on',
        adaptive_boundaries_config={
            'edge_threshold': 0.15,     # More lenient edge detection
            'pop_quantile': 0.6,        # Lower threshold for triggering
            'extension': 0.25,          # Larger extensions
            'check_period': 5           # Check every 5 iterations
        }
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    # Get boundary statistics
    stats = get_boundary_statistics(optimizer)
    
    print(f"\nBoundary Change Statistics:")
    print(f"Total boundary updates: {stats['total_changes']}")
    print(f"Parameters that had boundary changes: {stats['parameters_changed']}")
    print(f"Iterations with boundary changes: {stats['iterations_with_changes']}")
    
    # Verify the tracking
    assert stats['total_changes'] > 0, "Expected at least one boundary change"
    assert len(stats['parameters_changed']) > 0, "Expected at least one parameter to have boundary changes"
    assert len(stats['iterations_with_changes']) == stats['total_changes'], "Mismatch in tracking"
    
    # Check the boundary history in detail
    print("\nDetailed Boundary History:")
    all_iters = optimizer.all_boundaries.index.get_level_values('iter').unique()
    for iter_num in sorted(all_iters)[:5]:  # Show first 5 iterations
        print(f"\nIteration {iter_num}:")
        for param in ['x', 'y']:
            min_val = optimizer.all_boundaries.loc[(iter_num, 'min'), param]
            max_val = optimizer.all_boundaries.loc[(iter_num, 'max'), param]
            range_val = optimizer.all_boundaries.loc[(iter_num, 'range'), param]
            print(f"  {param}: [{min_val:.3f}, {max_val:.3f}] (range: {range_val:.3f})")
    
    # Verify that boundaries actually expanded
    initial_range_x = optimizer.all_boundaries.loc[(0, 'range'), 'x']
    initial_range_y = optimizer.all_boundaries.loc[(0, 'range'), 'y']
    
    final_iter = max(all_iters)
    final_range_x = optimizer.all_boundaries.loc[(final_iter, 'range'), 'x']
    final_range_y = optimizer.all_boundaries.loc[(final_iter, 'range'), 'y']
    
    print(f"\nBoundary expansion:")
    print(f"X range: {initial_range_x:.3f} -> {final_range_x:.3f} ({(final_range_x/initial_range_x - 1)*100:.1f}% increase)")
    print(f"Y range: {initial_range_y:.3f} -> {final_range_y:.3f} ({(final_range_y/initial_range_y - 1)*100:.1f}% increase)")
    
    assert final_range_x > initial_range_x, "Expected X boundaries to expand"
    assert final_range_y > initial_range_y, "Expected Y boundaries to expand"
    
    print("\nBoundary tracking test passed!")
    
    return optimizer


def main():
    """Run all adaptive boundaries tests."""
    print("Adaptive Boundaries Test Suite")
    print("=" * 60)
    
    # Import get_boundary_statistics for the results
    from aivalanche_lib.optimization.differential_evolution.adaptive_boundaries import get_boundary_statistics
    
    # Create results directory
    results_dir = create_test_results_dir('adaptive_boundaries')
    
    # Run tests
    results = {}
    
    # Test 1: Without adaptive boundaries
    optimizer_without = test_adaptive_boundaries_disabled()
    results['without_adaptive'] = {
        'best_metric': optimizer_without.best_metric,
        'best_parameters': optimizer_without.best_parameters.to_dict() if hasattr(optimizer_without.best_parameters, 'to_dict') else optimizer_without.best_parameters,
        'iterations': optimizer_without.iter,
        'stop_reason': optimizer_without.stop_reason
    }
    
    # Test 2: With adaptive boundaries
    optimizer_with = test_adaptive_boundaries_enabled()
    results['with_adaptive'] = {
        'best_metric': optimizer_with.best_metric,
        'best_parameters': optimizer_with.best_parameters.to_dict() if hasattr(optimizer_with.best_parameters, 'to_dict') else optimizer_with.best_parameters,
        'iterations': optimizer_with.iter,
        'stop_reason': optimizer_with.stop_reason
    }
    
    # Test 3: Mixed parameters
    optimizer_mixed = test_adaptive_boundaries_mixed_parameters()
    results['mixed_parameters'] = {
        'best_metric': optimizer_mixed.best_metric,
        'best_parameters': optimizer_mixed.best_parameters.to_dict() if hasattr(optimizer_mixed.best_parameters, 'to_dict') else optimizer_mixed.best_parameters,
        'iterations': optimizer_mixed.iter,
        'stop_reason': optimizer_mixed.stop_reason
    }
    
    # Test 4: Boundary tracking
    optimizer_tracking = test_boundary_tracking()
    results['boundary_tracking'] = {
        'best_metric': optimizer_tracking.best_metric,
        'iterations': optimizer_tracking.iter,
        'boundary_statistics': get_boundary_statistics(optimizer_tracking)
    }
    
    # Create comparison plots
    plt.figure(figsize=(12, 5))
    
    # Plot 1: Convergence comparison
    plt.subplot(1, 2, 1)
    for label, optimizer in [('Without Adaptive', optimizer_without), 
                             ('With Adaptive', optimizer_with)]:
        bests = optimizer.history['bests']
        plt.plot(bests['iter'], bests['metric'], label=label, linewidth=2)
    
    plt.xlabel('Iteration')
    plt.ylabel('Best Metric')
    plt.title('Convergence Comparison')
    plt.legend()
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Final population distribution
    plt.subplot(1, 2, 2)
    
    # Get final populations
    for label, optimizer, marker in [('Without Adaptive', optimizer_without, 'o'), 
                                     ('With Adaptive', optimizer_with, 's')]:
        trials = optimizer.history['trials']
        final_iter = trials['iter'].max()
        final_pop = trials[trials['iter'] == final_iter]
        
        if 'x' in final_pop.columns and 'y' in final_pop.columns:
            plt.scatter(final_pop['x'], final_pop['y'], label=label, 
                       alpha=0.6, s=50, marker=marker)
    
    # Mark the true optimum (outside initial bounds)
    plt.scatter([7.0], [7.0], c='red', s=200, marker='*', 
               edgecolors='black', linewidths=2, label='True Optimum (outside bounds)')
    
    # Show original boundaries
    plt.axhline(-5, color='gray', linestyle='--', alpha=0.5)
    plt.axhline(5, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(-5, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(5, color='gray', linestyle='--', alpha=0.5)
    
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Final Population Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    comparison_plot = os.path.join(results_dir, 'adaptive_boundaries_comparison.png')
    plt.savefig(comparison_plot, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Plot boundary evolution for the adaptive case
    plot_boundary_evolution(optimizer_with, results_dir)
    
    # Save test summary
    summary = {
        'test_name': 'Adaptive Boundaries Test',
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'conclusions': {
            'improvement': (results['without_adaptive']['best_metric'] - 
                          results['with_adaptive']['best_metric']) / 
                          results['without_adaptive']['best_metric'] * 100
        }
    }
    save_test_summary(results_dir, summary)
    
    print(f"\n{'='*60}")
    print("Test Summary:")
    print(f"Without adaptive boundaries - Best: {results['without_adaptive']['best_metric']:.6f}")
    print(f"With adaptive boundaries - Best: {results['with_adaptive']['best_metric']:.6f}")
    print(f"Improvement: {summary['conclusions']['improvement']:.2f}%")
    print(f"\nNote: True optimum is at (7.0, 7.0) - outside initial bounds [-5, 5]")
    if results['with_adaptive']['best_parameters']:
        print(f"With adaptive boundaries found: x={results['with_adaptive']['best_parameters'].get('x', 'N/A'):.3f}, y={results['with_adaptive']['best_parameters'].get('y', 'N/A'):.3f}")
    if results['without_adaptive']['best_parameters']:
        print(f"Without adaptive boundaries found: x={results['without_adaptive']['best_parameters'].get('x', 'N/A'):.3f}, y={results['without_adaptive']['best_parameters'].get('y', 'N/A'):.3f}")
    print(f"\nResults saved to: {results_dir}")


if __name__ == "__main__":
    main()