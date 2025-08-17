"""
Gaussian Process metamodel implementation using GPy.

This module provides a Gaussian Process surrogate model that can be used
for approximating expensive objective functions. It provides mean predictions
and uncertainty estimates.

Supports two hyperparameter optimization methods:
1. Standard GPy gradient-based optimization (default)
2. Differential Evolution for more robust global optimization
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


class GaussianProcessMetamodel(BaseMetamodel):
    """
    Gaussian Process metamodel using GPy.
    
    This implementation provides a flexible GP surrogate model with various
    kernel options and automatic hyperparameter optimization using either
    standard gradient-based methods or Differential Evolution.
    """
    
    def __init__(self,
                 kernel_type: str = 'rbf',
                 optimize_hyperparameters: bool = True,
                 n_restarts: int = 10,
                 optimization_method: str = 'standard',
                 noise_variance: float = 1e-6,
                 random_state: Optional[int] = None,
                 test_size: float = 0.2,
                 verbose_de: bool = False,
                 **kwargs):
        """
        Initialize the Gaussian Process metamodel.
        
        Args:
            kernel_type: Type of kernel ('rbf', 'matern32', 'matern52')
            optimize_hyperparameters: Whether to optimize hyperparameters
            n_restarts: Number of restarts for standard optimization (ignored for DE)
            optimization_method: Optimization method ('standard' or 'de'/'differential_evolution')
            noise_variance: Initial noise variance for the GP
            random_state: Random seed
            test_size: Fraction for validation
            verbose_de: Whether to show verbose output for DE optimization
            **kwargs: Additional arguments
        """
        super().__init__(random_state=random_state, test_size=test_size, **kwargs)
        
        self.kernel_type = kernel_type
        self.optimize_hyperparameters = optimize_hyperparameters
        self.n_restarts = n_restarts
        self.optimization_method = optimization_method.lower()
        self.noise_variance = noise_variance
        self.verbose_de = verbose_de
        
        # Validate optimization method
        if self.optimization_method in ['de', 'differential_evolution']:
            self.optimization_method = 'de'
        elif self.optimization_method != 'standard':
            raise ValueError(f"Unknown optimization method: {optimization_method}. "
                           "Use 'standard' or 'de'/'differential_evolution'")
        
        # GP model
        self.model = None
        
        # DE configuration
        if self.optimization_method == 'de':
            self.de_config = {
                'pop_size': 30,  # Increased for better exploration
                'max_iterations': 200,  # Increased for better convergence
                'max_iter_without_improvement': 30,  # Stop after 30 iterations without improvement
                'metric_threshold': float('-inf'),  # Don't stop based on metric value
                'verbose': self.verbose_de
            }
            
            # Always use refinement at the end only for DE
            self.refinement_config = {
                'trigger_ratio': -1,  # Only refine at the end
            }
        
    def _fit_model(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Fit the GP model to normalized training data.
        
        Args:
            X_train: Normalized training features
            y_train: Normalized training targets
        """
        # Create kernel
        input_dim = X_train.shape[1]
        if self.kernel_type == 'rbf':
            kernel = GPy.kern.RBF(input_dim, ARD=True)
        elif self.kernel_type == 'matern32':
            kernel = GPy.kern.Matern32(input_dim, ARD=True)
        elif self.kernel_type == 'matern52':
            kernel = GPy.kern.Matern52(input_dim, ARD=True)
        else:
            raise ValueError(f"Unknown kernel type: {self.kernel_type}")
            
        # Create GP model
        self.model = GPy.models.GPRegression(
            X_train, y_train.reshape(-1, 1), 
            kernel,
            noise_var=self.noise_variance,
            normalizer=None  # We handle normalization in base class
        )
        
        # Optimize hyperparameters
        if self.optimize_hyperparameters:
            if self.optimization_method == 'de':
                self._optimize_with_de(X_train, y_train)
            else:
                # Standard GPy optimization
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.model.optimize_restarts(
                        num_restarts=self.n_restarts,
                        messages=False,
                        verbose=False
                    )
    
    def _optimize_with_de(self, X_norm: np.ndarray, y_norm: np.ndarray):
        """
        Optimize GP hyperparameters using Differential Evolution.
        
        Args:
            X_norm: Normalized training features
            y_norm: Normalized training targets
        """        
        from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
        from aivalanche_lib.parameters import Parameters
        
        # Calculate data characteristics for adaptive bounds
        n_dims = X_norm.shape[1]
        n_samples = X_norm.shape[0]
        
        # Estimate data characteristics
        output_var = np.var(y_norm)
        output_std = np.std(y_norm)
        
        # Better bounds based on data
        # Kernel variance should be around the data variance
        kernel_var_min = output_var * 0.01
        kernel_var_max = output_var * 100
        kernel_var_default = output_var
        
        # Define the parameter space for optimization with adaptive bounds
        param_configs = []
        
        param_configs.append({
            'name': 'kernel_variance',
            'type': 'continuous',
            'min': max(1e-10, kernel_var_min),
            'max': min(1e10, kernel_var_max),
            'scale': 'log',
            'default': kernel_var_default
        })
        
        # Length scale(s)
        if self.kernel_type in ['rbf', 'matern32', 'matern52']:
            # ARD: one length scale per dimension
            # Length scales should be related to the data range
            for i in range(n_dims):
                data_range = X_norm[:, i].max() - X_norm[:, i].min()
                # Length scale between 1% and 200% of data range
                ls_min = data_range * 0.01
                ls_max = data_range * 2.0
                ls_default = data_range * 0.3  # Start with 30% of range
                
                param_configs.append({
                    'name': f'length_scale_{i}',
                    'type': 'continuous',
                    'min': max(1e-10, ls_min),
                    'max': min(1e10, ls_max),
                    'scale': 'log',
                    'default': ls_default
                })
        
        # Noise variance should be small relative to output variance
        noise_min = output_var * 1e-6
        noise_max = output_var * 0.5  # At most 50% of signal variance
        noise_default = output_var * 0.01  # Start with 1% noise
        
        param_configs.append({
            'name': 'noise_variance',
            'type': 'continuous',
            'min': max(1e-10, noise_min),
            'max': min(1e3, noise_max),
            'scale': 'log',
            'default': noise_default
        })
        
        # Create parameters object
        param_space = Parameters(param_configs)
        
        # Define the objective function: negative log marginal likelihood
        def eval_func(parameters, **kwargs):
            """Evaluate GP with given hyperparameters."""
            results = []
            
            for _, row in parameters.iterrows():
                try:
                    # Extract hyperparameters
                    kernel_var = row['kernel_variance']
                    noise_var = row['noise_variance']
                    
                    # Extract length scales
                    length_scales = []
                    for i in range(n_dims):
                        if f'length_scale_{i}' in row:
                            length_scales.append(row[f'length_scale_{i}'])
                    length_scales = np.array(length_scales)
                    
                    # Create kernel with these parameters
                    if self.kernel_type == 'rbf':
                        kernel = GPy.kern.RBF(
                            input_dim=n_dims,
                            variance=kernel_var,
                            lengthscale=length_scales,
                            ARD=True
                        )
                    elif self.kernel_type == 'matern32':
                        kernel = GPy.kern.Matern32(
                            input_dim=n_dims,
                            variance=kernel_var,
                            lengthscale=length_scales,
                            ARD=True
                        )
                    elif self.kernel_type == 'matern52':
                        kernel = GPy.kern.Matern52(
                            input_dim=n_dims,
                            variance=kernel_var,
                            lengthscale=length_scales,
                            ARD=True
                        )
                    else:
                        kernel = GPy.kern.RBF(
                            input_dim=n_dims,
                            variance=kernel_var,
                            lengthscale=length_scales,
                            ARD=True
                        )
                    
                    # Create GP model with these hyperparameters
                    model = GPy.models.GPRegression(
                        X_norm,
                        y_norm.reshape(-1, 1),
                        kernel,
                        noise_var=noise_var
                    )
                    
                    # Get the negative log marginal likelihood
                    # Lower is better for log likelihood, but we minimize negative
                    neg_log_likelihood = -model.log_likelihood()
                    
                    results.append({'metric': float(neg_log_likelihood)})
                    
                except Exception as e:
                    # If evaluation fails, return a high penalty
                    if self.de_config['verbose']:
                        print(f"Error evaluating hyperparameters: {e}")
                    results.append({'metric': 1e10})
            
            return results
        
        # Always use refinement at the end only
        refinement_config = self.refinement_config.copy()
        
        # Run DE optimization with refinement at the end
        de = DifferentialEvolution(
            seed=self.random_state if self.random_state is not None else 42,
            eval_func=eval_func,
            parameters=param_space,
            pop_size=self.de_config['pop_size'],
            max_iterations=self.de_config['max_iterations'],
            max_iter_without_improvement=self.de_config['max_iter_without_improvement'],
            metric_threshold=self.de_config['metric_threshold'],
            refinement_mode='on',  # Use DLS refinement for fine-tuning
            refinement_config={
                'trigger_ratio': -1,  # Only at end
                'method': 'dls',
                'max_iterations': 50,  # Limit refinement iterations
                'max_iter_without_improvement': 10
            },
            adaptive_boundaries_mode='on'
        )
        
        # Run optimization
        de.run_optimization()
        
        # Extract best hyperparameters
        best_params = de.best_parameters
        kernel_var = best_params['kernel_variance']
        noise_var = best_params['noise_variance']
        
        length_scales = []
        for i in range(n_dims):
            if f'length_scale_{i}' in best_params:
                length_scales.append(best_params[f'length_scale_{i}'])
        length_scales = np.array(length_scales)
        
        if self.de_config['verbose']:
            print(f"[GP-DE] Optimization complete!")
            print(f"[GP-DE] Best negative log-likelihood: {de.best_metric:.4f}")
            print(f"[GP-DE] Kernel variance: {kernel_var:.4f}")
            print(f"[GP-DE] Length scales: {length_scales}")
            print(f"[GP-DE] Noise variance: {noise_var:.6e}")
        
        # Update the model with best hyperparameters
        self.model.kern.variance = kernel_var
        self.model.kern.lengthscale = length_scales
        self.model.Gaussian_noise.variance = noise_var
                
    def _predict_model(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions with the GP model.
        
        Args:
            X: Normalized features
            
        Returns:
            Normalized predictions
        """
        y_pred, _ = self.model.predict(X)
        return y_pred.ravel()
        
    def predict_with_uncertainty(self, X: Union[np.ndarray, pd.DataFrame]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions with uncertainty estimates.
        
        Args:
            X: Input features
            
        Returns:
            (predictions, uncertainties)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
            
        # Convert and normalize
        X = self._to_numpy(X)
        X_norm = (X - self.X_min) / (self.X_max - self.X_min)
        
        # Predict with variance
        y_pred_norm, y_var_norm = self.model.predict(X_norm)
        
        # Convert variance to std
        y_std_norm = np.sqrt(np.maximum(y_var_norm, 0))
        
        # Denormalize
        y_pred = y_pred_norm.ravel() * self.y_std + self.y_mean
        y_std = y_std_norm.ravel() * self.y_std
        
        return y_pred, y_std
        
    def get_kernel_parameters(self) -> Dict[str, Any]:
        """Get current kernel hyperparameters."""
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
    
    def get_optimization_info(self) -> Dict[str, Any]:
        """Get information about the optimization process."""
        info = self.get_kernel_parameters()
        if self.optimization_method == 'de':
            info['optimization_method'] = 'differential_evolution_with_refinement'
            info['de_settings'] = {
                'pop_size': self.de_config['pop_size'],
                'max_iter_without_improvement': self.de_config['max_iter_without_improvement']
            }
            info['refinement'] = 'adam_at_end'
        else:
            info['optimization_method'] = 'standard_gpy'
            info['n_restarts'] = self.n_restarts
        return info
    
    def set_verbose(self, verbose: bool = True):
        """Enable or disable verbose output during DE optimization.
        
        Args:
            verbose: Whether to print optimization progress
        """
        if hasattr(self, 'de_config'):
            self.de_config['verbose'] = verbose
            self.verbose_de = verbose