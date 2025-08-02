"""
Parameter type implementations.

This module provides different parameter types:
- ContinuousParameter: Real-valued parameters within a range
- DiscreteParameter: Integer-valued parameters with optional step
- CategoricalParameter: Parameters that take values from a finite set
"""

from .base import BaseParameterType
from .continuous import ContinuousParameter
from .discrete import DiscreteParameter
from .categorical import CategoricalParameter

__all__ = [
    'BaseParameterType',
    'ContinuousParameter',
    'DiscreteParameter',
    'CategoricalParameter'
]