#%% Imports
import pandas as pd
import numpy as np
import re


# parse results
def parse_results(file_path: str = None, device: str = 'mosfet', characteristic_type: str = 'output_characteristic'):
    results = None
    
    if device is not None and characteristic_type is not None:
        function_name = f"parse_{device}_{characteristic_type}"
        results = globals()[function_name](file_path = file_path)
    
    return results
    

# parse the output characteristic of a mosfet
def parse_mosfet_output_characteristic(file_path: str = None):    
    return parse_dc_sweep(file_path = file_path)


# parse the output characteristic of a mosfet
def parse_mosfet_transfer_characteristic(file_path: str = None):    
    return parse_dc_sweep(file_path = file_path)


# parse the diode characteristic
def parse_diode_dc_characteristic(file_path: str = None):    
    return parse_dc_sweep(file_path = file_path)


# parse the output and transfer characteristic of a mosfet
def parse_dc_sweep(file_path: str = None):
    with open(file_path, 'r') as f:
        lines = f.readlines()                                                       # read the eintire file
        temp = [re.sub(r'\s+', ';', line.strip()).split(';') for line in lines]     # transform the strings into lists
        
        # the first column is to be ignores because it is the repetition of some other column
        columns = temp[0][1:]                                                       # first line has the columns names
        data = np.array(temp[1:]).astype(float)[:,1:]                               # the other lines have the values
        
        # save all the data into 
        results_extended = pd.DataFrame(columns = columns, data = data)
        
        results_compact = convert_extended_results_to_compact(results_extended)     
        return results_compact
    
    return None


def convert_extended_results_to_compact(results_extended: pd.DataFrame = None):
    results_compact = None
    
    if results_extended is not None:
        results_extended_columns = results_extended.columns
        
        # get the indices of the 
        indices = list(set([re.search(r'\d+', col).group() for col in results_extended_columns]))
        
        pattern = r'_(\d+)' # Regular expression pattern
        replacement = '' # Replacement string
        results_compact_columns = list(set([re.sub(pattern, replacement, col) for col in results_extended_columns]))
        results_compact_columns.sort()
        
        results_compact = pd.DataFrame(columns = results_compact_columns)
        for i in indices:
            data = results_extended[[col for col in results_extended_columns if i in col]].sort_index(axis = 1)
            data = np.array(data).T.tolist()
            data = [item[0] if check_same_value(item) else item for item in data]
            temp = pd.DataFrame(columns = results_compact_columns, data = [data])
            results_compact = pd.concat([results_compact, temp])
            
    return results_compact    


def check_same_value(arr):
    return np.all(np.equal(arr, arr[0]))
        
        
        