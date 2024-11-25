#%% Imports
import pandas as pd, os, numpy as np, pickle as pcl
from optimization.differential_evolution import Differential_evolution
from parameters.Parameters import Parameters
from xfoil import XFoilAnalyzer, XFoilBatch, XFoilSettings
from nurbs import Nurbs
from visualizations import create_airfoil_optimization_video, plot_airfoil, plot_airfoil_glowing, plot_polar, plot_pressure_distribution, plot_boundary_layer, create_optimization_summary, create_optimization_video

#%% Helper functions
def read_parameters(file):
    return Parameters(file)

def simulate_batch(parameters, **kwargs):    
    # Run batch simulation
    results_df = batch_handler.run_batch(param_list = parameters,
                                         alpha = kwargs['alpha'],
                                         Re = kwargs['Re'],
                                         Mach = kwargs['Mach'],
                                         show_progress = True)
    return results_df

def simulate_multiple_parameters(parameters, **kwargs):
    sim_results = simulate_batch(parameters, **kwargs)  # Simulate
    results_df = calculate_metric(sim_results)          # Calculate metric
    results = {'data': results_df, 'metrics': np.array(sim_results['total_metric'])}  # Final results as required by optimizer
    return results

def thickness_metric(data):
    """
    Check thickness constraints for a realistic airfoil
    """
        
    # Maximum thickness should be between 8-18% for typical subsonic airfoils
    if data['max_thickness'] < 0.08:
        metric_1 = 100 + (0.08 - data['max_thickness'])
    elif data['max_thickness'] > 0.18:
        metric_1 = 100 + (data['max_thickness'] - 0.18)
    else:
        metric_1 = 0
    
    # Maximum thickness location should be between 20-40% chord
    if data['max_thickness_location'] < 0.20:
        metric_2 = 100 + (0.2 - data['max_thickness_location'])
    elif  data['max_thickness_location'] > 0.40:
        metric_2 = 100 + (data['max_thickness_location'] - 0.4)
    else:
        metric_2 = 0
        
    # # Minimum thickness at 95% chord (trailing edge region) should be > 0.2%
    # x, thickness = data.thickness_distribution
    # te_index = np.argmin(np.abs(x - 0.95))
    # if thickness[te_index] < 0.002:
    #     return False
        
    return metric_1 + metric_2

def le_radius_metric(data):
    """
    Check leading edge radius constraints
    """
    # Leading edge radius typically 1-3% chord for subsonic airfoils
    # Too small: poor stall characteristics
    # Too large: excessive drag
    if data['leading_edge_radius'] < 0.01:
        metric = 100 + (0.01 - data['leading_edge_radius'])
    elif data['leading_edge_radius'] > 0.03:
        metric = 100 + (data['leading_edge_radius'] - 0.03)
    else:
        metric = 0
        
    return metric

def smoothness_metric(data):
    """
    Check surface smoothness constraints
    """
    # Maximum curvature should be limited to prevent separation
    # High curvature regions can cause flow separation
    if data['max_curvature'] > 50.0:  # This threshold needs tuning based on your specific case
        metric = 100 + (data['max_curvature'] - 50)
    else:
        metric = 0
        
    # # Check for curvature discontinuities
    # upper_curv, lower_curv = airfoil.surface_smoothness
    
    # # Calculate rate of change of curvature
    # d_upper_curv = np.abs(np.diff(upper_curv))
    # d_lower_curv = np.abs(np.diff(lower_curv))
    
    # # Limit sudden changes in curvature
    # if np.max(d_upper_curv) > 5.0 or np.max(d_lower_curv) > 5.0:
    #     return False
        
    return metric

def te_angle_metric(data):
    """
    Check trailing edge angle constraints
    """
    # Trailing edge angle (alpha_b) constraints
    # Too small: structural/manufacturing issues
    # Too large: excessive drag
    if data['trailing_edge_angle'] < 5:
        metric = 100 + (5 - data['trailing_edge_angle'])
    elif data['trailing_edge_angle'] > 15:
        metric = 100 + (data['trailing_edge_angle'] - 15)
    else:
        metric = 0

    return metric

def geometry_metric(data):
    """
    Sum of all the geometry metrics
    """
    metric = thickness_metric(data) + le_radius_metric(data) + smoothness_metric(data) + te_angle_metric(data)
    return metric

def ld_metric(data):
    """
    Calculate the lift over drag metric. Since this is to be maximized,
    the metric is 1/ld.
    """
    metric = 1 / data['ld']
    return metric

def convergence_metric(data):
    """
    Calculate the simulation converged. If not, set a huge penalty.
    """
    if pd.isna(data['ld']) or data['ld'] < 0:
        metric = 1e3
    else:
        metric = 0
    return metric

def total_metric(data):
    """
    Calculate the total metric.
    """
    if data['convergence_metric'] > 0:
        metric = data['convergence_metric']
    elif data['geometry_metric'] > 0:
        metric = data['geometry_metric']
    else:
        metric = data['ld_metric']
    return metric   
    
def calculate_metric(sim_results):
    results_df = sim_results
    
    # Calculate convergence metric
    results_df['convergence_metric'] = results_df.apply(lambda row: convergence_metric(row), axis = 1)
    
    # Calculate geometry metrics
    results_df['thickness_metric'] = results_df.apply(lambda row: thickness_metric(row), axis = 1)
    results_df['le_radius_metric'] = results_df.apply(lambda row: le_radius_metric(row), axis = 1)
    results_df['smoothness_metric'] = results_df.apply(lambda row: smoothness_metric(row), axis = 1)
    results_df['te_angle_metric'] = results_df.apply(lambda row: te_angle_metric(row), axis = 1)
    results_df['geometry_metric'] = results_df.apply(lambda row: geometry_metric(row), axis = 1)
    
    # Calculate ld metric
    results_df['ld_metric'] = results_df.apply(lambda row: ld_metric(row), axis = 1)
    
    # Calculate total metric
    results_df['total_metric'] = results_df.apply(lambda row: total_metric(row), axis = 1)

    return results_df

def callback_after_each_iter(parameters: dict = None,
                            responses: dict = None,
                            iteration: int = None,
                            best_parameters: dict = None,
                            best_metric: float = None,
                            better_solution_found: bool = False,
                            **kwargs):
    # Plot best airfoil
    param_names = list(parameters[0].keys())
    best_params_dict = {}
    for key, val in zip(param_names, list(best_parameters)):        
        best_params_dict[key] = val
    airfoil = Nurbs(best_params_dict)  
    plot_airfoil(airfoil._spline(), show_panels = True)
    
    all_results.append(responses)
    
    print(f'Iteration {iteration} completed.')
    print(f'Best metric: {best_metric}.')
    print(f'Best parameters: {best_params_dict}.')

#%% Variables

# Paths
results_path = os.path.abspath('../results')
inputs_path = os.path.abspath('../inputs')
parameters_file = os.path.join(inputs_path, 'parameters.csv')
pcp_path = os.path.join(results_path, 'pcp.html')
batch_results_path = os.path.join(results_path, 'batch_results.csv')

# Flow parameters
Re = 1e5
Mach = 0.0
alpha = 5

# DE options
pop_size = 50
metric_threshold = -1e10
max_iterations = 500
max_iter_without_improvement = 50
init_pop = None
init_pop_out_of_range_param = 'keep'
defaults_in_init_pop = False
use_population_prediction = False
plot_parameter_evolution_period = 5
plot_survivor_metric_evolution_period = 5
adaptive_boundaries = False
eval_func_args = {'Re': Re, 'Mach': Mach, 'alpha': alpha}

# Results
all_results = []

#%% Optimization process

# # Initialize analyzer and batch handler
# settings = XFoilSettings(working_dir = results_path)
# analyzer = XFoilAnalyzer(settings)
# batch_handler = XFoilBatch(analyzer)

# # Read parameters
# parameters = read_parameters(parameters_file)

# # Initialize optimizer
# diff_evolution = Differential_evolution(parameters = parameters.all_parameters,
#                                         eval_func = simulate_multiple_parameters,
#                                         eval_func_args = eval_func_args,
#                                         callback_after_each_iter = callback_after_each_iter,
#                                         pop_size = pop_size,
#                                         metric_threshold = metric_threshold,
#                                         max_iterations = max_iterations,
#                                         max_iter_without_improvement = max_iter_without_improvement,
#                                         init_pop = init_pop,
#                                         init_pop_out_of_range_param = init_pop_out_of_range_param,
#                                         defaults_in_init_pop = defaults_in_init_pop,
#                                         use_population_prediction = use_population_prediction,
#                                         plot_parameter_evolution_period = plot_parameter_evolution_period,
#                                         plot_survivor_metric_evolution_period = plot_survivor_metric_evolution_period,
#                                         adaptive_boundaries = adaptive_boundaries)

# # Run optimization
# diff_evolution.run_optimization()

# # Save the results into pcl files for later processing
# with open(os.path.join(results_path, 'diff_evolution.pcl'), 'wb') as f:
#     pcl.dump(diff_evolution, f)

# with open(os.path.join(results_path, 'all_results.pcl'), 'wb') as f:
#     pcl.dump(all_results, f)

#%% Visualize optimization

# Read the diff_evolution object
with open(os.path.join(results_path, 'diff_evolution.pcl'), 'rb') as f:
    diff_evolution = pcl.load(f)
    
# Read the diff_evolution object
with open(os.path.join(results_path, 'sim_results.pcl'), 'rb') as f:
    sim_results = pcl.load(f)

#############################################################
# Get all survivors that make sense
survivors = diff_evolution.get_all_survivors()
survivors = survivors[survivors['survivor_metric'] < 1e3]
# survivors = survivors[['iter', 'survivor_unscaled', 'survivor_metric']]

parameter_names = diff_evolution.parameter_names

# # Get the simulations to rerun
# df_exploded = survivors['survivor_unscaled'].apply(pd.Series)
# df_exploded = df_exploded.astype(float)
# df_exploded.columns = parameter_names
# df_exploded.reset_index(drop = True, inplace = True)
# df_exploded = df_exploded.drop_duplicates()

# params = df_exploded.to_dict('records')
# sim_results = simulate_batch(params, **eval_func_args)
# sim_results = calculate_metric(sim_results)

# Prepare the final dataframe
df_exploded = survivors['survivor_unscaled'].apply(pd.Series)
df_exploded = df_exploded.astype(float)
df_exploded.columns = parameter_names
# df_exploded.reset_index(drop = True, inplace = True)
df_exploded['iter'] = survivors['iter']

df_exploded_normed = survivors['survivor_normed'].apply(pd.Series)
df_exploded_normed = df_exploded_normed.astype(float)
df_exploded_normed.columns = parameter_names
# df_exploded_normed.reset_index(drop = True, inplace = True)
df_exploded_normed['iter'] = survivors['iter']
#############################################################

#############################################################
# # Get all trials that make sense
# trials = diff_evolution.history['trials']
# trials = trials[trials['trial_metric'] < 1e3]
# # survivors = survivors[['iter', 'survivor_unscaled', 'survivor_metric']]

# parameter_names = diff_evolution.parameter_names

# # # Get the simulations to rerun
# # df_exploded = survivors['survivor_unscaled'].apply(pd.Series)
# # df_exploded = df_exploded.astype(float)
# # df_exploded.columns = parameter_names
# # df_exploded.reset_index(drop = True, inplace = True)
# # df_exploded = df_exploded.drop_duplicates()

# # params = df_exploded.to_dict('records')
# # sim_results = simulate_batch(params, **eval_func_args)
# # sim_results = calculate_metric(sim_results)

# # Prepare the final dataframe
# df_exploded = trials['trial_unscaled'].apply(pd.Series)
# df_exploded = df_exploded.astype(float)
# df_exploded.columns = parameter_names
# # df_exploded.reset_index(drop = True, inplace = True)
# df_exploded['iter'] = trials['iter']

# df_exploded_normed = trials['trial_normed'].apply(pd.Series)
# df_exploded_normed = df_exploded_normed.astype(float)
# df_exploded_normed.columns = parameter_names
# # df_exploded_normed.reset_index(drop = True, inplace = True)
# df_exploded_normed['iter'] = trials['iter']
#############################################################

# Perform left merge
merged_df = df_exploded.merge(sim_results, 
                    on=parameter_names,  # Columns to merge on
                    how='left',        # Keep all rows from left DataFrame (df1)
                    indicator=True)

merged_df = merged_df.drop('_merge', axis=1)
merged_df['iter'] = merged_df['iter'].astype(int)

iter_start = 0
iter_end = 2
create_optimization_summary(merged_df[merged_df['iter'] >= iter_start], df_exploded_normed[df_exploded_normed['iter'] >= iter_start], iter_end, parameter_names)

# iter_min = merged_df['iter'].min()
# iter_max = merged_df['iter'].max()
# output_path = os.path.join(results_path, 'optimization_progress.mp4')
# create_optimization_video(merged_df, df_exploded_normed, iter_min, iter_max, parameter_names, output_path,
#                           n_previous=10, min_alpha=0.1, max_alpha=0.5, fps=10)

# Plot gloing airfoil
# plot_airfoil_glowing(merged_df, 10)

data = merged_df[merged_df['iter'] < 500]
# plot_airfoil_glowing(merged_df, 183)
create_airfoil_optimization_video(data, parameter_names, output_path='opt.mp4', fps=7)