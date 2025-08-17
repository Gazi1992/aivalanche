"""
Demonstrate Adam optimizer trajectories on 1000D Rastrigin function with multiple random starting points.
This version ensures we see actual optimization trajectories without premature stopping.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from datetime import datetime
import json

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from aivalanche_lib.optimization.adam import Adam
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions.definitions import rastrigin_nd


def create_rastrigin_eval_func(n_dim):
    """Create an evaluation function for n-dimensional Rastrigin function with analytical gradients."""
    def eval_func(params_df, **kwargs):
        responses = []
        for _, row in params_df.iterrows():
            # Convert row to numpy array
            x = np.array([row[f'x{i}'] for i in range(n_dim)])
            
            # Compute Rastrigin function: f(x) = 10n + sum(x_i^2 - 10*cos(2*pi*x_i))
            metric = rastrigin_nd(x)
            
            # Analytical gradient: df/dx_i = 2*x_i + 20*pi*sin(2*pi*x_i)
            gradients = {}
            for i in range(n_dim):
                grad_i = 2 * x[i] + 20 * np.pi * np.sin(2 * np.pi * x[i])
                gradients[f'x{i}'] = grad_i
            
            responses.append({'metric': metric, 'gradients': gradients})
        return responses
    
    return eval_func


def run_optimization_with_trajectory(n_dim, initial_point, seed, run_name, max_iterations=200):
    """Run optimization and return full trajectory."""
    
    # Create parameter configuration
    param_config = []
    for i in range(n_dim):
        param_dict = {
            'name': f'x{i}',
            'min': -5.12,
            'max': 5.12,
        }
        # Only add default if we have an initial point
        if initial_point is not None:
            param_dict['default'] = initial_point[i]
        param_config.append(param_dict)
    
    parameters = Parameters(param_config)
    eval_func = create_rastrigin_eval_func(n_dim)
    
    # Calculate initial metric if we have an initial point
    if initial_point is not None:
        initial_df = pd.DataFrame([{f'x{i}': initial_point[i] for i in range(n_dim)}])
        initial_response = eval_func(initial_df)
        initial_metric = initial_response[0]['metric']
        print(f"  {run_name}: Initial metric = {initial_metric:.2f}, Initial distance = {np.linalg.norm(initial_point):.2f}")
    else:
        print(f"  {run_name}: Starting from random point")
    
    # Create optimizer with settings optimized for trajectory visualization
    optimizer = Adam(
        seed=seed,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=max_iterations,
        learning_rate=0.02,  # Slightly higher initial learning rate
        learning_rate_decay=0.002,  # Gentle decay: lr_t = lr_0 / (1 + 0.002 * t)
        gradient_method='provided',  # Use analytical gradients for efficiency
        gradient_tolerance=None,  # Disable gradient tolerance check
        beta1=0.9,
        beta2=0.999,
        amsgrad=True,  # Use AMSGrad for better convergence
        boundary_handling=None,  # No boundary constraints (natural for unbounded Rastrigin)
        initial_point=None if initial_point is None else pd.DataFrame([{f'x{i}': initial_point[i] for i in range(n_dim)}]),
        use_defaults_in_initial_point=True if initial_point is not None else False,
        max_iter_without_improvement=100,  # Allow many iterations without improvement
        improvement_threshold=1e-6,  # Small improvement threshold
    )
    
    # Track detailed trajectory
    trajectory = {
        'metrics': [],
        'gradient_norms': [],
        'iterations': []
    }
    
    def progress_callback(**kwargs):
        trajectory['metrics'].append(kwargs['best_metric'])
        if kwargs.get('gradient_norm') is not None:
            trajectory['gradient_norms'].append(kwargs['gradient_norm'])
        trajectory['iterations'].append(kwargs['iteration'])
        
        # Print progress at key iterations
        if kwargs['iteration'] in [1, 25, 50, 100, 150, 200]:
            print(f"    Iteration {kwargs['iteration']:3d}: metric = {kwargs['best_metric']:.2f}, gradient_norm = {kwargs.get('gradient_norm', 0):.2e}")
    
    optimizer.callback_after_each_iter = progress_callback
    
    # Run optimization
    print(f"  Starting optimization...")
    optimizer.run_optimization()
    
    # Get final results
    trajectory['final_metric'] = optimizer.best_metric
    trajectory['iterations_run'] = optimizer.iter
    trajectory['improvement'] = trajectory['metrics'][0] - optimizer.best_metric if len(trajectory['metrics']) > 0 else 0
    trajectory['stop_reason'] = optimizer.stop_reason
    
    # Calculate final distance from origin
    best_params = optimizer.best_parameters
    final_distance = np.sqrt(sum(best_params[f'x{i}']**2 for i in range(n_dim)))
    trajectory['final_distance_from_origin'] = final_distance
    
    print(f"  Completed: Final metric = {optimizer.best_metric:.2f}, Iterations = {optimizer.iter}, Distance from origin = {final_distance:.2f}")
    print(f"  Stop reason: {optimizer.stop_reason}")
    
    return trajectory


def create_convergence_plot(all_trajectories, n_dim, save_path):
    """Create convergence plots for all trajectories."""
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Color map for different runs
    colors = plt.cm.tab10(np.linspace(0, 1, len(all_trajectories)))
    
    # 1. Metric convergence plot
    ax1 = axes[0, 0]
    for i, (name, traj) in enumerate(all_trajectories.items()):
        ax1.plot(traj['iterations'], traj['metrics'], 
                label=f'{name} (final={traj["final_metric"]:.1f})',
                color=colors[i], alpha=0.8, linewidth=2)
    
    ax1.set_xlabel('Iteration', fontsize=11)
    ax1.set_ylabel('Objective Value (log scale)', fontsize=11)
    ax1.set_title(f'Convergence Trajectories - {n_dim}D Rastrigin', fontsize=12, fontweight='bold')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=9, loc='best')
    
    # 2. Gradient norm evolution
    ax2 = axes[0, 1]
    for i, (name, traj) in enumerate(all_trajectories.items()):
        if traj['gradient_norms']:
            ax2.plot(range(len(traj['gradient_norms'])), traj['gradient_norms'],
                    label=name, color=colors[i], alpha=0.8, linewidth=2)
    
    ax2.set_xlabel('Iteration', fontsize=11)
    ax2.set_ylabel('Gradient Norm (log scale)', fontsize=11)
    ax2.set_title('Gradient Norm Evolution', fontsize=12, fontweight='bold')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # 3. Improvement over time
    ax3 = axes[1, 0]
    for i, (name, traj) in enumerate(all_trajectories.items()):
        if len(traj['metrics']) > 0:
            initial_metric = traj['metrics'][0]
            improvements = [initial_metric - m for m in traj['metrics']]
            ax3.plot(traj['iterations'], improvements,
                    label=name, color=colors[i], alpha=0.8, linewidth=2)
    
    ax3.set_xlabel('Iteration', fontsize=11)
    ax3.set_ylabel('Improvement from Initial', fontsize=11)
    ax3.set_title('Cumulative Improvement', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=9)
    
    # 4. Summary statistics
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # Calculate statistics
    final_metrics = [traj['final_metric'] for traj in all_trajectories.values()]
    improvements = [traj['improvement'] for traj in all_trajectories.values()]
    iterations = [traj['iterations_run'] for traj in all_trajectories.values()]
    distances = [traj['final_distance_from_origin'] for traj in all_trajectories.values()]
    
    summary_text = f"""Summary Statistics ({n_dim}D Rastrigin)
    
Final Metrics:
  Mean: {np.mean(final_metrics):.2f}
  Std:  {np.std(final_metrics):.2f}
  Best: {np.min(final_metrics):.2f}
  Worst: {np.max(final_metrics):.2f}

Performance:
  Mean Improvement: {np.mean(improvements):.2f}
  Mean Iterations: {np.mean(iterations):.0f}
  Mean Final Distance: {np.mean(distances):.2f}
  
Key Observations:
• Random initialization leads to diverse trajectories
• Some runs find better local minima than others
• High-dimensional Rastrigin is extremely challenging
• Gradient-based methods struggle with multimodality
• High-D space has exponentially many local minima"""
    
    ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle(f'Adam Optimizer Analysis: {n_dim}D Rastrigin Function', 
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\nPlot saved to: {save_path}")


def main():
    """Run demonstration of Adam optimizer trajectories on 1000D Rastrigin."""
    
    print("\n" + "="*80)
    print("ADAM OPTIMIZER TRAJECTORY DEMONSTRATION - HIGH-DIMENSIONAL RASTRIGIN")
    print("="*80)
    
    # Configuration
    n_dim = 1000    # Moderate-high dimensions
    n_runs = 5    # Number of different random starts  
    max_iterations = 1000  # More iterations to see decay effect
    
    print(f"\nConfiguration:")
    print(f"  Dimensions: {n_dim}")
    print(f"  Number of runs: {n_runs}")
    print(f"  Max iterations per run: {max_iterations}")
    print(f"  Function: Rastrigin (highly multimodal)")
    print(f"  Global optimum: f(0, 0, ..., 0) = 0")
    print(f"  Number of local minima: ~10^{n_dim}")
    print(f"\nAdam settings:")
    print(f"  Initial learning rate: 0.02")
    print(f"  Learning rate decay: 0.002 (lr_t = 0.02 / (1 + 0.002*t))")
    print(f"  At iteration 100: lr = {0.02 / (1 + 0.002*100):.4f}")
    print(f"  At iteration 200: lr = {0.02 / (1 + 0.002*200):.4f}")
    print(f"  Gradient method: Analytical (provided)")
    print(f"  AMSGrad: Enabled")
    
    # Create results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join(
        os.path.dirname(__file__), 
        'results', 
        f'adam_1000d_trajectories_{timestamp}'
    )
    os.makedirs(results_dir, exist_ok=True)
    
    print(f"\nResults will be saved to: {results_dir}")
    print(f"\nRunning {n_runs} optimizations from random starting points:")
    print("-" * 60)
    
    # Run optimizations from different starting points
    all_trajectories = {}
    
    for run in range(n_runs):
        run_name = f"Run{run+1}"
        
        # Use random initialization (let Adam pick the starting point)
        # This will now use the fixed random initialization, not (0,0)
        trajectory = run_optimization_with_trajectory(
            n_dim, 
            initial_point=None,  # Let Adam choose randomly
            seed=42 + run * 137,  # Different seed for each run
            run_name=run_name,
            max_iterations=max_iterations
        )
        
        all_trajectories[run_name] = trajectory
        print()  # Add spacing between runs
    
    print("-" * 60)
    
    # Save raw trajectories data
    trajectories_path = os.path.join(results_dir, 'trajectories.json')
    # Convert numpy values to Python native types for JSON serialization
    save_data = {}
    for name, traj in all_trajectories.items():
        save_data[name] = {
            'final_metric': float(traj['final_metric']),
            'iterations_run': int(traj['iterations_run']),
            'improvement': float(traj['improvement']),
            'final_distance_from_origin': float(traj['final_distance_from_origin']),
            'stop_reason': traj['stop_reason'],
            'metrics': [float(m) for m in traj['metrics']],
            'gradient_norms': [float(g) for g in traj['gradient_norms']],
        }
    
    with open(trajectories_path, 'w') as f:
        json.dump(save_data, f, indent=2)
    print(f"\nTrajectory data saved to: {trajectories_path}")
    
    # Create visualization
    plot_path = os.path.join(results_dir, 'convergence_analysis.png')
    create_convergence_plot(all_trajectories, n_dim, plot_path)
    
    # Print summary
    print(f"\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    final_metrics = [traj['final_metric'] for traj in all_trajectories.values()]
    best_idx = np.argmin(final_metrics)
    worst_idx = np.argmax(final_metrics)
    
    print(f"\nAcross {n_runs} runs with random starting points:")
    print(f"  Best final metric: {final_metrics[best_idx]:.2f} (Run {best_idx+1})")
    print(f"  Worst final metric: {final_metrics[worst_idx]:.2f} (Run {worst_idx+1})")
    print(f"  Mean final metric: {np.mean(final_metrics):.2f} ± {np.std(final_metrics):.2f}")
    
    # Check how many found the global optimum
    global_optimum_found = sum(1 for m in final_metrics if m < 10)  # Within 10 of global optimum
    print(f"\nRuns near global optimum (metric < 10): {global_optimum_found}/{n_runs}")
    
    if global_optimum_found == 0:
        print("  -> All runs got stuck in local minima (expected for high-D Rastrigin)")
    elif global_optimum_found < n_runs:
        print("  -> Most runs got stuck in local minima (realistic behavior)")
    else:
        print("  -> Surprisingly good performance!")
    
    print(f"\nKey Insights:")
    print("1. Starting point significantly affects final solution quality")
    print("2. 1000D Rastrigin is extremely challenging for gradient-based methods")
    print("3. Adam typically gets trapped in one of the many local minima")
    print("4. The trajectories show gradual improvement before convergence")
    print("5. Random initialization (not always 0,0) gives diverse results")
    
    print(f"\nAll results saved to: {results_dir}")
    print("="*80)


if __name__ == "__main__":
    main()