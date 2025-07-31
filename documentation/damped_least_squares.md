# Damped Least Squares (DLS) Optimizer

## Table of Contents

1. [Introduction](#introduction)
2. [Algorithm Overview](#algorithm-overview)
3. [Mathematical Foundation](#mathematical-foundation)
4. [Implementation Details](#implementation-details)
5. [Parameters Reference](#parameters-reference)
6. [Advanced Features](#advanced-features)
7. [Usage Examples](#usage-examples)
8. [Best Practices](#best-practices)

## 1. Introduction {#introduction}

The Damped Least Squares (DLS) algorithm, also known as the Levenberg-Marquardt algorithm, is a powerful optimization method that combines the Gauss-Newton method with gradient descent. It is particularly effective for nonlinear least squares problems and sensitivity-dependent optimization tasks.

### Key Characteristics

- **Hybrid approach**: Combines Gauss-Newton and gradient descent
- **Adaptive damping**: Automatically adjusts between methods
- **Fast convergence**: Quadratic convergence near optimum
- **Robust**: Handles ill-conditioned problems well

### When to Use DLS

DLS is ideal for:
- Nonlinear least squares problems
- Parameter estimation
- Curve fitting
- Sensitive optimization (e.g., lens design)
- Problems where Jacobian can be computed

## 2. Algorithm Overview {#algorithm-overview}

The DLS algorithm operates through these main steps:

1. **Evaluate** current point and residuals
2. **Compute** Jacobian matrix
3. **Solve** damped normal equations for step
4. **Update** position if improvement
5. **Adjust** damping parameter
6. **Repeat** until convergence

### Key Innovation

The algorithm dynamically adjusts between:
- **Gauss-Newton** (λ → 0): Fast quadratic convergence
- **Gradient Descent** (λ → ∞): Guaranteed descent

## 3. Mathematical Foundation {#mathematical-foundation}

### Problem Formulation

For a least squares problem, minimize:

$$f(x) = \frac{1}{2} \sum_{i=1}^{m} r_i(x)^2 = \frac{1}{2} ||r(x)||^2$$

Where $r(x)$ is the residual vector.

### Jacobian Matrix

The Jacobian $J$ contains partial derivatives:

$$J_{ij} = \frac{\partial r_i}{\partial x_j}$$

### Damped Normal Equations

The step $p$ is computed by solving:

$$(J^T J + \lambda I) p = -J^T r$$

Where:
- $J$ is the Jacobian matrix
- $\lambda$ is the damping parameter
- $I$ is the identity matrix
- $r$ is the residual vector

### Damping Parameter Update

The damping parameter λ is updated based on the gain ratio:

$$\rho = \frac{f(x) - f(x + p)}{L(0) - L(p)}$$

Where $L(p)$ is the linear model prediction.

- If $\rho > 0$ (improvement): Accept step, decrease λ
- If $\rho \leq 0$ (no improvement): Reject step, increase λ

## 4. Implementation Details {#implementation-details}

### Class Structure

```python
class DampedLeastSquares:
    def __init__(self,
                 seed: Optional[int] = None,
                 eval_func: Optional[Callable] = None,
                 parameters: Optional[Union[Parameters, str, pd.DataFrame]] = None,
                 opt_min_or_max: str = 'min',
                 max_iterations: int = 100,
                 metric_threshold: float = 0,
                 gradient_tolerance: float = 1e-8,
                 parameter_tolerance: float = 1e-8,
                 initial_damping: float = 0.01,
                 damping_increase_factor: float = 10.0,
                 damping_decrease_factor: float = 0.1,
                 min_damping: float = 1e-10,
                 max_damping: float = 1e10,
                 jacobian_method: str = 'finite_difference',
                 jacobian_step_size: float = 1e-6,
                 jacobian_step_size_relative: bool = True,
                 initial_point: Optional[Union[str, pd.DataFrame]] = None,
                 residual_type: str = 'scalar',
                 use_qr_decomposition: bool = True,
                 boundary_handling: str = 'reflect',
                 results_dir: Optional[str] = None)
```

### Residual Types

The algorithm supports two residual formulations:

1. **Scalar**: Single objective value
   - Artificial residual created as $r = \sqrt{|f(x)|}$
   - Simpler but less information

2. **Vector**: Multiple residuals
   - True least squares formulation
   - Better convergence properties
   - More information for algorithm

## 5. Parameters Reference {#parameters-reference}

### Convergence Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_iterations` | int | 100 | Maximum number of iterations |
| `metric_threshold` | float | 0 | Stop if metric below threshold |
| `gradient_tolerance` | float | 1e-8 | Stop if gradient norm below threshold |
| `parameter_tolerance` | float | 1e-8 | Stop if parameter change below threshold |
| `max_iter_without_improvement` | int | 20 | Stop after no improvement |

### Damping Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `initial_damping` | float | 0.01 | Starting damping value λ₀ |
| `damping_increase_factor` | float | 10.0 | Factor to increase λ on failure |
| `damping_decrease_factor` | float | 0.1 | Factor to decrease λ on success |
| `min_damping` | float | 1e-10 | Minimum allowed λ |
| `max_damping` | float | 1e10 | Maximum allowed λ |

### Jacobian Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `jacobian_method` | str | 'finite_difference' | Method for Jacobian computation |
| `jacobian_step_size` | float | 1e-6 | Step size for finite differences |
| `jacobian_step_size_relative` | bool | True | Use relative step size |

### Algorithm Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `residual_type` | str | 'scalar' | 'scalar' or 'vector' residuals |
| `use_qr_decomposition` | bool | True | Use QR for numerical stability |
| `boundary_handling` | str | 'reflect' | 'reflect', 'clip', or 'penalty' |
| `trust_region_radius` | float | None | Optional trust region constraint |

## 6. Advanced Features {#advanced-features}

### Adaptive Damping Strategy

The damping parameter λ adapts based on step success:

```
if step_accepted:
    λ = λ * damping_decrease_factor
else:
    λ = λ * damping_increase_factor
```

This provides:
- Fast convergence when near optimum (small λ)
- Robust progress in difficult regions (large λ)

### QR Decomposition

For numerical stability, the implementation can use QR decomposition:

```python
# Instead of solving (J^T J + λI) p = -J^T r
# Solve using QR of augmented system:
[J     ] [p] = [-r]
[√λ I  ] [ ] = [0 ]
```

Benefits:
- Better numerical conditioning
- More stable for ill-conditioned problems
- Slightly higher computational cost

### Boundary Handling

Three strategies for parameter bounds:

1. **Reflect**: Bounce off boundaries
   ```python
   if x < lower:
       x = 2*lower - x
   ```

2. **Clip**: Project onto boundaries
   ```python
   x = clip(x, lower, upper)
   ```

3. **Penalty**: Add penalty for violations
   ```python
   penalty = α * max(0, lower-x)² + α * max(0, x-upper)²
   ```

### Initial Point Options

Flexible initialization:
- `initial_point='default'`: Use parameter defaults
- `initial_point=DataFrame`: Specific starting point
- `initial_point='path/to/file.csv'`: Load from file
- `initial_point=None`: Random initialization

## 7. Usage Examples {#usage-examples}

### Basic Least Squares

```python
from aivalanche_lib.optimization.damped_least_squares import DampedLeastSquares

def rosenbrock_residuals(parameters, **kwargs):
    results = []
    for _, row in parameters.iterrows():
        x, y = row['x'], row['y']
        # Rosenbrock as sum of squares
        r1 = 1 - x
        r2 = 10 * (y - x**2)
        results.append({
            'metric': r1**2 + r2**2,
            'residuals': [r1, r2]
        })
    return results

# Create optimizer
dls = DampedLeastSquares(
    eval_func=rosenbrock_residuals,
    parameters=params_df,
    residual_type='vector',
    initial_damping=0.1
)

dls.run_optimization()
```

### Curve Fitting

```python
def curve_fit_residuals(parameters, x_data, y_data, **kwargs):
    results = []
    for _, row in parameters.iterrows():
        a, b, c = row['a'], row['b'], row['c']
        # Model: y = a * exp(b * x) + c
        y_pred = a * np.exp(b * x_data) + c
        residuals = y_data - y_pred
        results.append({
            'metric': np.sum(residuals**2),
            'residuals': residuals.tolist()
        })
    return results

dls = DampedLeastSquares(
    eval_func=lambda p, **k: curve_fit_residuals(p, x_data, y_data, **k),
    parameters=params_df,
    residual_type='vector',
    jacobian_step_size=1e-8,
    initial_point='default'
)
```

### Sensitive Optimization (Lens Design)

```python
# For highly sensitive problems
dls = DampedLeastSquares(
    eval_func=lens_merit_function,
    parameters=lens_params,
    residual_type='vector',
    initial_damping=0.001,          # Start with low damping
    damping_increase_factor=2.0,    # Gentle increases
    damping_decrease_factor=0.7,    # Conservative decreases
    jacobian_step_size=1e-10,       # Very small for sensitivity
    jacobian_step_size_relative=True,
    use_qr_decomposition=True,      # For stability
    boundary_handling='reflect'
)
```

## 8. Best Practices {#best-practices}

### Choosing Residual Type

**Use Vector Residuals when**:
- You have natural residuals (fitting, estimation)
- Problem is truly least squares
- You need better convergence

**Use Scalar Residuals when**:
- Simple optimization problem
- No natural residual decomposition
- Quick implementation needed

### Damping Strategy Selection

**Conservative** (High sensitivity):
```python
initial_damping=1.0
damping_increase_factor=5.0
damping_decrease_factor=0.2
```

**Moderate** (Balanced):
```python
initial_damping=0.1
damping_increase_factor=2.0
damping_decrease_factor=0.5
```

**Aggressive** (Fast convergence):
```python
initial_damping=0.001
damping_increase_factor=1.5
damping_decrease_factor=0.8
```

### Jacobian Computation

**Step Size Guidelines**:
- Absolute: `1e-6` to `1e-8` typically
- Relative: `1e-8` to `1e-10` for sensitive problems
- Use relative for parameters with different scales

**Improving Jacobian Accuracy**:
1. Use appropriate step size
2. Check for numerical noise
3. Consider central differences (future feature)
4. Analytical Jacobian if available

### Convergence Criteria

Set multiple criteria for robustness:
```python
gradient_tolerance=1e-8      # Small gradient
parameter_tolerance=1e-10    # Small steps
metric_threshold=1e-12       # Target accuracy
max_iter_without_improvement=20  # Stagnation check
```

### Common Issues and Solutions

**Slow Convergence**:
- Decrease initial damping
- Check Jacobian accuracy
- Use vector residuals if possible

**Oscillations**:
- Increase damping factors
- Use trust region
- Check for numerical issues

**Getting Stuck**:
- Adjust damping strategy
- Check parameter scaling
- Consider different initial point

### Performance Tips

1. **Preconditioning**: Scale parameters to similar ranges
2. **Warm Starting**: Use previous solution as initial point
3. **Jacobian Reuse**: Cache if expensive (future feature)
4. **Parallel Evaluation**: Batch Jacobian computations

### When DLS Excels

Best for problems with:
- Smooth objective functions
- Available derivatives (or finite differences work)
- Moderate dimensionality (< 1000 parameters)
- Least squares structure
- Need for high accuracy

### When to Use Other Methods

Consider alternatives when:
- Very high dimensional (use L-BFGS)
- No smooth derivatives (use Nelder-Mead)
- Global optimization needed (use DE)
- Stochastic objectives (use ADAM)

### Hybrid Approaches

Combine with other methods:
```python
# 1. Global search with DE
de = DifferentialEvolution(...)
de.run_optimization()

# 2. Local refinement with DLS
dls = DampedLeastSquares(
    initial_point=pd.DataFrame([de.best_parameters]),
    ...
)
dls.run_optimization()
```

This leverages global exploration and local refinement.
