"""
Simple test to verify ADAM optimizer basic functionality.
This test can run without the full test environment.
"""

import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))

try:
    from aivalanche_lib.optimization.adam import Adam
    from aivalanche_lib.parameters import Parameters
    print("✓ Successfully imported ADAM optimizer")
    
    # Create simple 2D quadratic function
    def simple_quadratic(params_df, **kwargs):
        """Simple quadratic function: f(x,y) = x^2 + y^2"""
        responses = []
        for _, row in params_df.iterrows():
            value = row['x']**2 + row['y']**2
            responses.append({'metric': value})
        return responses
    
    # Define parameters
    param_config = [
        {'name': 'x', 'min': -5.0, 'max': 5.0, 'default': 2.0, 'mode': 'variable', 'type': 'continuous'},
        {'name': 'y', 'min': -5.0, 'max': 5.0, 'default': -2.0, 'mode': 'variable', 'type': 'continuous'}
    ]
    
    # Create ADAM optimizer
    print("\n✓ Creating ADAM optimizer...")
    optimizer = Adam(
        seed=42,
        eval_func=simple_quadratic,
        parameters=Parameters(param_config),
        opt_min_or_max='min',
        max_iterations=50,
        learning_rate=0.1,
        gradient_tolerance=1e-6
    )
    
    print("✓ ADAM optimizer created successfully")
    print(f"  Number of parameters: {optimizer.nr_parameters}")
    print(f"  Number of variable parameters: {optimizer.nr_variable_parameters}")
    print(f"  Parameter names: {optimizer.parameters_names}")
    
    # Run optimization
    print("\n✓ Running optimization...")
    optimizer.run_optimization()
    
    print("\n✓ Optimization completed!")
    print(f"  Best metric: {optimizer.best_metric:.6e}")
    print(f"  Best parameters: x={optimizer.best_parameters['x']:.4f}, y={optimizer.best_parameters['y']:.4f}")
    print(f"  Iterations: {optimizer.iter}")
    print(f"  Evaluations: {optimizer.nr_evaluations}")
    print(f"  Stop reason: {optimizer.stop_reason}")
    
    # Test that we found the minimum
    assert optimizer.best_metric < 1e-6, f"Failed to minimize function: {optimizer.best_metric}"
    assert abs(optimizer.best_parameters['x']) < 1e-3, f"x not close to 0: {optimizer.best_parameters['x']}"
    assert abs(optimizer.best_parameters['y']) < 1e-3, f"y not close to 0: {optimizer.best_parameters['y']}"
    
    print("\n✓ All assertions passed!")
    print("\n[SUCCESS] ADAM optimizer is working correctly!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nMake sure you're running from the correct directory or have the package installed.")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()