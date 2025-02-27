#%% Imports
import pandas as pd
import numpy as np
from optimization.differential_evolution import Differential_evolution
from optimization.test_functions import Test_Functions
from optimization.visualization import plot_evolution_2d, create_plot_evolution_2d_video, plot_evolution_2d_with_metrics

#%% Function configurations
FUNCTION_CONFIGS = {
    'himmelblau': {
        'func': Test_Functions.himmelblau,
        'bounds': {'min': [-5, -5], 'max': [5, 5]},
        'default': [1, 1],
        'global_minimum_params': [(3, 2), (-2.805118, 3.131312), (-3.779310, -3.283186), (3.584428, -1.848126)],
        'global_minimum_value': 0,
        'info': 'Global minimum: f(3.0, 2.0) = 0.0. Multiple global minima.'
    },
    'modified_himmelblau': {
        'func': Test_Functions.modified_himmelblau,
        'bounds': {'min': [-5, -5], 'max': [5, 5]},
        'default': [1, 1],
        'global_minimum_params': [(3, 2)],
        'global_minimum_value': 0,
        'info': 'Global minimum: f(3.0, 2.0) = 0.0. Multiple local minima.'
    },
    'rastrigin': {
        'func': Test_Functions.rastrigin,
        'bounds': {'min': [-5.12, -5.12], 'max': [5.12, 5.12]},
        'default': [0, 0],
        'global_minimum_params': [(0, 0)],
        'global_minimum_value': 0,
        'info': 'Global minimum: f(0,0) = 0. Highly multimodal with regular spacing.'
    },
    'rosenbrock': {
        'func': Test_Functions.rosenbrock,
        'bounds': {'min': [-2, -2], 'max': [2, 2]},
        'default': [0, 0],
        'global_minimum_params': [(0, 0)],
        'global_minimum_value': 0,
        'info': 'Global minimum: f(1,1) = 0. Narrow parabolic valley.'
    },
    'eggholder': {
        'func': Test_Functions.eggholder,
        'bounds': {'min': [-512, -512], 'max': [512, 512]},
        'default': [0, 0],
        'global_minimum_params': [(512, 404.2319)],
        'global_minimum_value': -959.6407,
        'info': 'Global minimum: f(512, 404.2319) = -959.6407. Many local minima.'
    },
    'cross_in_tray': {
        'func': Test_Functions.cross_in_tray,
        'bounds': {'min': [-10, -10], 'max': [10, 10]},
        'default': [0, 0],
        'global_minimum_params': [(1.3491, 1.3491), (1.3491, -1.3491), (-1.3491, 1.3491), (-1.3491, -1.3491)],
        'global_minimum_value': -2.06261,
        'info': 'Global minima: f(±1.3491, ±1.3491) = -2.06261. Multiple global minima.'
    },
    'holder_table': {
        'func': Test_Functions.holder_table,
        'bounds': {'min': [-10, -10], 'max': [10, 10]},
        'default': [0, 0],
        'global_minimum_params': [(0, 0)],
        'global_minimum_value': -19.2085,
        'info': 'Global minima: f(±8.05502, ±9.66459) = -19.2085. Multiple global minima.'
    },
    'easom': {
        'func': Test_Functions.easom,
        'bounds': {'min': [-100, -100], 'max': [100, 100]},
        'default': [0, 0],
        'global_minimum_params': [(0, 0)],
        'global_minimum_value': -1,
        'info': 'Global minimum: f(π,π) = -1. Needle in a haystack problem.'
    }
}

def evaluate_function(parameters: dict = None, **kwargs):
    """
    Generic wrapper for all test functions.
    Args:
        parameters: Dictionary containing list of parameter sets to evaluate
        function_name: Name of the function to evaluate
        kwargs: Additional arguments (will be printed)
    Returns:
        Dictionary containing list of function values under 'metrics' key
    """
    print(f"kwargs: {kwargs}")
    function_name = kwargs['function_name']
    global_minimum_value = kwargs['global_minimum_value']
    response = {'metrics': []}
    response['metrics'] = [np.abs(FUNCTION_CONFIGS[function_name]['func'](item['x'], item['y']) - global_minimum_value) for item in parameters]
    return response

#%% Test configuration
function_name = 'rastrigin'  # Change this to test different functions
global_minimum_value = FUNCTION_CONFIGS[function_name]['global_minimum_value']
print(f"Testing {function_name} function")
print(FUNCTION_CONFIGS[function_name]['info'])

pop_size = 50
metric_threshold = 1e-10
max_iterations = 1000
max_iter_without_improvement = 100

adaptive_boundaries = False
init_pop = None
init_pop_out_of_range_param = 'keep'
defaults_in_init_pop = False
use_population_prediction = False
plot_parameter_evolution_period = None
plot_survivor_metric_evolution_period = 2

#%% Callbacks
def callback_after_first_iter(parameters: dict = None,
                             responses: dict = None,
                             iteration: int = None,
                             best_parameters: dict = None,
                             best_metric: float = None,
                             **kwargs):
    print('First iteration completed.')
    print(f'Parameters: {parameters}')
    print(f'Responses: {responses}')
    print(f"kwargs: {kwargs}")

def callback_after_each_iter(parameters: dict = None,
                            responses: dict = None,
                            iteration: int = None,
                            best_parameters: dict = None,
                            best_metric: float = None,
                            better_solution_found: bool = False,
                            **kwargs):
    print(f'Iteration {iteration} completed.')
    print(f'Best metric: {best_metric}.')
    # if better_solution_found:
    #     print(f'New best solution found: {best_parameters}')
    # print(f"kwargs: {kwargs}")

def callback_after_last_iter(iteration: int = None,
                            history: dict = None,
                            best_parameters: dict = None,
                            best_metric: float = None,
                            **kwargs):
    print(f'Optimization completed after {iteration} iterations.')
    print(f'Best solution found:')
    print(f'Parameters: {best_parameters}')
    print(f'Metric value: {best_metric}')
    print(f"kwargs: {kwargs}")



#%% Create parameters DataFrame from configuration
config = FUNCTION_CONFIGS[function_name]
params = {
    'name': ['x', 'y'],
    'min': config['bounds']['min'],
    'max': config['bounds']['max'],
    'default': config['default'],
    'scale': ['lin', 'lin']
}
parameters = pd.DataFrame(params)

#%% Initialize and run the optimization
if __name__ == '__main__':
    diff_evolution = Differential_evolution(
        parameters = parameters,
        eval_func = evaluate_function,
        eval_func_args = {'function_name': function_name, 'global_minimum_value': global_minimum_value},
        callback_after_first_iter = callback_after_first_iter,
        callback_after_each_iter = callback_after_each_iter,
        callback_after_last_iter = callback_after_last_iter,
        pop_size = pop_size,
        metric_threshold = metric_threshold,
        max_iterations = max_iterations,
        max_iter_without_improvement = max_iter_without_improvement,
        init_pop = init_pop,
        init_pop_out_of_range_param = init_pop_out_of_range_param,
        defaults_in_init_pop = defaults_in_init_pop,
        use_population_prediction = use_population_prediction,
        plot_parameter_evolution_period = plot_parameter_evolution_period,
        plot_survivor_metric_evolution_period = plot_survivor_metric_evolution_period,
        adaptive_boundaries = adaptive_boundaries,
        # mutation_factor_1=0.8,
        # mutation_factor_2=0.6,
        # mutation_factor_3=0.3,
        # use_classifier=True,
        # classifier_optimize=False,
        use_predictor = False
    )

    diff_evolution.run_optimization()

    diff_evolution.get_all_trials_exploded()
    diff_evolution.get_all_survivors_exploded()
    diff_evolution.get_all_survivors_normed_exploded()

    # survivors = diff_evolution.get_all_survivors_exploded()
    # create_plot_evolution_2d_video(survivors, FUNCTION_CONFIGS, function_name, diff_evolution.parameter_names,
    #                                 output_path=f'{function_name}.mp4')

    # for i in list(set(survivors['iter'])):
    #     plot_evolution_2d(survivors, FUNCTION_CONFIGS, function_name, diff_evolution.parameter_names, i)
    # plot_evolution_2d(survivors, FUNCTION_CONFIGS, function_name, diff_evolution.parameter_names, 100)
    # plot_evolution_2d_with_metrics(survivors, FUNCTION_CONFIGS, function_name, diff_evolution.parameter_names, 100)
