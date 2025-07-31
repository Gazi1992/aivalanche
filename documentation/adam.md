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
