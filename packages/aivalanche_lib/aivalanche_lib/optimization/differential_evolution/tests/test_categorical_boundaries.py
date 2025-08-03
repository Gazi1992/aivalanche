"""Test categorical boundaries handling in DE."""

import sys
import os
import numpy as np
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details
from test_utils import create_test_results_dir, create_test_function_wrapper

# Test with a categorical function
test_func = 'string_categorical_mixed_2d'
func_details = get_function_details(test_func)

# Create parameters
params_list = [
    {
        'name': 'x',
        'type': 'continuous',
        'min': -5.0,
        'max': 5.0,
        'default': 0.0
    },
    {
        'name': 'y',
        'type': 'categorical',
        'values': ['a', 'b', 'c'],
        'default': 'a'
    }
]

parameters = Parameters(params_list)
eval_func = create_test_function_wrapper(func_details)

# Create and run optimizer
optimizer = DifferentialEvolution(
    seed=42,
    eval_func=eval_func,
    parameters=parameters,
    pop_size=10,
    max_iterations=5,  # Just a few iterations to check boundaries
    adaptive_boundaries_mode='on'  # Enable adaptive boundaries
)

print(f"Testing: {test_func}")
print("=" * 60)

optimizer.run_optimization()

# Check the history
history = optimizer.history
boundaries = history['boundaries']
boundaries_normed = history['boundaries_normed']

print("\nBoundaries (denormalized):")
print(boundaries)

print("\nBoundaries (normalized):")
print(boundaries_normed)

# Check specific values for categorical parameter
print("\nCategorical parameter 'y' boundary handling:")
# Get available iterations from the boundaries dataframe
available_iters = boundaries.index.get_level_values('iter').unique()
print(f"Available iterations in boundaries: {sorted(available_iters)}")

for iter_num in sorted(available_iters):
    if (iter_num, 'min') in boundaries.index:
        min_val = boundaries.loc[(iter_num, 'min'), 'y']
        max_val = boundaries.loc[(iter_num, 'max'), 'y']
        range_val = boundaries.loc[(iter_num, 'range'), 'y']
        
        print(f"Iteration {iter_num}: min='{min_val}', max='{max_val}', range={range_val}")
    else:
        print(f"Iteration {iter_num}: No boundary data available")

print("\nTest completed successfully!")