#%% Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.style import context
from matplotlib import cm
from matplotlib.ticker import LinearLocator


#%% Quadratic function - min at (0, 0, 0)
def quadratic_3_variables(x, y, z):
    f = (1 + x**2 + y**2 + z**2) / 10
    return f

#%% Evaluation quadratic function
def evaluate_quadratic_3_variables(iteration: int = None, parameters: dict = None, extra_arg: str = None ):
    print(f"extra_arg: {extra_arg}")
    response = {'metrics': []}
    response['metrics'] = [quadratic_3_variables(item['x'], item['y'], item['z']) for item in parameters]
    return response


#%% Beale function - min at (3, 0.5)
def beale_2_variables(x, y):
    f = (1.5 - x + x*y)**2 + (2.25 - x + x*y**2)**2 +(2.625 - x + x*y**3)**2
    return f

#%% Evaluation beale function
def evaluate_beale_2_variables(iteration: int = None, parameters: dict = None, extra_arg: str = None ):
    print(f"extra_arg: {extra_arg}")
    response = {'metrics': []}
    response['metrics'] = [beale_2_variables(item['x'], item['y']) for item in parameters]
    return response

#%% Plot beale function
def plot_beale(parameters: dict = None):
    
    with context('seaborn-v0_8-bright'):
    
        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        
        # Make data.
        X = np.arange(-4.5, 4.5, 0.05)
        Y = np.arange(-4.5, 4.5, 0.05)
        X, Y = np.meshgrid(X, Y)
        Z = beale_2_variables(X, Y)
        
        # Plot the surface.
        surf = ax.plot_surface(X, Y, Z, cmap = cm.coolwarm, linewidth = 0, antialiased = False)
        
        plt.show()


#%% Quadratic function - min at (0, 0, 0, 0)
def quadratic_4_variables(x, y, z, w):
    f = (1 + x**2 + y**2 + z**2 + w**2) / 10
    return f

#%% Evaluation quadratic function
def evaluate_quadratic_4_variables(iteration: int = None, parameters: dict = None, extra_arg: str = None ):
    print(f"extra_arg: {extra_arg}")
    response = {'metrics': []}
    response['metrics'] = [quadratic_4_variables(item['x'], item['y'], item['z'], item['w']) for item in parameters]
    return response


#%% Sin_sqrt function - min at (0, 0, 0, 0)
def sin_sqrt_2_variables(x, y):
    f = np.sin(np.sqrt(x**2 + y**2)) + x / 10
    return f

#%% Evaluation sin_sqrt function
def evaluate_sin_sqrt_2_variables(iteration: int = None, parameters: dict = None, extra_arg: str = None ):
    print(f"extra_arg: {extra_arg}")
    response = {'metrics': []}
    response['metrics'] = [sin_sqrt_2_variables(item['x'], item['y']) for item in parameters]
    return response

#%% Plot sin_sqrt function
def plot_sin_sqrt(parameters: dict = None):
    
    if parameters is not None:
        x = [p['x'] for p in parameters]
        y = [p['y'] for p in parameters]
        z = [sin_sqrt_2_variables(i,j) for i,j in zip(x,y)]
    
    with context('seaborn-v0_8-bright'):
    
        fig, ax = plt.subplots(figsize=(9,9), subplot_kw={"projection": "3d"})
        
        # Make data.
        X = np.arange(-5, 5, 0.05)
        Y = np.arange(-5, 5, 0.05)
        X, Y = np.meshgrid(X, Y)
        Z = sin_sqrt_2_variables(X, Y)
        
        # Plot the surface.
        surf = ax.plot_surface(X, Y, Z, cmap = cm.coolwarm, linewidth = 0, antialiased = False, alpha = 0.5)
        ax.view_init(azim = 0, elev = 90)
        if parameters is not None:
            ax.scatter(x, y, z, c = 'black')
        
        plt.show()






















