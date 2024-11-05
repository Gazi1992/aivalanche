"""
Visualization functions for airfoil analysis including polar plots,
pressure distribution, boundary layer properties, and parameter studies
"""

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from nurbs import Nurbs

def rotate_coordinates(x, y, alpha):
    """
    Rotate coordinates by angle alpha (in degrees)
    
    Args:
        x, y: Coordinates to rotate
        alpha: Angle in degrees
    Returns:
        x_rot, y_rot: Rotated coordinates
    """
    alpha_rad = np.deg2rad(alpha)
    cos_a = np.cos(alpha_rad)
    sin_a = np.sin(alpha_rad)
    
    x_rot = x * cos_a - y * sin_a
    y_rot = x * sin_a + y * cos_a
    
    return x_rot, y_rot

def plot_airfoil(airfoil, show_panels=False, title=None, alpha=None):
    """
    Plot airfoil shape, optionally at a specified angle of attack
    
    Args:
        airfoil: Array containing [x_lower, y_lower, x_upper, y_upper] coordinates
        show_panels: Boolean to show panel points
        title: Optional plot title
        alpha: Angle of attack in degrees (optional)
    """
    plt.figure(figsize=(10, 5))
    
    x_l = airfoil[0]    # x-coordinates of lower surface
    y_l = airfoil[1]    # y-coordinates of lower surface
    x_u = airfoil[2]    # x-coordinates of upper surface
    y_u = airfoil[3]    # y-coordinates of upper surface
    
    
    if alpha is not None:
        x_l, y_l = rotate_coordinates(x_l, y_l, alpha)
        x_u, y_u = rotate_coordinates(x_u, y_u, alpha)
        
        if title:
            title = f"{title} (α = {alpha}°)"
        else:
            title = f"Airfoil Shape (α = {alpha}°)"
    
    plt.plot(x_l, y_l, 'b-', label='Lower surface')
    plt.plot(x_u, y_u, 'r-', label='Upper surface')
    
    if show_panels:
        plt.plot(x_l, y_l, 'k.', markersize=2)
        plt.plot(x_u, y_u, 'k.', markersize=2)
    
    if alpha is not None:
        arrow_x = min(x_l.min(), x_u.min()) - 0.2
        arrow_y = 0
        arrow_length = 0.2
        arrow_angle = alpha
        
        dx = arrow_length * np.cos(np.deg2rad(arrow_angle))
        dy = arrow_length * np.sin(np.deg2rad(arrow_angle))
        
        plt.arrow(arrow_x, arrow_y, dx, dy, 
                 head_width=0.02, head_length=0.02, 
                 fc='g', ec='g', label='Flow direction')
        
        plt.xlim(arrow_x - 0.1, max(x_l.max(), x_u.max()) + 0.1)
    
    plt.axis('equal')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlabel('x/c')
    plt.ylabel('y/c')
    plt.title(title or 'Airfoil Shape')
    plt.legend()
    plt.show()

def plot_polar(results):
    """Plot CL vs alpha and drag polar"""
    if not results['convergence']:
        print("No data to plot: simulation did not converge")
        return
        
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Sort data by alpha for smoother plots
    sort_idx = np.argsort(results['alpha'])
    alpha = results['alpha'][sort_idx]
    cl = results['cl'][sort_idx]
    cd = results['cd'][sort_idx]
    
    # CL vs alpha
    ax1.plot(alpha, cl, 'b-o', markersize=4)
    ax1.set_xlabel('α (deg)')
    ax1.set_ylabel('CL')
    ax1.grid(True)
    ax1.set_title('Lift Curve')
    
    # Drag polar
    ax2.plot(cd, cl, 'r-o', markersize=4)
    ax2.set_xlabel('CD')
    ax2.set_ylabel('CL')
    ax2.grid(True)
    ax2.set_title('Drag Polar')
    
    plt.tight_layout()
    plt.show()

def plot_pressure_distribution(cp_data):
    """Plot pressure coefficient distribution"""
    if not cp_data['convergence']:
        print("No pressure data to plot: analysis did not converge")
        return
        
    plt.figure(figsize=(8, 6))
    
    mask_upper = cp_data['upper']
    mask_lower = cp_data['lower']
    
    plt.plot(cp_data['x'][mask_upper], cp_data['cp'][mask_upper], 'b-', label='Upper surface')
    plt.plot(cp_data['x'][mask_lower], cp_data['cp'][mask_lower], 'r-', label='Lower surface')
    
    plt.gca().invert_yaxis()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlabel('x/c')
    plt.ylabel('Cp')
    plt.title('Pressure Coefficient Distribution')
    plt.legend()
    plt.show()

def plot_boundary_layer(bl_data):
    """Plot boundary layer properties"""
    if not bl_data['convergence']:
        print("No boundary layer data to plot: analysis did not converge")
        return
        
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
    
    # Displacement thickness
    ax1.plot(bl_data['upper']['x'], bl_data['upper']['Dstar'], 'b-', label='Upper')
    ax1.plot(bl_data['lower']['x'], bl_data['lower']['Dstar'], 'r-', label='Lower')
    ax1.set_xlabel('x/c')
    ax1.set_ylabel('δ* (displacement thickness)')
    ax1.grid(True)
    ax1.legend()
    
    # Momentum thickness
    ax2.plot(bl_data['upper']['x'], bl_data['upper']['theta'], 'b-', label='Upper')
    ax2.plot(bl_data['lower']['x'], bl_data['lower']['theta'], 'r-', label='Lower')
    ax2.set_xlabel('x/c')
    ax2.set_ylabel('θ (momentum thickness)')
    ax2.grid(True)
    ax2.legend()
    
    # Shape factor
    ax3.plot(bl_data['upper']['x'], bl_data['upper']['H'], 'b-', label='Upper')
    ax3.plot(bl_data['lower']['x'], bl_data['lower']['H'], 'r-', label='Lower')
    ax3.set_xlabel('x/c')
    ax3.set_ylabel('H (shape factor)')
    ax3.grid(True)
    ax3.legend()
    
    # Skin friction coefficient
    ax4.plot(bl_data['upper']['x'], bl_data['upper']['Cf'], 'b-', label='Upper')
    ax4.plot(bl_data['lower']['x'], bl_data['lower']['Cf'], 'r-', label='Lower')
    ax4.set_xlabel('x/c')
    ax4.set_ylabel('Cf (skin friction)')
    ax4.grid(True)
    ax4.legend()
    
    plt.tight_layout()
    plt.show()

def plot_aero_performance(results):
    """
    Plot aerodynamic performance metrics (L/D ratio and moment coefficient)
    
    Args:
        results: Dictionary containing simulation results with alpha, cl, cd, and cm data
    """
    if not results['convergence']:
        print("No data to plot: simulation did not converge")
        return
        
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Sort data by alpha for smoother plots
    sort_idx = np.argsort(results['alpha'])
    alpha = results['alpha'][sort_idx]
    cl = results['cl'][sort_idx]
    cd = results['cd'][sort_idx]
    
    # Calculate L/D ratio
    ld_ratio = cl/cd
    
    # L/D ratio vs alpha
    ax1.plot(alpha, ld_ratio, 'g-o', markersize=4)
    ax1.set_xlabel('α (deg)')
    ax1.set_ylabel('L/D')
    ax1.grid(True)
    ax1.set_title('L/D Ratio vs Angle of Attack')
    
    # Add horizontal line at max L/D
    max_ld = np.max(ld_ratio)
    ax1.axhline(y=max_ld, color='r', linestyle='--', alpha=0.5)
    ax1.text(alpha[0], max_ld, f'Max L/D = {max_ld:.2f}', 
             verticalalignment='bottom')
    
    # Moment coefficient vs alpha if available
    if 'cm' in results:
        cm = results['cm'][sort_idx]
        ax2.plot(alpha, cm, 'm-o', markersize=4)
        ax2.set_xlabel('α (deg)')
        ax2.set_ylabel('CM')
        ax2.grid(True)
        ax2.set_title('Moment Coefficient vs Angle of Attack')
        
        # Add horizontal line at CM = 0
        ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def plot_parallel_coordinates(df, color_column='ld', params_df=None, exclude = []):
    """
    Create interactive parallel coordinates plot of simulation results
    
    Args:
        df: DataFrame containing simulation results
        color_column: Column name to use for color mapping
        params_df: Optional DataFrame with parameter specifications
    """
    
    df = df.dropna()
    
    # Identify parameter columns
    param_cols = list(params_df['name'])
    result_cols = [col for col in df.columns if col not in param_cols and col not in exclude]

    dimensions = []
    
    # Add parameter dimensions
    for col in param_cols:
        if params_df is not None:
            param_range = params_df[params_df['name'] == col][['min', 'max']].values[0]
        else:
            param_range = [df[col].min(), df[col].max()]
            
        dimensions.append(
            dict(
                range=[param_range[0], param_range[1]],
                label=col,
                values=df[col]
            )
        )
    
    # Add result dimensions
    for col in result_cols:
        if df[col].dtype in [np.float64, np.int64]:
            dimensions.append(
                dict(
                    range=[df[col].min(), df[col].max()],
                    label=col,
                    values=df[col]
                )
            )
    
    fig = go.Figure(data=
        go.Parcoords(
            line=dict(
                color=df[color_column],
                colorscale='Viridis',
                showscale=True,
                cmin=df[color_column].min(),
                cmax=df[color_column].max()
            ),
            dimensions=dimensions
        )
    )
    
    fig.update_layout(
        title=f'Parameter Study Results (colored by {color_column})',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=600
    )
    
    return fig

def create_optimization_summary(df, normed_df, max_iter, param_names, figure_path = None):
    """
    Create summary plot showing airfoil shape, L/D evolution, and parameter evolution
    
    Args:
        df: DataFrame with original optimization data
        normed_df: DataFrame with normalized parameter values
        max_iter: Maximum iteration to consider
        param_names: List of parameter names to show
        figure_path: Optional path to save the figure
    """
    # Get best design
    filtered_df = df[df['iter'] <= max_iter]
    best_design = filtered_df.loc[filtered_df['total_metric'].idxmin()]
    
    # Create airfoil coordinates
    param_dict = {
        'ta_u': best_design['ta_u'],
        'ta_l': best_design['ta_l'],
        'tb_u': best_design['tb_u'],
        'tb_l': best_design['tb_l'],
        'alpha_b': best_design['alpha_b'],
        'alpha_c': best_design['alpha_c']
    }
    airfoil = Nurbs(param_dict)
    coords = airfoil._spline()
    
    # Create figure
    fig = plt.figure(figsize=(15 * 0.9, 8 * 0.9), dpi = 100)
    
    # Setup grid layout - adjust width_ratios based on number of parameters
    gs = fig.add_gridspec(2, len(param_names), 
                         height_ratios=[2, 1],
                         width_ratios=[1]*len(param_names))
    
    # Plot airfoil shape - spans first two columns
    ax_airfoil = fig.add_subplot(gs[0, :len(param_names)//2])
    ax_airfoil.plot(coords[0], coords[1], 'orange', label='Lower surface')
    ax_airfoil.plot(coords[2], coords[3], 'purple', label='Upper surface')
    ax_airfoil.axis('equal')
    ax_airfoil.grid(True, linestyle='--', alpha=0.5)
    ax_airfoil.set_xlabel('x/c')
    ax_airfoil.set_ylabel('y/c')
    ax_airfoil.set_title('Best Airfoil Shape')
    ax_airfoil.legend()
    
    # Plot L/D evolution with color based on constraint violation - spans last columns
    ax_ld = fig.add_subplot(gs[0, len(param_names)//2:])
    iterations = filtered_df['iter']
    ld_values = filtered_df['ld']
    
    # Split data into valid and invalid points
    valid_mask = filtered_df['geometry_metric'] == 0
    
    # Plot invalid points in red
    ax_ld.scatter(iterations[~valid_mask], ld_values[~valid_mask], 
                 c='red', s=20, alpha=0.5, label='Invalid')
    
    # Plot valid points in blue
    ax_ld.scatter(iterations[valid_mask], ld_values[valid_mask], 
                 c='green', s=20, alpha=0.5, label='Valid')
        
    ax_ld.grid(True, linestyle='--', alpha=0.5)
    ax_ld.set_xlabel('Iteration')
    ax_ld.set_ylabel('L/D Ratio')
    ax_ld.set_title('L/D Evolution')
    ax_ld.legend()
    
    # Plot parameter evolution - one subplot per parameter
    filtered_normed = normed_df[normed_df['iter'] <= max_iter]
    
    for idx, param in enumerate(param_names):
        ax_param = fig.add_subplot(gs[1, idx])
        
        # Calculate histogram
        hist, _ = np.histogram(filtered_normed[param], bins=100, range=(0, 1))
        hist = hist / hist.max()  # Normalize histogram
        
        # Plot histogram as image
        ax_param.imshow(np.atleast_2d(hist).T, 
                       aspect='auto', 
                       origin='lower',
                       extent=[0, 1, 0, 1],
                       cmap='jet')
        
        ax_param.set_xticks([])
        ax_param.set_yticks([])
        ax_param.set_xlabel(param)
        
        # if idx == 0:  # Add title only for first parameter
        #     ax_param.set_title('Parameter Evolution')
    
    plt.tight_layout()
    
    if figure_path is not None:
        fig.savefig(figure_path, dpi=100, bbox_inches='tight')
    
    plt.show()
    
def generate_single_frame(iter_num, temp_dir, df, normed_df, param_names, n_previous=10, min_alpha=0.1, max_alpha=0.8):
    """Function to generate a single frame"""
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    from nurbs import Nurbs
    
    # Create figure with fixed size and DPI
    plt.figure(figsize=(15 * 0.9, 8 * 0.9), tight_layout=True)
    
    # Setup grid layout
    gs = plt.gcf().add_gridspec(2, len(param_names), 
                               height_ratios=[2, 1],
                               width_ratios=[1]*len(param_names))
    
    # Plot airfoil shapes
    ax_airfoil = plt.subplot(gs[0, :len(param_names)//2])
    
    # Get previous best designs
    if iter_num > 0:
        start_iter = max(0, iter_num - n_previous)
        prev_iters = range(start_iter, iter_num)
        valid_prev_designs = []
        
        # Collect valid previous designs
        for prev_iter in prev_iters:
            prev_filtered_df = df[df['iter'] <= prev_iter]
            if not prev_filtered_df.empty:
                valid_prev_designs.append((prev_iter, prev_filtered_df.loc[prev_filtered_df['total_metric'].idxmin()]))
        
        # Calculate alpha values based on number of valid designs
        if valid_prev_designs:
            alpha_values = np.linspace(min_alpha, max_alpha, len(valid_prev_designs))
            
            # Plot previous airfoils
            for (_, prev_best_design), alpha in zip(valid_prev_designs, alpha_values):
                param_dict = {
                    'ta_u': prev_best_design['ta_u'],
                    'ta_l': prev_best_design['ta_l'],
                    'tb_u': prev_best_design['tb_u'],
                    'tb_l': prev_best_design['tb_l'],
                    'alpha_b': prev_best_design['alpha_b'],
                    'alpha_c': prev_best_design['alpha_c']
                }
                airfoil = Nurbs(param_dict)
                coords = airfoil._spline()
                
                # Plot previous airfoils with decreasing alpha
                ax_airfoil.plot(coords[0], coords[1], 'orange', alpha=alpha, linewidth=1)
                ax_airfoil.plot(coords[2], coords[3], 'purple', alpha=alpha, linewidth=1)
    
    # Plot current best airfoil
    filtered_df = df[df['iter'] <= iter_num]
    if not filtered_df.empty:
        best_design = filtered_df.loc[filtered_df['total_metric'].idxmin()]
        
        param_dict = {
            'ta_u': best_design['ta_u'],
            'ta_l': best_design['ta_l'],
            'tb_u': best_design['tb_u'],
            'tb_l': best_design['tb_l'],
            'alpha_b': best_design['alpha_b'],
            'alpha_c': best_design['alpha_c']
        }
        airfoil = Nurbs(param_dict)
        coords = airfoil._spline()
        
        # Plot current airfoil with full opacity
        ax_airfoil.plot(coords[0], coords[1], 'orange', label='Lower surface', linewidth=2)
        ax_airfoil.plot(coords[2], coords[3], 'purple', label='Upper surface', linewidth=2)
    
    ax_airfoil.axis('equal')
    ax_airfoil.grid(True, linestyle='--', alpha=0.5)
    ax_airfoil.set_xlabel('x/c')
    ax_airfoil.set_ylabel('y/c')
    ax_airfoil.set_title('Best Airfoil Shape')
    ax_airfoil.legend()
    
    # [Rest of the plotting code remains the same...]
    # Plot L/D evolution
    ax_ld = plt.subplot(gs[0, len(param_names)//2:])
    iterations = filtered_df['iter']
    ld_values = filtered_df['ld']
    
    valid_mask = filtered_df['geometry_metric'] == 0
    
    ax_ld.scatter(iterations[~valid_mask], ld_values[~valid_mask], 
                 c='red', s=20, alpha=0.5, label='Invalid')
    ax_ld.scatter(iterations[valid_mask], ld_values[valid_mask], 
                 c='green', s=20, alpha=0.5, label='Valid')
    
    ax_ld.grid(True, linestyle='--', alpha=0.5)
    ax_ld.set_xlabel('Iteration')
    ax_ld.set_ylabel('L/D Ratio')
    ax_ld.set_title('L/D Evolution')
    ax_ld.legend()
    
    # Plot parameter evolution
    filtered_normed = normed_df[normed_df['iter'] <= iter_num]
    
    for idx, param in enumerate(param_names):
        ax_param = plt.subplot(gs[1, idx])
        
        hist, _ = np.histogram(filtered_normed[param], bins=100, range=(0, 1))
        hist = hist / hist.max()  # Normalize histogram
        
        ax_param.imshow(np.atleast_2d(hist).T, 
                       aspect='auto', 
                       origin='lower',
                       extent=[0, 1, 0, 1],
                       cmap='jet')
        
        ax_param.set_xticks([])
        ax_param.set_yticks([])
        ax_param.set_xlabel(param)
    
    # Save frame with fixed dimensions
    frame_path = os.path.join(temp_dir, f'frame_{iter_num:04d}.png')
    plt.savefig(frame_path, bbox_inches='tight', dpi=300)
    plt.close('all')
    
    return frame_path

def create_optimization_video(df, normed_df, iter_min, iter_max, param_names, output_path, 
                            n_previous=10, min_alpha=0.1, max_alpha=0.8, fps=5, max_workers=None):
    """
    Create a video showing the optimization progress using parallel processing
    
    Args:
        df: DataFrame with optimization data
        normed_df: DataFrame with normalized parameter values
        iter_min: Starting iteration
        iter_max: Ending iteration
        param_names: List of parameter names
        output_path: Path for output file
        n_previous: Number of previous best airfoils to show
        min_alpha: Minimum alpha value for oldest airfoil
        max_alpha: Maximum alpha value for second-to-last airfoil
        fps: Frames per second
        max_workers: Maximum number of parallel workers
    """
    
    import tempfile
    import cv2
    import os
    from tqdm import tqdm
    from concurrent.futures import ProcessPoolExecutor
    import numpy as np
    import sys
    import imageio
    from PIL import Image
    
    # Add the path to nurbs module if needed
    nurbs_path = os.path.dirname(os.path.abspath(__file__))
    if nurbs_path not in sys.path:
        sys.path.append(nurbs_path)
    
    # Create temporary directory for frames
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate frames in parallel
        print("Generating frames in parallel...")
        frame_paths = []
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    generate_single_frame, 
                    iter_num, 
                    temp_dir, 
                    df, 
                    normed_df, 
                    param_names,
                    n_previous,
                    min_alpha,
                    max_alpha
                )
                for iter_num in range(iter_min, iter_max + 1)
            ]
            for future in tqdm(futures, desc="Processing frames"):
                frame_paths.append(future.result())
        
        # Sort frame paths
        frame_paths.sort()
        
        # Create video/gif
        print("Creating output file...")
        if output_path.endswith('.gif'):
            # Read first frame to get dimensions
            with Image.open(frame_paths[0]) as img:
                size = img.size
            
            # Read and resize frames
            frames = []
            for frame_path in tqdm(frame_paths, desc="Reading frames"):
                with Image.open(frame_path) as img:
                    # Ensure all frames have the same size
                    if img.size != size:
                        img = img.resize(size, Image.Resampling.LANCZOS)
                    frames.append(np.array(img))
            
            # Save as GIF
            print("Saving GIF...")
            imageio.mimsave(output_path, frames, fps=fps)
        else:
            # For MP4 or other video formats
            first_frame = cv2.imread(frame_paths[0])
            height, width, layers = first_frame.shape
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            for frame_path in tqdm(frame_paths, desc="Adding frames to video"):
                frame = cv2.imread(frame_path)
                # Resize frame if needed
                if frame.shape[:2] != (height, width):
                    frame = cv2.resize(frame, (width, height))
                video.write(frame)
            
            video.release()
            
        print(f'File saved to {output_path}')