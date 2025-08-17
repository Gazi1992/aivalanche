"""
Metamodels package for surrogate modeling in optimization.

This package provides various metamodel (surrogate model) implementations
that can be used to approximate expensive objective functions during optimization.
"""

from .base import BaseMetamodel

# Try to import GaussianProcessMetamodel, but don't fail if GPy is not available
try:
    from .gaussian_process import GaussianProcessMetamodel
    # For backward compatibility, alias the main class
    GaussianProcessDEMetamodel = GaussianProcessMetamodel
    __all__ = [
        'BaseMetamodel',
        'GaussianProcessMetamodel',
        'GaussianProcessDEMetamodel',  # Backward compatibility alias
    ]
except ImportError:
    # GPy not available, continue without GP support
    __all__ = [
        'BaseMetamodel',
    ]

# Version info
__version__ = '0.1.0'