# Damped Least Squares (Levenberg-Marquardt) Optimizer

## Overview

The Damped Least Squares (DLS) optimizer, also known as the Levenberg-Marquardt algorithm, is a powerful optimization method that combines the Gauss-Newton method with gradient descent. It's particularly effective for:

- **Nonlinear least squares problems**
- **High-sensitivity optimization** (e.g., lens design)
- **Problems with multiple residuals**
- **Situations where good initial guesses are available**

## Key Features

- **Adaptive damping**: Automatically adjusts between Gauss-Newton (fast near minimum) and gradient descent (robust far from minimum)
- **Vector and scalar residuals**: Supports both multi-objective (vector) and single-objective (scalar) optimization
- **Multiple Jacobian methods**: Finite difference, with provisions for complex step and automatic differentiation
- **Boundary handling**: Multiple strategies for parameter constraints
- **QR decomposition**: Optional numerical stability enhancement
- **Trust region**: Optional step size constraints

## Usage

### Basic Example

```python
from aivalanche_lib.optimization.damped_least_squares import DampedLeastSquares
import pandas as pd

# Define parameters
params_df = pd.DataFrame({
    'name': ['x', 'y'],
    'min': [-5.0, -5.0],
    'max': [5.0, 5.0],
    'initial': [2.0, 2.0],
    'variation': ['continuous', 'continuous']
})

# Define evaluation function
def eval_func(parameters, **kwargs):
    results = []
    for _, row in parameters.iterrows():
        x, y = row['x'], row['y']
        # Rosenbrock function
        metric = (1 - x)**2 + 100 * (y - x**2)**2
        results.append({'metric': metric})
    return results

# Create and run optimizer
dls = DampedLeastSquares(
    eval_func=eval_func,
    parameters=params_df,
    max_iterations=100,
    initial_damping=0.01
)

dls.run_optimization()
```

### Lens-like Optimization Example

```python
# For lens optimization with vector residuals
def lens_eval_func(parameters, **kwargs):
    results = []
    for _, row in parameters.iterrows():
        # Extract lens parameters
        c1 = row['curvature_1']
        c2 = row['curvature_2']
        thickness = row['thickness']
        
        # Compute multiple residuals
        residuals = []
        
        # Focal length error
        focal_error = compute_focal_length(c1, c2, thickness) - target_focal
        residuals.append(focal_error)
        
        # Aberration residuals
        for field_point in field_points:
            aberration = compute_aberration(c1, c2, thickness, field_point)
            residuals.append(aberration)
        
        # Total metric is sum of squared residuals
        metric = sum(r**2 for r in residuals)
        
        results.append({
            'metric': metric,
            'residuals': residuals  # Provide individual residuals
        })
    
    return results

# Use with tighter tolerances for lens precision
dls = DampedLeastSquares(
    eval_func=lens_eval_func,
    parameters=lens_params,
    max_iterations=100,
    parameter_tolerance=1e-10,  # Very tight for lens precision
    gradient_tolerance=1e-8,
    initial_damping=0.1,
    jacobian_step_size=1e-8,    # Small steps for sensitivity
    residual_type='vector',      # Use vector residuals
    use_qr_decomposition=True,   # Better numerical stability
    boundary_handling='reflect'  # Keep parameters in bounds
)
```

## Algorithm Parameters

### Core Parameters

#### Damping Parameters (λ control)
- **`initial_damping`** (default: 0.01): Starting value for damping parameter λ
  - Example: `0.01` = balanced start between Gauss-Newton and gradient descent
  - Small values (0.001) = more Gauss-Newton-like (faster but less stable)
  - Large values (1.0) = more gradient descent-like (slower but more stable)

- **`damping_increase_factor`** (default: 10.0): Multiplier when step is rejected
  - Example: If step fails, λ → λ × 10, making algorithm more conservative

- **`damping_decrease_factor`** (default: 0.1): Multiplier when step succeeds
  - Example: If step succeeds, λ → λ × 0.1, making algorithm more aggressive

- **`min_damping`** (default: 1e-10): Lower bound for λ
  - Prevents algorithm from becoming pure Gauss-Newton

- **`max_damping`** (default: 1e10): Upper bound for λ
  - Prevents algorithm from becoming too slow

### Convergence Criteria
- **`max_iterations`** (default: 100): Maximum optimization iterations

- **`metric_threshold`** (default: 0): Stop if metric reaches this value
  - Example: Set to `1e-6` to stop when residual is very small

- **`max_iter_without_improvement`** (default: 20): Stagnation detection

- **`improvement_threshold`** (default: 1e-6): Minimum relative improvement
  - Example: If improvement < 0.0001%, consider it stagnation

- **`gradient_tolerance`** (default: 1e-8): Stop if ||∇f|| < this value
  - Indicates we're at a stationary point

- **`parameter_tolerance`** (default: 1e-8): Stop if ||Δx|| < this value
  - Indicates parameters aren't changing anymore

### Jacobian Computation
- **`jacobian_method`** (default: 'finite_difference'): How to compute derivatives
  - `'finite_difference'`: f'(x) ≈ [f(x+h) - f(x)]/h
  - `'complex_step'`: More accurate using complex arithmetic
  - `'automatic'`: If eval_func provides derivatives

- **`jacobian_step_size`** (default: 1e-6): Step size h for finite differences
  - Too small: numerical errors
  - Too large: inaccurate derivatives

- **`jacobian_step_size_relative`** (default: True): 
  - True: h = x × step_size (scales with parameter)
  - False: h = step_size (absolute)

### Algorithm Options

#### Problem Type
- **`residual_type`** (default: 'scalar'): Defines how your evaluation function returns results
  - `'scalar'`: Single objective f(x) → converts to residual r = √f(x)
  - `'vector'`: Multiple residuals [r₁(x), r₂(x), ...] → minimizes Σrᵢ²

#### Trust Region
- **`trust_region_radius`** (default: None): Maximum step size allowed
  - Example: `0.1` = parameters can't change more than 10% in one step
  - Helps prevent overshooting in sensitive problems

#### Numerical Stability
- **`use_qr_decomposition`** (default: True): 
  - True: Solve (JᵀJ + λI)Δ = -Jᵀr using QR (more stable)
  - False: Solve normal equations directly (faster but less stable)

#### Boundary Handling
- **`boundary_handling`** (default: 'reflect'): How to handle parameter bounds
  - `'reflect'`: If x > max, use 2×max - x (bounce back)
  - `'clip'`: If x > max, use max (stick to boundary)
  - `'penalty'`: Add penalty term for boundary violations

#### Initial Point
- **`initial_point`**: Where to start optimization
  - `'default'`: Use parameter defaults
  - DataFrame: Specific starting values
  - CSV path: Load from file

- **`use_defaults_in_initial_point`** (default: False): 
  - Fill missing values with defaults

## Scalar vs Vector Residuals Explained

### Scalar Residual (`residual_type='scalar'`)
Your evaluation function returns a **single metric/value**. DLS internally converts it to a residual: r = √(metric) and minimizes r² = metric.

**Example 1: Minimizing a simple function**
```python
def eval_func(parameters):
    x = parameters['x']
    y = parameters['y']
    # Single objective: minimize (x-2)² + (y-3)²
    metric = (x - 2)**2 + (y - 3)**2
    return [{'metric': metric}]  # Single value

# DLS will internally work with residual = sqrt(metric)
```

**Example 2: Optimizing a design metric**
```python
def eval_func(parameters):
    length = parameters['length']
    width = parameters['width']
    
    # Single objective: minimize cost
    area = length * width
    perimeter = 2 * (length + width)
    cost = 10 * area + 5 * perimeter  # Single combined metric
    
    return [{'metric': cost}]
```

### Vector Residual (`residual_type='vector'`)
Your evaluation function returns **multiple residuals**. Each residual represents an individual error/difference. DLS minimizes: Σ(rᵢ²) - sum of squared residuals.

**Example 1: Curve fitting (most common use)**
```python
def eval_func(parameters):
    a = parameters['slope']
    b = parameters['intercept']
    
    # Data points to fit
    x_data = [1, 2, 3, 4, 5]
    y_data = [2.1, 3.9, 6.1, 7.8, 10.2]
    
    # Return one residual per data point
    residuals = []
    for x, y in zip(x_data, y_data):
        prediction = a * x + b
        error = prediction - y  # Individual residual
        residuals.append({'residual': error})
    
    return residuals  # List of residuals

# DLS minimizes: (a*1+b-2.1)² + (a*2+b-3.9)² + ... + (a*5+b-10.2)²
```

**Example 2: Multi-objective optimization**
```python
def eval_func(parameters):
    x = parameters['x']
    y = parameters['y']
    
    # Multiple objectives to satisfy simultaneously
    residuals = []
    
    # Objective 1: Want x + y ≈ 10
    residuals.append({'residual': (x + y) - 10})
    
    # Objective 2: Want x² + y² ≈ 50
    residuals.append({'residual': (x**2 + y**2) - 50})
    
    # Objective 3: Want x - y ≈ 2
    residuals.append({'residual': (x - y) - 2})
    
    return residuals  # Multiple residuals

# DLS minimizes: ((x+y)-10)² + ((x²+y²)-50)² + ((x-y)-2)²
```

**Example 3: Fitting model to multiple outputs**
```python
def eval_func(parameters):
    k1 = parameters['k1']
    k2 = parameters['k2']
    
    # Experimental data: inputs and multiple outputs
    inputs = [1, 2, 3, 4]
    outputs_A = [0.5, 1.2, 1.8, 2.3]  # Measured output A
    outputs_B = [1.1, 2.2, 3.1, 3.9]  # Measured output B
    
    residuals = []
    for i, x in enumerate(inputs):
        # Model predictions
        pred_A = k1 * x
        pred_B = k2 * x + 0.1
        
        # Residuals for both outputs
        residuals.append({'residual': pred_A - outputs_A[i]})
        residuals.append({'residual': pred_B - outputs_B[i]})
    
    return residuals  # 8 residuals total (4 inputs × 2 outputs)
```

### Key Differences

1. **Problem Structure**
   - **Scalar**: One combined objective
   - **Vector**: Multiple individual errors/objectives

2. **Mathematical Formulation**
   - **Scalar**: min f(x) where f returns one value
   - **Vector**: min Σrᵢ(x)² where each rᵢ is an individual residual

3. **Jacobian Size**
   - **Scalar**: Jacobian is 1×n (n = number of parameters)
   - **Vector**: Jacobian is m×n (m = number of residuals)

4. **When to Use Each**

   **Use Scalar when:**
   - You have a single objective function
   - Multiple objectives are already combined with weights
   - Optimizing a single performance metric

   **Use Vector when:**
   - Fitting data (each data point = one residual)
   - Multiple objectives that should be satisfied simultaneously
   - Over-determined systems (more equations than unknowns)
   - Want DLS to automatically balance multiple objectives

### Practical Comparison

**Scalar approach (less effective for fitting):**
```python
def eval_func_scalar(parameters):
    a, b = parameters['a'], parameters['b']
    x_data = [1, 2, 3, 4]
    y_data = [2, 4, 6, 8]
    
    # Combine all errors into one metric
    total_error = 0
    for x, y in zip(x_data, y_data):
        error = (a * x + b - y)**2
        total_error += error
    
    return [{'metric': total_error}]  # One combined value
```

**Vector approach (recommended for fitting):**
```python
def eval_func_vector(parameters):
    a, b = parameters['a'], parameters['b']
    x_data = [1, 2, 3, 4]
    y_data = [2, 4, 6, 8]
    
    # Return individual residuals
    residuals = []
    for x, y in zip(x_data, y_data):
        residual = a * x + b - y  # Note: not squared!
        residuals.append({'residual': residual})
    
    return residuals  # List of individual errors
```

The vector approach is better because:
1. DLS can use the structure of individual residuals
2. The Jacobian captures how each parameter affects each data point
3. More numerically stable
4. Better convergence properties

## Understanding Tolerance Parameters

The DLS algorithm uses three tolerance parameters to determine when to stop optimization:

### 1. **Gradient Tolerance** (`gradient_tolerance`)
- **What it checks**: ||∇f|| < gradient_tolerance
- **Meaning**: The norm (magnitude) of the gradient vector
- **When triggered**: When the gradient becomes very small, indicating we're at a stationary point (minimum, maximum, or saddle point)
- **Example**: If gradient_tolerance = 1e-8 and ||∇f|| = 5e-9, optimization stops

```python
# For scalar problems: gradient is a vector of partial derivatives
gradient = [∂f/∂x₁, ∂f/∂x₂, ..., ∂f/∂xₙ]
gradient_norm = sqrt(sum(g² for g in gradient))

# For vector problems: gradient is Jᵀr where J is Jacobian, r is residuals
gradient = Jᵀ @ residuals
gradient_norm = sqrt(sum(g² for g in gradient))
```

### 2. **Parameter Tolerance** (`parameter_tolerance`)
- **What it checks**: ||Δx|| < parameter_tolerance
- **Meaning**: The norm of the parameter update step
- **When triggered**: When parameters stop changing significantly between iterations
- **Example**: If parameter_tolerance = 1e-8 and the step size = 3e-9, optimization stops

```python
# The step is computed by solving: (JᵀJ + λI)Δx = -Jᵀr
step_norm = sqrt(sum(δ² for δ in parameter_updates))
```

### 3. **Improvement Threshold** (`improvement_threshold`)
- **What it checks**: relative_improvement < improvement_threshold
- **Meaning**: The relative change in the objective function
- **When triggered**: When the objective isn't improving significantly
- **Works with**: `max_iter_without_improvement` counter

```python
relative_improvement = abs(current_metric - previous_metric) / abs(previous_metric)
if relative_improvement < improvement_threshold:
    iter_without_improvement += 1
```

### How They Work Together

The algorithm stops when ANY of these conditions is met:
1. Gradient norm < gradient_tolerance (at a stationary point)
2. Step norm < parameter_tolerance (parameters converged)
3. No improvement for max_iter_without_improvement iterations
4. Metric reaches metric_threshold
5. Maximum iterations reached

### Typical Values

**High Precision (e.g., lens design):**
```python
gradient_tolerance=1e-10
parameter_tolerance=1e-10
improvement_threshold=1e-8
```

**Standard Precision:**
```python
gradient_tolerance=1e-8
parameter_tolerance=1e-8
improvement_threshold=1e-6
```

**Fast but Less Precise:**
```python
gradient_tolerance=1e-6
parameter_tolerance=1e-6
improvement_threshold=1e-4
```

## Providing Gradients to eval_func

Currently, DLS computes gradients numerically using finite differences. However, the framework supports providing analytical gradients for better performance:

### Automatic Differentiation (Future Feature)
When `jacobian_method='automatic'` is implemented, the eval_func would return gradients like this:

**For Scalar Problems:**
```python
def eval_func_with_gradient(parameters):
    x = parameters['x']
    y = parameters['y']
    
    # Compute objective
    f = (x - 2)**2 + (y - 3)**2
    
    # Compute gradient analytically
    df_dx = 2 * (x - 2)
    df_dy = 2 * (y - 3)
    
    return [{
        'metric': f,
        'gradient': [df_dx, df_dy]  # Order must match parameter order
    }]
```

**For Vector Problems:**
```python
def eval_func_with_jacobian(parameters):
    a = parameters['slope']
    b = parameters['intercept']
    
    x_data = [1, 2, 3]
    y_data = [2, 4, 6]
    
    residuals = []
    jacobian = []  # Will be m×n matrix
    
    for x, y in zip(x_data, y_data):
        # Residual
        r = a * x + b - y
        residuals.append({'residual': r})
        
        # Jacobian row: [∂r/∂a, ∂r/∂b]
        dr_da = x  # Derivative w.r.t. slope
        dr_db = 1  # Derivative w.r.t. intercept
        jacobian.append([dr_da, dr_db])
    
    # Return with Jacobian (not yet implemented)
    return residuals, {'jacobian': jacobian}
```

**Note**: Currently, only `finite_difference` is implemented. The `automatic` and `complex_step` methods are placeholders for future development.

## Theory

The DLS algorithm solves the optimization problem by iteratively updating parameters using:

```
(J^T J + λI) δ = -J^T r
```

Where:
- `J` is the Jacobian matrix
- `r` is the residual vector
- `λ` is the damping parameter
- `δ` is the parameter update step

The damping parameter λ adaptively controls the algorithm's behavior:
- **λ → 0**: Behaves like Gauss-Newton (fast quadratic convergence near minimum)
- **λ → ∞**: Behaves like gradient descent (robust but slower)

## Example Configurations

### Robust General Purpose
```python
DampedLeastSquares(
    initial_damping=0.01,
    damping_increase_factor=10.0,
    damping_decrease_factor=0.1,
    gradient_tolerance=1e-8,
    parameter_tolerance=1e-8
)
```

### Fast but Less Stable
```python
DampedLeastSquares(
    initial_damping=0.001,  # Start aggressive
    damping_increase_factor=5.0,  # Less conservative on failure
    damping_decrease_factor=0.2,  # Less aggressive on success
    trust_region_radius=0.5  # But limit step size
)
```

### Very Stable for Sensitive Problems
```python
DampedLeastSquares(
    initial_damping=1.0,  # Start conservative
    damping_increase_factor=20.0,  # Very conservative on failure
    min_damping=0.01,  # Don't get too aggressive
    trust_region_radius=0.1,  # Small steps
    boundary_handling='penalty'  # Smooth boundary behavior
)
```

### Curve Fitting (Vector Residuals)
```python
DampedLeastSquares(
    residual_type='vector',
    jacobian_method='finite_difference',
    jacobian_step_size=1e-6,
    use_qr_decomposition=True  # Important for overdetermined systems
)
```

## Comparison with Other Optimizers

### vs. Differential Evolution
- **DLS**: Fast local convergence, requires good initial guess
- **DE**: Global search, slower but doesn't need good initial guess
- **Use DLS when**: Problem is smooth and you have a reasonable starting point

### vs. Nelder-Mead
- **DLS**: Uses gradient information, faster convergence
- **Nelder-Mead**: Derivative-free, more robust to noise
- **Use DLS when**: Gradients can be computed accurately

### vs. Adam
- **DLS**: Better for least squares problems, adaptive damping
- **Adam**: Better for stochastic/noisy gradients
- **Use DLS when**: You have deterministic function evaluations

## Tips for Lens Optimization

1. **Use vector residuals**: Provide individual aberration terms as residuals
2. **Set tight tolerances**: Lens design requires high precision (1e-8 to 1e-10)
3. **Small Jacobian steps**: Use very small step sizes (1e-6 to 1e-8) due to high sensitivity
4. **Boundary handling**: Use 'reflect' to keep parameters physically reasonable
5. **Multi-stage optimization**: Consider DE → DLS for global → local optimization

## Visualization

The optimizer provides several plotting methods:

```python
# Plot optimization progress
dls.plot_metrics()

# Plot damping factor evolution
dls.plot_damping()

# Plot residuals evolution (for vector case)
dls.plot_residuals()

# Plot parameter evolution
dls.plot_parameters(['param1', 'param2'])
```

## References

1. Levenberg, K. (1944). "A method for the solution of certain non-linear problems in least squares"
2. Marquardt, D. (1963). "An Algorithm for Least-Squares Estimation of Nonlinear Parameters"
3. Moré, J. J. (1978). "The Levenberg-Marquardt algorithm: Implementation and theory"