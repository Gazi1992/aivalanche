"""
Example showing how to extend Adam optimizer to support provided gradients.

This demonstrates how the Adam optimizer could be enhanced to accept gradients
directly from the eval_func, which is much more efficient when gradients are
analytically available (e.g., from automatic differentiation).
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional


def modified_estimate_gradient(optimizer):
    """
    Modified gradient estimation that first checks if gradients were provided.
    
    This would replace the _estimate_gradient function in adam/utils.py
    """
    # Check if gradients were provided in the response
    if hasattr(optimizer, 'current_response') and 'gradients' in optimizer.current_response:
        # Use provided gradients
        provided_grads = optimizer.current_response['gradients']
        
        # Convert to numpy array in correct order
        gradient = np.zeros(optimizer.nr_variable_parameters)
        for i, param_name in enumerate(optimizer.variable_parameters_names):
            if param_name in provided_grads:
                # Note: gradients should be in denormalized space
                # We need to transform them to normalized space
                gradient[i] = provided_grads[param_name]
        
        # Transform gradients from denormalized to normalized space if needed
        # This would require the chain rule: grad_norm = grad_denorm * d(denorm)/d(norm)
        # For simplicity, assuming gradients are already in normalized space
        
        return gradient
    
    # Fall back to numerical estimation
    if optimizer.gradient_method == 'finite_difference':
        return _finite_difference_gradient(optimizer)
    elif optimizer.gradient_method == 'simultaneous_perturbation':
        return _simultaneous_perturbation_gradient(optimizer)
    elif optimizer.gradient_method == 'provided':
        raise ValueError("Gradients were expected to be provided but were not found in response")
    else:
        raise ValueError(f"Unknown gradient method: {optimizer.gradient_method}")


def example_eval_func_with_gradients(parameters_df, **kwargs):
    """
    Example evaluation function that provides both metrics and gradients.
    
    This is for optimizing f(x, y) = x^2 + y^2 (simple sphere function)
    where gradients are: df/dx = 2x, df/dy = 2y
    """
    responses = []
    
    for _, row in parameters_df.iterrows():
        x = row['x']
        y = row['y']
        
        # Compute metric
        metric = x**2 + y**2
        
        # Compute analytical gradients
        gradients = {
            'x': 2 * x,
            'y': 2 * y
        }
        
        # Return both metric and gradients
        response = {
            'metric': metric,
            'gradients': gradients  # NEW: Providing gradients directly
        }
        responses.append(response)
    
    return responses


def example_neural_network_eval_func(parameters_df, **kwargs):
    """
    Example showing how this would work with a neural network using automatic differentiation.
    
    In practice, you'd use PyTorch, TensorFlow, or JAX for this.
    """
    responses = []
    
    for _, row in parameters_df.iterrows():
        # Extract neural network weights
        weights = {param: row[param] for param in parameters_df.columns}
        
        # In a real scenario with PyTorch:
        # 1. Convert weights to tensors with requires_grad=True
        # 2. Forward pass through network
        # 3. Compute loss
        # 4. Backward pass to get gradients
        
        # Pseudo-code:
        # model.load_weights(weights)
        # loss = model.forward(training_data)
        # loss.backward()
        # gradients = {param: param.grad for param in model.parameters()}
        
        # For this example, we'll simulate it
        metric = sum(w**2 for w in weights.values())  # Simple L2 regularization as example
        gradients = {param: 2 * weights[param] for param in weights}
        
        response = {
            'metric': metric,
            'gradients': gradients
        }
        responses.append(response)
    
    return responses


def demonstrate_efficiency_gain():
    """
    Demonstrate the efficiency gain from using provided gradients.
    """
    import time
    
    print("=" * 70)
    print("EFFICIENCY COMPARISON: Provided vs Estimated Gradients")
    print("=" * 70)
    
    # Setup a 100-dimensional optimization problem
    n_dim = 100
    param_names = [f'x{i}' for i in range(n_dim)]
    
    # Create a simple quadratic function
    def eval_func_with_gradients(parameters_df, **kwargs):
        responses = []
        for _, row in parameters_df.iterrows():
            values = np.array([row[p] for p in param_names])
            metric = np.sum(values**2)
            gradients = {p: 2 * row[p] for p in param_names}
            responses.append({'metric': metric, 'gradients': gradients})
        return responses
    
    def eval_func_without_gradients(parameters_df, **kwargs):
        responses = []
        for _, row in parameters_df.iterrows():
            values = np.array([row[p] for p in param_names])
            metric = np.sum(values**2)
            responses.append({'metric': metric})
        return responses
    
    # Test point
    test_point = pd.DataFrame([{p: np.random.randn() for p in param_names}])
    
    # Time with provided gradients
    start = time.time()
    for _ in range(10):
        response = eval_func_with_gradients(test_point)
        # Extract gradients directly - 1 function evaluation
    time_provided = time.time() - start
    
    # Time with finite difference (simplified simulation)
    start = time.time()
    for _ in range(10):
        # Finite difference needs 2n evaluations for central difference
        for i in range(n_dim):
            eval_func_without_gradients(test_point)  # Forward
            eval_func_without_gradients(test_point)  # Backward
    time_estimated = time.time() - start
    
    print(f"\nDimensions: {n_dim}")
    print(f"Time with provided gradients: {time_provided:.4f}s (1 evaluation)")
    print(f"Time with finite difference: {time_estimated:.4f}s ({2*n_dim} evaluations)")
    print(f"Speedup: {time_estimated/time_provided:.1f}x faster")
    
    print("\n" + "=" * 70)
    print("KEY BENEFITS OF PROVIDED GRADIENTS:")
    print("=" * 70)
    print("""
1. EFFICIENCY:
   - Finite difference: O(n) evaluations per gradient
   - Simultaneous perturbation: O(1) evaluations but noisy
   - Provided gradients: O(1) with perfect accuracy
   
2. ACCURACY:
   - No numerical errors from finite differences
   - No noise from simultaneous perturbation
   - Exact gradients lead to better convergence
   
3. USE CASES:
   - Neural networks with automatic differentiation
   - Analytical functions with known derivatives
   - Physics simulations with adjoint methods
   - Any differentiable programming scenario
   
4. IMPLEMENTATION:
   To support this in Adam optimizer:
   - Add 'gradient_method': 'provided' option
   - Check for 'gradients' in eval_func response
   - Fall back to estimation if not provided
   - Handle gradient transformation between spaces
    """)


def example_mixed_mode():
    """
    Example showing mixed mode: some parameters with provided gradients, others estimated.
    """
    print("\n" + "=" * 70)
    print("MIXED MODE: Partial Gradient Provision")
    print("=" * 70)
    print("""
Sometimes you might have analytical gradients for some parameters but not others.
For example:
- Continuous parameters: analytical gradients available
- Discrete parameters: no gradients (use finite differences or REINFORCE)
- Black-box components: must estimate gradients

The optimizer could intelligently use provided gradients where available
and estimate the rest, getting the best of both worlds.
    """)
    
    def eval_func_mixed(parameters_df, **kwargs):
        responses = []
        for _, row in parameters_df.iterrows():
            # Continuous parameters with known gradients
            x = row['x_continuous']
            y = row['y_continuous']
            
            # Discrete parameter (no gradient)
            z_discrete = row['z_discrete']
            
            # Black-box function of w
            w = row['w_blackbox']
            blackbox_result = np.sin(w) * np.exp(-w)  # Pretend we don't know the derivative
            
            # Total metric
            metric = x**2 + y**2 + z_discrete**2 + blackbox_result
            
            # Provide gradients only for what we know
            gradients = {
                'x_continuous': 2 * x,
                'y_continuous': 2 * y,
                # 'z_discrete': not provided (will be estimated)
                # 'w_blackbox': not provided (will be estimated)
            }
            
            responses.append({'metric': metric, 'gradients': gradients})
        return responses
    
    print("\nThis mixed approach is particularly useful for:")
    print("- Hybrid continuous/discrete optimization")
    print("- Partially differentiable systems")
    print("- Combining ML models with traditional optimization")


if __name__ == "__main__":
    # Demonstrate the concept
    print("=" * 70)
    print("ENHANCING ADAM OPTIMIZER WITH PROVIDED GRADIENTS")
    print("=" * 70)
    
    # Show efficiency comparison
    demonstrate_efficiency_gain()
    
    # Show mixed mode example
    example_mixed_mode()
    
    print("\n" + "=" * 70)
    print("IMPLEMENTATION NOTES")
    print("=" * 70)
    print("""
To implement this enhancement in the actual Adam optimizer:

1. Modify adam/utils.py:
   - Update _estimate_gradient() to check for provided gradients first
   - Add gradient transformation if needed (denorm to norm space)

2. Modify Adam.__init__():
   - Add 'provided' as a valid gradient_method option
   - Document the expected response format with gradients

3. Update validation:
   - Check gradient dimensions match parameter dimensions
   - Handle missing gradients gracefully

4. Testing:
   - Compare convergence with provided vs estimated gradients
   - Verify gradient transformations are correct
   - Test mixed mode scenarios

This enhancement would make Adam optimizer much more powerful for
modern ML applications where automatic differentiation is standard!
    """)