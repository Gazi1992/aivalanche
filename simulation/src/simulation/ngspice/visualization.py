#%% Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.style import context
import re


#%% Plot the results
def plot_results(device: str = None, characteristic_type: str = None, data: pd.DataFrame = None):
    if device is not None and characteristic_type is not None and data is not None:
        function_name = f"plot_{device}_{characteristic_type}"
        globals()[function_name](data = data)


#%% Plot the output characteristics of a mosfet
def plot_mosfet_output_characteristic(data: pd.DataFrame = None):
    if data is not None:
        x_name = 'vds'
        y_name = 'ids'
        title = 'output characteristic'
        with context('seaborn-v0_8-bright'):
            figure, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(8, 4.5))
            if isinstance(data, pd.DataFrame):
                for idx, row in data:
                    ax.scatter(row['vds'], row['ids'], label = f"vgs = {row['vgs']}")
            elif isinstance(data, pd.Series):
                ax.scatter(data['vds'], data['ids'], label = f"vgs = {data['vgs']}")
            ax.set_title(title)
            ax.set_xlabel(x_name)
            ax.set_ylabel(y_name)
            ax.grid(which = 'both', axis = 'both')
            ax.legend()
            plt.show()


#%% Plot the transfer characteristics of a mosfet
def plot_mosfet_transfer_characteristic(data: pd.DataFrame = None):
    if data is not None:
        x_name = 'vgs'
        y_name = 'ids'
        title = 'transfer characteristic'
        with context('seaborn-v0_8-bright'):
            figure, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(8, 4.5))
            if isinstance(data, pd.DataFrame):
                for idx, row in data:
                    ax.scatter(row['vgs'], row['ids'], label = f"vds = {row['vds']}")
            elif isinstance(data, pd.Series):
                ax.scatter(data['vgs'], data['ids'], label = f"vds = {data['vds']}")
            ax.set_title(title)
            ax.set_xlabel(x_name)
            ax.set_ylabel(y_name)
            ax.grid(which = 'both', axis = 'both')
            ax.legend()
            plt.show()
            
            
#%% Plot the diode characteristics of a mosfet
def plot_diode_characteristic(data: pd.DataFrame = None):
    if data is not None:
        x_name = 'vd'
        y_name = 'id'
        title = 'diode characteristic'
        with context('seaborn-v0_8-bright'):
            figure, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(8, 4.5))
            if isinstance(data, pd.DataFrame):
                for idx, row in data:
                    ax.scatter(row['vd'], row['id'])
            elif isinstance(data, pd.Series):
                ax.scatter(data['vd'], data['id'])
            ax.set_title(title)
            ax.set_xlabel(x_name)
            ax.set_ylabel(y_name)
            ax.grid(which = 'both', axis = 'both')
            plt.show()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            