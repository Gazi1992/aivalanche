"""
Test script to plot all 1D and 2D test functions.
Results are saved in the results directory.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from test_functions.definitions import ALL_FUNCTIONS, get_function_details
from test_functions.plotting import plot_test_function


def create_results_dir():
    """Create results directory with timestamp."""
    results_base = os.path.join(os.path.dirname(__file__), 'results')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join(results_base, f'plots_{timestamp}')
    os.makedirs(results_dir, exist_ok=True)
    return results_dir


def plot_1d_functions(results_dir):
    """Plot all 1D test functions."""
    print("\n=== Plotting 1D Functions ===")
    
    # Get all 1D functions
    functions_1d = {name: details for name, details in ALL_FUNCTIONS.items() 
                    if details['dim'] == 1}
    
    if not functions_1d:
        print("No 1D functions found.")
        return
    
    for name, _ in functions_1d.items():
        try:
            print(f"Plotting {name}...")
            details = get_function_details(name)
            
            # Create the plot
            fig, ax = plot_test_function(details)
            
            # Save the plot
            filename = os.path.join(results_dir, f'{name}.png')
            fig.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"  Saved to: {filename}")
            
        except Exception as e:
            print(f"  Error plotting {name}: {e}")


def plot_2d_continuous_functions(results_dir):
    """Plot all 2D continuous test functions."""
    print("\n=== Plotting 2D Continuous Functions ===")
    
    # Get all 2D functions
    functions_2d = {name: details for name, details in ALL_FUNCTIONS.items() 
                    if details['dim'] == 2}
    
    # Filter for functions that can be plotted normally (continuous or discrete numeric)
    plottable_2d = {}
    for name, details in functions_2d.items():
        param_types = details.get('param_types', ['continuous', 'continuous'])
        # Skip functions with categorical parameters for now
        if 'categorical' not in param_types:
            plottable_2d[name] = details
    
    for name, _ in plottable_2d.items():
        try:
            print(f"Plotting {name}...")
            details = get_function_details(name)
            
            # Convert bounds format for discrete functions
            bounds = details['bounds']
            converted_bounds = []
            for bound in bounds:
                if isinstance(bound, tuple) and len(bound) == 3:
                    # (min, max, step) format - convert to (min, max)
                    converted_bounds.append((bound[0], bound[1]))
                elif isinstance(bound, list):
                    # List of values - use min and max
                    converted_bounds.append((min(bound), max(bound)))
                else:
                    converted_bounds.append(bound)
            
            # Update details with converted bounds for plotting
            plot_details = details.copy()
            plot_details['bounds'] = converted_bounds
            
            # Create the plot
            fig, axes = plot_test_function(plot_details)
            
            # Save the plot
            filename = os.path.join(results_dir, f'{name}.png')
            fig.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"  Saved to: {filename}")
            
        except Exception as e:
            print(f"  Error plotting {name}: {e}")


def plot_2d_categorical_functions(results_dir):
    """Plot 2D functions with categorical parameters using heatmaps."""
    print("\n=== Plotting 2D Functions with Categorical Parameters ===")
    
    # Get all 2D functions with categorical parameters
    functions_2d_cat = {}
    for name, details in ALL_FUNCTIONS.items():
        if details['dim'] == 2:
            param_types = details.get('param_types', ['continuous', 'continuous'])
            if 'categorical' in param_types:
                functions_2d_cat[name] = details
    
    for name, details in functions_2d_cat.items():
        try:
            print(f"Plotting {name}...")
            
            func = details['func']
            bounds = details['bounds']
            param_types = details['param_types']
            
            # Handle different types of categorical functions
            if param_types == ['continuous', 'categorical']:
                plot_continuous_categorical(name, func, bounds, results_dir)
            elif param_types == ['discrete', 'categorical']:
                plot_discrete_categorical(name, func, bounds, results_dir)
            elif param_types == ['categorical', 'categorical']:
                plot_categorical_categorical(name, func, bounds, results_dir)
            else:
                print(f"  Unsupported parameter type combination: {param_types}")
                
        except Exception as e:
            print(f"  Error plotting {name}: {e}")


def plot_continuous_categorical(name, func, bounds, results_dir):
    """Plot function with continuous x and categorical y."""
    x_bounds = bounds[0]
    y_categories = bounds[1]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Sample continuous dimension
    x_vals = np.linspace(x_bounds[0], x_bounds[1], 200)
    
    # Plot line for each category
    for cat in y_categories:
        y_vals = []
        for x in x_vals:
            # Create array with correct types
            input_array = np.array([x, cat], dtype=object)
            y_vals.append(func(input_array))
        ax.plot(x_vals, y_vals, label=f'y = {cat}', linewidth=2)
    
    ax.set_xlabel('x (continuous)')
    ax.set_ylabel('f(x, y)')
    ax.set_title(f'{name}\nContinuous x with Categorical y')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    filename = os.path.join(results_dir, f'{name}.png')
    fig.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved to: {filename}")


def plot_discrete_categorical(name, func, bounds, results_dir):
    """Plot function with discrete x and categorical y."""
    x_values = bounds[0]
    y_categories = bounds[1]
    
    # Create heatmap data
    heatmap_data = np.zeros((len(y_categories), len(x_values)))
    
    for i, y_cat in enumerate(y_categories):
        for j, x_val in enumerate(x_values):
            # Create array with correct types
            input_array = np.array([x_val, y_cat], dtype=object)
            heatmap_data[i, j] = func(input_array)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(heatmap_data, aspect='auto', cmap='viridis')
    
    # Set ticks
    ax.set_xticks(range(len(x_values)))
    ax.set_xticklabels([str(x) for x in x_values])
    ax.set_yticks(range(len(y_categories)))
    ax.set_yticklabels(y_categories)
    
    # Labels
    ax.set_xlabel('x (discrete values)')
    ax.set_ylabel('y (categorical)')
    ax.set_title(f'{name}\nDiscrete x with Categorical y')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('f(x, y)')
    
    # Add text annotations
    for i in range(len(y_categories)):
        for j in range(len(x_values)):
            text = ax.text(j, i, f'{heatmap_data[i, j]:.1f}',
                          ha="center", va="center", color="white" if heatmap_data[i, j] < heatmap_data.max()/2 else "black")
    
    filename = os.path.join(results_dir, f'{name}.png')
    fig.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved to: {filename}")


def plot_categorical_categorical(name, func, bounds, results_dir):
    """Plot function with two categorical parameters."""
    x_categories = bounds[0]
    y_categories = bounds[1]
    
    # Create heatmap data
    heatmap_data = np.zeros((len(y_categories), len(x_categories)))
    
    for i, y_cat in enumerate(y_categories):
        for j, x_cat in enumerate(x_categories):
            # Create array with correct types
            input_array = np.array([x_cat, y_cat], dtype=object)
            heatmap_data[i, j] = func(input_array)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(heatmap_data, aspect='auto', cmap='viridis')
    
    # Set ticks
    ax.set_xticks(range(len(x_categories)))
    ax.set_xticklabels(x_categories, rotation=45, ha='right')
    ax.set_yticks(range(len(y_categories)))
    ax.set_yticklabels(y_categories)
    
    # Labels
    ax.set_xlabel('x (categorical)')
    ax.set_ylabel('y (categorical)')
    ax.set_title(f'{name}\nCategorical x with Categorical y')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('f(x, y)')
    
    # Add text annotations
    for i in range(len(y_categories)):
        for j in range(len(x_categories)):
            text = ax.text(j, i, f'{heatmap_data[i, j]:.1f}',
                          ha="center", va="center", color="white" if heatmap_data[i, j] < heatmap_data.max()/2 else "black")
    
    plt.tight_layout()
    
    filename = os.path.join(results_dir, f'{name}.png')
    fig.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved to: {filename}")


def create_summary_report(results_dir):
    """Create a summary report of all functions."""
    report_file = os.path.join(results_dir, 'function_summary.txt')
    
    with open(report_file, 'w') as f:
        f.write("Test Functions Summary Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Count functions by dimension
        dim_counts = {}
        for name, details in ALL_FUNCTIONS.items():
            dim = details['dim']
            if dim == 'nD':
                dim = 'n-dimensional'
            dim_counts[dim] = dim_counts.get(dim, 0) + 1
        
        f.write("Function Count by Dimension:\n")
        # Sort by converting keys to strings first
        for dim, count in sorted(dim_counts.items(), key=lambda x: (isinstance(x[0], str), str(x[0]))):
            f.write(f"  {dim}: {count} functions\n")
        f.write("\n")
        
        # List all functions with their properties
        f.write("Function Details:\n")
        f.write("-" * 50 + "\n")
        
        for name, details in sorted(ALL_FUNCTIONS.items()):
            f.write(f"\n{name}:\n")
            f.write(f"  Dimension: {details['dim']}\n")
            if 'param_types' in details:
                f.write(f"  Parameter types: {details['param_types']}\n")
            f.write(f"  Bounds: {details['bounds']}\n")
            if 'optimum_val' in details:
                f.write(f"  Optimum value: {details['optimum_val']}\n")
            if 'optimum_loc' in details:
                f.write(f"  Optimum location: {details['optimum_loc']}\n")
    
    print(f"\nSummary report saved to: {report_file}")


def main():
    """Main function to run all plotting tests."""
    print("Test Functions Plotting Script")
    print("=" * 50)
    
    # Create results directory
    results_dir = create_results_dir()
    print(f"Results will be saved to: {results_dir}")
    
    # Plot different types of functions
    plot_1d_functions(results_dir)
    plot_2d_continuous_functions(results_dir)
    plot_2d_categorical_functions(results_dir)
    
    # Create summary report
    create_summary_report(results_dir)
    
    print("\nAll plots generated successfully!")


if __name__ == "__main__":
    main()