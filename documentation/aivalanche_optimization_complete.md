---
title: "AIvalanche Optimization Algorithms - Comprehensive Documentation"
author: "AIvalanche Library"
date: "July 30, 2025"
---

# AIvalanche Optimization Library Documentation

This comprehensive documentation covers all optimization algorithms available in the AIvalanche library.


\newpage

# Differential Evolution (DE) Optimizer

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

Differential Evolution (DE) is a powerful metaheuristic optimization algorithm that belongs to the family of evolutionary algorithms. It was proposed by Storn and Price in 1997 and has since become one of the most popular global optimization methods due to its simplicity, robustness, and effectiveness.

### Key Characteristics

- **Population-based**: Works with a population of candidate solutions
- **Stochastic**: Uses random mutations and crossovers
- **Derivative-free**: Does not require gradient information
- **Global optimization**: Capable of finding global optima in multimodal landscapes

## 2. Algorithm Overview {#algorithm-overview}

The DE algorithm operates through the following main steps:

1. **Initialization**: Generate initial population
2. **Mutation**: Create mutant vectors
3. **Crossover**: Combine mutant with target vectors
4. **Selection**: Choose better solutions
5. **Repeat** until convergence

### Population Structure

The algorithm maintains a population of `pop_size` individuals, where each individual represents a potential solution in the parameter space.

## 3. Mathematical Foundation {#mathematical-foundation}

### Mutation Operation

The mutation operation creates a mutant vector $v_i$ for each target vector $x_i$ in the population:

$$v_i = x_{r1} + F_1 \cdot (x_{r2} - x_{r3}) + F_2 \cdot (x_{best} - x_{r1})$$

Where:
- $x_{r1}, x_{r2}, x_{r3}$ are randomly selected distinct individuals
- $x_{best}$ is the best individual in the current population
- $F_1$ is `mutation_factor_1` (differential weight)
- $F_2$ is `mutation_factor_2` (best individual weight)

### Crossover Operation

The trial vector $u_i$ is created through binomial crossover:

$$u_{i,j} = \begin{cases}
v_{i,j} & \text{if } rand() < CR \text{ or } j = j_{rand} \\
x_{i,j} & \text{otherwise}
\end{cases}$$

Where:
- $CR$ is `recombination_factor` (crossover probability)
- $j_{rand}$ ensures at least one parameter is mutated

### Selection Operation

The selection is greedy:

$$x_i^{new} = \begin{cases}
u_i & \text{if } f(u_i) \leq f(x_i) \\
x_i & \text{otherwise}
\end{cases}$$

## 4. Implementation Details {#implementation-details}

### Class Structure

```python
class DifferentialEvolution:
    def __init__(self,
                 seed: Optional[int] = None,
                 eval_func: Optional[Callable] = None,
                 parameters: Optional[Union[Parameters, str, pd.DataFrame]] = None,
                 opt_min_or_max: str = 'min',
                 pop_size: int = 50,
                 max_iterations: int = 100,
                 metric_threshold: float = 0,
                 max_iter_without_improvement: int = 20,
                 mutation_factor_1: Union[float, Tuple[float, float]] = (0.5, 1.0),
                 mutation_factor_2: Union[float, Tuple[float, float]] = (0.0, 0.5),
                 recombination_factor: Union[float, Tuple[float, float]] = (0.7, 0.9),
                 perturbation_mode: str = 'off',
                 perturbation_config: Optional[Dict[str, Any]] = None,
                 initial_population: Optional[str] = None,
                 results_dir: Optional[str] = None)
```

### Population Initialization

The algorithm supports multiple initialization strategies:

1. **Random**: Uniform random sampling within bounds
2. **Latin Hypercube Sampling (LHS)**: Better space coverage
3. **Halton Sequence**: Low-discrepancy sequence for uniform coverage
4. **Custom**: Load from file or DataFrame

## 5. Parameters Reference {#parameters-reference}

### Core Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pop_size` | int | 50 | Population size. Larger populations explore more thoroughly but require more evaluations |
| `max_iterations` | int | 100 | Maximum number of generations |
| `metric_threshold` | float | 0 | Stop if best metric reaches this threshold |
| `max_iter_without_improvement` | int | 20 | Stop if no improvement for this many iterations |

### Evolution Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mutation_factor_1` | float or tuple | (0.5, 1.0) | Differential weight F1. Controls mutation step size |
| `mutation_factor_2` | float or tuple | (0.0, 0.5) | Best vector weight F2. Controls influence of best solution |
| `recombination_factor` | float or tuple | (0.7, 0.9) | Crossover probability CR. Higher values mean more mutation |

**Note**: When using tuples, the algorithm randomly samples within the range for each operation, providing adaptive behavior.

### Perturbation Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `perturbation_mode` | str | 'off' | Perturbation strategy: 'off', 'auto', 'aggressive', 'conservative', 'custom' |
| `perturbation_config` | dict | None | Custom perturbation configuration |

## 6. Advanced Features {#advanced-features}

### Adaptive Perturbation System

The perturbation feature helps escape local minima by intelligently perturbing stagnant parameters.

#### How It Works

1. **Detection**: Monitors parameter variance and convergence
2. **Selection**: Identifies parameters to perturb based on:
   - Low variance (stuck parameters)
   - High correlation with objective
   - Historical effectiveness
3. **Application**: Applies scaled perturbations
4. **Memory**: Tracks effectiveness with cooldown periods

#### Perturbation Modes

**Auto Mode** (Recommended):
```python
perturbation_mode='auto'
```
- Triggers at 30% of max iterations without improvement
- Perturbs 20% of parameters
- Moderate perturbation scale

**Aggressive Mode**:
```python
perturbation_mode='aggressive'
```
- Triggers at 20% of max iterations without improvement
- Perturbs 40% of parameters
- Larger perturbation scale

**Conservative Mode**:
```python
perturbation_mode='conservative'
```
- Triggers at 40% of max iterations without improvement
- Perturbs 10% of parameters
- Smaller perturbation scale

**Custom Mode**:
```python
perturbation_mode='custom',
perturbation_config={
    'trigger_threshold': 0.25,      # Fraction of max_iter_without_improvement
    'perturb_fraction': 0.3,        # Fraction of parameters to perturb
    'scale_factor': 2.0,            # Perturbation scale multiplier
    'variance_threshold': 0.001,    # Threshold for low variance detection
    'cooldown_period': 10,          # Iterations before re-perturbation
    'max_perturbations_per_param': 3  # Maximum perturbations per parameter
}
```

### Memory Mechanism

The perturbation system maintains memory of:
- Perturbation count per parameter
- Last perturbation iteration
- Effectiveness scores
- Parameter importance estimates

## 7. Usage Examples {#usage-examples}

### Basic Usage

```python
from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters

# Define parameters
params_df = pd.DataFrame({
    'name': ['x1', 'x2'],
    'min': [-5.0, -5.0],
    'max': [5.0, 5.0],
    'initial': [0.0, 0.0],
    'variation': ['continuous', 'continuous']
})

# Create optimizer
de = DifferentialEvolution(
    eval_func=my_objective_function,
    parameters=params_df,
    pop_size=30,
    max_iterations=100,
    mutation_factor_1=0.8,
    recombination_factor=0.9
)

# Run optimization
de.run_optimization()
print(f"Best solution: {de.best_parameters}")
```

### Advanced Usage with Perturbations

```python
# For difficult problems with many local minima
de = DifferentialEvolution(
    eval_func=complex_objective,
    parameters=params_df,
    pop_size=100,
    max_iterations=500,
    mutation_factor_1=(0.4, 1.2),  # Adaptive range
    mutation_factor_2=(0.0, 0.3),   # Some best influence
    recombination_factor=(0.6, 0.95),
    perturbation_mode='auto',       # Enable smart perturbations
    initial_population='halton'     # Better initial coverage
)
```

### Lens Optimization Example

```python
# High-sensitivity optimization
de = DifferentialEvolution(
    eval_func=lens_merit_function,
    parameters=lens_params,
    pop_size=50,
    max_iterations=200,
    mutation_factor_1=(0.3, 0.7),   # Smaller steps for sensitivity
    mutation_factor_2=(0.1, 0.3),   # Moderate best influence
    recombination_factor=(0.8, 0.95),
    perturbation_mode='conservative'
)
```

## 8. Best Practices {#best-practices}

### Population Size Selection

- **Rule of thumb**: `pop_size = 10 * n_parameters`
- **Simple problems**: 20-50 individuals
- **Complex problems**: 50-200 individuals
- **High-dimensional**: May need 200+ individuals

### Parameter Tuning Guidelines

1. **Mutation Factor 1** (`mutation_factor_1`):
   - Start with 0.5-0.8
   - Lower (0.3-0.5) for sensitive problems
   - Higher (0.8-1.2) for robust exploration

2. **Mutation Factor 2** (`mutation_factor_2`):
   - Usually keep low (0.0-0.3)
   - Set to 0 for pure DE/rand/1 strategy
   - Increase for faster convergence to best

3. **Recombination Factor** (`recombination_factor`):
   - Standard range: 0.7-0.9
   - Higher values = more exploration
   - Lower values = more exploitation

### When to Use Perturbations

Enable perturbations when:
- Problem has many local minima
- Population shows premature convergence
- Parameters have vastly different sensitivities
- Standard DE gets stuck

### Monitoring Convergence

Key metrics to watch:
- Population diversity (parameter variance)
- Best metric history
- Iterations without improvement
- Perturbation effectiveness (if enabled)

### Common Pitfalls

1. **Too small population**: Premature convergence
2. **Fixed evolution parameters**: Less adaptive behavior
3. **Ignoring boundaries**: Wasted evaluations
4. **No perturbations on hard problems**: Getting stuck

### Recommendations by Problem Type

**Smooth, Unimodal Functions**:
- Small population (20-30)
- Fixed, moderate parameters
- No perturbations needed

**Multimodal Functions**:
- Larger population (50-100)
- Adaptive parameters (use ranges)
- Auto perturbations recommended

**High-Dimensional Problems**:
- Very large population (10-20 × dimensions)
- Conservative parameters
- Aggressive perturbations may help

**Sensitive/Noisy Functions**:
- Moderate population
- Small mutation factors
- Conservative perturbations if any

\newpage

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

\newpage

# Nelder-Mead Simplex Optimizer

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

The Nelder-Mead algorithm, also known as the downhill simplex method, is a direct search optimization algorithm that doesn't require gradient information. Published in 1965, it remains one of the most popular derivative-free optimization methods.

### Key Characteristics

- **Derivative-free**: No gradient computation needed
- **Simplex-based**: Uses geometric simplex operations
- **Robust**: Works on non-smooth, noisy functions
- **Local search**: Finds local optima

### The Simplex Concept

A simplex is a geometric figure with n+1 vertices in n dimensions:
- 1D: Line segment (2 points)
- 2D: Triangle (3 points)
- 3D: Tetrahedron (4 points)

## 2. Algorithm Overview {#algorithm-overview}

The algorithm iteratively improves a simplex through four operations:

1. **Reflection**: Mirror worst point through centroid
2. **Expansion**: Extend beyond reflection if improving
3. **Contraction**: Shrink toward centroid if not improving
4. **Shrink**: Contract entire simplex toward best point

### Algorithm Flow

```
1. Initialize simplex
2. Evaluate all vertices
3. While not converged:
   a. Order vertices (best to worst)
   b. Calculate centroid of best n points
   c. Try reflection
   d. If good: try expansion
   e. If bad: try contraction
   f. If still bad: shrink simplex
4. Return best vertex
```

## 3. Mathematical Foundation {#mathematical-foundation}

### Simplex Operations

Given ordered vertices $x_1, x_2, ..., x_{n+1}$ where $f(x_1) \leq f(x_2) \leq ... \leq f(x_{n+1})$:

**Centroid** of best n points:
$$\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i$$

**Reflection**:
$$x_r = \bar{x} + \alpha (\bar{x} - x_{n+1})$$

**Expansion**:
$$x_e = \bar{x} + \gamma (x_r - \bar{x})$$

**Contraction** (outside):
$$x_{oc} = \bar{x} + \rho (x_r - \bar{x})$$

**Contraction** (inside):
$$x_{ic} = \bar{x} - \rho (\bar{x} - x_{n+1})$$

**Shrink**:
$$x_i^{new} = x_1 + \sigma (x_i - x_1), \quad i = 2, ..., n+1$$

### Standard Coefficients

Traditional values (can be adapted):
- α = 1.0 (reflection)
- γ = 2.0 (expansion)  
- ρ = 0.5 (contraction)
- σ = 0.5 (shrink)

## 4. Implementation Details {#implementation-details}

### Class Structure

```python
class NelderMead:
    def __init__(self,
                 seed: Optional[int] = None,
                 eval_func: Optional[Callable] = None,
                 parameters: Optional[Union[Parameters, str, pd.DataFrame]] = None,
                 opt_min_or_max: str = 'min',
                 max_iterations: int = 100,
                 metric_threshold: float = 0,
                 max_iter_without_improvement: int = 20,
                 improvement_threshold: float = 0.001,
                 reflection_coefficient: Union[float, Tuple[float, float]] = 1.0,
                 expansion_coefficient: Union[float, Tuple[float, float]] = 2.0,
                 contraction_coefficient: Union[float, Tuple[float, float]] = 0.5,
                 shrink_coefficient: Union[float, Tuple[float, float]] = 0.5,
                 initial_simplex_edge_length: float = 0.5,
                 adaptive_coefficients: bool = False,
                 defaults_in_initial_simplex: bool = True,
                 initial_simplex: Optional[Union[str, pd.DataFrame]] = None,
                 results_dir: Optional[str] = None)
```

### Simplex Initialization

Multiple strategies available:

1. **Default-based**: One vertex at defaults, others offset
2. **Random**: Random vertices within bounds
3. **Regular**: Geometrically regular simplex
4. **Custom**: Load from file or DataFrame

## 5. Parameters Reference {#parameters-reference}

### Core Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_iterations` | int | 100 | Maximum iterations allowed |
| `metric_threshold` | float | 0 | Target metric value |
| `max_iter_without_improvement` | int | 20 | Stagnation detection |
| `improvement_threshold` | float | 0.001 | Minimum relative improvement |

### Simplex Coefficients

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `reflection_coefficient` | float/tuple | 1.0 | Reflection distance α |
| `expansion_coefficient` | float/tuple | 2.0 | Expansion factor γ |
| `contraction_coefficient` | float/tuple | 0.5 | Contraction factor ρ |
| `shrink_coefficient` | float/tuple | 0.5 | Shrink factor σ |

**Note**: Tuple values enable adaptive coefficients (random sampling within range).

### Initialization Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `initial_simplex_edge_length` | float | 0.5 | Size of initial simplex (normalized) |
| `defaults_in_initial_simplex` | bool | True | Use defaults for first vertex |
| `initial_simplex` | str/DataFrame | None | Custom initial simplex |
| `adaptive_coefficients` | bool | False | Enable coefficient adaptation |

## 6. Advanced Features {#advanced-features}

### Adaptive Coefficients

When enabled, coefficients adjust based on simplex state:

```python
# Adaptive behavior (when tuple provided)
if simplex_is_contracting:
    α = uniform(α_range[0], α_range[1])  # More exploration
```

Benefits:
- Escape local plateaus
- Balance exploration/exploitation
- Automatic parameter tuning

### Convergence Detection

Multiple criteria checked:
1. **Metric threshold**: Objective below target
2. **Function tolerance**: Small spread in vertex values
3. **Simplex size**: Geometric size below threshold
4. **Stagnation**: No improvement for N iterations

### Restart Strategies

Though not built-in, implement restarts:

```python
best_overall = None
for restart in range(n_restarts):
    nm = NelderMead(
        seed=seed + restart,
        initial_simplex_edge_length=0.5 * (0.5 ** restart)  # Shrinking
    )
    nm.run_optimization()
    if best_overall is None or nm.best_metric < best_overall:
        best_overall = nm.best_metric
```

## 7. Usage Examples {#usage-examples}

### Basic Usage

```python
from aivalanche_lib.optimization.nelder_mead import NelderMead
from aivalanche_lib.parameters import Parameters

# Define parameters
params_df = pd.DataFrame({
    'name': ['x', 'y'],
    'min': [-5.0, -5.0],
    'max': [5.0, 5.0],
    'default': [0.0, 0.0],
    'variation': ['continuous', 'continuous']
})

# Create optimizer
nm = NelderMead(
    eval_func=objective_function,
    parameters=params_df,
    max_iterations=200
)

# Run optimization
nm.run_optimization()
print(f"Best solution: {nm.best_parameters}")
```

### Noisy Function Optimization

```python
# For noisy objectives
nm = NelderMead(
    eval_func=noisy_function,
    parameters=params_df,
    reflection_coefficient=(0.8, 1.2),     # Adaptive
    expansion_coefficient=(1.5, 2.5),      # Adaptive
    contraction_coefficient=(0.4, 0.6),    # Adaptive
    initial_simplex_edge_length=1.0,       # Larger initial simplex
    max_iter_without_improvement=50        # More patience
)
```

### High-Dimensional Problems

```python
# For many parameters
nm = NelderMead(
    eval_func=high_dim_function,
    parameters=params_df,  # Many parameters
    reflection_coefficient=1.0,
    expansion_coefficient=1.5,      # Conservative expansion
    contraction_coefficient=0.75,   # Less aggressive contraction
    shrink_coefficient=0.9,         # Gentle shrinking
    initial_simplex_edge_length=0.1 # Smaller initial simplex
)
```

### Constrained Optimization

```python
def constrained_objective(parameters, **kwargs):
    results = []
    for _, row in parameters.iterrows():
        x, y = row['x'], row['y']
        
        # Objective
        f = x**2 + y**2
        
        # Penalty for constraint g(x,y) <= 0
        g = x + y - 1  # Example: x + y <= 1
        penalty = max(0, g) ** 2 * 1000
        
        results.append({'metric': f + penalty})
    return results
```

## 8. Best Practices {#best-practices}

### When to Use Nelder-Mead

**Ideal for**:
- Non-smooth or discontinuous functions
- Noisy objectives
- No gradient information available
- Low to moderate dimensions (< 20)
- Quick approximate solutions

**Not ideal for**:
- High dimensions (> 50)
- Smooth functions (use gradient methods)
- Global optimization (use DE)
- High accuracy requirements

### Parameter Selection Guidelines

**For Smooth Functions**:
```python
reflection_coefficient=1.0
expansion_coefficient=2.0
contraction_coefficient=0.5
shrink_coefficient=0.5
```

**For Noisy Functions**:
```python
reflection_coefficient=(0.9, 1.1)    # Small variation
expansion_coefficient=(1.8, 2.2)     # Moderate expansion
contraction_coefficient=(0.4, 0.6)   # Adaptive contraction
initial_simplex_edge_length=0.8      # Larger simplex
```

**For Narrow Valleys**:
```python
reflection_coefficient=1.0
expansion_coefficient=3.0      # Aggressive expansion
contraction_coefficient=0.25   # Strong contraction
shrink_coefficient=0.25        # Aggressive shrinking
```

### Initial Simplex Strategy

1. **Known Good Region**: Use small simplex near good point
2. **Unknown Landscape**: Use larger simplex for exploration
3. **Multiple Scales**: Normalize parameters first
4. **Previous Results**: Use as initial vertex

### Handling Common Issues

**Premature Convergence**:
- Increase `initial_simplex_edge_length`
- Use adaptive coefficients
- Implement restarts
- Check parameter scaling

**Slow Convergence**:
- Decrease `max_iter_without_improvement`
- More aggressive expansion
- Check if gradient method better

**Oscillations**:
- Reduce coefficient variation
- Smaller initial simplex
- Check for noise in objective

### Performance Optimization

1. **Vectorize Evaluations**: Evaluate multiple points together
2. **Cache Results**: Avoid re-evaluating same points
3. **Parallel Trials**: Run multiple simplices
4. **Early Stopping**: Set reasonable thresholds

### Visualization and Debugging

For 2D problems, visualize:
- Simplex evolution
- Objective contours
- Operation types per iteration

```python
# After optimization
nm.plot_simplex_evolution(
    parameter_names=['x', 'y'],
    save_path='simplex_evolution.png'
)
```

### Hybrid Approaches

Combine with other methods:

**Global + Local**:
```python
# 1. Global search with DE
de = DifferentialEvolution(...)
de.run_optimization()

# 2. Local refinement with Nelder-Mead
nm = NelderMead(
    initial_simplex=create_simplex_around(de.best_parameters),
    initial_simplex_edge_length=0.01  # Small, focused search
)
```

**Multi-Start**:
```python
best_results = []
for i in range(10):
    nm = NelderMead(seed=i, ...)
    nm.run_optimization()
    best_results.append(nm.best_metric)
```

### Coefficient Adaptation Strategies

**Iteration-Based**:
- Start explorative, become exploitative
- Reduce coefficients over time

**Performance-Based**:
- Increase exploration if stuck
- Tighten when improving

**State-Based**:
- Large simplex → conservative
- Small simplex → aggressive

### Rules of Thumb

1. **Dimensions**: Works well up to ~20 dimensions
2. **Evaluations**: Expect O(n²) to O(n³) evaluations
3. **Accuracy**: Gets within 1-0.1% of optimum typically
4. **Robustness**: Very robust to noise and discontinuities

\newpage

# ADAM (Adaptive Moment Estimation) Optimizer

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

ADAM (Adaptive Moment Estimation) is a first-order gradient-based optimization algorithm that combines the advantages of two popular methods: AdaGrad and RMSProp. Introduced by Kingma and Ba in 2014, it has become one of the most popular optimizers in machine learning.

### Key Characteristics

- **Adaptive learning rates**: Per-parameter learning rate adaptation
- **Momentum**: Uses both first and second moment estimates
- **Bias correction**: Compensates for initialization bias
- **Efficient**: Computationally efficient and low memory requirements

### When to Use ADAM

ADAM excels in:
- Stochastic optimization
- High-dimensional parameter spaces
- Sparse gradients
- Non-stationary objectives
- Online learning scenarios

## 2. Algorithm Overview {#algorithm-overview}

ADAM maintains two moving averages:
1. **First moment** (mean) of gradients: momentum-like
2. **Second moment** (variance) of gradients: adaptive learning rates

### Key Steps

1. Compute gradient at current point
2. Update biased first moment estimate
3. Update biased second moment estimate
4. Compute bias-corrected estimates
5. Update parameters using moments

## 3. Mathematical Foundation {#mathematical-foundation}

### Update Equations

Given gradient $g_t$ at iteration $t$:

**First moment estimate** (momentum):
$$m_t = \beta_1 \cdot m_{t-1} + (1 - \beta_1) \cdot g_t$$

**Second moment estimate** (RMS):
$$v_t = \beta_2 \cdot v_{t-1} + (1 - \beta_2) \cdot g_t^2$$

**Bias correction**:
$$\hat{m}_t = \frac{m_t}{1 - \beta_1^t}$$
$$\hat{v}_t = \frac{v_t}{1 - \beta_2^t}$$

**Parameter update**:
$$x_{t+1} = x_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon} \cdot \hat{m}_t$$

Where:
- $\eta$ is the learning rate (`learning_rate`)
- $\beta_1$ is the first moment decay (`beta1`)
- $\beta_2$ is the second moment decay (`beta2`)
- $\epsilon$ is a small constant (`epsilon`)

### Intuition

- **First moment**: Exponentially weighted moving average of gradients (velocity)
- **Second moment**: Exponentially weighted moving average of squared gradients (acceleration)
- **Adaptive**: Learning rate scales with inverse square root of second moment

## 4. Implementation Details {#implementation-details}

### Class Structure

```python
class ADAM:
    def __init__(self,
                 seed: Optional[int] = None,
                 eval_func: Optional[Callable] = None,
                 parameters: Optional[Union[Parameters, str, pd.DataFrame]] = None,
                 opt_min_or_max: str = 'min',
                 max_iterations: int = 100,
                 metric_threshold: float = 0,
                 max_iter_without_improvement: int = 20,
                 improvement_threshold: float = 1e-6,
                 learning_rate: float = 0.001,
                 beta1: float = 0.9,
                 beta2: float = 0.999,
                 epsilon: float = 1e-8,
                 gradient_clip_value: Optional[float] = None,
                 learning_rate_decay: float = 0.0,
                 amsgrad: bool = False,
                 gradient_method: str = 'finite_difference',
                 gradient_step_size: float = 1e-6,
                 gradient_step_size_relative: bool = True,
                 initial_point: Optional[Union[str, pd.DataFrame]] = None,
                 use_defaults_in_initial_point: bool = True,
                 trust_region_radius: Optional[float] = None,
                 boundary_handling: str = 'clip',
                 results_dir: Optional[str] = None)
```

### Gradient Computation

Supports multiple methods:
1. **Finite Difference**: Numerical approximation
2. **Central Difference**: More accurate but costly
3. **Complex Step**: Machine precision accurate

### Moment Initialization

- First moment `m`: Initialized to zero
- Second moment `v`: Initialized to zero
- Bias correction ensures proper behavior early

## 5. Parameters Reference {#parameters-reference}

### Core Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_iterations` | int | 100 | Maximum number of iterations |
| `metric_threshold` | float | 0 | Stop if metric reaches threshold |
| `max_iter_without_improvement` | int | 20 | Patience for early stopping |
| `improvement_threshold` | float | 1e-6 | Minimum improvement to reset counter |

### ADAM-Specific Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `learning_rate` | float | 0.001 | Step size η |
| `beta1` | float | 0.9 | First moment decay rate |
| `beta2` | float | 0.999 | Second moment decay rate |
| `epsilon` | float | 1e-8 | Numerical stability constant |
| `gradient_clip_value` | float | None | Clip gradients to this value |
| `learning_rate_decay` | float | 0.0 | Learning rate decay per iteration |
| `amsgrad` | bool | False | Use AMSGrad variant |

### Gradient Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `gradient_method` | str | 'finite_difference' | Method for gradient computation |
| `gradient_step_size` | float | 1e-6 | Step size for finite differences |
| `gradient_step_size_relative` | bool | True | Use relative step size |

### Additional Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `trust_region_radius` | float | None | Maximum step size constraint |
| `boundary_handling` | str | 'clip' | How to handle bounds: 'clip', 'reflect', 'penalty' |

## 6. Advanced Features {#advanced-features}

### Learning Rate Scheduling

Exponential decay:
```python
lr_t = learning_rate * (1 - learning_rate_decay)^t
```

Custom scheduling example:
```python
def lr_callback(**kwargs):
    opt = kwargs['optimizer']
    if opt.iter % 50 == 0:
        opt.learning_rate *= 0.5  # Halve every 50 iterations
```

### Gradient Clipping

Prevents gradient explosion:
```python
if gradient_clip_value is not None:
    gradient = clip(gradient, -gradient_clip_value, gradient_clip_value)
```

Benefits:
- Stability in difficult landscapes
- Prevents overshooting
- Essential for some problems

### AMSGrad Variant

Addresses convergence issues in original ADAM:
```python
if amsgrad:
    v_hat_t = max(v_hat_{t-1}, v_t)  # Never decrease second moment
```

Use when:
- Standard ADAM doesn't converge
- Need convergence guarantees
- Dealing with difficult optimization landscapes

### Trust Region

Constrains maximum step size:
```python
if ||step|| > trust_region_radius:
    step = step * trust_region_radius / ||step||
```

## 7. Usage Examples {#usage-examples}

### Basic Usage

```python
from aivalanche_lib.optimization.adam import ADAM
from aivalanche_lib.parameters import Parameters

# Define parameters
params_df = pd.DataFrame({
    'name': ['w1', 'w2', 'b'],
    'min': [-10.0, -10.0, -10.0],
    'max': [10.0, 10.0, 10.0],
    'initial': [0.0, 0.0, 0.0],
    'variation': ['continuous', 'continuous', 'continuous']
})

# Create optimizer
adam = ADAM(
    eval_func=loss_function,
    parameters=params_df,
    learning_rate=0.001,
    max_iterations=1000
)

# Run optimization
adam.run_optimization()
print(f"Optimized parameters: {adam.best_parameters}")
```

### High-Dimensional Optimization

```python
# For many parameters
adam = ADAM(
    eval_func=neural_network_loss,
    parameters=params_df,  # Thousands of parameters
    learning_rate=0.001,
    beta1=0.9,
    beta2=0.999,
    gradient_clip_value=1.0,  # Prevent explosion
    learning_rate_decay=0.001,  # Gradual decay
    max_iterations=10000
)
```

### Stochastic Optimization

```python
def stochastic_objective(parameters, **kwargs):
    # Simulate mini-batch evaluation
    batch = kwargs.get('batch', get_random_batch())
    results = []
    for _, params in parameters.iterrows():
        loss = compute_batch_loss(params, batch)
        results.append({'metric': loss})
    return results

adam = ADAM(
    eval_func=stochastic_objective,
    parameters=params_df,
    learning_rate=0.01,      # Higher for stochastic
    beta1=0.9,
    beta2=0.99,             # Lower for more adaptation
    gradient_step_size=1e-4  # Larger for noise
)
```

### Sparse Optimization

```python
# For sparse gradients (e.g., embeddings)
adam = ADAM(
    eval_func=embedding_loss,
    parameters=params_df,
    learning_rate=0.1,       # Can use higher LR
    beta1=0.9,
    beta2=0.999,
    epsilon=1e-4            # Larger epsilon for sparse
)
```

### Non-Convex Optimization

```python
# For difficult non-convex problems
adam = ADAM(
    eval_func=non_convex_function,
    parameters=params_df,
    learning_rate=0.0001,    # Conservative
    beta1=0.95,              # More momentum
    beta2=0.999,
    amsgrad=True,            # Better convergence
    gradient_clip_value=0.5,
    trust_region_radius=0.1
)
```

## 8. Best Practices {#best-practices}

### Learning Rate Selection

**General Guidelines**:
- Start with 0.001 (default)
- Too high: Oscillations or divergence
- Too low: Slow convergence
- Problem-specific tuning needed

**By Problem Type**:
- Convex: 0.01 - 0.1
- Non-convex: 0.0001 - 0.001
- Stochastic: 0.001 - 0.01
- High-dimensional: 0.0001 - 0.001

### Beta Parameter Tuning

**Beta1 (Momentum)**:
- Default 0.9 works well
- Lower (0.8): Less momentum, more responsive
- Higher (0.95): More momentum, smoother

**Beta2 (RMS decay)**:
- Default 0.999 for most problems
- Lower (0.99): More adaptive to recent gradients
- Higher (0.9999): Longer memory

**Relationships**:
- Noisy gradients: Lower beta2
- Sparse gradients: Higher beta2
- Need stability: Higher both betas

### Handling Different Landscapes

**Smooth Convex**:
```python
learning_rate=0.01
beta1=0.9
beta2=0.999
```

**Noisy/Stochastic**:
```python
learning_rate=0.001
beta1=0.9
beta2=0.99  # More adaptive
gradient_clip_value=1.0
```

**Ill-Conditioned**:
```python
learning_rate=0.0001
beta1=0.95
beta2=0.999
amsgrad=True
```

**Sparse Gradients**:
```python
learning_rate=0.01
beta1=0.9
beta2=0.999
epsilon=1e-4  # Larger epsilon
```

### Common Issues and Solutions

**Divergence**:
- Reduce learning rate
- Enable gradient clipping
- Check gradient computation
- Use trust region

**Slow Convergence**:
- Increase learning rate carefully
- Adjust beta parameters
- Check if stuck in plateau
- Consider learning rate schedule

**Oscillations**:
- Reduce learning rate
- Increase beta1 (more momentum smoothing)
- Enable gradient clipping

**Poor Final Accuracy**:
- Reduce learning rate near end
- Use learning rate decay
- Increase epsilon if too small
- Run longer with patience

### Gradient Computation Tips

**Step Size Selection**:
- Relative: Good for different parameter scales
- Absolute: When parameters similar scale
- Too large: Inaccurate gradients
- Too small: Numerical errors

**Improving Accuracy**:
```python
# For critical applications
gradient_method='central_difference'  # More accurate
gradient_step_size=1e-8              # Smaller step
gradient_step_size_relative=True     # Handle scales
```

### Memory Efficiency

ADAM stores two moments per parameter:
- Memory: O(2n) for n parameters
- Computation: O(n) per iteration

For very large problems:
- Consider gradient checkpointing
- Use sparse updates if applicable
- Batch parameter updates

### Convergence Diagnostics

Monitor these metrics:
1. **Gradient norm**: Should decrease
2. **Update norm**: Should stabilize
3. **Moment magnitudes**: Check for explosion
4. **Learning rate**: Effective rate after adaptation

### When ADAM Excels

**Best for**:
- High-dimensional optimization
- Stochastic/online learning
- Sparse gradients
- Non-stationary objectives
- Parameters with different scales

**Not ideal for**:
- Simple convex problems (use L-BFGS)
- Low dimensions (use Newton methods)
- Need high accuracy (use second-order)
- Combinatorial optimization

### Hybrid Strategies

**Warm-up**:
```python
# Start with small LR, increase
for epoch in range(warmup_epochs):
    adam.learning_rate = base_lr * (epoch + 1) / warmup_epochs
```

**Switching Optimizers**:
```python
# ADAM for exploration, then L-BFGS for refinement
adam.run_optimization()
lbfgs = LBFGS(initial_point=adam.best_parameters)
lbfgs.run_optimization()
```

**Restart with Decay**:
```python
for restart in range(n_restarts):
    adam.learning_rate = initial_lr * (0.5 ** restart)
    adam.run_optimization()
```

### Advanced Techniques

**Lookahead**:
Maintain slow and fast weights:
```python
# Every k steps
slow_weights = 0.5 * slow_weights + 0.5 * fast_weights
```

**Weight Averaging**:
Average parameters over trajectory:
```python
averaged_params = sum(param_history[-k:]) / k
```

**Gradient Accumulation**:
For very large batch effects:
```python
accumulated_grad += compute_gradient(mini_batch)
if step % accumulation_steps == 0:
    apply_update(accumulated_grad / accumulation_steps)
```
