#%% Imports
from reference_data.parser import parser

file = 'nmos_example.json'

ref_data_parser = parser(file)

ref_data_parser.json_to_dataframe()


