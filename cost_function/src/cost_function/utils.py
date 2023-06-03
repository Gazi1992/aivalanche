#%% Imports
import pandas as pd
import numpy as np
from cost_function.exceptions import raise_exception


#%% Calculate the error metric for the given groups
def calculate_error_metric(data: pd.DataFrame = None, parameters: pd.DataFrame = None, 
                           group_types: list[str] = None, metric_type: str = 'rmse', 
                           weight = 1, norm: bool = True, transform: str = None, **kwargs):
    
    try:
        # Get only the groups included in the group_type
        groups = filter_groups(all_groups = data, relevant_groups = group_types)
        
        # If no output characteristic present, then raise an error
        if len(groups.index) <= 0:
            error_metric = raise_exception('no_group_exception', None, group_types)
            return error_metric
            
        # Transform the data
        groups = transform_groups(groups, transform)
            
        # Norm if required
        if norm:
            groups = norm_groups(groups)     
    
        # Calculate the error_metric
        if metric_type == 'rmse':
            error_metric = calculate_rmse(groups)
        else:
            error_metric = 0
            
            
        return error_metric
    
    except Exception:
        error_metric = raise_exception('failed_error_metric_exception', None, group_types)
        return error_metric
        
    
#%% Explode the dataframe
def explode_dataframe(data: pd.DataFrame = None, explode_columns = ['x_values', 'y_values', 'x_values_simulated', 'y_values_simulated']):
    return data.explode(explode_columns).reset_index(drop=True)


#%% Get the root mean squared between y_values and y_values_simulation
def calculate_rmse(groups: pd.DataFrame = None):
    
    if groups is None:
        return 0
    
    groups = groups.copy()
    
    groups['temp_error_metric'] = groups.apply(lambda row: np.nansum((row['group_weight'] * row['curve_weight'] * (row['y_values'] - row['y_values_simulation'])) ** 2), axis = 1)
    
    return np.sqrt(np.sum(groups['temp_error_metric']) / np.sum(groups['curve_length']))


#%% Apply transformation to the y_values and y_values_simulation
def transform_groups(groups: pd.DataFrame = None, transform: str = None):
    
    AVAILABLE_TRANSFORMS = ['log', 'grad_1', 'grad_2']
    
    # If no transform given, then return groups as they are
    if transform is None or transform == 'lin':
        return groups
    
    # If transform is not part of the available transform, then return groups as they are
    if transform not in AVAILABLE_TRANSFORMS:
        print(f'Warning: {transform} is not supported.')
        return groups
    
    # Create a copy of the groups to not modify the original dataframe
    groups = groups.copy()
    
    # Get the log10 of y_values and y_values_simulation
    if transform == 'log':
        groups['y_values'] = groups['y_values'].apply(lambda arr: np.where(np.isinf(np.log10(arr)), np.nan, np.log10(arr)))
        groups['y_values_simulation'] = groups['y_values_simulation'].apply(lambda arr: np.where(np.isinf(np.log10(arr)), np.nan, np.log10(arr)))
    
    return groups

#%% Norm the y_values and y_values_simulation based on the y_values
def norm_groups(groups: pd.DataFrame = None):
    # Create a copy of the groups to not modify the original dataframe
    groups = groups.copy()
    
    # Calculate the maximum value for each group
    groups['max_norm'] = groups.groupby('group_id')['y_values'].transform(lambda x: np.nanmax(np.concatenate(x.tolist())) )

    # Calculate the minimum value for each group
    groups['min_norm'] = groups.groupby('group_id')['y_values'].transform(lambda x: np.nanmin(np.concatenate(x.tolist())))
    
    # Get only the groups which have a max and min different from nan
    groups = groups[groups['max_norm'].notna() & groups['min_norm'].notna()]
    
    # Norm the y_values and the y_values_simulation
    groups['y_values'] = (groups['y_values'] - groups['min_norm']) / (groups['max_norm'] - groups['min_norm'])
    groups['y_values_simulation'] = (groups['y_values_simulation'] - groups['min_norm']) / (groups['max_norm'] - groups['min_norm'])
    
    return groups


#%% Get only the relevant groups
def filter_groups(all_groups: pd.DataFrame = None, relevant_groups: list[str] = None):
    filtered_groups = all_groups[all_groups['group_type'].isin(relevant_groups)]
    return filtered_groups
   


   
    
   
