# ADAM (Adaptive Moment Estimation) Optimizer

## Overview

ADAM is a first-order gradient-based optimization algorithm that combines the advantages of two popular methods: AdaGrad and RMSProp. Introduced by Kingma and Ba in 2014, ADAM has become one of the most popular optimization algorithms in machine learning and deep learning due to its adaptive learning rates and momentum.

## How ADAM Works

### Basic Principles

ADAM maintains two moving averages for each parameter:
1. **First moment (m)**: Exponential moving average of gradients (momentum)
2. **Second moment (v)**: Exponential moving average of squared gradients (adaptive learning rates)

These moments are used to compute adaptive learning rates for each parameter individually.

### Algorithm Steps

1. **Initialization**: Set initial parameters, m = 0, v = 0
2. **For each iteration t**:
   - **Compute gradient**: g = ∇f(θ)
   - **Update biased first moment**: m = β₁·m + (1-β₁)·g
   - **Update biased second moment**: v = β₂·v + (1-β₂)·g²
   - **Bias correction**: m̂ = m/(1-β₁ᵗ), v̂ = v/(1-β₂ᵗ)
   - **Update parameters**: θ = θ - α·m̂/(√v̂ + ε)
3. **Termination**: Stop when convergence criteria are met

### Key Features

- **Adaptive learning rates**: Different learning rate for each parameter
- **Momentum**: Uses moving average of gradients for smoother convergence
- **Bias correction**: Compensates for initialization bias in early iterations
- **Scale-invariant**: Works well with different parameter scales
- **Memory efficient**: Only stores two additional values per parameter

### Mathematical Foundation

The update rule combines momentum and adaptive learning rates:

```
θₜ₊₁ = θₜ - α · m̂ₜ / (√v̂ₜ + ε)
```

Where:
- α = learning rate
- m̂ₜ = bias-corrected first moment estimate
- v̂ₜ = bias-corrected second moment estimate
- ε = small constant for numerical stability

## Using the Adam Class

### Basic Usage

```python
from aivalanche_lib.optimization.adam import Adam
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
optimizer = Adam(
    eval_func=eval_func,
    parameters=Parameters(param_config),
    opt_min_or_max='min',
    max_iterations=100,
    learning_rate=0.01,
    beta1=0.9,
    beta2=0.999
)

optimizer.run_optimization()

# Access results
print(f"Best metric: {optimizer.best_metric}")
print(f"Best parameters: {optimizer.best_parameters}")
```

### Advanced Features

#### 1. Gradient Estimation Methods

Since ADAM requires gradients, the implementation provides gradient estimation:

```python
optimizer = Adam(
    # ... other parameters ...
    gradient_method='finite_difference',  # or 'simultaneous_perturbation'
    gradient_step_size=1e-5,
    gradient_step_size_relative=True  # Relative to parameter value
)
```

#### 2. Learning Rate Schedules

```python
# Constant learning rate
optimizer = Adam(
    # ... other parameters ...
    learning_rate=0.001
)

# Learning rate decay
optimizer = Adam(
    # ... other parameters ...
    learning_rate=0.1,
    learning_rate_decay=0.01  # lr = lr / (1 + decay * iteration)
)
```

#### 3. AMSGrad Variant

AMSGrad fixes a convergence issue in the original ADAM:

```python
optimizer = Adam(
    # ... other parameters ...
    amsgrad=True  # Uses maximum of v_hat for more stable convergence
)
```

#### 4. Boundary Handling

```python
optimizer = Adam(
    # ... other parameters ...
    boundary_handling='clip',  # Options: 'clip', 'reflect', 'none'
)
```

#### 5. Initial Point Specification

```python
# Start from specific point
initial_point = pd.DataFrame({'param1': [1.0], 'param2': [2.0]})
optimizer = Adam(
    # ... other parameters ...
    initial_point=initial_point
)

# Start from parameter defaults
optimizer = Adam(
    # ... other parameters ...
    use_defaults_in_initial_point=True
)
```

### Stopping Criteria

```python
optimizer = Adam(
    # ... other parameters ...
    max_iterations=1000,
    metric_threshold=1e-6,           # Stop if metric below threshold
    max_iter_without_improvement=50, # Patience
    improvement_threshold=1e-4,      # Minimum improvement
    gradient_tolerance=1e-6          # Stop if gradient norm below threshold
)
```

### Callbacks

```python
def callback_each_iter(**kwargs):
    print(f"Iteration {kwargs['iteration']}: "
          f"Metric = {kwargs['parameters']['metric']}, "
          f"Gradient norm = {kwargs['gradient_norm']:.6e}")

optimizer = Adam(
    # ... other parameters ...
    callback_after_each_iter=callback_each_iter,
    callback_after_better_solution=lambda **kw: print("New best found!")
)
```

### Visualization and Analysis

```python
# Plot metrics evolution
fig, ax = optimizer.plot_metrics()

# Plot gradient norm evolution
fig, ax = optimizer.plot_gradient_norm()

# Plot learning rate evolution (if using decay)
fig, ax = optimizer.plot_learning_rate()

# Plot parameter evolution
fig, axes = optimizer.plot_parameters_evolution()

# Create optimization summary plot
from aivalanche_lib.optimization.adam.visualizations import _plot_optimization_summary
fig = _plot_optimization_summary(optimizer)

# Create animation (for 2D problems)
from aivalanche_lib.optimization.adam.visualizations import _create_convergence_animation
anim = _create_convergence_animation(optimizer, save_path='adam_animation.gif')

# Save results
optimizer.write_best_parameters_to_file('best_params.csv')
optimizer.write_optimization_info_to_file('opt_info.json')
optimizer.write_history_to_file('points', 'history.csv')
```

## Parameter Guidelines

### Learning Rate (α)
- Typical range: 0.0001 - 0.1
- Default: 0.001 (good for many problems)
- Too high: Unstable, divergence
- Too low: Slow convergence

### Beta1 (β₁) - Momentum
- Typical range: 0.8 - 0.95
- Default: 0.9
- Controls exponential decay for first moment
- Higher values = more momentum

### Beta2 (β₂) - RMSProp term
- Typical range: 0.99 - 0.999
- Default: 0.999
- Controls exponential decay for second moment
- Higher values = longer memory of past gradients

### Epsilon (ε)
- Default: 1e-8
- Prevents division by zero
- Rarely needs adjustment

### Gradient Estimation
- **Step size**: 1e-5 to 1e-3
- **Finite difference**: More accurate, more evaluations
- **Simultaneous perturbation**: Fewer evaluations, less accurate

## When to Use ADAM

**Good for:**
- Non-convex optimization problems
- Problems with noisy or sparse gradients
- High-dimensional parameter spaces
- When different parameters need different learning rates
- Online and batch learning
- Neural network training

**Not ideal for:**
- Simple convex problems (use gradient descent)
- When exact gradients are expensive to compute
- Problems requiring guaranteed convergence
- When memory is extremely limited
- Simple low-dimensional problems

## Comparison with Other Methods

### vs. Gradient Descent
- ADAM: Adaptive learning rates, faster convergence
- GD: Simpler, better theoretical guarantees

### vs. Differential Evolution
- ADAM: Gradient-based, faster on smooth problems
- DE: Derivative-free, better for multimodal problems

### vs. Nelder-Mead
- ADAM: Uses gradient information, scales better
- NM: No gradients needed, better for non-smooth functions

## Common Issues and Solutions

1. **Poor gradient estimates**:
   - Increase gradient step size
   - Use more function evaluations
   - Try simultaneous perturbation method

2. **Slow convergence**:
   - Increase learning rate
   - Decrease beta1 for less momentum
   - Check gradient estimation accuracy

3. **Oscillations**:
   - Decrease learning rate
   - Increase beta1 for more momentum
   - Enable learning rate decay

4. **Stuck in local minimum**:
   - Use multiple random starts
   - Increase initial learning rate
   - Combine with global search method

## Tips for Effective Use

1. **Parameter scaling**: Normalize parameters to similar ranges
2. **Learning rate tuning**: Start with 0.001, adjust based on convergence
3. **Monitor gradients**: Check gradient norms for vanishing/exploding gradients
4. **Warm restarts**: Periodically reset learning rate for better exploration
5. **Hybrid approach**: Use with global optimizer for initial search

## Algorithm Variants

1. **AdaMax**: Uses infinity norm instead of L2 norm
2. **NAdam**: Nesterov-accelerated ADAM
3. **AdaBound**: ADAM with dynamic bounds on learning rates
4. **RAdam**: Rectified ADAM with variance reduction

## Mathematical Details

### Bias Correction

The bias correction is necessary because m and v are initialized to zero:

```
E[mₜ] = E[g] · (1 - β₁ᵗ)
E[vₜ] = E[g²] · (1 - β₂ᵗ)
```

### Convergence Properties

Under certain conditions, ADAM converges to stationary points:
- Bounded gradients
- β₁ < √β₂
- Appropriate learning rate schedule

## References

1. Kingma, D. P., & Ba, J. (2014). Adam: A method for stochastic optimization.
2. Reddi, S. J., Kale, S., & Kumar, S. (2018). On the convergence of Adam and beyond.
3. Loshchilov, I., & Hutter, F. (2019). Decoupled weight decay regularization.