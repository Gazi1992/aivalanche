from calibration.Calibration import Calibration
from reference_data.Reference_data import Reference_data
import os, numpy as np, pandas as pd
from utils import create_output_folder, plot_survivors, plot_ref_data, plot_parameter_evolution, plot_results, plot_fit, plot_loss, create_video_from_pngs

#%% Paths
results_path = os.path.abspath('../results')
inputs_path = os.path.abspath('../inputs')
reference_data_file = os.path.join(inputs_path, 'reference_data.json')
parameters_file = os.path.join(inputs_path, 'parameters.csv')
testbenches_file = os.path.join(inputs_path, 'testbenches.json')
dut_file = os.path.join(inputs_path, 'dut.cir')

#%% Create the output folder
output_path, figures_path, figures_video_path = create_output_folder(results_path)

#%% Plot reference data
data = Reference_data(reference_data_file)
ref_data_dir = os.path.join(output_path, 'ref_data')
os.makedirs(ref_data_dir, exist_ok=True)
for id, group in data.data.groupby('group_id'):
    plot_ref_data(group, path = os.path.join(ref_data_dir, f'{id}.png'))

#%% Some variables
dut_name = 'dut'
results_dir = output_path
best_metric = None
best_result = None
all_metrics = pd.DataFrame()

#%% Callback
def callback_after_each_iter(parameters: dict = None,
                             responses: dict = None,
                             iteration: int = None,
                             history: dict = None,
                             best_parameters: dict = None,
                             # best_metric: float = None,
                             better_solution_found: bool = None,
                             **kwargs):

    global all_metrics
    global best_result
    global best_metric

    optimizer = calibration.optimizer

    all_parameters = optimizer.get_all_survivors_normed_exploded()
    all_survivors = optimizer.get_all_survivors_exploded()

    if better_solution_found:
        # Update best metric
        best_metric = np.min(responses['metrics'])

        # Update best results
        best_result = responses['results'][np.argmin(responses['metrics'])]

        # Save parameters to file
        optimizer.write_best_parameters_to_file(file_path = os.path.join(output_path, 'best_parameters.csv'))

        # Save optimization info to file
        optimizer.write_optimization_info_to_file(os.path.join(output_path, 'optimization_info.json'))

    all_metrics = pd.concat([all_metrics, pd.DataFrame.from_dict([{'iter': iteration, 'metric': best_metric}])])

    optimization_data = {'parameters': all_parameters,
                         'metrics': all_metrics}

    # Plots
    plot_results(best_result, optimization_data, path = os.path.join(figures_video_path, f'{iteration}.png'))
    temp_path = os.path.join(figures_path, f'iteration_{iteration}')
    os.makedirs(temp_path, exist_ok=True)
    plot_parameter_evolution(data = all_parameters, path = os.path.join(temp_path, 'param_evolution.png') )
    plot_survivors(all_survivors, path = os.path.join(temp_path, 'survivors.png'))
    plot_loss(all_metrics, path = os.path.join(temp_path, 'mismatch.png'))

    for id, group in best_result.groupby('group_id'):
        plot_fit(group, path = os.path.join(temp_path, f'fit_{id}.png'))

    print(f'Iteration {iteration} completed.')
    print(f'Best metric: {best_metric}.')

#%% More variables
optimizer_config = {'type': 'differential_evolution',
                    'callback_after_each_iter': callback_after_each_iter,
                    'pop_size': 50,
                    'metric_threshold': 1e-5,
                    'max_iterations': 2000,
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
                                'id': 'out_trans_char_lin',
                                'group_types': ['ids_vds_vgs', 'ids_vgs_vbs'],
                                'metric_type': 'rmse',
                                'weight': 10,
                                'norm': True,
                                'transform': 'lin',
                                'extra_args': {}
                            },
                            {
                                'id': 'out_trans_char_log',
                                'group_types': ['ids_vds_vgs', 'ids_vgs_vbs'],
                                'metric_type': 'rmse',
                                'weight': 0,
                                'norm': True,
                                'transform': 'log',
                                'extra_args': {}
                            },
                            {
                                'id': 'capacitor_char_lin',
                                'group_types': ['cgd_vgs_vbs', 'cgs_vgs_vbs', 'cgb_vgs_vbs', 'cgg_vgs_vbs', 'crss_vds_vgs', 'ciss_vds_vgs'],
                                'metric_type': 'rmse',
                                'weight': 1,
                                'norm': True,
                                'transform': 'lin',
                                'extra_args': {}
                            },
                            {
                                'id': 'capacitor_char_log',
                                'group_types': ['cgd_vgs_vbs', 'cgs_vgs_vbs', 'cgb_vgs_vbs', 'cgg_vgs_vbs', 'crss_vds_vgs', 'ciss_vds_vgs'],
                                'metric_type': 'rmse',
                                'weight': 0,
                                'norm': True,
                                'transform': 'log',
                                'extra_args': {}
                            }
                        ]}

#%% Calibration
calibration = Calibration(reference_data = reference_data_file,
                          parameters = parameters_file,
                          testbenches = testbenches_file,
                          dut_file = dut_file,
                          dut_name = dut_name,
                          results_dir = results_dir,
                          simulator_config = simulator_config,
                          optimizer_config = optimizer_config,
                          cost_function_config = cost_function_config,
                          optimization_on_another_thread = False)

calibration.calibrate()

#%% Create video
# figures_video_path = r"C:\Users\gazme\OneDrive\Documents\aivalanche\code\aivalanche\use_cases\photon_design\taper\results\optimization_2025_02_04_21-58-32\figures\video"
# output_path = r"C:\Users\gazme\OneDrive\Documents\aivalanche\code\aivalanche\use_cases\photon_design\taper\results\optimization_2025_02_04_21-58-32"
create_video_from_pngs(figures_video_path, output_path, output_name='transistor calibration.mp4', fps=8)
