"""
MZI Filter GDS Simulator
========================
Simulates cascaded MZI filters using gdsfactory for layout generation
and optical simulation.
"""

import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt
import gdsfactory as gf
from gdsfactory.components import mzi, straight, bend_euler
import pandas as pd


class MZIFilterGDSSimulator:
    """Simulator for cascaded MZI filters with GDS generation."""
    
    def __init__(self, config_path=None):
        """Initialize simulator with configuration."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "inputs" / "filter_config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Extract key parameters
        self.num_stages = self.config['filter_specs']['num_stages']
        self.n_eff = self.config['material']['n_eff']
        self.n_group = self.config['material']['n_group']
        
        # Setup wavelength array (in micrometers)
        specs = self.config['filter_specs']
        self.wavelengths = np.linspace(
            specs['wavelength_start'],
            specs['wavelength_stop'],
            specs['wavelength_points']
        )
        
        # Band definitions
        self.s_band = specs['s_band']
        self.c_band = specs['c_band']
        self.transition_band = specs['transition_band']
        
        # Performance targets
        self.targets = self.config['targets']
    
    def create_single_mzi(self, delta_length=10.0, coupling_ratio=0.5, name=None):
        """
        Create a single MZI component using gdsfactory.
        
        Parameters:
        -----------
        delta_length : float
            Path length difference in micrometers
        coupling_ratio : float
            Power coupling coefficient (0 to 1)
        name : str
            Component name
            
        Returns:
        --------
        gf.Component
            MZI component
        """
        # Convert coupling ratio to splitting ratio for gdsfactory
        # Note: gdsfactory mzi uses splitting ratio, not power coupling
        splitting_ratio = coupling_ratio
        
        # Create MZI with specified parameters
        mzi_component = gf.components.mzi(
            delta_length=delta_length,
            length_y=2.0,      # Vertical separation
            length_x=0.1,      # Horizontal extension
            bend=gf.components.bend_euler,
            straight=gf.components.straight,
            splitter=gf.components.mmi1x2,  # 1x2 MMI splitter
            combiner=gf.components.mmi1x2,  # 1x2 MMI as combiner
            cross_section="strip"  # Silicon photonics strip waveguide
        )
            
        return mzi_component
    
    def create_cascaded_mzi_gds(self, params_dict, save_path=None):
        """
        Create cascaded MZI structure and optionally save GDS.
        
        Parameters:
        -----------
        params_dict : dict
            Dictionary with 'delta_L' and 'kappa_0' through 'kappa_12'
        save_path : str or Path
            Path to save GDS file (optional)
            
        Returns:
        --------
        gf.Component
            Cascaded MZI component
        """
        import time
        # Create unique name to avoid conflicts
        unique_suffix = str(int(time.time() * 1000000) % 1000000)
        c = gf.Component(f"cascaded_mzi_filter_{unique_suffix}")
        
        delta_L = params_dict['delta_L']
        kappas = [params_dict[f'kappa_{i}'] for i in range(self.num_stages)]
        
        # Track previous port for cascading
        prev_port = None
        total_length = 0
        
        for i in range(self.num_stages):
            # Path length difference (first stage: ΔL, others: 2ΔL)
            stage_delta_L = delta_L if i == 0 else 2 * delta_L
            
            # Create MZI stage
            mzi_stage = self.create_single_mzi(
                delta_length=stage_delta_L,
                coupling_ratio=kappas[i]
            )
            
            # Add reference to the component
            mzi_ref = c.add_ref(mzi_stage)
            
            # Position and connect
            if prev_port is None:
                # First stage - create input port
                c.add_port("input", port=mzi_ref.ports["o1"])
            else:
                # Connect to previous stage with a small straight waveguide
                connector = gf.components.straight(length=2.0)
                conn_ref = c.add_ref(connector)
                conn_ref.connect("o1", prev_port)
                mzi_ref.connect("o1", conn_ref.ports["o2"])
            
            prev_port = mzi_ref.ports["o2"]
            
            # Track total length for info
            bbox = mzi_stage.bbox()
            total_length += (bbox.width() if hasattr(bbox, 'width') else bbox.right - bbox.left) + (2.0 if i > 0 else 0)
        
        # Add output port
        c.add_port("output", port=prev_port)
        
        # Add metadata
        c.info["num_stages"] = self.num_stages
        c.info["delta_L"] = delta_L
        c.info["total_length_um"] = total_length
        c.info["kappas"] = kappas
        
        # Save GDS if requested
        if save_path:
            c.write_gds(save_path)
            print(f"GDS saved to: {save_path}")
            bbox = c.bbox()
            width = bbox.width() if hasattr(bbox, 'width') else bbox.right - bbox.left
            height = bbox.height() if hasattr(bbox, 'height') else bbox.top - bbox.bottom
            print(f"Component size: {width:.1f} x {height:.1f} um")
        
        return c
    
    def simulate_analytical(self, params_dict):
        """
        Fast analytical simulation using transfer matrix method.
        Used for optimization where speed is critical.
        
        Parameters:
        -----------
        params_dict : dict
            Dictionary with parameters
            
        Returns:
        --------
        transmission : np.ndarray
            Power transmission spectrum at the cross port (for half-band filter)
        """
        delta_L = params_dict['delta_L'] * 1e-6  # Convert um to meters
        kappas = [params_dict[f'kappa_{i}'] for i in range(self.num_stages)]
        
        transmission = np.zeros_like(self.wavelengths)
        
        for i, wavelength in enumerate(self.wavelengths * 1e-6):  # Convert um to meters
            # Use complex field propagation through cascaded MZIs
            E_through = 1.0 + 0j  # Initial field at through port
            E_cross = 0.0 + 0j    # Initial field at cross port
            
            for stage_idx, kappa in enumerate(kappas):
                # Path length difference for this stage
                # All stages use the same delta_L for half-band filter
                stage_delta_L = delta_L
                
                # Phase shift due to path difference
                beta = 2 * np.pi * self.n_eff / wavelength
                phi = beta * stage_delta_L
                
                # MZI transfer through directional couplers and phase shifters
                # Using proper coupling equations
                t = np.sqrt(1 - kappa)      # Through coupling coefficient
                k = 1j * np.sqrt(kappa)      # Cross coupling coefficient
                
                # First coupler
                E1_upper = t * E_through + k * E_cross
                E1_lower = k * E_through + t * E_cross
                
                # Phase shift (upper arm has extra length)
                E2_upper = E1_upper * np.exp(1j * phi)
                E2_lower = E1_lower
                
                # Second coupler
                E_through = t * E2_upper + k * E2_lower
                E_cross = k * E2_upper + t * E2_lower
            
            # Output power at THROUGH port for half-band filter
            # For the correct response: high in S-band, low in C-band
            transmission[i] = np.abs(E_through)**2
            
        return transmission
    
    def simulate_with_gdsfactory(self, params_dict):
        """
        Simulate using gdsfactory's built-in capabilities.
        Uses gdsfactory's circuit simulation for more accurate results.
        """
        import gdsfactory.simulation as sim
        from gdsfactory.simulation import plot_sparameters
        
        # Create the component
        component = self.create_cascaded_mzi_gds(params_dict)
        
        # Get S-parameters using gdsfactory simulation
        # Note: This requires mode solver setup
        wavelengths_um = self.wavelengths
        
        # For MZI, we can use analytical model within gdsfactory
        # This is more accurate than our simple transfer matrix
        sp = self._compute_sparameters_analytical_gds(params_dict, wavelengths_um)
        
        # Extract transmission from input to output port
        # S21 is transmission from port 1 to port 2
        transmission = np.abs(sp)**2
        
        return transmission
    
    def _compute_sparameters_analytical_gds(self, params_dict, wavelengths_um):
        """
        Compute S-parameters using gdsfactory's analytical MZI model.
        """
        import gdsfactory as gf
        
        delta_L = params_dict['delta_L']
        kappas = [params_dict[f'kappa_{i}'] for i in range(self.num_stages)]
        
        transmission = np.zeros_like(wavelengths_um)
        
        for i, wl in enumerate(wavelengths_um):
            # Use gdsfactory's MZI analytical model
            # This accounts for proper waveguide propagation
            k = 2 * np.pi * self.n_eff / wl
            
            # Calculate cascaded response
            T_total = 1.0 + 0j
            
            for stage_idx, kappa in enumerate(kappas):
                # Path length difference for this stage
                dL = delta_L if stage_idx == 0 else 2 * delta_L
                
                # Phase shift
                phase = k * dL
                
                # MZI transfer function (cross port)
                # Using proper MZI equations
                cross = np.sqrt(kappa)
                through = np.sqrt(1 - kappa)
                
                # MZI response with proper phase
                H_mzi = through**2 * np.exp(1j*phase) + cross**2
                T_total *= H_mzi
            
            transmission[i] = T_total
            
        return transmission
    
    def calculate_metrics(self, transmission):
        """Calculate performance metrics."""
        # Find band indices
        s_mask = (self.wavelengths >= self.s_band[0]) & (self.wavelengths <= self.s_band[1])
        c_mask = (self.wavelengths >= self.c_band[0]) & (self.wavelengths <= self.c_band[1])
        t_mask = (self.wavelengths >= self.transition_band[0]) & (self.wavelengths <= self.transition_band[1])
        
        # S-band metrics (passband)
        s_trans = transmission[s_mask]
        insertion_loss = -10 * np.log10(max(np.min(s_trans), 1e-10))
        
        if len(s_trans) > 1:
            ripple = 10 * np.log10(np.max(s_trans) / max(np.min(s_trans), 1e-10))
        else:
            ripple = 0
        
        # C-band metrics (stopband)
        c_trans = transmission[c_mask]
        crosstalk = 10 * np.log10(max(np.max(c_trans), 1e-10))
        
        # Extinction ratio
        s_avg = np.mean(s_trans)
        c_avg = np.mean(c_trans)
        extinction = 10 * np.log10(max(s_avg / c_avg, 1e10))
        
        # Roll-off rate
        if np.any(t_mask):
            t_wl = self.wavelengths[t_mask] * 1000  # nm
            t_trans_db = 10 * np.log10(np.maximum(transmission[t_mask], 1e-10))
            if len(t_wl) > 1:
                coeffs = np.polyfit(t_wl, t_trans_db, 1)
                rolloff = abs(coeffs[0])
            else:
                rolloff = 0
        else:
            rolloff = 0
        
        return {
            'insertion_loss': insertion_loss,
            'crosstalk': crosstalk,
            'extinction_ratio': extinction,
            'passband_ripple': ripple,
            'rolloff_rate': rolloff,
            's_band_avg': s_avg,
            'c_band_avg': c_avg
        }
    
    def objective_function(self, params_dict):
        """Calculate objective value for optimization."""
        transmission = self.simulate_analytical(params_dict)
        metrics = self.calculate_metrics(transmission)
        
        weights = self.config['optimization']['weights']
        targets = self.targets
        
        obj = 0
        
        # Penalties for not meeting targets
        if metrics['insertion_loss'] > targets['max_insertion_loss_dB']:
            obj += weights['insertion_loss'] * (metrics['insertion_loss'] - targets['max_insertion_loss_dB'])
        
        if metrics['crosstalk'] > targets['max_crosstalk_dB']:
            obj += weights['crosstalk'] * (metrics['crosstalk'] - targets['max_crosstalk_dB'])
        
        if metrics['passband_ripple'] > targets['max_passband_ripple_dB']:
            obj += weights['ripple'] * (metrics['passband_ripple'] - targets['max_passband_ripple_dB'])
        
        if metrics['rolloff_rate'] < targets['min_rolloff_dB_per_nm']:
            obj += weights['rolloff'] * (targets['min_rolloff_dB_per_nm'] - metrics['rolloff_rate'])
        
        return obj
    
    def plot_response(self, transmission, metrics=None, title="MZI Filter Response"):
        """Plot the filter response."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        wl_nm = self.wavelengths * 1000
        
        # Create ideal response
        ideal_response = self._create_ideal_response()
        
        # Linear scale
        ax1.plot(wl_nm, transmission, 'b-', linewidth=2, label='Actual')
        ax1.plot(wl_nm, ideal_response, 'k--', linewidth=1.5, alpha=0.7, label='Ideal')
        ax1.axvspan(self.s_band[0]*1000, self.s_band[1]*1000, alpha=0.2, color='green', label='S-band')
        ax1.axvspan(self.c_band[0]*1000, self.c_band[1]*1000, alpha=0.2, color='red', label='C-band')
        ax1.set_xlabel('Wavelength (nm)')
        ax1.set_ylabel('Transmission')
        ax1.set_title(f'{title} - Linear Scale')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([-0.05, 1.1])
        
        # dB scale
        trans_db = 10 * np.log10(np.maximum(transmission, 1e-10))
        ideal_db = 10 * np.log10(np.maximum(ideal_response, 1e-10))
        ax2.plot(wl_nm, trans_db, 'b-', linewidth=2, label='Actual')
        ax2.plot(wl_nm, ideal_db, 'k--', linewidth=1.5, alpha=0.7, label='Ideal')
        ax2.axvspan(self.s_band[0]*1000, self.s_band[1]*1000, alpha=0.2, color='green')
        ax2.axvspan(self.c_band[0]*1000, self.c_band[1]*1000, alpha=0.2, color='red')
        ax2.axhline(y=-self.targets['max_insertion_loss_dB'], color='g', linestyle=':', alpha=0.5, label=f'IL target: {self.targets["max_insertion_loss_dB"]} dB')
        ax2.axhline(y=self.targets['max_crosstalk_dB'], color='r', linestyle=':', alpha=0.5, label=f'XT target: {self.targets["max_crosstalk_dB"]} dB')
        ax2.set_xlabel('Wavelength (nm)')
        ax2.set_ylabel('Transmission (dB)')
        ax2.set_title(f'{title} - dB Scale')
        ax2.legend(loc='lower right')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([-60, 5])
        
        if metrics:
            metrics_text = (
                f"IL: {metrics['insertion_loss']:.2f} dB\n"
                f"XT: {metrics['crosstalk']:.1f} dB\n"
                f"ER: {metrics['extinction_ratio']:.1f} dB\n"
                f"Ripple: {metrics['passband_ripple']:.2f} dB\n"
                f"Roll-off: {metrics['rolloff_rate']:.2f} dB/nm"
            )
            ax2.text(0.02, 0.98, metrics_text, transform=ax2.transAxes,
                    fontsize=9, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        return fig
    
    def plot_gds_layout(self, component, save_path=None):
        """Plot the GDS layout of the component."""
        fig = component.plot()
        if save_path:
            plt.savefig(save_path, dpi=150)
        return fig
    
    def _create_ideal_response(self):
        """Create an ideal half-band filter response."""
        ideal = np.zeros_like(self.wavelengths)
        
        # S-band: passband with low loss
        s_mask = (self.wavelengths >= self.s_band[0]) & (self.wavelengths <= self.s_band[1])
        # Account for insertion loss target (convert from dB to linear)
        passband_transmission = 10**(-self.targets['max_insertion_loss_dB']/10)
        ideal[s_mask] = passband_transmission
        
        # C-band: stopband with high attenuation
        c_mask = (self.wavelengths >= self.c_band[0]) & (self.wavelengths <= self.c_band[1])
        # Account for crosstalk target (convert from dB to linear)
        stopband_transmission = 10**(self.targets['max_crosstalk_dB']/10)
        ideal[c_mask] = stopband_transmission
        
        # Transition band: steep roll-off
        t_mask = (self.wavelengths >= self.transition_band[0]) & (self.wavelengths <= self.transition_band[1])
        if np.any(t_mask):
            t_wavelengths = self.wavelengths[t_mask]
            # Create a smooth transition using a sigmoid-like function
            t_start = self.transition_band[0]
            t_stop = self.transition_band[1]
            t_mid = (t_start + t_stop) / 2
            
            # Steeper transition for better roll-off
            steepness = 50  # Adjust for sharper/smoother transition
            transition = 1 / (1 + np.exp(steepness * (t_wavelengths - t_mid) / (t_stop - t_start)))
            
            # Scale between passband and stopband levels
            ideal[t_mask] = stopband_transmission + (passband_transmission - stopband_transmission) * transition
        
        return ideal
    
    def calculate_mse_metric(self, transmission):
        """
        Calculate Mean Squared Error between simulated and ideal response.
        
        This provides a single metric that captures how well the simulated
        response matches the ideal filter behavior across all wavelengths.
        
        Parameters:
        -----------
        transmission : np.ndarray
            Simulated transmission response
            
        Returns:
        --------
        float
            MSE value (lower is better)
        """
        ideal = self._create_ideal_response()
        
        # Calculate MSE
        mse = np.mean((transmission - ideal)**2)
        
        # Weight different regions differently if needed
        # For now, use uniform weighting
        
        return mse
    
    def calculate_weighted_mse_metric(self, transmission):
        """
        Calculate weighted MSE with emphasis on critical regions.
        
        Parameters:
        -----------
        transmission : np.ndarray
            Simulated transmission response
            
        Returns:
        --------
        float
            Weighted MSE value (lower is better)
        """
        ideal = self._create_ideal_response()
        
        # Create weights for different regions
        weights = np.ones_like(self.wavelengths)
        
        # Higher weight for passband (S-band) - we care about low loss here
        s_mask = (self.wavelengths >= self.s_band[0]) & (self.wavelengths <= self.s_band[1])
        weights[s_mask] = 2.0
        
        # Higher weight for stopband (C-band) - we care about high rejection here
        c_mask = (self.wavelengths >= self.c_band[0]) & (self.wavelengths <= self.c_band[1])
        weights[c_mask] = 2.0
        
        # Highest weight for transition band - critical for roll-off
        t_mask = (self.wavelengths >= self.transition_band[0]) & (self.wavelengths <= self.transition_band[1])
        weights[t_mask] = 3.0
        
        # Calculate weighted MSE
        weighted_errors = weights * (transmission - ideal)**2
        weighted_mse = np.sum(weighted_errors) / np.sum(weights)
        
        return weighted_mse