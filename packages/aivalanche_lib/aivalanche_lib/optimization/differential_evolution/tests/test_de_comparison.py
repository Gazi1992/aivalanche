"""
Test Differential Evolution configuration comparisons.

This test compares different DE configurations including:
- Pure DE vs DE with enhancements (perturbations, refinement, metamodels)
- Different operator strategies
- Different population sizes
- Performance across different problem types
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, Any, List, Tuple
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details
from aivalanche_lib.test_functions.definitions import all_functions

from test_utils import create_test_results_dir, save_test_summary, create_test_function_wrapper


def run_de_configuration(config: Dict[str, Any], function_name: str, 
                        n_dim: int = None, n_runs: int = 5) -> Dict[str, Any]:
    """Run DE with given configuration multiple times and return statistics."""
    
    func_details = get_function_details(function_name, n_dim=n_dim)
    eval_func = create_test_function_wrapper(func_details)
    
    # Get parameter bounds
    bounds = func_details['bounds']
    n_params = len(bounds) if bounds else n_dim
    
    # Create parameters based on function type
    params_list = []
    param_names = func_details.get('param_names', [f'x{i}' for i in range(n_params)])
    
    for i, (param_name, bound) in enumerate(zip(param_names, bounds)):
        if isinstance(bound, list):
            # Check if it's categorical (all strings) or discrete (numbers)
            if all(isinstance(v, str) for v in bound):
                # Categorical with string values
                params_list.append({
                    'name': param_name,
                    'type': 'categorical',
                    'values': bound,
                    'default': bound[0]
                })
            else:
                # Discrete with numeric values
                params_list.append({
                    'name': param_name,
                    'type': 'discrete',
                    'values': bound,
                    'default': bound[0]
                })
        elif isinstance(bound, tuple) and len(bound) == 2:
            # Continuous parameter
            params_list.append({
                'name': param_name,
                'type': 'continuous',
                'min': bound[0],
                'max': bound[1],
                'default': (bound[0] + bound[1]) / 2
            })
        elif isinstance(bound, tuple) and len(bound) == 3:
            # Discrete with (min, max, step)
            values = list(np.arange(bound[0], bound[1] + bound[2], bound[2]))
            params_list.append({
                'name': param_name,
                'type': 'discrete',
                'values': values,
                'default': values[len(values)//2]
            })
    
    parameters = Parameters(params_list)
    
    # Run multiple times for statistics
    results = []
    for run in range(n_runs):
        optimizer = DifferentialEvolution(
            seed=42 + run,
            eval_func=eval_func,
            parameters=parameters,
            **config
        )
        
        start_time = time.time()
        optimizer.run_optimization()
        run_time = time.time() - start_time
        
        results.append({
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'evaluations': optimizer.nr_evaluations,
            'run_time': run_time,
            'stop_reason': optimizer.stop_reason
        })
    
    # Calculate statistics
    metrics = [r['best_metric'] for r in results]
    iterations = [r['iterations'] for r in results]
    evaluations = [r['evaluations'] for r in results]
    run_times = [r['run_time'] for r in results]
    
    return {
        'mean_metric': np.mean(metrics),
        'std_metric': np.std(metrics),
        'min_metric': np.min(metrics),
        'max_metric': np.max(metrics),
        'mean_iterations': np.mean(iterations),
        'mean_evaluations': np.mean(evaluations),
        'mean_time': np.mean(run_times),
        'success_rate': sum(1 for m in metrics if m < func_details.get('threshold', 1e-6)) / n_runs,
        'all_results': results
    }


def test_enhancement_comparison():
    """Compare pure DE with various enhancements."""
    print("\n" + "="*60)
    print("Testing DE Enhancement Comparison")
    print("="*60)
    
    # Test configurations
    configs = {
        'Pure DE': {
            'pop_size': 30,
            'max_iterations': 200
        },
        'DE + Perturbation': {
            'pop_size': 30,
            'max_iterations': 200,
            'perturbation_mode': 'moderate'
        },
        'DE + Refinement': {
            'pop_size': 30,
            'max_iterations': 200,
            'refinement_mode': 'auto'
        },
        'DE + Metamodel': {
            'pop_size': 30,
            'max_iterations': 200,
            'metamodel_mode': 'auto'
        },
        'DE + All': {
            'pop_size': 30,
            'max_iterations': 200,
            'perturbation_mode': 'moderate',
            'refinement_mode': 'auto',
            'metamodel_mode': 'auto'
        }
    }
    
    # Test on multiple functions
    test_functions = ['rosenbrock_2d', 'himmelblau_2d', 'griewank_2d']
    results = {}
    
    for func_name in test_functions:
        print(f"\nTesting on {func_name}:")
        results[func_name] = {}
        
        for config_name, config in configs.items():
            print(f"  Running {config_name}...")
            stats = run_de_configuration(config, func_name, n_runs=5)
            results[func_name][config_name] = stats
            print(f"    Mean metric: {stats['mean_metric']:.6e} ± {stats['std_metric']:.6e}")
    
    return results


def test_operator_strategies():
    """Compare different DE operator strategies."""
    print("\n" + "="*60)
    print("Testing Operator Strategy Comparison")
    print("="*60)
    
    # Test configurations with different strategies
    configs = {
        'rand/1/bin': {
            'pop_size': 30,
            'max_iterations': 200,
            'mutation_strategy': 'rand/1',
            'crossover_strategy': 'bin'
        },
        'best/1/bin': {
            'pop_size': 30,
            'max_iterations': 200,
            'mutation_strategy': 'best/1',
            'crossover_strategy': 'bin'
        },
        'rand-to-best/1/bin': {
            'pop_size': 30,
            'max_iterations': 200,
            'mutation_strategy': 'rand-to-best/1',
            'crossover_strategy': 'bin'
        },
        'rand/2/bin': {
            'pop_size': 30,
            'max_iterations': 200,
            'mutation_strategy': 'rand/2',
            'crossover_strategy': 'bin'
        },
        'rand/1/exp': {
            'pop_size': 30,
            'max_iterations': 200,
            'mutation_strategy': 'rand/1',
            'crossover_strategy': 'exp'
        }
    }
    
    # Test on a challenging function
    func_name = 'rastrigin_nd'
    n_dim = 5
    results = {}
    
    for config_name, config in configs.items():
        print(f"\nRunning {config_name}...")
        stats = run_de_configuration(config, func_name, n_dim=n_dim, n_runs=5)
        results[config_name] = stats
        print(f"  Mean metric: {stats['mean_metric']:.6e}")
        print(f"  Success rate: {stats['success_rate']*100:.1f}%")
    
    return results


def test_population_size_effect():
    """Test effect of population size on performance."""
    print("\n" + "="*60)
    print("Testing Population Size Effect")
    print("="*60)
    
    # Test different population sizes
    pop_sizes = [10, 20, 30, 50, 100]
    results = {}
    
    # Test on moderate difficulty function
    func_name = 'sphere_nd'
    n_dim = 10
    
    for pop_size in pop_sizes:
        print(f"\nTesting population size: {pop_size}")
        config = {
            'pop_size': pop_size,
            'max_iterations': 1000 // pop_size  # Keep total evaluations similar
        }
        
        stats = run_de_configuration(config, func_name, n_dim=n_dim, n_runs=5)
        results[pop_size] = stats
        
        print(f"  Mean metric: {stats['mean_metric']:.6e}")
        print(f"  Mean evaluations: {stats['mean_evaluations']:.0f}")
    
    return results


def test_problem_type_performance():
    """Test DE performance across different problem types."""
    print("\n" + "="*60)
    print("Testing Performance Across Problem Types")
    print("="*60)
    
    # Group functions by type
    problem_types = {
        'Continuous': ['sphere_2d', 'rosenbrock_2d', 'himmelblau_2d'],
        'Discrete': ['discrete_rastrigin_2d', 'step_function_2d', 'integer_quadratic_2d'],
        'Mixed': ['string_categorical_mixed_2d', 'mixed_discrete_continuous_2d', 'categorical_interaction_2d']
    }
    
    # Standard configuration
    config = {
        'pop_size': 30,
        'max_iterations': 150,
        'perturbation_mode': 'light'
    }
    
    results = {}
    
    for problem_type, functions in problem_types.items():
        print(f"\n{problem_type} Problems:")
        results[problem_type] = {}
        
        for func_name in functions:
            if func_name in all_functions:
                print(f"  Testing {func_name}...")
                stats = run_de_configuration(config, func_name, n_runs=3)
                results[problem_type][func_name] = stats
                print(f"    Mean metric: {stats['mean_metric']:.6e}")
    
    return results


def create_enhancement_comparison_plot(results: Dict[str, Dict], results_dir: str):
    """Create comparison plot for enhancements."""
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for idx, (func_name, func_results) in enumerate(results.items()):
        ax = axes[idx]
        
        configs = list(func_results.keys())
        means = [func_results[c]['mean_metric'] for c in configs]
        stds = [func_results[c]['std_metric'] for c in configs]
        
        x = np.arange(len(configs))
        bars = ax.bar(x, means, yerr=stds, capsize=5, 
                      color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lavender'],
                      edgecolor='black')
        
        # Highlight best
        best_idx = np.argmin(means)
        bars[best_idx].set_color('gold')
        
        ax.set_xticks(x)
        ax.set_xticklabels(configs, rotation=45, ha='right')
        ax.set_ylabel('Best Metric')
        ax.set_title(f'{func_name}')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('DE Enhancement Comparison', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'enhancement_comparison.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()


def create_operator_comparison_plot(results: Dict[str, Dict], results_dir: str):
    """Create comparison plot for operator strategies."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    strategies = list(results.keys())
    means = [results[s]['mean_metric'] for s in strategies]
    success_rates = [results[s]['success_rate'] * 100 for s in strategies]
    
    # Plot 1: Performance
    bars1 = ax1.bar(strategies, means, color='lightblue', edgecolor='darkblue')
    ax1.set_ylabel('Mean Best Metric')
    ax1.set_title('Operator Strategy Performance')
    ax1.tick_params(axis='x', rotation=45)
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Highlight best
    best_idx = np.argmin(means)
    bars1[best_idx].set_color('green')
    
    # Plot 2: Success rate
    bars2 = ax2.bar(strategies, success_rates, color='lightgreen', edgecolor='darkgreen')
    ax2.set_ylabel('Success Rate (%)')
    ax2.set_title('Operator Strategy Reliability')
    ax2.tick_params(axis='x', rotation=45)
    ax2.set_ylim(0, 105)
    ax2.grid(True, alpha=0.3)
    
    # Highlight best
    if max(success_rates) > 0:
        best_idx = np.argmax(success_rates)
        bars2[best_idx].set_color('gold')
    
    plt.suptitle('DE Operator Strategy Comparison', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'operator_comparison.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()


def create_population_size_plot(results: Dict[int, Dict], results_dir: str):
    """Create plot showing population size effects."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    pop_sizes = sorted(results.keys())
    means = [results[p]['mean_metric'] for p in pop_sizes]
    evaluations = [results[p]['mean_evaluations'] for p in pop_sizes]
    
    # Plot 1: Performance vs population size
    ax1.plot(pop_sizes, means, 'bo-', markersize=8, linewidth=2)
    ax1.set_xlabel('Population Size')
    ax1.set_ylabel('Mean Best Metric')
    ax1.set_title('Solution Quality vs Population Size')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Efficiency (metric per evaluation)
    efficiency = [m / e for m, e in zip(means, evaluations)]
    ax2.plot(pop_sizes, efficiency, 'go-', markersize=8, linewidth=2)
    ax2.set_xlabel('Population Size')
    ax2.set_ylabel('Metric per Evaluation')
    ax2.set_title('Efficiency vs Population Size')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Find optimal population size
    optimal_idx = np.argmin(efficiency)
    ax2.scatter(pop_sizes[optimal_idx], efficiency[optimal_idx], 
                s=200, c='red', marker='*', edgecolor='black', linewidth=2, zorder=10)
    ax2.text(pop_sizes[optimal_idx], efficiency[optimal_idx], 
             f'  Optimal: {pop_sizes[optimal_idx]}', fontsize=12, va='center')
    
    plt.suptitle('Population Size Analysis', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'population_size_analysis.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()


def create_problem_type_plot(results: Dict[str, Dict], results_dir: str):
    """Create plot comparing performance across problem types."""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Prepare data
    problem_types = list(results.keys())
    n_types = len(problem_types)
    
    # Create grouped bar chart
    bar_width = 0.25
    colors = ['lightblue', 'lightgreen', 'lightcoral']
    
    for i, problem_type in enumerate(problem_types):
        functions = list(results[problem_type].keys())
        metrics = [results[problem_type][f]['mean_metric'] for f in functions]
        
        x = np.arange(len(functions)) + i * bar_width
        bars = ax.bar(x, metrics, bar_width, label=problem_type, 
                      color=colors[i], edgecolor='black')
        
        # Add function names
        if i == 1:  # Middle group
            ax.set_xticks(x)
            ax.set_xticklabels(functions, rotation=45, ha='right')
    
    ax.set_ylabel('Mean Best Metric')
    ax.set_title('DE Performance Across Problem Types')
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'problem_type_comparison.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()


def main():
    """Run all DE comparison tests."""
    print("Differential Evolution Configuration Comparison Test Suite")
    print("=" * 60)
    
    # Create results directory
    results_dir = create_test_results_dir('de_comparison')
    
    # Test 1: Enhancement comparison
    enhancement_results = test_enhancement_comparison()
    create_enhancement_comparison_plot(enhancement_results, results_dir)
    
    # Test 2: Operator strategies
    operator_results = test_operator_strategies()
    create_operator_comparison_plot(operator_results, results_dir)
    
    # Test 3: Population size effect
    population_results = test_population_size_effect()
    create_population_size_plot(population_results, results_dir)
    
    # Test 4: Problem type performance
    problem_type_results = test_problem_type_performance()
    create_problem_type_plot(problem_type_results, results_dir)
    
    # Save comprehensive summary
    summary = {
        'test_name': 'DE Configuration Comparison',
        'timestamp': datetime.now().isoformat(),
        'enhancement_comparison': {
            func: {
                config: {
                    'mean_metric': stats['mean_metric'],
                    'std_metric': stats['std_metric']
                }
                for config, stats in func_results.items()
            }
            for func, func_results in enhancement_results.items()
        },
        'operator_comparison': {
            strategy: {
                'mean_metric': stats['mean_metric'],
                'success_rate': stats['success_rate']
            }
            for strategy, stats in operator_results.items()
        },
        'population_size_effect': {
            pop_size: {
                'mean_metric': stats['mean_metric'],
                'mean_evaluations': stats['mean_evaluations']
            }
            for pop_size, stats in population_results.items()
        },
        'problem_type_performance': {
            ptype: {
                func: stats['mean_metric']
                for func, stats in funcs.items()
            }
            for ptype, funcs in problem_type_results.items()
        }
    }
    
    # Find best configurations
    best_enhancement = None
    best_metric = float('inf')
    for func_results in enhancement_results.values():
        for config, stats in func_results.items():
            if stats['mean_metric'] < best_metric:
                best_metric = stats['mean_metric']
                best_enhancement = config
    
    best_operator = min(operator_results.items(), key=lambda x: x[1]['mean_metric'])[0]
    optimal_pop_size = min(population_results.items(), 
                          key=lambda x: x[1]['mean_metric'] / x[1]['mean_evaluations'])[0]
    
    summary['recommendations'] = {
        'best_enhancement_config': best_enhancement,
        'best_operator_strategy': best_operator,
        'optimal_population_size': optimal_pop_size
    }
    
    save_test_summary(results_dir, summary)
    
    print(f"\n{'='*60}")
    print("Test Summary:")
    print(f"Best enhancement configuration: {best_enhancement}")
    print(f"Best operator strategy: {best_operator}")
    print(f"Optimal population size: {optimal_pop_size}")
    print(f"\nResults saved to: {results_dir}")


if __name__ == "__main__":
    main()