# Imports
import json, re, pandas as pd
from reference_data import Reference_data


# Write dataframe to file
def write_reference_data_to_file(data: pd.DataFrame = None, file_path: str = None,
                                 title: str = '', description: str = '', device_type: str = '',
                                 x_values: str = 'x_values', y_values: str = 'y_values',
                                 include_simulation: bool = False, x_values_simulation: str = 'x_values_simulation', y_values_simulation: str = 'y_values_simulation',
                                 operating_conditions: list[str] = None, instance_parameters: list[str] = None):
    
    if isinstance(data, Reference_data):
        processed_data = json.dumps(data.raw_data, indent = 4)
    elif isinstance(data, pd.DataFrame):
        processed_data = {
            'title': title,
            'description': description,
            'device_type': device_type,
            'data': []}
        
        groups = data.groupby('group_id')
        
        for group_id, group in groups:        
            group_dict = {'group_type': group.iloc[0]['group_type'],
                          'group_name': group.iloc[0]['group_name'],
                          'testbench_type': group.iloc[0]['testbench_type'],
                          'x_name': group.iloc[0]['x_name'],
                          'y_name': group.iloc[0]['y_name'],
                          'group_weight': float(group.iloc[0]['group_weight']),
                          'operating_conditions': {},
                          'instance_parameters': {},
                          'curves': []}
            
            if not pd.isnull(group.iloc[0]['extra_var_name']):
                group_dict['extra_var_name'] = group.iloc[0]['extra_var_name']
                
            if operating_conditions is not None:
                for o_c in operating_conditions:
                    if o_c in group.columns and not pd.isnull(group.iloc[0][o_c]):
                        group_dict['operating_conditions'][o_c] = float(group.iloc[0][o_c])
            
            if instance_parameters is not None:
                for i_p in instance_parameters:
                    if i_p in group.columns and not pd.isnull(group.iloc[0][i_p]):
                        group_dict['instance_parameters'][i_p] = float(group.iloc[0][i_p])
            
            for index, curve in group.iterrows():
                curve_dict = {'x_values': curve[x_values] if isinstance(curve[x_values], list) else list(curve[x_values]) if isinstance(curve[x_values], tuple) else curve[x_values].tolist(),
                              'y_values': curve[y_values] if isinstance(curve[y_values], list) else list(curve[y_values]) if isinstance(curve[y_values], tuple) else curve[y_values].tolist(),
                              'curve_weight': float(curve['curve_weight'])}
                if not pd.isnull(group.iloc[0]['extra_var_name']):
                    curve_dict['extra_var_value'] = float(curve['extra_var_value'])
                if include_simulation:
                    curve_dict['x_values_simulation'] = curve[x_values_simulation] if isinstance(curve[x_values_simulation], list) else list(curve[x_values_simulation]) if isinstance(curve[x_values_simulation], tuple) else curve[x_values_simulation].tolist()
                    curve_dict['y_values_simulation'] = curve[y_values_simulation] if isinstance(curve[y_values_simulation], list) else list(curve[y_values_simulation]) if isinstance(curve[y_values_simulation], tuple) else curve[y_values_simulation].tolist()
                    
                group_dict['curves'].append(curve_dict)
            
            processed_data['data'].append(group_dict)
        
        # Transform the processed_data to a json string
        processed_data = json.dumps(processed_data, indent = 4)
        
    # Find and replace newline characters in x_values
    pattern = r'"x_values": \[\n(\s*[^]]+,\n)+\s*[^]]+\s*\]'
    replacement = lambda m: re.sub(r'[\n\s]+', ' ', m.group())
    processed_data = re.sub(pattern, replacement, processed_data)
    
    # Find and replace newline characters in y_values
    pattern = r'"y_values": \[\n(\s*[^]]+,\n)+\s*[^]]+\s*\]'
    replacement = lambda m: re.sub(r'[\n\s]+', ' ', m.group())
    processed_data = re.sub(pattern, replacement, processed_data)
    
    if include_simulation:
        # Find and replace newline characters in x_values_simulation
        pattern = r'"x_values_simulation": \[\n(\s*[^]]+,\n)+\s*[^]]+\s*\]'
        replacement = lambda m: re.sub(r'[\n\s]+', ' ', m.group())
        processed_data = re.sub(pattern, replacement, processed_data)
        
        # Find and replace newline characters in y_values_simulation
        pattern = r'"y_values_simulation": \[\n(\s*[^]]+,\n)+\s*[^]]+\s*\]'
        replacement = lambda m: re.sub(r'[\n\s]+', ' ', m.group())
        processed_data = re.sub(pattern, replacement, processed_data)
        

    # Open a file in write mode
    with open(file_path, 'w') as file:
        file.write(processed_data)
    
