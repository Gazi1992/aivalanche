"""
Metamodel evaluator for integration with optimization algorithms.

This module provides the MetamodelEvaluator class that acts as a wrapper
around expensive evaluation functions, using metamodels to reduce the number
of actual function evaluations.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List, Callable, Union, Tuple
from enum import Enum
import time

from .base import BaseMetamodel
from .gaussian_process import GaussianProcessMetamodel
from .utils import (
    expected_improvement, probability_of_improvement, 
    upper_confidence_bound, latin_hypercube_sampling
)


class AcquisitionStrategy(Enum):
    """Strategies for deciding when to use metamodel vs actual evaluation."""
    ALL_ACTUAL = "all_actual"  # Always use actual function
    ALL_METAMODEL = "all_metamodel"  # Always use metamodel (after initial training)
    MIXED = "mixed"  # Mix based on acquisition function
    ADAPTIVE = "adaptive"  # Adapt based on metamodel performance
    UNCERTAINTY = "uncertainty"  # Use actual when uncertainty is high
    PERIODIC = "periodic"  # Periodically validate with actual function


class MetamodelEvaluator:
    """
    Wrapper for evaluation functions that uses metamodels to reduce expensive evaluations.
    
    This class manages the interaction between actual function evaluations and
    metamodel predictions, deciding when to use each based on the specified strategy.
    """
    
    def __init__(self,
                 actual_eval_func: Callable,
                 metamodel: Optional[BaseMetamodel] = None,
                 acquisition_strategy: Union[str, AcquisitionStrategy] = AcquisitionStrategy.MIXED,
                 acquisition_function: str = "expected_improvement",
                 min_training_points: int = 20,
                 max_training_points: Optional[int] = None,
                 update_frequency: int = 5,
                 uncertainty_threshold: float = 0.2,
                 validation_frequency: int = 10,
                 exploration_ratio: float = 0.2,
                 enable_caching: bool = True,
                 verbose: bool = False):
        """
        Initialize the metamodel evaluator.
        
        Args:
            actual_eval_func: The actual (expensive) evaluation function
            metamodel: Metamodel instance (if None, uses default GP)
            acquisition_strategy: Strategy for choosing between actual/metamodel
            acquisition_function: Which acquisition function to use for MIXED strategy
            min_training_points: Minimum points before using metamodel
            max_training_points: Maximum training points to keep (for memory)
            update_frequency: How often to retrain the metamodel
            uncertainty_threshold: Threshold for UNCERTAINTY strategy
            validation_frequency: How often to validate for PERIODIC strategy
            exploration_ratio: Ratio of exploratory evaluations for MIXED strategy
            enable_caching: Whether to cache actual evaluations
            verbose: Whether to print information about evaluations
        """
        self.actual_eval_func = actual_eval_func
        self.metamodel = metamodel or GaussianProcessMetamodel()
        
        # Strategy settings
        if isinstance(acquisition_strategy, str):
            acquisition_strategy = AcquisitionStrategy(acquisition_strategy)
        self.acquisition_strategy = acquisition_strategy
        self.acquisition_function = acquisition_function
        
        # Training settings
        self.min_training_points = min_training_points
        self.max_training_points = max_training_points
        self.update_frequency = update_frequency
        
        # Strategy-specific settings
        self.uncertainty_threshold = uncertainty_threshold
        self.validation_frequency = validation_frequency
        self.exploration_ratio = exploration_ratio
        
        # Other settings
        self.enable_caching = enable_caching
        self.verbose = verbose
        
        # State tracking
        self.training_X = []
        self.training_y = []
        self.n_actual_evals = 0
        self.n_metamodel_evals = 0
        self.evaluations_since_update = 0
        self.total_evaluations = 0
        self.metamodel_trained = False
        
        # Performance tracking
        self.validation_errors = []
        self.actual_eval_times = []
        self.metamodel_eval_times = []
        
        # Cache for actual evaluations
        self.evaluation_cache = {} if enable_caching else None
        
        # Best observed value (for acquisition functions)
        self.best_observed = None
        self.minimize = True  # Will be set based on optimizer
        
    def __call__(self, parameters: pd.DataFrame, **kwargs) -> List[Dict[str, Any]]:
        """
        Evaluate parameters using metamodel or actual function based on strategy.
        
        Args:
            parameters: DataFrame with parameter values to evaluate
            **kwargs: Additional arguments passed to actual evaluation function
            
        Returns:
            List of response dictionaries with 'metric' and other fields
        """
        # Extract optimization direction if provided
        if 'opt_min_or_max' in kwargs:
            self.minimize = kwargs['opt_min_or_max'] == 'min'
        
        responses = []
        
        for idx, row in parameters.iterrows():
            # Convert row to array for metamodel
            x_array = row.values
            
            # Check cache first
            if self.enable_caching:
                cache_key = tuple(x_array)
                if cache_key in self.evaluation_cache:
                    responses.append(self.evaluation_cache[cache_key])
                    continue
            
            # Decide whether to use actual or metamodel
            use_actual = self._should_use_actual_evaluation(x_array, idx)
            
            if use_actual:
                # Actual evaluation
                response = self._evaluate_actual(row.to_frame().T, **kwargs)
                responses.append(response[0])  # Extract single response
                
                # Update training data
                self._update_training_data(x_array, response[0]['metric'])
                
            else:
                # Metamodel evaluation
                response = self._evaluate_metamodel(x_array)
                responses.append(response)
            
            self.total_evaluations += 1
        
        # Retrain metamodel if needed
        self._maybe_retrain_metamodel()
        
        return responses
    
    def _should_use_actual_evaluation(self, x: np.ndarray, index: int) -> bool:
        """
        Decide whether to use actual evaluation based on strategy.
        
        Args:
            x: Parameter values as array
            index: Index in current batch
            
        Returns:
            True if should use actual evaluation, False for metamodel
        """
        # Always use actual if not enough training data
        if len(self.training_X) < self.min_training_points:
            return True
        
        # Always use actual if metamodel not trained
        if not self.metamodel_trained:
            return True
        
        # Strategy-specific decisions
        if self.acquisition_strategy == AcquisitionStrategy.ALL_ACTUAL:
            return True
            
        elif self.acquisition_strategy == AcquisitionStrategy.ALL_METAMODEL:
            return False
            
        elif self.acquisition_strategy == AcquisitionStrategy.PERIODIC:
            # Use actual every N evaluations
            return self.total_evaluations % self.validation_frequency == 0
            
        elif self.acquisition_strategy == AcquisitionStrategy.UNCERTAINTY:
            # Use actual if uncertainty is high
            _, uncertainty = self.metamodel.predict_with_uncertainty(x.reshape(1, -1))
            return uncertainty[0] > self.uncertainty_threshold
            
        elif self.acquisition_strategy == AcquisitionStrategy.MIXED:
            # Use acquisition function to decide
            return self._mixed_strategy_decision(x)
            
        elif self.acquisition_strategy == AcquisitionStrategy.ADAPTIVE:
            # Adapt based on metamodel performance
            return self._adaptive_strategy_decision(x)
        
        return True  # Default to actual
    
    def _mixed_strategy_decision(self, x: np.ndarray) -> bool:
        """
        Decision logic for MIXED strategy using acquisition functions.
        
        Args:
            x: Parameter values
            
        Returns:
            True if should use actual evaluation
        """
        # Always explore with some probability
        if np.random.random() < self.exploration_ratio:
            return True
        
        # Calculate acquisition value
        X_array = np.array(self.training_X)
        y_array = np.array(self.training_y)
        
        if self.best_observed is None:
            self.best_observed = np.min(y_array) if self.minimize else np.max(y_array)
        
        # Get prediction and uncertainty
        mean, std = self.metamodel.predict_with_uncertainty(x.reshape(1, -1))
        
        # Calculate acquisition value
        if self.acquisition_function == "expected_improvement":
            acq_value = expected_improvement(mean, std, self.best_observed, self.minimize)
        elif self.acquisition_function == "probability_of_improvement":
            acq_value = probability_of_improvement(mean, std, self.best_observed, self.minimize)
        elif self.acquisition_function == "upper_confidence_bound":
            acq_value = upper_confidence_bound(mean, std, kappa=2.0, minimize=self.minimize)
        else:
            # Default to uncertainty-based
            acq_value = std
        
        # Use actual if acquisition value is high
        threshold = np.percentile([0.1, 0.2, 0.3], 80)  # Adaptive threshold
        return acq_value[0] > threshold
    
    def _adaptive_strategy_decision(self, x: np.ndarray) -> bool:
        """
        Adaptive decision based on metamodel performance.
        
        Args:
            x: Parameter values
            
        Returns:
            True if should use actual evaluation
        """
        # If we have validation errors, use them to adapt
        if len(self.validation_errors) > 5:
            recent_errors = self.validation_errors[-5:]
            avg_error = np.mean(recent_errors)
            
            # If error is high, use more actual evaluations
            if avg_error > 0.1:  # 10% relative error
                return np.random.random() < 0.5
            else:
                return np.random.random() < 0.1
        
        # Default to periodic validation
        return self.total_evaluations % self.validation_frequency == 0
    
    def _evaluate_actual(self, parameters: pd.DataFrame, **kwargs) -> List[Dict[str, Any]]:
        """
        Perform actual function evaluation.
        
        Args:
            parameters: Parameters to evaluate
            **kwargs: Additional arguments
            
        Returns:
            Evaluation results
        """
        start_time = time.time()
        
        # Call actual function
        results = self.actual_eval_func(parameters, **kwargs)
        
        # Track timing
        eval_time = time.time() - start_time
        self.actual_eval_times.append(eval_time)
        
        # Update counters
        self.n_actual_evals += 1
        
        if self.verbose:
            print(f"Actual evaluation #{self.n_actual_evals}: "
                  f"metric = {results[0]['metric']:.6f}, time = {eval_time:.3f}s")
        
        # Cache result
        if self.enable_caching:
            cache_key = tuple(parameters.iloc[0].values)
            self.evaluation_cache[cache_key] = results[0]
        
        return results
    
    def _evaluate_metamodel(self, x: np.ndarray) -> Dict[str, Any]:
        """
        Perform metamodel evaluation.
        
        Args:
            x: Parameter values as array
            
        Returns:
            Evaluation result dictionary
        """
        start_time = time.time()
        
        # Predict using metamodel
        prediction = self.metamodel.predict(x.reshape(1, -1))[0]
        
        # Track timing
        eval_time = time.time() - start_time
        self.metamodel_eval_times.append(eval_time)
        
        # Update counters
        self.n_metamodel_evals += 1
        
        if self.verbose:
            print(f"Metamodel evaluation #{self.n_metamodel_evals}: "
                  f"predicted metric = {prediction:.6f}, time = {eval_time:.6f}s")
        
        # Create response in same format as actual evaluation
        response = {
            'metric': prediction,
            'is_metamodel': True,
            'data': {'x': x.tolist()}
        }
        
        return response
    
    def _update_training_data(self, x: np.ndarray, y: float):
        """
        Update training data with new observation.
        
        Args:
            x: Input features
            y: Observed output
        """
        self.training_X.append(x)
        self.training_y.append(y)
        self.evaluations_since_update += 1
        
        # Update best observed
        if self.best_observed is None:
            self.best_observed = y
        else:
            if self.minimize:
                self.best_observed = min(self.best_observed, y)
            else:
                self.best_observed = max(self.best_observed, y)
        
        # Limit training data size if specified
        if self.max_training_points and len(self.training_X) > self.max_training_points:
            # Keep most recent and most diverse points
            self._prune_training_data()
    
    def _prune_training_data(self):
        """Remove oldest training points while keeping diversity."""
        # Simple strategy: keep most recent points
        # TODO: Implement more sophisticated pruning (e.g., keep diverse points)
        n_keep = self.max_training_points
        self.training_X = self.training_X[-n_keep:]
        self.training_y = self.training_y[-n_keep:]
    
    def _maybe_retrain_metamodel(self):
        """Retrain metamodel if conditions are met."""
        # Check if we have enough new data
        if self.evaluations_since_update < self.update_frequency:
            return
        
        # Check if we have minimum training points
        if len(self.training_X) < self.min_training_points:
            return
        
        # Retrain
        if self.verbose:
            print(f"Retraining metamodel with {len(self.training_X)} points...")
        
        X_train = np.array(self.training_X)
        y_train = np.array(self.training_y)
        
        self.metamodel.fit(X_train, y_train)
        self.metamodel_trained = True
        self.evaluations_since_update = 0
        
        # Validate if we have enough data
        if len(self.training_X) > self.min_training_points + 5:
            self._validate_metamodel()
    
    def _validate_metamodel(self):
        """Validate metamodel performance on recent data."""
        # Use last 20% of data for validation
        n_val = max(5, int(0.2 * len(self.training_X)))
        
        X_val = np.array(self.training_X[-n_val:])
        y_val = np.array(self.training_y[-n_val:])
        
        # Predict on validation set
        y_pred = self.metamodel.predict(X_val)
        
        # Calculate relative error
        rel_errors = np.abs((y_val - y_pred) / (y_val + 1e-10))
        avg_error = np.mean(rel_errors)
        
        self.validation_errors.append(avg_error)
        
        if self.verbose:
            print(f"Metamodel validation error: {avg_error:.4f}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about metamodel usage and performance.
        
        Returns:
            Dictionary with evaluation statistics
        """
        total_time_actual = sum(self.actual_eval_times)
        total_time_metamodel = sum(self.metamodel_eval_times)
        
        stats = {
            'n_actual_evaluations': self.n_actual_evals,
            'n_metamodel_evaluations': self.n_metamodel_evals,
            'total_evaluations': self.total_evaluations,
            'metamodel_usage_ratio': self.n_metamodel_evals / max(1, self.total_evaluations),
            'total_time_actual': total_time_actual,
            'total_time_metamodel': total_time_metamodel,
            'avg_time_actual': np.mean(self.actual_eval_times) if self.actual_eval_times else 0,
            'avg_time_metamodel': np.mean(self.metamodel_eval_times) if self.metamodel_eval_times else 0,
            'time_saved': total_time_actual - total_time_metamodel,
            'speedup_factor': total_time_actual / max(0.001, total_time_metamodel) if self.n_metamodel_evals > 0 else 1,
            'training_data_size': len(self.training_X),
            'avg_validation_error': np.mean(self.validation_errors) if self.validation_errors else None,
        }
        
        return stats
    
    def reset(self):
        """Reset the evaluator to initial state."""
        self.training_X = []
        self.training_y = []
        self.n_actual_evals = 0
        self.n_metamodel_evals = 0
        self.evaluations_since_update = 0
        self.total_evaluations = 0
        self.metamodel_trained = False
        self.validation_errors = []
        self.actual_eval_times = []
        self.metamodel_eval_times = []
        self.best_observed = None
        if self.enable_caching:
            self.evaluation_cache.clear()
        self.metamodel.reset()