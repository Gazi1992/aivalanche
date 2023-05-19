#%% Imports
from reference_data.parser import parser as ref_parser
from reference_data.visualization import plot_all_groups


file = 'testbenches_example.json'

#%% get a reference data dataframe
ref_data_file = 'nmos_ref_data_example.json'

# initialize the parser
ref_data_parser = ref_parser(ref_data_file)

# get the groups, curves and all the data together
groups = ref_data_parser.groups
curves = ref_data_parser.curves
data = ref_data_parser.data

# plot all groups
plot_all_groups(data)


#%% build testbenches for all the rows of the dataframe





