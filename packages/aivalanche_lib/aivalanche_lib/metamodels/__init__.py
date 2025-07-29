"""
Metamodels package for surrogate modeling in optimization.

This package provides various metamodel (surrogate model) implementations
that can be used to approximate expensive objective functions during optimization.
"""

from .base import BaseMetamodel
from .gaussian_process import GaussianProcessMetamodel
from .evaluator import MetamodelEvaluator, AcquisitionStrategy

__all__ = [
    'BaseMetamodel',
    'GaussianProcessMetamodel',
    'MetamodelEvaluator',
    'AcquisitionStrategy',
]

# Version info
__version__ = '0.1.0'