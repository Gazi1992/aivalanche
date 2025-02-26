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


def read_parameters(file):
    params = Parameters(file)
    return params.variable_parameters

def dict_2_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def fetch_oa_from_file(file_path = None):
    if file_path is None:
        print('Please provide a file path.')
        return None

    if not os.path.exists(file_path):
        print(f'Please provide a valid file path. {file_path} does not exist')
        return None

    with open(file_path, 'r') as f:
        results = json.load(f)
        results['oa'] = np.array(results['oa'])

    return results

#%% Simulation functions
def simulate_multiple_parameters(parameters: list[dict] = None, **kwargs):
    simulator = kwargs['simulator']
    if simulator is not None and parameters is not None:
        results = simulator.simulate_multiple_parameters(parameters)
    metrics = [calculate_metric(r) for r in tqdm(results, desc = "Calculating metrics")]
    responses = {'data': results, 'metrics': metrics}
    return responses

def calculate_metric(sim_results):
    # metric = 1 / sim_results['power']
    metric = -sim_results['power']
    return metric

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
    # ax.set_yscale('log')
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

def plot_z_field(data, path = None):
    values = data['values'][:,2].reshape(data['x_size'], data['y_size']).T
    x = data['values'][:,0].reshape(data['x_size'], data['y_size']).T
    y = data['values'][:,1].reshape(data['x_size'], data['y_size']).T
    plt.figure(figsize=(16, 9))
    # plt.imshow(values,
    #            # extent=[min(data['x']), 2, min(data['y']), max(data['y'])],
    #            cmap='jet')
    plt.pcolormesh(x, y, values, shading='auto', cmap='jet')
    # plt.colorbar()
    plt.title('z field')
    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)
        plt.close()

def plot_profile(profile, path = None):
    plt.figure(figsize=(8, 6))
    plt.plot(profile[:,0], profile[:,1], '-')
    plt.grid(True)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()
    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)
        plt.close()

def plot_z_field_and_profile(z_field = None, profile = None, ax = None, path = None):

    if z_field is not None or profile is not None:

        if ax is not None:
            plt.sca(ax)
        else:
            # Create figure
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 4.5))

        if z_field is not None:
            values = z_field['values'][:,2].reshape(z_field['x_size'], z_field['y_size']).T
            x = z_field['values'][:,0].reshape(z_field['x_size'], z_field['y_size']).T
            y = z_field['values'][:,1].reshape(z_field['x_size'], z_field['y_size']).T

            plt.pcolormesh(x, y, values, shading = 'auto', cmap='turbo')

        if profile is not None:
            plt.plot(profile[:,0], profile[:,1], color = 'w', linewidth = 0.5)

            plt.axvline(x = 2, color = 'w', linestyle = '--', linewidth = 0.5)
            plt.axvline(x = 9, color = 'w', linestyle = '--', linewidth = 0.5)

        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Taper zfield')
        if path is not None:
            plt.savefig(path, bbox_inches='tight', dpi=300)
            plt.close()

def plot_power(data, ax = None, path = None):
    if ax is not None:
        plt.sca(ax)
    else:
        # Create figure
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 4.5))

    ax.plot(data['iter'], data['power'], '-o')
    plt.text(0.99, 0.05, f"maximum power = {max(data['power']):.3f}",
        horizontalalignment='right',
        verticalalignment='bottom',
        transform=ax.transAxes,
        bbox=dict(facecolor='white', alpha=0.3, edgecolor='gray'))

    ax.set_xlabel('Iteration')
    ax.set_ylabel('Power')
    ax.set_title('Power evolution')
    plt.grid(which='major', linestyle='-', alpha=0.5)
    plt.grid(which='minor', axis='y', linestyle='--', alpha=0.3)

    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)
        plt.close()

def plot_parameters_spider(data = None, ax = None, path = None):

    param_names = list(data.keys())
    param_values = list(data.values())
    nr_params = len(param_names)

    angles = [n / float(nr_params) * 2 * np.pi for n in range(nr_params)]
    angles.append(angles[0])
    param_values.append(param_values[0])

    if ax is not None:
        plt.sca(ax)
    else:
        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(projection='polar'))

    ax.plot(angles, param_values, 'o--', linewidth = 2)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(param_names)

    ax.set_ylim(0, 1)
    ax.set_yticklabels([])
    ax.grid(True)

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
    title_ax.text(0.5, 0.7, 'Design of an optimal taper',
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
    taper_height = (available_height - ver_space) * 0.5
    param_height = taper_height
    power_height = available_height - taper_height - ver_space

    # Define widths
    taper_width = (available_width - hor_space) * 0.7
    all_param_width = available_width - taper_width - hor_space
    power_width = available_width

    # Calculate positions
    taper_x = left_margin
    taper_y = 1 - top_margin - taper_height

    param_x = 1 - right_margin - all_param_width
    param_y = taper_y

    power_x = left_margin
    power_y = bottom_margin

    # Add the tapoer plot
    ax = figure.add_axes([taper_x, taper_y, taper_width, taper_height])
    plot_z_field_and_profile(sim_data['z_field'], sim_data['profile'], ax = ax)

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

    # Add the power plot
    ax = figure.add_axes([power_x, power_y, power_width, power_height])
    if optimization_data is None:
        ax.scatter([1], sim_data['power'])
    else:
        plot_power(optimization_data['powers'], ax=ax)

    update_fontsize(figure, 14)

    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)

    plt.show()

def plot_results_nm(sim_data, optimization_data = None, path = None):

    # Get primary monitor size
    monitor = get_monitors()[0]
    width = monitor.width / 100  # Convert pixels to inches (approximate)
    height = monitor.height / 100

    figure = plt.figure(figsize=(width*0.8, height), dpi=300)

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
    title_ax.text(0.5, 0.7, 'Design of an optimal taper',
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
    taper_height = (available_height - ver_space) * 0.5
    param_height = taper_height
    power_height = available_height - taper_height - ver_space

    # Define widths
    param_width = param_height
    taper_width = available_width - param_width - hor_space
    power_width = available_width

    # Calculate positions
    taper_x = left_margin
    taper_y = 1 - top_margin - taper_height

    param_x = 1 - right_margin - param_width
    param_y = taper_y

    power_x = left_margin
    power_y = bottom_margin

    # Add the tapoer plot
    ax = figure.add_axes([taper_x, taper_y, taper_width, taper_height])
    plot_z_field_and_profile(sim_data['z_field'], sim_data['profile'], ax = ax)

    # Add the parameters evolution
    ax = figure.add_axes([param_x, param_y, param_width, param_height], projection='polar')
    if optimization_data is None:
        params = {'x': 0.1, 'y': 0.3, 'z': 0.7}
    else:
        params = optimization_data['best_parameters']
    plot_parameters_spider(data = params, ax = ax)

    # Add the power plot
    ax = figure.add_axes([power_x, power_y, power_width, power_height])
    if optimization_data is None:
        ax.scatter([1], sim_data['power'])
    else:
        plot_power(optimization_data['powers'], ax=ax)

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
