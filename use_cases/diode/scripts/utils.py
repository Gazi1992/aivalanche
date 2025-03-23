#%% Imports
import os, json, matplotlib.pyplot as plt, numpy as np
from datetime import datetime
from parameters.Parameters import Parameters
from screeninfo import get_monitors
from tqdm import tqdm

#%% Helpers
def create_output_folder(results_path):
    timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
    folder_name = f"optimization_{timestamp}"
    output_path = os.path.join(results_path, folder_name)
    figures_path = os.path.join(output_path, 'figures')
    figures_video_path = os.path.join(figures_path, 'video')
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(figures_path, exist_ok=True)
    os.makedirs(figures_video_path, exist_ok=True)
    return output_path, figures_path, figures_video_path

#%% Visualizations
def plot_survivors(data, ax = None, path = None):
    if ax is not None:
        plt.sca(ax)
    else:
        # Create figure
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 5))

    ax.scatter(data['iter'], data['metric'], s = 10)
    # ax.axvline(x=data['unity_gain_freq'], color='r', linestyle='--', label=f"unity gain at {data['unity_gain_freq']:.1f} Hz")

    ax.set_xlabel('Iteration')
    ax.set_ylabel('Metric')
    ax.set_title('Survivor metric evolution')
    ax.set_yscale('log')
    plt.grid(which='major', linestyle='-', alpha=0.5)
    plt.grid(which='minor', axis='y', linestyle='--', alpha=0.3)

    # plt.show()

    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)
        plt.close()

def plot_parameter_evolution(data, path = None):

    # Get primary monitor size
    monitor = get_monitors()[0]
    width = monitor.width / 100  # Convert pixels to inches (approximate)
    height = monitor.height / 100

    figure = plt.figure(figsize=(width, height), dpi=300)

    # params = params[params['iter'] >= params['iter'].max() - 5]
    cols_to_remove = ['iter', 'metric', 'evaluation_type']
    cols_to_keep = [col for col in data.columns if col not in cols_to_remove]
    params = data[cols_to_keep]
    param_names = list(params.columns)
    n_params = len(param_names)

    left_margin = 0.1
    right_margin = 0.1
    bottom_margin = 0.1
    top_margin = 0.1
    all_param_width = 1 - left_margin - right_margin
    param_width = all_param_width / n_params
    param_height = 1 - top_margin - bottom_margin

    for i, p in enumerate(param_names):
        values = params[p]
        hist, edges = np.histogram(values, bins = 100, range = (0,1))
        ax = figure.add_axes([left_margin + i * param_width, bottom_margin, param_width, param_height])
        plt.sca(ax)
        plt.imshow(np.atleast_2d(hist).T, extent = [0,1,0,1],
                    aspect = "auto", origin = 'lower',
                    cmap = 'YlGn')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(p)

        if i == n_params // 2:
            ax.set_title('Parameter evolution')

    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)
        plt.close()

# Plot reference data
def plot_ref_data(data, ax = None, path = None):
    if ax is not None:
        plt.sca(ax)
    else:
        # Create figure
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 5))

    for index, row in data.iterrows():
        ax.scatter(row['x_values'], row['y_values'], marker = 'o', label = f'{row["extra_var_name"]} = {row["extra_var_value"]}')

    ax.set_xlabel(f'{data.iloc[0]["x_name"]}')
    ax.set_ylabel(f'{data.iloc[0]["y_name"]}')
    ax.set_title('Forward current characteristic')
    plt.grid(which='major', linestyle='-', alpha=0.5)
    plt.grid(which='minor', axis='y', linestyle='--', alpha=0.3)
    plt.legend(loc = 'upper left')

    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)
        plt.close()

# Plot the fit
def plot_fit(data, ax = None, path = None):
    if ax is not None:
        plt.sca(ax)
    else:
        # Create figure
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 5))

    for index, row in data.iterrows():
        ax.scatter(row['x_values'], row['y_values'], marker = 'o', facecolors = "None", edgecolors = 'black')
        ax.plot(row['x_values_simulation'], row['y_values_simulation'], label = f'{row["extra_var_name"]} = {row["extra_var_value"]}')

    ax.set_xlabel(f'{data.iloc[0]["x_name"]}')
    ax.set_ylabel(f'{data.iloc[0]["y_name"]}')
    ax.set_title('Forward current characteristic')
    plt.grid(which='major', linestyle='-', alpha=0.5)
    plt.grid(which='minor', axis='y', linestyle='--', alpha=0.3)
    plt.legend(loc = 'upper left')

    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)
        plt.close()

def plot_loss(data, ax = None, path = None):
    if ax is not None:
        plt.sca(ax)
    else:
        # Create figure
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 5))

    ax.plot(data['iter'], data['metric'], '-o')

    ax.set_xlabel('Iteration')
    ax.set_ylabel('Mismatch')
    ax.set_title('Mismatch evolution')
    ax.set_yscale('log')
    plt.grid(which='major', linestyle='-', alpha=0.5)
    plt.grid(which='minor', axis='y', linestyle='--', alpha=0.3)

    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)
        plt.close()

def plot_results(sim_data, optimization_data = None, path = None):

    # Get primary monitor size
    monitor = get_monitors()[0]
    width = monitor.width / 100  # Convert pixels to inches (approximate)
    height = monitor.height / 100

    figure = plt.figure(figsize=(width, height), dpi=300)

    # Margins
    left_margin = 0.05
    right_margin = 0.01
    top_margin = 0.1
    bottom_margin = 0.02

    # Create a base subplot to hold the margin rectangles
    ax = figure.add_axes([0, 0, 1, 1])
    ax.axis('off')

    # Add title in the top margin
    title_ax = figure.add_axes([0, 1-top_margin, 1, top_margin])
    title_ax.axis('off')
    title_ax.text(0.5, 0.7, 'Diode calibration',
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=16,
                 fontweight='bold')

    # Available space after margins
    available_width = 1 - left_margin - right_margin
    available_height = 1 - top_margin - bottom_margin

    # Vertical spacing
    ver_space = 0.1

    # Horizontal spacing
    hor_space = 0.03

    # Define heights relative to available height
    fit_height = (available_height - ver_space) * 0.5
    param_height = fit_height
    loss_height = available_height - fit_height - ver_space

    # Define widths
    fit_width = (available_width - hor_space) * 0.5
    all_param_width = available_width - fit_width - hor_space
    loss_width = available_width

    # Calculate positions
    fit_x = left_margin
    fit_y = 1 - top_margin - fit_height

    param_x = 1 - right_margin - all_param_width
    param_y = fit_y

    loss_x = left_margin
    loss_y = bottom_margin

    # Add the fit plot
    ax = figure.add_axes([fit_x, fit_y, fit_width, fit_height])
    plot_fit(sim_data, ax = ax)

    # Add the parameters evolution
    if optimization_data is None:
        n_params = 20
        param_width = all_param_width / n_params
        for i in range(n_params):
            values = np.random.rand(1000)
            hist, edges = np.histogram(values, bins = 50, range = (0,1))
            ax = figure.add_axes([param_x + i * param_width, param_y, param_width, param_height])
            plt.sca(ax)
            plt.imshow(np.atleast_2d(hist).T, extent = [0,1,0,1],
                       aspect = "auto", origin = 'lower',
                       cmap = 'YlGn')
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel(f'param_{i}')
    else:
        params = optimization_data['parameters']
        # params = params[params['iter'] >= params['iter'].max() - 5]
        cols_to_remove = ['iter', 'metric', 'evaluation_type']
        cols_to_keep = [col for col in params.columns if col not in cols_to_remove]
        params = params[cols_to_keep]
        param_names = list(params.columns)
        n_params = len(param_names)
        param_width = all_param_width / n_params
        for i, p in enumerate(param_names):
            values = params[p]
            hist, edges = np.histogram(values, bins = 100, range = (0,1))
            ax = figure.add_axes([param_x + i * param_width, param_y, param_width, param_height])
            plt.sca(ax)
            plt.imshow(np.atleast_2d(hist).T, extent = [0,1,0,1],
                        aspect = "auto", origin = 'lower',
                        cmap = 'YlGn')
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel(p)
            if i == len(param_names) // 2:
                ax.set_title('Parameter evolution')

    # Add the loss plot
    ax = figure.add_axes([loss_x, loss_y, loss_width, loss_height])
    if optimization_data is None:
        ax.scatter([1], 10)
    else:
        plot_loss(optimization_data['metrics'], ax=ax)

        update_fontsize(figure, 14)

    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)

    plt.show()

# Update all text elements in a figure
def update_fontsize(fig, fontsize):
    # Update title and axis labels for all axes
    for ax in fig.get_axes():
        # Title
        if ax.get_title():
            ax.set_title(ax.get_title(), fontsize=fontsize*1.2)

        # Axis labels
        ax.set_xlabel(ax.get_xlabel(), fontsize=fontsize)
        ax.set_ylabel(ax.get_ylabel(), fontsize=fontsize)

        # Tick labels
        ax.tick_params(axis='both', labelsize=fontsize)

        # Legend - modify existing legend instead of creating new one
        if ax.get_legend():
            for text in ax.get_legend().get_texts():
                text.set_fontsize(fontsize)

        # Colorbar if it exists
        if hasattr(ax, 'collections'):
            for collection in ax.collections:
                if collection.colorbar:
                    collection.colorbar.ax.tick_params(labelsize=fontsize)

        # Text annotations
        for artist in ax.get_children():
            if isinstance(artist, plt.Text):
                artist.set_fontsize(fontsize*1.2)

def create_video_from_pngs(figures_path, output_path, output_name='output.mp4', fps=5, start_index = 0, end_index = None):
    import cv2
    import os
    import re
    from PIL import Image

    # Get and sort PNG files
    png_files = [f for f in os.listdir(figures_path) if f.endswith('.png')]
    png_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))

    if end_index is None:
        png_files = png_files[start_index:]
    else:
        png_files = png_files[start_index:end_index]

    output_path = os.path.join(output_path, output_name)
    output_format = os.path.splitext(output_name)[1].lower()

    if output_format == '.gif':
        # Read images with PIL for GIF
        images = []
        for png in png_files:
            img = Image.open(os.path.join(figures_path, png))
            images.append(img)

        # Save as GIF
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            duration=int(1000/fps),  # Duration in milliseconds
            loop=0
        )

    elif output_format == '.mp4':
        # Read first image for dimensions
        img = cv2.imread(os.path.join(figures_path, png_files[0]))
        height, width, _ = img.shape

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Add frames
        for png in png_files:
            frame = cv2.imread(os.path.join(figures_path, png))
            video.write(frame)

        video.release()

    else:
        raise ValueError("Unsupported output format. Use '.mp4' or '.gif'")
