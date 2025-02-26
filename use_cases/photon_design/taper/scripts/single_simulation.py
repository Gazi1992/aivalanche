#%% Imports
import pandas as pd, numpy as np, os
from utils import create_output_folder, read_parameters
from fimmwave_simulator import Fimmwave_simulator

#%% Paths
results_path = os.path.abspath('../results')
inputs_path = os.path.abspath('../inputs')
parameters_path = os.path.join(inputs_path, 'parameters.csv')
project_path = os.path.join(inputs_path, 'Taper', 'Taper.prj')

#%% Read parameters
parameters = read_parameters(parameters_path)
params_dict = pd.Series(parameters['default'].values, index = parameters['name']).to_dict()

#%% Initialize simulator
port = 2121
simulator = Fimmwave_simulator(port = port, project_path = project_path)
simulator.connect()
simulator.open_project()

#%% Single simulation
sim_results = simulator.simulate_parameters(params_dict)
print(sim_results)

#%% Multiple simulations
p_0 = pd.Series(parameters['default'].values, index = parameters['name']).to_dict()
p_1 = pd.Series(parameters['min'].values, index = parameters['name']).to_dict()
p_2 = pd.Series(parameters['max'].values, index = parameters['name']).to_dict()
params = [p_0, p_1, p_2]

sim_results = simulator.simulate_multiple_parameters(params)
print(sim_results)

#%% Simulate kalistos parameters
path = os.path.join(inputs_path, 'kalistos_parameters.csv')
parameters = pd.read_csv(path)
params_dict = pd.Series(parameters['value'].values, index = parameters['name']).to_dict()

sim_results = simulator.simulate_parameters(params_dict)
print(sim_results)

#%% Simulate DE parameters
path = os.path.join(inputs_path, 'best_parameters.csv')
parameters = pd.read_csv(path)
params_dict = pd.Series(parameters['value'].values, index = parameters['name']).to_dict()

sim_results = simulator.simulate_parameters(params_dict)
print(sim_results)

#%% Disconnect the simulator
simulator.disconnect()
