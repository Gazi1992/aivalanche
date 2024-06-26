from calibration import Calibration
from reference_data.visualization import plot_all_groups
from reference_data.utils import write_reference_data_to_file
import os, numpy as np


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
    
    calibration.optimizer.update_results_dir(os.path.join(calibration.output_path, 'output'))    
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


def callback_after_better_solution_found(iteration: int = None,
                                         responses: dict = None,
                                         best_parameters: dict = None,
                                         best_metric: float = None,
                                         **kwargs):
    print('Better solution found.')
    best_results = responses['results'][np.argmin(responses['metrics'])]
    
    output_path = calibration.output_path
    
    figures_path = os.path.join(output_path, 'figures')
    if not os.path.exists(figures_path):
        os.mkdir(figures_path)
    
    plot_all_groups(groups = best_results, save_dir = figures_path)
    write_reference_data_to_file(data = best_results, file_path = os.path.join(output_path, 'output/best_results.json'), include_simulation = True)

    
templates_diode_nmso_path = os.path.abspath('../../src/templates/diode/')

reference_data_file = os.path.join(templates_diode_nmso_path, 'reference_data.json')
parameters_file = os.path.join(templates_diode_nmso_path, 'parameters.csv')
testbenches_file = os.path.join(templates_diode_nmso_path, 'testbenches.json')
dut_file = os.path.join(templates_diode_nmso_path, 'dut.cir')
dut_name = 'dut'
results_dir = 'results'

optimizer_config = {'type': 'differential_evolution',
                    'callback_after_first_iter': callback_after_first_iter,
                    'callback_after_each_iter': callback_after_each_iter,
                    'callback_after_last_iter': callback_after_last_iter,
                    'callback_after_better_solution_found': callback_after_better_solution_found,
                    'pop_size': 30,
                    'metric_threshold': 1e-10,
                    'max_iterations': 1000,
                    'max_iter_without_improvement': 200,
                    'init_pop': None,
                    'init_pop_out_of_range_param': 'keep',
                    'defaults_in_init_pop': False,
                    'plot_parameter_evolution_period': 1,
                    'plot_survivor_metric_evolution_period': 20,
                    'results_dir': results_dir,
                    'adaptive_boundaries': False}

simulator_config = {'type': 'ngspice'}

cost_function_config = {'type': 'default',
                        'parts': [
                            {
                                'id': 'forward_char_lin',
                                'group_types': ['id_vd'],
                                'metric_type': 'rmse',
                                'weight': 1,
                                'norm': True,
                                'transform': 'lin',
                                'extra_args': {}
                            },
                            {
                                'id': 'forward_char_log',
                                'group_types': ['id_vd'],
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

# calibration.run_no_parameter_simulation(plot = True)

# calibration.run_default_simulation(plot = True, delete_files = True)

# calibration.run_random_simulation(plot = True, delete_files = True)

calibration.calibrate()


# for debug
# for i in range(100):
#     calibration.run_random_simulation(plot = True, delete_files = True)