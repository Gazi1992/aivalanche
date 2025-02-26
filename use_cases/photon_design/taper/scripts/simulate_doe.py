import os, pandas as pd, numpy as np
from fimmwave_simulator import Fimmwave_simulator
from utils import simulate_multiple_parameters

#%% Paths
scripts_path = os.path.abspath(os.getcwd())
inputs_path = os.path.join(scripts_path, '../inputs')
results_path = os.path.join(scripts_path, '../results')
parameters_path = os.path.join(inputs_path, 'parameters.csv')
doe_path = os.path.join(results_path, 'doe.csv')
project_path = os.path.join(inputs_path, 'Taper', 'Taper.prj')
results_file_path = os.path.join(results_path, 'sim_results.csv')

#%% Read the doe
doe = pd.read_csv(doe_path)
params_list = doe.to_dict('records')

#%% Initialize simulator
port = 2121
simulator = Fimmwave_simulator(port = port, project_path = project_path)
simulator.connect()
simulator.open_project()

#%% Simulate the doe
sim_results = simulate_multiple_parameters(parameters = params_list, simulator = simulator)

#%% Generate the results file to be used for the metamodel
power_array = np.array([item['power'] for item in sim_results['data']])
result = doe.copy()
result['power'] = power_array
result.to_csv(results_file_path, index = False)

#%% Disconnect the simulator
simulator.disconnect()
