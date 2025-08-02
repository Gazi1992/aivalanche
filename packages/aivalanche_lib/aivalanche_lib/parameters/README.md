# Parameters Module

A flexible and powerful parameter management system for optimization algorithms in the aivalanche library.

## Overview

The Parameters module provides a unified interface for defining, managing, and transforming parameters used in optimization algorithms. It supports multiple parameter types, automatic scaling/normalization, and batch operations.

## Features

- **Multiple Parameter Types**:
  - `ContinuousParameter`: Real-valued parameters with min/max bounds
  - `DiscreteParameter`: Integer or discrete-valued parameters
  - `CategoricalParameter`: Parameters with a set of named categories

- **Automatic Transformations**:
  - Linear and logarithmic scaling
  - Automatic selection of appropriate log transform (standard, negative, or symmetric)
  - Normalization to [0, 1] range for optimization algorithms

- **Flexible Input Formats**:
  - Direct parameter type instances
  - List of parameter definition dictionaries
  - CSV or JSON configuration files
  - Pandas DataFrames

- **Batch Operations**:
  - Normalize/denormalize multiple parameters at once
  - Support for arrays, dictionaries, DataFrames, and lists of dictionaries
  - Efficient vectorized operations

## Installation

The Parameters module is included with the aivalanche_lib package.

## Quick Start

### Basic Usage

```python
from aivalanche_lib.parameters import Parameters, ContinuousParameter, DiscreteParameter, CategoricalParameter

# Create parameters directly
params = Parameters([
    ContinuousParameter('learning_rate', min_val=0.001, max_val=1.0, default=0.1, scale='log'),
    DiscreteParameter('batch_size', values=[16, 32, 64, 128]),
    CategoricalParameter('optimizer', categories=['adam', 'sgd', 'rmsprop'], default='adam')
])

# Access parameter information
print(params.names)  # ['batch_size', 'learning_rate', 'optimizer']
print(params.n_variable)  # Number of variable parameters
print(params.n_continuous)  # Number of continuous parameters
```

### Creating Parameters from Dictionaries

```python
# Define parameters as a list of dictionaries
param_defs = [
    {
        'name': 'x1',
        'type': 'continuous',
        'min': -5.0,
        'max': 5.0,
        'default': 0.0,
        'scale': 'lin'
    },
    {
        'name': 'x2',
        'type': 'discrete',
        'min': 1,
        'max': 10,
        'step': 1,
        'default': 5
    }
]

params = Parameters(param_defs)
```

### Loading from Files

```python
# From JSON file
params = Parameters('parameters.json')

# From CSV file
params = Parameters('parameters.csv')
```

### Normalization and Denormalization

```python
# Normalize values to [0, 1] range
values = {'learning_rate': 0.01, 'batch_size': 32, 'optimizer': 'sgd'}
normalized = params.norm_all(values)
print(normalized)  # {'learning_rate': 0.5, 'batch_size': 0.333..., 'optimizer': 1}

# Denormalize back to original scale
original = params.unnorm_all(normalized)
print(original)  # {'learning_rate': 0.01, 'batch_size': 32, 'optimizer': 'sgd'}
```

### Working with DataFrames

```python
import pandas as pd

# Create a DataFrame of parameter values
df = pd.DataFrame([
    {'learning_rate': 0.01, 'batch_size': 32, 'optimizer': 'adam'},
    {'learning_rate': 0.1, 'batch_size': 64, 'optimizer': 'sgd'}
])

# Normalize all values
normalized_df = params.norm_all(df)

# Denormalize back
original_df = params.unnorm_all(normalized_df)
```

## Parameter Types

### ContinuousParameter

Real-valued parameters with bounds and optional scaling.

```python
# Linear scale (default)
param1 = ContinuousParameter('temperature', min_val=0.0, max_val=100.0, default=25.0)

# Logarithmic scale
param2 = ContinuousParameter('learning_rate', min_val=1e-5, max_val=1.0, default=1e-3, scale='log')

# Fixed parameter (not varied during optimization)
param3 = ContinuousParameter('constant', min_val=0.0, max_val=1.0, default=0.5, mode='fixed')
```

### DiscreteParameter

Parameters that take discrete values, either from a list or a range.

```python
# From a list of values
param1 = DiscreteParameter('layers', values=[1, 2, 4, 8, 16])

# From a range with step
param2 = DiscreteParameter('epochs', min_val=10, max_val=100, step=10)

# With logarithmic scale
param3 = DiscreteParameter('batch_size', values=[1, 2, 4, 8, 16, 32, 64], scale='log')
```

### CategoricalParameter

Parameters with named categories.

```python
param = CategoricalParameter(
    'activation',
    categories=['relu', 'tanh', 'sigmoid', 'elu'],
    default='relu'
)
```

## File Formats

### JSON Format

```json
[
    {
        "name": "learning_rate",
        "type": "continuous",
        "min": 0.0001,
        "max": 1.0,
        "default": 0.01,
        "scale": "log",
        "mode": "variable"
    },
    {
        "name": "hidden_units",
        "type": "discrete",
        "values": [32, 64, 128, 256],
        "default": 128
    },
    {
        "name": "activation",
        "type": "categorical",
        "values": ["relu", "tanh", "sigmoid"],
        "default": "relu"
    }
]
```

### CSV Format

```csv
name,type,min,max,step,values,default,scale,mode
learning_rate,continuous,0.0001,1.0,,,0.01,log,variable
hidden_units,discrete,,,,"32,64,128,256",128,,variable
activation,categorical,,,,"relu,tanh,sigmoid",relu,,variable
```

## Advanced Features

### Random Sampling

```python
# Generate random parameter values
samples = params.sample_random(n_samples=10, random_state=42)
print(samples)  # DataFrame with 10 rows of random parameter values

# Get a single random sample as a dictionary
single_sample = params.sample_random(n_samples=1, output_format='dict')
```

### Parameter Filtering

```python
# Get specific parameter types
continuous_params = params.get_continuous_parameters()
variable_params = params.get_variable_parameters()

# Get parameter bounds
bounds = params.get_bounds(only_variable=True)
print(bounds)  # {'learning_rate': (0.001, 1.0), 'batch_size': (0, 3), ...}
```

### Default Values

```python
# Get all default values
defaults = params.get_defaults()
print(defaults)  # {'learning_rate': 0.1, 'batch_size': 32, 'optimizer': 'adam'}
```

## Integration with Optimizers

The Parameters module is designed to work seamlessly with optimization algorithms:

```python
from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution

# Define parameters
params = Parameters([
    ContinuousParameter('x1', -5, 5, 0),
    ContinuousParameter('x2', -5, 5, 0)
])

# Create optimizer
optimizer = DifferentialEvolution(
    parameters=params,
    eval_func=my_objective_function,
    max_iterations=100
)

# Run optimization
optimizer.run_optimization()
```

## Scale Transformations

The module automatically selects appropriate transformations for logarithmic scaling:

- **Positive values only**: Standard log transform
- **Negative values only**: Negative log transform (-log(-x))
- **Mixed positive/negative**: Symmetric log transform (handles zero-crossing)

```python
# Automatic transform selection
param1 = ContinuousParameter('pos_param', 0.1, 100, scale='log')  # Uses LogTransform
param2 = ContinuousParameter('neg_param', -100, -0.1, scale='log')  # Uses NegLogTransform
param3 = ContinuousParameter('mixed_param', -100, 100, scale='log')  # Uses SymLogTransform
```

## Best Practices

1. **Use descriptive parameter names**: Makes configuration files more readable
2. **Set reasonable defaults**: Provide good starting points for optimization
3. **Choose appropriate scales**: Use log scale for parameters that vary over orders of magnitude
4. **Document parameter meanings**: Use the `description` field when creating parameters
5. **Validate parameter ranges**: Ensure min/max bounds are physically meaningful

## API Reference

### Parameters Class

- `__init__(parameters)`: Create from various input formats
- `norm_all(values)`: Normalize parameter values to [0, 1]
- `unnorm_all(norm_values)`: Denormalize values back to original scale
- `sample_random(n_samples, random_state, output_format)`: Generate random samples
- `get_parameter(name)`: Get a specific parameter by name
- `get_defaults()`: Get default values for all parameters
- `get_bounds(only_variable)`: Get parameter bounds
- `to_dict()`: Export parameters as list of dictionaries

### Properties

- `names`: List of all parameter names
- `variable_names`: List of variable parameter names
- `fixed_names`: List of fixed parameter names
- `n_parameters`: Total number of parameters
- `n_variable`: Number of variable parameters
- `n_fixed`: Number of fixed parameters
- `n_continuous`: Number of continuous parameters
- `n_discrete`: Number of discrete parameters
- `n_categorical`: Number of categorical parameters

## Examples

See the `tests/` directory for comprehensive examples of using the Parameters module in various scenarios.