"""
Damped Least Squares (Levenberg-Marquardt) Optimizer

This implementation provides an efficient optimization algorithm that combines the 
Gauss-Newton method with gradient descent through an adaptive damping parameter.
It integrates with the Parameters class for parameter handling and is particularly
effective for nonlinear least squares problems and sensitivity-dependent optimization
like lens design.

Author: Implementation based on Levenberg-Marquardt algorithm

Note: All functions in this module prefixed with an underscore (_) indicate
they are internal implementation details not meant to be called directly from outside
the DampedLeastSquares class.
"""

import numpy as np
import pandas as pd
import inspect
from typing import Dict, List, Optional, Union, Any, Callable, Tuple

from aivalanche_lib.parameters import Parameters
from .utils import (
    _update_history, _get_history_as_df,
    _run_callbacks, _compute_jacobian,
    _compute_residuals, _update_damping_factor
)
from .io import (
    write_history_to_file, write_optimization_info_to_file,
    write_best_parameters_to_file
)
from .visualizations import (
    _plot_metrics_evolution, _plot_damping_evolution,
    _plot_residuals_evolution, _plot_parameters_evolution
)


class DampedLeastSquares:
    """
    Damped Least Squares (Levenberg-Marquardt) optimizer for parameter spaces.
    
    This implementation provides the DLS/LM algorithm with support for the Parameters 
    class for parameter handling. It's particularly effective for problems where the
    objective can be expressed as a sum of squared residuals.
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
                 
                 max_iterations: int = 100,
                 metric_threshold: float = 0,
                 max_iter_without_improvement: int = 20,
                 improvement_threshold: float = 1e-6,
                 gradient_tolerance: float = 1e-8,
                 parameter_tolerance: float = 1e-8,
                 
                 initial_damping: float = 0.01,
                 damping_increase_factor: float = 10.0,
                 damping_decrease_factor: float = 0.1,
                 min_damping: float = 1e-10,
                 max_damping: float = 1e10,
                 
                 jacobian_method: str = 'finite_difference',
                 jacobian_step_size: float = 1e-6,
                 jacobian_step_size_relative: bool = True,
                 
                 initial_point: Optional[Union[str, pd.DataFrame]] = None,
                 use_defaults_in_initial_point: bool = False,
                 
                 residual_type: str = 'scalar',  # 'scalar' or 'vector'
                 trust_region_radius: Optional[float] = None,
                 
                 use_qr_decomposition: bool = True,
                 
                 boundary_handling: str = 'reflect',
                 
                 results_dir: Optional[str] = None):
        """
        Initialize the Damped Least Squares optimizer.
        
        Args:
            seed: Random seed for reproducibility
            eval_func: Function to evaluate parameter sets. Should return residuals or metric.
            eval_func_args: Additional arguments for the evaluation function
            callback_*: Various callback functions for monitoring progress
            parameters: Parameters object or DataFrame with parameter definitions
            opt_min_or_max: Optimization direction ('min' or 'max')
            max_iterations: Maximum number of iterations
            metric_threshold: Threshold value for early stopping
            max_iter_without_improvement: Stop after this many iterations without improvement
            improvement_threshold: Minimum relative improvement to reset no-improvement counter
            gradient_tolerance: Stop if gradient norm falls below this value
            parameter_tolerance: Stop if parameter change norm falls below this value
            initial_damping: Initial damping parameter (lambda)
            damping_increase_factor: Factor to increase damping when step is rejected
            damping_decrease_factor: Factor to decrease damping when step is accepted
            min_damping: Minimum allowed damping value
            max_damping: Maximum allowed damping value
            jacobian_method: Method for Jacobian estimation ('finite_difference', 'complex_step', 'automatic')
            jacobian_step_size: Step size for Jacobian estimation
            jacobian_step_size_relative: Whether step size is relative to parameter value
            initial_point: Initial parameter values (DataFrame, path to CSV, or 'default')
            use_defaults_in_initial_point: Whether to use default parameter values
            residual_type: 'scalar' for single objective, 'vector' for multi-objective
            trust_region_radius: Optional trust region constraint on step size
            use_qr_decomposition: Use QR decomposition for numerical stability
            boundary_handling: How to handle boundary constraints ('reflect', 'clip', 'penalty')
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
        
        # Stopping criteria
        self.max_iterations = int(max_iterations)
        self.metric_threshold = float(metric_threshold)
        self.max_iter_without_improvement = int(max_iter_without_improvement)
        self.improvement_threshold = improvement_threshold
        self.gradient_tolerance = gradient_tolerance
        self.parameter_tolerance = parameter_tolerance
        
        # Damping parameters
        self.initial_damping = initial_damping
        self.damping_increase_factor = damping_increase_factor
        self.damping_decrease_factor = damping_decrease_factor
        self.min_damping = min_damping
        self.max_damping = max_damping
        
        # Jacobian settings
        self.jacobian_method = jacobian_method
        self.jacobian_step_size = jacobian_step_size
        self.jacobian_step_size_relative = jacobian_step_size_relative
        
        # Initial point
        self.initial_point = initial_point
        self.use_defaults_in_initial_point = use_defaults_in_initial_point
        
        # Algorithm options
        self.residual_type = residual_type
        self.trust_region_radius = trust_region_radius
        self.use_qr_decomposition = use_qr_decomposition
        
        # Boundary handling
        valid_boundary_methods = ['reflect', 'clip', 'penalty']
        if boundary_handling not in valid_boundary_methods:
            raise ValueError(f"Invalid boundary_handling: '{boundary_handling}'. "
                           f"Must be one of: {', '.join(valid_boundary_methods)}")
        self.boundary_handling = boundary_handling
        
        # Results directory
        self.results_dir = results_dir
        
        # Initialize variables
        self._initialize_variables()
    
    @property
    def current_parameters(self):
        """
        Convert normalized parameters to real parameter values.
        Returns a DataFrame with parameter names and denormalized values.
        """
        if self.current_point is None:
            return None
        
        params_df = pd.DataFrame([self.current_point], columns=self.variable_parameters_names)
        return self.parameters.unnorm_all(params_df)
    
    @property
    def history(self):
        """Get optimization history as DataFrames."""
        points_df, points_normed_df = _get_history_as_df(self, which='points')
        
        return {
            'points': points_df,
            'points_normed': points_normed_df,
            'metrics': pd.DataFrame({
                'iter': range(1, len(self.all_metrics) + 1),
                'metric': self.all_metrics,
                'damping': self.all_damping_factors,
                'gradient_norm': self.all_gradient_norms,
                'step_norm': self.all_step_norms
            })
        }
    
    @property
    def optimization_info(self):
        """
        Property that dynamically assembles optimization information.
        
        Returns:
            dict: Dictionary containing input parameters and current output state
                  of the optimization process.
        """
        # Get the signature of the __init__ method
        init_signature = inspect.signature(self.__class__.__init__)
        
        # Extract all parameter names except 'self'
        param_names = [p for p in init_signature.parameters if p != 'self']
        
        # Create dictionary with all input parameters
        input_info = {name: getattr(self, name) for name in param_names if hasattr(self, name)}
        
        # Add parameters data in the proper format
        input_info['parameters'] = self.parameters.to_dict()
        
        # Current output state
        output_info = {
            'iter': self.iter,
            'nr_evaluations': self.nr_evaluations,
            'best_metric': self.best_metric,
            'best_parameters': self.best_parameters,
            'stop_reason': self.stop_reason,
            'is_stop_criteria_reached': self.is_stop_criteria_reached,
            'iter_no_improvement': self.iter_no_improvement,
            'final_damping': self.damping_factor,
            'final_gradient_norm': self.gradient_norm,
            'final_step_norm': self.step_norm
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
        self.better_solution_found = False
        
        # Initialize current point
        if self.initial_point is not None:
            self.current_point = self._process_initial_point()
        else:
            # Use defaults or random initialization
            if self.use_defaults_in_initial_point:
                defaults_dict = {}
                for name in self.variable_parameters_names:
                    param = self.parameters.get_parameter(name)
                    defaults_dict[name] = param.default
                defaults_df = pd.DataFrame([defaults_dict])
                normalized = self.parameters.norm_all(defaults_df)
                # Extract only variable parameter values
                variable_values = []
                for param_name in self.variable_parameters_names:
                    if param_name in normalized.columns:
                        variable_values.append(normalized[param_name].iloc[0])
                self.current_point = np.array(variable_values)
            else:
                # Random point in [0, 1]
                self.current_point = self.rng.random(self.nr_variable_parameters)
        
        # Initialize algorithm variables
        self.damping_factor = self.initial_damping
        self.current_metric = None
        self.current_residuals = None
        self.jacobian = None
        self.gradient = None
        self.gradient_norm = 0.0
        self.step = None
        self.step_norm = 0.0
        
        # Best solution tracking
        self.best_point = self.current_point.copy()
        self.best_parameters = None
        self.best_metric = float('inf') if self.opt_min_or_max == 'min' else float('-inf')
        self.best_response = None
        
        # History tracking
        self.all_points = []
        self.all_metrics = []
        self.all_residuals = []
        self.all_damping_factors = []
        self.all_gradient_norms = []
        self.all_step_norms = []
    
    def _process_initial_point(self):
        """Process initial point from various input formats."""
        if isinstance(self.initial_point, str):
            if self.initial_point.lower() == 'default':
                # Use default values from parameters
                defaults_dict = {}
                for name in self.variable_parameters_names:
                    param = self.parameters.get_parameter(name)
                    defaults_dict[name] = param.default
                initial_df = pd.DataFrame([defaults_dict])
            else:
                # Load from file
                initial_df = pd.read_csv(self.initial_point)
        elif isinstance(self.initial_point, pd.DataFrame):
            initial_df = self.initial_point.copy()
        else:
            raise ValueError("initial_point must be a DataFrame, path to CSV, or 'default'")
        
        # Normalize and scale
        normalized = self.parameters.norm_all(initial_df)
        
        # Extract only variable parameters
        variable_values = []
        for param_name in self.variable_parameters_names:
            if param_name in normalized.columns:
                variable_values.append(normalized[param_name].iloc[0])
        
        return np.array(variable_values)
    
    def run_optimization(self):
        """Run the optimization loop until stop criteria are met."""
        # Evaluate initial point
        self._evaluate_current_point()
        
        # Main optimization loop
        while not self.is_stop_criteria_reached:
            self._run_iteration()
            
            # Run callbacks
            _run_callbacks(self, last_iteration=False)
            
            # Check stop criteria
            self._set_is_stop_criteria_reached()
        
        _run_callbacks(self, last_iteration=True)
        
        # Final processing
        self.show_final_result()
    
    def _run_iteration(self):
        """Run a single iteration of the DLS algorithm."""
        self.iter += 1
        
        # Store initial point for this iteration
        initial_point = self.current_point.copy()
        initial_metric = self.current_metric
        
        # Compute Jacobian at current point
        self.jacobian = _compute_jacobian(self)
        
        # Compute gradient (J^T * r for least squares)
        if self.residual_type == 'vector':
            self.gradient = self.jacobian.T @ self.current_residuals
        else:
            # For scalar case, gradient is just the Jacobian
            self.gradient = self.jacobian.flatten()
        
        self.gradient_norm = np.linalg.norm(self.gradient)
        
        # Solve for step using damped least squares
        self._compute_step()
        
        # Try the step
        trial_point = self.current_point + self.step
        
        # Apply boundary constraints
        trial_point = self._apply_boundary_constraints(trial_point)
        
        # Evaluate trial point
        trial_metric, trial_residuals = self._evaluate_point(trial_point)
        
        # Decide whether to accept the step
        step_accepted = self._should_accept_step(self.current_metric, trial_metric)
        
        if step_accepted:
            # Accept step
            self.current_point = trial_point
            self.current_metric = trial_metric
            self.current_residuals = trial_residuals
            
            # Update damping (decrease for successful step)
            self.damping_factor = _update_damping_factor(
                self.damping_factor, 
                'decrease',
                self.damping_decrease_factor,
                self.min_damping,
                self.max_damping
            )
            
            # Check if this is the best solution
            self._update_best_solution()
        else:
            # Reject step - restore state
            self.current_point = initial_point
            self.current_metric = initial_metric
            
            # Update damping (increase for failed step)
            self.damping_factor = _update_damping_factor(
                self.damping_factor,
                'increase', 
                self.damping_increase_factor,
                self.min_damping,
                self.max_damping
            )
        
        # Update history
        _update_history(self)
    
    def _compute_step(self):
        """Compute the step using damped least squares."""
        if self.residual_type == 'vector':
            # Full least squares: solve (J^T J + lambda I) p = -J^T r
            JtJ = self.jacobian.T @ self.jacobian
            n = JtJ.shape[0]
            
            # Add damping to diagonal
            damped_JtJ = JtJ + self.damping_factor * np.eye(n)
            
            # Right hand side
            rhs = self.jacobian.T @ self.current_residuals
            
            try:
                if self.use_qr_decomposition:
                    # Use QR decomposition for better numerical stability
                    Q, R = np.linalg.qr(np.vstack([self.jacobian, 
                                                   np.sqrt(self.damping_factor) * np.eye(n)]))
                    # Solve R * step = -Q^T * [residuals; 0]
                    extended_residuals = np.hstack([self.current_residuals, 
                                                   np.zeros(n)])
                    self.step = np.linalg.solve(R, -Q.T @ extended_residuals)
                else:
                    # Direct solve
                    self.step = np.linalg.solve(damped_JtJ, -rhs)
            except np.linalg.LinAlgError:
                # Fallback to gradient descent
                self.step = -self.gradient / (np.linalg.norm(self.gradient) + 1e-10)
                self.step *= self.jacobian_step_size
        else:
            # Scalar case: gradient descent with damping
            # Step = -gradient / (||gradient||^2 + lambda)
            grad_norm_sq = np.dot(self.gradient, self.gradient)
            if grad_norm_sq > 0:
                self.step = -self.gradient / (grad_norm_sq / self.gradient_norm + self.damping_factor)
            else:
                self.step = np.zeros_like(self.gradient)
        
        # Apply trust region if specified
        if self.trust_region_radius is not None:
            step_norm = np.linalg.norm(self.step)
            if step_norm > self.trust_region_radius:
                self.step *= self.trust_region_radius / step_norm
        
        self.step_norm = np.linalg.norm(self.step)
    
    def _apply_boundary_constraints(self, point):
        """Apply boundary constraints to a point."""
        if self.boundary_handling == 'clip':
            return np.clip(point, 0, 1)
        elif self.boundary_handling == 'reflect':
            # Reflect points that go outside [0, 1]
            reflected = point.copy()
            # Handle lower boundary
            mask_low = reflected < 0
            reflected[mask_low] = -reflected[mask_low]
            # Handle upper boundary  
            mask_high = reflected > 1
            reflected[mask_high] = 2 - reflected[mask_high]
            return reflected
        elif self.boundary_handling == 'penalty':
            # Return as-is, penalty will be added in evaluation
            return point
        else:
            return point
    
    def _evaluate_current_point(self):
        """Evaluate the current point."""
        self.current_metric, self.current_residuals = self._evaluate_point(self.current_point)
        self.nr_evaluations += 1
        
        # Initialize best solution
        if self.iter == 0:
            self.best_metric = self.current_metric
            self.best_point = self.current_point.copy()
            # Get denormalized parameters for best_parameters
            params_df = pd.DataFrame([self.current_point], columns=self.variable_parameters_names)
            denorm_df = self.parameters.unnorm_all(params_df)
            self.best_parameters = denorm_df.iloc[0]
    
    def _evaluate_point(self, point):
        """Evaluate a parameter point and return metric and residuals."""
        # Denormalize parameters
        params_df = pd.DataFrame([point], columns=self.variable_parameters_names)
        params_df = self.parameters.unnorm_all(params_df)
        
        # Add penalty for boundary violations if using penalty method
        penalty = 0
        if self.boundary_handling == 'penalty':
            # Quadratic penalty for violations
            violations = np.maximum(0, -point) + np.maximum(0, point - 1)
            penalty = 1000 * np.sum(violations**2)
        
        # Evaluate function
        extra_arguments = {
            'iteration': self.iter,
            'best_metric': self.best_metric,
            'best_parameters': self.best_parameters,
            **self.eval_func_args
        }
        
        response = self.eval_func(parameters=params_df, **extra_arguments)
        
        # Extract metric and residuals based on response type
        if isinstance(response, list) and len(response) > 0:
            # Standard format with dict responses
            if 'residuals' in response[0]:
                # Vector residuals provided
                residuals = np.array(response[0]['residuals'])
                metric = np.sum(residuals**2) + penalty
            else:
                # Only metric provided
                metric = response[0]['metric'] + penalty
                # Create artificial residual for scalar case
                residuals = np.array([np.sqrt(abs(metric))])
        else:
            raise ValueError("eval_func must return a list with dict elements")
        
        # Adjust for optimization direction
        if self.opt_min_or_max == 'max':
            metric = -metric
            residuals = -residuals
        
        return metric, residuals
    
    def _should_accept_step(self, current_metric, trial_metric):
        """Determine whether to accept the trial step."""
        # Simple decrease criterion
        return trial_metric < current_metric
    
    def _update_best_solution(self):
        """Update best solution if current is better."""
        is_better = False
        
        if self.opt_min_or_max == 'min':
            is_better = self.current_metric < self.best_metric
        else:
            is_better = self.current_metric > self.best_metric
        
        if is_better:
            self.best_metric = self.current_metric
            self.best_point = self.current_point.copy()
            self.best_parameters = self.current_parameters.iloc[0]
            self.iter_no_improvement = 0
            self.better_solution_found = True
        else:
            self.iter_no_improvement += 1
            self.better_solution_found = False
    
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
        elif self.gradient_norm < self.gradient_tolerance:
            self.is_stop_criteria_reached = True
            self.stop_reason = "gradient tolerance reached"
        elif self.step_norm < self.parameter_tolerance:
            self.is_stop_criteria_reached = True
            self.stop_reason = "parameter tolerance reached"
        elif self.iter_no_improvement > self.max_iter_without_improvement:
            self.is_stop_criteria_reached = True
            self.stop_reason = "maximum iterations without improvement reached"
        elif self.iter >= self.max_iterations:
            self.is_stop_criteria_reached = True
            self.stop_reason = "maximum iterations reached"
        else:
            self.is_stop_criteria_reached = False
    
    def abort_optimization(self):
        """Abort optimization process."""
        self.abort_flag = True
    
    def show_final_result(self):
        """Print the final optimization results."""
        print("\n\n--------------------------- Optimization stopped ---------------------------\n\n")
        print(f"Reason: {self.stop_reason}\n\n")
        print(f"Number of iterations: {self.iter}\n\n")
        print(f"Number of evaluations: {self.nr_evaluations}\n\n")
        print(f"Best response: {self.best_metric}\n\n")
        print(f"Best parameters: {self.best_parameters}\n\n")
        print(f"Final gradient norm: {self.gradient_norm:.2e}\n\n")
        print(f"Final damping factor: {self.damping_factor:.2e}\n\n")
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
                    x_scale='linear', y_scale='log',
                    save_path=None, title=None, **kwargs):
        """Plot the evolution of metrics throughout the optimization process."""
        return _plot_metrics_evolution(self, fig, ax, figsize, x_scale, y_scale,
                                     save_path, title, **kwargs)
    
    def plot_damping(self, fig=None, ax=None, figsize=(10, 6),
                    save_path=None, title=None, **kwargs):
        """Plot the evolution of damping factor."""
        return _plot_damping_evolution(self, fig, ax, figsize,
                                     save_path, title, **kwargs)
    
    def plot_residuals(self, fig=None, ax=None, figsize=(10, 6),
                      save_path=None, title=None, **kwargs):
        """Plot the evolution of residuals."""
        return _plot_residuals_evolution(self, fig, ax, figsize,
                                       save_path, title, **kwargs)
    
    def plot_parameters(self, parameter_names=None, fig=None, ax=None, 
                       figsize=(10, 6), save_path=None, title=None, **kwargs):
        """Plot the evolution of parameters."""
        return _plot_parameters_evolution(self, parameter_names, fig, ax, figsize,
                                        save_path, title, **kwargs)