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
import subprocess
import time
import shlex
from simulation.ngspice.parser import parse_results
from simulation.ngspice.visualization import plot_results
import shutil


#%% simulator class

class simulator:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
        
    # Simulate one .cir file
    def simulate_single_file(self, file_path: str = None, results_dir: str = None, timeout: int = None,
                             device: str = 'mosfet', simulation_type: str = 'output_characteristic',
                             extract_results: bool = False, plot: bool = False):
        if file_path is not None:
            
            file_name = os.path.basename(file_path)
            
            if results_dir is None:
                results_dir = os.path.dirname(file_path)
            
            # copy the file to the results directory
            new_file_path = os.path.join(results_dir, file_name)
            if file_path != new_file_path:
                shutil.copy(file_path, new_file_path)
                
            if timeout is None:
                timeout = self.timeout
        
            command = f'ngspice {new_file_path}' # command that runs ngspice
            
            # start the simulation in a new subprocess
            try:
                process = subprocess.Popen(shlex.split(command), stdout = subprocess.DEVNULL, cwd = results_dir)
            except FileNotFoundError:
                print(f'{file_path} not found')
            
            # poll the simulation status
            try:
                 start_time = time.time()
                 while time.time() - start_time <= timeout:
                     exit_code = process.poll()
                     if exit_code is not None: # process ended
                         break
                 else:
                     raise subprocess.TimeoutExpired(cmd = command, timeout = timeout)
            except KeyboardInterrupt:
                 print('Keyboard interrupt.')
                 process.terminate()
                 raise KeyboardInterrupt()
            except subprocess.TimeoutExpired as e:
                 print('Ngspice simulation timeout.')
                 process.kill()
                 raise e
            
            # parse the results file
            if extract_results:
                results_file_path = os.path.join(results_dir, 'results.txt')
                results = parse_results(file_path = results_file_path, device = device, simulation_type = simulation_type)
                
                # plot the results
                if plot:
                    plot_results(device = device, simulation_type = simulation_type, data = results)
                
                return results
                
            return None
                    
            

    def simulate_multiple_files(self, files_paths: list[str] = None):
        print()
      
        # sim_processes = []
        # for runfile_fname in runfile_fnames:
        #     if platform.system() == 'Windows':
        #         executable = 'titan.bat'
        #     else:
        #         executable = 'titan'
        #         titan_args += ' -keepdata' if self.log_warnings or self.log_errors else ''
        #         titan_args += ' -toolarch clang' 
        #         titan_args += ' -local' if self.local else ' -info wait' 
        #     command = f'{executable} {titan_args} {str(runfile_fname)}'

        #     try:
        #         log.debug("Running " + command)
        #         process = subprocess.Popen(shlex.split(command), stdout=subprocess.DEVNULL, cwd=self.working_dir)
        #         sim_processes.append(process)
        #     except FileNotFoundError:
        #         raise TitanNotFound(
        #             "Titan can't be found. If you're on a Linux R&D server, you need to `module load titan`? " +
        #             "If you're on Windows, you need to install IFXspice via Inicio and set some env variables.")
        # try:
        #     start_time = time.time()
        #     while self.timeout is None or time.time() - start_time <= self.timeout:
        #         exit_codes = [p.poll() for p in sim_processes]
        #         if not any([c is None for c in exit_codes]):
        #             # all processes returned
        #             break
        #     else:
        #         raise subprocess.TimeoutExpired(cmd=command, timeout=self.timeout)
        # except KeyboardInterrupt:
        #     print("Interrupting Titan. Press Ctrl+C to exit right away")
        #     [p.terminate() for p in sim_processes]
        #     raise KeyboardInterrupt()
        # except subprocess.TimeoutExpired as e:
        #     log.warning('Titan jobs took longer than timeout. Killing remaining proccesses')
        #     [p.kill() for p in sim_processes]
        #     raise e
        
        
        
        
        
        
        
        
        
        
        
        