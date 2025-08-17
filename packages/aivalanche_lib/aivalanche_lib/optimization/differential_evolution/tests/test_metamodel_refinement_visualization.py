"""
Visualization test for metamodel-based refinement in Differential Evolution.

This script compares refinement with and without metamodel, showing:
1. Evaluation counts (efficiency)
2. Convergence speed
3. Final accuracy
4. Metamodel predictions vs real evaluations
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import time

# Add the package to path
sys.path.append(os.path.join(os.getcwd(), 'packages/aivalanche_lib'))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters


def create_test_function(function_type: str = 'sphere'):
    """Create a test function with evaluation counting."""
    eval_count = {'real': 0, 'history': []}
    
    if function_type == 'sphere':
        def eval_func(parameters, **kwargs):
            eval_count['real'] += len(parameters)
            responses = []
            for _, row in parameters.iterrows():
                x, y = row['x'], row['y']
                metric = x**2 + y**2
                responses.append({'metric': metric})
                eval_count['history'].append({'x': x, 'y': y, 'metric': metric})
            return responses
    elif function_type == 'rosenbrock':
        def eval_func(parameters, **kwargs):
            eval_count['real'] += len(parameters)
            responses = []
            for _, row in parameters.iterrows():
                x, y = row['x'], row['y']
                metric = (1 - x)**2 + 100 * (y - x**2)**2
                responses.append({'metric': metric})
                eval_count['history'].append({'x': x, 'y': y, 'metric': metric})
            return responses
    elif function_type == 'rastrigin':
        def eval_func(parameters, **kwargs):
            eval_count['real'] += len(parameters)
            responses = []
            for _, row in parameters.iterrows():
                x, y = row['x'], row['y']
                metric = 20 + x**2 + y**2 - 10*(np.cos(2*np.pi*x) + np.cos(2*np.pi*y))
                responses.append({'metric': metric})
                eval_count['history'].append({'x': x, 'y': y, 'metric': metric})
            return responses
    else:
        raise ValueError(f"Unknown function type: {function_type}")
    
    return eval_func, eval_count


def run_optimization_with_refinement(use_metamodel: bool, function_type: str = 'sphere', 
                                    seed: int = 42, verbose: bool = False) -> Dict:
    """Run DE optimization with refinement (with or without metamodel)."""
    
    # Create parameters
    parameters = Parameters([
        {'name': 'x', 'min': -5.0, 'max': 5.0},
        {'name': 'y', 'min': -5.0, 'max': 5.0}
    ])
    
    # Create evaluation function with counter
    eval_func, eval_count = create_test_function(function_type)
    
    # Configure DE
    de_config = {
        'seed': seed,
        'eval_func': eval_func,
        'parameters': parameters,
        'opt_min_or_max': 'min',
        'pop_size': 20,
        'max_iterations': 10,
        
        # Disable metamodel during main optimization for fair comparison
        'metamodel_mode': 'off',
        
        # Enable refinement
        'refinement_mode': 'on',
        'refinement_config': {
            'method': 'dls',
            'trigger_ratio': -1,  # Only at end
            'max_iterations': 100,
            
            # Metamodel settings for refinement
            'use_metamodel': use_metamodel,
            'metamodel_min_training_points': 20,
            'metamodel_min_accuracy': 0.8
        }
    }
    
    # Run optimization
    start_time = time.time()
    de = DifferentialEvolution(**de_config)
    de.run_optimization()
    elapsed_time = time.time() - start_time
    
    # Collect results
    results = {
        'use_metamodel': use_metamodel,
        'function_type': function_type,
        'best_metric': de.best_metric,
        'best_x': de.best_parameters['x'],
        'best_y': de.best_parameters['y'],
        'total_evaluations': eval_count['real'],
        'de_evaluations': de.pop_size * de.iter,  # Evaluations during DE
        'refinement_evaluations': eval_count['real'] - (de.pop_size * de.iter),
        'elapsed_time': elapsed_time,
        'eval_history': eval_count['history'],
        'de_instance': de
    }
    
    # Add refinement info if available
    if hasattr(de, 'refinement_info') and de.refinement_info:
        results['refinement_info'] = de.refinement_info
        results['refinement_improved'] = de.refinement_info.get('improved', False)
        results['refinement_iterations'] = de.refinement_info.get('iterations', 0)
        results['used_metamodel'] = de.refinement_info.get('used_metamodel', False)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Results for {function_type} with metamodel={use_metamodel}")
        print(f"{'='*60}")
        print(f"Best metric: {results['best_metric']:.6e}")
        print(f"Best point: ({results['best_x']:.4f}, {results['best_y']:.4f})")
        print(f"Total evaluations: {results['total_evaluations']}")
        print(f"  - DE phase: {results['de_evaluations']}")
        print(f"  - Refinement: {results['refinement_evaluations']}")
        print(f"Time: {results['elapsed_time']:.2f}s")
        if 'used_metamodel' in results:
            print(f"Actually used metamodel: {results['used_metamodel']}")
    
    return results


def plot_comparison(results_with: Dict, results_without: Dict, function_type: str):
    """Create comparison plots for refinement with and without metamodel."""
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(f'Metamodel Refinement Comparison - {function_type.capitalize()} Function', fontsize=16)
    
    # 1. Evaluation counts comparison
    ax = axes[0, 0]
    categories = ['Total', 'DE Phase', 'Refinement']
    x = np.arange(len(categories))
    width = 0.35
    
    with_vals = [results_with['total_evaluations'], 
                 results_with['de_evaluations'],
                 results_with['refinement_evaluations']]
    without_vals = [results_without['total_evaluations'],
                   results_without['de_evaluations'], 
                   results_without['refinement_evaluations']]
    
    bars1 = ax.bar(x - width/2, with_vals, width, label='With Metamodel', color='steelblue')
    bars2 = ax.bar(x + width/2, without_vals, width, label='Without Metamodel', color='coral')
    
    ax.set_xlabel('Phase')
    ax.set_ylabel('Number of Evaluations')
    ax.set_title('Evaluation Count Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{int(height)}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom')
    
    # 2. Time comparison
    ax = axes[0, 1]
    times = [results_with['elapsed_time'], results_without['elapsed_time']]
    labels = ['With\nMetamodel', 'Without\nMetamodel']
    colors = ['steelblue', 'coral']
    bars = ax.bar(labels, times, color=colors)
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Execution Time Comparison')
    ax.grid(True, alpha=0.3)
    
    for bar, time_val in zip(bars, times):
        ax.annotate(f'{time_val:.2f}s',
                   xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom')
    
    # 3. Final metric comparison
    ax = axes[0, 2]
    metrics = [results_with['best_metric'], results_without['best_metric']]
    bars = ax.bar(labels, metrics, color=colors)
    ax.set_ylabel('Best Metric (lower is better)')
    ax.set_title('Final Solution Quality')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    
    for bar, metric in zip(bars, metrics):
        ax.annotate(f'{metric:.2e}',
                   xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom')
    
    # 4. Optimization landscape with solutions
    ax = axes[1, 0]
    
    # Create a grid for contour plot
    x_range = np.linspace(-5, 5, 100)
    y_range = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x_range, y_range)
    
    # Calculate function values
    if function_type == 'sphere':
        Z = X**2 + Y**2
    elif function_type == 'rosenbrock':
        Z = (1 - X)**2 + 100 * (Y - X**2)**2
    elif function_type == 'rastrigin':
        Z = 20 + X**2 + Y**2 - 10*(np.cos(2*np.pi*X) + np.cos(2*np.pi*Y))
    
    # Plot contours
    contour = ax.contour(X, Y, Z, levels=20, alpha=0.5, cmap='viridis')
    ax.clabel(contour, inline=True, fontsize=8)
    
    # Plot best solutions
    ax.plot(results_with['best_x'], results_with['best_y'], 
           'b*', markersize=15, label=f"With Metamodel\n({results_with['best_metric']:.2e})")
    ax.plot(results_without['best_x'], results_without['best_y'], 
           'r*', markersize=15, label=f"Without Metamodel\n({results_without['best_metric']:.2e})")
    
    # Mark the true optimum
    if function_type == 'sphere' or function_type == 'rastrigin':
        ax.plot(0, 0, 'go', markersize=10, label='True Optimum')
    elif function_type == 'rosenbrock':
        ax.plot(1, 1, 'go', markersize=10, label='True Optimum')
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Optimization Landscape & Solutions')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    
    # 5. Refinement efficiency
    ax = axes[1, 1]
    
    # Calculate efficiency metrics
    with_efficiency = results_with['refinement_evaluations'] / max(results_with['refinement_iterations'], 1) if 'refinement_iterations' in results_with else 0
    without_efficiency = results_without['refinement_evaluations'] / max(results_without['refinement_iterations'], 1) if 'refinement_iterations' in results_without else 0
    
    data = {
        'Evaluations per Iteration': [with_efficiency, without_efficiency],
        'Total Refinement Evals': [results_with['refinement_evaluations'], results_without['refinement_evaluations']]
    }
    
    x = np.arange(len(data))
    width = 0.35
    
    for i, (label, values) in enumerate(data.items()):
        offset = width * (i - 0.5)
        bars = ax.bar(x + offset, values, width, label=label)
        
        for j, bar in enumerate(bars):
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom')
    
    ax.set_ylabel('Count')
    ax.set_title('Refinement Efficiency')
    ax.set_xticks(x)
    ax.set_xticklabels(['With\nMetamodel', 'Without\nMetamodel'])
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 6. Evaluation savings
    ax = axes[1, 2]
    
    # Calculate savings
    eval_savings = results_without['refinement_evaluations'] - results_with['refinement_evaluations']
    eval_savings_pct = (eval_savings / results_without['refinement_evaluations']) * 100 if results_without['refinement_evaluations'] > 0 else 0
    
    time_savings = results_without['elapsed_time'] - results_with['elapsed_time']
    time_savings_pct = (time_savings / results_without['elapsed_time']) * 100 if results_without['elapsed_time'] > 0 else 0
    
    # Create text summary
    summary_text = f"Metamodel Refinement Benefits:\n\n"
    summary_text += f"Evaluation Savings:\n"
    summary_text += f"  {eval_savings} evaluations saved\n"
    summary_text += f"  {eval_savings_pct:.1f}% reduction\n\n"
    summary_text += f"Time Savings:\n"
    summary_text += f"  {time_savings:.2f} seconds saved\n"
    summary_text += f"  {time_savings_pct:.1f}% reduction\n\n"
    summary_text += f"Accuracy:\n"
    summary_text += f"  With MM: {results_with['best_metric']:.2e}\n"
    summary_text += f"  Without: {results_without['best_metric']:.2e}\n"
    
    if results_with['best_metric'] < results_without['best_metric']:
        summary_text += f"  Better with metamodel!"
    elif results_with['best_metric'] > results_without['best_metric']:
        summary_text += f"  Better without metamodel"
    else:
        summary_text += f"  Same accuracy"
    
    ax.text(0.5, 0.5, summary_text, transform=ax.transAxes,
            fontsize=11, verticalalignment='center', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.set_title('Summary Statistics')
    ax.axis('off')
    
    plt.tight_layout()
    return fig


def run_comprehensive_comparison():
    """Run comprehensive comparison across multiple functions."""
    
    print("="*80)
    print("COMPREHENSIVE METAMODEL REFINEMENT COMPARISON")
    print("="*80)
    
    # Test functions to evaluate
    test_functions = ['sphere', 'rosenbrock', 'rastrigin']
    
    all_results = {}
    
    for func_type in test_functions:
        print(f"\n\nTesting {func_type.upper()} function...")
        print("-"*60)
        
        # Run with metamodel refinement
        print("\n1. Running WITH metamodel refinement...")
        results_with = run_optimization_with_refinement(
            use_metamodel=True, 
            function_type=func_type,
            seed=42,
            verbose=True
        )
        
        # Run without metamodel refinement
        print("\n2. Running WITHOUT metamodel refinement...")
        results_without = run_optimization_with_refinement(
            use_metamodel=False,
            function_type=func_type,
            seed=42,
            verbose=True
        )
        
        # Store results
        all_results[func_type] = {
            'with_metamodel': results_with,
            'without_metamodel': results_without
        }
        
        # Create comparison plot
        fig = plot_comparison(results_with, results_without, func_type)
        
        # Save plot
        plot_filename = f'metamodel_refinement_comparison_{func_type}.png'
        fig.savefig(plot_filename, dpi=100, bbox_inches='tight')
        print(f"\nPlot saved as: {plot_filename}")
        
        # Show plot
        plt.show()
    
    # Print overall summary
    print("\n\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    
    total_savings_evals = 0
    total_savings_time = 0
    
    for func_type in test_functions:
        with_mm = all_results[func_type]['with_metamodel']
        without_mm = all_results[func_type]['without_metamodel']
        
        eval_savings = without_mm['refinement_evaluations'] - with_mm['refinement_evaluations']
        time_savings = without_mm['elapsed_time'] - with_mm['elapsed_time']
        
        total_savings_evals += eval_savings
        total_savings_time += time_savings
        
        print(f"\n{func_type.upper()}:")
        print(f"  Evaluations saved: {eval_savings} ({eval_savings/without_mm['refinement_evaluations']*100:.1f}%)")
        print(f"  Time saved: {time_savings:.2f}s ({time_savings/without_mm['elapsed_time']*100:.1f}%)")
        print(f"  Final metric with MM: {with_mm['best_metric']:.2e}")
        print(f"  Final metric without: {without_mm['best_metric']:.2e}")
        
        if with_mm['best_metric'] < without_mm['best_metric']:
            print(f"  --> Better WITH metamodel (improvement: {(without_mm['best_metric']-with_mm['best_metric'])/without_mm['best_metric']*100:.2f}%)")
        elif with_mm['best_metric'] > without_mm['best_metric']:
            print(f"  --> Better WITHOUT metamodel (degradation: {(with_mm['best_metric']-without_mm['best_metric'])/without_mm['best_metric']*100:.2f}%)")
        else:
            print(f"  --> Same performance")
    
    print(f"\n" + "="*80)
    print(f"TOTAL ACROSS ALL FUNCTIONS:")
    print(f"  Total evaluations saved: {total_savings_evals}")
    print(f"  Total time saved: {total_savings_time:.2f}s")
    print("="*80)
    
    return all_results


if __name__ == "__main__":
    # Run the comprehensive comparison
    results = run_comprehensive_comparison()
    
    print("\n\nAll tests completed successfully!")
    print("Check the generated PNG files for detailed visualizations.")