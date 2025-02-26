import pandas as pd, os, numpy as np
from utils import create_output_folder, read_parameters, simulate_multiple_parameters, dict_2_json, \
                  plot_parameter_evolution, plot_survivors, plot_results, create_video_from_pngs, \
                  plot_z_field_and_profile, plot_power
from fimmwave_simulator import Fimmwave_simulator
from optimization.differential_evolution import Differential_evolution

#%% Paths
results_path = os.path.abspath('../results')
inputs_path = os.path.abspath('../inputs')
parameters_path = os.path.join(inputs_path, 'parameters.csv')
project_path = os.path.join(inputs_path, 'Taper', 'Taper.prj')

#%% Read parameters
parameters = read_parameters(parameters_path)

#%% Initialize simulator
port = 2121
simulator = Fimmwave_simulator(port = port, project_path = project_path)
simulator.connect()
simulator.open_project()

#%% Results variables
best_metric = None
best_result = None
all_results = []
all_parameters = None
all_metrics = pd.DataFrame()
all_powers = pd.DataFrame()

#%% Create the output folder
output_path, figures_path, figures_video_path = create_output_folder(results_path)

#%% DE config
seed = None
pop_size = 20
metric_threshold = -1e10
max_iterations = 1000
max_iter_without_improvement = 100
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
use_predictor = True
predictor_min_samples = 20
nr_predictor_iterations = 10
eval_func_args = {'results_path': output_path, 'simulator': simulator}

def callback_after_each_iter(responses: dict = None,
                            iteration: int = None,
                            better_solution_found: bool = False,
                            best_parameters: np.array = None,
                            parameter_names: list = None,
                            **kwargs):
    global all_results
    global all_parameters
    global all_metrics
    global all_powers
    global best_metric
    global best_result
    global figures_path
    global output_path

    # all_results.append(responses)
    all_parameters = diff_evolution.get_all_survivors_normed_exploded()
    all_survivors = diff_evolution.get_all_survivors_exploded()

    if better_solution_found:
        # Update best metric
        best_metric = np.min(responses['metrics'])

        # Update best results
        best_result = responses['data'][np.argmin(responses['metrics'])]

        # Save parameters to file
        diff_evolution.write_best_parameters_to_file(file_path = os.path.join(output_path, 'best_parameters.csv'))

        # Save optimization info to file
        diff_evolution.write_optimization_info_to_file(os.path.join(output_path, 'optimization_info.json'))

        # Save the results file
        temp = {k: best_result[k] for k in ['parameters', 'power']}
        dict_2_json(temp, os.path.join(output_path, 'best_result.json'))

    all_powers = pd.concat([all_powers, pd.DataFrame.from_dict([{'iter': iteration, 'power': best_result['power']}])])
    all_powers['iter'] = pd.factorize(all_powers['iter'])[0] + 1
    all_powers.reset_index(inplace = True, drop = True)

    optimization_data = {'parameters': all_parameters,
                         'powers': all_powers}

    # Plots
    plot_results(best_result, optimization_data, path = os.path.join(figures_video_path, f'{iteration}.png'))
    temp_path = os.path.join(figures_path, f'iteration_{iteration}')
    os.makedirs(temp_path, exist_ok=True)
    plot_parameter_evolution(data = all_parameters, path = os.path.join(temp_path, 'param_evolution.png') )
    plot_survivors(all_survivors, path = os.path.join(temp_path, 'survivors.png'))
    plot_z_field_and_profile(best_result['z_field'], best_result['profile'], path = os.path.join(temp_path, 'profile.png'))
    plot_power(all_powers, path = os.path.join(temp_path, 'power.png'))

    print(f'Iter {iteration}: {best_metric}, {best_result["power"]}')

#%% Optimization process

# Initialize optimizer
diff_evolution = Differential_evolution(seed = seed,
                                        parameters = parameters,
                                        eval_func = simulate_multiple_parameters,
                                        eval_func_args = eval_func_args,
                                        callback_after_each_iter = callback_after_each_iter,
                                        pop_size = pop_size,
                                        metric_threshold = metric_threshold,
                                        max_iterations = max_iterations,
                                        max_iter_without_improvement = max_iter_without_improvement,
                                        # mutation_factor_1 = 0.85,
                                        # mutation_factor_2 = 0,
                                        # mutation_factor_3 = 0.2,
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
create_video_from_pngs(figures_video_path, output_path, output_name='taper design.mp4', fps=5)
