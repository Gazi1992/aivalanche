#%% Imports
import pandas as pd
import numpy as np
from copy import deepcopy
from cost_function.utils import calculate_error_metric
from cost_function.exceptions import raise_exception


#%% calibration class

class Cost_function:
    def __init__(self,
                 parts: list[str] = None,
                 ):
                
        self.parts = parts
        self.validate_parts()
        
        
    def validate_parts(self):
        if self.parts is None:
            raise parts_missing('ERROR! Parts are missing. You need to provide a list of dicts, where each dict needs to have an id, group_types and metric_type.')


    # Reset the error metric dictionary
    def reset_error_metric(self):
        self.error_metric = {}
        for part in self.parts:
            self.error_metric[part['id']] = None
        self.error_metric['total'] = None
        
    
    # Calculate the error metric
    def run(self, data: pd.DataFrame = None, parameters: pd.DataFrame = None, overwrite: bool = False):
        # If no data is given, return HUGE_ERROR
        if data is None:
            error_metric = raise_exception('no_data_exception')
            if overwrite:
                self.error_metric['total'] = error_metric
            return error_metric
        
        # initialize error_metric
        error_metric = {}
        for part in self.parts:
            error_metric[part['id']] = None
        error_metric['total'] = None
        
        # Copy the data to not modify the original dataframe
        data_ = data.copy()
        data_['x_values'] = data_['x_values'].apply(lambda x: np.array(x)) # Convert the x_values np arrays
        data_['y_values'] = data_['y_values'].apply(lambda x: np.array(x)) # Convert the x_values np arrays
        data_['x_values_simulation'] = data_['x_values_simulation'].apply(lambda x: np.array(x)) # Convert the x_values np arrays
        data_['y_values_simulation'] = data_['y_values_simulation'].apply(lambda x: np.array(x)) # Convert the x_values np arrays

        
        # Calculate the error_metric for each part
        for part in self.parts:                
            part_error_metric = calculate_error_metric(data = data_,
                                                       parameters = parameters,
                                                       group_types = part['group_types'],
                                                       metric_type = part['metric_type'],
                                                       weight = part['weight'],
                                                       norm = part['norm'],
                                                       transform = part['transform'],
                                                       **part['extra_args'])
            error_metric[part['id']] = part_error_metric
            if error_metric['total'] is None:
                error_metric['total'] = part_error_metric
            else:
                error_metric['total'] += part_error_metric
        
        if overwrite:
            self.error_metric = error_metric
            self.data = data_
        
        return {'data': data, 'parameters': parameters, 'error_metric': error_metric}


#%% custom exception class for missing optimizer
class parts_missing(Exception):
    def __init__(self, message):
        print(message)