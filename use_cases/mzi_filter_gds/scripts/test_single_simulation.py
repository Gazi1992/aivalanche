"""
Test Single Simulation
======================
Tests the MZI filter simulator with parameters from the CSV file.
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "aivalanche_lib"))

# Import simulator first
from mzi_gds_simulator import MZIFilterGDSSimulator

# Try importing Parameters with better error handling
try:
    from aivalanche_lib.parameters import Parameters
except ImportError as e:
    # If GPy import fails, we can still use Parameters without metamodel support
    import warnings
    warnings.filterwarnings('ignore', module='aivalanche_lib.metamodels')
    # Import just the Parameters class directly
    from aivalanche_lib.parameters import Parameters


def load_parameters(csv_path):
    """Load parameters from CSV and create Parameters object."""
    df = pd.read_csv(csv_path)
    
    # Convert to Parameters format
    param_list = []
    for _, row in df.iterrows():
        param = {
            'name': row['name'],
            'type': 'continuous',
            'min': row['min'],
            'max': row['max']
        }
        param_list.append(param)
    
    parameters = Parameters(param_list)
    
    # Also return default values
    defaults = {}
    for _, row in df.iterrows():
        defaults[row['name']] = row['default']
    
    return parameters, defaults


def test_single_simulation():
    """Run a single simulation test."""
    print("="*70)
    print("MZI Filter - Single Simulation Test")
    print("="*70)
    
    # Paths
    inputs_dir = Path(__file__).parent.parent / "inputs"
    results_dir = Path(__file__).parent.parent / "results" / "single_test"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Load parameters
    parameters, default_values = load_parameters(inputs_dir / "parameters.csv")
    print(f"\nLoaded {len(default_values)} parameters from CSV")
    
    # Initialize simulator
    simulator = MZIFilterGDSSimulator(inputs_dir / "filter_config.json")
    print(f"Initialized simulator with {simulator.num_stages} stages")
    print(f"Wavelength range: {simulator.wavelengths[0]*1000:.1f} - {simulator.wavelengths[-1]*1000:.1f} nm")
    
    # Test with default parameters
    print("\n" + "-"*50)
    print("Testing with default parameters:")
    print("-"*50)
    print(f"delta_L = {default_values['delta_L']:.2f} um")
    print(f"kappa range: {default_values['kappa_0']:.3f} - {default_values['kappa_12']:.3f}")
    
    # Create GDS layout
    print("\nGenerating GDS layout...")
    gds_path = results_dir / "cascaded_mzi_filter.gds"
    component = simulator.create_cascaded_mzi_gds(default_values, save_path=gds_path)
    
    # Plot layout
    print("Creating layout visualization...")
    layout_fig = simulator.plot_gds_layout(component, save_path=results_dir / "layout.png")
    plt.close()
    
    # Simulate using analytical method for speed
    transmission = simulator.simulate_analytical(default_values)
    metrics = simulator.calculate_metrics(transmission)
    
    # Calculate MSE metrics
    mse = simulator.calculate_mse_metric(transmission)
    weighted_mse = simulator.calculate_weighted_mse_metric(transmission)
    
    # Print results
    print("\nPerformance Metrics:")
    print("-"*30)
    print(f"Insertion Loss:    {metrics['insertion_loss']:.2f} dB")
    print(f"Crosstalk:        {metrics['crosstalk']:.1f} dB")
    print(f"Extinction Ratio: {metrics['extinction_ratio']:.1f} dB")
    print(f"Passband Ripple:  {metrics['passband_ripple']:.2f} dB")
    print(f"Roll-off Rate:    {metrics['rolloff_rate']:.2f} dB/nm")
    print(f"\nMSE Metrics:")
    print(f"MSE (uniform):     {mse:.6f}")
    print(f"MSE (weighted):    {weighted_mse:.6f}")
    
    # Check against targets
    print("\nTarget Comparison:")
    print("-"*30)
    targets = simulator.targets
    
    passed = True
    if metrics['insertion_loss'] > targets['max_insertion_loss_dB']:
        print(f"X Insertion Loss: {metrics['insertion_loss']:.2f} > {targets['max_insertion_loss_dB']} dB")
        passed = False
    else:
        print(f"+ Insertion Loss: {metrics['insertion_loss']:.2f} <= {targets['max_insertion_loss_dB']} dB")
    
    if metrics['crosstalk'] > targets['max_crosstalk_dB']:
        print(f"X Crosstalk: {metrics['crosstalk']:.1f} > {targets['max_crosstalk_dB']} dB")
        passed = False
    else:
        print(f"+ Crosstalk: {metrics['crosstalk']:.1f} <= {targets['max_crosstalk_dB']} dB")
    
    if metrics['rolloff_rate'] < targets['min_rolloff_dB_per_nm']:
        print(f"X Roll-off: {metrics['rolloff_rate']:.2f} < {targets['min_rolloff_dB_per_nm']} dB/nm")
        passed = False
    else:
        print(f"+ Roll-off: {metrics['rolloff_rate']:.2f} >= {targets['min_rolloff_dB_per_nm']} dB/nm")
    
    # Calculate objective
    objective = simulator.objective_function(default_values)
    print(f"\nObjective value: {objective:.2f}")
    print("(0 = meets all targets, >0 = needs optimization)")
    
    # Save results
    np.savetxt(results_dir / "transmission.csv", 
               np.column_stack((simulator.wavelengths*1000, transmission)),
               delimiter=',', header='wavelength_nm,transmission', comments='')
    
    with open(results_dir / "metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)
    
    with open(results_dir / "parameters_used.json", 'w') as f:
        json.dump(default_values, f, indent=2)
    
    # Plot
    fig = simulator.plot_response(transmission, metrics, title="Initial Design")
    fig.savefig(results_dir / "response.png", dpi=150)
    plt.close()
    
    print(f"\nResults saved to: {results_dir}")
    
    # Test with optimized delta_L from paper
    print("\n" + "="*70)
    print("Testing with Optimized delta_L = 14.89 um (from paper)")
    print("="*70)
    
    optimized_params = default_values.copy()
    optimized_params['delta_L'] = 14.89
    
    # Generate optimized GDS
    print("\nGenerating optimized GDS layout...")
    opt_gds_path = results_dir / "cascaded_mzi_filter_optimized.gds"
    component_opt = simulator.create_cascaded_mzi_gds(optimized_params, save_path=opt_gds_path)
    
    transmission_opt = simulator.simulate_analytical(optimized_params)
    metrics_opt = simulator.calculate_metrics(transmission_opt)
    
    # Calculate MSE for optimized design
    mse_opt = simulator.calculate_mse_metric(transmission_opt)
    weighted_mse_opt = simulator.calculate_weighted_mse_metric(transmission_opt)
    
    print("\nOptimized Metrics:")
    print("-"*30)
    print(f"Insertion Loss:    {metrics_opt['insertion_loss']:.2f} dB")
    print(f"Crosstalk:        {metrics_opt['crosstalk']:.1f} dB")
    print(f"Extinction Ratio: {metrics_opt['extinction_ratio']:.1f} dB")
    print(f"Roll-off Rate:    {metrics_opt['rolloff_rate']:.2f} dB/nm")
    print(f"\nMSE Metrics:")
    print(f"MSE (uniform):     {mse_opt:.6f}")
    print(f"MSE (weighted):    {weighted_mse_opt:.6f}")
    
    print("\nImprovement:")
    print("-"*30)
    print(f"Insertion Loss:    {metrics['insertion_loss']-metrics_opt['insertion_loss']:+.2f} dB")
    print(f"Crosstalk:        {metrics['crosstalk']-metrics_opt['crosstalk']:+.1f} dB")
    print(f"Roll-off:         {metrics_opt['rolloff_rate']-metrics['rolloff_rate']:+.2f} dB/nm")
    print(f"MSE reduction:     {mse-mse_opt:+.6f}")
    print(f"Weighted MSE red.: {weighted_mse-weighted_mse_opt:+.6f}")
    
    return transmission, metrics, passed


if __name__ == "__main__":
    transmission, metrics, passed = test_single_simulation()
    
    if passed:
        print("\n+ Initial design meets all targets!")
    else:
        print("\nX Initial design needs optimization")
    
    print("\n" + "="*70)
    print("Single simulation test completed!")
    print("="*70)