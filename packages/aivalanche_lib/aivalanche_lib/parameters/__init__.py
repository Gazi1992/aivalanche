"""
Parameters submodule for aivalanche_lib.

This module provides functionality for managing optimization parameters.
Supports continuous, discrete, and categorical parameter types with
transformations and batch operations.
"""

from .Parameters import Parameters
from .types import (
    ContinuousParameter,
    DiscreteParameter,
    CategoricalParameter
)
from .transformations import (
    NoTransform,
    LogTransform,
    NegLogTransform,
    SymLogTransform
)
from .io import read_json, read_csv, read_dict_list

__all__ = [
    'Parameters',
    'ContinuousParameter',
    'DiscreteParameter',
    'CategoricalParameter',
    'NoTransform',
    'LogTransform',
    'NegLogTransform',
    'SymLogTransform',
    'read_json',
    'read_csv',
    'read_dict_list'
]
