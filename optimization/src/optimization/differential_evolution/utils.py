#%% Imports
import pandas as pd, numpy as np


#%% Set transfor to 'None' for the lin parameter, to 'log' for positive parameter in log scale and to 'neglog' for negative parameter in log scale.
def set_transform(parameter):
    if parameter['scale'].lower() == 'log':
        if parameter['min'] > 0 and parameter['max'] > 0:
            return 'log'
        elif parameter['min'] < 0 and parameter['max'] < 0:
            return 'neglog'
    return None


#%% Calculate the scaled value for the parameter
def scale_parameter(parameter, field = 'value'):
    if parameter['transform'] == 'log':
        return np.log10(parameter[field])
    elif parameter['transform'] == 'neglog':
        return np.log10(-parameter[field])
    else:
        return parameter[field]


#%% Calculate the unscaled values from the scaled parameter
def unscale_parameter(parameter, field):
    if parameter['transform'] == 'log':
        return np.longdouble(10.0**parameter[field])
    elif parameter['transform'] == 'neglog':
        return -np.longdouble(10.0**parameter[field])
    else:
        return parameter[field]
    

#%% Unnorm member 
def unnorm_member(member, minimum, maximum):
    return minimum + member * (maximum - minimum)


#%% Norm member 
def norm_member(member, minimum, maximum):
    return (member - minimum) / (maximum - minimum)


#%% Preprocess parameters, by checking their validity, calculating the corresponding transformation functions and scaling them respectively.
def preprocess_parameters(parameters: pd.DataFrame = None):
    if parameters is None or not isinstance(parameters, pd.DataFrame):
        raise SystemExit('ERROR! parameters have to be given as a pandas dataframe, with columns [name, min, max]')
    
    if 'name' not in parameters.columns or 'min' not in parameters.columns or 'max' not in parameters.columns:
        raise SystemExit('ERROR! parameters have to be given as a pandas dataframe, with columns [name, min, max]')
    
    if len(parameters['name'].tolist()) != len(set(parameters['name'].tolist())):
        raise SystemExit('ERROR! parameters cannot have duplicate names')
    
    # reset index
    parameters.reset_index(inplace = True, drop = True)
    
    # order parameters by name
    parameters = parameters.sort_values(by ='name')
    
    # set default to the middle value if it is not given
    if 'default' not in parameters.columns:
        parameters[['min', 'max']] = parameters[['min', 'max']].astype(float)
        parameters['default'] = (parameters['max'] + parameters['min']) / 2
    else:
        parameters[['min', 'max', 'default']] = parameters[['min', 'max', 'default']].astype(float)
        
    # set scale to linear if it is missing
    if 'scale' not in parameters.columns:
        parameters['scale'] = 'lin'
        
    parameters['transform'] = parameters.apply(lambda row: set_transform(row), axis = 1)                # set transform for each parameter
    parameters['value'] = parameters['default']                                                         # set the value to default
    parameters['value_scaled'] = parameters.apply(lambda row: scale_parameter(row, 'value'), axis = 1)  # set the value scaled
    parameters['min_scaled'] = parameters.apply(lambda row: scale_parameter(row, 'min'), axis = 1)      # set the min scaled
    parameters['max_scaled'] = parameters.apply(lambda row: scale_parameter(row, 'max'), axis = 1)      # set the max scaled
        
    return parameters





















