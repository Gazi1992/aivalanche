#%% Imports
import os, numpy as np, matplotlib.pyplot as plt, pandas as pd
from matplotlib.style import context

# Plot metric evolution
def plot_metric_evolution(iterations: np.array = None,
                          metrics: np.array = None,
                          y_scale: str = 'log',
                          upper_threshold: float = 1e10,
                          lower_threshold: float = 0,
                          save_dir: str = None):
    if iterations is not None and metrics is not None:
        # iterations = np.array(iterations)
        # metrics = np.array(metrics)
        mask = (metrics > lower_threshold) & (metrics < upper_threshold)
        with context('seaborn-v0_8-bright'):
            figure, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(8, 4.5))
            ax.scatter(iterations[mask], metrics[mask])
            ax.set_title('Metric evolution')
            ax.set_xlabel('Iterations')
            ax.set_ylabel('Metrics')
            ax.set_yscale(y_scale)
            ax.grid(which = 'both', axis = 'both')
            if save_dir is not None:
                try:
                    figure.savefig(os.path.join(save_dir, f'metric_evolution_{max(iterations)}.png'))
                except Exception as e:
                    print('Error saving figure.')
                    print(e)
                    plt.show()
                plt.close(figure)
            else:
                plt.show()
            
# Plot parameter evolution
def plot_parameter_evolution(parameters: list = None, data: np.array = None, iteration: int = None, save_dir: str = None):
    if parameters is None or data is not None:
        nr_plots = len(parameters)
        param_hist_width = 1 / nr_plots
        param_hist_height = 0.85
        param_hist_bottomY = 0.1
        with context('seaborn-v0_8-bright'):
            figure = plt.figure(figsize = (max(nr_plots * 0.2, 8), 4.5))
            for idx, param in enumerate(parameters):
                ax = figure.add_subplot()
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
            
            if save_dir is not None:
                try:
                    figure.savefig(os.path.join(save_dir, f'parameter_evolution_{iteration}.png'))
                except Exception as e:
                    print('Error saving figure.')
                    print(e)
                    plt.show()
                plt.close(figure)
            else:
                plt.show()

# Plot histogram
def plot_histogram(data: np.array = None):
    plt.hist(data)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Histogram')
    plt.show()         

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
            
            