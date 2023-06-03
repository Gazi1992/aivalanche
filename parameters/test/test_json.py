#%% Imports
from parameters import Parameters

file = 'example.json'

# initialize the parser
parameters = Parameters(file)
var_parameters = parameters.variable_parameters
fixed_parameters = parameters.fixed_parameters


