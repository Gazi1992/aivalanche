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
                             timeout: int = None, simulation_type: str = 'dc_sweep', extract_results: bool = False):
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
                results = parse_results(file_path = results_file_path, simulation_type = simulation_type)
                
                # plot the results
                # if plot:
                #     plot_results(device = device, simulation_type = simulation_type, data = results)
                
                return results
                
            return None
        
        
    def simulate_testbenches(self, testbenches: Ngspice_testbench_compiler = None, timeout: int = None, extract_results: bool = False, reference_data: pd.DataFrame = None):
        if testbenches is not None:
            testbenches.write_simulation_files()
            results = self.simulate_multiple_files(files = testbenches.files,
                                                   timeout = timeout,
                                                   extract_results = extract_results,
                                                   reference_data = reference_data)
            if reference_data is not None:
                results = self.combine_simulation_with_reference_data(reference_data = reference_data, simulation_results = results)
            return results
        return None
                    
            
    '''
    This will simulate all the files provided in the files dataframe. It should have the following columns:
        simulation_type, simulation_file_path, simulation_file_name, results_dir
    '''
    def simulate_multiple_files(self, files: pd.DataFrame = None, timeout: int = None, extract_results: bool = False, reference_data: pd.DataFrame = None):
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
                 raise e
        
        # parse the results file
        if extract_results:
            results = []
            for index, file in files.iterrows():
                temp_results_extended, temp_results_compact = parse_results(file_path = file['results_file_path'],
                                                                            simulation_type = file['simulation_type'],
                                                                            x_name = file['x_name'] if reference_data is not None else None,
                                                                            y_name = file['y_name'] if reference_data is not None else None)
                results.append(temp_results_compact)
            
            return results
            
        return None
        
        
    def combine_simulation_with_reference_data(self, reference_data: pd.DataFrame = None, simulation_results: list[pd.DataFrame] = None):
        reference_data = reference_data.copy()
        reference_data['x_values_simulation'] = None
        reference_data['y_values_simulation'] = None
        
        combined_results = pd.concat(simulation_results)
        
        reference_data.set_index('curve_index', inplace = True)
        reference_data['x_values_simulation'] = combined_results['x_values']
        reference_data['y_values_simulation'] = combined_results['y_values']
        
        reference_data.reset_index(inplace = True)
          
        return reference_data
        
        
        
        
        
        
        