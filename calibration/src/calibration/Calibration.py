#%% Imports
from reference_data import Reference_data
from reference_data.visualization import plot_all_groups
from testbench.ngspice import Ngspice_testbench_compiler
from parameters import Parameters
from optimization.differential_evolution import Differential_evolution
from simulation.ngspice import Ngspice_simulator
from cost_function import Cost_function


#%% calibration class

class Calibration:
    def __init__(self,
                 reference_data_file: str = None,
                 parameters_file: str = None,
                 optimizer: str = None,
                 simulator: str = None,
                 testbenches_file: str = None,
                 dut_file: str = None,
                 dut_name: str = None,
                 results_dir: str = None,
                 ):
                
        self.reference_data_file = reference_data_file
        self.parameters_file = parameters_file
        self.testbenches_file = testbenches_file
        self.optimizer = optimizer
        self.simulator = simulator
        self.dut_file = dut_file
        self.dut_name = dut_name
        self.results_dir = results_dir
        
        self.validate_simulator()
        self.validate_optimizer()
        
        
    def validate_simulator(self):
        available_simulators = ['ngspice']
        if self.simulator not in available_simulators:
            raise simulator_missing(f'ERROR! Simulator has to be one of the following: {available_simulators}')
            
        
    def validate_optimizer(self):
        available_optimizers = ['differential_evolution']
        if self.optimizer not in available_optimizers:
            raise optimizer_missing(f'ERROR! Optimizer has to be one of the following: {available_optimizers}')


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
        if self.simulator == 'ngspice':
            self.simulator = Ngspice_simulator()
    
    
    def get_optimizer(self):
        if self.optimizer == 'differential_evolution':
            self.optimizer = Differential_evolution()
    
    

            
        
        
    def run_default_simulation(self, plot = False):
        # 1. Parse the reference data
        self.get_reference_data()

        # 2. Parse the parameters
        self.get_parameters()
        
        # 3. Build the testbenches
        self.get_testbenches()
        
        # # 4. Generate random parameters
        # random_params = self.parameters.generate_random_parameters()
        
        # 4. Get the simulator
        self.get_simulator()
        
        # 5. Simulate
        results = self.simulator.simulate_testbenches(testbenches = self.testbenches,
                                                      extract_results = True,
                                                      reference_data = self.reference_data.data)
        
        
        
        if plot:
            plot_all_groups(results)

        parts = [
            {
                'id': 'out_char_lin',
                'group_types': ['ids_vds_vgs'],
                'metric_type': 'rmse',
                'weight': 1,
                'norm': True,
                'transform': 'lin',
                'extra_args': {}
            },
            {
                'id': 'out_char_log',
                'group_types': ['ids_vds_vgs'],
                'metric_type': 'rmse',
                'weight': 1,
                'norm': True,
                'transform': 'log',
                'extra_args': {}
            }
        ]

        cost_function = Cost_function(parts = parts)
        error_metric = cost_function.run(data = results)
        print(error_metric)
        
        
        
        
        
        
        
    def calibrate(self):
        # 1. Parse the reference data
        self.get_reference_data()

        # 2. Parse the parameters
        self.get_parameters()
        
        # 3. Build the testbenches
        self.get_testbenches()

        # 4. 



#%% custom exception class for missing simulator
class simulator_missing(Exception):
    def __init__(self, message):
        print(message)


#%% custom exception class for missing optimizer
class optimizer_missing(Exception):
    def __init__(self, message):
        print(message)