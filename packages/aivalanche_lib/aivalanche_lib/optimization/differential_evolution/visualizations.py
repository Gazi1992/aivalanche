"""
Visualization tools for the Differential Evolution optimizer.
This module provides a visualization function for analyzing the performance of the
Differential Evolution optimizer, focusing on metric evolution plots.

Note: All functions in this module are prefixed with an underscore (_) to indicate
they are internal implementation details not meant to be called directly from outside
the DifferentialEvolution class.
"""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt

def _plot_mutation_and_recombination(param_1_name, param_2_name,
                                    all_targets, target, donor, trial, best,
                                    mut_coef_1, mut_coef_2, mut_coef_3, recom_coef,
                                    rand_mem_1, rand_mem_2, rand_mem_3,
                                    fig=None, ax=None, save_path=None):
    """
    Plot the mutation and recombination vectors for differential evolution.
    Args:
        param_1_name: Name of first parameter (x-axis)
        param_2_name: Name of second parameter (y-axis)
        all_targets: Array of all target vectors
        target: Current target vector
        donor: Current donor vector
        trial: Current trial vector
        best: Current best vector
        mut_coef_1, mut_coef_2, mut_coef_3: Mutation coefficients
        recom_coef: Recombination coefficient
        rand_mem_1, rand_mem_2, rand_mem_3: Random members used in mutation
        fig: Optional existing figure to plot on
        ax: Optional existing axes to plot on
        save_path: If provided, the figure will be saved to this path
    Returns:
        tuple: Figure and axes objects
    """
    # Create figure and axes if not provided
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))

    # Plot all vectors
    ax.scatter(all_targets[:,0], all_targets[:,1], alpha=0.5, label='All targets', color='lightgray')
    ax.scatter(rand_mem_1[0], rand_mem_1[1], label='Random 1', color='skyblue')
    ax.scatter(rand_mem_2[0], rand_mem_2[1], label='Random 2', color='lightgreen')
    ax.scatter(rand_mem_3[0], rand_mem_3[1], label='Random 3', color='tan')
    ax.scatter(target[0], target[1], label='Target', color='blue', s = 100)
    ax.scatter(donor[0], donor[1], label='Donor', color='red', s = 80)
    ax.scatter(trial[0], trial[1], label='Trial', color='purple', s = 50)
    ax.scatter(best[0], best[1], label='Best', color='green', s=100, marker='*')

    # Add arrows
    # 1. Arrow from rand_mem_1 to best
    ax.annotate("", xy=(best[0], best[1]), xytext=(rand_mem_1[0], rand_mem_1[1]),
                arrowprops=dict(arrowstyle="->", color="green", lw=1.5, alpha=0.7))

    # 2. Arrow from rand_mem_3 to rand_mem_2
    ax.annotate("", xy=(rand_mem_2[0], rand_mem_2[1]), xytext=(rand_mem_3[0], rand_mem_3[1]),
                arrowprops=dict(arrowstyle="->", color="orange", lw=1.5, alpha=0.7))

    # 3. Arrow from target to best
    ax.annotate("", xy=(best[0], best[1]), xytext=(target[0], target[1]),
                arrowprops=dict(arrowstyle="->", color="blue", lw=1.5, alpha=0.7))

    # Set labels
    ax.set_xlabel(param_1_name)
    ax.set_ylabel(param_2_name)

    # Place legend to the right of the graph in one column
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1, frameon=False)

    # Add grid for better readability
    ax.grid(which='major', linestyle='-', alpha=0.5)
    ax.grid(which='minor', axis='y', linestyle='--', alpha=0.3)

    # Add coefficient information as text to the right, bottom-aligned with the graph
    info_text = (f"Mutation coeffs: {mut_coef_1:.2f}, {mut_coef_2:.2f}, {mut_coef_3:.2f}\n"
                 f"Recombination coeff: {recom_coef:.2f}")

    # Add text outside the plot, bottom-right aligned
    fig.text(0.77, 0.11, info_text,
         ha='left', va='bottom',
         # bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'),
         fontsize=9)

    # Adjust layout to make room for the legend and info text on the right
    plt.tight_layout()
    fig.subplots_adjust(right=0.75)  # Make room for legend on the right

    # Save figure if path provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig, ax

def _plot_metrics_evolution(
    iterations: np.ndarray,
    metrics: np.ndarray = None,
    x_scale: str = 'linear',
    y_scale: str = 'symlog',
    fig: plt.Figure = None,
    ax: plt.Axes = None,
    title: str = None,
    figsize: tuple[int, int] = (10, 6),
    save_path: str = None,
    **kwargs
) -> tuple[plt.Figure, plt.Axes]:
    """
    Plot the evolution of metrics over iterations, automatically selecting the plot
    type based on the structure of the iterations array.

    Args:
        iterations: Array of iteration numbers. The structure of this array determines
                   the plot type - if all values are unique, a line plot is created;
                   otherwise, a scatter plot is created.
        metrics: Array of metric values corresponding to the iterations
        fig: Optional matplotlib figure to plot on, if None, creates a new figure
        ax: Optional matplotlib axes to plot on, if None, creates a new axes
        title: Plot title. If None, no title will be displayed
        figsize: Figure size if creating a new figure
        save_path: If provided, the figure will be saved to this path
        **kwargs: Additional keyword arguments passed to the matplotlib plotting functions

    Returns:
        Tuple containing the matplotlib figure and axes object with the plot
    """
    # Handle figure and axes creation based on what's provided
    if fig is None and ax is None:
        # Create a new figure and axes if neither is provided
        fig, ax = plt.subplots(figsize=figsize)
    elif fig is not None and ax is None:
        # If a figure is provided but no axes, create a new subplot in the existing figure
        ax = fig.add_subplot(111)
    elif fig is None and ax is not None:
        # If axes are provided but no figure, get the figure from the axes
        fig = ax.figure

    # Determine the plot type based on the structure of the iterations array
    # If all iteration values are unique, use a line plot (typically for best metrics)
    # Otherwise, use a scatter plot (typically for population metrics)
    if len(iterations) == len(np.unique(iterations)):
        # Line plot with markers for best metrics (one point per iteration)
        ax.plot(iterations, metrics, marker='o', **kwargs)
    else:
        # Scatter plot for trials or survivors metrics (multiple points per iteration)
        ax.scatter(iterations, metrics, **kwargs)

    # Set the plot title if provided
    if title is not None:
        ax.set_title(title)

    # Set axis labels for better understanding of the plot
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Metric Value')

    # Set axis scales
    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)

    # Add grid for better readability
    ax.grid(which='major', axis = 'both', linestyle='-', alpha=0.5)
    ax.grid(which='minor', axis = 'both', linestyle='--', alpha=0.3)

    # Adjust layout to prevent clipping of labels
    plt.tight_layout()

    # Save the figure if a save path is provided
    if save_path is not None:
        fig.savefig(save_path, dpi=300, bbox_inches='tight') # High resolution for publication quality

    # Return both the figure and axes for further customization if needed
    return fig, ax

def _plot_all_parameters_evolution(
    df: pd.DataFrame,
    iter_start: int = None,
    iter_end: int = None,
    fig: plt.Figure = None,
    axes: list = None,
    title: str = "Parameter evolution",
    show_parameter_names: bool = True,
    save_path: str = None,
    figsize: tuple = None,
    bins: int = 100,
    nr_rows: int = 1,
    **kwargs
) -> tuple[plt.Figure, list]:
    """
    Create vertical histograms for each parameter, arranged in a grid.

    Args:
        df: DataFrame with parameter values (parameter names as columns)
        iter_start: First iteration to include
        iter_end: Last iteration to include. If None, include all iterations
        fig: Optional existing figure to plot on
        axes: Optional list of existing axes to plot on
        title: Title for the figure
        save_path: If provided, the figure will be saved to this path
        figsize: Size of the figure in inches (width, height). If None, calculated automatically
        bins: Number of bins for the histograms
        nr_rows: Number of rows to arrange the parameter plots
        **kwargs: Additional keyword arguments passed to plt.imshow

    Returns:
        tuple: Figure and list of axes
    """
    # Get parameter columns (exclude 'iter' and any other non-parameter columns)
    exclude_cols = ['iter', 'metric']
    param_columns = [col for col in df.columns if col not in exclude_cols]
    n_params = len(param_columns)

    if n_params == 0:
        raise ValueError("No parameter columns found in DataFrame")

    # Check if 'iter' column exists in the DataFrame
    if 'iter' in df.columns:
        iter_min = df['iter'].min()
        iter_max = df['iter'].max()

        if iter_start is None:
            iter_start = iter_min

        if iter_end is None:
            iter_end = iter_max

        iter_start = max(iter_start, iter_min)
        iter_end = min(iter_end, iter_max)

        # Filter DataFrame to selected iterations
        filtered_df = df[(df['iter'] <= iter_end) & (df['iter'] >= iter_start)].copy()
    else:
        filtered_df = df.copy()

    # Calculate layout parameters
    nr_cols = int(np.ceil(n_params / nr_rows))

    # Set default figure size if not provided
    if figsize is None:
        # Scale width based on number of parameters and columns
        width = min(nr_cols * 2, 12)
        height = min(nr_rows * 5, 8)
        figsize = (width, height)

    # Create figure and axes if not provided
    if fig is None and axes is None:
        fig, axes_array = plt.subplots(nr_rows, nr_cols, figsize=figsize)

        # Handle different axes shapes based on rows and columns
        if nr_rows == 1 and nr_cols == 1:
            axes = np.array([axes_array])
        elif nr_rows == 1:
            axes = np.array([ax for ax in axes_array])
        elif nr_cols == 1:
            axes = np.array([[ax] for ax in axes_array])
        else:
            axes = axes_array
    elif fig is not None and axes is None:
        # Create axes in the existing figure
        axes = []
        for i in range(nr_rows):
            row_axes = []
            for j in range(nr_cols):
                ax = fig.add_subplot(nr_rows, nr_cols, i*nr_cols + j + 1)
                row_axes.append(ax)
            axes.append(row_axes)
        axes = np.array(axes)
    elif fig is None and axes is not None:
        # If axes are provided but no figure, get the figure from the first axes
        if len(axes) > 0:
            if isinstance(axes, np.ndarray) and axes.size > 0:
                fig = axes.flat[0].figure
            elif isinstance(axes, list) and len(axes) > 0:
                fig = axes[0].figure
            else:
                raise ValueError("Invalid axes input")

    # Ensure axes is a numpy array for consistent indexing
    if not isinstance(axes, np.ndarray):
        axes = np.array(axes)

    # Flatten the axes array for easier indexing
    if nr_rows == 1:
        axes_flat = axes
    else:
        axes_flat = axes.flatten()

    # Set default kwargs for imshow
    imshow_kwargs = {
        'aspect': 'auto',
        'interpolation': 'nearest',
        'cmap': 'YlGn',
        'origin': 'lower'
    }

    # Update with user provided kwargs
    imshow_kwargs.update(kwargs)

    # Create histograms for each parameter
    for i, param_name in enumerate(param_columns):
        if i < len(axes_flat):
            # Get the appropriate axis
            ax = axes_flat[i]

            # Get parameter values
            values = np.array(filtered_df[param_name])

            # Determine range for this parameter
            param_min = np.min(values)
            param_max = np.max(values)

            # Ensure that min and max are different to avoid issues with histogram
            if param_min == param_max:
                param_min = param_min - 0.5
                param_max = param_max + 0.5

            # Create histogram
            hist, edges = np.histogram(values, bins=bins, range=(param_min, param_max))

            # Clear the axis before plotting
            ax.clear()

            # Plot the histogram as an image
            ax.imshow(np.atleast_2d(hist).T, extent=[0, 1, param_min, param_max], **imshow_kwargs)

            # Remove ticks
            ax.set_xticks([])
            ax.set_yticks([])

            # Add parameter name at the bottom
            if show_parameter_names:
                ax.set_xlabel(param_name)

    # Hide unused subplots
    for i in range(n_params, len(axes_flat)):
        axes_flat[i].axis('off')

    # Add title
    if title:
        fig.suptitle(title)

    # Adjust spacing between subplots
    fig.tight_layout(rect=[0, 0, 1, 0.95] if title else [0, 0, 1, 1])

    # Save figure if path provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig, axes

def _plot_parameters_evolution(
    df: pd.DataFrame,
    parameter_names: list = None,
    iter_start: int = None,
    iter_end: int = None,
    iter_step: int = 1,
    fig: plt.Figure = None,
    axes: list = None,
    bins: int = 100,
    figsize: tuple = None,
    title: str = None,
    save_path: str = None,
    nr_rows: int = 1,
    **kwargs
) -> tuple[plt.Figure, list]:
    """
    Plot the evolution of multiple parameters' histograms across iterations.

    Args:
        df: DataFrame with parameter values (must contain 'iter' column and parameter columns)
        parameter_names: List of parameter names to visualize (if None, use all columns except 'iter' and 'metric')
        iter_start: First iteration to include (if None, starts from minimum)
        iter_end: Last iteration to include (if None, goes to maximum)
        iter_step: Step size for iterations (to reduce number of histograms)
        fig: Optional existing figure to plot on
        axes: Optional list of existing axes to plot on
        bins: Number of bins for the histograms
        figsize: Size of the figure in inches (width, height). If None, calculated automatically
        title: Title for the figure (if None, uses generic title)
        save_path: If provided, the figure will be saved to this path
        nr_rows: Number of rows to arrange the parameter plots
        **kwargs: Additional keyword arguments passed to plt.imshow

    Returns:
        tuple: Figure and list of axes
    """
    # Check if 'iter' column exists in the DataFrame
    if 'iter' not in df.columns:
        raise ValueError("DataFrame must contain an 'iter' column")

    # Determine parameter names if not specified
    if parameter_names is None:
        # Exclude 'iter' and 'metric' columns
        parameter_names = [col for col in df.columns if col not in ['iter', 'metric']]
    else:
        # Check if all requested parameters exist in the DataFrame
        for param in parameter_names:
            if param not in df.columns:
                raise ValueError(f"Parameter '{param}' not found in DataFrame")

    n_params = len(parameter_names)
    if n_params == 0:
        raise ValueError("No parameters to plot")

    # Get iteration range
    unique_iters = sorted(df['iter'].unique())

    if iter_start is None:
        iter_start = min(unique_iters)

    if iter_end is None:
        iter_end = max(unique_iters)

    # Filter iterations by range and step
    selected_iters = [iter_num for iter_num in unique_iters
                     if iter_start <= iter_num <= iter_end and
                     (iter_num - iter_start) % iter_step == 0]

    if not selected_iters:
        raise ValueError(f"No iterations found in range [{iter_start}, {iter_end}] with step {iter_step}")

    # Calculate layout parameters
    nr_cols = int(np.ceil(n_params / nr_rows))

    # Set default figure size if not provided
    if figsize is None:
        # Scale width based on number of parameters and columns
        width = min(nr_cols * 5, 20)  # Cap width at 20 inches
        height = min(nr_rows * 4, 16)  # Cap height at 16 inches
        figsize = (width, height)

    # Create figure and axes if not provided
    if fig is None and axes is None:
        fig, axes_array = plt.subplots(nr_rows, nr_cols, figsize=figsize)

        # Handle different axes shapes based on rows and columns
        if nr_rows == 1 and nr_cols == 1:
            axes = np.array([axes_array])
        elif nr_rows == 1:
            axes = np.array([ax for ax in axes_array])
        elif nr_cols == 1:
            axes = np.array([[ax] for ax in axes_array])
        else:
            axes = axes_array
    elif fig is not None and axes is None:
        # Create axes in the existing figure
        axes = []
        for i in range(nr_rows):
            row_axes = []
            for j in range(nr_cols):
                ax = fig.add_subplot(nr_rows, nr_cols, i*nr_cols + j + 1)
                row_axes.append(ax)
            axes.append(row_axes)
        axes = np.array(axes)
    elif fig is None and axes is not None:
        # If axes are provided but no figure, get the figure from the first axes
        if len(axes) > 0:
            if isinstance(axes, np.ndarray) and axes.size > 0:
                fig = axes.flat[0].figure
            elif isinstance(axes, list) and len(axes) > 0:
                fig = axes[0].figure
            else:
                raise ValueError("Invalid axes input")

    # Ensure axes is a numpy array for consistent indexing
    if not isinstance(axes, np.ndarray):
        axes = np.array(axes)

    # Flatten the axes array for easier indexing
    if nr_rows == 1:
        axes_flat = axes
    else:
        axes_flat = axes.flatten()

    # Plot each parameter
    for i, param_name in enumerate(parameter_names):
        if i < len(axes_flat):
            ax = axes_flat[i]

            # Determine parameter range
            param_min = df[param_name].min()
            param_max = df[param_name].max()

            # Ensure min and max are different
            if param_min == param_max:
                param_min -= 0.5
                param_max += 0.5

            # Create a 2D array to store all histograms
            hist_matrix = []

            # Calculate histograms for each iteration
            for iter_num in selected_iters:
                # Get parameter values for this iteration
                iter_values = df[df['iter'] == iter_num][param_name].values

                # Calculate histogram
                hist, _ = np.histogram(iter_values, bins=bins, range=(param_min, param_max))

                # Add to matrix
                hist_matrix.append(hist)

            # Convert to numpy array
            hist_matrix = np.array(hist_matrix)

            # Transpose the matrix for the rotated view (iterations on x-axis)
            hist_matrix = hist_matrix.T

            # Set default kwargs for imshow
            imshow_kwargs = {
                'aspect': 'auto',
                'interpolation': 'nearest',
                'cmap': 'YlGn',
                'origin': 'lower',
                'extent': [min(selected_iters), max(selected_iters), param_min, param_max]
            }

            # Update with user provided kwargs
            imshow_kwargs.update(kwargs)

            # Plot histograms as image
            im = ax.imshow(hist_matrix, **imshow_kwargs)

            # Add colorbar
            cbar = fig.colorbar(im, ax=ax)
            cbar.set_label('Frequency')

            # Set labels
            ax.set_xlabel('Iteration')
            ax.set_ylabel(param_name)

            # Set title for each subplot
            ax.set_title(f"Evolution of {param_name}")

    # Hide unused subplots
    for i in range(n_params, len(axes_flat)):
        axes_flat[i].axis('off')

    # Add title to the figure
    if title is None:
        title = "Parameters Distribution Evolution"
    fig.suptitle(title)

    # Adjust spacing between subplots
    fig.tight_layout(rect=[0, 0, 1, 0.96] if title else [0, 0, 1, 1])

    # Save figure if path provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig, axes

def _plot_boundaries_evolution(
    df: pd.DataFrame,
    parameter_names: list = None,
    iter_start: int = None,
    iter_end: int = None,
    fig: plt.Figure = None,
    axes: list = None,
    title: str = "Boundaries Evolution",
    save_path: str = None,
    figsize: tuple = None,
    nr_rows: int = 1,
    normalized: bool = True,
    alpha: float = 0.3,
    **kwargs
) -> tuple[plt.Figure, list]:
    """
    Plot the evolution of parameter boundaries over iterations.

    Args:
        df: DataFrame with multi-index (iter, type) where type is 'min', 'max', 'range'
            and columns are parameter names
        parameter_names: List of parameter names to plot (if None, plots all parameters)
        iter_start: First iteration to include
        iter_end: Last iteration to include. If None, include all iterations
        fig: Optional existing figure to plot on
        axes: Optional list of existing axes to plot on
        title: Title for the figure
        save_path: If provided, the figure will be saved to this path
        figsize: Size of the figure in inches (width, height). If None, calculated automatically
        nr_rows: Number of rows to arrange the parameter plots
        normalized: Whether the data is in normalized (0-1) or original units
        alpha: Alpha value for the fill between min and max
        **kwargs: Additional keyword arguments passed to plt.plot

    Returns:
        tuple: Figure and list of axes
    """
    # Get all iterations in the DataFrame
    all_iters = sorted(df.index.get_level_values('iter').unique())

    if iter_start is None:
        iter_start = min(all_iters)

    if iter_end is None:
        iter_end = max(all_iters)

    # Filter iterations
    selected_iters = [i for i in all_iters if iter_start <= i <= iter_end]

    # Create a new DataFrame with just the selected iterations
    filtered_df = df.loc[pd.IndexSlice[selected_iters, :], :]

    # Get parameter columns (if not specified, use all columns)
    if parameter_names is None:
        parameter_names = df.columns.tolist()

    n_params = len(parameter_names)

    if n_params == 0:
        raise ValueError("No parameters to plot")

    # Calculate layout parameters
    nr_cols = int(np.ceil(n_params / nr_rows))

    # Set default figure size if not provided
    if figsize is None:
        # Scale width based on number of parameters and columns
        width = min(nr_cols * 4, 16)
        height = min(nr_rows * 3, 12)
        figsize = (width, height)

    # Create figure and axes if not provided
    if fig is None and axes is None:
        fig, axes_array = plt.subplots(nr_rows, nr_cols, figsize=figsize)

        # Handle different axes shapes based on rows and columns
        if nr_rows == 1 and nr_cols == 1:
            axes = np.array([axes_array])
        elif nr_rows == 1:
            axes = np.array([ax for ax in axes_array])
        elif nr_cols == 1:
            axes = np.array([[ax] for ax in axes_array])
        else:
            axes = axes_array
    elif fig is not None and axes is None:
        # Create axes in the existing figure
        axes = []
        for i in range(nr_rows):
            row_axes = []
            for j in range(nr_cols):
                ax = fig.add_subplot(nr_rows, nr_cols, i*nr_cols + j + 1)
                row_axes.append(ax)
            axes.append(row_axes)
        axes = np.array(axes)
    elif fig is None and axes is not None:
        # If axes are provided but no figure, get the figure from the first axes
        if len(axes) > 0:
            if isinstance(axes, np.ndarray) and axes.size > 0:
                fig = axes.flat[0].figure
            elif isinstance(axes, list) and len(axes) > 0:
                fig = axes[0].figure
            else:
                raise ValueError("Invalid axes input")

    # Ensure axes is a numpy array for consistent indexing
    if not isinstance(axes, np.ndarray):
        axes = np.array(axes)

    # Flatten the axes array for easier indexing
    if nr_rows == 1:
        axes_flat = axes
    else:
        axes_flat = axes.flatten()

    # Create a color cycle for consistent colors across plots
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']

    # Plot each parameter
    for i, param_name in enumerate(parameter_names):
        if i < len(axes_flat):
            ax = axes_flat[i]

            # Get min and max values for this parameter
            min_values = filtered_df.xs('min', level='type')[param_name]
            max_values = filtered_df.xs('max', level='type')[param_name]

            # Plot min and max as lines
            iterations = min_values.index.values
            ax.plot(iterations, min_values.values, color=colors[0], label='Min', **kwargs)
            ax.plot(iterations, max_values.values, color=colors[1], label='Max', **kwargs)

            # Fill between min and max
            ax.fill_between(iterations, min_values.values, max_values.values,
                           color=colors[0], alpha=alpha)

            # Set axis labels
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Boundary')

            # Set title for each subplot
            ax.set_title(param_name)

            # Add grid for better readability
            ax.grid(which='major', axis = 'both', linestyle='-', alpha=0.5)
            ax.grid(which='minor', axis = 'both', linestyle='--', alpha=0.3)

            # # Add legend to the first subplot only
            # if i == 0:
            #     ax.legend()

    # Hide unused subplots
    for i in range(n_params, len(axes_flat)):
        axes_flat[i].axis('off')

    # Add title
    fig.suptitle(title)

    # Adjust spacing between subplots
    fig.tight_layout(rect=[0, 0, 1, 0.96] if title else [0, 0, 1, 1])

    # Save figure if path provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig, axes
