"""
Simple test to debug metamodel issues.
"""

import numpy as np
import warnings
from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details, generate_parameters_config

# Suppress warnings
warnings.filterwarnings('ignore')

def test_simple_optimization():
    """Test basic DE optimization without metamodel."""
    print("\n" + "="*60)
    print("TESTING SIMPLE DE OPTIMIZATION")
    print("="*60)
    
    # Setup simple 2D function
    func_details = get_function_details('sphere_2d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    
    # Simple evaluation function
    def eval_func(parameters=None, parameters_df=None, **kwargs):
        df = parameters if parameters is not None else parameters_df
        responses = []
        for _, row in df.iterrows():
            x = np.array([row['x1'], row['x2']])
            value = func_details['func'](x)
            responses.append({'metric': value})
        return responses
    
    print("\nTest 1: Without metamodel")
    print("-" * 40)
    
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        pop_size=10,
        max_iterations=20,
        metamodel_mode='off'
    )
    
    optimizer.run_optimization()
    
    print(f"Best metric: {optimizer.best_metric:.6e}")
    print(f"Iterations: {optimizer.iter}")
    print(f"Evaluations: {optimizer.nr_evaluations}")
    
    # Test 2: With metamodel (if available)
    print("\nTest 2: With metamodel")
    print("-" * 40)
    
    try:
        optimizer2 = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            opt_min_or_max='min',
            pop_size=10,
            max_iterations=20,
            metamodel_mode='auto'
        )
        
        print("Metamodel created successfully!")
        print("Starting optimization...")
        
        # Add iteration callback to track progress
        def callback(optimizer, **kwargs):
            print(f"  Iteration {optimizer.iter}: best = {optimizer.best_metric:.6e}")
        
        optimizer2.callback_after_each_iter = callback
        optimizer2.run_optimization()
        
        print(f"\nFinal best metric: {optimizer2.best_metric:.6e}")
        print(f"Iterations: {optimizer2.iter}")
        print(f"Evaluations: {optimizer2.nr_evaluations}")
        
        # Print metamodel statistics
        stats = optimizer2.get_metamodel_statistics()
        if stats:
            print("\nMetamodel Statistics:")
            print(f"  Actual evaluations: {stats.get('n_actual_evaluations', 'N/A')}")
            print(f"  Metamodel predictions: {stats.get('n_metamodel_evaluations', 'N/A')}")
            print(f"  Metamodel usage ratio: {stats.get('metamodel_usage_ratio', 0):.2%}")
            
    except ImportError as e:
        print(f"Metamodel not available: {e}")
    except Exception as e:
        print(f"Error with metamodel: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_simple_optimization()
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)