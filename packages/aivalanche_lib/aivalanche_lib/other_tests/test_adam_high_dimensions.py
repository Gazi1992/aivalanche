"""
Comprehensive study of Adam optimizer performance in high-dimensional spaces.

This script investigates how gradient-based optimizers like Adam can work effectively
in high-dimensional spaces despite the presence of many local minima, using the 
Rastrigin function as a challenging test case.

The Rastrigin function has (3^n - 1) local minima, making it an excellent test
for understanding the paradox of why gradient descent works in neural networks
with millions of parameters.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from aivalanche_lib.optimization.adam import Adam
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details, generate_parameters_config


class AdamHighDimensionalStudy:
    """Class to study Adam optimizer performance across dimensions."""
    
    def __init__(self, dimensions: List[int] = None, num_runs_per_dim: int = 3):
        """
        Initialize the study.
        
        Args:
            dimensions: List of dimensions to test
            num_runs_per_dim: Number of runs per dimension for averaging
        """
        if dimensions is None:
            # Default dimensions to test - comprehensive range
            self.dimensions = [2, 3, 5, 10, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
        else:
            self.dimensions = dimensions
        
        self.num_runs = num_runs_per_dim
        self.results = []
        
    def create_eval_func(self, n_dim: int):
        """Create evaluation function for n-dimensional Rastrigin."""
        func_details = get_function_details('rastrigin_nd', n_dim=n_dim)
        func = func_details['func']
        
        def wrapper(parameters, **kwargs):
            responses = []
            for _, row in parameters.iterrows():
                x_values = [row[f'x{i+1}'] for i in range(n_dim)]
                value = func(np.array(x_values))
                responses.append({
                    'metric': value,
                    'data': {f'x{i+1}': x_values[i] for i in range(len(x_values))}
                })
            return responses
        
        return wrapper
    
    def get_optimizer_config(self, n_dim: int) -> Dict:
        """Get dimension-appropriate optimizer configuration."""
        # Adaptive configuration based on dimensionality
        if n_dim <= 10:
            config = {
                'max_iterations': 300,
                'learning_rate': 0.1,
                'gradient_method': 'finite_difference',
                'gradient_step_size': 1e-4,
                'max_iter_without_improvement': 50
            }
        elif n_dim <= 50:
            config = {
                'max_iterations': 400,
                'learning_rate': 0.05,
                'gradient_method': 'finite_difference',
                'gradient_step_size': 1e-4,
                'max_iter_without_improvement': 60
            }
        elif n_dim <= 200:
            config = {
                'max_iterations': 500,
                'learning_rate': 0.01,
                'gradient_method': 'simultaneous_perturbation',
                'gradient_step_size': 1e-3,
                'max_iter_without_improvement': 70
            }
        else:
            config = {
                'max_iterations': 600,
                'learning_rate': 0.005,
                'gradient_method': 'simultaneous_perturbation',
                'gradient_step_size': 1e-3,
                'max_iter_without_improvement': 80
            }
        
        # Scale learning rate with sqrt of dimensions for better stability
        config['learning_rate'] = config['learning_rate'] / np.sqrt(n_dim / 10)
        
        return config
    
    def run_single_optimization(self, n_dim: int, seed: int) -> Dict:
        """Run a single optimization for given dimension."""
        # Setup
        func_details = get_function_details('rastrigin_nd', n_dim=n_dim)
        param_config = generate_parameters_config(func_details)
        parameters = Parameters(param_config)
        eval_func = self.create_eval_func(n_dim)
        
        # Random initial point (avoid starting at optimum)
        np.random.seed(seed)
        initial_values = {}
        for i in range(n_dim):
            # Start from random point in [-3, 3] range
            initial_values[f'x{i+1}'] = np.random.uniform(-3, 3)
        initial_point = pd.DataFrame([initial_values])
        
        # Calculate initial state
        initial_metric = eval_func(initial_point)[0]['metric']
        initial_distance = np.linalg.norm(list(initial_values.values()))
        
        # Get optimizer configuration
        config = self.get_optimizer_config(n_dim)
        
        # Create and run optimizer
        optimizer = Adam(
            seed=seed,
            eval_func=eval_func,
            parameters=parameters,
            opt_min_or_max='min',
            max_iterations=config['max_iterations'],
            learning_rate=config['learning_rate'],
            beta1=0.9,
            beta2=0.999,
            epsilon=1e-8,
            gradient_tolerance=1e-8,
            max_iter_without_improvement=config['max_iter_without_improvement'],
            improvement_threshold=1e-6,
            gradient_method=config['gradient_method'],
            gradient_step_size=config['gradient_step_size'],
            gradient_step_size_relative=True,
            boundary_handling='clip',
            initial_point=initial_point,
            use_defaults_in_initial_point=False
        )
        
        start_time = time.time()
        optimizer.run_optimization()
        elapsed_time = time.time() - start_time
        
        # Collect results
        best_params = optimizer.best_parameters[[f'x{i+1}' for i in range(n_dim)]].values
        final_distance = np.linalg.norm(best_params)
        
        # Calculate theoretical lower bound (global optimum is 0)
        # Rastrigin has local minima at integer multiples of 1
        nearest_local_minimum = n_dim * 10 * (1 - np.cos(2 * np.pi))  # Approximate
        
        return {
            'dimension': n_dim,
            'seed': seed,
            'initial_metric': initial_metric,
            'final_metric': optimizer.best_metric,
            'improvement': initial_metric - optimizer.best_metric,
            'improvement_percent': (initial_metric - optimizer.best_metric) / initial_metric * 100,
            'initial_distance': initial_distance,
            'final_distance': final_distance,
            'iterations': optimizer.iter,
            'evaluations': optimizer.nr_evaluations,
            'time_seconds': elapsed_time,
            'learning_rate': config['learning_rate'],
            'found_global': optimizer.best_metric < 1.0  # Close to global optimum
        }
    
    def run_study(self):
        """Run the complete dimensional study."""
        print("=" * 80)
        print("ADAM OPTIMIZER: HIGH-DIMENSIONAL OPTIMIZATION STUDY")
        print("Investigating the paradox of gradient descent in high dimensions")
        print("=" * 80)
        print(f"\nTest function: Rastrigin (has 3^n - 1 local minima)")
        print(f"Dimensions to test: {self.dimensions}")
        print(f"Runs per dimension: {self.num_runs}")
        print("-" * 80)
        
        total_runs = len(self.dimensions) * self.num_runs
        current_run = 0
        
        for n_dim in self.dimensions:
            print(f"\n[Dimension {n_dim}] - {3**n_dim - 1:,} local minima")
            dim_results = []
            
            for run in range(self.num_runs):
                current_run += 1
                print(f"  Run {run+1}/{self.num_runs} (Overall: {current_run}/{total_runs})", end="")
                
                try:
                    result = self.run_single_optimization(n_dim, seed=42 + run)
                    dim_results.append(result)
                    print(f" - Metric: {result['final_metric']:.2f}, Time: {result['time_seconds']:.1f}s")
                except Exception as e:
                    print(f" - FAILED: {e}")
                    continue
            
            # Average results for this dimension
            if dim_results:
                avg_result = {
                    'dimension': n_dim,
                    'num_runs': len(dim_results),
                    'avg_initial_metric': np.mean([r['initial_metric'] for r in dim_results]),
                    'avg_final_metric': np.mean([r['final_metric'] for r in dim_results]),
                    'std_final_metric': np.std([r['final_metric'] for r in dim_results]),
                    'avg_improvement': np.mean([r['improvement'] for r in dim_results]),
                    'avg_improvement_percent': np.mean([r['improvement_percent'] for r in dim_results]),
                    'avg_final_distance': np.mean([r['final_distance'] for r in dim_results]),
                    'avg_iterations': np.mean([r['iterations'] for r in dim_results]),
                    'avg_evaluations': np.mean([r['evaluations'] for r in dim_results]),
                    'avg_time_seconds': np.mean([r['time_seconds'] for r in dim_results]),
                    'found_global_rate': sum([r['found_global'] for r in dim_results]) / len(dim_results),
                    'local_minima_count': 3**n_dim - 1
                }
                self.results.append(avg_result)
                
                print(f"  Average: Metric={avg_result['avg_final_metric']:.2f}, "
                      f"Improvement={avg_result['avg_improvement_percent']:.1f}%")
        
        return pd.DataFrame(self.results)
    
    def create_visualizations(self, results_df: pd.DataFrame, save_dir: str):
        """Create comprehensive visualizations of the results."""
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Main title
        fig.suptitle('Adam Optimizer Performance in High-Dimensional Spaces\n'
                     'Test Function: Rastrigin (Highly Multimodal)', 
                     fontsize=16, fontweight='bold')
        
        # Plot 1: Final metric vs dimensions (main result)
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.errorbar(results_df['dimension'], results_df['avg_final_metric'], 
                     yerr=results_df['std_final_metric'], 
                     fmt='bo-', linewidth=2, markersize=8, capsize=5)
        ax1.axhline(y=0, color='r', linestyle='--', alpha=0.3, label='Global optimum')
        ax1.set_xlabel('Number of Dimensions', fontsize=12)
        ax1.set_ylabel('Final Metric Value', fontsize=12)
        ax1.set_title('Optimization Quality vs Dimensionality', fontsize=14, fontweight='bold')
        ax1.set_xscale('log')
        if results_df['avg_final_metric'].min() > 0:
            ax1.set_yscale('log')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Plot 2: Local minima count
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.plot(results_df['dimension'], results_df['local_minima_count'], 
                 'r^-', linewidth=2, markersize=6)
        ax2.set_xlabel('Dimensions', fontsize=10)
        ax2.set_ylabel('Number of Local Minima', fontsize=10)
        ax2.set_title('Complexity Growth\n(3^n - 1 local minima)', fontsize=11)
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Improvement percentage
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.plot(results_df['dimension'], results_df['avg_improvement_percent'], 
                 'go-', linewidth=2, markersize=8)
        ax3.set_xlabel('Dimensions', fontsize=10)
        ax3.set_ylabel('Improvement (%)', fontsize=10)
        ax3.set_title('Optimization Effectiveness', fontsize=11)
        ax3.set_xscale('log')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Normalized metric (per dimension)
        ax4 = fig.add_subplot(gs[1, 1])
        normalized = results_df['avg_final_metric'] / results_df['dimension']
        ax4.plot(results_df['dimension'], normalized, 'mo-', linewidth=2, markersize=8)
        ax4.set_xlabel('Dimensions', fontsize=10)
        ax4.set_ylabel('Final Metric / Dimension', fontsize=10)
        ax4.set_title('Normalized Performance', fontsize=11)
        ax4.set_xscale('log')
        if normalized.min() > 0:
            ax4.set_yscale('log')
        ax4.grid(True, alpha=0.3)
        
        # Plot 5: Convergence speed
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.plot(results_df['dimension'], results_df['avg_iterations'], 
                 'co-', linewidth=2, markersize=8)
        ax5.set_xlabel('Dimensions', fontsize=10)
        ax5.set_ylabel('Iterations to Converge', fontsize=10)
        ax5.set_title('Convergence Speed', fontsize=11)
        ax5.set_xscale('log')
        ax5.grid(True, alpha=0.3)
        
        # Plot 6: Computational cost
        ax6 = fig.add_subplot(gs[2, 0])
        ax6.plot(results_df['dimension'], results_df['avg_time_seconds'], 
                 'ko-', linewidth=2, markersize=8)
        ax6.set_xlabel('Dimensions', fontsize=10)
        ax6.set_ylabel('Time (seconds)', fontsize=10)
        ax6.set_title('Computational Cost', fontsize=11)
        ax6.set_xscale('log')
        ax6.set_yscale('log')
        ax6.grid(True, alpha=0.3)
        
        # Plot 7: Evaluations per dimension
        ax7 = fig.add_subplot(gs[2, 1])
        evals_per_dim = results_df['avg_evaluations'] / results_df['dimension']
        ax7.plot(results_df['dimension'], evals_per_dim, 'yo-', linewidth=2, markersize=8)
        ax7.set_xlabel('Dimensions', fontsize=10)
        ax7.set_ylabel('Evaluations / Dimension', fontsize=10)
        ax7.set_title('Evaluation Efficiency', fontsize=11)
        ax7.set_xscale('log')
        ax7.grid(True, alpha=0.3)
        
        # Plot 8: Scaling analysis
        ax8 = fig.add_subplot(gs[2, 2])
        # Fit power law
        valid_data = results_df[results_df['avg_final_metric'] > 0]
        if len(valid_data) > 2:
            log_dims = np.log(valid_data['dimension'].values)
            log_metrics = np.log(valid_data['avg_final_metric'].values)
            coeffs = np.polyfit(log_dims, log_metrics, 1)
            alpha = coeffs[0]
            
            # Plot actual vs fitted
            ax8.scatter(valid_data['dimension'], valid_data['avg_final_metric'], 
                       s=50, alpha=0.6, label='Actual')
            fit_line = np.exp(coeffs[1]) * valid_data['dimension'].values ** alpha
            ax8.plot(valid_data['dimension'], fit_line, 'r--', linewidth=2,
                    label=f'Fit: metric ~ dim^{alpha:.2f}')
            ax8.set_xlabel('Dimensions', fontsize=10)
            ax8.set_ylabel('Final Metric', fontsize=10)
            ax8.set_title('Scaling Law Analysis', fontsize=11)
            ax8.set_xscale('log')
            ax8.set_yscale('log')
            ax8.legend()
            ax8.grid(True, alpha=0.3)
        
        plt.savefig(os.path.join(save_dir, 'adam_high_dimensional_analysis.png'), 
                    dpi=150, bbox_inches='tight')
        plt.show()
        
        return fig
    
    def analyze_results(self, results_df: pd.DataFrame):
        """Perform detailed analysis of results."""
        print("\n" + "=" * 80)
        print("DETAILED ANALYSIS")
        print("=" * 80)
        
        # Scaling analysis
        valid_data = results_df[results_df['avg_final_metric'] > 0]
        if len(valid_data) > 2:
            log_dims = np.log(valid_data['dimension'].values)
            log_metrics = np.log(valid_data['avg_final_metric'].values)
            alpha = np.polyfit(log_dims, log_metrics, 1)[0]
            
            print(f"\n1. SCALING BEHAVIOR:")
            print(f"   Power law exponent: {alpha:.2f}")
            print(f"   This means: final_metric ~ dimension^{alpha:.2f}")
            
            if alpha < 1:
                print("   -> SUB-LINEAR scaling: Excellent! Adam handles dimensions well.")
            elif alpha < 1.5:
                print("   -> NEAR-LINEAR scaling: Good performance degradation.")
            else:
                print("   -> SUPER-LINEAR scaling: Significant curse of dimensionality.")
        
        # Performance summary
        print(f"\n2. PERFORMANCE SUMMARY:")
        print(f"   Lowest dimension ({results_df.iloc[0]['dimension']}D):")
        print(f"     - Final metric: {results_df.iloc[0]['avg_final_metric']:.2f}")
        print(f"     - Improvement: {results_df.iloc[0]['avg_improvement_percent']:.1f}%")
        
        if len(results_df) > 1:
            print(f"   Highest dimension ({results_df.iloc[-1]['dimension']}D):")
            print(f"     - Final metric: {results_df.iloc[-1]['avg_final_metric']:.2f}")
            print(f"     - Improvement: {results_df.iloc[-1]['avg_improvement_percent']:.1f}%")
            print(f"     - {results_df.iloc[-1]['local_minima_count']:,} local minima!")
        
        # Success rate
        if 'found_global_rate' in results_df.columns:
            successful_dims = results_df[results_df['found_global_rate'] > 0]['dimension'].tolist()
            if successful_dims:
                print(f"\n3. GLOBAL OPTIMUM FOUND:")
                print(f"   Dimensions where global was found: {successful_dims}")
        
        print("\n" + "=" * 80)
        print("KEY INSIGHTS AND EXPLANATIONS")
        print("=" * 80)
        print("""
THE PARADOX EXPLAINED:

1. WHY ADAM WORKS DESPITE MANY LOCAL MINIMA:
   - Gradient information provides systematic search direction
   - Adaptive learning rates adjust to local landscape geometry  
   - Momentum helps traverse flat regions and escape shallow minima
   - Early iterations make large progress before getting trapped

2. CONNECTION TO NEURAL NETWORKS:
   Neural networks with millions of parameters work because:
   - Loss landscapes have different structure than Rastrigin
   - Many local minima are nearly equivalent (not true for Rastrigin)
   - Overparameterization creates beneficial redundancy
   - SGD noise provides implicit exploration
   - Skip connections and normalization improve landscape

3. PRACTICAL IMPLICATIONS:
   - For smooth landscapes: Gradient methods excel even in high dimensions
   - For highly multimodal: Population-based methods (DE, PSO) may be better
   - Problem structure matters more than dimensionality alone
   - Initialization and learning rate scheduling are crucial

4. THE RASTRIGIN CHALLENGE:
   With 3^n - 1 local minima, Rastrigin represents a worst-case scenario
   that doesn't reflect real-world optimization problems like neural networks,
   where the landscape geometry is more favorable for gradient descent.
        """)


def main():
    """Main execution function."""
    # Configuration
    # You can modify these dimensions based on your computational budget
    # Full test: [2, 3, 5, 10, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
    # Quick test: [2, 5, 10, 20, 50, 100]
    dimensions_to_test = [2, 3, 5, 10, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000]  # Moderate test
    num_runs_per_dimension = 3  # Average over multiple runs for reliability
    
    # Create study instance
    study = AdamHighDimensionalStudy(
        dimensions=dimensions_to_test,
        num_runs_per_dim=num_runs_per_dimension
    )
    
    # Run the study
    print(f"\nStarting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results_df = study.run_study()
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save results
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    results_df.to_csv(os.path.join(results_dir, 'adam_high_dimensional_results.csv'), index=False)
    print(f"\nResults saved to: {os.path.join(results_dir, 'adam_high_dimensional_results.csv')}")
    
    # Create visualizations
    study.create_visualizations(results_df, results_dir)
    
    # Perform analysis
    study.analyze_results(results_df)
    
    return results_df


if __name__ == "__main__":
    results = main()