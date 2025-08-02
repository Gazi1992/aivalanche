"""
Test Differential Evolution operators (mutation and crossover).

This test evaluates different DE operator configurations including:
- Different mutation strategies
- Various crossover methods
- Adaptive parameter settings
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


def test_mutation_strategies(function_name: str = 'rosenbrock_2d', n_iterations: int = 50):
    """Test different mutation strategies."""
    print("\n" + "="*60)
    print("Testing Mutation Strategies")
    print("="*60)
    
    # Get function details
    func_details = get_function_details(function_name)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create parameters
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # Test different mutation factors
    mutation_configs = [
        {'name': 'Low Fixed (0.3)', 'mutation_factor_1': 0.3},
        {'name': 'Medium Fixed (0.5)', 'mutation_factor_1': 0.5},
        {'name': 'High Fixed (0.8)', 'mutation_factor_1': 0.8},
        {'name': 'Adaptive (0.3-0.9)', 'mutation_factor_1': (0.3, 0.9)},
        {'name': 'Narrow Adaptive (0.4-0.6)', 'mutation_factor_1': (0.4, 0.6)},
        {'name': 'Wide Adaptive (0.1-1.0)', 'mutation_factor_1': (0.1, 1.0)}
    ]
    
    results = {}
    
    for config in mutation_configs:
        print(f"\nTesting {config['name']}...")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            max_iterations=n_iterations,
            mutation_factor_1=config['mutation_factor_1'],
            recombination_factor=0.7  # Fixed for this test
        )
        
        optimizer.run_optimization()
        
        results[config['name']] = {
            'optimizer': optimizer,
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'convergence': optimizer.history['bests']['metric'].values
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Iterations: {optimizer.iter}")
    
    return results


def test_crossover_methods(function_name: str = 'rosenbrock_2d', n_iterations: int = 50):
    """Test different crossover/recombination settings."""
    print("\n" + "="*60)
    print("Testing Crossover Methods")
    print("="*60)
    
    # Get function details
    func_details = get_function_details(function_name)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create parameters
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # Test different recombination factors
    crossover_configs = [
        {'name': 'Low CR (0.3)', 'recombination_factor': 0.3},
        {'name': 'Medium CR (0.5)', 'recombination_factor': 0.5},
        {'name': 'High CR (0.9)', 'recombination_factor': 0.9},
        {'name': 'Adaptive CR (0.3-0.9)', 'recombination_factor': (0.3, 0.9)},
        {'name': 'Low Adaptive (0.1-0.4)', 'recombination_factor': (0.1, 0.4)},
        {'name': 'High Adaptive (0.7-1.0)', 'recombination_factor': (0.7, 1.0)}
    ]
    
    results = {}
    
    for config in crossover_configs:
        print(f"\nTesting {config['name']}...")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            max_iterations=n_iterations,
            mutation_factor_1=0.5,  # Fixed for this test
            recombination_factor=config['recombination_factor']
        )
        
        optimizer.run_optimization()
        
        results[config['name']] = {
            'optimizer': optimizer,
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'convergence': optimizer.history['bests']['metric'].values
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Iterations: {optimizer.iter}")
    
    return results


def test_combined_adaptive(function_name: str = 'rosenbrock_2d', n_iterations: int = 50):
    """Test combined adaptive mutation and crossover."""
    print("\n" + "="*60)
    print("Testing Combined Adaptive Parameters")
    print("="*60)
    
    # Get function details
    func_details = get_function_details(function_name)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create parameters
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # Test combinations
    combined_configs = [
        {
            'name': 'Fixed F & CR',
            'mutation_factor_1': 0.5,
            'recombination_factor': 0.7
        },
        {
            'name': 'Adaptive F, Fixed CR',
            'mutation_factor_1': (0.3, 0.9),
            'recombination_factor': 0.7
        },
        {
            'name': 'Fixed F, Adaptive CR',
            'mutation_factor_1': 0.5,
            'recombination_factor': (0.3, 0.9)
        },
        {
            'name': 'Both Adaptive',
            'mutation_factor_1': (0.3, 0.9),
            'recombination_factor': (0.3, 0.9)
        },
        {
            'name': 'Conservative Adaptive',
            'mutation_factor_1': (0.4, 0.6),
            'recombination_factor': (0.6, 0.8)
        }
    ]
    
    results = {}
    
    for config in combined_configs:
        print(f"\nTesting {config['name']}...")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            max_iterations=n_iterations,
            mutation_factor_1=config['mutation_factor_1'],
            recombination_factor=config['recombination_factor']
        )
        
        optimizer.run_optimization()
        
        results[config['name']] = {
            'optimizer': optimizer,
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'convergence': optimizer.history['bests']['metric'].values
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Iterations: {optimizer.iter}")
    
    return results


def test_operators_on_different_functions():
    """Test operators on different types of functions."""
    print("\n" + "="*60)
    print("Testing Operators on Different Function Types")
    print("="*60)
    
    test_functions = [
        'sphere_2d',      # Simple unimodal
        'rosenbrock_2d',  # Valley-shaped
        'rastrigin_nd',   # Highly multimodal
        'himmelblau_2d'   # Multiple global optima
    ]
    
    # Best configuration from previous tests
    best_config = {
        'mutation_factor_1': (0.3, 0.9),
        'recombination_factor': (0.3, 0.9)
    }
    
    results = {}
    
    for func_name in test_functions:
        print(f"\nTesting on {func_name}...")
        
        # Get function details
        n_dim = 2 if func_name.endswith('_nd') else None
        func_details = get_function_details(func_name, n_dim)
        eval_func = create_test_function_wrapper(func_details)
        
        # Create parameters based on function bounds
        params_list = []
        for i, bound in enumerate(func_details['bounds']):
            param_name = 'x' if i == 0 else 'y'
            params_list.append({
                'name': param_name,
                'type': 'continuous',
                'min': bound[0],
                'max': bound[1],
                'default': (bound[0] + bound[1]) / 2
            })
        
        parameters = Parameters(params_list)
        
        # Run optimization
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            max_iterations=100,
            **best_config
        )
        
        optimizer.run_optimization()
        
        results[func_name] = {
            'best_metric': optimizer.best_metric,
            'optimum_val': func_details.get('optimum_val', None),
            'error': abs(optimizer.best_metric - func_details.get('optimum_val', 0)) 
                    if 'optimum_val' in func_details else None,
            'iterations': optimizer.iter
        }
        
        print(f"  Best found: {optimizer.best_metric:.6e}")
        if 'optimum_val' in func_details:
            print(f"  True optimum: {func_details['optimum_val']:.6e}")
            print(f"  Error: {results[func_name]['error']:.6e}")
    
    return results


def create_operator_comparison_plots(mutation_results: Dict, crossover_results: Dict, 
                                   combined_results: Dict, results_dir: str):
    """Create comparison plots for operator tests."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Mutation strategies convergence
    ax1 = axes[0, 0]
    for name, result in mutation_results.items():
        ax1.plot(result['convergence'], label=name, linewidth=2)
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Best Metric')
    ax1.set_title('Mutation Strategy Comparison')
    ax1.set_yscale('log')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Crossover methods convergence
    ax2 = axes[0, 1]
    for name, result in crossover_results.items():
        ax2.plot(result['convergence'], label=name, linewidth=2)
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Best Metric')
    ax2.set_title('Crossover Method Comparison')
    ax2.set_yscale('log')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Combined adaptive comparison
    ax3 = axes[1, 0]
    for name, result in combined_results.items():
        ax3.plot(result['convergence'], label=name, linewidth=2)
    ax3.set_xlabel('Iteration')
    ax3.set_ylabel('Best Metric')
    ax3.set_title('Combined Adaptive Comparison')
    ax3.set_yscale('log')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Final performance comparison
    ax4 = axes[1, 1]
    all_results = {**mutation_results, **crossover_results, **combined_results}
    names = list(all_results.keys())
    metrics = [res['best_metric'] for res in all_results.values()]
    
    bars = ax4.bar(range(len(names)), metrics)
    ax4.set_xticks(range(len(names)))
    ax4.set_xticklabels(names, rotation=45, ha='right')
    ax4.set_ylabel('Final Best Metric')
    ax4.set_title('Final Performance Comparison')
    ax4.set_yscale('log')
    ax4.grid(True, alpha=0.3)
    
    # Color bars by performance
    best_metric = min(metrics)
    for bar, metric in zip(bars, metrics):
        if metric <= best_metric * 1.1:  # Within 10% of best
            bar.set_color('green')
        elif metric <= best_metric * 2:  # Within 2x of best
            bar.set_color('yellow')
        else:
            bar.set_color('red')
    
    plt.suptitle('DE Operators Performance Analysis', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'operators_comparison.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nComparison plot saved to: {plot_file}")


def main():
    """Run all operator tests."""
    print("Differential Evolution Operators Test Suite")
    print("=" * 60)
    
    # Create results directory
    results_dir = create_test_results_dir('operators')
    
    # Run tests
    mutation_results = test_mutation_strategies()
    crossover_results = test_crossover_methods()
    combined_results = test_combined_adaptive()
    function_results = test_operators_on_different_functions()
    
    # Create comparison plots
    create_operator_comparison_plots(mutation_results, crossover_results, 
                                   combined_results, results_dir)
    
    # Save test summary
    summary = {
        'test_name': 'DE Operators Test',
        'timestamp': datetime.now().isoformat(),
        'mutation_results': {
            name: {
                'best_metric': res['best_metric'],
                'iterations': res['iterations']
            }
            for name, res in mutation_results.items()
        },
        'crossover_results': {
            name: {
                'best_metric': res['best_metric'],
                'iterations': res['iterations']
            }
            for name, res in crossover_results.items()
        },
        'combined_results': {
            name: {
                'best_metric': res['best_metric'],
                'iterations': res['iterations']
            }
            for name, res in combined_results.items()
        },
        'function_test_results': function_results,
        'best_configurations': {
            'mutation': min(mutation_results.items(), key=lambda x: x[1]['best_metric'])[0],
            'crossover': min(crossover_results.items(), key=lambda x: x[1]['best_metric'])[0],
            'combined': min(combined_results.items(), key=lambda x: x[1]['best_metric'])[0]
        }
    }
    save_test_summary(results_dir, summary)
    
    print(f"\n{'='*60}")
    print("Test Summary:")
    print(f"Best mutation strategy: {summary['best_configurations']['mutation']}")
    print(f"Best crossover method: {summary['best_configurations']['crossover']}")
    print(f"Best combined configuration: {summary['best_configurations']['combined']}")
    print(f"\nResults saved to: {results_dir}")


if __name__ == "__main__":
    main()