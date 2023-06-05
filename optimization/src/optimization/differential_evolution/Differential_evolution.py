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
    mutation_factor ->
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
import pandas as pd
import numpy as np
from pyDOE import lhs
from optimization.differential_evolution.utils import preprocess_parameters, unnorm_member, norm_member, scale_parameter
from optimization.differential_evolution.visualization import plot_metric_evolution, plot_parameter_evolution


#%% differential_evolution class

class Differential_evolution:
    def __init__(self,
                 eval_func: callable = None,                            # function that is used for the evaluation of the fittness of the parameter sets
                 eval_func_args: dict = None,                           # extra arguments to pass to the evaluation function 
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
        self.eval_func_args = {} if eval_func_args is None else eval_func_args
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
        

    # Run the optimization loop.
    def run_optimization(self):
        
        # Prepare for the first iteration
        self.prepare_first_iter()
        
        # stay in the loop as long as the stop criteria is not reached
        while not self.is_stop_criteria_reached:
            parameters = self.get_trials_unscaled()             # get the trials_unscaled
            responses = self.eval_func(iteration = self.iter,
                                       parameters = parameters,
                                       **self.eval_func_args)   # run the evaluation function
            self.save_metrics(responses['metrics'])             # save the metrics
            
            self.determine_survivors()                          # determine the survivors
            self.determine_best()                               # determine the best parameters and best metric
            self.update_history_trials()                        # append the trials to the history trials
            
            # plot trial metric evolution
            if self.plot_trial_metric_evolution_period is not None and self.iter % self.plot_trial_metric_evolution_period == 0:
                plot_metric_evolution(iterations = self.history['trials']['iter'],
                                      metrics = self.history['trials']['trial_metric'])
                
            # plot parameter evolution
            if self.plot_parameter_evolution_period is not None and self.iter % self.plot_parameter_evolution_period == 0:
                plot_parameter_evolution(parameters = self.parameter_names, data = np.array(self.history['trials']['trial_normed'].tolist()))
            
            
            # plot survivor metric evolution
            if self.plot_survivor_metric_evolution_period is not None and self.iter % self.plot_survivor_metric_evolution_period == 0:    
                all_survivors = self.get_all_survivors()
                plot_metric_evolution(iterations = all_survivors['iter'],
                                      metrics = all_survivors['survivor_metric'])
            
            # Run the callback
            if self.iter == 1:
                if self.callback_after_first_iter is not None:
                    self.callback_after_first_iter(parameters = parameters,
                                                   responses = responses,
                                                   iteration = self.iter,
                                                   best_parameters = self.best_unscaled,
                                                   best_metric = self.best_metric,
                                                   **self.eval_func_args)
            else:
                if self.callback_after_each_iter is not None:
                    self.callback_after_each_iter(parameters = parameters,
                                                  responses = responses,
                                                  iteration = self.iter,
                                                  best_parameters = self.best_unscaled,
                                                  best_metric = self.best_metric,
                                                  **self.eval_func_args)
            
            # Determine survivor and best, update history and generate new trials
            self.prepare_next_iter()
        
        # once the stop criteria is reached
        self.show_final_result()
        if self.callback_after_last_iter is not None:
            self.callback_after_last_iter(iteration = self.iter,
                                          responses = responses,
                                          best_parameters = self.best_unscaled,
                                          best_metric = self.best_metric,
                                          history = self.history,
                                          **self.eval_func_args)
            
    
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
        if self.opt_min_or_max == 'min' and self.best_metric < self.metric_threshold:
            self.is_stop_criteria_reached = True
            self.stop_reason = "Good Enough Metric reached"
        elif self.opt_min_or_max == 'max' and self.best_metric > self.metric_threshold:
            self.is_stop_criteria_reached = True
            self.stop_reason = "Good Enough Metric reached"
        elif self.iter_no_improvement > self.max_iter_without_improvement:
            self.is_stop_criteria_reached = True
            self.stop_reason = "Maximum number of iterations without improvement reached"
        elif self.iter > self.max_iterations:
            self.iter -= 1
            self.is_stop_criteria_reached = True
            self.stop_reason = "Maximum number of iterations reached"
        else:
            self.is_stop_criteria_reached = False
    
    
    # Save metrics
    def save_metrics(self, metrics):
        self.trials_metric = np.array(metrics)
        
    
    # Prepare first iteration
    def prepare_first_iter(self):
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
    
    
    # Get best parameters as a dictionary
    def get_best_parameters(self):
        return {key: val for key, val in zip(self.parameter_names, self.best_unscaled)}
    
    
    # Generate a mutation
    def generate_mutations(self):        
        # throw the dice to get 3 random intigers between 0 and pop_size-1
        dice = [np.random.choice([j for j in range(self.pop_size) if j != i], size = (1, 3), replace = False) for i in range(self.pop_size)]
        dice = np.array(dice).reshape(-1,3)
        
        # get random members
        temp = self.targets_normed[dice].reshape(-1,3,self.nr_parameters)
        rand_mem_1 = temp[:,0,:]
        rand_mem_2 = temp[:,1,:]
        rand_mem_3 = temp[:,2,:]

        # calculate the donor
        donors_normed = (rand_mem_1
                       + self.mutation_factor * (self.best_normed - rand_mem_1)
                       + self.mutation_factor * (rand_mem_2 - rand_mem_3))
        
        # if donor goes beyond [0,1], then assign it a random value
        violation_mask = (donors_normed > 1) | (donors_normed < 0)
        donors_normed[violation_mask] = np.random.rand()
        
        return donors_normed
    
    
    # Generate a recombination between the target and the donor
    def generate_recombinations(self):
        # get a random number for each parameter
        dice = np.random.rand(self.pop_size, self.nr_parameters)        

        # combine donor and target, getting the value from the donor whereever dice is less than the recombination_factor and from the target otheerwise
        trials_normed = np.where(dice < self.recombination_factor, self.donors_normed, self.targets_normed)

        return trials_normed
    
    
    # Generate a donor for each target
    def generate_donors(self):
        # In the first iteration generate donor at random.
        if(self.iter == 1):
            self.donors_normed = lhs(self.nr_parameters, samples = self.pop_size) # Use latin-hyper-cube to generate the random samples
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
            else:
                self.iter_no_improvement = 0
        
        # If a better solution was found or it is the first iteration, then update best.
        if self.iter == 1 or self.iter_no_improvement == 0:
            self.best_normed = self.survivors_normed[self.best_index]
            self.best = self.survivors[self.best_index]
            self.best_unscaled = self.survivors_unscaled[self.best_index]
            self.best_metric = self.survivors_metric[self.best_index]
            self.update_history_bests()
                

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
            
            
            
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
