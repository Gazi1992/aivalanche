#%% Imports
import numpy as np
import re, os


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


# Write the contents to a file
def write_contents_to_file(file):
    with open(file['simulation_file_path'], 'w') as f:
        f.write(file['contents'])
        

def extract_between_tags(string):
    pattern = r"<<(.*?)>>"
    matches = re.findall(pattern, string)
    return matches

# process include lines in order to write the contents of the file directly
# into the netlist in case of include statements
def process_file_contents_for_inline_includes(file_contents):
    processed_files = set()
    
    modified_file_content = []
    for line in file_contents.splitlines():
        modified_file_content.extend(process_include_line(line, processed_files))
        
    modified_file_content = '\n'.join(modified_file_content)

    return modified_file_content

def process_include_line(line, processed_files, base_path = '.'):
    match = re.match(r'^\s*\.include\s+(.+)$', line, re.IGNORECASE)
    if match:
        filepath = match.group(1)
        
        # Construct the absolute path for the included file
        absolute_path = os.path.join(base_path, filepath)

        # Check if the file has already been processed to avoid infinite recursion
        if absolute_path in processed_files:
            return [line]

        processed_files.add(absolute_path)

        # Read the contents of the included file and process its content recursively
        with open(filepath, 'r') as file:
            included_content = file.readlines()

        processed_content = []
        for included_line in included_content:
            processed_content.extend(process_include_line(included_line, processed_files, os.path.dirname(absolute_path)))

        return processed_content
    else:
        return [line]
    