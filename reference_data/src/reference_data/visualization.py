#%% Imports
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.style import context


#%% Plot one group
def plot_group(group: pd.DataFrame = None):
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
                    ax.scatter(curve['x_value'], curve['y_value'])
                else:
                    ax.scatter(curve['x_value'], curve['y_value'], label = f"{extra_var_name} = {curve['extra_var_value']}")
            ax.set_title(title)
            ax.set_xlabel(x_name)
            ax.set_ylabel(y_name)
            ax.grid(which = 'both', axis = 'both')
            ax.legend()
            plt.show()
            

def plot_all_groups(groups: pd.DataFrame = None):
    groups_split = groups.groupby('group_id')
    for name, group in groups_split:
        plot_group(group)