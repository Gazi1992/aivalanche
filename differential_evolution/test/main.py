#%% Imports
import pandas as pd
from differential_evolution.main import differential_evolution
from utils import evaluate_quadratic

#%% Start testing without initial population

def callbac_after_first_iter(iteration, parameters, responses):
    print('First iteration completed.')
    print(f'Parameters: {parameters}')
    print(f'Responses: {responses}')
    
def callbac_after_each_iter(iteration, parameters, responses):
    print(f'Iteration {iteration} completed.')
    print(f'Best metric: {min(responses["metrics"])}.')
    
def callbac_after_last_iter(iteration, parameters, responses):
    print(f'Optimization completed after {iteration} iterations.')

params = {}
params['name'] = ['x', 'y', 'z']
params['min'] = [-1000, 1e-15, -10]
params["max"] = [100, 100, 200]
params["default"] = [0, 100, 100]
params['scale'] = ['lin', 'lin', 'lin']
parameters = pd.DataFrame(params)

init_pop_columns = ['name', 'member_1', 'member_2', 'member_3', 'member_4']
init_pop_data = []
init_pop_data.append(['x', 10, 10, 5, 0])
init_pop_data.append(['y', 10, 10, 5, 0])
init_pop_data.append(['z', 10, 300, 100, 0])
init_pop = pd.DataFrame(columns = init_pop_columns, data = init_pop_data)
init_pop = pd.DataFrame(init_pop)

diff_evolution = differential_evolution(parameters = parameters,
                                        eval_func = evaluate_quadratic,
                                        callback_after_first_iter = callbac_after_first_iter,
                                        callback_after_each_iter = callbac_after_each_iter,
                                        callback_after_last_iter = callbac_after_last_iter,
                                        pop_size = 10,
                                        init_pop = init_pop,
                                        init_pop_out_of_range_param = 'random',
                                        defaults_in_init_pop = True)

diff_evolution.run_optimization()


