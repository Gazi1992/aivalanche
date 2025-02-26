#%% Imports
import os, numpy as np, pandas as pd
from utils import read_parameters, fetch_oa_from_file
from pyDOE import lhs

#%% Paths
scripts_path = os.path.abspath(os.getcwd())
inputs_path = os.path.join(scripts_path, '../inputs')
results_path = os.path.join(scripts_path, '../results')
parameters_path = os.path.join(inputs_path, 'parameters.csv')
doe_path = os.path.join(results_path, 'doe.csv')

#%% Variables
n_samples = 200

#%% Read the parameters
params = read_parameters(parameters_path)
param_names = params['name'].tolist()

# oa parameters
n_params = len(param_names)
n_levels = 3
strength = 3

#%% Get oa samples
oa_path = os.path.join(inputs_path,'oa', f'oa_{n_params}_{n_levels}_{strength}.json')
oa = fetch_oa_from_file(oa_path)
oa_samples = pd.DataFrame(data = oa['oa'], columns = param_names)
oa_samples = (oa_samples - oa_samples.min()) / (oa_samples.max() - oa_samples.min())
oa_length = len(oa_samples)

#%% Get the lhs samples
n_lhs_samples = n_samples - oa_length
lhs_samples = lhs(n_params, samples = n_lhs_samples)
lhs_samples = pd.DataFrame(data = lhs_samples, columns = param_names)

#%% Combine samples
samples = pd.concat((oa_samples, lhs_samples), ignore_index=True)

#%% Scale the samples
min_array = np.array(params['min']).reshape(1,-1)
max_array = np.array(params['max']).reshape(1,-1)
samples_scaled = samples * (max_array - min_array) + min_array

#%% Write them to csv
samples_scaled.to_csv(doe_path, index = False)
