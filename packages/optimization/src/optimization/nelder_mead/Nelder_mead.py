import numpy as np, pandas as pd, json
from typing import Callable, Tuple
from optimization.utils import preprocess_parameters, unnorm_member, norm_member, scale_parameter, generate_spendley_points
from optimization.nelder_mead.visualization import plot_simplex_2d

class Nelder_mead:
    """
    Nelder-Mead optimization algorithm implementation.
    """

    def __init__(
        self,
        seed: int = None,                                      # seed for reproducibility
        # function that is used for the evaluation of the fittness of the parameter sets.
        # It should accept an array of dicts, i.e. one dict is made of param_name: param_value, and it should return a dict with 2 keys, 'data' and 'metrics'.
        # Metrics should be an array of the metrics, one for each entry of the input array.
        # And data should also be an array to contain the results of each simulation of the inputs.
        eval_func: callable = None,
        eval_func_args: dict = None,                           # extra arguments to pass to the evaluation function
        callback_after_first_iter: callable = None,            # callback that is called after the first iteration
        callback_after_each_iter: callable = None,             # callback that is called after each iteration
        callback_after_last_iter: callable = None,             # callback that is called after the last iteration
        callback_after_better_solution_found: callable = None, # callback that is called after finding a better solution

        parameters: pd.DataFrame = None,                       # the parameters to be optimized
        opt_min_or_max: str = 'min',                           # either search for the 'min' or 'max'
        ignore_boundaries: bool = False,                       # when True, boundaries will not be respected

        reflection_coefficient: float | tuple = (0.9, 1.1),
        expansion_coefficient: float | tuple = (1.5, 2.5),
        contraction_coefficient: float | tuple = (0.3, 0.5),
        shrink_coefficient: float | tuple = (0.3, 0.5),

        max_iterations: int = 1000,
        max_iter_without_improvement: int = 50,
        metric_threshold: float = 1e-8,
        improvement_threshold: float = 0.01,                   # consider as improvement if the difference to the previous best metric is greater than this number

        initial_point: np.array = None,
        initial_point_mode: str = None,                   # 'corner' or 'centroid'. when corner, it is part of the first simplex, when centroid, then the initial point is the centroid of the first simplex
        initial_simplex_edge_length: float | tuple = (0.4, 0.7),
        use_default_in_initial_simplex: bool = False,
    ):

        # Seed
        if seed is None:
            seed = np.random.randint(0, 1000)
        self.seed = seed
        self.rng = np.random.RandomState(self.seed)

        self.eval_func = eval_func
        self.eval_func_args = {} if eval_func_args is None else eval_func_args
        self.callback_after_first_iter = callback_after_first_iter
        self.callback_after_each_iter = callback_after_each_iter
        self.callback_after_last_iter = callback_after_last_iter
        self.callback_after_better_solution_found = callback_after_better_solution_found

        # Algorithm coefficients
        self.reflection_coefficient = reflection_coefficient
        self.expansion_coefficient = expansion_coefficient
        self.contraction_coefficient = contraction_coefficient
        self.shrink_coefficient = shrink_coefficient

        # Stopping criteria parameters
        self.max_iterations = max_iterations
        self.max_iter_without_improvement = max_iter_without_improvement
        self.metric_threshold = metric_threshold
        self.improvement_threshold = improvement_threshold

        # Parameters
        self.parameters = parameters
        self.ignore_boundaries = ignore_boundaries
        self.opt_min_or_max = opt_min_or_max

        # Initial points
        self.initial_point = initial_point
        self.initial_point_mode = initial_point_mode
        self.initial_simplex_edge_length = initial_simplex_edge_length
        self.use_default_in_initial_simplex = use_default_in_initial_simplex

        self._initialize_variables()

    def _initialize_variables(self):
        # Initialize tracking variables
        self.simplex = None
        self.simplex_normed = None
        self.simplex_unscaled = None
        self.simplex_metric = None
        self.simplex_response = None
        self.simplex_size = 0

        self.reflected = None
        self.reflected_normed = None
        self.reflected_unscaled = None
        self.reflected_metric = None
        self.reflected_response = None

        self.expanded = None
        self.expanded_normed = None
        self.expanded_unscaled = None
        self.expanded_metric = None
        self.expanded_response = None

        self.contracted = None
        self.contracted_normed = None
        self.contracted_unscaled = None
        self.contracted_metric = None
        self.contracted_response = None

        self.best = None
        self.best_normed = None
        self.best_unscaled = None
        self.best_metric = float('inf') if self.opt_min_or_max == 'min' else float('-inf')

        self.worst_metric = None
        self.second_worst_metric = None

        # Results and state
        self.iter = 0
        self.iter_no_improvement = 0
        self.abort_flag = False
        self.is_stop_criteria_reached = False
        self.stop_reason = ""
        self.centroid = None

        self.parameters = preprocess_parameters(self.parameters)
        self.nr_parameters = self.parameters.shape[0]
        self.parameter_names = self.parameters['name'].tolist()
        self.parameters_transform_list = self.parameters['transform'].tolist()

        self.boundaries = np.array([self.parameters['min_scaled'], self.parameters['max_scaled']])
        self.boundaries_min = np.min(self.boundaries, axis = 0)
        self.boundaries_max = np.max(self.boundaries, axis = 0)
        self.boundaries_range = self.boundaries_max - self.boundaries_min

        self.history = {'parameters': self.parameters,
                        'trials': pd.DataFrame(columns = ['iter', 'trial_normed', 'trial', 'trial_unscaled', 'trial_metric']),
                        'simplexes': pd.DataFrame(columns = ['iter', 'simplex_normed', 'simplex', 'simplex_unscaled', 'simplex_metric']),
                        'bests': pd.DataFrame(columns = ['iter', 'best_normed', 'best', 'best_unscaled', 'best_metric']),
                        'boundaries': pd.DataFrame(columns = ['iter', 'boundaries_min', 'boundaries_max'])}
        self.optimization_info = {}
        self.nr_evaluations = 0

        if self.initial_point is not None:
            if self.initial_point_mode is None:
                self.initial_point_mode = 'corner'
        elif self.use_default_in_initial_simplex:
            default_values = np.array(self.parameters['value_scaled'])
            self.initial_point = np.apply_along_axis(func1d = norm_member,
                                                     axis = 0,
                                                     arr = default_values,
                                                     minimum = self.boundaries_min,
                                                     maximum = self.boundaries_max)
            if self.initial_point_mode is None:
                self.initial_point_mode = 'corner'
        else:
            self.initial_point = np.full(self.nr_parameters, 0.5)
            if self.initial_point_mode is None:
                self.initial_point_mode = 'centroid'

    def run_optimization(self):

        self._run_first_iteration()

        while not self.is_stop_criteria_reached:

            # Calculate centroid
            self._compute_centroid()

            # Try reflection
            self._try_reflection()

            if self._is_better(self.reflected_metric, self.best_metric): # better than best
                # Try expansion
                self._try_expansion()
                if self._is_better(self.expanded_metric, self.reflected_metric):
                    self._accept_expansion()
                else:
                    self._accept_reflection()
            elif self._is_better(self.reflected_metric, self.second_worst_metric): # between best and second_worst
                self._accept_reflection()
            elif self._is_better(self.reflected_metric, self.worst_metric): # between worst and second_worst
                # Outside contraction
                self._try_contraction(mode = 'outside')
                if self._is_better(self.contracted_metric, self.reflected_metric):
                    self._accept_contraction()
                else:
                    self._perform_shrink()
            else: # worse than worst
                # Inside contraction
                self._try_contraction(mode = 'inside')
                if self._is_better(self.contracted_metric, self.worst_metric):
                    self._accept_contraction()
                else:
                    self._perform_shrink()

            self._prepare_next_iteration()

        if self.callback_after_last_iter is not None:
            self.callback_after_last_iter(history = self.history,
                                          iteration = self.iter,
                                          best_parameters = self._get_parameters(self.best_unscaled),
                                          best_metric = self.best_metric,
                                          parameter_names = self.parameter_names,
                                          stop_reason = self.stop_reason,
                                          **self.eval_func_args)

    def _is_better(self, metric_1, metric_2, include_equal: bool = False):
        if np.isnan(metric_1) or np.isnan(metric_2):
            return False

        if self.opt_min_or_max == 'min':
            if include_equal:
                return metric_1 <= metric_2
            else:
                return metric_1 < metric_2
        else:
            if include_equal:
                return metric_1 >= metric_2
            else:
                return metric_1 > metric_2

    def _run_first_iteration(self):
        self.iter = 1

        # Initialize
        self._initialize_simplex()

        self._run_simplex()
        self._sort_simplex()
        self._update_history_simplexes()
        self._update_history_trials(mode = 'simplex')

        self._set_is_stop_criteria_reached()
        self._update_optimization_info()

        if self.callback_after_first_iter is not None:
            self.callback_after_first_iter(parameters = self._get_parameters(self.simplex_unscaled),
                                           responses = self.simplex_response,
                                           iteration = self.iter,
                                           best_parameters = self._get_best_parameters_unscaled(),
                                           best_metric = self.best_metric,
                                           parameter_names = self.parameter_names,
                                           **self.eval_func_args)

        if self.callback_after_each_iter is not None:
            self.callback_after_each_iter(parameters = self._get_parameters(self.simplex_unscaled),
                                          responses = self.simplex_response,
                                          iteration = self.iter,
                                          best_parameters = self._get_best_parameters_unscaled(),
                                          best_metric = self.best_metric,
                                          parameter_names = self.parameter_names,
                                          better_solution_found = self.better_solution_found,
                                          **self.eval_func_args)

    def _run_simplex(self, exclude_best = False):
        if exclude_best:
            parameters = self._get_parameters(self.simplex_unscaled[1:])
            extra_arguments = {'iteration': self.iter,                              # extra arguments to give to the evaluation function
                               'best_metric': self.best_metric,
                               'best_parameters': self.best_unscaled,
                               **self.eval_func_args}
            responses = self.eval_func(parameters = parameters, **extra_arguments)  # run the evaluation function
            self.simplex_response['data'][1:] = responses['data']
            self.simplex_response['metrics'][1:] = responses['metrics']
            self.simplex_metric[1:] = np.array(responses['metrics'])
        else:
            parameters = self._get_parameters(self.simplex_unscaled)
            extra_arguments = {'iteration': self.iter,                              # extra arguments to give to the evaluation function
                               'best_metric': self.best_metric,
                               'best_parameters': self.best_unscaled,
                               **self.eval_func_args}
            responses = self.eval_func(parameters = parameters, **extra_arguments)  # run the evaluation function
            self.simplex_response = responses
            self.simplex_metric = np.array(responses['metrics'])
        self.nr_evaluations += len(parameters)

    def _sort_simplex(self):
        # Sort simplex by metric value
        order = np.argsort(self.simplex_metric)
        if self.opt_min_or_max == 'max':
            order = order[::-1]  # Reverse order for maximization
        self.simplex = self.simplex[order]
        self.simplex_normed = self.simplex_normed[order]
        self.simplex_unscaled = self.simplex_unscaled[order]
        self.simplex_metric = self.simplex_metric[order]
        self.simplex_response['data'] = [self.simplex_response['data'][i] for i in order]
        self.simplex_response['metrics'] = [self.simplex_response['metrics'][i] for i in order]

        self._update_best()
        self.worst_metric = self.simplex_metric[-1]
        self.second_worst_metric = self.simplex_metric[-2]

    def _get_parameters(self, arr):
        parameters = []
        for values in arr.reshape(-1, self.nr_parameters):
            tmp = {key: val for key, val in zip(self.parameter_names, values)}
            parameters.append(tmp)
        return parameters

    def _get_unscaled_arr(self, arr):
        temp = np.copy(arr)
        ind = 1 if len(temp.shape) == 2 else 0
        for i, val in np.ndenumerate(temp):
            index = i[ind]
            if self.parameters_transform_list[index] == 'log':
                temp[i] = np.longdouble(10.0**val)
            elif self.parameters_transform_list[index] == 'neglog':
                temp[i] = -np.longdouble(10.0**val)
            else:
                temp[i] = val
        return temp

    # Get best parameters as a dictionary
    def get_best_parameters(self):
        return self._get_best_parameters_unscaled()

    def _get_best_parameters_unscaled(self):
        return {key: val for key, val in zip(self.parameter_names, self.best_unscaled)}

    def _get_best_parameters_normed(self):
        return {key: val for key, val in zip(self.parameter_names, self.best_normed)}

    def _set_is_stop_criteria_reached(self) -> None:
        """Check if any stopping criteria have been reached."""
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
        elif self.iter >= self.max_iterations:
            self.iter -= 1
            self.is_stop_criteria_reached = True
            self.stop_reason = "maximum number of iterations reached"
        else:
            self.is_stop_criteria_reached = False

    def _update_best(self):
        new_best_metric = self.simplex_metric[0]
        if (self.opt_min_or_max == 'min' and new_best_metric < self.best_metric) or \
           (self.opt_min_or_max == 'max' and new_best_metric > self.best_metric):
            self.better_solution_found = True
        else:
            self.better_solution_found = False

        if self.better_solution_found:
            self.best = self.simplex[0]
            self.best_normed = self.simplex_normed[0]
            self.best_unscaled = self.simplex_unscaled[0]
            self.best_metric = self.simplex_metric[0]

            # Calculate relative improvement with protection against division by zero
            if np.abs(self.best_metric) > np.finfo(float).eps:
                relative_improvement = np.abs(new_best_metric - self.best_metric) / np.abs(self.best_metric)
            else:
                relative_improvement = np.abs(new_best_metric - self.best_metric)

            if relative_improvement >= self.improvement_threshold:
                self.iter_no_improvement = 0
            else:
                self.iter_no_improvement += 1

            if self.callback_after_better_solution_found is not None:
                self.callback_after_better_solution_found(parameters = self._get_parameters(self.simplex_unscaled),
                                                          responses = self.simplex_response,
                                                          iteration = self.iter,
                                                          best_parameters = self.best_unscaled,
                                                          best_metric = self.best_metric,
                                                          parameter_names = self.parameter_names,
                                                          **self.eval_func_args)

        self._update_history_bests()

    def _initialize_simplex(self) -> None:
        points = generate_spendley_points(n = self.nr_parameters,
                                          r = self._generate_initial_simplex_edge_length(),
                                          initial_point = self.initial_point,
                                          initial_point_mode = self.initial_point_mode)

        points = self._check_boundaries(points)

        self.simplex_normed = points
        self.simplex = np.apply_along_axis(func1d = unnorm_member,
                                           axis = 1,
                                           arr = self.simplex_normed,
                                           minimum = self.boundaries_min,
                                           maximum = self.boundaries_max)
        self.simplex_unscaled = self._get_unscaled_arr(self.simplex)
        # plot_simplex_2d(self.simplex_unscaled)
        self.simplex_size = self.simplex.shape[0]

    def _update_history_simplexes(self):
        zipped = zip([self.iter] * self.simplex_size,
                     self.simplex_normed.tolist(),
                     self.simplex.tolist(),
                     self.simplex_unscaled.tolist(),
                     self.simplex_metric.tolist())
        new_simplex = pd.DataFrame(columns = ['iter', 'simplex_normed', 'simplex', 'simplex_unscaled', 'simplex_metric'],
                                   data = [item for item in zipped])

        self.history['simplexes'] = pd.concat([self.history['simplexes'], new_simplex]).reset_index(drop = True)

    def _update_history_trials(self, mode: str = 'simplex'):
        if mode == 'simplex':
            zipped = zip([self.iter] * self.simplex_size,
                         self.simplex_normed.tolist(),
                         self.simplex.tolist(),
                         self.simplex_unscaled.tolist(),
                         self.simplex_metric.tolist())
            df = pd.DataFrame(columns = ['iter', 'trial_normed', 'trial', 'trial_unscaled', 'trial_metric'],
                              data = [item for item in zipped])
        elif mode == 'reflection':
            df = pd.DataFrame.from_dict([{'iter': self.iter,
                                          'trial_normed': self.reflected_normed,
                                          'trial': self.reflected,
                                          'trial_unscaled': self.reflected_unscaled,
                                          'trial_metric': self.reflected_metric}])
        elif mode == 'expansion':
            df = pd.DataFrame.from_dict([{'iter': self.iter,
                                          'trial_normed': self.expanded_normed,
                                          'trial': self.expanded,
                                          'trial_unscaled': self.expanded_unscaled,
                                          'trial_metric': self.expanded_metric}])
        elif mode == 'contraction':
            df = pd.DataFrame.from_dict([{'iter': self.iter,
                                          'trial_normed': self.contracted_normed,
                                          'trial': self.contracted,
                                          'trial_unscaled': self.contracted_unscaled,
                                          'trial_metric': self.contracted_metric}])

        self.history['trials'] = pd.concat([self.history['trials'], df]).reset_index(drop = True)

    def _update_history_bests(self):
        new_best = pd.DataFrame.from_dict([{'iter': self.iter,
                                            'best_normed': self.best_normed,
                                            'best': self.best,
                                            'best_unscaled': self.best_unscaled,
                                            'best_metric': self.best_metric}])
        self.history['bests'] = pd.concat([self.history['bests'], new_best]).reset_index(drop = True)

    def _compute_centroid(self):
        self.centroid = np.mean(self.simplex_normed[:-1], axis=0)

    def _prepare_next_iteration(self):
        self.iter += 1
        self._sort_simplex()
        self._update_history_simplexes()
        self._set_is_stop_criteria_reached()
        self._update_optimization_info()
        if self.callback_after_each_iter is not None:
            self.callback_after_each_iter(parameters = self._get_parameters(self.simplex_unscaled),
                                          responses = self.simplex_response,
                                          iteration = self.iter,
                                          best_parameters = self._get_best_parameters_unscaled(),
                                          best_metric = self.best_metric,
                                          parameter_names = self.parameter_names,
                                          better_solution_found = self.better_solution_found,
                                          **self.eval_func_args)

    def _accept_reflection(self):
        self.simplex[-1,:] = self.reflected
        self.simplex_normed[-1,:] = self.reflected_normed
        self.simplex_unscaled[-1,:] = self.reflected_unscaled
        self.simplex_metric[-1] = self.reflected_metric
        self.simplex_response['data'][-1] = self.reflected_response['data']
        self.simplex_response['metrics'][-1] = self.reflected_metric

    def _accept_expansion(self):
        self.simplex[-1,:] = self.expanded
        self.simplex_normed[-1,:] = self.expanded_normed
        self.simplex_unscaled[-1,:] = self.expanded_unscaled
        self.simplex_metric[-1] = self.expanded_metric
        self.simplex_response['data'][-1] = self.expanded_response['data']
        self.simplex_response['metrics'][-1] = self.expanded_metric

    def _accept_contraction(self):
        self.simplex[-1,:] = self.contracted
        self.simplex_normed[-1,:] = self.contracted_normed
        self.simplex_unscaled[-1,:] = self.contracted_unscaled
        self.simplex_metric[-1] = self.contracted_metric
        self.simplex_response['data'][-1] = self.contracted_response['data']
        self.simplex_response['metrics'][-1] = self.contracted_metric

    def _try_reflection(self):
        coeff = self._generate_reflection_coefficient()
        self.reflected_normed = self.centroid + coeff * (self.centroid - self.simplex_normed[-1])
        self.reflected_normed = self._check_boundaries(self.reflected_normed)
        self.reflected = np.apply_along_axis(func1d = unnorm_member,
                                           axis = 0,
                                           arr = self.reflected_normed,
                                           minimum = self.boundaries_min,
                                           maximum = self.boundaries_max)
        self.reflected_unscaled = self._get_unscaled_arr(self.reflected)
        parameters = self._get_parameters(self.reflected_unscaled)
        extra_arguments = {'iteration': self.iter,                              # extra arguments to give to the evaluation function
                           'best_metric': self.best_metric,
                           'best_parameters': self.best_unscaled,
                           **self.eval_func_args}
        responses = self.eval_func(parameters = parameters, **extra_arguments)  # run the evaluation function
        self.reflected_metric = np.array(responses['metrics'])[0]
        self.reflected_response = {'data': responses['data'][0], 'metric': responses['metrics'][0]}
        self._update_history_trials(mode = 'reflection')
        self.nr_evaluations += 1

    def _try_expansion(self):
        coeff = self._generate_expansion_coefficient()
        self.expanded_normed = self.centroid + coeff * (self.reflected_normed - self.centroid)
        self.expanded_normed = self._check_boundaries(self.expanded_normed)
        self.expanded = np.apply_along_axis(func1d = unnorm_member,
                                           axis = 0,
                                           arr = self.expanded_normed,
                                           minimum = self.boundaries_min,
                                           maximum = self.boundaries_max)
        self.expanded_unscaled = self._get_unscaled_arr(self.expanded)
        parameters = self._get_parameters(self.expanded_unscaled)
        extra_arguments = {'iteration': self.iter,                              # extra arguments to give to the evaluation function
                           'best_metric': self.best_metric,
                           'best_parameters': self.best_unscaled,
                           **self.eval_func_args}
        responses = self.eval_func(parameters = parameters, **extra_arguments)  # run the evaluation function
        self.expanded_metric = np.array(responses['metrics'])[0]
        self.expanded_response = {'data': responses['data'][0], 'metric': responses['metrics'][0]}
        self._update_history_trials(mode = 'expansion')
        self.nr_evaluations += 1

    def _try_contraction(self, mode: str = 'outside'):
        coeff = self._generate_contraction_coefficient()
        if mode == 'outside':
            self.contracted_normed = self.centroid + coeff * (self.reflected_normed - self.centroid)
        elif mode == 'inside':
            self.contracted_normed = self.centroid + coeff * (self.simplex_normed[-1] - self.centroid)
        else:
            raise Exception("Error: mode has to be 'outside' or 'inside'")

        self.contracted_normed = self._check_boundaries(self.contracted_normed)
        self.contracted = np.apply_along_axis(func1d = unnorm_member,
                                              axis = 0,
                                              arr = self.contracted_normed,
                                              minimum = self.boundaries_min,
                                              maximum = self.boundaries_max)
        self.contracted_unscaled = self._get_unscaled_arr(self.contracted)
        parameters = self._get_parameters(self.contracted_unscaled)
        extra_arguments = {'iteration': self.iter,                              # extra arguments to give to the evaluation function
                           'best_metric': self.best_metric,
                           'best_parameters': self.best_unscaled,
                           **self.eval_func_args}
        responses = self.eval_func(parameters = parameters, **extra_arguments)  # run the evaluation function
        self.contracted_metric = np.array(responses['metrics'])[0]
        self.contracted_response = {'data': responses['data'][0], 'metric': responses['metrics'][0]}
        self._update_history_trials(mode = 'contraction')
        self.nr_evaluations += 1

    def _perform_shrink(self):
        """Perform the shrink operation on the simplex."""
        coeff = self._generate_shrink_coefficient()
        for i in range(1, self.simplex_size):
            self.simplex_normed[i] = self.best_normed + coeff * (self.simplex_normed[i] - self.best_normed)

        self.simplex_normed = self._check_boundaries(self.simplex_normed)
        self.simplex = np.apply_along_axis(func1d = unnorm_member,
                                           axis = 1,
                                           arr = self.simplex_normed,
                                           minimum = self.boundaries_min,
                                           maximum = self.boundaries_max)
        self.simplex_unscaled = self._get_unscaled_arr(self.simplex)
        self._run_simplex(exclude_best = True)
        self._update_history_trials(mode = 'simplex')

    def _generate_reflection_coefficient(self):
        if isinstance(self.reflection_coefficient, (float, int)):
            return self.reflection_coefficient
        elif isinstance(self.reflection_coefficient, (tuple, list)):
            return self.rng.uniform(self.reflection_coefficient[0], self.reflection_coefficient[1])

    def _generate_contraction_coefficient(self):
        if isinstance(self.contraction_coefficient, (float, int)):
            return self.contraction_coefficient
        elif isinstance(self.reflection_coefficient, (tuple, list)):
            return self.rng.uniform(self.contraction_coefficient[0], self.contraction_coefficient[1])

    def _generate_expansion_coefficient(self):
        if isinstance(self.expansion_coefficient, (float, int)):
            return self.expansion_coefficient
        elif isinstance(self.expansion_coefficient, (tuple, list)):
            return self.rng.uniform(self.expansion_coefficient[0], self.expansion_coefficient[1])

    def _generate_shrink_coefficient(self):
        if isinstance(self.shrink_coefficient, (float, int)):
            return self.shrink_coefficient
        elif isinstance(self.shrink_coefficient, (tuple, list)):
            return self.rng.uniform(self.shrink_coefficient[0], self.shrink_coefficient[1])

    def _generate_initial_simplex_edge_length(self):
        if isinstance(self.initial_simplex_edge_length, (float, int)):
            return self.initial_simplex_edge_length
        elif isinstance(self.initial_simplex_edge_length, (tuple, list)):
            return self.rng.uniform(self.initial_simplex_edge_length[0], self.initial_simplex_edge_length[1])

    def _check_boundaries(self, arr):
        if not self.ignore_boundaries:
            upper_violation_mask = arr > 1
            arr[upper_violation_mask] = self.rng.uniform(arr[upper_violation_mask], 1, size = len(arr[upper_violation_mask]))

            # if donor is lower than 0, correct its value by generating a value between 0 and the current one
            lower_violation_mask = arr < 0
            arr[lower_violation_mask] = self.rng.uniform(0, arr[lower_violation_mask], size = len(arr[lower_violation_mask]))

        return arr

    def _update_optimization_info(self):
        if self.iter == 1:
            self.optimization_info['input'] = {'seed': self.seed,
                                               'max_iterations': self.max_iterations,
                                               'max_iter_without_improvement': self.max_iter_without_improvement,
                                               'improvement_threshold': self.improvement_threshold,
                                               'metric_threshold': self.metric_threshold,
                                               'reflection_coefficient': self.reflection_coefficient,
                                               'expansion_coefficient': self.expansion_coefficient,
                                               'contraction_coefficient': self.contraction_coefficient,
                                               'shrink_coefficient': self.shrink_coefficient,
                                               'initial_point': list(self.initial_point),
                                               'initial_point_mode': self.initial_point_mode,
                                               'initial_simplex_edge_length': self.initial_simplex_edge_length,
                                               'use_default_in_initial_simplex': self.use_default_in_initial_simplex,
                                               'ignore_bounaries': self.ignore_boundaries,
                                               'parameters': self.parameters[['name', 'min', 'default', 'max', 'scale']].to_dict('records')}
        self.optimization_info['output'] = {'iter': self.iter,
                                            'best_metric': self.best_metric,
                                            'best_parameters': self._get_best_parameters_unscaled(),
                                            'nr_evaluations': self.nr_evaluations,
                                            'stop_reason': self.stop_reason}

    def get_all_trials_exploded(self):
        data = self.history['trials'][['iter', 'trial_unscaled', 'trial_metric']]
        result_df = pd.concat([data.drop('trial_unscaled', axis=1),
                               pd.DataFrame(data['trial_unscaled'].tolist(), columns = self.parameter_names)], axis=1)
        result_df = result_df.rename(columns={'trial_metric': 'metric'})
        result_df['iter'] = result_df['iter'].astype(int)
        result_df = result_df[['iter'] + self.parameter_names + ['metric']]
        return result_df

    def get_all_simplexes_exploded(self):
        data = self.history['simplexes'][['iter', 'simplex_unscaled', 'simplex_metric']]
        result_df = pd.concat([data.drop('simplex_unscaled', axis=1),
                               pd.DataFrame(data['simplex_unscaled'].tolist(), columns = self.parameter_names)], axis=1)
        result_df = result_df.rename(columns={'simplex_metric': 'metric'})
        result_df['iter'] = result_df['iter'].astype(int)
        result_df = result_df[['iter'] + self.parameter_names + ['metric']]
        return result_df

    def write_best_parameters_to_file(self, file_path: str = None):
        if file_path is not None:
            try:
                df = pd.DataFrame({'name': self.parameter_names, 'value': self.best_unscaled})

                if file_path.split('.')[-1] == 'csv':
                    df.to_csv(file_path, index = False)
                elif file_path.split('.')[-1] == 'json':
                    df.to_json(file_path, orient = 'records', indent = 4)

            except Exception as e:
                print('ERROR on write_best_parameters_to_file:')
                print(e)
                pass

    # Write optimization info to a file
    def write_optimization_info_to_file(self, file_path = None):
        if file_path is not None:
            # Convert the main structure to a formatted string
            json_str = json.dumps(self.optimization_info, indent=4)

            # Find the parameters section and replace it with single-line formatting
            param_list = self.optimization_info['input']['parameters']
            single_line_params = ',\n      '.join(json.dumps(param) for param in param_list)
            param_section = '"parameters": [\n      ' + single_line_params + '\n    ]'

            # Replace the original parameters section
            start = json_str.find('"parameters":')
            end = json_str.find(']', start) + 1
            json_str = json_str[:start] + param_section + json_str[end:]
            with open(file_path, 'w') as f:
                f.write(json_str)

    def abort_optimization(self):
        """Set the abort flag to stop the optimization."""
        self.abort_flag = True
