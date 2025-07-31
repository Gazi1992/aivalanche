"""
Comprehensive test suite for DampedLeastSquares optimizer.

This script tests the DLS optimizer with various test functions
from the aivalanche_lib.test_functions module, creating visualizations
and animations similar to the Nelder-Mead tests.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.patches as patches

from aivalanche_lib.optimization.damped_least_squares import DampedLeastSquares
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import (
    ALL_FUNCTIONS, 
    get_function_details, 
    generate_parameters_config as _generate_parameters_config
)


def generate_parameters_config(details, use_random_start=True, random_seed=None):
    """
    Generate parameter configuration with random starting points.
    
    Args:
        details: Function details from get_function_details
        use_random_start: If True, use random starting points instead of midpoint
        random_seed: Random seed for reproducibility
        
    Returns:
        List of parameter configurations
    """
    config = []
    dim = details['dim']
    bounds = details['bounds']
    
    if random_seed is not None:
        rng = np.random.RandomState(random_seed)
    else:
        rng = np.random.RandomState()
    
    for i in range(dim):
        param_name = f"x{i+1}"
        min_val, max_val = bounds[i]
        
        if use_random_start:
            # Generate random starting point away from boundaries
            # Use a point in the middle 80% of the range to avoid boundary issues
            range_width = max_val - min_val
            margin = 0.1 * range_width
            default_val = rng.uniform(min_val + margin, max_val - margin)
        else:
            # Use midpoint
            default_val = (min_val + max_val) / 2.0
            
        config.append({
            "name": param_name,
            "min": min_val,
            "max": max_val,
            "default": default_val,
            "variation": "continuous"
        })
    
    return config


def create_test_function_wrapper(func_details, residual_type='scalar'):
    """
    Creates a wrapper function that adapts test functions to the format expected by DLS.
    
    Args:
        func_details: Dictionary containing function details from get_function_details
        residual_type: 'scalar' or 'vector' - determines return format
        
    Returns:
        A function that accepts parameters DataFrame and returns list of response dicts
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
            if residual_type == 'vector':
                # For vector residuals, create artificial residuals
                # This is a simple decomposition - more sophisticated ones could be used
                if dim == 2:
                    # For 2D functions, create residuals based on distance from optimum
                    optimum = func_details.get('optimum', np.zeros(dim))
                    r1 = (x[0] - optimum[0]) * np.sqrt(abs(value) + 1e-10)
                    r2 = (x[1] - optimum[1]) * np.sqrt(abs(value) + 1e-10)
                    residuals = [r1, r2]
                else:
                    # General case: split the objective into multiple residuals
                    residuals = [np.sqrt(abs(value) / dim) for _ in range(dim)]
            else:
                residuals = None
            
            response = {
                'metric': value,
                'data': {f'x{i+1}': x_values[i] for i in range(len(x_values))}
            }
            
            if residuals is not None:
                response['residuals'] = residuals
            
            responses.append(response)
        
        return responses
    
    return wrapper


def plot_function_landscape(func_details, test_results_dir, optimizer=None, func_name=None):
    """
    Plot the function landscape for 2D functions with optimizer path.
    
    Args:
        func_details: Function details dictionary
        test_results_dir: Directory to save the plot
        optimizer: Optional DLS optimizer instance to overlay path
    """
    if func_details['dim'] != 2:
        return
    
    func = func_details['func']
    bounds = func_details['bounds']
    
    # Create grid
    x = np.linspace(bounds[0][0], bounds[0][1], 200)
    y = np.linspace(bounds[1][0], bounds[1][1], 200)
    X, Y = np.meshgrid(x, y)
    
    # Evaluate function on grid
    Z = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i, j] = func(np.array([X[i, j], Y[i, j]]))
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot contour
    levels = np.logspace(np.log10(Z.min() + 1e-10), np.log10(Z.max()), 50)
    contour = ax.contour(X, Y, Z, levels=levels, alpha=0.6)
    ax.clabel(contour, inline=True, fontsize=8, fmt='%.2e')
    
    # Plot optimum
    if 'optimum' in func_details:
        optimum = func_details['optimum']
        ax.plot(optimum[0], optimum[1], 'r*', markersize=15, label='Global Optimum')
    
    # Plot optimization path if optimizer provided
    if optimizer is not None:
        history = optimizer.history['points']
        ax.plot(history['x1'], history['x2'], 'b.-', alpha=0.7, label='Optimization Path')
        ax.plot(history.iloc[0]['x1'], history.iloc[0]['x2'], 'go', markersize=10, label='Start')
        ax.plot(history.iloc[-1]['x1'], history.iloc[-1]['x2'], 'ro', markersize=10, label='End')
    
    ax.set_xlabel('x1')
    ax.set_ylabel('x2')
    title_name = func_name if func_name else func_details.get('name', 'Unknown')
    ax.set_title(f'{title_name} Function Landscape')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(test_results_dir, 'function_landscape.png'), dpi=150)
    plt.close()


def create_optimization_animation(optimizer, func_details, test_results_dir):
    """
    Create an animation of the optimization process for 2D functions.
    
    Args:
        optimizer: DLS optimizer instance
        func_details: Function details dictionary
        test_results_dir: Directory to save the animation
    """
    if func_details['dim'] != 2:
        return
    
    func = func_details['func']
    bounds = func_details['bounds']
    
    # Create grid for background
    x = np.linspace(bounds[0][0], bounds[0][1], 100)
    y = np.linspace(bounds[1][0], bounds[1][1], 100)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i, j] = func(np.array([X[i, j], Y[i, j]]))
    
    # Get optimization history
    history = optimizer.history['points']
    metrics_history = optimizer.history['metrics']
    
    # Create figure with subplots
    fig = plt.figure(figsize=(15, 6))
    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2)
    
    # Plot function landscape
    levels = np.logspace(np.log10(Z.min() + 1e-10), np.log10(Z.max()), 30)
    contour = ax1.contourf(X, Y, Z, levels=levels, alpha=0.6, cmap='viridis')
    fig.colorbar(contour, ax=ax1)
    
    # Initialize plots
    line1, = ax1.plot([], [], 'r.-', linewidth=2, markersize=8)
    point1, = ax1.plot([], [], 'ro', markersize=12)
    
    line2, = ax2.semilogy([], [], 'b-', linewidth=2)
    point2, = ax2.plot([], [], 'bo', markersize=8)
    
    ax1.set_xlim(bounds[0])
    ax1.set_ylim(bounds[1])
    ax1.set_xlabel('x1')
    ax1.set_ylabel('x2')
    ax1.set_title('Parameter Space')
    
    ax2.set_xlim(0, len(history))
    ax2.set_ylim(metrics_history['metric'].min() * 0.5, metrics_history['metric'].max() * 2)
    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Metric (log scale)')
    ax2.set_title('Convergence History')
    ax2.grid(True, alpha=0.3)
    
    # Add optimum point if known
    if 'optimum' in func_details:
        optimum = func_details['optimum']
        ax1.plot(optimum[0], optimum[1], 'g*', markersize=15)
    
    def init():
        line1.set_data([], [])
        point1.set_data([], [])
        line2.set_data([], [])
        point2.set_data([], [])
        return line1, point1, line2, point2
    
    def animate(frame):
        # Update parameter space plot
        x_data = history.iloc[:frame+1]['x1'].values
        y_data = history.iloc[:frame+1]['x2'].values
        line1.set_data(x_data, y_data)
        point1.set_data([x_data[-1]], [y_data[-1]])
        
        # Update convergence plot
        iters = metrics_history.iloc[:frame+1]['iter'].values
        metrics = metrics_history.iloc[:frame+1]['metric'].values
        line2.set_data(iters, metrics)
        point2.set_data([iters[-1]], [metrics[-1]])
        
        # Update damping factor in title
        damping = metrics_history.iloc[frame]['damping']
        fig.suptitle(f'DLS Optimization - Iteration {frame+1}, λ = {damping:.2e}', fontsize=14)
        
        return line1, point1, line2, point2
    
    # Create animation
    frames_dir = os.path.join(test_results_dir, 'optimization_frames')
    os.makedirs(frames_dir, exist_ok=True)
    
    anim = FuncAnimation(fig, animate, init_func=init, frames=len(history), 
                        interval=100, blit=True, repeat=True)
    
    # Save animation
    writer = PillowWriter(fps=10)
    anim.save(os.path.join(test_results_dir, 'optimization_animation.gif'), writer=writer)
    
    plt.close()


def test_function_optimization(func_name, max_iterations=100, residual_type='vector', 
                             results_base_dir=None, initial_point='default'):
    """
    Test DLS optimization with a specific test function.
    
    Args:
        func_name: Name of the test function from ALL_FUNCTIONS
        max_iterations: Maximum iterations for optimization
        residual_type: 'scalar' or 'vector' residual formulation
        results_base_dir: Base directory for results (if None, uses default)
        initial_point: Initial point strategy ('default', 'random', or DataFrame)
    """
    print(f"\n{'='*60}")
    print(f"Testing DLS optimizer with {func_name} function")
    print(f"Residual type: {residual_type}")
    print(f"Initial point: {initial_point}")
    print(f"{'='*60}")
    
    # Get function details
    if func_name in ['sphere_nd', 'ackley_nd', 'rastrigin_nd', 'griewank_nd']:
        # For n-dimensional functions, use 2D for visualization
        func_details = get_function_details(func_name, n_dim=2)
    else:
        func_details = get_function_details(func_name)
    
    # Generate parameter configuration with random starting point
    param_config = generate_parameters_config(func_details, use_random_start=True, random_seed=42)
    parameters = Parameters(param_config)
    
    # Print starting point
    print("\nStarting point:")
    for param in param_config:
        print(f"  {param['name']}: {param['default']:.4f} (range: [{param['min']}, {param['max']}])")
    
    # Print known optimum if available
    if 'optimum' in func_details:
        print("\nKnown optimum:")
        optimum = func_details['optimum']
        for i, val in enumerate(optimum):
            print(f"  x{i+1}: {val:.4f}")
    
    # Create wrapper function
    eval_func = create_test_function_wrapper(func_details, residual_type=residual_type)
    
    # Set up results directory
    if results_base_dir is None:
        results_base_dir = os.path.dirname(__file__)
    test_results_dir = os.path.join(results_base_dir, f'test_results_{func_name}_{residual_type}')
    os.makedirs(test_results_dir, exist_ok=True)
    
    # Determine initial point
    if isinstance(initial_point, str):
        if initial_point == 'random':
            initial_point_value = None
            use_defaults = False
        elif initial_point == 'default':
            initial_point_value = 'default'
            use_defaults = False
        else:
            initial_point_value = initial_point
            use_defaults = False
    else:
        # initial_point is a DataFrame or other object
        initial_point_value = initial_point
        use_defaults = False
    
    # Create optimizer
    optimizer = DampedLeastSquares(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=max_iterations,
        metric_threshold=1e-10,
        max_iter_without_improvement=30,
        gradient_tolerance=1e-8,
        parameter_tolerance=1e-8,
        initial_damping=0.1,
        damping_increase_factor=2.0,
        damping_decrease_factor=0.5,
        min_damping=1e-10,
        max_damping=1e6,
        jacobian_step_size=1e-6,
        jacobian_step_size_relative=True,
        initial_point=initial_point_value,
        use_defaults_in_initial_point=use_defaults,
        residual_type=residual_type,
        use_qr_decomposition=True,
        boundary_handling='reflect',
        results_dir=test_results_dir
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    # Print results
    print(f"\nOptimization completed!")
    print(f"Best metric: {optimizer.best_metric:.6e}")
    print(f"Best parameters: {optimizer.best_parameters}")
    print(f"Number of iterations: {optimizer.iter}")
    print(f"Number of evaluations: {optimizer.nr_evaluations}")
    print(f"Stop reason: {optimizer.stop_reason}")
    
    # Check against known optimum
    optimum_val = func_details['optimum_val']
    print(f"\nKnown optimum value: {optimum_val}")
    print(f"Distance from optimum: {abs(optimizer.best_metric - optimum_val):.6e}")
    
    # Save results
    print("\nSaving results...")
    
    # Save best parameters
    optimizer.write_best_parameters_to_file(
        os.path.join(test_results_dir, 'best_parameters.csv')
    )
    print("- Best parameters saved")
    
    # Save optimization info
    optimizer.write_optimization_info_to_file(
        os.path.join(test_results_dir, 'optimization_info.json')
    )
    print("- Optimization info saved")
    
    # Save history
    optimizer.write_history_to_file(
        which='points',
        file_path=os.path.join(test_results_dir, 'history_points.csv')
    )
    print("- History saved")
    
    # Create visualizations
    print("\nCreating visualizations...")
    
    # Plot metrics evolution
    fig1, ax1 = optimizer.plot_metrics(
        figsize=(10, 6),
        y_scale='log',
        save_path=os.path.join(test_results_dir, 'metrics_evolution.png')
    )
    plt.close(fig1)
    print("- Metrics evolution plot saved")
    
    # Plot damping evolution
    fig2, ax2 = optimizer.plot_damping(
        figsize=(10, 6),
        save_path=os.path.join(test_results_dir, 'damping_evolution.png')
    )
    plt.close(fig2)
    print("- Damping evolution plot saved")
    
    # For 2D functions, create additional visualizations
    if func_details['dim'] == 2:
        # Plot function landscape with path
        plot_function_landscape(func_details, test_results_dir, optimizer, func_name)
        print("- Function landscape plot saved")
        
        # Create optimization animation
        print("\nCreating optimization animation...")
        create_optimization_animation(optimizer, func_details, test_results_dir)
        print("- Optimization animation saved")
        
        # Plot parameter evolution
        fig3, ax3 = optimizer.plot_parameters(
            parameter_names=['x1', 'x2'],
            figsize=(10, 6),
            save_path=os.path.join(test_results_dir, 'parameter_evolution.png')
        )
        plt.close(fig3)
        print("- Parameter evolution plot saved")
    
    # Plot residuals evolution (if vector type)
    if residual_type == 'vector':
        fig4, ax4 = optimizer.plot_residuals(
            figsize=(10, 6),
            save_path=os.path.join(test_results_dir, 'residuals_evolution.png')
        )
        plt.close(fig4)
        print("- Residuals evolution plot saved")
    
    print(f"\nAll files saved to: {test_results_dir}")
    
    return optimizer


def test_multiple_functions():
    """
    Test DLS optimization with multiple test functions.
    """
    # Select a variety of test functions
    test_functions = [
        # 2D functions for full visualization
        ('rosenbrock_2d', 'vector'),
        ('sphere_2d', 'scalar'),
        ('himmelblau_2d', 'vector'),
        ('beale_2d', 'vector'),
        
        # 1D function
        ('parabola_1d', 'scalar'),
        
        # 3D function  
        ('sphere_3d', 'scalar'),
        
        # n-dimensional functions (tested in 2D)
        ('ackley_nd', 'vector'),
        ('rastrigin_nd', 'vector')
    ]
    
    results = {}
    
    for func_name, residual_type in test_functions:
        try:
            print(f"\n{'#'*80}")
            print(f"# Testing {func_name} with {residual_type} residuals")
            print(f"{'#'*80}")
            
            optimizer = test_function_optimization(
                func_name, 
                max_iterations=100,
                residual_type=residual_type,
                initial_point='default'
            )
            
            results[func_name] = {
                'success': True,
                'best_metric': optimizer.best_metric,
                'iterations': optimizer.iter,
                'evaluations': optimizer.nr_evaluations,
                'stop_reason': optimizer.stop_reason
            }
            
        except Exception as e:
            print(f"\nError testing {func_name}: {str(e)}")
            results[func_name] = {
                'success': False,
                'error': str(e)
            }
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY OF ALL TESTS")
    print(f"{'='*80}")
    
    for func_name, result in results.items():
        if result['success']:
            print(f"\n{func_name}:")
            print(f"  - Best metric: {result['best_metric']:.6e}")
            print(f"  - Iterations: {result['iterations']}")
            print(f"  - Evaluations: {result['evaluations']}")
            print(f"  - Stop reason: {result['stop_reason']}")
        else:
            print(f"\n{func_name}: FAILED")
            print(f"  - Error: {result['error']}")
    
    return results


def test_initial_point_options():
    """
    Test different initial point options for DLS.
    """
    print(f"\n{'='*80}")
    print("Testing Different Initial Point Options")
    print(f"{'='*80}")
    
    func_name = 'rosenbrock_2d'
    
    # Test with 'default'
    print("\n1. Testing with initial_point='default'")
    opt1 = test_function_optimization(
        func_name,
        max_iterations=50,
        residual_type='vector',
        initial_point='default',
        results_base_dir=os.path.join(os.path.dirname(__file__), 'test_initial_default')
    )
    
    # Test with random (None)
    print("\n2. Testing with random initial point")
    opt2 = test_function_optimization(
        func_name,
        max_iterations=50,
        residual_type='vector',
        initial_point='random',
        results_base_dir=os.path.join(os.path.dirname(__file__), 'test_initial_random')
    )
    
    # Test with specific point
    print("\n3. Testing with specific initial point")
    initial_df = pd.DataFrame([{'x1': -1.0, 'x2': 2.0}])
    opt3 = test_function_optimization(
        func_name,
        max_iterations=50,
        residual_type='vector',
        initial_point=initial_df,
        results_base_dir=os.path.join(os.path.dirname(__file__), 'test_initial_specific')
    )
    
    print("\nComparison:")
    print(f"Default: {opt1.iter} iterations, final metric = {opt1.best_metric:.6e}")
    print(f"Random:  {opt2.iter} iterations, final metric = {opt2.best_metric:.6e}")
    print(f"Specific: {opt3.iter} iterations, final metric = {opt3.best_metric:.6e}")


if __name__ == "__main__":
    # Test all functions
    print("Running comprehensive DLS tests...")
    
    # Test multiple functions
    results = test_multiple_functions()
    
    # Test initial point options
    test_initial_point_options()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED!")
    print("="*80)