"""
Test script to demonstrate the new perturbation modes functionality.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

from aivalanche_lib.optimization.differential_evolution import (
    DifferentialEvolution,
    PERTURBATION_MODES,
    get_perturbation_mode_description,
    suggest_perturbation_mode
)
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details, generate_parameters_config


def test_perturbation_modes_functionality():
    """Test basic perturbation modes functionality."""
    print("\n" + "="*60)
    print("TESTING PERTURBATION MODES FUNCTIONALITY")
    print("="*60)
    
    # Test available modes
    print("\nAvailable perturbation modes:")
    for mode in PERTURBATION_MODES.keys():
        description = get_perturbation_mode_description(mode)
        print(f"  {mode:15s}: {description}")
    
    # Test mode suggestions
    print("\nMode suggestions for different scenarios:")
    
    scenarios = [
        {'problem_type': 'smooth', 'desc': 'Smooth function'},
        {'problem_type': 'multimodal', 'desc': 'Multimodal function'},
        {'problem_type': 'highly_multimodal', 'desc': 'Highly multimodal function'},
        {'problem_type': 'rugged', 'desc': 'Rugged landscape'},
        {'landscape': 'convex', 'desc': 'Convex landscape'},
        {'landscape': 'many_local_minima', 'desc': 'Many local minima'},
        {'landscape': 'deceptive', 'desc': 'Deceptive landscape'},
        {'n_dim': 50, 'desc': 'High-dimensional (50D)'},
        {'noise_level': 'high', 'desc': 'High noise'},
        {'convergence_speed': 'fast', 'desc': 'Fast convergence desired'},
        {'convergence_speed': 'thorough', 'desc': 'Thorough search desired'},
    ]
    
    for scenario in scenarios:
        desc = scenario.pop('desc')
        suggested_mode = suggest_perturbation_mode(**scenario)
        print(f"  {desc:30s}: {suggested_mode}")


def compare_perturbation_modes():
    """Compare different perturbation modes on a multimodal function."""
    print("\n" + "="*60)
    print("PERTURBATION MODES COMPARISON")
    print("="*60)
    
    # Setup test function (Rastrigin 5D - highly multimodal)
    func_name = 'rastrigin_nd'
    n_dim = 5
    func_details = get_function_details(func_name, n_dim=n_dim)
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    
    # Create evaluation function
    def eval_func(parameters_df, **kwargs):
        responses = []
        for _, row in parameters_df.iterrows():
            x = np.array([row[f'x{i+1}'] for i in range(n_dim)])
            value = func_details['func'](x)
            responses.append({
                'metric': value,
                'data': {f'x{i+1}': x[i] for i in range(n_dim)}
            })
        return responses
    
    # Test different perturbation modes
    test_modes = ['off', 'very_light', 'light', 'auto', 'moderate', 'strong', 'smart_escape']
    
    results = {}
    
    # Create results directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = os.path.join(
        os.path.dirname(__file__), 
        f'test_perturbation_modes_{timestamp}'
    )
    os.makedirs(results_dir, exist_ok=True)
    
    for mode in test_modes:
        print(f"\nTesting mode: {mode}")
        print(f"Description: {get_perturbation_mode_description(mode)}")
        
        # Create optimizer
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            opt_min_or_max='min',
            pop_size=50,
            max_iterations=200,
            max_iter_without_improvement=50,
            perturbation_mode=mode,
            results_dir=os.path.join(results_dir, mode)
        )
        
        # Run optimization
        optimizer.run_optimization()
        
        # Store results
        results[mode] = {
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'evaluations': optimizer.nr_evaluations,
            'stop_reason': optimizer.stop_reason,
            'history': optimizer.history['bests'],
            'perturbation_count': len(optimizer.perturbation_memory.get('history', [])) if hasattr(optimizer, 'perturbation_memory') else 0
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Iterations: {optimizer.iter}")
        print(f"  Perturbations: {results[mode]['perturbation_count']}")
    
    # Create comparison plot
    create_comparison_plot(results, func_details, results_dir)
    
    return results


def create_comparison_plot(results, func_details, results_dir):
    """Create visualization comparing perturbation modes."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Convergence curves
    for mode, result in results.items():
        history = result['history']
        iterations = [h['iteration'] for h in history]
        metrics = [h['metric'] for h in history]
        
        ax1.semilogy(iterations, metrics, label=f"{mode} (perturb: {result['perturbation_count']})", 
                     linewidth=2, alpha=0.8)
    
    ax1.axhline(y=func_details['optimum_val'], color='red', linestyle='--', 
                alpha=0.5, label='Global Optimum')
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Best Metric (log scale)')
    ax1.set_title('Convergence Comparison of Perturbation Modes')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Final performance comparison
    modes = list(results.keys())
    final_metrics = [results[mode]['best_metric'] for mode in modes]
    perturbation_counts = [results[mode]['perturbation_count'] for mode in modes]
    
    x = np.arange(len(modes))
    width = 0.35
    
    # Create bars
    bars1 = ax2.bar(x - width/2, final_metrics, width, label='Final Metric', alpha=0.8)
    
    # Create secondary y-axis for perturbation counts
    ax2_twin = ax2.twinx()
    bars2 = ax2_twin.bar(x + width/2, perturbation_counts, width, 
                         label='Perturbations', color='orange', alpha=0.8)
    
    ax2.set_xlabel('Perturbation Mode')
    ax2.set_ylabel('Final Metric')
    ax2_twin.set_ylabel('Number of Perturbations')
    ax2.set_title('Final Performance and Perturbation Count')
    ax2.set_xticks(x)
    ax2.set_xticklabels(modes, rotation=45, ha='right')
    
    # Add value labels on bars
    for bar, value in zip(bars1, final_metrics):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                 f'{value:.2e}', ha='center', va='bottom', fontsize=8)
    
    for bar, count in zip(bars2, perturbation_counts):
        height = bar.get_height()
        ax2_twin.text(bar.get_x() + bar.get_width()/2., height,
                      f'{count}', ha='center', va='bottom', fontsize=8)
    
    # Combine legends
    h1, l1 = ax2.get_legend_handles_labels()
    h2, l2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(h1+h2, l1+l2, loc='upper right')
    
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=func_details['optimum_val'], color='red', linestyle='--', 
                alpha=0.5, label='Global Optimum')
    
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'perturbation_modes_comparison.png'), 
                dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\nPlot saved to: {os.path.join(results_dir, 'perturbation_modes_comparison.png')}")


def test_custom_perturbation_configuration():
    """Test custom perturbation configuration."""
    print("\n" + "="*60)
    print("TESTING CUSTOM PERTURBATION CONFIGURATION")
    print("="*60)
    
    # Setup simple test function
    func_details = get_function_details('sphere_nd', n_dim=3)
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    
    def eval_func(parameters_df, **kwargs):
        responses = []
        for _, row in parameters_df.iterrows():
            x = np.array([row[f'x{i+1}'] for i in range(3)])
            value = func_details['func'](x)
            responses.append({'metric': value})
        return responses
    
    # Custom perturbation configuration
    custom_config = {
        'trigger_ratio': 0.4,
        'param_selection': 'smart',
        'param_ratio': (0.3, 0.5),
        'population_ratio': (0.2, 0.4),
        'scale': (1.0, 3.0),  # Custom scale range
        'memory_enabled': True,
        'cooldown_ratio': 0.15,
        'sigma_threshold': 0.015,
        # Additional custom parameters
        'custom_parameter': 'test_value'
    }
    
    print("Creating optimizer with custom perturbation configuration...")
    print(f"Configuration: {custom_config}")
    
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        pop_size=30,
        max_iterations=50,
        max_iter_without_improvement=20,
        perturbation_mode='custom',
        perturbation_config=custom_config
    )
    
    print("\nRunning optimization with custom perturbation...")
    optimizer.run_optimization()
    
    print(f"\nOptimization completed:")
    print(f"  Best metric: {optimizer.best_metric:.6e}")
    print(f"  Iterations: {optimizer.iter}")
    
    if hasattr(optimizer, 'perturbation_memory'):
        n_perturb = len(optimizer.perturbation_memory.get('history', []))
        print(f"  Perturbations applied: {n_perturb}")


def visualize_perturbation_modes_table():
    """Create a visual comparison table of perturbation modes."""
    from aivalanche_lib.optimization.differential_evolution.perturbation_modes import get_mode_comparison
    
    print("\n" + "="*60)
    print("PERTURBATION MODES COMPARISON TABLE")
    print("="*60)
    
    df = get_mode_comparison()
    print("\n" + str(df))
    
    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = os.path.join(
        os.path.dirname(__file__), 
        f'test_perturbation_modes_{timestamp}'
    )
    os.makedirs(results_dir, exist_ok=True)
    
    df.to_csv(os.path.join(results_dir, 'perturbation_modes_comparison.csv'), index=False)
    print(f"\nTable saved to: {os.path.join(results_dir, 'perturbation_modes_comparison.csv')}")


if __name__ == "__main__":
    # Test basic functionality
    test_perturbation_modes_functionality()
    
    # Visualize modes table
    visualize_perturbation_modes_table()
    
    # Run comparison test
    results = compare_perturbation_modes()
    
    # Test custom configuration
    test_custom_perturbation_configuration()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)