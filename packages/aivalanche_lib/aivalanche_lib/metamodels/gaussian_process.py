"""
Gaussian Process metamodel implementation using GPy.

This module provides a Gaussian Process surrogate model that can be used
for approximating expensive objective functions. It provides mean predictions
and uncertainty estimates.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, Tuple, Union
import warnings

try:
    import GPy
except ImportError:
    raise ImportError(
        "GPy is required for Gaussian Process metamodel. "
        "Install it with: pip install GPy"
    )

from .base import BaseMetamodel
from .utils import check_array_shape


class GaussianProcessMetamodel(BaseMetamodel):
    """
    Gaussian Process metamodel using GPy.
    
    This implementation provides a flexible GP surrogate model with various
    kernel options and automatic hyperparameter optimization.
    """
    
    def __init__(self,
                 kernel_type: str = 'rbf',
                 length_scale: Optional[Union[float, np.ndarray]] = None,
                 variance: Optional[float] = None,
                 noise_variance: Optional[float] = None,
                 optimize_hyperparameters: bool = True,
                 n_restarts: int = 10,
                 normalize_inputs: bool = True,
                 normalize_outputs: bool = True,
                 random_state: Optional[int] = None,
                 **kwargs):
        """
        Initialize the Gaussian Process metamodel.
        
        Args:
            kernel_type: Type of kernel to use ('rbf', 'matern32', 'matern52', 'exponential')
            length_scale: Initial length scale(s) for the kernel. If None, will be estimated.
            variance: Initial variance for the kernel. If None, will be estimated.
            noise_variance: Gaussian noise variance. If None, will be estimated.
            optimize_hyperparameters: Whether to optimize hyperparameters
            n_restarts: Number of random restarts for hyperparameter optimization
            normalize_inputs: Whether to normalize inputs to [0, 1]
            normalize_outputs: Whether to standardize outputs
            random_state: Random seed
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(
            normalize_inputs=normalize_inputs,
            normalize_outputs=normalize_outputs,
            random_state=random_state,
            **kwargs
        )
        
        self.kernel_type = kernel_type
        self.length_scale = length_scale
        self.variance = variance
        self.noise_variance = noise_variance
        self.optimize_hyperparameters = optimize_hyperparameters
        self.n_restarts = n_restarts
        
        # GP model placeholder
        self.model = None
        self._kernel = None
        
    def _create_kernel(self, input_dim: int) -> GPy.kern.Kern:
        """
        Create the GP kernel based on specified type.
        
        Args:
            input_dim: Number of input dimensions
            
        Returns:
            GPy kernel object
        """
        # Set initial parameters
        if self.length_scale is None:
            # Default: start with length scale of 0.5 (in normalized space)
            ls = 0.5 * np.ones(input_dim) if self.normalize_inputs else np.ones(input_dim)
        else:
            ls = self.length_scale
            
        if self.variance is None:
            var = 1.0
        else:
            var = self.variance
        
        # Create kernel based on type
        if self.kernel_type == 'rbf':
            kernel = GPy.kern.RBF(input_dim, variance=var, lengthscale=ls, ARD=True)
        elif self.kernel_type == 'matern32':
            kernel = GPy.kern.Matern32(input_dim, variance=var, lengthscale=ls, ARD=True)
        elif self.kernel_type == 'matern52':
            kernel = GPy.kern.Matern52(input_dim, variance=var, lengthscale=ls, ARD=True)
        elif self.kernel_type == 'exponential':
            kernel = GPy.kern.Exponential(input_dim, variance=var, lengthscale=ls, ARD=True)
        else:
            raise ValueError(f"Unknown kernel type: {self.kernel_type}. "
                           f"Supported types: rbf, matern32, matern52, exponential")
        
        return kernel
    
    def fit(self, X: Union[np.ndarray, pd.DataFrame], 
            y: Union[np.ndarray, pd.Series]) -> 'GaussianProcessMetamodel':
        """
        Fit the Gaussian Process to training data.
        
        Args:
            X: Input features of shape (n_samples, n_features)
            y: Target values of shape (n_samples,) or (n_samples, 1)
            
        Returns:
            self: The fitted metamodel instance
        """
        # Convert to numpy
        X = self._to_numpy(X)
        y = self._to_numpy(y)
        
        # Ensure correct shapes
        X = check_array_shape(X, expected_dim=self.input_dim, name="X")
        if y.ndim == 1:
            y = y.reshape(-1, 1)
            
        # Update input dimension if not set
        if self.input_dim is None:
            self.input_dim = X.shape[1]
            
        # Normalize data
        X_norm = self._normalize_inputs(X, fit=True)
        y_norm = self._normalize_outputs(y, fit=True)
        
        # Store training data
        self.X_train = X_norm
        self.y_train = y_norm
        self.n_samples = X.shape[0]
        
        # Create kernel
        self._kernel = self._create_kernel(self.input_dim)
        
        # Create GP model
        self.model = GPy.models.GPRegression(
            X_norm, y_norm, 
            self._kernel,
            normalizer=None  # We handle normalization ourselves
        )
        
        # Set noise variance if specified
        if self.noise_variance is not None:
            self.model.Gaussian_noise.variance = self.noise_variance
            self.model.Gaussian_noise.variance.fix()
        
        # Optimize hyperparameters
        if self.optimize_hyperparameters:
            # Suppress warnings during optimization
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.model.optimize_restarts(
                    num_restarts=self.n_restarts,
                    messages=False,
                    verbose=False
                )
        
        self.is_fitted = True
        return self
    
    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Make predictions using the GP model.
        
        Args:
            X: Input features of shape (n_samples, n_features)
            
        Returns:
            Predictions of shape (n_samples,)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
            
        # Convert and normalize
        X = self._to_numpy(X)
        X = check_array_shape(X, expected_dim=self.input_dim, name="X")
        X_norm = self._normalize_inputs(X)
        
        # Predict
        y_pred_norm, _ = self.model.predict(X_norm)
        
        # Denormalize and return
        y_pred = self._denormalize_outputs(y_pred_norm)
        return y_pred.ravel()
    
    def predict_with_uncertainty(self, X: Union[np.ndarray, pd.DataFrame]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions with uncertainty estimates.
        
        Args:
            X: Input features of shape (n_samples, n_features)
            
        Returns:
            Tuple of (predictions, uncertainties), each of shape (n_samples,)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
            
        # Convert and normalize
        X = self._to_numpy(X)
        X = check_array_shape(X, expected_dim=self.input_dim, name="X")
        X_norm = self._normalize_inputs(X)
        
        # Predict with variance
        y_pred_norm, y_var_norm = self.model.predict(X_norm)
        
        # Convert variance to standard deviation
        y_std_norm = np.sqrt(y_var_norm)
        
        # Denormalize
        y_pred = self._denormalize_outputs(y_pred_norm)
        y_std = self._denormalize_uncertainty(y_std_norm)
        
        return y_pred.ravel(), y_std.ravel()
    
    def get_kernel_parameters(self) -> Dict[str, Any]:
        """
        Get the current kernel hyperparameters.
        
        Returns:
            Dictionary of kernel parameters
        """
        if self.model is None:
            return {}
            
        params = {
            'kernel_type': self.kernel_type,
            'variance': float(self.model.kern.variance),
            'noise_variance': float(self.model.Gaussian_noise.variance),
        }
        
        # Get length scales
        if hasattr(self.model.kern, 'lengthscale'):
            ls = self.model.kern.lengthscale
            if ls.size == 1:
                params['length_scale'] = float(ls)
            else:
                params['length_scale'] = ls.tolist()
                
        return params
    
    def set_kernel_parameters(self, **params) -> None:
        """
        Set kernel hyperparameters manually.
        
        Args:
            **params: Keyword arguments for kernel parameters
                     (variance, length_scale, noise_variance)
        """
        if self.model is None:
            raise ValueError("Model must be fitted before setting parameters")
            
        if 'variance' in params:
            self.model.kern.variance = params['variance']
            
        if 'length_scale' in params:
            self.model.kern.lengthscale = params['length_scale']
            
        if 'noise_variance' in params:
            self.model.Gaussian_noise.variance = params['noise_variance']
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the GP model.
        
        Returns:
            Dictionary containing model information
        """
        info = super().get_info()
        info.update({
            'kernel_type': self.kernel_type,
            'optimize_hyperparameters': self.optimize_hyperparameters,
        })
        
        if self.is_fitted:
            info.update(self.get_kernel_parameters())
            
        return info
    
    def plot(self, X_test: Optional[np.ndarray] = None, 
             show_uncertainty: bool = True,
             confidence_level: float = 0.95) -> None:
        """
        Plot the GP model predictions (for 1D or 2D inputs).
        
        Args:
            X_test: Test points to plot predictions for
            show_uncertainty: Whether to show confidence intervals
            confidence_level: Confidence level for intervals
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before plotting")
            
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("matplotlib is required for plotting")
            
        if self.input_dim == 1:
            # 1D plot
            if X_test is None:
                # Create test points
                X_range = self.X_train.max() - self.X_train.min()
                X_test_norm = np.linspace(
                    self.X_train.min() - 0.1 * X_range,
                    self.X_train.max() + 0.1 * X_range,
                    200
                ).reshape(-1, 1)
            else:
                X_test_norm = self._normalize_inputs(X_test)
                
            # Get predictions
            y_pred_norm, y_var_norm = self.model.predict(X_test_norm)
            y_std_norm = np.sqrt(y_var_norm)
            
            # Denormalize for plotting
            X_plot = self._denormalize_inputs(X_test_norm)
            y_pred = self._denormalize_outputs(y_pred_norm)
            y_std = self._denormalize_uncertainty(y_std_norm)
            
            # Denormalize training data
            X_train_plot = self._denormalize_inputs(self.X_train)
            y_train_plot = self._denormalize_outputs(self.y_train)
            
            # Create plot
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plot predictions
            ax.plot(X_plot, y_pred, 'b-', label='GP mean', linewidth=2)
            
            if show_uncertainty:
                # Confidence intervals
                z_score = 1.96 if confidence_level == 0.95 else 2.58
                lower = y_pred - z_score * y_std
                upper = y_pred + z_score * y_std
                ax.fill_between(X_plot.ravel(), lower.ravel(), upper.ravel(),
                               alpha=0.3, color='blue', 
                               label=f'{confidence_level*100:.0f}% confidence')
            
            # Plot training data
            ax.scatter(X_train_plot, y_train_plot, c='red', s=50, 
                      zorder=5, label='Training data')
            
            ax.set_xlabel('X')
            ax.set_ylabel('y')
            ax.set_title('Gaussian Process Model')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        else:
            print(f"Plotting is only supported for 1D inputs, got {self.input_dim}D")