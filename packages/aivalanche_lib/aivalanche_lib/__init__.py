"""
aivalanche_lib - A Python library for AI and optimization algorithms
"""

__version__ = "0.1.0"

# Import and expose the Parameters class at the package level
from .parameters import Parameters

# Import common submodules
from . import optimization
from . import parameters
from . import utils

# Define what's available with a wildcard import (not recommended but supported)
__all__ = [
    'Parameters',
    'optimization',
    'parameters',
    'utils'
]
