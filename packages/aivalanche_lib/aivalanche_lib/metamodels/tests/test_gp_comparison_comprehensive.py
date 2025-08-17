"""
Comprehensive comparison of standard GPy optimization vs DE-based optimization
for Gaussian Process metamodels across various test functions.

The DE-based GP now uses a simplified interface with optimal defaults:
- No configuration needed
- Adaptive bounds based on data
- Automatic refinement at the end
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from metamodels.gaussian_process import GaussianProcessMetamodel


def sphere_function(X):
    """Sphere function - simple convex."""
    return np.sum(X**2, axis=1)


def rosenbrock_function(X):
    """Rosenbrock function - valley shaped."""
    x, y = X[:, 0], X[:, 1]
    return (1 - x)**2 + 100 * (y - x**2)**2


def himmelblau_function(X):
    """Himmelblau function - multi-modal."""
    x, y = X[:, 0], X[:, 1]
    return (x**2 + y - 11)**2 + (x + y**2 - 7)**2


def rastrigin_function(X):
    """Rastrigin function - highly multi-modal."""
    A = 10
    n = X.shape[1]
    return A * n + np.sum(X**2 - A * np.cos(2 * np.pi * X), axis=1)


def ackley_function(X):
    """Ackley function - multi-modal with global structure."""
    a = 20
    b = 0.2
    c = 2 * np.pi
    n = X.shape[1]
    
    sum1 = np.sum(X**2, axis=1)
    sum2 = np.sum(np.cos(c * X), axis=1)
    
    term1 = -a * np.exp(-b * np.sqrt(sum1 / n))
    term2 = -np.exp(sum2 / n)
    
    return term1 + term2 + a + np.exp(1)


def generate_test_data(func, n_train=50, n_test=20, noise_level=0.01, bounds=(-5, 5), seed=42):
    """Generate training and test data for a given function."""
    np.random.seed(seed)
    
    # Generate training data
    X_train = np.random.uniform(bounds[0], bounds[1], (n_train, 2))
    y_train = func(X_train)
    
    # Add noise
    if noise_level > 0:
        y_train += np.random.normal(0, noise_level * np.std(y_train), y_train.shape)
    
    # Generate test data (on a grid for better coverage)
    x_test = np.linspace(bounds[0], bounds[1], int(np.sqrt(n_test)))
    X_test_grid = np.array(np.meshgrid(x_test, x_test)).T.reshape(-1, 2)
    y_test = func(X_test_grid)
    
    # Convert to DataFrames
    X_train_df = pd.DataFrame(X_train, columns=['x', 'y'])
    X_test_df = pd.DataFrame(X_test_grid, columns=['x', 'y'])
    
    return X_train_df, y_train, X_test_df, y_test


def compare_gp_methods(func, func_name, n_train=50, n_test=25, noise_level=0.01, bounds=(-5, 5)):
    """Compare standard GP with DE-optimized GP on a given function."""
    
    print(f"\n{'='*70}")
    print(f"Testing: {func_name}")
    print(f"{'='*70}")
    
    # Generate data
    X_train, y_train, X_test, y_test = generate_test_data(
        func, n_train, n_test, noise_level, bounds
    )
    
    print(f"Data: {n_train} training samples, {n_test} test samples")
    print(f"Noise level: {noise_level * 100:.1f}% of std")
    
    results = {}
    
    # Method 1: Standard GPy optimization
    print("\n1. STANDARD GPy OPTIMIZATION")
    print("-" * 40)
    
    gp_standard = GaussianProcessMetamodel(
        kernel_type='rbf',
        optimize_hyperparameters=True,
        n_restarts=5
    )
    
    start_time = time.time()
    gp_standard.fit(X_train, y_train)
    fit_time_standard = time.time() - start_time
    
    # Make predictions
    start_time = time.time()
    y_pred_standard = gp_standard.predict(X_test)
    pred_time_standard = time.time() - start_time
    
    # Calculate metrics
    r2_standard = r2_score(y_test, y_pred_standard)
    mse_standard = mean_squared_error(y_test, y_pred_standard)
    mae_standard = mean_absolute_error(y_test, y_pred_standard)
    
    # Get hyperparameters
    params_standard = gp_standard.get_kernel_parameters()
    
    print(f"  Fitting time: {fit_time_standard:.3f}s")
    print(f"  Prediction time: {pred_time_standard:.4f}s")
    print(f"  R² score: {r2_standard:.4f}")
    print(f"  MSE: {mse_standard:.4e}")
    print(f"  MAE: {mae_standard:.4e}")
    print(f"  Kernel variance: {params_standard.get('variance', 'N/A'):.4f}")
    print(f"  Noise variance: {params_standard.get('noise_variance', 'N/A'):.2e}")
    if 'length_scale' in params_standard:
        ls = params_standard['length_scale']
        if isinstance(ls, list):
            print(f"  Length scales: [{ls[0]:.4f}, {ls[1]:.4f}]")
        else:
            print(f"  Length scale: {ls:.4f}")
    
    results['standard'] = {
        'fit_time': fit_time_standard,
        'pred_time': pred_time_standard,
        'r2': r2_standard,
        'mse': mse_standard,
        'mae': mae_standard,
        'params': params_standard,
        'predictions': y_pred_standard
    }
    
    # Method 2: DE optimization with simplified interface
    print("\n2. DE OPTIMIZATION (Simplified Interface)")
    print("-" * 40)
    
    gp_de = GaussianProcessMetamodel(
        kernel_type='rbf',
        optimize_hyperparameters=True,
        optimization_method='de'  # Use DE optimization
        # No additional configuration needed - optimal defaults are built-in
    )
    
    start_time = time.time()
    gp_de.fit(X_train, y_train)
    fit_time_de = time.time() - start_time
    
    # Make predictions
    start_time = time.time()
    y_pred_de = gp_de.predict(X_test)
    pred_time_de = time.time() - start_time
    
    # Calculate metrics
    r2_de = r2_score(y_test, y_pred_de)
    mse_de = mean_squared_error(y_test, y_pred_de)
    mae_de = mean_absolute_error(y_test, y_pred_de)
    
    # Get hyperparameters
    params_de = gp_de.get_kernel_parameters()
    
    print(f"  Fitting time: {fit_time_de:.3f}s")
    print(f"  Prediction time: {pred_time_de:.4f}s")
    print(f"  R² score: {r2_de:.4f}")
    print(f"  MSE: {mse_de:.4e}")
    print(f"  MAE: {mae_de:.4e}")
    print(f"  Kernel variance: {params_de.get('variance', 'N/A'):.4f}")
    print(f"  Noise variance: {params_de.get('noise_variance', 'N/A'):.2e}")
    if 'length_scale' in params_de:
        ls = params_de['length_scale']
        if isinstance(ls, list):
            print(f"  Length scales: [{ls[0]:.4f}, {ls[1]:.4f}]")
        else:
            print(f"  Length scale: {ls:.4f}")
    
    results['de'] = {
        'fit_time': fit_time_de,
        'pred_time': pred_time_de,
        'r2': r2_de,
        'mse': mse_de,
        'mae': mae_de,
        'params': params_de,
        'predictions': y_pred_de
    }
    
    
    # Summary comparison
    print("\n" + "="*70)
    print("COMPARISON SUMMARY")
    print("="*70)
    
    print(f"{'Method':<20} {'Fit Time':<10} {'R²':<10} {'MSE':<12} {'MAE':<12}")
    print("-"*64)
    print(f"{'Standard GPy':<20} {results['standard']['fit_time']:<10.3f} "
          f"{results['standard']['r2']:<10.4f} {results['standard']['mse']:<12.4e} "
          f"{results['standard']['mae']:<12.4e}")
    print(f"{'DE (Simplified)':<20} {results['de']['fit_time']:<10.3f} "
          f"{results['de']['r2']:<10.4f} {results['de']['mse']:<12.4e} "
          f"{results['de']['mae']:<12.4e}")
    
    # Calculate improvements
    r2_improvement = (results['de']['r2'] - results['standard']['r2']) / (1 - results['standard']['r2'] + 1e-10) * 100
    mse_improvement = (results['standard']['mse'] - results['de']['mse']) / (results['standard']['mse'] + 1e-10) * 100
    
    print(f"\nImprovement of DE over Standard GPy:")
    print(f"  R² improvement: {r2_improvement:+.2f}%")
    print(f"  MSE reduction: {mse_improvement:+.2f}%")
    
    return results, X_train, y_train, X_test, y_test


def create_visualization(results, X_test, y_test, func_name):
    """Create visualization comparing the methods."""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Only compare standard and DE methods
    methods = ['standard', 'de']
    titles = ['Standard GPy', 'DE (Simplified)']
    colors = ['blue', 'green']
    
    # Row 1: Predictions vs True values
    for idx, (method, title, color) in enumerate(zip(methods, titles, colors)):
        ax = axes[0, idx]
        y_pred = results[method]['predictions']
        
        ax.scatter(y_test, y_pred, alpha=0.6, s=50, c=color, edgecolors='black', linewidth=0.5)
        
        # Perfect prediction line
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Perfect')
        
        # Add R² score
        r2 = results[method]['r2']
        ax.text(0.05, 0.95, f'R² = {r2:.4f}', transform=ax.transAxes,
                verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', 
                facecolor='white', alpha=0.8))
        
        ax.set_xlabel('True Values', fontsize=10)
        ax.set_ylabel('Predicted Values', fontsize=10)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    # Row 2: Error distributions
    for idx, (method, title, color) in enumerate(zip(methods, titles, colors)):
        ax = axes[1, idx]
        y_pred = results[method]['predictions']
        errors = y_test - y_pred
        
        ax.hist(errors, bins=20, alpha=0.7, color=color, edgecolor='black')
        ax.axvline(x=0, color='red', linestyle='--', alpha=0.5)
        
        # Add statistics
        mae = results[method]['mae']
        mse = results[method]['mse']
        ax.text(0.05, 0.95, f'MAE = {mae:.4e}\nMSE = {mse:.4e}', 
                transform=ax.transAxes, verticalalignment='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlabel('Prediction Error', fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        ax.set_title(f'{title} - Error Distribution', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle(f'GP Hyperparameter Optimization Comparison\nFunction: {func_name}',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save plot
    save_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(save_dir, f'gp_comparison_{func_name.lower().replace(" ", "_")}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved to: {save_path}")
    
    plt.show()


def main():
    """Run comprehensive comparison on multiple test functions."""
    
    print("="*70)
    print("COMPREHENSIVE GP HYPERPARAMETER OPTIMIZATION COMPARISON")
    print("Standard GPy vs Differential Evolution")
    print("="*70)
    
    # Test functions
    test_cases = [
        (sphere_function, "Sphere Function", (-5, 5), 0.02),
        (rosenbrock_function, "Rosenbrock Function", (-2, 2), 0.05),
        (himmelblau_function, "Himmelblau Function", (-5, 5), 0.02),
        (rastrigin_function, "Rastrigin Function", (-5.12, 5.12), 0.01),
        (ackley_function, "Ackley Function", (-5, 5), 0.02),
    ]
    
    all_results = {}
    
    for func, func_name, bounds, noise in test_cases:
        results, X_train, y_train, X_test, y_test = compare_gp_methods(
            func, func_name, 
            n_train=80,  # More training data
            n_test=100,  # More test points
            noise_level=noise,
            bounds=bounds
        )
        all_results[func_name] = results
        
        # Create visualization for each function
        create_visualization(results, X_test, y_test, func_name)
    
    # Overall summary
    print("\n" + "="*70)
    print("OVERALL SUMMARY ACROSS ALL FUNCTIONS")
    print("="*70)
    
    # Calculate average metrics
    avg_metrics = {method: {'r2': [], 'mse': [], 'mae': [], 'time': []} 
                   for method in ['standard', 'de']}
    
    for func_name, results in all_results.items():
        for method in avg_metrics.keys():
            avg_metrics[method]['r2'].append(results[method]['r2'])
            avg_metrics[method]['mse'].append(results[method]['mse'])
            avg_metrics[method]['mae'].append(results[method]['mae'])
            avg_metrics[method]['time'].append(results[method]['fit_time'])
    
    print(f"{'Method':<20} {'Avg R²':<12} {'Avg MSE':<12} {'Avg MAE':<12} {'Avg Time':<10}")
    print("-"*66)
    
    for method, label in [('standard', 'Standard GPy'), 
                          ('de', 'DE (Simplified)')]:
        avg_r2 = np.mean(avg_metrics[method]['r2'])
        avg_mse = np.mean(avg_metrics[method]['mse'])
        avg_mae = np.mean(avg_metrics[method]['mae'])
        avg_time = np.mean(avg_metrics[method]['time'])
        
        print(f"{label:<20} {avg_r2:<12.4f} {avg_mse:<12.4e} {avg_mae:<12.4e} {avg_time:<10.3f}")
    
    # Calculate average improvements
    avg_r2_improvement = []
    
    for func_name, results in all_results.items():
        r2_std = results['standard']['r2']
        r2_de = results['de']['r2']
        
        # Calculate improvement in terms of reducing error (1-R²)
        if r2_std < 0.9999:  # Avoid division by very small numbers
            imp = (r2_de - r2_std) / (1 - r2_std) * 100
            avg_r2_improvement.append(imp)
    
    if avg_r2_improvement:
        print(f"\nAverage R² Error Reduction:")
        print(f"  DE (Simplified): {np.mean(avg_r2_improvement):+.2f}%")
    
    print("\nTest completed successfully!")
    print("\nKey Advantages of DE Optimization in GP:")
    print("✓ Unified interface - just set optimization_method='de'")
    print("✓ No configuration required - optimal defaults built-in")
    print("✓ Adaptive bounds based on data characteristics")
    print("✓ Automatic refinement at the end for fine-tuning")
    print("✓ Consistent results without random restarts")
    print("✓ Falls back to standard GPy optimization by default")


if __name__ == "__main__":
    main()