#%% Imports
import pandas as pd, numpy as np, os, matplotlib.pyplot as plt, uuid, shutil
from simulation.ngspice import Ngspice_simulator
from screeninfo import get_monitors

#%% Simulation
def single_simulation(parameters, **kwargs):
    template_file = kwargs['template_file']
    results_path = kwargs['results_path']
        
    simulation_dir = os.path.join(results_path, f'simulations_{str(uuid.uuid4())[-8:]}')
    if not os.path.exists(simulation_dir):
        os.mkdir(simulation_dir)
    
    simulation_file = replace_parameters(template_file, parameters, simulation_dir, 'filter.cir')
    results_file = os.path.join(simulation_dir, 'filter_response.txt')
    
    sim = Ngspice_simulator()
    sim.simulate_single_file(file_path = simulation_file, results_dir = simulation_dir)
    results = parse_results_file(results_file)
    
    # ref_data = None
    # if 'ref_data' in kwargs.keys():
    #     ref_data = kwargs['ref_data']
    
    # plot_magnitude(results, ref_data)
    # plot_phase(results, ref_data)
    
    if os.path.exists(simulation_dir):
        shutil.rmtree(simulation_dir, ignore_errors=True)   
    
    return results

def simulate_multiple_parameters(parameters, **kwargs):
    
    ref_data = None
    if 'ref_data' in kwargs.keys():
        ref_data = kwargs['ref_data']
        
    results = []
    
    for p in parameters:
                    
        # Run simulation
        try:
            sim_result = single_simulation(p, **kwargs)
            if ref_data is None:
                sim_result['metrics'] = calculate_optimization_metric(sim_result)
            else:
                sim_result['metrics'] = calculate_calibration_metric(sim_result, ref_data)
        except:
            sim_result = {}
            sim_result['metrics'] = {'total_error': 1e15}
            
        sim_result['parameters'] = p
        results.append(sim_result)
    
    responses = {'data': results, 'metrics': [item['metrics']['total_error'] for item in results]}
    
    return responses

def calculate_calibration_metric(sim_data, ref_data):
    magnitude_interpolated = np.interp(ref_data['freq'], sim_data['freq'], sim_data['magnitude_db'])
    phase_interpolated = np.interp(ref_data['freq'], sim_data['freq'], sim_data['phase'])
    
    magnitude_min = min(ref_data['magnitude'])
    magnitude_max = max(ref_data['magnitude'])
    
    phase_min = min(ref_data['phase'])
    phase_max = max(ref_data['phase'])
    
    ref_magnitude = (ref_data['magnitude'] - magnitude_min) / (magnitude_max - magnitude_min)
    ref_phase = (ref_data['phase'] - phase_min) / (phase_max - phase_min)
    
    sim_magnitude = (magnitude_interpolated - magnitude_min) / (magnitude_max - magnitude_min)
    sim_phase = (phase_interpolated - phase_min) / (phase_max - phase_min)
    
    magnitude_error = np.sqrt(np.mean((ref_magnitude - sim_magnitude)**2))
    phase_error = np.sqrt(np.mean((ref_phase - sim_phase)**2))
    total_error = magnitude_error + phase_error
    
    return {'magnitude_error': magnitude_error,
            'phase_error': phase_error,
            'total_error': total_error}   

def calculate_optimization_metric(results):
    
    huge_metric = 1e10
    
    targets = {'cutoff_freq': 10e3,
               'dc_gain': 20,
               'phase_margin': 45,
               'stop_gain': -60}
    
    try:
        cutoff_freq_error = np.abs(targets['cutoff_freq'] - results['cutoff_freq']) / targets['cutoff_freq']
        dc_gain_error = np.abs(targets['dc_gain'] - results['dc_gain']) / targets['dc_gain']
        phase_margin_error = max(0, (targets['phase_margin'] - results['phase_margin'])/targets['phase_margin'])
        stop_gain_error = max(0, (results['stop_gain'] - targets['stop_gain'])/abs(results['stop_gain']))
        total_error = cutoff_freq_error + dc_gain_error + phase_margin_error + stop_gain_error
    except:
        cutoff_freq_error = results['cutoff_freq']
        dc_gain_error = results['dc_gain']
        phase_margin_error = results['phase_margin']
        stop_gain_error = results['stop_gain']
        total_error = huge_metric
    
    return {'targets': targets,
            'cutoff_freq_error': cutoff_freq_error,
            'dc_gain_error': dc_gain_error,
            'phase_margin_error': phase_margin_error,
            'stop_gain_error': stop_gain_error,
            'total_error': total_error}    

def replace_parameters(template_path, params_dict, output_dir, filename = None):
    # Read template file
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Replace each parameter
    for param, value in params_dict.items():
        placeholder = f"<<{param}>>"
        template_content = template_content.replace(placeholder, str(value))
    
    # Generate output filename if not provided
    if filename is None:
        filename = 'chebyshev_filter.cir'
    
    # Create full output path
    output_path = os.path.join(output_dir, filename)
    
    # Write the modified content
    with open(output_path, 'w') as f:
        f.write(template_content)
        
    return output_path

def parse_results_file(file):
    # Read the data, skipping the header lines
    data = np.loadtxt(file, comments='#')
    freq = data[:, 0]
    output_real = data[:, 1]
    output_imag = data[:, 2]
    
    # Calculate magnitude and phase
    magnitude = np.sqrt(output_real**2 + output_imag**2) * 1e-4
    magnitude_db = 20 * np.log10(magnitude)
    phase = np.arctan2(output_imag, output_real) * 180 / np.pi
    
    # Find the gain at different frequencies
    dc_gain = magnitude_db[0]  # Gain at lowest frequency
    max_gain = np.max(magnitude_db)
    min_gain = np.min(magnitude_db)
    
    # Find the -3dB frequency (cutoff frequency)
    cutoff_idx = np.where(magnitude_db <= max_gain - 3)[0][0]
    cutoff_freq = freq[cutoff_idx]
    
    # Find the stop gain (at 100kHz)
    stop_freq = 100e3
    stop_idx = np.argmin(np.abs(freq - stop_freq))
    stop_gain = magnitude_db[stop_idx]
    
    # Find unity gain frequency (0 dB crossing)
    unity_gain_idx = np.where(np.diff(np.signbit(magnitude_db)))[0]
    if len(unity_gain_idx) > 0:
        unity_gain_freq = freq[unity_gain_idx[0]]
        # Find phase margin at unity gain frequency
        phase_margin = 180 + phase[unity_gain_idx[0]]  # Add 180 because we want margin from -180°
    else:
        unity_gain_freq = None
        phase_margin = None
        
    results = {'freq': freq,
               'output_real': output_real,
               'output_imag': output_imag,
               'magnitude': magnitude,
               'magnitude_db': magnitude_db,
               'phase': phase,
               'dc_gain': dc_gain,
               'cutoff_freq': cutoff_freq,
               'unity_gain_freq': unity_gain_freq,
               'phase_margin': phase_margin,
               'stop_gain': stop_gain}
    
    return results

#%% Plotting
def plot_magnitude(data, ref_data = None, ax = None, path = None):
    if ax is not None:
        plt.sca(ax)
    else:
        # Create figure
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 5))
    
    if ref_data is not None:
        ax.scatter(ref_data['freq'], ref_data['magnitude'], marker='o', facecolors='none', edgecolors='black', label = 'Reference data')
        # ax.plot(ref_data['freq'], ref_data['magnitude'], label = 'Reference data')
   
    if data is not None:
        # ax.scatter(data['freq'], data['magnitude'], marker='o', label = 'Simulation data')
        ax.plot(data['freq'], data['magnitude_db'], label = 'Simulation data')
    
    # ax.axvline(x=data['cutoff_freq'], color='r', linestyle='--', label=f"-3dB at {data['cutoff_freq']:.1f} Hz")
    
    ax.set_xlabel('Frequency [Hz]')
    ax.set_ylabel('Magnitude [db]')
    ax.set_title('Magnitude')
    ax.set_xscale('log')
    plt.grid(which='major', linestyle='-', alpha=0.5)
    plt.grid(which='minor', axis='x', linestyle='--', alpha=0.3)
    
    if data is not None and ref_data is not None:
        plt.legend(loc = 'upper right')
    
    # plt.show()
    
    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)
        
def plot_phase(data, ref_data = None, ax = None, path = None):
    if ax is not None:
        plt.sca(ax)
    else:
        # Create figure
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 5))
    
    if ref_data is not None:
        ax.scatter(ref_data['freq'], ref_data['phase'], marker='o', facecolors='none', edgecolors='black', label = 'Reference data')
        # ax.plot(ref_data['freq'], ref_data['phase'], label = 'Reference data')
        
    if data is not None:
        # ax.scatter(data['freq'], data['phase'], marker='o', label = 'Simulation data')
        ax.plot(data['freq'], data['phase'], label = 'Simulation data')

    # ax.axvline(x=data['unity_gain_freq'], color='r', linestyle='--', label=f"unity gain at {data['unity_gain_freq']:.1f} Hz")
    
    ax.set_xlabel('Frequency [Hz]')
    ax.set_ylabel('Phase [deg]')
    ax.set_title('Phase')
    ax.set_xscale('log')
    plt.grid(which='major', linestyle='-', alpha=0.5)
    plt.grid(which='minor', axis='x', linestyle='--', alpha=0.3)
    if data is not None and ref_data is not None:
        plt.legend(loc = 'upper right')
    
    # plt.show()
    
    if path is not None:
        plt.savefig(path, bbox_inches='tight', dpi=300)
    
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
        
def plot_parameter_evolution(data, path = None):
    
    # Get primary monitor size
    monitor = get_monitors()[0]
    width = monitor.width / 100  # Convert pixels to inches (approximate)
    height = monitor.height / 100
    
    figure = plt.figure(figsize=(width, height), dpi=300)
    
    # params = params[params['iter'] >= params['iter'].max() - 5]
    params = data.drop(['iter', 'metric'], axis = 1)
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
    
    
def plot_results(sim_data, ref_data, optimization_data = None, path = None):
    
    # Get primary monitor size
    monitor = get_monitors()[0]
    width = monitor.width / 100  # Convert pixels to inches (approximate)
    height = monitor.height / 100
    
    figure = plt.figure(figsize=(width, height), dpi=300)
    
    # Margins
    left_margin = 0.05
    right_margin = 0.01
    top_margin = 0.07
    bottom_margin = 0.03
    
    # Create a base subplot to hold the margin rectangles
    ax = figure.add_axes([0, 0, 1, 1])
    ax.axis('off')
    
    # Add title in the top margin
    title_ax = figure.add_axes([0, 1-top_margin, 1, top_margin])
    title_ax.axis('off')
    title_ax.text(0.5, 0.7, 'Calibration of a 7th order Chebyshev filter', 
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
    hor_space = 0.05
    
    # Define heights relative to available height
    magnitude_height = (available_height - ver_space) * 0.5
    phase_height = magnitude_height
    mismatch_height = magnitude_height
    param_height = magnitude_height
    
    # Define widths
    magnitude_width = available_width * 0.35
    phase_width = magnitude_width
    mismatch_width = available_width - magnitude_width - hor_space
    all_param_width = mismatch_width
    
    # Calculate positions
    magnitude_x = left_margin
    magnitude_y = 1 - top_margin - magnitude_height
    
    phase_x = magnitude_x
    phase_y = bottom_margin
    
    mismatch_x = 1 - right_margin - mismatch_width
    mismatch_y = 1 - top_margin - mismatch_height
    
    param_x = mismatch_x
    param_y = bottom_margin
    
    # Add the magnitude plot
    ax = figure.add_axes([magnitude_x, magnitude_y, magnitude_width, magnitude_height])
    plot_magnitude(sim_data, ref_data, ax = ax)
    
    # Add the phase plot
    ax = figure.add_axes([phase_x, phase_y, phase_width, phase_height])
    plot_phase(sim_data, ref_data, ax=ax)
    
    # Add the mismatch plot
    ax = figure.add_axes([mismatch_x, mismatch_y, mismatch_width, mismatch_height])
    if optimization_data is not None:
        metrics = optimization_data['metrics']
        ax.plot(metrics['iter'], metrics['magnitude_error'], '-o', label = 'Magnitude')
        ax.plot(metrics['iter'], metrics['phase_error'], '-o', label = 'Phase')
        ax.plot(metrics['iter'], metrics['total_error'], '-o', label = 'Total')
        ax.legend(loc = 'upper right')
        ax.set_xlabel('iteration')
        ax.set_ylabel('RMSE')
        ax.set_yscale('log')
        plt.grid(which='major', linestyle='--', alpha=0.5)
        plt.grid(which='minor', axis='y', linestyle='--', alpha=0.3)
        plt.title('Mismatch between simulation and reference data', fontsize = 16)

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
        params = params.drop(['iter', 'metric'], axis = 1)
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
            
    update_fontsize(figure, 12)

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

def create_video_from_pngs(figures_path, output_path, output_name='output.mp4', fps=5):
    import cv2
    import os
    import re
    from PIL import Image
    
    # Get and sort PNG files
    png_files = [f for f in os.listdir(figures_path) if f.endswith('.png')]
    png_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))
    
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
        