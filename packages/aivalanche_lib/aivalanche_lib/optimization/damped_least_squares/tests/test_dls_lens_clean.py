"""
Clean lens optimization test for DLS optimizer.

Demonstrates how DLS excels at sensitive optimization problems
like lens design where parameters have complex interactions.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from aivalanche_lib.optimization.damped_least_squares.DampedLeastSquares import DampedLeastSquares


def lens_merit_function(parameters, **kwargs):
    """
    Realistic lens merit function with vector residuals.
    Models a singlet lens with focal length and aberration constraints.
    """
    results = []
    
    for _, row in parameters.iterrows():
        # Extract lens parameters
        c1 = row['curvature_1']  # First surface curvature (1/mm)
        c2 = row['curvature_2']  # Second surface curvature (1/mm) 
        t = row['thickness']      # Center thickness (mm)
        n = row['index']          # Refractive index
        
        # Initialize residuals list
        residuals = []
        
        # 1. Focal length constraint (primary objective)
        # Using lensmaker's equation
        power = (n - 1) * (c1 - c2 + (n - 1) * c1 * c2 * t / n)
        if abs(power) > 1e-6:
            f_actual = 1 / power
        else:
            f_actual = 1e6  # Very large focal length
        
        f_target = 100.0  # Target focal length in mm
        focal_residual = (f_actual - f_target) / 10.0  # Scale for balance
        residuals.append(focal_residual)
        
        # 2. Spherical aberration at different heights
        # Simplified Seidel approximation
        for h in [0.5, 0.707, 1.0]:  # Normalized pupil heights
            sa_coeff = h**4 * (c1**3 - c2**3) * t * (n - 1) / n
            residuals.append(sa_coeff * 100)  # Scale factor
        
        # 3. Physical constraints as soft penalties
        # Minimum thickness
        thickness_residual = max(0, (2.0 - t))
        residuals.append(thickness_residual)
        
        # Maximum thickness  
        max_thickness_residual = max(0, (t - 20.0))
        residuals.append(max_thickness_residual)
        
        # Edge thickness constraint
        edge_thickness = t - 0.1 * (abs(c1) + abs(c2)) * 100  # Simplified
        edge_residual = max(0, (1.0 - edge_thickness))
        residuals.append(edge_residual)
        
        # Compute total merit (for reporting)
        metric = sum(r**2 for r in residuals)
        
        results.append({
            'metric': metric,
            'residuals': residuals
        })
    
    return results


def plot_lens_optimization_results(optimizer, output_dir):
    """Create comprehensive plots of lens optimization results."""
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    history = optimizer.history
    points = history['points']
    metrics = history['metrics']
    
    # 1. Merit function evolution
    ax = axes[0]
    ax.semilogy(metrics['iter'], metrics['metric'], 'b-', linewidth=2)
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Merit Function')
    ax.set_title('Convergence History')
    ax.grid(True, alpha=0.3)
    
    # 2. Focal length evolution
    focal_lengths = []
    for idx, row in points.iterrows():
        c1, c2, t, n = row['curvature_1'], row['curvature_2'], row['thickness'], row['index']
        power = (n - 1) * (c1 - c2 + (n - 1) * c1 * c2 * t / n)
        f = 1 / power if abs(power) > 1e-6 else np.sign(power) * 1000
        focal_lengths.append(f)
    
    ax = axes[1]
    ax.plot(points['iter'], focal_lengths, 'r-', linewidth=2)
    ax.axhline(y=100, color='g', linestyle='--', label='Target (100mm)')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Focal Length (mm)')
    ax.set_title('Focal Length Convergence')
    ax.set_ylim(50, 150)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Damping factor evolution
    ax = axes[2]
    ax.semilogy(metrics['iter'], metrics['damping'], 'g-', linewidth=2)
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Damping Factor (λ)')
    ax.set_title('Adaptive Damping')
    ax.grid(True, alpha=0.3)
    
    # 4. Curvature evolution
    ax = axes[3]
    ax.plot(points['iter'], points['curvature_1'], 'b-', label='Surface 1')
    ax.plot(points['iter'], points['curvature_2'], 'r-', label='Surface 2')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Curvature (1/mm)')
    ax.set_title('Surface Curvatures')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 5. Physical parameters
    ax = axes[4]
    ax.plot(points['iter'], points['thickness'], 'purple', label='Thickness')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Thickness (mm)')
    ax.set_title('Lens Thickness')
    ax.grid(True, alpha=0.3)
    
    # 6. Gradient and step norms
    ax = axes[5]
    ax.semilogy(metrics['iter'], metrics['gradient_norm'], 'b-', label='Gradient Norm')
    ax.semilogy(metrics['iter'], metrics['step_norm'], 'r-', label='Step Norm')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Norm')
    ax.set_title('Gradient and Step Norms')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'lens_optimization_summary.png'), dpi=150)
    plt.close()


def test_lens_optimization(results_dir=None):
    """Main lens optimization test."""
    
    print("="*70)
    print("LENS OPTIMIZATION WITH DAMPED LEAST SQUARES")
    print("="*70)
    print("\nObjective: Design a singlet lens with:")
    print("- Target focal length: 100mm")
    print("- Minimized spherical aberration")
    print("- Physical manufacturability constraints")
    
    # Set up results directory
    if results_dir is None:
        results_dir = os.path.join(os.path.dirname(__file__), 'test_results_lens')
    os.makedirs(results_dir, exist_ok=True)
    
    # Define lens parameters
    params_df = pd.DataFrame({
        'name': ['curvature_1', 'curvature_2', 'thickness', 'index'],
        'min': [-0.05, -0.05, 2.0, 1.45],       # Physical bounds
        'max': [0.05, 0.05, 20.0, 1.85],        # Glass catalog range
        'default': [0.01, -0.01, 5.0, 1.517],   # BK7-like starting point
        'variation': ['continuous', 'continuous', 'continuous', 'continuous']
    })
    
    print(f"\nInitial parameters:")
    for _, row in params_df.iterrows():
        print(f"  {row['name']:12s}: {row['default']:.4f} (range: [{row['min']:.4f}, {row['max']:.4f}])")
    
    # Create optimizer
    dls = DampedLeastSquares(
        seed=42,
        eval_func=lens_merit_function,
        parameters=params_df,
        opt_min_or_max='min',
        max_iterations=100,
        metric_threshold=1e-6,
        gradient_tolerance=1e-8,
        parameter_tolerance=1e-10,
        max_iter_without_improvement=30,
        initial_damping=0.01,
        damping_increase_factor=2.0,
        damping_decrease_factor=0.7,
        min_damping=1e-10,
        max_damping=1e4,
        jacobian_method='finite_difference',
        jacobian_step_size=1e-7,
        jacobian_step_size_relative=True,
        initial_point='default',  # Use default values
        residual_type='vector',
        use_qr_decomposition=True,
        boundary_handling='reflect',
        results_dir=results_dir
    )
    
    # Progress callback
    def progress_callback(**kwargs):
        if kwargs['iteration'] % 10 == 0:
            opt = kwargs['optimizer']
            c1 = opt.current_parameters.iloc[0]['curvature_1']
            c2 = opt.current_parameters.iloc[0]['curvature_2']
            t = opt.current_parameters.iloc[0]['thickness']
            n = opt.current_parameters.iloc[0]['index']
            
            power = (n - 1) * (c1 - c2 + (n - 1) * c1 * c2 * t / n)
            f = 1 / power if abs(power) > 1e-6 else 1e6
            
            print(f"Iter {opt.iter:3d}: merit = {opt.current_metric:.6f}, "
                  f"f = {f:6.1f}mm, λ = {opt.damping_factor:.1e}")
    
    dls.callback_after_each_iter = progress_callback
    
    # Run optimization
    print("\nOptimizing...")
    dls.run_optimization()
    
    # Extract and display results
    c1_final = dls.best_parameters['curvature_1']
    c2_final = dls.best_parameters['curvature_2']
    t_final = dls.best_parameters['thickness']
    n_final = dls.best_parameters['index']
    
    power_final = (n_final - 1) * (c1_final - c2_final + 
                                   (n_final - 1) * c1_final * c2_final * t_final / n_final)
    f_final = 1 / power_final if abs(power_final) > 1e-6 else 1e6
    
    print(f"\n" + "="*70)
    print("OPTIMIZATION RESULTS")
    print("="*70)
    print(f"\nFinal parameters:")
    print(f"  Curvature 1  : {c1_final:8.5f} (1/mm)")
    print(f"  Curvature 2  : {c2_final:8.5f} (1/mm)")
    print(f"  Thickness    : {t_final:8.3f} mm")
    print(f"  Index        : {n_final:8.5f}")
    print(f"\nDerived properties:")
    print(f"  Focal length : {f_final:8.2f} mm (target: 100 mm)")
    print(f"  Radius 1     : {1/c1_final if abs(c1_final) > 1e-6 else 'inf':8.1f} mm")
    print(f"  Radius 2     : {1/c2_final if abs(c2_final) > 1e-6 else 'inf':8.1f} mm")
    print(f"\nOptimization statistics:")
    print(f"  Iterations   : {dls.iter}")
    print(f"  Evaluations  : {dls.nr_evaluations}")
    print(f"  Final merit  : {dls.best_metric:.6e}")
    
    # Save results
    print("\nSaving results...")
    
    # Save optimization data
    dls.write_best_parameters_to_file()
    dls.write_optimization_info_to_file()
    dls.write_history_to_file()
    
    # Create visualizations
    plot_lens_optimization_results(dls, results_dir)
    
    # Additional plots
    dls.plot_metrics(save_path=os.path.join(results_dir, 'metrics_evolution.png'))
    dls.plot_damping(save_path=os.path.join(results_dir, 'damping_evolution.png'))
    dls.plot_residuals(save_path=os.path.join(results_dir, 'residuals_evolution.png'))
    dls.plot_parameters(save_path=os.path.join(results_dir, 'parameters_evolution.png'))
    
    print(f"\nAll results saved to: {results_dir}")
    
    return dls


def test_sensitivity_analysis():
    """Test DLS behavior with different damping strategies."""
    
    print("\n" + "="*70)
    print("SENSITIVITY ANALYSIS: DAMPING STRATEGIES")
    print("="*70)
    
    damping_configs = [
        ('Conservative', 1.0, 5.0, 0.2),
        ('Moderate', 0.1, 2.0, 0.5),
        ('Aggressive', 0.001, 1.5, 0.8),
    ]
    
    results = {}
    
    for name, initial, increase, decrease in damping_configs:
        print(f"\nTesting {name} damping: lambda_0={initial}, up={increase}, down={decrease}")
        
        params_df = pd.DataFrame({
            'name': ['curvature_1', 'curvature_2', 'thickness', 'index'],
            'min': [-0.05, -0.05, 2.0, 1.45],
            'max': [0.05, 0.05, 20.0, 1.85],
            'default': [0.01, -0.01, 5.0, 1.517],
            'variation': ['continuous', 'continuous', 'continuous', 'continuous']
        })
        
        dls = DampedLeastSquares(
            seed=42,
            eval_func=lens_merit_function,
            parameters=params_df,
            opt_min_or_max='min',
            max_iterations=50,
            initial_damping=initial,
            damping_increase_factor=increase,
            damping_decrease_factor=decrease,
            residual_type='vector',
            initial_point='default'
        )
        
        dls.run_optimization()
        
        results[name] = {
            'iterations': dls.iter,
            'evaluations': dls.nr_evaluations,
            'final_metric': dls.best_metric,
            'final_damping': dls.damping_factor
        }
        
        print(f"  Result: {dls.iter} iters, metric={dls.best_metric:.6e}")
    
    # Summary
    print("\nSummary:")
    for name, res in results.items():
        print(f"{name:12s}: {res['iterations']:3d} iterations, "
              f"final metric = {res['final_metric']:.6e}")
    
    return results


if __name__ == "__main__":
    # Run main lens optimization test
    dls_lens = test_lens_optimization()
    
    # Run sensitivity analysis
    sensitivity_results = test_sensitivity_analysis()
    
    print("\n" + "="*70)
    print("LENS OPTIMIZATION TESTS COMPLETED!")
    print("DLS excels at sensitive optimization problems")
    print("="*70)