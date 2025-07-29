# Nelder-Mead (Simplex) Optimizer

## Overview

The Nelder-Mead method, also known as the downhill simplex method, is a direct search optimization algorithm for multidimensional unconstrained optimization. Developed by John Nelder and Roger Mead in 1965, it is one of the most widely used derivative-free optimization methods.

## How Nelder-Mead Works

### Basic Principles

The algorithm maintains a simplex - a geometric figure consisting of n+1 vertices in n-dimensional space (e.g., a triangle in 2D, a tetrahedron in 3D). The simplex evolves through a series of geometric transformations to find the optimum.

### Algorithm Steps

1. **Initialization**: Create an initial simplex with n+1 vertices
2. **For each iteration**:
   - **Order**: Sort vertices by function value (best to worst)
   - **Centroid**: Calculate the centroid of all vertices except the worst
   - **Reflection**: Reflect the worst vertex through the centroid
   - **Expansion**: If reflection is best so far, try expanding further
   - **Contraction**: If reflection is poor, contract the simplex
   - **Shrink**: If all else fails, shrink the entire simplex toward the best vertex
3. **Termination**: Stop when simplex becomes sufficiently small

### Simplex Operations

- **Reflection**: xr = xc + α(xc - xw), typically α = 1
- **Expansion**: xe = xc + γ(xr - xc), typically γ = 2
- **Contraction**: xc = xc + ρ(xw - xc), typically ρ = 0.5
- **Shrink**: xi = xb + σ(xi - xb), typically σ = 0.5

Where:
- xw = worst vertex
- xb = best vertex
- xc = centroid
- xr, xe, xc = reflected, expanded, contracted points

### Key Features

- **Derivative-free**: No gradient information required
- **Robust**: Works on non-smooth, noisy functions
- **Simple**: Easy to implement and understand
- **Local search**: Good for refinement, may get stuck in local minima
- **Geometric**: Based on simplex transformations

## Using the NelderMead Class

### Basic Usage

```python
from aivalanche_lib.optimization.nelder_mead import NelderMead
from aivalanche_lib.parameters import Parameters

# Define your evaluation function
def eval_func(parameters_df, **kwargs):
    """
    Evaluate a set of parameters.
    
    Args:
        parameters_df: DataFrame with parameter values
        **kwargs: Additional arguments
    
    Returns:
        list: List of dictionaries with 'metric' key
    """
    responses = []
    for _, row in parameters_df.iterrows():
        # Your evaluation logic here
        metric = some_calculation(row['param1'], row['param2'])
        responses.append({'metric': metric})
    return responses

# Define parameters
param_config = [
    {'name': 'param1', 'min': -5.0, 'max': 5.0, 'default': 0.0, 'mode': 'variable', 'type': 'continuous'},
    {'name': 'param2', 'min': -5.0, 'max': 5.0, 'default': 0.0, 'mode': 'variable', 'type': 'continuous'}
]

# Create and run optimizer
optimizer = NelderMead(
    eval_func=eval_func,
    parameters=Parameters(param_config),
    opt_min_or_max='min',
    max_iterations=100,
    simplex_edge_length=0.5
)

optimizer.run_optimization()

# Access results
print(f"Best metric: {optimizer.best_metric}")
print(f"Best parameters: {optimizer.best_parameters}")
```

### Advanced Features

#### 1. Simplex Initialization

```python
# Method 1: Specify initial point
initial_point = pd.DataFrame({'param1': [1.0], 'param2': [2.0]})
optimizer = NelderMead(
    # ... other parameters ...
    initial_point=initial_point,
    initial_point_mode='corner',  # or 'center'
    initial_simplex_edge_length=0.5
)

# Method 2: Provide complete initial simplex
initial_simplex = pd.DataFrame({
    'param1': [0.0, 1.0, 0.5],
    'param2': [0.0, 0.0, 1.0]
})
optimizer = NelderMead(
    # ... other parameters ...
    initial_simplex=initial_simplex
)

# Method 3: Use defaults
optimizer = NelderMead(
    # ... other parameters ...
    use_defaults_in_initial_point=True
)
```

#### 2. Algorithm Parameters

```python
optimizer = NelderMead(
    # ... other parameters ...
    alpha=1.0,    # Reflection coefficient
    gamma=2.0,    # Expansion coefficient
    rho=0.5,      # Contraction coefficient
    sigma=0.5,    # Shrink coefficient
    adaptive_parameters=True  # Auto-adapt coefficients
)
```

#### 3. Stopping Criteria

```python
optimizer = NelderMead(
    # ... other parameters ...
    max_iterations=200,
    metric_threshold=1e-6,
    patience=50,
    improvement_threshold=1e-4,
    min_simplex_size_abs=1e-8,
    min_simplex_size_rel=1e-8
)
```

#### 4. Callbacks

```python
def callback_each_iter(**kwargs):
    print(f"Iteration {kwargs['iteration']}: Best = {kwargs['best_metric']}")
    print(f"Simplex size: {kwargs['optimizer'].get_simplex_size()}")

optimizer = NelderMead(
    # ... other parameters ...
    callback_after_each_iter=callback_each_iter
)
```

#### 5. Boundary Handling

```python
optimizer = NelderMead(
    # ... other parameters ...
    ensure_feasibility=True,  # Keep simplex within bounds
    reflect_at_bounds=True    # Special reflection at boundaries
)
```

### Visualization and Analysis

```python
# Plot metrics evolution
fig, ax = optimizer.plot_metrics()

# Plot simplex evolution (for 2D problems)
fig, ax = optimizer.plot_simplex_evolution(iterations=[0, 10, 20, 50])

# Create animation (for 2D problems)
anim = optimizer.create_simplex_animation(save_path='nm_animation.gif')

# Plot final simplex
fig, ax = optimizer.plot_final_simplex()

# Save results
optimizer.write_best_parameters_to_file('best_params.csv')
optimizer.write_optimization_info_to_file('opt_info.json')
optimizer.write_history_to_file(which='simplexes', file_path='simplex_history.csv')
```

### Restarting and Warm Starts

```python
# Save state after first run
best_params = optimizer.best_parameters

# Create new optimizer with warm start
optimizer2 = NelderMead(
    # ... same parameters ...
    initial_point=pd.DataFrame([best_params]),
    initial_simplex_edge_length=0.1  # Smaller simplex for refinement
)
optimizer2.run_optimization()
```

## Parameter Guidelines

### Initial Simplex Size
- Large simplex: Better exploration, slower convergence
- Small simplex: Faster local convergence, may miss global optimum
- Typical: 5-20% of parameter range

### Transformation Coefficients
- **α (reflection)**: Standard value 1.0, rarely changed
- **γ (expansion)**: 2.0 for aggressive search, 1.5-3.0 range
- **ρ (contraction)**: 0.5 standard, 0.25-0.75 range
- **σ (shrink)**: 0.5 standard, rarely changed

### Adaptive Parameters
- Enable for difficult problems with varying landscape
- Coefficients adjust based on success rates
- Can improve robustness but may slow convergence

## When to Use Nelder-Mead

**Good for:**
- Low to medium dimensional problems (< 20 parameters)
- Non-smooth or noisy objective functions
- When derivatives are unavailable or unreliable
- Local optimization or refinement
- Quick initial exploration
- Problems with discontinuities

**Not ideal for:**
- High-dimensional problems (degrades above 10-20 dimensions)
- Highly multimodal functions (gets stuck in local optima)
- When high precision is required
- Problems where function evaluations are very expensive
- When gradient information is readily available

## Common Issues and Solutions

1. **Premature convergence**: 
   - Increase initial simplex size
   - Use multiple restarts from different points
   - Relax convergence tolerances

2. **Slow convergence**:
   - Reduce initial simplex size if near optimum
   - Enable adaptive parameters
   - Check for flat regions in objective function

3. **Degenerate simplex**:
   - Monitor simplex condition number
   - Restart if simplex becomes too flat
   - Use minimum simplex size criteria

4. **Boundary issues**:
   - Enable boundary reflection
   - Use penalty methods for constraints
   - Consider transformation of variables

## Algorithm Variants

1. **Adaptive Nelder-Mead**: Adjusts coefficients during optimization
2. **Nelder-Mead with restarts**: Multiple runs from different starting points
3. **Constrained Nelder-Mead**: Extensions for bounded/constrained problems
4. **Parallel Nelder-Mead**: Evaluates multiple vertices simultaneously

## Tips for Effective Use

1. **Multi-start strategy**: Run from multiple initial points for global search
2. **Hybrid approach**: Use with global optimizer for refinement
3. **Parameter scaling**: Normalize parameters to similar ranges
4. **Monitor convergence**: Track simplex size and function values
5. **Appropriate tolerances**: Set based on problem requirements

## References

1. Nelder, J. A., & Mead, R. (1965). A simplex method for function minimization.
2. Lagarias, J. C., et al. (1998). Convergence properties of the Nelder–Mead simplex method in low dimensions.
3. Gao, F., & Han, L. (2012). Implementing the Nelder-Mead simplex algorithm with adaptive parameters.