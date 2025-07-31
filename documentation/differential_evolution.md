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
                 use_local_refinement: bool = False,
                 refinement_method: str = 'dls',
                 refinement_trigger: str = 'on_completion',
                 refinement_max_iterations: int = 50,
                 refinement_options: Optional[Dict[str, Any]] = None,
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
| `use_local_refinement` | bool | False | Enable local refinement with DLS |
| `refinement_method` | str | 'dls' | Local refinement method |
| `refinement_trigger` | str | 'on_completion' | When to trigger: 'on_completion', 'on_stagnation', 'adaptive', 'both' |
| `refinement_max_iterations` | int | 50 | Maximum iterations for refinement |
| `refinement_options` | dict | None | Options for refinement method |

## 6. Advanced Features {#advanced-features}

### Local Refinement with DLS

DE can be combined with local optimization methods for hybrid global-local optimization. This feature uses Damped Least Squares (DLS) to refine the best solution found by DE.

#### Refinement Parameters

- **use_local_refinement**: Enable/disable local refinement
- **refinement_method**: Currently supports 'dls'
- **refinement_trigger**: When to apply refinement
  - `'on_completion'`: After DE finishes (default)
  - `'on_stagnation'`: When DE stagnates
  - `'adaptive'`: Periodically during optimization
  - `'both'`: Adaptive during optimization AND on_completion after
- **refinement_max_iterations**: Max iterations for refinement
- **refinement_options**: Options passed to DLS optimizer

#### How It Works

1. **Global Search**: DE explores the search space
2. **Trigger Check**: System checks if refinement should start
3. **Local Refinement**: DLS refines the best solution
4. **Update**: If improved during optimization, updates trials for natural selection

**Design Philosophy**: When refinement runs during optimization (on_stagnation, adaptive, both modes), it updates the trials array with the refined solution. This allows DE's selection mechanism to naturally decide whether to keep the refined solution, maintaining the evolutionary process integrity.

#### Example Usage

```python
# Basic hybrid optimization
de = DifferentialEvolution(
    eval_func=objective_function,
    parameters=params,
    pop_size=50,
    max_iterations=100,
    
    # Enable DLS refinement
    use_local_refinement=True,
    refinement_trigger='on_completion',
    refinement_max_iterations=50
)

# Advanced: Adaptive refinement
de = DifferentialEvolution(
    eval_func=objective_function,
    parameters=params,
    pop_size=50,
    max_iterations=200,
    
    # Adaptive refinement
    use_local_refinement=True,
    refinement_trigger='adaptive',  # Refine during optimization
    refinement_max_iterations=30,
    refinement_options={
        'residual_type': 'vector',  # If objective provides residuals
        'initial_damping': 0.1,
        'gradient_tolerance': 1e-10
    }
)
```

#### Benefits of Hybrid Optimization

1. **Best of Both Worlds**: Global exploration + local precision
2. **Higher Accuracy**: DLS achieves machine precision near optima
3. **Efficiency**: Fewer total evaluations than pure global search
4. **Robustness**: Less sensitive to initial conditions

### Adaptive Perturbation System

The perturbation feature helps escape local minima by intelligently perturbing stagnant parameters.

**Design Note**: Perturbations are applied to the trials array after donor and trial generation. This provides a final exploration boost before evaluation, allowing perturbation to act as an additional mutation operator.

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

### Hybrid DE-DLS Example

```python
# For problems requiring both global search and high precision
def rosenbrock_with_residuals(parameters, **kwargs):
    results = []
    for _, row in parameters.iterrows():
        x, y = row['x'], row['y']
        # Objective value
        metric = (1 - x)**2 + 100 * (y - x**2)**2
        
        # Residuals for DLS (optional but recommended)
        r1 = 1 - x
        r2 = 10 * (y - x**2)
        
        results.append({
            'metric': metric,
            'residuals': [r1, r2]  # Enables efficient DLS refinement
        })
    return results

# Create hybrid optimizer
de = DifferentialEvolution(
    eval_func=rosenbrock_with_residuals,
    parameters=params_df,
    pop_size=40,
    max_iterations=100,
    
    # DE parameters for global search
    mutation_factor_1=(0.5, 0.9),
    recombination_factor=(0.7, 0.9),
    
    # Enable local refinement
    use_local_refinement=True,
    refinement_trigger='on_stagnation',  # Refine when DE stagnates
    refinement_max_iterations=50,
    refinement_options={
        'residual_type': 'vector',
        'gradient_tolerance': 1e-10,
        'parameter_tolerance': 1e-12
    }
)

# Run hybrid optimization
de.run_optimization()

# Access refinement information
if de.refinement_applied:
    print(f"Refinement improved solution by {de.refinement_info['relative_improvement']:.2%}")
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

### When to Use Hybrid DE-DLS

Enable local refinement when:
- **High precision needed**: Final solution requires many decimal places
- **Smooth objective near optimum**: DLS works best with smooth functions
- **Limited evaluation budget**: Refinement can achieve precision faster
- **Known good region**: DE found promising area but needs refinement

Avoid local refinement when:
- **Highly discontinuous objective**: DLS requires smoothness
- **Very noisy evaluations**: Gradients become unreliable
- **Only rough solution needed**: Extra precision not worth the cost

### Refinement Trigger Selection

1. **on_completion** (default):
   - Best for: Standard optimization problems
   - Pros: Simple, predictable behavior
   - Cons: May miss opportunities during optimization

2. **on_stagnation**:
   - Best for: Problems where DE gets stuck
   - Pros: Can escape stagnation earlier
   - Cons: May trigger prematurely

3. **adaptive**:
   - Best for: Long runs, complex landscapes
   - Pros: Multiple refinement opportunities
   - Cons: More complex behavior, higher cost

4. **both**:
   - Best for: Maximum precision requirements
   - Pros: Benefits during optimization AND final polish
   - Cons: Highest computational cost
   - Use when: You need both escape from local minima and final high precision
