"""
Base classes for metamodel implementations.

This module provides the abstract base class that all metamodel implementations
should inherit from, ensuring a consistent interface across different surrogate
modeling techniques.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple, Union
import numpy as np
import pandas as pd


class BaseMetamodel(ABC):
    """
    Abstract base class for metamodel implementations.
    
    This class defines the interface that all metamodel implementations must follow.
    Metamodels (surrogate models) are used to approximate expensive objective functions
    based on a limited set of evaluated points.
    """
    
    def __init__(self, 
                 input_dim: Optional[int] = None,
                 output_dim: int = 1,
                 normalize_inputs: bool = True,
                 normalize_outputs: bool = True,
                 random_state: Optional[int] = None,
                 **kwargs):
        """
        Initialize the base metamodel.
        
        Args:
            input_dim: Number of input dimensions (features)
            output_dim: Number of output dimensions (typically 1 for single objective)
            normalize_inputs: Whether to normalize inputs to [0, 1]
            normalize_outputs: Whether to normalize outputs (standardize)
            random_state: Random seed for reproducibility
            **kwargs: Additional model-specific parameters
        """
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.normalize_inputs = normalize_inputs
        self.normalize_outputs = normalize_outputs
        self.random_state = random_state
        
        # Training data storage
        self.X_train = None
        self.y_train = None
        self.n_samples = 0
        
        # Normalization parameters
        self.X_min = None
        self.X_max = None
        self.y_mean = None
        self.y_std = None
        
        # Model state
        self.is_fitted = False
        
    @abstractmethod
    def fit(self, X: Union[np.ndarray, pd.DataFrame], 
            y: Union[np.ndarray, pd.Series]) -> 'BaseMetamodel':
        """
        Fit the metamodel to training data.
        
        Args:
            X: Input features of shape (n_samples, n_features)
            y: Target values of shape (n_samples,) or (n_samples, n_outputs)
            
        Returns:
            self: The fitted metamodel instance
        """
        pass
    
    @abstractmethod
    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Make predictions using the metamodel.
        
        Args:
            X: Input features of shape (n_samples, n_features)
            
        Returns:
            Predictions of shape (n_samples,) or (n_samples, n_outputs)
        """
        pass
    
    @abstractmethod
    def predict_with_uncertainty(self, X: Union[np.ndarray, pd.DataFrame]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions with uncertainty estimates.
        
        Args:
            X: Input features of shape (n_samples, n_features)
            
        Returns:
            Tuple of (predictions, uncertainties), each of shape (n_samples,)
        """
        pass
    
    def update(self, X_new: Union[np.ndarray, pd.DataFrame], 
               y_new: Union[np.ndarray, pd.Series]) -> 'BaseMetamodel':
        """
        Update the metamodel with new data points.
        
        Default implementation appends new data and refits. Subclasses may
        implement more efficient incremental updates.
        
        Args:
            X_new: New input features
            y_new: New target values
            
        Returns:
            self: The updated metamodel instance
        """
        # Convert to numpy arrays
        X_new = self._to_numpy(X_new)
        y_new = self._to_numpy(y_new)
        
        if self.X_train is None:
            self.X_train = X_new
            self.y_train = y_new
        else:
            self.X_train = np.vstack([self.X_train, X_new])
            self.y_train = np.concatenate([self.y_train, y_new])
        
        # Refit the model
        return self.fit(self.X_train, self.y_train)
    
    def _to_numpy(self, data: Union[np.ndarray, pd.DataFrame, pd.Series]) -> np.ndarray:
        """Convert input data to numpy array."""
        if isinstance(data, (pd.DataFrame, pd.Series)):
            return data.values
        return np.asarray(data)
    
    def _normalize_inputs(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        """
        Normalize inputs to [0, 1] range.
        
        Args:
            X: Input features
            fit: Whether to fit normalization parameters
            
        Returns:
            Normalized inputs
        """
        if not self.normalize_inputs:
            return X
            
        if fit:
            self.X_min = X.min(axis=0)
            self.X_max = X.max(axis=0)
            # Avoid division by zero
            self.X_range = self.X_max - self.X_min
            self.X_range[self.X_range == 0] = 1.0
        
        return (X - self.X_min) / self.X_range
    
    def _denormalize_inputs(self, X_norm: np.ndarray) -> np.ndarray:
        """Denormalize inputs from [0, 1] range."""
        if not self.normalize_inputs:
            return X_norm
        return X_norm * self.X_range + self.X_min
    
    def _normalize_outputs(self, y: np.ndarray, fit: bool = False) -> np.ndarray:
        """
        Normalize outputs (standardize to zero mean, unit variance).
        
        Args:
            y: Target values
            fit: Whether to fit normalization parameters
            
        Returns:
            Normalized outputs
        """
        if not self.normalize_outputs:
            return y
            
        if fit:
            self.y_mean = y.mean(axis=0)
            self.y_std = y.std(axis=0)
            # Avoid division by zero
            self.y_std[self.y_std == 0] = 1.0
        
        return (y - self.y_mean) / self.y_std
    
    def _denormalize_outputs(self, y_norm: np.ndarray) -> np.ndarray:
        """Denormalize outputs."""
        if not self.normalize_outputs:
            return y_norm
        return y_norm * self.y_std + self.y_mean
    
    def _denormalize_uncertainty(self, uncertainty_norm: np.ndarray) -> np.ndarray:
        """Denormalize uncertainty estimates."""
        if not self.normalize_outputs:
            return uncertainty_norm
        return uncertainty_norm * self.y_std
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the metamodel.
        
        Returns:
            Dictionary containing model information
        """
        return {
            'model_type': self.__class__.__name__,
            'input_dim': self.input_dim,
            'output_dim': self.output_dim,
            'n_samples': self.n_samples,
            'is_fitted': self.is_fitted,
            'normalize_inputs': self.normalize_inputs,
            'normalize_outputs': self.normalize_outputs,
        }
    
    def reset(self) -> None:
        """Reset the metamodel to its initial state."""
        self.X_train = None
        self.y_train = None
        self.n_samples = 0
        self.X_min = None
        self.X_max = None
        self.y_mean = None
        self.y_std = None
        self.is_fitted = False