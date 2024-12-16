import pandas as pd, os, numpy as np, pickle as pcl
from water_system import water_distribution_network, plot_result
from parameters.Parameters import Parameters
from optimization.differential_evolution import Differential_evolution
from datetime import datetime

#%% Helper functions
def create_output_folder(results_path):
    timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
    folder_name = f"optimization_{timestamp}"
    output_path = os.path.join(results_path, folder_name)
    figures_path = os.path.join(output_path, 'figures')
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(figures_path, exist_ok=True)
    return output_path, figures_path

def create_video_from_pngs(figures_path, output_path, output_name='output.mp4', fps=5):
    import cv2
    import os
    import re
    from PIL import Image
    
    # Get and sort PNG files
    png_files = [f for f in os.listdir(figures_path) if f.endswith('.png')]
    png_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))
    
    output_path = os.path.join(output_path, output_name)
    output_format = os.path.splitext(output_name)[1].lower()
    
    if output_format == '.gif':
        # Read images with PIL for GIF
        images = []
        for png in png_files:
            img = Image.open(os.path.join(figures_path, png))
            images.append(img)
        
        # Save as GIF
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            duration=int(1000/fps),  # Duration in milliseconds
            loop=0
        )
    
    elif output_format == '.mp4':
        # Read first image for dimensions
        img = cv2.imread(os.path.join(figures_path, png_files[0]))
        height, width, _ = img.shape
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Add frames
        for png in png_files:
            frame = cv2.imread(os.path.join(figures_path, png))
            video.write(frame)
        
        video.release()
    
    else:
        raise ValueError("Unsupported output format. Use '.mp4' or '.gif'")

def read_parameters(file):
    params = Parameters(file)
    return params.variable_parameters

def simulate_single_parameters(parameters, network = None):
    if network is None:
        network = water_distribution_network()
        
    network.update_network(parameters)
    results = network.run_simulation()    
    network.plot_network()
    plot_result(network, path = 'temp_figure.png')
    network.save_network_elements('temp_netwrok.json')
    
    return results    

def simulate_multiple_parameters(parameters, **kwargs):

    # try:
    #     network = kwargs['network']
    # except:
    #     network = None    

    results = []
    
    for p in parameters:
        
        network = water_distribution_network()  
            
        # Run simulation
        sim_result = network.run_simulation(p)
        
        # Add parameter values to results
        sim_result['parameters'] = p
        results.append(sim_result)
    
    responses = {'data': results, 'metrics': [item['total_metric'] for item in results]}
    
    return responses

def callback_after_each_iter(responses: dict = None,
                            iteration: int = None,
                            better_solution_found: bool = False,
                            **kwargs):
    
    global all_results
    global all_parameters
    global all_costs
    global all_metrics
    global best_metric
    global best_network
    global best_result
    global figures_path
    
    all_results.append(responses)
    all_parameters = diff_evolution.get_all_survivors_normed_exploded()
        
    # Update best metric
    if better_solution_found:
        best_metric = np.min(responses['metrics'])
    
    # Update best network
    if better_solution_found:
        best_result = responses['data'][np.argmin(responses['metrics'])]
        best_network = best_result['network']
    
    best_cost = pd.DataFrame.from_dict([{
        'iter': iteration,
        'all_constraints_met': best_result['all_constraints_met'],
        'energy_cost': best_result['energy_cost'],
        'pipe_cost': best_result['pipe_cost'],
        'total_cost': best_result['total_cost']
        }])
    
    all_costs = pd.concat([all_costs, best_cost])
    
    all_metrics = pd.concat([all_metrics, pd.DataFrame.from_dict([{'iter': iteration, 'metric': best_metric}])])
    
    optimization_data = {'parameters': all_parameters,
                         'costs': all_costs,
                         'metrics': all_metrics}
    plot_result(best_network, optimization_data, path = os.path.join(figures_path, f'{iteration}.png'))
        
    print(f'Iter {iteration}: {best_metric}')

#%% Variables

# Paths
results_path = os.path.abspath('../results')
inputs_path = os.path.abspath('../inputs')
parameters_file = os.path.join(inputs_path, 'parameters.csv')
pcp_path = os.path.join(results_path, 'pcp.html')
batch_results_path = os.path.join(results_path, 'batch_results.csv')

# DE options
pop_size = 50
metric_threshold = -1e10
max_iterations = 200
max_iter_without_improvement = 30
init_pop = None
init_pop_out_of_range_param = 'keep'
defaults_in_init_pop = False
use_population_prediction = False
plot_parameter_evolution_period = 0
plot_survivor_metric_evolution_period = 0
adaptive_boundaries = False
eval_func_args = {}

# Results
all_results = []
best_network = None
best_metric = None
best_result = None
all_parameters = None
all_costs = pd.DataFrame()
all_metrics = pd.DataFrame()

# %% Test single simulation
# parameters = read_parameters(parameters_file)
# params_dict = pd.Series(parameters['default'].values, index = parameters['name']).to_dict()
# res = simulate_single_parameters(params_dict)

#%% Optimization process

output_path, figures_path = create_output_folder(results_path)

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
                                        init_pop = init_pop,
                                        init_pop_out_of_range_param = init_pop_out_of_range_param,
                                        defaults_in_init_pop = defaults_in_init_pop,
                                        use_population_prediction = use_population_prediction,
                                        plot_parameter_evolution_period = plot_parameter_evolution_period,
                                        plot_survivor_metric_evolution_period = plot_survivor_metric_evolution_period,
                                        adaptive_boundaries = adaptive_boundaries)

# Run optimization
diff_evolution.run_optimization()

create_video_from_pngs(figures_path, output_path, output_name='water network optimization.mp4', fps=5)
create_video_from_pngs(figures_path, output_path, output_name='water network optimization.gif', fps=5)