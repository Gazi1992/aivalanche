#%% Imports
from reference_data.parser import parser
from reference_data.visualization import plot_all_groups

file = 'nmos_example.json'

# initialize the parser
ref_data_parser = parser(file)

# get the groups, curves and all the data together
groups = ref_data_parser.groups
curves = ref_data_parser.curves
data = ref_data_parser.data

# plot all groups
plot_all_groups(data)
