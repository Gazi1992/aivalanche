# aivalanche_lib

A Python library for AI optimization algorithms, including differential evolution and Gaussian process methods.

## Installation

### From PyPI

```bash
pip install aivalanche_lib
```

### From Source

```bash
git clone https://github.com/yourusername/aivalanche_lib.git
cd aivalanche_lib
pip install -e .
```

## Features

- **Differential Evolution**: Customizable evolutionary algorithm for complex optimization problems
- **Gaussian Process**: Implementation of GP regression with various kernels
- **Parameter Management**: Tools for handling and validating optimization parameters

## Quick Start

```python
import pandas as pd
from aivalanche_lib.optimization.differential_evolution import Differential_evolution

# Define parameters
parameters = pd.DataFrame({
    'name': ['x1', 'x2'],
    'min': [-5.0, 0.1],
    'max': [5.0, 10.0],
    'default': [0.0, 1.0],
    'scale': ['lin', 'log']
})

# Define evaluation function
def evaluate_func(parameters, **kwargs):
    metrics = []
    for p in parameters:
        x1, x2 = p['x1'], p['x2']
        # Function to minimize
        value = (x1 - 3)**2 + (x2 - 2)**2
        metrics.append(value)
    return {'metrics': metrics}

# Run optimization
optimizer = Differential_evolution(
    parameters=parameters,
    eval_func=evaluate_func,
    pop_size=20,
    max_iterations=50,
    opt_min_or_max='min'
)
optimizer.run_optimization()

# Print results
print(f"Best parameters: {optimizer.get_best_parameters()}")
print(f"Best metric value: {optimizer.best_metric}")
```

## Documentation

For more detailed documentation and examples, please visit [our documentation site](https://aivalanche_lib.readthedocs.io/).

## Requirements

- Python 3.8+
- NumPy
- Pandas
- SciPy
- Scikit-learn
- Matplotlib
- GPy
- pyDOE

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
