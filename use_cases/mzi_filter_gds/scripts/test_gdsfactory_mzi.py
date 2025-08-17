"""
Test gdsfactory's native MZI simulation capabilities
=====================================================
Use gdsfactory's built-in MZI components and see how they behave.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import gdsfactory as gf
from gdsfactory.components import mzi


def test_gdsfactory_single_mzi():
    """Test a single MZI using gdsfactory's native component."""
    
    print("Testing gdsfactory's native MZI component...")
    print("-" * 50)
    
    # Create a single MZI with gdsfactory
    # Default MZI parameters
    delta_lengths = [0, 10, 20, 30, 40]  # um path differences
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('GDSFactory Native MZI Response', fontsize=14, fontweight='bold')
    axes = axes.flatten()
    
    wavelengths = np.linspace(1.48, 1.58, 200)  # um
    
    for idx, delta_L in enumerate(delta_lengths):
        ax = axes[idx]
        
        # Create MZI component
        c = gf.components.mzi(
            delta_length=delta_L,
            length_y=2.0,
            length_x=0.1,
            port_e0_splitter='o3',  # Use correct port names
            port_e0_combiner='o3',
            port_e1_splitter='o2',
            port_e1_combiner='o2',
            with_splitter=True,
            straight='straight',
            bend='bend_euler',
            splitter='mmi1x2',
            combiner='mmi1x2'
        )
        
        # Calculate analytical response for this MZI
        # Using simple MZI equation: T = cos²(Δφ/2)
        n_eff = 2.4  # Effective index for silicon
        transmission = []
        
        for wl in wavelengths:
            # Phase difference
            delta_phi = 2 * np.pi * n_eff * delta_L * 1e-6 / (wl * 1e-6)
            # MZI bar port transmission (assuming 50:50 coupling)
            T = np.cos(delta_phi / 2) ** 2
            transmission.append(T)
        
        # Plot
        ax.plot(wavelengths * 1000, transmission, 'b-', linewidth=2)
        
        # Add S-band and C-band regions
        ax.axvspan(1480, 1517, alpha=0.1, color='green', label='S-band' if idx==0 else '')
        ax.axvspan(1528, 1568, alpha=0.1, color='red', label='C-band' if idx==0 else '')
        
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Transmission')
        ax.set_title(f'delta_L = {delta_L} um', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([-0.05, 1.1])
        
        if idx == 0:
            ax.legend(loc='upper right')
        
        # Add FSR calculation
        if delta_L > 0:
            FSR = (1.5e-6)**2 / (n_eff * delta_L * 1e-6) * 1e9  # nm
            ax.text(0.02, 0.95, f'FSR ≈ {FSR:.1f} nm', transform=ax.transAxes,
                   fontsize=9, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    # Test cascaded MZI response
    ax = axes[5]
    
    # Cascade multiple MZIs analytically
    num_stages = 5
    delta_L = 16.485  # um
    kappas = [0.1, 0.3, 0.5, 0.3, 0.1]  # Apodized coupling
    
    transmission_cascade = []
    for wl in wavelengths:
        T_total = 1.0 + 0j
        
        for kappa in kappas:
            # Phase for this wavelength
            delta_phi = 2 * np.pi * n_eff * delta_L * 1e-6 / (wl * 1e-6)
            
            # MZI response with variable coupling
            t = np.sqrt(1 - kappa)
            k = np.sqrt(kappa)
            
            # Transfer function
            H = t**2 * np.exp(1j * delta_phi) + k**2
            T_total *= H
        
        transmission_cascade.append(np.abs(T_total)**2)
    
    ax.plot(wavelengths * 1000, transmission_cascade, 'r-', linewidth=2, label='5-stage cascade')
    ax.axvspan(1480, 1517, alpha=0.1, color='green')
    ax.axvspan(1528, 1568, alpha=0.1, color='red')
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Transmission')
    ax.set_title(f'Cascaded MZI (N=5, delta_L={delta_L} um)', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim([-0.05, 1.1])
    ax.legend()
    
    plt.tight_layout()
    
    # Save
    output_dir = Path(__file__).parent.parent / "results" / "gdsfactory_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "gdsfactory_mzi_test.png", dpi=150, bbox_inches='tight')
    # plt.show()  # Commented to avoid blocking
    
    return c


def test_gdsfactory_circuit_model():
    """Test if gdsfactory has circuit-level simulation."""
    
    print("\n\nTesting gdsfactory circuit capabilities...")
    print("-" * 50)
    
    # Create an MZI
    c = gf.components.mzi(delta_length=10.0)
    
    # Check available methods
    print("MZI component info:")
    print(f"  - Component name: {c.name}")
    print(f"  - Number of ports: {len(c.ports)}")
    print(f"  - Port names: {[p.name for p in c.ports]}")
    
    # Check if gdsfactory has S-parameter extraction
    print("\nChecking for simulation capabilities:")
    
    # Check for circuit models
    if hasattr(gf, 'simulation'):
        print("  [YES] Has simulation module")
    else:
        print("  [NO] No simulation module found")
    
    # Alternative: Check for models
    if hasattr(gf, 'models'):
        print("  [YES] Has models module")
        print(f"    Available: {dir(gf.models)[:5]}...")
    else:
        print("  [NO] No models module")
    
    # Check components
    print("\nAvailable MZI-related components:")
    mzi_components = [name for name in dir(gf.components) if 'mzi' in name.lower()]
    for comp in mzi_components[:10]:
        print(f"  - {comp}")
    
    return c


def create_half_band_filter_analytical():
    """
    Create analytical model of what a proper half-band filter should look like.
    Based on coupled-mode theory for cascaded MZIs.
    """
    
    print("\n\nCreating analytical half-band filter model...")
    print("-" * 50)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Analytical Half-Band Filter Design', fontsize=14, fontweight='bold')
    
    wavelengths = np.linspace(1.48, 1.58, 500)  # um
    n_eff = 2.4
    
    # 1. Single MZI with optimal delta_L
    ax = axes[0, 0]
    
    # For half-band filter, delta_L should give π phase shift between bands
    # Target: S-band center = 1.498 um, C-band center = 1.548 um
    s_center = 1.498e-6  # m
    c_center = 1.548e-6  # m
    
    # Want delta_phi = π between these wavelengths
    # delta_phi = 2π * n_eff * delta_L * (1/λ1 - 1/λ2) = π
    # delta_L = λ1*λ2 / (2*n_eff*(λ2-λ1))
    
    optimal_delta_L = s_center * c_center / (2 * n_eff * (c_center - s_center)) * 1e6  # um
    print(f"Calculated optimal delta_L = {optimal_delta_L:.3f} um")
    
    transmission_single = []
    for wl in wavelengths:
        delta_phi = 2 * np.pi * n_eff * optimal_delta_L * 1e-6 / (wl * 1e-6)
        T = 0.5 * (1 + np.cos(delta_phi))  # 50:50 coupler
        transmission_single.append(T)
    
    ax.plot(wavelengths * 1000, transmission_single, 'b-', linewidth=2)
    ax.axvspan(1480, 1517, alpha=0.1, color='green', label='S-band')
    ax.axvspan(1528, 1568, alpha=0.1, color='red', label='C-band')
    ax.set_title(f'Single MZI (delta_L = {optimal_delta_L:.2f} um)')
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Transmission')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylim([-0.05, 1.1])
    
    # 2. Effect of coupling ratio
    ax = axes[0, 1]
    
    kappa_values = [0.1, 0.3, 0.5, 0.7, 0.9]
    for kappa in kappa_values:
        transmission = []
        for wl in wavelengths:
            delta_phi = 2 * np.pi * n_eff * optimal_delta_L * 1e-6 / (wl * 1e-6)
            # With variable coupling
            T = (1-kappa) * np.cos(delta_phi/2)**2 + kappa * np.sin(delta_phi/2)**2
            transmission.append(T)
        ax.plot(wavelengths * 1000, transmission, linewidth=1.5, label=f'κ={kappa:.1f}')
    
    ax.axvspan(1480, 1517, alpha=0.1, color='green')
    ax.axvspan(1528, 1568, alpha=0.1, color='red')
    ax.set_title('Effect of Coupling Ratio')
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Transmission')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='right')
    ax.set_ylim([-0.05, 1.1])
    
    # 3. Cascaded with uniform coupling
    ax = axes[1, 0]
    
    num_stages = [1, 3, 5, 7, 9]
    for N in num_stages:
        transmission = []
        kappa = 0.5  # 50:50
        
        for wl in wavelengths:
            delta_phi = 2 * np.pi * n_eff * optimal_delta_L * 1e-6 / (wl * 1e-6)
            
            # N-stage cascade
            T_single = 0.5 * (1 + np.cos(delta_phi))
            T_cascade = T_single ** N
            transmission.append(T_cascade)
        
        ax.plot(wavelengths * 1000, transmission, linewidth=1.5, label=f'N={N}')
    
    ax.axvspan(1480, 1517, alpha=0.1, color='green')
    ax.axvspan(1528, 1568, alpha=0.1, color='red')
    ax.set_title('Cascaded MZIs (Uniform κ=0.5)')
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Transmission')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylim([-0.05, 1.1])
    
    # 4. Cascaded with apodized coupling
    ax = axes[1, 1]
    
    # Apodized coupling for sharper transition
    N = 13  # Number of stages
    
    # Different apodization profiles
    profiles = {
        'Uniform': [0.5] * N,
        'Gaussian': [0.5 + 0.4*np.exp(-(i-N/2)**2/(N/4)**2) for i in range(N)],
        'Triangular': [0.1 + 0.8*min(i, N-1-i)/(N//2) for i in range(N)],
        'Optimized': [0.05, 0.15, 0.25, 0.35, 0.45, 0.5, 0.5, 0.5, 0.45, 0.35, 0.25, 0.15, 0.05]
    }
    
    for name, kappas in profiles.items():
        transmission = []
        
        for wl in wavelengths:
            T_total = 1.0
            
            for kappa in kappas:
                delta_phi = 2 * np.pi * n_eff * optimal_delta_L * 1e-6 / (wl * 1e-6)
                T_stage = (1-kappa) * np.cos(delta_phi/2)**2 + kappa * np.sin(delta_phi/2)**2
                T_total *= T_stage
            
            transmission.append(T_total)
        
        ax.plot(wavelengths * 1000, transmission, linewidth=1.5, label=name)
    
    ax.axvspan(1480, 1517, alpha=0.1, color='green')
    ax.axvspan(1528, 1568, alpha=0.1, color='red')
    ax.set_title(f'Apodized Coupling (N={N})')
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Transmission')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylim([-0.05, 1.1])
    
    plt.tight_layout()
    
    # Save
    output_dir = Path(__file__).parent.parent / "results" / "gdsfactory_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "analytical_halfband_design.png", dpi=150, bbox_inches='tight')
    # plt.show()  # Commented to avoid blocking
    
    return optimal_delta_L


def main():
    """Main test function."""
    
    print("="*70)
    print("GDSFactory MZI Simulation Test")
    print("="*70)
    
    # Test single MZI
    c = test_gdsfactory_single_mzi()
    
    # Test circuit capabilities
    test_gdsfactory_circuit_model()
    
    # Create analytical model
    optimal_delta_L = create_half_band_filter_analytical()
    
    print("\n" + "="*70)
    print("Key Findings:")
    print("-" * 50)
    print("1. GDSFactory creates proper MZI layout components")
    print("2. Analytical simulation shows periodic response")
    print("3. For half-band filter, need:")
    print(f"   - Optimal delta_L = {optimal_delta_L:.2f} um")
    print("   - Cascaded stages with apodized coupling")
    print("   - More stages = sharper transition")
    print("="*70)


if __name__ == "__main__":
    main()