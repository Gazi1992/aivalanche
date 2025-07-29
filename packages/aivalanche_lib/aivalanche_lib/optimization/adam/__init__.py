"""
ADAM (Adaptive Moment Estimation) Optimizer

A gradient-based optimization algorithm that combines the advantages of two other extensions
of stochastic gradient descent: AdaGrad and RMSProp. ADAM computes adaptive learning rates
for each parameter using estimates of first and second moments of the gradients.
"""

from .Adam import Adam

__all__ = ['Adam']