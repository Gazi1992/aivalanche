'''
Author: Gazmend Alia
Description: differential_evolution class is efficient for optimizations in high dimensional spaces.
Inputs:
    eval_func -> 
    eval_func_args ->
    callback_after_first_iter ->
    callback_after_each_iter ->
    callback_after_last_iter ->
    parameters ->
    pop_size ->
    opt_min_or_max ->
    max_iterations ->
    metric_threshold ->
    max_iter_without_improvement ->
    mutation_factor_1 ->
    mutation_factor_2 ->
    mutation_factor_3 ->
    recombination_factor ->
    init_pop ->
    init_pop_out_of_range_param ->
    defaults_in_init_pop ->
    adaptive_boundaries ->
    plot_trial_metric_evolution_period ->
    plot_survivor_metric_evolution_period ->
    plot_parameter_evolution_period ->
'''

#%% Imports
import os, pandas as pd, numpy as np, time, json
from pyDOE import lhs
from scipy.stats.qmc import Sobol, Halton
from optimization.differential_evolution.utils import preprocess_parameters, unnorm_member, norm_member, scale_parameter, \
                                                      get_gaussian_process_fit, get_exponential_or_linear_fit, smooth_data, exponential_func, linear_func
from optimization.differential_evolution.visualization import plot_df, plot_parameter_fit, plot_quantile_fits
from optimization.visualization import plot_metric_evolution, plot_parameter_evolution, plot_histogram


#%% differential_evolution class

class Differential_evolution:
    def __init__(self,
                 eval_func: callable = None,                            # function that is used for the evaluation of the fittness of the parameter sets
                 eval_func_args: dict = None,                           # extra arguments to pass to the evaluation function 
                 callback_after_first_iter: callable = None,            # callback that is called after the first iteration
                 callback_after_each_iter: callable = None,             # callback that is called after each iteration
                 callback_after_last_iter: callable = None,             # callback that is called after the last iteration
                 callback_after_better_solution_found: callable = None, # callback that is called after finding a better solution
                 parameters: pd.DataFrame = None,                       # the parameters to be optimized
                 pop_size: int = 100,                                   # number of parameter sets that are evaluated in each iteration
                 opt_min_or_max: str = 'min',                           # either search for the 'min' or 'max'
                 max_iterations: int = 1000,                            # when that many iterations are done, optimization stops
                 metric_threshold: float = 0,                           # when this threshold is reached, optimization stops  
                 max_iter_without_improvement: int = 50,                # when no improvement is seem in that many iterations, optimization stops
                 mutation_factor_1: float = 0.8,                        # the scaling factor for difference of the two random members
                 mutation_factor_2: float = 0.6,                        # the scaling factor for difference of best and random member
                 mutation_factor_3: float = 0,                          # the scaling factor for difference of current and random member
                 recombination_factor: float = 0.95,                     # the factor used during trials generation
                 init_pop: pd.DataFrame = None,                         # initial population to be used in the first iteration of the optimization
                 init_pop_out_of_range_param: str = 'keep',             # what to do with the parameters of the initial population that are out of range; either 'keep' as is or replace with 'random' value
                 defaults_in_init_pop: bool = False,                    # when true, then use the default values of the parameters in the initial population
                 adaptive_boundaries: bool = False,                     # when true, expand boundaries of a parameter if the optimizer is concentrated on the edges of the parameter range
                 adaptive_boundaries_edge_threshold: float = 0.05,      # closer than this distance from the edge is considered as on the edge
                 adaptive_boundaries_pop_quantitle: float = 0.7,        # when this quantile of the population is on the edge, the boundary is extended
                 adaptive_boundaries_extention: float = 0.1,            # how much is the min or max extended when the a parameter is considered on the edge
                 adaptive_boundaries_check_period: int = 10,            # check for adaptive boundaries periodically each that much iterations
                 use_population_prediction: bool = False,
                 population_prediction_back_window: int = 10,
                 population_prediction_front_window: int = 10,
                 population_prediction_period: int = 10,
                 population_prediction_std_drop_threshold: float = 0.5,
                 population_prediction_upper_quantile: float = 0.75,
                 population_prediction_lower_quantile: float = 0.25,
                 plot_trial_metric_evolution_period: int = None,        # plot trial metric evolution when iteration is a multiple of this number
                 plot_survivor_metric_evolution_period: int = None,     # plot trial metric evolution when iteration is a multiple of this number
                 plot_parameter_evolution_period: int = None,           # plot parameter evolution when iteration is a multiple of this number
                 write_history_to_file_period: int = None,              # write the de history to file when iteration is a multiple of this number
                 results_dir: str = None,                               # directory where to save the results
                 seed: int = None,                                      # seed for reproducibility
                 ):
        
        
        if seed is None:
            seed = np.random.randint(0, 1000)
        self.seed = seed
        np.random.seed(self.seed)
        self.rng = np.random.RandomState(self.seed)
        
        self.eval_func = eval_func
        self.eval_func_args = {} if eval_func_args is None else eval_func_args
        self.callback_after_first_iter = callback_after_first_iter
        self.callback_after_each_iter = callback_after_each_iter
        self.callback_after_last_iter = callback_after_last_iter
        self.callback_after_better_solution_found = callback_after_better_solution_found
        
        self.parameters = parameters
        self.pop_size = int(pop_size)
        self.opt_min_or_max = opt_min_or_max
        self.mutation_factor_1 = float(mutation_factor_1)
        self.mutation_factor_2 = float(mutation_factor_2)
        self.mutation_factor_3 = float(mutation_factor_3)
        self.recombination_factor = float(recombination_factor        )
        
        self.max_iterations = int(max_iterations)
        self.metric_threshold = float(metric_threshold)
        self.max_iter_without_improvement = int(max_iter_without_improvement)
        
        self.init_pop = None
        if isinstance(init_pop, str) and os.path.exists(init_pop):
            self.init_pop = init_pop
        elif isinstance(init_pop, pd.DataFrame):
            self.init_pop = init_pop
        
        if isinstance(self.init_pop, str):
            if self.init_pop.split('.')[-1] == 'csv':
                self.init_pop = pd.read_csv(filepath_or_buffer = self.init_pop)
            else:
                self.init_pop = None
        self.init_pop_out_of_range_param = str(init_pop_out_of_range_param)
        self.defaults_in_init_pop = bool(defaults_in_init_pop)
        
        self.adaptive_boundaries = bool(adaptive_boundaries)
        self.adaptive_boundaries_edge_threshold = adaptive_boundaries_edge_threshold
        self.adaptive_boundaries_pop_quantitle = adaptive_boundaries_pop_quantitle
        self.adaptive_boundaries_extention = adaptive_boundaries_extention
        self.adaptive_boundaries_check_period = adaptive_boundaries_check_period
        
        self.use_population_prediction = use_population_prediction
        self.population_prediction_back_window = population_prediction_back_window
        self.population_prediction_front_window = population_prediction_front_window
        self.population_prediction_period = population_prediction_period
        self.population_prediction_std_drop_threshold = population_prediction_std_drop_threshold
        self.population_prediction_upper_quantile = population_prediction_upper_quantile
        self.population_prediction_lower_quantile = population_prediction_lower_quantile
        
        self.plot_trial_metric_evolution_period = int(plot_trial_metric_evolution_period) if plot_trial_metric_evolution_period is not None and plot_trial_metric_evolution_period > 0 else None
        self.plot_survivor_metric_evolution_period = int(plot_survivor_metric_evolution_period) if plot_survivor_metric_evolution_period is not None and plot_survivor_metric_evolution_period > 0 else None
        self.plot_parameter_evolution_period = int(plot_parameter_evolution_period) if plot_parameter_evolution_period is not None  and plot_parameter_evolution_period > 0 else None
        self.write_history_to_file_period = int(write_history_to_file_period) if results_dir is not None and write_history_to_file_period is not None and write_history_to_file_period > 0 else None
        
        self.results_dir = results_dir
        
        self.iter = 0
        self.abort_flag = False
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
        
        self.best_metric = None
        self.best_unscaled = None
        self.best = None
        self.best_normed = None
        self.optimization_info = {}

    # Run the optimization loop.
    def run_optimization(self):
        
        # Prepare for the first iteration
        self.prepare_first_iter()
        
        # stay in the loop as long as the stop criteria is not reached
        while not self.is_stop_criteria_reached:
            parameters = self.get_trials_unscaled()                                 # get the trials_unscaled
            extra_arguments = {'iteration': self.iter,                              # extra arguments to give to the evaluation function
                               'best_metric': self.best_metric,
                               'best_parameters': self.best_unscaled,
                               **self.eval_func_args}
            responses = self.eval_func(parameters = parameters, **extra_arguments)  # run the evaluation function
            
            self.save_metrics(responses['metrics'])                                 # save the metrics
            
            self.determine_survivors()                                              # determine the survivors
            self.determine_best()                                                   # determine the best parameters and best metric
            self.update_history_trials()                                            # append the trials to the history trials
            self.update_optimization_info()
            
            # Run the callback
            if self.iter == 1 and self.callback_after_first_iter is not None:
                    self.callback_after_first_iter(parameters = parameters,
                                                   responses = responses,
                                                   iteration = self.iter,
                                                   best_parameters = self.best_unscaled,
                                                   best_metric = self.best_metric,
                                                   parameter_names = self.parameter_names,
                                                   **self.eval_func_args)
            
            if self.callback_after_each_iter is not None:
                self.callback_after_each_iter(parameters = parameters,
                                              responses = responses,
                                              iteration = self.iter,
                                              best_parameters = self.best_unscaled,
                                              best_metric = self.best_metric,
                                              better_solution_found = self.better_solution_found,
                                              trials = self.history['trials'],
                                              parameter_names = self.parameter_names,
                                              **self.eval_func_args)
            
            if self.better_solution_found:
                if self.results_dir is not None:
                    if not os.path.exists(self.results_dir):
                        os.makedirs(self.results_dir)
                    self.write_best_parameters_to_file(file_path = os.path.join(self.results_dir, 'best_parameters.csv'))
                    self.write_population_to_file(file_path = os.path.join(self.results_dir, 'last_population.csv'))
                    
                if self.callback_after_better_solution_found is not None:
                    self.callback_after_better_solution_found(iteration = self.iter,
                                                              responses = responses,
                                                              best_parameters = self.best_unscaled,
                                                              best_metric = self.best_metric,
                                                              parameter_names = self.parameter_names,
                                                              **self.eval_func_args)
                    
            # plot trial metric evolution
            if self.plot_trial_metric_evolution_period is not None and self.iter % self.plot_trial_metric_evolution_period == 0:
                plot_metric_evolution(iterations = self.history['trials']['iter'],
                                      metrics = self.history['trials']['trial_metric'],
                                      y_scale = 'lin')
                
            # plot parameter evolution
            if self.plot_parameter_evolution_period is not None and self.iter % self.plot_parameter_evolution_period == 0:
                plot_parameter_evolution(parameters = self.parameter_names,
                                         data = np.array(self.history['trials']['trial_normed'].tolist()),
                                         iteration = self.iter,
                                         save_dir = self.results_dir)
            
            # plot survivor metric evolution
            if self.plot_survivor_metric_evolution_period is not None and self.iter % self.plot_survivor_metric_evolution_period == 0:    
                all_survivors = self.get_all_survivors()
                plot_metric_evolution(iterations = all_survivors['iter'],
                                      metrics = all_survivors['survivor_metric'],
                                      save_dir = self.results_dir)
            
            # write the history to file
            if self.write_history_to_file_period is not None and self.iter % self.write_history_to_file_period == 0:    
                self.write_history_to_file(self.results_dir)
            
            # Generate new trials
            self.prepare_next_iter()
        
        # once the stop criteria is reached
        self.show_final_result()
        if self.callback_after_last_iter is not None:
            self.callback_after_last_iter(iteration = self.iter,
                                          responses = responses,
                                          best_parameters = self.best_unscaled,
                                          best_metric = self.best_metric,
                                          trials = self.history['trials'],
                                          stop_reason = self.stop_reason,
                                          parameter_names = self.parameter_names,
                                          **self.eval_func_args)
            
        # Show final plots
        if self.plot_survivor_metric_evolution_period is not None:
            all_survivors = self.get_all_survivors()
            plot_metric_evolution(iterations = all_survivors['iter'],
                                  metrics = all_survivors['survivor_metric'],
                                  save_dir = self.results_dir)
                        
    # Update optimization info
    def update_optimization_info(self):
        if self.iter == 1:
            self.optimization_info['input'] = {'seed': self.seed,
                                               'pop_size': self.pop_size,
                                               'max_iterations': self.max_iterations,
                                               'max_iter_without_improvement': self.max_iter_without_improvement,
                                               'metric_threshold': self.metric_threshold,
                                               'adaptive_boundaries': self.adaptive_boundaries,
                                               'results_dir': self.results_dir,
                                               'parameters': self.parameters[['name', 'min', 'default', 'max', 'scale']].to_dict('records')}
            
        self.optimization_info['output'] = {'iter': self.iter,
                                            'best_metric': self.best_metric,
                                            'best_parameters': self.get_best_parameters(),
                                            'nr_evaluations': self.iter * self.pop_size,
                                            'stop_reason': self.stop_reason}
    
    def write_optimization_info_to_file(self, file_path = None):
        if file_path is not None:
            # Convert the main structure to a formatted string
            json_str = json.dumps(self.optimization_info, indent=4)
            
            # Find the parameters section and replace it with single-line formatting
            param_list = self.optimization_info['input']['parameters']
            single_line_params = ',\n      '.join(json.dumps(param) for param in param_list)
            param_section = '"parameters": [\n      ' + single_line_params + '\n    ]'
            
            # Replace the original parameters section
            start = json_str.find('"parameters":')
            end = json_str.find(']', start) + 1
            json_str = json_str[:start] + param_section + json_str[end:]
            with open(file_path, 'w') as f:
                f.write(json_str)
    
    # Print the final result
    def show_final_result(self):
        print("\n\n--------------------------- Optimization stopped ---------------------------\n\n")
        print(f"Reason: {self.stop_reason}\n\n")
        print(f"Number of iteration: {self.iter}\n\n")
        print(f"Best response: {self.best_metric}\n\n")
        print(f"Best parameters: {self.best_unscaled}\n\n")
        print("--------------------------------------------------------------------------------\n\n")
    
    # Set is_stop_criteria_reached
    def set_is_stop_criteria_reached(self):
        if self.abort_flag:
            self.is_stop_criteria_reached = True
            self.stop_reason = "optimization aborted"
        elif self.opt_min_or_max == 'min' and self.best_metric < self.metric_threshold:
            self.is_stop_criteria_reached = True
            self.stop_reason = "metric threshold reached"
        elif self.opt_min_or_max == 'max' and self.best_metric > self.metric_threshold:
            self.is_stop_criteria_reached = True
            self.stop_reason = "metric threshold reached"
        elif self.iter_no_improvement > self.max_iter_without_improvement:
            self.is_stop_criteria_reached = True
            self.stop_reason = "maximum number of iterations without improvement reached"
        elif self.iter > self.max_iterations:
            self.iter -= 1
            self.is_stop_criteria_reached = True
            self.stop_reason = "maximum number of iterations reached"
        else:
            self.is_stop_criteria_reached = False
        
    # Abort optimization
    def abort_optimization(self):
        self.abort_flag = True

    # Save metrics
    def save_metrics(self, metrics):
        self.trials_metric = np.array(metrics)

    # Prepare first iteration
    def prepare_first_iter(self):
        if not self.is_stop_criteria_reached:
            self.iter_no_improvement = 0
            self.iter += 1
            self.set_boundaries()     
            self.targets = np.full((self.pop_size, self.nr_parameters), None)
            self.targets_unscaled = np.full((self.pop_size, self.nr_parameters), None)
            self.targets_normed = np.full((self.pop_size, self.nr_parameters), None)
            self.targets_metric = np.full((self.pop_size), None)
            self.generate_donors()
            self.generate_trials()

    # Prepare next iteration
    def prepare_next_iter(self):        
        self.iter += 1
        self.targets_normed = self.survivors_normed
        self.targets = self.survivors
        self.targets_unscaled = self.survivors_unscaled
        self.targets_metric = self.survivors_metric
        self.set_is_stop_criteria_reached()
        if self.adaptive_boundaries:
            self.set_boundaries()
            
        # apply population prediction
        population_prediction_applied = False
        if self.use_population_prediction and self.iter > 0 and self.iter % self.population_prediction_period == 0:
            population_prediction_applied = self.apply_population_prediction()
            
        if not population_prediction_applied:
            self.generate_donors()
            self.generate_trials()

    # Calculate the boundaries for each parameter
    def set_boundaries(self):
        if(self.iter == 1):
            self.boundaries = np.array([self.parameters['min_scaled'], self.parameters['max_scaled']])
            self.boundaries_min = np.min(self.boundaries, axis = 0)
            self.boundaries_max = np.max(self.boundaries, axis = 0)
            self.boundaries_range = self.boundaries_max - self.boundaries_min
            self.update_history_boundaries()
        else:
            if self.adaptive_boundaries and self.iter % self.adaptive_boundaries_check_period == 0:
                # get the quantile values for each parameter according to adaptive_boundaries_pop_quantitle
                quantile_values_min = np.quantile(self.survivors_normed, self.adaptive_boundaries_pop_quantitle, axis = 0)
                quantile_values_max = np.quantile(self.survivors_normed, 1 - self.adaptive_boundaries_pop_quantitle, axis = 0)
                
                # determin all the parameters, where the quantile value is on the edge
                min_mask = quantile_values_min < self.adaptive_boundaries_edge_threshold
                max_mask = quantile_values_max > 1 - self.adaptive_boundaries_edge_threshold
                
                # if there is some parameter on the edge, then update the respective boundaries
                if True in min_mask or True in max_mask:
                    self.boundaries_min[min_mask] = self.boundaries_min[min_mask] - self.adaptive_boundaries_extention * self.boundaries_range[min_mask]
                    self.boundaries_max[max_mask] = self.boundaries_max[max_mask] + self.adaptive_boundaries_extention * self.boundaries_range[max_mask]
                    self.boundaries_range = self.boundaries_max - self.boundaries_min
                    self.boundaries = np.vstack((self.boundaries_min, self.boundaries_max))
                    
                    # renorm the targets based on the new boundaries
                    self.targets_normed = np.apply_along_axis(func1d = norm_member,
                                                              axis = 1,
                                                              arr = self.targets,
                                                              minimum = self.boundaries_min,
                                                              maximum = self.boundaries_max)    
                    
                    # save the new boundaries in the history
                    self.update_history_boundaries()

    # Get unscaled array
    def get_unscaled_arr(self, arr):
        temp = np.copy(arr)
        ind = 1 if len(temp.shape) == 2 else 0
        for i, val in np.ndenumerate(temp):
            index = i[ind]
            if self.parameters_transform_list[index] == 'log':
                temp[i] = np.longdouble(10.0**val)
            elif self.parameters_transform_list[index] == 'neglog':
                temp[i] = -np.longdouble(10.0**val)
            else:
                temp[i] = val
        return temp

    # Get the trials as a list of dictionaries
    def get_trials_unscaled(self):
        new_trials = []
        for values in self.trials_unscaled:
            tmp = {key: val for key, val in zip(self.parameter_names, values)}
            new_trials.append(tmp)
        return new_trials

    # Get all survivors
    def get_all_survivors(self):
        data = []
        for row_idx, row in self.history['trials'].iterrows():
            if row_idx < self.pop_size:
                data.append(row.tolist())
            else:
                if self.opt_min_or_max == 'max':
                    if row['trial_metric'] > data[row_idx - self.pop_size][-1]:
                        data.append(row.tolist())
                    else:
                        temp = data[row_idx - self.pop_size].copy()
                        temp[0] = row['iter']
                        data.append(temp)
                else:
                    if row['trial_metric'] < data[row_idx - self.pop_size][-1]:
                        data.append(row.tolist())
                    else:
                        temp = data[row_idx - self.pop_size].copy()
                        temp[0] = row['iter']
                        data.append(temp)
        
        all_survivors = pd.DataFrame(columns = ['iter', 'survivor_normed', 'survivor', 'survivor_unscaled', 'survivor_metric'],
                                     data = data)

        return all_survivors
    
    # Get trials exploded
    def get_all_trials_exploded(self):
        data = self.history['trials'][['iter', 'trial_unscaled', 'trial_metric']]
        result_df = pd.concat([data.drop('trial_unscaled', axis=1), 
                               pd.DataFrame(data['trial_unscaled'].tolist(), columns = self.parameter_names)], axis=1)
        result_df = result_df.rename(columns={'trial_metric': 'metric'})
        result_df['iter'] = result_df['iter'].astype(int)
        result_df = result_df[['iter'] + self.parameter_names + ['metric']]
        return result_df
    
    # Get trials normed exploded
    def get_all_trials_normed_exploded(self):
        data = self.history['trials'][['iter', 'trial_normed', 'trial_metric']]
        result_df = pd.concat([data.drop('trial_normed', axis=1), 
                               pd.DataFrame(data['trial_normed'].tolist(), columns = self.parameter_names)], axis=1)
        result_df = result_df.rename(columns={'trial_metric': 'metric'})
        result_df['iter'] = result_df['iter'].astype(int)
        result_df = result_df[['iter'] + self.parameter_names + ['metric']]
        return result_df
        
    # Get survivors exploded
    def get_all_survivors_exploded(self):
        data = self.get_all_survivors()
        data = data[['iter', 'survivor_unscaled', 'survivor_metric']]
        result_df = pd.concat([data.drop('survivor_unscaled', axis=1), 
                               pd.DataFrame(data['survivor_unscaled'].tolist(), columns = self.parameter_names)], axis=1)
        result_df = result_df.rename(columns={'survivor_metric': 'metric'})
        result_df['iter'] = result_df['iter'].astype(int)
        result_df = result_df[['iter'] + self.parameter_names + ['metric']]
        return result_df
    
    # Get survivors normed exploded
    def get_all_survivors_normed_exploded(self):
        data = self.get_all_survivors()
        data = data[['iter', 'survivor_normed', 'survivor_metric']]
        result_df = pd.concat([data.drop('survivor_normed', axis=1), 
                               pd.DataFrame(data['survivor_normed'].tolist(), columns = self.parameter_names)], axis=1)
        result_df = result_df.rename(columns={'survivor_metric': 'metric'})
        result_df['iter'] = result_df['iter'].astype(int)
        result_df = result_df[['iter'] + self.parameter_names + ['metric']]
        return result_df
    
    # Get best parameters as a dictionary
    def get_best_parameters(self):
        return {key: val for key, val in zip(self.parameter_names, self.best_unscaled)}

    # Generate a mutation
    def generate_mutations(self, dice: np.array = None):
        if dice is None:        
            # throw the dice to get 3 random intigers between 0 and pop_size-1
            dice = [self.rng.choice([j for j in range(self.pop_size) if j != i], size = (1, 3), replace = False) for i in range(self.pop_size)]
            dice = np.array(dice).reshape(-1,3)
            # dice = np.random.randint(self.pop_size, size = (self.pop_size, 3))            
        
        # get random members
        temp = self.targets_normed[dice].reshape(-1,3,self.nr_parameters)
        rand_mem_1 = temp[:,0,:]
        rand_mem_2 = temp[:,1,:]
        rand_mem_3 = temp[:,2,:]

        # calculate the donor
        donors_normed = (rand_mem_1
                       + self.mutation_factor_1 * (rand_mem_2 - rand_mem_3)
                       + self.mutation_factor_2 * (self.best_normed - rand_mem_1)
                       + self.mutation_factor_3 * (self.best_normed - self.targets_normed))

        # if donor goes beyond [0,1], then assign it a random value
        violation_mask = (donors_normed > 1) | (donors_normed < 0)
        donors_normed[violation_mask] = np.random.rand(np.sum(violation_mask))
                
        return donors_normed

    # Generate a recombination between the target and the donor
    def generate_recombinations(self, dice: np.array = None):
        # get a random number for each parameter
        if dice is None:
            dice = self.rng.rand(self.pop_size, self.nr_parameters)

        # combine donor and target, getting the value from the donor whereever dice is less than the recombination_factor and from the target otheerwise
        trials_normed = np.where(dice < self.recombination_factor, self.donors_normed, self.targets_normed)

        return trials_normed

    # Generate a donor for each target
    def generate_donors(self):
        # In the first iteration generate donor at random.
        if(self.iter == 1):
            # self.donors_normed = lhs(self.nr_parameters, samples = self.pop_size, criterion = 'correlation') # Use latin-hyper-cube to generate the random samples
            sampler = Halton(d=self.nr_parameters, seed = self.seed)
            self.donors_normed = sampler.random(self.pop_size) # Use Halton to generate the random samples
            self.donors = np.apply_along_axis(func1d = unnorm_member,
                                              axis = 1,
                                              arr = self.donors_normed,
                                              minimum = self.boundaries_min,
                                              maximum = self.boundaries_max) # unnorm all the donors
            
            # If initial population is given, then incorporate it in the first donors.
            if self.init_pop is not None:
                
                # drop duplicate factors based on name
                self.init_pop = self.init_pop.drop_duplicates(subset = 'name', keep = "first")
                
                # remove any parameters not part of the self.parameters
                self.init_pop = self.init_pop[self.init_pop['name'].isin(self.parameter_names)]
                
                # for parameters out of range, generate random values or take whatever is the default value
                if self.init_pop_out_of_range_param == 'random':
                    for row_idx, row in self.init_pop.iterrows():
                        parameter = row['name']
                        minimum = self.parameters[self.parameters['name'] == parameter]['min'].values[0]
                        maximum = self.parameters[self.parameters['name'] == parameter]['max'].values[0]
                        row.drop(labels = ['name'], inplace = True)
                        for col_idx, (col_name, value) in enumerate(row.items()):
                            if value > maximum or value < minimum:
                                new_val = np.random.uniform(minimum, maximum) # random value between min and max
                                self.init_pop.iloc[row_idx, col_idx + 1] = new_val
                
                # initial population members
                init_pop_member_names = self.init_pop.columns.tolist()
                init_pop_member_names.remove('name')
                init_pop_nr_members = len(init_pop_member_names)
                
                # initial population parameters
                init_pop_parameter_names = self.init_pop['name'].tolist()
                init_pop_nr_parameters = len(init_pop_parameter_names)
                
                init_pop_parameter_indices = [self.parameter_names.index(p) for p in init_pop_parameter_names]
                init_pop_transforms = [self.parameters_transform_list[i] for i in init_pop_parameter_indices]
                
                # set the transform for each parameter of the initial population
                self.init_pop['transform'] = init_pop_transforms
                
                for member in init_pop_member_names:
                    self.init_pop[f"{member}_scaled"] = self.init_pop.apply(lambda row: scale_parameter(row, member), axis = 1)
                
                # keep only the scaled members
                col_to_exclude = init_pop_member_names
                col_to_exclude.extend(['name', 'transform'])
                init_pop_values = self.init_pop.drop(columns = col_to_exclude).to_numpy().transpose()

                # determine indices to replace in the donors array
                for i in range(init_pop_nr_members):
                    for j in range(init_pop_nr_parameters):
                        self.donors[i, init_pop_parameter_indices[j]] = init_pop_values[i,j]
                
                # norm all the donors
                self.donors_normed = np.apply_along_axis(func1d = norm_member,
                                                         axis = 1,
                                                         arr = self.donors,
                                                         minimum = self.boundaries_min,
                                                         maximum = self.boundaries_max)
 
            # if the default values are used in the initial population.
            if self.defaults_in_init_pop:
                
                # use default values in initial population only if the given init_pop has less members than poo_size
                if self.init_pop is None or self.pop_size > init_pop_nr_members:
                    self.donors[-1] = np.array(self.parameters['value_scaled']).reshape(1,-1)

        else:
            self.donors_normed = self.generate_mutations()                      # Generate mutations for each target
            self.donors = np.apply_along_axis(func1d = unnorm_member,
                                              axis = 1,
                                              arr = self.donors_normed,
                                              minimum = self.boundaries_min,
                                              maximum = self.boundaries_max)    # Unnorm all the donors
            
        self.donors_unscaled = self.get_unscaled_arr(self.donors)               # Unscale the donors, i.e. transform the log and neglog
     
    # Generate a trial for each target-donor pair
    def generate_trials(self):       
        if self.iter == 1: # In the first iteration, trial is equal to donor, because there is no target.
            self.trials = self.donors
            self.trials_normed = self.donors_normed
        else:
            self.trials_normed = self.generate_recombinations()
            self.trials = np.apply_along_axis(func1d = unnorm_member,
                                              axis = 1,
                                              arr = self.trials_normed,
                                              minimum = self.boundaries_min,
                                              maximum = self.boundaries_max) # unnorm all the trials
        self.trials_unscaled = self.get_unscaled_arr(self.trials)

    # Determine the survivor for each target-trial pair
    def determine_survivors(self):
        if(self.iter == 1): # In the first iteration, there is no target, so survivor = trial
            self.survivors_normed = self.trials_normed
            self.survivors = self.trials
            self.survivors_unscaled = self.trials_unscaled
            self.survivors_metric = self.trials_metric
        else:
           mask = (self.trials_metric > self.targets_metric if self.opt_min_or_max == 'max' else self.trials_metric < self.targets_metric)
           self.survivors_metric = np.where(mask, self.trials_metric, self.targets_metric)
           self.survivors_normed = np.where(mask.reshape(-1,1), self.trials_normed, self.targets_normed)
           self.survivors = np.where(mask.reshape(-1,1), self.trials, self.targets)
           self.survivors_unscaled = np.where(mask.reshape(-1,1), self.trials_unscaled, self.targets_unscaled)

    # Determine the best parameters and metric
    def determine_best(self):
        # Get the index of the best survivor
        self.best_index = np.argmax(self.survivors_metric) if self.opt_min_or_max == 'max' else np.argmin(self.survivors_metric)
        
        # Reset iter_no_improvement if a better solution is found.
        if self.iter > 1:
            if(self.survivors_metric[self.best_index] == self.best_metric):
                self.iter_no_improvement += 1
                self.better_solution_found = False
            else:
                self.iter_no_improvement = 0
                self.better_solution_found = True
                
        
        # If a better solution was found or it is the first iteration, then update best.
        if self.iter == 1 or self.iter_no_improvement == 0:
            self.best_normed = self.survivors_normed[self.best_index]
            self.best = self.survivors[self.best_index]
            self.best_unscaled = self.survivors_unscaled[self.best_index]
            self.best_metric = self.survivors_metric[self.best_index]
            self.update_history_bests()
            self.better_solution_found = True

    # Update the history trials
    def update_history_trials(self):
        zipped = zip([self.iter] * self.pop_size,
                     self.trials_normed.tolist(),
                     self.trials.tolist(),
                     self.trials_unscaled.tolist(),
                     self.trials_metric.tolist())
        new_trials = pd.DataFrame(columns = ['iter', 'trial_normed', 'trial', 'trial_unscaled', 'trial_metric'],
                                  data = [item for item in zipped])
        self.history['trials'] = pd.concat([self.history['trials'], new_trials]).reset_index(drop = True)
    
    # Update the history bests
    def update_history_bests(self):
        new_best = pd.DataFrame(columns = ['iter', 'best_normed', 'best', 'best_unscaled', 'best_metric'],
                                data = [[self.iter,
                                         self.best_normed.tolist(),
                                         self.best.tolist(),
                                         self.best_unscaled.tolist(),
                                         self.best_metric]])        
        self.history['bests'] = pd.concat([self.history['bests'], new_best]).reset_index(drop = True)
        
    # Update the history boundaries
    def update_history_boundaries(self):
        new_boundaries = pd.DataFrame(columns = ['iter', 'boundaries_min', 'boundaries_max'],
                                      data = [[self.iter,
                                               self.boundaries_min.tolist(),
                                               self.boundaries_max.tolist()]])
        self.history['boundaries'] = pd.concat([self.history['boundaries'], new_boundaries]).reset_index(drop = True)
    
    def write_best_parameters_to_file(self, file_path: str = None):
        if file_path is not None:
            try:
                df = pd.DataFrame({'name': self.parameter_names, 'value': self.best_unscaled})
                
                if file_path.split('.')[-1] == 'csv':
                    df.to_csv(file_path, index = False)
                elif file_path.split('.')[-1] == 'json':
                    df.to_json(file_path, orient = 'records', indent = 4)
                
            except Exception as e:
                print('ERROR on write_best_parameters_to_file:')
                print(e)
                pass
    
    def write_population_to_file(self, file_path: str = None):
        if file_path is not None:
            try:
                # Convert the dictionary to a DataFrame                
                df = pd.DataFrame(data = self.survivors_unscaled.T.tolist(), columns = [f'member_{i+1}' for i in range(self.pop_size)])
                df.insert(loc = 0, column = 'name', value = self.parameter_names)
                                
                if file_path.split('.')[-1] == 'csv':
                    df.to_csv(file_path, index = False)
                elif file_path.split('.')[-1] == 'json':
                    df.to_json(file_path, orient = 'columns', indent = 4)
                
            except Exception as e:
                print('ERROR on write_best_parameters_to_file:')
                print(e)
                pass

    def write_history_to_file(self, dir_path: str = None):
        if dir_path is not None:
            try:
                trials_path = os.path.join(dir_path, 'trials.csv')                                                      # Get the trials history
                temp = self.history['trials'][['iter', 'trial_unscaled', 'trial_metric']]                               # Get only the columns of interest.
                temp = pd.concat([temp, temp['trial_unscaled'].apply(pd.Series)], axis=1)                               # Concatenate the original DataFrame with the exploded 'trial_unscaled' column
                temp = temp.drop('trial_unscaled', axis=1)                                                              # Drop the original 'trial_unscaled' column
                temp = temp.rename(columns = {i: self.parameter_names[i] for i in range(len(self.parameter_names))})    # Rename the columns using the dictionary
                temp.to_csv(trials_path, index = False)                                                                 # Write to csv      
            except Exception as e:
                print('ERROR on write_history_to_file:')
                print(e)
                pass

    def update_results_dir(self, new_results_dir: str = None):
        self.results_dir = new_results_dir
    
    def apply_population_prediction(self):
        all_survivors = self.get_all_survivors() # get all survivors
        all_survivors = all_survivors[all_survivors['iter'] > self.iter - self.population_prediction_back_window] # get only the last population_prediction_back_window iterations
        all_survivors = all_survivors[['iter', 'survivor_normed']] # keep only the important columns
        iter_index = all_survivors['iter'] # index to be saved for later
        all_survivors = all_survivors['survivor_normed'].apply(pd.Series) # explode the values
        all_survivors.columns = self.parameter_names # set column names
        all_survivors.set_index(iter_index, inplace = True) # set index equal to iter

        std = all_survivors.groupby('iter').std() # calculate the std
        # std_smooth = std.apply(lambda col: smooth_data(col))
        std_drop = std.apply(lambda col: col.values[-1] / col.values[0]) # calculate the drop in std
        converging_parameters = std_drop[std_drop <= self.population_prediction_std_drop_threshold].index.to_list() # get the parameters which have a significant drop
        
        # Continue only if at least one parameter is converging
        if len(converging_parameters) == 0:
            return False
        
        # Calculate the lower and upper quantile for the converging parameters
        lower_quantile = all_survivors[converging_parameters].groupby('iter').agg({col: lambda x: x.quantile(self.population_prediction_lower_quantile) for col in converging_parameters})
        lower_quantile.reset_index(inplace = True, drop = True)
        # lower_quantile_smooth = lower_quantile.apply(lambda col: smooth_data(col))

        upper_quantile = all_survivors[converging_parameters].groupby('iter').agg({col: lambda x: x.quantile(self.population_prediction_upper_quantile) for col in converging_parameters})
        upper_quantile.reset_index(inplace = True, drop = True)
        # upper_quantile_smooth = upper_quantile.apply(lambda col: smooth_data(col))

        # plot_df(std)
        # plot_df(lower_quantile_smooth)
        # plot_df(upper_quantile_smooth)
        
        # Get the min and max of the lower and upper quantile
        lower_quantile_min_max = lower_quantile.apply(lambda col: pd.Series({'min': col.min(), 'max': col.max()}))
        upper_quantile_min_max = upper_quantile.apply(lambda col: pd.Series({'min': col.min(), 'max': col.max()}))

        # Norm the lower and upper quantile to [0, 1]
        lower_quantile_normed = lower_quantile.apply(lambda col: (col - col.min())/(col.max() - col.min()))
        upper_quantile_normed = upper_quantile.apply(lambda col: (col - col.min())/(col.max() - col.min()))
        
        # Fit the lower and upper quantile
        lower_quantile_fit = lower_quantile_normed.apply(lambda col: get_exponential_or_linear_fit(np.array(lower_quantile_normed.index), np.array(col)))
        lower_quantile_fit.set_index(pd.Index(['fit_parameters', 'fit_type']), inplace = True)
        
        upper_quantile_fit = upper_quantile_normed.apply(lambda col: get_exponential_or_linear_fit(np.array(upper_quantile_normed.index), np.array(col)))
        upper_quantile_fit.set_index(pd.Index(['fit_parameters', 'fit_type']), inplace = True)
        
        # lower_quantile_gp = pd.DataFrame(lower_quantile_normed.apply(lambda col: get_gaussian_process_fit(np.array(lower_quantile_normed.index), np.array(col)))).T
        # upper_quantile_gp = pd.DataFrame(upper_quantile_normed.apply(lambda col: get_gaussian_process_fit(np.array(upper_quantile_normed.index), np.array(col)))).T
        
        # Get the parameters that could be fit on the lower and upper quantile
        common_columns = lower_quantile_fit.columns.intersection(upper_quantile_fit.columns).to_list()
        lower_quantile_fit = lower_quantile_fit[common_columns]
        upper_quantile_fit = upper_quantile_fit[common_columns]
        
        # update the converging parameters
        converging_parameters = list(set(converging_parameters) & set(common_columns))
                    
        # Generate the fit data
        x = np.linspace(start = 0, stop = len(lower_quantile.index) + self.population_prediction_front_window - 1, num = len(lower_quantile.index) + self.population_prediction_front_window)
        lower_quantile_normed_fit_data = lower_quantile_fit.apply(lambda col: exponential_func(x, *col['fit_parameters']) if col['fit_type'] == 'exponential' else linear_func(x, *col['fit_parameters']))
        upper_quantile_normed_fit_data = upper_quantile_fit.apply(lambda col: exponential_func(x, *col['fit_parameters']) if col['fit_type'] == 'exponential' else linear_func(x, *col['fit_parameters']))
        
        # x = np.linspace(start = 0, stop = len(lower_quantile.index) + self.population_prediction_front_window - 1, num = len(lower_quantile.index) + self.population_prediction_front_window).reshape(-1, 1)
        # lower_quantile_normed_fit_data = lower_quantile_gp.apply(lambda col: col.values[0].predict(x))
        # upper_quantile_normed_fit_data = upper_quantile_gp.apply(lambda col: col.values[0].predict(x))

        # unnorm the fits
        lower_quantile_fit_data = lower_quantile_normed_fit_data.apply(lambda col: lower_quantile_min_max.loc['min'][col.name] + col * (lower_quantile_min_max.loc['max'][col.name] - lower_quantile_min_max.loc['min'][col.name]))
        upper_quantile_fit_data = upper_quantile_normed_fit_data.apply(lambda col: upper_quantile_min_max.loc['min'][col.name] + col * (upper_quantile_min_max.loc['max'][col.name] - upper_quantile_min_max.loc['min'][col.name]))

        # plot_parameter_fit(lower_quantile, lower_quantile_fit_data)
        # plot_parameter_fit(upper_quantile, upper_quantile_fit_data)
        # plot_quantile_fits(lower_quantile, upper_quantile, lower_quantile_fit_data, upper_quantile_fit_data)
        
        # get the upper and lower quantile fit for the last points
        last_predictions = lower_quantile_fit_data.apply(lambda col: [lower_quantile_fit_data[col.name].iloc[-1], upper_quantile_fit_data[col.name].iloc[-1]])
        last_predictions.set_index(pd.Index(['lower_quantile', 'upper_quantile']), inplace = True)
        
        # clip any values higher than 1 and lower than 0
        last_predictions_clipped = last_predictions.clip(0, 1)
        
        # filter the columns based on the condition that lower_quantile < upper_quantile
        converging_parameters = [col for col in last_predictions_clipped.columns if last_predictions_clipped.loc['lower_quantile', col] < last_predictions_clipped.loc['upper_quantile', col]]
        
        # Continue only if at least one parameter is converging
        if len(converging_parameters) == 0:
            return False
        
        # Generate a new population, where the converging parameters are taken from the fitted range
        last_predictions = last_predictions[converging_parameters]
        predictions = last_predictions.apply(lambda col: np.random.uniform(last_predictions.loc['lower_quantile', col.name], last_predictions.loc['upper_quantile', col.name], self.pop_size))
        
        # Insert the new values into the last population
        indices = []
        for col in predictions.columns:
            indices.append(self.parameter_names.index(col))
        self.donors_normed[:, indices] = np.array(predictions)
        
        # Unnorm and unscale the donors
        self.donors = np.apply_along_axis(func1d = unnorm_member,
                                          axis = 1,
                                          arr = self.donors_normed,
                                          minimum = self.boundaries_min,
                                          maximum = self.boundaries_max)
        self.donors_unscaled = self.get_unscaled_arr(self.donors)        
        
        # Set the trials equal to the donors
        self.trials_normed = self.donors_normed
        self.trials = self.donors
        self.trials_unscaled = self.donors_unscaled
                
        return True
    
    # def applyAuroraAcceleration(self):
    #     if((self.iteration >= self.auroraAccelerationStartThreshold) and (self.iteration % self.auroraAccelerationFrequency == 0)):
    #         print('Aurora acceleration...')
    #         # self.plotAllParamsEvolution()
    #         # self.plotSingleParamAuroraEvolution('x', 500)
            
    #         SLOPE_UP = 1
    #         SLOPE_DOWN = 2
    #         SLOPE_ZERO_HIGH_STD = 3
    #         SLOPE_ZERO_LOW_STD = 4
 
    #         STD_SLOPE_THRESHOLD = 0.0025
    #         STD_VALUE_THRESHOLD = 0.05
            
    #         MEAN_QUANTILE_LOW = 0.35
    #         MEAN_QUANTILE_HIGH = 0.65
            
    #         std = np.stack(self.history.groupby('iteration').first()['survivorStd'])
    #         std = pd.DataFrame(std, columns=self.factorNames).tail(self.auroraAccelerationBackWindow).reset_index().drop(columns=['index'], axis=0)
    #         stdSmooth = std.apply(lambda col: self.smoothData(col), axis=0)
    #         stdSmoothDiff = stdSmooth.apply(lambda col: self.diffData(col), axis=0)
            
    #         mean = np.stack(self.history.groupby('iteration').first()['survivorMean'])
    #         mean = pd.DataFrame(mean, columns=self.factorNames).tail(self.auroraAccelerationBackWindow).reset_index().drop(columns=['index'], axis=0)
    #         meanSmooth = mean.apply(lambda col: self.smoothData(col), axis=0)

    #         temp = np.stack(self.history['survivorNormed'])
    #         temp = pd.DataFrame(temp, columns=self.factorNames).set_index(self.history['iteration'])
            
    #         meanQuantileLow = temp.groupby('iteration').quantile(q=MEAN_QUANTILE_LOW).tail(self.auroraAccelerationBackWindow)
    #         meanQuantileLowSmooth = meanQuantileLow.apply(lambda col: self.smoothData(col), axis=0)

    #         meanQuantileHigh = temp.groupby('iteration').quantile(q=MEAN_QUANTILE_HIGH).tail(self.auroraAccelerationBackWindow)
    #         meanQuantileHighSmooth = meanQuantileHigh.apply(lambda col: self.smoothData(col), axis=0)
            
    #         def getParamCategory(val, diff):
    #             # temp = diff.mean()
    #             temp = np.array(val)
    #             temp = (temp[-1] - temp[0]) / temp.shape[0]
    #             if(temp < -STD_SLOPE_THRESHOLD):
    #                 category = SLOPE_DOWN
    #             elif(temp > STD_SLOPE_THRESHOLD):
    #                 category = SLOPE_UP
    #             elif(temp > STD_VALUE_THRESHOLD):
    #                 category = SLOPE_ZERO_HIGH_STD
    #             else:
    #                 category = SLOPE_ZERO_LOW_STD
    #             return category
            
    #         paramsCategories = stdSmooth.apply(lambda col: getParamCategory(col, stdSmoothDiff[col.name]), axis=0)
            
    #         paramsSlopeDown = paramsCategories[paramsCategories == SLOPE_DOWN].index.values
    #         print(f"Number of slope down parameters: {len(paramsSlopeDown)} / {len(self.factorNames)}")
    #         if(paramsSlopeDown.size == 0):
    #             print('No slope down parameters found')
    #         else:
    #             # paramsSlopeUp = paramsCategories[paramsCategories == SLOPE_UP].index.values
    #             # paramsSlopeZeroLowStd = paramsCategories[paramsCategories == SLOPE_ZERO_LOW_STD].index.values
    #             # paramsSlopeZeroHighStd = paramsCategories[paramsCategories == SLOPE_ZERO_HIGH_STD].index.values
                
    #             paramsSlopeDownStdSmooth = stdSmooth[paramsSlopeDown]
    #             paramsSlopeDownMeanSmooth = meanSmooth[paramsSlopeDown]
    #             paramsSlopeDownmeanQuantileLowSmooth = meanQuantileLowSmooth[paramsSlopeDown]
    #             paramsSlopeDownmeanQuantileHighSmooth = meanQuantileHighSmooth[paramsSlopeDown]
                
    #             paramsSlopeDownPredictions = paramsSlopeDownStdSmooth.apply(lambda col: self.getPredictionsExpOrLinear(col, paramsSlopeDownMeanSmooth[col.name], paramsSlopeDownmeanQuantileLowSmooth[col.name], paramsSlopeDownmeanQuantileHighSmooth[col.name]), axis=0).set_index(pd.Index(['std_pred', 'mean_pred', 'meanQuantileLow_pred', 'meanQuantileHigh_pred']))              
    #             # self.plotPredictionsExp(paramsSlopeDownStdSmooth, paramsSlopeDownMeanSmooth, paramsSlopeDownmeanQuantileLowSmooth, paramsSlopeDownmeanQuantileHighSmooth, paramsSlopeDownPredictions)

    #             stdSlopeDown = paramsSlopeDownPredictions.loc['std_pred'].apply(lambda row: np.min(np.abs(row)))
    #             stdModified = pd.DataFrame(stdSmooth.iloc[-1]).apply(lambda row: stdSlopeDown[row.name] if row.name in stdSlopeDown.index.values else row, axis=1)
    #             if(isinstance(stdModified, pd.DataFrame)):
    #                 stdModified = stdModified.iloc[:, 0]
                
    #             meanSlopeDown = paramsSlopeDownPredictions.loc['mean_pred'].apply(lambda row: row[-1])
    #             meanModified = pd.DataFrame(meanSmooth.iloc[-1]).apply(lambda row: meanSlopeDown[row.name] if row.name in meanSlopeDown.index.values else row, axis=1)
    #             if(isinstance(meanModified, pd.DataFrame)):
    #                 meanModified = meanModified.iloc[:, 0]

    #             meanQuantileLowSlopeDown = paramsSlopeDownPredictions.loc['meanQuantileLow_pred'].apply(lambda row: row[-1])
    #             meanQuantileLowModified = pd.DataFrame(meanQuantileLowSmooth.iloc[-1]).apply(lambda row: meanQuantileLowSlopeDown[row.name] if row.name in meanQuantileLowSlopeDown.index.values else row, axis=1)
    #             if(isinstance(meanQuantileLowModified, pd.DataFrame)):
    #                 meanQuantileLowModified = meanQuantileLowModified.iloc[:, 0]

    #             meanQuantileHighSlopeDown = paramsSlopeDownPredictions.loc['meanQuantileHigh_pred'].apply(lambda row: row[-1])
    #             meanQuantileHighModified = pd.DataFrame(meanQuantileHighSmooth.iloc[-1]).apply(lambda row: meanQuantileHighSlopeDown[row.name] if row.name in meanQuantileHighSlopeDown.index.values else row, axis=1)
    #             if(isinstance(meanQuantileHighModified, pd.DataFrame)):
    #                 meanQuantileHighModified = meanQuantileHighModified.iloc[:, 0]

    #             auroraTrialNormed = np.zeros([self.populationSize, len(self.factorNames)])
    #             i = 0
    #             for factor in self.factorNames:
    #                 if(factor in meanSlopeDown.index.values):
    #                     # temp = np.random.normal(meanModified[factor], stdModified[factor], self.populationSize)
    #                     temp = np.random.uniform(meanQuantileLowModified[factor], meanQuantileHighModified[factor], self.populationSize)
    #                 else:
    #                     temp = np.full((self.populationSize,), meanModified[factor])
    #                 auroraTrialNormed[:,i] = temp
    #                 i = i + 1
    #             auroraTrialNormed[0,:] = meanModified.values
    #             self.auroraTrialNormed = auroraTrialNormed
    #             auroraTrial = np.apply_along_axis(self.unnormMember, 1, auroraTrialNormed)
    #             self.auroraTrial = auroraTrial
                
    #             auroraTrialFactors = []
    #             temp = self.factors.copy()
    #             for values in self.auroraTrial:
    #                 temp['valueScaled'] = values
    #                 temp['value'] = temp.apply(lambda row: self.unscaleParam(row, 'valueScaled'), axis=1)
    #                 auroraTrialFactors.append(temp.copy())
                
    #             auroraResponse = self.evalFunc(auroraTrialFactors, *self.evalFuncArgs)
    #             self.auroraResponse = auroraResponse
    #             print(f"Best aurora result: {min(auroraResponse)}")
                
    #             numberOfMembersToSubstitute = np.int(self.populationSize * self.auroraAccelerationSubstituteQuantile)
    #             auroraBestIndices = np.argsort(np.array(auroraResponse))[0:numberOfMembersToSubstitute]
    #             randomIndices = np.random.choice(self.populationSize, numberOfMembersToSubstitute, replace=False)
                
    #             i = 0
    #             numberOfBetterResults = 0
    #             for index in randomIndices:
    #                 if(auroraResponse[auroraBestIndices[i]] < self.trialResponse[index]):
    #                     self.trialNormed[index, :] = auroraTrialNormed[auroraBestIndices[i], :]
    #                     self.trial[index, :] = auroraTrial[auroraBestIndices[i], :]
    #                     self.trialResponse[index] = auroraResponse[auroraBestIndices[i]]
    #                     numberOfBetterResults = numberOfBetterResults + 1 
    #                 i = i + 1
                 
    #             print(f"Number of better results: {numberOfBetterResults}")
                
    #             self.updateAuroraHistory()
        
        
        
        
        
        
        
