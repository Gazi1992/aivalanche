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
