'''
Author: Gazmend Alia
Description: parser class is used for reading the reference data file.
Inputs:
    file -> 

'''

#%% Imports
import pandas as pd
import numpy as np
import json


#%% differential_evolution class

class Reference_data:
    def __init__(self,
                 file: str = None, # the path of the reference data file
               ):
        
        self.file = file
        self.groups = pd.DataFrame()
        self.curves = pd.DataFrame()
        self.data = pd.DataFrame()
        self.error_parsing = None
        
        self.parse_file()
            
    @property
    def group_columns(self):
        return self.groups.columns.tolist()

    @property
    def curve_columns(self):
        return self.curves.columns.tolist()
        
    @property
    def data_columns(self):
        return self.data.columns.tolist()    
    
    @property
    def nr_groups(self):
        return len(self.groups.index)
    
    @property
    def nr_curves(self):
        return len(self.curves.index)
    
    # Set file and parse the file
    def set_file(self, file: str = None):
        self.file = file
        self.parse_file()
        
        
    # Parse the file and save the data into the respective dataframes
    def parse_file(self):
        if self.file is not None:
            if self.file.split('.')[-1] == 'json':
                self.parse_json()
    

    # Convert json file to pandas dataframe
    def parse_json(self):
        with open(self.file) as json_file:
            self.raw_data = json.load(json_file)           
            group_info = []
            curve_info = []
            for group_idx, group in enumerate(self.raw_data['data']):
                self.validate_group(group)
                
                temp_group_dict = {
                        'group_id': group_idx,
                        'group_type': group['group_type'],
                        'group_name': group['group_name'],
                        'testbench_type': group['testbench_type'] if 'testbench_type' in group else group['group_type'],
                        'x_name': group['x_name'],
                        'y_name': group['y_name'],
                        'extra_var_name': group['extra_var_name'] if 'extra_var_name' in group else np.nan,
                        'group_weight': group['group_weight'] if 'group_weight' in group else 1
                }
                
                if 'operating_conditions' in group:
                    for key, val in group['operating_conditions'].items():
                        temp_group_dict[key] = val
                
                if 'instance_parameters' in group:
                    for key, val in group['instance_parameters'].items():
                        temp_group_dict[key] = val
                    
                group_info.append(temp_group_dict)
                
                # get the data for each curve of the group
                for curve_idx, curve in enumerate(group['curves']):
                    self.validate_curve(curve)

                    # Zip the x and y values
                    combined = list(zip(curve['x_values'], curve['y_values']))
                    
                    # Sort the combined list based on the values in x
                    sorted_combined = sorted(combined, key = lambda x: x[0])
                    
                    # Unzip the sorted list to retrieve the ordered A and B
                    sorted_x, sorted_y = zip(*sorted_combined)
                    
                    temp_curve_dict = {
                        'group_id': group_idx,
                        'curve_id': curve_idx,
                        'x_values': np.array(sorted_x),
                        'y_values': np.array(sorted_y),
                        'extra_var_value': curve['extra_var_value'] if 'extra_var_value' in curve else np.nan,
                        'curve_weight': curve['curve_weight'] if 'curve_weight' in curve else 1,
                        'curve_length': len(sorted_y)
                    }
                    
                    
                    if 'temp' not in temp_group_dict:
                        if temp_group_dict['extra_var_name'] == 'temp':
                            temp_curve_dict['temp'] = temp_curve_dict['extra_var_value']
                    
                    curve_info.append(temp_curve_dict)
                    
            self.groups = pd.DataFrame.from_dict(data = group_info)
            self.curves = pd.DataFrame.from_dict(data = curve_info)
            self.data = pd.merge(left = self.groups, right = self.curves, on = 'group_id')

        
    # validate that a group has the necessary elements    
    def validate_group(self, group):
        keys = group.keys()
        if 'group_type' not in keys:
            self.error_parsing = "\nError parsing reference data.\n"
            self.error_parsing += "Each group has to have group_type.\n"
            self.error_parsing += f"Error happened at group: {group}.\n"
        elif 'group_name' not in keys:
            self.error_parsing = "\nError parsing reference data.\n"
            self.error_parsing += "Each group has to have group_name.\n"
            self.error_parsing += f"Error happened at group: {group}.\n"
        elif 'x_name' not in keys:
            self.error_parsing = "\nError parsing reference data.\n"
            self.error_parsing += "Each group has to have x_name.\n"
            self.error_parsing += f"Error happened at group: {group}.\n"    
        elif 'y_name' not in keys:
            self.error_parsing = "\nError parsing reference data.\n"
            self.error_parsing += "Each group has to have y_name.\n"
            self.error_parsing += f"Error happened at group: {group}.\n"
        if self.error_parsing is not None:
            raise key_missing_exception(self.error_parsing)
        
        
    # validate that a curve has the necessary elements    
    def validate_curve(self, curve):
        keys = curve.keys()
        if 'x_values' not in keys:
            self.error_parsing = "\nError parsing reference data.\n"
            self.error_parsing += "Each curve has to have x_values.\n"
            self.error_parsing += f"Error happened at curve: {curve}.\n"
        elif 'y_values' not in keys:
            self.error_parsing = "\nError parsing reference data.\n"
            self.error_parsing += "Each curve has to have y_values.\n"
            self.error_parsing += f"Error happened at curve: {curve}.\n"

            
        if self.error_parsing is not None:
            raise key_missing_exception(self.error_parsing)


# custom exception class for missing key
class key_missing_exception(Exception):
    def __init__(self, message):
        print(message)

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
