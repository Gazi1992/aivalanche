"""
Complex refinement test using high-dimensional Rastrigin function.
This test evaluates refinement efficacy on a challenging multi-modal problem.
"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'packages/aivalanche_lib'))

import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import time

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.optimization.differential_evolution.refinement import get_refinement_history
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details


def test_rastrigin_20d_refinement():
    """Test refinement on 20-dimensional Rastrigin function."""
    print("\n" + "="*80)
    print("Complex Refinement Test: 20D Rastrigin Function")
    print("="*80)
    print("\nRastrigin function characteristics:")
    print("- Highly multimodal with ~10^n local minima")
    print("- Global minimum at origin: f(0,0,...,0) = 0")
    print("- Search space: [-5.12, 5.12]^20")
    print("- Extremely challenging for optimization")
    
    n_dim = 20
    
    # Get Rastrigin function from test_functions module
    func_details = get_function_details('rastrigin_nd', n_dim)
    rastrigin = func_details['func']
    
    # Create evaluation function
    def eval_func(parameters, **kwargs):
        results = []
        for idx in range(len(parameters)):
            x_vals = [parameters[f'x{i}'].iloc[idx] for i in range(n_dim)]
            metric = rastrigin(np.array(x_vals))
            results.append({'metric': metric})
        return results
    
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
    
    # Test configurations
    configs = [
        {
            'name': 'No Refinement',
            'refinement_mode': 'off',
            'refinement_config': None
        },
        {
            'name': 'DLS During Optimization (Conservative)',
            'refinement_mode': 'on',
            'refinement_config': {
                'method': 'dls',
                'trigger_ratio': 0.3,  # Trigger at 30% stagnation
                'max_iterations': 200
            }
        },
        {
            'name': 'Adam During Optimization (Aggressive)',
            'refinement_mode': 'on',
            'refinement_config': {
                'method': 'adam',
                'trigger_ratio': 0.2,  # Trigger at 20% stagnation
                'max_iterations': 500,
                'options': {
                    'learning_rate': 0.01,
                    'gradient_tolerance': 1e-6
                }
            }
        },
        {
            'name': 'DLS Post-Optimization (Extended)',
            'refinement_mode': 'on',
            'refinement_config': {
                'method': 'dls',
                'trigger_ratio': -1,  # Only after optimization completes
                'max_iterations': 1000,
                'options': {
                    'parameter_tolerance': 1e-8,
                    'gradient_tolerance': 1e-8
                }
            }
        },
        {
            'name': 'Adam Post-Optimization (Extended)',
            'refinement_mode': 'on',
            'refinement_config': {
                'method': 'adam',
                'trigger_ratio': -1,  # Only after optimization completes
                'max_iterations': 1000,
                'options': {
                    'learning_rate': 0.001,
                    'learning_rate_decay': 0.99,
                    'gradient_tolerance': 1e-8
                }
            }
        },
        {
            'name': 'Nelder-Mead Post (Corner, 1% scale)',
            'refinement_mode': 'on',
            'refinement_config': {
                'method': 'nelder_mead',
                'trigger_ratio': -1,
                'max_iterations': 1000,
                'options': {
                    'best_point_position': 'corner',
                    'initial_simplex_scale': 0.01  # 1% of parameter range
                }
            }
        },
        {
            'name': 'Nelder-Mead Post (Centroid, 0.5% scale)',
            'refinement_mode': 'on',
            'refinement_config': {
                'method': 'nelder_mead',
                'trigger_ratio': -1,
                'max_iterations': 1000,
                'options': {
                    'best_point_position': 'centroid',
                    'initial_simplex_scale': 0.005  # 0.5% of parameter range
                }
            }
        }
    ]
    
    results = {}
    
    # Common DE settings for fair comparison
    de_settings = {
        'seed': 42,
        'eval_func': eval_func,
        'parameters': parameters,
        'pop_size': 100,  # 5 * n_dim
        'max_iterations': 2000,
        'max_iter_without_improvement': 300,
        'mutation_factor_1': 0.8,
        'recombination_factor': 0.9
    }
    
    for config in configs:
        print(f"\n{'='*60}")
        print(f"Testing: {config['name']}")
        print('='*60)
        
        # Create DE instance
        de = DifferentialEvolution(
            **de_settings,
            refinement_mode=config['refinement_mode'],
            refinement_config=config['refinement_config']
        )
        
        # Time the optimization
        start_time = time.time()
        de.run_optimization()
        end_time = time.time()
        
        # Get refinement history
        history = get_refinement_history(de)
        
        # Calculate distance from global optimum
        best_x = [de.best_parameters[f'x{i}'] for i in range(n_dim)]
        distance_from_optimum = np.linalg.norm(best_x)
        
        # Get convergence history from bests dataframe
        bests_df = de.history['bests']
        convergence_history = bests_df['metric'].values
        
        # Store results
        results[config['name']] = {
            'final_metric': de.best_metric,
            'distance_from_optimum': distance_from_optimum,
            'evaluations': de.nr_evaluations,
            'time_seconds': end_time - start_time,
            'refinement_count': len(history),
            'refinement_history': history,
            'convergence_history': convergence_history
        }
        
        print(f"\nResults:")
        print(f"  Final metric: {de.best_metric:.6f}")
        print(f"  Distance from optimum: {distance_from_optimum:.6f}")
        print(f"  Total evaluations: {de.nr_evaluations}")
        print(f"  Time: {end_time - start_time:.2f} seconds")
        print(f"  Refinements applied: {len(history)}")
        
        if history:
            total_improvement = sum(h['relative_improvement'] for h in history)
            print(f"  Total refinement improvement: {total_improvement:.2%}")
            
            for i, h in enumerate(history):
                trigger_point = h.get('trigger_iter', 'post-optimization')
                trigger_desc = f"iteration {trigger_point}" if isinstance(trigger_point, int) else trigger_point
                print(f"\n  Refinement {i+1}:")
                print(f"    Triggered at: {trigger_desc}")
                print(f"    Method: {h['method']}")
                print(f"    Iterations: {h.get('iterations', h.get('evaluations', 0))}")
                print(f"    Improvement: {h['relative_improvement']:.2%}")
    
    # Comparative analysis
    print("\n" + "="*80)
    print("COMPARATIVE ANALYSIS")
    print("="*80)
    
    # Sort by final metric
    sorted_results = sorted(results.items(), key=lambda x: x[1]['final_metric'])
    
    print("\nRanking by final metric:")
    for i, (name, res) in enumerate(sorted_results):
        print(f"{i+1}. {name}: {res['final_metric']:.6f} (distance: {res['distance_from_optimum']:.6f})")
    
    # Calculate improvements over baseline
    baseline_metric = results['No Refinement']['final_metric']
    print(f"\nImprovement over no refinement (baseline: {baseline_metric:.6f}):")
    for name, res in results.items():
        if name != 'No Refinement':
            improvement = (baseline_metric - res['final_metric']) / baseline_metric * 100
            print(f"  {name}: {improvement:.2f}% improvement")
    
    # Efficiency analysis
    print("\nEfficiency (metric per evaluation):")
    for name, res in results.items():
        efficiency = res['final_metric'] / res['evaluations']
        print(f"  {name}: {efficiency:.6e}")
    
    return results


def plot_convergence_comparison(results, save_path=None):
    """Plot convergence curves for all configurations."""
    plt.figure(figsize=(12, 8))
    
    # Define colors for each configuration type
    colors = {
        'No Refinement': 'black',
        'DLS During Optimization (Conservative)': 'blue',
        'Adam During Optimization (Aggressive)': 'red',
        'DLS Post-Optimization (Extended)': 'green',
        'Adam Post-Optimization (Extended)': 'orange',
        'Nelder-Mead Post (Corner, 1% scale)': 'purple',
        'Nelder-Mead Post (Centroid, 0.5% scale)': 'brown'
    }
    
    for name, res in results.items():
        history = res['convergence_history']
        color = colors.get(name, 'gray')
        plt.semilogy(history, label=name, linewidth=2, color=color)
    
    plt.xlabel('Iteration')
    plt.ylabel('Best Metric (log scale)')
    plt.title('20D Rastrigin: Convergence Comparison')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nConvergence plot saved to: {save_path}")
    
    plt.close()


def plot_refinement_impact(results, save_path=None):
    """Visualize the impact of refinements."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Bar chart of final metrics
    names = list(results.keys())
    metrics = [results[name]['final_metric'] for name in names]
    refinements = [results[name]['refinement_count'] for name in names]
    
    bars = ax1.bar(range(len(names)), metrics)
    ax1.set_xticks(range(len(names)))
    ax1.set_xticklabels(names, rotation=45, ha='right')
    ax1.set_ylabel('Final Metric')
    ax1.set_title('Final Optimization Results')
    
    # Color bars by refinement count
    colors = plt.cm.viridis(np.linspace(0, 1, max(refinements) + 1))
    for bar, ref_count in zip(bars, refinements):
        bar.set_color(colors[ref_count])
    
    # Scatter plot: evaluations vs metric
    evaluations = [results[name]['evaluations'] for name in names]
    scatter = ax2.scatter(evaluations, metrics, s=100, c=refinements, 
                         cmap='viridis', edgecolors='black', linewidth=2)
    
    for i, name in enumerate(names):
        ax2.annotate(name, (evaluations[i], metrics[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax2.set_xlabel('Total Evaluations')
    ax2.set_ylabel('Final Metric')
    ax2.set_title('Efficiency Analysis')
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('Number of Refinements')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Impact analysis plot saved to: {save_path}")
    
    plt.close()


if __name__ == "__main__":
    # Create results directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(test_dir, 'results', 
                              f'refinement_complex_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    os.makedirs(results_dir, exist_ok=True)
    
    # Run the complex test
    results = test_rastrigin_20d_refinement()
    
    # Generate visualizations
    plot_convergence_comparison(results, 
                               os.path.join(results_dir, 'convergence_comparison.png'))
    plot_refinement_impact(results,
                          os.path.join(results_dir, 'refinement_impact.png'))
    
    # Save detailed results
    with open(os.path.join(results_dir, 'detailed_results.txt'), 'w') as f:
        f.write("20D Rastrigin Refinement Test Results\n")
        f.write("=" * 80 + "\n\n")
        
        for name, res in results.items():
            f.write(f"{name}:\n")
            f.write(f"  Final metric: {res['final_metric']:.6f}\n")
            f.write(f"  Distance from optimum: {res['distance_from_optimum']:.6f}\n")
            f.write(f"  Evaluations: {res['evaluations']}\n")
            f.write(f"  Time: {res['time_seconds']:.2f} seconds\n")
            f.write(f"  Refinements: {res['refinement_count']}\n")
            
            if res['refinement_history']:
                f.write("  Refinement details:\n")
                for i, h in enumerate(res['refinement_history']):
                    trigger_point = h.get('trigger_iter', 'post-optimization')
                    trigger_desc = f"iter {trigger_point}" if isinstance(trigger_point, int) else trigger_point
                    iterations = h.get('iterations', h.get('evaluations', 0))
                    f.write(f"    Refinement {i+1}: {h['method']} at {trigger_desc}, "
                           f"{iterations} iters, "
                           f"{h['relative_improvement']:.2%} improvement\n")
            f.write("\n")
    
    print(f"\n[SUCCESS] Complex refinement test completed!")
    print(f"Results saved to: {results_dir}")