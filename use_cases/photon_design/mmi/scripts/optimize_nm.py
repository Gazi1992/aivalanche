import pandas as pd, os, numpy as np
from utils import create_output_folder, read_parameters, simulate_multiple_widths, dict_2_json, \
                  plot_parameter_evolution, plot_survivors, plot_results_nm, create_video_from_pngs, \
                  plot_z_field_and_profile, plot_power, plot_parameters_spider, dict_2_csv, normalize_dict_with_df
from fimmwave_simulator import Fimmwave_simulator
from optimization.nelder_mead import Nelder_mead

#%% Paths
results_path = os.path.abspath('../results')
inputs_path = os.path.abspath('../inputs')
parameters_widths_path = os.path.join(inputs_path, 'parameters_widths.csv')
parameters_lengths_path = os.path.join(inputs_path, 'parameters_lengths.csv')
project_path = os.path.join(inputs_path, 'FIMMPROP MMI', 'MMICoupler.prj')

#%% Read parameters
parameters_widths = read_parameters(parameters_widths_path)
parameters_lengths = read_parameters(parameters_lengths_path)
all_parameters = pd.concat((parameters_widths, parameters_lengths))

#%% Initialize simulator
port = 2121
simulator = Fimmwave_simulator(port = port, project_path = project_path)
simulator.connect()
simulator.open_project()

#%% Results variables
best_metric = None
best_result = None
best_parameters_all = None
best_parameters_normed_all = None
all_powers = pd.DataFrame()

#%% Create the output folder
output_path, figures_path, figures_video_path = create_output_folder(results_path)

#%% DE config
seed = None
metric_threshold = -1e10
max_iterations = 1000
max_iter_without_improvement = 30
ignore_boundaries = False
use_default_in_initial_simplex = False
eval_func_args = {'results_path': output_path,
                  'simulator': simulator,
                  'parameters_lengths_path': parameters_lengths_path,
                  'seed': seed}

def callback_after_each_iter(responses: dict = None,
                            iteration: int = None,
                            better_solution_found: bool = False,
                            best_parameters: dict = None,
                            parameter_names: list = None,
                            **kwargs):
    global all_powers
    global best_metric
    global best_result
    global best_parameters_all
    global best_parameters_normed_all
    global figures_path
    global output_path

    if better_solution_found:
        # Update best metric
        best_metric = np.min(responses['metrics'])

        # Update best results
        best_result = responses['data'][np.argmin(responses['metrics'])]
        best_parameters_all = best_result['parameters']
        best_parameters_normed_all = normalize_dict_with_df(best_parameters_all, all_parameters)

        # Save parameters to file
        dict_2_csv(best_parameters_all, os.path.join(output_path, 'best_parameters.csv'))

        # Save optimization info to file
        optimizer.write_optimization_info_to_file(os.path.join(output_path, 'optimization_info.json'))

        # Save the results file
        temp = {k: best_result[k] for k in ['parameters', 'power']}
        dict_2_json(temp, os.path.join(output_path, 'best_result.json'))

    all_powers = pd.concat([all_powers, pd.DataFrame.from_dict([{'iter': iteration, 'power': best_result['power']}])])

    optimization_data = {'best_parameters': best_parameters_normed_all,
                         'powers': all_powers}

    # Plots
    plot_results_nm(best_result, optimization_data, path = os.path.join(figures_video_path, f'{iteration}.png'))
    temp_path = os.path.join(figures_path, f'iteration_{iteration}')
    os.makedirs(temp_path, exist_ok=True)
    plot_z_field_and_profile(best_result['z_field'], best_result['profile'], path = os.path.join(temp_path, 'profile.png'))
    plot_power(all_powers, path = os.path.join(temp_path, 'power.png'))
    plot_parameters_spider(best_parameters_normed_all, path = os.path.join(temp_path, 'parameters.png'))

    print(f'Iter {iteration}: {best_metric}, {best_result["power"]}')

#%% Optimization process

# Initialize optimizer
optimizer = Nelder_mead(seed = seed,
                        parameters = parameters_widths,
                        eval_func = simulate_multiple_widths,
                        eval_func_args = eval_func_args,
                        callback_after_each_iter = callback_after_each_iter,
                        metric_threshold = metric_threshold,
                        max_iterations = max_iterations,
                        max_iter_without_improvement = max_iter_without_improvement,
                        use_default_in_initial_simplex = use_default_in_initial_simplex,
                        ignore_boundaries = ignore_boundaries)

# Run optimization
optimizer.run_optimization()

#%% Disconnect the simulator
simulator.disconnect()

#%% Create video
# figures_video_path = r"C:\Users\gazme\OneDrive\Documents\aivalanche\code\aivalanche\use_cases\photon_design\taper\results\optimization_2025_01_26_08-22-15\figures\video"
# output_path = r"C:\Users\gazme\OneDrive\Documents\aivalanche\code\aivalanche\use_cases\photon_design\taper\results\optimization_2025_01_26_08-22-15"
create_video_from_pngs(figures_video_path, output_path, output_name='splitter design - simplex.mp4', fps=5)
