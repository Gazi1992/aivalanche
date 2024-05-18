'''
Author: Gazmend Alia
Description: parser class is used for reading the parameters file.
Inputs:
    file -> 

'''

#%% Imports
import pandas as pd, json, random

#%% differential_evolution class

class Parameters:
    def __init__(self,
                 file: str = None, # the path of the reference data file
               ):
        
        self.file = file
        self.all_parameters = pd.DataFrame()
        self.error_parsing = None
        
        self.parse_file()
            
    @property
    def fixed_parameters(self):
        return self.all_parameters[self.all_parameters['mode'] == 'fixed']

    @property
    def variable_parameters(self):
        return self.all_parameters[self.all_parameters['mode'] == 'variable']
    
    @property
    def nr_parameters(self):
        return len(self.all_parameters.index)
    
    
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
            self.all_parameters = pd.DataFrame.from_dict(self.raw_data)
            
            if 'scale' not in self.all_parameters.columns:
                self.all_parameters['scale'] = 'lin'
            
            if 'mode' not in self.all_parameters.columns:
                self.all_parameters['mode'] = 'variable'
                
            
    # Convert csv file to pandas dataframe
    def parse_csv(self):
        self.raw_data = pd.read_csv(filepath_or_buffer = self.file, comment = '#') 
        self.all_parameters = self.raw_data
        
        if 'scale' not in self.all_parameters.columns:
            self.all_parameters['scale'] = 'lin'
        
        if 'mode' not in self.all_parameters.columns:
            self.all_parameters['mode'] = 'variable'

    # Generate random parameters
    def generate_random_parameters(self):
        return self.all_parameters.set_index('name').apply(self.generate_random_number, axis=1).to_dict()
        
    # Get default parameters
    def get_default_parameters(self):
        return self.all_parameters.set_index('name')['default'].to_dict()
    
    # Generate a random number
    def generate_random_number(self, row):
        if row['mode'] == 'fixed':
            return row['default']
        else:
            return random.uniform(row['min'], row['max'])

    # Write parameters to file
    def write_parameters_to_file(self, file_path: str = None):
        if self.file.split('.')[-1] == 'json':
            self.all_parameters.to_json(path_or_buf = file_path, orient = 'records')
        elif self.file.split('.')[-1] == 'csv':
            self.all_parameters.to_csv(path_or_buf = file_path, index = False)