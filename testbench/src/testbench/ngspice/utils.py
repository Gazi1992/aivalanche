#%% Imports
import pandas as pd
import numpy as np
import json


# Chech if an array data are equally distant from each other 
def is_equidistant(arr):
    diff = np.diff(arr)  # Calculate the differences between consecutive elements
    return np.allclose(diff, diff[0])


# Combine the group_id and curve_id to create a unique index for each curve
def get_curve_index(curve):
    return f"{curve['group_id']}_{curve['curve_id']}"


# Determine the instance parameters for a given curve and testbench
def get_instance_parameters_for_curve(testbench, curve):
    instance_parameter_names = testbench['instance_parameters']
    instance_parameters = {}
    for param in instance_parameter_names:
        if param in curve:
            instance_parameters[param] = curve[param]
    return instance_parameters


#
def write_contents_to_file(file):
    with open(file['simulation_file_path'], 'w') as f:
        f.write(file['contents'])