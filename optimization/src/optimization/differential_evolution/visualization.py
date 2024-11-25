#%% Imports
import os, numpy as np, matplotlib.pyplot as plt, pandas as pd
from matplotlib.style import context      

# Plot all columns of a df
def plot_df(data: pd.DataFrame = None, title = 'title', x_label = 'x', y_label = 'y', show_legend = True, save_dir: str = None):
    with context('seaborn-v0_8-bright'):
        figure, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(8, 4.5))
        for column in data.columns:
            ax.plot(data.index, data[column], label = column)
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(which = 'both', axis = 'both')
        if show_legend:
            ax.legend()
        if save_dir is not None:
            try:
                figure.savefig(os.path.join(save_dir, 'std_evolution.png'))
            except Exception as e:
                print('Error saving figure.')
                print(e)
                plt.show()
            plt.close(figure)
        else:
            plt.show()
            
# Plot the parameter fit
def plot_parameter_fit(real_data: pd.DataFrame = None, fit_data: pd.DataFrame = None):
    with context('seaborn-v0_8-bright'):
        figure, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(8, 4.5))
        for column in real_data.columns:
            ax.scatter(real_data.index, real_data[column], label = column)
            ax.plot(fit_data.index, fit_data[column], label = column)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.grid(which = 'both', axis = 'both')
        ax.legend()
        plt.show()
        
# Plot the quantile fits for each parameter
def plot_quantile_fits(lower_quantile, upper_quantile, lower_quantile_fit, upper_quantile_fit):
    with context('seaborn-v0_8-bright'):
        for col in lower_quantile.columns:
            figure, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(8, 4.5))
            ax.fill_between(lower_quantile_fit.index, lower_quantile_fit[col], upper_quantile_fit[col], color = 'lightblue')
            ax.scatter(lower_quantile.index, lower_quantile[col], facecolors = 'none', edgecolors = 'black')
            ax.scatter(upper_quantile.index, upper_quantile[col], facecolors = 'none', edgecolors = 'black')
            ax.plot(lower_quantile_fit.index, lower_quantile_fit[col], color = 'black')
            ax.plot(upper_quantile_fit.index, upper_quantile_fit[col], color = 'black')
            ax.set_title(col)
            ax.set_xlabel('iteration')
            ax.set_ylabel('quantiles')
            ax.grid(which = 'both', axis = 'both')
            plt.show()
            
            