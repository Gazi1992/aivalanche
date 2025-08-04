"""
Nelder-Mead Optimizer

This implementation provides an efficient optimization algorithm using the Nelder-Mead simplex method.
It integrates with the Parameters class for parameter handling and supports various adaptive strategies
and customizable stopping criteria.

Author: Gazmend Alia

Note: All functions in this module prefixed with an underscore (_) indicate
they are internal implementation details not meant to be called directly from outside
the NelderMead class.
"""

import numpy as np, pandas as pd, inspect
from typing import Dict, List, Optional, Union, Any, Callable

from aivalanche_lib.parameters import Parameters
from .utils import (
    _update_history, _get_history_as_df,
    _run_callbacks, _generate_spendley_points
)
from .io import (
    write_history_to_file, write_optimization_info_to_file,
    write_best_parameters_to_file, write_current_population_to_file
)
from .operators import (
    _compute_centroid, _try_reflection, _try_expansion,
    _try_contraction, _perform_shrink, _sort_simplex
)
from .visualizations import (
    _plot_metrics_evolution, _plot_simplex_evolution,
    _plot_parameters_evolution
)

class NelderMead:
    """
    Nelder-Mead optimizer for parameter spaces.
    
    This implementation provides the core Nelder-Mead simplex algorithm functionality 
    with support for the Parameters class for parameter handling.
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
                 
                 reflection_coefficient: Union[float, tuple] = (0.9, 1.1),
                 expansion_coefficient: Union[float, tuple] = (1.5, 2.5),
                 contraction_coefficient: Union[float, tuple] = (0.3, 0.5),
                 shrink_coefficient: Union[float, tuple] = (0.3, 0.5),
                 boundary_constraint_method: str = 'random_from_target',
                 
                 initial_point: Optional[Union[str, pd.DataFrame]] = None,
                 initial_point_mode: str = 'centroid',
                 initial_simplex_edge_length: Union[float, tuple] = (0.4, 0.7),
                 defaults_in_initial_simplex: bool = False,
                 initial_simplex: Optional[Union[np.ndarray, pd.DataFrame]] = None,
                 
                 results_dir: Optional[str] = None):
        """
        Initialize the Nelder-Mead optimizer.
        
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
            reflection_coefficient: Scaling factor for reflection operation
            expansion_coefficient: Scaling factor for expansion operation
            contraction_coefficient: Scaling factor for contraction operation
            shrink_coefficient: Scaling factor for shrink operation
            boundary_constraint_method: Method to handle values outside boundaries
            initial_point: Initial point (DataFrame or path to CSV)
            initial_point_mode: How to use initial point ('corner' or 'centroid')
            initial_simplex_edge_length: Edge length for initial simplex
            defaults_in_initial_simplex: Whether to use default parameter values
            initial_simplex: Initial simplex vertices (numpy array or DataFrame)
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
        
        self.parameters = parameters if isinstance(parameters, Parameters) else Parameters(parameters)
        self.parameters_names = self.parameters.names
        self.variable_parameters_names = self.parameters.variable_names
        self.nr_parameters = len(self.parameters)
        self.nr_variable_parameters = self.parameters.n_variable
        
        self.opt_min_or_max = opt_min_or_max
        
        # Algorithm coefficients
        self.reflection_coefficient = reflection_coefficient
        self.expansion_coefficient = expansion_coefficient
        self.contraction_coefficient = contraction_coefficient
        self.shrink_coefficient = shrink_coefficient
        
        # valid_boundary_methods check
        valid_boundary_methods = ['random_from_target', 'clamp', 'random']
        if boundary_constraint_method not in valid_boundary_methods:
            raise ValueError(f"Invalid boundary_constraint_method: '{boundary_constraint_method}'. "
                             f"Must be one of: {', '.join(valid_boundary_methods)}")
        self.boundary_constraint_method = boundary_constraint_method
        
        # Stopping criteria
        self.max_iterations = int(max_iterations)
        self.metric_threshold = float(metric_threshold)
        self.max_iter_without_improvement = int(max_iter_without_improvement)
        self.improvement_threshold = improvement_threshold
        
        # Initial simplex settings
        self.initial_point = initial_point
        self.initial_point_mode = str(initial_point_mode)
        self.initial_simplex_edge_length = initial_simplex_edge_length
        self.defaults_in_initial_simplex = bool(defaults_in_initial_simplex)
        self.initial_simplex = initial_simplex
        
        # Results directory
        self.results_dir = results_dir
        
        # Initialize variables
        self._initialize_variables()
    
    @property
    def current_parameters(self):
        '''
        Convert normalized simplex to real parameter values.
        Returns a DataFrame where columns are parameter names and rows are simplex vertices,
        using the Parameters class to handle denormalization and descaling.
        '''
        if self.iter < 1:
            return None
            
        # Create DataFrame with normalized values and denormalize
        df_normalized = pd.DataFrame(columns=self.variable_parameters_names, data=self.simplex)
        return self.parameters.unnorm_all(df_normalized)
    
    @property
    def history(self):
        simplexes_df, simplexes_normed_df = _get_history_as_df(self, which='simplexes')
        trials_df, trials_normed_df = _get_history_as_df(self, which='trials')
        bests_df, bests_normed_df = _get_history_as_df(self, which='bests')
        
        return {
            'simplexes': simplexes_df,
            'simplexes_normed': simplexes_normed_df,
            'trials': trials_df,
            'trials_normed': trials_normed_df,
            'bests': bests_df,
            'bests_normed': bests_normed_df
        }
    
    @property
    def optimization_info(self):
        """
        Property that dynamically assembles optimization information.
        
        Returns:
            dict: Dictionary containing input parameters and current output state
                  of the optimization process.
        """
        # Dynamically capture all input parameters from __init__ signature
        init_signature = inspect.signature(self.__class__.__init__)
        
        # Extract all parameter names except 'self'
        param_names = [p for p in init_signature.parameters if p != 'self']
        
        # Create dictionary with all input parameters
        input_info = {name: getattr(self, name) for name in param_names if hasattr(self, name)}
        
        # Add parameters data in the proper format
        input_info['parameters'] = self.parameters.to_dict()
        
        # Current output state that changes during optimization
        output_info = {
            'iter': self.iter,
            'nr_evaluations': self.nr_evaluations,
            'best_metric': self.best_metric,
            'best_parameters': self.best_parameters,
            'stop_reason': self.stop_reason,
            'is_stop_criteria_reached': self.is_stop_criteria_reached,
            'iter_no_improvement': self.iter_no_improvement
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
        
        # Initialize the simplex vertices
        self.simplex_size = self.nr_variable_parameters + 1
        self.simplex = np.full((self.simplex_size, self.nr_variable_parameters), np.nan)
        self.simplex_metrics = np.full((self.simplex_size), np.nan)
        
        # Centroid and trial points
        self.centroid = np.full((self.nr_variable_parameters), np.nan)
        self.reflected = np.full((self.nr_variable_parameters), np.nan)
        self.reflected_metric = np.nan
        self.expanded = np.full((self.nr_variable_parameters), np.nan)
        self.expanded_metric = np.nan
        self.contracted = np.full((self.nr_variable_parameters), np.nan)
        self.contracted_metric = np.nan
        
        # History tracking
        self.all_simplexes = np.zeros((0, self.simplex_size, self.nr_variable_parameters))
        self.all_simplexes_metrics = np.zeros((0, self.simplex_size))
        
        self.all_trials = np.zeros((0, self.nr_variable_parameters))
        self.all_trials_metrics = np.zeros((0,))
        
        self.all_bests = np.zeros((0, self.nr_variable_parameters))
        self.all_bests_metrics = np.zeros((0,1))
        
        # Best solution tracking
        self.best = np.full((1, self.nr_variable_parameters), None)
        self.best_parameters = None
        self.best_metric = float('-inf') if self.opt_min_or_max == 'max' else float('inf')
        self.best_response = None
        self.better_solution_found = False
        
        # Current responses
        self.current_responses = None
        self.current_metrics = None
        
        # Metrics for ordering
        self.worst_metric = None
        self.second_worst_metric = None
        
        # Coefficients for current iteration
        self.reflection_coef = None
        self.expansion_coef = None
        self.contraction_coef = None
        self.shrink_coef = None
    
    def run_optimization(self):
        """Run the optimization loop until stop criteria are met."""
        # Initialize simplex and run first iteration
        self._initialize_simplex()
        self._run_first_iteration()
        
        # Main optimization loop
        while not self.is_stop_criteria_reached:
            self._run_iteration()
            
            # Run callbacks
            _run_callbacks(self, last_iteration = False)
            
            # Check stop criteria
            self._set_is_stop_criteria_reached()
        
        _run_callbacks(self, last_iteration = True)
        
        # Final processing
        self.show_final_result()
    
    def _run_first_iteration(self):
        """Run the first iteration to evaluate initial simplex."""
        self.iter = 1
        
        # Evaluate initial simplex
        extra_arguments = {
            'iteration': self.iter,
            'best_metric': self.best_metric,
            'best_parameters': self.best_parameters,
            **self.eval_func_args
        }
        
        # The eval_func should return a list, where each item is a dict that has at least the element 'metric'.
        self.current_responses = self.eval_func(parameters = self.current_parameters, **extra_arguments)
        self.current_metrics = [item['metric'] for item in self.current_responses]
        
        # Save metrics
        self.simplex_metrics = np.array(self.current_metrics)
        
        # Sort simplex and update best
        _sort_simplex(self)
        _update_history(self)
        
        # Update nr of evaluations
        self.nr_evaluations += len(self.current_responses)
    
    def _run_iteration(self):
        """Run a single iteration of the optimization algorithm."""
        
        self.iter += 1
        
        # Calculate centroid
        _compute_centroid(self)
        
        # Try reflection
        _try_reflection(self)
        
        if self._is_better(self.reflected_metric, self.best_metric):
            # Better than best - try expansion
            _try_expansion(self)
            if self._is_better(self.expanded_metric, self.reflected_metric):
                self._accept_expansion()
            else:
                self._accept_reflection()
        elif self._is_better(self.reflected_metric, self.second_worst_metric):
            # Between best and second worst - accept reflection
            self._accept_reflection()
        elif self._is_better(self.reflected_metric, self.worst_metric):
            # Between worst and second worst - outside contraction
            _try_contraction(self, mode='outside')
            if self._is_better(self.contracted_metric, self.reflected_metric):
                self._accept_contraction()
            else:
                _perform_shrink(self)
        else:
            # Worse than worst - inside contraction
            _try_contraction(self, mode='inside')
            if self._is_better(self.contracted_metric, self.worst_metric):
                self._accept_contraction()
            else:
                _perform_shrink(self)
        
        # Sort simplex and update history
        _sort_simplex(self)
        _update_history(self)
    
    def _is_better(self, metric_1, metric_2):
        """Check if metric_1 is better than metric_2 based on optimization direction."""
        if np.isnan(metric_1) or np.isnan(metric_2):
            return False
            
        if self.opt_min_or_max == 'min':
            return metric_1 < metric_2
        else:
            return metric_1 > metric_2
    
    def _accept_reflection(self):
        """Accept the reflected point."""
        self.simplex[-1] = self.reflected
        self.simplex_metrics[-1] = self.reflected_metric
        self.current_responses[-1] = self.reflected_response
    
    def _accept_expansion(self):
        """Accept the expanded point."""
        self.simplex[-1] = self.expanded
        self.simplex_metrics[-1] = self.expanded_metric
        self.current_responses[-1] = self.expanded_response
    
    def _accept_contraction(self):
        """Accept the contracted point."""
        self.simplex[-1] = self.contracted
        self.simplex_metrics[-1] = self.contracted_metric
        self.current_responses[-1] = self.contracted_response
    
    def _initialize_simplex(self):
        """Initialize the simplex using Parameters class normalization."""
        if self.initial_simplex is not None:
            # Use provided initial simplex
            if isinstance(self.initial_simplex, pd.DataFrame):
                # Convert DataFrame to array and normalize
                # Assume DataFrame has columns matching variable parameter names
                simplex_df = self.initial_simplex[self.variable_parameters_names]
                # Normalize the simplex vertices
                normalized_simplex = self.parameters.norm_all(simplex_df)
                # Extract only variable parameters
                variable_values = []
                for vertex_idx in range(len(normalized_simplex)):
                    vertex_values = []
                    for param_name in self.variable_parameters_names:
                        if param_name in normalized_simplex.columns:
                            vertex_values.append(normalized_simplex[param_name].iloc[vertex_idx])
                    variable_values.append(vertex_values)
                self.simplex = np.array(variable_values)
            else:
                # Assume it's a numpy array
                if isinstance(self.initial_simplex, np.ndarray):
                    if self.initial_simplex.shape[0] != self.simplex_size:
                        raise ValueError(f"Initial simplex must have {self.simplex_size} vertices, "
                                       f"but has {self.initial_simplex.shape[0]}")
                    if self.initial_simplex.shape[1] != self.nr_variable_parameters:
                        raise ValueError(f"Initial simplex must have {self.nr_variable_parameters} dimensions, "
                                       f"but has {self.initial_simplex.shape[1]}")
                    
                    # Check if values are normalized (in [0, 1] range)
                    if np.all((self.initial_simplex >= 0) & (self.initial_simplex <= 1)):
                        # Already normalized
                        self.simplex = self.initial_simplex.copy()
                    else:
                        # Need to normalize - create DataFrame for normalization
                        simplex_df = pd.DataFrame(self.initial_simplex, columns=self.variable_parameters_names)
                        normalized_simplex = self.parameters.norm_all(simplex_df)
                        # Extract only variable parameters
                        variable_values = []
                        for vertex_idx in range(len(normalized_simplex)):
                            vertex_values = []
                            for param_name in self.variable_parameters_names:
                                if param_name in normalized_simplex.columns:
                                    vertex_values.append(normalized_simplex[param_name].iloc[vertex_idx])
                            variable_values.append(vertex_values)
                        self.simplex = np.array(variable_values)
                else:
                    raise ValueError("initial_simplex must be a numpy array or pandas DataFrame")
        else:
            # Generate initial simplex vertices using existing method
            simplex_vertices = _generate_spendley_points(self)
            
            # Store normalized simplex
            self.simplex = simplex_vertices
    
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
        print(f"Best response: {self.best_metric}\n\n")
        print(f"Best parameters: {self.best_parameters}\n\n")
        print("--------------------------------------------------------------------------------\n\n")
    
    # i/o functions
    def write_history_to_file(self, which='trials', file_path=None):
        """Delegate to the io module function"""
        return write_history_to_file(self, which, file_path)
    
    def write_optimization_info_to_file(self, file_path=None):
        """Delegate to the io module function"""
        return write_optimization_info_to_file(self, file_path)
    
    def write_best_parameters_to_file(self, file_path=None):
        """Delegate to the io module function"""
        return write_best_parameters_to_file(self, file_path)
    
    def write_current_population_to_file(self, file_path=None):
        """Delegate to the io module function"""
        return write_current_population_to_file(self, file_path)
    
    # plotting functions
    def plot_metrics(self, which="bests", fig=None, ax=None, figsize=(10, 6),
                     x_scale = 'linear', y_scale = 'symlog',
                     save_path=None, title=None, **kwargs):
        """
        Plot the evolution of metrics throughout the optimization process.
        
        Args:
            which (str): Which metrics to plot, can be 'trials' or 'bests'
            fig (matplotlib.figure.Figure): Optional existing figure to plot on
            ax (matplotlib.axes.Axes): Optional existing axes to plot on
            figsize (tuple): Size of the figure in inches (width, height)
            save_path (str): If provided, the figure will be saved to this path
            title (str): Custom title for the plot. If None, a default title will be used
            **kwargs: Additional keyword arguments passed to the matplotlib plotting functions
        
        Returns:
            tuple: Figure and axes objects from matplotlib
        """
        # Create iteration array
        iter_array = np.arange(1, self.iter + 1)
        
        # Prepare data based on the selected metrics type
        if which == "trials":
            # Get trial metrics
            metrics = self.all_trials_metrics
            iterations = np.arange(1, len(metrics) + 1)
            
            # Set title if not given
            title = title or "Trials metrics evolution"
            
        elif which == "bests":
            # Get best metrics
            if len(self.all_bests_metrics.shape) > 1 and self.all_bests_metrics.shape[1] == 1:
                metrics = self.all_bests_metrics.flatten()
            else:
                metrics = self.all_bests_metrics
            # Use standard iteration array (one point per iteration)
            iterations = iter_array
            
            # Set title if not given
            title = title or "Best metrics evolution"
            
        else:
            raise ValueError(f"Invalid 'which' parameter: {which}. Must be 'trials' or 'bests'")
        
        # Create the plot
        fig, ax = _plot_metrics_evolution(
            iterations=iterations,
            metrics=metrics,
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
    
    def plot_simplex_evolution(self, parameter_names: list = None, 
                              fig=None, axes=None, figsize=(10, 6),
                              title=None, save_path=None, **kwargs):
        """
        Plot the evolution of the simplex in parameter space.
        
        Args:
            parameter_names (list): Names of parameters to visualize (max 2)
            fig (matplotlib.figure.Figure): Optional existing figure to plot on
            axes (matplotlib.axes.Axes): Optional existing axes to plot on
            figsize (tuple): Size of the figure in inches (width, height)
            title (str): Title for the figure
            save_path (str): If provided, the figure will be saved to this path
            **kwargs: Additional keyword arguments passed to the plotting function
        
        Returns:
            tuple: Figure and axes objects
        """
        # Validate parameter names
        if parameter_names is not None:
            for param in parameter_names:
                if param not in self.variable_parameters_names:
                    raise ValueError(f"Parameter '{param}' not found in variable parameters")
        else:
            parameter_names = self.variable_parameters_names[:2]
            
        if len(parameter_names) > 2:
            raise ValueError("Can only visualize up to 2 parameters in simplex evolution")
        
        # Create the simplex evolution visualization
        fig, ax = _plot_simplex_evolution(
            self,
            parameter_names=parameter_names,
            fig=fig,
            axes=axes,
            figsize=figsize,
            title=title,
            save_path=save_path,
            **kwargs
        )
        
        return fig, ax