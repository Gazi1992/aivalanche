# Differential Evolution (DE) Optimizer

## Overview

Differential Evolution (DE) is a robust population-based metaheuristic optimization algorithm. This implementation includes advanced features like adaptive perturbation, local refinement with DLS, and adaptive boundaries, making it suitable for challenging optimization problems.

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
- **Local refinement**: DLS integration for high precision
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

#### 2. Perturbation System

DE now supports a comprehensive perturbation system with many predefined modes:

##### Available Perturbation Modes

1. **`off`** (Default) - No perturbation
2. **`very_light`** - Minimal perturbation only in extreme stagnation
3. **`light`** - Gentle perturbations late in stagnation
4. **`conservative`** - Careful perturbations with moderate strength
5. **`auto`** - Balanced perturbation strategy (recommended)
6. **`moderate`** - More frequent perturbations
7. **`strong`** - Strong perturbations triggered early
8. **`aggressive`** - Very strong and frequent perturbations
9. **`very_aggressive`** - Extreme perturbations for difficult landscapes
10. **`random_walk`** - Random perturbations without memory
11. **`smart_escape`** - Intelligent escape using memory
12. **`periodic`** - Regular perturbations at fixed intervals
13. **`emergency`** - Last resort massive perturbation
14. **`custom`** - User-defined configuration

##### Usage Examples

```python
# Simple usage with predefined mode
optimizer = DifferentialEvolution(
    perturbation_mode='auto'  # Balanced strategy
)

# For smooth landscapes
optimizer = DifferentialEvolution(
    perturbation_mode='light'
)

# For highly multimodal problems
optimizer = DifferentialEvolution(
    perturbation_mode='strong'
)

# Custom configuration
optimizer = DifferentialEvolution(
    perturbation_mode='custom',
    perturbation_config={
        'trigger_ratio': 0.5,           # Trigger after 50% of max_iter_without_improvement
        'param_selection': 'smart',     # 'random', 'variance', 'smart', 'all'
        'param_ratio': (0.2, 0.4),      # Perturb 20-40% of parameters
        'population_ratio': 0.3,        # Perturb 30% of population
        'scale': 'adaptive',            # Perturbation scale
        'memory_enabled': True,         # Track effectiveness
        'cooldown_ratio': 0.2,          # Cooldown period
        'sigma_threshold': 0.02         # Convergence threshold
    }
)
```

##### Choosing the Right Perturbation Mode

```python
from aivalanche_lib.optimization.differential_evolution import suggest_perturbation_mode

# Get suggestion based on problem characteristics
mode = suggest_perturbation_mode(
    problem_type='multimodal',      # Returns 'moderate' or 'strong'
    landscape='many_local_minima',  # Returns 'moderate'
    noise_level='high'              # Returns 'conservative'
)

# Get description of what a mode does
from aivalanche_lib.optimization.differential_evolution import get_perturbation_mode_description
print(get_perturbation_mode_description('auto'))
# Output: "Balanced perturbation strategy. Good general purpose choice."
```

##### Adaptive Perturbation Scaling

When using adaptive scaling modes ('adaptive', 'adaptive_strong', 'adaptive_weak'), the perturbation scale is calculated dynamically:

1. **Base Scale**: 
   ```
   base_scale = max(param_std * 3, param_range * 0.05)
   ```
   - Uses 3 times the parameter's standard deviation in the population
   - Ensures minimum 5% of parameter range even if population has converged
   - Provides exploration proportional to current population spread

2. **Progress Factor**:
   ```
   progress_factor = 1.0 - (iteration / max_iterations) * 0.5
   ```
   - Starts at 1.0 (full scale) and decreases to 0.5 (half scale)
   - Larger perturbations early for exploration
   - Smaller perturbations later for exploitation
   - Similar to temperature scheduling in simulated annealing

3. **Strength Multipliers**:
   - `adaptive`: 1.0x base scale
   - `adaptive_strong`: 1.5x base scale
   - `adaptive_weak`: 0.5x base scale

4. **Memory-based Adjustments** (if enabled):
   
   The memory system tracks the effectiveness of perturbations and adjusts future perturbation scales:

   **a) Reconvergence Speed Multiplier**:
   ```
   reconvergence_mult = 1.0 + param_reconvergence_speed * 0.5
   ```
   - Tracks how quickly each parameter returns to low variance after perturbation
   - If a parameter converges back quickly (within 2-20 iterations to std < 0.01), it indicates a strong attractor
   - Reconvergence speed = 1/(iterations_to_reconverge + 1)
   - Fast reconvergence → Higher multiplier → Larger future perturbations
   - Example: If reconverges in 3 iterations → speed = 0.25 → multiplier = 1.125

   **b) Attempt Count Multiplier**:
   ```
   attempt_mult = 1.0 + (param_perturbation_count * 0.1)
   ```
   - Counts how many times each parameter has been perturbed
   - More attempts → Higher multiplier → More aggressive perturbations
   - Example: After 5 perturbations → multiplier = 1.5

   **c) Success History** (used in parameter selection, not scaling):
   - Tracks if perturbation led to improvement in the objective function
   - Updated using exponential moving average (α = 0.3)
   - Parameters that improve after perturbation are less likely to be selected again

   **Combined Memory Effect**:
   ```
   memory_mult = reconvergence_mult * attempt_mult
   ```
   - Example: Fast reconvergence (1.125) × 5 attempts (1.5) = 1.6875x scale increase
   - This helps escape persistent local minima by progressively increasing perturbation strength

**Example**: For a parameter with std=0.01, range=10, at iteration 50/100:
- Base scale = max(0.03, 0.5) = 0.5
- Progress factor = 1.0 - (50/100) * 0.5 = 0.75
- Final scale = 0.5 * 0.75 = 0.375 (before memory adjustments)

#### 3. Local Refinement with DLS

```python
# Simple usage with predefined modes
optimizer = DifferentialEvolution(
    # ... other parameters ...
    refinement_mode='auto'  # Automatic refinement configuration
)

# Available refinement modes:
# 'off': No refinement
# 'auto': Balanced general-purpose (default)
# 'light': Quick polish with loose tolerances
# 'moderate': Refinement on stagnation
# 'aggressive': Thorough with tight tolerances
# 'high_precision': Ultra-precise refinement
# 'curve_fitting': Optimized for least squares
# 'multi_objective': For multiple objectives
# 'sensitive': Conservative for sensitive problems
# 'custom': User-defined configuration

# Custom refinement configuration
optimizer = DifferentialEvolution(
    # ... other parameters ...
    refinement_mode='custom',
    refinement_config={
        'method': 'dls',
        'max_iterations': 100,
        'trigger': 'on_stagnation',
        'stagnation_threshold': 30,
        'options': {
            'gradient_tolerance': 1e-10,
            'residual_type': 'vector'
        }
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

```python
optimizer = DifferentialEvolution(
    # ... other parameters ...
    adaptive_boundaries=True  # Dynamically adjust search space
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

# Access history
best_history = optimizer.history['bests']  # Best solutions per iteration
trial_history = optimizer.history['trials']  # All trials

# Save results
if optimizer.results_dir:
    # Results are automatically saved to the specified directory
    pass
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
- `auto`: Balanced exploration boost
- `aggressive`: Strong perturbations for tough landscapes
- `conservative`: Gentle perturbations for sensitive problems
- `custom`: Fine-tuned control

### Refinement Modes

DE now supports predefined refinement configurations for different problem types:

#### Available Modes

1. **`auto`** (Default)
   - Balanced general-purpose refinement
   - Triggers on completion
   - Moderate tolerances (1e-8)
   - Good for most problems

2. **`light`**
   - Quick polish with loose tolerances
   - Only 20 iterations
   - Fast but less precise
   - Good for rough optimization

3. **`moderate`**
   - Triggers on stagnation (not just completion)
   - 100 iterations with balanced settings
   - Good for problems that get stuck

4. **`aggressive`**
   - Thorough refinement with tight tolerances (1e-10)
   - 200 iterations
   - Triggers adaptively during optimization
   - Good when precision matters

5. **`high_precision`**
   - Ultra-precise with tolerances down to 1e-12
   - 500 iterations allowed
   - Very conservative damping
   - For problems requiring extreme accuracy

6. **`curve_fitting`**
   - Optimized for least squares problems
   - Uses vector residuals
   - QR decomposition for stability
   - Perfect for data fitting

7. **`multi_objective`**
   - For problems with multiple objectives
   - Vector residuals with balanced settings
   - Triggers on stagnation

8. **`sensitive`**
   - Very conservative settings
   - Large initial damping (10.0)
   - Tiny trust region (0.001)
   - For problems where small changes matter

9. **`custom`**
   - Define your own configuration
   - Full control over all parameters

#### Usage Examples

```python
# Let the system choose refinement settings
optimizer = DifferentialEvolution(
    refinement_mode='auto'
)

# Quick final polish
optimizer = DifferentialEvolution(
    refinement_mode='light'
)

# High precision optimization
optimizer = DifferentialEvolution(
    refinement_mode='high_precision'
)

# Curve fitting problem
optimizer = DifferentialEvolution(
    refinement_mode='curve_fitting'
)

# Fully custom configuration
optimizer = DifferentialEvolution(
    refinement_mode='custom',
    refinement_config={
        'method': 'dls',
        'max_iterations': 150,
        'trigger': 'both',  # During and after
        'stagnation_threshold': 25,
        'adaptive_interval': 75,
        'options': {
            'initial_damping': 0.5,
            'gradient_tolerance': 1e-9,
            'parameter_tolerance': 1e-9,
            'residual_type': 'vector',
            'trust_region_radius': 0.05
        }
    }
)
```

#### Choosing the Right Mode

```python
from aivalanche_lib.optimization.differential_evolution import suggest_refinement_mode

# Get suggestion based on problem type
mode = suggest_refinement_mode(
    problem_type='fitting',      # Returns 'curve_fitting'
    precision_required='high'    # Or would return 'aggressive'
)

# Get description of what a mode does
from aivalanche_lib.optimization.differential_evolution import get_mode_description
print(get_mode_description('auto'))
# Output: "Balanced refinement after DE converges. Good general purpose choice."
```

### Refinement Triggers

Each mode can specify when refinement happens:

- **`on_completion`**: Polish final solution after DE converges
- **`on_stagnation`**: Apply when DE hasn't improved for N iterations
- **`adaptive`**: Apply periodically during optimization
- **`both`**: Apply both adaptively and on completion

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

## Common Issues and Solutions

1. **Slow convergence**: Use adaptive parameters or increase mutation factors
2. **Premature convergence**: Enable perturbation system or increase population
3. **Stagnation**: Use refinement with 'on_stagnation' trigger
4. **Low precision**: Enable local refinement with DLS
5. **Wide search space**: Enable adaptive boundaries

## Directory Structure

```
differential_evolution/
├── DifferentialEvolution.py    # Main optimizer class
├── operators.py               # Core DE operators
├── perturbation.py           # Perturbation system implementation
├── perturbation_modes.py     # Predefined perturbation configurations
├── refinement.py             # DLS integration
├── refinement_modes.py       # Predefined refinement configurations
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