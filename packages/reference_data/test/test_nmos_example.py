#%% Imports
from reference_data import Reference_data
from reference_data.visualization import plot_all_groups
from reference_data.utils import write_reference_data_to_file

file = 'test.json'

# initialize the parser
ref_data = Reference_data(file)

# get the groups, curves and all the data together
groups = ref_data.groups
curves = ref_data.curves
data = ref_data.data

# plot all groups
plot_all_groups(data)

write_reference_data_to_file(data = data,
                             file_path = 'test.json',
                             operating_conditions = ['temp', 'vbs', 'vds', 'vgs'],
                             instance_parameters = ['w', 'l', 'm'])
