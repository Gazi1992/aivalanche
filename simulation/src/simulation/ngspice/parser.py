#%% Imports
import pandas as pd
import numpy as np
import re


# parse results
def parse_results(file_path: str = None, simulation_type: str = 'dc_sweep', compact: bool = False,
                  rename_variables: dict = None, x_name: str = None, y_name: str = None):
    results = None
    
    if simulation_type is not None:
        function_name = f"parse_{simulation_type}"
        results = globals()[function_name](file_path = file_path, rename_variables = rename_variables, compact = compact)
        if results is not None:
            if compact:
                if x_name is not None:
                    results.rename(columns = {x_name: 'x_values'}, inplace = True)
                if y_name is not None:
                    results.rename(columns = {y_name: 'y_values'}, inplace = True)
    
    return results
    

# parse dc_sweep results file
def parse_dc_sweep(file_path: str = None, compact: bool = False, rename_variables: dict = None):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()                                                       # read the entire file
            temp = [re.sub(r'\s+', ';', line.strip()).split(';') for line in lines]     # transform the strings into lists
            
            # the first column is to be ignores because it is the repetition of some other column
            columns = temp[0][1:]                                                       # first line has the columns names
            data = np.array(temp[1:]).astype(float)[:,1:]                               # the other lines have the values
            # data = np.where(data == 'NAN', np.nan, data)                                # replace NAN whith numpy.nan
            
            # save all the data
            results_extended = pd.DataFrame(columns = columns, data = data)
    
            if rename_variables is not None:
                results_extended.rename(columns = rename_variables, inplace = True)
    
            if compact:
                results_compact = convert_extended_results_to_compact(results_extended)     
                return results_compact
    
            return results_extended        
        return None
    except FileNotFoundError:
        print(f'Error! Results file {file_path} has not been generated.')
        print('Returning None.')
        return None


# parse dc_list results file
def parse_dc_list(file_path: str = None, compact: bool = False, rename_variables: dict = None):
    try:
        results_extended = pd.read_csv(filepath_or_buffer = file_path, na_values = 'NAN')
        if rename_variables is not None:
            results_extended.rename(columns = rename_variables, inplace = True)
        
        if compact:
            results_compact = convert_extended_results_to_compact(results_extended)     
            return results_compact

        return results_extended
    except Exception as e:
        print('Error reading dc_list results file.')
        print(e)
        return None


# parse ac_sweep results file
def parse_ac_point_dc_sweep(file_path: str = None, compact: bool = False, rename_variables: dict = None):
    return parse_ac_point(file_path = file_path, compact = compact, rename_variables = rename_variables)


# parse ac_list results file
def parse_ac_point_dc_list(file_path: str = None, compact: bool = False, rename_variables: dict = None):
    return parse_ac_point(file_path = file_path, compact = compact, rename_variables = rename_variables)

    
# parse ac results file
def parse_ac_point(file_path: str = None, compact: bool = False, rename_variables: dict = None):
    try:
        results_extended = pd.read_csv(filepath_or_buffer = file_path, na_values = 'NAN')
        if rename_variables is not None:
            results_extended.rename(columns = rename_variables, inplace = True)
        
        if compact:
            results_compact = convert_extended_results_to_compact(results_extended)     
            return results_compact

        return results_extended
    except Exception as e:
        print('Error reading ac_sweep results file.')
        print(e)
        return None


def convert_extended_results_to_compact(results_extended: pd.DataFrame = None):
    results_compact = None
    
    try:
        if results_extended is not None:
            results_extended_columns = results_extended.columns
            
            # the columns that do not contain '_' are in common for all the curves
            common_columns = [col for col in results_extended_columns if '_' not in col]

            # the columns that contain '_' are in separate for each curves
            separate_columns = [col for col in results_extended_columns if '_' in col]
            
            # get the common part of the separate columns
            indices = list(set([col.split('_', 1)[1] for col in separate_columns]))
            indices.sort()
            
            # build the results_compact considering first only the separate_columns
            results_compact_columns = list(set([col.split('_', 1)[0] for col in separate_columns]))
            results_compact_columns.sort()
            
            results_compact = pd.DataFrame(columns = results_compact_columns)
            for i in indices:
                data = results_extended[[col for col in separate_columns if i in col]].sort_index(axis = 1)
                data = np.array(data).T.tolist()
                # data = [item[0] if check_same_value(item) else item for item in data]
                temp = pd.DataFrame(columns = results_compact_columns, data = [data])
                temp.index = [i]
                results_compact = pd.concat([results_compact, temp])
                
            # now add the common columns
            for col in common_columns:
                data = np.array(results_extended[col]).tolist()
                data = [data for _ in range(len(results_compact))]
                results_compact[col] = data         
            
    except Exception as e:
        print('Error converting results into compact form!')
        print(e)
        
    return results_compact    


def check_same_value(arr):
    return np.all(np.equal(arr, arr[0]))
        
        
        