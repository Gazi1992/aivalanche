"""
Differential Evolution Optimizer

This implementation provides an efficient optimization algorithm for high-dimensional spaces,
using the Differential Evolution method. It integrates with the Parameters class for parameter
handling and supports various DE strategies, adaptive boundaries, and customizable stopping criteria.

Author: Gazmend Alia

Note: All functions in this module prefixed with an underscore (_) indicate
they are internal implementation details not meant to be called directly from outside
the DifferentialEvolution class.
"""

import numpy as np, pandas as pd, inspect
from typing import Dict, List, Optional, Union, Any, Callable

from aivalanche_lib.parameters.Parameters import Parameters
from .utils import (
    _update_history, _update_boundaries,
    _get_history_as_df, _get_all_denormalized_boundaries,
    _run_callbacks
    )
from .io import (
    write_history_to_file, write_optimization_info_to_file,
    write_best_parameters_to_file, write_current_population_to_file
    )
from .operators import (
    _generate_donors, _generate_trials,
    _determine_survivors, _determine_best
    )
from .visualizations import (
    _plot_metrics_evolution, _plot_all_parameters_evolution, _plot_boundaries_evolution,
    _plot_mutation_and_recombination, _plot_parameters_evolution
    )

'''
TODO
1. implement clasiffier
2. implement predictor
'''

class DifferentialEvolution:
    """
    Differential Evolution optimizer for high-dimensional parameter spaces.

    This implementation provides the core DE algorithm functionality with support
    for the Parameters class for parameter handling.
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

                 pop_size: int = 100,
                 max_iterations: int = 1000,
                 metric_threshold: float = 0,
                 max_iter_without_improvement: int = 50,
                 improvement_threshold: float = 0.01,

                 mutation_factor_1: Union[float, tuple] = (0.7, 1.1),
                 mutation_factor_2: Union[float, tuple] = (0.2, 0.6),
                 mutation_factor_3: Union[float, tuple] = (0, 0.3),
                 recombination_factor: Union[float, tuple] = (0.8, 0.97),
                 boundary_constraint_method: str = 'random_from_target',

                 init_pop: Optional[Union[str, pd.DataFrame]] = None,
                 init_pop_out_of_range_param: str = 'keep',
                 defaults_in_init_pop: bool = False,
                 defaults_in_init_pop_ratio: float = 0.2,

                 adaptive_boundaries: bool = False,
                 adaptive_boundaries_edge_threshold: float = 0.05,
                 adaptive_boundaries_pop_quantile: float = 0.7,
                 adaptive_boundaries_extension: float = 0.1,
                 adaptive_boundaries_check_period: int = 10,

                 results_dir: Optional[str] = None,
                 
                 # Metamodel parameters
                 use_metamodel: bool = False,
                 metamodel_type: str = 'gaussian_process',
                 metamodel_config: Optional[Dict[str, Any]] = None,
                 metamodel_acquisition_strategy: str = 'mixed',
                 metamodel_acquisition_function: str = 'expected_improvement',
                 metamodel_min_training_points: Optional[int] = None,
                 metamodel_update_frequency: int = 5,
                 metamodel_exploration_ratio: float = 0.2,
                 metamodel_uncertainty_threshold: float = 0.2,
                 metamodel_validation_frequency: int = 10,
                 metamodel_verbose: bool = False):
        """
        Initialize the Differential Evolution optimizer.

        Args:
            seed: Random seed for reproducibility
            eval_func: Function to evaluate parameter sets
            eval_func_args: Additional arguments for the evaluation function
            callback_*: Various callback functions for monitoring progress
            parameters: Parameters object or DataFrame with parameter definitions
            opt_min_or_max: Optimization direction ('min' or 'max')
            pop_size: Population size
            max_iterations: Maximum number of iterations
            metric_threshold: Threshold value for early stopping
            max_iter_without_improvement: Stop after this many iterations without improvement
            improvement_threshold: Minimum relative improvement to reset no-improvement counter
            mutation_factor_*: Scaling factors for DE mutation operator
            recombination_factor: Factor for DE crossover operator
            boundary_constraint_method (str): Method to handle donor values outside boundaries [0, 1]. Options:
                - 'random_from_target' (default): Replace with random value between target and boundary.
                - 'clamp': Set value directly to the boundary limit (0 or 1).
                - 'random': Replace with a new random value within the [0, 1] range.
            init_pop: Initial population (DataFrame or path to CSV)
            init_pop_out_of_range_param: How to handle out-of-range parameters
            defaults_in_init_pop: Whether to use default parameter values in initial population
            defaults_in_init_pop_ratio: Ratio of members with default values
            adaptive_boundaries: Whether to adapt parameter boundaries during optimization
            adaptive_boundaries_*: Settings for adaptive boundaries
            results_dir: Directory to save results
            
            # Metamodel parameters
            use_metamodel: Whether to use metamodel-assisted optimization
            metamodel_type: Type of metamodel ('gaussian_process', 'random_forest', etc.)
            metamodel_config: Configuration dict for the metamodel (passed to metamodel constructor)
            metamodel_acquisition_strategy: Strategy for using metamodel ('all_actual', 'all_metamodel', 
                                          'mixed', 'adaptive', 'uncertainty', 'periodic')
            metamodel_acquisition_function: Acquisition function for 'mixed' strategy 
                                          ('expected_improvement', 'probability_of_improvement', 'upper_confidence_bound')
            metamodel_min_training_points: Minimum training points before using metamodel (default: pop_size)
            metamodel_update_frequency: How often to retrain the metamodel
            metamodel_exploration_ratio: Ratio of exploratory evaluations for 'mixed' strategy
            metamodel_uncertainty_threshold: Uncertainty threshold for 'uncertainty' strategy
            metamodel_validation_frequency: Validation frequency for 'periodic' strategy
            metamodel_verbose: Whether to print metamodel information
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
        self.parameters_names = self.parameters.parameters_names
        self.variable_parameters_names = self.parameters.variable_parameters_names
        self.nr_parameters = self.parameters.nr_parameters
        self.nr_variable_parameters = self.parameters.nr_variable_parameters

        self.opt_min_or_max = opt_min_or_max

        # Population settings
        self.pop_size = int(pop_size)

        # Mutation and recombination factors
        self.mutation_factor_1 = mutation_factor_1
        self.mutation_factor_2 = mutation_factor_2
        self.mutation_factor_3 = mutation_factor_3
        self.recombination_factor = recombination_factor

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

        # Initial population
        self.init_pop = init_pop
        self.init_pop_out_of_range_param = str(init_pop_out_of_range_param)
        self.defaults_in_init_pop = bool(defaults_in_init_pop)
        self.defaults_in_init_pop_ratio = defaults_in_init_pop_ratio

        # Adaptive boundaries
        self.adaptive_boundaries = bool(adaptive_boundaries)
        self.adaptive_boundaries_edge_threshold = adaptive_boundaries_edge_threshold
        self.adaptive_boundaries_pop_quantile = adaptive_boundaries_pop_quantile
        self.adaptive_boundaries_extension = adaptive_boundaries_extension
        self.adaptive_boundaries_check_period = adaptive_boundaries_check_period

        # Results directory
        self.results_dir = results_dir
        
        # Metamodel settings
        self.use_metamodel = use_metamodel
        self.metamodel_evaluator = None
        
        if self.use_metamodel:
            # Import metamodel components
            try:
                from aivalanche_lib.metamodels import MetamodelEvaluator, GaussianProcessMetamodel, AcquisitionStrategy
            except ImportError:
                raise ImportError(
                    "Metamodel support requires the aivalanche_lib.metamodels package. "
                    "Please ensure it is properly installed."
                )
            
            # Create metamodel instance based on type
            if metamodel_type == 'gaussian_process':
                metamodel = GaussianProcessMetamodel(
                    random_state=self.seed,
                    **(metamodel_config or {})
                )
            else:
                raise ValueError(f"Unsupported metamodel type: {metamodel_type}")
            
            # Set default min training points if not specified
            if metamodel_min_training_points is None:
                metamodel_min_training_points = self.pop_size
            
            # Create metamodel evaluator wrapper
            self.metamodel_evaluator = MetamodelEvaluator(
                actual_eval_func=self.eval_func,
                metamodel=metamodel,
                acquisition_strategy=AcquisitionStrategy(metamodel_acquisition_strategy),
                acquisition_function=metamodel_acquisition_function,
                min_training_points=metamodel_min_training_points,
                update_frequency=metamodel_update_frequency,
                exploration_ratio=metamodel_exploration_ratio,
                uncertainty_threshold=metamodel_uncertainty_threshold,
                validation_frequency=metamodel_validation_frequency,
                verbose=metamodel_verbose
            )
            
            # Store original eval_func for reference
            self._original_eval_func = self.eval_func
            # Replace eval_func with metamodel evaluator
            self.eval_func = self.metamodel_evaluator

        # Initialize variables
        self._initialize_variables()

    @property
    def current_parameters(self):
        '''
        Convert normalized trial vectors to real parameter values.
        Returns a DataFrame where columns are parameter names and rows are trial vectors,
        using the Parameters class to handle denormalization and descaling.
        '''
        if self.iter < 1:
            return None

        return self.parameters.denormalize_and_descale_parameters_array(
            pd.DataFrame(columns = self.variable_parameters_names, data = self.trials),
            include_fixed = True
            )

    @property
    def history(self):
        trials_df, trials_normed_df = _get_history_as_df(self, which='trials')
        survivors_df, survivors_normed_df = _get_history_as_df(self, which='survivors')
        bests_df, bests_normed_df = _get_history_as_df(self, which='bests')

        return {
            'trials': trials_df,
            'trials_normed': trials_normed_df,
            'survivors': survivors_df,
            'survivors_normed': survivors_normed_df,
            'bests': bests_df,
            'bests_normed': bests_normed_df,
            'boundaries': self.all_boundaries,
            'boundaries_normed': _get_all_denormalized_boundaries(self)
            }

    @property
    def parameter_evolution_stats(self):
        """
        Extract and compute statistics from the optimization history using pandas groupby.

        Returns:
            dict: Dictionary with one entry per population type ('trials', 'trials_normed', etc.),
                  each containing a single multi-indexed DataFrame. The DataFrame has:
                  - First index level: 'iter' (iteration number)
                  - Second index level: 'stat' (statistic type: 'mean', 'std', etc.)
                  - Columns: parameter names
        """
        # Get history data
        history_data = self.history

        # List of populations to analyze
        populations = ['trials', 'trials_normed', 'survivors', 'survivors_normed']

        # List of statistics to compute - using string method names to avoid FutureWarning
        stat_functions = {
            'mean': 'mean',
            'std': 'std',
            'var': 'var',
            'min': 'min',
            'max': 'max',
            'median': 'median',
            # For percentiles, we need to use a lambda or a custom function
            'q25': lambda x: x.quantile(0.25),
            'q75': lambda x: x.quantile(0.75)
        }

        # Dictionary to store results for each population
        all_stats = {}

        # Process each population
        for pop_name in populations:
            if pop_name in history_data and not history_data[pop_name].empty:
                # Get the dataframe for this population
                df = history_data[pop_name]

                # Get parameter columns (exclude 'iter' and 'metric')
                param_cols = [col for col in df.columns if col not in ['iter', 'metric']]

                # Create a list to store statistic DataFrames
                stat_dfs = []

                # Calculate all statistics using groupby
                for stat_name, stat_func in stat_functions.items():
                    # Group by iteration and calculate the statistic for each parameter
                    grouped_stats = df.groupby('iter')[param_cols].agg(stat_func)

                    # Add the statistic name as a new index level
                    grouped_stats['stat'] = stat_name
                    grouped_stats.set_index('stat', append=True, inplace=True)

                    # Add to the list of statistic DataFrames
                    stat_dfs.append(grouped_stats)

                # Combine all statistic DataFrames into one
                if stat_dfs:
                    combined_stats = pd.concat(stat_dfs)

                    # Reorder index levels to have iter first, then stat
                    combined_stats = combined_stats.reorder_levels(['iter', 'stat'])

                    # Sort by iteration and then statistic name
                    combined_stats = combined_stats.sort_index(level=['iter', 'stat'])

                    # Store in the result dictionary
                    all_stats[pop_name] = combined_stats

        return all_stats

    @property
    def optimization_info(self):
        """
        Property that dynamically assembles optimization information.

        Returns:
            dict: Dictionary containing input parameters and current output state
                  of the optimization process.
        """
        # Dynamically capture all input parameters from __init__ signature

        # Get the signature of the __init__ method
        init_signature = inspect.signature(self.__class__.__init__)

        # Extract all parameter names except 'self'
        param_names = [p for p in init_signature.parameters if p != 'self']

        # Create dictionary with all input parameters
        input_info = {name: getattr(self, name) for name in param_names if hasattr(self, name)}

        # Add parameters data in the proper format
        input_info['parameters'] = self.parameters.all_parameters.to_dict('records')

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

        # Initialize the targets, donors, trials and survivors to None
        self.targets = np.full((self.pop_size, self.nr_variable_parameters), np.nan)
        self.targets_metrics = np.full((self.pop_size), np.nan)

        self.donors = np.full((self.pop_size, self.nr_variable_parameters), np.nan)

        self.trials = np.full((self.pop_size, self.nr_variable_parameters), np.nan)
        self.trials_metrics = np.full((self.pop_size), np.nan)

        self.survivors = np.full((self.pop_size, self.nr_variable_parameters), np.nan)
        self.survivors_metrics = np.full((self.pop_size), np.nan)

        # Initialize adaptive boundaries
        self.boundaries_min = np.zeros((self.nr_variable_parameters))       # Initialize with zeros
        self.boundaries_max = np.ones((self.nr_variable_parameters))        # Initialize with ones
        self.boundaries_range = self.boundaries_max - self.boundaries_min   # Initialize boundaries range

        # History tracking
        self.all_trials = np.zeros((0, self.pop_size, self.nr_variable_parameters))
        self.all_trials_metrics = np.zeros((0, self.pop_size))

        self.all_survivors = np.zeros((0, self.pop_size, self.nr_variable_parameters))
        self.all_survivors_metrics = np.zeros((0, self.pop_size))

        self.all_bests = np.zeros((0, self.nr_variable_parameters))
        self.all_bests_metrics = np.zeros((0,1))

        # Initialize boundaries history tracking with multi-indexed DataFrame
        # First index: iteration number
        # Second index: boundary type ('min', 'max', 'range')
        # Columns: parameter names
        index = pd.MultiIndex.from_product([[0], ['min', 'max', 'range']], names=['iter', 'type'])
        self.all_boundaries = pd.DataFrame(
            index=index,
            columns=self.variable_parameters_names,
            dtype=float
        )

        # Set initial values
        self.all_boundaries.loc[(0, 'min'), :] = self.boundaries_min
        self.all_boundaries.loc[(0, 'max'), :] = self.boundaries_max
        self.all_boundaries.loc[(0, 'range'), :] = self.boundaries_range

        # Best solution tracking
        self.best = np.full((1, self.nr_variable_parameters), None)
        self.best_parameters = None
        self.best_metric = float('-inf') if self.opt_min_or_max == 'max' else float('inf')
        self.best_response = None

        # Current responses
        self.current_responses = None
        self.current_metrics = None

        # Coefficients
        self.mut_coef_1 = None
        self.mut_coef_2 = None
        self.mut_coef_3 = None
        self.recom_coef = None
        self.rand_mem_1 = None
        self.rand_mem_2 = None
        self.rand_mem_3 = None

    def run_optimization(self):
        """Run the optimization loop until stop criteria are met."""
        # Prepare first iteration
        self._prepare_next_iter()

        # Main optimization loop
        while not self.is_stop_criteria_reached:
            self._run_iteration()

            # Run callbacks
            _run_callbacks(self, last_iteration = False)

            # Generate new trials for next iteration
            self._prepare_next_iter()

        _run_callbacks(self, last_iteration = True)

        # Final processing
        self.show_final_result()

    def _run_iteration(self):
        """Run a single iteration of the optimization algorithm."""

        # Evaluate parameters
        extra_arguments = {
            'iteration': self.iter,
            'best_metric': self.best_metric,
            'best_parameters': self.best_parameters,
            **self.eval_func_args
        }
        
        # Add optimization direction for metamodel evaluator
        if self.use_metamodel:
            extra_arguments['opt_min_or_max'] = self.opt_min_or_max

        # The eval_func should return a list, where each item is a dict that has at least the element 'metric'.
        self.current_responses = self.eval_func(parameters = self.current_parameters, **extra_arguments)
        self.current_metrics = [item['metric'] for item in self.current_responses]

        # Save metrics
        self.trials_metrics = np.array(self.current_metrics)

        # Determine survivors, best solution and update history
        _determine_survivors(self)
        _determine_best(self)
        _update_history(self)

        # Update nr of evaluations
        self.nr_evaluations += len(self.current_responses)

    def _prepare_next_iter(self):
        """Prepare for the next iteration."""

        self.iter += 1

        # Check if stop criteria are met
        self._set_is_stop_criteria_reached()

        if self.is_stop_criteria_reached:
            # Decrement the iter if the last iteration is already finished.
            self.iter -= 1
        else:
            # Set the survivors as targets for the next iteration
            self.targets = self.survivors
            self.targets_metrics = self.survivors_metrics

            # Adapt boundaries if enabled
            if self.adaptive_boundaries:
                _update_boundaries(self)

            # Generate new donors and trials
            _generate_donors(self)
            _generate_trials(self)

            # # Plot mutation and recombination for 2 params
            # if self.iter == 2:
            #     self._plot_mutation_and_recombination()

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
        
        # Show metamodel statistics if used
        if self.use_metamodel and self.metamodel_evaluator:
            print("\n-------------------------- Metamodel Statistics --------------------------\n")
            stats = self.get_metamodel_statistics()
            if stats:
                print(f"Actual function evaluations: {stats['n_actual_evaluations']}")
                print(f"Metamodel predictions: {stats['n_metamodel_evaluations']}")
                print(f"Metamodel usage ratio: {stats['metamodel_usage_ratio']:.2%}")
                print(f"Time saved: {stats['time_saved']:.2f} seconds")
                print(f"Speedup factor: {stats['speedup_factor']:.2f}x")
                if stats['avg_validation_error'] is not None:
                    print(f"Average validation error: {stats['avg_validation_error']:.4f}")
            print("\n--------------------------------------------------------------------------------\n\n")
    
    def get_metamodel_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Get statistics about metamodel usage if metamodel is enabled.
        
        Returns:
            Dictionary with metamodel statistics or None if metamodel not used
        """
        if self.use_metamodel and self.metamodel_evaluator:
            return self.metamodel_evaluator.get_statistics()
        return None

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
    def _plot_mutation_and_recombination(self, param_1_name = None, param_2_name = None, fig = None, ax = None, save_path = None):
        if param_1_name is None:
            param_1_name = self.parameters_names[0]

        if param_2_name is None:
            param_2_name = self.parameters_names[1]

        param_1_idx = self.parameters_names.index(param_1_name)
        param_2_idx = self.parameters_names.index(param_2_name)

        # member_idx = self.rng.randint(0, self.pop_size)
        for member_idx in range(self.pop_size):
            all_targets = self.targets[:, [param_1_idx, param_2_idx]]
            target = self.targets[member_idx, [param_1_idx, param_2_idx]]
            donor = self.donors[member_idx, [param_1_idx, param_2_idx]]
            trial = self.trials[member_idx, [param_1_idx, param_2_idx]]
            best = self.best[[param_1_idx, param_2_idx]]
            mut_coef_1 = self.mut_coef_1[member_idx, 0]
            mut_coef_2 = self.mut_coef_2[member_idx, 0]
            mut_coef_3 = self.mut_coef_3[member_idx, 0]
            recom_coef = self.recom_coef[member_idx, 0]
            rand_mem_1 = self.rand_mem_1[member_idx]
            rand_mem_2 = self.rand_mem_2[member_idx]
            rand_mem_3 = self.rand_mem_3[member_idx]

            _plot_mutation_and_recombination(param_1_name, param_2_name,
                               all_targets, target, donor, trial, best,
                               mut_coef_1, mut_coef_2, mut_coef_3, recom_coef,
                               rand_mem_1, rand_mem_2, rand_mem_3,
                               fig, ax, save_path)

    def plot_metrics(self, which="bests", fig=None, ax=None, figsize=(10, 6),
                     x_scale = 'linear', y_scale = 'symlog',
                     save_path=None, title=None, **kwargs):
        """
        Plot the evolution of metrics throughout the optimization process.

        Args:
            which (str): Which metrics to plot, can be 'trials', 'survivors', or 'bests'
            fig (matplotlib.figure.Figure): Optional existing figure to plot on
            ax (matplotlib.axes.Axes): Optional existing axes to plot on
            figsize (tuple): Size of the figure in inches (width, height)
            save_path (str): If provided, the figure will be saved to this path
            title (str): Custom title for the plot. If None, a default title will be used
            add_info (bool): Whether to add optimization information to the plot (only for 'bests')
            **kwargs: Additional keyword arguments passed to the matplotlib plotting functions

        Returns:
            tuple: Figure and axes objects from matplotlib
        """
        # Import the visualization function if it's in a separate module
        # from visualization import plot_metrics_evolution

        # Create iteration array
        iter_array = np.arange(1, self.iter + 1)

        # Prepare data based on the selected metrics type
        if which == "trials":
            # Get trial metrics and flatten
            metrics = self.all_trials_metrics.flatten()
            # Create iteration points that match the shape of flattened metrics
            # Each iteration is repeated for each member of the population
            iterations = np.repeat(iter_array, self.pop_size)

            # Set title if not given
            title = title or "Trials metrics evolution"

        elif which == "survivors":
            # Get survivor metrics and flatten
            metrics = self.all_survivors_metrics.flatten()
            # Create iteration points that match the shape of flattened metrics
            # Each iteration is repeated for each member of the population
            iterations = np.repeat(iter_array, self.pop_size)

            # Set title if not given
            title = title or "Survivors metrics evolution"

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
            raise ValueError(f"Invalid 'which' parameter: {which}. Must be 'trials', 'survivors', or 'bests'")

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

    def plot_all_parameters_evolution(self, which="trials", iter_start=None, iter_end=None,
                                      fig=None, axes=None, title=None, show_parameter_names=True, save_path=None,
                                      figsize=None, bins=100, nr_rows=1, **kwargs):
        """
        Create vertical histograms for each parameter, arranged in a grid.

        Args:
            which (str): Type of data to plot, either 'trials', 'survivors', or 'bests'
            iter_start (int): First iteration to include
            iter_end (int): Last iteration to include. If None, include all iterations
            fig (matplotlib.figure.Figure): Optional existing figure to plot on
            axes (list): Optional list of existing axes to plot on
            title (str): Custom title for the figure. If None, a default title will be used
            save_path (str): If provided, the figure will be saved to this path
            figsize (tuple): Size of the figure in inches (width, height). If None, calculated automatically
            bins (int): Number of bins for the histograms
            nr_rows (int): Number of rows to arrange the parameter plots
            **kwargs: Additional keyword arguments passed to plt.imshow

        Returns:
            tuple: Figure and list of axes
        """

        # Get parameter values and metrics based on the 'which' parameter
        if which == "trials":
            # Get history as DataFrame
            df = self.history['trials']
            title = title or "Trial Parameters Distribution"
        elif which == "survivors":
            # Get history as DataFrame
            df = self.history['survivors']
            title = title or "Survivor Parameters Distribution"
        elif which == "bests":
            # Get history as DataFrame
            df = self.history['bests']
            title = title or "Best Solution Parameters Distribution"
        else:
            raise ValueError(f"Invalid 'which' parameter: {which}. Must be 'trials', 'survivors', or 'bests'")

        # Create the parameter evolution histogram visualization
        fig, axes = _plot_all_parameters_evolution(
            df=df,
            iter_start=iter_start,
            iter_end=iter_end,
            fig=fig,
            axes=axes,
            title=title,
            show_parameter_names=show_parameter_names,
            save_path=save_path,
            figsize=figsize,
            bins=bins,
            nr_rows=nr_rows,
            **kwargs
        )

        return fig, axes

    def plot_parameters_evolution(self, parameter_names: list = None, which="trials",
                                        iter_start=None, iter_end=None, iter_step=1,
                                        fig=None, axes=None, bins=100, figsize=(10, 6),
                                        title=None, save_path=None, nr_rows=1, **kwargs):
        """
        Plot the evolution of a single parameter's histogram across iterations.

        Args:
            parameter_name (str): Name of the parameter to visualize
            which (str): Type of data to plot, either 'trials', 'survivors', or 'bests'
            iter_start (int): First iteration to include (if None, starts from minimum)
            iter_end (int): Last iteration to include (if None, goes to maximum)
            iter_step (int): Step size for iterations (to reduce number of histograms)
            fig (matplotlib.figure.Figure): Optional existing figure to plot on
            axes (matplotlib.axes.Axes): Optional existing axes to plot on
            bins (int): Number of bins for the histograms
            figsize (tuple): Size of the figure in inches (width, height)
            colormap (str): Colormap to use for the histograms
            title (str): Title for the figure (if None, uses parameter name)
            save_path (str): If provided, the figure will be saved to this path
            nr_rows: Number of rows to arrange the parameter plots
            **kwargs: Additional keyword arguments passed to plt.imshow

        Returns:
            tuple: Figure and axes objects
        """
        # Validate parameter names
        if parameter_names is not None:
            for param in parameter_names:
                if param not in self.variable_parameters_names:
                    raise ValueError(f"Parameter '{param}' not found in variable parameters")
        else:
            parameter_names = self.parameters_names

        # Get parameter values and metrics based on the 'which' parameter
        if which == "trials":
            # Get history as DataFrame
            df = self.history['trials']
            title = title or "Evolution of parameter distributions in trials"
        elif which == "survivors":
            # Get history as DataFrame
            df = self.history['survivors']
            title = title or "Evolution of parameter distributions in survivors"
        else:
            raise ValueError(f"Invalid 'which' parameter: {which}. Must be 'trials', 'survivors', or 'bests'")

        # Create the parameter histogram evolution visualization
        fig, ax = _plot_parameters_evolution(
            df=df,
            parameter_names=parameter_names,
            iter_start=iter_start,
            iter_end=iter_end,
            iter_step=iter_step,
            fig=fig,
            axes=axes,
            bins=bins,
            figsize=figsize,
            title=title,
            save_path=save_path,
            nr_rows=nr_rows,
            **kwargs
        )

        return fig, ax

    def plot_boundaries(self, normed: bool = True, parameter_names: list = None,
                     iter_start: int = None, iter_end: int = None,
                     fig = None, axes: list = None, title: str = None,
                     save_path: str = None, figsize: tuple = None, nr_rows: int = 1,
                     **kwargs):
        """
        Plot the evolution of parameter boundaries throughout the optimization.

        Args:
            normed: Whether to plot normalized (True) or denormalized (False) boundaries
            parameter_names: List of parameter names to plot (if None, plots all parameters)
            iter_start: First iteration to include
            iter_end: Last iteration to include
            fig: Optional existing figure to plot on
            axes: Optional list of existing axes to plot on
            title: Title for the figure (if None, a default title will be used)
            save_path: If provided, the figure will be saved to this path
            figsize: Size of the figure in inches (width, height)
            nr_rows: Number of rows to arrange the parameter plots
            **kwargs: Additional keyword arguments passed to the plotting function

        Returns:
            tuple: Figure and list of axes
        """
        # Get boundary data
        if normed:
            boundaries_df = self.all_boundaries
            title = title or "Evolution of Normalized Parameter Boundaries"
        else:
            boundaries_df = _get_all_denormalized_boundaries(self)
            title = title or "Evolution of Parameter Boundaries in Original Units"

        # Validate parameter names
        if parameter_names is not None:
            for param in parameter_names:
                if param not in self.variable_parameters_names:
                    raise ValueError(f"Parameter '{param}' not found in variable parameters")
        else:
            parameter_names = self.parameters_names


        # Call the visualization function
        return _plot_boundaries_evolution(
            df=boundaries_df,
            parameter_names=parameter_names,
            iter_start=iter_start,
            iter_end=iter_end,
            fig=fig,
            axes=axes,
            title=title,
            save_path=save_path,
            figsize=figsize,
            nr_rows=nr_rows,
            normalized=normed,
            **kwargs
        )

        return fig, axes
