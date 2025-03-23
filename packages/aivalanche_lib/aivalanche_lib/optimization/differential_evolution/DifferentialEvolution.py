"""
Differential Evolution Optimizer

This implementation provides an efficient optimization algorithm for high-dimensional spaces,
using the Differential Evolution method. It integrates with the Parameters class for parameter
handling and supports various DE strategies, adaptive boundaries, and customizable stopping criteria.

Author: Gazmend Alia
"""

import numpy as np, pandas as pd
from scipy.stats.qmc import Halton
from typing import Dict, List, Optional, Union, Any, Callable

# Import Parameters class
from aivalanche_lib.parameters.Parameters import Parameters
from .visualizations import (plot_metrics_evolution, plot_all_parameters_evolution, plot_boundaries_evolution,
                             plot_mutation_and_recombination, plot_single_parameter_evolution)

'''
TODO
2. implement incoorpotation of defaults and init pop in the first population
3. implement clasiffier
4. implement predictor
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

                 init_pop: Optional[Union[str, pd.DataFrame]] = None,
                 init_pop_out_of_range_param: str = 'keep',
                 defaults_in_init_pop: bool = False,
                 defaults_in_init_pop_ratio: float = 0.2,

                 adaptive_boundaries: bool = False,
                 adaptive_boundaries_edge_threshold: float = 0.05,
                 adaptive_boundaries_pop_quantile: float = 0.7,
                 adaptive_boundaries_extension: float = 0.1,
                 adaptive_boundaries_check_period: int = 10,

                 results_dir: Optional[str] = None):
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
            init_pop: Initial population (DataFrame or path to CSV)
            init_pop_out_of_range_param: How to handle out-of-range parameters
            defaults_in_init_pop: Whether to use default parameter values in initial population
            defaults_in_init_pop_ratio: Ratio of members with default values
            adaptive_boundaries: Whether to adapt parameter boundaries during optimization
            adaptive_boundaries_*: Settings for adaptive boundaries
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

        # Initialize variables
        self._initialize_variables()

    @property
    def history(self):
        trials_df, trials_normed_df = self._get_history_as_df(which='trials')
        survivors_df, survivors_normed_df = self._get_history_as_df(which='survivors')
        bests_df, bests_normed_df = self._get_history_as_df(which='bests')

        return {
            'trials': trials_df,
            'trials_normed': trials_normed_df,
            'survivors': survivors_df,
            'survivors_normed': survivors_normed_df,
            'bests': bests_df,
            'bests_normed': bests_normed_df,
            'all_boundaries': self.all_boundaries,
            'all_boundaries_normed': self._get_all_denormalized_boundaries()
            }

    @property
    def stats(self):
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

    def _initialize_variables(self):
        """Initialize all internal variables for the optimization process."""
        self.iter = 0
        self.iter_no_improvement = 0
        self.abort_flag = False
        self.is_stop_criteria_reached = False
        self.stop_reason = ""

        # Initialize the targets, donors, trials and survivors to None
        self.targets = np.full((self.pop_size, self.nr_variable_parameters), None)
        self.targets_metrics = np.full((self.pop_size), None)

        self.donors = np.full((self.pop_size, self.nr_variable_parameters), None)

        self.trials = np.full((self.pop_size, self.nr_variable_parameters), None)
        self.trials_metrics = np.full((self.pop_size), None)

        self.survivors = np.full((self.pop_size, self.nr_variable_parameters), None)
        self.survivors_metrics = np.full((self.pop_size), None)

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

        # Optimization info
        self.optimization_info = {}

        # Current parameters and responses
        self.current_parameters = None
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
            self._run_callbacks(last_iteration = False)

            # Generate new trials for next iteration
            self._prepare_next_iter()

        self._run_callbacks(last_iteration = True)

        # Final processing
        self.show_final_result()

    def _run_iteration(self):
        """Run a single iteration of the optimization algorithm."""
        # Get next parameters to evaluate
        self.current_parameters = self._get_current_parameters()

        # Evaluate parameters
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
        self.trials_metrics = np.array(self.current_metrics)

        # Determine survivors and update best solution
        self._determine_survivors()
        self._determine_best()
        self._update_boundaries()
        self._update_history()
        self._update_optimization_info()

    def _get_current_parameters(self):
        '''
        Convert normalized trial vectors to real parameter values.
        Returns a DataFrame where columns are parameter names and rows are trial vectors,
        using the Parameters class to handle denormalization and descaling.
        '''
        return self.parameters.denormalize_and_descale_parameters_array(
            pd.DataFrame(columns = self.variable_parameters_names, data = self.trials),
            include_fixed_parameters = True
            )

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
            if self.adaptive_boundaries and self.iter % self.adaptive_boundaries_check_period == 0:
                self._update_boundaries()

            # Generate new donors and trials
            self._generate_donors()
            self._generate_trials()

            # # Plot mutation and recombination for 2 params
            # if self.iter == 2:
            #     self._plot_mutation_and_recombination()

    def _incorporate_initial_population(self):
        """Incorporate provided initial population into donors."""
        print('incorporate init pop')

    def _incorporate_default_values(self):
        """Incorporate default parameter values in initial population."""
        print('incorporate default values')

    def _generate_trials(self):
        """Generate trial vectors for each target-donor pair."""
        if self.iter == 1:
            # In the first iteration, trials are equal to donors
            self.trials = self.donors
        else:
            # Generate recombinations between targets and donors
            self._generate_recombinations()

    def _generate_donors(self):
        """Generate donor vectors for each target."""
        if self.iter == 1:
            self._generate_initial_population()
        else:
            # Generate mutations for each target
            self._generate_mutations()

    def _generate_initial_population(self):
         # Generate donors randomly using Halton sequence
         sampler = Halton(d=self.nr_variable_parameters, seed=self.seed)
         self.donors = sampler.random(self.pop_size)

         # Handle initial population if provided
         if self.init_pop is not None:
             self._incorporate_initial_population()

         # Handle default values in initial population
         if self.defaults_in_init_pop:
             self._incorporate_default_values()

    def _generate_mutations(self, dice=None):
        """Generate mutation vectors using DE mutation operators."""
        if dice is None:
            # Select 3 distinct random indices for each target
            dice = [
                self.rng.choice([j for j in range(self.pop_size) if j != i], size=(1, 3), replace=False)
                for i in range(self.pop_size)
            ]
            dice = np.array(dice).reshape(-1, 3)

        # Extract random members from the population
        temp = self.targets[dice].reshape(-1, 3, self.nr_variable_parameters)
        self.rand_mem_1 = temp[:, 0, :]
        self.rand_mem_2 = temp[:, 1, :]
        self.rand_mem_3 = temp[:, 2, :]

        # Calculate mutation coefficients
        self.mut_coef_1 = self._get_coefficient(self.mutation_factor_1)
        self.mut_coef_2 = self._get_coefficient(self.mutation_factor_2)
        self.mut_coef_3 = self._get_coefficient(self.mutation_factor_3)

        # Calculate donor vectors using DE mutation formula
        self.donors = (
            self.rand_mem_1 +                                        # Random vector 1
            self.mut_coef_1 * (self.rand_mem_2 - self.rand_mem_3) +  # Scaled difference between random vectors 2 and 3
            self.mut_coef_2 * (self.best - self.rand_mem_1) +        # Scaled difference between best and random vector 1
            self.mut_coef_3 * (self.best - self.targets)             # Scaled difference between best and target
        )

        # Correct values outside [0, 1] range
        self._check_donors_boundaries()

    def _get_coefficient(self, factor):
        if isinstance(factor, (float, int)):
            return factor
        elif isinstance(factor, (tuple, list)):
            return self.rng.uniform(factor[0], factor[1], size=(self.pop_size, 1))
        return None

    def _check_donors_boundaries(self):
        """
        Correct values outside [0, 1] range in donor vectors.
        Returns:
            Corrected donor vectors
        """
        # Get row and column indices of violations
        upper_violation_mask = self.donors > self.boundaries_max
        lower_violation_mask = self.donors < self.boundaries_min

        # Process upper violations
        if np.any(upper_violation_mask):
            rows, cols = np.where(upper_violation_mask)
            self.donors[upper_violation_mask] = self.rng.uniform(
                self.targets[upper_violation_mask],
                self.boundaries_max[cols],
                size=len(rows)
            )

        # Process lower violations
        if np.any(lower_violation_mask):
            rows, cols = np.where(lower_violation_mask)
            self.donors[lower_violation_mask] = self.rng.uniform(
                self.boundaries_min[cols],
                self.targets[lower_violation_mask],
                size=len(rows)
            )

    def _generate_recombinations(self, dice=None):
        """Generate recombination vectors by crossing over targets and donors."""
        # Generate random values for each parameter
        if dice is None:
            dice = self.rng.rand(self.pop_size, self.nr_variable_parameters)

        # Get recombination coefficient
        self.recom_coef = self._get_coefficient(self.recombination_factor)

        # Create trials by combining donors and targets
        self.trials = np.where(dice < self.recom_coef, self.donors, self.targets)

    def _run_callbacks(self, last_iteration = False):
        callbacks_args = {
            'optimizer': self,
            'iteration': self.iter,
            'parameters': self.current_parameters,
            'responses': self.current_responses,
            'best_parameters': self.best_parameters,
            'best_metric': self.best_metric,
            'best_response': self.best_response,
            'parameters_names': self.parameters.parameters_names,
            'all_trials': self.all_trials,
            'stop_reason': self.stop_reason,
            **self.eval_func_args
        }

        if last_iteration:
            if self.callback_after_last_iter is not None:
                self.callback_after_last_iter(**callbacks_args)
        else:
            if self.iter == 1 and self.callback_after_first_iter is not None:
                self.callback_after_first_iter(**callbacks_args)

            if self.callback_after_each_iter is not None:
                self.callback_after_each_iter(**callbacks_args)

            if self.better_solution_found and self.callback_after_better_solution is not None:
                    self.callback_after_better_solution(**callbacks_args)

    def _determine_survivors(self):
        """Determine survivors for the next generation."""
        if self.iter == 1:
            # In the first iteration, all trials become survivors
            self.survivors = self.trials
            self.survivors_metrics = self.trials_metrics
        else:
            # Selection: compare trials with targets and choose the better ones
            mask = (self.trials_metrics > self.targets_metrics) if self.opt_min_or_max == 'max' else (self.trials_metrics < self.targets_metrics)

            # Create survivors by selecting better solutions
            self.survivors_metrics = np.where(mask, self.trials_metrics, self.targets_metrics)
            self.survivors = np.where(mask.reshape(-1, 1), self.trials, self.targets)

    def _determine_best(self):
        """Determine the best solution in the current population."""
        # Get the index of the best survivor
        best_index = np.argmax(self.survivors_metrics) if self.opt_min_or_max == 'max' else np.argmin(self.survivors_metrics)
        current_best_metric = self.survivors_metrics[best_index]

        if self.opt_min_or_max == 'max' and current_best_metric > self.best_metric:
            self.better_solution_found = True
        elif self.opt_min_or_max == 'min' and current_best_metric < self.best_metric:
            self.better_solution_found = True
        else:
            self.better_solution_found = False

        # Update best if better solution found
        if self.better_solution_found:
            if abs(current_best_metric - self.best_metric) / abs(self.best_metric) >= self.improvement_threshold:
                self.iter_no_improvement = 0
            else:
                self.iter_no_improvement += 1

            self.best = self.survivors[best_index]
            self.best_parameters = self.current_parameters.iloc[best_index]
            self.best_metric = self.survivors_metrics[best_index]
            self.best_response = self.current_responses[best_index]
        else:
            self.iter_no_improvement += 1

    def _update_history(self):
        """Update history by appending current trial vectors, metrics, survivors, and survivor metrics."""
        # Append current trials to history
        trials_to_append = self.trials.reshape(1, self.pop_size, self.nr_variable_parameters)
        self.all_trials = np.vstack((self.all_trials, trials_to_append))

        # Append current metrics to metrics history
        metrics_to_append = self.trials_metrics.reshape(1, self.pop_size)
        self.all_trials_metrics = np.vstack((self.all_trials_metrics, metrics_to_append))

        # Append current survivors to survivors history
        survivors_to_append = self.survivors.reshape(1, self.pop_size, self.nr_variable_parameters)
        self.all_survivors = np.vstack((self.all_survivors, survivors_to_append))

        # Append current survivor metrics to survivor metrics history
        survivor_metrics_to_append = self.survivors_metrics.reshape(1, self.pop_size)
        self.all_survivors_metrics = np.vstack((self.all_survivors_metrics, survivor_metrics_to_append))

        # Append current best to bests history
        best_to_append = self.best.reshape(1, self.nr_variable_parameters)
        self.all_bests = np.vstack((self.all_bests, best_to_append))

        # Append current best metric to bests metrics history
        best_metric_to_append = self.best_metric
        self.all_bests_metrics = np.vstack((self.all_bests_metrics, best_metric_to_append))

    def _update_boundaries(self):
        """
        Update the parameter boundaries based on population distribution using vectorized operations.

        This method implements adaptive boundaries by checking if a significant portion
        of the population is near the boundaries, and extending them if necessary.
        """
        # Skip if adaptive boundaries are not enabled
        if not self.adaptive_boundaries:
            return

        # Skip if it's not time to check boundaries based on the period
        if self.iter % self.adaptive_boundaries_check_period != 0:
            return

        # Calculate quantiles for all parameters at once
        lower_quantiles = np.quantile(self.survivors, 1 - self.adaptive_boundaries_pop_quantile, axis=0)
        upper_quantiles = np.quantile(self.survivors, self.adaptive_boundaries_pop_quantile, axis=0)

        # Calculate thresholds for boundary extension
        lower_thresholds = self.boundaries_min + self.adaptive_boundaries_edge_threshold * self.boundaries_range
        upper_thresholds = self.boundaries_max - self.adaptive_boundaries_edge_threshold * self.boundaries_range

        # Check which parameters need boundary extensions
        lower_extension_mask = lower_quantiles < lower_thresholds
        upper_extension_mask = upper_quantiles > upper_thresholds

        # Flag to track if boundaries were changed
        boundaries_changed = False

        # Calculate new boundary values
        if np.any(lower_extension_mask):
            boundaries_changed = True
            # Extend lower boundaries where needed
            extension_amount = self.adaptive_boundaries_extension * self.boundaries_range[lower_extension_mask]
            new_mins = self.boundaries_min[lower_extension_mask] - extension_amount

            # Log the parameters that were extended
            for i, param_idx in enumerate(np.where(lower_extension_mask)[0]):
                print(f"Extended lower boundary for parameter {param_idx} to {new_mins[i]}")

            # Update the boundaries
            self.boundaries_min[lower_extension_mask] = new_mins

        if np.any(upper_extension_mask):
            boundaries_changed = True
            # Extend upper boundaries where needed
            extension_amount = self.adaptive_boundaries_extension * self.boundaries_range[upper_extension_mask]
            new_maxs = self.boundaries_max[upper_extension_mask] + extension_amount

            # Log the parameters that were extended
            for i, param_idx in enumerate(np.where(upper_extension_mask)[0]):
                print(f"Extended upper boundary for parameter {param_idx} to {new_maxs[i]}")

            # Update the boundaries
            self.boundaries_max[upper_extension_mask] = new_maxs

        # Update the range after modifying boundaries
        self.boundaries_range = self.boundaries_max - self.boundaries_min

        # If boundaries were changed, add new entries to the boundaries history
        if boundaries_changed:
            # Create MultiIndex for the new entries
            new_index = pd.MultiIndex.from_product([[self.iter], ['min', 'max', 'range']], names=['iter', 'type'])

            # Create DataFrame with current boundaries
            new_boundaries = pd.DataFrame(
                index=new_index,
                columns=self.variable_parameters_names,
                dtype=float
            )

            # Set values
            new_boundaries.loc[(self.iter, 'min'), :] = self.boundaries_min
            new_boundaries.loc[(self.iter, 'max'), :] = self.boundaries_max
            new_boundaries.loc[(self.iter, 'range'), :] = self.boundaries_range

            # Append to the history
            self.all_boundaries = pd.concat([self.all_boundaries, new_boundaries])

    def _update_optimization_info(self):
        """Update optimization information dictionary."""
        if self.iter == 1:
            self.optimization_info['input'] = {
                'seed': self.seed,
                'pop_size': self.pop_size,
                'max_iterations': self.max_iterations,
                'max_iter_without_improvement': self.max_iter_without_improvement,
                'improvement_threshold': self.improvement_threshold,
                'metric_threshold': self.metric_threshold,
                'mutation_factor_1': self.mutation_factor_1,
                'mutation_factor_2': self.mutation_factor_2,
                'mutation_factor_3': self.mutation_factor_3,
                'recombination_factor': self.recombination_factor,
                'adaptive_boundaries': self.adaptive_boundaries,
                'results_dir': self.results_dir,
                'parameters': self.parameters.all_parameters.to_dict('records')
            }

        self.optimization_info['output'] = {
            'iter': self.iter,
            'best_metric': self.best_metric,
            'best_parameters': self.best_parameters,
            'stop_reason': self.stop_reason
        }

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

    def _get_history_as_df(self, which='trials'):
        """
        Convert the optimization history to two DataFrames for analysis.

        Args:
            which (str): Which history to convert: 'trials', 'survivors', or 'bests'

        Returns:
            tuple: (df, df_normed)
                - df: DataFrame with iteration number, denormalized parameters, and metrics
                - df_normed: DataFrame with iteration number, normalized parameters, and metrics
        """
        if which not in ['trials', 'survivors', 'bests']:
            raise ValueError("'which' parameter must be 'trials', 'survivors', or 'bests'")

        # Select the appropriate arrays based on 'which' parameter
        if which == 'trials':
            values_array = self.all_trials
            metrics_array = self.all_trials_metrics
        elif which == 'survivors':
            values_array = self.all_survivors
            metrics_array = self.all_survivors_metrics
        else:  # bests
            values_array = self.all_bests
            metrics_array = self.all_bests_metrics

        if len(values_array) == 0:
            return pd.DataFrame(), pd.DataFrame()

        # Number of iterations
        n_iters = values_array.shape[0]

        # Special handling for bests which has a different shape
        if which == 'bests':
            # Create iteration column (one iteration number per best solution)
            iter_column = np.arange(1, n_iters + 1)

            # For bests, metrics_array might be a 2D array with one value per row
            # Ensure metrics_flat is a 1D array
            metrics_flat = metrics_array.flatten()

            # Reshape values to 2D array (n_iters, n_params) - bests already has the right shape
            values_normed_flat = values_array
        else:
            # Create iteration column (repeating each iteration number pop_size times)
            iter_column = np.repeat(np.arange(1, n_iters + 1), self.pop_size)

            # Flatten metrics to 1D array
            metrics_flat = metrics_array.flatten()

            # Reshape values to 2D array (n_iters*pop_size, n_params)
            values_normed_flat = values_array.reshape(-1, self.nr_variable_parameters)

        # Create DataFrame with normalized values
        df_normed = pd.DataFrame(
            values_normed_flat,
            columns=self.variable_parameters_names
        )

        # Convert normalized values to original parameter values
        df = self.parameters.denormalize_and_descale_parameters_array(
            pd.DataFrame(columns=self.variable_parameters_names, data=values_normed_flat),
            include_fixed_parameters=True
        )

        # Add iter and metric columns to both DataFrames
        # Insert iter as first column
        df_normed.insert(0, 'iter', iter_column)
        df.insert(0, 'iter', iter_column)

        # Add metric as last column
        df_normed['metric'] = metrics_flat
        df['metric'] = metrics_flat

        return df, df_normed

    def _get_all_denormalized_boundaries(self):
        """
        Get the denormalized boundary values for all iterations in history using vectorized operations.

        Returns:
            pandas.DataFrame: DataFrame with multi-index (iter, type: 'min', 'max', 'range')
                             and columns for each parameter name, containing the
                             denormalized boundary values throughout optimization.
        """
        # Initialize result DataFrame with same structure as all_boundaries
        result = pd.DataFrame(
            index=self.all_boundaries.index,
            columns=self.variable_parameters_names,
            dtype=float
        )

        # Get all unique iterations
        iterations = self.all_boundaries.index.get_level_values('iter').unique()

        # Extract all min boundaries at once
        all_mins = self.all_boundaries.xs('min', level='type')

        # Extract all max boundaries at once
        all_maxs = self.all_boundaries.xs('max', level='type')

        # Denormalize all min values at once
        denorm_mins = self.parameters.denormalize_and_descale_parameters_array(
            all_mins,
            include_fixed_parameters=False
        )

        # Denormalize all max values at once
        denorm_maxs = self.parameters.denormalize_and_descale_parameters_array(
            all_maxs,
            include_fixed_parameters=False
        )

        # Calculate the range in denormalized space
        denorm_ranges = denorm_maxs - denorm_mins

        # Store the denormalized values in the result DataFrame
        for iter_num in iterations:
            result.loc[(iter_num, 'min')] = denorm_mins.loc[iter_num]
            result.loc[(iter_num, 'max')] = denorm_maxs.loc[iter_num]
            result.loc[(iter_num, 'range')] = denorm_ranges.loc[iter_num]

        return result

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

    def write_best_parameters_to_file(self, file_path=None):
        """
        Write best parameters to a file (CSV or JSON).

        Args:
            file_path (str): Path to the output file. If None, uses 'best_parameters.csv'
                            The file extension (.csv or .json) determines the output format.
        """
        if file_path is None:
            raise ValueError('Please provide a file_path!')

        self.best_parameters.name = 'value'
        self.best_parameters.index.name = 'param'

        # Write to file based on extension
        ext = file_path.lower().split('.')[-1]

        if ext == 'csv':
            self.best_parameters.to_csv(file_path)
            print(f"Best parameters written to {file_path}")
        elif ext == 'json':
            self.best_parameters.to_json(file_path, indent=4)
            print(f"Best parameters written to {file_path}")
        else:
            raise ValueError(f"Unsupported file extension: .{ext}. Use .csv or .json")

    def write_current_population_to_file(self, file_path=None):
        """
        Write current population to a file (CSV or JSON).

        Args:
            file_path (str): Path to the output file. If None, uses 'population.csv'
                            The file extension (.csv or .json) determines the output format.
        """
        if file_path is None:
            raise ValueError('Please provide a file_path!')

        # Write to file based on extension
        ext = file_path.lower().split('.')[-1]

        if ext == 'csv':
            self.current_parameters.to_csv(file_path, index=False)
            print(f"Current population written to {file_path}")
        elif ext == 'json':
            self.current_parameters.to_json(file_path, orient='records', indent=4)
            print(f"Current population written to {file_path}")
        else:
            raise ValueError(f"Unsupported file extension: .{ext}. Use .csv or .json")

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

            plot_mutation_and_recombination(param_1_name, param_2_name,
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
        fig, ax = plot_metrics_evolution(
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
        fig, axes = plot_all_parameters_evolution(
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

    def plot_single_parameter_evolution(self, parameter_name: str, which="trials",
                                        iter_start=None, iter_end=None, iter_step=1,
                                        fig=None, ax=None, bins=100, figsize=(10, 6),
                                        title=None, save_path=None, **kwargs):
        """
        Plot the evolution of a single parameter's histogram across iterations.

        Args:
            parameter_name (str): Name of the parameter to visualize
            which (str): Type of data to plot, either 'trials', 'survivors', or 'bests'
            iter_start (int): First iteration to include (if None, starts from minimum)
            iter_end (int): Last iteration to include (if None, goes to maximum)
            iter_step (int): Step size for iterations (to reduce number of histograms)
            fig (matplotlib.figure.Figure): Optional existing figure to plot on
            ax (matplotlib.axes.Axes): Optional existing axes to plot on
            bins (int): Number of bins for the histograms
            figsize (tuple): Size of the figure in inches (width, height)
            colormap (str): Colormap to use for the histograms
            title (str): Title for the figure (if None, uses parameter name)
            save_path (str): If provided, the figure will be saved to this path
            **kwargs: Additional keyword arguments passed to plt.imshow

        Returns:
            tuple: Figure and axes objects
        """
        # Check if the parameter exists in the variable parameters
        if parameter_name not in self.variable_parameters_names:
            raise ValueError(f"Parameter '{parameter_name}' not found in variable parameters")

        # Get parameter values and metrics based on the 'which' parameter
        if which == "trials":
            # Get history as DataFrame
            df = self.history['trials']
            title = title or f"Evolution of {parameter_name} distribution in trials"
        elif which == "survivors":
            # Get history as DataFrame
            df = self.history['survivors']
            title = title or f"Evolution of {parameter_name} distribution in survivors"
        else:
            raise ValueError(f"Invalid 'which' parameter: {which}. Must be 'trials', 'survivors', or 'bests'")

        # Create the parameter histogram evolution visualization
        fig, ax = plot_single_parameter_evolution(
            df=df,
            parameter_name=parameter_name,
            iter_start=iter_start,
            iter_end=iter_end,
            iter_step=iter_step,
            fig=fig,
            ax=ax,
            bins=bins,
            figsize=figsize,
            title=title,
            save_path=save_path,
            **kwargs
        )

        return fig, ax

    def plot_boundaries(self,
                     normed: bool = True,
                     parameter_names: list = None,
                     iter_start: int = None,
                     iter_end: int = None,
                     fig = None,
                     axes: list = None,
                     title: str = None,
                     save_path: str = None,
                     figsize: tuple = None,
                     nr_rows: int = 1,
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
            boundaries_df = self._get_all_denormalized_boundaries()
            title = title or "Evolution of Parameter Boundaries in Original Units"

        # Validate parameter names
        if parameter_names is not None:
            for param in parameter_names:
                if param not in self.variable_parameters_names:
                    raise ValueError(f"Parameter '{param}' not found in variable parameters")
        else:
            parameter_names = self.parameters_names


        # Call the visualization function
        return plot_boundaries_evolution(
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
