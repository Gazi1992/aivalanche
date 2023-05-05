#%% Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.style import context


#%% Plot metric evolution
def plot_metric_evolution(iterations: np.array = None,
                          metrics: np.array = None,
                          y_scale: str = 'log'):
    if iterations is not None and metrics is not None:
        with context('seaborn-v0_8-bright'):
            figure, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(8, 4.5))
            ax.scatter(iterations, metrics)
            ax.set_title('Metric evolution')
            ax.set_xlabel('Iterations')
            ax.set_ylabel('Metrics')
            ax.set_yscale(y_scale)
            ax.grid(which = 'both', axis = 'both')
            plt.show()
            

#%% Plot parameter evolution
def plot_parameter_evolution(parameters: list = None, data: np.array = None):
    if parameters is None or data is not None:
        nr_plots = len(parameters)
        param_hist_width = 1 / nr_plots
        param_hist_height = 0.85
        param_hist_bottomY = 0.1
        with context('seaborn-v0_8-bright'):
            fig = plt.figure(figsize = (max(nr_plots * 0.2, 8), 4.5))
            for idx, param in enumerate(parameters):
                ax = fig.add_subplot()
                ax.set_position([idx * param_hist_width, param_hist_bottomY, param_hist_width, param_hist_height])
                hist, edges = np.histogram(data[:,idx], bins = 500, range = (0,1))
                plt.sca(ax)
                plt.imshow(np.atleast_2d(hist).T, extent = [0,1,0,1], aspect = "auto", origin = 'lower', cmap = 'jet')
                ax.set_xticks([])
                ax.set_yticks([])
                if idx == int(nr_plots / 2):
                    ax.set_title('Parameter evolution')
                ax.xaxis.label.set_color('black')
                if nr_plots > 20:
                    ax.set_xlabel(param, rotation = 'vertical')
                else:
                    ax.set_xlabel(param)
            plt.show()
            
            
            
            
            
            
            