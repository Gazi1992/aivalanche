import pandas as pd, os, numpy as np, pickle as pcl, uuid, shutil
from xfoil import XFoilAnalyzer, XFoilBatch, XFoilSettings, plot_results, kill_xfoil_processes, \
                  plot_parameter_evolution, plot_survivors, plot_ld_evolution
from parameters.Parameters import Parameters
from optimization.differential_evolution import Differential_evolution
from datetime import datetime
from multiprocessing import Pool

#%% Helper functions
def create_output_folder(results_path):
    timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
    folder_name = f"optimization_{timestamp}"
    output_path = os.path.join(results_path, folder_name)
    figures_path = os.path.join(output_path, 'figures')
    figures_video_path = os.path.join(figures_path, 'video')
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(figures_path, exist_ok=True)
    os.makedirs(figures_video_path, exist_ok=True)
    return output_path, figures_path, figures_video_path

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

def simulate_single_parameters(parameters, **kwargs):
    
    xfoil_analyzer = XFoilAnalyzer()
    xfoil_analyzer.update_parameter_boundaries(param_boundaries)
    alpha = kwargs['alpha']
    Re = kwargs['Re']
    Mach = kwargs['Mach']
    results = xfoil_analyzer.analyze_airfoil(parameters, alpha, Re, Mach)
    # xfoil_analyzer.plot_airfoil()
    # xfoil_analyzer.plot_geometry()
    plot_results(xfoil_analyzer, path='temp_airfoil.png')
    
    return results    

def simulate_single(params):
    alpha = params['alpha']
    Re = params['Re']
    Mach = params['Mach']
    p = params['parameters']
    
    working_dir = os.path.abspath(f'{str(uuid.uuid4())[-8:]}')
    xfoil_settings = XFoilSettings(working_dir=working_dir)
    xfoil_analyzer = XFoilAnalyzer(settings = xfoil_settings)
    xfoil_analyzer.update_parameter_boundaries(param_boundaries)
    sim_result = xfoil_analyzer.analyze_airfoil(p, alpha, Re, Mach)
    sim_result['parameters'] = p
    if os.path.exists(working_dir):
        shutil.rmtree(working_dir, ignore_errors=True)
    return sim_result

def simulate_multiple_parameters(parameters, **kwargs):
    
    # Prepare input for each process
    inputs = [{'parameters': p, 'alpha': kwargs['alpha'], 
                'Re': kwargs['Re'], 'Mach': kwargs['Mach']} 
              for p in parameters]
    
    # Use number of CPU cores for parallelization
    num_cores = os.cpu_count()
    
    # Run parallel simulations
    with Pool(num_cores) as pool:
        results = pool.map(simulate_single, inputs)
    
    responses = {
        'data': results,
        'metrics': [item['metrics']['total_metric'] for item in results]
    }
    
    return responses
    
    # alpha = kwargs['alpha']
    # Re = kwargs['Re']
    # Mach = kwargs['Mach']
    
    # results = []
    
    # for p in parameters:
        
    #     xfoil_analyzer = XFoilAnalyzer()
            
    #     # Run simulation
    #     sim_result = xfoil_analyzer.analyze_airfoil(p, alpha, Re, Mach)
        
    #     # Add parameter values to results
    #     sim_result['parameters'] = p
    #     results.append(sim_result)
    
    # responses = {'data': results, 'metrics': [item['metrics']['total_metric'] for item in results]}
    
    # return responses

def callback_after_each_iter(responses: dict = None,
                            iteration: int = None,
                            better_solution_found: bool = False,
                            best_parameters: np.array = None,
                            parameter_names: list = None,
                            **kwargs):
    global all_results
    global all_parameters
    global all_survivors
    global all_airfoils
    global all_metrics
    global all_constraints
    global all_ld
    global best_metric
    global best_airfoil
    global best_result
    global figures_path
    global output_path
    
    # all_results.append(responses)
    all_parameters = diff_evolution.get_all_survivors_normed_exploded()
    all_survivors = diff_evolution.get_all_survivors_exploded()
        
    if better_solution_found:
        # Update best metric
        best_metric = np.min(responses['metrics'])
    
        # Update best airfoil
        best_result = responses['data'][np.argmin(responses['metrics'])]
        best_airfoil = best_result['airfoil']
        
        # Save parameters to file        
        diff_evolution.write_best_parameters_to_file(file_path = os.path.join(output_path, 'best_parameters.csv'))
    
        # Save optimization info to file
        diff_evolution.write_optimization_info_to_file(os.path.join(output_path, 'optimization_info.json'))
        
    
    all_airfoils.append(best_airfoil.airfoil)
    
    all_ld = pd.concat([all_ld, pd.DataFrame.from_dict([{'iter': iteration,
                                                         'lift': best_result['cl'],
                                                         'drag': best_result['cd'],
                                                         'ld_ratio': best_result['ld_ratio'],
                                                         'constraints_met': best_result['constraints_met']}])])
    
    
    all_metrics = pd.concat([all_metrics, pd.DataFrame.from_dict([{'iter': iteration,
                                                                   'metric': best_metric,
                                                                   'constraints_met': best_result['constraints_met']}])])
    
    all_constraints = pd.concat((all_constraints, pd.DataFrame.from_dict([{'iter': iteration,
                                                                        'constraints_met': best_result['constraints_met'],
                                                                        **best_result['geometry']}])))
    
    optimization_data = {'parameters': all_parameters,
                         'metrics': all_metrics,
                         'all_airfoils': all_airfoils,
                         'all_constraints': all_constraints,
                         'ld': all_ld}
    
    # Plots
    if best_metric < 1000:
        plot_results(best_airfoil, optimization_data, path = os.path.join(figures_video_path, f'{iteration}.png'))
    
    temp_path = os.path.join(figures_path, f'iteration_{iteration}')
    os.makedirs(temp_path, exist_ok=True)
    plot_parameter_evolution(data = all_parameters, path = os.path.join(temp_path, 'param_evolution.png') )  
    plot_survivors(all_survivors, path = os.path.join(temp_path, 'survivors.png'))
    best_airfoil.plot_airfoil(path = os.path.join(temp_path, 'airfoil.png'))
    best_airfoil.plot_geometry(path = os.path.join(temp_path, 'constraints.png'))
    plot_ld_evolution(data = all_ld, path = os.path.join(temp_path, 'lift_and_drag.png'))
    
    print(f'Iter {iteration}: {best_metric}')
    
    kill_xfoil_processes()

#%% Variables

# Paths
results_path = os.path.abspath('../results')
inputs_path = os.path.abspath('../inputs')
parameters_file = os.path.join(inputs_path, 'parameters.csv')

# DE options
seed = None
pop_size = 150
metric_threshold = -1e10
max_iterations = 1000
max_iter_without_improvement = 20
init_pop = None
init_pop_out_of_range_param = 'keep'
defaults_in_init_pop = False
use_population_prediction = False
plot_parameter_evolution_period = 0
plot_survivor_metric_evolution_period = 0
adaptive_boundaries = False
eval_func_args = {}

# Flow parameters
Re = 1e5
Mach = 0.0
alpha = 5
eval_func_args = {'Re': Re, 'Mach': Mach, 'alpha': alpha}

# Results
best_airfoil = None
best_metric = None
best_result = None
all_results = []
all_airfoils = []
all_parameters = None
all_metrics = pd.DataFrame()
all_constraints = pd.DataFrame()
all_ld = pd.DataFrame()
all_survivors = pd.DataFrame()

# %% Test single simulation
# parameters = read_parameters(parameters_file)
# params_dict = pd.Series(parameters['default'].values, index = parameters['name']).to_dict()
# res = simulate_single_parameters(params_dict, **eval_func_args)

#%% Optimization process
output_path, figures_path, figures_video_path = create_output_folder(results_path)

# Read parameters
parameters = read_parameters(parameters_file)
param_boundaries = parameters[['name', 'min', 'max']]

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

create_video_from_pngs(figures_video_path, output_path, output_name='airfoil optimization.mp4', fps=5)
# create_video_from_pngs(figures_path, output_path, output_name='water network optimization.gif', fps=5)