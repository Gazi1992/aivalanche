from calibration import Calibration
from reference_data.visualization import plot_all_groups
import numpy as np


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
    
    best_results = responses['results'][np.argmin(responses['metrics'])]
    plot_all_groups(best_results)
    
    
    
def callback_after_each_iter(parameters: dict = None,
                            responses: dict = None,
                            iteration: int = None,
                            best_parameters: dict = None,
                            best_metric: float = None,
                            **kwargs):
    print(f'Iteration {iteration} completed.')
    print(f'Best metric: {best_metric}.')

    
def callback_after_last_iter(iteration: int = None,
                            responses: dict = None,
                            best_parameters: dict = None,
                            best_metric: float = None,
                            history: dict = None,
                            **kwargs):
    print(f'Optimization completed after {iteration} iterations.')
    print(f"history: {history}")
    print(f"kwargs: {kwargs}")
    best_results = responses['results'][np.argmin(responses['metrics'])]
    plot_all_groups(best_results)



reference_data_file = '../../src/templates/bsim4/nmos/reference_data.json'
parameters_file = '../../src/templates/bsim4/nmos/parameters.csv'
testbenches_file = '../../src/templates/bsim4/nmos/testbenches.json'
dut_file = '../../../src/templates/bsim4/nmos/dut.cir'
dut_name = 'dut'
results_dir = 'results'

optimizer_config = {'type': 'differential_evolution',
                    'callback_after_first_iter': callback_after_first_iter,
                    'callback_after_each_iter': callback_after_each_iter,
                    'callback_after_last_iter': callback_after_last_iter,
                    'pop_size': 100,
                    'metric_threshold': 1e-10,
                    'max_iterations': 1000,
                    'max_iter_without_improvement': 50,
                    'init_pop': None,
                    'init_pop_out_of_range_param': 'keep',
                    'defaults_in_init_pop': True,
                    'plot_parameter_evolution_period': 20,
                    'plot_survivor_metric_evolution_period': 20,
                    'adaptive_boundaries': False}

simulator_config = {'type': 'ngspice'}

cost_function_config = {'type': 'default',
                        'parts': [
                            {
                                'id': 'out_char_lin',
                                'group_types': ['ids_vds_vgs'],
                                'metric_type': 'rmse',
                                'weight': 1,
                                'norm': True,
                                'transform': 'lin',
                                'extra_args': {}
                            },
                            {
                                'id': 'out_char_log',
                                'group_types': ['ids_vds_vgs'],
                                'metric_type': 'rmse',
                                'weight': 1,
                                'norm': True,
                                'transform': 'log',
                                'extra_args': {}
                            }
                        ]}



calibration = Calibration(reference_data_file = reference_data_file,
                          parameters_file = parameters_file,
                          testbenches_file = testbenches_file,
                          dut_file = dut_file,
                          dut_name = dut_name,
                          results_dir = results_dir,
                          simulator_config = simulator_config,
                          optimizer_config = optimizer_config,
                          cost_function_config = cost_function_config)

# calibration.run_default_simulation(plot = True)
# calibration.run_random_simulation(plot = True)

calibration.calibrate()