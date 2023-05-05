#%% Imports
import pandas as pd
from differential_evolution.optimizer import differential_evolution
from utils import evaluate_quadratic_3_variables, evaluate_beale_2_variables, \
                  evaluate_quadratic_4_variables, evaluate_sin_sqrt_2_variables, plot_sin_sqrt

#%% Function selector
function = evaluate_quadratic_3_variables
adaptive_boundaries = False
init_pop = None
init_pop_out_of_range_param = 'keep'
defaults_in_init_pop = False
plot_parameter_evolution_period = 2
plot_survivor_metric_evolution_period = None


#%% Declare callbacks
def callbac_after_first_iter(parameters: dict = None,
                             responses: dict = None,
                             iteration: int = None,
                             best_parameters: dict = None,
                             best_metric: float = None,
                             **kwargs):
    print('First iteration completed.')
    print(f'Parameters: {parameters}')
    print(f'Responses: {responses}')
    print(f"kwargs: {kwargs}")
    
def callbac_after_each_iter(parameters: dict = None,
                            responses: dict = None,
                            iteration: int = None,
                            best_parameters: dict = None,
                            best_metric: float = None,
                            **kwargs):
    print(f'Iteration {iteration} completed.')
    print(f'Best metric: {best_metric}.')
    print(f"kwargs: {kwargs}")
    if function == evaluate_sin_sqrt_2_variables:
        plot_sin_sqrt(parameters = parameters)

    
def callbac_after_last_iter(iteration: int = None,
                            best_parameters: dict = None,
                            best_metric: float = None,
                            history: dict = None,
                            **kwargs):
    print(f'Optimization completed after {iteration} iterations.')
    print(f"history: {history}")
    print(f"kwargs: {kwargs}")


#%% Select function
if function == evaluate_quadratic_3_variables:
    
    params = {}
    params['name'] = ['x', 'y', 'z']
    params['min'] = [-100, 1e-15, -10]
    params["max"] = [-10, 100, 200]
    params["default"] = [0, 1e-10, 0]
    params['scale'] = ['lin', 'log', 'lin']
    parameters = pd.DataFrame(params)
    
    init_pop_columns = ['name', 'member_1', 'member_2', 'member_3']
    init_pop_data = []
    init_pop_data.append(['x', 10, 10, 10])
    init_pop_data.append(['y', 10, 10, 1e-15])
    init_pop_data.append(['z', 10, 300, 0])
    init_pop = pd.DataFrame(columns = init_pop_columns, data = init_pop_data)
    init_pop = pd.DataFrame(init_pop)
    
    adaptive_boundaries = True

elif function == evaluate_beale_2_variables:

    params = {}
    params['name'] = ['x', 'y']
    params['min'] = [-4.5, -4.5]
    params["max"] = [4.5, 4.5]
    params["default"] = [0, 0]
    params['scale'] = ['lin', 'log']
    parameters = pd.DataFrame(params)
    
    
elif function == evaluate_quadratic_4_variables:
    
    params = {}
    params['name'] = ['x', 'y', 'z', 'w']
    params['min'] = [-100, 1e-15, -10, -1000]
    params["max"] = [100, 100, 200, -1e-15]
    params["default"] = [0, 1e-10, 0, -100]
    params['scale'] = ['lin', 'log', 'lin', 'lin']
    parameters = pd.DataFrame(params)
    
    init_pop_columns = ['name', 'member_1', 'member_2', 'member_3']
    init_pop_data = []
    init_pop_data.append(['x', 10, 10, 5])
    init_pop_data.append(['y', 10, 10, 5])
    init_pop_data.append(['z', 10, 300, 100])
    init_pop_data.append(['w', 10, 300, 100])
    init_pop = pd.DataFrame(columns = init_pop_columns, data = init_pop_data)
    init_pop = pd.DataFrame(init_pop)
    init_pop = None

elif function == evaluate_sin_sqrt_2_variables:

    params = {}
    params['name'] = ['x', 'y']
    params['min'] = [-5, -5]
    params["max"] = [5, 5]
    params["default"] = [0, 0]
    params['scale'] = ['lin', 'log']
    parameters = pd.DataFrame(params)
    

#%% Initialize and run the optimization
diff_evolution = differential_evolution(parameters = parameters,
                                        eval_func = function,
                                        eval_func_args = {'extra_arg': 'extra_arg_test'},
                                        callback_after_first_iter = callbac_after_first_iter,
                                        callback_after_each_iter = callbac_after_each_iter,
                                        callback_after_last_iter = callbac_after_last_iter,
                                        pop_size = 20,
                                        metric_threshold = -10,
                                        max_iterations = 500,
                                        max_iter_without_improvement = 50,
                                        init_pop = init_pop,
                                        init_pop_out_of_range_param = init_pop_out_of_range_param,
                                        defaults_in_init_pop = defaults_in_init_pop,
                                        plot_parameter_evolution_period = plot_parameter_evolution_period,
                                        plot_survivor_metric_evolution_period = plot_survivor_metric_evolution_period,
                                        adaptive_boundaries = adaptive_boundaries)

diff_evolution.run_optimization()


