"""
Test Differential Evolution perturbation mechanisms.

This test evaluates different perturbation strategies including:
- Different perturbation modes on various problems
- High-dimensional visualization of perturbation effects
- Analysis of when and why perturbations are triggered
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details

from test_utils import create_test_results_dir, save_test_summary, create_test_function_wrapper


def test_perturbation_modes(function_name: str = 'himmelblau_2d', n_iterations: int = 100):
    """Test different perturbation modes on a multimodal function."""
    print("\n" + "="*60)
    print("Testing Different Perturbation Modes")
    print("="*60)
    
    func_details = get_function_details(function_name)
    eval_func = create_test_function_wrapper(func_details)
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    modes = ['off', 'light', 'moderate', 'strong', 'smart_escape']
    results = {}
    
    for mode in modes:
        print(f"\nTesting mode: {mode}")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            pop_size=30,
            max_iterations=n_iterations,
            max_iter_without_improvement=30,
            perturbation_mode=mode
        )
        
        optimizer.run_optimization()
        
        results[mode] = {
            'optimizer': optimizer,
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'convergence': optimizer.history['bests']['metric'].values,
            'perturbation_count': len(getattr(optimizer, '_perturbation_history', []))
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Perturbations triggered: {results[mode]['perturbation_count']}")
    
    return results


def test_perturbation_high_dimensional(mode: str = 'moderate', n_dim: int = 20, 
                                     max_iter: int = 2000, pop_size: int = 100):
    """Test perturbation on high-dimensional problem with visualization."""
    print(f"\n{'='*60}")
    print(f"Testing {mode.upper()} Perturbation on {n_dim}D Rastrigin")
    print(f"{'='*60}")
    
    # Use Rastrigin function - highly multimodal
    func_details = get_function_details('rastrigin_nd', n_dim=n_dim)
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
    
    # Adjust max_iter_without_improvement based on problem difficulty
    # For 20D, use higher threshold to avoid premature perturbations
    max_no_improve = max(50, n_dim * 2)  # At least 2 iterations per dimension
    max_no_improve = max_iter // 2
    
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        pop_size=pop_size,
        max_iterations=max_iter,
        max_iter_without_improvement=max_no_improve,
        perturbation_mode=mode
    )
    
    print(f"Configuration:")
    print(f"  Population size: {pop_size}")
    print(f"  Max iterations without improvement: {max_no_improve}")
    
    optimizer.run_optimization()
    
    print(f"\nOptimization completed:")
    print(f"  Best metric: {optimizer.best_metric:.6f}")
    print(f"  Stop reason: {optimizer.stop_reason}")
    print(f"  Total iterations: {optimizer.iter}")
    
    if hasattr(optimizer, '_perturbation_history'):
        print(f"  Perturbations triggered: {len(optimizer._perturbation_history)}")
        print(f"  At iterations: {optimizer._perturbation_history[:10]}{'...' if len(optimizer._perturbation_history) > 10 else ''}")
    
    return optimizer


def create_perturbation_visualization(optimizer, mode: str, results_dir: str, 
                                    param_indices: tuple = (0, 1)):
    """
    Create visualization showing perturbation effects on population.
    
    Creates both static analysis plots and an animation showing population
    distribution changes when perturbations occur.
    """
    print(f"\nCreating visualization for {mode} perturbation...")
    
    # Get optimization history
    history = optimizer.history
    trials = history['trials']
    bests = history['bests']
    
    # Calculate population diversity over iterations
    iterations = sorted(trials['iter'].unique())
    diversity_std = []
    diversity_range = []
    
    for iter_num in iterations:
        iter_data = trials[trials['iter'] == iter_num]
        # Average std across selected dimensions
        stds = []
        ranges = []
        for idx in param_indices:
            param_name = f'x{idx}'
            if param_name in iter_data.columns:
                stds.append(iter_data[param_name].std())
                ranges.append(iter_data[param_name].max() - iter_data[param_name].min())
        
        diversity_std.append(np.mean(stds) if stds else 0)
        diversity_range.append(np.mean(ranges) if ranges else 0)
    
    # Get perturbation iterations
    perturbation_iters = getattr(optimizer, '_perturbation_history', [])
    
    # Create static analysis plot
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Plot 1: Optimization progress
    ax1 = axes[0]
    ax1.plot(bests['iter'], bests['metric'], 'b-', linewidth=2)
    ax1.set_ylabel('Best Metric')
    ax1.set_title(f'{optimizer.nr_variable_parameters}D Optimization - Perturbation: {mode}')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Mark perturbations
    for p_iter in perturbation_iters:
        ax1.axvline(x=p_iter, color='red', alpha=0.5, linestyle='--', linewidth=1)
    
    # Plot 2: Population diversity
    ax2 = axes[1]
    ax2.plot(iterations, diversity_std, 'g-', linewidth=2, label='Std Dev')
    ax2.set_ylabel('Population Diversity')
    ax2.set_xlabel('Iteration')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Mark perturbations and show their effect
    for i, p_iter in enumerate(perturbation_iters):
        ax2.axvline(x=p_iter, color='red', alpha=0.5, linestyle='--', linewidth=1)
        if i == 0:  # Label only first one
            ax2.text(p_iter, max(diversity_std)*0.9, 'Perturbation', 
                    rotation=90, color='red', ha='right', va='top')
    
    # Plot 3: Population scatter (2D projection) at key iterations
    ax3 = axes[2]
    
    # Select key iterations
    key_iters = [0]  # Initial
    if perturbation_iters:
        # Add first perturbation and one after
        first_pert = perturbation_iters[0]
        key_iters.append(first_pert)
        if first_pert < optimizer.iter - 1:
            key_iters.append(min(first_pert + 5, optimizer.iter))
    key_iters.append(optimizer.iter)  # Final
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(key_iters)))
    param_names = [f'x{param_indices[0]}', f'x{param_indices[1]}']
    
    for iter_num, color in zip(key_iters, colors):
        iter_data = trials[trials['iter'] == iter_num]
        if not iter_data.empty and all(p in iter_data.columns for p in param_names):
            ax3.scatter(iter_data[param_names[0]], iter_data[param_names[1]], 
                       c=[color], alpha=0.6, s=50, label=f'Iter {iter_num}')
    
    ax3.set_xlabel(param_names[0])
    ax3.set_ylabel(param_names[1])
    ax3.set_title('Population Distribution (2D projection)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, f'perturbation_analysis_{mode}.png'), dpi=150)
    plt.close()
    
    print(f"Static analysis saved")
    
    # Create simple animation if perturbations occurred
    if perturbation_iters and len(iterations) < 500:  # Limit animation size
        create_perturbation_animation(trials, bests, perturbation_iters, 
                                    param_names, mode, results_dir)


def create_perturbation_animation(trials, bests, perturbation_iters, 
                                param_names, mode, results_dir):
    """Create animation showing population changes during perturbations."""
    print(f"Creating animation...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    # Setup plots
    ax1.set_xlim(-5.12, 5.12)
    ax1.set_ylim(-5.12, 5.12)
    ax1.set_xlabel(param_names[0])
    ax1.set_ylabel(param_names[1])
    ax1.set_title('Population Distribution')
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Best Metric')
    ax2.set_title('Optimization Progress')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Initialize
    scatter = ax1.scatter([], [], c='red', s=50, alpha=0.6)
    line, = ax2.plot([], [], 'b-', linewidth=2)
    
    # Text elements
    iter_text = ax1.text(0.02, 0.98, '', transform=ax1.transAxes, 
                        va='top', bbox=dict(boxstyle='round', facecolor='wheat'))
    pert_text = fig.text(0.5, 0.95, '', ha='center', fontsize=16, 
                         color='red', weight='bold')
    
    iterations = sorted(trials['iter'].unique())
    
    def init():
        scatter.set_offsets(np.empty((0, 2)))
        line.set_data([], [])
        return scatter, line, iter_text, pert_text
    
    def update(frame_idx):
        frame = iterations[frame_idx]
        
        # Get population at this iteration
        iter_data = trials[trials['iter'] == frame]
        
        if not iter_data.empty:
            # Update scatter
            offsets = np.c_[iter_data[param_names[0]], iter_data[param_names[1]]]
            scatter.set_offsets(offsets)
            
            # Color based on perturbation
            if frame in perturbation_iters:
                scatter.set_color('blue')
                scatter.set_sizes([100])  # Larger during perturbation
                pert_text.set_text('PERTURBATION ACTIVE!')
            else:
                scatter.set_color('red')
                scatter.set_sizes([50])
                pert_text.set_text('')
            
            # Update progress line
            best_up_to = bests[bests['iter'] <= frame]
            line.set_data(best_up_to['iter'], best_up_to['metric'])
            ax2.set_xlim(0, max(10, frame))
            ax2.set_ylim(best_up_to['metric'].min() * 0.5, 
                        best_up_to['metric'].max() * 2)
            
            # Update text
            best_metric = best_up_to['metric'].iloc[-1]
            pop_std = np.mean([iter_data[p].std() for p in param_names])
            iter_text.set_text(f'Iter: {frame}\nBest: {best_metric:.3e}\nPop Std: {pop_std:.3f}')
        
        return scatter, line, iter_text, pert_text
    
    # Create animation
    frame_step = max(1, len(iterations) // 200)  # Max 200 frames
    frames = range(0, len(iterations), frame_step)
    
    anim = animation.FuncAnimation(fig, update, frames=frames, 
                                  init_func=init, interval=50, blit=True)
    
    animation_file = os.path.join(results_dir, f'perturbation_{mode}.gif')
    anim.save(animation_file, writer='pillow', fps=20)
    plt.close(fig)
    print(f"Animation saved to: {animation_file}")


def main():
    """Run all perturbation tests."""
    print("Differential Evolution Perturbation Test Suite")
    print("=" * 60)
    
    # Create results directory
    results_dir = create_test_results_dir('perturbation')
    
    # Test 1: Different modes on 2D problem
    mode_results = test_perturbation_modes()
    
    # Test 2: High-dimensional visualization (20D with proper settings)
    print(f"\n{'='*60}")
    print("High-Dimensional Perturbation Analysis")
    print(f"{'='*60}")
    
    # Test with and without perturbation on 20D
    hd_results = {}
    for mode in ['off', 'moderate']:
        optimizer = test_perturbation_high_dimensional(
            mode=mode, 
            n_dim=20,      # 20D as requested
            max_iter=10000,
            pop_size=100   # 5x dimensions
        )
        
        hd_results[mode] = {
            'optimizer': optimizer,
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'perturbation_count': len(getattr(optimizer, '_perturbation_history', []))
        }
        
        # Create visualization
        create_perturbation_visualization(optimizer, mode, results_dir, 
                                        param_indices=(0, 1))
    
    # Create comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Mode comparison (2D)
    ax1 = axes[0, 0]
    for mode, data in mode_results.items():
        ax1.plot(data['convergence'], label=f'{mode} ({data["perturbation_count"]} pert.)', 
                linewidth=2)
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Best Metric')
    ax1.set_title('Perturbation Modes - 2D Himmelblau')
    ax1.set_yscale('log')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Final performance comparison
    ax2 = axes[0, 1]
    modes = list(mode_results.keys())
    metrics = [mode_results[m]['best_metric'] for m in modes]
    bars = ax2.bar(modes, metrics)
    ax2.set_ylabel('Final Best Metric')
    ax2.set_title('Final Performance - 2D')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Color bars
    best_metric = min(metrics)
    for bar, metric in zip(bars, metrics):
        if metric <= best_metric * 1.1:
            bar.set_color('green')
        elif metric <= best_metric * 2:
            bar.set_color('yellow')
        else:
            bar.set_color('red')
    
    # Plot 3: High-dimensional comparison
    ax3 = axes[1, 0]
    for mode in ['off', 'moderate']:
        optimizer = hd_results[mode]['optimizer']
        bests = optimizer.history['bests']
        ax3.plot(bests['iter'], bests['metric'], 
                label=f'{mode} ({hd_results[mode]["perturbation_count"]} pert.)', 
                linewidth=2)
    ax3.set_xlabel('Iteration')
    ax3.set_ylabel('Best Metric')
    ax3.set_title('20D Rastrigin - Perturbation Comparison')
    ax3.set_yscale('log')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Summary statistics
    ax4 = axes[1, 1]
    ax4.axis('off')
    summary_text = "Summary:\n\n"
    summary_text += "2D Himmelblau:\n"
    best_2d = min(mode_results.items(), key=lambda x: x[1]['best_metric'])
    summary_text += f"  Best mode: {best_2d[0]}\n"
    summary_text += f"  Best metric: {best_2d[1]['best_metric']:.6e}\n\n"
    
    summary_text += "20D Rastrigin:\n"
    summary_text += f"  Without perturbation: {hd_results['off']['best_metric']:.2f}\n"
    summary_text += f"  With perturbation: {hd_results['moderate']['best_metric']:.2f}\n"
    improvement = (hd_results['off']['best_metric'] - hd_results['moderate']['best_metric']) / hd_results['off']['best_metric'] * 100
    summary_text += f"  Improvement: {improvement:.1f}%\n\n"
    
    summary_text += "Key Insights:\n"
    summary_text += "• Perturbations help escape local optima\n"
    summary_text += "• Higher max_iter_without_improvement\n"
    summary_text += "  prevents premature perturbations\n"
    summary_text += "• Population diversity ≠ convergence"
    
    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, 
            fontsize=12, va='top', family='monospace')
    
    plt.suptitle('Perturbation Mechanism Analysis', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'perturbation_summary.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Save test summary
    summary = {
        'test_name': 'DE Perturbation Test',
        'timestamp': datetime.now().isoformat(),
        '2d_results': {
            mode: {
                'best_metric': data['best_metric'],
                'iterations': data['iterations'],
                'perturbation_count': data['perturbation_count']
            }
            for mode, data in mode_results.items()
        },
        '20d_results': {
            mode: {
                'best_metric': data['best_metric'],
                'iterations': data['iterations'],
                'perturbation_count': data['perturbation_count']
            }
            for mode, data in hd_results.items()
        },
        'best_2d_mode': best_2d[0],
        '20d_improvement': improvement
    }
    save_test_summary(results_dir, summary)
    
    print(f"\n{'='*60}")
    print("Test Summary:")
    print(f"Best 2D mode: {best_2d[0]} (metric: {best_2d[1]['best_metric']:.6e})")
    print(f"20D improvement with perturbation: {improvement:.1f}%")
    print(f"\nResults saved to: {results_dir}")


if __name__ == "__main__":
    main()