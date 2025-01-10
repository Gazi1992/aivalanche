import pandas as pd, os, numpy as np, pickle as pcl, uuid, shutil
from parameters.Parameters import Parameters
from optimization.differential_evolution import Differential_evolution
from datetime import datetime
from multiprocessing import Pool
from filter import single_simulation, simulate_multiple_parameters, plot_magnitude, plot_phase, replace_parameters

#%% Helper functions
def create_output_folder(results_path):
    timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
    folder_name = f"optimization_{timestamp}"
    output_path = os.path.join(results_path, folder_name)
    figures_path = os.path.join(output_path, 'figures')
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(figures_path, exist_ok=True)
    return output_path, figures_path

def read_parameters(file):
    params = Parameters(file)
    return params.variable_parameters

def callback_after_each_iter(responses: dict = None,
                            iteration: int = None,
                            better_solution_found: bool = False,
                            best_parameters: np.array = None,
                            parameter_names: list = None,
                            **kwargs):
    global all_results
    global all_parameters
    global all_metrics
    global best_metric
    global best_result
    global figures_path
    global output_path
    
    # all_results.append(responses)
    all_parameters = diff_evolution.get_all_survivors_normed_exploded()
        
    if better_solution_found:
        # Update best metric
        best_metric = np.min(responses['metrics'])
    
        # Update best airfoil
        best_result = responses['data'][np.argmin(responses['metrics'])]
        
        # Save parameters to file        
        diff_evolution.write_best_parameters_to_file(file_path = os.path.join(output_path, 'best_parameters.csv'))
    
        # Save optimization info to file
        diff_evolution.write_optimization_info_to_file(os.path.join(output_path, 'optimization_info.json'))
        
        # Save the results file
        df = pd.DataFrame(columns = ['freq', 'magnitude', 'phase'],
                          data = np.vstack((best_result['freq'], best_result['magnitude_db'], best_result['phase'])).T)
        df = df[df.index % 15 == 0]
        df.to_csv(os.path.join(output_path, 'best_result.csv'), index = False)
        
        # Save the best circuit
        replace_parameters(os.path.join(inputs_path, 'filter_template.cir'), diff_evolution.get_best_parameters(), output_path, filename = 'best_circuit.cir')
        
        plot_magnitude(df, path = os.path.join(figures_path, 'magnitude.png'))
        plot_phase(df, path = os.path.join(figures_path, 'phase.png'))
        
    print(f'Iter {iteration}: {best_metric}')
    
#%% Variables

# Paths
results_path = os.path.abspath('../results')
inputs_path = os.path.abspath('../inputs')
parameters_file = os.path.join(inputs_path, 'parameters.csv')
template_file = os.path.join(inputs_path, 'filter_template.cir')

# DE options
seed = None
pop_size = 100
metric_threshold = -1e10
max_iterations = 1000
max_iter_without_improvement = 15
init_pop = None
init_pop_out_of_range_param = 'keep'
defaults_in_init_pop = False
use_population_prediction = False
plot_parameter_evolution_period = 0
plot_survivor_metric_evolution_period = 0
adaptive_boundaries = False
eval_func_args = {'template_file': template_file, 'results_path': results_path}

# Results
best_metric = None
best_result = None
all_results = []
all_airfoils = []
all_parameters = None
all_metrics = pd.DataFrame()
all_constraints = pd.DataFrame()

#%% Test single simulation
# parameters = read_parameters(parameters_file)
# params_dict = pd.Series(parameters['min'].values, index = parameters['name']).to_dict()
# res = single_simulation(params_dict, **eval_func_args)
# plot_magnitude(res)
# plot_phase(res)

#%% Optimization process
output_path, figures_path = create_output_folder(results_path)
eval_func_args = {'template_file': template_file, 'results_path': output_path}

# Read parameters
parameters = read_parameters(parameters_file)

# Initialize optimizer
diff_evolution = Differential_evolution(parameters = parameters,
                                        eval_func = simulate_multiple_parameters,
                                        eval_func_args = eval_func_args,
                                        callback_after_each_iter = callback_after_each_iter,
                                        pop_size = pop_size,
                                        metric_threshold = metric_threshold,
                                        max_iterations = max_iterations,
                                        max_iter_without_improvement = max_iter_without_improvement,
                                        # mutation_factor_3 = 0,
                                        init_pop = init_pop,
                                        init_pop_out_of_range_param = init_pop_out_of_range_param,
                                        defaults_in_init_pop = defaults_in_init_pop,
                                        use_population_prediction = use_population_prediction,
                                        plot_parameter_evolution_period = plot_parameter_evolution_period,
                                        plot_survivor_metric_evolution_period = plot_survivor_metric_evolution_period,
                                        adaptive_boundaries = adaptive_boundaries,
                                        seed = seed)

# Run optimization
diff_evolution.run_optimization()


