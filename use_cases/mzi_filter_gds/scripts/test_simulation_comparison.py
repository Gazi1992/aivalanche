"""
Test and compare different simulation methods for MZI filter
==============================================================
Compares analytical simulation with ideal response to understand
the filter behavior and verify the simulation is working correctly.
"""

import sys
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "aivalanche_lib"))

from mzi_gds_simulator import MZIFilterGDSSimulator


def test_simulation_methods():
    """Test and compare different simulation approaches."""
    
    # Load configuration
    inputs_dir = Path(__file__).parent.parent / "inputs"
    simulator = MZIFilterGDSSimulator(inputs_dir / "filter_config.json")
    
    # Load parameters
    params_df = pd.read_csv(inputs_dir / "parameters.csv")
    params = {row['name']: row['default'] for _, row in params_df.iterrows()}
    
    # Test different parameter sets
    test_cases = {
        'Default Parameters': params.copy(),
        'Optimized (from paper)': create_optimized_params(params, simulator.num_stages),
        'Uniform Coupling': create_uniform_params(params, simulator.num_stages, kappa=0.5),
        'Weak Coupling': create_uniform_params(params, simulator.num_stages, kappa=0.1),
    }
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('MZI Filter Simulation Comparison', fontsize=14, fontweight='bold')
    
    for idx, (name, test_params) in enumerate(test_cases.items()):
        ax = axes[idx // 2, idx % 2]
        
        # Simulate
        transmission = simulator.simulate_analytical(test_params)
        
        # Calculate metrics
        metrics = simulator.calculate_metrics(transmission)
        
        # Get ideal response
        ideal = simulator._create_ideal_response()
        
        # Plot
        wl_nm = simulator.wavelengths * 1000
        
        # Plot responses
        ax.plot(wl_nm, ideal, 'k--', linewidth=2, alpha=0.7, label='Ideal')
        ax.plot(wl_nm, transmission, 'b-', linewidth=2, label='Simulated')
        
        # Add bands
        ax.axvspan(simulator.s_band[0]*1000, simulator.s_band[1]*1000, 
                  alpha=0.1, color='green', label='S-band')
        ax.axvspan(simulator.c_band[0]*1000, simulator.c_band[1]*1000, 
                  alpha=0.1, color='red', label='C-band')
        ax.axvspan(simulator.transition_band[0]*1000, simulator.transition_band[1]*1000,
                  alpha=0.1, color='gray')
        
        # Format
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Transmission')
        ax.set_title(name, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=8)
        ax.set_ylim([-0.05, 1.1])
        
        # Add metrics text
        metrics_text = (
            f"IL: {metrics['insertion_loss']:.2f} dB\n"
            f"XT: {metrics['crosstalk']:.1f} dB\n"
            f"ER: {metrics['extinction_ratio']:.1f} dB"
        )
        ax.text(0.02, 0.98, metrics_text, transform=ax.transAxes,
                fontsize=8, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Add parameter summary
        delta_L = test_params['delta_L']
        kappa_avg = np.mean([test_params[f'kappa_{i}'] for i in range(simulator.num_stages)])
        param_text = f"ΔL: {delta_L:.2f} μm\nκ_avg: {kappa_avg:.3f}"
        ax.text(0.02, 0.75, param_text, transform=ax.transAxes,
                fontsize=8, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path(__file__).parent.parent / "results" / "simulation_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "simulation_comparison.png", dpi=150, bbox_inches='tight')
    plt.show()
    
    return test_cases, simulator


def create_optimized_params(base_params, num_stages):
    """Create optimized parameters based on literature values."""
    params = base_params.copy()
    
    # Optimized path difference for half-band filter
    # This should give FSR aligned with band separation
    params['delta_L'] = 16.485  # um
    
    # Optimized coupling ratios from literature
    # These values are typical for sharp half-band filters
    kappas = [0.05, 0.15, 0.25, 0.35, 0.45, 0.50, 0.45,
              0.35, 0.25, 0.15, 0.05, 0.03, 0.02][:num_stages]
    
    for i, k in enumerate(kappas):
        params[f'kappa_{i}'] = k
    
    return params


def create_uniform_params(base_params, num_stages, kappa=0.5):
    """Create parameters with uniform coupling."""
    params = base_params.copy()
    
    for i in range(num_stages):
        params[f'kappa_{i}'] = kappa
    
    return params


def analyze_phase_response():
    """Analyze the phase response to understand filter behavior."""
    
    # Load configuration
    inputs_dir = Path(__file__).parent.parent / "inputs"
    simulator = MZIFilterGDSSimulator(inputs_dir / "filter_config.json")
    
    # Test parameters
    delta_L_values = [10, 12, 14, 16, 16.485, 18, 20]  # um
    wavelengths = simulator.wavelengths * 1000  # nm
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle('Phase Analysis for MZI Half-Band Filter', fontsize=14, fontweight='bold')
    
    # Top: Phase shift vs wavelength for different delta_L
    ax1 = axes[0]
    for delta_L in delta_L_values:
        phase = 2 * np.pi * simulator.n_eff * delta_L * 1e-6 / (simulator.wavelengths * 1e-6)
        phase_wrapped = np.mod(phase, 2*np.pi)
        
        color = 'red' if delta_L == 16.485 else 'blue'
        alpha = 1.0 if delta_L == 16.485 else 0.5
        linewidth = 2 if delta_L == 16.485 else 1
        
        ax1.plot(wavelengths, phase_wrapped, 
                color=color, alpha=alpha, linewidth=linewidth,
                label=f'ΔL = {delta_L:.2f} μm')
    
    ax1.axvspan(simulator.s_band[0]*1000, simulator.s_band[1]*1000, alpha=0.1, color='green')
    ax1.axvspan(simulator.c_band[0]*1000, simulator.c_band[1]*1000, alpha=0.1, color='red')
    ax1.set_xlabel('Wavelength (nm)')
    ax1.set_ylabel('Phase (rad)')
    ax1.set_title('Phase Shift in MZI Arms')
    ax1.legend(loc='upper right', fontsize=8, ncol=2)
    ax1.grid(True, alpha=0.3)
    
    # Bottom: Single MZI response for different coupling ratios
    ax2 = axes[1]
    delta_L_opt = 16.485  # um
    kappa_values = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    for kappa in kappa_values:
        transmission = []
        for wl in simulator.wavelengths * 1e-6:
            beta = 2 * np.pi * simulator.n_eff / wl
            phi = beta * delta_L_opt * 1e-6
            
            # Single MZI response
            T = np.cos(phi/2)**2 * (1 - kappa) + np.sin(phi/2)**2 * kappa
            transmission.append(T)
        
        ax2.plot(wavelengths, transmission, linewidth=1.5,
                label=f'κ = {kappa:.1f}')
    
    ax2.axvspan(simulator.s_band[0]*1000, simulator.s_band[1]*1000, alpha=0.1, color='green')
    ax2.axvspan(simulator.c_band[0]*1000, simulator.c_band[1]*1000, alpha=0.1, color='red')
    ax2.set_xlabel('Wavelength (nm)')
    ax2.set_ylabel('Transmission')
    ax2.set_title('Single MZI Response (ΔL = 16.485 μm)')
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([-0.05, 1.1])
    
    plt.tight_layout()
    
    # Save
    output_dir = Path(__file__).parent.parent / "results" / "simulation_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "phase_analysis.png", dpi=150, bbox_inches='tight')
    plt.show()
    
    print("\nPhase Analysis Summary:")
    print("-" * 50)
    print(f"Optimal delta_L = 16.485 um gives:")
    
    # Calculate FSR
    center_wl = 1.5  # um
    FSR = center_wl**2 / (simulator.n_eff * delta_L_opt * 1e-6) * 1e9  # nm
    print(f"  Free Spectral Range (FSR) ≈ {FSR:.1f} nm")
    
    # Check phase at band centers
    s_center = np.mean(simulator.s_band)  # um
    c_center = np.mean(simulator.c_band)  # um
    
    phase_s = 2 * np.pi * simulator.n_eff * delta_L_opt * 1e-6 / (s_center * 1e-6)
    phase_c = 2 * np.pi * simulator.n_eff * delta_L_opt * 1e-6 / (c_center * 1e-6)
    
    print(f"  Phase at S-band center ({s_center*1000:.0f} nm): {phase_s:.2f} rad = {phase_s/np.pi:.2f}π")
    print(f"  Phase at C-band center ({c_center*1000:.0f} nm): {phase_c:.2f} rad = {phase_c/np.pi:.2f}π")
    print(f"  Phase difference: {(phase_s - phase_c):.2f} rad = {(phase_s - phase_c)/np.pi:.2f}π")


def main():
    """Main function."""
    print("="*70)
    print("MZI Filter Simulation Test and Comparison")
    print("="*70)
    
    # Test simulation methods
    print("\n1. Testing different parameter configurations...")
    test_cases, simulator = test_simulation_methods()
    
    # Analyze phase response
    print("\n2. Analyzing phase response...")
    analyze_phase_response()
    
    print("\n" + "="*70)
    print("Analysis complete! Check results/simulation_tests folder.")
    print("="*70)


if __name__ == "__main__":
    main()