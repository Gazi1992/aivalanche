#%% Imports
from reference_data import Reference_data
from reference_data.visualization import plot_all_groups

file = 'nmos_example.json'

# initialize the parser
ref_data = Reference_data(file)

# get the groups, curves and all the data together
groups = ref_data.groups
curves = ref_data.curves
data = ref_data.data

# plot all groups
plot_all_groups(data)
