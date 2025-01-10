import os, pickle as pcl
from airfoil_optimization import simulate_multiple_parameters

# Read results
results_path = os.path.abspath('../results')

# Read the diff_evolution object
with open(os.path.join(results_path, 'diff_evolution.pcl'), 'rb') as f:
    diff_evolution = pcl.load(f)
    
# Read the diff_evolution object
with open(os.path.join(results_path, 'sim_results.pcl'), 'rb') as f:
    sim_results = pcl.load(f)