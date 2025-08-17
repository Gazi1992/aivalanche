"""
MZI Filter Optimization using Differential Evolution
=====================================================
Optimizes cascaded MZI filter parameters using DE from aivalanche_lib.
Generates GDS files for the best designs found during optimization.
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime
import time

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "aivalanche_lib"))

# Import simulator
from mzi_gds_simulator import MZIFilterGDSSimulator

# Import optimization components
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution


class MZIFilterOptimizer:
    """Optimizer for MZI filter using Differential Evolution."""
    
    def __init__(self, inputs_dir, results_dir):
        """Initialize optimizer with paths and configurations."""
        self.inputs_dir = Path(inputs_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Create separate folder for iteration results
        self.iterations_dir = self.results_dir / "iterations"
        self.iterations_dir.mkdir(exist_ok=True)
        
        # Initialize simulator
        self.simulator = MZIFilterGDSSimulator(self.inputs_dir / "filter_config.json")
        
        # Load parameters
        self.parameters, self.default_values = self.load_parameters(
            self.inputs_dir / "parameters.csv"
        )
        
        # Track best designs
        self.best_designs = []
        self.iteration_count = 0
        self.eval_count = 0
        self.start_time = None
        self.de_instance = None  # Store DE instance for visualization
        
    def load_parameters(self, csv_path):
        """Load parameters from CSV."""
        df = pd.read_csv(csv_path)
        
        # Convert to Parameters format
        param_list = []
        for _, row in df.iterrows():
            param = {
                'name': row['name'],
                'type': 'continuous',
                'min': row['min'],
                'max': row['max']
            }
            param_list.append(param)
        
        parameters = Parameters(param_list)
        
        # Get default values
        defaults = {}
        for _, row in df.iterrows():
            defaults[row['name']] = row['default']
        
        return parameters, defaults
    
    def evaluation_function(self, parameters, **kwargs):
        """
        Evaluation function for DE optimizer.
        
        Parameters:
        -----------
        parameters : pd.DataFrame
            DataFrame with parameter values to evaluate
            
        Returns:
        --------
        list of dict
            Results with 'metric' key for each evaluation
        """
        results = []
        
        for idx, row in parameters.iterrows():
            # Convert row to dictionary
            params_dict = row.to_dict()
            
            # Simulate response
            transmission = self.simulator.simulate_analytical(params_dict)
            
            # Calculate MSE-based objective (to minimize)
            # Use weighted MSE for better optimization focus
            objective = self.simulator.calculate_weighted_mse_metric(transmission) * 1000  # Scale for better numerics
            
            # Store result
            results.append({'metric': objective})
            
            self.eval_count += 1
            
            # Track best designs periodically
            if objective < 10:  # Good design threshold (adjusted for MSE metric)
                transmission = self.simulator.simulate_analytical(params_dict)
                metrics = self.simulator.calculate_metrics(transmission)
                
                self.best_designs.append({
                    'eval_count': self.eval_count,
                    'objective': objective,
                    'params': params_dict.copy(),
                    'metrics': metrics
                })
        
        return results
    
    def callback_function(self, optimizer, iteration, best_parameters, best_metric, **kwargs):
        """Callback function called after each DE iteration."""
        self.iteration_count = iteration
        self.de_instance = optimizer  # Store DE instance for visualizations
        
        # Get best parameters
        if best_parameters is not None:
            best_params = best_parameters.to_dict() if hasattr(best_parameters, 'to_dict') else best_parameters
            best_fitness = best_metric
        else:
            return  # Skip if no best yet
        
        # Calculate metrics for best
        transmission = self.simulator.simulate_analytical(best_params)
        metrics = self.simulator.calculate_metrics(transmission)
        
        # Print progress
        elapsed = time.time() - self.start_time
        print(f"\nIteration {self.iteration_count:3d} | "
              f"Evals: {self.eval_count:5d} | "
              f"Time: {elapsed:6.1f}s | "
              f"Best Obj: {best_fitness:8.2f}")
        print(f"  IL: {metrics['insertion_loss']:6.2f} dB | "
              f"XT: {metrics['crosstalk']:6.1f} dB | "
              f"Roll-off: {metrics['rolloff_rate']:5.2f} dB/nm")
        
        # Save intermediate results every 5 iterations (or every iteration for short runs)
        if self.iteration_count % 5 == 0 or self.iteration_count <= 10:
            self.save_intermediate_results(best_params, metrics)
    
    def callback_better_found(self, optimizer, iteration, best_parameters, best_metric, **kwargs):
        """Callback when a better solution is found."""
        # Generate DE visualization plots
        iter_dir = self.iterations_dir / f"iteration_{iteration:03d}"
        iter_dir.mkdir(exist_ok=True)
        
        print(f"  -> Better solution found! Generating visualization plots...")
        
        # Generate parameter evolution plot for both iteration and final results
        try:
            fig, axes = optimizer.plot_all_parameters_evolution()
            if fig is not None:
                # Save to iteration folder
                fig.savefig(iter_dir / "parameters_evolution.png", dpi=150, bbox_inches='tight')
                # Also save/update in main results folder
                fig.savefig(self.results_dir / "parameters_evolution.png", dpi=150, bbox_inches='tight')
                plt.close(fig)
        except Exception as e:
            print(f"  Warning: Could not generate parameters evolution plot: {e}")
        
        # Generate metrics evolution plot for both iteration and final results
        try:
            fig, ax = optimizer.plot_metrics(which="bests")
            if fig is not None:
                # Save to iteration folder
                fig.savefig(iter_dir / "metrics_evolution.png", dpi=150, bbox_inches='tight')
                # Also save/update in main results folder
                fig.savefig(self.results_dir / "metrics_evolution.png", dpi=150, bbox_inches='tight')
                plt.close(fig)
        except Exception as e:
            print(f"  Warning: Could not generate metrics evolution plot: {e}")
    
    def save_intermediate_results(self, best_params, metrics):
        """Save intermediate results and generate GDS."""
        iter_dir = self.iterations_dir / f"iteration_{self.iteration_count:03d}"
        iter_dir.mkdir(exist_ok=True)
        
        # Save parameters
        params_df = pd.DataFrame([best_params])
        params_df.to_csv(iter_dir / "best_parameters.csv", index=False)
        
        # Save metrics
        with open(iter_dir / "metrics.json", 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Generate and save GDS
        gds_path = iter_dir / f"mzi_filter_iter{self.iteration_count}.gds"
        component = self.simulator.create_cascaded_mzi_gds(best_params, save_path=gds_path)
        
        # Generate response plot
        transmission = self.simulator.simulate_analytical(best_params)
        # Calculate MSE for display
        mse = self.simulator.calculate_weighted_mse_metric(transmission)
        fig = self.simulator.plot_response(
            transmission, metrics, 
            title=f"Iteration {self.iteration_count} - MSE: {mse:.6f}"
        )
        fig.savefig(iter_dir / "response.png", dpi=150)
        plt.close()
    
    def run_optimization(self, pop_size=50, max_iterations=100):
        """
        Run DE optimization.
        
        Parameters:
        -----------
        pop_size : int
            Population size for DE
        max_iterations : int
            Maximum number of iterations
        """
        print("="*70)
        print("MZI Filter Optimization with Differential Evolution")
        print("="*70)
        print(f"Population size: {pop_size}")
        print(f"Max iterations: {max_iterations}")
        print(f"Parameters: {len(self.default_values)}")
        print(f"Saving results to: {self.results_dir}")
        print("="*70)
        
        self.start_time = time.time()
        
        # Configure DE
        de_config = {
            'seed': 42,
            'pop_size': pop_size,
            'max_iterations': max_iterations,
            'eval_func': self.evaluation_function,
            'parameters': self.parameters,
            'callback_after_each_iter': self.callback_function,
            'callback_after_better_solution': self.callback_better_found,
            'max_iter_without_improvement': max_iterations // 3,
            'improvement_threshold': 0.001,
            'adaptive_boundaries_mode': 'on',
        }
        
        # Initialize and run DE
        de = DifferentialEvolution(**de_config)
        de.run_optimization()
        
        # Process final results
        self.process_final_results(de)
        
        return de
    
    def process_final_results(self, de):
        """Process and save final optimization results."""
        print("\n" + "="*70)
        print("Optimization Complete!")
        print("="*70)
        
        # Get best solution
        if hasattr(de, 'best_parameters') and de.best_parameters is not None:
            best_params = de.best_parameters.to_dict() if hasattr(de.best_parameters, 'to_dict') else de.best_parameters
            best_fitness = de.best_metric if hasattr(de, 'best_metric') else float('inf')
        else:
            # Fallback to history
            best_fitness = de.history.iloc[-1]['best_metric'] if len(de.history) > 0 else float('inf')
            best_params = self.default_values  # Use defaults as fallback
        
        # Calculate final metrics
        transmission = self.simulator.simulate_analytical(best_params)
        metrics = self.simulator.calculate_metrics(transmission)
        
        # Also calculate and display MSE
        mse = self.simulator.calculate_mse_metric(transmission)
        weighted_mse = self.simulator.calculate_weighted_mse_metric(transmission)
        
        print(f"\nMSE Metrics:")
        print("-"*30)
        print(f"MSE (uniform):    {mse:.6f}")
        print(f"MSE (weighted):   {weighted_mse:.6f}")
        
        # Print summary
        print(f"\nBest Objective Value (Weighted MSE x 1000): {best_fitness:.4f}")
        print("\nBest Performance Metrics:")
        print("-"*30)
        print(f"Insertion Loss:    {metrics['insertion_loss']:.3f} dB")
        print(f"Crosstalk:        {metrics['crosstalk']:.1f} dB")
        print(f"Extinction Ratio: {metrics['extinction_ratio']:.1f} dB")
        print(f"Passband Ripple:  {metrics['passband_ripple']:.3f} dB")
        print(f"Roll-off Rate:    {metrics['rolloff_rate']:.2f} dB/nm")
        
        print("\nBest Parameters:")
        print("-"*30)
        print(f"delta_L: {best_params['delta_L']:.3f} um")
        for i in range(self.simulator.num_stages):
            print(f"kappa_{i:2d}: {best_params[f'kappa_{i}']:.4f}")
        
        # Save final results directly to results directory
        final_dir = self.results_dir
        
        # Save best parameters
        params_df = pd.DataFrame([best_params])
        params_df.to_csv(final_dir / "best_parameters.csv", index=False)
        
        # Save all parameters history
        if hasattr(de, 'current_parameters') and de.current_parameters is not None:
            de.current_parameters.to_csv(final_dir / "final_population.csv", index=False)
        
        # Save metrics
        with open(final_dir / "best_metrics.json", 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Generate final GDS
        print("\nGenerating final GDS layout...")
        gds_path = final_dir / "optimized_mzi_filter.gds"
        component = self.simulator.create_cascaded_mzi_gds(best_params, save_path=gds_path)
        
        # Generate layout visualization
        layout_fig = self.simulator.plot_gds_layout(component, 
                                                   save_path=final_dir / "layout.png")
        plt.close()
        
        # Generate final response plots
        fig = self.simulator.plot_response(transmission, metrics, 
                                          title="Optimized Design")
        fig.savefig(final_dir / "response.png", dpi=150)
        plt.close()
        
        # Generate final DE visualization plots
        print("\nGenerating final DE visualization plots...")
        try:
            # Parameter evolution
            fig, axes = de.plot_all_parameters_evolution()
            if fig is not None:
                fig.savefig(final_dir / "parameters_evolution.png", dpi=150, bbox_inches='tight')
                plt.close(fig)
                print("  + Saved parameters evolution plot")
        except Exception as e:
            print(f"  Warning: Could not generate final parameters evolution: {e}")
        
        try:
            # Metrics evolution
            fig, ax = de.plot_metrics(which="bests")
            if fig is not None:
                fig.savefig(final_dir / "metrics_evolution.png", dpi=150, bbox_inches='tight')
                plt.close(fig)
                print("  + Saved metrics evolution plot")
        except Exception as e:
            print(f"  Warning: Could not generate final metrics evolution: {e}")
        
        # Save optimization history
        history_df = pd.DataFrame()
        if hasattr(de, 'history'):
            if isinstance(de.history, pd.DataFrame):
                history_df = de.history
            elif isinstance(de.history, dict):
                # Convert dict with lists to DataFrame
                try:
                    history_df = pd.DataFrame(de.history)
                except:
                    # If dict has scalar values, create single row DataFrame
                    history_df = pd.DataFrame([de.history])
            
            if not history_df.empty:
                history_df.to_csv(final_dir / "optimization_history.csv", index=False)
        
        # Plot convergence
        if not history_df.empty:
            self.plot_convergence(history_df, final_dir)
        
        # Compare with initial design
        self.compare_with_initial(best_params, metrics, final_dir)
        
        print(f"\nResults saved to: {final_dir}")
        
        # Check targets
        print("\nTarget Achievement:")
        print("-"*30)
        targets = self.simulator.targets
        
        if metrics['insertion_loss'] <= targets['max_insertion_loss_dB']:
            print(f"+ IL: {metrics['insertion_loss']:.3f} <= {targets['max_insertion_loss_dB']} dB")
        else:
            print(f"X IL: {metrics['insertion_loss']:.3f} > {targets['max_insertion_loss_dB']} dB")
        
        if metrics['crosstalk'] <= targets['max_crosstalk_dB']:
            print(f"+ XT: {metrics['crosstalk']:.1f} <= {targets['max_crosstalk_dB']} dB")
        else:
            print(f"X XT: {metrics['crosstalk']:.1f} > {targets['max_crosstalk_dB']} dB")
        
        if metrics['rolloff_rate'] >= targets['min_rolloff_dB_per_nm']:
            print(f"+ Roll-off: {metrics['rolloff_rate']:.2f} >= {targets['min_rolloff_dB_per_nm']} dB/nm")
        else:
            print(f"X Roll-off: {metrics['rolloff_rate']:.2f} < {targets['min_rolloff_dB_per_nm']} dB/nm")
    
    def plot_convergence(self, history_df, save_dir):
        """Plot optimization convergence."""
        # Check what columns are available
        if 'iteration' not in history_df.columns:
            # Try to use index as iteration
            if not history_df.empty:
                history_df['iteration'] = range(1, len(history_df) + 1)
            else:
                return  # No data to plot
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Best fitness over iterations
        if 'best_metric' in history_df.columns:
            ax1.plot(history_df['iteration'], history_df['best_metric'], 'b-', linewidth=2)
            ax1.set_xlabel('Iteration')
            ax1.set_ylabel('Best Objective Value')
            ax1.set_title('Optimization Convergence')
            ax1.grid(True, alpha=0.3)
            ax1.set_yscale('log')
        
        # Population diversity (if available)
        if 'mean_metric' in history_df.columns and 'std_metric' in history_df.columns:
            ax2.plot(history_df['iteration'], history_df['mean_metric'], 'g-', 
                    label='Mean', linewidth=2)
            ax2.fill_between(history_df['iteration'], 
                             history_df['mean_metric'] - history_df['std_metric'],
                             history_df['mean_metric'] + history_df['std_metric'],
                             alpha=0.3, color='g', label='Std Dev')
            ax2.set_xlabel('Iteration')
            ax2.set_ylabel('Population Objective')
            ax2.set_title('Population Statistics')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_yscale('log')
        else:
            # Just show the best metric again if no population stats
            if 'best_metric' in history_df.columns:
                ax2.plot(history_df['iteration'], history_df['best_metric'], 'b-', linewidth=2)
                ax2.set_xlabel('Iteration')
                ax2.set_ylabel('Best Objective Value')
                ax2.set_title('Best Solution Progress')
                ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        fig.savefig(save_dir / "convergence.png", dpi=150)
        plt.close()
    
    def compare_with_initial(self, best_params, best_metrics, save_dir):
        """Compare optimized design with initial design."""
        # Calculate initial metrics
        initial_transmission = self.simulator.simulate_analytical(self.default_values)
        initial_metrics = self.simulator.calculate_metrics(initial_transmission)
        
        # Calculate optimized transmission
        opt_transmission = self.simulator.simulate_analytical(best_params)
        
        # Calculate MSE for both initial and optimized
        initial_mse = self.simulator.calculate_mse_metric(initial_transmission)
        opt_mse = self.simulator.calculate_mse_metric(opt_transmission)
        initial_weighted_mse = self.simulator.calculate_weighted_mse_metric(initial_transmission)
        opt_weighted_mse = self.simulator.calculate_weighted_mse_metric(opt_transmission)
        
        # Create comparison plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        wl_nm = self.simulator.wavelengths * 1000
        
        # Linear scale comparison
        ax1.plot(wl_nm, initial_transmission, 'r-', linewidth=2, 
                alpha=0.7, label='Initial')
        ax1.plot(wl_nm, opt_transmission, 'b-', linewidth=2, 
                alpha=0.7, label='Optimized')
        
        # Add ideal response
        ideal = self.simulator._create_ideal_response()
        ax1.plot(wl_nm, ideal, 'k--', linewidth=1.5, alpha=0.5, label='Ideal')
        
        ax1.axvspan(self.simulator.s_band[0]*1000, self.simulator.s_band[1]*1000, 
                   alpha=0.2, color='green')
        ax1.axvspan(self.simulator.c_band[0]*1000, self.simulator.c_band[1]*1000, 
                   alpha=0.2, color='red')
        ax1.set_xlabel('Wavelength (nm)')
        ax1.set_ylabel('Transmission')
        ax1.set_title('Initial vs Optimized Design - Linear Scale')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([-0.05, 1.1])
        
        # dB scale comparison
        initial_db = 10 * np.log10(np.maximum(initial_transmission, 1e-10))
        opt_db = 10 * np.log10(np.maximum(opt_transmission, 1e-10))
        ideal_db = 10 * np.log10(np.maximum(ideal, 1e-10))
        
        ax2.plot(wl_nm, initial_db, 'r-', linewidth=2, alpha=0.7, label='Initial')
        ax2.plot(wl_nm, opt_db, 'b-', linewidth=2, alpha=0.7, label='Optimized')
        ax2.plot(wl_nm, ideal_db, 'k--', linewidth=1.5, alpha=0.5, label='Ideal')
        
        ax2.axvspan(self.simulator.s_band[0]*1000, self.simulator.s_band[1]*1000, 
                   alpha=0.2, color='green')
        ax2.axvspan(self.simulator.c_band[0]*1000, self.simulator.c_band[1]*1000, 
                   alpha=0.2, color='red')
        ax2.axhline(y=-self.simulator.targets['max_insertion_loss_dB'], 
                   color='g', linestyle=':', alpha=0.5)
        ax2.axhline(y=self.simulator.targets['max_crosstalk_dB'], 
                   color='r', linestyle=':', alpha=0.5)
        ax2.set_xlabel('Wavelength (nm)')
        ax2.set_ylabel('Transmission (dB)')
        ax2.set_title('Initial vs Optimized Design - dB Scale')
        ax2.legend(loc='lower right')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([-60, 5])
        
        # Add metrics comparison text
        improvement_text = (
            f"Initial -> Optimized:\n"
            f"IL: {initial_metrics['insertion_loss']:.2f} -> {best_metrics['insertion_loss']:.3f} dB\n"
            f"XT: {initial_metrics['crosstalk']:.1f} -> {best_metrics['crosstalk']:.1f} dB\n"
            f"Roll-off: {initial_metrics['rolloff_rate']:.2f} -> {best_metrics['rolloff_rate']:.2f} dB/nm\n"
            f"MSE: {initial_weighted_mse:.6f} -> {opt_weighted_mse:.6f}"
        )
        ax2.text(0.02, 0.5, improvement_text, transform=ax2.transAxes,
                fontsize=9, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        fig.savefig(save_dir / "comparison.png", dpi=150)
        plt.close()
        
        # Save comparison data
        comparison_data = {
            'initial_metrics': initial_metrics,
            'optimized_metrics': best_metrics,
            'initial_mse': initial_mse,
            'optimized_mse': opt_mse,
            'initial_weighted_mse': initial_weighted_mse,
            'optimized_weighted_mse': opt_weighted_mse,
            'improvement': {
                'insertion_loss': initial_metrics['insertion_loss'] - best_metrics['insertion_loss'],
                'crosstalk': initial_metrics['crosstalk'] - best_metrics['crosstalk'],
                'extinction_ratio': best_metrics['extinction_ratio'] - initial_metrics['extinction_ratio'],
                'rolloff_rate': best_metrics['rolloff_rate'] - initial_metrics['rolloff_rate'],
                'mse_reduction': initial_mse - opt_mse,
                'weighted_mse_reduction': initial_weighted_mse - opt_weighted_mse
            }
        }
        
        with open(save_dir / "comparison.json", 'w') as f:
            json.dump(comparison_data, f, indent=2)


def main():
    """Main function to run optimization."""
    # Setup paths
    base_dir = Path(__file__).parent.parent
    inputs_dir = base_dir / "inputs"
    
    # Create results directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = base_dir / "results" / f"optimization_{timestamp}"
    
    # Initialize optimizer
    optimizer = MZIFilterOptimizer(inputs_dir, results_dir)
    
    # Run optimization
    # Start with smaller values for testing, increase for better results
    de = optimizer.run_optimization(
        pop_size=50,  # Population size
        max_iterations=10000  # Number of iterations
    )
    
    print("\n" + "="*70)
    print("Optimization completed successfully!")
    print("="*70)
    
    return de, optimizer


if __name__ == "__main__":
    de, optimizer = main()