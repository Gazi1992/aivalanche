# Differential Evolution (DE) Optimizer

## Overview

Differential Evolution (DE) is a population-based metaheuristic optimization algorithm that belongs to the family of evolutionary algorithms. It was developed by Storn and Price in 1997 and has become one of the most popular algorithms for continuous optimization problems.

## How Differential Evolution Works

### Basic Principles

DE maintains a population of candidate solutions (called individuals or vectors) and evolves them over generations using three main operations:

1. **Mutation**: Creates a donor vector by combining existing population members
2. **Crossover**: Mixes the donor vector with the target vector to create a trial vector
3. **Selection**: Chooses between the trial and target vectors based on fitness

### Algorithm Steps

1. **Initialization**: Generate a random initial population within the parameter bounds
2. **For each generation**:
   - For each individual in the population:
     - **Mutation**: Create a donor vector using a mutation strategy (e.g., DE/rand/1)
     - **Crossover**: Create a trial vector by mixing donor and target vectors
     - **Selection**: Keep the better solution between trial and target
3. **Termination**: Stop when convergence criteria are met

### Key Features

- **Self-adaptive**: Parameters can be adapted during optimization
- **Global search**: Good at escaping local optima
- **Simple**: Few control parameters (F, CR, population size)
- **Robust**: Works well on a wide variety of problems
- **Parallel-friendly**: Population members can be evaluated independently

## Using the DifferentialEvolution Class

### Basic Usage

```python
from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
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
optimizer = DifferentialEvolution(
    eval_func=eval_func,
    parameters=Parameters(param_config),
    opt_min_or_max='min',
    pop_size=50,
    max_iterations=100,
    F=0.8,
    CR=0.9
)

optimizer.run_optimization()

# Access results
print(f"Best metric: {optimizer.best_metric}")
print(f"Best parameters: {optimizer.best_parameters}")
```

### Advanced Features

#### 1. Mutation Strategies

```python
optimizer = DifferentialEvolution(
    # ... other parameters ...
    mutation_strategy='DE/best/1',  # Options: 'DE/rand/1', 'DE/best/1', 'DE/target-to-best/1', etc.
    F=0.8  # Mutation factor
)
```

#### 2. Adaptive Parameters

```python
optimizer = DifferentialEvolution(
    # ... other parameters ...
    adaptive_F=True,  # Adapt mutation factor
    adaptive_CR=True,  # Adapt crossover rate
    F_min=0.4, F_max=1.0,  # Bounds for adaptive F
    CR_min=0.1, CR_max=0.9  # Bounds for adaptive CR
)
```

#### 3. Population Initialization

```python
# Use Latin Hypercube Sampling for better initial coverage
optimizer = DifferentialEvolution(
    # ... other parameters ...
    init_pop_method='lhs'  # or 'random'
)

# Or provide your own initial population
import pandas as pd
initial_pop = pd.DataFrame({
    'param1': [1.0, 2.0, 3.0, ...],
    'param2': [0.5, 1.5, 2.5, ...]
})
optimizer = DifferentialEvolution(
    # ... other parameters ...
    init_pop=initial_pop
)
```

#### 4. Callbacks

```python
def callback_each_iter(**kwargs):
    print(f"Iteration {kwargs['iteration']}: Best = {kwargs['best_metric']}")

optimizer = DifferentialEvolution(
    # ... other parameters ...
    callback_after_each_iter=callback_each_iter
)
```

#### 5. Boundary Handling

```python
optimizer = DifferentialEvolution(
    # ... other parameters ...
    boundary_strategy='reflect',  # Options: 'clip', 'reflect', 'reject'
    ensure_feasibility=True
)
```

### Stopping Criteria

The optimizer supports multiple stopping criteria:

- `max_iterations`: Maximum number of generations
- `metric_threshold`: Stop if metric reaches this value
- `patience`: Stop if no improvement for this many iterations
- `improvement_threshold`: Minimum improvement to reset patience counter
- `early_stop_mode`: 'abs' or 'rel' for absolute or relative improvement

### Visualization and Analysis

```python
# Plot metrics evolution
fig, ax = optimizer.plot_metrics()

# Plot population evolution (for 2D problems)
fig, ax = optimizer.plot_population(iter_num=50)

# Create animation (for 2D problems)
from aivalanche_lib.optimization.differential_evolution.visualizations import _plot_population_animation
anim = _plot_population_animation(optimizer, save_path='de_animation.gif')

# Plot survivor selection histograms
fig, axes = optimizer.plot_survivor_histograms()

# Save results
optimizer.write_best_parameters_to_file('best_params.csv')
optimizer.write_optimization_info_to_file('opt_info.json')
optimizer.write_history_to_file('population', 'population_history.csv')
```

## Parameter Guidelines

### Population Size
- General rule: 5-10 times the number of parameters
- Larger populations for multimodal problems
- Smaller populations for faster convergence

### Mutation Factor (F)
- Typical range: 0.4 - 1.0
- Lower F: More exploitation (local search)
- Higher F: More exploration (global search)
- Default: 0.8

### Crossover Rate (CR)
- Typical range: 0.1 - 1.0
- Lower CR: Slower convergence, better for separable problems
- Higher CR: Faster convergence, better for rotated problems
- Default: 0.9

## When to Use Differential Evolution

**Good for:**
- Global optimization problems
- Non-convex, multimodal functions
- Problems with many local optima
- When gradient information is unavailable
- Noisy objective functions
- Mixed integer/continuous problems

**Not ideal for:**
- Very high-dimensional problems (>100 parameters)
- When gradient information is available and reliable
- Problems requiring extremely high precision
- When function evaluations are extremely expensive

## Common Issues and Solutions

1. **Slow convergence**: Increase F or CR, or use adaptive parameters
2. **Premature convergence**: Increase population size or use different mutation strategy
3. **Stagnation**: Enable adaptive parameters or increase population diversity
4. **Boundary violations**: Use appropriate boundary handling strategy

## References

1. Storn, R., & Price, K. (1997). Differential evolution–a simple and efficient heuristic for global optimization over continuous spaces.
2. Das, S., & Suganthan, P. N. (2011). Differential evolution: A survey of the state-of-the-art.
3. Price, K., Storn, R. M., & Lampinen, J. A. (2005). Differential evolution: a practical approach to global optimization.