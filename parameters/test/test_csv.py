#%% Imports
from parameters import Parameters

file = 'example.csv'

# initialize the parser
parameters = Parameters(file)
var_parameters = parameters.variable_parameters
fixed_parameters = parameters.fixed_parameters

rand_params = parameters.generate_random_parameters()



