"""
Damped Least Squares (Levenberg-Marquardt) Optimizer Module

This module provides an implementation of the Damped Least Squares algorithm,
also known as the Levenberg-Marquardt algorithm. It's particularly effective
for nonlinear least squares problems and optimization tasks with high sensitivity
to parameter changes (e.g., lens design).
"""

from .DampedLeastSquares import DampedLeastSquares

__all__ = ['DampedLeastSquares']