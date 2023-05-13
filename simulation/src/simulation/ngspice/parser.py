#%% Imports
import pandas as pd
import numpy as np
import re


# parse results
def parse_results(file_path: str = None, device: str = 'mosfet', simulation_type: str = 'output_characteristic'):
    results = None
    
    if device is not None and simulation_type is not None:
        function_name = f"parse_{device}_{simulation_type}"
        results = globals()[function_name](file_path = file_path)
    
    return results
    

# parse the output characteristic of a mosfet
def parse_mosfet_output_characteristic(file_path: str = None):
    with open(file_path, 'r') as f:
        lines = f.readlines()                                                       # read the eintire file
        temp = [re.sub(r'\s+', ';', line.strip()).split(';') for line in lines]     # transform the strings into lists
        
        # the first column is to be ignores because it is the repetition of some other column
        columns = temp[0][1:]                                                       # first line has the columns names
        data = np.array(temp[1:]).astype(float)[:,1:]                               # the other lines have the values
    
        results = pd.DataFrame(columns = columns, data = data)
        results.rename(columns = {'i(vs)': 'i_ds', 'v(d,s)': 'v_ds', 'v(g,s)': 'v_gs'}, inplace = True)
        
        return results
    
    return None

#
function_dict = {
    'parse_mosfet_output_characteristic': parse_mosfet_output_characteristic,
    }
        
        
        
        
        
        
        
        
        