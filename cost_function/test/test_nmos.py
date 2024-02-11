#%% Imports
from reference_data import Reference_data
from cost_function import Cost_function

#%% get a reference data dataframe
ref_data_file = 'nmos_output_transfer.json'

# initialize the parser
ref_data = Reference_data(ref_data_file)

# get the groups, curves and all the data together
groups = ref_data.groups
curves = ref_data.curves
data = ref_data.data

# create the x_values_simulation and y_values_simulation columns
data['x_values_simulation'] = data['x_values']
data['y_values_simulation'] = data['x_values']


a = data.iloc[0]['y_values_simulation']
b = data.iloc[0]['y_values']

#%% Test the cost function
parts = [
    {
        'id': 'out_char_lin',
        'group_types': ['ids_vds_vgs'],
        'metric_type': 'rmse',
        'weight': 1,
        'norm': True,
        'transform': 'lin',
        'extra_args': {}
    },
    {
        'id': 'out_char_log',
        'group_types': ['ids_vds_vgs'],
        'metric_type': 'rmse',
        'weight': 1,
        'norm': True,
        'transform': 'log',
        'extra_args': {}
    },
    {
        'id': 'kot',
        'group_types': ['kot'],
        'metric_type': 'rmse',
        'weight': 1,
        'norm': True,
        'transform': 'log',
        'extra_args': {}
    },
]

cost_function = Cost_function(parts = parts)
error_metric = cost_function.run(data = data)
