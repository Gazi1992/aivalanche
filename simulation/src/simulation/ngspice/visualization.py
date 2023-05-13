#%% Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.style import context


#%% Plot the results
def plot_results(device: str = None, simulation_type: str = None, data: pd.DataFrame = None):
    if device is not None and simulation_type is not None and data is not None:
        function_name = f"plot_{device}_{simulation_type}"
        globals()[function_name](data = data)


#%% Plot the output characteristics of a mosfet
def plot_mosfet_output_characteristic(data: pd.DataFrame = None):
    if data is not None:
        x_name = 'v_ds'
        y_name = 'i_ds'
        title = 'output characteristic'
        with context('seaborn-v0_8-bright'):
            figure, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(8, 4.5))
            grouped_data = data.groupby('v_gs')
            for name, values in grouped_data:
                ax.scatter(values['v_ds'], values['i_ds'], label = f"v_gs = {name}")
            ax.set_title(title)
            ax.set_xlabel(x_name)
            ax.set_ylabel(y_name)
            ax.grid(which = 'both', axis = 'both')
            ax.legend()
            plt.show()
