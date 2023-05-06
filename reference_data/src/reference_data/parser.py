'''
Author: Gazmend Alia
Description: parser class is used for processing the .
Inputs:
    eval_func -> 

'''

#%% Imports
import pandas as pd
import numpy as np


#%% differential_evolution class

class parser:
    def __init__(self,
                 eval_func: callable = None,                            # function that is used for the evaluation of the fittness of the parameter sets
                 eval_func_args: dict = {},                             # extra arguments to pass to the evaluation function 
                 callback_after_first_iter: callable = None,            # callback that is called after the first iteration
                 callback_after_each_iter: callable = None,             # callback that is called after each iteration
                 callback_after_last_iter: callable = None,             # callback that is called after the last iteration
                 parameters: pd.DataFrame = None,                       # the parameters to be optimized
                 pop_size: int = 100,                                   # number of parameter sets that are evaluated in each iteration
                 opt_min_or_max: str = 'min',                           # either search for the 'min' or 'max'
                 max_iterations: int = 1000,                            # when that many iterations are done, optimization stops
                 metric_threshold: float = 0,                           # when this threshold is reached, optimization stops  
                 max_iter_without_improvement: int = 50,                # when no improvement is seem in that many iterations, optimization stops
                 mutation_factor: float = 0.8,                          # the scaling factor during mutation
                 recombination_factor: float = 0.9,                     # the factor used during trials generation
                 init_pop: pd.DataFrame = None,                         # initial population to be used in the first iteration of the optimization
                 init_pop_out_of_range_param: str = 'keep',             # what to do with the parameters of the initial population that are out of range; either 'keep' as is or replace with 'random' value
                 defaults_in_init_pop: bool = False,                    # when true, then use the default values of the parameters in the initial population
                 adaptive_boundaries: bool = False,                     # when true, expand boundaries of a parameter if the optimizer is concentrated on the edges of the parameter range
                 adaptive_boundaries_edge_threshold: float = 0.05,      # closer than this distance from the edge is considered as on the edge
                 adaptive_boundaries_pop_quantitle: float = 0.7,        # when this quantile of the population is on the edge, the boundary is extended
                 adaptive_boundaries_extention: float = 0.1,            # how much is the min or max extended when the a parameter is considered on the edge
                 adaptive_boundaries_check_period: int = 10,            # check for adaptive boundaries periodically each that much iterations
                 plot_trial_metric_evolution_period: int = None,        # plot trial metric evolution when iteration is a multiple of this factor
                 plot_survivor_metric_evolution_period: int = None,     # plot trial metric evolution when iteration is a multiple of this factor
                 plot_parameter_evolution_period: int = None,           # plot parameter evolution when iteration is a multiple of this factor
                 ):
        
        
        self.eval_func = eval_func
        self.eval_func_args = eval_func_args
        self.callback_after_first_iter = callback_after_first_iter
        self.callback_after_each_iter = callback_after_each_iter
        self.callback_after_last_iter = callback_after_last_iter
        
        self.parameters = parameters
        self.pop_size = pop_size
        self.opt_min_or_max = opt_min_or_max
        self.mutation_factor = mutation_factor
        self.recombination_factor = recombination_factor        
        
        self.max_iterations = max_iterations
        self.metric_threshold = metric_threshold
        self.max_iter_without_improvement = max_iter_without_improvement
        
        self.init_pop = init_pop
        self.init_pop_out_of_range_param = init_pop_out_of_range_param
        self.defaults_in_init_pop = defaults_in_init_pop
        
        self.adaptive_boundaries = adaptive_boundaries
        self.adaptive_boundaries_edge_threshold = adaptive_boundaries_edge_threshold
        self.adaptive_boundaries_pop_quantitle = adaptive_boundaries_pop_quantitle
        self.adaptive_boundaries_extention = adaptive_boundaries_extention
        self.adaptive_boundaries_check_period = adaptive_boundaries_check_period
        
        self.plot_trial_metric_evolution_period = plot_trial_metric_evolution_period if plot_trial_metric_evolution_period is not None and plot_trial_metric_evolution_period > 0 else None
        self.plot_survivor_metric_evolution_period = plot_survivor_metric_evolution_period if plot_survivor_metric_evolution_period is not None and plot_survivor_metric_evolution_period > 0 else None
        self.plot_parameter_evolution_period = plot_parameter_evolution_period if plot_parameter_evolution_period is not None  and plot_parameter_evolution_period > 0 else None
        
        self.iter = 0
        self.is_stop_criteria_reached = False
        self.stop_reason = ""
        
        self.parameters = preprocess_parameters(self.parameters)
        self.nr_parameters = self.parameters.shape[0]
        self.parameter_names = self.parameters['name'].tolist()
        self.parameters_transform_list = self.parameters['transform'].tolist()
                
        self.history = {'parameters': self.parameters,
                        'trials': pd.DataFrame(columns = ['iter', 'trial_normed', 'trial', 'trial_unscaled', 'trial_metric']),
                        'bests': pd.DataFrame(columns = ['iter', 'best_normed', 'best', 'best_unscaled', 'best_metric']),
                        'boundaries': pd.DataFrame(columns = ['iter', 'boundaries_min', 'boundaries_max'])} 
        


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
