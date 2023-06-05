#%% Imports
from reference_data import Reference_data
from reference_data.visualization import plot_all_groups
from testbench.ngspice import Ngspice_testbench_compiler
from parameters import Parameters
from optimization.differential_evolution import Differential_evolution
from simulation.ngspice import Ngspice_simulator
from cost_function import Cost_function
from cost_function.exceptions import raise_exception
from copy import deepcopy

#%% calibration class

class Calibration:
    def __init__(self,
                 reference_data_file: str = None,
                 parameters_file: str = None,
                 testbenches_file: str = None,
                 dut_file: str = None,
                 dut_name: str = None,
                 results_dir: str = None,
                 optimizer_config: dict = None,
                 simulator_config: dict = None,
                 cost_function_config: dict = None
                 ):
                
        self.reference_data_file = reference_data_file
        self.parameters_file = parameters_file
        self.testbenches_file = testbenches_file
        self.dut_file = dut_file
        self.dut_name = dut_name
        self.results_dir = results_dir
        self.optimizer_config = optimizer_config
        self.simulator_config = simulator_config
        self.cost_function_config = cost_function_config
        
        self.validate_simulator()
        self.validate_cost_function()
        
        self.get_reference_data()
        self.get_parameters()
        self.get_testbenches()
        self.get_simulator()
        self.get_cost_function()

        
    def validate_simulator(self):
        available_simulators = ['ngspice']
        if self.simulator_config['type'] not in available_simulators:
            raise simulator_missing(f'ERROR! Simulator type has to be one of the following: {available_simulators}')
            
        
    def validate_optimizer(self):
        available_optimizers = ['differential_evolution']
        if self.optimizer_config['type'] not in available_optimizers:
            raise optimizer_missing(f'ERROR! Optimizer type has to be one of the following: {available_optimizers}')
        
    
    def validate_cost_function(self):
        available_cost_functions = ['default']
        if self.cost_function_config['type'] not in available_cost_functions:
            raise cost_function_missing(f'ERROR! Cost function type has to be one of the following: {available_cost_functions}')


    def get_reference_data(self):
        self.reference_data = Reference_data(file = self.reference_data_file)


    def get_parameters(self):
        self.parameters = Parameters(file = self.parameters_file)


    def get_testbenches(self):
        self.testbenches = Ngspice_testbench_compiler(testbenches_file = self.testbenches_file,
                                                      reference_data = self.reference_data.data,
                                                      dut_file = self.dut_file,
                                                      dut_name = self.dut_name,
                                                      model_parameters = self.parameters.get_default_parameters(),
                                                      working_directory = self.results_dir)
        self.testbenches.create_testbenches()
        
        
    def get_simulator(self):
        if self.simulator_config['type'] == 'ngspice':
            self.simulator = Ngspice_simulator()
    
    
    def get_optimizer(self):
        if self.optimizer_config['type'] == 'differential_evolution':
            self.optimizer = Differential_evolution(parameters = self.parameters.all_parameters,
                                                    eval_func = self.run_multiple_simulations,
                                                    eval_func_args = None,
                                                    callback_after_first_iter = self.optimizer_config['callback_after_first_iter'],
                                                    callback_after_each_iter = self.optimizer_config['callback_after_each_iter'],
                                                    callback_after_last_iter = self.optimizer_config['callback_after_last_iter'],
                                                    pop_size = self.optimizer_config['pop_size'],
                                                    metric_threshold = self.optimizer_config['metric_threshold'],
                                                    max_iterations = self.optimizer_config['max_iterations'],
                                                    max_iter_without_improvement = self.optimizer_config['max_iter_without_improvement'],
                                                    init_pop = self.optimizer_config['init_pop'],
                                                    init_pop_out_of_range_param = self.optimizer_config['init_pop_out_of_range_param'],
                                                    defaults_in_init_pop = self.optimizer_config['defaults_in_init_pop'],
                                                    plot_parameter_evolution_period = self.optimizer_config['plot_parameter_evolution_period'],
                                                    plot_survivor_metric_evolution_period = self.optimizer_config['plot_survivor_metric_evolution_period'],
                                                    adaptive_boundaries = self.optimizer_config['adaptive_boundaries'])
    
    
    def get_cost_function(self):
        if self.cost_function_config['type'] == 'default':
            self.cost_function = Cost_function(parts = self.cost_function_config['parts'])
    

    def run_single_simulation(self, parameters: dict = None, plot: bool = False,
                              delete_files: bool = True, return_results: bool = False, print_output: bool = True):
        
        # If parameters are given, then create new testbenches
        if parameters is not None:
            new_testbenches = deepcopy(self.testbenches)
            new_testbenches.modify_model_parameters(parameters)
        else:
            new_testbenches = self.testbenches
        
        # Simulate
        results = self.simulator.simulate_testbenches(testbenches = new_testbenches,
                                                      extract_results = True,
                                                      reference_data = self.reference_data.data,
                                                      delete_files = delete_files,
                                                      print_output = print_output)
    
        # Plot the data
        if plot:
            plot_all_groups(results)
        
        # Calculate the error metric
        error_metric = self.cost_function.run(data = results, parameters = parameters)
        
        if return_results:
            return error_metric, results
        else:
            return error_metric


    def run_default_simulation(self, plot = False):
        error_metric = self.run_single_simulation(plot = plot)
        print(error_metric)


    def run_random_simulation(self, plot = False):
        random_params = self.parameters.generate_random_parameters()
        error_metric = self.run_single_simulation(parameters = random_params, plot = plot)
        print(error_metric)


    def run_multiple_simulations(self, iteration: int = None, parameters: list[dict] = None):     
        responses = {'results': [], 'error_metrics': [], 'metrics': []}
        for param in parameters:
            try:
                error_metric, results = self.run_single_simulation(parameters = param,
                                                          plot = False,
                                                          delete_files = True,
                                                          return_results = True,
                                                          print_output = False)
            except Exception:
                e_m = raise_exception('simulation_failed_exception')
                error_metric = {'total': e_m}
                
            responses['error_metrics'].append(error_metric)
            responses['metrics'].append(error_metric['total'])
            responses['results'].append(results)
                    
        return responses


    def calibrate(self):
        self.validate_optimizer()
        self.get_optimizer()
        self.optimizer.run_optimization()


#%% custom exception class for missing simulator
class simulator_missing(Exception):
    def __init__(self, message):
        print(message)


#%% custom exception class for missing optimizer
class optimizer_missing(Exception):
    def __init__(self, message):
        print(message)


#%% custom exception class for missing cost_function
class cost_function_missing(Exception):
    def __init__(self, message):
        print(message)