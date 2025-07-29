"""
aivalanche_lib - A Python library for AI and optimization algorithms
"""

__version__ = "0.1.0"

# Import common submodules
from . import optimization
from . import parameters
from . import utils

# Import and expose the Parameters class at the package level
from .parameters.Parameters import Parameters
from .optimization.differential_evolution.DifferentialEvolution import DifferentialEvolution
from .optimization.nelder_mead.NelderMead import NelderMead
from .optimization.adam.Adam import Adam
