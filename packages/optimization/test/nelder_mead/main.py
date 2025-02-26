#%% Imports
import pandas as pd, tempfile, os, numpy as np
from optimization.nelder_mead import Nelder_mead
from optimization.test_functions import Test_Functions
from optimization.visualization import plot_simplex, create_video_from_pngs
from optimization.nelder_mead.visualization import plot_simplex_2d

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

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
    # print(f"kwargs: {kwargs}")
    function_name = kwargs['function_name']
    global_minimum_value = kwargs['global_minimum_value']
    response = {'metrics': [], 'data': []}
    response['metrics'] = [np.abs(FUNCTION_CONFIGS[function_name]['func'](item['x'], item['y']) - global_minimum_value) for item in parameters]
    response['data'] = response['metrics']
    return response

#%% Test configuration
function_name = 'modified_himmelblau'  # Change this to test different functions
global_minimum_value = FUNCTION_CONFIGS[function_name]['global_minimum_value']
print(f"Testing {function_name} function")
print(FUNCTION_CONFIGS[function_name]['info'])

metric_threshold = -1e10
max_iterations = 1000
max_iter_without_improvement = 30

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
    # simplex = np.array([list(item.values()) for item in parameters])
    # plot_simplex_2d(np.array(simplex))
    optimizer.write_optimization_info_to_file('opt_info.json')

def callback_after_last_iter(iteration: int = None,
                            responses: dict = None,
                            best_parameters: dict = None,
                            best_metric: float = None,
                            history: dict = None,
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
    optimizer = Nelder_mead(
        parameters = parameters,
        eval_func = evaluate_function,
        eval_func_args = {'function_name': function_name, 'global_minimum_value': global_minimum_value},
        callback_after_first_iter = callback_after_first_iter,
        callback_after_each_iter = callback_after_each_iter,
        callback_after_last_iter = callback_after_last_iter,
        metric_threshold = metric_threshold,
        max_iterations = max_iterations,
        max_iter_without_improvement = max_iter_without_improvement,
        initial_simplex_edge_length = 0.5,
        use_default_in_initial_simplex=True
    )

    optimizer.run_optimization()
    optimizer.get_all_simplexes_exploded()

    # # Plot a simplex
    # simplexes = optimizer.history['simplexes']
    # groups = simplexes.groupby('iter')
    # with tempfile.TemporaryDirectory() as temp_dir:
    #     for i, data in groups:
    #         simplex = np.array(data['simplex_unscaled'].tolist())
    #         metrics = np.array(data['simplex_metric'])
    #         file_path = os.path.join(temp_dir, f"{i}.png")
    #         plot_simplex(simplex, i, metrics, FUNCTION_CONFIGS, function_name, file_path)
    #     create_video_from_pngs(temp_dir, output_name= f'{function_name}.mp4', output_path='.')
