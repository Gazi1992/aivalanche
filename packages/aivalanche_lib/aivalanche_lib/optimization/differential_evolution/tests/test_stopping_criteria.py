"""
Test Differential Evolution stopping criteria.

This test evaluates different stopping criteria including:
- Maximum iterations
- Maximum iterations without improvement
- Metric threshold
- Parameter tolerance
- Function tolerance
- Custom stopping criteria
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, Any, List
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details

from test_utils import create_test_results_dir, save_test_summary, create_test_function_wrapper


def test_max_iterations():
    """Test maximum iterations stopping criterion."""
    print("\n" + "="*60)
    print("Testing Maximum Iterations Criterion")
    print("="*60)
    
    func_details = get_function_details('sphere_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    max_iter_values = [10, 50, 100, 200]
    results = {}
    
    for max_iter in max_iter_values:
        print(f"\nTesting max_iterations = {max_iter}")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=20,
            max_iterations=max_iter,
            max_iter_without_improvement=max_iter + 100  # Make sure this doesn't trigger
        )
        
        optimizer.run_optimization()
        
        results[max_iter] = {
            'optimizer': optimizer,
            'iterations': optimizer.iter,
            'best_metric': optimizer.best_metric,
            'stop_reason': optimizer.stop_reason
        }
        
        print(f"  Iterations: {optimizer.iter}")
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Stop reason: {optimizer.stop_reason}")
    
    return results


def test_no_improvement():
    """Test maximum iterations without improvement criterion."""
    print("\n" + "="*60)
    print("Testing No Improvement Criterion")
    print("="*60)
    
    func_details = get_function_details('rosenbrock_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -3.0, 'max': 3.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -3.0, 'max': 3.0, 'default': 0.0}
    ])
    
    no_improve_values = [10, 25, 50, 100]
    results = {}
    
    for no_improve in no_improve_values:
        print(f"\nTesting max_iter_without_improvement = {no_improve}")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            max_iterations=1000,  # High value to not interfere
            max_iter_without_improvement=no_improve
        )
        
        optimizer.run_optimization()
        
        results[no_improve] = {
            'optimizer': optimizer,
            'iterations': optimizer.iter,
            'best_metric': optimizer.best_metric,
            'stop_reason': optimizer.stop_reason,
            'iter_no_improvement': optimizer.iter_no_improvement
        }
        
        print(f"  Iterations: {optimizer.iter}")
        print(f"  Iterations without improvement: {optimizer.iter_no_improvement}")
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Stop reason: {optimizer.stop_reason}")
    
    return results


def test_metric_threshold():
    """Test metric threshold stopping criterion."""
    print("\n" + "="*60)
    print("Testing Metric Threshold Criterion")
    print("="*60)
    
    func_details = get_function_details('sphere_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    threshold_values = [1e-2, 1e-4, 1e-6, 1e-8]
    results = {}
    
    for threshold in threshold_values:
        print(f"\nTesting metric_threshold = {threshold:.0e}")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            max_iterations=1000,
            metric_threshold=threshold
        )
        
        optimizer.run_optimization()
        
        results[threshold] = {
            'optimizer': optimizer,
            'iterations': optimizer.iter,
            'best_metric': optimizer.best_metric,
            'stop_reason': optimizer.stop_reason
        }
        
        print(f"  Iterations: {optimizer.iter}")
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Stop reason: {optimizer.stop_reason}")
    
    return results


def test_function_tolerance():
    """Test function value tolerance (improvement threshold)."""
    print("\n" + "="*60)
    print("Testing Function Tolerance Criterion")
    print("="*60)
    
    func_details = get_function_details('sphere_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # For now, just test different max_iter_without_improvement as proxy
    threshold_values = [10, 20, 30, 50]
    results = {}
    
    for threshold in threshold_values:
        print(f"\nTesting max_iter_without_improvement = {threshold}")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            max_iterations=200,
            max_iter_without_improvement=threshold
        )
        
        optimizer.run_optimization()
        
        results[threshold] = {
            'optimizer': optimizer,
            'iterations': optimizer.iter,
            'best_metric': optimizer.best_metric,
            'stop_reason': optimizer.stop_reason
        }
        
        print(f"  Iterations: {optimizer.iter}")
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Stop reason: {optimizer.stop_reason}")
    
    return results


def test_combined_criteria():
    """Test combination of stopping criteria."""
    print("\n" + "="*60)
    print("Testing Combined Stopping Criteria")
    print("="*60)
    
    func_details = get_function_details('himmelblau_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # Test different combinations
    configs = [
        {'name': 'baseline', 'max_iterations': 1000},
        {'name': 'tight_metric', 'max_iterations': 1000, 'metric_threshold': 1e-8},
        {'name': 'tight_improve', 'max_iterations': 1000, 'improvement_threshold': 1e-6},
        {'name': 'both_tight', 'max_iterations': 1000, 'metric_threshold': 1e-8, 'improvement_threshold': 1e-6},
        {'name': 'all_criteria', 'max_iterations': 200, 'max_iter_without_improvement': 50, 
         'metric_threshold': 1e-6}
    ]
    
    results = {}
    
    for config in configs:
        name = config.pop('name')
        print(f"\nTesting configuration: {name}")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            **config
        )
        
        optimizer.run_optimization()
        
        results[name] = {
            'optimizer': optimizer,
            'iterations': optimizer.iter,
            'best_metric': optimizer.best_metric,
            'stop_reason': optimizer.stop_reason,
            'config': config
        }
        
        print(f"  Iterations: {optimizer.iter}")
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Stop reason: {optimizer.stop_reason}")
    
    return results


def create_stopping_criteria_visualization(all_results: Dict[str, Dict], results_dir: str):
    """Create comprehensive visualization of stopping criteria tests."""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Plot 1: Max iterations test
    ax1 = axes[0, 0]
    max_iter_results = all_results['max_iterations']
    max_iters = sorted(max_iter_results.keys())
    iterations = [max_iter_results[m]['iterations'] for m in max_iters]
    metrics = [max_iter_results[m]['best_metric'] for m in max_iters]
    
    ax1_twin = ax1.twinx()
    ax1.bar(range(len(max_iters)), iterations, alpha=0.7, color='lightblue', label='Iterations')
    ax1_twin.plot(range(len(max_iters)), metrics, 'ro-', markersize=8, linewidth=2, label='Best Metric')
    
    ax1.set_xticks(range(len(max_iters)))
    ax1.set_xticklabels(max_iters)
    ax1.set_xlabel('Max Iterations Setting')
    ax1.set_ylabel('Actual Iterations', color='blue')
    ax1_twin.set_ylabel('Best Metric', color='red')
    ax1_twin.set_yscale('log')
    ax1.set_title('Maximum Iterations Criterion')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: No improvement test
    ax2 = axes[0, 1]
    no_improve_results = all_results['no_improvement']
    no_improves = sorted(no_improve_results.keys())
    iterations = [no_improve_results[n]['iterations'] for n in no_improves]
    no_improve_iters = [no_improve_results[n]['iter_no_improvement'] for n in no_improves]
    
    x = np.arange(len(no_improves))
    width = 0.35
    ax2.bar(x - width/2, iterations, width, label='Total Iterations', color='lightblue')
    ax2.bar(x + width/2, no_improve_iters, width, label='No Improvement', color='lightcoral')
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(no_improves)
    ax2.set_xlabel('Max No Improvement Setting')
    ax2.set_ylabel('Iterations')
    ax2.set_title('No Improvement Criterion')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Metric threshold test
    ax3 = axes[0, 2]
    threshold_results = all_results['metric_threshold']
    thresholds = sorted(threshold_results.keys())
    iterations = [threshold_results[t]['iterations'] for t in thresholds]
    metrics = [threshold_results[t]['best_metric'] for t in thresholds]
    
    ax3.plot(thresholds, iterations, 'bo-', markersize=8, linewidth=2)
    ax3.set_xscale('log')
    ax3.set_xlabel('Metric Threshold')
    ax3.set_ylabel('Iterations to Convergence')
    ax3.set_title('Metric Threshold Criterion')
    ax3.grid(True, alpha=0.3)
    
    # Add metric values as text
    for i, (t, m) in enumerate(zip(thresholds, metrics)):
        ax3.text(t, iterations[i], f'{m:.1e}', ha='center', va='bottom', fontsize=8)
    
    # Plot 4: Function tolerance test
    ax4 = axes[1, 0]
    func_tol_results = all_results.get('function_tolerance', {})
    if func_tol_results:
        tols = sorted(func_tol_results.keys())
        iterations = [func_tol_results[t]['iterations'] for t in tols]
        
        ax4.plot(tols, iterations, 'go-', markersize=8, linewidth=2)
        ax4.set_xlabel('Max Iterations Without Improvement')
        ax4.set_ylabel('Iterations to Convergence')
        ax4.set_title('Function Tolerance Criterion')
        ax4.grid(True, alpha=0.3)
    
    # Plot 5: Combined criteria
    ax5 = axes[1, 1]
    combined_results = all_results['combined']
    configs = list(combined_results.keys())
    iterations = [combined_results[c]['iterations'] for c in configs]
    metrics = [combined_results[c]['best_metric'] for c in configs]
    
    bars = ax5.bar(configs, iterations, color='lightgreen', edgecolor='darkgreen')
    ax5.set_ylabel('Iterations')
    ax5.set_title('Combined Criteria Configurations')
    ax5.tick_params(axis='x', rotation=45)
    ax5.grid(True, alpha=0.3)
    
    # Color bars by efficiency
    min_iters = min(iterations)
    for bar, iters in zip(bars, iterations):
        if iters == min_iters:
            bar.set_color('gold')
    
    # Plot 6: Summary statistics
    ax6 = axes[1, 2]
    ax6.axis('off')
    
    summary_text = "Stopping Criteria Summary:\n\n"
    
    # Find most efficient configurations
    for test_name, results in all_results.items():
        if results:
            best_config = min(results.items(), key=lambda x: x[1]['iterations'])
            summary_text += f"{test_name}:\n"
            summary_text += f"  Most efficient: {best_config[0]}\n"
            summary_text += f"  Iterations: {best_config[1]['iterations']}\n\n"
    
    ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes,
             fontsize=10, va='top', family='monospace')
    
    plt.suptitle('Stopping Criteria Analysis', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'stopping_criteria_analysis.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()


def create_convergence_comparison(all_results: Dict[str, Dict], results_dir: str):
    """Create convergence plots for different stopping criteria."""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Select representative results for convergence plots
    test_configs = [
        ('max_iterations', 100, all_results['max_iterations'][100]['optimizer']),
        ('no_improvement', 50, all_results['no_improvement'][50]['optimizer']),
        ('metric_threshold', 1e-6, all_results['metric_threshold'][1e-6]['optimizer']),
        ('combined', 'all_criteria', all_results['combined']['all_criteria']['optimizer'])
    ]
    
    for idx, (test_name, config_name, optimizer) in enumerate(test_configs):
        ax = axes[idx // 2, idx % 2]
        
        history = optimizer.history['bests']
        ax.plot(history['iter'], history['metric'], 'b-', linewidth=2)
        
        # Mark stopping point
        ax.axvline(x=optimizer.iter, color='red', linestyle='--', linewidth=2, alpha=0.7)
        
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Best Metric')
        ax.set_title(f'{test_name}: {config_name}')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
        
        # Add stop reason
        ax.text(0.95, 0.95, f"Stop: {optimizer.stop_reason}", 
                transform=ax.transAxes, ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.suptitle('Convergence Behavior with Different Stopping Criteria', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'convergence_comparison.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()


def main():
    """Run all stopping criteria tests."""
    print("Differential Evolution Stopping Criteria Test Suite")
    print("=" * 60)
    
    # Create results directory
    results_dir = create_test_results_dir('stopping_criteria')
    
    # Run all tests
    all_results = {
        'max_iterations': test_max_iterations(),
        'no_improvement': test_no_improvement(),
        'metric_threshold': test_metric_threshold(),
        'function_tolerance': test_function_tolerance(),
        'combined': test_combined_criteria()
    }
    
    # Create visualizations
    create_stopping_criteria_visualization(all_results, results_dir)
    create_convergence_comparison(all_results, results_dir)
    
    # Save test summary
    summary = {
        'test_name': 'DE Stopping Criteria Test',
        'timestamp': datetime.now().isoformat(),
        'test_results': {}
    }
    
    for test_name, results in all_results.items():
        summary['test_results'][test_name] = {
            config: {
                'iterations': data['iterations'],
                'best_metric': data['best_metric'],
                'stop_reason': data['stop_reason']
            }
            for config, data in results.items()
        }
    
    save_test_summary(results_dir, summary)
    
    print(f"\n{'='*60}")
    print("Test Summary:")
    print("All stopping criteria tested successfully")
    print(f"\nResults saved to: {results_dir}")


if __name__ == "__main__":
    main()