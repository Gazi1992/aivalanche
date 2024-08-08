#%% Imports
from reference_data.Reference_data import Reference_data
from reference_data.visualization import plot_all_groups
from reference_data.utils import write_reference_data_to_file
from testbench.ngspice import Ngspice_testbench_compiler
from parameters.Parameters import Parameters
from optimization.differential_evolution import Differential_evolution
from calibration.custom_dask import init_dask, close_dask
from calibration.utils import run_single_simulation, calculate_error_metrics, run_single_simulation_kafka_local
from calibration.logging import logging_config, set_log_file, set_log_level
from simulation.ngspice import Ngspice_simulator
from cost_function import Cost_function
from cost_function.exceptions import raise_exception
from datetime import datetime
from copy import copy
import os, shutil, json, uuid, dask, pickle, logging, pandas as pd, threading, time, queue

#%% calibration class
class Calibration:
    def __init__(self,
                 reference_data: str | Reference_data = None,
                 parameters: str | Parameters = None,
                 testbenches: str | Ngspice_testbench_compiler = None,
                 dut_file: str = None,
                 dut_name: str = 'dut',
                 results_dir: str = None,
                 optimizer_config: dict = None,
                 simulator_config: dict = None,
                 cost_function_config: dict = None,
                 running_environment = 'local',
                 command_queue = None):
                
        self.reference_data = reference_data
        self.parameters = parameters
        self.testbenches = testbenches
        self.dut_file = dut_file
        self.dut_name = dut_name
        self.results_dir = results_dir
        self.output_path = results_dir
        self.optimizer_config = optimizer_config
        self.simulator_config = simulator_config
        self.cost_function_config = cost_function_config
        
        self.running_environment = running_environment
        self.running_environment_options = ('local', 'dask_local', 'kafka_local')    
        self.dask_upload_files = []
        
        self.command_queue = command_queue
        
        self.validate_simulator()
        self.validate_cost_function()
        
        self.get_reference_data()
        self.get_parameters()
        self.get_testbenches()
        self.get_simulator()
        self.get_cost_function()
        
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            
        if self.running_environment not in self.running_environment_options:
            print(f'WARNING: running_environment must be on of te following: {self.running_environment_options}. Setting it to "local".')
            self.running_environment = 'local'
        
        self.setup_logging()
        
        self.abort_flag = False
        self.optimization_thread = None
        
    def setup_logging(self):
        self.logging_config = logging_config
        logging.config.dictConfig(self.logging_config)
        self.logger = logging.getLogger(self.__class__.__name__)
            
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
        if type(self.reference_data) == str:
            self.reference_data = Reference_data(file = self.reference_data)

    def get_parameters(self):
        if type(self.parameters) == str:
            self.parameters = Parameters(file = self.parameters)

    def get_testbenches(self):
        if type(self.testbenches) == str:
            self.testbenches = Ngspice_testbench_compiler(file = self.testbenches,
                                                          reference_data = self.reference_data.data,
                                                          dut_file = self.dut_file,
                                                          dut_name = self.dut_name,
                                                          model_parameters = self.parameters.get_default_parameters(),
                                                          working_directory = self.output_path,
                                                          inline = self.running_environment in ['dask_local', 'kafka'])
        self.testbenches.create_testbenches()
        
    def get_simulator(self):
        if self.simulator_config['type'] == 'ngspice':
            if 'timeout' in self.simulator_config.keys():
                self.simulator = Ngspice_simulator(timeout = self.simulator_config['timeout'])
            else:
                self.simulator = Ngspice_simulator()
    
    def get_optimizer(self):
        if self.optimizer_config['type'] == 'differential_evolution':
            
            temp = copy(self.optimizer_config)
            del temp['type']
            self.optimizer = Differential_evolution(parameters = self.parameters.all_parameters,
                                                    eval_func = self.run_multiple_simulations,
                                                    eval_func_args = None,
                                                    **temp)

    def get_cost_function(self):
        if self.cost_function_config['type'] == 'default':
            self.cost_function = Cost_function(parts = self.cost_function_config['parts'])

    def run_no_parameter_simulation(self, plot: bool = False, delete_files: bool = False):
        self.testbenches.remove_model_parameters()
        simulation_results = run_single_simulation(testbenches = self.testbenches,
                                                   simulator = self.simulator,
                                                   reference_data = self.reference_data.data,
                                                   simulation_files_path = self.results_dir,
                                                   plot = plot,
                                                   delete_files = delete_files)
        
        error_metric = calculate_error_metrics(cost_function = self.cost_function, data = simulation_results)
        return(error_metric)

    def run_default_simulation(self, plot: bool = False, delete_files: bool = False, print_output: bool = True):
        simulation_files_dir = os.path.join(self.results_dir, 'simulation_files')
        if not os.path.exists(simulation_files_dir):
            simulation_files_dir = self.results_dir
            
        simulation_results = run_single_simulation(testbenches = self.testbenches,
                                                   simulator = self.simulator,
                                                   reference_data = self.reference_data.data,
                                                   simulation_files_path = simulation_files_dir,
                                                   plot = plot,
                                                   delete_files = delete_files,
                                                   print_output = print_output)
        
        error_metric = calculate_error_metrics(cost_function = self.cost_function, data = simulation_results, parameters = self.parameters)
        return(error_metric)

    def run_random_simulation(self, plot: bool = False, delete_files: bool = False):
        random_params = self.parameters.generate_random_parameters()
        simulation_results = run_single_simulation(parameters = random_params, 
                                                   testbenches = self.testbenches,
                                                   simulator = self.simulator,
                                                   reference_data = self.reference_data.data,
                                                   simulation_files_path = self.results_dir,
                                                   plot = plot,
                                                   delete_files = delete_files)
        
        error_metric = calculate_error_metrics(cost_function = self.cost_function, data = simulation_results, parameters = random_params)
        return(error_metric)

    def run_multiple_simulations(self, parameters: list[dict] = None, **kwargs):
        if self.running_environment == 'local':
            return self.run_multiple_simulations_local(parameters, **kwargs)
        elif self.running_environment == 'dask_local':
            return self.run_multiple_simulations_dask_local(parameters, **kwargs)
        elif self.running_environment == 'kafka_local':
            return self.run_multiple_simulations_kafka_local(parameters, **kwargs)
    
    def run_multiple_simulations_local(self, parameters: list[dict] = None, **kwargs):
        responses = {'results': [], 'error_metrics': [], 'metrics': []}
        for param in parameters:
            try:
                simulation_results = run_single_simulation(parameters = param, 
                                                           testbenches = self.testbenches,
                                                           simulator = self.simulator,
                                                           reference_data = self.reference_data.data,   
                                                           simulation_files_path = self.simulation_files_path,
                                                           plot = False,
                                                           delete_files = True,
                                                           print_output = False)
                metric = calculate_error_metrics(cost_function = self.cost_function, data = simulation_results, parameters = param)
            except Exception:
                e_m = raise_exception('simulation_failed_exception')
                simulation_results = None
                metric = {'data': simulation_results, 'parameters': param, 'error_metric': {'total': e_m}}

            responses['results'].append(metric['data'])
            responses['error_metrics'].append(metric['error_metric'])
            responses['metrics'].append(metric['error_metric']['total'])
        return responses
    
    def run_multiple_simulations_dask_local(self, parameters: list[dict] = None, **kwargs):
        responses = {'results': [], 'error_metrics': [], 'metrics': []}
        # Create simulation futures
        simulation_futures = [dask.delayed(run_single_simulation)(parameters = param, 
                                                                  testbenches = self.testbenches,
                                                                  simulator = self.simulator,
                                                                  reference_data = self.reference_data.data,   
                                                                  simulation_files_path = self.simulation_files_path,
                                                                  running_environment = self.running_environment,
                                                                  plot = False,
                                                                  delete_files = True,
                                                                  print_output = False) for param in parameters]
        # Create error metric futures
        error_metric_futures = [dask.delayed(calculate_error_metrics)(cost_function = self.cost_function,
                                                                      data = sim_res,
                                                                      parameters = param) for sim_res, param in zip(simulation_futures, parameters)]
        # Evaluate the futures
        error_metrics = dask.compute(error_metric_futures, scheduler = "threads", synchronous = True)
        
        if len(error_metrics) == 1:
            error_metrics = error_metrics[0]
            
        responses['results'] = [item['data'] for item in error_metrics]
        responses['error_metrics'] = [item['error_metric'] for item in error_metrics]
        responses['metrics'] = [item['error_metric']['total'] for item in error_metrics]
        return responses    

    def run_multiple_simulations_kafka_local(self, parameters: list[dict] = None, **kwargs):
        responses = {'results': [], 'error_metrics': [], 'metrics': []}
        simulation_files = []
        # create the pickle files
        for param in parameters:
            output_dir = os.path.join(self.simulation_files_path, str(uuid.uuid4()))
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            file_path = os.path.join(output_dir, 'simulation_input.pkl')
            simulation_files.append(file_path)
            self.write_input_to_pkl(file_path = file_path, parameters = param,
                                    testbenches = self.testbenches, simulator = self.simulator,
                                    reference_data = self.reference_data, simulation_files_path = output_dir,
                                    cost_function = self.cost_function, plot = False, delete_files = False)
        # simulate and calculate the error metric
        for file in simulation_files:
            metric = run_single_simulation_kafka_local(file)
            responses['results'].append(metric['data'])
            responses['error_metrics'].append(metric['error_metric'])
            responses['metrics'].append(metric['error_metric']['total'])
        return responses

    def calibrate(self, create_new_dir: bool = True, simulation_files_path: str = None, write_input_to_files: bool = True):
        self.validate_optimizer()
        self.get_optimizer()
        if self.running_environment == 'dask_local':
            self.cluster = init_dask(scale = 2)
        if create_new_dir:
            self.create_new_output_dir()
        else:
            if simulation_files_path is not None and os.path.exists(simulation_files_path):
                self.simulation_files_path = simulation_files_path
            else:
                self.simulation_files_path = self.results_dir
            self.testbenches.update_working_directory(new_working_dir = self.simulation_files_path)
        if write_input_to_files:
            self.write_input_to_files()    
        
        # Start optimization in a separate thread
        self.optimization_thread = threading.Thread(target = self.run_optimization_thread)
        self.optimization_thread.start()
        
        # Monitor the abort flag
        while self.optimization_thread.is_alive():
            if self.command_queue is not None:
                try:
                    command = self.command_queue.get_nowait()
                    if command == 'abort':
                        self.abort_flag = True
                except queue.Empty:
                    pass
            
            if self.abort_flag:
                self.optimizer.abort_optimization()
                break
            time.sleep(0.1)  # Sleep to prevent busy waiting
            # if i > 100:
            #     self.abort_calibration()
        # Wait for the optimization thread to finish
        self.optimization_thread.join()

        if self.running_environment == 'dask_local':
            close_dask(self.cluster)
    
    def abort_calibration(self):
        self.abort_flag = True
    
    def run_optimization_thread(self):
       self.optimizer.run_optimization()
       
    def check_for_abort(self):
        if self.command_queue:
            try:
                command = self.command_queue.get_nowait()
                if command == 'abort':
                    print("Received abort command")
                    self.abort_flag = True
                    if hasattr(self, 'optimizer'):
                        self.optimizer.abort_flag = True
            except queue.Empty:
                pass  # No command in the queue
       
    def create_new_output_dir(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self.output_path = os.path.join(self.results_dir, f"calibration_{timestamp}")
        os.makedirs(self.output_path)

        self.simulation_files_path = os.path.join(self.output_path, 'simulation_files')
        os.mkdir(self.simulation_files_path)

        self.input_path = os.path.join(self.output_path, 'inputs')
        os.mkdir(self.input_path)

        set_log_file(self.logging_config, os.path.join(self.output_path, 'calibrate.log'))
        self.testbenches.update_working_directory(new_working_dir = self.simulation_files_path)
        
    def write_input_to_files(self):
        shutil.copy(self.reference_data.file, os.path.join(self.input_path, os.path.basename(self.reference_data.file)))
        shutil.copy(self.parameters.file, os.path.join(self.input_path, os.path.basename(self.parameters.file)))
        shutil.copy(self.testbenches.file, os.path.join(self.input_path, os.path.basename(self.testbenches.file)))
        shutil.copy(self.dut_file, os.path.join(self.input_path, os.path.basename(self.dut_file)))
        self.write_config_dict_to_file(config_dict = self.optimizer_config, file_path = os.path.join(self.input_path, 'optimizer_config.json'))
        self.write_config_dict_to_file(config_dict = self.cost_function_config, file_path = os.path.join(self.input_path, 'cost_function_config.json'))
        self.write_config_dict_to_file(config_dict = self.simulator_config, file_path = os.path.join(self.input_path, 'simulator_config.json'))

    def write_config_dict_to_file(self, config_dict: dict = None, file_path: str = None):
        if config_dict is not None and file_path is not None:
            filtered_data = {}
            for key, value in config_dict.items(): # Filter out non-numeric and non-string values
                if isinstance(value, (int, str, float, dict, list, tuple)):
                    filtered_data[key] = value
            with open(file_path, "w") as file: # Open a file in write mode and write the filtered data to the file in JSON format
                json.dump(filtered_data, file, indent = 4)
                
    def write_input_to_pkl(self, file_path: str = None, parameters: dict = None,
                           testbenches: Ngspice_testbench_compiler = None, simulator: Ngspice_simulator = None,
                           reference_data: pd.DataFrame = None, simulation_files_path: str = None,
                           cost_function: Cost_function = None, plot: bool = False, delete_files: bool = True):
        input_dict = {'parameters': parameters,
                      'testbenches': testbenches,
                      'simulator': simulator,
                      'reference_data': reference_data.data,
                      'simulation_files_path': simulation_files_path,
                      'cost_function': cost_function,
                      'plot': plot,
                      'delete_files': delete_files}
        with open(file_path, 'wb') as file:
            pickle.dump(input_dict, file)

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