#%% Imports
import json
import re, os, tempfile, pandas as pd, numpy as np
from testbench.ngspice.utils import is_equidistant, get_curve_index, get_instance_parameters_for_curve, write_contents_to_file, extract_between_tags


#%% Ngspice_testbench_compiler is used to create all the simulation files.
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
        self.build_circuit_and_results()
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
                return 'dc_sweep', curve['x_values'][0], curve['x_values'][-1], round(curve['x_values'][1]-curve['x_values'][0], 10)
            else:
                return 'dc_list', None, None, None
        elif testbench['simulation_type'] == 'ac_point':
            if is_equidistant(curve['x_values']):
                return 'ac_point_dc_sweep', curve['x_values'][0], curve['x_values'][-1], round(curve['x_values'][1]-curve['x_values'][0], 10)
            else:
                return 'ac_point_dc_list', None, None, None
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
                data_split_2 = split_1.groupby(['start', 'stop', 'step', 'testbench_type'], dropna = False)
                for (start, stop, step, testbench_type), split_2 in data_split_2:
                    self.set_file_id_for_split(split_2)
            elif simulation_type == 'dc_list':
                data_split_2 = split_1.groupby(['x_values', 'testbench_type'], dropna = False)
                for (x_values, testbench_type), split_2 in data_split_2:
                    self.set_file_id_for_split(split_2)
            elif simulation_type == 'ac_point_dc_sweep':
                data_split_2 = split_1.groupby(['start', 'stop', 'step', 'testbench_type'], dropna = False)
                for (start, stop, step, testbench_type), split_2 in data_split_2:
                    self.set_file_id_for_split(split_2)
            elif simulation_type == 'ac_point_dc_list':
                data_split_2 = split_1.groupby(['x_values', 'testbench_type'], dropna = False)
                for (x_values, testbench_type), split_2 in data_split_2:
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
    def build_circuit_and_results(self):      
        self.reference_data['circuit'] = self.reference_data.apply(lambda row: self.build_circuit_for_curve(row), axis = 1)
        self.reference_data[['save_variables',
                             'rename_variables',
                             'calculate_variables',
                             'output_variables']] = self.reference_data.apply(lambda row: self.build_results_for_curve(row), axis = 1, result_type = 'expand')        
        

    # Build circuit block for one curve
    def build_circuit_for_curve(self, curve) -> str:
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
                print(f'ERROR: {param} not found in the curve, but is defined in the testbench.')
                print(f'curve: {curve}')
                print(f'testbench: {testbench}')
                return None
        
        return circuit

    
    # Build measure block for one curve
    def build_results_for_curve(self, curve):
        testbench = self.get_testbench_by_type(curve['testbench_type'])
        if testbench is None:
            return None
        
        if 'results' not in testbench:
            print('ERROR: No results defined for the following testbench:')
            print(testbench)
            return None
        
        save_variables = None
        if "save" in testbench['results']:
            save_variables = [item.replace('<<index>>', curve['curve_index']) for item in testbench['results']['save']]
        
        output_variables = save_variables
        if "output" in testbench['results']:
            output_variables = [item.replace('<<index>>', curve['curve_index']) for item in testbench['results']['output']]
        
        rename_variables = None
        if 'rename' in testbench['results']:
            rename_variables = {key.replace('<<index>>', curve['curve_index']): value.replace('<<index>>', curve['curve_index']) for key, value in testbench['results']['rename'].items()}
        
        calculate_variables = None
        if 'calculate' in testbench['results']:
            calculate_variables = {key.replace('<<index>>', curve['curve_index']): value.replace('<<index>>', curve['curve_index']) for key, value in testbench['results']['calculate'].items()}
            for key, value in calculate_variables.items():
                to_replace = extract_between_tags(value)
                for item in to_replace:
                    try:
                        calculate_variables[key] = value.replace(f'<<{item}>>', str(curve[item]))
                    except Exception as e:
                        print(e)
                        print(f'ERROR trying to replace the value for {item} in the testbench.')
                        print(testbench)
                        return None
        
        return save_variables, rename_variables, calculate_variables, output_variables
    
    
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
                                             'results_dir', 'results_file_name', 'results_file_path',
                                             'save_variables', 'output_variables', 'rename_variables', 'calculate_variables'])
        data_split = self.reference_data.groupby('file_id')
        for file_id, split in data_split:
            simulation_type = split.iloc[0]['simulation_type']
            if simulation_type == 'dc_sweep':
                self.build_file_dc_sweep(split)
            elif simulation_type == 'dc_list':
                self.build_file_dc_list(split)
            elif simulation_type == 'ac_point_dc_sweep':
                self.build_file_ac_point_dc_sweep(split)
            elif simulation_type == 'ac_point_dc_list':
                self.build_file_ac_point_dc_list(split)

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
        all_save_variables = list(set(sum(curves['save_variables'].tolist(), [])))
        all_output_variables = list(set(sum(curves['output_variables'].tolist(), [])))
        all_rename_variables = {k: v for var in curves['rename_variables'] for k, v in var.items()}

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
        
        file_contents += self.add_model_parameters_to_file()
        
        file_contents += "** Declare the vectors to save.\n"
        file_contents += f"save {' '.join(all_save_variables)}\n\n"
        
        file_contents += "** Run the dc sweep analysis.\n"
        file_contents += f"dc v_sweep {curve['start']} {curve['stop']} {curve['step']}\n"
        
        file_contents += "\n** Save the output to file.\n"
        file_contents += "set wr_vecnames\n"
        file_contents += "set wr_singlescale\n"
        file_contents += f"wrdata {results_file_path} {' '.join(all_output_variables)}\n\n"

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
                                 'results_file_path': [results_file_path],
                                 'save_variables': [all_save_variables],
                                 'output_variables': [all_output_variables],
                                 'rename_variables': [all_rename_variables],
                                 'calculate_variables': [None]})
        
        self.files = pd.concat([self.files, new_file])
    
    
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
        all_save_variables = list(set(sum(curves['save_variables'].tolist(), [])))
        all_output_variables = list(set(sum(curves['output_variables'].tolist(), [])))
        all_rename_variables = {k: v for var in curves['rename_variables'] for k, v in var.items()}

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
        
        file_contents += self.add_model_parameters_to_file()
        
        file_contents += "** Declare the vectors to save.\n"
        file_contents += f"save {' '.join(all_save_variables)}\n\n"
        
        file_contents += "** Write the header of the results file.\n"
        file_contents += f"echo \"{','.join(all_output_variables)}\" > {results_file_path}\n\n"
        
        file_contents += "** Start the simulation loop.\n"
        file_contents += f"set values_list = ( {values_list} )\n"
        file_contents += "foreach val $values_list\n"
        file_contents += "    alter v_sweep $val\n"
        file_contents += "    op\n"
        
        file_contents += f"    echo \"{','.join(['$&' + var for var in all_output_variables])}\" >> {results_file_path}\n"
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
                                 'results_file_path': [results_file_path],
                                 'save_variables': [all_save_variables],
                                 'output_variables': [all_output_variables],
                                 'rename_variables': [all_rename_variables],
                                 'calculate_variables': [None]})
        
        self.files = pd.concat([self.files, new_file])


    # Build file for ac_sweep simulations.
    def build_file_ac_point_dc_sweep(self, curves):
        file_id = curves.iloc[0]['file_id']
        simulation_type = curves.iloc[0]['simulation_type']
        x_name = curves.iloc[0]['x_name']
        y_name = curves.iloc[0]['y_name']
        results_dir = self.working_directory
        simulation_file_name = f'ac_point_dc_sweep_{file_id}.cir'
        simulation_file_path = os.path.join(results_dir, simulation_file_name)
        results_file_name = f'ac_point_dc_sweep_{file_id}.csv'
        results_file_path = os.path.join(results_dir, results_file_name)
        all_save_variables = list(set(sum(curves['save_variables'].tolist(), [])))
        all_output_variables = list(set(sum(curves['output_variables'].tolist(), [])))
        all_rename_variables =  None if curves['rename_variables'].isnull().all() else {k: v for var in curves['rename_variables'][curves['rename_variables'].notnull()] for k, v in var.items()}
        all_calculate_variables = None if curves['calculate_variables'].isnull().all() else {k: v for var in curves['calculate_variables'][curves['calculate_variables'].notnull()] for k, v in var.items()}

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
        
        file_contents += self.add_model_parameters_to_file()
        
        file_contents += "** Declare the vectors to save.\n"
        file_contents += f"save {' '.join(all_save_variables)}\n\n"
        
        file_contents += "** Write the header of the results file.\n"
        file_contents += f"echo \"{x_name},{','.join(all_output_variables)}\" > {results_file_path}\n\n"
        
        file_contents += "** Start the simulation loop.\n"
        file_contents += f"compose values_list start={curve['start']} stop={curve['stop']} step={curve['step']}\n"
        file_contents += "foreach val $&values_list\n"
        file_contents += "    alter v_sweep $val\n"
        file_contents += f"    ac lin 1 {curve['frequency']} {curve['frequency']}\n\n"
        
        if all_calculate_variables is not None:
            for key, value in all_calculate_variables.items():
                file_contents += f"    let {key} = {value}\n"
            file_contents += "\n"
            
        file_contents += f"    echo \"$val,{','.join(['$&' + var for var in all_output_variables])}\" >> {results_file_path}\n"
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
                                 'results_file_path': [results_file_path],
                                 'save_variables': [all_save_variables],
                                 'output_variables': [all_output_variables],
                                 'rename_variables': [all_rename_variables],
                                 'calculate_variables': [all_calculate_variables]})
        
        self.files = pd.concat([self.files, new_file])


    # Build file for ac_list simulations.
    def build_file_ac_point_dc_list(self, curves):
        file_id = curves.iloc[0]['file_id']
        simulation_type = curves.iloc[0]['simulation_type']
        x_name = curves.iloc[0]['x_name']
        y_name = curves.iloc[0]['y_name']
        values_list = ' '.join([str(val) for val in curves.iloc[0]['x_values']])
        results_dir = self.working_directory
        simulation_file_name = f'ac_point_dc_list_{file_id}.cir'
        simulation_file_path = os.path.join(results_dir, simulation_file_name)
        results_file_name = f'ac_point_dc_list_{file_id}.csv'
        results_file_path = os.path.join(results_dir, results_file_name)
        all_save_variables = list(set(sum(curves['save_variables'].tolist(), [])))
        all_output_variables = list(set(sum(curves['output_variables'].tolist(), [])))
        all_rename_variables =  None if curves['rename_variables'].isnull().all() else {k: v for var in curves['rename_variables'][curves['rename_variables'].notnull()] for k, v in var.items()}
        all_calculate_variables = None if curves['calculate_variables'].isnull().all() else {k: v for var in curves['calculate_variables'][curves['calculate_variables'].notnull()] for k, v in var.items()}

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
        
        file_contents += self.add_model_parameters_to_file()
        
        file_contents += "** Declare the vectors to save.\n"
        file_contents += f"save {' '.join(all_save_variables)}\n\n"
        
        file_contents += "** Write the header of the results file.\n"
        file_contents += f"echo \"{x_name},{','.join(all_output_variables)}\" > {results_file_path}\n\n"
        
        file_contents += "** Start the simulation loop.\n"
        file_contents += f"set values_list = ( {values_list} )\n"
        file_contents += "foreach val $values_list\n"
        file_contents += "    alter v_sweep $val\n"
        file_contents += f"    ac lin 1 {curve['frequency']} {curve['frequency']}\n\n"
        
        if all_calculate_variables is not None:
            for key, value in all_calculate_variables.items():
                file_contents += f"    let {key} = {value}\n"
            file_contents += "\n"
            
        file_contents += f"    echo \"$val,{','.join(['$&' + var for var in all_output_variables])}\" >> {results_file_path}\n"
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
                                 'results_file_path': [results_file_path],
                                 'save_variables': [all_save_variables],
                                 'output_variables': [all_output_variables],
                                 'rename_variables': [all_rename_variables],
                                 'calculate_variables': [all_calculate_variables]})
        
        self.files = pd.concat([self.files, new_file])
        
    
    def add_model_parameters_to_file(self):
        model_parameters_part = "** Model parameters start\n"
        
        if self.model_parameters is not None:
            for key, value in self.model_parameters.items():
                if value < 0:
                    model_parameters_part += f"alterparam {self.dut_name} {key} = 1*{value}\n"
                else:
                    model_parameters_part += f"alterparam {self.dut_name} {key} = {value}\n"
            model_parameters_part += "reset\n"
        
        model_parameters_part += "** Model parameters end\n\n"
        
        return model_parameters_part
    
    
    # Modify the model parameters that exist in the files
    def modify_model_parameters(self, parameters: dict = None, add_new_parameters: bool = True):
        self.model_parameters = parameters
        self.build_files()
        # self.files['contents'] = self.files.apply(lambda row: self.modify_model_parameters_per_file(row, parameters, add_new_parameters), axis = 1)
        
    
    # Modify the parameters in a single file
    def modify_model_parameters_per_file(self, file: pd.Series = None, parameters: dict = None, add_new_parameters: bool = True):
        contents = file['contents']
        
        for key, value in parameters.items():
            pattern = r'(alterparam dut ' + key + r' = )(.*?)(?=\n)'
            if re.search(pattern, contents):
                # Parameter exists, perform substitution
                def replace_value(match):
                    if value < 0:
                        return match.group(1) + '1*' + str(value)
                    else:
                        return match.group(1) + str(value)
               
                contents = re.sub(pattern, replace_value, contents, flags = re.DOTALL)

            else:
                if add_new_parameters:
                    # Parameter does not exist, add it after "** Model parameters start"
                    new_parameter = '** Model parameters start\n'
                    if value < 0:
                        new_parameter += f'alterparam dut {key} = 1*{value}\n'
                    else:
                        new_parameter += f'alterparam dut {key} = {value}\n'
                    contents = contents.replace('** Model parameters start\n', new_parameter)
            
        return contents
    
    
    # Remove model parameters
    def remove_model_parameters(self):
        self.files['contents'] = self.files.apply(lambda row: self.remove_model_parameters_per_file(row), axis = 1)

    
    # Remove model parameters per file
    def remove_model_parameters_per_file(self, file: pd.Series = None):
        contents = file['contents']
        contents = re.sub(r'\*\* Model parameters start\n.*?\*\* Model parameters end\n', '', contents, flags = re.DOTALL)
        return contents
    
    
    # Update working directory
    def update_working_directory(self, new_working_dir: str = None):
        self.working_directory = os.path.abspath(new_working_dir)
        self.build_files()
        
        
        
        
        
        
        
        
        
        
        
        