#%% Imports
import pandas as pd
import numpy as np
import json
import re
import tempfile
import os
from testbench.ngspice.utils import is_equidistant, get_curve_index, get_instance_parameters_for_curve, write_contents_to_file


#%% 
class Ngspice_testbench_compiler():
    
    def __init__(self,
                 testbenches_file: str = None,          # file where testbenches are defined
                 reference_data: pd.DataFrame = None,   # dataframe of the reference data
                 max_testbenches_per_file = 1000,       # maximum testbenches per file
                 working_directory: str = None,         # the directory where to save the simulation files
                 model_parameters: dict = None,         # parameters of the model
                 dut_name: str = 'dut',                 # the name of the dut (device under test)
                 dut_file: str = 'dut.cir',             # the path of the dut
                 ):
        
        self.testbenches_file = testbenches_file
        self.reference_data = reference_data
        self.max_testbenches_per_file = max_testbenches_per_file
        self.working_directory = working_directory
        self.model_parameters = model_parameters
        self.dut_name = dut_name
        self.dut_file = dut_file
        
        if self.working_directory is None:
            self.working_directory = tempfile.TemporaryDirectory().name
            
        self.working_directory = os.path.abspath(self.working_directory)


    def create_testbenches(self):
        self.deternime_curve_index()
        self.parse_testbenches_file()        
        self.determine_simulation_type()
        self.determine_file_id()
        self.build_circuit_and_measure_blocks()
        self.build_files()
        
        
    def write_simulation_files(self):
        self.files.apply(lambda row: write_contents_to_file(row), axis = 1)
                

    # Set a unique curve_index for each curve
    def deternime_curve_index(self):
        if self.reference_data is not None:
            self.reference_data['curve_index'] = self.reference_data.apply(lambda row: get_curve_index(row), axis = 1)

    
    # Read and parse the testbench file and save them in a dataframe
    def parse_testbenches_file(self):
        if self.testbenches_file is not None:
            with open(self.testbenches_file) as json_file:
                self.testbenches_raw = json.load(json_file)
                self.testbenches = pd.DataFrame.from_dict(self.testbenches_raw).explode('testbench_type', ignore_index=True)


    # Set the simulation_type and some auxiliary columns
    def determine_simulation_type(self):
        if self.reference_data is not None:
            self.reference_data[['simulation_type', 'start', 'stop', 'step']] = self.reference_data.apply(lambda row: self.get_simulation_type_from_curve(row), axis = 1, result_type = 'expand')


    # Get the simulation type from the curve data
    def get_simulation_type_from_curve(self, curve) -> tuple:
        testbench = self.testbenches[self.testbenches['testbench_type'] == curve['testbench_type']]
        
        if len(testbench.index) == 0:
            print('ERROR: No testbench for the following curve.')
            print(curve)
            return None, None, None, None
        elif len(testbench.index) > 1:
            print('WARNING: More than 1 testbench found for the following curve:')
            print(curve)
            print('Considering the first of the testbenches defined.')
            
        testbench = testbench.iloc[0]
        
        if testbench['simulation_type'] == 'dc':
            if is_equidistant(curve['x_values']):
                return 'dc_sweep', curve['x_values'][0], curve['x_values'][-1], curve['x_values'][1]-curve['x_values'][0]
            else:
                return 'dc_list', None, None, None
        elif testbench['simulation_type'] == 'ac':
            return None, None, None, None
            # return 'ac', None, None, None
        else:
            return None, None, None, None


    # Group the curves into similar ones in order to put them in the same file
    def determine_file_id(self):
        self.reference_data['x_values'] = self.reference_data['x_values'].apply(lambda x: tuple(x)) # Convert the x_values into tuples, so that they can be grouped upon
        self.reference_data['file_id'] = None
        self.file_id = 0
        data_split_1 = self.reference_data.groupby(['temp', 'simulation_type'], dropna = False)
        for (temp, simulation_type), split_1 in data_split_1:
            if simulation_type == 'dc_sweep':
                data_split_2 = split_1.groupby(['start', 'stop', 'step'], dropna = False)
                for (start, stop, step), split_2 in data_split_2:
                    self.set_file_id_for_split(split_2)
            elif simulation_type == 'dc_list':
                data_split_2 = split_1.groupby(['x_values'], dropna = False)
                for (x_values), split_2 in data_split_2:
                    self.set_file_id_for_split(split_2)

   

    # For each split, set the file_id
    def set_file_id_for_split(self, split):
        split_length = len(split.index)
        
        # if the max nr of testbenches per file is smaller than the length of the split,
        # then it should be split into chunks which have to be as equal as possible in length
        if split_length > self.max_testbenches_per_file:
            nr_chunks = int(np.ceil(split_length / self.max_testbenches_per_file))
            if split_length % self.max_testbenches_per_file == 0:
                chunk_sizes = [int(split_length / nr_chunks)] * nr_chunks
            else:
                small_chunk_size = int(np.floor(split_length / nr_chunks))
                big_chunk_size = small_chunk_size + 1
                nr_big_chunks = split_length % nr_chunks
                nr_small_chunks = nr_chunks - nr_big_chunks
                chunk_sizes = [1] * nr_chunks
                chunk_sizes[0:nr_big_chunks] = [big_chunk_size] * nr_big_chunks
                chunk_sizes[nr_big_chunks:] = [small_chunk_size] * nr_small_chunks
            
            # Calculate chunk_sizes
            chunk_indices = []
            cumulative_sum = 0
            for num in chunk_sizes:
                cumulative_sum += num
                chunk_indices.append(cumulative_sum)
            chunk_indices = chunk_indices[0:-1]

            chunks = np.split(split, chunk_indices)
            for chunk in chunks:
                self.reference_data.loc[self.reference_data.index.isin(chunk.index), 'file_id'] = self.file_id
                self.file_id += 1
        else:
            self.reference_data.loc[self.reference_data.index.isin(split.index), 'file_id'] = self.file_id
            self.file_id += 1


    # Build circuit and measure blocks
    def build_circuit_and_measure_blocks(self):      
        self.reference_data['circuit'] = self.reference_data.apply(lambda row: self.build_circuit_block_for_curve(row), axis = 1)
        self.reference_data[['measure', 'measure_variables']] = self.reference_data.apply(lambda row: self.build_measure_block_for_curve(row), axis = 1, result_type = 'expand')        
        
    
    # Build circuit block for one curve
    def build_circuit_block_for_curve(self, curve) -> str:
        testbench = self.get_testbench_by_type(curve['testbench_type'])
        if testbench is None:
            return None
        
        if 'circuit' not in testbench:
            print('ERROR: No circuit defined for the following testbench:')
            print(testbench)
            return None
        
        circuit_template = '\n'.join(testbench['circuit'])
        
        to_replace = set(re.findall(r"<<(.*?)>>", circuit_template))
        
        circuit = f"********************* dut testbench {curve['curve_index']} *********************\n"
        circuit += circuit_template
        circuit += '\n*************************************************************'
        
        if 'dut_name' in to_replace:
            circuit = circuit.replace('<<dut_name>>', self.dut_name)
            to_replace.remove('dut_name')
        
        if 'index' in to_replace:
            circuit = circuit.replace('<<index>>', curve['curve_index'])
            to_replace.remove('index')
        
        if 'instance_parameters' in to_replace:
            instance_parameters = get_instance_parameters_for_curve(testbench, curve)
            instance_parameters_joined = ' '.join([f'{key}={value}' for key, value in instance_parameters.items()])
            circuit = circuit.replace('<<instance_parameters>>', instance_parameters_joined)
            to_replace.remove('instance_parameters')
        
        for param in to_replace:
            if curve['extra_var_name'] == param:
                circuit = circuit.replace(f'<<{param}>>', str(curve['extra_var_value']))
            elif param in curve:
                circuit = circuit.replace(f'<<{param}>>', str(curve[param]))
            else:
                print('ERROR: {param} not found in the curve, but is defined in the testbench.')
                print(f'curve: {curve}')
                print(f'testbench: {testbench}')
                return None
        
        return circuit

    
    # Build measure block for one curve
    def build_measure_block_for_curve(self, curve):
        testbench = self.get_testbench_by_type(curve['testbench_type'])
        if testbench is None:
            return None
        
        if 'measure' not in testbench:
            print('ERROR: No measure defined for the following testbench:')
            print(testbench)
            return None
        
        measure_variables = [key.replace('<<index>>', curve['curve_index']) for key, value in testbench['measure'].items()]

        measure_template = '\n'.join([f'let {key} = {value}' for key, value in testbench['measure'].items()])
        measure = measure_template.replace('<<index>>', curve['curve_index'])
        return measure, measure_variables
    
    
    # Get testbench by type
    def get_testbench_by_type(self, testbench_type) -> pd.Series:
        testbench = self.testbenches[self.testbenches['testbench_type'] == testbench_type]
        
        if len(testbench.index) == 0: # if no testbench exists, return none
            print('ERROR: No testbench found for the following testbench_type:')
            print(testbench_type)
            print('Returning None.')
            return None
        elif len(testbench.index) > 1: # if more than 1 testbench exist, then return the first one.
            print('WARNING: More than 1 testbench found for the following testbench_type:')
            print(testbench_type)
            print('Considering the first of the testbenches defined.')
        
        return testbench.iloc[0]
    
    
    # Build files
    def build_files(self):
        self.files = pd.DataFrame(columns = ['file_id', 'simulation_type', 'nr_testbenches',
                                             'contents', 'x_name', 'y_name',
                                             'simulation_file_name', 'simulation_file_path',
                                             'results_dir', 'results_file_name', 'results_file_path'])
        data_split = self.reference_data.groupby('file_id')
        for file_id, split in data_split:
            simulation_type = split.iloc[0]['simulation_type']
            if simulation_type == 'dc_list':
                self.build_file_dc_list(split)
            elif simulation_type == 'dc_sweep':
                self.build_file_dc_sweep(split)            


    # Build file for dc_list simulations.
    def build_file_dc_list(self, curves):
        file_id = curves.iloc[0]['file_id']
        simulation_type = curves.iloc[0]['simulation_type']
        x_name = curves.iloc[0]['x_name']
        y_name = curves.iloc[0]['y_name']
        values_list = ' '.join([str(val) for val in curves.iloc[0]['x_values']])
        results_dir = self.working_directory
        simulation_file_name = f'dc_list_{file_id}.cir'
        simulation_file_path = os.path.join(results_dir, simulation_file_name)
        results_file_name = f'dc_list_{file_id}.csv'
        results_file_path = os.path.join(results_dir, results_file_name)
        all_measure_variables = sum(curves['measure_variables'].tolist(), [])
        
        if 'temp' in curves:
            temp = curves.iloc[0]['temp']
        else:
            temp = 27
            
        file_contents = "**********************************************************\n"
        file_contents += "* THIS FILE IS GENERATED BY AIVALANCHE\n"
        file_contents += f"* FILE ID: {file_id}\n"
        file_contents += f"* SIMULATION TYPE: {simulation_type}\n"
        file_contents += "**********************************************************\n\n"
        
        file_contents += "* Define the temperature\n"
        file_contents += f".TEMP {temp}\n\n"
        
        file_contents += "* Include the dut file\n"
        file_contents += f".INCLUDE {self.dut_file}\n\n"
        
        file_contents += "** Start testbenches\n"
        for index, curve in curves.iterrows():
            file_contents += "\n"
            file_contents += curve['circuit']
            file_contents += "\n"
        file_contents += "\n** End testbenches\n\n"
        
        file_contents += "* Declare the v_sweep, which will change during the simulation.\n"
        file_contents += "v_sweep v_sweep 0 0\n\n"
        
        file_contents += "********** Start of control section **********\n"
        file_contents += ".control\n\n"
        
        if self.model_parameters is not None:
            file_contents += "** Change model parameters.\n"
            for key, value in self.model_parameters.items():
                if value < 0:
                    file_contents += f"alterparam {self.dut_name} {key} = 1*{value}\n"
                else:
                    file_contents += f"alterparam {self.dut_name} {key} = {value}\n"
            file_contents += "reset\n\n"
        
        file_contents += "** Write the header of the results file.\n"
        file_contents += f"echo \"{','.join(all_measure_variables)}\" > {results_file_path}\n\n"
        
        file_contents += "** Start the simulation loop.\n"
        file_contents += f"set values_list = ( {values_list} )\n"
        file_contents += "foreach val $values_list\n"
        file_contents += "alter v_sweep $val\n"
        file_contents += "op\n"
        for index, curve in curves.iterrows():
            file_contents += curve['measure']
            file_contents += "\n"
        
        file_contents += f"echo \"{','.join(['$&' + var for var in all_measure_variables])}\" >> {results_file_path}\n"
        file_contents += "end\n\n"

        file_contents += ".endc\n"
        file_contents += "********** End of control section **********\n\n"

        file_contents += ".end"
        
        new_file = pd.DataFrame({'file_id': [file_id],
                                 'simulation_type': [simulation_type],
                                 'nr_testbenches': [len(curves.index)],
                                 'contents': [file_contents],
                                 'x_name': x_name,
                                 'y_name': y_name,
                                 'simulation_file_name': [simulation_file_name],
                                 'simulation_file_path': [simulation_file_path],
                                 'results_dir': [results_dir],
                                 'results_file_name': [results_file_name],
                                 'results_file_path': [results_file_path]})
        
        self.files = pd.concat([self.files, new_file])


    # Build file for dc_sweep simulations.        
    def build_file_dc_sweep(self, curves):
        file_id = curves.iloc[0]['file_id']
        simulation_type = curves.iloc[0]['simulation_type']
        x_name = curves.iloc[0]['x_name']
        y_name = curves.iloc[0]['y_name']
        results_dir = self.working_directory
        simulation_file_name = f'dc_sweep_{file_id}.cir'
        simulation_file_path = os.path.join(results_dir, simulation_file_name)
        results_file_name = f'dc_sweep_{file_id}.csv'
        results_file_path = os.path.join(results_dir, results_file_name)
        all_measure_variables = sum(curves['measure_variables'].tolist(), [])
        
        if 'temp' in curves:
            temp = curves.iloc[0]['temp']
        else:
            temp = 27
            
        file_contents = "**********************************************************\n"
        file_contents += "* THIS FILE IS GENERATED BY AIVALANCHE\n"
        file_contents += f"* FILE ID: {file_id}\n"
        file_contents += f"* SIMULATION TYPE: {simulation_type}\n"
        file_contents += "**********************************************************\n\n"
        
        file_contents += "* Define the temperature\n"
        file_contents += f".TEMP {temp}\n\n"
        
        file_contents += "* Include the dut file\n"
        file_contents += f".INCLUDE {self.dut_file}\n\n"
        
        file_contents += "** Start testbenches\n"
        for index, curve in curves.iterrows():
            file_contents += "\n"
            file_contents += curve['circuit']
            file_contents += "\n"
        file_contents += "\n** End testbenches\n\n"
        
        file_contents += "* Declare the v_sweep, which will change during the simulation.\n"
        file_contents += "v_sweep v_sweep 0 0\n"
        file_contents += f".dc v_sweep {curve['start']} {curve['stop']} {curve['step']}\n\n"
        
        file_contents += "********** Start of control section **********\n"
        file_contents += ".control\n\n"
        
        if self.model_parameters is not None:
            file_contents += "** Change model parameters.\n"
            for key, value in self.model_parameters.items():
                if value < 0:
                    file_contents += f"alterparam {self.dut_name} {key} = 1*{value}\n"
                else:
                    file_contents += f"alterparam {self.dut_name} {key} = {value}\n"
            file_contents += "reset\n\n"
        
        file_contents += "** Run the simulation.\n"
        file_contents += "run\n\n"
        
        for index, curve in curves.iterrows():
            file_contents += curve['measure']
            file_contents += "\n"
        
        file_contents += "\n** Save the output to file.\n"
        file_contents += "set wr_vecnames\n"
        file_contents += "set wr_singlescale\n"
        file_contents += f"wrdata {results_file_path} {' '.join(all_measure_variables)}\n\n"

        file_contents += ".endc\n"
        file_contents += "********** End of control section **********\n\n"

        file_contents += ".end"
        
        new_file = pd.DataFrame({'file_id': [file_id],
                                 'simulation_type': [simulation_type],
                                 'nr_testbenches': [len(curves.index)],
                                 'contents': [file_contents],
                                 'x_name': x_name,
                                 'y_name': y_name,
                                 'simulation_file_name': [simulation_file_name],
                                 'simulation_file_path': [simulation_file_path],
                                 'results_dir': [results_dir],
                                 'results_file_name': [results_file_name],
                                 'results_file_path': [results_file_path]})
        
        self.files = pd.concat([self.files, new_file])
    
        
    