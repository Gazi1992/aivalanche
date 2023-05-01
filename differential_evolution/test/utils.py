#%% Imports
import numpy as np


#%% Quadratic function
def quadratic(x, y, z):
    f = (1 + x**2 + y**2 + z**2) / 10
    return f


#%% Evaluation function
def evaluate_quadratic(iteration = None, parameters = None):
    response = {'metrics': []}
    response['metrics'] = [quadratic(item['x'], item['y'], item['z']) for item in parameters]
    return response
