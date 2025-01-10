from visualizations import plot_polar, plot_pressure_distribution, plot_boundary_layer, plot_aero_performance, plot_parallel_coordinates
from xfoil import XFoilAnalyzer, XFoilBatch, XFoilSettings
import tempfile, os, pandas as pd, numpy as np, itertools
from scipy.stats import qmc

results_path = os.path.abspath('../results')
inputs_path = os.path.abspath('../inputs')
parameters_file = os.path.join(inputs_path, 'parameters_paper.csv')
pcp_path = os.path.join(results_path, 'pcp.html')
batch_results_path = os.path.join(results_path, 'batch_results.csv')

def single_simulation():
    alpha = list(range(-10, 20))
    alpha = 5
    Re = 1e6
    Mach = 0.2
    
    # Define NURBS parameters (similar to NACA 5410)
    params = {
        'ta_u': 0.1584,   # Upper surface leading edge tangent
        'ta_l': 0.1565,   # Lower surface leading edge tangent
        'tb_u': 2.1241,   # Upper surface trailing edge tangent
        'tb_l': 1.8255,   # Lower surface trailing edge tangent
        'alpha_b': 11.6983,  # Trailing edge angle
        'alpha_c': 3.8270    # Camber angle
    }
       
    # params = {
    #     'ta_u': 0.05,   # Upper surface leading edge tangent
    #     'ta_l': 0.05,   # Lower surface leading edge tangent
    #     'tb_u': 0.1,   # Upper surface trailing edge tangent
    #     'tb_l': 10,   # Lower surface trailing edge tangent
    #     'alpha_b': 5,  # Trailing edge angle
    #     'alpha_c': 10    # Camber angle
    # }
    
    # Initialize analyzer
    settings = XFoilSettings(working_dir = results_path)
    analyzer = XFoilAnalyzer(settings)
    
    # Run analysis
    results = analyzer.analyze_airfoil(
        parameters=params,
        alpha=alpha,
        Re=Re,
        Mach=Mach,
        get_pressure=True,
        get_boundary_layer=True,
        plot_airfoil=True
    )
    
    if results['convergence'] and isinstance(alpha, list):
        # Plot polar results
        plot_polar(results)
        plot_aero_performance(results)
        # plot_boundary_layer(results['boundary_layer'])
        # plot_pressure_distribution(results['pressure'])        
        
        # Print performance metrics
        print("\nPerformance Metrics:")
        print(f"Maximum Lift Coefficient: {results['cl_max']:.3f}")
        print(f"Minimum Drag Coefficient: {results['cd_min']:.4f}")
        print(f"Maximum L/D Ratio: {results['ld_max']:.2f}")
        print(f"Optimal Angle of Attack: {results['alpha_opt']:.1f}°")
        
    return results

def batch_simulation():
    
    params = read_parameters(parameters_file)
    param_list = generate_parameter_combinations(params, num_values = 2, lhs_samples = 5)
    print(len(param_list))
    
    # # Create list of parameter sets to test
    # param_list = [
    #     {
    #         'ta_u': 0.1584,
    #         'ta_l': 0.1565,
    #         'tb_u': 2.1241,
    #         'tb_l': 1.8255,
    #         'alpha_b': 11.6983,
    #         'alpha_c': 3.8270
    #     },
    #     {
    #         'ta_u': 0.15,
    #         'ta_l': 0.15,
    #         'tb_u': 2.0,
    #         'tb_l': 1.8,
    #         'alpha_b': 12.0,
    #         'alpha_c': 4.0
    #     },
    #     # Add more parameter sets as needed
    # ]
    
    
    # Initialize analyzer and batch handler
    
    settings = XFoilSettings(working_dir = results_path)
    analyzer = XFoilAnalyzer(settings)
    batch_handler = XFoilBatch(analyzer)
    
    # Define flow conditions
    Re = 1e6
    Mach = 0.2
    # alpha = (-5, 15, 1.0) 
    # alpha = [-5, 0, 5, 10, 15]
    alpha = -5
    
    # Run batch simulation
    results_df = batch_handler.run_batch(
        param_list=param_list,
        alpha=alpha,
        Re=Re,
        Mach=Mach,
        show_progress=True
    )
    
    # Print summary
    print("\nSimulation Results Summary:")
    print(f"Total parameter sets: {len(param_list)}")
    print(f"Converged cases: {results_df['cl'].notna().sum()}")
    print(f"Failed cases: {results_df['cl'].isna().sum()}")
    
    # Create and show pcp plot
    fig = plot_parallel_coordinates(results_df, color_column='ld', params_df = params, exclude = ['Re', 'Mach', 'alpha'])
    fig.write_html(pcp_path)
    fig.show()
    
    # Save results to CSV
    results_df.to_csv(batch_results_path, index=False)
    
    return results_df

def read_parameters(csv_file: str) -> pd.DataFrame:
    """
    Read parameter specifications from CSV file
    
    Args:
        csv_file: Path to CSV file containing parameter specifications
                 with columns: name, min, default, max, scale, mode
                 
    Returns:
        pandas DataFrame containing parameter specifications
        
    Raises:
        ValueError: If CSV file format is invalid
    """
    # Read CSV file
    params_df = pd.read_csv(csv_file)
    
    # Check required columns
    required_cols = ['name', 'min', 'default', 'max', 'scale', 'mode']
    missing_cols = set(required_cols) - set(params_df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Validate numerical values
    for col in ['min', 'default', 'max']:
        if not pd.to_numeric(params_df[col], errors='coerce').notna().all():
            raise ValueError(f"Non-numeric values found in {col} column")
    
    # Validate min <= default <= max
    if not (params_df['min'] <= params_df['default']).all():
        raise ValueError("Found min values greater than default values")
    if not (params_df['default'] <= params_df['max']).all():
        raise ValueError("Found default values greater than max values")
    
    return params_df

def generate_parameter_combinations(params_df: pd.DataFrame, num_values: int = 2, lhs_samples = 5):
    """
    Generate all combinations of parameter values
    
    Args:
        params_df: DataFrame from read_parameters containing parameter specifications
        num_values: Number of values to use for each parameter (including min and max)
        
    Returns:
        List of dictionaries containing parameter combinations
    """
    # Initialize dictionary to store parameter values
    param_ranges = {}
    param_bounds = {}
    
    # Get parameters and their ranges
    for _, row in params_df.iterrows():
        if row['mode'] == 'variable':
            if row['scale'] == 'linear':
                values = np.linspace(row['min'], row['max'], num_values)
                param_ranges[row['name']] = values
                param_bounds[row['name']] = (row['min'], row['max'])
            else:
                raise ValueError(f"Unsupported scale: {row['scale']} for parameter {row['name']}")
    
    # Generate all combinations
    param_names = list(param_ranges.keys())
    param_values = [param_ranges[param] for param in param_names]
    combinations = list(itertools.product(*param_values))
    
    # Convert to list of dictionaries
    param_list = [
        {name: value for name, value in zip(param_names, combo)}
        for combo in combinations
    ]
       
            
    # Create LHS sampler
    sampler = qmc.LatinHypercube(d=len(param_names))
    
    # Generate samples
    samples = sampler.random(n=lhs_samples)
    
    # Scale samples to parameter ranges
    bounds = np.array([param_bounds[name] for name in param_names])
    scaled_samples = qmc.scale(samples, bounds[:, 0], bounds[:, 1])
    
    # Convert to list of dictionaries
    param_list_lhs = [
        {name: value for name, value in zip(param_names, sample)}
        for sample in scaled_samples
    ]
    
    param_list.extend(param_list_lhs)
    
    return param_list

def main():
    # results = single_simulation()
    results = batch_simulation()
    return results

if __name__ == "__main__":
    results = main()