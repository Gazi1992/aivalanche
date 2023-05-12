#%% Imports
from testbench.parser import parser

file = 'example.json'

# initialize the parser
parameters_parser = parser(file)
var_parameters = parameters_parser.variable_parameters
fixed_parameters = parameters_parser.fixed_parameters


