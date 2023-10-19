#%% Imports
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.style import context


#%% Plot one group
def plot_group(group: pd.DataFrame = None, save_dir: str = None, extra_legend: list[str] = [], scientific_y_axis: bool = True):
    if group is not None:
        group_name = group['group_name'].values[0]
        group_id = group['group_id'].values[0]
        x_name = group['x_name'].values[0]
        y_name = group['y_name'].values[0]
        extra_var_name = group['extra_var_name'].values[0]
        title = f"{group_name} - {group_id}"
        
        extra_legend_text = ''
        for item in extra_legend:
            if item in group.columns and not pd.isnull(group.iloc[0][item]) and item != group.iloc[0]['extra_var_name']:
                extra_legend_text += f"{item} = {group.iloc[0][item]}\n"
        
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
            legend = ax.legend()
            
            if scientific_y_axis:
                ax.ticklabel_format(style = 'sci', axis = 'y', scilimits = (0, 0))
            
            if extra_legend_text != '':
                # Get the position of the legend in figure coordinates
                legend_bbox = legend.get_window_extent().transformed(figure.transFigure.inverted())
                
                if legend_bbox.x0 < 0.5:
                    x_pos = legend_bbox.x0 + legend_bbox.width + 0.01
                else:
                    x_pos = legend_bbox.x0 - 0.01

                y_pos = legend_bbox.y0 + legend_bbox.height - 0.015
                plt.text(x_pos, y_pos, extra_legend_text.rstrip("\n"), color = 'black',
                         bbox = dict(facecolor = 'white', edgecolor = 'gray', alpha = 0.9),
                         transform = figure.transFigure, ha = 'left' if legend_bbox.x0 < 0.5 else 'right', va = 'top')
            
            if save_dir is not None:
                try:
                    figure.savefig(os.path.join(save_dir, f'{group_id}.png'))
                except Exception as e:
                    print('Error saving figure.')
                    print(e)
                plt.close(figure)
            else:
                plt.show()
            

def plot_all_groups(groups: pd.DataFrame = None, save_dir: str = None, extra_legend: list[str] = []):
    groups_split = groups.groupby('group_id')
    for name, group in groups_split:
        plot_group(group, save_dir, extra_legend)