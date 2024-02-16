#%% Imports
from reference_data import Reference_data
from reference_data.visualization import plot_all_groups
from reference_data.utils import write_reference_data_to_file
from testbench.ngspice import Ngspice_testbench_compiler
from parameters import Parameters
from optimization.differential_evolution import Differential_evolution
from calibration.custom_dask import init_dask, close_dask
from calibration.utils import run_single_simulation, calculate_error_metrics, test_ngspice
from simulation.ngspice import Ngspice_simulator
from cost_function import Cost_function
from cost_function.exceptions import raise_exception
from copy import deepcopy
from datetime import datetime
import os, shutil, json, uuid, dask


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
                 cost_function_config: dict = None,
                 use_dask: bool = False,
                 dask_env: str = 'local'):
                
        self.reference_data_file = reference_data_file
        self.parameters_file = parameters_file
        self.testbenches_file = testbenches_file
        self.dut_file = dut_file
        self.dut_name = dut_name
        self.results_dir = results_dir
        self.output_path = results_dir
        self.optimizer_config = optimizer_config
        self.simulator_config = simulator_config
        self.cost_function_config = cost_function_config
        
        self.use_dask = use_dask
        self.dask_env = dask_env
        self.dask_env_options = ('local', 'containers')        
        self.dask_upload_files = []
        
        self.validate_simulator()
        self.validate_cost_function()
        
        self.get_reference_data()
        self.get_parameters()
        self.get_testbenches()
        self.get_simulator()
        self.get_cost_function()
        
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            
        if self.dask_env not in self.dask_env_options:
            print(f'WARNING: dask_env must be on of te following: {self.dask_env_options}. Setting it to "local".')
            self.dask_env = 'local'
        
        if self.use_dask:
            self.cluster = init_dask(dask_env = self.dask_env, uplaod_files = self.dask_upload_files)
            
                    
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
                                                      working_directory = self.output_path,
                                                      inline = self.use_dask and self.dask_env == 'containers')
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
                                                    callback_after_better_solution_found = self.optimizer_config['callback_after_better_solution_found'],
                                                    pop_size = self.optimizer_config['pop_size'],
                                                    metric_threshold = self.optimizer_config['metric_threshold'],
                                                    max_iterations = self.optimizer_config['max_iterations'],
                                                    max_iter_without_improvement = self.optimizer_config['max_iter_without_improvement'],
                                                    init_pop = self.optimizer_config['init_pop'],
                                                    init_pop_out_of_range_param = self.optimizer_config['init_pop_out_of_range_param'],
                                                    defaults_in_init_pop = self.optimizer_config['defaults_in_init_pop'],
                                                    plot_parameter_evolution_period = self.optimizer_config['plot_parameter_evolution_period'],
                                                    plot_survivor_metric_evolution_period = self.optimizer_config['plot_survivor_metric_evolution_period'],
                                                    write_history_to_file_period = self.optimizer_config['write_history_to_file_period'],
                                                    results_dir = self.optimizer_config['results_dir'],
                                                    adaptive_boundaries = self.optimizer_config['adaptive_boundaries'])
    
    
    def get_cost_function(self):
        if self.cost_function_config['type'] == 'default':
            self.cost_function = Cost_function(parts = self.cost_function_config['parts'])


    def run_no_parameter_simulation(self, plot: bool = False, delete_files: bool = False):
        self.testbenches.remove_model_parameters()
        error_metric = run_single_simulation(testbenches = self.testbenches,
                                             simulator = self.simulator,
                                             reference_data = self.reference_data.data,
                                             simulation_files_path = self.results_dir,
                                             plot = plot,
                                             delete_files = delete_files)
        print(error_metric)


    def run_default_simulation(self, plot: bool = False, delete_files: bool = False):
        simulation_results = run_single_simulation(testbenches = self.testbenches,
                                                   simulator = self.simulator,
                                                   reference_data = self.reference_data.data,
                                                   simulation_files_path = self.results_dir,
                                                   plot = plot,
                                                   delete_files = delete_files)
        
        error_metric = calculate_error_metrics(cost_function = self.cost_function, data = simulation_results)
        
        print(error_metric)


    def run_random_simulation(self, plot: bool = False, delete_files: bool = False):
        random_params = self.parameters.generate_random_parameters()
        simulation_results = run_single_simulation(parameters = random_params, 
                                                   testbenches = self.testbenches,
                                                   simulator = self.simulator,
                                                   reference_data = self.reference_data.data,
                                                   simulation_files_path = self.results_dir,
                                                   plot = plot,
                                                   delete_files = delete_files)
        
        error_metric = calculate_error_metrics(cost_function = self.cost_function, data = simulation_results)

        print(error_metric)
        

    def run_multiple_simulations(self, parameters: list[dict] = None, **kwargs):  
        responses = {'results': [], 'error_metrics': [], 'metrics': []}
        if self.use_dask:
            
            # Create simulation futures
            simulation_futures = [dask.delayed(run_single_simulation)(parameters = param, 
                                                                      testbenches = self.testbenches,
                                                                      simulator = self.simulator,
                                                                      reference_data = self.reference_data.data,   
                                                                      simulation_files_path = self.simulation_files_path,
                                                                      use_dask = True,
                                                                      dask_env = self.dask_env,
                                                                      plot = False,
                                                                      delete_files = True,
                                                                      print_output = False) for param in parameters]
            
            # Create error metric futures
            error_metric_futures = [dask.delayed(calculate_error_metrics)(cost_function = self.cost_function,
                                                                          data = sim_res,
                                                                          parameters = param) for sim_res, param in zip(simulation_futures, parameters)]
            
            # Evaluate the futures
            if self.dask_env == 'local':
                error_metrics = dask.compute(error_metric_futures, scheduler = "threads", synchronous = True)
            elif self.dask_env == 'containers':
                error_metrics = dask.compute(error_metric_futures, synchronous = True)
            
            if len(error_metrics) == 1:
                error_metrics = error_metrics[0]
            responses['results'] = [item['data'] for item in error_metrics]
            responses['error_metrics'] = [item['error_metric'] for item in error_metrics]
            responses['metrics'] = [item['error_metric']['total'] for item in error_metrics]
        else:
            for param in parameters:
                try:
                    simulation_results = run_single_simulation(parameters = param, 
                                                               testbenches = self.testbenches,
                                                               simulator = self.simulator,
                                                               reference_data = self.reference_data.data,   
                                                               simulation_files_path = self.simulation_files_path,
                                                               plot = False,
                                                               delete_files = False,
                                                               print_output = True)
                    metric = calculate_error_metrics(cost_function = self.cost_function, data = simulation_results, parameters = param)
                except Exception:
                    e_m = raise_exception('simulation_failed_exception')
                    simulation_results = None
                    metric = {'data': simulation_results, 'parameters': param, 'error_metric': {'total': e_m}}

                responses['results'].append(metric['data'])
                responses['error_metrics'].append(metric['error_metric'])
                responses['metrics'].append(metric['error_metric']['total'])
                    
        return responses
    
    
    def calibrate(self):
        self.create_new_output_dir()
        self.validate_optimizer()
        self.get_optimizer()
        self.write_input_to_files()
        self.optimizer.run_optimization()
        if self.use_dask:
            close_dask(self.cluster)
        
    def create_new_output_dir(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_path = os.path.join(self.results_dir, f"calibration_{timestamp}")
        self.simulation_files_path = os.path.join(self.output_path, 'simulation_files')
        self.input_path = os.path.join(self.output_path, 'input')
        os.makedirs(self.output_path)
        os.mkdir(self.simulation_files_path)
        os.mkdir(self.input_path)
        self.testbenches.update_working_directory(new_working_dir = self.simulation_files_path)
        
    
    def write_input_to_files(self):
        shutil.copy(self.reference_data_file, os.path.join(self.input_path, os.path.basename(self.reference_data_file)))
        shutil.copy(self.parameters_file, os.path.join(self.input_path, os.path.basename(self.parameters_file)))
        shutil.copy(self.testbenches_file, os.path.join(self.input_path, os.path.basename(self.testbenches_file)))
        shutil.copy(self.dut_file, os.path.join(self.input_path, os.path.basename(self.dut_file)))
        self.write_config_dict_to_file(config_dict = self.optimizer_config, file_path = os.path.join(self.input_path, 'optimizer_config.json'))
        self.write_config_dict_to_file(config_dict = self.cost_function_config, file_path = os.path.join(self.input_path, 'cost_function_config.json'))
        self.write_config_dict_to_file(config_dict = self.simulator_config, file_path = os.path.join(self.input_path, 'simulator_config.json'))


    def write_config_dict_to_file(self, config_dict: dict = None, file_path: str = None):
        if config_dict is not None and file_path is not None:
        
            filtered_data = {}
    
            # Filter out non-numeric and non-string values
            for key, value in config_dict.items():
                if isinstance(value, (int, str, float, dict, list, tuple)):
                    filtered_data[key] = value
            
            # Open a file in write mode
            with open(file_path, "w") as file:
                # Write the filtered data to the file in JSON format
                json.dump(filtered_data, file, indent = 4)


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