'''
Author: Gazmend Alia
Description: parser class is used for reading the parameters file.
Inputs:
    file -> 

'''

#%% Imports
import pandas as pd
import numpy as np
import json


#%% differential_evolution class

class parser:
    def __init__(self,
                 file: str = None, # the path of the reference data file
               ):
        
        self.file = file
        self.parameters = pd.DataFrame()
        self.error_parsing = None
        
        self.parse_file()
            
    @property
    def fixed_parameters(self):
        return self.parameters[self.parameters['mode'] == 'fixed']

    @property
    def variable_parameters(self):
        return self.parameters[self.parameters['mode'] == 'variable']
    
    @property
    def nr_parameters(self):
        return len(self.parameters.index)
    
    # Set file and parse the file
    def set_file(self, file: str = None):
        self.file = file
        self.parse_file()
        
        
    # Parse the file and save the data into the respective dataframes
    def parse_file(self):
        if self.file is not None:
            if self.file.split('.')[-1] == 'json':
                self.parse_json()
            elif self.file.split('.')[-1] == 'csv':
                self.parse_csv()
    

    # Convert json file to pandas dataframe
    def parse_json(self):
        with open(self.file) as json_file:
            self.raw_data = json.load(json_file)           
            
            self.parameters = pd.DataFrame.from_dict(self.raw_data)
            
            if 'scale' not in self.parameters.columns:
                self.parameters['scale'] = 'lin'
            
            if 'mode' not in self.parameters.columns:
                self.parameters['mode'] = 'variable'
    
    
    # Convert csv file to pandas dataframe
    def parse_csv(self):
        self.raw_data = pd.read_csv(filepath_or_buffer = self.file, comment = '#') 
        self.parameters = self.raw_data
        
        if 'scale' not in self.parameters.columns:
            self.parameters['scale'] = 'lin'
        
        if 'mode' not in self.parameters.columns:
            self.parameters['mode'] = 'variable'        
        
        
        
        
        
        
        
        
        
        
        
        
        