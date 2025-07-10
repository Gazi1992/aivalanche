"""
Optimization Test Functions Package

Provides a collection of standard mathematical functions used for testing
optimization algorithms. Includes function definitions, metadata (bounds, optima),
and plotting utilities for 1D and 2D functions.
"""

# Expose key components directly from the package level
from .definitions import ALL_FUNCTIONS, get_function_details
from .plotting import plot_test_function
from .utils import generate_parameters_config

__version__ = "0.1.0"

__all__ = [
    'ALL_FUNCTIONS',
    'get_function_details',
    'plot_test_function',
    'generate_parameters_config',
]

# You could add a function here to list available functions easily:
def list_available_functions():
    """Returns a list of available test function names."""
    return sorted(list(ALL_FUNCTIONS.keys()))

# Add the listing function to __all__ if you want it importable via *
__all__.append('list_available_functions')
