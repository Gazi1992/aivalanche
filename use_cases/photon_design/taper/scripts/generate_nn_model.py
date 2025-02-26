import os, pandas as pd, numpy as np, torch
from metamodel_utils import create_best_model, optimize_hyperparameters

#%% Paths
scripts_path = os.path.abspath(os.getcwd())
inputs_path = os.path.join(scripts_path, '../inputs')
results_path = os.path.join(scripts_path, '../results')
results_file_path = os.path.join(results_path, 'sim_results.csv')

#%% Read the results
results = pd.read_csv(results_file_path)
target_column = 'power'

#%% Metamodel
best_params, best_value = optimize_hyperparameters(results, target_column, n_trials=100)

best_model, train_loader, test_loader = create_best_model(results, target_column, best_params)
