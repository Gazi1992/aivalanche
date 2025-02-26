import os, pandas as pd, numpy as np
from optimization.differential_evolution.gaussian_process import Gaussian_process

#%% Paths
scripts_path = os.path.abspath(os.getcwd())
inputs_path = os.path.join(scripts_path, '../inputs')
results_path = os.path.join(scripts_path, '../results')
results_file_path = os.path.join(results_path, 'sim_results.csv')

#%% Read the results
results = pd.read_csv(results_file_path)
target_col = 'power'
param_cols = results.columns.tolist()
param_cols.remove(target_col)

x = np.array(results[param_cols])
y = np.array(results[target_col])

# x = np.linspace(0, 10, num = 100)
# y = np.sin(x)

#%% Build the model
gp = Gaussian_process(noise_variance = 1e-5, standardize = True, auto_kernel_selection=True)
gp.fit(x, y, optimize = True, num_restarts = 10)
gp.plot_accuracy()
