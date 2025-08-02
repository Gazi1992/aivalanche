"""
ADAM (Adaptive Moment Estimation) Optimizer

This implementation provides an efficient gradient-based optimization algorithm that uses
moving averages of the parameters to provide adaptive learning rates for each parameter.
It integrates with the Parameters class for parameter handling and supports various
stopping criteria and gradient estimation methods.

Author: Based on the paper "Adam: A Method for Stochastic Optimization" by Kingma & Ba

Note: All functions in this module prefixed with an underscore (_) indicate
they are internal implementation details not meant to be called directly from outside
the Adam class.
"""

import numpy as np
import pandas as pd
import inspect
from typing import Dict, List, Optional, Union, Any, Callable

from aivalanche_lib.parameters import Parameters
from .utils import (
    _update_history, _get_history_as_df,
    _run_callbacks, _estimate_gradient
)
from .io import (
    write_history_to_file, write_optimization_info_to_file,
    write_best_parameters_to_file
)
from .visualizations import (
    _plot_metrics_evolution, _plot_gradient_norm_evolution,
    _plot_learning_rate_evolution, _plot_parameters_evolution
)


class Adam:
    """
    ADAM optimizer for parameter spaces.
    
    This implementation provides the ADAM optimization algorithm with support
    for the Parameters class for parameter handling and gradient estimation.
    """
    
    def __init__(self,
                 seed: Optional[int] = None,
                 eval_func: Optional[Callable] = None,
                 eval_func_args: Optional[Dict[str, Any]] = None,
                 callback_after_first_iter: Optional[Callable] = None,
                 callback_after_each_iter: Optional[Callable] = None,
                 callback_after_last_iter: Optional[Callable] = None,
                 callback_after_better_solution: Optional[Callable] = None,
                 
                 parameters: Optional[Union[Parameters, str, pd.DataFrame, List[Dict[str, Any]]]] = None,
                 opt_min_or_max: str = 'min',
                 
                 max_iterations: int = 1000,
                 metric_threshold: float = 0,
                 max_iter_without_improvement: int = 50,
                 improvement_threshold: float = 0.01,
                 gradient_tolerance: float = 1e-6,
                 
                 learning_rate: float = 0.001,
                 beta1: float = 0.9,
                 beta2: float = 0.999,
                 epsilon: float = 1e-8,
                 
                 gradient_method: str = 'finite_difference',
                 gradient_step_size: float = 1e-5,
                 gradient_step_size_relative: bool = True,
                 
                 initial_point: Optional[Union[str, pd.DataFrame]] = None,
                 use_defaults_in_initial_point: bool = False,
                 
                 learning_rate_decay: Optional[float] = None,
                 amsgrad: bool = False,
                 
                 boundary_handling: str = 'clip',
                 
                 results_dir: Optional[str] = None):
        """
        Initialize the ADAM optimizer.
        
        Args:
            seed: Random seed for reproducibility
            eval_func: Function to evaluate parameter sets
            eval_func_args: Additional arguments for the evaluation function
            callback_*: Various callback functions for monitoring progress
            parameters: Parameters object or DataFrame with parameter definitions
            opt_min_or_max: Optimization direction ('min' or 'max')
            max_iterations: Maximum number of iterations
            metric_threshold: Threshold value for early stopping
            max_iter_without_improvement: Stop after this many iterations without improvement
            improvement_threshold: Minimum relative improvement to reset no-improvement counter
            gradient_tolerance: Stop if gradient norm falls below this value
            learning_rate: Learning rate (alpha in the paper)
            beta1: Exponential decay rate for first moment estimates
            beta2: Exponential decay rate for second moment estimates
            epsilon: Small value to prevent division by zero
            gradient_method: Method for gradient estimation ('finite_difference' or 'simultaneous_perturbation')
            gradient_step_size: Step size for gradient estimation
            gradient_step_size_relative: Whether step size is relative to parameter value
            initial_point: Initial point (DataFrame or path to CSV)
            use_defaults_in_initial_point: Whether to use default parameter values
            learning_rate_decay: Optional learning rate decay factor per iteration
            amsgrad: Whether to use AMSGrad variant
            boundary_handling: How to handle parameter boundaries ('clip', 'reflect', or 'none')
            results_dir: Directory to save results
        """
        # Set random seed
        self.seed = seed if seed is not None else np.random.randint(0, 1000)
        self.rng = np.random.RandomState(self.seed)
        
        # Evaluation function and callbacks
        self.eval_func = eval_func
        self.eval_func_args = {} if eval_func_args is None else eval_func_args
        self.callback_after_first_iter = callback_after_first_iter
        self.callback_after_each_iter = callback_after_each_iter
        self.callback_after_last_iter = callback_after_last_iter
        self.callback_after_better_solution = callback_after_better_solution
        
        # Parameters
        self.parameters = parameters if isinstance(parameters, Parameters) else Parameters(parameters)
        self.parameters_names = self.parameters.names
        self.variable_parameters_names = self.parameters.variable_names
        self.nr_parameters = len(self.parameters)
        self.nr_variable_parameters = self.parameters.n_variable
        
        self.opt_min_or_max = opt_min_or_max
        
        # ADAM hyperparameters
        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.learning_rate_decay = learning_rate_decay
        self.amsgrad = amsgrad
        
        # Gradient estimation
        self.gradient_method = gradient_method
        self.gradient_step_size = gradient_step_size
        self.gradient_step_size_relative = gradient_step_size_relative
        
        # Boundary handling
        valid_boundary_methods = ['clip', 'reflect', 'none']
        if boundary_handling not in valid_boundary_methods:
            raise ValueError(f"Invalid boundary_handling: '{boundary_handling}'. "
                           f"Must be one of: {', '.join(valid_boundary_methods)}")
        self.boundary_handling = boundary_handling
        
        # Stopping criteria
        self.max_iterations = int(max_iterations)
        self.metric_threshold = float(metric_threshold)
        self.max_iter_without_improvement = int(max_iter_without_improvement)
        self.improvement_threshold = improvement_threshold
        self.gradient_tolerance = gradient_tolerance
        
        # Initial point settings
        self.initial_point = initial_point
        self.use_defaults_in_initial_point = bool(use_defaults_in_initial_point)
        
        # Results directory
        self.results_dir = results_dir
        
        # Initialize variables
        self._initialize_variables()
    
    @property
    def current_parameters(self):
        """Get current parameters as denormalized DataFrame."""
        if self.current_point is None:
            return None
        params_df = pd.DataFrame([self.current_point], columns=self.variable_parameters_names)
        return self.parameters.unnorm_all(params_df)
    
    @property
    def best_parameters(self):
        """Get best parameters as denormalized series."""
        if self.best_point is None:
            return None
        params_df = pd.DataFrame([self.best_point], columns=self.variable_parameters_names)
        denorm = self.parameters.unnorm_all(params_df)
        return denorm.iloc[0]
    
    def get_info(self) -> Dict[str, Any]:
        """Get current optimization state information."""
        # Input parameters that don't change
        input_info = {
            'optimizer_type': 'ADAM',
            'seed': self.seed,
            'opt_min_or_max': self.opt_min_or_max,
            'max_iterations': self.max_iterations,
            'metric_threshold': self.metric_threshold,
            'max_iter_without_improvement': self.max_iter_without_improvement,
            'improvement_threshold': self.improvement_threshold,
            'gradient_tolerance': self.gradient_tolerance,
            'learning_rate': self.learning_rate,
            'beta1': self.beta1,
            'beta2': self.beta2,
            'epsilon': self.epsilon,
            'amsgrad': self.amsgrad,
            'gradient_method': self.gradient_method,
            'gradient_step_size': self.gradient_step_size,
            'gradient_step_size_relative': self.gradient_step_size_relative,
            'boundary_handling': self.boundary_handling
        }
        
        # Current output state
        output_info = {
            'iter': self.iter,
            'nr_evaluations': self.nr_evaluations,
            'best_metric': self.best_metric,
            'best_parameters': self.best_parameters,
            'stop_reason': self.stop_reason,
            'is_stop_criteria_reached': self.is_stop_criteria_reached,
            'iter_no_improvement': self.iter_no_improvement,
            'current_gradient_norm': self.gradient_norm
        }
        
        return {
            'input': input_info,
            'output': output_info
        }
    
    def _initialize_variables(self):
        """Initialize all internal variables for the optimization process."""
        self.iter = 0
        self.iter_no_improvement = 0
        self.abort_flag = False
        self.is_stop_criteria_reached = False
        self.stop_reason = ""
        self.nr_evaluations = 0
        
        # Current point in normalized space
        self.current_point = None
        self.current_metric = None
        self.current_response = None
        
        # Gradient and moment estimates
        self.gradient = np.zeros(self.nr_variable_parameters)
        self.gradient_norm = 0.0
        self.m = np.zeros(self.nr_variable_parameters)  # First moment
        self.v = np.zeros(self.nr_variable_parameters)  # Second moment
        self.v_hat_max = np.zeros(self.nr_variable_parameters) if self.amsgrad else None
        
        # History tracking
        self.all_points = np.zeros((0, self.nr_variable_parameters))
        self.all_metrics = np.zeros((0,))
        self.all_gradients = np.zeros((0, self.nr_variable_parameters))
        self.all_gradient_norms = np.zeros((0,))
        self.all_learning_rates = np.zeros((0,))
        
        # Best solution tracking
        self.best_point = None
        self.best_metric = float('-inf') if self.opt_min_or_max == 'max' else float('inf')
        self.best_response = None
        self.better_solution_found = False
    
    def _initialize_starting_point(self):
        """Initialize the starting point for optimization."""
        if self.initial_point is not None:
            if isinstance(self.initial_point, str):
                # Load from file
                initial_point_df = pd.read_csv(self.initial_point)
                if 'value' in initial_point_df.columns:
                    initial_values = initial_point_df.set_index('name')['value'].to_dict()
                else:
                    initial_values = initial_point_df.iloc[0].to_dict()
                
                # Create parameter DataFrame
                params_dict = {}
                for param_name in self.parameters_names:
                    if param_name in initial_values:
                        params_dict[param_name] = initial_values[param_name]
                    else:
                        # Use default value
                        param = self.parameters.get_parameter(param_name)
                        params_dict[param_name] = param.default
                
                params_df = pd.DataFrame([params_dict])
                
            elif isinstance(self.initial_point, pd.DataFrame):
                params_df = self.initial_point
            else:
                raise ValueError("initial_point must be a DataFrame or path to CSV")
            
            # Normalize the initial point
            normalized = self.parameters.norm_all(params_df)
            self.current_point = normalized.values[0]
            
        elif self.use_defaults_in_initial_point:
            # Use default values
            default_dict = {}
            for param_name in self.variable_parameters_names:
                param = self.parameters.get_parameter(param_name)
                default_dict[param_name] = param.default
            
            params_df = pd.DataFrame([default_dict])
            normalized = self.parameters.norm_all(params_df)
            self.current_point = normalized.values[0]
            
        else:
            # Use center of normalized space
            self.current_point = np.full(self.nr_variable_parameters, 0.5)
    
    def _apply_boundary_constraints(self, point):
        """Apply boundary constraints to a point in normalized space."""
        if self.boundary_handling == 'clip':
            return np.clip(point, 0, 1)
        elif self.boundary_handling == 'reflect':
            # Reflect points that go outside boundaries
            reflected = point.copy()
            # Handle lower boundary
            mask_low = reflected < 0
            reflected[mask_low] = -reflected[mask_low]
            # Handle upper boundary
            mask_high = reflected > 1
            reflected[mask_high] = 2 - reflected[mask_high]
            # Ensure still within bounds after reflection
            return np.clip(reflected, 0, 1)
        else:  # 'none'
            return point
    
    def run_optimization(self):
        """Run the optimization loop until stop criteria are met."""
        # Initialize starting point
        self._initialize_starting_point()
        
        # Evaluate initial point
        self._evaluate_current_point()
        
        # First iteration setup
        self.iter = 1
        self._update_best_if_better()
        _update_history(self)
        
        # Run first iteration callback
        _run_callbacks(self, last_iteration=False)
        
        # Main optimization loop
        while not self.is_stop_criteria_reached:
            # Estimate gradient
            self.gradient = _estimate_gradient(self)
            self.gradient_norm = np.linalg.norm(self.gradient)
            
            # Update moment estimates
            self.m = self.beta1 * self.m + (1 - self.beta1) * self.gradient
            self.v = self.beta2 * self.v + (1 - self.beta2) * self.gradient**2
            
            # Bias correction
            m_hat = self.m / (1 - self.beta1**self.iter)
            v_hat = self.v / (1 - self.beta2**self.iter)
            
            # AMSGrad variant
            if self.amsgrad:
                self.v_hat_max = np.maximum(self.v_hat_max, v_hat)
                v_hat_use = self.v_hat_max
            else:
                v_hat_use = v_hat
            
            # Compute effective learning rate
            if self.learning_rate_decay is not None:
                current_lr = self.learning_rate * (1 / (1 + self.learning_rate_decay * self.iter))
            else:
                current_lr = self.learning_rate
            
            # Update parameters
            if self.opt_min_or_max == 'min':
                update = -current_lr * m_hat / (np.sqrt(v_hat_use) + self.epsilon)
            else:  # max
                update = current_lr * m_hat / (np.sqrt(v_hat_use) + self.epsilon)
            
            # Apply update
            new_point = self.current_point + update
            
            # Apply boundary constraints
            self.current_point = self._apply_boundary_constraints(new_point)
            
            # Evaluate new point
            self._evaluate_current_point()
            
            # Update iteration counter
            self.iter += 1
            
            # Check if better solution found
            self._update_best_if_better()
            
            # Update history
            _update_history(self)
            self.all_learning_rates = np.append(self.all_learning_rates, current_lr)
            
            # Run callbacks
            _run_callbacks(self, last_iteration=False)
            
            # Check stop criteria
            self._set_is_stop_criteria_reached()
        
        # Run final callback
        _run_callbacks(self, last_iteration=True)
        
        # Final processing
        self.show_final_result()
    
    def _evaluate_current_point(self):
        """Evaluate the current point."""
        # Convert to denormalized parameters
        params_df = pd.DataFrame([self.current_point], columns=self.variable_parameters_names)
        denorm_params = self.parameters.unnorm_all(params_df)
        
        # Evaluate
        responses = self.eval_func(denorm_params, **self.eval_func_args)
        self.nr_evaluations += 1
        
        # Extract metric
        self.current_response = responses[0]
        self.current_metric = self.current_response['metric']
    
    def _update_best_if_better(self):
        """Update best solution if current is better."""
        is_better = False
        
        if self.opt_min_or_max == 'min':
            is_better = self.current_metric < self.best_metric
        else:  # max
            is_better = self.current_metric > self.best_metric
        
        if is_better:
            self.best_point = self.current_point.copy()
            self.best_metric = self.current_metric
            self.best_response = self.current_response
            self.better_solution_found = True
            self.iter_no_improvement = 0
        else:
            self.better_solution_found = False
            self.iter_no_improvement += 1
    
    def _set_is_stop_criteria_reached(self):
        """Check if any stop criteria are met."""
        if self.abort_flag:
            self.is_stop_criteria_reached = True
            self.stop_reason = "optimization aborted"
        elif self.opt_min_or_max == 'min' and self.best_metric < self.metric_threshold:
            self.is_stop_criteria_reached = True
            self.stop_reason = "metric threshold reached"
        elif self.opt_min_or_max == 'max' and self.best_metric > self.metric_threshold:
            self.is_stop_criteria_reached = True
            self.stop_reason = "metric threshold reached"
        elif self.iter_no_improvement > self.max_iter_without_improvement:
            self.is_stop_criteria_reached = True
            self.stop_reason = "maximum number of iterations without improvement reached"
        elif self.iter > self.max_iterations:
            self.is_stop_criteria_reached = True
            self.stop_reason = "maximum number of iterations reached"
        elif self.gradient_norm < self.gradient_tolerance:
            self.is_stop_criteria_reached = True
            self.stop_reason = "gradient tolerance reached"
        else:
            self.is_stop_criteria_reached = False
    
    def abort_optimization(self):
        """Abort optimization process."""
        self.abort_flag = True
    
    def _get_history_as_df(self, which='points'):
        """Get optimization history as DataFrame."""
        return _get_history_as_df(self, which)
    
    def show_final_result(self):
        """Print the final optimization results."""
        print("\n\n--------------------------- Optimization stopped ---------------------------\n\n")
        print(f"Reason: {self.stop_reason}\n\n")
        print(f"Number of iterations: {self.iter}\n\n")
        print(f"Number of evaluations: {self.nr_evaluations}\n\n")
        print(f"Best response: {self.best_metric}\n\n")
        print(f"Best parameters: {self.best_parameters}\n\n")
        print(f"Final gradient norm: {self.gradient_norm:.6e}\n\n")
        print("--------------------------------------------------------------------------------\n\n")
    
    # I/O functions
    def write_history_to_file(self, which='points', file_path=None):
        """Delegate to the io module function"""
        return write_history_to_file(self, which, file_path)
    
    def write_optimization_info_to_file(self, file_path=None):
        """Delegate to the io module function"""
        return write_optimization_info_to_file(self, file_path)
    
    def write_best_parameters_to_file(self, file_path=None):
        """Delegate to the io module function"""
        return write_best_parameters_to_file(self, file_path)
    
    # Plotting functions
    def plot_metrics(self, fig=None, ax=None, figsize=(10, 6),
                     x_scale='linear', y_scale='symlog',
                     save_path=None, title=None, **kwargs):
        """Plot the evolution of metrics throughout the optimization process."""
        iter_array = np.arange(1, self.iter + 1)
        
        # Set default title
        title = title or "Metric evolution"
        
        # Create the plot
        fig, ax = _plot_metrics_evolution(
            iterations=iter_array,
            metrics=self.all_metrics,
            x_scale=x_scale,
            y_scale=y_scale,
            fig=fig,
            ax=ax,
            title=title,
            figsize=figsize,
            save_path=save_path,
            **kwargs
        )
        
        return fig, ax
    
    def plot_gradient_norm(self, fig=None, ax=None, figsize=(10, 6),
                          save_path=None, title=None, gradient_tolerance=None, **kwargs):
        """Plot the evolution of gradient norm."""
        iter_array = np.arange(1, len(self.all_gradient_norms) + 1)
        
        # Set default title
        title = title or "Gradient norm evolution"
        
        # Use instance gradient_tolerance if not provided
        if gradient_tolerance is None:
            gradient_tolerance = self.gradient_tolerance
        
        # Create the plot
        fig, ax = _plot_gradient_norm_evolution(
            iterations=iter_array,
            gradient_norms=self.all_gradient_norms,
            fig=fig,
            ax=ax,
            title=title,
            figsize=figsize,
            save_path=save_path,
            gradient_tolerance=gradient_tolerance,
            **kwargs
        )
        
        return fig, ax
    
    def plot_learning_rate(self, fig=None, ax=None, figsize=(10, 6),
                          save_path=None, title=None, **kwargs):
        """Plot the evolution of learning rate."""
        iter_array = np.arange(1, len(self.all_learning_rates) + 1)
        
        # Set default title
        title = title or "Learning rate evolution"
        
        # Create the plot
        fig, ax = _plot_learning_rate_evolution(
            iterations=iter_array,
            learning_rates=self.all_learning_rates,
            fig=fig,
            ax=ax,
            title=title,
            figsize=figsize,
            save_path=save_path,
            **kwargs
        )
        
        return fig, ax
    
    def plot_parameters_evolution(self, parameter_names=None, fig=None, axes=None,
                                 figsize=(12, 8), save_path=None, title=None, **kwargs):
        """Plot the evolution of parameters over iterations."""
        # Get history as DataFrame
        df, _ = _get_history_as_df(self, which='points')
        
        if parameter_names is None:
            parameter_names = self.parameters_names
        
        # Set default title
        title = title or "Parameters evolution"
        
        # Create the plot
        fig, axes = _plot_parameters_evolution(
            df=df,
            parameter_names=parameter_names,
            fig=fig,
            axes=axes,
            title=title,
            figsize=figsize,
            save_path=save_path,
            **kwargs
        )
        
        return fig, axes