#%% Imports
import pandas as pd
import numpy as np
import re


# parse results
def parse_results(file_path: str = None, simulation_type: str = 'dc_sweep', x_name: str = None, y_name: str = None):
    results = None
    
    if simulation_type is not None:
        function_name = f"parse_{simulation_type}"
        results = globals()[function_name](file_path = file_path)
        if x_name is not None:
            results[1].rename(columns = {x_name: 'x_values'}, inplace = True)
        if y_name is not None:
            results[1].rename(columns = {y_name: 'y_values'}, inplace = True)
    
    return results
    

# parse dc_sweep results file
def parse_dc_sweep(file_path: str = None):
    with open(file_path, 'r') as f:
        lines = f.readlines()                                                       # read the eintire file
        temp = [re.sub(r'\s+', ';', line.strip()).split(';') for line in lines]     # transform the strings into lists
        
        # the first column is to be ignores because it is the repetition of some other column
        columns = temp[0][1:]                                                       # first line has the columns names
        data = np.array(temp[1:]).astype(float)[:,1:]                               # the other lines have the values
        
        # save all the data
        results_extended = pd.DataFrame(columns = columns, data = data)
        results_compact = convert_extended_results_to_compact(results_extended)     
        
        return results_extended, results_compact
    
    return None


# parse dc_list results file
def parse_dc_list(file_path: str = None):
    try:
        results_extended = pd.read_csv(filepath_or_buffer = file_path)
        results_compact = convert_extended_results_to_compact(results_extended)             
        return results_extended, results_compact
    except Exception as e:
        print('Error reading dc_list results file.')
        print(e)
        return None


def convert_extended_results_to_compact(results_extended: pd.DataFrame = None):
    results_compact = None
    
    try:
        if results_extended is not None:
            results_extended_columns = results_extended.columns
            
            indices = list(set([col.split('_', 1)[1] for col in results_extended_columns]))
            indices.sort()
            
            results_compact_columns = list(set([col.split('_', 1)[0] for col in results_extended_columns]))
            results_compact_columns.sort()
            
            results_compact = pd.DataFrame(columns = results_compact_columns)
            for i in indices:
                data = results_extended[[col for col in results_extended_columns if i in col]].sort_index(axis = 1)
                data = np.array(data).T.tolist()
                data = [item[0] if check_same_value(item) else item for item in data]
                temp = pd.DataFrame(columns = results_compact_columns, data = [data])
                temp.index = [i]
                results_compact = pd.concat([results_compact, temp])
    except Exception as e:
        print('Error converting results into compact form!')
        print(e)
        
    return results_compact    


def check_same_value(arr):
    return np.all(np.equal(arr, arr[0]))
        
        
        