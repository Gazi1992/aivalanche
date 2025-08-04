# Differential Evolution (DE) Optimizer

## Overview

Differential Evolution (DE) is a robust population-based metaheuristic optimization algorithm. This implementation includes advanced features like adaptive perturbation, local refinement with DLS/Adam/Nelder-Mead, and adaptive boundaries, making it suitable for challenging optimization problems.

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
- **Perturbation system**: Intelligent escape from stagnation
- **Local refinement**: DLS/Adam/Nelder-Mead integration for high precision
- **Adaptive boundaries**: Dynamic search space adjustment
- **Multiple stop criteria**: Flexible termination conditions
- **Robust**: Works well on a wide variety of problems

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
    seed=42,
    eval_func=eval_func,
    parameters=Parameters(param_config),
    opt_min_or_max='min',
    pop_size=50,
    max_iterations=100,
    mutation_factor_1=0.8,  # F in classical DE
    recombination_factor=0.9  # CR in classical DE
)

optimizer.run_optimization()

# Access results
print(f"Best metric: {optimizer.best_metric}")
print(f"Best parameters: {optimizer.best_parameters}")
```

### Advanced Features

#### 1. Adaptive Parameters

```python
optimizer = DifferentialEvolution(
    # ... other parameters ...
    # Use ranges for adaptive parameters
    mutation_factor_1=(0.5, 0.9),
    mutation_factor_2=(0.0, 0.3),
    recombination_factor=(0.7, 0.95)
)
```

#### 2. Perturbation System (Simplified)

DE includes a streamlined perturbation system to help escape local minima by intelligently perturbing converged parameters.

##### How It Works

1. **Triggering**: Perturbations are triggered when the algorithm hasn't improved for a certain number of iterations
2. **Parameter Selection**: Parameters with low variance (converged) are selected for perturbation
3. **Perturbation Application**: Gaussian noise proportional to the parameter's current standard deviation is added
4. **Population Coverage**: A random subset of the population is perturbed

##### Configuration

```python
# Enable with default settings
optimizer = DifferentialEvolution(
    perturbation_mode='on'  # Simple on/off switch
)

# Custom configuration
optimizer = DifferentialEvolution(
    perturbation_mode='on',
    perturbation_config={
        'trigger_ratio': 0.2,         # Trigger after 20% of max_iter_without_improvement (default)
        'std_threshold': 0.05,        # Parameters with std < 0.05 are considered converged (default)
        'scale': (1.5, 4),            # Perturbation scale multiplier range (default)
        'population_ratio': (0.6, 1.0) # Fraction of population to perturb (default)
    }
)
```

##### Configuration Parameters

1. **`trigger_ratio`** (float, default=0.2)
   - When to trigger perturbation as a fraction of `max_iter_without_improvement`
   - Example: 0.2 means trigger after 20% of allowed stagnation iterations
   - Lower values = earlier perturbation, higher values = later perturbation

2. **`std_threshold`** (float, default=0.05)
   - Parameters with standard deviation below this are considered converged
   - In normalized space [0,1], so 0.05 means 5% of the range
   - Lower values = only very converged parameters, higher = more parameters selected

3. **`scale`** (float or tuple, default=(1.5, 4))
   - Multiplier for the parameter's standard deviation when generating perturbation
   - Single value: fixed scale, tuple: random value from range
   - Perturbation = Normal(0, current_std × scale)
   - Higher values = stronger perturbations

4. **`population_ratio`** (float or tuple, default=(0.6, 1.0))
   - Fraction of population members to perturb
   - Single value: fixed ratio, tuple: random value from range
   - Lower values = fewer members perturbed, preserving more of the current population

##### Example Configurations

```python
# Early and gentle perturbations
optimizer = DifferentialEvolution(
    perturbation_mode='on',
    perturbation_config={
        'trigger_ratio': 0.1,    # Trigger at 10%
        'std_threshold': 0.15,   # Higher threshold
        'scale': (0.5, 1.5),     # Gentler perturbations
        'population_ratio': 0.5   # Half the population
    }
)

# Late and strong perturbations
optimizer = DifferentialEvolution(
    perturbation_mode='on',
    perturbation_config={
        'trigger_ratio': 0.3,    # Trigger at 30%
        'std_threshold': 0.05,   # Lower threshold
        'scale': (2, 5),         # Stronger perturbations
        'population_ratio': (0.8, 1.0)  # Most of the population
    }
)

# Fixed configuration (no randomness)
optimizer = DifferentialEvolution(
    perturbation_mode='on',
    perturbation_config={
        'trigger_ratio': 0.2,
        'std_threshold': 0.1,
        'scale': 2.0,            # Fixed scale
        'population_ratio': 0.7   # Fixed ratio
    }
)
```

##### When to Use Perturbations

- **Multimodal problems**: Many local optima where the algorithm can get stuck
- **High-dimensional problems**: Where convergence to suboptimal solutions is common
- **Plateau landscapes**: Where the objective function has flat regions
- **When you see premature convergence**: Population diversity drops too quickly

##### Perturbation Behavior

The perturbation system tracks its effectiveness:
- Green markers in visualizations: Perturbation led to improvement
- Red markers: Perturbation didn't improve (but may have helped exploration)
- History tracking: All perturbation events are recorded for analysis

#### 3. Local Refinement with DLS/Adam/Nelder-Mead

```python
# Enable refinement with default settings (DLS)
optimizer = DifferentialEvolution(
    # ... other parameters ...
    refinement_mode='on'  # Enable refinement with default DLS
)

# Custom refinement configuration with DLS
optimizer = DifferentialEvolution(
    # ... other parameters ...
    refinement_mode='on',
    refinement_config={
        'method': 'dls',  # Damped Least Squares
        'trigger_ratio': 0.2,  # Trigger at 20% of max_iter_without_improvement
        'max_iterations': 200,  # Max refinement iterations
        'options': {  # DLS-specific options
            'gradient_tolerance': 1e-10,
            'parameter_tolerance': 1e-10,
            'improvement_threshold': 1e-8
        }
    }
)

# Using Adam optimizer for refinement
optimizer = DifferentialEvolution(
    # ... other parameters ...
    refinement_mode='on',
    refinement_config={
        'method': 'adam',
        'trigger_ratio': -1,  # Post-optimization only
        'max_iterations': 500,
        'options': {
            'learning_rate': 0.001,
            'beta1': 0.9,
            'beta2': 0.999,
            'learning_rate_decay': 0.95
        }
    }
)

# Using Nelder-Mead for refinement
optimizer = DifferentialEvolution(
    # ... other parameters ...
    refinement_mode='on',
    refinement_config={
        'method': 'nelder_mead',
        'trigger_ratio': -1,  # Post-optimization only
        'max_iterations': 300,
        'options': {
            'best_point_position': 'centroid',  # or 'corner'
            'initial_simplex_scale': 0.02,  # 2% of parameter range
            'reflection_coefficient': 1.0,
            'expansion_coefficient': 2.0
        }
    }
)

# Refine only after optimization completes
optimizer = DifferentialEvolution(
    # ... other parameters ...
    refinement_mode='on',
    refinement_config={
        'trigger_ratio': -1  # Only refine after DE finishes
    }
)
```

#### 4. Population Initialization

```python
# Use different initialization methods
optimizer = DifferentialEvolution(
    # ... other parameters ...
    initial_population='halton'  # 'random', 'halton', 'sobol'
)
```

#### 5. Adaptive Boundaries

Adaptive boundaries allow the search space to dynamically expand or contract based on where the population is exploring.

```python
# Enable with default settings
optimizer = DifferentialEvolution(
    # ... other parameters ...
    adaptive_boundaries_mode='on'  # Enable adaptive boundaries
)

# Custom configuration
optimizer = DifferentialEvolution(
    # ... other parameters ...
    adaptive_boundaries_mode='on',
    adaptive_boundaries_config={
        'edge_threshold': 0.05,    # How close to boundary is "edge" (default)
        'pop_quantile': 0.7,       # Fraction of population needed at edge (default)
        'extension': 0.1,          # How much to extend boundaries (default)
        'check_period': 10         # Check every N iterations (default)
    }
)
```

##### Configuration Parameters

1. **`edge_threshold`** (float, default=0.05)
   - Defines how close to the boundary is considered "at the edge"
   - Value between 0 and 1, where 0.05 means within 5% of the boundary
   - Lower values = stricter edge detection

2. **`pop_quantile`** (float, default=0.7)
   - Fraction of population that must be at the edge to trigger extension
   - Value between 0 and 1, where 0.7 means 70% of population
   - Higher values = more conservative extension

3. **`extension`** (float, default=0.1)
   - How much to extend the boundaries when triggered
   - Value between 0 and 1, where 0.1 means extend by 10% of current range
   - Higher values = larger extensions

4. **`check_period`** (int, default=10)
   - Check boundaries every N iterations
   - Higher values = less frequent checks (better performance)

##### Example Configurations

```python
# Conservative - careful boundary adjustments
optimizer = DifferentialEvolution(
    adaptive_boundaries_mode='on',
    adaptive_boundaries_config={
        'edge_threshold': 0.02,    # Stricter edge detection
        'pop_quantile': 0.9,       # Need 90% of population
        'extension': 0.05,         # Small extensions
        'check_period': 20         # Check less frequently
    }
)

# Aggressive - for unknown search spaces
optimizer = DifferentialEvolution(
    adaptive_boundaries_mode='on',
    adaptive_boundaries_config={
        'edge_threshold': 0.1,     # Looser edge detection
        'pop_quantile': 0.5,       # Only 50% needed
        'extension': 0.2,          # Large extensions
        'check_period': 5          # Frequent checks
    }
)
```

#### 6. Callbacks

```python
def callback_each_iter(**kwargs):
    print(f"Iteration {kwargs['iteration']}: Best = {kwargs['best_metric']}")

optimizer = DifferentialEvolution(
    # ... other parameters ...
    callback_after_each_iter=callback_each_iter
)
```


### Stopping Criteria

The optimizer supports multiple stopping criteria:

- `max_iterations`: Maximum number of generations
- `metric_threshold`: Stop if metric reaches this value
- `max_iter_without_improvement`: Stop if no improvement for this many iterations

### Results and History

```python
# Access optimization results
print(f"Best metric: {optimizer.best_metric}")
print(f"Best parameters: {optimizer.best_parameters}")
print(f"Stop reason: {optimizer.stop_reason}")
print(f"Total evaluations: {optimizer.nr_evaluations}")

# Check optimization status
print(f"Has started: {optimizer.has_started}")
print(f"Is running: {optimizer.is_running}")
print(f"Has finished: {optimizer.has_finished}")

# Access history
best_history = optimizer.history['bests']  # Best solutions per iteration
trial_history = optimizer.history['trials']  # All trials

# Save results
if optimizer.results_dir:
    # Results are automatically saved to the specified directory
    pass
```

### Status Flags

DE provides three status flags to track the optimization state:

- **`has_started`**: `True` if `run_optimization()` has been called, `False` otherwise
- **`is_running`**: `True` if optimization is currently in progress, `False` otherwise
- **`has_finished`**: `True` if optimization has completed (either successfully or with an error), `False` otherwise

These flags are useful for:
- Monitoring optimization progress in real-time
- Building user interfaces that show optimization status
- Handling callbacks and external monitoring
- Ensuring proper cleanup even if optimization fails

Example usage:
```python
# Before optimization
assert optimizer.has_started == False
assert optimizer.is_running == False
assert optimizer.has_finished == False

# During optimization (in a callback)
def my_callback(**kwargs):
    opt = kwargs['optimizer']
    print(f"Running: {opt.is_running}")  # Will be True
    
# After optimization
optimizer.run_optimization()
assert optimizer.has_started == True
assert optimizer.is_running == False
assert optimizer.has_finished == True

# The flags are also available in optimization_info
info = optimizer.optimization_info
print(info['output']['has_started'])  # True
print(info['output']['is_running'])   # False
print(info['output']['has_finished']) # True
```

## Parameter Guidelines

### Population Size
- General rule: 5-10 times the number of parameters
- Larger populations for multimodal problems
- Smaller populations for faster convergence

### Mutation Factors
- `mutation_factor_1` (F1): Differential weight, typical range 0.4-1.0
- `mutation_factor_2` (F2): Best individual weight, typical range 0.0-0.5
- Use tuples for adaptive ranges: (0.5, 0.9)

### Recombination Factor (CR)
- Typical range: 0.5-1.0
- Lower CR: More parent information retained
- Higher CR: More donor information used
- Use tuple for adaptive range: (0.7, 0.95)

### Perturbation Settings
- `'off'`: No perturbation (default)
- `'on'`: Enable perturbation with default or custom configuration
- Use `trigger_ratio` to control when perturbations happen
- Use `std_threshold` to control which parameters get perturbed
- Use `scale` to control perturbation strength
- Use `population_ratio` to control how many individuals are affected

### Refinement Configuration

DE supports local refinement with multiple methods to polish solutions:

#### Key Parameters

- **`refinement_mode`**: 'off' (default) or 'on'
- **`refinement_config`**: Dictionary with configuration options:
  - **`method`**: Refinement method - 'dls' (default), 'adam', or 'nelder_mead'
  - **`trigger_ratio`**: When to trigger refinement during optimization (0-1, default 0.2)
    - 0.2 = trigger at 20% of max_iter_without_improvement
    - -1 = only refine after optimization completes
  - **`max_iterations`**: Maximum refinement iterations (default 1000)
  - **`options`**: Method-specific options dict

#### When Refinement Happens

1. **During optimization**: When stagnation reaches `trigger_ratio * max_iter_without_improvement`
2. **After optimization**: Always runs if `refinement_mode='on'` (unless `trigger_ratio=-1` is set)

#### Default Configuration

The default refinement configuration is optimized for convergence:

```python
# Default configuration structure
{
    'method': 'dls',  # Default method
    'trigger_ratio': 0.2,
    'max_iterations': 1000,
    'options': {
        # Method-specific defaults are applied automatically
    }
}
```

Each method has its own optimized defaults that are automatically applied:

```python
{
    'method': 'dls',
    'trigger_ratio': 0.2,  # Trigger at 20% stagnation
    'max_iterations': 200,  # Allow sufficient iterations
    'options': {
        'initial_damping': 0.01,
        'gradient_tolerance': 1e-10,
        'parameter_tolerance': 1e-10,
        'improvement_threshold': 1e-8,
        'max_iter_without_improvement': 50
    }
}
```

### Metamodel-Assisted Optimization

DE now supports metamodel-assisted optimization to reduce function evaluations:

#### Available Metamodel Modes

1. **`off`** (Default)
   - No metamodel, all evaluations use actual function
   
2. **`auto`**
   - Balanced metamodel usage
   - Good general purpose choice for speedup
   
3. **`exploration`**
   - Emphasizes exploration with uncertain predictions
   - Good for complex landscapes
   
4. **`exploitation`**
   - Trusts the model more for exploitation
   - Good when function is smooth
   
5. **`fast`**
   - Maximum speedup by using metamodel for most evaluations
   - May sacrifice accuracy
   
6. **`accurate`**
   - Conservative usage only when model is very certain
   - Maintains high accuracy
   
7. **`periodic`**
   - Periodically validates metamodel predictions
   - Good balance of speed and reliability
   
8. **`noisy`**
   - Configured for noisy objective functions
   - More robust to noise
   
9. **`high_dimensional`**
   - Optimized for high-dimensional problems
   - Careful with training data
   
10. **`custom`**
    - User-defined configuration
    - Full control over all parameters

#### Usage Examples

```python
# Simple metamodel usage
optimizer = DifferentialEvolution(
    metamodel_mode='auto'
)

# For noisy functions
optimizer = DifferentialEvolution(
    metamodel_mode='noisy'
)

# For high-dimensional problems
optimizer = DifferentialEvolution(
    metamodel_mode='high_dimensional'
)

# Custom configuration
optimizer = DifferentialEvolution(
    metamodel_mode='custom',
    metamodel_config={
        'enabled': True,
        'type': 'gaussian_process',
        'model_config': {
            'kernel': 'matern',
            'alpha': 1e-6
        },
        'acquisition_strategy': 'mixed',
        'acquisition_function': 'expected_improvement',
        'min_training_points': 100,
        'update_frequency': 5,
        'exploration_ratio': 0.2,
        'uncertainty_threshold': 0.2,
        'validation_frequency': 10,
        'verbose': True
    }
)
```

#### Choosing the Right Metamodel Mode

```python
from aivalanche_lib.optimization.differential_evolution import suggest_metamodel_mode

# Get suggestion based on problem
mode = suggest_metamodel_mode(
    problem_type='smooth',           # Returns 'exploitation'
    n_dim=50,                       # Or would return 'high_dimensional'
    function_noise='high'           # Or would return 'noisy'
)

# Get description of what a mode does
from aivalanche_lib.optimization.differential_evolution import get_metamodel_mode_description
print(get_metamodel_mode_description('auto'))
# Output: "Balanced metamodel usage. Good general purpose choice for speedup."
```

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

## Handling of Categorical Parameters

### Overview

Differential Evolution internally converts categorical parameters to numerical indices (0, 1, 2, ..., N-1) for optimization. While DE can optimize categorical parameters through its standard operators (mutation, crossover, selection), certain advanced features handle them differently.

### Perturbation System

**Note:** In the simplified implementation, categorical parameters are included in perturbation for code simplicity. The perturbation is applied in the normalized space [0,1] and then mapped back to valid categorical values.

**Behavior:**
- Perturbation adds Gaussian noise to all parameter values
- For categorical parameters, the perturbed continuous value is mapped to the nearest valid category
- This can cause random jumps between categories
- While not theoretically ideal for categorical variables, it maintains code simplicity

### Local Refinement

**Categorical parameters are automatically excluded from refinement.**

**Rationale:**
- DLS and Adam are gradient-based optimization methods
- Nelder-Mead, while derivative-free, still assumes continuous variables
- Gradients are undefined for discrete categorical variables
- These algorithms assume continuous, differentiable (or at least continuous) functions

**Implementation:**
- During refinement, categorical parameters are held fixed at their current best values

#### Method-Specific Details:

**DLS (Damped Least Squares)**:
- Gradient-based method using the Levenberg-Marquardt algorithm
- Best for smooth, well-behaved functions
- Very efficient when close to optimum

**Adam**:
- Adaptive learning rate gradient-based optimizer
- Good for noisy or sparse gradients
- Includes momentum for faster convergence

**Nelder-Mead**:
- Derivative-free simplex method
- Good for non-smooth or discontinuous functions
- Initial simplex can be configured:
  - `best_point_position`: 'corner' (default) or 'centroid'
  - `initial_simplex_scale`: Controls initial simplex size (default 0.05 = 5% of range)
- Only continuous and discrete numeric parameters are refined
- The refined solution merges improved numeric parameters with existing categorical values

### Example

```python
# Parameters with mixed types
params = Parameters([
    {'name': 'learning_rate', 'type': 'continuous', 'min': 0.001, 'max': 0.1},
    {'name': 'batch_size', 'type': 'discrete', 'values': [16, 32, 64, 128]},
    {'name': 'optimizer', 'type': 'categorical', 'values': ['adam', 'sgd', 'rmsprop']}
])

# DE will optimize all parameters
optimizer = DifferentialEvolution(
    eval_func=my_eval_func,
    parameters=params,
    perturbation_mode='on',      # Will perturb all parameters including categorical
    refinement_mode='on'         # Will only refine learning_rate and batch_size
)

# The optimizer parameter will be optimized through normal DE operations
# and included in perturbation (though effects may be limited)
# but excluded from gradient-based refinement
```

### Best Practices

1. **Use DE's standard operators** for categorical optimization - they work well
2. **Perturbation is most effective** for continuous parameters that can truly "escape" local minima
3. **Refinement provides high precision** for continuous parameters near the optimum
4. **Consider problem structure** - if you have mostly categorical parameters, standard DE without perturbation/refinement may be sufficient

## Common Issues and Solutions

1. **Slow convergence**: Use adaptive parameters or increase mutation factors
2. **Premature convergence**: Enable perturbation system or increase population
3. **Stagnation**: Enable refinement - it triggers automatically on stagnation
4. **Low precision**: Enable local refinement with DLS
5. **Wide search space**: Enable adaptive boundaries

## Directory Structure

```
differential_evolution/
├── DifferentialEvolution.py    # Main optimizer class
├── operators.py               # Core DE operators
├── perturbation.py           # Simplified perturbation system
├── refinement.py             # DLS integration and configuration
├── metamodel_modes.py        # Predefined metamodel configurations
├── utils.py                  # Utility functions
├── visualizations.py         # Plotting functions
├── io.py                     # Input/output operations
├── examples/                 # Example scripts
└── tests/                    # Test suite
    ├── test_differential_evolution.py
    ├── test_adaptive_boundaries.py
    ├── test_perturbation_rastrigin.py
    ├── test_de_strategies_comparison.py
    └── test_metamodel_modes.py
```

## References

1. Storn, R., & Price, K. (1997). Differential evolution–a simple and efficient heuristic for global optimization over continuous spaces.
2. Das, S., & Suganthan, P. N. (2011). Differential evolution: A survey of the state-of-the-art.