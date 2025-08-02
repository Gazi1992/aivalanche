"""
Test Differential Evolution metamodel functionality.

This test evaluates metamodel-assisted optimization including:
- Different metamodel modes (auto, exploration, exploitation, etc.)
- Efficiency gains from using metamodels
- Metamodel accuracy and validation
- Performance on expensive functions
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, Any
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details

from test_utils import create_test_results_dir, save_test_summary, create_test_function_wrapper


class ExpensiveFunctionWrapper:
    """Wrapper to simulate expensive function evaluations."""
    
    def __init__(self, base_func, delay: float = 0.001):
        self.base_func = base_func
        self.delay = delay
        self.eval_count = 0
        self.total_time = 0.0
    
    def __call__(self, parameters, **kwargs):
        start_time = time.time()
        # Simulate expensive computation
        time.sleep(self.delay)
        result = self.base_func(parameters, **kwargs)
        self.total_time += time.time() - start_time
        self.eval_count += 1
        return result
    
    def reset(self):
        self.eval_count = 0
        self.total_time = 0.0


def test_metamodel_modes(function_name: str = 'himmelblau_2d'):
    """Test different metamodel modes."""
    print("\n" + "="*60)
    print("Testing Different Metamodel Modes")
    print("="*60)
    
    func_details = get_function_details(function_name)
    base_func = create_test_function_wrapper(func_details)
    
    # Create expensive function wrapper with minimal delay
    expensive_func = ExpensiveFunctionWrapper(base_func, delay=0.001)
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    modes = ['off', 'auto', 'exploration', 'exploitation', 'fast']
    results = {}
    
    for mode in modes:
        print(f"\nTesting mode: {mode}")
        expensive_func.reset()
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=expensive_func,
            parameters=parameters,
            pop_size=20,
            max_iterations=100,
            metamodel_mode=mode
        )
        
        start_time = time.time()
        optimizer.run_optimization()
        total_time = time.time() - start_time
        
        # Calculate actual vs predicted evaluations
        actual_evals = expensive_func.eval_count
        expected_evals = optimizer.nr_evaluations
        saved_evals = expected_evals - actual_evals
        
        results[mode] = {
            'optimizer': optimizer,
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'actual_evaluations': actual_evals,
            'expected_evaluations': expected_evals,
            'saved_evaluations': saved_evals,
            'total_time': total_time,
            'eval_time': expensive_func.total_time,
            'overhead_time': total_time - expensive_func.total_time
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Actual evaluations: {actual_evals}")
        print(f"  Expected evaluations: {expected_evals}")
        print(f"  Saved evaluations: {saved_evals} ({saved_evals/expected_evals*100:.1f}%)")
        print(f"  Total time: {total_time:.2f}s")
    
    return results


def test_metamodel_accuracy():
    """Test metamodel prediction accuracy."""
    print("\n" + "="*60)
    print("Testing Metamodel Prediction Accuracy")
    print("="*60)
    
    # Use a smooth function for better metamodel performance
    func_details = get_function_details('rosenbrock_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -2.0, 'max': 2.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -2.0, 'max': 2.0, 'default': 0.0}
    ])
    
    # Enable metamodel with verbose mode
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        pop_size=30,
        max_iterations=50,
        metamodel_mode='accurate',
        metamodel_config={'verbose': True}
    )
    
    optimizer.run_optimization()
    
    # Check if metamodel info is available
    if hasattr(optimizer, 'metamodel_history'):
        history = optimizer.metamodel_history
        
        # Calculate prediction errors if available
        if 'predictions' in history and 'actuals' in history:
            predictions = np.array(history['predictions'])
            actuals = np.array(history['actuals'])
            
            errors = np.abs(predictions - actuals)
            relative_errors = errors / (np.abs(actuals) + 1e-10)
            
            print(f"\nMetamodel Accuracy Statistics:")
            print(f"  Mean absolute error: {np.mean(errors):.6e}")
            print(f"  Max absolute error: {np.max(errors):.6e}")
            print(f"  Mean relative error: {np.mean(relative_errors):.2%}")
            print(f"  Max relative error: {np.max(relative_errors):.2%}")
    
    return optimizer


def test_metamodel_on_expensive_function():
    """Test metamodel on truly expensive function (high dimensional)."""
    print("\n" + "="*60)
    print("Testing Metamodel on High-Dimensional Function")
    print("="*60)
    
    n_dim = 10
    func_details = get_function_details('sphere_nd', n_dim=n_dim)
    base_func = create_test_function_wrapper(func_details)
    
    # Create wrapper with minimal delay for high dimensions
    expensive_func = ExpensiveFunctionWrapper(base_func, delay=0.001)
    
    # Create high-dimensional parameters
    params_list = []
    for i in range(n_dim):
        params_list.append({
            'name': f'x{i}',
            'type': 'continuous',
            'min': -5.0,
            'max': 5.0,
            'default': 0.0
        })
    
    parameters = Parameters(params_list)
    
    # Test with and without metamodel
    results = {}
    
    for use_metamodel in [False, True]:
        mode = 'fast' if use_metamodel else 'off'
        print(f"\n{'With' if use_metamodel else 'Without'} metamodel:")
        
        expensive_func.reset()
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=expensive_func,
            parameters=parameters,
            pop_size=50,
            max_iterations=100,
            metamodel_mode=mode
        )
        
        start_time = time.time()
        optimizer.run_optimization()
        total_time = time.time() - start_time
        
        results[mode] = {
            'optimizer': optimizer,
            'best_metric': optimizer.best_metric,
            'actual_evaluations': expensive_func.eval_count,
            'total_time': total_time,
            'speedup': None
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Actual evaluations: {expensive_func.eval_count}")
        print(f"  Total time: {total_time:.2f}s")
    
    # Calculate speedup
    if 'off' in results and 'fast' in results:
        speedup = results['off']['total_time'] / results['fast']['total_time']
        results['fast']['speedup'] = speedup
        print(f"\nSpeedup with metamodel: {speedup:.2f}x")
    
    return results


def create_metamodel_visualization(results: Dict[str, Any], results_dir: str):
    """Create visualization comparing metamodel modes."""
    
    modes = list(results.keys())
    metrics = [results[mode]['best_metric'] for mode in modes]
    actual_evals = [results[mode]['actual_evaluations'] for mode in modes]
    saved_evals = [results[mode]['saved_evaluations'] for mode in modes]
    total_times = [results[mode]['total_time'] for mode in modes]
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Final metrics
    ax1 = axes[0, 0]
    bars = ax1.bar(modes, metrics, color='skyblue', edgecolor='navy')
    ax1.set_ylabel('Best Metric')
    ax1.set_title('Final Performance by Metamodel Mode')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Highlight best
    best_idx = np.argmin(metrics)
    bars[best_idx].set_color('green')
    
    # Plot 2: Actual evaluations
    ax2 = axes[0, 1]
    ax2.bar(modes, actual_evals, color='lightcoral', edgecolor='darkred')
    ax2.set_ylabel('Actual Function Evaluations')
    ax2.set_title('Computational Cost')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Saved evaluations percentage
    ax3 = axes[1, 0]
    saved_pct = [s/e*100 if e > 0 else 0 for s, e in 
                 zip(saved_evals, [results[m]['expected_evaluations'] for m in modes])]
    bars3 = ax3.bar(modes, saved_pct, color='lightgreen', edgecolor='darkgreen')
    ax3.set_ylabel('Saved Evaluations (%)')
    ax3.set_title('Metamodel Efficiency')
    ax3.grid(True, alpha=0.3)
    
    # Highlight most efficient
    if max(saved_pct) > 0:
        best_eff_idx = np.argmax(saved_pct)
        bars3[best_eff_idx].set_color('gold')
    
    # Plot 4: Time comparison
    ax4 = axes[1, 1]
    ax4.bar(modes, total_times, color='lightyellow', edgecolor='orange')
    ax4.set_ylabel('Total Time (seconds)')
    ax4.set_title('Runtime Comparison')
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('Metamodel Mode Comparison', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'metamodel_comparison.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()


def create_efficiency_plot(hd_results: Dict[str, Any], results_dir: str):
    """Create efficiency comparison plot for high-dimensional test."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Extract data
    modes = ['Without\nMetamodel', 'With\nMetamodel']
    metrics = [hd_results['off']['best_metric'], hd_results['fast']['best_metric']]
    times = [hd_results['off']['total_time'], hd_results['fast']['total_time']]
    evals = [hd_results['off']['actual_evaluations'], hd_results['fast']['actual_evaluations']]
    
    # Plot 1: Time and evaluations
    x = np.arange(len(modes))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, times, width, label='Time (s)', color='lightblue')
    bars2 = ax1.bar(x + width/2, np.array(evals)/10, width, label='Evals/10', color='lightcoral')
    
    ax1.set_ylabel('Value')
    ax1.set_title('Computational Cost Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(modes)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add speedup annotation
    if hd_results['fast']['speedup']:
        ax1.text(0.5, max(times)*0.9, f"Speedup: {hd_results['fast']['speedup']:.2f}x",
                ha='center', fontsize=14, weight='bold', color='green')
    
    # Plot 2: Solution quality
    bars = ax2.bar(modes, metrics, color='lightgreen', edgecolor='darkgreen')
    ax2.set_ylabel('Best Metric')
    ax2.set_title('Solution Quality')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Highlight better solution
    best_idx = np.argmin(metrics)
    bars[best_idx].set_color('green')
    
    plt.suptitle('High-Dimensional Function: Metamodel Efficiency', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'metamodel_efficiency.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()


def main():
    """Run all metamodel tests."""
    print("Differential Evolution Metamodel Test Suite")
    print("=" * 60)
    
    # Create results directory
    results_dir = create_test_results_dir('metamodels')
    
    # Test 1: Different metamodel modes
    mode_results = test_metamodel_modes()
    create_metamodel_visualization(mode_results, results_dir)
    
    # Test 2: Metamodel accuracy
    accuracy_test = test_metamodel_accuracy()
    
    # Test 3: High-dimensional expensive function
    hd_results = test_metamodel_on_expensive_function()
    create_efficiency_plot(hd_results, results_dir)
    
    # Save test summary
    summary = {
        'test_name': 'DE Metamodel Test',
        'timestamp': datetime.now().isoformat(),
        'mode_comparison': {
            mode: {
                'best_metric': data['best_metric'],
                'actual_evaluations': data['actual_evaluations'],
                'saved_evaluations': data['saved_evaluations'],
                'efficiency': data['saved_evaluations'] / data['expected_evaluations'] * 100
                    if data['expected_evaluations'] > 0 else 0
            }
            for mode, data in mode_results.items()
        },
        'high_dimensional_test': {
            'without_metamodel': {
                'best_metric': hd_results['off']['best_metric'],
                'evaluations': hd_results['off']['actual_evaluations'],
                'time': hd_results['off']['total_time']
            },
            'with_metamodel': {
                'best_metric': hd_results['fast']['best_metric'],
                'evaluations': hd_results['fast']['actual_evaluations'],
                'time': hd_results['fast']['total_time'],
                'speedup': hd_results['fast']['speedup']
            }
        },
        'best_mode': min(mode_results.items(), key=lambda x: x[1]['best_metric'])[0],
        'most_efficient_mode': max(mode_results.items(), 
                                  key=lambda x: x[1]['saved_evaluations'] / x[1]['expected_evaluations'] 
                                  if x[1]['expected_evaluations'] > 0 else 0)[0]
    }
    save_test_summary(results_dir, summary)
    
    print(f"\n{'='*60}")
    print("Test Summary:")
    print(f"Best mode for solution quality: {summary['best_mode']}")
    print(f"Most efficient mode: {summary['most_efficient_mode']}")
    if hd_results['fast']['speedup']:
        print(f"Speedup on expensive function: {hd_results['fast']['speedup']:.2f}x")
    print(f"\nResults saved to: {results_dir}")


if __name__ == "__main__":
    main()