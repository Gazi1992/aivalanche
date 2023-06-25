'''
Author: Gazmend Alia
Description: simulator class is used for simulating and extracting results in ngspice.
Inputs:
    file -> 

'''

#%% Imports
import pandas as pd
import numpy as np
import json
import os
from subprocess import Popen, PIPE, TimeoutExpired
import time
import shlex
from simulation.ngspice.parser import parse_results
from simulation.ngspice.visualization import plot_results
import shutil
from testbench.ngspice import Ngspice_testbench_compiler



#%% simulator class

class Ngspice_simulator:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout


    # Simulate one .cir file
    def simulate_single_file(self, file_path: str = None, results_dir: str = None, results_file_name: str = 'results.txt',
                             timeout: int = None, simulation_type: str = 'dc_sweep',
                             extract_results: bool = False, compact: bool = False, rename_variables: dict = None):
        if file_path is not None:
            
            file_name = os.path.basename(file_path)
            
            if results_dir is None:
                results_dir = os.path.dirname(file_path)
            
            # copy the file to the results directory, if not already there
            new_file_path = os.path.join(results_dir, file_name)
            if file_path != new_file_path:
                shutil.copy(file_path, new_file_path)
                
            if timeout is None:
                timeout = self.timeout
        
            command = f'ngspice -b {new_file_path}' # command that runs ngspice
            
            # start the simulation in a new subprocess
            try:
                process = Popen(shlex.split(command), stdout=PIPE, stderr=PIPE, cwd = results_dir)
            except FileNotFoundError:
                print(f'{file_path} not found')
            
            # poll the simulation status
            try:
                 start_time = time.time()
                 while time.time() - start_time <= timeout:
                     out, err = process.communicate()
                     exit_code = process.poll()
                     if exit_code is not None: # process ended
                         print(out.decode())
                         print(err.decode())
                         break
                 else:
                     raise TimeoutExpired(cmd = command, timeout = timeout)
            except KeyboardInterrupt:
                 print('Keyboard interrupt.')
                 process.terminate()
                 raise KeyboardInterrupt()
            except TimeoutExpired as e:
                 print('Ngspice simulation timeout.')
                 process.kill()
                 raise e
            
            # parse the results file
            if extract_results:
                results_file_path = os.path.join(results_dir, results_file_name)
                results = parse_results(file_path = results_file_path, simulation_type = simulation_type,
                                        compact = compact, rename_variables = rename_variables)
                
                # plot the results
                # if plot:
                #     plot_results(device = device, simulation_type = simulation_type, data = results)
                
                return results
                
            return None


    def simulate_testbenches(self, testbenches: Ngspice_testbench_compiler = None, timeout: int = None,
                             extract_results: bool = False, compact: bool = False, rename_variables: dict = None,
                             reference_data: pd.DataFrame = None, delete_files: bool = True, print_output: bool = True):
        if testbenches is not None:
            testbenches.write_simulation_files()
            results = self.simulate_multiple_files(files = testbenches.files, timeout = timeout,
                                                   extract_results = extract_results, compact = compact, rename_variables = rename_variables,
                                                   reference_data = reference_data, delete_files = delete_files, print_output = print_output)
            if reference_data is not None:
                results = self.combine_simulation_with_reference_data(reference_data = reference_data, simulation_results = results)
            return results
        return None


    '''
    This will simulate all the files provided in the files dataframe. It should have the following columns:
        simulation_type, simulation_file_path, simulation_file_name, results_dir
    '''
    def simulate_multiple_files(self, files: pd.DataFrame = None, timeout: int = None,
                                extract_results: bool = False, compact: bool = False, rename_variables: dict = None,
                                reference_data: pd.DataFrame = None, delete_files: bool = True, print_output: bool = True):
        
        results = None
        
        if files is not None:
            
            if timeout is None:
                timeout = self.timeout
            
            # Start all the simulation processes
            all_processes = []
            for index, file in files.iterrows():
                               
                # copy the file to the results directory, if not already there
                new_file_path = os.path.join(file['results_dir'], file['simulation_file_name'])
                if file['simulation_file_path'] != new_file_path:
                    shutil.copy(file['simulation_file_path'], new_file_path)
            
                command = f'ngspice -b {new_file_path}' # command that runs ngspice
                
                # start the simulation in a new subprocess
                try:
                    process = Popen(shlex.split(command), stdout = PIPE, stderr = PIPE, cwd = file['results_dir'])
                    all_processes.append(process)
                except FileNotFoundError:
                    print(f'{new_file_path} not found')

            # Monitor the simulation processes
            try:
                start_time = time.time()
                while time.time() - start_time <= timeout:
                    exit_codes = [process.poll() for process in all_processes]
                    if not any([exit_code is None for exit_code in exit_codes]):
                        break # all simulations finished succesfully
                else:
                    raise TimeoutExpired(cmd = command, timeout = timeout)
                
                if print_output:
                    for index, exit_code in enumerate(exit_codes):
                        if exit_code is not None: # process ended
                            out, err = all_processes[index].communicate()
                            print(out.decode())
                            print(err.decode())
                        
            except KeyboardInterrupt:
                 print('Keyboard interrupt.')
                 [process.terminate() for process in all_processes]
                 raise KeyboardInterrupt()
            except TimeoutExpired as e:
                 print('Ngspice simulation timeout.')
                 [process.kill() for process in all_processes]
                 # raise e
                 pass
        
        # parse the results file
        if extract_results:
            results = []
            for index, file in files.iterrows():
                rename_variables = file['rename_variables'] if 'rename_variables' in file else rename_variables
                temp_results = parse_results(file_path = file['results_file_path'],
                                             simulation_type = file['simulation_type'],
                                             compact = compact,
                                             rename_variables = rename_variables,
                                             x_name = file['x_name'] if reference_data is not None else None,
                                             y_name = file['y_name'] if reference_data is not None else None)                    
                
                results.append(temp_results)
                    
        # Delete the results files
        if delete_files:
            all_dirs = set(files['results_dir'])
            for directory in all_dirs:
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('Failed to delete %s. Reason: %s' % (file_path, e))

        return results


    def combine_simulation_with_reference_data(self, reference_data: pd.DataFrame = None, simulation_results: list[pd.DataFrame] = None):
        reference_data = reference_data.copy()
        reference_data['x_values_simulation'] = None
        reference_data['y_values_simulation'] = None
        
        combined_results = pd.concat(simulation_results)
        
        reference_data.set_index('curve_index', inplace = True)
        reference_data['x_values_simulation'] = combined_results['x_values']
        reference_data['y_values_simulation'] = combined_results['y_values']
        
        reference_data.reset_index(inplace = True)
        
        # Check the simulation validity
        reference_data[['simulation_status', 'simulation_status_message']] = reference_data.apply(lambda row: self.check_simulation_validity(row), axis=1, result_type = 'expand')

        return reference_data
        
        
    def check_simulation_validity(self, row):
        status = 'success'
        message = 'success'
        if len(row['y_values']) != len(row['y_values_simulation']):
            status = 'failed'
            message = 'simulation data not the same length as reference data'
        elif all(np.isnan(row['y_values_simulation'])):
            status = 'failed'
            message = 'all simulation data is NaN'
        elif any(np.isnan(row['y_values_simulation'])):
            status = 'failed'
            message = 'at least one value in simulation data is NaN'
        
        return status, message
    
        
        
        
        