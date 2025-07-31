"""
Comprehensive comparison of Differential Evolution strategies on challenging optimization problems.

This script tests various DE configurations including:
- Pure DE (baseline)
- DE with different perturbation strategies (light to aggressive)
- DE with local refinement (DLS)
- DE with both perturbations and refinement

The test uses the Griewank function in 20 dimensions, which is a challenging
multimodal function with many local minima.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from datetime import datetime
import json

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details, generate_parameters_config


# =============================================================================
# Common Configuration
# =============================================================================

# Problem configuration
PROBLEM_CONFIG = {
    'function_name': 'griewank_nd',
    'n_dim': 20,
    'seed': 42
}

# Common optimizer settings
COMMON_OPTIMIZER_CONFIG = {
    'max_iterations': 1000,
    'max_iter_without_improvement': 500,
    'metric_threshold': 1e-10,
    'improvement_threshold': 0.0001,
    'pop_size': 100,  # 5x dimensions for challenging problem
}

# Note: Refinement is now configured through refinement_mode in each strategy

# =============================================================================
# Strategy Configurations
# =============================================================================

STRATEGIES = {
    'pure_de': {
        'name': 'Pure DE (Baseline)',
        'config': {
            'perturbation_mode': 'off',
            'refinement_mode': 'off'
        }
    },
    
    'de_light_perturbation': {
        'name': 'DE + Light Perturbation',
        'config': {
            'perturbation_mode': 'custom',
            'perturbation_config': {
                'trigger_ratio': 0.8,  # Trigger late
                'param_selection': 'smart',
                'param_ratio': (0.1, 0.2),  # Few parameters
                'population_ratio': (0.1, 0.2),  # Small population fraction
                'scale': 'adaptive_weak',
                'memory_enabled': True,
                'cooldown_ratio': 0.3,
                'sigma_threshold': 0.005
            },
            'refinement_mode': 'off'
        }
    },
    
    'de_moderate_perturbation': {
        'name': 'DE + Moderate Perturbation',
        'config': {
            'perturbation_mode': 'auto',  # Balanced auto mode
            'refinement_mode': 'off'
        }
    },
    
    'de_strong_perturbation': {
        'name': 'DE + Strong Perturbation',
        'config': {
            'perturbation_mode': 'custom',
            'perturbation_config': {
                'trigger_ratio': 0.3,  # Trigger early
                'param_selection': 'smart',
                'param_ratio': (0.3, 0.5),  # Many parameters
                'population_ratio': (0.3, 0.5),  # Large population fraction
                'scale': 'adaptive_strong',
                'memory_enabled': True,
                'cooldown_ratio': 0.1,
                'sigma_threshold': 0.02
            },
            'refinement_mode': 'off'
        }
    },
    
    'de_aggressive_perturbation': {
        'name': 'DE + Aggressive Perturbation',
        'config': {
            'perturbation_mode': 'aggressive',
            'refinement_mode': 'off'
        }
    },
    
    'de_refinement': {
        'name': 'DE + Refinement',
        'config': {
            'perturbation_mode': 'off',
            'refinement_mode': 'auto'
        }
    },
    
    'de_moderate_perturb_refine': {
        'name': 'DE + Moderate Perturbation + Refinement',
        'config': {
            'perturbation_mode': 'auto',
            'refinement_mode': 'moderate'  # Triggers on stagnation
        }
    },
    
    'de_strong_perturb_refine': {
        'name': 'DE + Strong Perturbation + Refinement',
        'config': {
            'perturbation_mode': 'custom',
            'perturbation_config': {
                'trigger_ratio': 0.3,
                'param_selection': 'smart',
                'param_ratio': (0.3, 0.5),
                'population_ratio': (0.3, 0.5),
                'scale': 'adaptive_strong',
                'memory_enabled': True,
                'cooldown_ratio': 0.1,
                'sigma_threshold': 0.02
            },
            'refinement_mode': 'aggressive'  # Thorough refinement
        }
    }
}

# =============================================================================
# Helper Functions
# =============================================================================

def create_test_function_wrapper(func_details):
    """
    Creates a wrapper function that adapts test functions to the format expected by the optimizer.
    """
    func = func_details['func']
    dim = func_details['dim']
    
    def wrapper(parameters, **kwargs):
        responses = []
        
        for _, row in parameters.iterrows():
            # Extract parameter values in order (x1, x2, ..., xn)
            x_values = []
            for i in range(dim):
                param_name = f'x{i+1}'
                if param_name in row:
                    x_values.append(row[param_name])
            
            # Convert to numpy array
            x = np.array(x_values)
            
            # Evaluate function
            value = func(x)
            
            # Create response dict
            response = {
                'metric': value,
                'data': {f'x{i+1}': x_values[i] for i in range(len(x_values))}
            }
            responses.append(response)
        
        return responses
    
    return wrapper


class StrategyMonitor:
    """Monitor to track detailed optimization progress."""
    
    def __init__(self, strategy_name):
        self.strategy_name = strategy_name
        self.history = {
            'iterations': [],
            'best_metrics': [],
            'mean_metrics': [],
            'std_metrics': [],
            'population_diversity': [],
            'iter_no_improvement': [],
            'perturbation_events': [],
            'refinement_events': []
        }
        
    def record_iteration(self, optimizer):
        """Record current iteration state."""
        self.history['iterations'].append(optimizer.iter)
        self.history['best_metrics'].append(optimizer.best_metric)
        
        # Calculate population statistics
        if hasattr(optimizer, 'survivors_metrics'):
            # Handle both 1D and 2D arrays
            metrics = optimizer.survivors_metrics
            if metrics.ndim > 1:
                metrics = metrics[:, 0]
            self.history['mean_metrics'].append(np.mean(metrics))
            self.history['std_metrics'].append(np.std(metrics))
        else:
            self.history['mean_metrics'].append(optimizer.best_metric)
            self.history['std_metrics'].append(0)
        
        # Population diversity
        pop_diversity = np.mean(np.std(optimizer.survivors, axis=0))
        self.history['population_diversity'].append(pop_diversity)
        
        # Stagnation counter
        self.history['iter_no_improvement'].append(optimizer.iter_no_improvement)
        
        # Check for perturbation event
        if hasattr(optimizer, 'perturbation_memory'):
            last_perturb = optimizer.perturbation_memory.get('last_perturbation_iter', -1)
            if last_perturb == optimizer.iter:
                self.history['perturbation_events'].append(optimizer.iter)
        
        # Check for refinement event
        if hasattr(optimizer, '_refinement_applied') and optimizer._refinement_applied:
            self.history['refinement_events'].append(optimizer.iter)
            optimizer._refinement_applied = False  # Reset flag


def run_strategy_comparison():
    """Run the main strategy comparison experiment."""
    
    print("="*80)
    print("DIFFERENTIAL EVOLUTION STRATEGY COMPARISON")
    print(f"Problem: {PROBLEM_CONFIG['function_name']} ({PROBLEM_CONFIG['n_dim']}D)")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Setup problem
    func_details = get_function_details(
        PROBLEM_CONFIG['function_name'], 
        n_dim=PROBLEM_CONFIG['n_dim']
    )
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create results directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = os.path.join(
        os.path.dirname(__file__), 
        f'test_strategies_comparison_{timestamp}'
    )
    os.makedirs(results_dir, exist_ok=True)
    
    # Save configuration
    config_data = {
        'problem': PROBLEM_CONFIG,
        'common_config': COMMON_OPTIMIZER_CONFIG,
        'strategies': {k: v['name'] for k, v in STRATEGIES.items()},
        'func_details': {
            'name': PROBLEM_CONFIG['function_name'],
            'dim': func_details['dim'],
            'optimum_val': func_details['optimum_val'],
            'optimum_point': func_details.get('optimum_point', 'origin')
        }
    }
    
    with open(os.path.join(results_dir, 'experiment_config.json'), 'w') as f:
        json.dump(config_data, f, indent=2)
    
    # Run strategies
    results = {}
    monitors = {}
    
    for strategy_id, strategy_info in STRATEGIES.items():
        print(f"\n{'='*60}")
        print(f"Running: {strategy_info['name']}")
        print(f"{'='*60}")
        
        # Create monitor
        monitor = StrategyMonitor(strategy_info['name'])
        
        # Callback function
        def callback_after_each_iter(optimizer, **kwargs):
            monitor.record_iteration(optimizer)
        
        # Create optimizer with merged configuration
        optimizer_config = {
            **COMMON_OPTIMIZER_CONFIG,
            **strategy_info['config'],
            'seed': PROBLEM_CONFIG['seed'],
            'eval_func': eval_func,
            'parameters': parameters,
            'opt_min_or_max': 'min',
            'callback_after_each_iter': callback_after_each_iter,
            'results_dir': os.path.join(results_dir, strategy_id)
        }
        
        optimizer = DifferentialEvolution(**optimizer_config)
        
        # Run optimization
        start_time = datetime.now()
        optimizer.run_optimization()
        end_time = datetime.now()
        
        # Store results
        results[strategy_id] = {
            'optimizer': optimizer,
            'monitor': monitor,
            'runtime': (end_time - start_time).total_seconds(),
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'evaluations': optimizer.nr_evaluations,
            'stop_reason': optimizer.stop_reason,
            'distance_from_optimum': abs(optimizer.best_metric - func_details['optimum_val'])
        }
        
        monitors[strategy_id] = monitor
        
        # Print summary
        print(f"\nResults for {strategy_info['name']}:")
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Distance from optimum: {results[strategy_id]['distance_from_optimum']:.6e}")
        print(f"  Iterations: {optimizer.iter}")
        print(f"  Evaluations: {optimizer.nr_evaluations}")
        print(f"  Runtime: {results[strategy_id]['runtime']:.2f} seconds")
        print(f"  Stop reason: {optimizer.stop_reason}")
        
        if hasattr(optimizer, 'perturbation_memory'):
            n_perturb = optimizer.perturbation_memory.get('perturbations_applied', 0)
            print(f"  Perturbations applied: {n_perturb}")
    
    # Create visualizations
    print(f"\n{'='*60}")
    print("Creating visualizations...")
    print(f"{'='*60}")
    
    create_comparison_visualizations(results, monitors, func_details, results_dir)
    
    # Save summary results
    save_summary_results(results, results_dir)
    
    print(f"\n{'='*60}")
    print(f"Experiment completed!")
    print(f"Results saved to: {results_dir}")
    print(f"{'='*60}")
    
    return results, monitors


def create_comparison_visualizations(results, monitors, func_details, results_dir):
    """Create comprehensive visualizations comparing all strategies."""
    
    # 1. Convergence curves comparison
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    for strategy_id, monitor in monitors.items():
        strategy_name = STRATEGIES[strategy_id]['name']
        iterations = monitor.history['iterations']
        best_metrics = monitor.history['best_metrics']
        
        # Plot convergence
        ax1.semilogy(iterations, best_metrics, linewidth=2, label=strategy_name, alpha=0.8)
        
        # Mark perturbation events
        for p_iter in monitor.history['perturbation_events'][:5]:  # First 5 only
            idx = iterations.index(p_iter) if p_iter in iterations else None
            if idx is not None:
                ax1.plot(p_iter, best_metrics[idx], 'o', markersize=6, alpha=0.6)
    
    ax1.axhline(y=func_details['optimum_val'], color='red', linestyle='--', 
                alpha=0.5, label='Global Optimum')
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Best Metric (log scale)')
    ax1.set_title('Convergence Comparison')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 2. Population diversity comparison
    for strategy_id, monitor in monitors.items():
        strategy_name = STRATEGIES[strategy_id]['name']
        iterations = monitor.history['iterations']
        diversity = monitor.history['population_diversity']
        
        ax2.plot(iterations, diversity, linewidth=2, label=strategy_name, alpha=0.8)
    
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Population Diversity (avg std)')
    ax2.set_title('Population Diversity Evolution')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'convergence_diversity_comparison.png'), 
                dpi=150, bbox_inches='tight')
    plt.close()
    
    # 3. Performance summary heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Prepare data for heatmap
    metrics = ['Best Metric', 'Distance from Optimum', 'Iterations', 
               'Evaluations', 'Runtime (s)', 'Efficiency']
    
    data = []
    strategy_names = []
    
    for strategy_id, result in results.items():
        strategy_names.append(STRATEGIES[strategy_id]['name'])
        efficiency = -np.log10(result['distance_from_optimum'] + 1e-20) / result['evaluations'] * 1000
        data.append([
            result['best_metric'],
            result['distance_from_optimum'],
            result['iterations'],
            result['evaluations'],
            result['runtime'],
            efficiency
        ])
    
    data = np.array(data)
    
    # Normalize data for heatmap (0-1 scale per metric)
    data_norm = np.zeros_like(data)
    for i in range(data.shape[1]):
        col = data[:, i]
        if i in [0, 1]:  # For metrics where lower is better
            data_norm[:, i] = 1 - (col - col.min()) / (col.max() - col.min() + 1e-10)
        else:  # For metrics where interpretation depends
            data_norm[:, i] = (col - col.min()) / (col.max() - col.min() + 1e-10)
    
    # Create heatmap
    im = ax.imshow(data_norm.T, cmap='RdYlGn', aspect='auto')
    
    # Set ticks
    ax.set_xticks(np.arange(len(strategy_names)))
    ax.set_yticks(np.arange(len(metrics)))
    ax.set_xticklabels(strategy_names, rotation=45, ha='right')
    ax.set_yticklabels(metrics)
    
    # Add text annotations
    for i in range(len(metrics)):
        for j in range(len(strategy_names)):
            text_color = 'white' if data_norm[j, i] < 0.5 else 'black'
            if i < 2:  # Scientific notation for small numbers
                text = ax.text(j, i, f'{data[j, i]:.2e}', ha='center', va='center',
                             color=text_color, fontsize=8)
            else:
                text = ax.text(j, i, f'{data[j, i]:.0f}', ha='center', va='center',
                             color=text_color, fontsize=8)
    
    ax.set_title('Strategy Performance Summary\n(Green = Better, Red = Worse)', pad=20)
    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'performance_summary_heatmap.png'), 
                dpi=150, bbox_inches='tight')
    plt.close()
    
    # 4. Box plot of final metrics
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Prepare data for box plots
    final_metrics = []
    distances = []
    labels = []
    
    for strategy_id, result in results.items():
        optimizer = result['optimizer']
        if hasattr(optimizer, 'survivors_metrics'):
            metrics = optimizer.survivors_metrics
            if metrics.ndim > 1:
                metrics = metrics[:, 0]
            final_metrics.append(metrics)
        else:
            final_metrics.append([optimizer.best_metric])
        
        distances.append(result['distance_from_optimum'])
        labels.append(STRATEGIES[strategy_id]['name'].replace(' + ', '\n+ '))
    
    # Box plot of final population metrics
    bp1 = ax1.boxplot(final_metrics, labels=labels, patch_artist=True, showfliers=False)
    ax1.set_yscale('log')
    ax1.set_ylabel('Final Population Metrics (log scale)')
    ax1.set_title('Distribution of Final Population')
    ax1.tick_params(axis='x', rotation=45)
    
    # Color boxes by strategy type
    colors = []
    for strategy_id in results.keys():
        if 'aggressive' in strategy_id:
            colors.append('red')
        elif 'strong' in strategy_id:
            colors.append('orange')
        elif 'moderate' in strategy_id:
            colors.append('yellow')
        elif 'light' in strategy_id:
            colors.append('lightgreen')
        elif 'refinement' in strategy_id and 'perturb' in strategy_id:
            colors.append('purple')
        elif 'refinement' in strategy_id:
            colors.append('blue')
        else:
            colors.append('gray')
    
    for patch, color in zip(bp1['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    # Bar plot of distances from optimum
    bars = ax2.bar(range(len(distances)), distances, color=colors, alpha=0.6)
    ax2.set_yscale('log')
    ax2.set_ylabel('Distance from Global Optimum (log scale)')
    ax2.set_title('Final Distance from Optimum')
    ax2.set_xticks(range(len(labels)))
    ax2.set_xticklabels(labels, rotation=45, ha='right')
    
    # Add value labels on bars
    for bar, dist in zip(bars, distances):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{dist:.2e}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'final_metrics_comparison.png'), 
                dpi=150, bbox_inches='tight')
    plt.close()
    
    # 5. Perturbation and refinement timeline
    fig, axes = plt.subplots(len(monitors), 1, figsize=(14, 2*len(monitors)), 
                            sharex=True)
    
    if len(monitors) == 1:
        axes = [axes]
    
    for idx, (strategy_id, monitor) in enumerate(monitors.items()):
        ax = axes[idx]
        strategy_name = STRATEGIES[strategy_id]['name']
        
        # Plot metric evolution
        iterations = monitor.history['iterations']
        best_metrics = monitor.history['best_metrics']
        
        ax.semilogy(iterations, best_metrics, 'b-', linewidth=1, alpha=0.7)
        ax.set_ylabel('Metric', fontsize=8)
        ax.set_title(strategy_name, fontsize=10)
        
        # Mark perturbation events
        for p_iter in monitor.history['perturbation_events']:
            ax.axvline(x=p_iter, color='red', linestyle='--', alpha=0.5, linewidth=1)
        
        # Mark refinement events
        for r_iter in monitor.history['refinement_events']:
            ax.axvline(x=r_iter, color='green', linestyle=':', alpha=0.5, linewidth=1)
        
        # Add legend for the first subplot only
        if idx == 0 and (monitor.history['perturbation_events'] or 
                        monitor.history['refinement_events']):
            ax.plot([], [], 'r--', label='Perturbation', linewidth=1)
            ax.plot([], [], 'g:', label='Refinement', linewidth=1)
            ax.legend(loc='upper right', fontsize=8)
        
        ax.grid(True, alpha=0.2)
        ax.set_xlim(0, max(iterations))
    
    axes[-1].set_xlabel('Iteration')
    plt.suptitle('Strategy Timeline with Perturbation and Refinement Events', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'strategy_timeline.png'), 
                dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Visualizations created successfully!")


def save_summary_results(results, results_dir):
    """Save summary results to CSV and JSON files."""
    
    # Create summary DataFrame
    summary_data = []
    
    for strategy_id, result in results.items():
        strategy_name = STRATEGIES[strategy_id]['name']
        
        row = {
            'Strategy': strategy_name,
            'Best Metric': result['best_metric'],
            'Distance from Optimum': result['distance_from_optimum'],
            'Iterations': result['iterations'],
            'Evaluations': result['evaluations'],
            'Runtime (s)': result['runtime'],
            'Stop Reason': result['stop_reason'],
            'Efficiency': -np.log10(result['distance_from_optimum'] + 1e-20) / result['evaluations'] * 1000
        }
        
        # Add perturbation stats if available
        optimizer = result['optimizer']
        if hasattr(optimizer, 'perturbation_memory'):
            row['Perturbations Applied'] = optimizer.perturbation_memory.get('perturbations_applied', 0)
        else:
            row['Perturbations Applied'] = 0
        
        summary_data.append(row)
    
    # Save to CSV
    df = pd.DataFrame(summary_data)
    df = df.sort_values('Distance from Optimum')
    df.to_csv(os.path.join(results_dir, 'summary_results.csv'), index=False)
    
    # Save detailed results to JSON
    detailed_results = {}
    for strategy_id, result in results.items():
        monitor = result['monitor']
        detailed_results[strategy_id] = {
            'strategy_name': STRATEGIES[strategy_id]['name'],
            'best_metric': float(result['best_metric']),
            'distance_from_optimum': float(result['distance_from_optimum']),
            'iterations': int(result['iterations']),
            'evaluations': int(result['evaluations']),
            'runtime': float(result['runtime']),
            'stop_reason': result['stop_reason'],
            'final_metrics': {
                'mean': float(monitor.history['mean_metrics'][-1]) if monitor.history['mean_metrics'] else None,
                'std': float(monitor.history['std_metrics'][-1]) if monitor.history['std_metrics'] else None,
                'diversity': float(monitor.history['population_diversity'][-1]) if monitor.history['population_diversity'] else None
            },
            'perturbation_events': len(monitor.history['perturbation_events']),
            'refinement_events': len(monitor.history['refinement_events'])
        }
    
    with open(os.path.join(results_dir, 'detailed_results.json'), 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"Summary results saved to CSV and JSON files")


if __name__ == "__main__":
    # Run the comparison
    results, monitors = run_strategy_comparison()
    
    # Print final ranking
    print("\n" + "="*60)
    print("FINAL RANKING (by distance from optimum)")
    print("="*60)
    
    ranking = sorted(results.items(), key=lambda x: x[1]['distance_from_optimum'])
    
    for rank, (strategy_id, result) in enumerate(ranking, 1):
        strategy_name = STRATEGIES[strategy_id]['name']
        print(f"{rank}. {strategy_name}")
        print(f"   Distance from optimum: {result['distance_from_optimum']:.6e}")
        print(f"   Best metric: {result['best_metric']:.6e}")
        print(f"   Evaluations: {result['evaluations']}")
        print(f"   Runtime: {result['runtime']:.2f}s")
        print()