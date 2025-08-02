"""
Test Differential Evolution refinement mechanisms with DLS.

This test evaluates different refinement modes including:
- Different refinement modes (light, moderate, aggressive, etc.)
- Refinement on problems with categorical parameters
- Timing of refinement (on_completion, on_stagnation, adaptive, both)
- Visual comparison of with/without refinement
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details

from test_utils import create_test_results_dir, save_test_summary, create_test_function_wrapper


def test_refinement_modes(function_name: str = 'rastrigin_nd', n_dim: int = 20):
    """Test different refinement modes on a challenging function."""
    print("\n" + "="*60)
    print(f"Testing Different Refinement Modes on {n_dim}D {function_name}")
    print("="*60)
    
    func_details = get_function_details(function_name, n_dim=n_dim)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create high-dimensional parameters
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
    
    modes = ['off', 'light', 'moderate', 'aggressive']
    results = {}
    
    for mode in modes:
        print(f"\nTesting refinement mode: {mode}")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            max_iterations=1000,
            max_iter_without_improvement=200,
            refinement_mode=mode
        )
        
        optimizer.run_optimization()
        
        results[mode] = {
            'optimizer': optimizer,
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'evaluations': optimizer.nr_evaluations,
            'best_params': optimizer.best_parameters,
            'refinement_info': getattr(optimizer, 'refinement_info', None)
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Total evaluations: {optimizer.nr_evaluations}")
        
        if mode != 'off' and hasattr(optimizer, 'refinement_info'):
            info = optimizer.refinement_info
            if info and 'improved' in info:
                print(f"  Refinement: {'IMPROVED' if info['improved'] else 'NO IMPROVEMENT'}")
                if info['improved']:
                    print(f"  Refinement iterations: {info.get('iterations', 'N/A')}")
                    print(f"  Relative improvement: {info.get('relative_improvement', 0):.2%}")
    
    return results


def test_refinement_with_categorical():
    """Test refinement on problems with categorical parameters."""
    print("\n" + "="*60)
    print("Testing Refinement with Categorical Parameters")
    print("="*60)
    
    # Use mixed continuous/categorical function
    func_details = get_function_details('string_categorical_mixed_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    bounds = func_details['bounds']
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': bounds[0][0], 'max': bounds[0][1], 'default': 0.0},
        {'name': 'y', 'type': 'categorical', 'values': bounds[1], 'default': bounds[1][0]}
    ])
    
    # Test with and without refinement
    results = {}
    
    for use_refinement in [False, True]:
        mode = 'moderate' if use_refinement else 'off'
        print(f"\n{'With' if use_refinement else 'Without'} refinement:")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            max_iterations=100,
            refinement_mode=mode
        )
        
        optimizer.run_optimization()
        
        results[mode] = {
            'optimizer': optimizer,
            'best_metric': optimizer.best_metric,
            'best_params': optimizer.best_parameters,
            'refinement_info': getattr(optimizer, 'refinement_info', None)
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Best x: {optimizer.best_parameters['x']:.4f}")
        print(f"  Best y: {optimizer.best_parameters['y']}")
        
        if use_refinement and hasattr(optimizer, 'refinement_info'):
            info = optimizer.refinement_info
            if info and info.get('reason') == 'no_refinable_parameters':
                print("  Note: Only continuous parameter 'x' was refined")
    
    return results


def test_refinement_timing(function_name: str = 'griewank_2d'):
    """Test different refinement trigger modes."""
    print("\n" + "="*60)
    print("Testing Refinement Trigger Timing")
    print("="*60)
    
    func_details = get_function_details(function_name)
    eval_func = create_test_function_wrapper(func_details)
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # Test different trigger modes
    trigger_tests = [
        ('on_completion', {'refinement_mode': 'moderate'}),
        ('on_stagnation', {
            'refinement_mode': 'custom',
            'refinement_config': {
                'method': 'dls',
                'max_iterations': 50,
                'trigger': 'on_stagnation',
                'stagnation_threshold': 30
            }
        }),
        ('adaptive', {
            'refinement_mode': 'custom',
            'refinement_config': {
                'method': 'dls',
                'max_iterations': 50,
                'trigger': 'adaptive',
                'adaptive_interval': 50
            }
        }),
        ('both', {
            'refinement_mode': 'custom',
            'refinement_config': {
                'method': 'dls',
                'max_iterations': 50,
                'trigger': 'both'
            }
        })
    ]
    
    results = {}
    
    for trigger_name, config in trigger_tests:
        print(f"\nTesting trigger: {trigger_name}")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            max_iterations=200,
            **config
        )
        
        optimizer.run_optimization()
        
        # Count refinement applications
        refinement_count = 0
        if hasattr(optimizer, '_refinement_history'):
            refinement_count = len(optimizer._refinement_history)
        elif hasattr(optimizer, 'refinement_info') and optimizer.refinement_info:
            refinement_count = 1
        
        results[trigger_name] = {
            'optimizer': optimizer,
            'best_metric': optimizer.best_metric,
            'refinement_count': refinement_count,
            'stop_reason': optimizer.stop_reason
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Refinement applications: {refinement_count}")
        print(f"  Stop reason: {optimizer.stop_reason}")
    
    return results


def create_refinement_visualization(results: Dict[str, Any], results_dir: str):
    """Create visualization comparing refinement modes."""
    
    # Extract data for plotting
    modes = list(results.keys())
    metrics = [results[mode]['best_metric'] for mode in modes]
    evaluations = [results[mode]['evaluations'] for mode in modes]
    
    # Calculate improvements relative to 'off' mode
    base_metric = results['off']['best_metric']
    improvements = [(base_metric - m) / base_metric * 100 for m in metrics]
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Final metrics comparison
    ax1 = axes[0, 0]
    bars = ax1.bar(modes, metrics, color='skyblue', edgecolor='navy')
    ax1.set_ylabel('Best Metric')
    ax1.set_title('Final Performance by Refinement Mode')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Highlight best performer
    best_idx = np.argmin(metrics)
    bars[best_idx].set_color('green')
    
    # Plot 2: Improvement percentage
    ax2 = axes[0, 1]
    bars2 = ax2.bar(modes, improvements, color='lightgreen', edgecolor='darkgreen')
    ax2.set_ylabel('Improvement vs No Refinement (%)')
    ax2.set_title('Relative Improvement')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.grid(True, alpha=0.3)
    
    # Color negative improvements
    for i, imp in enumerate(improvements):
        if imp < 0:
            bars2[i].set_color('salmon')
    
    # Plot 3: Evaluations used
    ax3 = axes[1, 0]
    ax3.bar(modes, evaluations, color='lightcoral', edgecolor='darkred')
    ax3.set_ylabel('Total Evaluations')
    ax3.set_title('Computational Cost')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Efficiency (improvement per evaluation)
    ax4 = axes[1, 1]
    efficiency = [imp / (evals / 1000) for imp, evals in zip(improvements, evaluations)]
    bars4 = ax4.bar(modes, efficiency, color='lightyellow', edgecolor='orange')
    ax4.set_ylabel('Improvement % per 1000 Evaluations')
    ax4.set_title('Refinement Efficiency')
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax4.grid(True, alpha=0.3)
    
    # Highlight most efficient
    if any(e > 0 for e in efficiency):
        best_eff_idx = np.argmax(efficiency)
        bars4[best_eff_idx].set_color('gold')
    
    plt.suptitle('Refinement Mode Comparison', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'refinement_comparison.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\nVisualization saved to: {plot_file}")


def create_convergence_comparison(results: Dict[str, Any], results_dir: str):
    """Create convergence plots comparing refinement modes."""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(results)))
    
    for (mode, data), color in zip(results.items(), colors):
        optimizer = data['optimizer']
        history = optimizer.history['bests']
        
        # For modes with refinement, we need to show the actual refined values
        if mode != 'off' and hasattr(optimizer, 'refinement_info') and optimizer.refinement_info:
            # Plot normal convergence
            ax.plot(history['iter'], history['metric'], 
                    label=f'{mode}', color=color, linewidth=2)
            
            # Add the final refined value as a separate point
            if optimizer.refinement_info.get('improved'):
                final_iter = history['iter'].max()
                refined_metric = optimizer.refinement_info['refined_metric']
                
                # Show refinement improvement with arrow
                initial_metric = optimizer.refinement_info['initial_metric']
                ax.annotate('', xy=(final_iter, refined_metric), 
                           xytext=(final_iter, initial_metric),
                           arrowprops=dict(arrowstyle='->', color=color, lw=2))
                
                # Add refined point
                ax.scatter(final_iter, refined_metric, color=color, s=200, 
                          marker='*', edgecolor='black', linewidth=2, zorder=10)
                
                # Add text showing improvement
                improvement = optimizer.refinement_info['relative_improvement']
                ax.text(final_iter + 2, refined_metric, f'-{improvement:.1%}', 
                       fontsize=10, color=color, va='center')
        else:
            # Plot normal convergence for non-refinement modes
            ax.plot(history['iter'], history['metric'], 
                    label=f'{mode}', color=color, linewidth=2)
    
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Best Metric')
    ax.set_title('Convergence Comparison with Refinement')
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add note about refinement
    ax.text(0.02, 0.02, 'Note: Arrows show refinement improvements at final iteration', 
            transform=ax.transAxes, fontsize=9, alpha=0.7)
    
    plot_file = os.path.join(results_dir, 'convergence_comparison.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Convergence plot saved to: {plot_file}")


def main():
    """Run all refinement tests."""
    print("Differential Evolution Refinement Test Suite")
    print("=" * 60)
    
    # Create results directory
    results_dir = create_test_results_dir('refinement')
    
    # Test 1: Different refinement modes
    mode_results = test_refinement_modes()
    create_refinement_visualization(mode_results, results_dir)
    create_convergence_comparison(mode_results, results_dir)
    
    # Test 2: Refinement with categorical parameters
    categorical_results = test_refinement_with_categorical()
    
    # Test 3: Refinement timing
    timing_results = test_refinement_timing()
    
    # Create timing comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot refinement counts
    triggers = list(timing_results.keys())
    counts = [timing_results[t]['refinement_count'] for t in triggers]
    metrics = [timing_results[t]['best_metric'] for t in triggers]
    
    ax1.bar(triggers, counts, color='lightblue', edgecolor='darkblue')
    ax1.set_ylabel('Refinement Applications')
    ax1.set_title('Refinement Frequency by Trigger Mode')
    ax1.grid(True, alpha=0.3)
    
    # Plot final metrics
    bars = ax2.bar(triggers, metrics, color='lightgreen', edgecolor='darkgreen')
    ax2.set_ylabel('Best Metric')
    ax2.set_title('Final Performance by Trigger Mode')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Highlight best
    best_idx = np.argmin(metrics)
    bars[best_idx].set_color('green')
    
    plt.suptitle('Refinement Trigger Timing Analysis', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'timing_comparison.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Save test summary
    summary = {
        'test_name': 'DE Refinement Test',
        'timestamp': datetime.now().isoformat(),
        'mode_comparison': {
            mode: {
                'best_metric': data['best_metric'],
                'evaluations': data['evaluations'],
                'improvement_vs_base': (mode_results['off']['best_metric'] - data['best_metric']) / mode_results['off']['best_metric'] * 100
            }
            for mode, data in mode_results.items()
        },
        'categorical_test': {
            'without_refinement': categorical_results['off']['best_metric'],
            'with_refinement': categorical_results['moderate']['best_metric'] if 'moderate' in categorical_results else None
        },
        'timing_test': {
            trigger: {
                'best_metric': data['best_metric'],
                'refinement_count': data['refinement_count']
            }
            for trigger, data in timing_results.items()
        },
        'best_mode': min(mode_results.items(), key=lambda x: x[1]['best_metric'])[0],
        'best_trigger': min(timing_results.items(), key=lambda x: x[1]['best_metric'])[0]
    }
    save_test_summary(results_dir, summary)
    
    print(f"\n{'='*60}")
    print("Test Summary:")
    print(f"Best refinement mode: {summary['best_mode']}")
    print(f"Best trigger mode: {summary['best_trigger']}")
    print(f"\nResults saved to: {results_dir}")


if __name__ == "__main__":
    main()