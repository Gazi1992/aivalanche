import pandas as pd, os, numpy as np
from utils import create_output_folder, read_parameters, simulate_multiple_widths, dict_2_json, \
                  plot_parameter_evolution, plot_survivors, plot_results_nm, create_video_from_pngs, \
                  plot_z_field_and_profile, plot_power, plot_parameters_spider, dict_2_csv, normalize_dict_with_df
from fimmwave_simulator import Fimmwave_simulator
from optimization.differential_evolution import Differential_evolution

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
pop_size = 10
metric_threshold = -1e10
max_iterations = 1000
max_iter_without_improvement = 10
init_pop = None
init_pop_out_of_range_param = 'keep'
defaults_in_init_pop = False
plot_parameter_evolution_period = 0
plot_survivor_metric_evolution_period = 0
adaptive_boundaries = False
use_population_prediction = False
use_classifier = False
classifier_optimize = False
classifier_accuracy_threshold = 0.7
use_predictor = False
predictor_min_samples = 20
nr_predictor_iterations = 10
eval_func_args = {'results_path': output_path,
                  'simulator': simulator,
                  'parameters_lengths_path': parameters_lengths_path,
                  'seed': seed}

def callback_after_each_iter(responses: dict = None,
                            iteration: int = None,
                            better_solution_found: bool = False,
                            best_parameters: np.array = None,
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
        diff_evolution.write_optimization_info_to_file(os.path.join(output_path, 'optimization_info.json'))

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
diff_evolution = Differential_evolution(seed = seed,
                                        parameters = parameters_widths,
                                        eval_func = simulate_multiple_widths,
                                        eval_func_args = eval_func_args,
                                        callback_after_each_iter = callback_after_each_iter,
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
                                        use_predictor = use_predictor,
                                        predictor_min_samples = predictor_min_samples,
                                        nr_predictor_iterations = nr_predictor_iterations,
                                        use_classifier = use_classifier,
                                        classifier_optimize = classifier_optimize,
                                        classifier_accuracy_threshold = classifier_accuracy_threshold)

# Run optimization
diff_evolution.run_optimization()

#%% Disconnect the simulator
simulator.disconnect()

#%% Create video
# figures_video_path = r"C:\Users\gazme\OneDrive\Documents\aivalanche\code\aivalanche\use_cases\photon_design\taper\results\optimization_2025_02_04_21-58-32\figures\video"
# output_path = r"C:\Users\gazme\OneDrive\Documents\aivalanche\code\aivalanche\use_cases\photon_design\taper\results\optimization_2025_02_04_21-58-32"
create_video_from_pngs(figures_video_path, output_path, output_name='splitter design - genetic.mp4', fps=5)
