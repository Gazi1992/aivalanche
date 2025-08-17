"""
Simple visualization test for metamodel-based refinement.
Shows comparison for a single function with reduced iterations.
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

# Add the package to path
sys.path.append(os.path.join(os.getcwd(), '..', '..', '..', '..', '..'))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters


def run_comparison_test():
    """Run a simple comparison test with visualization."""
    
    print("="*60)
    print("METAMODEL REFINEMENT COMPARISON - SPHERE FUNCTION")
    print("="*60)
    
    # Create parameters
    parameters = Parameters([
        {'name': 'x', 'min': -5.0, 'max': 5.0},
        {'name': 'y', 'min': -5.0, 'max': 5.0}
    ])
    
    # Track evaluations
    eval_counts = {'with_mm': 0, 'without_mm': 0}
    
    # Create evaluation function
    def make_eval_func(tracker_key):
        def eval_func(parameters, **kwargs):
            eval_counts[tracker_key] += len(parameters)
            responses = []
            for _, row in parameters.iterrows():
                x, y = row['x'], row['y']
                metric = x**2 + y**2  # Sphere function
                responses.append({'metric': metric})
            return responses
        return eval_func
    
    # Run WITH metamodel refinement
    print("\n1. Running WITH metamodel refinement...")
    start_time = time.time()
    
    de_with = DifferentialEvolution(
        seed=42,
        eval_func=make_eval_func('with_mm'),
        parameters=parameters,
        opt_min_or_max='min',
        pop_size=10,
        max_iterations=5,
        
        # No metamodel during main optimization
        metamodel_mode='off',
        
        # Enable metamodel refinement
        refinement_mode='on',
        refinement_config={
            'method': 'dls',
            'trigger_ratio': -1,  # Only at end
            'max_iterations': 50,
            'use_metamodel': True,
            'metamodel_min_training_points': 10,
            'metamodel_min_accuracy': 0.8
        }
    )
    
    de_with.run_optimization()
    time_with = time.time() - start_time
    
    print(f"  Best metric: {de_with.best_metric:.6e}")
    print(f"  Evaluations: {eval_counts['with_mm']}")
    print(f"  Time: {time_with:.2f}s")
    
    # Run WITHOUT metamodel refinement
    print("\n2. Running WITHOUT metamodel refinement...")
    start_time = time.time()
    
    de_without = DifferentialEvolution(
        seed=42,
        eval_func=make_eval_func('without_mm'),
        parameters=parameters,
        opt_min_or_max='min',
        pop_size=10,
        max_iterations=5,
        
        # No metamodel during main optimization
        metamodel_mode='off',
        
        # Regular refinement (no metamodel)
        refinement_mode='on',
        refinement_config={
            'method': 'dls',
            'trigger_ratio': -1,
            'max_iterations': 50,
            'use_metamodel': False  # No metamodel
        }
    )
    
    de_without.run_optimization()
    time_without = time.time() - start_time
    
    print(f"  Best metric: {de_without.best_metric:.6e}")
    print(f"  Evaluations: {eval_counts['without_mm']}")
    print(f"  Time: {time_without:.2f}s")
    
    # Calculate savings
    eval_savings = eval_counts['without_mm'] - eval_counts['with_mm']
    eval_savings_pct = (eval_savings / eval_counts['without_mm']) * 100
    time_savings = time_without - time_with
    time_savings_pct = (time_savings / time_without) * 100
    
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"Evaluation savings: {eval_savings} ({eval_savings_pct:.1f}%)")
    print(f"Time savings: {time_savings:.2f}s ({time_savings_pct:.1f}%)")
    print(f"Final metric comparison:")
    print(f"  With metamodel:    {de_with.best_metric:.6e}")
    print(f"  Without metamodel: {de_without.best_metric:.6e}")
    
    # Create visualization
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Metamodel Refinement Comparison - Sphere Function', fontsize=14)
    
    # 1. Evaluation counts
    ax = axes[0]
    labels = ['With\nMetamodel', 'Without\nMetamodel']
    values = [eval_counts['with_mm'], eval_counts['without_mm']]
    colors = ['steelblue', 'coral']
    bars = ax.bar(labels, values, color=colors)
    ax.set_ylabel('Number of Evaluations')
    ax.set_title('Total Evaluations')
    ax.grid(True, alpha=0.3)
    
    for bar, val in zip(bars, values):
        ax.annotate(f'{val}',
                   xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom')
    
    # 2. Time comparison
    ax = axes[1]
    times = [time_with, time_without]
    bars = ax.bar(labels, times, color=colors)
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Execution Time')
    ax.grid(True, alpha=0.3)
    
    for bar, t in zip(bars, times):
        ax.annotate(f'{t:.2f}s',
                   xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom')
    
    # 3. Solution quality
    ax = axes[2]
    
    # Create contour plot
    x_range = np.linspace(-1, 1, 100)
    y_range = np.linspace(-1, 1, 100)
    X, Y = np.meshgrid(x_range, y_range)
    Z = X**2 + Y**2
    
    contour = ax.contour(X, Y, Z, levels=15, alpha=0.5, cmap='viridis')
    ax.clabel(contour, inline=True, fontsize=8)
    
    # Plot solutions
    ax.plot(de_with.best_parameters['x'], de_with.best_parameters['y'],
           'b*', markersize=12, label=f'With MM: {de_with.best_metric:.2e}')
    ax.plot(de_without.best_parameters['x'], de_without.best_parameters['y'],
           'r*', markersize=12, label=f'Without: {de_without.best_metric:.2e}')
    ax.plot(0, 0, 'go', markersize=8, label='True Optimum')
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Final Solutions')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    
    plt.tight_layout()
    
    # Save figure
    filename = 'metamodel_refinement_comparison_simple.png'
    plt.savefig(filename, dpi=100, bbox_inches='tight')
    print(f"\nVisualization saved as: {filename}")
    # plt.show()  # Comment out to avoid hanging
    
    return de_with, de_without


if __name__ == "__main__":
    de_with, de_without = run_comparison_test()
    print("\nTest completed successfully!")