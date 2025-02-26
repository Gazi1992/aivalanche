#%% Imports
import os, numpy as np, matplotlib.pyplot as plt, pandas as pd
from matplotlib.style import context
from matplotlib import cm

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
            if y_scale == 'log':
                ax.set_yscale('log')
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

# Plot the test function 3d and 2d
def plot_function_2d_3d(func, x_range, y_range, title, points=100, view_angle=(30, 45)):
    """
    Creates a combined figure with 3D surface plot, contour plot, and heatmap side by side
    """
    x = np.linspace(x_range[0], x_range[1], points)
    y = np.linspace(y_range[0], y_range[1], points)
    X, Y = np.meshgrid(x, y)

    Z = np.zeros_like(X)
    for i in range(points):
        for j in range(points):
            Z[i,j] = func(X[i,j], Y[i,j])

    # Create a figure with three subplots side by side
    fig = plt.figure(figsize=(24, 8))

    # 3D Surface plot
    ax1 = fig.add_subplot(131, projection='3d')
    surface = ax1.plot_surface(X, Y, Z, cmap=cm.viridis, alpha=0.8)
    fig.colorbar(surface, ax=ax1, shrink=0.5, aspect=5)
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('f(X,Y)')
    ax1.view_init(*view_angle)
    ax1.set_title('3D Surface')

    # Contour plot
    ax2 = fig.add_subplot(132)
    contour = ax2.contour(X, Y, Z, levels=20, cmap=cm.viridis)
    fig.colorbar(contour, ax=ax2, shrink=0.5, aspect=5)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_title('Contour Plot')

    # Heatmap
    ax3 = fig.add_subplot(133)
    heatmap = ax3.imshow(Z, extent=[x_range[0], x_range[1], y_range[0], y_range[1]],
                        origin='lower', cmap=cm.viridis, aspect='auto')
    fig.colorbar(heatmap, ax=ax3, shrink=0.5, aspect=5)
    ax3.set_xlabel('X')
    ax3.set_ylabel('Y')
    ax3.set_title('Heatmap')

    # Add main title
    plt.suptitle(title, fontsize=16, y=1.05)
    plt.tight_layout()
    plt.show()

    return fig, (ax1, ax2, ax3)

def plot_evolution_2d(data, function_configs, function_name, parameter_names, iteration = None, dpi = 300):
    """
    Creates a heatmap of the 2D function with optimization points plotted on top.

    Args:
        data: DataFrame containing the columns 'x', 'y', 'iter', and 'metric'
        function_configs: Dictionary containing function configurations
        function_name: Name of the function from function_configs
        parameter_names: List of parameter names
        iter_value: Specific iteration to plot. If None, plots the last iteration
    """
    config = function_configs[function_name]
    bounds = config['bounds']

    # Filter data for specific iteration
    if iteration is None:
        iteration = data['iter'].max()
    plot_data = data[data['iter'] == iteration].copy()

    # Create meshgrid for function visualization
    points = 1000
    x_grid = np.linspace(bounds['min'][0], bounds['max'][0], points)
    y_grid = np.linspace(bounds['min'][1], bounds['max'][1], points)
    X, Y = np.meshgrid(x_grid, y_grid)

    # Evaluate function on grid
    Z = np.zeros_like(X)
    for i in range(points):
        for j in range(points):
            Z[i,j] = config['func'](X[i,j], Y[i,j])

    # Create figure
    fig = plt.figure(figsize=(8, 6))

    # Plot function heatmap
    plt.imshow(Z, extent=[bounds['min'][0], bounds['max'][0], bounds['min'][1], bounds['max'][1]],
              origin='lower', cmap='viridis', aspect='equal')
    plt.colorbar(label='Function Value')

    # Create legend entries list
    legend_elements = []
    legend_labels = []

    # Add best point found and optimization info
    best_point = plot_data.loc[plot_data['metric'].idxmin()]

    # Plot trials and add to legend
    trials = plt.scatter(plot_data['x'], plot_data['y'], c='red', s=50, alpha=1,
                        edgecolors='white', linewidth=0.5)
    legend_elements.append(trials)
    legend_labels.append('Trials')

    # Add known minima if available and get global minimum value
    try:
        for item in config['global_minimum_params']:
            min_point = plt.plot([item[0]], [item[1]], 'g*', markersize=10)[0]
        legend_elements.append(min_point)
        legend_labels.append('Global minimum')
        global_minimum_value = config['global_minimum_value']
    except:
        global_minimum_value = None

    # Add optimization info to legend
    info_str = '\n'.join([
        f'Iteration: {iteration}',
        f'Best found value: {best_point["metric"]:.4e}',
        f'Global minimum: {"unknown" if global_minimum_value is None else f"{global_minimum_value:.4e}"}',
        f'Deviation: {np.abs(best_point["metric"] - global_minimum_value):.4e}' if global_minimum_value is not None else ''
    ])
    legend_elements.append(plt.plot([], [], ' ')[0])  # Empty line for text
    legend_labels.append(info_str)

    plt.xlabel(parameter_names[0])
    plt.ylabel(parameter_names[1])
    plt.title(f'{function_name.replace("_", " ").title()} Function Optimization')
    plt.legend(legend_elements, legend_labels, loc='lower center')
    plt.grid(True, alpha=0.1)
    plt.tight_layout()

    return fig

def plot_evolution_2d_with_metrics(data, function_configs, function_name, parameter_names, iteration=None, y_scale='log',
                                   upper_threshold=1e10, lower_threshold=-1e10, dpi=300):
    """
    Creates a figure with two subplots: 2D heatmap and metric evolution
    """
    # Create figure with two subplots
    fig = plt.figure(figsize=(16, 6))

    # Left subplot: 2D heatmap
    plt.subplot(121)
    config = function_configs[function_name]
    bounds = config['bounds']

    if iteration is None:
        iteration = data['iter'].max()
    plot_data = data[data['iter'] == iteration].copy()

    points = 1000
    x_grid = np.linspace(bounds['min'][0], bounds['max'][0], points)
    y_grid = np.linspace(bounds['min'][1], bounds['max'][1], points)
    X, Y = np.meshgrid(x_grid, y_grid)

    Z = np.zeros_like(X)
    for i in range(points):
        for j in range(points):
            Z[i,j] = config['func'](X[i,j], Y[i,j])

    plt.imshow(Z, extent=[bounds['min'][0], bounds['max'][0], bounds['min'][1], bounds['max'][1]],
              origin='lower', cmap='viridis', aspect='equal')
    plt.colorbar(label='Function Value')

    legend_elements = []
    legend_labels = []

    best_point = plot_data.loc[plot_data['metric'].idxmin()]

    trials = plt.scatter(plot_data['x'], plot_data['y'], c='red', s=50, alpha=1,
                        edgecolors='white', linewidth=0.5)
    legend_elements.append(trials)
    legend_labels.append('Trials')

    try:
        for item in config['global_minimum_params']:
            min_point = plt.plot([item[0]], [item[1]], 'g*', markersize=10)[0]
        legend_elements.append(min_point)
        legend_labels.append('Global minimum')
        global_minimum_value = config['global_minimum_value']
    except:
        global_minimum_value = None

    info_str = '\n'.join([
        f'Iteration: {iteration}',
        f'Best found value: {best_point["metric"] + global_minimum_value:.4e}',
        f'Global minimum: {"unknown" if global_minimum_value is None else f"{global_minimum_value:.4e}"}',
        f'Deviation: {best_point["metric"]:.4e}' if global_minimum_value is not None else ''
    ])
    legend_elements.append(plt.plot([], [], ' ')[0])
    legend_labels.append(info_str)

    plt.xlabel(parameter_names[0])
    plt.ylabel(parameter_names[1])
    plt.title(f'{function_name.replace("_", " ").title()} Function Optimization')
    plt.legend(legend_elements, legend_labels, loc='lower center')
    plt.grid(True, alpha=0.1)

    # Right subplot: Metric evolution
    plt.subplot(122)
    plot_data = data[data['iter'] <= iteration].copy()
    metrics = plot_data['metric']
    iterations = plot_data['iter']
    mask = (metrics > lower_threshold) & (metrics < upper_threshold)
    with plt.style.context('seaborn-v0_8-bright'):
        plt.scatter(iterations[mask], metrics[mask])
        plt.title('Metric Evolution')
        plt.xlabel('Iterations')
        plt.ylabel('Metrics')
        plt.yscale(y_scale)
        plt.grid(which='both', axis='both')

    plt.tight_layout()
    return fig

def create_plot_evolution_2d_video(data, function_configs, function_name, parameter_names,
                                 output_path='evolution.gif', fps=5, working_dir = None):  # Increased default fps
    """
    Create a video of the optimization evolution
    """
    frame_args = {
        'data': data,
        'function_configs': function_configs,
        'function_name': function_name,
        'parameter_names': parameter_names
    }

    create_video(
        frame_generator_func=plot_evolution_2d_with_metrics, #plot_evolution_2d,
        frame_generator_args=frame_args,
        iterations=range(data['iter'].min(), data['iter'].max() + 1),
        output_path=output_path,
        fps=fps,
        dpi=300,
        working_dir = working_dir
        )

def generate_single_frame(iter_value, temp_dir, frame_generator_func, frame_generator_args):
    """Memory-optimized helper function to generate and save a single frame"""
    import matplotlib.pyplot as plt

    # Generate the figure
    fig = frame_generator_func(iteration=iter_value, **frame_generator_args)

    # Save frame
    frame_path = os.path.join(temp_dir, f'frame_{iter_value:04d}.png')
    fig.savefig(frame_path, dpi=300, bbox_inches='tight')

    # Clean up
    plt.close('all')
    fig.clf()
    del fig

    return frame_path

def create_video(frame_generator_func, frame_generator_args, iterations, output_path,
                working_dir=None, fps=5, max_workers=None, dpi=300):
    """
    Create a video using parallel processing with optional working directory.
    """
    import tempfile
    import cv2
    import os
    from tqdm import tqdm
    from concurrent.futures import ProcessPoolExecutor
    import numpy as np
    import imageio
    from PIL import Image

    if working_dir:
        os.makedirs(working_dir, exist_ok=True)
        frame_dir = working_dir
        cleanup_dir = False
    else:
        temp_dir = tempfile.TemporaryDirectory()
        frame_dir = temp_dir.name
        cleanup_dir = True

    try:
        print("Generating frames in parallel...")
        frame_paths = []
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    generate_single_frame,
                    iter_num,
                    frame_dir,
                    frame_generator_func,
                    frame_generator_args
                )
                for iter_num in iterations
            ]
            for future in tqdm(futures, desc="Processing frames"):
                frame_paths.append(future.result())

        frame_paths.sort()

        print("Creating output file...")
        if output_path.endswith('.gif'):
            with Image.open(frame_paths[0]) as img:
                size = img.size

            frames = []
            for frame_path in tqdm(frame_paths, desc="Reading frames"):
                with Image.open(frame_path) as img:
                    if img.size != size:
                        img = img.resize(size, Image.Resampling.LANCZOS)
                    frames.append(np.array(img))

            print("Saving GIF...")
            with Image.open(output_path) as im:
                im.save(
                    output_path,
                    save_all=True,
                    append_images=[Image.fromarray(f) for f in frames[1:]],
                    duration=int(1000/fps),
                    loop=0,
                    optimize=False,
                    quality=95
                )
        else:
            first_frame = cv2.imread(frame_paths[0])
            height, width, layers = first_frame.shape

            # Use mp4v codec directly instead of trying H264 first
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(
                output_path,
                fourcc,
                fps,
                (width, height)
            )

            if not video.isOpened():
                raise RuntimeError("Failed to initialize VideoWriter")

            for frame_path in tqdm(frame_paths, desc="Adding frames to video"):
                frame = cv2.imread(frame_path)
                if frame.shape[:2] != (height, width):
                    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LANCZOS4)
                video.write(frame)

            video.release()
    finally:
        if cleanup_dir:
            temp_dir.cleanup()

    print(f'File saved to {output_path}')

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

def plot_simplex(simplex = None, iteration = None, metrics = None, function_configs = None, function_name = None, save_path = None):
    if simplex is not None:
        fig = plt.figure(figsize=(10, 8))

        config = function_configs[function_name]
        bounds = config['bounds']

        points = 1000
        x_grid = np.linspace(bounds['min'][0], bounds['max'][0], points)
        y_grid = np.linspace(bounds['min'][1], bounds['max'][1], points)
        X, Y = np.meshgrid(x_grid, y_grid)

        Z = np.zeros_like(X)
        for i in range(points):
            for j in range(points):
                Z[i,j] = config['func'](X[i,j], Y[i,j])

        plt.imshow(Z, extent=[bounds['min'][0], bounds['max'][0], bounds['min'][1], bounds['max'][1]],
                  origin='lower', cmap='viridis', aspect='equal')
        plt.colorbar(label='Function Value')

        legend_elements = []
        legend_labels = []

        # Plot vertices
        vertices = plt.scatter(simplex[:,0], simplex[:,1], c = 'red', s = 100)
        legend_elements.append(vertices)
        legend_labels.append('Simplex')

        # Plot edges
        for i in range(simplex.shape[0]):
            for j in range(i + 1, simplex.shape[0]):
                plt.plot([simplex[i,0], simplex[j,0]], [simplex[i,1], simplex[j,1]], 'r--')

        try:
            for item in config['global_minimum_params']:
                min_point = plt.plot([item[0]], [item[1]], 'g*', markersize=10)[0]
            legend_elements.append(min_point)
            legend_labels.append('Global minimum')
            global_minimum_value = config['global_minimum_value']
        except:
            global_minimum_value = None

        info_str = '\n'.join([
            f'Iteration: {iteration}',
            f'Best found value: {metrics[0] + global_minimum_value:.4e}',
            f'Global minimum: {"unknown" if global_minimum_value is None else f"{global_minimum_value:.4e}"}',
            f'Deviation: {metrics[0]:.4e}' if global_minimum_value is not None else ''
        ])
        legend_elements.append(plt.plot([], [], ' ')[0])
        legend_labels.append(info_str)

        plt.xlabel('x')
        plt.ylabel('y')
        plt.title(f'{function_name.replace("_", " ").title()} Function Optimization')
        plt.legend(legend_elements, legend_labels, loc='lower center')
        plt.grid(True, alpha=0.1)

        if save_path is not None:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        else:
            plt.show()
