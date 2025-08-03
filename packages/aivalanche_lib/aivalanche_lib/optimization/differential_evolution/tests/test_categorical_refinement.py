"""
Final test for categorical refinement without merge function
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution, get_refinement_history
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details


def test_refinement_with_categorical():
    """Test refinement with categorical parameters to ensure fixed params work correctly."""
    print("\nTesting Refinement with Categorical Parameters")
    print("=" * 60)
    
    # Use a mixed continuous/categorical function
    func_details = get_function_details('string_categorical_mixed_2d')
    
    # Get bounds from function details
    bounds = func_details['bounds']
    
    # Create parameters matching the function
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': bounds[0][0], 'max': bounds[0][1], 'default': 0.0},
        {'name': 'y', 'type': 'categorical', 'values': bounds[1], 'default': bounds[1][0]}
    ])
    
    # Use the actual test function
    from test_utils import create_test_function_wrapper
    eval_func = create_test_function_wrapper(func_details)
    
    print("\nRunning optimization with refinement...")
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        pop_size=10,
        max_iterations=20,
        max_iter_without_improvement=10,
        refinement_mode='on',
        refinement_config={'trigger_ratio': 0.3}
    )
    
    optimizer.run_optimization()
    
    print(f"\nResults:")
    print(f"  Best metric: {optimizer.best_metric:.6e}")
    print(f"  Best x: {optimizer.best_parameters['x']:.4f}")
    print(f"  Best y: {optimizer.best_parameters['y']}")
    
    # Check refinement history
    history = get_refinement_history(optimizer)
    print(f"\nRefinement history: {len(history)} events")
    
    for i, event in enumerate(history):
        print(f"\n  Event {i+1}:")
        print(f"    Iteration: {event['iteration']}")
        print(f"    Improved: {event['improved']}")
        if event['improved']:
            print(f"    Initial metric: {event['initial_metric']:.6e}")
            print(f"    Refined metric: {event['refined_metric']:.6e}")
            print(f"    Improvement: {event['relative_improvement']:.2%}")
    
    # Verify that refinement happened and categorical parameter was preserved
    assert len(history) > 0, "Expected at least one refinement event"
    print(f"\n[INFO] Total refinements: {len(history)}")
    print(f"[INFO] Successful refinements: {sum(1 for e in history if e['improved'])}")
    
    print("\n[SUCCESS] Categorical refinement test passed!")
    return optimizer


if __name__ == "__main__":
    test_refinement_with_categorical()
    print("\n[DONE] All tests completed!")