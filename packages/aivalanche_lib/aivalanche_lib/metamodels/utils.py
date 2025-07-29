"""
Utility functions for metamodel implementations.

This module provides common functionality used across different metamodel types,
including acquisition functions, sampling strategies, and validation utilities.
"""

import numpy as np
from typing import Union, Tuple, Optional, Callable
from scipy.stats import norm


def expected_improvement(mean: np.ndarray, std: np.ndarray, 
                        best_value: float, minimize: bool = True) -> np.ndarray:
    """
    Calculate Expected Improvement acquisition function.
    
    Args:
        mean: Predicted mean values
        std: Predicted standard deviations
        best_value: Best observed value so far
        minimize: Whether we're minimizing (True) or maximizing (False)
        
    Returns:
        Expected improvement values
    """
    if minimize:
        improvement = best_value - mean
    else:
        improvement = mean - best_value
    
    # Avoid division by zero
    mask = std > 0
    ei = np.zeros_like(mean)
    
    if np.any(mask):
        z = improvement[mask] / std[mask]
        ei[mask] = improvement[mask] * norm.cdf(z) + std[mask] * norm.pdf(z)
    
    return ei


def probability_of_improvement(mean: np.ndarray, std: np.ndarray,
                              best_value: float, minimize: bool = True) -> np.ndarray:
    """
    Calculate Probability of Improvement acquisition function.
    
    Args:
        mean: Predicted mean values
        std: Predicted standard deviations
        best_value: Best observed value so far
        minimize: Whether we're minimizing (True) or maximizing (False)
        
    Returns:
        Probability of improvement values
    """
    if minimize:
        improvement = best_value - mean
    else:
        improvement = mean - best_value
    
    # Avoid division by zero
    mask = std > 0
    pi = np.zeros_like(mean)
    
    if np.any(mask):
        z = improvement[mask] / std[mask]
        pi[mask] = norm.cdf(z)
    
    return pi


def upper_confidence_bound(mean: np.ndarray, std: np.ndarray,
                          kappa: float = 2.0, minimize: bool = True) -> np.ndarray:
    """
    Calculate Upper Confidence Bound acquisition function.
    
    Args:
        mean: Predicted mean values
        std: Predicted standard deviations
        kappa: Exploration parameter (higher = more exploration)
        minimize: Whether we're minimizing (True) or maximizing (False)
        
    Returns:
        UCB values
    """
    if minimize:
        return mean - kappa * std
    else:
        return mean + kappa * std


def latin_hypercube_sampling(n_samples: int, n_dims: int, 
                           bounds: Optional[np.ndarray] = None,
                           random_state: Optional[int] = None) -> np.ndarray:
    """
    Generate Latin Hypercube Samples.
    
    Args:
        n_samples: Number of samples to generate
        n_dims: Number of dimensions
        bounds: Array of shape (n_dims, 2) with min/max bounds for each dimension
                If None, uses [0, 1] for all dimensions
        random_state: Random seed
        
    Returns:
        Array of shape (n_samples, n_dims) with LHS samples
    """
    rng = np.random.RandomState(random_state)
    
    # Generate samples in unit hypercube
    samples = np.zeros((n_samples, n_dims))
    for i in range(n_dims):
        # Create equally spaced intervals
        intervals = np.linspace(0, 1, n_samples + 1)
        # Random point within each interval
        for j in range(n_samples):
            samples[j, i] = rng.uniform(intervals[j], intervals[j + 1])
        # Shuffle the dimension
        rng.shuffle(samples[:, i])
    
    # Scale to bounds if provided
    if bounds is not None:
        for i in range(n_dims):
            samples[:, i] = samples[:, i] * (bounds[i, 1] - bounds[i, 0]) + bounds[i, 0]
    
    return samples


def cross_validate_metamodel(metamodel_class: type, X: np.ndarray, y: np.ndarray,
                           n_folds: int = 5, random_state: Optional[int] = None,
                           **model_kwargs) -> Tuple[float, float]:
    """
    Perform k-fold cross-validation for a metamodel.
    
    Args:
        metamodel_class: The metamodel class to instantiate
        X: Input features
        y: Target values
        n_folds: Number of cross-validation folds
        random_state: Random seed
        **model_kwargs: Additional arguments for metamodel initialization
        
    Returns:
        Tuple of (mean_rmse, std_rmse) across folds
    """
    n_samples = X.shape[0]
    indices = np.arange(n_samples)
    rng = np.random.RandomState(random_state)
    rng.shuffle(indices)
    
    fold_size = n_samples // n_folds
    rmse_scores = []
    
    for fold in range(n_folds):
        # Define fold indices
        start_idx = fold * fold_size
        end_idx = start_idx + fold_size if fold < n_folds - 1 else n_samples
        
        test_indices = indices[start_idx:end_idx]
        train_indices = np.concatenate([indices[:start_idx], indices[end_idx:]])
        
        # Split data
        X_train, X_test = X[train_indices], X[test_indices]
        y_train, y_test = y[train_indices], y[test_indices]
        
        # Train model
        model = metamodel_class(random_state=random_state, **model_kwargs)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
        rmse_scores.append(rmse)
    
    return np.mean(rmse_scores), np.std(rmse_scores)


def calculate_r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate R-squared score.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        R-squared score
    """
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0


def check_array_shape(X: np.ndarray, expected_dim: Optional[int] = None,
                     name: str = "Input") -> np.ndarray:
    """
    Check and reshape array to ensure correct dimensions.
    
    Args:
        X: Input array
        expected_dim: Expected number of features (columns)
        name: Name for error messages
        
    Returns:
        Reshaped array with at least 2 dimensions
    """
    X = np.asarray(X)
    
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    elif X.ndim > 2:
        raise ValueError(f"{name} must be 1D or 2D array, got {X.ndim}D")
    
    if expected_dim is not None and X.shape[1] != expected_dim:
        raise ValueError(f"{name} has {X.shape[1]} features, expected {expected_dim}")
    
    return X