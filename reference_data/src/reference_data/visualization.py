#%% Imports
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.style import context


#%% Plot one group
def plot_group(group: pd.DataFrame = None, save_dir: str = None):
    if group is not None:
        group_name = group['group_name'].values[0]
        group_id = group['group_id'].values[0]
        x_name = group['x_name'].values[0]
        y_name = group['y_name'].values[0]
        extra_var_name = group['extra_var_name'].values[0]
        title = f"{group_name} - {group_id}"
        with context('seaborn-v0_8-bright'):
            figure, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(8, 4.5))
            for index, curve in group.iterrows():
                if pd.isnull(extra_var_name):
                    ax.scatter(curve['x_values'], curve['y_values'])
                    if 'x_values_simulation' in group.columns and 'y_values_simulation' in group.columns:
                        ax.plot(curve['x_values_simulation'], curve['y_values_simulation'])
                else:
                    ax.scatter(curve['x_values'], curve['y_values'], label = f"{extra_var_name} = {curve['extra_var_value']}")
                    if 'x_values_simulation' in group.columns and 'y_values_simulation' in group.columns:
                        ax.plot(curve['x_values_simulation'], curve['y_values_simulation'])
            ax.set_title(title)
            ax.set_xlabel(x_name)
            ax.set_ylabel(y_name)
            ax.grid(which = 'both', axis = 'both')
            ax.legend()
            plt.show()
        if save_dir is not None:
            try:
                figure.savefig(os.path.join(save_dir, f'{group_id}.png'))
            except Exception as e:
                print('Error saving figure.')
                print(e)
            

def plot_all_groups(groups: pd.DataFrame = None, save_dir: str = None):
    groups_split = groups.groupby('group_id')
    for name, group in groups_split:
        plot_group(group, save_dir)